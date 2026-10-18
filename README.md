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

Targeting version 2.1.0 on a 4:3 handheld via emulator. See `notes/target.md`.
Waiting on analysis of the game executable.
