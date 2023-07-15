from typing import Any
from uuid import UUID
from loguru import logger
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

logger.add("./logs/task_utils.log", format="{time:DD-MM-YYYY, HH:mm:ss zz} {level} {message}", enqueue=True)
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
    logger.info("Starting create_audio_task algorithm. Acquiring data.")

    audio_plugin_info = get_audio_plugins().get(request.audio_model)
    audio_file_path = config.storage.audio_dir / str(request.audio_file)

    logger.info(f"Checking if audio model ({request.audio_model}) exists.")

    if audio_plugin_info is None:
        logger.error(f"No such audio model ({request.audio_model}) exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio model available",
        )

    logger.info(f"Audio model ({request.audio_model}) exists. Checking if audio file ({request.audio_file}) exists.")

    if not audio_file_path.exists():
        logger.error(f"No such audio file ({request.audio_file}) exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such audio file available"
        )

    logger.info(f"Audio file ({request.audio_file}) exists. Creating task for audio processing.\n"
                f"Check core/logs/task_system.log for more info.\n"
                f"Process: audio_processing_call.")

    job: Result = task_system.audio_processing_call(  # type: ignore
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
    )

    logger.info(f"Task for processing audio (file: ({request.audio_file}), model: ({request.audio_model}))\n"
                f"has been created successfully."
                f"Task id: {UUID(job.id)}")
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
    logger.info("Starting create_image_task algorithm. Acquiring data.")

    image_plugin_info = get_image_plugins().get(request.image_model)
    image_file_path = config.storage.image_dir / str(request.image_file)

    logger.info(f"Checking if image model ({request.image_model}) exists.")
    if image_plugin_info is None:
        logger.error(f"No such image model ({request.image_model}) exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image model available",
        )

    logger.info(f"Image model ({request.image_model}) exists. Checking if image file ({request.image_file}) exists.")
    if not image_file_path.exists():
        logger.error(f"No such image file ({request.image_file}) exists.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such image file available"
        )

    logger.info(f"Image file ({request.image_file}) exists. Creating task for image processing.\n"
                f"Check core/logs/task_system.log for more info.\n"
                f"Process: image_processing_call")
    job: Result = task_system.image_processing_call(  # type: ignore
        image_plugin_info.class_name,
        ImageProcessingFunction,
        image_file_path.as_posix(),
    )

    logger.info(f"Task for processing image (file: ({request.image_file}), model: ({request.image_model}))\n"
                f"has been created successfully."
                f"Task id: {UUID(job.id)}")
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
    logger.info(f"Starting _get_job_status algorithm. Checking if the results of the task ({task_id}) are available yet.")
    if scheduler.result(str(task_id), preserve=True) is None:
        logger.info(f"Results of the task ({task_id}) are not available")
        return TaskStatusResponse(
            task_id=task_id, status="results are not available", ready=False
        )
    else:
        logger.info(f"The task ({task_id}) is already finished.")
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
    logger.info(f"Starting _get_job_result algorithm. Acquiring results of task ({task_id}).")
    data = scheduler.result(str(task_id), preserve=True)
    if data is not None:
        logger.info(f"The task ({task_id}) exists and is finished. Returning the result.")
        return data
    else:
        logger.error(f"The task ({task_id}) does not exist or its results are not ready yet. Raising 406 file error.")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Results are not ready yet or no task with such id exist",
        )
