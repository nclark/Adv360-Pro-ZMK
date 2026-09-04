#!/bin/sh
# Toggle the Adv360 keymap cheat sheet popup (bound to ctrl+alt+cmd+shift-k in skhd).
#
# The page is a single self-contained HTML file rendered by keymap-viewer/gen_keymap.py
# and shown in a chromeless Chrome --app= window. The yabai rule in ~/.config/yabai/yabairc
# floats and centers it (manage=off, grid). We do NOT use a yabai scratchpad: show/hide
# needs the scripting addition, which needs SIP off. Instead the hotkey is focus/close:
#   window focused       -> close it, then refocus whatever was focused before
#   window in background -> bring it to the front
#   no window            -> regenerate the page, launch, and raise it
#
# `show_keymap.sh --restore` only refocuses the previously focused window. A yabai
# window_destroyed signal calls it so Esc / q inside the page also restore focus.
cd "$(dirname "$0")/.."
TITLE="Adv360 keymap"
PREV="${TMPDIR:-/tmp}/adv360-keymap.prev"

# Focus restore. Prefer a yabai window id; fall back to the frontmost app name
# (yabai sometimes cannot report the focused window; the app is the next best thing).
restore() {
  if [ -s "$PREV" ]; then
    prev=$(cat "$PREV")
    case "$prev" in
      *[!0-9]*) osascript -e "tell application \"$prev\" to activate" >/dev/null 2>&1 ;;
      *)        yabai -m window --focus "$prev" >/dev/null 2>&1 ;;
    esac
  fi
  rm -f "$PREV"
}
if [ "$1" = "--restore" ]; then restore; exit 0; fi

save_prev() {
  yabai -m query --windows 2>/dev/null | python3 -c '
import json, sys
ws = [w for w in json.load(sys.stdin) if w["has-focus"] and w["title"] != sys.argv[1]]
print(ws[0]["id"]) if ws else sys.exit(1)' "$TITLE" > "$PREV" 2>/dev/null \
  || osascript -e 'tell application "System Events" to get name of first process whose frontmost is true' > "$PREV" 2>/dev/null \
  || rm -f "$PREV"
}

# prints "<window id> <1 if focused else 0>", or nothing if no window.
# yabai can emit malformed JSON while a window is being created/destroyed;
# retry a few times, and give up (exit 1) rather than launch a duplicate.
state() {
  yabai -m query --windows | python3 -c '
import json, sys
ws = [w for w in json.load(sys.stdin) if w["title"] == sys.argv[1]]
print(ws[0]["id"], int(ws[0]["has-focus"])) if ws else None' "$TITLE" 2>/dev/null
}
query() {
  n=0
  while [ $n -lt 5 ]; do
    if out=$(state); then printf '%s\n' "$out"; return 0; fi
    n=$((n + 1)); sleep 0.1
  done
  return 1
}

set -- $(query) || exit 1
if [ -n "$1" ]; then
  if [ "$2" = 1 ]; then
    yabai -m window --close "$1"
    restore
  else
    save_prev
    yabai -m window --focus "$1"
  fi
  exit 0
fi

save_prev
python3 keymap-viewer/gen_keymap.py >/dev/null
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --app="file://$PWD/keymap-viewer/keymap.html" >/dev/null 2>&1 &

# Chrome does not activate when launched from skhd; raise the window once it exists.
i=0
while [ $i -lt 40 ]; do
  sleep 0.1
  set -- $(query)
  if [ -n "$1" ]; then
    yabai -m window --focus "$1"
    exit 0
  fi
  i=$((i + 1))
done
