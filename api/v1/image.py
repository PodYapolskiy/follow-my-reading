from fastapi import APIRouter, UploadFile, HTTPException, status
from uuid import uuid4
from .models import (
    UploadFileResponse,
    ModelData,
    ImageProcessingRequest,
    ModelsDataReponse,
    ImageProcessingResponse,
)
import aiofiles
from core.models import image_models
from core.processing.image import extract_text


router = APIRouter(prefix="/image", tags=["image"])


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
        models=[ModelData.from_orm(model) for model in image_models.values()]
    )


@router.post("/process", response_model=ImageProcessingResponse)
async def process_image(request: ImageProcessingRequest):
    return ImageProcessingResponse(
        text=await extract_text(request.image_model, str(request.image_file))
    )
