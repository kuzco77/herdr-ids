#!/usr/bin/env bash
# Action entrypoint. Resolve the pane that was focused when the action fired, then open the
# picker popup with that pane id in its environment (a popup has no pane id of its own).
set -euo pipefail

herdr_bin="${HERDR_BIN_PATH:-herdr}"

pane="${HERDR_ACTIVE_PANE_ID:-${HERDR_PANE_ID:-}}"

if [ -z "$pane" ] && [ -n "${HERDR_PLUGIN_CONTEXT_JSON:-}" ]; then
  pane=$(printf '%s' "$HERDR_PLUGIN_CONTEXT_JSON" | python3 -c '
import sys, json
c = json.load(sys.stdin)
print(c.get("focused_pane_id") or c.get("pane_id") or (c.get("pane") or {}).get("pane_id") or "")
' 2>/dev/null || true)
fi

if [ -z "$pane" ]; then
  pane=$("$herdr_bin" pane current \
    | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
fi

exec "$herdr_bin" plugin pane open \
  --plugin herdr-ids \
  --entrypoint picker \
  --placement popup \
  --width 64 \
  --height 16 \
  --env "HERDR_IDS_PANE=$pane" \
  --focus
