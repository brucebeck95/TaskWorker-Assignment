import logging

from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.models import User
from app.core.auth import create_access_token


router = APIRouter(tags=["initial_auth"])


@router.post("/token", status_code=200)
def request_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    """
    This only exists because I don't have a OAuth client that I can use
    to verify identities.
    FastAPI looks for /token to handle the Auth on the Swagger.
    """

    logging.info(form_data)
    username = form_data.username
    with User() as user_db:
        user = user_db.get_user_by_username(username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with username: {username}",
        )

    if username == user.username and form_data.password == user.password:
        access_token = create_access_token(
            to_encode={
                "is_admin": user.admin,
                "user_id": user.id,
            },
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
