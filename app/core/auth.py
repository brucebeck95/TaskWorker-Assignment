import jwt
import logging
from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import status, Depends
from fastapi.exceptions import HTTPException


from app.config import OAUTH2_SCHEMA
from app.config import JWT_SECRET_KEY


ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(to_encode: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("user_id")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def retrieve_and_decode_token(token: str) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Authentication missing"
        )
    token_payload = verify_token(token.replace("Bearer ", ""))
    return token_payload


def has_admin_rights(token: Annotated[str, Depends(OAUTH2_SCHEMA)]) -> bool:
    """
    Helper method to help determine if a user is an admin or not.
    FastAPI automatically pulls the token and injects it into this functions
    """
    if retrieve_and_decode_token(token).get("is_admin"):
        return True
    return False


def identify_user(token: Annotated[str, Depends(OAUTH2_SCHEMA)]) -> str:
    user_id = retrieve_and_decode_token(token)["user_id"]
    return user_id
