from typing import List, Protocol, runtime_checkable


@runtime_checkable
class ModelPlugin(Protocol):
    """
    ModelPlugin is a base protocol for models,
    which contain common metadata,
    such as name, list of supported languages, and description
    """

    name: str
    languages: List[str]
    description: str


@runtime_checkable
class ImageModel(ModelPlugin, Protocol):
    """
    ImageModel is a protocol, that requires class implements method
    called `process_image`, which accepts filename (string) as a parameter
    and returns text string
    """

    def process_image(self, filename: str) -> str:
        ...


@runtime_checkable
class AudioModel(ModelPlugin, Protocol):
    """
    AudioModel is a protocol, that requires class implements method
    called `process_audio`, which accepts filename (string) as a parameter
    and returns text string
    """

    def process_audio(self, filename: str) -> str:
        ...
