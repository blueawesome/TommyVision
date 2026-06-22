# TommyVision CRT Media Box — Master Project Brief

## Project Summary

TommyVision is a Raspberry Pi-based CRT media appliance designed for a 27" Sony Trinitron CRT TV. The project should feel like a custom analog-era device rather than a modern media center squeezed onto an old TV.

The first hardware target is a **Raspberry Pi 3B** connected to the CRT using composite video through the Pi’s 3.5mm TRRS AV output. The target TV is a **Sony KV-27FS12** with composite, S-Video, and component inputs. For this project, the Pi should primarily output standard NTSC composite video suitable for 4:3 CRT playback.

The first version should use a USB keyboard for control/testing and should be built so future input methods can be added cleanly.

## Core Product Idea

The box should boot into a simple 4:3 interface with three main modes:

1. **Simpsons Mode**
   - A dedicated season/episode selector.
   - Eventually controlled by two big physical rotary dials.
   - Left dial selects season.
   - Right dial selects episode.
   - Press/select plays the episode.
   - Keyboard controls should simulate this first.

2. **CRT Library Mode**
   - A curated media browser for movies, TV, specials, VHS rips, and playlists.
   - This mode will likely be remote-first later, not dial-first.
   - No metadata scraping is required.
   - Folder names and filenames are enough for v1.
   - Playback should be handled by an existing media player, not custom video-decoding code.

3. **Retro Games Mode**
   - Eventually launches an existing retro emulation frontend such as RetroPie or EmulationStation.
   - This does not need to be implemented in the first version.
   - For v1, it can be a placeholder menu item.

## Design Goals

- Designed for a 4:3 CRT, not modern widescreen.
- Big readable text.
- No tiny UI.
- No poster walls.
- No scraping.
- No modern streaming-app feel.
- Avoid thin 1px lines that may shimmer on 480i composite.
- Use generous margins because CRT overscan may cut off screen edges.
- Keep the first visual design extremely simple and reliable.

## First Hardware Target

The first version is specifically targeting a **Raspberry Pi 3B** connected to a Sony KV-27FS12 CRT through the Pi’s 3.5mm TRRS composite AV output.

Assume:

- Raspberry Pi 3B
- Raspberry Pi OS
- Composite RCA output
- NTSC 4:3 CRT display
- USB keyboard for initial control/testing
- Local media stored on USB drive, external storage, or local folders
- mpv installed locally for playback

The app should still be written in a way that can run on a normal desktop computer for development, but the first real deployment target is the Pi 3B on the CRT.

Do not assume modern HD output, widescreen UI, mouse input, touch input, or a high-resolution display.

## Initial Visual Design

For v1, keep the UI extremely simple.

The starting visual style should mimic the Sony CRT’s own menu look:

- solid blue background
- white text
- simple cursor or highlight
- no poster art
- no thumbnails
- no gradients
- no animations required
- no tiny labels
- no thin decorative lines
- no complex layout

The goal is not to make the first version visually fancy. The goal is to make it readable, stable, and usable on a composite CRT.

A basic screen can look like:

```txt
TOMMYVISION

> SIMPSONS
  CRT LIBRARY
  RETRO GAMES
```

A Simpsons screen can look like:

```txt
THE SIMPSONS

SEASON 04
EPISODE 12

SELECT: PLAY
BACK: MENU
```

CRT Library mode can look like:

```txt
CRT LIBRARY

> MOVIES
  TV
  SPECIALS
  VHS RIPS
  PLAYLISTS
```

Future versions can add more personality, such as VCR-style OSD elements, fake cable-box styling, scanline-aware layout polish, custom fonts, or mode-specific screens. Those are not required for v1.

## Important Constraint

Do not build a full media center from scratch.

The custom app should handle:

- menus
- library browsing
- file selection
- mode switching
- input mapping
- launching playback
- returning from playback

The app should not handle:

- video decoding
- audio playback internals
- subtitle rendering internals
- pause/resume engine internals

Use `mpv` as the playback engine.

## Target First Version

The first version should be built to run on the Raspberry Pi 3B connected to the CRT, but it should also be runnable on a normal computer for easier development.

Use keyboard controls first. The USB keyboard is the initial stand-in for both the future dials and future remote.

The first version should prove:

- the app launches on the Pi 3B
- the UI is readable on the CRT
- the blue/white menu style works
- main menu navigation works
- Simpsons mode can browse/select/play episodes
- CRT Library mode can browse/select/play local video files
- Retro Games mode placeholder works
- the input/action system is clean enough to support dials, remote, and controllers later
- selected media files launch in mpv fullscreen and return to the app after mpv exits

## Preferred Tech Stack

- Python 3
- pygame for the fullscreen CRT-style UI
- mpv launched through subprocess for video playback
- YAML or JSON config files for media paths and settings
- Keep the architecture modular so future input methods can be added cleanly

## Abstract Input Model

The app should not directly hard-code behavior to keyboard keys.

Instead, create an internal action system.

Example actions:

