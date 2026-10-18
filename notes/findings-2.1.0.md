# Findings: 2.1.0

Build ID `646761F643AFEBB379EDD5E6A5151AF2CEF93DC1`, program ID `010093801237C000`.
Addresses are offsets in the decompressed image (`scripts/nso_unpack.py`);
`.text` is `0x0000000-0x123AC10`.

## Display globals

| What | Variable | Getter (stub → body) |
|------|----------|----------------------|
| Render width, init 1600 | `0x1A1BE18` | `0x132F80 → 0x132970` |
| Render height, init 900 | `0x1A1BE1C` | `0x132F90 → 0x132980` |
| Aspect = width / height | `0xB371028` (bss) | `0x132FA0 → 0x132990` |
| 1 / aspect | `0xB37102C` (bss) | `0x132FB0 → 0x1329A0` |

The aspect and inverse are computed once by the static initializer at
`0x132B80` (`fdiv` at `0x132BDC`). **v1 patch:** store 4/3 there instead.

## Camera FOV

- Cameras store a horizontal FOV (`m_fFovX`, camera `+0x80`), and many also store
  an aspect (`+0x94`).
- `0x217EE0` converts FovX to FovY: `2*atan(tan(fovx/2) / aspect)`. It has 15
  callers. Most pass the global aspect or the camera's `+0x94`, but
  `0xE94F20` passes a hard-coded 16/9. **v1 patch:** use 4/3 there too.
- With FovX unchanged, 4:3 gives **Vert+**: the same horizontal view and more
  vertical view.

## Other 16:9 constants (left alone)

- `0x1C985C`, `0x1D2BD0`: pick the display mode closest to 16:9 (≤1280x720).
- `0x00AF4`: the display config struct's aspect field. Its only use is a viewport
  fit (`0x1C9718`) that goes to `0x132F70`, which is an empty `ret` on Switch.
- `0x1A1E758`: written and read only by `0x1C9718`.

## Open questions for testing

- Does Vert+ show areas above/below rooms that should stay hidden? If it does,
  v2 can scale FovX by (4/3)/(16/9) to get Hor- instead.
- UI: `0x15BF40` builds a (1, aspect, 1) scale matrix. We need to see whether the
  HUD/menus look right after the emulator stretches the image.
- `0x1BB3B0` computes an aspect from a render target's width and height
  instead of the global, so whichever camera uses it may still be 16:9.

## v1 crash (Eden Android: game exits to the menu while loading)

Likely cause: the viewport fit at `0x1FFD58` calculates `height = width / aspect`
(1600 / (4/3) = 1200, larger than the 900-pixel render target) and
`y = (900 - 1200) >> 1`, which underflows as an unsigned value.
**v1.1** makes it use the full render height instead (`0x1FFDD0`-`0x1FFDD8`).
For narrowing it down, `patches/2.1.0/test/` holds two v1 halves: global aspect
only, and camera only.

## Eden Android: any exefs patch crashes (solved)

Not the patch: Android's low-memory killer. `main` has a 1.8 GB bss, and Eden's
`PatchNSO` copies the whole image to apply an IPS/pchtxt, pushing the process
past ~5.1 GB. A pre-patched `exefs/main` (`scripts/make_patched_nso.py`) avoids
it. The cheat route crashed under NCE and was dropped. Details in `status.md`.

## Projection path (in-game results)

- `0x1BB1CC` (reached from `0x2195FC`/`0x219724` -> `0x150D30` -> `0x1D1F54`)
  sets a camera up for a viewport {x, y, w, h}. Perspective branch: aspect =
  w/h (`0x1BB3C0`), FovY = `0x217EE0`(FovX, aspect), then
  `0x79A04`(FovY, aspect, 1, 1e7) builds the matrix
  (m00 = cot(FovY/2)/aspect, m11 = cot(FovY/2)); `0x15BF00` remaps depth.
- `0x1BAF78` is the matching unproject (screen to world) using camera `+0x94`.
- `0xE94EB8`-`0xE94FCC` computes the visible world area (FovX, plus FovY from a
  hard-coded 16/9) for camera bounds. Reverting the v1.1 change here (v1.3)
  made no visible difference.
- `0x1FFD58` viewport fit: both its compare operands are the global aspect, so
  it always takes the second branch; v1.1's change there yields the full
  1600x900 viewport.
- v1.2/v1.3 (global aspect 4/3 + the `0x1BB3C0` change): runs, shapes look
  about right, but the floor under Samus and the top of the minimap are
  cropped compared with vanilla. v2.0 keeps all of that at 16:9 and only
  changes the aspect passed to `0x79A04` (`0x1BB408`, literal at `0x1BD654`).
