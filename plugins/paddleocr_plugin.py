# NOTE: temporary disabled

# from core.plugins import register_plugin
# from paddleocr import PaddleOCR


# @register_plugin
# class PaddleOCRPlugin:
#     name = "paddleocr"
#     languages = ["eng"]
#     description = "An open universal and multifunctional source library."

#     ocr = PaddleOCR(lang="en")

#     @staticmethod
#     def process_image(filename: str) -> str:
#         result = ""
#         for el in PaddleOCRPlugin.ocr.ocr(filename, cls=False)[0]:
#             print(el)
#             result += el[1][0] + " "
#         return result
