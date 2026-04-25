"""CLI commands for managing project watchers."""

from __future__ import annotations

import click

from envault.watchers import add_watcher, remove_watcher, list_watchers, watched_projects


def register_watcher_commands(cli: click.Group) -> None:
    cli.add_command(cmd_watcher)


@click.group("watcher")
def cmd_watcher() -> None:
    """Manage project watchers."""


@cmd_watcher.command("add")
@click.argument("project")
@click.argument("email")
@click.option("--store", envvar="ENVAULT_STORE", required=True, help="Path to vault store.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def watcher_add(project: str, email: str, store: str, password: str) -> None:
    """Add EMAIL as a watcher for PROJECT."""
    try:
        add_watcher(store, password, project, email)
        click.echo(f"Watcher '{email}' added to project '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_watcher.command("remove")
@click.argument("project")
@click.argument("email")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def watcher_remove(project: str, email: str, store: str, password: str) -> None:
    """Remove EMAIL from watchers of PROJECT."""
    removed = remove_watcher(store, password, project, email)
    if removed:
        click.echo(f"Watcher '{email}' removed from project '{project}'.")
    else:
        click.echo(f"'{email}' is not watching '{project}'.", err=True)
        raise SystemExit(1)


@cmd_watcher.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def watcher_list(project: str, store: str, password: str) -> None:
    """List all watchers for PROJECT."""
    watchers = list_watchers(store, password, project)
    if watchers:
        for email in watchers:
            click.echo(email)
    else:
        click.echo(f"No watchers for project '{project}'.")


@cmd_watcher.command("projects")
@click.argument("email")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def watcher_projects(email: str, store: str, password: str) -> None:
    """List all projects watched by EMAIL."""
    projects = watched_projects(store, password, email)
    if projects:
        for proj in projects:
            click.echo(proj)
    else:
        click.echo(f"'{email}' is not watching any projects.")
