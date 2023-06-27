import pytesseract

from core.plugins import register_plugin


@register_plugin
class EngTesseractPlugin:
    name = "eng_tesseract"
    languages = ["eng"]
    description = "Tesseract Open Source OCR Engine For English Language"

    @staticmethod
    def process_image(filename: str) -> str:
        return pytesseract.image_to_string(
            filename, lang="+".join(EngTesseractPlugin.languages)
        )
