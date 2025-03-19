from datetime import date, datetime

from app.core.db import UserTable, TaskTable, engine
from sqlalchemy.orm import scoped_session, sessionmaker, subqueryload, Query
from sqlalchemy import update, delete, asc, desc, null


class DBContext:
    def __init__(self):

        self._engine = engine
        self.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False,
            )
        )

    def end_session(self):
        if self.session:
            self.session.commit()
            self.session.close()

    """
    Creating it as a context manager allows me to 
    commit all transactions in 1 session and then automatically 
    close when I am finished.
    """

    def __enter__(self):
        self.session = self.session()  # type: ignore
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_session()


class User(DBContext):
    def __init__(self):
        super().__init__()

    def create_user(self, username, password):
        user = UserTable(username=username, password=password, admin=False)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_id(self, user_id):

        return (
            self.session.query(UserTable)
            .filter(UserTable.id == user_id)
            .options(subqueryload(UserTable.tasks))
            .first()
        )

    def get_all_validated_users(self, order_by_column=None, order_direction="asc"):

        query = (
            self.session.query(UserTable)
            .filter(UserTable.validated == True)
            .options(subqueryload(UserTable.tasks))
        )

        if order_by_column:
            if order_direction == "desc":
                query = query.order_by(desc(order_by_column))
            else:
                query = query.order_by(asc(order_by_column))

        return query.all()

    def get_user_by_username(self, username: str) -> UserTable | None:
        return (
            self.session.query(UserTable).filter(UserTable.username == username).first()
        )

    def validate_user(self, user_id: str) -> None:

        stmt = update(UserTable).where(UserTable.id == user_id).values(validated=True)
        self.session.execute(stmt)


class Task(DBContext):
    def __init__(self):
        super().__init__()

    def create_task(self, title: str, description: str, due_date: date) -> TaskTable:
        task = TaskTable(title=title, description=description, due_date=due_date)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_task(self, task_id: int) -> TaskTable | None:

        return self.session.query(TaskTable).filter(TaskTable.id == task_id).first()

    def get_all_assigned_tasks(self) -> Query[TaskTable]:

        return self.session.query(TaskTable).filter(TaskTable.assigned_to.is_not(None))

    def get_all_unassigned_tasks(self) -> Query[TaskTable]:

        return self.session.query(TaskTable).filter(TaskTable.assigned_to == None)

    async def assign_task(self, task_id: int, user_id: int) -> None:

        stmt = (
            update(TaskTable).where(TaskTable.id == task_id).values(assigned_to=user_id)
        )
        self.session.execute(stmt)

        stmt = (
            update(UserTable)
            .where(UserTable.id == user_id)
            .values(updated_at=datetime.now())
        )
        self.session.execute(stmt)

    def delete_task(self, task_id: int) -> None:
        stmt = delete(TaskTable).where(TaskTable.id == task_id)
        self.session.execute(stmt)

    def reject_task(self, task_id: int) -> None:
        stmt = (
            update(TaskTable)
            .where(TaskTable.id == task_id)
            .values(assigned_to=null())
            .values(completed_at=null())
        )
        self.session.execute(stmt)

    def complete_task(self, task_id: int) -> None:

        today = date.today().strftime("%Y-%m-%d")
        stmt = (
            update(TaskTable).where(TaskTable.id == task_id).values(completed_at=today)
        )
        self.session.execute(stmt)
