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

## Notes

- Ids are read live from `herdr pane get` when the popup opens. herdr ids can compact when
  tabs or panes close, so always copy at the moment you need them.
- Labels update when herdr reports a change. A process started in a shell is picked up when the
  pane's terminal title changes (`pane.updated`); shells that never set a title keep the old name
  until the next pane event.
- `agent session` is the agent's session uuid as reported by herdr (`agent_session.value`).
- Local development: `herdr plugin link /path/to/herdr-ids`.

## License

MIT
