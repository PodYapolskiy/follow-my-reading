from typing import Dict

from core.plugins.loader import PluginInfo
from core.task_system import _get_audio_plugins, _get_image_plugins


def get_audio_plugins() -> Dict[str, PluginInfo]:
    """
    `get_audio_plugins` is a function, which runs scheduled job
    `_get_audio_plugins`. This job returns info about loaded
    into the worker plugins. This function does NOT load plugins
    into the memory.
    """
    return _get_audio_plugins().get(blocking=True)  # type: ignore


def get_image_plugins() -> Dict[str, PluginInfo]:
    """
    `get_image_plugins` is a function, which runs scheduled job
    `_get_image_plugins`. This job returns info about loaded
    into the worker plugins. This function does NOT load plugins
    into the memory.
    """
    return _get_image_plugins().get(blocking=True)  # type: ignore
