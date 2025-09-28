import typer
from typing_extensions import Annotated
import rich
from rich.table import Table
from datetime import datetime
from .services import ProjectService, TaskService
from .exceptions import ToDoListError, ProjectNotFoundError
from .database import get_db_session
from .sqlalchemy_repositories import SqlAlchemyProjectRepository, SqlAlchemyTaskRepository
from .models import TaskStatus

app = typer.Typer(
    help="A professional CLI for managing your ToDoList application.",
    rich_markup_mode="markdown"
)

project_app = typer.Typer(help="Commands for managing projects.")
task_app = typer.Typer(help="Commands for managing tasks.")
app.add_typer(project_app, name="project")
app.add_typer(task_app, name="task")

@project_app.command("create")
def create_project(
        name: Annotated[str, typer.Argument(help="The name of the new project.")],
        description: Annotated[str, typer.Option(help="A short description for the project.")] = ""
):
    rich.print(f"Attempting to create project: [bold cyan]{name}[/bold cyan]")
    try:
        with get_db_session() as db_session:
            repo = SqlAlchemyProjectRepository(session=db_session)
            service = ProjectService(project_repo=repo)
            project = service.create_project(name=name, description=description)

        rich.print(f"[bold green]Project '{project.name}' created successfully![/bold green]")

    except ToDoListError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@project_app.command("list")
def list_projects():
    try:
        with get_db_session() as db_session:
            repo = SqlAlchemyProjectRepository(session=db_session)
            service = ProjectService(project_repo=repo)
            all_projects = service.get_all_projects()

            if not all_projects:
                rich.print("[yellow]No projects found.[/yellow]")
                return

            table = Table("ID", "Name", "Description", "Created At")
            for proj in all_projects:
                table.add_row(
                    str(proj.id),
                    proj.name,
                    proj.description or "-",
                    str(proj.created_at.date()) if proj.created_at else "-"
                )
            rich.print(table)

    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@project_app.command("delete")
def delete_project(
        project_id: Annotated[int, typer.Argument(help="The ID of the project to delete.")]
):
    rich.print(f"Attempting to delete project with ID: [bold cyan]{project_id}[/bold cyan]")
    try:
        with get_db_session() as db_session:
            repo = SqlAlchemyProjectRepository(session=db_session)
            service = ProjectService(project_repo=repo)
            service.delete_project_by_id(project_id)

        rich.print(f"[bold green]Project {project_id} deleted successfully![/bold green]")

    except ToDoListError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@task_app.command("create")
def add_task(
        project_id: Annotated[int, typer.Argument(help="The ID of the project to add the task to.")],
        title: Annotated[str, typer.Argument(help="The title of the task.")],
        description: Annotated[str, typer.Option(help="A description for the task.")] = None,
        deadline_str: Annotated[
            str, typer.Option("--deadline", help="The deadline for the task in YYYY-MM-DD format.")] = None,
):
    rich.print(f"Attempting to add task '[bold cyan]{title}[/bold cyan]' to project {project_id}...")

    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        except ValueError:
            rich.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")
            raise typer.Exit(code=1)

    try:
        with get_db_session() as db_session:
            project_repo = SqlAlchemyProjectRepository(session=db_session)
            task_repo = SqlAlchemyTaskRepository(session=db_session)
            service = TaskService(task_repo=task_repo, project_repo=project_repo)

            task = service.add_task_to_project(
                project_id=project_id,
                title=title,
                description=description,
                deadline=deadline
            )

        rich.print(f"[bold green]Task '{task.title}' added to project successfully![/bold green]")

    except ToDoListError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@task_app.command("list")
def list_tasks(
        project_id: Annotated[int, typer.Argument(help="The ID of the project whose tasks you want to see.")]
):
    try:
        with get_db_session() as db_session:
            project_repo = SqlAlchemyProjectRepository(session=db_session)
            project = project_repo.get_by_id(project_id)
            if not project:
                raise ProjectNotFoundError(project_id)

            task_repo = SqlAlchemyTaskRepository(session=db_session)
            tasks = task_repo.get_all_for_project(project_id)

            rich.print(f"Tasks for Project: [bold cyan]{project.name}[/bold cyan]")
            if not tasks:
                rich.print("[yellow]No tasks found for this project.[/yellow]")
                return

            table = Table("ID", "Title", "Status", "Deadline", "Closed At")
            for task in tasks:
                table.add_row(
                    str(task.id),
                    task.title,
                    task.status.value,
                    str(task.deadline.date()) if task.deadline else "-",
                    str(task.closed_at) if task.closed_at else "-"
                )
            rich.print(table)

    except ToDoListError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@task_app.command("status")
def change_task_status(
        task_id: Annotated[int, typer.Argument(help="The ID of the task to update.")],
        status: Annotated[TaskStatus, typer.Argument(help="The new status (todo, doing, or done).")]
):
    rich.print(f"Attempting to change status of task {task_id} to [bold cyan]{status.value}[/bold cyan]...")
    try:
        with get_db_session() as db_session:
            project_repo = SqlAlchemyProjectRepository(session=db_session)  # Needed by TaskService
            task_repo = SqlAlchemyTaskRepository(session=db_session)
            service = TaskService(task_repo=task_repo, project_repo=project_repo)
            service.change_task_status(task_id=task_id, new_status=status)

        rich.print(f"[bold green]Task {task_id} status updated successfully![/bold green]")
    except ToDoListError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()