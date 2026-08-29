"""
worker.py — RQ (Redis Queue) worker process for inference tasks.

Start with:
    rq worker --url $REDIS_URL inference-tasks

On Railway / Docker, start.sh launches this before Gunicorn so inference
jobs never run inside the web process, keeping the web server responsive.
"""

import os
os.environ["IS_WORKER"] = "true"
import logging
import torch

# Low-RAM tuning: restrict to 1 CPU thread so the worker doesn't compete
# with itself when PyTorch spawns multiple OpenMP threads on tiny VMs.
try:
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except Exception:
    pass
try:
    import cv2
    cv2.setNumThreads(1)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

import redis
from rq import Worker, Queue, Connection

# Pre-load models in the parent process to enable memory sharing (Copy-on-Write)
# with the child worker processes (work-horses).
try:
    from app1 import get_model_v7, get_model_v8
    logging.info("Pre-loading models in worker parent process...")
    get_model_v8()
    get_model_v7()
    logging.info("Models pre-loaded successfully.")
except Exception as e:
    logging.error(f"Failed to pre-load models: {e}")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUES = ["inference-tasks"]

if __name__ == "__main__":
    conn = redis.from_url(REDIS_URL)
    with Connection(conn):
        worker = Worker(QUEUES)
        # with_scheduler=False ensures we don't start the scheduler in every worker process
        worker.work(with_scheduler=False)
