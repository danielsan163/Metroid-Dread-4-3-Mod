# Metroid Dread 4:3

A 4:3 aspect ratio patch for Metroid Dread (Switch), shipped as exefs patches
(`.pchtxt` / IPS) for Atmosphère and Switch emulators.

This repo contains **only** patches, notes and analysis scripts. It does not
contain, and must never contain, game files or console keys. Dump your own
copy of the game to use or develop this patch.

## Layout

- `patches/<version>/` – patch files, keyed by the game's build ID
- `scripts/` – analysis helpers (Ghidra headless scripts, constant scanners)
- `notes/` – findings: addresses, what each patch changes, known issues

## Status

**v2.0 (experimental)** for game version 2.1.0: `patches/2.1.0/4x3.pchtxt`, and the
same patch as IPS: `patches/2.1.0/646761F643AFEBB379EDD5E6A5151AF2CEF93DC1.ips`
(regenerate it with `scripts/pchtxt_to_ips.py`).
It renders at the normal resolution with 4:3 proportions, so the emulator has
to stretch the 16:9 output to 4:3. The game logic still sees 16:9; only the
final 3D projection is 4:3 (the sides are cropped). Test variants are in
`patches/2.1.0/test/`. Progress is in `notes/status.md`, findings in
`notes/findings-2.1.0.md`.

## Install (emulator)

1. Create a mod folder for Metroid Dread (`010093801237C000`) with this structure:
   ```
   load/010093801237C000/4x3/exefs/4x3.pchtxt
   ```
   Or use the `.ips` file in its place. Use one or the other, not both.
   **Eden / yuzu forks on Android:** don't use the `.pchtxt` or `.ips`. Patching
   Dread's NSO in memory makes extra copies of its 1.8 GB image and Android
   kills the emulator for low memory. Build a pre-patched `main` from your own
   dump instead and install it as `4x3/exefs/main`:
   ```
   python scripts/make_patched_nso.py path/to/exefs/main patches/2.1.0/4x3.pchtxt main
   ```
   Install the `4x3` folder through the game's Add-ons menu, so the emulator
   owns the files (it may ignore files copied in over ADB).
2. Enable the `4x3` add-on for the game.
3. Set the emulator's aspect ratio to **Force 4:3** (or **Stretch to window** on
   a 4:3 screen).
