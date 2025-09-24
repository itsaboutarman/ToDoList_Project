from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Project, Task
from abc import ABC, abstractmethod

class ProjectRepository(ABC):
# This is the interface for all project-related data operations
    @abstractmethod
    def add(self, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, project_id: int) -> Optional[Project]:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, project_name: str) -> Optional[Project]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[Project]:
        raise NotImplementedError

    @abstractmethod
    def update(self, project: Project) -> Project:
        raise NotImplementedError

    @abstractmethod
    def delete(self, project_id: int) -> None:
        raise NotImplementedError



class TaskRepository(ABC):
# This is the interface for all task-related data operations
    @abstractmethod
    def add(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, task_name: str) -> Optional[Task]:
        raise NotImplementedError

    @abstractmethod
    def get_all_for_project(self, project_id: int) -> List[Task]:
    # The list of all tasks for specific project
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_id: int) -> None:
        raise NotImplementedError




class SqlAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, project: Project) -> Project:
        self.session.add(project)
        self.session.flush()
        return project

    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.session.get(Project, project_id)

    def get_by_name(self, project_name: str) -> Optional[Project]:
        statement = select(Project).filter_by(name=project_name)
        return self.session.scalars(statement).first()

    def get_all(self) -> List[Project]:
        statement = select(Project)
        return list(self.session.scalars(statement).all())

    def update(self, project: Project) -> Project:
        self.session.add(project)
        self.session.flush()
        return project

    def delete(self, project_id: int) -> None:
        project = self.get_by_id(project_id)
        if project:
            self.session.delete(project)
            self.session.flush()