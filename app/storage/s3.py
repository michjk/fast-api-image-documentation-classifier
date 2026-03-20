from io import BytesIO

import boto3
from botocore.client import Config

from app.config import settings


class S3Storage:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.s3_bucket

    def upload_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> None:
        self.client.upload_fileobj(BytesIO(data), self.bucket, key, ExtraArgs={"ContentType": content_type})

    def generate_presigned_url(self, key: str) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=settings.s3_presigned_url_expire_seconds,
        )
