"""CLI commands for managing favorite projects."""
from __future__ import annotations

import click

from envault.favorites import add_favorite, remove_favorite, list_favorites, is_favorite


def register_favorites_commands(cli, store_file, password):
    @cli.group("favorite", help="Manage favorite projects.")
    def cmd_favorite():
        pass

    @cmd_favorite.command("add")
    @click.argument("project")
    def fav_add(project):
        """Mark a project as favorite."""
        try:
            add_favorite(store_file(), password(), project)
            click.echo(f"Marked '{project}' as favorite.")
        except KeyError as e:
            click.echo(str(e), err=True)
            raise SystemExit(1)

    @cmd_favorite.command("remove")
    @click.argument("project")
    def fav_remove(project):
        """Remove a project from favorites."""
        try:
            remove_favorite(store_file(), password(), project)
            click.echo(f"Removed '{project}' from favorites.")
        except KeyError as e:
            click.echo(str(e), err=True)
            raise SystemExit(1)

    @cmd_favorite.command("list")
    def fav_list():
        """List all favorite projects."""
        favs = list_favorites(store_file(), password())
        if not favs:
            click.echo("No favorites set.")
        else:
            for name in favs:
                click.echo(name)

    @cmd_favorite.command("check")
    @click.argument("project")
    def fav_check(project):
        """Check if a project is a favorite."""
        result = is_favorite(store_file(), password(), project)
        click.echo("yes" if result else "no")
