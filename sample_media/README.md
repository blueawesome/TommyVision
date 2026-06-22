# Sample Media Layout

This folder is for local development paths only. Media files are ignored by Git.

Preferred structure:

```txt
sample_media/
  library/
    TV/
      The Simpsons/
        Season 01/
          S01E01 Simpsons Roasting on an Open Fire.mkv
    Movies/
    Specials/
    VHS Rips/
```

TommyVision's dedicated Simpsons mode should point at `sample_media/library/TV/The Simpsons` through `simpsons.path` in `config/library.yaml`. Legacy `sample_media/simpsons` layouts can still work through the old `paths.simpsons` fallback if `simpsons.path` is not configured.
