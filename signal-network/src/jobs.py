"""Redis-backed job queue and worker for the Signal Network spine."""

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.ingest import download_video
from src.pipeline import SignalPipeline
from src.schemas import JobStatus


@dataclass
class JobConfig:
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    queue_key: str = "signal_network:jobs:pending"
    job_key_prefix: str = "signal_network:job:"


class JobStore:
    """Redis-backed store for job state."""

    def __init__(self, redis_client=None, config: Optional[JobConfig] = None):
        self.config = config or JobConfig()
        self._redis = redis_client

    def _connect(self):
        if self._redis is None:
            import redis as redis_lib
            self._redis = redis_lib.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=True,
            )
        return self._redis

    def _job_key(self, job_id: str) -> str:
        return f"{self.config.job_key_prefix}{job_id}"

    def create_job(self, source_lang: str, target_langs: List[str], source_url: Optional[str] = None, file_path: Optional[str] = None) -> str:
        job_id = str(uuid.uuid4())
        payload = {
            "id": job_id,
            "status": JobStatus.PENDING.value,
            "source_lang": source_lang,
            "target_langs": target_langs,
            "source_url": source_url,
            "file_path": file_path,
            "outputs": {},
            "error": None,
            "created_at": time.time(),
        }
        r = self._connect()
        r.set(self._job_key(job_id), json.dumps(payload))
        r.lpush(self.config.queue_key, job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        r = self._connect()
        data = r.get(self._job_key(job_id))
        if data is None:
            return None
        return json.loads(data)

    def update_job(self, job_id: str, **fields) -> None:
        r = self._connect()
        job = self.get_job(job_id)
        if job is None:
            return
        job.update(fields)
        job["updated_at"] = time.time()
        r.set(self._job_key(job_id), json.dumps(job))

    def pop_pending(self) -> Optional[str]:
        r = self._connect()
        result = r.brpop(self.config.queue_key, timeout=1)
        if result is None:
            return None
        return result[1]


class SpineWorker:
    """Worker that consumes pending jobs and runs the spine pipeline."""

    def __init__(
        self,
        job_store: JobStore,
        pipeline: Optional[SignalPipeline] = None,
        output_dir: str = "outputs",
    ):
        self.store = job_store
        self.pipeline = pipeline or SignalPipeline(output_dir=output_dir)
        self._running = False

    def process_one(self, job_id: str) -> None:
        job = self.store.get_job(job_id)
        if job is None:
            return

        self.store.update_job(job_id, status=JobStatus.RUNNING.value)

        try:
            video_path = job.get("file_path")
            if video_path is None and job.get("source_url"):
                from src.ingest import DownloadResult
                download_path = Path(self.pipeline.output_dir) / f"{job_id}_download.mp4"
                result = download_video(job["source_url"], download_path)
                if not result.success:
                    raise RuntimeError(f"Download failed: {result.error}")
                video_path = str(result.output_path)

            if video_path is None or not Path(video_path).exists():
                raise RuntimeError("No valid video source provided")

            result = self.pipeline.run(
                video_path=video_path,
                source_lang=job["source_lang"],
                target_langs=job["target_langs"],
            )

            if result.success:
                self.store.update_job(
                    job_id,
                    status=JobStatus.COMPLETED.value,
                    outputs=result.outputs,
                )
            else:
                self.store.update_job(
                    job_id,
                    status=JobStatus.FAILED.value,
                    error=result.error,
                )
        except Exception as exc:
            self.store.update_job(job_id, status=JobStatus.FAILED.value, error=str(exc))

    def run_once(self) -> Optional[str]:
        """Process one pending job. Returns job_id or None."""
        job_id = self.store.pop_pending()
        if job_id is not None:
            self.process_one(job_id)
        return job_id

    def run_forever(self) -> None:
        """Blocking loop processing jobs until stop() is called."""
        self._running = True
        while self._running:
            self.run_once()

    def stop(self) -> None:
        self._running = False
