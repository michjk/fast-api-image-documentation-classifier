from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.classification.extractor import ExtractedImageInfo, ImageExtractor
from app.classification.grouper import ImageGrouper
from app.models import Group, Image, Job, JobStatus


class ClassificationPipeline:
    def __init__(self) -> None:
        self.extractor = ImageExtractor()
        self.grouper = ImageGrouper()

    async def process(self, session: AsyncSession, job_id: UUID, user_id: UUID) -> None:
        job = await session.scalar(select(Job).where(Job.id == job_id, Job.user_id == user_id))
        if job is None:
            raise ValueError("Job not found")

        job.status = JobStatus.processing
        await session.commit()

        images = list(await session.scalars(select(Image).where(Image.job_id == job_id)))
        extracted: list[tuple[str, ExtractedImageInfo]] = []
        for image in images:
            info = await self.extractor.extract(image.original_filename)
            image.extracted_text = info.summary
            image.page_info = {"page_number": info.page_number}
            extracted.append((str(image.id), info))

        title_to_image_ids = self.grouper.group_and_sort(extracted)

        await session.execute(delete(Group).where(Group.job_id == job_id))
        await session.flush()

        id_to_image = {str(img.id): img for img in images}
        for title, image_ids in title_to_image_ids.items():
            group = Group(job_id=job_id, title=title)
            session.add(group)
            await session.flush()
            for idx, image_id in enumerate(image_ids, start=1):
                target = id_to_image[image_id]
                target.group_id = group.id
                target.sequence_number = idx

        job.status = JobStatus.completed
        job.error_message = None
        await session.commit()
