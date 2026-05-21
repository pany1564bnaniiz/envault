"""CLI commands for project status management."""

import click

from envault.status import (
    _VALID_STATUSES,
    get_status,
    list_statuses,
    projects_by_status,
    remove_status,
    set_status,
)


def register_status_commands(cli: click.Group) -> None:
    cli.add_command(cmd_status)


@click.group("status")
def cmd_status() -> None:
    """Manage project status labels."""


@cmd_status.command("set")
@click.argument("project")
@click.argument("status", type=click.Choice(sorted(_VALID_STATUSES)))
@click.option("--note", default=None, help="Optional note about the status change.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def status_set(project: str, status: str, note: str, store: str, password: str) -> None:
    """Set the status of PROJECT."""
    try:
        entry = set_status(store, password, project, status, note=note)
        click.echo(f"Status for '{project}' set to '{entry['status']}'.")
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}")


@cmd_status.command("get")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def status_get(project: str, store: str, password: str) -> None:
    """Show the status of PROJECT."""
    entry = get_status(store, password, project)
    if entry is None:
        click.echo(f"No status set for '{project}'.")
    else:
        click.echo(f"status   : {entry['status']}")
        click.echo(f"updated  : {entry['updated_at']}")
        if entry.get("note"):
            click.echo(f"note     : {entry['note']}")


@cmd_status.command("remove")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def status_remove(project: str, store: str, password: str) -> None:
    """Remove the status label from PROJECT."""
    removed = remove_status(store, password, project)
    if removed:
        click.echo(f"Status removed for '{project}'.")
    else:
        click.echo(f"No status found for '{project}'.")


@cmd_status.command("list")
@click.option("--filter", "filter_status", default=None,
              type=click.Choice(sorted(_VALID_STATUSES)),
              help="Filter by a specific status value.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def status_list(filter_status: str, store: str, password: str) -> None:
    """List all project statuses."""
    if filter_status:
        projects = projects_by_status(store, password, filter_status)
        if not projects:
            click.echo(f"No projects with status '{filter_status}'.")
        for proj in sorted(projects):
            click.echo(proj)
    else:
        mapping = list_statuses(store, password)
        if not mapping:
            click.echo("No statuses recorded.")
        for proj, entry in sorted(mapping.items()):
            click.echo(f"{proj}: {entry['status']}")
