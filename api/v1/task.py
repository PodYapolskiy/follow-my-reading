from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from .models import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    MultipleTasksStatusResponse,
    TaskResultsResponse,
)
from core import task_system
from core.task_system import scheduler
from core.plugins import AUDIO_PLUGINS, IMAGE_PLUGINS
from core.plugins.base import AudioProcessingFunction, ImageProcessingFunction
from huey.api import Result
from pathlib import Path

router = APIRouter(prefix="/task", tags=["task"])


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    image_plugin_info = IMAGE_PLUGINS.get(request.image_model)
    audio_plugin_info = AUDIO_PLUGINS.get(request.audio_model)
    files_dir = Path("./temp_data")
    image_file_path = files_dir / "image" / str(request.image_file)
    audio_file_path = files_dir / "audio" / str(request.audio_file)

    if image_plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image model available",
        )

    if audio_plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio model available",
        )

    if not image_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image file available",
        )

    if not audio_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio file available",
        )

    job: Result = task_system.compate_image_audio(
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        str(audio_file_path),
        image_plugin_info.class_name,
        ImageProcessingFunction,
        str(image_file_path),
    )
    return TaskCreateResponse(task_id=UUID(job.id))


@router.get("/status", response_model=TaskStatusResponse)
async def get_job_status(task_id: UUID):
    if scheduler.result(str(task_id), preserve=True) is None:
        return TaskStatusResponse(
            task_id=task_id, status="results are not available", ready=False
        )
    else:
        return TaskStatusResponse(task_id=task_id, status="finished", ready=True)


@router.get("/result", response_model=TaskResultsResponse)
async def get_result(task_id: UUID):
    data = scheduler.result(str(task_id), preserve=True)
    if data is not None:
        return TaskResultsResponse(data=data)
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Results are not ready yet or no task with such id exist",
        )
