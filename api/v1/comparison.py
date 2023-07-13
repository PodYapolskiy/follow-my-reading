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
    AudioToImageComparisonRequest,
    AudioToTextComparisonRequest,
    TaskCreateResponse,
    AudioImageComparisonResultsResponse,
    AudioTextComparisonResultsResponse,
)

config = get_config()

router = APIRouter(
    prefix="/comparison",
    tags=["comparison"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post(
    "/audio/image",
    response_model=TaskCreateResponse,
    status_code=200,
    summary="""The endpoint `/audio/image` creates a task to compare an audio against image file using specified
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
async def compare_audio_to_image(
    request: AudioToImageComparisonRequest,
) -> TaskCreateResponse:
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

    job: Result = task_system.compare_audio_image(  # type: ignore
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
        image_plugin_info.class_name,
        ImageProcessingFunction,
        image_file_path.as_posix(),
    )
    return TaskCreateResponse(task_id=UUID(job.id))


@router.post(
    "/audio/text",
    response_model=TaskCreateResponse,
    summary="""The endpoint '/audio/text' creates a task to compare audio against text from user input 
    using specified models and returns the task ID.""",
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
async def compare_audio_to_text(
    request: AudioToTextComparisonRequest,
) -> TaskCreateResponse:
    """
    Parameters:
    - **audio_file**: an uuid of file to process
    - **audio_model**: an audio processing model name (check '_/audio/models_' for available models)
    - **text**: a list of strings to compare audio against


    Responses:
    - 200, Task created
    - 404, No such audio file available
    - 404, No such audio model available
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such audio file available",
        )

    job: Result = task_system.compare_audio_text(  # type: ignore
        audio_plugin_info.class_name,
        AudioProcessingFunction,
        audio_file_path.as_posix(),
        request.text,
    )
    return TaskCreateResponse(task_id=UUID(job.id))


@router.get(
    "/audio/image/result",
    response_model=AudioImageComparisonResultsResponse,
    status_code=200,
    summary="""The endpoint `/audio/image/result` retrieves the results of a task with a given task ID, and returns the
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
                        "detail": "There is no such task consists of the both image and audio",
                    }
                }
            },
        },
    },
)
async def get_audio_image_comparison_result(
    task_id: UUID,
) -> AudioImageComparisonResultsResponse:
    """
    Parameters:
    - **task_id**: The `task_id` is the uuid of the task to fetch results of

    Responses:
    - 200, job results in the format
    ```js
    {
    "image": { // image proccessing result
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
        "expected": "string" // exptected word (suggetion for improvement based on image)
        }
    ]
    }
    ```
    - 406, Results are not ready yet or no task with such id exist
    - 422, There is no such audio processing task
    """
    data = scheduler.result(str(task_id), preserve=True)

    if data is not None:
        try:
            return AudioImageComparisonResultsResponse.parse_obj(data.dict())
        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="There is no such task consists of the both image and audio",
            ) from error
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Results are not ready yet or no task with such id exist",
    )


@router.get(
    "/audio/text/result",
    response_model=AudioTextComparisonResultsResponse,
    status_code=200,
    summary="""The endpoint `/audio/text/result` retrieves the results of a task with a given task ID, and returns the
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
            "description": "There is no such task consists of the both audio and text.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "There is no such task consists of the both audio and text",
                    }
                }
            },
        },
    },
)
async def get_audio_text_comparison_result(
    task_id: UUID,
) -> AudioTextComparisonResultsResponse:
    """
    Parameters:
    - **task_id**: The `task_id` is the uuid of the task to fetch results of

    Responses:
    - 200, job results in the format
    ```js
    {
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
        "expected": "string" // exptected word (suggetion for improvement based on image)
        }
    ]
    }
    ```
    - 406, Results are not ready yet or no task with such id exist
    - 422, There is no such audio processing task
    """
    data = scheduler.result(str(task_id), preserve=True)

    if data is not None:
        try:
            return AudioTextComparisonResultsResponse.parse_obj(data.dict())
        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="There is no such task consists of the both image and audio",
            ) from error
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Results are not ready yet or no task with such id exist",
    )
