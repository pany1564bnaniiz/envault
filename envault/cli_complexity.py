"""CLI commands for project complexity scoring."""

from __future__ import annotations

import click

from envault.complexity import compute_complexity, rank_projects


def register_complexity_commands(cli: click.Group) -> None:
    cli.add_command(cmd_complexity)


@click.group("complexity")
def cmd_complexity() -> None:
    """Analyse project complexity."""


@cmd_complexity.command("show")
@click.argument("project")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--store", "store_path", default=None, hidden=True)
def complexity_show(project: str, password: str, store_path) -> None:
    """Show the complexity score for PROJECT."""
    try:
        result = compute_complexity(project, password, store_path=store_path)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Project : {result['project']}")
    click.echo(f"Score   : {result['score']}")
    click.echo("Breakdown:")
    for factor, value in result["breakdown"].items():
        click.echo(f"  {factor:<20} {value}")


@cmd_complexity.command("rank")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--store", "store_path", default=None, hidden=True)
@click.option("--top", default=0, help="Limit output to top N projects (0 = all).")
def complexity_rank(password: str, store_path, top: int) -> None:
    """Rank all projects by complexity score."""
    results = rank_projects(password, store_path=store_path)
    if not results:
        click.echo("No projects found.")
        return
    if top:
        results = results[:top]
    click.echo(f"{'Project':<30} {'Score':>6}")
    click.echo("-" * 38)
    for r in results:
        click.echo(f"{r['project']:<30} {r['score']:>6}")
