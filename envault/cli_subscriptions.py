"""CLI commands for managing project subscriptions."""

from __future__ import annotations

import click

from envault.subscriptions import (
    subscribe,
    unsubscribe,
    list_subscribers,
    subscriptions_for,
)


def register_subscription_commands(cli: click.Group) -> None:
    cli.add_command(cmd_subscription)


@click.group("subscription")
def cmd_subscription():
    """Manage project subscriptions."""


@cmd_subscription.command("add")
@click.argument("project")
@click.argument("user")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def sub_add(project: str, user: str, store: str, password: str):
    """Subscribe USER to PROJECT."""
    try:
        subscribe(store, password, project, user)
        click.echo(f"User '{user}' subscribed to '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_subscription.command("remove")
@click.argument("project")
@click.argument("user")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def sub_remove(project: str, user: str, store: str, password: str):
    """Unsubscribe USER from PROJECT."""
    unsubscribe(store, password, project, user)
    click.echo(f"User '{user}' unsubscribed from '{project}'.")


@cmd_subscription.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def sub_list(project: str, store: str, password: str):
    """List all subscribers of PROJECT."""
    users = list_subscribers(store, password, project)
    if users:
        click.echo("\n".join(users))
    else:
        click.echo(f"No subscribers for '{project}'.")


@cmd_subscription.command("projects")
@click.argument("user")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def sub_projects(user: str, store: str, password: str):
    """List all projects USER is subscribed to."""
    projects = subscriptions_for(store, password, user)
    if projects:
        click.echo("\n".join(projects))
    else:
        click.echo(f"User '{user}' has no subscriptions.")
