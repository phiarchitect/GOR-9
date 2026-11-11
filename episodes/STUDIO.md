# GOR-9 — Narrative Episode Studio Context (`episodes/STUDIO.md`)

This document defines the project-specific conventions, multi-character audio synthesis, Mode 2 (`motion`) rendering pipeline, and archive/broadcast workflow for narrative episodes in **`phiarchitect/GOR-9/episodes/`**.

> **Broadcast Policy (`@GOR-9-station`)**:
> - Do **not** make any `GOR-9` videos `public` on YouTube without explicit session approval from Phi. Uploads default to `private` using `~/.config/geometor/youtube_token_gor9.json`.

---

## 1. Directory & Package Layout (`episodes/`)

Every narrative episode lives in `episodes/ep<nn>_<slug>/` (e.g., `episodes/ep01_2736.305_parallelogram/`):

### Tier 1 — Git-Tracked Source & Manifests
* `script.scr` / `script.txt` — Episode script, scene timing, camera cues, and multi-character `[voice: <Voice> | style: <style>]` dialogue lines (synthesized via `photon_platform.studio.speak`).
* `youtube/youtube.json` (or `youtube.json`) — Broadcast metadata and uploaded `video_id` ledger.

### Tier 2 — Local Git-Ignored Master Media (Synced via `studio archive`)
All rendered `.mp4`, `.wav`, and thumbnail masters remain directly inside `episodes/ep<nn>_<slug>/` as real local files (**never create symlinks to `/home/phi/MEDIA`**):
* `gor9_ep<nn>*.mp4` — Full episode master (`2560x1440` QHD @ `30.00 fps` CFR, `yuv420p`, `+faststart`, AAC).
* `audio/*.wav` — Master 24 kHz PCM audio mix.

### Tier 3 — Ephemeral Build Scratch
* `console_plates/`, `frames_cold_open_3d/`, `slides_cold_open_3d/`, `audio/segments/`, `_*_concat.txt`.

---

## 2. Rendering Mode: 30 FPS Full-Motion Animation (`studio motion`)

1. **True Native `2560x1440` @ `30.00 fps` Capture**:
   * **WebGL (`docs/tower-3d.html`)**: Driven via `studio motion` on hardware GPU (`--use-gl=angle --use-angle=gl`) with window-resize lock and full PBR basalt/anisotropy fidelity.
   * **HTML Console Plates (`scripts/capture_console_plates.py`)**: Captured at `1920x1080` CSS with `--force-device-scale-factor=1.3333333333` -> `2560x1440` PNGs.
   * **Blender & Python/PIL Compositor (`scripts/render_full_episode.py`)**: Rendered at native `2560x1440` and `FPS = 30` (never `24 fps` converted to `30 fps`).
2. **Clean FFmpeg Encode (Zero `-vf` Filters)**:
   * Do **not** pass `-vf` filters (`noise=...`, `setsar=...`), `-color_range tv`, or custom x264 AQ overrides.
   * Always output `-pix_fmt yuv420p -movflags +faststart` for universal playback across YouTube (`vp09`), Safari, QuickTime, and mobile:
     ```bash
     /usr/bin/ffmpeg -y -framerate 30 -i frames/frame_%04d.png -i audio.wav -pix_fmt yuv420p -movflags +faststart output.mp4
     ```
   * Verify masters with `studio verify episodes/ep01_2736.305_parallelogram`.

---

## 3. Archive & Broadcast Commands (`@GOR-9-station`)

```bash
# Push or pull git-ignored Tier 2 episode media with Google Drive (gdrive:PHOTON-MEDIA)
studio archive sync episodes/ phiarchitect/GOR-9/episodes --direction push
studio archive sync episodes/ phiarchitect/GOR-9/episodes --direction pull

# Check status, repair thumbnails, or explicitly publish approved episodes
studio broadcast status --project GOR-9
studio broadcast repair episodes/ep01_2736.305_parallelogram
studio broadcast publish episodes/ep01_2736.305_parallelogram --channel @GOR-9-station
```
