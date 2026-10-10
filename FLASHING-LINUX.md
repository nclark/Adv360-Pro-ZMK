# Flashing the Advantage 360 Pro on Linux

Linux-specific companion to the "Flashing firmware" section of [README.md](README.md).
Written for an Arch/Omarchy desktop (Hyprland, `udiskie` automount, Nautilus), but the
commands are plain `udisks2`, so they work on any systemd distro.

## What the keyboard looks like to Linux

In bootloader mode each half shows up as a USB mass-storage device with the FAT label
`ADV360PRO`. With `udiskie --automount` running (it is, on this machine) it mounts at:

```
/run/media/$USER/ADV360PRO
```

Copying a `.uf2` file to that drive flashes it. The keyboard flashes blue while writing,
then reboots and disconnects on its own. Linux will often print "device not ejected",
"I/O error" or a Nautilus warning at that point. That is expected and does not mean the
flash failed.

## Which keys enter the bootloader

On this keymap the stock Kinesis hotkeys still hold `&bootloader` on the Mod layer
(`config/layers/mod.dtsi`). Positions are from `assets/key-positions.md`.

| Half | Keys | Positions |
|---|---|---|
| Left | hold Mod, tap left inner-column key below Kp (stock legend "hotkey 1") | Mod = 75, hotkey = 20 |
| Right | hold Mod, tap right inner-column key below Mod (stock legend "hotkey 3") | Mod = 75, hotkey = 21 |

Fallback: double-click the physical bootloader button on the underside of the half with a
paperclip. The timing is fiddly; it may take a couple of tries. The button locations are in
section 2.7 of the user manual in `restore/`.

Only the half connected over USB can be flashed. Open one drive at a time so the two halves
cannot be mixed up.

## Flashing both halves

Build first (`make`), then from the repo root:

1. **Left half.** Switch it on and connect it to the computer with USB-C.
2. Hold Mod and tap hotkey 1. Wait for the drive to mount:

   ```sh
   until [ -d /run/media/$USER/ADV360PRO ]; do sleep 0.5; done; echo mounted
   ```

3. Copy the newest left firmware and flush the write. `sync` matters: Linux buffers the
   copy, and the keyboard only reboots once the whole file has landed.

   ```sh
   cp "$(ls -t firmware/*-left-clique.uf2 | head -1)" /run/media/$USER/ADV360PRO/ && sync
   ```

   The drive disappears by itself within a few seconds. Ignore any eject or I/O error
   message.

4. Unplug the left half, and switch **both** halves off.
5. Switch the left half on (no USB).
6. **Right half.** Connect it over USB. Hold Mod and tap hotkey 3. Wait for the mount as in
   step 2.
7. Copy the right firmware:

   ```sh
   cp "$(ls -t firmware/*-right-clique.uf2 | head -1)" /run/media/$USER/ADV360PRO/ && sync
   ```

8. Unplug the right half and switch it on. The halves re-pair with each other.
9. Check the build you are running: hold Mod and tap V to type the version string
   (date, branch prefix, commit).

Local builds are named `<timestamp>-<commit>-left-clique.uf2` and
`...-right-clique.uf2`. GitHub Actions artifacts use the same scheme without the `-clique`
suffix.

## Settings reset

If the halves will not pair, or Bluetooth profiles behave oddly after a flash, flash
`settings-reset.uf2` (repo root, same file as `restore/Adv360 Pro Settings Reset (Clique).uf2`)
to **each** half using the same steps, then flash the real firmware again. Bluetooth
pairings on the computer side need to be removed and re-done afterwards.

## Troubleshooting

**Drive never appears.** Check the kernel saw the device and whether it got mounted:

```sh
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT
journalctl -k -n 30 --no-pager
```

If `lsblk` shows the `ADV360PRO` partition with no mountpoint, mount it by hand:

```sh
udisksctl mount -b /dev/sdX1     # use the device from lsblk
```

If `udiskie` is not running (`pgrep -a udiskie` prints nothing), start it:

```sh
udiskie --automount --no-notify --no-tray &
```

You can also open the drive in Nautilus and drag the file onto it; that goes through the
same `udisks2` path. Beware that a drag can **move** the file instead of copying it (it
happened here), which leaves `firmware/` without the build you just flashed. Hold Ctrl while
dragging to force a copy, or use the `cp` commands above.

**Copy hangs, then errors.** The keyboard rebooted before the writeback finished. Check the
version with Mod+V. If it is still the old build, redo the flash with the `&& sync` form.

**Wrong file on the wrong half.** The left firmware on the right half (or vice versa) will
not brick it. Enter the bootloader with the physical button and flash the correct file.

**Keystrokes stop working while a drive is open.** Normal. Nothing is sent while the half is
in bootloader mode.
