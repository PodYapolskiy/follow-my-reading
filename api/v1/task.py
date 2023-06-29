from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from huey.api import Result

from core import task_system
from core.plugins.base import AudioProcessingFunction, ImageProcessingFunction
from core.plugins.no_mem import get_audio_plugins, get_image_plugins
from core.task_system import scheduler

from .auth import get_current_active_user
from .models import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskResultsResponse,
    TaskStatusResponse,
    AudioProcessingRequest,
    ImageProcessingRequest
)

router = APIRouter(
    prefix="/task", tags=["task"], dependencies=[Depends(get_current_active_user)]
)


async def create_audio_task(request: AudioProcessingRequest):
    audio_plugin_info = get_audio_plugins().get(request.audio_model)
    files_dir = Path("./temp_data")
    audio_file_path = files_dir / "audio" / str(request.audio_file)

    if audio_plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio model available"
        )

    if not audio_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio file available"
        )

    job: Result = task_system.audio_processing_call(
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        str(audio_file_path)
    )

    return TaskCreateResponse(task_id=UUID(job.id))


async def create_image_task(request: ImageProcessingRequest):
    image_plugin_info = get_image_plugins().get(request.image_model)
    files_dir = Path("./temp_data")
    image_file_path = files_dir / "audio" / str(request.image_file)

    if image_plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image model available"
        )

    if not image_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image file available"
        )

    job: Result = task_system.audio_processing_call(
        image_plugin_info.class_name,
        ImageProcessingFunction,
        str(image_file_path)
    )

    return TaskCreateResponse(task_id=UUID(job.id))


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    image_plugin_info = get_image_plugins().get(request.image_model)
    audio_plugin_info = get_audio_plugins().get(request.audio_model)
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

    job: Result = task_system.compare_image_audio(
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        str(audio_file_path),
        image_plugin_info.class_name,
        ImageProcessingFunction,
        str(image_file_path),
    )
    return TaskCreateResponse(task_id=UUID(job.id))


async def get_job_status(task_id: UUID):
    if scheduler.result(str(task_id), preserve=True) is None:
        return TaskStatusResponse(
            task_id=task_id, status="results are not available", ready=False
        )
    else:
        return TaskStatusResponse(task_id=task_id, status="finished", ready=True)


@router.get("/status", response_model=TaskStatusResponse)
async def get_user_job_status(task_id: UUID):
    return await get_job_status(task_id)


async def get_result(task_id: UUID):
    data = scheduler.result(str(task_id), preserve=True)
    if data is not None:
        return TaskResultsResponse(data=data)
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Results are not ready yet or no task with such id exist",
        )


@router.get("/result", response_model=TaskResultsResponse)
async def get_user_result(task_id: UUID):
    return await get_result(task_id)
