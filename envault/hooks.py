"""Pre/post hooks for envault operations."""
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

_HOOKS_KEY = "__hooks__"

HOOK_EVENTS = [
    "pre_set", "post_set",
    "pre_delete", "post_delete",
    "pre_export", "post_export",
    "pre_import", "post_import",
]


def _hooks_for(store: dict, project: str) -> dict:
    return store.get(_HOOKS_KEY, {}).get(project, {})


def add_hook(store: dict, password: str, project: str, event: str, command: str) -> None:
    from envault.storage import load_store, save_store
    if event not in HOOK_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid: {HOOK_EVENTS}")
    data = load_store(store["_path"], password)
    hooks = data.setdefault(_HOOKS_KEY, {}).setdefault(project, {})
    hooks.setdefault(event, []).append(command)
    save_store(store["_path"], password, data)


def remove_hook(store: dict, password: str, project: str, event: str, index: int) -> None:
    from envault.storage import load_store, save_store
    data = load_store(store["_path"], password)
    hooks = data.get(_HOOKS_KEY, {}).get(project, {}).get(event, [])
    if index < 0 or index >= len(hooks):
        raise IndexError(f"Hook index {index} out of range.")
    hooks.pop(index)
    data[_HOOKS_KEY][project][event] = hooks
    save_store(store["_path"], password, data)


def list_hooks(store: dict, password: str, project: str) -> Dict[str, List[str]]:
    from envault.storage import load_store
    data = load_store(store["_path"], password)
    return data.get(_HOOKS_KEY, {}).get(project, {})


def run_hooks(store: dict, password: str, project: str, event: str, env: Optional[Dict] = None) -> List[str]:
    """Run all hooks for an event, returns list of outputs."""
    import subprocess
    from envault.storage import load_store
    data = load_store(store["_path"], password)
    commands = data.get(_HOOKS_KEY, {}).get(project, {}).get(event, [])
    results = []
    run_env = {**os.environ, **(env or {})}
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=run_env)
        results.append(result.stdout.strip())
    return results
