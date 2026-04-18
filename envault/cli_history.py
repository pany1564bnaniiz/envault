"""CLI commands for key change history."""
import click
from envault.history import get_history, clear_history


def register_history_commands(cli: click.Group) -> None:
    cli.add_command(cmd_history)


@click.group("history")
def cmd_history() -> None:
    """View or clear per-key change history."""


@cmd_history.command("show")
@click.argument("project")
@click.option("--key", default=None, help="Filter by key name.")
@click.option("--store", "store_path", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def history_show(project: str, key: str | None, store_path: str, password: str) -> None:
    """Show change history for a project (optionally filtered by key)."""
    entries = get_history(store_path, password, project, key=key)
    if not entries:
        click.echo("No history found.")
        return
    for e in entries:
        import datetime
        ts = datetime.datetime.fromtimestamp(e["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        old = e["old_value"] if e["old_value"] is not None else "(none)"
        new = e["new_value"] if e["new_value"] is not None else "(none)"
        click.echo(f"[{ts}] {e['action']:6s}  {e['key']}  {old} -> {new}")


@cmd_history.command("clear")
@click.argument("project")
@click.option("--store", "store_path", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.confirmation_option(prompt="Clear all history for this project?")
def history_clear(project: str, store_path: str, password: str) -> None:
    """Delete all history entries for a project."""
    clear_history(store_path, password, project)
    click.echo(f"History cleared for project '{project}'.")
