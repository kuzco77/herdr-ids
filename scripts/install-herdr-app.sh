#!/usr/bin/env bash
# Install (or remove) the ids popup in the Herdr desktop app (herdr-app).
#
#   scripts/install-herdr-app.sh              install / reinstall
#   scripts/install-herdr-app.sh --uninstall
#
# Links herdr-app/ids into ~/.config/herdr-app/mods/ids and binds ctrl-a i to
# mod.open:ids. The herdr TUI plugin (herdr-plugin.toml) is separate and keeps working.
# keys.json is copied once to keys.json.ids-backup before the first edit.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
app_home="${HERDR_APP_HOME:-$HOME/.config/herdr-app}"
mod="ids"
mod_link="$app_home/mods/$mod"
keys="$app_home/keys.json"
keys_tool="$repo/scripts/herdr_app_keys.py"

die() {
  echo "$*" >&2
  exit 1
}

install() {
  # Fail before touching anything: a key conflict or bad keys.json must not leave a half install.
  python3 "$keys_tool" check "$keys"
  if [ -e "$mod_link" ] && [ ! -L "$mod_link" ]; then
    die "$mod_link exists and is not our link; move it away first"
  fi
  mkdir -p "$app_home/mods"
  ln -sfn "$repo/herdr-app/$mod" "$mod_link"
  herdr-app check "$mod_link"
  python3 "$keys_tool" add "$keys"
  echo "installed $mod (key ctrl-a i, or run mod.open:ids from the palette)"
}

uninstall() {
  if [ -f "$keys" ]; then
    python3 "$keys_tool" remove "$keys"
  fi
  if [ -L "$mod_link" ]; then
    rm "$mod_link"
  fi
  echo "removed $mod and its key"
}

command -v herdr-app >/dev/null || die "herdr-app not on PATH"
[ -d "$app_home" ] || die "$app_home not found; open the Herdr app once first"

if [ "${1:-}" = "--uninstall" ]; then
  uninstall
else
  install
fi
