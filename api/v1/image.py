from io import BytesIO
from uuid import UUID, uuid4
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from PIL import Image
from pydantic.error_wrappers import ValidationError

from config import get_config
from core.plugins.no_mem import get_image_plugins

from .auth import get_current_active_user
from .models import (
    ImageProcessingRequest,
    ImageProcessingResponse,
    ModelData,
    ModelsDataResponse,
    TaskCreateResponse,
    UploadFileResponse,
)
from .task_utils import _get_job_result, _get_job_status, create_image_task

logger.add(
    "./logs/image.log",
    format="{time:DD-MM-YYYY HH:mm:ss zz} {level} {message}",
    enqueue=True,
)
config = get_config()

router = APIRouter(
    prefix="/image", tags=["image"], dependencies=[Depends(get_current_active_user)]
)


@router.post(
    "/upload",
    response_model=UploadFileResponse,
    status_code=200,
    summary="""The endpoint /upload allows clients to upload image files and returns a unique file ID.""",
    responses={
        200: {"description": "The file is uploaded successfully"},
        422: {
            "description": "The file was not sent or the file has prohibited extension",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Only image files uploads are allowed",
                    }
                }
            },
        },
    },
)
async def upload_image(upload_file: UploadFile) -> UploadFileResponse:
    """
    The endpoint validates file based on
    [MIME types specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types).
    The endpoint converts image file into .png format.

    Parameters:
    - **upload_file**: The file to upload

    Allowed extension:
    - .avif
    - .bmp
    - .gif
    - .ico
    - .jpeg, .jpg
    - .png
    - .svg
    - .tif, .tiff
    - .webp
    """
    logger.info("Starting upload_image algorithm. Acquiring data.")
    file_id = uuid4()

    # Here we are using MIME types specification, which have format
    # "kind/name". In the following code, we are checking that the kind of document
    # is "image". It is the easiest methods to allow uploading any image format files.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    logger.info(f"Checking if file ({file_id}) is of allowed format.")
    if (
        upload_file.content_type is None
        or upload_file.content_type.split("/")[0] != "image"
    ):
        logger.error(
            f"The file ({file_id}) is of not allowed format. Raising 422 file error."
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only image files uploads are allowed",
        )

    logger.info(
        f"File ({file_id}) is of allowed format. Converting to png and saving to "
        f"{config.storage.image_dir / str(file_id)}."
    )
    # convert import into png
    byte_content = await upload_file.read()
    Image.open(BytesIO(byte_content)).save(
        config.storage.image_dir / str(file_id), format="png"
    )

    logger.info(
        f"The file ({file_id}) has been uploaded successfully.\n"
        f"Filepath: {config.storage.image_dir / str(file_id)}"
    )
    return UploadFileResponse(file_id=file_id)


@router.get(
    "/download",
    response_class=FileResponse,
    status_code=200,
    summary="""The endpoint `/download` allows to download image file by given uuid.""",
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
async def download_image_file(file: UUID) -> FileResponse:
    """
    The endpoint `/download` takes a file UUID as input, checks if the file exists in the
    image directory, and returns the file as bytes. If file does not exist, returns 404 HTTP response code

    Responses:
    - 200, file bytes
    """
    logger.info("Starting download_image_file algorithm. Acquiring data.")
    filepath = config.storage.image_dir / str(file)

    logger.info(f"Searching for image ({str(file)})")
    if not filepath.exists():
        logger.error(f"File ({str(file)}) does not exist. Raising 404 file error.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    logger.info(f"File ({str(file)}) was found. Returning file response.")
    return FileResponse(path=filepath.as_posix(), media_type="image/png")


@router.get(
    "/models",
    response_model=ModelsDataResponse,
    status_code=200,
    summary="""The endpoint /models returns available (loaded) image models.""",
    responses={
        200: {"description": "List of available models"},
    },
)
async def get_models() -> ModelsDataResponse:
    """
    Returns list of models, which are loaded into the worker and available for usage.
    """
    logger.info("Starting get_models algorithm. Acquiring image models.")
    # Transform any known image model into ModelData object format and
    # store them as a list inside ModelsDataResponse
    return ModelsDataResponse(
        models=[ModelData.from_orm(model) for model in get_image_plugins().values()]
    )


@router.post(
    "/process/task",
    response_model=TaskCreateResponse,
    status_code=200,
    summary="""The endpoint `/process` creates an image processing task based on the given request parameters.""",
    responses={
        200: {"description": "Task was successfully created and scheduled"},
        404: {
            "description": "The specified file or model was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No such image file available",
                    }
                }
            },
        },
    },
)
async def process_image(request: ImageProcessingRequest) -> TaskCreateResponse:
    """
    Parameters:
    - **image_file**: an uuid of file to process
    - **image_model**: an image processing model name (check '_/models_' for available models)

    Responses:
    - 404, No such image file available
    - 404, No such image model available
    """
    logger.info("Starting process_image algorithm. Creating task for image processing.")
    created_task: TaskCreateResponse = create_image_task(request)
    logger.info(f"Task ({created_task.task_id}) has been created successfully.")
    return created_task


@router.get(
    "/process/result",
    response_model=ImageProcessingResponse,
    status_code=200,
    summary="""The endpoint `/process/result` retrieves the result of an image
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
            "description": "The specified task is not image processing task.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "There is no such image processing task",
                    }
                }
            },
        },
    },
)
async def get_response(task_id: UUID) -> ImageProcessingResponse:
    """
    Responses:
    - 200, returns a processing result in the format:
    ```js
    {
        "text": "string", // total extracted text
        "boxes": [ // list of boxes with text
            {
            "text": "string", // text, which was extracted from the box
            "coordinates": { // coordinates of the box on image
                "left_top": { // four points defining the rectangle
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
    }
    ```
    - 406, is impossible to get task result (task does not exist, or it has not finished yet).
    - 422, if the task was not created as audio processing task
    """
    logger.info("Starting get_response algorithm. Acquiring data.")
    response = _get_job_status(task_id)

    logger.info(f"Checking if task ({task_id}) exists and if it is finished.")
    if not response.ready:
        logger.error(
            f"The task ({task_id}) is non-existent or not finished. Raising 406 error."
        )
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The job is non-existent or not done",
        )

    logger.info(f"The task ({task_id}) is finished. Acquiring results")
    job_results = _get_job_result(task_id)

    try:
        logger.info(f"Trying to return the results of the task ({task_id}).")
        return ImageProcessingResponse.parse_obj(job_results.dict())
    except ValidationError as error:
        logger.error("Wrong type of task was passed. Raising 422 file error.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="There is no such image processing task",
        ) from error
