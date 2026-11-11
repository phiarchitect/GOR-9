#!/usr/bin/env python3
"""Universal 3D WebGL Model + Camera Path/Sequence Recorder (`record_model_sequence`).

Takes any Three.js / WebGL 3D model HTML file (e.g., `docs/tower-3d.html`, future
`docs/dilithium-reactor-3d.html`, `docs/dilithium-pellets-3d.html`) and a declarative
camera path/sequence specification (`camera_path.json` or Python dict) and records a
frame-accurate, tear-audited `2560x1440` QHD (`30.00 fps` CFR) video without modifying
the 3D model HTML on disk.

Supported Coordinate Systems in `camera_path.json`:
  - `cylindrical` / `tower_cylindrical`:
      `{ t, camAz, camR, camY, lookAz, lookR, lookY, fov }` around `origin: [ox, oy, oz]`
  - `spherical` (ideal for 360° macro/orbital inspection of reactors, crystals, pellets):
      `{ t, camAz, camEl, camR, lookX, lookY, lookZ, fov, roll }`
  - `cartesian` (direct 3D world coordinates):
      `{ t, camX, camY, camZ, lookX, lookY, lookZ, fov, roll }`
  - `booth_cylindrical` / `interior_cylindrical`:
      `{ t, camAng, camR, camYRel, lookAng, lookR, lookYRel, fov }`
  - `object_locked` / `satellite_locked`:
      Camera locked to a moving scene object (`target_object`, `local_pos`, `local_look`, `fov`)

Python API:
  ```python
  from scripts.record_model_sequence import record_model_sequence

  result = record_model_sequence(
      model_html="docs/tower-3d.html",
      camera_path="videos/drone_loop/camera_path.json",
      workers=2,
  )
  ```

CLI Usage:
  ```bash
  python3 scripts/record_model_sequence.py \
      --model docs/tower-3d.html \
      --path videos/drone_loop/camera_path.json \
      --workers 2
  ```
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import shutil
import socketserver
import struct
import subprocess
import sys
import threading
import time
import zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_WIDTH = 2560
DEFAULT_HEIGHT = 1440
DEFAULT_FPS = 30


# ═══════════════════════════════════════════════════════════════════════════
# 1. UNIVERSAL IN-MEMORY THREE.JS / WEBGL CAMERA & SEQUENCE DRIVER (JS)
# ═══════════════════════════════════════════════════════════════════════════

UNIVERSAL_RECORDER_JS = r"""
    // ═════════════════════════════════════════════════════════════════
    // UNIVERSAL DETERMINISTIC 3D MODEL & CAMERA PATH RECORDER ENGINE
    // Supports:
    //   1. Fritsch-Carlson monotonic cubic Hermite keyframe interpolation
    //      with optional periodic loop slopes (`is_loop: true`) and automatic
    //      angle unwrapping (`angle_unit: "rad" | "deg"`).
    //   2. Coordinate systems:
    //      - `cylindrical` / `tower_cylindrical`
    //      - `spherical` (azimuth + elevation + radius around target)
    //      - `cartesian` (camX/Y/Z + lookX/Y/Z)
    //      - `booth_cylindrical` / `interior_cylindrical`
    //      - `object_locked` / `satellite_locked`
    //   3. Model animation hooks:
    //      - `window.setModelStateAtTime(t, duration, cfg)` (universal hook for new models)
    //      - `window.setModelTime(t, duration, cfg)`
    //      - Built-in GOR-9 `tower-3d.html` deterministic state adapter
    //      - Fallback deterministic virtual clock + RAF stepper
    // ═════════════════════════════════════════════════════════════════
    let _lastHudState = -1;

    function unwrapAngleSeries(angles) {
      if (!angles || angles.length === 0) return [];
      const out = [angles[0]];
      for (let i = 1; i < angles.length; i++) {
        let d = angles[i] - angles[i - 1];
        while (d > Math.PI) d -= Math.PI * 2.0;
        while (d < -Math.PI) d += Math.PI * 2.0;
        out.push(out[i - 1] + d);
      }
      return out;
    }

    function evalMonotonicCubic(xs, ys, xQuery, isPeriodicSlope) {
      const n = xs.length;
      if (n === 0) return 0.0;
      if (n === 1) return ys[0];
      const dxs = [];
      const dys = [];
      const ms = [];
      for (let i = 0; i < n - 1; i++) {
        const dx = Math.max(1e-6, xs[i + 1] - xs[i]);
        const dy = ys[i + 1] - ys[i];
        dxs.push(dx);
        dys.push(dy);
        ms.push(dy / dx);
      }
      const c1s = new Array(n).fill(0);
      if (isPeriodicSlope) {
        const mAvg = 0.5 * (ms[0] + ms[n - 2]);
        c1s[0] = mAvg;
        c1s[n - 1] = mAvg;
      } else {
        c1s[0] = 0.0;
        c1s[n - 1] = 0.0;
      }
      for (let i = 1; i < n - 1; i++) {
        const m0 = ms[i - 1];
        const m1 = ms[i];
        if (m0 * m1 <= 0) {
          c1s[i] = 0.0;
        } else {
          const dx0 = dxs[i - 1];
          const dx1 = dxs[i];
          const common = dx0 + dx1;
          c1s[i] = (3.0 * common) / ((common + dx1) / m0 + (common + dx0) / m1);
        }
      }
      let seg = n - 2;
      for (let i = 0; i < n - 1; i++) {
        if (xQuery >= xs[i] && xQuery <= xs[i + 1]) {
          seg = i;
          break;
        }
      }
      const h = dxs[seg];
      const u = Math.max(0.0, Math.min(1.0, (xQuery - xs[seg]) / h));
      const u2 = u * u;
      const u3 = u2 * u;
      const h00 = 2.0 * u3 - 3.0 * u2 + 1.0;
      const h10 = u3 - 2.0 * u2 + u;
      const h01 = -2.0 * u3 + 3.0 * u2;
      const h11 = u3 - u2;
      return h00 * ys[seg] + h10 * h * c1s[seg] + h01 * ys[seg + 1] + h11 * h * c1s[seg + 1];
    }

    function evalCameraPathPose(cfg, t, duration) {
      const kfs = cfg.keyframes || [];
      if (kfs.length === 0) {
        return { camX: 0, camY: 5, camZ: 15, targetX: 0, targetY: 0, targetZ: 0, fov: 45, roll: 0 };
      }
      const isLoop = !!cfg.is_loop;
      const pathDur = cfg.duration || duration;
      const tQuery = isLoop
        ? (((t % duration) + duration) % duration) * (pathDur / duration)
        : Math.max(0.0, Math.min(pathDur, (t / duration) * pathDur));
      const ts = kfs.map((k) => k.t);
      const coordSys = cfg.coordinate_system || 'cylindrical';
      const angleScale = (cfg.angle_unit === 'deg' || cfg.angle_unit === 'degrees') ? (Math.PI / 180.0) : 1.0;
      const origin = cfg.origin || [0.0, 0.0, 0.0];
      const ox = origin[0] || 0.0;
      const oy = origin[1] || 0.0;
      const oz = origin[2] || 0.0;

      if (coordSys === 'cylindrical' || coordSys === 'tower_cylindrical') {
        const camAz = evalMonotonicCubic(ts, kfs.map((k) => (k.camAz ?? k.az ?? 0.0) * angleScale), tQuery, true);
        const camR = evalMonotonicCubic(ts, kfs.map((k) => k.camR ?? k.distR ?? 50.0), tQuery, false);
        const camY = evalMonotonicCubic(ts, kfs.map((k) => k.camY ?? 35.0), tQuery, false);
        const lookAz = evalMonotonicCubic(ts, kfs.map((k) => (k.lookAz ?? k.camAz ?? k.az ?? 0.0) * angleScale), tQuery, true);
        const lookR = evalMonotonicCubic(ts, kfs.map((k) => k.lookR ?? 0.0), tQuery, false);
        const lookY = evalMonotonicCubic(ts, kfs.map((k) => k.lookY ?? k.targetY ?? 42.0), tQuery, false);
        const fov = evalMonotonicCubic(ts, kfs.map((k) => k.fov ?? 46.0), tQuery, false);
        const roll = evalMonotonicCubic(ts, kfs.map((k) => (k.roll ?? 0.0) * angleScale), tQuery, false);
        return {
          camX: ox + Math.cos(camAz) * camR,
          camY: oy + camY,
          camZ: oz + Math.sin(camAz) * camR,
          targetX: ox + Math.cos(lookAz) * lookR,
          targetY: oy + lookY,
          targetZ: oz + Math.sin(lookAz) * lookR,
          fov: fov,
          roll: roll,
        };
      } else if (coordSys === 'spherical') {
        // Spherical orbit around target (lookX, lookY, lookZ): ideal for inspecting reactors, pellets, artifacts
        const camAz = evalMonotonicCubic(ts, kfs.map((k) => (k.camAz ?? k.az ?? 0.0) * angleScale), tQuery, isLoop);
        const camEl = evalMonotonicCubic(ts, kfs.map((k) => (k.camEl ?? k.el ?? 0.25) * angleScale), tQuery, false);
        const camR = evalMonotonicCubic(ts, kfs.map((k) => k.camR ?? k.distR ?? 10.0), tQuery, false);
        const targetX = evalMonotonicCubic(ts, kfs.map((k) => k.lookX ?? k.targetX ?? ox), tQuery, false);
        const targetY = evalMonotonicCubic(ts, kfs.map((k) => k.lookY ?? k.targetY ?? oy), tQuery, false);
        const targetZ = evalMonotonicCubic(ts, kfs.map((k) => k.lookZ ?? k.targetZ ?? oz), tQuery, false);
        const fov = evalMonotonicCubic(ts, kfs.map((k) => k.fov ?? 42.0), tQuery, false);
        const roll = evalMonotonicCubic(ts, kfs.map((k) => (k.roll ?? 0.0) * angleScale), tQuery, false);
        const cosEl = Math.cos(camEl);
        return {
          camX: targetX + cosEl * Math.cos(camAz) * camR,
          camY: targetY + Math.sin(camEl) * camR,
          camZ: targetZ + cosEl * Math.sin(camAz) * camR,
          targetX,
          targetY,
          targetZ,
          fov,
          roll,
        };
      } else if (coordSys === 'booth_cylindrical' || coordSys === 'interior_cylindrical') {
        const baseFloorY = cfg.floor_y ?? (typeof BOOTH_Y !== 'undefined' ? BOOTH_Y : oy);
        const camAng = evalMonotonicCubic(ts, kfs.map((k) => (k.camAng ?? 0.0) * angleScale), tQuery, isLoop);
        const camR = evalMonotonicCubic(ts, kfs.map((k) => k.camR ?? 2.5), tQuery, isLoop);
        const camYRel = evalMonotonicCubic(ts, kfs.map((k) => k.camYRel ?? 1.5), tQuery, isLoop);
        const lookAng = evalMonotonicCubic(ts, kfs.map((k) => (k.lookAng ?? 0.0) * angleScale), tQuery, isLoop);
        const lookR = evalMonotonicCubic(ts, kfs.map((k) => k.lookR ?? 4.74), tQuery, isLoop);
        const lookYRel = evalMonotonicCubic(ts, kfs.map((k) => k.lookYRel ?? 1.25), tQuery, isLoop);
        const fov = evalMonotonicCubic(ts, kfs.map((k) => k.fov ?? 50.0), tQuery, isLoop);
        const roll = evalMonotonicCubic(ts, kfs.map((k) => (k.roll ?? 0.0) * angleScale), tQuery, isLoop);
        const strides = cfg.head_bob_strides || 0;
        const loopPhase = (tQuery / pathDur) * Math.PI * 2.0;
        const stepBob = strides > 0 ? 0.010 * Math.sin(strides * loopPhase) : 0.0;
        return {
          camX: ox + camR * Math.sin(camAng),
          camY: baseFloorY + camYRel + stepBob,
          camZ: oz - camR * Math.cos(camAng),
          targetX: ox + lookR * Math.sin(lookAng),
          targetY: baseFloorY + lookYRel + stepBob * 0.5,
          targetZ: oz - lookR * Math.cos(lookAng),
          fov: fov,
          roll: roll,
        };
      } else {
        // 'cartesian' direct world coordinates
        const camX = evalMonotonicCubic(ts, kfs.map((k) => k.camX ?? 0.0), tQuery, isLoop);
        const camY = evalMonotonicCubic(ts, kfs.map((k) => k.camY ?? 30.0), tQuery, isLoop);
        const camZ = evalMonotonicCubic(ts, kfs.map((k) => k.camZ ?? 50.0), tQuery, isLoop);
        const targetX = evalMonotonicCubic(ts, kfs.map((k) => k.lookX ?? k.targetX ?? 0.0), tQuery, isLoop);
        const targetY = evalMonotonicCubic(ts, kfs.map((k) => k.lookY ?? k.targetY ?? 30.0), tQuery, isLoop);
        const targetZ = evalMonotonicCubic(ts, kfs.map((k) => k.lookZ ?? k.targetZ ?? 0.0), tQuery, isLoop);
        const fov = evalMonotonicCubic(ts, kfs.map((k) => k.fov ?? 46.0), tQuery, isLoop);
        const roll = evalMonotonicCubic(ts, kfs.map((k) => (k.roll ?? 0.0) * angleScale), tQuery, isLoop);
        return { camX, camY, camZ, targetX, targetY, targetZ, fov, roll };
      }
    }

    function applyCameraPoseToThree(pose) {
      camera.fov = pose.fov;
      camera.updateProjectionMatrix();
      camera.position.set(pose.camX, pose.camY, pose.camZ);
      if (typeof controls !== 'undefined' && controls && controls.target) {
        controls.enableDamping = false;
        controls.target.set(pose.targetX, pose.targetY, pose.targetZ);
        controls.update();
      } else {
        camera.lookAt(pose.targetX, pose.targetY, pose.targetZ);
      }
      if (pose.roll && Math.abs(pose.roll) > 1e-5) {
        camera.rotateZ(pose.roll);
      }
    }

    function setUniversalModelStateAtTime(mode, t, duration, targetW, targetH) {
      const cfg = typeof CAMERA_PATH_CONFIG !== 'undefined' ? CAMERA_PATH_CONFIG : { mode, duration, is_loop: false };

      // 1. Hide HTML UI overlays for clean cinema capture
      const defaultSelectors = ['.top-nav', '#hud-left', '#hud-right', '#hud-bottom', '.hud-overlay', '.ui-panel'];
      const customSelectors = cfg.hide_selectors || [];
      for (const sel of defaultSelectors.concat(customSelectors)) {
        document.querySelectorAll(sel).forEach((el) => {
          el.style.display = 'none';
        });
      }

      // 2. If the model provides a native `window.setModelStateAtTime` or `window.setModelTime` hook, call it!
      if (typeof window.setModelStateAtTime === 'function') {
        window.setModelStateAtTime(t, duration, cfg);
      } else if (typeof window.setModelTime === 'function') {
        window.setModelTime(t, duration, cfg);
      }

      // 3. Built-in adapter for GOR-9 `docs/tower-3d.html` when present
      if (typeof marzelRings !== 'undefined' && typeof ors351Sat !== 'undefined') {
        setGor9TowerStateAtTime(mode, t, duration, cfg);
      } else {
        // Generic Three.js model camera evaluation & render
        const pose = evalCameraPathPose(cfg, t, duration);
        applyCameraPoseToThree(pose);
      }

      if (renderer.domElement.width !== targetW || renderer.domElement.height !== targetH) {
        renderer.setPixelRatio(1);
        renderer.setSize(targetW, targetH, false);
      }
      camera.aspect = targetW / targetH;
      camera.updateProjectionMatrix();
      renderer.render(scene, camera);
    }
