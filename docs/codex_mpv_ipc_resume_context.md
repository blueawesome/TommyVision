# TommyVision Codex Context — mpv IPC Playback Session + Resume State

## Current Status

TommyVision already has a working local v1 prototype.

Current working features include:

- Python + pygame 640x480 CRT-style UI
- Blue/white menu system
- Main menu with Simpsons, CRT Library, and Retro Games
- Simpsons season/episode browsing
- CRT Library folder/file browsing
- `mpv` subprocess playback
- Return to TommyVision after `mpv` exits
- Optional logo support
- Optional boot video support
- Optional menu music support
- Graceful missing media / missing player / missing optional asset handling

Do **not** rewrite the app.

Do **not** redesign the UI.

Do **not** add major new menus yet.

Do **not** implement poster art, scraping, databases, cover art, FLIRC, GPIO, RetroPie launching, or a full settings UI.

This pass is about turning video playback into a more TommyVision-owned playback session so resume tracking can be implemented cleanly.

## Goal

Implement a first pass of **mpv IPC-backed playback session management** and **TommyVision-owned resume state saving**.

The main desired behavior:

```txt
TommyVision launches a video
→ TommyVision starts mpv with an IPC socket
→ TommyVision can ask mpv for current time and duration
→ When a STOP playback action is triggered:
    - query mpv for current timestamp
    - query mpv for duration
    - save resume state to local JSON
    - tell mpv to quit
    - return to TommyVision menu
```

This is not meant to be a full media center. Keep it simple and appliance-like.

## Important Design Intent

Do **not** rely on constant disk writes.

Do **not** write playback state every few seconds.

Save state primarily when TommyVision intentionally stops playback.

It is acceptable to keep the latest known timestamp in memory as a fallback, but do not continuously write JSON to disk while video is playing.

The clean design is:

```txt
STOP action
→ read mpv time-pos
→ read mpv duration
→ save state once
→ quit mpv
→ return to menu
```

## New Files / Suggested Structure

Add new modules only if they fit the current architecture.

Suggested files:

```txt
app/playback_session.py
app/resume_state.py
data/.gitkeep
data/playback_state.json
```

Do not commit a real populated `data/playback_state.json` if it contains local machine paths or personal media history.

Better:

```txt
data/.gitkeep
```

and make sure runtime-generated JSON is gitignored.

Update `.gitignore` to ignore:

```txt
data/playback_state.json
```

If the app already has a better location/pattern for runtime state, use that instead.

## Resume State File

Use a local JSON file, default:

```txt
data/playback_state.json
```

It should be created automatically when needed.

Store media-root-relative IDs where practical, not absolute machine-specific paths.

Good item IDs:

```txt
simpsons/Season 01/S01E01 Simpsons Roasting on an Open Fire.mkv
library/Movies/Pee-wees Big Adventure.mkv
library/VHS Rips/Tape 001 Saturday Morning Mix.mp4
```

Avoid storing only absolute paths like:

```txt
/Users/tommyday/TommyVision/sample_media/library/Movies/...
/media/crt/library/Movies/...
```

The same library should eventually be movable from Mac to Raspberry Pi.

If the current code makes relative media IDs difficult, implement a clean helper that derives a relative ID from the configured Simpsons/library roots.

Suggested JSON shape:

```json
{
  "items": {
    "library/Movies/Example Movie.mkv": {
      "display_name": "Example Movie",
      "absolute_path": "/Users/tommyday/TommyVision/sample_media/library/Movies/Example Movie.mkv",
      "position_seconds": 1234.5,
      "duration_seconds": 5400.0,
      "percent": 22.86,
      "updated_at": "2026-06-21T22:30:00",
      "completed": false
    }
  }
}
```

It is acceptable to store `absolute_path` as a convenience/debug field, but the item key should not be absolute.

## In-Progress Rules

Only save meaningful resume state.

Suggested rules:

- Ignore / remove state if `position_seconds` is less than 60 seconds.
- Mark completed or remove from in-progress if playback position is at least 90–95% of duration.
- If duration is unknown, still save position if it is greater than 60 seconds, but do not calculate percent.
- Clamp invalid values safely.
- Never crash if mpv returns null/unknown properties.

Config defaults can be:

```yaml
resume:
  enabled: true
  state_file: "./data/playback_state.json"
  minimum_position_seconds: 60
  completion_threshold_percent: 92
```

## mpv IPC Requirements

When launching normal media playback, start mpv with an IPC socket.

Use a unique socket path per playback session to avoid stale socket conflicts.

Examples:

macOS/Linux style:

```txt
/tmp/tommyvision-mpv-<pid>-<timestamp>.sock
```

Launch mpv with something like:

```txt
--input-ipc-server=<socket_path>
```

Keep existing configured mpv command and extra args.

Do not break current simple playback behavior.

If IPC setup fails, fallback should still play the video normally if possible, or show the existing readable error screen if playback cannot start.

## Playback Actions

The app already has an action system.

Add or wire these playback actions if not already present:

```txt
PLAY_PAUSE
STOP
SEEK_FORWARD
SEEK_BACK
```

For this pass, focus mainly on `STOP`.

During normal pygame menus, these actions can remain unused.

During mpv playback:

```txt
STOP:
  - query current mpv time-pos
  - query mpv duration
  - save resume state
  - send mpv quit
  - return to TommyVision

PLAY_PAUSE:
  - optional for this pass
  - if easy, send mpv cycle pause

SEEK_FORWARD:
  - optional for this pass
  - if easy, send mpv seek +10

SEEK_BACK:
  - optional for this pass
  - if easy, send mpv seek -10
```

