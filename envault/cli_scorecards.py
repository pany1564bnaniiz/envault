"""CLI commands for project scorecards."""

from __future__ import annotations

import click

from envault.scorecards import (
    VALID_METRICS,
    delete_metric,
    get_scorecard,
    list_scorecards,
    overall_score,
    set_metric,
)


def register_scorecard_commands(cli: click.Group) -> None:
    cli.add_command(cmd_scorecard)


@click.group("scorecard")
def cmd_scorecard() -> None:
    """Manage project health scorecards."""


@cmd_scorecard.command("set")
@click.argument("project")
@click.argument("metric")
@click.argument("value", type=float)
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def scorecard_set(project: str, metric: str, value: float, store: str, password: str) -> None:
    """Set METRIC (0.0-1.0) for PROJECT."""
    try:
        set_metric(store, password, project, metric, value)
        click.echo(f"Set {metric}={value} for '{project}'.")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))


@cmd_scorecard.command("show")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def scorecard_show(project: str, store: str, password: str) -> None:
    """Show scorecard metrics and overall score for PROJECT."""
    metrics = get_scorecard(store, password, project)
    if not metrics:
        click.echo(f"No scorecard metrics set for '{project}'.")
        return
    for m, v in sorted(metrics.items()):
        click.echo(f"  {m}: {v:.2%}")
    score = overall_score(store, password, project)
    click.echo(f"Overall: {score:.2%}")


@cmd_scorecard.command("delete")
@click.argument("project")
@click.argument("metric")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def scorecard_delete(project: str, metric: str, store: str, password: str) -> None:
    """Remove METRIC from PROJECT's scorecard."""
    removed = delete_metric(store, password, project, metric)
    if removed:
        click.echo(f"Removed metric '{metric}' from '{project}'.")
    else:
        click.echo(f"Metric '{metric}' was not set for '{project}'.")


@cmd_scorecard.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def scorecard_list(store: str, password: str) -> None:
    """List overall scores for all projects with scorecards."""
    cards = list_scorecards(store, password)
    if not cards:
        click.echo("No scorecards found.")
        return
    for project, metrics in sorted(cards.items()):
        avg = round(sum(metrics.values()) / len(metrics), 4)
        click.echo(f"{project}: {avg:.2%} ({len(metrics)} metric(s))")
