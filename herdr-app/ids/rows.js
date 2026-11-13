// The rows the ids popup lists. No imports, so Node can test it.

/**
 * [label, value, note] for each id of the focused pane that has a value.
 * `focus` is `focused()`, `spaces` is `spaces()`, `panes` is `panes()`.
 * `terminal` is the herdr-core address that `hc` takes (`t7`, or `machine/t7` when remote).
 */
export function idRows(focus, spaces, panes) {
  if (!focus) return [];
  const space = spaces.find((s) => s.id === focus.space);
  const tab = space?.tabs.find((t) => t.id === focus.tab);
  const pane = panes.find((p) => p.pane === focus.pane);
  const agent = pane?.program?.agent ? pane.app ?? pane.program.name : null;
  return [
    ["space", focus.space, space?.name],
    ["tab", focus.tab, tab?.name],
    ["pane", focus.pane],
    ["terminal", focus.terminal],
    ["agent", agent],
    ["status", pane?.status],
    ["cwd", focus.cwd ?? pane?.cwd],
  ].filter(([, value]) => value);
}

/** Every row as `label=value`, space-separated: the `a` (all) copy. */
export function allLine(rows) {
  return rows.map(([label, value]) => `${label}=${value}`).join(" ");
}
