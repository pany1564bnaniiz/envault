"""CLI entry-point for envault using Click."""

from __future__ import annotations

import click

from envault.projects import (
    delete_env,
    delete_project,
    get_all_env,
    get_env,
    set_env,
)
from envault.storage import list_projects


@click.group()
def cli() -> None:
    """envault — securely manage and sync .env files."""


@cli.command("set")
@click.argument("project")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_set(project: str, key: str, value: str, password: str) -> None:
    """Set KEY=VALUE for PROJECT."""
    set_env(project, key, value, password)
    click.echo(f"✔  Set {key} for project '{project}'.")


@cli.command("get")
@click.argument("project")
@click.argument("key")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_get(project: str, key: str, password: str) -> None:
    """Get the value of KEY from PROJECT."""
    try:
        value = get_env(project, key, password)
        click.echo(value)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("list")
@click.argument("project")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_list(project: str, password: str) -> None:
    """List all KEY=VALUE pairs for PROJECT."""
    try:
        env = get_all_env(project, password)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    if not env:
        click.echo(f"No variables stored for project '{project}'.")
        return
    for k, v in sorted(env.items()):
        click.echo(f"{k}={v}")


@cli.command("delete")
@click.argument("project")
@click.argument("key")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_delete(project: str, key: str, password: str) -> None:
    """Delete KEY from PROJECT."""
    try:
        delete_env(project, key, password)
        click.echo(f"✔  Deleted '{key}' from project '{project}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("remove-project")
@click.argument("project")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_remove_project(project: str, password: str) -> None:
    """Remove PROJECT and all its variables."""
    try:
        delete_project(project, password)
        click.echo(f"✔  Removed project '{project}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("projects")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_projects(password: str) -> None:
    """List all stored projects."""
    projects = list_projects(password)
    if not projects:
        click.echo("No projects stored yet.")
        return
    for name in sorted(projects):
        click.echo(name)


if __name__ == "__main__":
    cli()
