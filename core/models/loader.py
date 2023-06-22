from .base import ModelPlugin, AudioModel, ImageModel
from typing import Dict
from functools import lru_cache
import importlib
import pathlib

audio_models: Dict[str, AudioModel] = {}
image_models: Dict[str, ImageModel] = {}


@lru_cache
def get_audio_models():
    return audio_models


@lru_cache
def get_image_models():
    return image_models


def register_model(cls: ModelPlugin):
    # create an instanse of decorated class
    instance = cls.__call__()  # type: ignore
    # reference to dictionary
    models_obj: Dict[str, AudioModel] | Dict[str, ImageModel] | None = None
    if isinstance(instance, ImageModel):
        # if object matches ImageModel interface, register it to the image_models
        models_obj = image_models
    elif isinstance(instance, AudioModel):
        # if object matches AudioModel interface, register it to the audio_models
        models_obj = audio_models
    else:
        # todo: warning about not matching interface
        return

    if cls.name in models_obj:
        # todo: warning about not unique name
        return

    # register instanse by static name
    models_obj[cls.name] = instance


def load_models():
    # iterate over all .py files in models_plugins direcory
    for filepath in pathlib.Path("./models_plugins").glob("*.py"):
        # transform path to module name
        module_name = filepath.as_posix().replace("/", ".")[:-3]
        # import it, loading into the memory
        importlib.import_module(module_name)