- `UP`
- `DOWN`
- `LEFT`
- `RIGHT`
- `SELECT`
- `BACK`
- `HOME`
- `PLAY_PAUSE`
- `STOP`
- `SEEK_FORWARD`
- `SEEK_BACK`
- `RANDOM`
- `LEFT_DIAL_CW`
- `LEFT_DIAL_CCW`
- `LEFT_DIAL_PRESS`
- `RIGHT_DIAL_CW`
- `RIGHT_DIAL_CCW`
- `RIGHT_DIAL_PRESS`
- `QUIT`

Keyboard input should map to these actions.

Future input sources may include:

- USB keyboard
- USB media remote
- FLIRC IR receiver
- GPIO rotary encoders
- GPIO buttons
- game controller

## Prototype Keyboard Mapping

Use these controls for development:

General navigation:

- Arrow Up: `UP`
- Arrow Down: `DOWN`
- Arrow Left: `LEFT`
- Arrow Right: `RIGHT`
- Enter: `SELECT`
- Backspace: `BACK`
- H: `HOME`
- R: `RANDOM`
- Escape: `BACK` or `QUIT` depending on context
- Q: quit app from main menu

Fake dial controls:

- A: `LEFT_DIAL_CCW`
- D: `LEFT_DIAL_CW`
- S: `LEFT_DIAL_PRESS`
- J: `RIGHT_DIAL_CCW`
- L: `RIGHT_DIAL_CW`
- K: `RIGHT_DIAL_PRESS`

Playback controls for v1 can mostly be handled by mpv while mpv is focused. Deeper playback control can come later through mpv IPC.

## Media Folder Structure

The app should support a simple folder-based media structure.

Example:

```txt
/media/crt/
  simpsons/
    Season 01/
      S01E01 - Simpsons Roasting on an Open Fire.mp4
      S01E02 - Bart the Genius.mp4
    Season 02/
      S02E01 - Bart Gets an F.mp4

  library/
    Movies/
      Movie Title.mp4
    TV/
      Show Name/
        Episode File.mp4
    Specials/
      Holiday Special.mp4
    VHS Rips/
      Tape 001 - Saturday Morning Mix.mp4
      Tape 002 - MTV Commercials Random Mix.mp4
    Playlists/
      Halloween Block.m3u
      Saturday Morning.m3u
```

For v1, the app can read folders and files directly. It does not need a database.

## Supported Media Files

For v1, support common local video files:

- `.mp4`
- `.mkv`
- `.avi`
- `.mov`
- `.m4v`
- `.mpg`
- `.mpeg`

For playlists, support may come later:

- `.m3u`
- `.m3u8`

## Config File

Create a config file at:

```txt
config/library.yaml
```

Example:

```yaml
app:
  title: "TOMMYVISION"
  fullscreen: false
  width: 640
  height: 480

paths:
  simpsons: "./sample_media/simpsons"
  library: "./sample_media/library"

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

Use relative sample paths for development. Later, the Pi can use absolute paths like `/media/crt`.

## Main Menu

The app should boot to:

```txt
TOMMYVISION

> SIMPSONS
  CRT LIBRARY
  RETRO GAMES
```

The selected item should be obvious. Use large text and a simple cursor/arrow. Do not use small icons.

## Simpsons Mode

The Simpsons screen should show:

```txt
THE SIMPSONS

SEASON 04
EPISODE 12

SELECT: PLAY
BACK: MENU
```

Behavior:

- Left fake dial changes season.
- Right fake dial changes episode.
- Right dial press or Enter plays selected episode.
- Left dial press or Backspace returns to main menu.
- R chooses a random episode.
- Arrow keys should also work as a fallback.
- The app should scan available season folders and episode files.
- Do not assume every season has the same number of episodes.
- If a selected episode does not exist, clamp to a valid episode.

Filename parsing:

- Prefer files matching `S01E01`, `s01e01`, `S1E1`, or similar.
- Fall back to sorted filename order if parsing fails.

## CRT Library Mode

The CRT Library screen should show top-level categories from the library folder:

```txt
CRT LIBRARY

> Movies
  TV
  Specials
  VHS Rips
  Playlists
```

Behavior:

- Up/Down moves selection.
- Enter/Select enters folder or plays file.
- Backspace returns to previous folder.
- H returns to main menu.
- R can choose a random playable file from the current section.
- Display folder/file names in a readable list.
- Use pagination if there are too many items to fit on screen.
- Do not show file extensions unless necessary.
- VHS Rips should simply be a folder/category like anything else.

## Playback Behavior

When a video is selected:

- launch mpv using subprocess
- run mpv fullscreen if configured
- wait for mpv to exit
- return to the previous menu after playback ends or is closed

For v1, it is acceptable for mpv to handle playback controls directly while focused.

Use something like:

```txt
mpv --fs --really-quiet "/path/to/file.mp4"
```

The exact command should be configurable.

If mpv is missing or playback fails, show a simple readable error screen instead of crashing.

Do not implement mpv IPC yet. Pause, seek, resume, and advanced playback controls can come later.

## Retro Games Mode

For v1, Retro Games mode can show a placeholder screen:

```txt
RETRO GAMES

