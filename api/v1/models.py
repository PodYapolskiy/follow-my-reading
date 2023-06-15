from pydantic import BaseModel
from uuid import UUID
from typing import List


class UploadFileResponse(BaseModel):
    file_id: UUID


class ImageProcessingRequest(BaseModel):
    image_file: UUID
    image_model: str


class ModelData(BaseModel):
    name: str
    languages: List[str]
    description: str

    class Config:
        orm_mode = True


class ModelsDataReponse(BaseModel):
    models: List[ModelData]



class ImageProcessingResponse(BaseModel):
    text: str


class AudioProcessingRequest(BaseModel):
    audio_file: UUID
    audio_model: str


class AudioProcessingResponse(BaseModel):
    text: str
