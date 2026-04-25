"""CLI commands for project ratings."""

from __future__ import annotations

import click

from envault.ratings import (
    average_score,
    delete_rating,
    get_rating,
    list_ratings,
    set_rating,
)


def register_rating_commands(cli: click.Group) -> None:
    cli.add_command(cmd_rating)


@click.group("rating")
def cmd_rating() -> None:
    """Manage project ratings."""


@cmd_rating.command("set")
@click.argument("project")
@click.argument("score", type=int)
@click.option("--comment", "-c", default="", help="Optional comment.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def rating_set(project: str, score: int, comment: str, store: str, password: str) -> None:
    """Rate PROJECT with SCORE (1-5)."""
    try:
        set_rating(store, password, project, score, comment)
        click.echo(f"Rated '{project}': {score}/5")
    except (ValueError, KeyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_rating.command("get")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def rating_get(project: str, store: str, password: str) -> None:
    """Show the rating for PROJECT."""
    rating = get_rating(store, password, project)
    if rating is None:
        click.echo(f"'{project}' has not been rated.")
    else:
        comment_part = f" — {rating['comment']}" if rating["comment"] else ""
        click.echo(f"{project}: {rating['score']}/5{comment_part} (updated {rating['updated_at']})")


@cmd_rating.command("delete")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def rating_delete(project: str, store: str, password: str) -> None:
    """Remove the rating for PROJECT."""
    removed = delete_rating(store, password, project)
    if removed:
        click.echo(f"Rating for '{project}' removed.")
    else:
        click.echo(f"No rating found for '{project}'.")


@cmd_rating.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def rating_list(store: str, password: str) -> None:
    """List all project ratings sorted by score."""
    ratings = list_ratings(store, password)
    if not ratings:
        click.echo("No ratings recorded.")
        return
    avg = average_score(store, password)
    for project, info in ratings.items():
        comment_part = f" — {info['comment']}" if info["comment"] else ""
        click.echo(f"{project}: {info['score']}/5{comment_part}")
    click.echo(f"\nAverage score: {avg:.2f}")
