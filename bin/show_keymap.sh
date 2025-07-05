 #!/bin/bash

# Generate and display keymap visualization
# Note: `pip install keymap-drawer`

set -e

KEYMAP_FILE="$HOME/workspace/projects/Adv360-Pro-ZMK/config/adv360.keymap"
TMP_DIR=$(mktemp -d)
SVG_FILE="$TMP_DIR/keymap.svg"

keymap parse -z "$KEYMAP_FILE" | keymap draw - > "$SVG_FILE"

open -a "Chromium" "$SVG_FILE"
