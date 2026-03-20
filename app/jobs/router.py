from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db_session
from app.jobs.schemas import JobCreateResponse, JobStatusResponse
from app.jobs.service import add_uploaded_image, create_job, fetch_job_response, launch_job
from app.models import User
from app.storage.s3 import S3Storage

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_storage() -> S3Storage:
    return S3Storage()


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_job(
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    storage: S3Storage = Depends(get_storage),
) -> JobCreateResponse:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")

    job = await create_job(session, user.id)
    for upload in files:
        await add_uploaded_image(
            session=session,
            storage=storage,
            user_id=user.id,
            job_id=job.id,
            filename=upload.filename,
            content_type=upload.content_type or "application/octet-stream",
            fileobj=upload.file,
        )
    launch_job(job.id, user.id)
    return JobCreateResponse(job_id=job.id, status=job.status.value)


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job(
    job_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    storage: S3Storage = Depends(get_storage),
) -> JobStatusResponse:
    try:
        payload = await fetch_job_response(session, storage, job_id, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return JobStatusResponse(**payload)
