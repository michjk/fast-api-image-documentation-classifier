from collections import defaultdict

from app.classification.extractor import ExtractedImageInfo


class ImageGrouper:
    def group_and_sort(self, items: list[tuple[str, ExtractedImageInfo]]) -> dict[str, list[str]]:
        grouped: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for image_id, info in items:
            order = info.page_number if info.page_number is not None else 10**9
            grouped[info.document_title].append((image_id, order))

        result: dict[str, list[str]] = {}
        for title, images in grouped.items():
            result[title] = [image_id for image_id, _ in sorted(images, key=lambda x: x[1])]
        return result
