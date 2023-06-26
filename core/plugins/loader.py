import importlib
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Type

from core.plugins.base import AudioProcessingPlugin, BasePlugin, ImageProcessingPlugin


@dataclass
class PluginInfo:
    """
    `PluginInfo` is a descriptive dataclass, which contains system information
    about a plugin
    """

    name: str
    class_name: str
    description: str
    languages: List[str]

    @staticmethod
    def from_baseplugin_cls(cls: Type[BasePlugin]):
        """
        `from_baseplugin_cls` is a static method (constructor), which build `PluginInfo`
        using date from a class, that satisfy to `BasePlugin` protocol
        """
        return PluginInfo(
            name=cls.name,
            class_name=cls.__name__,
            description=cls.description,
            languages=cls.languages,
        )


"""
AUDIO_PLUGINS is a dictionary containing plugin names as keys
and plugin class names as values. E.g.: 'whisper' -> 'WhisperPlugin'
"""
AUDIO_PLUGINS: Dict[str, PluginInfo] = {}

"""
IMAGE_PLUGINS is a dictionary containing plugin names as keys
and plugin class names as values. E.g.: 'easyocr' -> 'EasyOCRPlugin'
"""
IMAGE_PLUGINS: Dict[str, PluginInfo] = {}


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

        # put {plugin class name} into dictionary with key {plugin info}
        IMAGE_PLUGINS[plugin_cls.name] = PluginInfo.from_baseplugin_cls(plugin_cls)

    elif isinstance(plugin_cls, AudioProcessingPlugin):
        # if object matches AudioModel interface

        # put {plugin class name} into dictionary with key {plugin info}
        AUDIO_PLUGINS[plugin_cls.name] = PluginInfo.from_baseplugin_cls(plugin_cls)
    else:
        # todo: warning about not matching interface
        return

    return plugin_cls


def load_plugins():
    """
    `load_plugins` is a function, that iterates over all files in `./plugins` directory,
    which satify the mask "*_plugin.py", and dynamically imports them as modules,
    thus loading them into the memory and triggering `@register_plugin` decorator.
    Returns loaded models as list of python objects.
    """
    # iterate over all *_plugin.py files in plugins directory
    imported_modules = []
    for filepath in pathlib.Path("./plugins").glob("*_plugin.py"):
        # transform path to module name
        module_name = filepath.as_posix().replace("/", ".")[:-3]
        # import it, loading into the memory
        imported_modules.append(importlib.import_module(module_name))

    return imported_modules
