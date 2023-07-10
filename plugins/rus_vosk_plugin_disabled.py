import json
import wave

from pydub import AudioSegment
from vosk import KaldiRecognizer, Model

from core.plugins import AudioChunk, AudioProcessingResult, register_plugin


@register_plugin
class RusVoskPlugin:
    name = "rus_vosk"
    languages = ["rus"]
    description = (
        "The Vosk API is a library for real-time speech recognition"
        " in different languages. It uses machine learning technology"
        " and a large data set to improve the quality of recognition."
    )

    # List of available models can be found here: https://alphacephei.com/vosk/models
    pretrained_model = "vosk-model-ru-0.42"

    model = Model(model_name=pretrained_model)

    @staticmethod
    def process_audio(filename: str) -> AudioProcessingResult:
        AudioSegment.from_file(filename).export(filename, format="wav")
        wf = wave.open(filename, "rb")
        rec = KaldiRecognizer(RusVoskPlugin.model, wf.getframerate())
        rec.SetWords(True)
        rec.SetPartialWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                # print(rec.Result())  # todo: logging
                pass
            else:
                # print(rec.PartialResult())
                pass

        model_response = json.loads(rec.FinalResult())

        chunks = [
            AudioChunk(start=seg["start"], end=seg["end"], text=seg["word"])
            for seg in model_response["result"]
        ]

        return AudioProcessingResult(text=model_response["text"], segments=chunks)
