import pytesseract

from core.plugins import (
    register_plugin,
    ImageProcessingResult,
    Point,
    ImageTextBox,
    Rectangle,
)


@register_plugin
class EngTesseractPlugin:
    name = "eng_tesseract"
    languages = ["eng"]
    description = "Tesseract Open Source OCR Engine For English Language"

    # Additional models could be found here: https://github.com/tesseract-ocr/tessdata_best

    @staticmethod
    def process_image(filename: str) -> ImageProcessingResult:
        model_response = pytesseract.image_to_data(
            filename, lang="+".join(EngTesseractPlugin.languages), output_type="dict"
        )
        print(model_response)

        words_count = model_response["word_num"]
        words = model_response["text"]
        xs = model_response["left"]
        ys = model_response["top"]
        dxs = model_response["width"]
        dys = model_response["height"]

        boxes = []
        for word_count, text, x, y, w, h in zip(words_count, words, xs, ys, dxs, dys):
            if word_count != 0:
                boxes.append(
                    ImageTextBox(
                        text=text,
                        coordinates=Rectangle(
                            left_top=Point(x=x, y=y),
                            right_top=Point(x=x + w, y=y),
                            right_bottom=Point(x=x + w, y=y + h),
                            left_bottom=Point(x=x, y=y + h),
                        ),
                    )
                )

        result_text = " ".join(filter(lambda x: x != "", words))

        return ImageProcessingResult(text=result_text, boxes=boxes)
