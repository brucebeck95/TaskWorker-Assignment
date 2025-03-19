import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app
from app.core.models import User, Task
from app.core.auth import create_access_token
from app.core.db import db_session, TaskTable, UserTable


@pytest.fixture
def fastapi_client():
    return TestClient(app=app)


@pytest.fixture(autouse=True)
def reset_db():
    yield
    session = db_session()

    stmt = delete(TaskTable)
    session.execute(stmt)

    stmt = delete(UserTable).where(UserTable.username != "admin")
    session.execute(stmt)

    session.commit()
    session.close()


def create_user():
    with User() as user_db:
        user = user_db.create_user(username="testing", password="dummy")
    return user.id


def create_valid_user():
    user_id = create_user()
    with User() as user_db:
        user_db.validate_user(user_id)
    return user_id


@pytest.fixture
def create_invalid_user():
    return create_user()


@pytest.fixture
def create_and_validate_dummy_user():
    return create_valid_user()


@pytest.fixture
def admin_headers():
    token = create_access_token(
        to_encode={
            "is_admin": True,
            "user_id": "1",
        },
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers():
    token = create_access_token(
        to_encode={
            "is_admin": False,
            "user_id": create_valid_user(),
        },
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def create_mock_task():
    with Task() as task_db:
        task = task_db.create_task(
            title="Test task",
            description="Task to create something",
            due_date="2012-12-12",
        )
    return task.id
