# Patches to the Kinesis ZMK fork

Applied with `git apply` on top of the `refil/zmk` revision in `config/west.yml`
by the Dockerfile, after `west update`. Builds happen on this machine only. If the
revision in `west.yml` ever changes and a patch no longer applies, the image build
fails at that step: regenerate the patch against the new source.

- `0001-low-battery-indicator.patch`: new Kconfig options
  `ZMK_RGB_UNDERGLOW_LOW_BATTERY_THRESHOLD` and `..._BLINK`. While a half's own
  charge is at or below the threshold, that half's leftmost indicator LED (caps
  lock on the left, num lock on the right) shows the battery colour: green above
  80, yellow 50-79, orange 20-49, red below 20, same as Mod + Hotkey 4. At or
  below the blink level it blinks at 1 Hz. Set in both `adv360_*_defconfig`:
  threshold 40, blink 20. 0 disables either.
