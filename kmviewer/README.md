# KMViewer - Terminal Image Viewer

A fast, lightweight terminal-based image viewer built with Go and the Bubble Tea TUI framework. Designed for displaying PNG images directly in your terminal using the Kitty graphics protocol.

## Features

- **Terminal Graphics**: Direct PNG rendering using Kitty graphics protocol
- **Two-Pane Layout**: 90% image viewer, 10% navigation menu
- **Perfect Aspect Ratio**: Maintains original image proportions with terminal character compensation
- **Smart Sizing**: Responsive design that adapts to different screen sizes
- **Image Caching**: Fast loading and switching between images
- **Clean Navigation**: Intuitive keyboard controls for browsing multiple images
- **Auto-Centering**: Images are automatically centered in the viewer pane

## Requirements

- **Terminal**: Kitty terminal emulator (required for image display)
- **Go**: Version 1.19+ for building from source

## Installation

### Build from Source

```bash
# Clone and navigate to the kmviewer directory
cd kmviewer

# Build the application
./build.sh

# Or manually:
go build -o kmviewer
```

## Usage

```bash
# View a single image
./kmviewer image.png

# View multiple images with navigation
./kmviewer layer-0-base.png layer-1-keypad.png layer-2-function.png

# Example with keymap images
./kmviewer assets/*.png
```

## Navigation

| Key | Action |
|-----|--------|
| `h`, `←`, `Shift+Tab` | Previous image |
| `l`, `→`, `Tab` | Next image |
| `q`, `Ctrl+C` | Quit |

## Features

### Image Display
- **Native Kitty Sizing**: Uses Kitty's `c=columns,r=rows` parameters for optimal display
- **Aspect Ratio Preservation**: Compensates for terminal character dimensions (14×26 pixels)
- **Edge Safety**: Automatically adds margins to prevent clipping at terminal boundaries
- **Dynamic Sizing**: Adapts to terminal window size changes

### Menu System
- **Clean Filenames**: Automatically removes prefixes and `.png` extensions
  - `layer-0-base.png` → `base`
  - `adv360-keypad-layer.png` → `layer`
- **Visual Selection**: Selected image highlighted with dark blue background
- **Horizontal Layout**: Compact menu that doesn't waste vertical space

### Performance
- **Image Caching**: Loaded images are cached for instant switching
- **Smooth Transitions**: Screen clearing between images for clean display
- **Error Handling**: Graceful fallbacks for missing or corrupted images

## File Format Support

Currently supports:
- **PNG**: Primary format with full transparency support

## Technical Details

### Architecture
- **Bubble Tea**: Modern TUI framework for Go
- **Lipgloss**: Styling and layout library
- **Kitty Graphics**: Direct terminal image rendering protocol

### Optimizations
- Character aspect ratio compensation (14×26 pixel cells)
- 98% viewport utilization for maximum space usage
- Smart centering with margin calculations
- Minimal memory footprint with efficient caching

## Use Cases

- **Keymap Visualization**: Perfect for displaying keyboard layer diagrams
- **Image Previews**: Quick terminal-based image browsing
- **Documentation**: Visual references that stay in your terminal workflow
- **Presentations**: Terminal-native image display for demos

## Troubleshooting

### Image Not Displaying
- Ensure you're using Kitty terminal emulator
- Check that the image file exists and is a valid PNG
- Try adjusting terminal size if images appear clipped

### Navigation Issues
- Verify you're using supported key combinations
- Check that multiple images are provided as arguments

### Performance Issues
- Large images may take a moment to load initially
- Subsequent viewing of cached images should be instant

## Building

```bash
# Standard Go build
go build

# With build script (includes helpful output)
./build.sh

# Install dependencies
go mod tidy
```

## Contributing

idk Claude Code wrote it

## License

WTFPL