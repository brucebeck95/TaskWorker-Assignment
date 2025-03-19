from fastapi import status, Depends, Path
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from app.core.auth import has_admin_rights, identify_user
from app.core.models import Task, User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/assigned", status_code=200)
def get_assigned_tasks(user_id=Depends(identify_user)):
    with User() as user_db:
        user = user_db.get_user_by_id(user_id=user_id)
        tasks = [task.to_dict() for task in user.tasks]
    return {"message": f"Retrieved tasks for user: {user_id}", "tasks": tasks}


@router.get("/{task_id}", status_code=200)
def get_task(
    task_id: int = Path(..., ge=1), admin: str = Depends(has_admin_rights)
) -> dict:

    with Task() as task_db:
        task = task_db.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No task found with id: {task_id}",
        )
    if not admin:
        if task.assigned_to is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to view this task: {task_id}",
            )
        else:
            return {"message": "Task retrieved", "task": task.to_dict()}

    return {"message": "Task retrieved", "task": task.to_dict()}
