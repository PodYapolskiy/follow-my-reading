from fastapi import APIRouter, UploadFile
from uuid import uuid4, UUID
from .models import UploadFileResponse
import aiofiles

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/upload", response_model=UploadFile)
async def upload_audio(upload_file: UploadFile):
    file_id = uuid4()
    async with aiofiles.open("/temp_data/" + str(file_id), "wb") as file:
        byte_content = await upload_file.read()
        await file.write(byte_content)
    return UploadFileResponse(file_id=file_id)
