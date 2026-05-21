"""CLI commands for the project voting feature."""

from __future__ import annotations

import click

from envault.votes import downvote, get_voters, get_votes, top_projects, upvote


def register_vote_commands(cli: click.Group) -> None:
    cli.add_command(cmd_vote)


@click.group("vote")
def cmd_vote() -> None:
    """Manage project votes."""


@cmd_vote.command("up")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD")
@click.option("--actor", default="anonymous", show_default=True)
def vote_up(project: str, store: str, password: str, actor: str) -> None:
    """Upvote PROJECT."""
    try:
        count = upvote(store, password, project, actor)
        click.echo(f"Upvoted '{project}'. Total votes: {count}")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_vote.command("down")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD")
@click.option("--actor", default="anonymous", show_default=True)
def vote_down(project: str, store: str, password: str, actor: str) -> None:
    """Retract upvote from PROJECT."""
    count = downvote(store, password, project, actor)
    click.echo(f"Vote retracted from '{project}'. Total votes: {count}")


@cmd_vote.command("show")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD")
def vote_show(project: str, store: str, password: str) -> None:
    """Show vote count and voters for PROJECT."""
    count = get_votes(store, password, project)
    voters = get_voters(store, password, project)
    click.echo(f"Votes: {count}")
    if voters:
        click.echo("Voters: " + ", ".join(voters))
    else:
        click.echo("Voters: none")


@cmd_vote.command("top")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD")
@click.option("--limit", default=5, show_default=True, type=int)
def vote_top(store: str, password: str, limit: int) -> None:
    """Show top voted projects."""
    results = top_projects(store, password, limit)
    if not results:
        click.echo("No votes recorded yet.")
        return
    for entry in results:
        click.echo(f"{entry['project']}: {entry['count']} vote(s)")
