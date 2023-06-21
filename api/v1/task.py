from fastapi import APIRouter
from .models import TaskCreateRequest, TaskCreateResponse
from core import tasks, processing


router = APIRouter(prefix="/task", tags=["task"])


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    task_id = tasks.put_in_queue(
        processing.task.find_difference,
        request.audio_model,
        request.image_model,
        str(request.audio_file),
        str(request.image_file),
    )

    return TaskCreateResponse(task_id=task_id)


@router.get("/tasks")
async def get_all_tasks():
    # todo: this is demo. to be removed in the future
    answer = {}
    for uuid, task in tasks.get_tasks().items():
        answer[uuid] = {"status": task.get_status(), "ended_at": task.ended_at}

    return answer
