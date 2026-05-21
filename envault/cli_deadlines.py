"""CLI commands for deadline management."""
import sys
from datetime import datetime, timezone

import click

from envault.deadlines import (
    delete_deadline,
    get_deadline,
    list_deadlines,
    overdue_projects,
    set_deadline,
)


def register_deadline_commands(cli, store_file_opt, password_opt):
    @cli.group("deadline")
    def cmd_deadline():
        """Manage project deadlines."""

    @cmd_deadline.command("set")
    @store_file_opt
    @password_opt
    @click.argument("project")
    @click.argument("due")  # ISO-8601 string
    @click.option("--label", default="", help="Short description of the deadline.")
    def deadline_set(store, password, project, due, label):
        """Set a deadline for PROJECT (due date as ISO-8601)."""
        try:
            due_dt = datetime.fromisoformat(due)
        except ValueError:
            click.echo(f"Invalid date format: {due}", err=True)
            sys.exit(1)
        try:
            set_deadline(store, password, project, due_dt, label=label)
            click.echo(f"Deadline set for '{project}': {due}")
        except KeyError as exc:
            click.echo(str(exc), err=True)
            sys.exit(1)

    @cmd_deadline.command("get")
    @store_file_opt
    @password_opt
    @click.argument("project")
    def deadline_get(store, password, project):
        """Show the deadline for PROJECT."""
        info = get_deadline(store, password, project)
        if info is None:
            click.echo(f"No deadline set for '{project}'.")
        else:
            label = f" ({info['label']})" if info["label"] else ""
            click.echo(f"{project}: {info['due']}{label}")

    @cmd_deadline.command("delete")
    @store_file_opt
    @password_opt
    @click.argument("project")
    def deadline_delete(store, password, project):
        """Remove the deadline for PROJECT."""
        try:
            delete_deadline(store, password, project)
            click.echo(f"Deadline removed for '{project}'.")
        except KeyError as exc:
            click.echo(str(exc), err=True)
            sys.exit(1)

    @cmd_deadline.command("list")
    @store_file_opt
    @password_opt
    def deadline_list(store, password):
        """List all deadlines sorted by due date."""
        entries = list_deadlines(store, password)
        if not entries:
            click.echo("No deadlines set.")
        for e in entries:
            label = f" ({e['label']})" if e["label"] else ""
            click.echo(f"{e['project']}: {e['due']}{label}")

    @cmd_deadline.command("overdue")
    @store_file_opt
    @password_opt
    def deadline_overdue(store, password):
        """List projects whose deadline has already passed."""
        entries = overdue_projects(store, password)
        if not entries:
            click.echo("No overdue projects.")
        for e in entries:
            label = f" ({e['label']})" if e["label"] else ""
            click.echo(f"{e['project']}: {e['due']}{label}")
