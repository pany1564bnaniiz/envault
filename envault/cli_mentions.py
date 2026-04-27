"""cli_mentions.py — CLI commands for the mentions feature."""
from __future__ import annotations

import click

from envault.mentions import add_mention, list_mentions, mentions_for_user, clear_mentions


def register_mention_commands(cli: click.Group, store_file: click.Path, get_password):
    @cli.group("mention")
    def cmd_mention():
        """Manage @user mentions on projects."""

    @cmd_mention.command("add")
    @click.argument("project")
    @click.argument("user")
    @click.option("--message", "-m", default="", help="Optional message body.")
    @click.pass_context
    def mention_add(ctx, project: str, user: str, message: str):
        """Mention USER on PROJECT."""
        path = ctx.obj[store_file]
        password = get_password(ctx)
        try:
            entry = add_mention(path, password, project, user, message)
            ts = entry["timestamp"]
            click.echo(f"Mentioned @{user} on '{project}' at {ts}.")
        except KeyError as exc:
            click.echo(str(exc), err=True)
            ctx.exit(1)

    @cmd_mention.command("list")
    @click.argument("project")
    @click.pass_context
    def mention_list(ctx, project: str):
        """List all mentions on PROJECT."""
        path = ctx.obj[store_file]
        password = get_password(ctx)
        try:
            entries = list_mentions(path, password, project)
        except KeyError as exc:
            click.echo(str(exc), err=True)
            ctx.exit(1)
            return
        if not entries:
            click.echo(f"No mentions on '{project}'.")
            return
        for e in entries:
            msg = f" — {e['message']}" if e.get("message") else ""
            click.echo(f"  @{e['user']} [{e['timestamp']}]{msg}")

    @cmd_mention.command("search")
    @click.argument("user")
    @click.pass_context
    def mention_search(ctx, user: str):
        """Find all projects that mention USER."""
        path = ctx.obj[store_file]
        password = get_password(ctx)
        result = mentions_for_user(path, password, user)
        if not result:
            click.echo(f"No mentions found for @{user}.")
            return
        for project, entries in sorted(result.items()):
            click.echo(f"{project}: {len(entries)} mention(s)")

    @cmd_mention.command("clear")
    @click.argument("project")
    @click.pass_context
    def mention_clear(ctx, project: str):
        """Clear all mentions on PROJECT."""
        path = ctx.obj[store_file]
        password = get_password(ctx)
        try:
            count = clear_mentions(path, password, project)
            click.echo(f"Cleared {count} mention(s) from '{project}'.")
        except KeyError as exc:
            click.echo(str(exc), err=True)
            ctx.exit(1)
