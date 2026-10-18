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

**v1 (experimental)** for game version 2.1.0: `patches/2.1.0/4x3.pchtxt`.
It renders at the normal resolution with 4:3 proportions, so the emulator has
to stretch the 16:9 output to 4:3. Findings are in `notes/findings-2.1.0.md`.

## Install (emulator)

1. Create a mod folder for Metroid Dread (`010093801237C000`) with this structure:
   ```
   load/010093801237C000/4x3/exefs/4x3.pchtxt
   ```
   On Android emulators you can also install the `4x3` folder through the game's
   Add-ons / Mods menu.
2. Enable the `4x3` add-on for the game.
3. Set the emulator's aspect ratio to **Force 4:3** (or **Stretch to window** on
   a 4:3 screen).
