from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from .models import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    MultipleTasksStatusResponse,
)
from core import task_system, processing
from rq.job import Job
from rq.exceptions import NoSuchJobError
from rq.registry import (
    StartedJobRegistry,
    FailedJobRegistry,
    ScheduledJobRegistry,
    FinishedJobRegistry,
)


router = APIRouter(prefix="/task", tags=["task"])


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    job = task_system.get_queue().enqueue(
        processing.task.find_difference,
        request.audio_model,
        request.image_model,
        str(request.audio_file),
        str(request.image_file),
    )
    return TaskCreateResponse(task_id=UUID(job.get_id()))


@router.get("/status", response_model=TaskStatusResponse)
async def get_status(task_id: UUID):
    try:
        job = Job.fetch(id=str(task_id), connection=task_system.get_connection())

        return TaskStatusResponse(
            task_id=task_id, status=job.get_status(), ready=job.is_finished
        )
    except NoSuchJobError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such job exist"
        )


@router.get("/started")
async def get_started_tasks():
    jobs = StartedJobRegistry(queue=task_system.get_queue()).get_job_ids()
    data = []
    for job_id in jobs:
        job = Job.fetch(id=job_id, connection=task_system.get_connection())
        data.append(
            TaskStatusResponse(
                task_id=UUID(job.get_id()),
                status=job.get_status(),
                ready=job.is_finished,
            )
        )

    return MultipleTasksStatusResponse(data=data)


@router.get("/failed")
async def get_failed_tasks():
    jobs = FailedJobRegistry(queue=task_system.get_queue()).get_job_ids()
    data = []
    for job_id in jobs:
        job = Job.fetch(id=job_id, connection=task_system.get_connection())
        data.append(
            TaskStatusResponse(
                task_id=UUID(job.get_id()),
                status=job.get_status(),
                ready=job.is_finished,
            )
        )

    return MultipleTasksStatusResponse(data=data)


@router.get("/scheduled")
async def get_scheduled_tasks():
    jobs = ScheduledJobRegistry(queue=task_system.get_queue()).get_job_ids()
    data = []
    for job_id in jobs:
        job = Job.fetch(id=job_id, connection=task_system.get_connection())
        data.append(
            TaskStatusResponse(
                task_id=UUID(job.get_id()),
                status=job.get_status(),
                ready=job.is_finished,
            )
        )

    return MultipleTasksStatusResponse(data=data)


@router.get("/finished")
async def get_finished_tasks():
    jobs = FinishedJobRegistry(queue=task_system.get_queue()).get_job_ids()
    data = []
    for job_id in jobs:
        job = Job.fetch(id=job_id, connection=task_system.get_connection())
        data.append(
            TaskStatusResponse(
                task_id=UUID(job.get_id()),
                status=job.get_status(),
                ready=job.is_finished,
            )
        )
