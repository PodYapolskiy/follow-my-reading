from uuid import UUID
from loguru import logger
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
    AudioToImageComparisonRequest,
    AudioToTextComparisonRequest,
    TaskCreateResponse,
    TaskResultsResponse,
    TaskStatusResponse,
)
from .task_utils import _get_job_status

config = get_config()
logger.add("./logs/task.log", format="{time:DD-MM-YYYY HH:mm:ss zz} {level} {message}", enqueue=True)
router = APIRouter(
    prefix="/task", tags=["task"], dependencies=[Depends(get_current_active_user)]
)


@router.post(
    "/comparison/image",
    response_model=TaskCreateResponse,
    status_code=200,
    summary="""The endpoint `/comparison/image` creates a task to compare an image and audio file using specified
    models and returns the task ID.""",
    responses={
        200: {"description": "Task was successfully created and scheduled"},
        404: {
            "description": "The specified file or model was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No such image model available",
                    }
                }
            },
        },
    },
)
async def compare_image_and_audio(request: AudioToImageComparisonRequest) -> TaskCreateResponse:
    """
    Parameters:
    - **audio_file**: an uuid of file to process
    - **audio_model**: an audio processing model name (check '_/audio/models_' for available models)
    - **image_file**: an uuid of file to process
    - **image_model**: an image processing model name (check '_/image/models_' for available models)


    Responses:
    - 200, Task created
    - 404, No such audio file available
    - 404, No such audio model available
    - 404, No such image file available
    - 404, No such image model available
    """
    logger.info("Starting compare_image_audio algorithm. Acquiring data.")

    image_plugin_info = get_image_plugins().get(request.image_model)
    audio_plugin_info = get_audio_plugins().get(request.audio_model)

    image_file_path = config.storage.image_dir / str(request.image_file)
    audio_file_path = config.storage.audio_dir / str(request.audio_file)

    logger.info(f"Checking if image model ({request.image_model}) exists.")
    if image_plugin_info is None:
        logger.error(f"No such image model ({request.image_model} exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image model available",
        )

    logger.info(f"Image model ({request.image_model}) exists. Checking if audio model ({request.audio_model}) exists.")
    if audio_plugin_info is None:
        logger.error(f"No such audio model ({request.image_model}) exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio model available",
        )

    logger.info(f"Audio model ({request.audio_model}) exists. Checking if image file ({request.image_file}) exists.")
    if not image_file_path.exists():
        logger.error(f"No such image file ({request.image_file}) exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such image file available",
        )

    logger.info(f"Image file ({request.image_file}) exists. Checking if audio file ({request.audio_file}) exists.")
    if not audio_file_path.exists():
        logger.error("non-existent audiofile passed at line 93.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio file available",
        )

    logger.info(f"Audio file ({request.audio_file}) exists. Creating task for comparison of image and audio.\n"
                f"Check core/processing/logs/task_system.log for more info.\n"
                f"Process: compare_image_audio")
    job: Result = task_system.compare_image_audio(  # type: ignore
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
        image_plugin_info.class_name,
        ImageProcessingFunction,
        image_file_path.as_posix(),
    )

    logger.info(f"Task for comparing image (file: {image_file_path}, model: {request.image_model}))\n"
                f"and audio (file: {audio_file_path}, model: {request.audio_model}))\n"
                f"has been created successfully.\n"
                f"Task id: {UUID(job.id)}")
    return TaskCreateResponse(task_id=UUID(job.id))


@router.post(
    "/comparison/text",
    response_model=TaskCreateResponse,
    summary="""The endpoint '/comparison/text' creates a task to compare text from user input 
    and audio file using specified models and returns the task ID.""",
    responses={
        200: {"description": "Task was successfully created and scheduled"},
        404: {
            "description": "The specified file or model was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No such audio model available",
                    }
                }
            },
        },
    },
)
async def compare_text_and_audio(request: AudioToTextComparisonRequest) -> TaskCreateResponse:
    """
    Parameters:
    - **audio_file**: an uuid of file to process
    - **audio_model**: an audio processing model name (check '_/audio/models_' for available models)


    Responses:
    - 200, Task created
    - 404, No such audio file available
    - 404, No such audio model available
    - 404, No such image file available
    - 404, No such image model available
    """
    logger.info("Starting compare_text_audio algorithm. Acquiring data.")

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
        logger.error(f"No such audio file ({request.audio_file} exists. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio file available",
        )

    logger.info(f"Audio file ({request.audio_file} exists. Creating task of comparison text and audio.\n"
                f"Check core/processing/logs/task_system.log for more info.\n"
                f"Process: compare_text_audio.")
    job: Result = task_system.compare_text_audio(
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
        request.text
    )

    logger.info(f"Task for comparing text ({request.text})\n"
                f"and audio (file: ({request.audio_file}), model: ({request.audio_model}))\n"
                f"has been created successfully.\n"
                f"Task id: ({UUID(job.id)})")
    return TaskCreateResponse(task_id=UUID(job.id))


