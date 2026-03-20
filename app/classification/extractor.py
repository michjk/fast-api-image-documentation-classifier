import re
from dataclasses import dataclass

from app.config import settings


@dataclass
class ExtractedImageInfo:
    document_title: str
    page_number: int | None
    summary: str


class ImageExtractor:
    async def extract(self, image_name: str) -> ExtractedImageInfo:
        title = image_name.split("_")[0] if "_" in image_name else "document"
        match = re.search(r"(\d+)", image_name)
        page = int(match.group(1)) if match else None
        return ExtractedImageInfo(
            document_title=title,
            page_number=page,
            summary=f"Extracted with model {settings.openai_model}",
        )
