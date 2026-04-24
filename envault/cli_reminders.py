"""CLI commands for managing project reminders."""
from __future__ import annotations

import time
from datetime import datetime

import click

from envault.reminders import (
    delete_reminder,
    due_reminders,
    get_reminder,
    list_reminders,
    set_reminder,
)


def register_reminder_commands(cli: click.Group) -> None:
    cli.add_command(cmd_reminder)


@click.group("reminder")
def cmd_reminder() -> None:
    """Manage project reminders."""


@cmd_reminder.command("set")
@click.argument("project")
@click.argument("message")
@click.argument("due")  # ISO-8601 or UNIX timestamp string
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def reminder_set(project: str, message: str, due: str, store: str, password: str) -> None:
    """Set a reminder for PROJECT with MESSAGE due at DUE (ISO-8601 datetime)."""
    try:
        due_ts = datetime.fromisoformat(due).timestamp()
    except ValueError:
        raise click.BadParameter(f"Cannot parse date: {due}")
    try:
        set_reminder(store, password, project, message, due_ts)
    except KeyError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Reminder set for '{project}'.")


@cmd_reminder.command("get")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def reminder_get(project: str, store: str, password: str) -> None:
    """Show the reminder for PROJECT."""
    entry = get_reminder(store, password, project)
    if entry is None:
        click.echo("No reminder set.")
    else:
        due_str = datetime.fromtimestamp(entry["due"]).isoformat()
        click.echo(f"Due: {due_str}\nMessage: {entry['message']}")


@cmd_reminder.command("delete")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def reminder_delete(project: str, store: str, password: str) -> None:
    """Delete the reminder for PROJECT."""
    delete_reminder(store, password, project)
    click.echo(f"Reminder for '{project}' deleted.")


@cmd_reminder.command("list")
@click.option("--due", is_flag=True, default=False, help="Show only overdue reminders.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def reminder_list(due: bool, store: str, password: str) -> None:
    """List all reminders (or only overdue ones with --due)."""
    entries = due_reminders(store, password) if due else list_reminders(store, password)
    if not entries:
        click.echo("No reminders found.")
        return
    for entry in entries:
        due_str = datetime.fromtimestamp(entry["due"]).isoformat()
        click.echo(f"{entry['project']:<20} {due_str}  {entry['message']}")
