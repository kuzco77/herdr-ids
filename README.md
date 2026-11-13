# herdr-ids

A [herdr](https://herdr.dev) plugin that shows the ids of the focused pane in a popup and
copies the one you pick to the clipboard.

```
 herdr ids  (pane w26:p41)

  1  workspace id   w26
  2  tab id         w26:t22
  3  pane id        w26:p41
  4  agent          claude
  5  agent session  7ed0e343-c95a-4e9a-8aaa-7b169faed0ff
  6  agent status   working
  7  cwd            /Users/me/project

  a  all (one line)
  q  quit

press a key to copy:
```

Useful when you drive herdr from the CLI (`herdr pane read`, `herdr agent prompt`,
`herdr wait agent-status`, ...) and need a current id without parsing `herdr pane list`.

## Install

```bash
herdr plugin install kuzco77/herdr-ids
```

Then bind the action in `~/.config/herdr/config.toml`:

```toml
[[keys.command]]
key = "prefix+i"
type = "plugin_action"
command = "herdr-ids.show"
description = "pane/tab/agent ids"
```

Reload with `herdr server reload-config`.

## Pane ids on borders

The plugin also labels every pane border `<name> - <pane id>`, e.g. `claude - w5W:p2`:

- `<name>` is your own pane label if you set one (`herdr pane rename`), else the agent, else the
  foreground process (`zsh`, `nvim`, ...).
- Labels are applied at server startup and refreshed on pane, tab and workspace events, because
  pane ids can change when tabs or panes close.
- A single pane has no border with the default `ui.pane_borders = "auto"`. Set
  `ui.pane_borders = "always"` to see the label there too.

Turn it off or on with the plugin actions (bind them like `show` if you use them often):

| Action | Effect |
|---|---|
| `herdr-ids.labels-off` | Stop labelling; restore your own labels and clear the ones the plugin added |
| `herdr-ids.labels-on` | Label all panes again and keep them current |

Run `labels-off` before uninstalling, otherwise the last labels stay on the panes.

## Herdr app

The same popup ships as a mod for the Herdr desktop app (`herdr-app`), in
`herdr-app/ids`. The TUI plugin above is unaffected; install either or both.

```bash
bash scripts/install-herdr-app.sh              # install / reinstall
bash scripts/install-herdr-app.sh --uninstall
```

The installer links `herdr-app/ids` into `~/.config/herdr-app/mods/ids`, runs
`herdr-app check` on it, and binds `ctrl-a i` to `mod.open:ids` in
`~/.config/herdr-app/keys.json`. It stops before changing anything when `keys.json` is
missing, is not valid JSON, or already binds `ctrl-a i` to something else, or when
`mods/ids` exists and is not its link. `keys.json` is rewritten as 2-space JSON; the
original is copied once to `keys.json.ids-backup`. Uninstall removes the key (only while
it still opens `ids`) and the link.

The app popup lists what the app knows about the focused pane:

| Row | Value |
|---|---|
| `space` | space id (space name beside it) |
| `tab` | tab id (tab name beside it) |
| `pane` | pane id |
| `terminal` | herdr-core address for `hc` (`t7`, or `machine/t7` for a remote terminal) |
| `agent` | what the agent reports (`claude-code`), else the program name |
| `status` | agent status |
| `cwd` | folder |

Rows without a value are left out, so the numbers can shift (a shell pane has no
`agent` or `status`). herdr-core reports no agent session id, so the app popup has no
`agent session` row. The keys are the same as in the TUI, and clicking a row copies it.
Pane border labels are TUI only: in the app, a pane header mod
(e.g. herdr-accept-tool's `accept-header`) shows the terminal address.

## Keys in the popup

| Key | Action |
|---|---|
| `1`..`7` | Copy that value and close |
| `a` | Copy all ids as one line: `workspace_id=… tab_id=… pane_id=… agent=… agent_session=… …` |
| `q` / `Esc` | Close without copying |

A toast confirms what was copied.

## Requirements

- herdr `>= 0.9.0`
- `bash`, `python3`
- a clipboard tool: `pbcopy` (macOS), `wl-copy`, `xclip` or `xsel` (Linux)
- Herdr app mod: `herdr-app` on `PATH` and `python3` for the installer; the app copies
  through its own clipboard

## Notes

- Ids are read live from `herdr pane get` when the popup opens. herdr ids can compact when
  tabs or panes close, so always copy at the moment you need them.
- Labels update when herdr reports a change. A process started in a shell is picked up when the
  pane's terminal title changes (`pane.updated`); shells that never set a title keep the old name
  until the next pane event.
- `agent session` is the agent's session uuid as reported by herdr (`agent_session.value`).
- Local development: `herdr plugin link /path/to/herdr-ids`.

## Tests

```bash
python3 -m unittest discover -s tests -v
node --test tests/js/
```

## License

MIT
