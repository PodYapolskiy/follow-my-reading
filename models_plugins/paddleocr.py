from core.models import register_model
from paddleocr import PaddleOCR

@register_model
class PaddleOCR:
    name = "paddleocr"
    languages = ["eng"]
    description = "An open universal and multifunctional source library."

    def __init__(self):
        self.ocr = PaddleOCR(lang='en')
    
    def process_image(self, filename: str) -> str:
        result = ''
        for el in self.ocr.ocr(filename, cls=False)[0]:
            result += el[1][0] + ' '
        return result
