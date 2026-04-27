"""CLI commands for managing per-key comments."""

from __future__ import annotations

import click

from envault.comments import set_comment, get_comment, delete_comment, list_comments


def register_comments_commands(cli: click.Group) -> None:
    cli.add_command(cmd_comment)


@click.group("comment")
def cmd_comment() -> None:
    """Manage comments attached to env keys."""


@cmd_comment.command("set")
@click.argument("project")
@click.argument("key")
@click.argument("comment")
@click.option("--store", envvar="ENVAULT_STORE", required=True, help="Path to vault store.")
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def comment_set(project: str, key: str, comment: str, store: str, password: str) -> None:
    """Attach COMMENT to KEY in PROJECT."""
    try:
        set_comment(store, password, project, key, comment)
        click.echo(f"Comment set for '{key}' in '{project}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_comment.command("get")
@click.argument("project")
@click.argument("key")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def comment_get(project: str, key: str, store: str, password: str) -> None:
    """Show the comment for KEY in PROJECT."""
    value = get_comment(store, password, project, key)
    if value is None:
        click.echo(f"No comment set for '{key}'.")
    else:
        click.echo(value)


@cmd_comment.command("delete")
@click.argument("project")
@click.argument("key")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def comment_delete(project: str, key: str, store: str, password: str) -> None:
    """Remove the comment for KEY in PROJECT."""
    removed = delete_comment(store, password, project, key)
    if removed:
        click.echo(f"Comment removed for '{key}'.")
    else:
        click.echo(f"No comment found for '{key}'.")


@cmd_comment.command("list")
@click.argument("project")
@click.option("--store", envvar="ENVAULT_STORE", required=True)
@click.password_option("--password", envvar="ENVAULT_PASSWORD", confirmation_prompt=False)
def comment_list(project: str, store: str, password: str) -> None:
    """List all comments for PROJECT."""
    mapping = list_comments(store, password, project)
    if not mapping:
        click.echo("No comments found.")
        return
    for key, comment in sorted(mapping.items()):
        click.echo(f"{key}: {comment}")
