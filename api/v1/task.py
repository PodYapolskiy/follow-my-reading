from uuid import UUID

from fastapi import APIRouter, Depends

from config import get_config

from .auth import get_current_active_user
from .models import TaskStatusResponse
from .task_utils import _get_job_result, _get_job_status

config = get_config()

router = APIRouter(
    prefix="/task", tags=["task"], dependencies=[Depends(get_current_active_user)]
)


@router.get(
    "/status",
    response_model=TaskStatusResponse,
    status_code=200,
    summary="""The endpoint `status` returns the status of a task identified by its `task_id`.""",
)
async def get_job_status(task_id: UUID) -> TaskStatusResponse:
    """
    Parameters:
    - **task_id**: The `task_id` is the uuid of the task to fetch status of

    Responses:
    - 200, Job status
    """
    return _get_job_status(task_id)


@router.get(
    "/result",
    status_code=200,
    summary="""The endpoint `/result` retrieves the results of a task with a given task ID, and returns the
    results.""",
    responses={
        406: {
            "description": "It is impossible to get task result (task does not exist or it has not finished yet).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Results are not ready yet or no task with such id exist",
                    }
                }
            },
        }
    },
)
async def get_job_result(task_id: UUID) -> dict:
    """
    Parameters:
    - **task_id**: The `task_id` is the uuid of the task to fetch results of

    Responses:
    - 200, job results
    - 406, Results are not ready yet or no task with such id exist
    """
    data: dict = _get_job_result(task_id).dict()
    return data
