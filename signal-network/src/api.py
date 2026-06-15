"""FastAPI service for the Signal Network job queue."""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException

from src.jobs import JobConfig, JobStore, SpineWorker
from src.pipeline import SignalPipeline
from src.schemas import JobRequest, JobResponse


# Global state is shared between lifespan and endpoints.
_store: Optional[JobStore] = None
_worker: Optional[SpineWorker] = None


def get_store() -> JobStore:
    if _store is None:
        raise RuntimeError("JobStore not initialized")
    return _store


def _job_config_from_env() -> JobConfig:
    return JobConfig(
        redis_host=os.environ.get("REDIS_HOST", "localhost"),
        redis_port=int(os.environ.get("REDIS_PORT", "6379")),
    )


def create_app(redis_client=None, pipeline: Optional[SignalPipeline] = None) -> FastAPI:
    """Create the FastAPI app with injected dependencies."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        global _store, _worker
        config = _job_config_from_env()
        _store = JobStore(redis_client=redis_client, config=config)
        _worker = SpineWorker(job_store=_store, pipeline=pipeline)
        yield
        _store = None
        _worker = None

    app = FastAPI(
        title="Signal Network",
        description="Deterministic regional edutainment pipeline",
        version="0.2.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/jobs", response_model=JobResponse)
    def create_job(request: JobRequest) -> JobResponse:
        if not request.source_url and not request.file_path:
            raise HTTPException(status_code=400, detail="Provide source_url or file_path")

        store = get_store()
        job_id = store.create_job(
            source_lang=request.source_lang,
            target_langs=request.target_langs,
            source_url=request.source_url,
            file_path=request.file_path,
        )
        job = store.get_job(job_id)
        return _to_response(job)

    @app.get("/jobs/{job_id}", response_model=JobResponse)
    def get_job(job_id: str) -> JobResponse:
        store = get_store()
        job = store.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return _to_response(job)

    @app.post("/jobs/{job_id}/run")
    def run_job_sync(job_id: str) -> JobResponse:
        """Run a single job synchronously (useful for testing/small jobs)."""
        store = get_store()
        job = store.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        if _worker is None:
            raise HTTPException(status_code=500, detail="Worker not initialized")
        _worker.process_one(job_id)
        return _to_response(store.get_job(job_id))

    return app


def _to_response(job: dict) -> JobResponse:
    return JobResponse(
        id=job["id"],
        status=job["status"],
        source_lang=job["source_lang"],
        target_langs=job["target_langs"],
        outputs=job.get("outputs", {}),
        error=job.get("error"),
    )
