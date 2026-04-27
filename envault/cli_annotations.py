"""CLI commands for per-key annotations."""

from __future__ import annotations

import click

from envault.annotations import (
    set_annotation,
    get_annotation,
    delete_annotation,
    list_annotations,
)


def register_annotation_commands(cli: click.Group) -> None:
    cli.add_command(cmd_annotation)


@click.group("annotation")
def cmd_annotation() -> None:
    """Manage per-key annotations."""


@cmd_annotation.command("set")
@click.argument("project")
@click.argument("key")
@click.argument("note")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def annotation_set(project: str, key: str, note: str, store: str, password: str) -> None:
    """Attach NOTE to KEY in PROJECT."""
    try:
        entry = set_annotation(store, password, project, key, note)
        click.echo(f"Annotation set for '{key}' (updated_at={entry['updated_at']}).")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_annotation.command("get")
@click.argument("project")
@click.argument("key")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def annotation_get(project: str, key: str, store: str, password: str) -> None:
    """Show annotation for KEY in PROJECT."""
    entry = get_annotation(store, password, project, key)
    if entry is None:
        click.echo(f"No annotation for '{key}'.")
    else:
        click.echo(f"{entry['note']}  (updated_at={entry['updated_at']})")


@cmd_annotation.command("delete")
@click.argument("project")
@click.argument("key")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def annotation_delete(project: str, key: str, store: str, password: str) -> None:
    """Remove annotation for KEY in PROJECT."""
    removed = delete_annotation(store, password, project, key)
    if removed:
        click.echo(f"Annotation for '{key}' deleted.")
    else:
        click.echo(f"No annotation found for '{key}'.")


@cmd_annotation.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def annotation_list(project: str, store: str, password: str) -> None:
    """List all annotations for PROJECT."""
    entries = list_annotations(store, password, project)
    if not entries:
        click.echo("No annotations.")
        return
    for key, entry in sorted(entries.items()):
        click.echo(f"{key}: {entry['note']}  (updated_at={entry['updated_at']})")
