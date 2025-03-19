from fastapi import Depends, status, Body
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from app.core.models import User

from app.core.auth import has_admin_rights

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/{user_id}/validate", status_code=200)
def validate_user(user_id: str, is_admin: str = Depends(has_admin_rights)) -> dict:
    with User() as user_db:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )
        user = user_db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
            )
        if user.validated:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User is already validated"
            )
        user_db.validate_user(user_id)
    return {"message": "User has been validated"}


@router.post("/register", status_code=201)
async def register_user(username: str = Body(...), password: str = Body(...)) -> dict:
    with User() as user_db:
        new_user = user_db.create_user(username=username, password=password)
    return {
        "message": "New user created successfully",
        "user": {"user_id": new_user.id, "username": new_user.username},
    }
