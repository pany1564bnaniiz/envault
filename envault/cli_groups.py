"""CLI commands for managing project groups in envault."""

import click
from envault.groups import (
    add_to_group,
    remove_from_group,
    list_groups,
    projects_in_group,
    rename_group,
)


def register_group_commands(cli: click.Group) -> None:
    """Attach the 'group' command subtree to the root CLI."""
    cli.add_command(cmd_group)


@click.group("group")
def cmd_group() -> None:
    """Organise projects into named groups."""


@cmd_group.command("add")
@click.argument("group")
@click.argument("project")
@click.option("--store", default=None, envvar="ENVAULT_STORE", help="Path to vault store.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def group_add(group: str, project: str, store: str, password: str) -> None:
    """Add PROJECT to GROUP."""
    try:
        add_to_group(group, project, password, store_path=store)
        click.echo(f"Project '{project}' added to group '{group}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_group.command("remove")
@click.argument("group")
@click.argument("project")
@click.option("--store", default=None, envvar="ENVAULT_STORE", help="Path to vault store.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def group_remove(group: str, project: str, store: str, password: str) -> None:
    """Remove PROJECT from GROUP."""
    try:
        remove_from_group(group, project, password, store_path=store)
        click.echo(f"Project '{project}' removed from group '{group}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_group.command("list")
@click.option("--store", default=None, envvar="ENVAULT_STORE", help="Path to vault store.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def group_list(store: str, password: str) -> None:
    """List all groups and their member projects."""
    groups = list_groups(password, store_path=store)
    if not groups:
        click.echo("No groups defined.")
        return
    for name in sorted(groups):
        members = projects_in_group(name, password, store_path=store)
        member_str = ", ".join(sorted(members)) if members else "(empty)"
        click.echo(f"{name}: {member_str}")


@cmd_group.command("show")
@click.argument("group")
@click.option("--store", default=None, envvar="ENVAULT_STORE", help="Path to vault store.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def group_show(group: str, store: str, password: str) -> None:
    """Show all projects that belong to GROUP."""
    try:
        members = projects_in_group(group, password, store_path=store)
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if not members:
        click.echo(f"Group '{group}' is empty.")
        return
    for project in sorted(members):
        click.echo(project)


@cmd_group.command("rename")
@click.argument("old_name")
@click.argument("new_name")
@click.option("--store", default=None, envvar="ENVAULT_STORE", help="Path to vault store.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def group_rename(old_name: str, new_name: str, store: str, password: str) -> None:
    """Rename a group from OLD_NAME to NEW_NAME."""
    try:
        rename_group(old_name, new_name, password, store_path=store)
        click.echo(f"Group '{old_name}' renamed to '{new_name}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
