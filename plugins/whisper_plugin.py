import whisper

from core.plugins import AudioChunk, AudioProcessingResult, register_plugin


@register_plugin
class WhisperPlugin:
    name = "whisper"
    languages = ["en", "ru", "ar"]
    description = "Robust Speech Recognition via Large-Scale Weak Supervision By OpenAI"

    model = whisper.load_model("base")  # large-v2

    @staticmethod
    def process_audio(filename: str) -> AudioProcessingResult:
        model_response = WhisperPlugin.model.transcribe(filename)
        chunks = [
            AudioChunk(start=seg["start"], end=seg["end"], text=seg["text"])
            for seg in model_response["segments"]
        ]

        return AudioProcessingResult(text=model_response["text"], segments=chunks)
