"""CLI commands for template management."""

from __future__ import annotations

import click

from envault.templates import (
    save_template,
    load_template,
    list_templates,
    delete_template,
    apply_template,
)


def register_template_commands(cli: click.Group) -> None:
    cli.add_command(cmd_template)


@click.group("template")
def cmd_template() -> None:
    """Manage reusable env templates."""


@cmd_template.command("save")
@click.argument("name")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--set", "pairs", multiple=True, metavar="KEY=VALUE",
              help="Key=value pairs to include in the template.")
def template_save(name: str, store: str, password: str, pairs: tuple) -> None:
    """Save a new template with KEY=VALUE pairs."""
    env: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Invalid pair '{pair}', expected KEY=VALUE.")
        k, v = pair.split("=", 1)
        env[k.strip()] = v.strip()
    if not env:
        click.echo("No key=value pairs provided.", err=True)
        raise SystemExit(1)
    save_template(store, password, name, env)
    click.echo(f"Template '{name}' saved with {len(env)} key(s).")


@cmd_template.command("list")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def template_list(store: str, password: str) -> None:
    """List all saved templates."""
    names = list_templates(store, password)
    if not names:
        click.echo("No templates saved.")
    for name in names:
        click.echo(name)


@cmd_template.command("delete")
@click.argument("name")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def template_delete(name: str, store: str, password: str) -> None:
    """Delete a saved template."""
    try:
        delete_template(store, password, name)
        click.echo(f"Template '{name}' deleted.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_template.command("apply")
@click.argument("name")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys in the project.")
def template_apply(name: str, project: str, store: str, password: str, overwrite: bool) -> None:
    """Apply a template to a project."""
    try:
        written = apply_template(store, password, name, project, overwrite=overwrite)
        click.echo(f"Applied {len(written)} key(s) from template '{name}' to '{project}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
