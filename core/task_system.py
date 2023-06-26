from rq import Queue
from rq.worker import Worker
from typing import Dict
from uuid import UUID
from redis import Redis
from core.models import load_models
from functools import lru_cache


@lru_cache
def get_connection():
    return Redis()


@lru_cache
def get_queue():
    return Queue(connection=get_connection(), default_timeout=36000)


class PluginWorker(Worker):
    def __init__(self, *args, **kwargs):
        load_models()
        super().__init__(*args, **kwargs)
