"""Publishing adapters for social platforms."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PublishResult:
    platform: str
    success: bool
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class BasePublisher:
    """Interface for platform publishers."""

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        raise NotImplementedError


class FilePublisher(BasePublisher):
    """Test publisher that writes a manifest to disk instead of uploading."""

    def __init__(self, output_dir: str = "outputs/publish_manifests"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        manifest = {
            "video_path": video_path,
            "caption": caption,
            "hashtags": hashtags,
            "schedule_time": schedule_time,
        }
        stem = Path(video_path).stem
        out_file = self.output_dir / f"{stem}_manifest.json"
        out_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return PublishResult(
            platform="file_manifest",
            success=True,
            post_id=str(out_file),
            url=str(out_file),
        )


class OpenShortsPublisher(BasePublisher):
    """Stub for OpenShorts auto-publishing API."""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        # Placeholder: integrate with OpenShorts upload-post API.
        return PublishResult(
            platform="openshorts",
            success=False,
            error="OpenShorts integration not yet implemented",
        )


class YouTubePublisher(BasePublisher):
    """Stub for YouTube Data API v3 publishing."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        if not self.api_key:
            return PublishResult(
                platform="youtube_shorts",
                success=False,
                error="YOUTUBE_API_KEY not configured",
            )
        # Placeholder: use google-api-python-client to upload.
        return PublishResult(
            platform="youtube_shorts",
            success=False,
            error="YouTube upload not yet implemented (configure YOUTUBE_API_KEY)",
        )


class InstagramPublisher(BasePublisher):
    """Stub for Instagram Reels publishing via instagrapi."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.environ.get("INSTAGRAM_USERNAME")
        self.password = password or os.environ.get("INSTAGRAM_PASSWORD")

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        if not self.username or not self.password:
            return PublishResult(
                platform="instagram_reels",
                success=False,
                error="INSTAGRAM_USERNAME/PASSWORD not configured",
            )
        # Placeholder: use instagrapi to upload reel.
        return PublishResult(
            platform="instagram_reels",
            success=False,
            error="Instagram upload not yet implemented (configure credentials)",
        )


class TikTokPublisher(BasePublisher):
    """Stub for TikTok publishing via tiktok-uploader."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or os.environ.get("TIKTOK_SESSION_ID")

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        if not self.session_id:
            return PublishResult(
                platform="tiktok",
                success=False,
                error="TIKTOK_SESSION_ID not configured",
            )
        # Placeholder: use tiktok-uploader.
        return PublishResult(
            platform="tiktok",
            success=False,
            error="TikTok upload not yet implemented (configure TIKTOK_SESSION_ID)",
        )


class AzureBlobPublisher(BasePublisher):
    """Upload videos to Azure Blob Storage using azure-storage-blob."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        container_name: Optional[str] = None,
        blob_prefix: str = "signal-network/",
    ):
        self.connection_string = connection_string or os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = container_name or os.environ.get("AZURE_STORAGE_CONTAINER")
        self.blob_prefix = blob_prefix

    def publish(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None,
    ) -> PublishResult:
        if not self.connection_string:
            return PublishResult(
                platform="azure_blob",
                success=False,
                error="AZURE_STORAGE_CONNECTION_STRING not configured",
            )
        if not self.container_name:
            return PublishResult(
                platform="azure_blob",
                success=False,
                error="AZURE_STORAGE_CONTAINER not configured",
            )

        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            return PublishResult(
                platform="azure_blob",
                success=False,
                error="azure-storage-blob is not installed; run 'pip install azure-storage-blob'",
            )

        try:
            path = Path(video_path)
            if not path.exists():
                return PublishResult(
                    platform="azure_blob",
                    success=False,
                    error=f"Video file not found: {video_path}",
                )

            blob_name = f"{self.blob_prefix}{path.name}"
            blob_service = BlobServiceClient.from_connection_string(self.connection_string)
            blob_client = blob_service.get_blob_client(container=self.container_name, blob=blob_name)

            with open(path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            url = blob_client.url
            return PublishResult(
                platform="azure_blob",
                success=True,
                post_id=blob_name,
                url=url,
            )
        except Exception as exc:
            return PublishResult(
                platform="azure_blob",
                success=False,
                error=f"Azure upload failed: {exc}",
            )


class MultiPlatformPublisher:
    """Publishes to multiple platforms using injected publishers."""

    def __init__(self, publishers: Optional[Dict[str, BasePublisher]] = None):
        self.publishers = publishers or {
            "file_manifest": FilePublisher(),
            "azure_blob": AzureBlobPublisher(),
            "youtube_shorts": YouTubePublisher(),
            "instagram_reels": InstagramPublisher(),
            "tiktok": TikTokPublisher(),
            "openshorts": OpenShortsPublisher(),
        }

    def publish_all(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        platforms: List[str],
        schedule_time: Optional[str] = None,
    ) -> List[PublishResult]:
        results = []
        for platform in platforms:
            publisher = self.publishers.get(platform)
            if publisher is None:
                results.append(
                    PublishResult(
                        platform=platform,
                        success=False,
                        error=f"No publisher configured for {platform}",
                    )
                )
                continue
            results.append(
                publisher.publish(video_path, caption, hashtags, schedule_time)
            )
        return results
