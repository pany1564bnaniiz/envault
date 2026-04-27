"""CLI commands for project badges."""

from __future__ import annotations

import click

from envault.badges import (
    VALID_BADGES,
    add_badge,
    clear_badges,
    list_badges,
    projects_with_badge,
    remove_badge,
)


def register_badge_commands(cli: click.Group) -> None:
    cli.add_command(cmd_badge)


@click.group("badge")
def cmd_badge() -> None:
    """Manage project badges."""


@cmd_badge.command("add")
@click.argument("project")
@click.argument("badge")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def badge_add(project: str, badge: str, store: str, password: str) -> None:
    """Add BADGE to PROJECT."""
    try:
        add_badge(store, password, project, badge)
        click.echo(f"Badge '{badge}' added to '{project}'.")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_badge.command("remove")
@click.argument("project")
@click.argument("badge")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def badge_remove(project: str, badge: str, store: str, password: str) -> None:
    """Remove BADGE from PROJECT."""
    removed = remove_badge(store, password, project, badge)
    if removed:
        click.echo(f"Badge '{badge}' removed from '{project}'.")
    else:
        click.echo(f"Badge '{badge}' was not set on '{project}'.")


@cmd_badge.command("list")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def badge_list(project: str, store: str, password: str) -> None:
    """List badges on PROJECT."""
    badges = list_badges(store, password, project)
    if badges:
        for b in badges:
            click.echo(b)
    else:
        click.echo(f"No badges set on '{project}'.")


@cmd_badge.command("find")
@click.argument("badge")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
def badge_find(badge: str, store: str, password: str) -> None:
    """List all projects with BADGE."""
    projects = projects_with_badge(store, password, badge)
    if projects:
        for p in projects:
            click.echo(p)
    else:
        click.echo(f"No projects have badge '{badge}'.")


@cmd_badge.command("valid")
def badge_valid() -> None:
    """Print all valid badge names."""
    for b in sorted(VALID_BADGES):
        click.echo(b)
