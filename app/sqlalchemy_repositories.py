from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Project, Task
from repositories import ProjectRepository, TaskRepository


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


class SqlAlchemyTaskRepository(TaskRepository):
    # The concrete SQLAlchemy implementation of the Task Repository.
    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        return task

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_by_name(self, task_name: str) -> Optional[Task]:
        statement = select(Task).where(Task.title == task_name)
        return self.session.scalar(statement)

    def get_all_for_project(self, project_id: int) -> List[Task]:
        statement = select(Task).where(Task.project_id == project_id)
        return list(self.session.scalars(statement).all())

    def update(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        return task

    def delete(self, task_id: int) -> None:
        task = self.get_by_id(task_id)
        if task:
            self.session.delete(task)
            self.session.flush()
