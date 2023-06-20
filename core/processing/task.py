from . import audio, image, text


def find_difference(
    audio_model: str, image_model: str, audio_file: str, image_file: str
):
    audio_text = audio.extract_text(audio_model, audio_file)
    image_text = image.extract_text(image_model, image_file)
    difference = text.match(audio_text, image_text)

    return difference
