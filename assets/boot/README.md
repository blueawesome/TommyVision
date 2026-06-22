# Boot Video

Put an optional startup video here, for example:

```txt
assets/boot/boot.mp4
```

Enable it with `startup.play_boot_video` in `config/library.yaml`. TommyVision launches the video with `mpv`, waits for it to finish, then opens the main menu. Press `Q` in `mpv` to quit the boot video early.
