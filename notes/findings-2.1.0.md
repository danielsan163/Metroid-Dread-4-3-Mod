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
