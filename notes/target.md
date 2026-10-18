# Target

- **Game version:** 2.1.0 (build ID: TBD, read from the dumped `main` NSO header)
- **Device:** Nova handheld with a 4:3 screen, running a Switch emulator
- **Output:** a 4:3 image that fills the screen with the emulator's
  "stretch to window" aspect setting

## Plan

1. Find the 16:9 aspect constant (`0x3FE38E39`) and the render-target sizes
   (1280x720 handheld, 1920x1080 docked) in `main`.
2. First patch: change the camera projection aspect to 4:3 (`0x3FAAAAAB`) and
   keep the 16:9 framebuffer. The emulator's stretch to 4:3 then makes the
   geometry correct and keeps full horizontal resolution.
3. Fallback: if stretching distorts post-processing or the UI, resize the
   render targets to 4:3 (960x720 / 1440x1080).
4. Fix the HUD, minimap, menus and cutscenes separately as testing shows
   problems.