@router.get(
    "/status",
    response_model=TaskStatusResponse,
    status_code=200,
    summary="""The endpoint `status` returns the status of a task identified by its `task_id`.""",
)
async def get_job_status(task_id: UUID) -> TaskStatusResponse:
    """
    Parameters:
    - **task_id**: The `task_id` is the uuid of the task to fetch status of

    Responses:
    - 200, Job status
    """
    logger.info(f"Starting get_job status algorithm. Getting status of task ({task_id}).\n"
                f"For more info see in api/v1/logs task_utils logs for more info.\n"
                f"Process: _get_job_status")
    return _get_job_status(task_id)


@router.get(
    "/result",
    response_model=TaskResultsResponse,
    status_code=200,
    summary="""The endpoint `/result` retrieves the results of a task with a given task ID, and returns the
    results.""",
    responses={
        406: {
            "description": "It is impossible to get task result (task does not exist or it has not finished yet).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Results are not ready yet or no task with such id exist",
                    }
                }
            },
        },
        422: {
            "description": "There is no such task consists of the both image and audio.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "There is no such audio processing task",
                    }
                }
            },
        },
    },
)
async def get_job_result(task_id: UUID) -> TaskResultsResponse:
    """
    Parameters:
    - **task_id**: The `task_id` is the uuid of the task to fetch results of

    Responses:
    - 200, job results in the format
    ```js
    {
    "image": { // image processing result
        "text": "string", // total extracted text
        "boxes": [ // list of boxes with text
        {
            "text": "string", // text extracted from the box
            "coordinates": { // coordinates of the box on the image
            "left_top": { // four points defining a rectangle
                "x": 0,
                "y": 0
            },
            "right_top": {
                "x": 0,
                "y": 0
            },
            "left_bottom": {
                "x": 0,
                "y": 0
            },
            "right_bottom": {
                "x": 0,
                "y": 0
            }
            }
        }
        ]
    },
    "audio": { // audio processing results
        "text": "string", // total extracted text
        "segments": [ // audio segments, that were processed
        {
            "start": 0, // absolute time code of the beginning of the segment
            "end": 0, // absolute time code of the ending of the segment
            "text": "string", // text extracted from the segment
            "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6" // audio segment
        }
        ]
    },
    "errors": [ // results of comparing
        {
        "audio_segment": { // audio segment where error was made
            "start": 0,
            "end": 0,
            "text": "string",
            "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        },
        "at_char": 0, // chat, at which an error stats
        "found": "string", // found word (based on audio)
        "expected": "string" // expected word (suggestion for improvement based on image)
        }
    ]
    }
    ```
    - 406, Results are not ready yet or no task with such id exist
    - 422, File of wrong type was passed
    """
    logger.info(f"Starting get_job_result algorithm. Acquiring data of task ({task_id}).")

    data = scheduler.result(str(task_id), preserve=True)

    logger.info("Checking if data acquired exists.")
    if data is not None:
        try:
            logger.info(f"Parsing data acquired to the appropriate form and returning "
                        f"the result of the task ({task_id})")
            return TaskResultsResponse.parse_obj(data.dict())
        except ValidationError as error:
            logger.error(f"Task data is not in the requested format. Requested format: (name_of_the_model), "
                         f"Data: {data.dict()}. Raising 422 file error.")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File object of wrong type was passed",
            ) from error

    logger.error(f"Results of the task ({task_id}) are not ready yet, or the task is non-existent.\n"
                 f"Raising 406 file error.")

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Results are not ready yet or no task with such id exist",
    )
