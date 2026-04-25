"""CLI commands for managing workflows."""
from __future__ import annotations

import json

import click

from envault.workflows import (
    delete_workflow,
    list_workflows,
    load_workflow,
    save_workflow,
)


def register_workflow_commands(cli: click.Group, store_file: click.Path) -> None:  # noqa: ARG001
    """Attach the `workflow` command group to the root CLI."""
    cli.add_command(cmd_workflow)


@click.group("workflow")
def cmd_workflow() -> None:
    """Manage named workflows (sequences of operations)."""


@cmd_workflow.command("save")
@click.argument("name")
@click.argument("steps_json")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def workflow_save(name: str, steps_json: str, store: str, password: str) -> None:
    """Save a workflow from a JSON array of step objects."""
    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON: {exc}") from exc
    try:
        save_workflow(store, password, name, steps)
    except (ValueError, KeyError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Workflow '{name}' saved ({len(steps)} step(s)).")


@cmd_workflow.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def workflow_list(store: str, password: str) -> None:
    """List all saved workflows."""
    names = list_workflows(store, password)
    if not names:
        click.echo("No workflows saved.")
    else:
        for name in names:
            click.echo(name)


@cmd_workflow.command("show")
@click.argument("name")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def workflow_show(name: str, store: str, password: str) -> None:
    """Print the steps of a workflow as JSON."""
    try:
        steps = load_workflow(store, password, name)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(steps, indent=2))


@cmd_workflow.command("delete")
@click.argument("name")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def workflow_delete(name: str, store: str, password: str) -> None:
    """Delete a saved workflow."""
    try:
        delete_workflow(store, password, name)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Workflow '{name}' deleted.")
