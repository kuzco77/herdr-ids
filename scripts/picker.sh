#!/usr/bin/env bash
# Popup body. Lists the ids of the target pane and copies the chosen one to the clipboard.
# Target pane: $HERDR_IDS_PANE (set by open.sh), else the currently focused pane.
set -euo pipefail

herdr_bin="${HERDR_BIN_PATH:-herdr}"

pane="${HERDR_IDS_PANE:-${HERDR_ACTIVE_PANE_ID:-}}"
if [ -z "$pane" ]; then
  pane=$("$herdr_bin" pane current \
    | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
fi

copy_to_clipboard() {
  if command -v pbcopy >/dev/null 2>&1; then
    printf '%s' "$1" | pbcopy
  elif command -v wl-copy >/dev/null 2>&1; then
    printf '%s' "$1" | wl-copy
  elif command -v xclip >/dev/null 2>&1; then
    printf '%s' "$1" | xclip -selection clipboard
  elif command -v xsel >/dev/null 2>&1; then
    printf '%s' "$1" | xsel --clipboard --input
  else
    return 1
  fi
}

# one "label<TAB>value" line per row
rows=$("$herdr_bin" pane get "$pane" | python3 -c '
import sys, json
p = json.load(sys.stdin)["result"]["pane"]
session = p.get("agent_session") or {}
rows = [
    ("workspace id",  p.get("workspace_id") or "-"),
    ("tab id",        p.get("tab_id") or "-"),
    ("pane id",       p.get("pane_id") or "-"),
    ("agent",         p.get("agent") or "-"),
    ("agent session", session.get("value") or "-"),
    ("agent status",  p.get("agent_status") or "-"),
    ("cwd",           p.get("cwd") or "-"),
]
for k, v in rows:
    print(f"{k}\t{v}")
')

labels=()
values=()
while IFS=$'\t' read -r k v; do
  labels+=("$k")
  values+=("$v")
done <<< "$rows"

all_line=""
for i in "${!labels[@]}"; do
  key=$(printf '%s' "${labels[$i]}" | tr ' ' '_')
  all_line+="${key}=${values[$i]} "
done

bold=$'\e[1m'; dim=$'\e[2m'; cyan=$'\e[36m'; green=$'\e[32m'; reset=$'\e[0m'

draw() {
  clear
  printf '%s herdr ids %s %s(pane %s)%s\n\n' "$bold" "$reset" "$dim" "$pane" "$reset"
  for i in "${!labels[@]}"; do
    printf '  %s%d%s  %-14s %s%s%s\n' "$cyan" $((i + 1)) "$reset" "${labels[$i]}" "$green" "${values[$i]}" "$reset"
  done
  printf '\n  %sa%s  all (one line)\n' "$cyan" "$reset"
  printf '  %sq%s  quit\n\n' "$cyan" "$reset"
  printf '%spress a key to copy: %s' "$dim" "$reset"
}

copy_and_exit() {
  if copy_to_clipboard "$1"; then
    "$herdr_bin" notification show "copied: $2" --body "$1" --position top-right --sound none >/dev/null 2>&1 || true
  else
    "$herdr_bin" notification show "no clipboard tool" --body "install pbcopy, wl-copy, xclip or xsel" --position top-right --sound none >/dev/null 2>&1 || true
  fi
  exit 0
}

draw
while true; do
  IFS= read -rsn1 key
  case "$key" in
    [1-9])
      idx=$((key - 1))
      if [ "$idx" -lt "${#labels[@]}" ]; then
        copy_and_exit "${values[$idx]}" "${labels[$idx]}"
      fi
      ;;
    a|A) copy_and_exit "${all_line% }" "all ids" ;;
    q|Q|$'\e') exit 0 ;;
  esac
done
