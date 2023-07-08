from uuid import UUID, uuid4

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic.error_wrappers import ValidationError

from config import get_config
from core.plugins.no_mem import get_audio_plugins

from .auth import get_current_active_user
from .models import (
    AudioProcessingRequest,
    AudioProcessingResponse,
    ModelData,
    ModelsDataReponse,
    TaskCreateResponse,
    UploadFileResponse,
)
from .task import _get_job_result, _get_job_status, create_audio_task

config = get_config()
router = APIRouter(
    prefix="/audio", tags=["audio"], dependencies=[Depends(get_current_active_user)]
)


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

    async with aiofiles.open(config.storage.audio_dir / str(file_id), "wb") as file:
        byte_content = await upload_file.read()
        await file.write(byte_content)

    return UploadFileResponse(file_id=file_id)


@router.get("/models", response_model=ModelsDataReponse)
async def get_models() -> ModelsDataReponse:
    # Transform any known audio model into ModelData object format and
    # store them as a list inside ModelsDataResponse
    return ModelsDataReponse(
        models=[ModelData.from_orm(model) for model in get_audio_plugins().values()]
    )


@router.post("/process", response_model=TaskCreateResponse)
async def process_audio(request: AudioProcessingRequest) -> TaskCreateResponse:
    created_task: TaskCreateResponse = await create_audio_task(request)
    return created_task


@router.get("/download", response_class=FileResponse)
async def download_audio_file(file: UUID) -> str:
    filepath = config.storage.audio_dir / str(file)

    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return filepath.as_posix()


@router.get("/result", response_model=AudioProcessingResponse)
async def get_response(task_id: UUID) -> AudioProcessingResponse:
    response = await _get_job_status(task_id)
    if not response.ready:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The job is non-existent or not done",
        )

    data = await _get_job_result(task_id)
    try:
        return AudioProcessingResponse.parse_obj(data.dict())
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="There is no such audio processing task",
        ) from error
