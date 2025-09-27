from __future__ import annotations
import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .task import Task


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = Column(String(500), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
