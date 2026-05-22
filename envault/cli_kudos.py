"""CLI commands for the kudos feature."""
from __future__ import annotations

import click

from envault.kudos import clear_kudos, get_kudos, give_kudos, kudos_count


def register_kudos_commands(cli: click.Group) -> None:
    cli.add_command(cmd_kudos)


@click.group("kudos")
def cmd_kudos() -> None:
    """Give and view kudos for projects."""


@cmd_kudos.command("give")
@click.argument("project")
@click.argument("actor")
@click.option("--message", "-m", default="", help="Optional kudos message.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def kudos_give(
    project: str, actor: str, message: str, store: str, password: str
) -> None:
    """Give kudos to PROJECT from ACTOR."""
    try:
        entry = give_kudos(store, password, project, actor, message)
        msg = entry["message"]
        click.echo(f"Kudos given to '{project}' by '{actor}'." + (f" \"{msg}\"" if msg else ""))
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_kudos.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def kudos_list(project: str, store: str, password: str) -> None:
    """List all kudos for PROJECT."""
    entries = get_kudos(store, password, project)
    if not entries:
        click.echo(f"No kudos for '{project}' yet.")
        return
    for e in entries:
        line = f"[{e['timestamp']}] {e['actor']}"
        if e.get("message"):
            line += f": {e['message']}"
        click.echo(line)


@cmd_kudos.command("count")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def kudos_count_cmd(project: str, store: str, password: str) -> None:
    """Show total kudos count for PROJECT."""
    count = kudos_count(store, password, project)
    click.echo(f"{project}: {count} kudos")


@cmd_kudos.command("clear")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def kudos_clear(project: str, store: str, password: str) -> None:
    """Clear all kudos for PROJECT."""
    removed = clear_kudos(store, password, project)
    click.echo(f"Cleared {removed} kudos from '{project}'.")
