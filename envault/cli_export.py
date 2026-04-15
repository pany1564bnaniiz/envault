"""CLI commands for export/import functionality."""

import click

from envault.export import export_env, import_env


def register_export_commands(cli: click.Group) -> None:
    """Register export/import commands onto the main CLI group."""

    @cli.command("export")
    @click.argument("project")
    @click.option("--password", "-p", prompt=True, hide_input=True, help="Master password.")
    @click.option(
        "--output",
        "-o",
        default=None,
        help="Output file path (e.g. .env). Prints to stdout if omitted.",
    )
    def cmd_export(project: str, password: str, output: str) -> None:
        """Export PROJECT env vars to a .env file or stdout."""
        try:
            content = export_env(project, password, output_path=output)
            if output:
                click.echo(f"Exported project '{project}' to {output}")
            else:
                click.echo(content, nl=False)
        except KeyError:
            click.echo(f"Error: project '{project}' not found.", err=True)
            raise SystemExit(1)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1)

    @cli.command("import")
    @click.argument("project")
    @click.argument("file", type=click.Path(exists=True))
    @click.option("--password", "-p", prompt=True, hide_input=True, help="Master password.")
    @click.option(
        "--overwrite",
        is_flag=True,
        default=False,
        help="Overwrite existing keys if present.",
    )
    def cmd_import(project: str, file: str, password: str, overwrite: bool) -> None:
        """Import env vars from FILE into PROJECT."""
        try:
            count = import_env(project, password, input_path=file, overwrite=overwrite)
            click.echo(f"Imported {count} variable(s) into project '{project}'.")
        except FileNotFoundError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1)
        except ValueError as exc:
            click.echo(f"Parse error: {exc}", err=True)
            raise SystemExit(1)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1)
