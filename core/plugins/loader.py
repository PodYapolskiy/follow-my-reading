from core.plugins.base import BasePlugin, AudioProcessingPlugin, ImageProcessingPlugin
from typing import Dict, Type
import importlib
import pathlib


"""
AUDIO_PLUGINS is a dictionary containing plugin names as keys
and plugin class names as values. E.g.: 'whisper' -> 'WhisperPlugin'
"""
AUDIO_PLUGINS: Dict[str, str] = {}

"""
IMAGE_PLUGINS is a dictionary containing plugin names as keys
and plugin class names as values. E.g.: 'easyocr' -> 'EasyOCRPlugin'
"""
IMAGE_PLUGINS: Dict[str, str] = {}


def register_plugin(plugin_cls: Type[BasePlugin]):
    """
    `register_plugin` is a function (decorator) which accepts a class (not an object),
    that satisfies protocol `BasePlugin`. It checks, weather the class additionally
    satisfies protocols `ImageProccesingPlugin` or `AudioProcessingPlugin`. If it does,
    the function adds this plugin into the `IMAGE_PLUGINS` or `AUDIO_PLUGINS` dictionary
    correspondingly and returns the class.
    If the class does not satisfy neither of these protocols, the function warn user,
    and drops the class.
    """
    if isinstance(plugin_cls, ImageProcessingPlugin):
        # if class matches ImageModel interface

        # put {plugin class name} into dictionary with key {plugin name}
        IMAGE_PLUGINS[plugin_cls.name] = plugin_cls.__name__

    elif isinstance(plugin_cls, AudioProcessingPlugin):
        # if object matches AudioModel interface

        # put {plugin class name} into dictionary with key {plugin name}
        AUDIO_PLUGINS[plugin_cls.name] = plugin_cls.__name__
    else:
        # todo: warning about not matching interface
        return

    return plugin_cls


def load_plugins():
    """
    `load_plugins` is a function, that iterates over all files in `./plugins` directory,
    which satify the mask "*_plugin.py", and dynamically imports them as modules,
    thus loading them into the memory and triggering `@register_plugin` decorator
    """
    # iterate over all *_plugin.py files in plugins directory
    for filepath in pathlib.Path("./plugins").glob("*_plugin.py"):
        # transform path to module name
        module_name = filepath.as_posix().replace("/", ".")[:-3]
        # import it, loading into the memory
        importlib.import_module(module_name)
