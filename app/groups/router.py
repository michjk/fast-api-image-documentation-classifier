from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db_session
from app.groups.schemas import GroupResponse
from app.jobs.router import get_storage
from app.models import Group, Job, User
from app.storage.s3 import S3Storage

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    storage: S3Storage = Depends(get_storage),
) -> GroupResponse:
    group = await session.scalar(
        select(Group)
        .join(Job, Group.job_id == Job.id)
        .where(Group.id == group_id, Job.user_id == user.id)
        .options(joinedload(Group.images))
    )
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    sorted_images = sorted(
        [img for img in group.images if img.sequence_number is not None],
        key=lambda img: img.sequence_number,
    )
    return GroupResponse(
        group_id=group.id,
        title=group.title,
        images=[
            {
                "image_id": img.id,
                "url": storage.generate_presigned_url(img.s3_key),
                "sequence_number": img.sequence_number,
            }
            for img in sorted_images
        ],
    )
