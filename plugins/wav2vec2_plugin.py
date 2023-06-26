from core.plugins import register_plugin
import librosa
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer


@register_plugin
class Wav2Vec2Plugin:
    name = "wav2vec2"
    languages = ["eng"]
    description = (
        "Wav2Vec2 designed to predict text data from an audio file, "
        "for example, to generate subtitles for a video."
        "It uses deep neural network models that are trained"
        " on large training datasets."
    )

    tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    @staticmethod
    def process_audio(filename: str) -> str:
        input_audio, _ = librosa.load(filename, sr=16000)

        input_values = Wav2Vec2Plugin.tokenizer(
            input_audio, return_tensors="pt"
        ).input_values
        logits = Wav2Vec2Plugin.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        return Wav2Vec2Plugin.tokenizer.batch_decode(predicted_ids)[0]
