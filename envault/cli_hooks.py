"""CLI commands for managing hooks."""
import click
from envault.hooks import add_hook, remove_hook, list_hooks, HOOK_EVENTS


def register_hook_commands(cli):
    cli.add_command(cmd_hook)


@click.group("hook")
def cmd_hook():
    """Manage pre/post hooks for projects."""


@cmd_hook.command("add")
@click.argument("project")
@click.argument("event")
@click.argument("command")
@click.option("--store", required=True, envvar="ENVAULT_STORE", help="Path to store file.")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def hook_add(project, event, command, store, password):
    """Add a hook COMMAND for EVENT on PROJECT."""
    try:
        add_hook({"_path": store}, password, project, event, command)
        click.echo(f"Hook added: [{event}] {command}")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cmd_hook.command("remove")
@click.argument("project")
@click.argument("event")
@click.argument("index", type=int)
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def hook_remove(project, event, index, store, password):
    """Remove hook at INDEX for EVENT on PROJECT."""
    try:
        remove_hook({"_path": store}, password, project, event, index)
        click.echo(f"Hook {index} removed from [{event}].")
    except (IndexError, ValueError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cmd_hook.command("list")
@click.argument("project")
@click.option("--store", required=True, envvar="ENVAULT_STORE")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def hook_list(project, store, password):
    """List all hooks for PROJECT."""
    hooks = list_hooks({"_path": store}, password, project)
    if not hooks:
        click.echo("No hooks defined.")
        return
    for event, commands in sorted(hooks.items()):
        for i, cmd in enumerate(commands):
            click.echo(f"[{event}] {i}: {cmd}")
