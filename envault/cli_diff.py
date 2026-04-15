"""CLI commands for diff and snapshot management."""

from __future__ import annotations

import click

from envault.diff import diff_envs, format_diff
from envault.projects import get_all_env
from envault.snapshots import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


def register_diff_commands(cli: click.Group) -> None:
    cli.add_command(cmd_snapshot)
    cli.add_command(cmd_diff)


@click.group("snapshot")
def cmd_snapshot() -> None:
    """Manage named env snapshots."""


@cmd_snapshot.command("save")
@click.argument("project")
@click.argument("name")
@click.password_option("--password", "-p", prompt="Master password")
def snapshot_save(project: str, name: str, password: str) -> None:
    """Save current env of PROJECT as snapshot NAME."""
    try:
        save_snapshot(project, name, password)
        click.echo(f"Snapshot '{name}' saved for project '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_snapshot.command("list")
@click.argument("project")
@click.password_option("--password", "-p", prompt="Master password")
def snapshot_list(project: str, password: str) -> None:
    """List snapshots for PROJECT."""
    names = list_snapshots(project, password)
    if not names:
        click.echo(f"No snapshots for project '{project}'.")
    else:
        for n in names:
            click.echo(n)


@cmd_snapshot.command("delete")
@click.argument("project")
@click.argument("name")
@click.password_option("--password", "-p", prompt="Master password")
def snapshot_delete(project: str, name: str, password: str) -> None:
    """Delete snapshot NAME from PROJECT."""
    try:
        delete_snapshot(project, name, password)
        click.echo(f"Snapshot '{name}' deleted.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@click.command("diff")
@click.argument("project")
@click.argument("snapshot")
@click.option("--reveal", is_flag=True, default=False, help="Show actual values.")
@click.password_option("--password", "-p", prompt="Master password")
def cmd_diff(project: str, snapshot: str, reveal: bool, password: str) -> None:
    """Diff current env of PROJECT against SNAPSHOT."""
    try:
        old = load_snapshot(project, snapshot, password)
        new = get_all_env(project, password)
        entries = diff_envs(old, new)
        click.echo(format_diff(entries, mask_values=not reveal))
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
