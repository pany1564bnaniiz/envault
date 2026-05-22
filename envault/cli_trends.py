"""CLI commands for project key-count trend tracking."""
from __future__ import annotations

import click

from envault.trends import clear_trend, get_trend, record_snapshot, summarise_trend


def register_trend_commands(cli: click.Group) -> None:  # noqa: D401
    cli.add_command(cmd_trend)


@click.group("trend")
def cmd_trend() -> None:
    """Track key-count trends for a project."""


@cmd_trend.command("record")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE", help="Path to vault store.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def trend_record(project: str, store: str, password: str) -> None:
    """Record a trend snapshot for PROJECT."""
    try:
        entry = record_snapshot(store, password, project)
        click.echo(
            f"Snapshot recorded for '{project}': {entry['key_count']} key(s) at {entry['recorded_at']}."
        )
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_trend.command("show")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def trend_show(project: str, store: str, password: str) -> None:
    """Show trend snapshots for PROJECT."""
    snapshots = get_trend(store, password, project)
    if not snapshots:
        click.echo(f"No trend data for '{project}'.")
        return
    for snap in snapshots:
        click.echo(f"  {snap['recorded_at']}  keys={snap['key_count']}")


@cmd_trend.command("summary")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def trend_summary(project: str, store: str, password: str) -> None:
    """Print a trend summary for PROJECT."""
    info = summarise_trend(store, password, project)
    if info["snapshots"] == 0:
        click.echo(f"No trend data for '{project}'.")
        return
    click.echo(
        f"Project: {info['project']}  snapshots={info['snapshots']}  "
        f"first={info['first_count']}  latest={info['latest_count']}  delta={info['delta']:+d}"
    )


@cmd_trend.command("clear")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def trend_clear(project: str, store: str, password: str) -> None:
    """Remove all trend snapshots for PROJECT."""
    removed = clear_trend(store, password, project)
    click.echo(f"Cleared {removed} snapshot(s) for '{project}'.")
