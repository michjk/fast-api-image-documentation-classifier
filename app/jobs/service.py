import asyncio
import uuid
from datetime import UTC, datetime
from typing import BinaryIO
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.classification.pipeline import ClassificationPipeline
from app.database import AsyncSessionLocal
from app.models import Group, Image, Job, JobStatus
from app.storage.s3 import S3Storage

pipeline = ClassificationPipeline()


def build_image_key(user_id: UUID, job_id: UUID, filename: str) -> str:
    return f"users/{user_id}/jobs/{job_id}/{uuid.uuid4()}-{filename}"


async def create_job(session, user_id: UUID) -> Job:
    job = Job(user_id=user_id, status=JobStatus.pending)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def add_uploaded_image(
    session,
    storage: S3Storage,
    user_id: UUID,
    job_id: UUID,
    filename: str,
    content_type: str,
    fileobj: BinaryIO,
) -> Image:
    key = build_image_key(user_id, job_id, filename)
    data = fileobj.read()
    storage.upload_bytes(data, key, content_type)
    image = Image(job_id=job_id, original_filename=filename, s3_key=key)
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


async def process_job_background(job_id: UUID, user_id: UUID) -> None:
    async with AsyncSessionLocal() as session:
        try:
            await pipeline.process(session, job_id, user_id)
        except Exception as exc:
            job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == user_id))
            if job is None:
                return
            job.status = JobStatus.failed
            job.updated_at = datetime.now(UTC)
            job.error_message = str(exc)
            await session.commit()


def launch_job(job_id: UUID, user_id: UUID) -> None:
    asyncio.create_task(process_job_background(job_id, user_id))


async def fetch_job_response(session, storage: S3Storage, job_id: UUID, user_id: UUID):
    job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == user_id))
    if job is None:
        raise ValueError("Job not found")

    groups = list(
        await session.scalars(
            select(Group)
            .where(Group.job_id == job_id)
            .options(selectinload(Group.images))
            .order_by(Group.created_at.asc())
        )
    )

    payload_groups = []
    for group in groups:
        sorted_images = sorted(
            [img for img in group.images if img.sequence_number is not None],
            key=lambda img: img.sequence_number,
        )
        payload_groups.append(
            {
                "group_id": group.id,
                "title": group.title,
                "images": [
                    {
                        "image_id": img.id,
                        "url": storage.generate_presigned_url(img.s3_key),
                        "sequence_number": img.sequence_number,
                    }
                    for img in sorted_images
                ],
            }
        )

    return {
        "job_id": job.id,
        "status": job.status.value,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "groups": payload_groups,
        "error_message": job.error_message,
    }
