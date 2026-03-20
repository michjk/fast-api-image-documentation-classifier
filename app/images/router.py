from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db_session
from app.jobs.router import get_storage
from app.models import Image, Job, User
from app.storage.s3 import S3Storage

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{image_id}")
async def get_image(
    image_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    storage: S3Storage = Depends(get_storage),
):
    image = await session.scalar(
        select(Image)
        .join(Job, Image.job_id == Job.id)
        .where(Image.id == image_id, Job.user_id == user.id)
    )
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return RedirectResponse(url=storage.generate_presigned_url(image.s3_key), status_code=status.HTTP_307_TEMPORARY_REDIRECT)
