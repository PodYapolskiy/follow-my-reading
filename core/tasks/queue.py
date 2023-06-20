from rq import Queue
from rq.job import Job
from typing import Dict
from uuid import UUID, uuid4
from redis import Redis

tasks: Dict[UUID, Job] = {}


def get_tasks():
    return tasks


task_queue = Queue(connection=Redis())


def put_in_queue(function, *args, **kwargs) -> UUID:
    task_uuid = uuid4()
    task = task_queue.enqueue(function, *args, **kwargs)
    tasks[task_uuid] = task

    return task_uuid