"""


def _rgba_bottom_up_to_png_bytes(data: bytes, width: int, height: int) -> bytes:
    """Convert bottom-up WebGL RGBA bytes into a valid lossless PNG using stdlib zlib."""
    stride = width * 4
    raw_rows = bytearray((stride + 1) * height)
    pos = 0
    for y in range(height - 1, -1, -1):
        raw_rows[pos] = 0
        pos += 1
        row_start = y * stride
        raw_rows[pos : pos + stride] = data[row_start : row_start + stride]
        pos += stride

    def make_chunk(chunk_type: bytes, chunk_data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        return struct.pack(">I", len(chunk_data)) + chunk_type + chunk_data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw_rows), level=1)
    return (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(b"IHDR", ihdr)
        + make_chunk(b"IDAT", compressed)
        + make_chunk(b"IEND", b"")
    )


def find_chrome_binary() -> str:
    pw_root = Path.home() / ".cache" / "ms-playwright"
    if pw_root.is_dir():
        for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
            return str(candidate)
    for c in (
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
    ):
        p = shutil.which(c)
        if p:
            return p
    raise RuntimeError("No Chromium/Chrome binary found.")


def purge_torn_frames(
    frames_dir: Path,
    mode: str,
    width: int = DEFAULT_WIDTH,
    audit_only: bool = False,
) -> list[int]:
    """Detect and optionally delete frames affected by headless window resize tears (duplicate top-32-row CRC groups)."""
    if not frames_dir.exists():
        return []
    row_stride = 1 + width * 4
    top32_len = 32 * row_stride
    crc_to_frames: dict[int, list[tuple[int, Path]]] = {}
    torn_indices: list[int] = []

    for png_path in sorted(frames_dir.glob("frame_*.png")):
        try:
            frame_num = int(png_path.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        data = png_path.read_bytes()
        if len(data) < 64:
            torn_indices.append(frame_num)
            if not audit_only:
                png_path.unlink(missing_ok=True)
            continue
        try:
            raw = zlib.decompress(data[41:-16])
        except Exception:
            torn_indices.append(frame_num)
            if not audit_only:
                png_path.unlink(missing_ok=True)
            continue

        top_crc = zlib.crc32(raw[:top32_len])
        crc_to_frames.setdefault(top_crc, []).append((frame_num, png_path))

    for top_crc, items in crc_to_frames.items():
        if len(items) > 1:
            for frame_num, png_path in items:
                torn_indices.append(frame_num)
                if not audit_only:
                    png_path.unlink(missing_ok=True)

    torn_indices.sort()
    action = "Audited (found)" if audit_only else "Purged"
    print(
        f"[{mode}] {action} {len(torn_indices)} torn frames in {frames_dir}"
        + (f" (sample: {torn_indices[:15]})" if torn_indices else ""),
        flush=True,
    )
    return torn_indices


class _ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _ModelSequenceHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(
        self,
        *args: Any,
        directory: str,
        model_html_path: Path,
        frames_dir: Path,
        camera_path_cfg: dict[str, Any],
        injected_driver_js: str,
        width: int,
        height: int,
        done_event: threading.Event,
        expected_workers: int,
        state: dict[str, Any],
        lock: threading.Lock,
        **kwargs: Any,
    ) -> None:
        self._model_html_path = model_html_path
        self._frames_dir = frames_dir
        self._camera_path_cfg = camera_path_cfg
        self._injected_driver_js = injected_driver_js
        self._width = width
        self._height = height
        self._done_event = done_event
        self._expected_workers = expected_workers
        self._state = state
        self._lock = lock
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/__capture_tour.html") or self.path.startswith("/__capture_model.html"):
            orig_html = self._model_html_path.read_text(encoding="utf-8")
            patched = orig_html.replace(
                "window.addEventListener('resize'",
                "window.addEventListener('__disabled_resize'",
            )
            cfg_js = (
                f"    const CAMERA_PATH_CONFIG = {json.dumps(self._camera_path_cfg)};\n"
                f"    const STUDIO_TARGET_W = {self._width};\n"
                f"    const STUDIO_TARGET_H = {self._height};\n"
            )
            if "    animate();\n  </script>" in patched:
                patched = patched.replace(
                    "    animate();\n  </script>",
                    cfg_js + self._injected_driver_js + "\n  </script>",
                    1,
                )
            elif "</script>" in patched:
                idx = patched.rfind("</script>")
                patched = (
                    patched[:idx]
                    + "\n"
                    + cfg_js
                    + self._injected_driver_js
                    + "\n"
                    + patched[idx:]
                )
            else:
                patched += f"\n<script>\n{cfg_js}\n{self._injected_driver_js}\n</script>\n"

            body = patched.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = self.rfile.read(length) if length > 0 else b""
            if self.path.startswith("/__js_log"):
                print(f"  [JS] {data.decode('utf-8', errors='replace')}", flush=True)
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"OK")
                return
            if self.path.startswith("/__raw_rgba/"):
                idx = int(self.path.split("/")[-1])
                png_bytes = _rgba_bottom_up_to_png_bytes(data, self._width, self._height)
                out_path = self._frames_dir / f"frame_{idx + 1:04d}.png"
                out_path.write_bytes(png_bytes)
                with self._lock:
                    self._state["captured"] = self._state.get("captured", 0) + 1
                    self._state["last_capture_ts"] = time.monotonic()
                    c = self._state["captured"]
                    tf = self._state.get("total_frames", 1)
                if c % 10 == 0 or c == tf:
                    print(f"  Captured {c}/{tf} frames (latest: frame_{idx + 1:04d}.png)", flush=True)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", "2")
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(b"OK")
                return
            if self.path.startswith("/__done"):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", "4")
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(b"DONE")
                with self._lock:
                    self._state["done_workers"] = self._state.get("done_workers", 0) + 1
                    if self._state["done_workers"] >= self._expected_workers:
                        self._done_event.set()
                return
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
        except (BrokenPipeError, ConnectionResetError):
            pass


def resolve_model_and_camera_path(
    model_html: str | Path | None,
    camera_path: str | Path | dict[str, Any],
    output_dir: str | Path | None = None,
) -> tuple[Path, dict[str, Any], Path]:
    """Resolve `(model_html_path, camera_path_cfg, output_dir_path)` from flexible arguments."""
    path_file: Path | None = None
    if isinstance(camera_path, dict):
        cfg = dict(camera_path)
    else:
        p = Path(camera_path).resolve()
        if p.is_dir():
            p = p / "camera_path.json"
        if not p.exists():
            raise FileNotFoundError(f"Camera path file not found: {p}")
        path_file = p
        cfg = json.loads(p.read_text(encoding="utf-8"))

    # Resolve model HTML path (from explicit argument, or `cfg["model"]`, or default `docs/tower-3d.html`)
    raw_model = model_html or cfg.get("model") or "docs/tower-3d.html"
    model_candidate = Path(raw_model)
    if not model_candidate.is_absolute():
        if (ROOT / model_candidate).exists():
            model_candidate = (ROOT / model_candidate).resolve()
        elif path_file and (path_file.parent / model_candidate).exists():
            model_candidate = (path_file.parent / model_candidate).resolve()
        else:
            model_candidate = model_candidate.resolve()
    if not model_candidate.exists():
        raise FileNotFoundError(f"3D model HTML file not found: {model_candidate}")

    # Resolve output directory
    if output_dir is not None:
        out_dir = Path(output_dir).resolve()
    elif path_file is not None:
        out_dir = path_file.parent
    else:
        mode_slug = cfg.get("mode", "sequence")
        out_dir = ROOT / "videos" / mode_slug

    return model_candidate, cfg, out_dir


def record_model_sequence(
    model_html: str | Path | None = None,
    camera_path: str | Path | dict[str, Any] = "",
    output_dir: str | Path | None = None,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int | None = None,
    duration: float | None = None,
    workers: int = 2,
    clean: bool = False,
    test_frames_only: bool = False,
    repair_torn: bool = True,
    encode_mp4: bool = True,
    audio_wav: str | Path | None = None,
) -> dict[str, Any]:
    """Record a 3D HTML model (`model_html`) along a declarative `camera_path` sequence accurately.

    1. Loads `model_html` in headless hardware-GPU Chromium without modifying the HTML file on disk.
    2. Steps every frame `idx` at exact timestamp `t = idx / fps` using monotonic cubic Hermite
       camera interpolation (`cylindrical`, `spherical`, `cartesian`, `booth_cylindrical`, or `object_locked`).
    3. Audits rendered PNG frames for headless window resize tears (duplicate top-32-row CRCs)
       and automatically re-renders any torn/missing frames until `0` torn frames remain.
    4. Encodes the final `2560x1440` QHD MP4 using direct FFmpeg (`zero -vf filters`) and exports
       the hero thumbnail.
    """
    from scripts.capture_tours_webgl import (
        INJECTED_TOUR_JS,
        build_generative_lydian_score,
        encode_qhd_mp4_from_frames,
        ensure_tour_youtube_json,
        save_wav,
    )

    model_path, cfg, out_dir = resolve_model_and_camera_path(model_html, camera_path, output_dir)
    mode = cfg.get("mode", out_dir.name)
    job_dur = float(duration if duration is not None else cfg.get("duration", 30.0))
    job_fps = int(fps if fps is not None else cfg.get("fps", DEFAULT_FPS))
    total_frames = int(round(job_dur * job_fps))

    frames_dir = out_dir / "frames"
    if clean and frames_dir.exists():
        shutil.rmtree(frames_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    ensure_tour_youtube_json(out_dir, mode, cfg)

    wav_name = cfg.get("wav_name", f"gor9_{mode}_audio.wav")
    mp4_name = cfg.get("mp4_name", f"gor9_{mode}.mp4")
    thumb_name = cfg.get("thumb_name", f"gor9_{mode}_thumb.jpg")
    thumb_frame = int(cfg.get("thumb_frame", max(1, int(total_frames * 0.618))))

    wav_path = Path(audio_wav).resolve() if audio_wav else (out_dir / wav_name)
    mp4_path = out_dir / mp4_name
    thumb_path = out_dir / thumb_name

    if not wav_path.exists() or clean:
        print(f"=== [{mode.upper()}] Synthesizing {job_dur:.2f}s Generative C-Lydian Score -> {wav_path} ===", flush=True)
        score_samples = build_generative_lydian_score(mode=mode, duration=job_dur)
        save_wav(wav_path, score_samples)

    target_indices: list[int] | None = None
    if test_frames_only:
        target_indices = cfg.get("test_frames", [0, int(total_frames * 0.25), int(total_frames * 0.5), int(total_frames * 0.75), total_frames - 1])
        for idx in target_indices:
            (frames_dir / f"frame_{idx + 1:04d}.png").unlink(missing_ok=True)

    all_pairs = (
        [(idx, idx / float(job_fps)) for idx in target_indices]
        if target_indices is not None
        else [(idx, idx / float(job_fps)) for idx in range(total_frames)]
    )

    chrome_bin = find_chrome_binary()
    serve_dir = model_path.parent
    t_start = time.monotonic()

    for pass_num in range(1, 15):
        if repair_torn and pass_num > 1 and not test_frames_only:
            purge_torn_frames(frames_dir, mode=mode, width=width, audit_only=False)

        missing_pairs = [
            (idx, t)
            for idx, t in all_pairs
            if not (frames_dir / f"frame_{idx + 1:04d}.png").exists()
        ]
        if not missing_pairs:
            if repair_torn and not test_frames_only:
                torn = purge_torn_frames(frames_dir, mode=mode, width=width, audit_only=False)
                if torn:
                    continue
            break

        actual_workers = min(workers, len(missing_pairs))
        shards = [missing_pairs[w::actual_workers] for w in range(actual_workers)]

        done_event = threading.Event()
        lock = threading.Lock()
        state: dict[str, Any] = {
            "captured": len(all_pairs) - len(missing_pairs),
            "total_frames": len(all_pairs),
            "done_workers": 0,
            "last_capture_ts": time.monotonic(),
        }
        handler = functools.partial(
            _ModelSequenceHTTPHandler,
            directory=str(serve_dir),
            model_html_path=model_path,
            frames_dir=frames_dir,
            camera_path_cfg=cfg,
            injected_driver_js=INJECTED_TOUR_JS,
            width=width,
            height=height,
            done_event=done_event,
            expected_workers=actual_workers,
            state=state,
            lock=lock,
        )
        server = _ThreadedTCPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]
        srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
        srv_thread.start()

        print(
            f"[{mode} ({model_path.name}) Pass {pass_num}] Capturing {len(missing_pairs)} frames "
            f"(of {len(all_pairs)}) across {actual_workers} WebGL workers on port {port}...",
            flush=True,
        )

        procs = []
        profiles = []
        for w, shard in enumerate(shards):
            tmp_profile = Path(f"/tmp/model_seq_{mode}_{os.getpid()}_{pass_num}_{w}")
            if tmp_profile.exists() and not tmp_profile.is_dir():
                tmp_profile.unlink(missing_ok=True)
            tmp_profile.mkdir(parents=True, exist_ok=True)
            profiles.append(tmp_profile)
            pairs_q = ",".join(f"{idx}:{t:.4f}" for idx, t in shard)
            url = (
                f"http://127.0.0.1:{port}/__capture_model.html"
                f"?mode={mode}&fps={job_fps}&dur={job_dur:.2f}&wid={w}&pairs={pairs_q}"
            )
            cmd = [
                chrome_bin,
                "--headless=new",
                f"--user-data-dir={tmp_profile}",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--use-gl=angle",
                "--use-angle=gl",
                "--enable-gpu-rasterization",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={width},{height + 120}",
                url,
            ]
            procs.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

        try:
            start_ts = time.monotonic()
            while not done_event.wait(timeout=0.5):
                now = time.monotonic()
                if now - start_ts > 600.0:
                    break
                if all(p.poll() is not None for p in procs):
                    break
                with lock:
                    idle_s = now - state.get("last_capture_ts", start_ts)
                    captured_now = state.get("captured", 0)
                if captured_now >= len(all_pairs):
                    break
                if idle_s > 180.0:
                    break
        finally:
            for proc in procs:
                proc.terminate()
            for proc in procs:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            server.shutdown()
            server.server_close()
            for prof in profiles:
                shutil.rmtree(prof, ignore_errors=True)

    torn_after = purge_torn_frames(frames_dir, mode=mode, width=width, audit_only=True) if not test_frames_only else []

    if encode_mp4 and not test_frames_only:
        encode_qhd_mp4_from_frames(
            frames_dir=frames_dir,
            audio_wav=wav_path,
            out_mp4=mp4_path,
            out_thumb=thumb_path,
            thumb_frame_idx=thumb_frame,
            duration=job_dur,
            fps=job_fps,
        )

    elapsed = round(time.monotonic() - t_start, 2)
    return {
        "ok": len(torn_after) == 0,
        "model_html": str(model_path),
        "mode": mode,
        "output_dir": str(out_dir),
        "frames_dir": str(frames_dir),
        "mp4_path": str(mp4_path) if (encode_mp4 and not test_frames_only) else None,
        "thumb_path": str(thumb_path) if (encode_mp4 and not test_frames_only) else None,
        "wav_path": str(wav_path),
        "width": width,
        "height": height,
        "fps": job_fps,
        "duration": job_dur,
        "frames_rendered": len(all_pairs),
        "torn_frames_remaining": len(torn_after),
        "elapsed_sec": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal 3D WebGL Model + Camera Path/Sequence Recorder (2560x1440 QHD @ 30fps CFR)."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to the 3D HTML model file (e.g., docs/tower-3d.html, docs/dilithium-reactor-3d.html). Defaults to `model` in camera_path.json.",
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to camera_path.json (or project folder containing camera_path.json).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Optional output directory (defaults to the camera_path.json folder).",
    )
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel WebGL workers (default: 2).")
    parser.add_argument("--clean", action="store_true", help="Clean existing frames before rendering.")
    parser.add_argument("--test-frames", action="store_true", help="Render only diagnostic test_frames from camera_path.json.")
    parser.add_argument("--no-encode", action="store_true", help="Skip MP4 encoding after frame capture.")
    args = parser.parse_args()

    res = record_model_sequence(
        model_html=args.model,
        camera_path=args.path,
        output_dir=args.out,
        workers=args.workers,
        clean=args.clean,
        test_frames_only=args.test_frames,
        encode_mp4=not args.no_encode,
    )
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
