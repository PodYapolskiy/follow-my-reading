from core.plugins import register_plugin
import easyocr


@register_plugin
class EasyOCRPlugin:
    name = "easyocr"
    description = (
        "An open source library for certain languages and alphabets,"
        "mainly used for working with text on an image"
    )

    languages = ["en", "ru"]

    reader = easyocr.Reader(languages, gpu=False)

    @staticmethod
    def process_image(filename: str) -> str:
        result = ""
        for el in EasyOCRPlugin.reader.readtext(filename):
            result += el[1] + " "
        return result
