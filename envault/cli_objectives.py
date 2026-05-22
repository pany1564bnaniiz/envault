"""CLI commands for managing project objectives."""
import click

from envault.objectives import (
    set_objective,
    get_objective,
    delete_objective,
    list_objectives,
)


def register_objective_commands(cli, store_file, get_password):
    @cli.group("objective")
    def cmd_objective():
        """Manage project objectives."""

    @cmd_objective.command("set")
    @click.argument("project")
    @click.argument("text")
    @click.option("--due", default=None, help="Optional due date (ISO format).")
    def objective_set(project, text, due):
        """Set an objective for PROJECT."""
        password = get_password()
        try:
            entry = set_objective(store_file(), password, project, text, due=due)
            click.echo(f"Objective set for '{project}': {entry['text']}")
            if due:
                click.echo(f"  Due: {due}")
        except KeyError as exc:
            click.echo(str(exc), err=True)
            raise SystemExit(1)

    @cmd_objective.command("get")
    @click.argument("project")
    def objective_get(project):
        """Show the objective for PROJECT."""
        password = get_password()
        entry = get_objective(store_file(), password, project)
        if entry is None:
            click.echo(f"No objective set for '{project}'.")
        else:
            click.echo(entry["text"])
            if "due" in entry:
                click.echo(f"Due: {entry['due']}")
            click.echo(f"Updated: {entry['updated_at']}")

    @cmd_objective.command("delete")
    @click.argument("project")
    def objective_delete(project):
        """Delete the objective for PROJECT."""
        password = get_password()
        removed = delete_objective(store_file(), password, project)
        if removed:
            click.echo(f"Objective for '{project}' deleted.")
        else:
            click.echo(f"No objective found for '{project}'.")

    @cmd_objective.command("list")
    def objective_list():
        """List all project objectives."""
        password = get_password()
        objectives = list_objectives(store_file(), password)
        if not objectives:
            click.echo("No objectives recorded.")
        else:
            for proj, entry in sorted(objectives.items()):
                due_part = f"  [due: {entry['due']}]" if "due" in entry else ""
                click.echo(f"{proj}: {entry['text']}{due_part}")
