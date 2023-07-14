from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from huey.api import Result

from config import get_config
from core import task_system
from core.plugins.base import AudioProcessingFunction, ImageProcessingFunction
from core.plugins.no_mem import get_audio_plugins, get_image_plugins
from core.task_system import scheduler

from .models import (
    AudioProcessingRequest,
    ImageProcessingRequest,
    TaskCreateResponse,
    TaskStatusResponse,
)

config = get_config()


def create_audio_task(request: AudioProcessingRequest) -> TaskCreateResponse:
    """
    The function `create_audio_task` creates a task for audio processing based on the provided audio
    model and file.

    :param request: An instance of the AudioProcessingRequest class, which contains information about
    the audio model and audio file to be processed
    :type request: AudioProcessingRequest
    :return: a TaskCreateResponse object with a task_id attribute set to the UUID of the job.
    """
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


def create_image_task(request: ImageProcessingRequest) -> TaskCreateResponse:
    """
    The function `create_image_task` creates a task for image processing based on the provided image
    model and file.

    :param request: An instance of the ImageProcessingRequest class, which contains information about
    the image model and image file to be processed
    :type request: ImageProcessingRequest
    :return: a TaskCreateResponse object with a task_id attribute set to the UUID of the job.
    """
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


def _get_job_status(task_id: UUID) -> TaskStatusResponse:
    """
    The function `_get_job_status` checks the status of a task and returns a response indicating whether
    the task has finished and if the results are available.

    :param task_id: The task_id parameter is of type UUID, which stands for Universally Unique
    Identifier. It is a unique identifier that is used to identify a specific task
    :type task_id: UUID
    :return: a TaskStatusResponse object.
    """
    if scheduler.result(str(task_id), preserve=True) is None:
        return TaskStatusResponse(
            task_id=task_id, status="results are not available", ready=False
        )
    else:
        return TaskStatusResponse(task_id=task_id, status="finished", ready=True)


def _get_job_result(task_id: UUID) -> Any:
    """
    The function `_get_job_result` retrieves the result of a job based on its ID, and raises an
    exception if the result is not ready or the task does not exist.

    :param task_id: The `task_id` parameter is of type `UUID` and represents the unique identifier of a
    task
    :type task_id: UUID
    :return: The function `_get_job_result` returns the result of a job/task with the given `task_id`.
    The result are of type `dict`.
    """
    data = scheduler.result(str(task_id), preserve=True)
    if data is not None:
        return data
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Results are not ready yet or no task with such id exist",
        )
