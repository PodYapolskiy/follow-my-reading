from core.models import register_model
import whisper


@register_model
class WhisperPlugin:
    name = "whisper"
    languages = ["eng"]
    description = "Robust Speech Recognition via Large-Scale Weak Supervision By OpenAI"

    def __init__(self):
        self.model = whisper.load_model("base")

    def process_audio(self, filename: str) -> str:
        return self.model.transcribe(filename)["text"]
