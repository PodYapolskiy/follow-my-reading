from typing import List
from uuid import UUID

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    text: str


class UploadFileResponse(BaseModel):
    file_id: UUID


class ModelData(BaseModel):
    name: str
    languages: List[str]
    description: str

    class Config:
        orm_mode = True


class ModelsDataResponse(BaseModel):
    models: List[ModelData]


class ImageProcessingRequest(BaseModel):
    image_file: UUID
    image_model: str


class IPRPoint(BaseModel):
    x: int
    y: int


class IPRRectangle(BaseModel):
    left_top: IPRPoint
    right_top: IPRPoint
    left_bottom: IPRPoint
    right_bottom: IPRPoint


class IPRTextBox(BaseModel):
    text: str
    coordinates: IPRRectangle


class ImageProcessingResponse(BaseModel):
    text: str
    boxes: List[IPRTextBox]


class AudioProcessingRequest(BaseModel):
    audio_file: UUID
    audio_model: str


class AudioChunk(BaseModel):
    start: float
    end: float
    text: str
    file: UUID


class AudioProcessingResponse(BaseModel):
    text: str
    segments: List[AudioChunk]


class AudioToImageComparisonRequest(BaseModel):
    audio_file: UUID
    image_file: UUID
    audio_model: str
    image_model: str


class AudioToTextComparisonRequest(BaseModel):
    audio_file: UUID
    text: List[str]
    audio_model: str


class TaskCreateResponse(BaseModel):
    task_id: UUID


class TaskStatusResponse(BaseModel):
    task_id: UUID
    status: str
    ready: bool


class TextDiff(BaseModel):
    audio_segment: AudioChunk
    at_char: int
    found: str
    expected: str


class AudioImageComparisonResultsResponse(BaseModel):
    image: ImageProcessingResponse
    audio: AudioProcessingResponse
    errors: List[TextDiff]


class AudioTextComparisonResultsResponse(BaseModel):
    audio: AudioProcessingResponse
    errors: List[TextDiff]


class MultipleTasksStatusResponse(BaseModel):
    data: List[TaskStatusResponse]


class AudioExtractPhrasesRequest(BaseModel):
    audio_file: UUID
    audio_model: str
    phrases: List[str]


class AudioPhrase(BaseModel):
    audio_segment: AudioChunk | None
    found: bool
    phrase: str


class AudioExtractPhrasesResponse(BaseModel):
    data: List[AudioPhrase]
