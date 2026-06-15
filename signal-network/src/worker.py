"""Background worker entrypoint for Signal Network."""

import os

from src.jobs import JobConfig, JobStore, SpineWorker
from src.pipeline import SignalPipeline


def main():
    config = JobConfig(
        redis_host=os.environ.get("REDIS_HOST", "localhost"),
        redis_port=int(os.environ.get("REDIS_PORT", "6379")),
    )
    store = JobStore(config=config)
    worker = SpineWorker(job_store=store, pipeline=SignalPipeline())
    print(f"Signal Network worker started (Redis: {config.redis_host}:{config.redis_port})")
    try:
        worker.run_forever()
    except KeyboardInterrupt:
        worker.stop()
        print("Worker stopped.")


if __name__ == "__main__":
    main()
