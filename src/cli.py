from __future__ import annotations

import sys
from pathlib import Path

import questionary
import typer

from handoff import write_target
from installer import install as run_install
from installer import is_launched_by_double_click
from matching import ambiguous_matches, is_clear_winner, rank
from storage import load_locations, save_locations

RESERVED_NAMES = {"save", "remove", "list", "menu", "go", "install"}

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Save and jump to folder locations.",
)


def sorted_names(locations: dict[str, str]) -> list[str]:
    """Saved names in alphabetical order, ignoring case."""
    return sorted(locations, key=str.lower)


def resolve_name(query: str, locations: dict[str, str]) -> str:
    """Turn user input into a saved name, tolerating typos and partial names.

    Exits with an error when nothing matches, and prompts to disambiguate when
    several saved names are equally plausible.
    """
    if query in locations:
        return query

    matches = rank(query, locations)
    if not matches:
        typer.echo(f"No saved location matching '{query}'. Use 'ff list' to see what's saved.", err=True)
        raise typer.Exit(1)

    if is_clear_winner(matches):
        best = matches[0][0]
        if best != query:
            typer.echo(f"Matched '{best}'.")
        return best

    candidates = ambiguous_matches(matches)
    choices = [questionary.Choice(title=f"{name}  ->  {locations[name]}", value=name) for name in candidates]
    selected = questionary.select(f"Several matches for '{query}':", choices=choices).ask()
    if selected is None:
        raise typer.Exit(0)
    return selected


@app.command()
def save(name: str = typer.Argument(None)) -> None:
    """Save the current directory under NAME. Defaults to the current folder's name."""
    current_path = str(Path.cwd())

    if name is None:
        name = Path.cwd().name

    if name in RESERVED_NAMES:
        typer.echo(f"'{name}' is a reserved command name, pick another.", err=True)
        raise typer.Exit(1)

    locations = load_locations()

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
    resolved = resolve_name(name, locations)

    if resolved != name and not typer.confirm(f"Remove '{resolved}' ({locations[resolved]})?"):
        typer.echo("Cancelled.")
        raise typer.Exit(0)

    del locations[resolved]
    save_locations(locations)
    typer.echo(f"Removed '{resolved}'.")


@app.command(name="list")
def list_locations() -> None:
    """List all saved locations, alphabetically."""
    locations = load_locations()
    if not locations:
        typer.echo("No locations saved yet. Use 'ff save <name>' to add one.")
        return

    name_width = max(len(name) for name in locations)
    for name in sorted_names(locations):
        path = locations[name]
        suffix = "" if Path(path).is_dir() else "  (missing)"
        typer.echo(f"{name.ljust(name_width)}  {path}{suffix}")


@app.command()
def menu() -> None:
    """Pick a saved location from an interactive menu and jump to it."""
    locations = load_locations()
    if not locations:
        typer.echo("No locations saved yet. Use 'ff save <name>' to add one.")
        return

    choices = [
        questionary.Choice(title=f"{name}  ->  {locations[name]}", value=name) for name in sorted_names(locations)
    ]
    selected = questionary.select("Jump to:", choices=choices).ask()
    if selected is None:
        raise typer.Exit(0)

    write_target(Path(locations[selected]))


@app.command()
def go(name: str) -> None:
    """Resolve NAME and hand its path off to the shell wrapper."""
    locations = load_locations()
    if not locations:
        typer.echo("No locations saved yet. Use 'ff save <name>' to add one.")
        raise typer.Exit(1)

    write_target(Path(locations[resolve_name(name, locations)]))


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
    if not args:
        sys.argv = [sys.argv[0], "menu"]
    elif args[0] not in RESERVED_NAMES and not args[0].startswith("-"):
        sys.argv = [sys.argv[0], "go", *args]
    app()


if __name__ == "__main__":
    main()
