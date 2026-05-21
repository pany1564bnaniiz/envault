"""CLI commands for the project changelog feature."""

from __future__ import annotations

import sys

import click

from envault.changelog import add_entry, get_changelog, clear_changelog


def register_changelog_commands(cli, store_file, get_password):
    @cli.group("changelog")
    def cmd_changelog():
        """Manage per-project changelogs."""

    @cmd_changelog.command("add")
    @click.argument("project")
    @click.argument("message")
    @click.option("--author", default="envault", show_default=True)
    def changelog_add(project, message, author):
        """Add a changelog entry for PROJECT."""
        password = get_password()
        try:
            entry = add_entry(store_file, password, project, message, author=author)
        except KeyError as exc:
            click.echo(str(exc), err=True)
            sys.exit(1)
        click.echo(f"[{entry['timestamp']}] {entry['author']}: {entry['message']}")

    @cmd_changelog.command("show")
    @click.argument("project")
    def changelog_show(project):
        """Show changelog entries for PROJECT."""
        password = get_password()
        entries = get_changelog(store_file, password, project)
        if not entries:
            click.echo("No changelog entries.")
            return
        for e in entries:
            click.echo(f"[{e['timestamp']}] {e['author']}: {e['message']}")

    @cmd_changelog.command("clear")
    @click.argument("project")
    def changelog_clear(project):
        """Clear all changelog entries for PROJECT."""
        password = get_password()
        removed = clear_changelog(store_file, password, project)
        click.echo(f"Cleared {removed} changelog entry/entries for '{project}'.")
