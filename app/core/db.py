import os
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Date,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL)
db_session = sessionmaker(bind=engine)


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    admin = Column(Boolean, default=False)
    validated = Column(Boolean, default=False)
    created_at = Column(Date, default=date.today())
    updated_at = Column(DateTime, default=datetime.now())
    tasks = relationship("TaskTable", back_populates="user")


class TaskTable(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(Date, default=date.today())
    completed_at = Column(Date)
    user = relationship("UserTable", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


Base.metadata.create_all(engine)
