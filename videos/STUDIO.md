# GOR-9 — Standalone Video Studio Context (`videos/STUDIO.md`)

This document defines the project-specific conventions, native `2560×1440` QHD WebGL capture pipeline, FFmpeg dark-space encoding settings, and YouTube broadcast structure for standalone video packages in **`phiarchitect/GOR-9/videos/`**.

> **Broadcast Policy**: Do **not** publish any `GOR-9` videos as `public` on YouTube without explicit session approval from Phi (default test/staging uploads to `unlisted` or `private`).

---

## 1. Directory & Package Layout (`videos/`)

Standalone station videos live in top-level `videos/<slug>/` folders at the repository root:

```text
/home/phi/PROJECTS/phiarchitect/GOR-9/videos/
├── STUDIO.md                           # This Studio specification
├── cold_open/                          # 21.62s Station Power-Up, Marzelvane Burst & Lift-to-Booth Cold Open
│   ├── cold_open.wav                   # 24 kHz PCM master audio (Argon III-C + 1B C-Lydian Chime)
│   ├── gor9_cold_open.mp4              # 2560x1440 QHD 30.00 fps High@L5.1 master MP4
│   ├── gor9_cold_open_thumb.jpg        # 2560x1440 QHD <2MB JPEG thumbnail
│   ├── youtube.json                    # YouTube broadcast metadata & uploaded video_id tracking
│   └── frames/                         # Native 2560x1440 30.00 fps PNG sequence (frame_0000.png .. frame_0648.png)
├── drone_tour/                         # 30.00s Continuous Aerial Drone Tour + 3 C-Lydian Marzelvane Bursts
│   ├── gor9_drone_tour_audio.wav       # 24 kHz PCM generative C-Lydian soundtrack
│   ├── gor9_drone_tour.mp4             # 2560x1440 QHD 30.00 fps High@L5.1 master MP4
│   ├── gor9_drone_tour_thumb.jpg       # 2560x1440 QHD <2MB JPEG thumbnail
│   ├── youtube.json                    # YouTube broadcast metadata & uploaded video_id tracking
│   └── frames/                         # Native 2560x1440 30.00 fps PNG sequence (frame_0001.png .. frame_0900.png)
└── satellite_orbit/                    # 30.00s One Full 360° Pass of O.R.S. 351 + 3 C-Lydian Marzelvane Bursts
    ├── gor9_satellite_orbit_audio.wav  # 24 kHz PCM generative C-Lydian soundtrack
    ├── gor9_satellite_orbit.mp4        # 2560x1440 QHD 30.00 fps High@L5.1 master MP4
    ├── gor9_satellite_orbit_thumb.jpg  # 2560x1440 QHD <2MB JPEG thumbnail
    ├── youtube.json                    # YouTube broadcast metadata & uploaded video_id tracking
    └── frames/                         # Native 2560x1440 30.00 fps PNG sequence (frame_0001.png .. frame_0900.png)
```

---

## 2. Native `2560×1440` QHD WebGL Capture Standard

1. **Native QHD Framebuffer (`2560×1440`)**:
   - Launch headless Chromium with `--window-size=2560,1560` (`+120px` vertical headroom so window chrome never clips the canvas).
   - Lock Three.js WebGL renderer dimensions directly in memory:
     ```javascript
     renderer.setPixelRatio(1);
     renderer.setSize(2560, 1440, false);
     camera.aspect = 2560 / 1440;
     camera.updateProjectionMatrix();
     ```
2. **Disable Window Resize Listeners**:
   - Neutralize `window.addEventListener('resize'` (`-> '__disabled_resize'`) in the in-memory HTML response so asynchronous headless window resize events can never alter `camera.aspect` or `renderer.setSize` mid-capture.
3. **Full Surface Detail on Orbital Passes**:
   - Preserve full basalt PBR bump/roughness maps, anisotropic filtering, and station lighting during `satellite_orbit` renders.

---

## 3. Production `ffmpeg` Encoding Specification (Dark-Space Banding & VP9 Trigger)

All `2560×1440` (`16:9` QHD) masters are encoded at **Constant Frame Rate (`30.00 fps`)**, **1-Second Closed GOPs (`-g 30 -keyint_min 30`)**, **Temporal Micro-Dither (`noise=alls=2:allf=t`)**, and **Dark-Biased Auto-Variance Adaptive Quantization (`aq-mode=3:aq-strength=0.8`)**:

```bash
/usr/bin/ffmpeg -y \
  -framerate 30 -i frames/frame_%04d.png \
  -i audio.wav \
  -c:a aac -ar 48000 -ac 2 -b:a 192k -shortest \
  -t <duration> \
  -vf "fps=30,setsar=1:1,noise=alls=2:allf=t,format=yuv420p" \
  -vsync cfr -r 30 \
  -c:v libx264 -preset slow -profile:v high -level:v 5.1 \
  -crf 16 -x264-params "aq-mode=3:aq-strength=0.8" \
  -maxrate 16M -bufsize 32M \
  -g 30 -keyint_min 30 -sc_threshold 0 -bf 2 -flags +cgop \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -movflags +faststart \
  output.mp4
```
