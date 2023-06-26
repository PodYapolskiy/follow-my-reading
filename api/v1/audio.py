import asyncio
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from huey.api import Result

from core import task_system
from core.plugins import AUDIO_PLUGINS
from core.plugins.base import AudioProcessingFunction

from .models import (
    AudioProcessingRequest,
    AudioProcessingResponse,
    ModelData,
    ModelsDataReponse,
    UploadFileResponse,
)

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/upload", response_model=UploadFileResponse)
async def upload_audio(upload_file: UploadFile) -> UploadFileResponse:
    file_id = uuid4()

    # Here we using MIME types specification, which have format
    # "kind/name". In the following code, we checking that the kind of document
    # is "audio". It is the easiest methods to allow uploading any audio format files.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    if (
        upload_file.content_type is None
        or upload_file.content_type.split("/")[0] != "audio"
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only audio files uploads are allowed",
        )

    async with aiofiles.open("./temp_data/audio/" + str(file_id), "wb") as file:
        byte_content = await upload_file.read()
        await file.write(byte_content)

    return UploadFileResponse(file_id=file_id)


@router.get("/models", response_model=ModelsDataReponse)
async def get_models() -> ModelsDataReponse:
    # Transform any known audio model into ModelData object format and
    # store them as a list inside ModelsDataResponse
    return ModelsDataReponse(
        models=[ModelData.from_orm(model) for model in AUDIO_PLUGINS.values()]
    )


@router.post("/process", response_model=AudioProcessingResponse)
async def process_audio(request: AudioProcessingRequest):
    plugin_info = AUDIO_PLUGINS.get(request.audio_model)

    if plugin_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such model available"
        )

    filepath = Path("./temp_data/audio") / str(request.audio_file)

    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such file available"
        )

    job: Result = task_system.dynamic_plugin_call(
        plugin_info.class_name, AudioProcessingFunction, str(filepath)
    )

    extracted_text = await asyncio.get_running_loop().run_in_executor(
        None, lambda: job.get(blocking=True, preserve=True)
    )

    return AudioProcessingResponse(text=extracted_text, data=[])
