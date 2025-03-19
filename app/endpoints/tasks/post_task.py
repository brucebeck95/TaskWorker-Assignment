from fastapi import Request, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter


from app.core.models import Task
from app.config import logger
from app.core.auth import has_admin_rights, identify_user
from app.endpoints.utils import trigger_round_robin_assignment, request_body_mapping

router = APIRouter(prefix="/tasks", tags=["tasks"])

schema_object = {
    "type": "object",
    "properties": {
        "decription": {"type": "string"},
        "title": {"type": "string"},
        "due_date": {"type": "date"},
    },
}


@router.post(
    "",
    status_code=201,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/x-yaml": {"schema": schema_object},
                "application/json": {"schema": schema_object},
            },
            "required": True,
        },
    },
)
async def create_task(
    request: Request,
    is_admin: bool = Depends(has_admin_rights),
) -> dict:
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    logger.info(request.headers)
    request_body = await request_body_mapping(request)

    with Task() as task_db:
        new_task = task_db.create_task(
            title=request_body["title"],
            description=request_body["description"],
            due_date=request_body["due_date"],
        )
    return {"message": "Task created", "id": new_task.id}


@router.patch("/assign", status_code=200)
async def trigger_task_assignment(is_admin=Depends(has_admin_rights)):
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )

    await trigger_round_robin_assignment()

    return {"message": "Tasks distributed successfully"}


@router.patch("/{task_id}/reject", status_code=200)
def reject_assigned_task(task_id: int, user_id: int = Depends(identify_user)) -> dict:
    with Task() as task_db:
        task = task_db.get_task(task_id=task_id)
        if task.assigned_to != user_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to reject this task",
            )
        task_db.reject_task(task.id)
    return {"message": "Task rejected successfully"}


@router.patch("/{task_id}/complete", status_code=200)
def complete_assigned_task(task_id: int, user_id: str = Depends(identify_user)) -> dict:
    with Task() as task_db:
        task = task_db.get_task(task_id=task_id)
        if task.assigned_to != user_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to reject this task",
            )
        task_db.complete_task(task.id)

    return {"message": "Task completed successfully"}
