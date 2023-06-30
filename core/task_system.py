import logging

from huey import RedisHuey

from core.plugins import (
    AUDIO_PLUGINS,
    IMAGE_PLUGINS,
    AudioProcessingResult,
    ImageProcessingResult,
    load_plugins,
)
from core.plugins.base import AudioSegment, AudioTaskResult
from core.processing.text import match_phrases
from core.processing.audio_split import split_audio, split_silence

scheduler = RedisHuey()


plugins = []


@scheduler.on_startup()
def load_plugins_into_memories():
    """
    Load plugins on startup. This function is introduced
    in order not to load plugins into the module on import.
    """
    global plugins
    plugins = load_plugins()


logger = logging.getLogger("huey")


def _plugin_class_method_call(class_name: str, function: str, filepath: str):
    """
    `_plugin_class_method_call` is a function, which search each plugin for `class_name`
    object. If the object is not found, it raises KeyError. If found, the function
    gets the class and loads the `function` from it. According to `AudioProcessingPlugin`
    and `ImageProccesingPlugin` this function must be `@staticmethod`. Then,
    `_plugin_class_method_call` calls the loaded function with `filepath` argument and
    returns the result.
    """
    logger.info(f"Searching target plugin, which contains {class_name}")
    target = None
    # look through all loaded plugin
    for plugin in plugins:
        # if any plugin contain specified class, use this plugin as a targer
        if hasattr(plugin, class_name):
            logger.info(f"Target plugin found: {plugin.__name__}")
            target = plugin
            break
    else:
        # if no plugin is found, raise an error
        logger.info("Target plugin not found")
        raise KeyError(f"No plugin contain class {class_name}")

    logger.info(f"Getting class object ({class_name}) from target plugin")
    cls = getattr(target, class_name)  # load class from plugin module
    logger.info(f"Getting fuction ({function}) from class")
    func = getattr(cls, function)  # load function from class
    logger.info(f"Executing function {function} with {filepath=}")
    return func(filepath)  # call the function


@scheduler.task()
def dynamic_plugin_call(class_name: str, function: str, filepath: str):
    """
    `dynamic_plugin_call` is a sheduled job, which accepts `class_name` (str),
    `function` (str), `filepath` (str) and returns the result of calling
    `_plugin_class_method_call` with these parameters.
    """
    return _plugin_class_method_call(class_name, function, filepath)


@scheduler.task()
def audio_processing_call(audio_class: str, audio_function: str, audio_path: str):
    logger.info("Executing audio processing")
    audio_model_response: AudioProcessingResult = _plugin_class_method_call(
        audio_class, audio_function, audio_path
    )

    segments = []
    if len(audio_model_response.segments) != 0:
        audio_splits = [(s.start, s.end) for s in audio_model_response.segments]
        audio_files = split_audio(audio_path, audio_splits)

        for index, file_id in enumerate(audio_files):
            segments.append(
                AudioSegment(
                    start=audio_model_response.segments[index].start,
                    end=audio_model_response.segments[index].end,
                    text=audio_model_response.segments[index].text,
                    file=file_id,
                )
            )

        return AudioTaskResult(text=audio_model_response.text, segments=segments)

    # todo: use split silence on models, which can not split audio
    return AudioTaskResult(text=audio_model_response.text, segments=[])


@scheduler.task()
def image_processing_call(image_class: str, image_function: str, image_path: str):
    logger.info("Executing image processing")
    image_model_response: ImageProcessingResult = _plugin_class_method_call(
        image_class, image_function, image_path
    )
    return image_model_response


@scheduler.task()
def compare_image_audio(
    audio_class: str,
    audio_function: str,
    audio_path: str,
    image_class: str,
    image_function: str,
    image_path: str,
):
    """
    `compare_image_audio` is a scheduled job, which accepts these parameters:
    - `audio_class: str`
    - `audio_function: str`
    - `audio_path: str`
    - `image_class: str`
    - `image_function: str`
    - `image_path: str`

    Then `compare_image_audio` calls `_plugin_class_method_call` two times: for audio
    and for image correspondingly. When both of the calls are completed, it matches
    resulted texts and returns the difference.

    Note: with increased amount of workers, this job can call `dynamic_plugin_call`
    instead of `_plugin_class_method_call` and execute code simultaneously for
    audio and image processing.
    """
    audio_model_response = audio_processing_call(
        audio_class, audio_function, audio_path
    )
    image_model_response = image_processing_call(
        image_class, image_function, image_path
    )
    logger.info("Text matching")
    phrases = [x.text for x in audio_model_response.segments]
    # todo: return TaskResultResponse
    return match_phrases(phrases, image_model_response.text)


@scheduler.task()
def _get_audio_plugins():
    """
    `get_audio_plugins` is a scheduled job, which returns info about
    loaded into the worker audio plugins.
    """
    return AUDIO_PLUGINS


@scheduler.task()
def _get_image_plugins():
    """
    `get_image_plugins` is scheduled job, which returns info about
    loaded into the worker image plugins.
    """
    return IMAGE_PLUGINS
