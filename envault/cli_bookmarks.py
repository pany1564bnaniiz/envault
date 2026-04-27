"""CLI commands for managing bookmarks."""

from __future__ import annotations

import click

from envault.bookmarks import (
    add_bookmark,
    get_bookmark,
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
)


def register_bookmark_commands(cli: click.Group) -> None:
    cli.add_command(cmd_bookmark)


@click.group("bookmark")
def cmd_bookmark() -> None:
    """Manage quick-access bookmarks for project keys."""


@cmd_bookmark.command("add")
@click.argument("name")
@click.argument("project")
@click.argument("key")
@click.option("--desc", default="", help="Optional description.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def bookmark_add(name: str, project: str, key: str, desc: str, store: str, password: str) -> None:
    """Add a bookmark NAME pointing to PROJECT KEY."""
    try:
        add_bookmark(store, password, name, project, key, desc)
        click.echo(f"Bookmark '{name}' -> {project}/{key} saved.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_bookmark.command("remove")
@click.argument("name")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def bookmark_remove(name: str, store: str, password: str) -> None:
    """Remove a bookmark by NAME."""
    try:
        remove_bookmark(store, password, name)
        click.echo(f"Bookmark '{name}' removed.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_bookmark.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def bookmark_list(store: str, password: str) -> None:
    """List all bookmarks."""
    entries = list_bookmarks(store, password)
    if not entries:
        click.echo("No bookmarks saved.")
        return
    for e in entries:
        desc = f"  # {e['description']}" if e["description"] else ""
        click.echo(f"{e['name']}: {e['project']}/{e['key']}{desc}")


@cmd_bookmark.command("get")
@click.argument("name")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def bookmark_get(name: str, store: str, password: str) -> None:
    """Resolve and print the value referenced by bookmark NAME."""
    try:
        value = resolve_bookmark(store, password, name)
        if value is None:
            click.echo(f"Key referenced by '{name}' not found.", err=True)
            raise SystemExit(1)
        click.echo(value)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
