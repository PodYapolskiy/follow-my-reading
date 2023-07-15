from io import BytesIO
from uuid import UUID, uuid4

import pydub
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic.error_wrappers import ValidationError
from loguru import logger

from config import get_config
from core.plugins.no_mem import get_audio_plugins

from .auth import get_current_active_user
from .models import (
    AudioProcessingRequest,
    AudioProcessingResponse,
    ModelData,
    ModelsDataResponse,
    TaskCreateResponse,
    UploadFileResponse,
)
from .task_utils import _get_job_result, _get_job_status, create_audio_task

logger.add("./logs/audio.log", format="{time:DD-MM-YYYY HH:mm:ss zz} {level} {message}", enqueue=True)
config = get_config()
router = APIRouter(
    prefix="/audio", tags=["audio"], dependencies=[Depends(get_current_active_user)]
)


@router.post(
    "/upload",
    response_model=UploadFileResponse,
    status_code=200,
    summary="""The endpoint /upload allows clients to upload audio files and returns a unique file ID.""",
    responses={
        200: {"description": "The file is uploaded successfully"},
        422: {
            "description": "The file was not sent or the file has prohibited extension",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Only audio files uploads are allowed",
                    }
                }
            },
        },
    },
)
async def upload_audio_file(upload_file: UploadFile) -> UploadFileResponse:
    """
    The endpoint validates file based on
    [MIME types specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types).
    The endpoint converts audio file into .mp3 format.

    Parameters:
    - **upload_file**: The file to upload

    Allowed extension:
    - .acc
    - .mid, .midi
    - .mp3
    - .oga, .ogv
    - .opus
    - .wav
    - .weba"""
    logger.info("Starting upload_audio_file algorithm. Acquiring data.")
    file_id = uuid4()

    # Here we are using MIME types specification, which have format
    # "kind/name". In the following code, we are checking that the kind of document
    # is "audio". It is the easiest methods to allow uploading any audio format files.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types

    logger.info(f"Checking if audio file (id: {file_id}) is of allowed format.")
    if (
        upload_file.content_type is None
        or upload_file.content_type.split("/")[0] != "audio"
    ):
        logger.error(f"File (id: {file_id}) is of not allowed format. "
                     f"Raising 422 file error")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only audio files uploads are allowed",
        )

    logger.info(f"Audio file (id: {file_id}) is valid. Reading and storing it.")
    byte_content = await upload_file.read()
    filepath = config.storage.audio_dir / str(file_id)

    # convert file to mp3
    logger.info(f"Converting audio file (id: {file_id}) to .mp3 extension and saving it to ({filepath})")
    pydub.AudioSegment.from_file(BytesIO(byte_content)).export(
        out_f=filepath, format="mp3"
    )

    logger.info(f"Audio file ({file_id}) was saved successfully.")
    return UploadFileResponse(file_id=file_id)


@router.get(
    "/models",
    response_model=ModelsDataResponse,
    status_code=200,
    summary="""The endpoint /models returns available (loaded) audio models.""",
    responses={
        200: {"description": "List of available models"},
    },
)
async def get_audio_processing_models() -> ModelsDataResponse:
    """
    Returns list of models, which are loaded into the worker and available for usage.
    """
    logger.info("Starting get_audio_processing_models algorithm. Acquiring models.\n"
                "For more info check core/plugins/logs/no_mem.log\n"
                "Process: get_audio_plugins")
    # Transform any known audio model into ModelData object format and
    # store them as a list inside ModelsDataResponse
    return ModelsDataResponse(
        models=[ModelData.from_orm(model) for model in get_audio_plugins().values()]
    )


@router.post(
    "/process",
    response_model=TaskCreateResponse,
    status_code=200,
    summary="""The endpoint `/process` creates an audio processing task based on the given request parameters.""",
    responses={
        200: {"description": "Task was successfully created and scheduled"},
        404: {
            "description": "The specified file or model was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No such audio file available",
                    }
                }
            },
        },
    },
)
async def process_audio(request: AudioProcessingRequest) -> TaskCreateResponse:
    """
    Parameters:
    - **audio_file**: an uuid of file to process
    - **audio_model**: an audio processing model name (check '_/models_' for available models)

    Responses:
    - 404, No such audio file available
    - 404, No such audio model available
    """
    logger.info("Starting process_audio algorithm. Creating task for processing audio.\n"
                "For more info check api/v1/logs/task_utils.log\n"
                "Process: create_audio_task")
    created_task: TaskCreateResponse = create_audio_task(request)

    logger.info(f"Task created successfully. Returning task instance (id: {created_task.task_id})")
    return created_task


@router.get(
    "/download",
    response_class=FileResponse,
    status_code=200,
    summary="""The endpoint `/download` allows to download audio file by given uuid.""",
    responses={
        404: {
            "description": "The specified file was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File not found",
                    }
                }
            },
        },
    },
)
async def download_audio_file(file: UUID) -> FileResponse:
    """
    The endpoint `/download` takes a file UUID as input, checks if the file exists in the
    audio directory, and returns the file as bytes. If file does not exist, returns 404 HTTP response code

    Responses:
    - 200, file bytes
    """
    logger.info(f"Starting download_audio_file algorithm. Searching for audio file ({str(file)}).")
    filepath = config.storage.audio_dir / str(file)

    if not filepath.exists():
        logger.error(f"File ({file}) does not exist. Returning 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    logger.info(f"Audio file ({file}) was found. Returning file response.")
    return FileResponse(path=filepath.as_posix(), media_type="audio/mpeg")


@router.get(
    "/result",
    response_model=AudioProcessingResponse,
    status_code=200,
    summary="""The endpoint `/result` retrieves the result of an audio
processing task from task system and returns it.""",
    responses={
        406: {
            "description": "It is impossible to get task result (task does not exist or it has not finished yet).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The job is non-existent or not done",
                    }
                }
            },
        },
        422: {
            "description": "The specified task is not audio processing task.",
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
async def get_response(task_id: UUID) -> AudioProcessingResponse:
    """
    Responses:
    - 200, returns a processing result in the format:
    ```js
    {
        "text": "string", // total extracted text
        "segments": [ // list of audio segments
            {
            "start": 0.0, // absolute timecode (in seconds) of the beginning of the segment
            "end": 10.0,  // absolute timecode (in seconds) of the beginning of the segment
            "text": "string", // text, which was extracted from the segment
            "file": "3fa85f64-5717-4562-b3fc-2c963f66afa6" // file uuid of the audio segment (for downloading)
            }
        ]
    }
    ```
    - 406, is impossible to get task result (task does not exist, or it has not finished yet).
    - 422, if the task was not created as audio processing task
    """

    logger.info("Starting get_response algorithm. Acquiring data.")
    response = _get_job_status(task_id)

    logger.info(f"Checking if task ({task_id}) exists and if it is finished.")
    if not response.ready:
        logger.error(f"The task ({task_id}) does not exist or is not finished yet.")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The job is non-existent or not done",
        )

    logger.info(f"The task ({task_id}) exists and is finished. Acquiring results.")
    data = _get_job_result(task_id)
    try:
        logger.info(f"Trying to return the results of the task ({task_id}).")
        return AudioProcessingResponse.parse_obj(data.dict())
    except ValidationError as error:
        logger.error(f"Wrong type of task was passed. Raising 422 error.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="There is no such audio processing task",
        ) from error
