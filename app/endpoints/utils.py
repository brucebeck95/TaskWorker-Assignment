import json
import yaml
import yaml.scanner
from typing import Callable

from fastapi import Request, status
from fastapi.exceptions import HTTPException

from app.core.models import Task, User


async def trigger_round_robin_assignment() -> str:
    """
    Using the updated_at date, we can assign the next task to the user that
    has not received a task recently or joined between the last run and this one.
    """
    with User() as user_db:
        users = user_db.get_all_validated_users(
            order_by_column="updated_at", order_direction="asc"
        )
    if not users:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Not enough users to assign tasks to",
        )

    with Task() as task_db:
        unassigned_tasks = task_db.get_all_unassigned_tasks().all()
        if not unassigned_tasks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Not enough tasks to assign",
            )
        for index, task in enumerate(unassigned_tasks):
            # When we reach the end of the users list, we start again
            user_id = users[index % len(users)].id
            await task_db.assign_task(task_id=task.id, user_id=user_id)
    return "Tasks distributed successfully"


async def translate_json(request: Request) -> dict:
    try:
        return await request.json()
    except json.decoder.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid json payload provided",
        )


async def translate_yaml(request: Request) -> dict:
    try:

        body = await request.body()
        return yaml.safe_load(body)
    except yaml.scanner.ScannerError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid yaml payload provided",
        )


# To allow more content types, add the new content types here
# and an additional callable to translate that content type.
CONTENT_TYPES: dict[str, Callable] = {
    "application/json": translate_json,
    "application/x-yaml": translate_yaml,
}


async def request_body_mapping(request: Request) -> dict:
    content_type = request.headers.get("content-type")
    if content_type not in CONTENT_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content type provided is not supported yet",
        )
    data = await CONTENT_TYPES[content_type](request)
    return data
