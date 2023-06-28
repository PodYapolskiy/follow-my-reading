from typing import Any, List
from uuid import UUID

from pydantic import BaseModel


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


class ImageProcessingRequest(BaseModel):
    image_file: UUID
    image_model: str


class ImageProcessingResponse(BaseModel):
    text: str


class AudioProcessingRequest(BaseModel):
    audio_file: UUID
    audio_model: str


class AudioChunk(BaseModel):
    start: float
    end: float
    text: str


class AudioProcessingResponse(BaseModel):
    text: str
    segments: List[AudioChunk]


class TaskCreateRequest(BaseModel):
    audio_file: UUID
    image_file: UUID
    audio_model: str
    image_model: str


class TaskCreateResponse(BaseModel):
    task_id: UUID


class TaskStatusResponse(BaseModel):
    task_id: UUID
    status: str
    ready: bool


class TaskResultsResponse(BaseModel):
    data: Any


class MultipleTasksStatusResponse(BaseModel):
    data: List[TaskStatusResponse]
