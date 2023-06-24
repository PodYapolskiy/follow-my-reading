from rq import Queue
from rq.job import Job
from typing import Dict
from uuid import UUID, uuid4
from redis import Redis
from .worker import ModelsWorker

tasks: Dict[UUID, Job] = {}


def get_tasks():
    return tasks


task_queue = Queue(connection=Redis())


def put_in_queue(function, *args, **kwargs) -> UUID:
    task = task_queue.enqueue(function, *args, **kwargs)
    task_id = UUID(task.get_id())
    tasks[task_id] = task

    return task_id


def terminate(uuid: UUID):
    tasks.get(uuid).cancel()
