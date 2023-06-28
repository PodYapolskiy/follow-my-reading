import easyocr

from core.plugins import (
    ImageProcessingResult,
    ImageTextBox,
    Point,
    Rectangle,
    register_plugin,
)


@register_plugin
class EasyOCRPlugin:
    name = "easyocr"
    description = (
        "An open source library for certain languages and alphabets,"
        "mainly used for working with text on an image"
    )

    # List of supported languages can be found here: https://www.jaided.ai/easyocr/
    languages = ["en", "ru"]

    reader = easyocr.Reader(languages, gpu=False)

    @staticmethod
    def process_image(filename: str) -> ImageProcessingResult:
        model_response = EasyOCRPlugin.reader.readtext(filename)
        boxes = []
        for coordinates, text, _ in model_response:
            lt, rt, rb, lb = coordinates
            boxes.append(
                ImageTextBox(
                    text=text,
                    coordinates=Rectangle(
                        left_top=Point(x=lt[0], y=lt[1]),
                        right_top=Point(x=rt[0], y=rt[1]),
                        right_bottom=Point(x=rb[0], y=rb[1]),
                        left_bottom=Point(x=lb[0], y=lb[1]),
                    ),
                )
            )
        result_text = " ".join(map(lambda x: x[1], model_response))

        return ImageProcessingResult(text=result_text, boxes=boxes)
