"""CLI commands for stale project detection."""

from __future__ import annotations

import sys
from datetime import datetime

import click

from envault.stale import get_last_active, list_stale, mark_stale, touch_project


def register_stale_commands(cli: click.Group) -> None:
    cli.add_command(cmd_stale)


@click.group("stale")
def cmd_stale() -> None:
    """Manage stale project detection."""


@cmd_stale.command("touch")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def stale_touch(project: str, store: str, password: str) -> None:
    """Mark PROJECT as recently active."""
    try:
        ts = touch_project(store, password, project)
        dt = datetime.fromtimestamp(ts).isoformat()
        click.echo(f"Touched '{project}' at {dt}.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_stale.command("get")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def stale_get(project: str, store: str, password: str) -> None:
    """Show the last-active timestamp for PROJECT."""
    ts = get_last_active(store, password, project)
    if ts is None:
        click.echo(f"'{project}' has never been touched (stale).")
    else:
        dt = datetime.fromtimestamp(ts).isoformat()
        click.echo(f"Last active: {dt}")


@cmd_stale.command("mark")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def stale_mark(project: str, store: str, password: str) -> None:
    """Explicitly mark PROJECT as stale."""
    mark_stale(store, password, project)
    click.echo(f"'{project}' marked as stale.")


@cmd_stale.command("list")
@click.option("--days", default=30, show_default=True, help="Inactivity threshold.")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def stale_list(days: int, store: str, password: str) -> None:
    """List projects inactive for more than DAYS days."""
    entries = list_stale(store, password, days=days)
    if not entries:
        click.echo("No stale projects found.")
        return
    for entry in entries:
        last = entry["last_active"]
        last_str = datetime.fromtimestamp(last).isoformat() if last else "never"
        click.echo(f"{entry['project']}  (last active: {last_str})")
