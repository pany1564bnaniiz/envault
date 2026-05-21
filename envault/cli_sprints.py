"""CLI commands for sprint tracking."""
import click

from envault.sprints import (
    active_sprints,
    delete_sprint,
    get_sprint,
    list_sprints,
    set_sprint,
)


def register_sprint_commands(cli):
    cli.add_command(cmd_sprint)


@click.group("sprint")
def cmd_sprint():
    """Manage sprints for projects."""


@cmd_sprint.command("set")
@click.argument("project")
@click.argument("sprint_name")
@click.argument("start_date")
@click.argument("end_date")
@click.option("--description", "-d", default="", help="Optional description.")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def sprint_set(project, sprint_name, start_date, end_date, description, store, password):
    """Assign SPRINT_NAME to PROJECT with START_DATE and END_DATE (ISO format)."""
    try:
        set_sprint(store, password, project, sprint_name, start_date, end_date, description)
        click.echo(f"Sprint '{sprint_name}' set for project '{project}'.")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))


@cmd_sprint.command("get")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def sprint_get(project, store, password):
    """Show the sprint assigned to PROJECT."""
    entry = get_sprint(store, password, project)
    if entry is None:
        click.echo(f"No sprint assigned to '{project}'.")
    else:
        click.echo(
            f"{entry['sprint']}  {entry['start']} -> {entry['end']}  {entry['description']}".strip()
        )


@cmd_sprint.command("delete")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def sprint_delete(project, store, password):
    """Remove the sprint assignment from PROJECT."""
    removed = delete_sprint(store, password, project)
    if removed:
        click.echo(f"Sprint removed from '{project}'.")
    else:
        click.echo(f"No sprint found for '{project}'.")


@cmd_sprint.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def sprint_list(store, password):
    """List all sprint assignments."""
    sprints = list_sprints(store, password)
    if not sprints:
        click.echo("No sprints defined.")
        return
    for proj, entry in sorted(sprints.items()):
        click.echo(f"{proj}: {entry['sprint']}  {entry['start']} -> {entry['end']}")


@cmd_sprint.command("active")
@click.option("--as-of", default=None, help="ISO date to check against (default: today).")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def sprint_active(as_of, store, password):
    """List sprints that are currently active."""
    sprints = active_sprints(store, password, as_of=as_of)
    if not sprints:
        click.echo("No active sprints.")
        return
    for proj, entry in sorted(sprints.items()):
        click.echo(f"{proj}: {entry['sprint']}  {entry['start']} -> {entry['end']}")
