from typing import List, Protocol, runtime_checkable


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
    def process_audio(filename: str) -> str:
        ...


"""
`AudioProcessingFunction` is a constant string variable, which contains the name of
statis method within `AudioProcessingPlugin` protocol to process audio
"""
AudioProcessingFunction = AudioProcessingPlugin.process_audio.__name__
