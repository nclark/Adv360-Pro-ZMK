#!/usr/bin/env bash

# Script to generate layer images for the Advantage 360 Pro keyboard
# Dynamically parses the keymap file to determine layer order

set -eu

KEYMAP_FILE="config/adv360.keymap"
LAYERS_DIR="config/layers"

# Create img directory if it doesn't exist
mkdir -p img

# Clear existing layer images
echo "Clearing existing layer images..."
rm -f img/Layer*.svg img/Layer*.png img/layer_*.svg img/layer_*.png

# Check for required tools
if ! command -v inkscape &> /dev/null; then
  echo "Warning: Inkscape not found, PNG conversion will be skipped"
  HAS_INKSCAPE=false
else
  HAS_INKSCAPE=true
fi

# Extract layer includes from keymap file
echo "Parsing keymap file for layer order..."
LAYER_INCLUDES=$(grep -E '^\s*#include\s+"layers/.*\.dtsi"' "$KEYMAP_FILE")

# Generate images for each layer
echo "Generating layer images..."
LAYER_NUM=0

while read -r include_line; do
  # Extract the layer name from the include line
  LAYER_FILE=$(echo "$include_line" | sed -E 's/.*"layers\/(.*)\.dtsi".*/\1/')
  
  # Get the display name from the layer file if available
  if [ -f "$LAYERS_DIR/$LAYER_FILE.dtsi" ]; then
    DISPLAY_NAME=$(grep -E '^\s*display-name\s*=\s*"[^"]*"' "$LAYERS_DIR/$LAYER_FILE.dtsi" | head -1 | sed -E 's/.*"([^"]*)".*/\1/')
    
    # If no display-name found, use the file name
    if [ -z "$DISPLAY_NAME" ]; then
      DISPLAY_NAME="$LAYER_FILE"
    fi
    
    # Format the layer number with leading zero
    FORMATTED_NUM=$(printf "%02d" $LAYER_NUM)
    
    # Use lowercase name for the filename
    LOWERCASE_NAME=$(echo "$DISPLAY_NAME" | tr '[:upper:]' '[:lower:]')
    
    SVG_FILE="img/layer_${FORMATTED_NUM}-${LOWERCASE_NAME}.svg"
    PNG_FILE="img/layer_${FORMATTED_NUM}-${LOWERCASE_NAME}.png"
    
    echo "  Creating ${SVG_FILE}... (from $LAYER_FILE.dtsi)"
    keymap parse -z "$KEYMAP_FILE" | keymap draw - -s "$DISPLAY_NAME" -o "$SVG_FILE"
    
    # Convert SVG to PNG using Inkscape
    if [ "$HAS_INKSCAPE" = true ]; then
      echo "  Converting to ${PNG_FILE}..."
      inkscape --export-filename="$PNG_FILE" --export-dpi=300 "$SVG_FILE" >/dev/null 2>&1
    fi
    
    LAYER_NUM=$((LAYER_NUM + 1))
  else
    echo "  Warning: Layer file $LAYERS_DIR/$LAYER_FILE.dtsi not found, skipping"
  fi
done <<< "$LAYER_INCLUDES"

echo "Layer images generated successfully!"