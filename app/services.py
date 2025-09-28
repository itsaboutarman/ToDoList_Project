from datetime import datetime
from typing import Optional
from .models import Project, Task, TaskStatus
from .repositories import ProjectRepository, TaskRepository
from .exceptions import (
    DuplicateProjectNameError,
    ProjectNotFoundError,
    TaskNotFoundError,
    ProjectLimitExceededError,
    TaskLimitExceededError,
)

MAX_PROJECTS = 10
MAX_TASKS_PER_PROJECT = 20


class ProjectService:
    # contains the business logic for project-related operations
    def __init__(self, project_repo: ProjectRepository):
        self._repo = project_repo

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        # creates a new project after validating business rules.
        # Business Rule 1: Check if the total number of projects exceeds the limit.
        if len(self._repo.get_all()) >= MAX_PROJECTS:
            raise ProjectLimitExceededError(MAX_PROJECTS)

        # Business Rule 2: Ensure the project name is unique.
        if self._repo.get_by_name(name):
            raise DuplicateProjectNameError(name)

        # If rules pass, create the new model object.
        new_project = Project(name, description)

        # Delegate the actual saving to the repository.
        return self._repo.add(new_project)

    def get_project_by_id(self, project_id: int) -> Project:
        project = self._repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return project

    def get_project_by_name(self, project_name: str) -> Project:
        project = self._repo.get_by_name(project_name)
        if not project:
            raise ProjectNotFoundError(project_name)
        return project

    def get_all_projects(self) -> list[Project]:

        return self._repo.get_all()

    def update_project(self, project_id: int, name: str, description: str) -> Project:
        project_to_update = self.get_project_by_id(project_id)

        # Business Rule: Check for name duplication only if the name is being changed.
        if project_to_update.name != name and self._repo.get_by_name(name):
            raise DuplicateProjectNameError(name)

        project_to_update.name = name
        project_to_update.description = description
        return self._repo.update(project_to_update)

    def delete_project_by_id(self, project_id: int) -> None:
        # Business Rule: Ensure the project exists before attempting to delete.
        self.get_project_by_id(project_id)
        self._repo.delete(project_id)


class TaskService:
    def __init__(self, task_repo: TaskRepository, project_repo: ProjectRepository):
        # This ser vice depends on both repositories.
        self._task_repo = task_repo
        self._project_repo = project_repo

    def add_task_to_project(
            self,
            project_id: int,
            title: str,
            description: Optional[str] = None,
            deadline: Optional[datetime] = None
    ) -> Task:

        # Business Rule 1: The project must exist.
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        # Business Rule 2: Check the task limit for the project.
        if len(self._task_repo.get_all_for_project(project_id)) >= MAX_TASKS_PER_PROJECT:
            raise TaskLimitExceededError(project.name, MAX_TASKS_PER_PROJECT)


        # If rules pass, create the new task object.
        new_task = Task(
            title,
            description,
            deadline,
            project_id
        )

        # Delegate saving to the repository.
        return self._task_repo.add(new_task)

    def get_task_by_id(self, task_id: int) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def get_task_by_name(self, task_name: str) -> Task:
        task = self._task_repo.get_by_name(task_name)
        if not task:
            raise TaskNotFoundError(task_name)
        return task

    def change_task_status(self, task_id: int, new_status: TaskStatus) -> Task:
        task_to_update = self.get_task_by_id(task_id)
        # Business Rule: You could add rules here, e.g., a 'DONE' task cannot be moved back to 'TO DO'
        # For now, we keep it simple.

        task_to_update.status = new_status

        # Business Logic: If a task is marked as done, set its completion time.
        if new_status == TaskStatus.DONE and task_to_update.closed_at is None:
            task_to_update.closed_at = datetime.utcnow()
        elif new_status != TaskStatus.DONE:
            task_to_update.closed_at = None

        return self._task_repo.update(task_to_update)