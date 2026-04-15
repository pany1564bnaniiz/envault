"""Export and import .env file functionality for envault."""

import os
from pathlib import Path
from typing import Optional

from envault.projects import get_all_env, set_env


def export_env(project: str, password: str, output_path: Optional[str] = None) -> str:
    """Export a project's env vars to a .env formatted file.

    Args:
        project: The project name to export.
        password: The master password for decryption.
        output_path: Optional file path to write to. If None, returns the content.

    Returns:
        The .env formatted string content.

    Raises:
        KeyError: If the project does not exist.
    """
    env_vars = get_all_env(project, password)

    lines = [f"# envault export: {project}\n"]
    for key, value in sorted(env_vars.items()):
        # Wrap value in quotes if it contains spaces or special characters
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"\n')
        else:
            lines.append(f"{key}={value}\n")

    content = "".join(lines)

    if output_path:
        path = Path(output_path)
        path.write_text(content)
        # Restrict permissions to owner only
        os.chmod(path, 0o600)

    return content


def import_env(project: str, password: str, input_path: str, overwrite: bool = False) -> int:
    """Import env vars from a .env file into a project.

    Args:
        project: The project name to import into.
        password: The master password for encryption.
        input_path: Path to the .env file to read.
        overwrite: If True, overwrite existing keys. Default is False.

    Returns:
        The number of variables imported.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If a line in the file is malformed.
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    content = path.read_text()
    imported = 0

    for lineno, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(f"Malformed line {lineno}: {line!r}")

        key, _, value = line.partition("=")
        key = key.strip()
        # Strip surrounding quotes from value
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]

        if not key:
            raise ValueError(f"Empty key on line {lineno}")

        set_env(project, key, value, password, overwrite=overwrite)
        imported += 1

    return imported
