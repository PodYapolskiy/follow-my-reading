from core.plugins import AUDIO_PLUGINS
from fastapi import HTTPException, status
import os


def extract_text(model_name: str, file_name: str):
    model = AUDIO_PLUGINS.get(model_name)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )

    filepath = "./temp_data/audio/" + file_name

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not Found"
        )

    return model.process_audio(filepath)
