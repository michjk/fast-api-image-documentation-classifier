from uuid import UUID

from pydantic import BaseModel


class GroupImageResponse(BaseModel):
    image_id: UUID
    url: str
    sequence_number: int


class GroupResponse(BaseModel):
    group_id: UUID
    title: str
    images: list[GroupImageResponse]
