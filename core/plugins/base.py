from typing import List, Protocol, runtime_checkable
from uuid import UUID

from pydantic import BaseModel


class AudioChunk(BaseModel):
    start: float
    end: float
    text: str


class AudioProcessingResult(BaseModel):
    text: str
    segments: List[AudioChunk]


class AudioSegment(BaseModel):
    start: float
    end: float
    text: str
    file: UUID


class AudioTaskResult(BaseModel):
    text: str
    segments: List[AudioSegment]


class Point(BaseModel):
    x: int
    y: int


class Rectangle(BaseModel):
    left_top: Point
    right_top: Point
    left_bottom: Point
    right_bottom: Point


class ImageTextBox(BaseModel):
    text: str
    coordinates: Rectangle


class ImageProcessingResult(BaseModel):
    text: str
    boxes: List[ImageTextBox]


class ImageTaskResult(ImageProcessingResult):
    pass


class TextDiff(BaseModel):
    audio_segment: AudioSegment
    at_char: int
    found: str
    expected: str


class AudioToImageComparisonResponse(BaseModel):
    audio: AudioTaskResult
    image: ImageProcessingResult
    errors: List[TextDiff]


class AudioToTextComparisonResponse(BaseModel):
    audio: AudioTaskResult
    errors: List[TextDiff]


class AudioPhrase(BaseModel):
    audio_segment: AudioSegment | None
    found: bool
    phrase: str


class AudioExtractPhrasesResponse(BaseModel):
    data: List[AudioPhrase]


@runtime_checkable
class BasePlugin(Protocol):
    """
    `ModelPlugin` is a base protocol for models, which contain common metadata,
    such as name, list of supported languages, and description
    """

    name: str
    languages: List[str]
    description: str


@runtime_checkable
class ImageProcessingPlugin(BasePlugin, Protocol):
    """
    `ImageModel` is a protocol, that requires class implements method
    called `process_image`, which accepts filename (string) as a parameter
    and returns text string
    """

    @staticmethod
    def process_image(filename: str) -> str:
        ...


"""
`ImageProcessingFunction` is a constant string variable, which contains the name of
statis method within `ImageProcessingPlugin` protocol to process image
"""
ImageProcessingFunction = ImageProcessingPlugin.process_image.__name__


@runtime_checkable
class AudioProcessingPlugin(BasePlugin, Protocol):
    """
    AudioModel is a protocol, that requires class implements method
    called `process_audio`, which accepts filename (string) as a parameter
    and returns text string
    """

    @staticmethod
    def process_audio(filename: str) -> AudioProcessingResult:
        ...


"""
`AudioProcessingFunction` is a constant string variable, which contains the name of
statis method within `AudioProcessingPlugin` protocol to process audio
"""
AudioProcessingFunction = AudioProcessingPlugin.process_audio.__name__
