"""CLI commands for project activity forecasts."""
import click

from envault.forecasts import (
    clear_forecasts,
    get_forecasts,
    latest_forecast,
    record_forecast,
)


def register_forecast_commands(cli: click.Group) -> None:
    cli.add_command(cmd_forecast)


@click.group("forecast")
def cmd_forecast():
    """Manage project activity forecasts."""


@cmd_forecast.command("add")
@click.argument("project")
@click.option("--horizon", required=True, type=int, help="Days into the future")
@click.option("--changes", required=True, type=int, help="Predicted number of changes")
@click.option("--confidence", required=True, type=float, help="Confidence score 0.0-1.0")
@click.option("--notes", default="", help="Optional notes")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def forecast_add(project, horizon, changes, confidence, notes, store, password):
    """Record a new forecast for PROJECT."""
    try:
        entry = record_forecast(store, password, project, horizon, changes, confidence, notes)
        click.echo(
            f"Forecast recorded for '{project}': "
            f"{changes} changes over {horizon} days "
            f"(confidence={entry['confidence']:.2%})"
        )
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_forecast.command("show")
@click.argument("project")
@click.option("--all", "show_all", is_flag=True, help="Show all forecasts, not just latest")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def forecast_show(project, show_all, store, password):
    """Show forecast(s) for PROJECT."""
    if show_all:
        entries = get_forecasts(store, password, project)
        if not entries:
            click.echo(f"No forecasts for '{project}'.")
            return
        for e in entries:
            click.echo(
                f"[{e['created_at']}] horizon={e['horizon_days']}d "
                f"changes={e['predicted_changes']} "
                f"confidence={e['confidence']:.2%}"
                + (f" notes={e['notes']}" if e["notes"] else "")
            )
    else:
        entry = latest_forecast(store, password, project)
        if entry is None:
            click.echo(f"No forecasts for '{project}'.")
        else:
            click.echo(
                f"Latest forecast for '{project}': "
                f"{entry['predicted_changes']} changes over {entry['horizon_days']} days "
                f"(confidence={entry['confidence']:.2%})"
            )


@cmd_forecast.command("clear")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def forecast_clear(project, store, password):
    """Remove all forecasts for PROJECT."""
    removed = clear_forecasts(store, password, project)
    click.echo(f"Cleared {removed} forecast(s) for '{project}'.")
