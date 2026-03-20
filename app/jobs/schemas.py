from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GroupedImage(BaseModel):
    image_id: UUID
    url: str
    sequence_number: int


class JobGroup(BaseModel):
    group_id: UUID
    title: str
    images: list[GroupedImage]


class JobCreateResponse(BaseModel):
    job_id: UUID
    status: str


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    groups: list[JobGroup] = []
    error_message: str | None = None
