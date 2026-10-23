#!/usr/bin/env python3
# Pane border labels: keep every pane labelled "<name> - <pane id>".
#
# <name> is the manual label the user set, else the agent, else the foreground process.
# Pane ids compact when tabs or panes close, so every run relabels all panes. State is
# keyed by terminal_id (stable across id changes) and remembers which label this plugin
# applied, so a label that differs from it is recognised as a manual rename.
#
# usage: labels.py        relabel all panes (startup / event hooks); no-op while labels are off
#        labels.py --on   turn labels on and relabel
#        labels.py --off  turn labels off: restore manual labels, remove the ones this plugin added
import json
import os
import re
import subprocess
import sys
import time

HERDR = os.environ.get("HERDR_BIN_PATH") or "herdr"
STATE_DIR = os.environ.get("HERDR_PLUGIN_STATE_DIR") or os.path.expanduser("~/.local/state/herdr-ids")
STATE_FILE = os.path.join(STATE_DIR, "labels.json")
LOCK_DIR = os.path.join(STATE_DIR, "labels.lock")
DIRTY_FILE = os.path.join(STATE_DIR, "labels.dirty")
OFF_FILE = os.path.join(STATE_DIR, "labels.off")
STALE_LOCK_SECONDS = 60
SEP = " - "
ID_SUFFIX = re.compile(SEP + r"w[0-9A-Za-z]+:p[0-9A-Za-z]+$")


def herdr(*args):
    out = subprocess.run([HERDR, *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out)["result"]


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def process_name(pane_id):
    try:
        info = herdr("pane", "process-info", "--pane", pane_id)["process_info"]
    except (subprocess.CalledProcessError, ValueError, KeyError):
        return None
    procs = info.get("foreground_processes") or []
    leader = next((p for p in procs if p.get("pid") == info.get("foreground_process_group_id")), None)
    proc = leader or (procs[-1] if procs else None)
    if not proc:
        return None
    # argv0 rather than name: name can be a version string (claude reports "2.1.303")
    argv0 = proc.get("argv0") or proc.get("name") or ""
    return os.path.basename(argv0).lstrip("-") or None


def manual_label(pane, entry):
    """The user's own label for this pane, or None when the label is ours or unset."""
    current = pane.get("label")
    if not current:
        return None
    if entry is not None and current == entry.get("applied"):
        return entry.get("manual")
    name = ID_SUFFIX.sub("", current)
    if entry is None and name != current:
        # Labelled before this plugin's state was lost (e.g. new terminal ids after a server
        # restart): it is ours if the name is what this plugin would have generated.
        generated = {pane.get("display_agent"), pane.get("agent"), "shell"}
        if name in generated or name == process_name(pane["pane_id"]):
            return None
    return name


def relabel(event_pane):
    state = load_state()
    panes = herdr("pane", "list")["panes"]
    new_state = {}
    for p in panes:
        pane_id, term = p["pane_id"], p.get("terminal_id") or p["pane_id"]
        entry = state.get(term)
        current = p.get("label")
        manual = manual_label(p, entry)
        process = entry.get("process") if entry else None
        if manual is None and not p.get("agent") and (process is None or pane_id == event_pane):
            process = process_name(pane_id) or process
        name = manual or p.get("display_agent") or p.get("agent") or process or "shell"
        label = name + SEP + pane_id
        if label != current:
            rename(pane_id, label)
        new_state[term] = {"applied": label, "manual": manual, "process": process}
    save_state(new_state)


def rename(pane_id, label):
    try:
        herdr("pane", "rename", pane_id, label)
    except (subprocess.CalledProcessError, ValueError):
        pass  # pane closed since it was listed; the close event triggers another run


def clear():
    state = load_state()
    for p in herdr("pane", "list")["panes"]:
        entry = state.get(p.get("terminal_id") or p["pane_id"])
        current = p.get("label")
        ours = current == entry.get("applied") if entry else bool(current and ID_SUFFIX.search(current))
        if ours:
            rename(p["pane_id"], manual_label(p, entry) or "--clear")
    save_state({})


def event_pane_id():
    try:
        data = json.loads(os.environ.get("HERDR_PLUGIN_EVENT_JSON") or "null")
    except ValueError:
        return None
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if isinstance(node.get("pane_id"), str):
                return node["pane_id"]
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return None


def acquire_lock(wait):
    while True:
        try:
            os.mkdir(LOCK_DIR)
            return True
        except FileExistsError:
            try:
                if time.time() - os.stat(LOCK_DIR).st_mtime >= STALE_LOCK_SECONDS:
                    os.rmdir(LOCK_DIR)
                elif not wait:
                    return False
                else:
                    time.sleep(0.1)
            except FileNotFoundError:
                pass


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode == "--off":
        open(OFF_FILE, "w").close()  # stops event runs before they relabel again
        acquire_lock(wait=True)
        try:
            clear()
        finally:
            os.rmdir(LOCK_DIR)
        return
    if mode == "--on" and os.path.exists(OFF_FILE):
        os.remove(OFF_FILE)
    if os.path.exists(OFF_FILE):
        return
    event_pane = event_pane_id()
    # Events arrive in bursts (a tab close emits several). A run that finds the lock taken
    # marks the state dirty and leaves; the lock holder repeats until nothing is pending.
    open(DIRTY_FILE, "w").close()
    if not acquire_lock(wait=False):
        return
    try:
        while os.path.exists(DIRTY_FILE) and not os.path.exists(OFF_FILE):
            os.remove(DIRTY_FILE)
            relabel(event_pane)
            event_pane = None
    finally:
        os.rmdir(LOCK_DIR)


if __name__ == "__main__":
    main()
