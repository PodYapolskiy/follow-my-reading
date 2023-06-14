from core.models import register_model
import pytesseract


@register_model
class EngTesseract:
    name = "eng_tesseract"
    languages = ["eng"]
    description = "Tesseract Open Source OCR Engine For English Language"

    def process_image(self, filename: str) -> str:
        return pytesseract.image_to_string(filename, lang="eng")
