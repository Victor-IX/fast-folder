from __future__ import annotations

import sys
from pathlib import Path

import questionary
import typer

from handoff import write_target
from installer import install as run_install
from installer import is_launched_by_double_click
from storage import load_locations, save_locations

RESERVED_NAMES = {"save", "remove", "list", "menu", "go", "install"}

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Save and jump to folder locations.",
)


@app.command()
def save(name: str) -> None:
    """Save the current directory under NAME."""
    if name in RESERVED_NAMES:
        typer.echo(f"'{name}' is a reserved command name, pick another.", err=True)
        raise typer.Exit(1)

    locations = load_locations()
    current_path = str(Path.cwd())

    if name in locations:
        overwrite = typer.confirm(f"'{name}' already points to {locations[name]}. Overwrite?")
        if not overwrite:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

    locations[name] = current_path
    save_locations(locations)
    typer.echo(f"Saved '{name}' -> {current_path}")


@app.command()
def remove(name: str) -> None:
    """Remove a saved location by NAME."""
    locations = load_locations()
    if name not in locations:
        typer.echo(f"No saved location named '{name}'.", err=True)
        raise typer.Exit(1)

    del locations[name]
    save_locations(locations)
    typer.echo(f"Removed '{name}'.")


@app.command(name="list")
def list_locations() -> None:
    """List all saved locations."""
    locations = load_locations()
    if not locations:
        typer.echo("No locations saved yet. Use 'ff save <name>' to add one.")
        return

    name_width = max(len(name) for name in locations)
    for name in sorted(locations):
        typer.echo(f"{name.ljust(name_width)}  {locations[name]}")


@app.command()
def menu() -> None:
    """Pick a saved location from an interactive menu and jump to it."""
    locations = load_locations()
    if not locations:
        typer.echo("No locations saved yet. Use 'ff save <name>' to add one.")
        return

    choices = [questionary.Choice(title=f"{name}  ->  {path}", value=name) for name, path in sorted(locations.items())]
    selected = questionary.select("Jump to:", choices=choices).ask()
    if selected is None:
        raise typer.Exit(0)

    write_target(Path(locations[selected]))


@app.command()
def go(name: str) -> None:
    """Resolve NAME and hand its path off to the shell wrapper."""
    locations = load_locations()
    if name not in locations:
        typer.echo(f"No saved location named '{name}'.", err=True)
        raise typer.Exit(1)

    write_target(Path(locations[name]))


@app.command()
def install() -> None:
    """Copy fast-folder to a permanent location and wire up your PowerShell profile."""
    run_install()


def main() -> None:
    args = sys.argv[1:]
    if not args and is_launched_by_double_click():
        run_install()
        input("\nPress Enter to exit...")
        return
    if args and args[0] not in RESERVED_NAMES and not args[0].startswith("-"):
        sys.argv = [sys.argv[0], "go", *args]
    app()


if __name__ == "__main__":
    main()
