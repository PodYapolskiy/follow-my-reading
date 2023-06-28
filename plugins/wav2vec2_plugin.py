import librosa
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer

from core.plugins import AudioProcessingResult, register_plugin


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

    pretrained_model = "facebook/wav2vec2-large-960h"

    tokenizer = Wav2Vec2Tokenizer.from_pretrained(pretrained_model)
    model = Wav2Vec2ForCTC.from_pretrained(pretrained_model)

    @staticmethod
    def process_audio(filename: str) -> AudioProcessingResult:
        input_audio, _ = librosa.load(filename, sr=16000)

        input_values = Wav2Vec2Plugin.tokenizer(
            input_audio, return_tensors="pt"
        ).input_values
        logits = Wav2Vec2Plugin.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        return AudioProcessingResult(
            text="\n".join(Wav2Vec2Plugin.tokenizer.batch_decode(predicted_ids)),
            segments=[],
        )
