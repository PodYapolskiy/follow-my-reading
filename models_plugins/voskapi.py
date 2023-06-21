from core.models import register_model
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave
import json

#https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

@register_model
class VoskAPI:
    name = "voskapi"
    languages = ["eng"]
    description = "The Vosk API is a library for real-time speech recognition in different languages. It uses machine learning technology and a large data set to improve the quality of recognition."

    def process_audio(self, filename: str) -> str:
        SetLogLevel(-1)
        wf = wave.open(filename, "rb")
        model = Model(r"models_plugins\\forVOSK")
        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                recognizerResult = recognizer.Result()

        recognizerResult = recognizer.Result()
        resultDict = json.loads(recognizerResult)
        return resultDict.get("text", "")
