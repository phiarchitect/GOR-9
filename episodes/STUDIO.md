# GOR-9 — Narrative Episode & 3D Tour Studio Context (`STUDIO.md`)

This document defines the project-specific conventions, rendering modes, and archive workflow for producing narrative episodes and 3D WebGL/Blender tours in **`phiarchitect/GOR-9`**.

> **Broadcast Policy**: Do **not** make any `GOR-9` videos public on YouTube without explicit session approval from Phi.

---

## 1. Directory & Package Layout

Every episode and 3D tour lives directly in `episodes/ep<nn>_<slug>/` (e.g., `episodes/ep01_2736.305_parallelogram/`):

### Tier 1 — Git-Tracked Source & Manifests
* `script.scr` / `script.txt` — Episode script, scene timing, camera cues, and dialogue lines.
* `youtube.json` — Broadcast metadata (kept local/private until release approval).

### Tier 2 — Local Git-Ignored Master Media (Archived via `studio archive push` / `pull`)
All rendered `.mp4`, `.wav`, and thumbnail masters stay directly inside `episodes/ep<nn>_<slug>/` as real local files (**never create symlinks to `/home/phi/MEDIA`**):
* `gor9_ep<nn>.mp4` — Full episode master (`2560x1440` QHD @ `30.00 fps` CFR, H.264 High@L5.1 + AAC).
* `drone_tour/gor9_drone_tour.mp4` — 30.00s WebGL Drone Tour (`2560x1440` QHD @ `30.00 fps` CFR).
* `satellite_orbit/gor9_satellite_orbit.mp4` — 30.00s WebGL Satellite Orbit (`2560x1440` QHD @ `30.00 fps` CFR).

---

## 2. Rendering Mode: 30 FPS Full-Motion Animation (`motion`)

Unlike slide-deck repositories, `GOR-9` 3D tours, cold opens, and composite episodes use **Studio Mode 2 (`motion` — 30 FPS Full-Motion Animation)**:

1. **True Native `2560x1440` @ `30.00 fps` Capture**:
   * **WebGL (`docs/tower-3d.html`)**: Launch Chromium with padded window height (`--window-size=2560,1560`, `--ozone-platform=headless`) and disable `window.addEventListener('resize')` so the framebuffer is never clipped to `941px`. Render at `renderer.setPixelRatio(1); renderer.setSize(2560, 1440, false);` with full material fidelity (preserve `anisotropy`, `basaltBumpMap`, and `basaltRoughMap`).
   * **Blender & Python/PIL Compositor (`render_full_episode.py`)**: Always render at native `2560x1440` and `FPS = 30` (never render at `24 fps` and convert to `30 fps`, which causes 4:5 frame-duplication judder).
2. **Direct FFmpeg Encode (Zero Filters)**:
   * Do **not** pass `-vf` filters (such as `noise=...`, `setsar=...`, or `format=yuv420p`) or custom x264 rate-control/AQ overrides, which inflate bitrates and degrade YouTube's adaptive stream selection.
   * Assemble frames and audio directly with default `ffmpeg`:
     ```bash
     ffmpeg -y -framerate 30 -i frames/frame_%04d.png -i audio.wav output.mp4
     ```

---

## 3. Archive Commands (No Symlinks)

* **Push Git-Ignored Master Media to Google Drive (`gdrive:PHOTON-MEDIA`)**:
  ```bash
  studio archive sync episodes/ phiarchitect/GOR-9/episodes --direction push
  ```
* **Pull Git-Ignored Master Media on Another Machine**:
  ```bash
  studio archive sync episodes/ phiarchitect/GOR-9/episodes --direction pull
  ```
