# -*- coding: utf-8 -*-
# prism/rich_handler.py

from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.padding import Padding
from rich.style import Style

from .exceptions import (
    PrismError,
    TemplatedPrismError,
    AssetValidationError,
    ModelIDMismatchError,
    VariantNotFoundError,
    RecipeReferenceError,
    ResolutionError
)

from contextlib import contextmanager
from typing import Callable, Dict
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from .entities import CompilationSources


def _format_generic(error: TemplatedPrismError) -> Text:
    """A good default formatter for any TemplatedPrismError that doesn't have a custom one."""
    text = Text()
    text.append(error.message, style="bold")
    
    if error.context:
        text.append("\n\nDetails:", style="bold white")
        for key, value in error.context.items():
            # Don't repeat what's already in the formatted message
            if f"{{{key}}}" not in error.message_template:
                text.append(f"\n  • {key}: ", style="cyan")
                text.append(repr(value), style="green")
    return text

def _format_asset_validation(error: AssetValidationError) -> Text:
    """Custom formatter for validation errors to create a nice list."""
    text = Text()
    text.append("Validation failed for asset '", style="bold")
    text.append(error.context['asset_file_name'], style="bold yellow")
    text.append("'.\n", style="bold")
    text.append(f"Found {error.context['error_count']} error(s):", style="default")

    for err_detail in error.context['errors']:
        text.append(f"\n  • {err_detail}", style="default")
    return text

def _format_variant_not_found(error: VariantNotFoundError) -> Text:
    """Custom formatter to make available variants very clear."""
    text = Text()
    text.append("Variant '", style="bold")
    text.append(error.context['variant_id'], style="bold yellow")
    text.append("' not found in Block '", style="bold")
    text.append(error.context['block_id'], style="bold cyan")
    text.append("'.\n\n", style="bold")
    text.append("Available variants are: ", style="default")
    text.append(error.context['available_variants'], style="green")
    return text

def _format_model_id_mismatch(error: ModelIDMismatchError) -> Text:
    """Highlights the conflicting IDs between filename and file content."""
    text = Text()
    text.append("ID Mismatch found in ", style="bold")
    text.append(f"'{error.context['model_type']}'", style="bold cyan")
    text.append(" asset.\n\n", style="bold")
    
    text.append("  • Filename implies ID: ", style="default")
    text.append(f"'{error.context['file_id']}'\n", style="yellow")
    
    text.append("  • File content declares ID: ", style="default")
    text.append(f"'{error.context['content_id']}'\n\n", style="yellow")

    text.append("Action: Please ensure the filename and the 'meta.id' inside the file are identical.", style="bold")
    return text

def _format_resolution_error(error: ResolutionError) -> Text:
    """Clearly shows what couldn't be found and where it was referenced."""
    text = Text()
    text.append("Could not resolve ", style="bold")
    text.append(f"'{error.context['asset_type']}'", style="bold cyan")
    text.append(" with ID '", style="bold")
    text.append(error.context['identifier'], style="bold yellow")
    text.append("'.\n\n", style="bold")

    text.append("This asset was referenced from:\n", style="default")
    text.append(f"  • {error.context['source_context']}\n\n", style="cyan")

    text.append("Hint: Check for typos or ensure the corresponding file is loaded correctly.", style="dim")
    return text

def _format_recipe_reference_error(error: RecipeReferenceError) -> Text:
    """Explains that a composition reference is missing from imports."""
    text = Text()
    text.append("Invalid reference in recipe composition sequence.\n\n", style="bold")
    
    text.append("The reference '", style="default")
    text.append(error.context['reference'], style="bold yellow")
    text.append("' is used in the ", style="default")
    text.append("'composition.sequence'", style="cyan")
    text.append(", but it is not defined in the ", style="default")
    text.append("'imports'", style="cyan")
    text.append(" section.\n\n", style="default")

    text.append("Action: Add an entry for this reference in the 'imports' section of your recipe.", style="bold")
    return text


def handle_exception(error: Exception):
    """
    The main entry point for pretty-printing Prism exceptions using rich.
    It acts as a dispatcher, matching the exception type to the best
    available formatter for maximum clarity.
    """
    console = Console(stderr=True, theme=None)
    
    title = f"[bold red]Error: {error.__class__.__name__}[/bold red]"
    content: Any = str(error) # Default content for unexpected errors

    if isinstance(error, AssetValidationError):
        content = _format_asset_validation(error)
    elif isinstance(error, VariantNotFoundError):
        content = _format_variant_not_found(error)
    elif isinstance(error, ModelIDMismatchError):
        content = _format_model_id_mismatch(error)
    elif isinstance(error, ResolutionError):
        content = _format_resolution_error(error)
    elif isinstance(error, RecipeReferenceError):
        content = _format_recipe_reference_error(error)

    elif isinstance(error, TemplatedPrismError):
        # This catches all your other custom errors that don't have a
        # special formatter and displays them nicely.
        content = _format_generic(error)
    elif isinstance(error, PrismError):
        # For base PrismError that isn't templated
        content = Text(error.message, style="bold")

    # Add padding to the content for better readability
    padded_content = Padding(content, (1, 2))

    console.print(
        Panel(
            padded_content,
            title=title,
            border_style="red",
            expand=False
        )
    )
