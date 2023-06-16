from fastapi import APIRouter
from .models import TaskCreateRequest, TaskCreateResponse
from core.processing import audio, image, text
from uuid import uuid4

router = APIRouter(prefix="/task", tags=["task"])


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    audio_text = await audio.extract_text(request.audio_model, str(request.audio_file))
    image_text = await image.extract_text(request.image_model, str(request.image_file))
    difference = text.match(audio_text, image_text)

    return TaskCreateResponse(
        task_id=uuid4(),
        audio_text=audio_text,
        image_text=image_text,
        difference=difference,
    )
