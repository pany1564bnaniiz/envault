"""CLI commands for archiving and restoring projects."""

from __future__ import annotations

import sys

import click

from envault.archive import archive_project, list_archived, purge_archived, restore_project


def register_archive_commands(cli: click.Group) -> None:
    cli.add_command(cmd_archive)


@click.group("archive")
def cmd_archive() -> None:
    """Archive, restore, or purge projects."""


@cmd_archive.command("add")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True, help="Path to vault store.")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt=False, required=True)
def archive_add(project: str, store: str, password: str) -> None:
    """Archive PROJECT (soft-delete, recoverable)."""
    try:
        archive_project(store, password, project)
        click.echo(f"Project '{project}' archived.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_archive.command("restore")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt=False, required=True)
def archive_restore(project: str, store: str, password: str) -> None:
    """Restore an archived PROJECT back to active storage."""
    try:
        restore_project(store, password, project)
        click.echo(f"Project '{project}' restored.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_archive.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt=False, required=True)
def archive_list(store: str, password: str) -> None:
    """List all archived projects."""
    entries = list_archived(store, password)
    if not entries:
        click.echo("No archived projects.")
        return
    for entry in entries:
        click.echo(f"{entry['project']}  (archived: {entry['archived_at']})")


@cmd_archive.command("purge")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", prompt=False, required=True)
@click.confirmation_option(prompt="Permanently delete this archived project?")
def archive_purge(project: str, store: str, password: str) -> None:
    """Permanently delete an archived PROJECT."""
    try:
        purge_archived(store, password, project)
        click.echo(f"Archived project '{project}' permanently deleted.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
