import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped


Base = declarative_base()

class TaskStatus(enum.Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = Column(String(500), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(150), nullable=False)
    description: Mapped[Optional[str]] = Column(String(500), nullable=True)
    status: Mapped[TaskStatus] = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    deadline: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    project_id: Mapped[int] = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
