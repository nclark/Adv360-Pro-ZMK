# Advantage 360 Pro ZMK Firmware - Claude Code Guide

## Project Overview
This repository contains the ZMK firmware configuration for the Kinesis Advantage 360 Pro keyboard (Clique variant, V3.0). It uses a custom ZMK fork with Advantage 360 Pro specific functionality.

- **Custom ZMK Fork**: `refil/zmk:adv360-z3.5-2` (defined in `config/west.yml`)
- **Current Branch**: `local` (for personal customizations)
- **Main Branch**: `V3.0` (for pull requests)
- **Keyboard Type**: Split ergonomic keyboard with pointing device support

## ⚠️ IMPORTANT: Key Position Reference

**ALWAYS refer to `assets/key-positions.md` for precise key mapping!**

This file contains the definitive key position mappings for the Advantage 360 Pro:

- **Visual Reference**: `assets/key-positions.png` - Visual diagram of all key positions
- **Code Definitions**: `assets/key-positions.md` - Numerical position mappings

### Key Position Ranges:
- **Left Main Keys**: `0-6, 14-20, 28-34, 46-51, 60-64`
- **Right Main Keys**: `7-13, 21-27, 39-45, 54-59, 71-75`
- **Left Thumb Cluster**: `35-36, 52, 65-67`
- **Right Thumb Cluster**: `37-38, 53, 68-70`

### Homerow Positions:
- **Left Homerow**: `28=A, 29=S, 30=D, 31=F`
- **Right Homerow**: `42=J, 43=K, 44=L, 45=;`

**When discussing specific keys, always reference these position numbers or the visual diagram to avoid confusion.**

## Key Configuration Files

### Primary Keymap
- **`config/adv360.keymap`**: Main keymap configuration
  - Layer 0: Base (QWERTY)
  - Layer 1: Keypad (numerical keypad mode)
  - Layer 2: Function (F1-F12 keys)
  - Layer 3: Mod (system controls, RGB, Bluetooth)
  - Layers 4-7: Reserved for future use
  - Includes homerow mods behavior with 200ms tapping term

### Macro Definitions
- **`config/macros.dtsi`**: Extensive macro library including:
  - Text editing macros (quotes, brackets, parens)
  - Windows shortcuts (Cut/Copy/Paste, Explorer, Snip Tool, etc.)
  - Mac shortcuts (Mission Control, Spotlight Search, etc.)
  - Window management (tiling, desktop switching)
  - Special: Double-click macro for pointing device

### Hardware Configuration
- **`config/boards/arm/adv360/adv360_left_defconfig`**: Hardware feature toggles
  - Battery reporting: `CONFIG_BT_BAS=n` (disabled by default)
  - Extended NKRO: `CONFIG_ZMK_HID_KEYBOARD_EXTENDED_REPORT=n` (F13-F24 disabled)
  - RGB underglow: Enabled with auto-off on idle
  - Backlight: PWM-based, starts at 20% brightness
  - Pointing device: `CONFIG_ZMK_POINTING=y` (Clique support)

### Version Control
- **`config/version.dtsi`**: Version information (currently empty)
- **`config/west.yml`**: ZMK fork specification

## Build System

### Local Building
```bash
make           # Build both halves
make left      # Build left half only
make clean     # Clean all build artifacts
```

### Cloud Building (GitHub Actions)
1. Push commit to trigger build
2. Download artifacts from Actions tab
3. Firmware files are timestamped: `YYYYMMDD-HHMM-COMMIT-left.uf2`

### Output Location
- **`firmware/`**: Local build output directory
- Generates `.uf2` files for each keyboard half

## Flashing Process

### Standard Flashing
1. **Left Half**: Connect USB, press `Mod+macro1` for bootloader mode
2. Copy `left.uf2` to mounted drive
3. **Right Half**: Connect USB, press `Mod+macro3` for bootloader mode
4. Copy `right.uf2` to mounted drive

### Reset Files (in `/restore/`)
- Factory firmware: `202502091719-091a5d4-left.uf2`, `202502091719-091a5d4-right.uf2`
- Settings reset: `Adv360 Pro Settings Reset (Clique).uf2`
- Documentation: Multiple PDF manuals and guides

## Layer System

### Layer Colors (Visual Indication)
- Layer 0: Black (off)
- Layer 1: White
- Layer 2: Blue
- Layer 3: Green
- Higher layers cycle through additional colors

### Layer Access
- **Layer 1**: `&tog 1` (toggle keypad)
- **Layer 2**: `&mo 2` (momentary function)
- **Layer 3**: `&mo 3` (momentary mod)

## Common Customization Tasks

### Adding New Macros
1. Edit `config/macros.dtsi`
2. Add new macro definition
3. Reference in `config/adv360.keymap` with `&macro_name`

### Modifying Key Layout
1. Edit `config/adv360.keymap`
2. Modify bindings arrays for desired layer
3. Use ZMK keycodes from documentation

### Enabling Hardware Features
1. Edit `config/boards/arm/adv360/adv360_left_defconfig`
2. Change `=n` to `=y` for desired features
3. Rebuild firmware

### Adding Custom Behaviors
1. Add to behaviors section in `config/adv360.keymap`
2. Define parameters (tapping-term-ms, etc.)
3. Reference in keymap bindings

## Key Position Reference
- See `assets/key-positions.md` for matrix positions
- Use for advanced features like combos
- Layout documentation available in repository

## Bluetooth Management
- **Pairing**: Bluetooth profiles 0-4 available via `&bt BT_SEL X`
- **Clear**: `&bt BT_CLR` to clear current profile
- **Battery**: Reporting disabled by default (prevents wake issues)

## RGB and Lighting
- **RGB Underglow**: Configurable effects via `&rgb_ug RGB_TOG`
- **Backlight**: PWM-based key lighting via `&bl BL_TOG`
- **Indicators**: CAPS/NUM/SCROLL lock LEDs
- **Auto-off**: Both RGB and backlight auto-disable on idle

## Pointing Device (Clique)
- **Configuration**: Enabled via `CONFIG_ZMK_POINTING=y`
- **Macros**: Double-click macro available
- **Bindings**: Use `&mkp` for mouse button presses

## Advanced Features
- **Studio Mode**: `&studio_unlock` for ZMK Studio compatibility
- **Bootloader**: `&bootloader` for manual bootloader entry
- **Version Info**: `&macro_ver` outputs build information (Mod+V)

## File Structure Summary
```
config/
├── adv360.keymap              # Main keymap configuration
├── macros.dtsi                # Macro definitions
├── version.dtsi               # Version info (empty)
├── west.yml                   # ZMK fork specification
├── keymap.json                # GUI editor compatible format
└── boards/arm/adv360/
    ├── adv360_left_defconfig  # Left half hardware config
    ├── adv360_right_defconfig # Right half hardware config
    └── ...                    # Device tree files
```

## Troubleshooting
- **Build Failures**: Use `make clean` and rebuild
- **Bootloader Issues**: Use physical reset buttons on keyboard
- **Bluetooth Problems**: Clear profiles and re-pair
- **Layer Issues**: Check layer toggle/momentary bindings

## External Resources
- **ZMK Documentation**: https://zmk.dev/docs
- **Kinesis GUI Editor**: https://kinesiscorporation.github.io/Adv360-Pro-GUI
- **Support**: https://kinesis-ergo.com/support/kb360pro/