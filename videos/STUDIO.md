# GOR-9 — Standalone Video Studio Context (`videos/STUDIO.md`)

This document defines the project-specific conventions, native `2560×1440` QHD WebGL capture pipeline (`studio motion`), clean FFmpeg encoding specification, and YouTube broadcast guardrails for standalone video packages in **`phiarchitect/GOR-9/videos/`**.

> **Broadcast Policy (`@GOR-9-station`)**:
> - Default uploads to **`private`** (or `unlisted` when staging). **Never** publish any `GOR-9` video as `public` without explicit session approval from Phi (`studio broadcast publish <pkg> --channel @GOR-9-station`).
> - OAuth token: `~/.config/geometor/youtube_token_gor9.json` (verified against `@GOR-9-station` before every upload).

---

## 1. Directory & Package Layout (`videos/`)

Standalone station videos live in top-level `videos/<slug>/` folders at the repository root:

```text
/home/phi/PROJECTS/phiarchitect/GOR-9/videos/
├── STUDIO.md                           # This Studio specification
├── playlists.json                      # GOR-9 YouTube playlist manifest
├── cold_open/                          # Station Power-Up, Marzelvane Burst & Lift-to-Booth Cold Open
├── drone_tour/                         # 30.00s Continuous Aerial Drone Tour + 3 C-Lydian Marzelvane Bursts
├── drone_loop/                         # 54.00s Seamless Inverse-Keplerian Elliptical Drone Loop (`camera_path.json`)
├── satellite_orbit/                    # 30.00s One Full 360° Pass of O.R.S. 351 (`camera_path.json`)
├── booth_tour/                         # Interior Octagonal Broadcast Booth Tour (`camera_path.json`)
├── booth_loop/                         # Seamless Interior Broadcast Booth Loop (`camera_path.json`)
└── mk4_demo/                           # Hauser Dynamics MK-IV Receiver Interactive Console Demo (`script.scr`)
```

### 3-Tier Storage Policy (No Symlinks)
- **Tier 1 (Git-Tracked Source)**: `STUDIO.md`, `playlists.json`, `camera_path.json`, `motion.json`, `script.scr`, `tour_choreography.js`, `youtube.json`.
- **Tier 2 (Local Git-Ignored Master Media, synced via `studio archive`)**: `gor9_*.mp4`, `*.wav`, `*_thumb.jpg`, `*_thumb.png`, `.tts_cache/`.
- **Tier 3 (Ephemeral Build Scratch)**: `frames/`, `test_frames/`, `segments/`, `stage.html`.

---

## 2. Mode 2 (`studio motion`) Native `2560×1440` QHD WebGL Capture

`photon_platform.studio.motion` natively drives `docs/tower-3d.html` (and any Three.js / WebGL / DOM console) from `camera_path.json` or `motion.json`:

1. **5 Declarative Coordinate Systems (`camera_path.json`)**:
   - `cylindrical` / `tower_cylindrical` (`camAz`, `camR`, `camY`, `lookAz`, `lookR`, `lookY`, `fov`)
   - `spherical` (`camAz`, `camEl`, `camR`, `lookX`, `lookY`, `lookZ`, `fov`, `roll`)
   - `cartesian` (`camX`, `camY`, `camZ`, `lookX`, `lookY`, `lookZ`, `fov`, `roll`)
   - `booth_cylindrical` / `interior_cylindrical` (`camAng`, `camR`, `camYRel`, `lookAng`, `lookR`, `lookYRel`, `fov`)
   - `object_locked` / `satellite_locked` (`target_object`, `local_pos`, `local_look`, `fov`)
2. **Hardware GPU & Resize Lock**:
   - Runs headless Chromium on hardware GPU (`--use-gl=angle --use-angle=gl`) with `--window-size=2560,1600` (`1920x1080` @ `scale_factor: 1.333333` for HUD console demos) and neutralizes `window.addEventListener('resize')` so WebGL framebuffers never tear.
3. **Commands**:
   ```bash
   studio motion videos/drone_loop
   studio motion videos/drone_loop --test-frames
   studio motion videos/drone_loop --encode-only
   studio verify videos/mk4_demo
   ```

---

## 3. Clean FFmpeg Encoding Specification (Zero `-vf` Filters)

All `2560×1440` (`16:9` QHD, triggering YouTube's `vp09` hardware pipeline) masters are encoded at **`30.00 fps` CFR** with **`-pix_fmt yuv420p -movflags +faststart`** and **zero `-vf` filters** (no synthetic grain `noise=...`, no `-color_range tv` crushing, and no custom x264 AQ overrides; `-vf vflip` is used only when streaming raw bottom-up `gl.readPixels` RGBA buffers directly into FFmpeg):

```bash
/usr/bin/ffmpeg -y \
  -framerate 30 -i frames/frame_%04d.png \
  -i audio.wav \
  -c:v libx264 -crf 16 -preset slow \
  -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest \
  -movflags +faststart \
  output.mp4
```

---

## 4. Archive & YouTube Broadcast (`@GOR-9-station`)

```bash
# Scan & sync Tier 2 master media with Google Drive (no symlinks)
studio archive scan videos/
studio archive sync videos/ phiarchitect/GOR-9/videos --direction push

# Authorize, upload (defaults to private), verify status, or explicitly publish
studio broadcast auth --channel @GOR-9-station
studio broadcast upload videos/mk4_demo --no-captions
studio broadcast status --project GOR-9
studio broadcast publish videos/mk4_demo --channel @GOR-9-station
```
