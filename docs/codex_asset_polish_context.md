# TommyVision Codex Context — Optional Logo, Boot Video, and Menu Music

## Current Status

TommyVision already has a working v1 prototype.

The app currently supports:

* Python + pygame UI
* 640x480 blue/white CRT-style menu
* Main menu with Simpsons, CRT Library, and Retro Games
* Simpsons season/episode scanning
* CRT Library folder browsing
* `mpv` playback through subprocess
* Return to TommyVision after `mpv` exits
* Graceful missing media / missing player handling
* Local testing on macOS with real sample media

Do **not** rewrite the app.
Do **not** redesign the UI.
Do **not** change core navigation behavior unless required for these features.
Do **not** add unrelated features.

This task is a small v1 personality/assets pass.

## Goal

Add optional support for:

1. Logo image on menu screens
2. Boot-up video before the main menu
3. Menu background music shuffled from a folder

These should be configurable, optional, and safe. If assets are missing, the app should continue working exactly like it does now.

## Design Direction

Keep the current simple Sony CRT-style UI:

* Blue background
* White readable text
* 640x480 target
* 4:3 CRT-safe layout
* No poster art
* No metadata
* No modern streaming app look
* No complex animations
* No tiny text
* No heavy on-screen instruction clutter

Do not make big visual or behavior decisions. Keep changes conservative and reversible.

## Asset Folder Structure

Add an `assets/` folder if missing.

Suggested structure:

```txt
assets/
  README.md
  logo/
    tommyvision-logo.png
  boot/
    boot.mp4
  menu_music/
    README.md
```

Use placeholder folders and documentation. Do not add large binary assets unless they already exist locally.

Media/audio/image files should be ignored by git unless specifically intended as tiny placeholders.

## Config Additions

Update `config/library.yaml` with optional config sections.

Example:

```yaml
startup:
  play_boot_video: false
  boot_video: "./assets/boot/boot.mp4"

audio:
  menu_music_enabled: false
  menu_music_folder: "./assets/menu_music"
  menu_music_volume: 0.35
  shuffle: true

ui:
  logo_path: "./assets/logo/tommyvision-logo.png"
  show_text_title_if_logo_missing: true
```

Keep existing config values intact.

If the current config loader expects certain structures, integrate these new keys safely with defaults.

## Feature 1: Optional Logo Image

Add optional logo support.

Behavior:

* If `ui.logo_path` is set and the file exists, render the image near the top of the main menu.
* Keep the menu layout largely the same.
* Do not redesign the menu.
* Scale the logo safely so it fits within CRT-safe margins.
* Avoid huge images overflowing the 640x480 screen.
* If the logo is missing, invalid, or unset, fall back to the existing text title behavior.
* Do not crash if the image cannot be loaded.

Supported image formats can be whatever pygame supports normally, such as PNG.

The logo should not be required on every screen unless the current UI structure makes that easy. Start with the main menu only unless it is trivial and clean to reuse.

## Feature 2: Optional Boot Video

Add optional boot video playback before the main menu appears.

Behavior:

* On app startup, before entering the main menu, check:

  * `startup.play_boot_video`
  * `startup.boot_video`
* If enabled and the file exists, launch it with `mpv`.
* Wait for the boot video to end or be quit by the user.
* Then continue into the normal TommyVision main menu.
* If the file is missing, `mpv` is missing, or playback fails, skip the boot video and continue to the main menu.
* Do not show a scary error screen for a missing optional boot video.
* Do not block the app from launching if boot video fails.

Use existing player/mpv patterns where reasonable, but avoid forcing the normal media playback error flow if that would make startup annoying.

Recommended `mpv` behavior:

* Fullscreen if configured or appropriate
* Quiet mode
* Exit automatically when the boot video ends
* User can quit/skip with `Q`

Do not implement pygame-native video playback.

## Feature 3: Optional Menu Background Music

Add optional menu music support using pygame audio/mixer unless the current architecture suggests a cleaner approach.

Behavior:

* If `audio.menu_music_enabled` is true and `audio.menu_music_folder` exists:

  * Find supported audio files in that folder.
  * Shuffle them if `audio.shuffle` is true.
  * Play one while the app is in menus.
  * Continue playing/shuffling while navigating menus.
* When launching `mpv` playback for a video:

  * Stop or pause menu music before playback starts.
* After `mpv` exits and TommyVision returns to menus:

  * Resume menu music or start another shuffled track.
* If the folder is missing or empty, silently do nothing.
* If audio playback fails, do not crash the app.

Supported audio formats can be limited to practical pygame-friendly files:

```txt
.mp3
.ogg
.wav
```

Keep volume configurable using:

```yaml
audio:
  menu_music_volume: 0.35
```

Default should be conservative, not loud.

Do not add UI controls for music yet.
Do not add volume menus.
Do not add mute menus.
Do not add visualizers.
Do not add playlist UI.

## Important Behavior Constraints

Do not change the core navigation model.

Do not add lots of on-screen instructions.

Do not add new menu items unless necessary.

Do not change Simpsons browsing behavior.

Do not change CRT Library browsing behavior.

Do not change mpv as the video playback engine.

Do not implement:

* GPIO
* FLIRC setup
* IR remote support
* RetroPie launching
* mpv IPC
* resume tracking
* metadata scraping
* poster art
* databases
* themes beyond the current blue/white CRT menu
* complex animation systems
* settings UI

## Graceful Failure Rules

All three new features are optional.

The app must still run normally when:

* `assets/` folder is missing
* logo file is missing
* logo file is invalid
* boot video is missing
* boot video fails to play
* menu music folder is missing
* menu music folder is empty
* menu music file fails to load
* pygame mixer cannot initialize
* `mpv` is missing

The base menu app should remain usable.

## README / Docs Updates

Update documentation lightly.

Add notes for:

* where to put logo files
* where to put boot video
* where to put menu music
* how to enable/disable these in `config/library.yaml`
* note that boot video and menu music are optional
* note that menu music stops during video playback
* note that `Q` quits `mpv` playback and returns to TommyVision

Do not over-document.

## Acceptance Criteria

After implementation:

* `python -m app.main` still starts the app.
* App still opens at 640x480.
* Existing main menu still works.
* Simpsons mode still works.
* CRT Library mode still works.
* Selecting a video still launches `mpv`.
* After `mpv` exits, the app returns to TommyVision.
* If no assets are present, app behaves basically like before.
* If logo exists and is configured, it appears on the main menu.
* If boot video exists and is enabled, it plays before the main menu.
* If menu music folder has playable audio and is enabled, music plays in menus.
* Menu music stops/pauses when a video launches.
* Menu music resumes or restarts after video playback exits.
* Missing optional assets do not crash the app.

## Testing Suggestions

Run:

```bash
source .venv/bin/activate
python -m app.main
```

Test cases:

1. Default config with no assets
2. Logo path configured but logo missing
3. Logo path configured with a real PNG
4. Boot video disabled
5. Boot video enabled but file missing
6. Boot video enabled with a real short video
7. Menu music disabled
8. Menu music enabled but folder empty
9. Menu music enabled with one audio file
10. Menu music enabled with multiple audio files
11. Launch a movie while menu music is playing
12. Quit movie with `Q` and confirm app returns to menu

Keep the implementation small and boring. The goal is asset hooks, not a full theme system.
