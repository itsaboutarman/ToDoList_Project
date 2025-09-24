class ToDoListError(Exception):
    # base exception class for this application
    pass

class DuplicateProjectNameError(ToDoListError):
    # raised when trying to create a project with a name that already exists
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"A project with the name '{name}' already exists.")

class ProjectNotFoundError(ToDoListError):
    # raised when a project is not found by its ID or name
    def __init__(self, identifier: int | str):
        super().__init__(f"Project with identifier '{identifier}' not found.")

class ProjectLimitExceededError(ToDoListError):
    # raised when the maximum number of projects has been reached
    def __init__(self, limit: int):
        super().__init__(f"Cannot create new project. The maximum limit of {limit} projects has been reached.")

class TaskNotFoundError(ToDoListError):
    # raised when a task is not found by its ID
    def __init__(self, task_id: int):
        super().__init__(f"Task with ID '{task_id}' not found.")

class TaskLimitExceededError(ToDoListError):
    # raised when the maximum number of tasks for a project has been reached
    def __init__(self, project_name: str, limit: int):
        super().__init__(f"Cannot add new task to '{project_name}'. The maximum limit of {limit} tasks has been reached.")

class InvalidTaskStateError(ToDoListError):
    # raised for invalid operations related to task state
    pass