# TommyVision

TommyVision is a simple Python/pygame CRT media box UI for a Raspberry Pi 3B connected to a 4:3 Sony CRT. Version 1 is intentionally plain: a 640x480 blue-and-white menu shell, folder-based media browsing, and video playback delegated to `mpv`.

`MASTER.md` is the source of truth for the project goals and controls.

## Local Setup

Requirements:

- Python 3
- `mpv` installed and available on `PATH`
- Python packages from `requirements.txt`

Install and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

The app opens at 640x480 using the paths in [config/library.yaml](/Users/tommyday/TommyVision/config/library.yaml). The default config points to `sample_media`, which is safe for development but mostly empty.

## Media Layout

Configure local folders in `config/library.yaml`:

```yaml
paths:
  library: "./sample_media/library"

simpsons:
  enabled: true
  path: "./sample_media/library/TV/The Simpsons"
```

Preferred Simpsons episodes live inside the main CRT Library tree:

```txt
library/
  TV/
    The Simpsons/
      Season 01/
        S01E01 Simpsons Roasting on an Open Fire.mkv
```

Legacy configs with `paths.simpsons` are still supported as a fallback when `simpsons.path` is not configured, but new setups should keep Simpsons inside the library folder.

The CRT Library mode browses folders and supported video files directly. Supported video extensions are `.mp4`, `.mkv`, `.avi`, `.mov`, `.m4v`, `.mpg`, and `.mpeg`.

## Controls

- Arrow Up/Down: move through menus
- Arrow Left/Right: season changes in Simpsons mode
- Enter: select or play
- Backspace: go back
- Escape: back, or quit from the main menu
- H: home menu
- R: random episode or random playable file
- Q: quit from the main menu

Fake dial controls:

- A/D: left dial counter-clockwise/clockwise
- S: left dial press
- J/L: right dial counter-clockwise/clockwise
- K: right dial press

During video playback, `X` is the TommyVision-owned stop action for local testing. TommyVision gives `mpv` a temporary `x` binding, tracks playback position through IPC, saves resume state, quits playback, and returns to the menu. `Q` can still quit `mpv` directly as a local fallback, but that path does not use TommyVision's save-and-exit flow.

## Raspberry Pi 3B Assumptions

The first hardware target is a Raspberry Pi 3B running Raspberry Pi OS, outputting NTSC 4:3 composite video through the Pi 3.5mm TRRS AV jack to a Sony KV-27FS12 or similar CRT.

For the Pi:

- Keep `app.fullscreen` enabled in `config/library.yaml` when deployed to the CRT.
- Install `mpv` with the OS package manager.
- Store media on local storage or a mounted USB drive and point `paths.library` plus `simpsons.path` at those folders.
- Use a USB keyboard for v1 control/testing.

TommyVision does not decode video itself; it launches `mpv` and returns to the menu when `mpv` exits. Missing media folders or a missing `mpv` command show readable error/empty states instead of crashing.

## Optional Assets

TommyVision can use optional local personality assets without requiring them:

- Logo image: `assets/logo/tommyvision-logo.png`
- Boot video: `assets/boot/boot.mp4`
- Menu music: audio files in `assets/menu_music`

Enable or change these paths in `config/library.yaml` with `ui.logo_path`, `startup.play_boot_video`, and `audio.menu_music_enabled`. If an asset is missing or invalid, the app falls back silently. Menu music stops during `mpv` video playback and starts again afterward. Press `Q` while `mpv` is focused to quit playback and return to TommyVision.

## Resume State

TommyVision saves resume positions through `mpv` IPC when playback is stopped with the TommyVision STOP action. Runtime state is stored locally in `data/playback_state.json`, which is ignored by Git. If a selected file has saved progress, TommyVision shows a small Resume / Start Over / Cancel prompt before launching playback.
