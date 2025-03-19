from fastapi import Depends, status
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from app.core.models import Task
from app.core.auth import has_admin_rights

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, is_admin: bool = Depends(has_admin_rights)) -> None:
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )

    with Task() as task_db:
        task = task_db.get_task(task_id=task_id)
        if not task:
            raise HTTPException(status.HTTP_410_GONE, detail="Record does not exist")
        if task.assigned_to is not None:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to delete this resource",
            )
        task_db.delete_task(task_id=task_id)

    return None
