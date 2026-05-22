"""CLI commands for endorsements."""

from __future__ import annotations

import click

from envault.endorsements import (
    VALID_QUALITIES,
    endorse,
    endorsement_counts,
    list_endorsements,
    withdraw,
)


def register_endorsement_commands(cli: click.Group) -> None:
    cli.add_command(cmd_endorsement)


@click.group("endorsement")
def cmd_endorsement() -> None:
    """Manage project endorsements."""


@cmd_endorsement.command("add")
@click.argument("project")
@click.argument("quality")
@click.option("--actor", default="anonymous", show_default=True, help="Endorser name.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def endorsement_add(project: str, quality: str, actor: str, store: str, password: str) -> None:
    """Endorse a project for a quality."""
    try:
        entry = endorse(store, password, project, quality, actor)
        click.echo(f"Endorsed '{project}' for '{quality}' by {entry['actor']} at {entry['endorsed_at']}.")
    except (KeyError, ValueError) as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_endorsement.command("remove")
@click.argument("project")
@click.argument("quality")
@click.option("--actor", default="anonymous", show_default=True)
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def endorsement_remove(project: str, quality: str, actor: str, store: str, password: str) -> None:
    """Withdraw an endorsement."""
    removed = withdraw(store, password, project, quality, actor)
    if removed:
        click.echo(f"Endorsement for '{quality}' by {actor} removed from '{project}'.")
    else:
        click.echo(f"No endorsement found for '{quality}' by {actor} on '{project}'.")


@cmd_endorsement.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def endorsement_list(project: str, store: str, password: str) -> None:
    """List endorsements for a project."""
    counts = endorsement_counts(store, password, project)
    if not counts:
        click.echo(f"No endorsements for '{project}'.")
        return
    for quality, count in sorted(counts.items()):
        click.echo(f"  {quality}: {count}")


@cmd_endorsement.command("qualities")
def endorsement_qualities() -> None:
    """List all valid endorsement qualities."""
    for q in sorted(VALID_QUALITIES):
        click.echo(f"  {q}")
