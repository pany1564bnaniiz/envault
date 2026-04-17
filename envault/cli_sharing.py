"""CLI commands for sharing encrypted project bundles."""
import click
from pathlib import Path
from envault.sharing import export_bundle, import_bundle, list_bundle_keys
from cryptography.fernet import InvalidToken


def register_sharing_commands(cli: click.Group) -> None:
    cli.add_command(cmd_share)


@click.group("share")
def cmd_share() -> None:
    """Share encrypted project bundles."""


@cmd_share.command("export")
@click.argument("project")
@click.option("--store", default="~/.envault/store", show_default=True)
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
@click.option("--bundle-password", prompt=True, hide_input=True, confirmation_prompt=True)
def share_export(project: str, store: str, password: str, bundle_password: str) -> None:
    """Export PROJECT as an encrypted bundle string."""
    store_path = Path(store).expanduser()
    bundle = export_bundle(store_path, password, project, bundle_password)
    click.echo(bundle)


@cmd_share.command("import")
@click.argument("project")
@click.argument("bundle")
@click.option("--store", default="~/.envault/store", show_default=True)
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
@click.option("--bundle-password", prompt=True, hide_input=True)
def share_import(project: str, bundle: str, store: str, password: str, bundle_password: str) -> None:
    """Import a bundle into PROJECT."""
    store_path = Path(store).expanduser()
    try:
        count = import_bundle(store_path, password, project, bundle, bundle_password)
        click.echo(f"Imported {count} key(s) into '{project}'.")
    except (InvalidToken, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_share.command("peek")
@click.argument("bundle")
@click.option("--bundle-password", prompt=True, hide_input=True)
def share_peek(bundle: str, bundle_password: str) -> None:
    """List keys inside a bundle without importing."""
    try:
        keys = list_bundle_keys(bundle, bundle_password)
        if keys:
            click.echo("\n".join(keys))
        else:
            click.echo("Bundle is empty.")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
