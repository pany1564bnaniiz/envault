"""CLI sub-command for password rotation."""

from __future__ import annotations

import click

from envault.rotate import rotate_password
from envault.storage import _store_path


def register_rotate_commands(cli: click.Group) -> None:  # noqa: D401
    """Attach the *rotate* command to *cli*."""
    cli.add_command(cmd_rotate)


@click.command("rotate")
@click.option(
    "--store",
    default=None,
    help="Path to the store file (defaults to ~/.envault/store.enc).",
)
@click.password_option(
    "--old-password",
    prompt="Current master password",
    confirmation_prompt=False,
    help="Current master password.",
)
@click.password_option(
    "--new-password",
    prompt="New master password",
    help="New master password (prompted twice for confirmation).",
)
def cmd_rotate(
    store: str | None,
    old_password: str,
    new_password: str,
) -> None:
    """Re-encrypt the entire store with a new master password."""
    path = store or str(_store_path())
    try:
        count = rotate_password(path, old_password, new_password)
        click.echo(
            click.style(
                f"Password rotated successfully. {count} project(s) re-encrypted.",
                fg="green",
            )
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
