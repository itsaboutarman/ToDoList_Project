from __future__ import annotations
import datetime
import enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project

class TaskStatus(enum.Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


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
