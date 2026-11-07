# GOR-9 — Narrative Episode Studio Context (`STUDIO.md`)

This document defines the project-specific conventions, script syntax, 3D visual pipeline, and acoustic vocabulary for producing narrative episodes in **`phiarchitect/GOR-9`**.

> **Broadcast Policy**: Do **not** make any `GOR-9` videos public on YouTube without explicit session approval from Phi.

---

## 1. Directory & Package Layout

Every episode lives in `episodes/ep<nn>_<slug>/` (e.g., `episodes/ep01_awakening/`):

### Tier 1 — Git-Tracked Source & Manifests
* `script.txt` / `scenes.json` — Episode script, scene timing, camera cues, and dialogue lines.
* `youtube.json` — Broadcast metadata (kept local/private until release approval).

### Tier 2 — Vault-Linked Master Media (`/home/phi/MEDIA/phiarchitect/GOR-9/episodes/ep<nn>_<slug>/`)
* `gor9_ep<nn>.mp4` — Master episode render (`1920x1080` or `2560x1440`, H.264 + AAC).
* `renders/` — Per-scene Blender / Three.js / SVG composite sequences and audio stems.

---

## 2. Episode Structure & Acoustic Cues

* Modular `=== <act_or_scene> ===` boundaries allow individual scenes and dialogue exchanges to be re-rendered without rebuilding the entire episode.
* Scene directives coordinate 3D console displays, tower telemetry, and atmospheric sound design (`[sfx:telemetry]`, `[sfx:console]`, `[bell:...]`).
* Master binary `.mp4` and `.wav` files are stored in `/home/phi/MEDIA/phiarchitect/GOR-9/` and symlinked into the working repository via:
  ```bash
  studio archive link --project gor9 --execute
  ```
