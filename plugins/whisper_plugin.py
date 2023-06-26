from core.plugins import register_plugin
import whisper


@register_plugin
class WhisperPlugin:
    name = "whisper"
    languages = ["eng"]
    description = "Robust Speech Recognition via Large-Scale Weak Supervision By OpenAI"

    model = whisper.load_model("base")

    @staticmethod
    def process_audio(filename: str) -> str:
        return WhisperPlugin.model.transcribe(filename)["text"]
