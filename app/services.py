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

# --- Constants for Business Rules ---
# In a real application, these would come from a config file or environment variables.
MAX_PROJECTS = 10
MAX_TASKS_PER_PROJECT = 20


class ProjectService:
    """
    This service contains the business logic for project-related operations.
    It's completely decoupled from the database and presentation layers.
    """

    def __init__(self, project_repo: ProjectRepository):
        # The service receives its dependency (the repository) via constructor injection.
        self._repo = project_repo

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """
        Creates a new project after validating business rules.
        """
        # Business Rule 1: Check if the total number of projects exceeds the limit.
        if len(self._repo.get_all()) >= MAX_PROJECTS:
            raise ProjectLimitExceededError(limit=MAX_PROJECTS)

        # Business Rule 2: Ensure the project name is unique.
        if self._repo.get_by_name(name):
            raise DuplicateProjectNameError(name=name)

        # If rules pass, create the new project object.
        new_project = Project(name=name, description=description)

        # Delegate the actual saving to the repository.
        return self._repo.add(new_project)

    def get_project_by_id(self, project_id: int) -> Project:
        """
        Fetches a single project by its ID.
        """
        project = self._repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(identifier=project_id)
        return project

    def get_all_projects(self) -> list[Project]:
        """
        Returns a list of all projects.
        """
        return self._repo.get_all()

    def delete_project(self, project_id: int) -> None:
        """
        Deletes a project by its ID after ensuring it exists.
        """
        # First, ensure the project exists before attempting to delete.
        project_to_delete = self.get_project_by_id(project_id)
        self._repo.delete(project_to_delete.id)


class TaskService:
    """
    This service handles all business logic for task-related operations.
    """

    def __init__(self, task_repo: TaskRepository, project_repo: ProjectRepository):
        # This service depends on both repositories.
        self._task_repo = task_repo
        self._project_repo = project_repo

    def add_task_to_project(
            self,
            project_id: int,
            title: str,
            description: Optional[str] = None,
            deadline: Optional[datetime] = None
    ) -> Task:
        """
        Adds a new task to a specific project.
        """
        # Business Rule 1: The project must exist.
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(identifier=project_id)

        # Business Rule 2: Check if the number of tasks in the project exceeds the limit.
        if len(self._task_repo.get_all_for_project(project_id)) >= MAX_TASKS_PER_PROJECT:
            raise TaskLimitExceededError(project_name=project.name, limit=MAX_TASKS_PER_PROJECT)

        # If rules pass, create the new task object.
        new_task = Task(
            title=title,
            description=description,
            deadline=deadline,
            project_id=project_id
        )

        # Delegate saving to the repository.
        return self._task_repo.add(new_task)

    def get_task_by_id(self, task_id: int) -> Task:
        """
        Fetches a single task by its ID.
        """
        task = self._task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id=task_id)
        return task

    def change_task_status(self, task_id: int, new_status: TaskStatus) -> Task:
        """
        Updates the status of a task.
        """
        task = self.get_task_by_id(task_id)
        task.status = new_status

        # If the task is being marked as done, set the closed_at timestamp.
        if new_status == TaskStatus.DONE:
            task.closed_at = datetime.utcnow()
        else:
            task.closed_at = None  # Ensure it's null if moved back from 'done'

        return self._task_repo.update(task)