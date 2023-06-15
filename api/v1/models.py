from pydantic import BaseModel
from uuid import UUID
from typing import List


class UploadFileResponse(BaseModel):
    file_id: UUID


class ModelData(BaseModel):
    name: str
    languages: List[str]
    description: str

    class Config:
        orm_mode = True


class ModelsDataReponse(BaseModel):
    models: List[ModelData]


class AudioProcessingRequest(BaseModel):
    audio_file: UUID
    audio_model: str


class AudioProcessingResponse(BaseModel):
    text: str
