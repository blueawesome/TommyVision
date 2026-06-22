# Raspberry Pi 3B Setup

This guide is for the first TommyVision hardware target: a Raspberry Pi 3B running Raspberry Pi OS, connected to a 4:3 CRT over composite video through the Pi 3.5mm TRRS AV output.

TommyVision v1 uses a USB keyboard for control, pygame for the 640x480 menu UI, and `mpv` for fullscreen video playback. It does not install a boot service yet.

## Hardware Assumptions

- Raspberry Pi 3B
- Raspberry Pi OS
- Sony KV-27FS12 or similar NTSC 4:3 CRT
- Composite RCA video from the Pi 3.5mm TRRS AV jack
- USB keyboard for v1 testing/control
- Local media on USB storage, external storage, or local folders
- Media mounted at `/media/crt`

The app is designed for 640x480, large white text, a solid blue background, and generous CRT overscan margins. Avoid assuming widescreen HDMI behavior when testing the real target.

## System Packages

Update the Pi and install Python, pygame dependencies, PyYAML, and `mpv`:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-pygame python3-yaml mpv
```

`python3-pygame` and `python3-yaml` are preferred on the Pi because they use Raspberry Pi OS packages. If you use a virtual environment instead, install the Python packages from the repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you use the system packages directly, run the app with `python3 -m app.main`. If you use the virtual environment, activate it first and then run `python -m app.main`.

## Clone And Install

From the Pi:

```bash
git clone <repo-url> TommyVision
cd TommyVision
```

For virtualenv-based setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For system-package setup, the `apt install` command above is enough for pygame and PyYAML.

## Media Folder Structure

TommyVision v1 reads folders and video files directly. No database, metadata scraping, thumbnails, or playlists are used yet.

Expected Pi media layout:

```txt
/media/crt/
  library/
    Movies/
      Movie Title.mp4
    TV/
      The Simpsons/
        Season 01/
          S01E01 Simpsons Roasting on an Open Fire.mkv
          S01E02 Bart the Genius.mkv
        Season 02/
          S02E01 Bart Gets an F.mkv
      Show Name/
        Episode File.mp4
    Specials/
      Holiday Special.mp4
    VHS Rips/
      Tape 001 - Saturday Morning Mix.mp4
    Playlists/
```

Supported v1 video file extensions:

- `.mp4`
- `.mkv`
- `.avi`
- `.mov`
- `.m4v`
- `.mpg`
- `.mpeg`

The Simpsons scanner prefers filenames like `S01E01`, `s01e01`, or `S1E1`. If it cannot parse an episode number, it falls back to sorted filename order.

## Configure Media Paths

Edit `config/library.yaml` on the Pi:

```yaml
app:
  title: "TOMMYVISION"
  fullscreen: true
  width: 640
  height: 480

paths:
  library: "/media/crt/library"

simpsons:
  enabled: true
  path: "/media/crt/library/TV/The Simpsons"

player:
  command: "mpv"
  fullscreen: true
  extra_args:
    - "--fs"
    - "--really-quiet"

ui:
  background_color: "blue"
  text_color: "white"
  safe_margin_x: 48
  safe_margin_y: 36
  font_size_large: 48
  font_size_medium: 32
  font_size_small: 24
```

For desktop development, keep the relative sample paths. For Pi deployment, use absolute `/media/crt` paths so the app does not depend on the launch directory.

Legacy configs with `paths.simpsons` still work as a fallback when `simpsons.path` is not configured. New installs should prefer `simpsons.path` inside the main library tree so Simpsons episodes also appear naturally in CRT Library browsing.

## Run The App

From the repo root:

```bash
python3 -m app.main
```

Or, if using the virtual environment:

```bash
source .venv/bin/activate
python -m app.main
```

The app should open at 640x480. Use the keyboard controls from `docs/controls.md` or `MASTER.md`. Selecting a video launches `mpv`; when `mpv` exits, TommyVision returns to the previous menu.

If `mpv` is missing or a media folder is empty/missing, TommyVision should show a readable error or empty state instead of crashing.

## Optional Assets

Optional logo, boot video, and menu music assets can be copied into:

```txt
assets/logo/tommyvision-logo.png
assets/boot/boot.mp4
assets/menu_music/
```

Enable them in `config/library.yaml` with `ui.logo_path`, `startup.play_boot_video`, and `audio.menu_music_enabled`. These assets are optional; missing or invalid files should not prevent the app from launching. Menu music stops during `mpv` video playback and starts again after playback exits. Press `Q` while `mpv` is focused to quit playback and return to TommyVision.

## Composite CRT Notes

The project assumes NTSC 4:3 composite output for the real CRT. Configure Raspberry Pi OS for composite output using the current Raspberry Pi documentation for your OS release and Pi firmware version.

Practical checks:

- Confirm the Pi displays the desktop or console on the CRT before testing TommyVision.
- Keep the app at 640x480.
- Keep `fullscreen: true` for CRT deployment.
- Expect overscan. The UI already uses safe margins, but the TV may still crop edges.
- Use `mpv` fullscreen so playback fills the CRT output.

Exact composite configuration differs between Raspberry Pi OS releases, especially between legacy `config.txt` setups and newer display-stack behavior. Treat OS-level video output as a Pi setup step outside the app.

## Future Boot-To-App Service

Do not implement systemd yet for v1. Later, TommyVision can add a service that starts after the graphical session or display target is ready.

Future service notes:

- Run from the TommyVision repo directory.
- Use the same Python environment chosen above.
- Ensure `/media/crt` is mounted before app startup.
- Set any required display environment variables for pygame.
- Restart on failure only after the manual launch path is stable.
- Keep logs accessible with `journalctl`.

For now, launch manually with `python3 -m app.main` while validating CRT output, media paths, keyboard controls, and `mpv` playback.