Do not overbuild playback controls yet.

## Keyboard Mapping for Local Testing

For local testing, add temporary keyboard mappings if needed:

```txt
X = STOP during playback
Space = PLAY_PAUSE during playback
Right Arrow = SEEK_FORWARD during playback
Left Arrow = SEEK_BACK during playback
```

However, do not break current mpv keyboard behavior unless necessary.

It is acceptable if `Q` still quits mpv directly during local testing.

The important architecture goal is that TommyVision can perform its own STOP action through IPC.

If the current implementation blocks while waiting for mpv, adjust the playback path so a STOP action can be tested cleanly, but keep the implementation as simple as possible.

## Avoid Excessive Polling

Do not constantly write playback state to disk.

Optional fallback polling is allowed only if it is lightweight:

- Poll every 5–10 seconds maximum.
- Store latest known `time-pos` and `duration` in memory only.
- Save to disk only when STOP is triggered or when mpv exits and a valid latest-known position exists.

If polling adds too much complexity, skip it for now and rely on STOP-time querying.

## Resume Playback Behavior

This pass should save resume state.

It does **not** need to add a full Continue Watching UI yet.

However, when selecting a file that has saved progress, implement one of these conservative options:

Preferred if simple:

```txt
Show a small Resume / Start Over / Cancel screen:
  RESUME PLAYBACK?

  <display name>
  43:12 / 1:31:00

  > RESUME
    START OVER
    CANCEL
```

If that is too much for this pass, do this instead:

- Add resume state saving only.
- Do not change file selection behavior yet.
- Document that Continue Watching / Resume prompt will come in a later pass.

Do not add a big new main-menu Continue Watching item unless explicitly requested later.

## Starting Playback From a Saved Position

If implementing the Resume prompt now:

- `RESUME` should launch mpv with `--start=<seconds>` or equivalent.
- `START OVER` should launch from the beginning and optionally clear that item's resume state.
- `CANCEL` should return to the previous menu.

Do not use mpv's `--save-position-on-quit` as the primary resume system for this feature. TommyVision should own the saved state.

## Menu Music Interaction

The app already has optional menu music.

Preserve current behavior:

- Stop/pause menu music when launching mpv.
- Resume menu music after mpv exits.
- Do not allow menu music to keep playing over video playback.

## Boot Video / Screensaver Exclusion

Do not track resume state for:

- boot videos
- future screensaver videos
- UI asset videos

Resume tracking should apply only to normal user-selected media playback from Simpsons / CRT Library.

## Failure Handling

The app must not crash if:

- mpv is missing
- IPC socket cannot be created
- mpv starts but IPC never becomes available
- mpv exits immediately
- mpv returns null for time-pos
- mpv returns null for duration
- state file is missing
- state file contains invalid JSON
- data folder is missing
- selected media file has no saved state
- selected media file was moved/deleted

If state is invalid or stale, ignore it gracefully.

## Docs

Update documentation lightly.

Add notes to README and/or docs/controls.md:

- TommyVision can save resume positions through mpv IPC.
- Resume state is stored locally in `data/playback_state.json`.
- Runtime playback state is not intended to be committed to Git.
- STOP action is intended to become the remote Stop button later.
- For local testing, note whichever key maps to STOP during playback.
- `Q` may still quit mpv directly during local testing, but STOP is the TommyVision-owned save-and-exit path.

Do not add lots of on-screen instructions.

## Acceptance Criteria

After implementation:

- `python -m app.main` still starts the app.
- Existing menus still work.
- Simpsons playback still works.
- CRT Library playback still works.
- Optional logo, boot video, and menu music behavior is not broken.
- Normal media playback launches mpv with IPC support when possible.
- STOP action during playback queries mpv for `time-pos` and `duration`.
- STOP action saves resume state to `data/playback_state.json`.
- STOP action quits mpv and returns to TommyVision.
- State file is created automatically when needed.
- State file is ignored by Git.
- State keys are media-root-relative where practical.
- Very short playback sessions under the configured minimum are not kept as in-progress.
- Near-complete playback is marked completed or removed from in-progress.
- Missing/broken IPC does not crash the app.
- If a Resume prompt is implemented, Resume starts at saved position and Start Over starts from beginning.
- If Resume prompt is not implemented, the saved state still exists and docs note that the UI is future work.

## Testing Suggestions

Test locally with real sample media.

Baseline:

```bash
source .venv/bin/activate
python -m app.main
```

Manual tests:

1. Start a movie.
2. Stop with the TommyVision STOP key/action.
3. Confirm mpv quits and TommyVision returns to menu.
4. Confirm `data/playback_state.json` exists.
5. Confirm the file contains an entry for the movie.
6. Confirm the saved position is roughly correct.
7. Start and stop a video before 60 seconds; confirm it does not clutter in-progress state.
8. Stop a video near the end; confirm it is completed or removed based on the implementation.
9. Confirm menu music stops during playback and resumes after playback.
10. Confirm Q still works as a local mpv quit fallback if it was not intentionally changed.
11. Confirm app still behaves normally if `data/playback_state.json` is deleted.
12. Confirm app still behaves normally if `data/playback_state.json` contains invalid JSON.

Keep this pass focused. Build the playback-session/resume foundation, not the entire future media center.
