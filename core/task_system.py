from huey import RedisHuey
from huey.api import Result
from core.plugins import load_plugins
from core.processing.text import match
import logging

scheduler = RedisHuey()

plugins = load_plugins()
logger = logging.getLogger("huey")


def _plugin_class_method_call(class_name: str, function: str, filepath: str):
    logger.info(f"Searching target plugin, which contains {class_name}")
    target = None
    for plugin in plugins:
        if hasattr(plugin, class_name):
            logger.info(f"Target plugin found: {plugin.__name__}")
            target = plugin
            break
    else:
        logger.info("Target plugin not found")
        raise KeyError(f"No plugin contain class {class_name}")
    logger.info(f"Getting class object ({class_name}) from target plugin")
    cls = getattr(target, class_name)
    logger.info(f"Getting fuction ({function}) from class")
    func = getattr(cls, function)
    logger.info(f"Executing function {function} with {filepath=}")
    return func(filepath)  # Call the function.


@scheduler.task()
def dynamic_plugin_call(class_name: str, function: str, filepath: str):
    _plugin_class_method_call(class_name, function, filepath)


@scheduler.task()
def compate_image_audio(
    audio_class: str,
    audio_function: str,
    audio_path: str,
    image_class: str,
    image_function: str,
    image_path: str,
):
    logger.info("Executing audio processing")
    audio_text = _plugin_class_method_call(audio_class, audio_function, audio_path)
    logger.info("Executing image processing")
    image_text = _plugin_class_method_call(image_class, image_function, image_path)

    logger.info("Text matching")
    return match(image_text, audio_text)
