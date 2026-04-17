"""CLI commands for project notes."""

from __future__ import annotations

import click

from envault.notes import delete_note, get_note, list_notes, set_note


def register_notes_commands(cli, store_file, get_password):
    @cli.group("note")
    def cmd_note():
        """Manage per-project notes."""

    @cmd_note.command("set")
    @click.argument("project")
    @click.argument("text")
    def note_set(project, text):
        """Set a note for PROJECT."""
        pw = get_password()
        try:
            set_note(store_file(), pw, project, text)
            click.echo(f"Note saved for '{project}'.")
        except KeyError as exc:
            raise SystemExit(str(exc))

    @cmd_note.command("get")
    @click.argument("project")
    def note_get(project):
        """Show the note for PROJECT."""
        pw = get_password()
        note = get_note(store_file(), pw, project)
        if note is None:
            click.echo(f"No note for '{project}'.")
        else:
            click.echo(f"[{note['updated_at']}] {note['text']}")

    @cmd_note.command("delete")
    @click.argument("project")
    def note_delete(project):
        """Delete the note for PROJECT."""
        pw = get_password()
        existed = delete_note(store_file(), pw, project)
        if existed:
            click.echo(f"Note for '{project}' deleted.")
        else:
            click.echo(f"No note found for '{project}'.")

    @cmd_note.command("list")
    def note_list():
        """List all projects that have notes."""
        pw = get_password()
        notes = list_notes(store_file(), pw)
        if not notes:
            click.echo("No notes stored.")
        else:
            for project, note in sorted(notes.items()):
                click.echo(f"{project}: {note['text'][:60]}")
