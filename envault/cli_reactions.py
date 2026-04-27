"""CLI commands for emoji reactions."""
from __future__ import annotations

import click

from envault.reactions import (
    add_reaction,
    list_reactions,
    reaction_summary,
    remove_reaction,
    projects_reacted_by,
    _VALID_REACTIONS,
)


def register_reaction_commands(cli: click.Group) -> None:
    cli.add_command(cmd_reaction)


@click.group("reaction")
def cmd_reaction() -> None:
    """Manage emoji reactions for projects."""


@cmd_reaction.command("add")
@click.argument("project")
@click.argument("emoji")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--actor", default="user", show_default=True)
def reaction_add(project: str, emoji: str, store: str, password: str, actor: str) -> None:
    """Add EMOJI reaction to PROJECT."""
    try:
        add_reaction(store, password, project, emoji, actor)
        click.echo(f"Reaction {emoji} added to '{project}' by {actor}.")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_reaction.command("remove")
@click.argument("project")
@click.argument("emoji")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--actor", default="user", show_default=True)
def reaction_remove(project: str, emoji: str, store: str, password: str, actor: str) -> None:
    """Remove EMOJI reaction from PROJECT."""
    remove_reaction(store, password, project, emoji, actor)
    click.echo(f"Reaction {emoji} removed from '{project}' by {actor}.")


@cmd_reaction.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--summary", is_flag=True, default=False, help="Show counts only.")
def reaction_list(project: str, store: str, password: str, summary: bool) -> None:
    """List reactions for PROJECT."""
    if summary:
        data = reaction_summary(store, password, project)
        if not data:
            click.echo("No reactions.")
        else:
            for emoji, count in sorted(data.items()):
                click.echo(f"  {emoji}  {count}")
    else:
        data = list_reactions(store, password, project)
        if not data:
            click.echo("No reactions.")
        else:
            for emoji, actors in sorted(data.items()):
                click.echo(f"  {emoji}  {', '.join(actors)}")


@cmd_reaction.command("by")
@click.argument("actor")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def reaction_by(actor: str, store: str, password: str) -> None:
    """List all projects ACTOR has reacted to."""
    projects = projects_reacted_by(store, password, actor)
    if not projects:
        click.echo(f"{actor} has not reacted to any project.")
    else:
        for p in projects:
            click.echo(f"  {p}")
