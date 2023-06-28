import asyncio
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends
from huey.api import Result

from core import task_system
from core.plugins.no_mem import get_image_plugins
from core.plugins.base import ImageProcessingFunction

from .models import (
    ImageProcessingRequest,
    ImageProcessingResponse,
    ModelData,
    ModelsDataReponse,
    UploadFileResponse,
)

from .auth import get_current_active_user

router = APIRouter(prefix="/image", tags=["image"], dependencies=[Depends(get_current_active_user)])


@router.post("/upload", response_model=UploadFileResponse)
async def upload_image(upload_file: UploadFile) -> UploadFileResponse:
    file_id = uuid4()

    # Here we using MIME types specification, which have format
    # "kind/name". In the following code, we checking that the kind of document
    # is "image". It is the easiest methods to allow uploading any image format files.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    if (
        upload_file.content_type is None
        or upload_file.content_type.split("/")[0] != "image"
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only image files uploads are allowed",
        )

    async with aiofiles.open("./temp_data/image/" + str(file_id), "wb") as file:
        byte_content = await upload_file.read()
        await file.write(byte_content)
    return UploadFileResponse(file_id=file_id)


@router.get("/models", response_model=ModelsDataReponse)
async def get_models() -> ModelsDataReponse:
    # Transform any known image model into ModelData object format and
    # store them as a list inside ModelsDataResponse
    return ModelsDataReponse(
        models=[ModelData.from_orm(model) for model in get_image_plugins().values()]
    )


@router.post("/process", response_model=ImageProcessingResponse)
async def process_image(request: ImageProcessingRequest):
    plugin_info = get_image_plugins().get(request.image_model)

    if plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such model available"
        )

    filepath = Path("./temp_data/image") / str(request.image_file)

    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such file available"
        )

    job: Result = task_system.dynamic_plugin_call(
        plugin_info.class_name, ImageProcessingFunction, str(filepath)
    )

    extracted_text = await asyncio.get_running_loop().run_in_executor(
        None, lambda: job.get(blocking=True, preserve=True)
    )

    return ImageProcessingResponse(text=extracted_text)
