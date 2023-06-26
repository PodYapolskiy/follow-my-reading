from huey import RedisHuey
from core.plugins import load_plugins
import logging

scheduler = RedisHuey()

plugins = load_plugins()


@scheduler.task()
def dynamic_plugin_call(class_name: str, function: str, *args, **kwargs):
    logger = logging.getLogger("huey")

    logger.info(">>> Searching target plugin")
    target = None
    for plugin in plugins:
        if hasattr(plugin, class_name):
            logger.info(">>> Target plugin found")
            target = plugin
            break
    else:
        logger.info(">>> Target plugin not found")
        raise KeyError(f"No plugin contain class {class_name}")
    logger.info(">>> Getting class object from target plugin")
    cls = getattr(target, class_name)
    logger.info(">>> Getting fuction from class")
    func = getattr(cls, function)
    logger.info(">>> Executing function")
    return func(*args, **kwargs)  # Call the function.
