# Controls

## Menus

- Arrow Up/Down: move selection
- Enter: select
- Backspace: go back
- Escape: back, or quit from the main menu
- H: home menu
- R: random episode or random playable file
- Q: quit from the main menu

## Simpsons Fake Dials

- A/D: left dial counter-clockwise/clockwise
- S: left dial press
- J/L: right dial counter-clockwise/clockwise
- K: right dial press

## Playback Testing

Normal video playback runs through `mpv`.

- X: TommyVision-owned STOP action. TommyVision gives `mpv` a temporary `x` binding, tracks playback position through IPC, saves resume state, and returns to TommyVision.
- Space: play/pause. TommyVision gives `mpv` a temporary binding for local testing.
- Left/Right: seek backward/forward. TommyVision gives `mpv` temporary bindings for local testing.
- Q: mpv's own local quit fallback. This can still quit playback, but it does not use the TommyVision save-and-exit path.

The STOP action is intended to become the future remote Stop button.
