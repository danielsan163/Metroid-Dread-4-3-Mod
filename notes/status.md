# Status / next steps (handoff)

## Where things stand
- Target: 2.1.0 (build ID `646761F643AFEBB379EDD5E6A5151AF2CEF93DC1`) on a 4:3
  Android handheld (Nova) running **Eden Nightly**.
- Patch v1.1 is in `patches/2.1.0/`: `.pchtxt`, `.ips`, and a cheat version under
  `cheats/`. The analysis is in `findings-2.1.0.md`.
- **Untested in game.** On Eden Android, every exefs patch crashed, even the no-op
  one (`test/c-noop`). The unmodded game launched at that point.
- During cleanup over Windows MTP, the unmodded game **stopped launching** too.
  Not yet diagnosed. Check the update (v2.1.0) is still installed, plus the keys
  and firmware, and per-game settings.

## Next steps
1. Get the unmodded game launching again.
2. Get Eden's crash log: `adb logcat` with USB debugging on, or Eden's log file.
3. Try the cheat version (`cheats/646761F643AFEBB3.txt`, first entry only).
4. If possible, test the patch on a PC build of Eden to separate Eden Android
   problems from patch problems.

## Local setup
- Keep game files (`exefs/main`, keys, dumps) **outside** this repo. The
  `.gitignore` blocks them anyway.
- Analysis scripts need Python 3 with `lz4` and `capstone`:
  `python scripts/nso_unpack.py path/to/main main.bin`
