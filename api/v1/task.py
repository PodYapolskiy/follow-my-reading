from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from huey.api import Result
from pydantic.error_wrappers import ValidationError

from config import get_config
from core import task_system
from core.plugins.base import AudioProcessingFunction, ImageProcessingFunction
from core.plugins.no_mem import get_audio_plugins, get_image_plugins
from core.task_system import scheduler

from .auth import get_current_active_user
from .models import (
    AudioProcessingRequest,
    ImageProcessingRequest,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskResultsResponse,
    TaskStatusResponse,
)

config = get_config()

router = APIRouter(
    prefix="/task", tags=["task"], dependencies=[Depends(get_current_active_user)]
)


async def create_audio_task(request: AudioProcessingRequest) -> TaskCreateResponse:
    audio_plugin_info = get_audio_plugins().get(request.audio_model)
    audio_file_path = config.storage.audio_dir / str(request.audio_file)

    if audio_plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio model available",
        )

    if not audio_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such audio file available"
        )

    job: Result = task_system.audio_processing_call(  # type: ignore
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
    )

    return TaskCreateResponse(task_id=UUID(job.id))


async def create_image_task(request: ImageProcessingRequest) -> TaskCreateResponse:
    image_plugin_info = get_image_plugins().get(request.image_model)
    image_file_path = config.storage.image_dir / str(request.image_file)

    if image_plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image model available",
        )

    if not image_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such image file available"
        )

    job: Result = task_system.image_processing_call(  # type: ignore
        image_plugin_info.class_name,
        ImageProcessingFunction,
        image_file_path.as_posix(),
    )

    return TaskCreateResponse(task_id=UUID(job.id))


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest) -> TaskCreateResponse:
    image_plugin_info = get_image_plugins().get(request.image_model)
    audio_plugin_info = get_audio_plugins().get(request.audio_model)

    image_file_path = config.storage.image_dir / str(request.image_file)
    audio_file_path = config.storage.audio_dir / str(request.audio_file)

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

    job: Result = task_system.compare_image_audio(  # type: ignore
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
        image_plugin_info.class_name,
        ImageProcessingFunction,
        image_file_path.as_posix(),
    )
    return TaskCreateResponse(task_id=UUID(job.id))


async def _get_job_status(task_id: UUID) -> TaskStatusResponse:
    if scheduler.result(str(task_id), preserve=True) is None:
        return TaskStatusResponse(
            task_id=task_id, status="results are not available", ready=False
        )
    else:
        return TaskStatusResponse(task_id=task_id, status="finished", ready=True)


@router.get("/status", response_model=TaskStatusResponse)
async def get_job_status(task_id: UUID) -> TaskStatusResponse:
    return await _get_job_status(task_id)


async def _get_job_result(task_id: UUID) -> Any:
    data = scheduler.result(str(task_id), preserve=True)
    if data is not None:
        return data
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Results are not ready yet or no task with such id exist",
        )


@router.get("/result", response_model=TaskResultsResponse)
async def get_job_result(task_id: UUID) -> TaskResultsResponse:
    data = scheduler.result(str(task_id), preserve=True)

    if data is not None:
        try:
            return TaskResultsResponse.parse_obj(data.dict())
        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="There is no such task consists of the both image and audio",
            ) from error
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Results are not ready yet or no task with such id exist",
    )
