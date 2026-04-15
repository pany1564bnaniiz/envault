"""CLI commands for managing project aliases."""

from __future__ import annotations

import sys
import click

from envault.aliases import set_alias, remove_alias, resolve_alias, list_aliases


def register_alias_commands(cli: click.Group) -> None:
    """Attach the 'alias' command group to *cli*."""
    cli.add_command(cmd_alias)


@click.group("alias")
def cmd_alias() -> None:
    """Manage short aliases for project names."""


@cmd_alias.command("set")
@click.argument("alias")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE", help="Path to the vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt_input=True)
def alias_set(alias: str, project: str, store: str, password: str) -> None:
    """Bind ALIAS to PROJECT."""
    try:
        set_alias(store, password, alias, project)
        click.echo(f"Alias '{alias}' -> '{project}' saved.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_alias.command("remove")
@click.argument("alias")
@click.option("--store", required=True, envvar="ENVAULT_STORE", help="Path to the vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def alias_remove(alias: str, store: str, password: str) -> None:
    """Remove ALIAS."""
    try:
        remove_alias(store, password, alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@cmd_alias.command("list")
@click.option("--store", required=True, envvar="ENVAULT_STORE", help="Path to the vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def alias_list(store: str, password: str) -> None:
    """List all aliases."""
    mapping = list_aliases(store, password)
    if not mapping:
        click.echo("No aliases defined.")
        return
    for alias, project in sorted(mapping.items()):
        click.echo(f"{alias} -> {project}")


@cmd_alias.command("resolve")
@click.argument("alias")
@click.option("--store", required=True, envvar="ENVAULT_STORE", help="Path to the vault file.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def alias_resolve(alias: str, store: str, password: str) -> None:
    """Print the project name that ALIAS maps to."""
    project = resolve_alias(store, password, alias)
    click.echo(project)
