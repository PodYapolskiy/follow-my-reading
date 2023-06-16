from core.models import audio_models
from fastapi import HTTPException, status
import os


async def extract_text(model_name: str, file_name: str):
    model = audio_models.get(model_name)

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
