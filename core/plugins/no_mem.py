from functools import lru_cache
from typing import Dict

from core.plugins.loader import PluginInfo
from core.task_system import _get_audio_plugins, _get_image_plugins


@lru_cache
def get_audio_plugins() -> Dict[str, PluginInfo]:
    """
    `get_audio_plugins` is a function, which runs scheduled job
    `_get_audio_plugins`. This job returns info about loaded
    into the worker plugins. This function does NOT load plugins
    into the memory. This function caches results and its body should
    be executed only once and cached result used later. However, there are
    NO negative side effects of running the function or function's body
    several times.
    """
    return _get_audio_plugins().get(blocking=True)


@lru_cache
def get_image_plugins() -> Dict[str, PluginInfo]:
    """
    `get_image_plugins` is a function, which runs scheduled job
    `_get_image_plugins`. This job returns info about loaded
    into the worker plugins. This function does NOT load plugins
    into the memory. This function caches results and its body should
    be executed only once and cached result used later. However, there are
    NO negative side effects of running the function or function's body
    several times.
    """
    return _get_image_plugins().get(blocking=True)
