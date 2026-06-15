"""Pydantic schemas for the Signal Network API."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRequest(BaseModel):
    source_url: Optional[str] = Field(None, description="URL to download (YouTube, etc.)")
    file_path: Optional[str] = Field(None, description="Local path to existing video file")
    source_lang: str = Field(..., description="Source language code, e.g. te, mr, hi")
    target_langs: List[str] = Field(..., description="List of target language codes")


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    source_lang: str
    target_langs: List[str]
    outputs: Dict[str, str] = Field(default_factory=dict)
    error: Optional[str] = None