This mode will eventually launch RetroPie or EmulationStation.

BACK: MENU
```

Do not implement emulation or RetroPie launching in v1.

Later, the app may launch:

- EmulationStation
- RetroPie
- another shell command configured in YAML

## Suggested Repo Structure

```txt
tommyvision/
  README.md
  MASTER.md
  requirements.txt

  app/
    __init__.py
    main.py
    actions.py
    config.py
    input_keyboard.py
    media_library.py
    player.py
    ui.py

    modes/
      __init__.py
      main_menu.py
      simpsons.py
      crt_library.py
      retro_games.py
      error_screen.py

  config/
    library.yaml

  sample_media/
    README.md
    simpsons/
      Season 01/
    library/
      Movies/
      TV/
      Specials/
      VHS Rips/
      Playlists/

  docs/
    setup_pi_3b.md
    controls.md
    future_hardware.md
```

## Development Priorities

### Milestone 1: Pi 3B-Ready UI Shell

- pygame window at 640x480
- solid blue background
- white text
- main menu
- keyboard input mapping
- action system
- mode switching
- placeholder Retro Games mode

### Milestone 2: Media Scanning

- read `config/library.yaml`
- scan Simpsons folders
- scan CRT Library folders
- display categories and files
- handle missing/empty folders gracefully

### Milestone 3: mpv Playback

- launch selected files with mpv
- return to menu after playback exits
- handle missing mpv gracefully with a readable error message

### Milestone 4: Simpsons Mode Polish

- season/episode selection
- fake dial controls
- random episode
- clamp valid episodes
- readable CRT-style layout

### Milestone 5: CRT Library Polish

- browse folders
- play files
- random from current category
- pagination
- clean display names

### Milestone 6: Raspberry Pi Prep

- document Raspberry Pi OS setup
- document composite output assumptions
- create optional fullscreen config
- create systemd service later for boot-to-app

### Future Milestones

- USB remote support
- FLIRC mapping guide
- GPIO rotary encoder support
- GPIO Home/Menu button
- RetroPie/EmulationStation launch mode
- mpv IPC controls
- watch-later/resume support
- playlist support
- fake cable channel/random TV mode
- CRT visual theme polish
- enclosure/hardware docs

## Revised First Codex Task: Raspberry Pi 3B v1 With mpv Playback

Build the first working version of TommyVision for a Raspberry Pi 3B connected to a 4:3 CRT over composite video.

The app should use Python + pygame for a simple 640x480 menu interface and launch local media files with mpv.

### First Task Requirements

Implement:

- pygame app window at 640x480
- solid blue background
- white readable text
- config loading from `config/library.yaml`
- main menu with:
  - Simpsons
  - CRT Library
  - Retro Games
- Simpsons mode that scans configured season folders
- CRT Library mode that browses configured folders
- Retro Games placeholder screen
- action-based keyboard input layer
- fake dial keyboard mappings for future rotary encoder behavior
- video playback through mpv subprocess
- return to menu after mpv exits
- graceful handling of missing media folders
- graceful handling of missing mpv
- basic README with Raspberry Pi 3B setup assumptions

Do not implement yet:

- GPIO rotary encoders
- IR remote
- FLIRC setup
- RetroPie launching
- metadata scraping
- custom themes beyond blue background / white text
- mpv IPC
- resume tracking
- playlist support

### Acceptance Criteria

- `python -m app.main` starts the app.
- App opens at 640x480.
- Background is solid blue.
- Text is white and readable.
- Main menu shows Simpsons, CRT Library, and Retro Games.
- Arrow keys navigate the main menu.
- Enter selects a mode.
- Backspace returns to the previous menu.
- Escape quits from the main menu.
- Simpsons mode scans configured season folders.
- Simpsons mode can select season and episode.
- CRT Library mode browses configured folders.
- Selecting a supported video file launches mpv.
- After mpv exits, the app returns to the previous menu.
- Missing media folders do not crash the app.
- Missing mpv does not crash the app.
- Retro Games mode displays a placeholder screen.
- Fake dial keyboard mappings exist:
  - A = left dial counterclockwise
  - D = left dial clockwise
  - S = left dial press
  - J = right dial counterclockwise
  - L = right dial clockwise
  - K = right dial press
- Code structure leaves room for remote input, GPIO encoders, mpv IPC, and RetroPie launch mode later.

## Coding Style

- Keep code simple and readable.
- Prefer explicit state machines/mode classes over clever abstractions.
- Do not over-engineer the first version.
- Make it easy to run locally.
- Make it easy to replace input sources later.
- Keep media paths configurable.
- Avoid hard-coded absolute paths.
- Handle missing folders gracefully.
- Handle empty folders gracefully.
- Handle no media found gracefully.

## Out of Scope for v1

Do not build these yet:

- metadata scraping
- poster art
- Kodi integration
- RetroPie integration
- GPIO encoders
- IR remote
- database-backed library
- web UI
- network streaming
- Blu-ray support
- transcoding
- advanced emulation configuration
- custom video decoder
