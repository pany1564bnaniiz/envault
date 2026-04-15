"""CLI commands for project tag management."""

from __future__ import annotations

import sys

import click

from envault import tags as tag_mod


def register_tag_commands(cli: click.Group) -> None:
    """Attach tag sub-commands to *cli*."""
    cli.add_command(cmd_tag)


@click.group("tag")
def cmd_tag() -> None:
    """Manage tags on projects."""


@cmd_tag.command("add")
@click.argument("project")
@click.argument("tag")
@click.option("--store", envvar="ENVAULT_STORE", required=True, help="Path to store file.")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def tag_add(project: str, tag: str, store: str, password: str) -> None:
    """Add TAG to PROJECT."""
    try:
        tag_mod.add_tag(store, password, project, tag)
        click.echo(f"Tag '{tag}' added to project '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_tag.command("remove")
@click.argument("project")
@click.argument("tag")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def tag_remove(project: str, tag: str, store: str, password: str) -> None:
    """Remove TAG from PROJECT."""
    try:
        tag_mod.remove_tag(store, password, project, tag)
        click.echo(f"Tag '{tag}' removed from project '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_tag.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def tag_list(project: str, store: str, password: str) -> None:
    """List tags for PROJECT."""
    try:
        result = tag_mod.list_tags(store, password, project)
        if result:
            click.echo("\n".join(result))
        else:
            click.echo(f"No tags for project '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_tag.command("find")
@click.argument("tag")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def tag_find(tag: str, store: str, password: str) -> None:
    """List all projects that carry TAG."""
    projects = tag_mod.projects_by_tag(store, password, tag)
    if projects:
        click.echo("\n".join(projects))
    else:
        click.echo(f"No projects found with tag '{tag}'.")


@cmd_tag.command("rename")
@click.argument("old_tag")
@click.argument("new_tag")
@click.option("--store", envvar="ENVAULT_STORE", required=True, help="Path to store file.")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def tag_rename(old_tag: str, new_tag: str, store: str, password: str) -> None:
    """Rename OLD_TAG to NEW_TAG across all projects."""
    try:
        affected = tag_mod.rename_tag(store, password, old_tag, new_tag)
        if affected:
            click.echo(f"Tag '{old_tag}' renamed to '{new_tag}' on {affected} project(s).")
        else:
            click.echo(f"No projects found with tag '{old_tag}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
