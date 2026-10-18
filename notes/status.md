# Status / next steps (handoff)

## Where things stand (2026-10-18)
- Target: 2.1.0 (build ID `646761F643AFEBB379EDD5E6A5151AF2CEF93DC1`) on a
  Retroid Pocket Nova (4:3, 1280x960, 8 GB, Android 13) running **Eden Nightly**
  (`dev.eden.eden_emulator.nightly`). A stable Eden v0.2.1
  (`dev.eden.eden_emulator`) is installed too.
- **The mod loads and runs in game on Eden Nightly**, delivered as a pre-patched
  `exefs/main` (see below). Tested: v1.2 and v1.3 (now
  `test/v1.3-vertplus`). Both cut off the floor under Samus and the top of the
  minimap.
- **v2.0** (`patches/2.1.0/4x3.pchtxt`) is built and checked by disassembly
  but **untested in game**. It keeps all game logic at 16:9 and makes only the
  final perspective matrix 4:3 (Hor-). Expected: same vertical framing and
  minimap as vanilla, sides cropped, correct proportions after Eden's 4:3
  stretch. `test/v2-vertplus` is the render-only Vert+ alternative.

## What was wrong on Eden Android (solved)
1. **Unmodded game not launching:** Nightly's add-on list had the 2.1.0
   update disabled (`DisabledAddOns ... Update@327680` in `config.ini`).
   Nightly still applied the update's RomFS but not its ExeFS, so it ran the
   1.0.0 `main` (build `49161D9C...`) against 2.1.0 data and got killed.
   Check the update is ON in the game's Add-ons screen.
2. **"Any exefs patch crashes, even a no-op":** Android's low-memory killer.
   Dread's `main` has a **1.8 GB bss** (0x70CD2FA0). Eden's NSO loader keeps the
   image including bss in a buffer, and `PatchNSO` (used for `.ips`/`.pchtxt`)
   makes more full-size copies, so the process passes ~5.1 GB and gets killed
   right after logcat shows `Patching NSO for name=main`. Even unmodded loading
   peaks near 5 GB, so close other emulators (the stable Eden left in the
   background counts).
   **Fix:** `scripts/make_patched_nso.py` builds a patched `main` that Eden
   loads through LayeredExeFS (`load/<tid>/4x3/exefs/main`) with no PatchNSO.
3. **Mod files pushed over ADB were ignored, then disappeared:** files created
   by `adb push` are owned by `shell`. Install the mod folder through Eden's
   Add-ons → Install instead (stage it in `/sdcard/Download/` first). After
   that, updating the file in place with `cat new > existing` over ADB keeps
   Eden's ownership.
4. **Cheat delivery (runtime code writes):** crashed both times on Eden's NCE
   backend (wild jump to `PC=17FFFA3CD65F03C0` within a second). Dropped.

## Next steps
1. Test v2.0 in the statue room (save is right after the intro): floor under
   Samus visible? Minimap fully on screen? Circles round?
2. If 3D looks right, compare against `test/v2-vertplus` and pick one.
3. HUD/UI is 16:9 squeezed into 4:3 (narrow). Next target: the UI scale
   (`0x15BF40` builds scale(1, aspect, 1); title screen didn't change with the
   global aspect, so UI may use its own path).
4. Cutscenes: check they go through the same projection path.

## Device workflow (ADB)
- adb: `C:\Users\Scott\AppData\Local\Android\Sdk\platform-tools\adb.exe`. In Git
  Bash set `MSYS_NO_PATHCONV=1` and pass Windows paths (`cygpath -w`) to
  `adb push`.
- Eden data: `/sdcard/Android/data/dev.eden.eden_emulator.nightly/files/`
  (`keys/`, `nand/`, `load/`, `config/`, `log/`). Game + update NSPs are in
  `/storage/EB9D-E224/ROMS/Switch/` and the update loads as external content.
- Screenshots: `adb exec-out screencap -p > shot.png`. Crash diagnosis:
  `adb logcat -v threadtime` (look for `lowmemorykiller` and `Backtrace`).
  Eden's own `log/eden_log.txt` is buffered and gets cut off at a crash.

## Local setup
- Keep game files (`exefs/main`, keys, dumps, built `main`) **outside** this
  repo. The `.gitignore` blocks them anyway.
- Analysis scripts need Python 3 with `lz4` and `capstone`. `disasm.py` was
  renamed from `dis.py`, which shadowed Python's `dis` module.
