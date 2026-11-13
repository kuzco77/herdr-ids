#!/usr/bin/env python3
"""Bind or unbind the ids popup key in herdr-app's keys.json.

usage:
  herdr_app_keys.py check <keys.json>    exit 1 when keys.json is unreadable or the key is taken
  herdr_app_keys.py add <keys.json>      bind ctrl-a i to mod.open:ids (refuses a conflict)
  herdr_app_keys.py remove <keys.json>   unbind it, only while it still opens ids

keys.json is copied once to keys.json.ids-backup before the first write.
A missing file is an error: nothing is created.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import List

KEY = "ctrl-a i"
COMMAND = "mod.open:ids"


class KeysError(Exception):
    """A keys.json problem worth a one-line message, not a traceback."""


def load(path: Path) -> dict:
    if not path.is_file():
        raise KeysError("%s: no such file" % path)
    try:
        data = json.loads(path.read_text())
    except ValueError as exc:
        raise KeysError("%s: not valid JSON (%s)" % (path, exc))
    if not isinstance(data, dict):
        raise KeysError("%s: top level must be a JSON object" % path)
    bound = data.setdefault("global", {})
    if not isinstance(bound, dict):
        raise KeysError('%s: "global" must be an object' % path)
    return data


def conflict(keys: dict) -> bool:
    bound = keys["global"]
    return KEY in bound and bound[KEY] != COMMAND


def save(path: Path, data: dict) -> None:
    backup = path.with_name(path.name + ".ids-backup")
    if not backup.exists():
        shutil.copy2(path, backup)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def run(command: str, path: Path) -> int:
    keys = load(path)
    if command in ("check", "add") and conflict(keys):
        sys.stderr.write("%s: %s is already bound to %s\n" % (path, KEY, keys["global"][KEY]))
        return 1
    bound = keys["global"]
    if command == "add" and bound.get(KEY) != COMMAND:
        bound[KEY] = COMMAND
        save(path, keys)
    elif command == "remove" and bound.get(KEY) == COMMAND:
        del bound[KEY]
        save(path, keys)
    return 0


def main(argv: List[str]) -> int:
    if len(argv) != 2 or argv[0] not in ("check", "add", "remove"):
        sys.stderr.write(__doc__)
        return 2
    try:
        return run(argv[0], Path(argv[1]))
    except KeysError as exc:
        sys.stderr.write("%s\n" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
