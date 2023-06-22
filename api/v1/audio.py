from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from uuid import uuid4
from .models import (
    UploadFileResponse,
    ModelsDataReponse,
    ModelData,
    AudioProcessingRequest,
    AudioProcessingResponse,
    AudioChunk,
    SplitAudioResponse
)
from typing import Dict, Annotated
from core.models import get_audio_models
from core.models.base import AudioModel
from core.processing.audio import extract_text
from core.processing.audio_split import duration, split_audio
import aiofiles

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
async def get_models(
    audio_models: Annotated[Dict[str, AudioModel], Depends(get_audio_models)]
) -> ModelsDataReponse:
    # Transform any known audio model into ModelData object format and
    # store them as a list inside ModelsDataResponse
    return ModelsDataReponse(
        models=[ModelData.from_orm(model) for model in audio_models.values()]
    )


@router.post("/process", response_model=AudioProcessingResponse)
async def process_audio(request: AudioProcessingRequest):
    return AudioProcessingResponse(
        text=await extract_text(request.audio_model, str(request.audio_file))
    )


@router.post("/split", response_model=SplitAudioResponse)
async def audio_split_res(request: AudioProcessingRequest, interval: int | float = 10):
    data = []
    intervals = []
    cur = 0
    dur = duration(str(request.audio_file))
    # Might not be the final interval separation algorithm
    while True:
        if not dur - cur - interval < 0:
            intervals.append((cur, cur + interval))
            cur += interval
        elif (not dur - cur > interval) and dur - cur > 0:
            intervals.append((cur, dur))
            break
        elif dur == cur:
            break

    unipath = split_audio("./temp_data/audio/" + str(request.audio_file), intervals)
    for i in range(len(intervals)):
        tmp = await extract_text(request.audio_model, str(i))
        data.append(AudioChunk(start=intervals[i][0], end=intervals[i][1], text=tmp))
    return SplitAudioResponse(data=data)
