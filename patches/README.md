# Patches to the Kinesis ZMK fork

Applied with `git apply` on top of the `refil/zmk` revision in `config/west.yml`
by the Dockerfile, after `west update`. Builds happen on this machine only. If the
revision in `west.yml` ever changes and a patch no longer applies, the image build
fails at that step: regenerate the patch against the new source.

- `0001-low-battery-indicator.patch`: new Kconfig options
  `ZMK_RGB_UNDERGLOW_LOW_BATTERY_THRESHOLD` and `..._BLINK`. While a half's own
  charge is at or below the threshold, that half's leftmost indicator LED (caps
  lock on the left, num lock on the right) shows the battery band: yellow 20-49,
  red below 20 (Mod + Hotkey 4's orange reads as red on these LEDs, so the patch
  uses yellow for that band). At or below the blink level it blinks at 1 Hz. Set in both `adv360_*_defconfig`:
  threshold 40, blink 20. 0 disables either.
