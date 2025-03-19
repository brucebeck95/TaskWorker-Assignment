from fastapi import Depends, status
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from app.core.models import User

from app.core.auth import has_admin_rights

router = APIRouter(tags=["users"])


@router.get("/users", status_code=200)
def get_all_users(admin: str = Depends(has_admin_rights)) -> dict:
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )

    with User() as user_db:
        users = [
            {
                "id": user.id,
                "username": user.username,
                "validated": user.validated,
                "assigned_tasks": [task.to_dict() for task in user.tasks],
            }
            for user in user_db.get_all_validated_users()
        ]
    return {"message": "Users retrieved", "users": users}
