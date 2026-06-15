"""Tests for publishing adapters."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure src/ is on path.
_SRC_DIR = Path(__file__).parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from src.publishers import (
    AzureBlobPublisher,
    FilePublisher,
    MultiPlatformPublisher,
)


def test_file_publisher_writes_manifest(tmp_path):
    pub = FilePublisher(output_dir=str(tmp_path / "manifests"))
    result = pub.publish(
        video_path=str(tmp_path / "video.mp4"),
        caption="test caption",
        hashtags=["#test"],
        schedule_time="19:00",
    )
    assert result.success
    assert result.url
    assert Path(result.url).exists()


def test_azure_blob_publisher_missing_connection_string(monkeypatch):
    monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
    pub = AzureBlobPublisher(container_name="test")
    result = pub.publish(
        video_path="/tmp/v.mp4",
        caption="c",
        hashtags=["#h"],
    )
    assert not result.success
    assert "AZURE_STORAGE_CONNECTION_STRING" in result.error


def test_azure_blob_publisher_missing_container_name(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "fake")
    monkeypatch.delenv("AZURE_STORAGE_CONTAINER", raising=False)
    pub = AzureBlobPublisher()
    result = pub.publish(
        video_path="/tmp/v.mp4",
        caption="c",
        hashtags=["#h"],
    )
    assert not result.success
    assert "AZURE_STORAGE_CONTAINER" in result.error


def test_azure_blob_publisher_uploads_video(tmp_path, monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "fake-conn")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "testcontainer")

    video = tmp_path / "hello.mp4"
    video.write_text("fake video bytes")

    mock_blob_client = MagicMock()
    mock_blob_client.url = "https://example.blob.core.windows.net/testcontainer/signal-network/hello.mp4"

    mock_service = MagicMock()
    mock_service.get_blob_client.return_value = mock_blob_client

    with patch("azure.storage.blob.BlobServiceClient") as MockClient:
        MockClient.from_connection_string.return_value = mock_service
        pub = AzureBlobPublisher()
        result = pub.publish(
            video_path=str(video),
            caption="c",
            hashtags=["#h"],
        )

    assert result.success
    assert result.platform == "azure_blob"
    assert result.post_id == "signal-network/hello.mp4"
    assert result.url == mock_blob_client.url
    mock_service.get_blob_client.assert_called_once_with(
        container="testcontainer",
        blob="signal-network/hello.mp4",
    )
    mock_blob_client.upload_blob.assert_called_once()


def test_azure_blob_publisher_returns_error_for_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "fake-conn")
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "testcontainer")

    pub = AzureBlobPublisher()
    result = pub.publish(
        video_path=str(tmp_path / "missing.mp4"),
        caption="c",
        hashtags=["#h"],
    )
    assert not result.success
    assert "not found" in result.error.lower()


def test_multi_platform_publisher_skips_unknown():
    publisher = MultiPlatformPublisher()
    results = publisher.publish_all(
        video_path="/tmp/v.mp4",
        caption="c",
        hashtags=["#h"],
        platforms=["file_manifest", "unknown_platform"],
    )
    assert len(results) == 2
    assert results[0].success
    assert not results[1].success
