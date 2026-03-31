import io
import logging
from uuid import uuid4

import boto3
from botocore.config import Config as BotoConfig

from src.core.config import settings

logger = logging.getLogger(__name__)


def client_facing_asset_url(url: str | None) -> str | None:
    """Rewrite stored `{endpoint}/{bucket}/key` URLs for browser access.

    R2/S3 API endpoints are not publicly readable; set S3_PUBLIC_BASE_URL to your public bucket
    URL (or CDN) so list/detail responses return loadable image URLs.
    """
    if url is None or not str(url).strip():
        return url
    u = str(url).strip()
    pub = settings.s3_public_base_url.strip()
    if not pub:
        return u
    marker = f"/{settings.s3_bucket}/"
    if marker not in u:
        return u
    suffix = u.split(marker, 1)[1]
    base = pub.rstrip("/")
    if settings.s3_public_bucket_in_path:
        return f"{base}/{settings.s3_bucket}/{suffix}"
    return f"{base}/{suffix}"


class StorageService:
    """S3-compatible object storage client for asset uploads."""

    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=BotoConfig(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self._bucket = settings.s3_bucket

    def object_url(self, object_key: str) -> str:
        """URL returned after upload and in API responses (uses public base when configured)."""
        pub = settings.s3_public_base_url.strip()
        if pub:
            base = pub.rstrip("/")
            if settings.s3_public_bucket_in_path:
                return f"{base}/{self._bucket}/{object_key}"
            return f"{base}/{object_key}"
        return f"{settings.s3_endpoint.rstrip('/')}/{self._bucket}/{object_key}"

    def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except Exception:
            self._client.create_bucket(Bucket=self._bucket)

    async def upload_file(
        self,
        file_content: bytes,
        content_type: str,
        merchant_id: str,
        asset_pack_id: str,
        original_filename: str,
    ) -> str:
        """Upload a file to S3 and return the storage URL.

        Files are stored under: {merchant_id}/{asset_pack_id}/{uuid}_{original_filename}
        """
        file_ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "bin"
        object_key = f"{merchant_id}/{asset_pack_id}/{uuid4().hex}.{file_ext}"

        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=object_key,
                Body=io.BytesIO(file_content),
                ContentType=content_type,
            )
        except Exception:
            logger.exception(
                "S3 put_object failed bucket=%s key=%s endpoint=%s",
                self._bucket,
                object_key,
                settings.s3_endpoint,
            )
            raise

        url = self.object_url(object_key)
        logger.info(
            "storage uploaded bucket=%s key=%s bytes=%s url_prefix=%s",
            self._bucket,
            object_key,
            len(file_content),
            url[:80] + ("…" if len(url) > 80 else ""),
        )
        return url

    def get_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for downloading an asset."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": object_key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, object_key: str) -> None:
        """Delete a file from S3."""
        self._client.delete_object(Bucket=self._bucket, Key=object_key)


storage = StorageService()
