from typing import Any, Dict

from huey import RedisHuey
from typing import List
from loguru import logger
from core.plugins import (
    AUDIO_PLUGINS,
    IMAGE_PLUGINS,
    AudioProcessingResult,
    ImageProcessingResult,
    load_plugins,
)
from core.plugins.base import (
    AudioSegment,
    AudioTaskResult,
    ImageTaskResult,
    AudioToImageComparisonResponse,
    AudioToTextComparisonResponse,
    TextDiff,
)
from core.plugins.loader import PluginInfo
from core.processing.audio_split import split_audio
from core.processing.text import match_phrases

scheduler = RedisHuey()

logger.add("./logs/task_system.log", format="{time:DD-MM-YYYY HH:mm:ss zz} {level} {message}", enqueue=True)

plugins = []


@scheduler.on_startup()
def load_plugins_into_memories() -> None:
    """
    Load plugins on startup. This function is introduced
    in order not to load plugins into the module on import.
    """
    logger.info("Starting load_plugins_into_memories algorithm. Loading plugins.")
    global plugins
    plugins = load_plugins()
    logger.info("Plugins have been loaded successfully.")


def _plugin_class_method_call(class_name: str, function: str, filepath: str) -> Any:
    """
    `_plugin_class_method_call` is a function, which search each plugin for `class_name`
    object. If the object is not found, it raises KeyError. If found, the function
    gets the class and loads the `function` from it. According to `AudioProcessingPlugin`
    and `ImageProcessingPlugin` this function must be `@staticmethod`. Then,
    `_plugin_class_method_call` calls the loaded function with `filepath` argument and
    returns the result.
    """
    logger.info("Starting _plugin_class_method_call algorithm.")
    logger.info(f"Searching target plugin, which contains {class_name}")
    target = None
    # look through all loaded plugin
    for plugin in plugins:
        # if any plugin contain specified class, use this plugin as a target
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
    logger.info(f"Getting function ({function}) from class")
    func = getattr(cls, function)  # load function from class
    logger.info(f"Executing function {function} with {filepath}.\n"
                f"End of _plugin_class_method_call algorithm.")
    return func(filepath)  # call the function


@scheduler.task()
def dynamic_plugin_call(class_name: str, function: str, filepath: str) -> Any:
    """
    `dynamic_plugin_call` is a scheduled job, which accepts `class_name` (str),
    `function` (str), `filepath` (str) and returns the result of calling
    `_plugin_class_method_call` with these parameters.
    """
    logger.info("Starting dynamic_plugin_call algorithm.\n"
                "For more info check Process _plugin_class_method_call")
    return _plugin_class_method_call(class_name, function, filepath)


def _audio_process(
    audio_class: str, audio_function: str, audio_path: str
) -> AudioTaskResult:
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

        logger.info("Audio processed successfully")
        return AudioTaskResult(text=audio_model_response.text, segments=segments)

    # todo: use split silence on models, which can not split audio
    return AudioTaskResult(text=audio_model_response.text, segments=[])


@scheduler.task()
def audio_processing_call(
    audio_class: str, audio_function: str, audio_path: str
) -> AudioTaskResult:
    return _audio_process(audio_class, audio_function, audio_path)


def _image_process(
    image_class: str, image_function: str, image_path: str
) -> ImageTaskResult:
    logger.info("Executing image processing")
    image_model_response: ImageProcessingResult = _plugin_class_method_call(
        image_class, image_function, image_path
    )
    logger.info("Image processed successfully.")
    return ImageTaskResult.parse_obj(image_model_response.dict())


@scheduler.task()
def image_processing_call(
    image_class: str, image_function: str, image_path: str
) -> ImageTaskResult:
    return _image_process(image_class, image_function, image_path)


@scheduler.task()
def compare_image_audio(
    audio_class: str,
    audio_function: str,
    audio_path: str,
    image_class: str,
    image_function: str,
    image_path: str,
) -> AudioToImageComparisonResponse:
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
    audio_model_response: AudioTaskResult = _audio_process(
        audio_class, audio_function, audio_path
    )
    image_model_response: ImageProcessingResult = _image_process(
        image_class, image_function, image_path
    )

    logger.info("Starting compare_image_audio algorithm.")

    phrases = [x.text for x in audio_model_response.segments]
    text_diffs = match_phrases(phrases, image_model_response.text)

    data = []
    for index, diff in enumerate(text_diffs):
        for at_char, found, expected in diff:
            data.append(
                TextDiff(
                    audio_segment=audio_model_response.segments[index],
                    at_char=at_char,
                    found=found,
                    expected=expected,
                )
            )
    logger.info("Process compare_image_audio has been completed successfully. Returning the result")
    return AudioToImageComparisonResponse(
        audio=audio_model_response, image=image_model_response, errors=data
    )


@scheduler.task()
def compare_text_audio(
        audio_class: str,
        audio_function: str,
        audio_path: str,
        text: List[str]
) -> AudioToTextComparisonResponse:
    audio_model_response: AudioTaskResult = _audio_process(
        audio_class, audio_function, audio_path
    )
    logger.info("Starting compare_text_audio algorithm.")
    phrases = [x.text for x in audio_model_response.segments]
    original_text = ''
    for phrase in text:
        original_text += phrase + " "
    text_diffs = match_phrases(phrases, original_text)

    data = []
    for index, diff in enumerate(text_diffs):
        for at_char, found, expected in diff:
            data.append(
                TextDiff(
                    audio_segment=audio_model_response.segments[index],
                    at_char=at_char,
                    found=found,
                    expected=expected,
                )
            )

    logger.info("Process compare_text_audio has been completed successfully. Returning the result.")
    return AudioToTextComparisonResponse(
        audio=audio_model_response, original_text=text, errors=data
    )


@scheduler.task()
def _get_audio_plugins() -> Dict[str, PluginInfo]:
    """
    `get_audio_plugins` is a scheduled job, which returns info about
    loaded into the worker audio plugins.
    """
    return AUDIO_PLUGINS


@scheduler.task()
def _get_image_plugins() -> Dict[str, PluginInfo]:
    """
    `get_image_plugins` is scheduled job, which returns info about
    loaded into the worker image plugins.
    """
    return IMAGE_PLUGINS
