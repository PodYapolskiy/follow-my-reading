from core.models import register_model
import easyocr


@register_model
class EasyOCRPlugin:
    name = "easyocr"
    languages = ["eng", "chi"]
    description = "An open source library for certain languages and alphabets, mainly used for working with text on an image"

    def __init__(self):
        self.reader = easyocr.Reader(["en", "ru"], gpu=False)

    def process_image(self, filename: str) -> str:
        result = ""
        for el in self.reader.readtext(filename):
            result += el[1] + " "
        return result
