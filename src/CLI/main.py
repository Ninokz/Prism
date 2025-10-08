# -*- coding: utf-8 -*-
# CLI/main.py

import typer
from pathlib import Path
from typing_extensions import Annotated

from rich.console import Console
from rich.panel import Panel

from CLI.actions.initializer import ProjectInitializer
from CLI.actions.scaffolder import Scaffolder
from CLI.actions.loader import ProjectLoader
from CLI.utils.finder import ProjectFinder

from CLI.exception import CLIError, LoaderError

from Prism.core import compile_recipe_to_artifacts
from Prism.exceptions import PrismError

from Prism.rich_handler import handle_exception 

# --- CLI App Initialization ---
app = typer.Typer(
    name="prism",
    help="Prism: A powerful, modular prompt engineering toolkit.",
    add_completion=False
)
console = Console()

# --- Helper Function for Error Handling ---
def handle_cli_error(err: Exception):
    if isinstance(err, PrismError):
        handle_exception(err) 
    elif isinstance(err, CLIError):
        console.print(Panel(f"[bold]{err.__class__.__name__}[/bold]\n\n{err.message}", border_style="red", title="Error"))
    elif isinstance(err, FileNotFoundError):
         console.print(Panel(f"[bold]Project Not Found[/bold]\n\n{err}", border_style="red", title="Error"))
    else:
        console.print(Panel(f"[bold]An unexpected error occurred[/bold]\n\n{err}", border_style="red", title="Error"))
        # 可以在这里添加 traceback 打印，用于调试
        # console.print_exception()

# --- Top-Level Commands ---
@app.command()
def init(
    project_name: Annotated[str, typer.Argument(help="The name of the new project directory.")]
):
    """
    Initializes a new Prism project with the recommended directory structure.
    """
    try:
        project_path = Path(project_name)
        initializer = ProjectInitializer(project_path)
        initializer.run()
    except Exception as e:
        handle_cli_error(e)
        raise typer.Exit(code=1)

@app.command()
def compile(
    recipe_name: Annotated[str, typer.Argument(help="The name of the recipe to compile (without extension).")]
):
    """
    Compiles a recipe into its final prompt template and data model.
    """
    try:
        console.print(f"🚀 [bold]Starting compilation for recipe: [cyan]{recipe_name}[/cyan][/bold]")
        
        # 1. 找到项目根目录
        project_root = ProjectFinder.find_root()
        console.print(f"✅ Found project root at: [green]{project_root}[/green]")
        
        # 2. 初始化 Loader 并加载所有资源
        loader = ProjectLoader(project_root)
        sources = loader.load_compilation_sources()
        task = loader.load_recipe(recipe_name)
        
        # 3. 调用核心库进行编译
        artifacts = compile_recipe_to_artifacts(task, sources)
        
        # 4. 美化输出结果
        console.print("\n✨ [bold green]Compilation Successful![/bold green] ✨")
        
        console.print(Panel(
            artifacts.template_content,
            title="[bold blue]Generated Prompt Template[/bold blue]",
            border_style="blue"
        ))
        
        if artifacts.model_code:
            console.print(Panel(
                artifacts.model_code,
                title="[bold magenta]Generated Pydantic Model[/bold magenta]",
                border_style="magenta"
            ))

    except Exception as e:
        handle_cli_error(e)
        raise typer.Exit(code=1)

# --- "new" Subcommand Group ---

new_app = typer.Typer(name="new", help="Create new Prism files from templates.")
app.add_typer(new_app)

@new_app.command("block")
def new_block(name: Annotated[str, typer.Argument(help="The name of the new block.")]):
    """Creates a new block file (*.block.yaml)."""
    try:
        root = ProjectFinder.find_root()
        scaffolder = Scaffolder(root)
        scaffolder.create_block_file(name)
    except Exception as e:
        handle_cli_error(e)
        raise typer.Exit(code=1)

@new_app.command("recipe")
def new_recipe(name: Annotated[str, typer.Argument(help="The name of the new recipe.")]):
    """Creates a new recipe file (*.recipe.yaml)."""
    try:
        root = ProjectFinder.find_root()
        scaffolder = Scaffolder(root)
        scaffolder.create_recipe_file(name)
    except Exception as e:
        handle_cli_error(e)
        raise typer.Exit(code=1)

@new_app.command("dataschema")
def new_dataschema(name: Annotated[str, typer.Argument(help="The name of the new dataschema.")]):
    """Creates a new dataschema file (*.dataschema.yaml)."""
    try:
        root = ProjectFinder.find_root()
        scaffolder = Scaffolder(root)
        scaffolder.create_dataschema_file(name)
    except Exception as e:
        handle_cli_error(e)
        raise typer.Exit(code=1)

# --- Main Entry Point ---

if __name__ == "__main__":
    app()