#!/usr/bin/env python3
"""Compile `videos/mk4_demo/script.scr`, synthesize audio, capture 30fps 2560x1440 frames, and assemble MP4.

Follows the GOR-9 3D capture workflow:
1. Parses `videos/mk4_demo/script.scr` (`=== <section> ===`, `[bell:...]`, `[screen: ...]`, and `say:` lines).
2. Synthesizes narration via Argon III-C (`speak.py` + `.tts_cache/`) and mixes hardware/station SFX + C-Lydian pad
   into `videos/mk4_demo/gor9_mk4_demo_audio.wav` and `videos/mk4_demo/timeline.json`.
3. Launches parallel headless Chromium workers at `--window-size=1920,1080 --force-device-scale-factor=1.3333333333`
   (producing exact `2560x1440` QHD frames with 4/3 typography scaling), stepping the live Hauser MK-IV console
   (`docs/index.html`) deterministically at 30.00 fps via CDP (`window.__mk4StepAtTime(t, idx)` + `Page.captureScreenshot`)
   into `videos/mk4_demo/frames/frame_0001.png` .. `frame_NNNN.png`.
4. Assembles `frames/frame_%04d.png` + `gor9_mk4_demo_audio.wav` into `videos/mk4_demo/gor9_mk4_demo.mp4`
   and exports `gor9_mk4_demo_thumb.jpg` + `youtube.json`.
"""

from __future__ import annotations

import argparse
import base64
import functools
import hashlib
import http.server
import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import socketserver
import struct
import subprocess
import sys
import threading
import time
import urllib.request
import wave

import numpy as np

# Import Studio speak engine
sys.path.insert(0, "/home/phi/PROJECTS/photon-platform/studio/src/photon_platform/studio/engines")
import speak  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / "videos" / "mk4_demo"
SCRIPT_SCR = OUT_DIR / "script.scr"
FRAMES_DIR = OUT_DIR / "frames"
CLIP_CACHE_DIR = DOCS_DIR / "assets" / "clips" / "_mk4_demo_frames"

SAMPLE_RATE = 24000
FPS = 30
TARGET_W = 2560
TARGET_H = 1440
CSS_W = 1920
CSS_H = 1080
SCALE_FACTOR = 4.0 / 3.0  # 1.3333333333333333 -> 1920x1080 * 4/3 = 2560x1440


def ensure_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        env_file = Path("/home/phi/.photon/.env")
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip().removeprefix("export ").strip()
                if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip("'\"")
                    os.environ["GEMINI_API_KEY"] = api_key
                    break
    if not api_key:
        raise RuntimeError("Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set in environment or ~/.photon/.env")
    return api_key


def parse_mk4_script_scr(script_path: Path) -> tuple[dict[str, str], list[dict]]:
    """Parse `videos/mk4_demo/script.scr` into metadata and a flat list of screen step dicts."""
    text = script_path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    steps: list[dict] = []
    cur_section = "intro"
    cur_bell: str | None = None
    cur_screen: dict | None = None

    def flush_screen() -> None:
        nonlocal cur_screen
        if cur_screen is not None:
            steps.append(cur_screen)
            cur_screen = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        m_sec = re.match(r"^===+\s*(.+?)\s*===+$", line)
        if m_sec:
            flush_screen()
            cur_section = m_sec.group(1).strip()
            cur_bell = None
            continue

        m_bell = re.match(r"^\[(bell:[^\]]+)\]$", line, flags=re.I)
        if m_bell:
            cur_bell = m_bell.group(1).lower()
            if cur_screen is not None and not cur_screen.get("say"):
                cur_screen["bell"] = cur_bell
            continue

        if line.lower().startswith("[style:"):
            continue

        m_scr = re.match(r"^\[screen:\s*(.+)\]$", line, flags=re.I)
        if m_scr:
            flush_screen()
            parts = [p.strip() for p in m_scr.group(1).split("|") if p.strip()]
            step_kind = parts[0] if parts else "STEP"
            attrs: dict[str, str] = {}
            for p in parts[1:]:
                if ":" in p:
                    k, v = p.split(":", 1)
                    attrs[k.strip().lower()] = v.strip()
            cur_screen = {
                "step_index": len(steps),
                "section": cur_section,
                "bell": cur_bell,
                "step_kind": step_kind,
                "target": attrs.get("target", ""),
                "punchline": attrs.get("punchline", "").lower() in ("true", "1", "yes"),
                "active": "",
                "preset": "radio-corrugated",
                "mode": "AM-W",
                "filter": "6000",
                "viewport": "video",
                "alg": "ALG-03",
                "action": "",
                "symbolic": "",
                "clause": "",
                "just": "",
                "say": "",
            }
            cur_bell = None
            continue

        if cur_screen is None and not steps:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
            continue

        if cur_screen is not None and ":" in line:
            k, v = line.split(":", 1)
            k_low = k.strip().lower()
            v_str = v.strip()
            if k_low in cur_screen:
                cur_screen[k_low] = v_str

    flush_screen()
    return meta, steps


def load_wav_float(path: Path) -> np.ndarray:
    if not path.exists():
        return np.zeros(0, dtype=np.float64)
    raw = subprocess.check_output(
        ["/usr/bin/ffmpeg", "-v", "quiet", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"]
    )
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32767.0


def save_wav_float(path: Path, arr: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(arr * 32767.0, -32767.0, 32767.0).astype(np.int16).tobytes()
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm)


def make_switch_click(freq: float = 1350.0, dur: float = 0.045, amp: float = 0.16) -> np.ndarray:
    n = int(SAMPLE_RATE * dur)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    env = np.exp(-t / 0.009)
    sig = (
        0.65 * np.sin(2.0 * math.pi * freq * t)
        + 0.35 * np.sin(2.0 * math.pi * (freq * 2.15) * t)
    ) * env * amp
    return sig


def make_vernier_tick_train(dur: float = 1.6, rate_hz: float = 14.0, amp: float = 0.09) -> np.ndarray:
    n = int(SAMPLE_RATE * dur)
    out = np.zeros(n, dtype=np.float64)
    step = int(SAMPLE_RATE / rate_hz)
    tick = make_switch_click(freq=1820.0, dur=0.018, amp=amp)
    for i in range(0, n - len(tick), step):
        out[i : i + len(tick)] += tick
    return out


def add_at(buf: np.ndarray, clip: np.ndarray, start_sec: float, gain: float = 1.0) -> None:
    i0 = int(round(start_sec * SAMPLE_RATE))
    if i0 < 0 or i0 >= len(buf) or len(clip) == 0:
        return
    d = min(len(clip), len(buf) - i0)
    buf[i0 : i0 + d] += clip[:d] * gain


def build_audio_and_timeline(force_tts: bool = False) -> dict:
    """Synthesize narration from `script.scr`, mix console SFX & ambient pad, and write `timeline.json`."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta, steps = parse_mk4_script_scr(SCRIPT_SCR)

    voice_wav = OUT_DIR / "gor9_mk4_demo_voice.wav"
    voice_json = OUT_DIR / "gor9_mk4_demo_voice.json"
    master_wav = OUT_DIR / "gor9_mk4_demo_audio.wav"
    timeline_path = OUT_DIR / "timeline.json"

    if force_tts or not voice_wav.exists() or not voice_json.exists():
        ensure_api_key()
        print("Synthesizing narration from videos/mk4_demo/script.scr via speak.py...", flush=True)
        speak.synthesize_script(SCRIPT_SCR.read_text(encoding="utf-8"), voice_wav)

    manifest = json.loads(voice_json.read_text(encoding="utf-8"))
    flat_subs: list[dict] = []
    for seg in manifest.get("segments", []):
        for sub in seg.get("subsegments", []):
            flat_subs.append(sub)

    if len(flat_subs) != len(steps):
        raise RuntimeError(f"Mismatch between script.scr steps ({len(steps)}) and synthesized subsegments ({len(flat_subs)})")

    for st, sub in zip(steps, flat_subs):
        st["start_sec"] = float(sub["start_sec"])
        st["end_sec"] = float(sub["end_sec"])
        st["duration_sec"] = float(sub["duration_sec"])
        st["caption"] = sub["text"]

    # Add a 1.25s tail after the final spoken line so the closing C-Lydian chord rings out cleanly
    voice_flt = load_wav_float(voice_wav)
    tail_sec = 1.25
    total_dur = round(len(voice_flt) / SAMPLE_RATE + tail_sec, 3)
    steps[-1]["end_sec"] = total_dur
    steps[-1]["duration_sec"] = round(steps[-1]["end_sec"] - steps[-1]["start_sec"], 3)

    n_total = int(round(total_dur * SAMPLE_RATE))
    mix = np.zeros(n_total, dtype=np.float64)
    mix[: len(voice_flt)] += voice_flt

    # 1. Subtle C-Lydian broadcast watchroom ambient pad (C3 + G3 + D4 + F#4)
    tt = np.arange(n_total, dtype=np.float64) / SAMPLE_RATE
    pad = (
        0.40 * np.sin(2.0 * math.pi * 130.81 * tt)
        + 0.30 * np.sin(2.0 * math.pi * 196.00 * tt)
        + 0.20 * np.sin(2.0 * math.pi * 293.66 * tt)
        + 0.10 * np.sin(2.0 * math.pi * 369.99 * tt)
    ) * (0.65 + 0.35 * np.sin(2.0 * math.pi * 0.14 * tt))
    fade_in = np.minimum(1.0, tt / 1.0)
    fade_out = np.minimum(1.0, (total_dur - tt) / 1.2)
    mix += pad * fade_in * fade_out * 0.028

    # 2. Layer interactive hardware clicks, vernier wheel ticks, and station audio vignettes per step
    step_by_kind = {s["step_kind"]: s for s in steps}

    # Add subtle hardware sub-beat clicks across all overview & operational steps
    for s in steps:
        for frac, f_hz in ((0.04, 1340.0), (0.38, 1480.0), (0.72, 1620.0)):
            add_at(mix, make_switch_click(freq=f_hz, dur=0.04, amp=0.13), s["start_sec"] + s["duration_sec"] * frac)

    # S06_TUNER_PRESETS_BANDS: rapid band-switch clicks
    if "S06_TUNER_PRESETS_BANDS" in step_by_kind:
        s = step_by_kind["S06_TUNER_PRESETS_BANDS"]
        for frac, f_hz in ((0.18, 1280.0), (0.36, 1420.0), (0.54, 1560.0), (0.72, 1680.0), (0.88, 1820.0)):
            add_at(mix, make_switch_click(freq=f_hz, dur=0.045, amp=0.17), s["start_sec"] + s["duration_sec"] * frac)

    # S07_TUNER_DIAL_VERNIER: vernier wheel rotary ticks + filter crystal clicks
    if "S07_TUNER_DIAL_VERNIER" in step_by_kind:
        s = step_by_kind["S07_TUNER_DIAL_VERNIER"]
        add_at(mix, make_vernier_tick_train(dur=min(2.6, s["duration_sec"] * 0.55), rate_hz=16.0, amp=0.085), s["start_sec"] + s["duration_sec"] * 0.12)

    # S10_CORRELATOR_VIDEO_EXPAND & S13_CORRELATOR_CIPHER_EXPAND_AUDIO: station audio snippets
    rc_intercept = load_wav_float(DOCS_DIR / "assets" / "audio" / "intercept_radio_corrugated.wav")
    rc_is = load_wav_float(DOCS_DIR / "assets" / "audio" / "is_radio_corrugated.wav")
    if "S10_CORRELATOR_VIDEO_EXPAND" in step_by_kind and len(rc_intercept) > 0:
        s = step_by_kind["S10_CORRELATOR_VIDEO_EXPAND"]
        clip_len = min(len(rc_intercept), int((s["duration_sec"] - 0.5) * SAMPLE_RATE))
        if clip_len > 0:
            add_at(mix, rc_intercept[:clip_len], s["start_sec"] + 0.3, gain=0.12)

    if "S13_CORRELATOR_CIPHER_EXPAND_AUDIO" in step_by_kind:
        s = step_by_kind["S13_CORRELATOR_CIPHER_EXPAND_AUDIO"]
        if len(rc_intercept) > 0:
            c1 = rc_intercept[: int(min(2.2, s["duration_sec"] * 0.28) * SAMPLE_RATE)]
            add_at(mix, c1, s["start_sec"] + s["duration_sec"] * 0.42, gain=0.20)
        if len(rc_is) > 0:
            c2 = rc_is[: int(min(2.2, s["duration_sec"] * 0.26) * SAMPLE_RATE)]
            add_at(mix, c2, s["start_sec"] + s["duration_sec"] * 0.72, gain=0.20)

    # S16_EQSL_SSTV_WIPE: SSTV Robot-24 burst chirp during scanline wipe
    rc_sstv = load_wav_float(DOCS_DIR / "assets" / "audio" / "sstv_radio_corrugated.wav")
    if "S16_EQSL_SSTV_WIPE" in step_by_kind and len(rc_sstv) > 0:
        s = step_by_kind["S16_EQSL_SSTV_WIPE"]
        c_sstv = rc_sstv[: int(min(3.2, s["duration_sec"] * 0.65) * SAMPLE_RATE)]
        add_at(mix, c_sstv, s["start_sec"] + s["duration_sec"] * 0.22, gain=0.13)

    # Closing C-Lydian resolution chord at the end of S20_RECAP_SIGNOFF
    chord_start = max(0.0, total_dur - 2.4)
    n_c = int((total_dur - chord_start) * SAMPLE_RATE)
    tc = np.arange(n_c, dtype=np.float64) / SAMPLE_RATE
    env_c = (1.0 - np.exp(-tc / 0.02)) * np.exp(-tc / 0.95)
    chord = (
        0.32 * np.sin(2.0 * math.pi * 261.63 * tc)
        + 0.26 * np.sin(2.0 * math.pi * 392.00 * tc)
        + 0.20 * np.sin(2.0 * math.pi * 587.33 * tc)
        + 0.14 * np.sin(2.0 * math.pi * 739.99 * tc)
        + 0.08 * np.sin(2.0 * math.pi * 987.77 * tc)
    ) * env_c * 0.18
    add_at(mix, chord, chord_start)

    save_wav_float(master_wav, np.clip(mix, -0.96, 0.96))

    # Write synchronized .srt captions
    srt_lines = []
    for idx_s, st in enumerate(steps, 1):
        def _fmt_srt(sec: float) -> str:
            ms = int(round((sec % 1.0) * 1000))
            s_i = int(sec) % 60
            m_i = (int(sec) // 60) % 60
            h_i = int(sec) // 3600
            return f"{h_i:02d}:{m_i:02d}:{s_i:02d},{ms:03d}"
        clean_cap = re.sub(r"\[sfx:[^\]]+\]\s*", "", st.get("caption", "")).strip()
        srt_lines.append(f"{idx_s}\n{_fmt_srt(st['start_sec'])} --> {_fmt_srt(st['end_sec'])}\n{clean_cap}\n")
    (OUT_DIR / "gor9_mk4_demo.srt").write_text("\n".join(srt_lines), encoding="utf-8")

    timeline_doc = {
        "console": meta.get("console", "HAUSER MK-IV"),
        "title": meta.get("title", ""),
        "g_id": meta.get("g_id", "2736.305"),
        "folio": meta.get("folio", ""),
        "enunciation": meta.get("enunciation", ""),
        "url": meta.get("url", "docs/index.html"),
        "next": meta.get("next", ""),
        "fps": FPS,
        "width": TARGET_W,
        "height": TARGET_H,
        "css_viewport": [CSS_W, CSS_H],
        "scale_factor": SCALE_FACTOR,
        "total_duration_sec": total_dur,
        "total_frames": int(round(total_dur * FPS)),
        "steps": steps,
    }
    timeline_path.write_text(json.dumps(timeline_doc, indent=2) + "\n", encoding="utf-8")
    print(
        f"Master Audio & Timeline ready: {master_wav.name} ({total_dur:.2f}s, {timeline_doc['total_frames']} frames @ {FPS}fps)",
        flush=True,
    )
    return timeline_doc


def prepare_station_video_frames() -> int:
    """Extract 30fps JPEG frames from `docs/assets/clips/radio_corrugated_blowtorch.mp4` for deterministic canvas playback."""
    CLIP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(CLIP_CACHE_DIR.glob("frame_*.jpg"))
    if len(existing) >= 60:
        return len(existing)
    src_mp4 = DOCS_DIR / "assets" / "clips" / "radio_corrugated_blowtorch.mp4"
    if not src_mp4.exists():
        return 0
    cmd = [
        "/usr/bin/ffmpeg",
        "-y",
        "-v",
        "quiet",
        "-i",
        str(src_mp4),
        "-vf",
        "fps=30,scale=640:360",
        "-q:v",
        "3",
        str(CLIP_CACHE_DIR / "frame_%04d.jpg"),
    ]
    subprocess.run(cmd, check=True)
    extracted = sorted(CLIP_CACHE_DIR.glob("frame_*.jpg"))
    print(f"Pre-extracted {len(extracted)} deterministic video frames -> {CLIP_CACHE_DIR}", flush=True)
    return len(extracted)


INJECTED_MK4_DEMO_JS = r"""
<style>
  /* Disable asynchronous CSS transitions during deterministic frame stepping so we control interpolation exactly */
  .vfo-wheel, .wf-cursor-line, .wf-passband, #sstv-wipe-curtain, .smeter-seg {
    transition: none !important;
  }

  /* Active Component Focus Bracket & Step Badge Overlay */
  #mk4-demo-focus-box {
    position: fixed;
    pointer-events: none;
    z-index: 9990;
    border: 2px solid rgba(240, 184, 73, 0.92);
    border-radius: 6px;
    box-shadow: 0 0 22px rgba(240, 184, 73, 0.35), inset 0 0 14px rgba(240, 184, 73, 0.12);
    display: none;
  }
  #mk4-demo-focus-box::before,
  #mk4-demo-focus-box::after {
    content: '';
    position: absolute;
    width: 18px;
    height: 18px;
    border-color: #38bdf8;
    border-style: solid;
  }
  #mk4-demo-focus-box::before {
    top: -4px;
    left: -4px;
    border-width: 3px 0 0 3px;
    border-top-left-radius: 4px;
  }
  #mk4-demo-focus-box::after {
    bottom: -4px;
    right: -4px;
    border-width: 0 3px 3px 0;
    border-bottom-right-radius: 4px;
  }

  #mk4-demo-step-pill {
    position: absolute;
    top: -28px;
    right: 6px;
    background: rgba(6, 10, 18, 0.94);
    border: 1.5px solid #f0b849;
    color: #f0b849;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border-radius: 3px;
    white-space: nowrap;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.85);
  }

  /* Simulated Operator Cursor & Click Ripple */
  #mk4-demo-cursor {
    position: fixed;
    width: 22px;
    height: 22px;
    margin-left: -11px;
    margin-top: -11px;
    border: 2px solid #38bdf8;
    background: rgba(56, 189, 248, 0.22);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9995;
    display: none;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.8);
  }
  #mk4-demo-cursor::after {
    content: '';
    position: absolute;
    left: 50%;
    top: 50%;
    width: 6px;
    height: 6px;
    margin-left: -3px;
    margin-top: -3px;
    background: #f0b849;
    border-radius: 50%;
  }
  #mk4-demo-ripple {
    position: fixed;
    width: 44px;
    height: 44px;
    margin-left: -22px;
    margin-top: -22px;
    border: 2.5px solid #f0b849;
    border-radius: 50%;
    pointer-events: none;
    z-index: 9994;
    display: none;
  }
</style>
<script>
(() => {
  const TIMELINE = __TIMELINE_JSON_PLACEHOLDER__;
  const CLIP_FRAME_COUNT = __CLIP_FRAME_COUNT_PLACEHOLDER__;

  window.__mk4Ready = false;

  // Deterministic PRNG for noise traces so parallel workers render identical waveforms at frame idx
  function mulberry32(a) {
    return function() {
      let t = a += 0x6D2B79F5;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function smoothstep(edge0, edge1, x) {
    const t = Math.max(0, Math.min(1, (x - edge0) / Math.max(1e-6, edge1 - edge0)));
    return t * t * (3 - 2 * t);
  }

  function lerp(a, b, u) {
    return a + (b - a) * u;
  }

  let videoCanvas = null;
  let videoCtx = null;
  const clipImgCache = new Map();
  let qslImgLoaded = false;

  async function preloadClipFrame(frameNum) {
    if (CLIP_FRAME_COUNT <= 0) return null;
    const clamped = ((frameNum - 1) % CLIP_FRAME_COUNT + CLIP_FRAME_COUNT) % CLIP_FRAME_COUNT + 1;
    if (clipImgCache.has(clamped)) return clipImgCache.get(clamped);
    const numStr = String(clamped).padStart(4, '0');
    const url = `assets/clips/_mk4_demo_frames/frame_${numStr}.jpg`;
    const img = new Image();
    const p = new Promise((resolve) => {
      img.onload = () => resolve(img);
      img.onerror = () => resolve(null);
    });
    img.src = url;
    const loaded = await p;
    if (loaded) {
      if (clipImgCache.size > 45) {
        const firstKey = clipImgCache.keys().next().value;
        clipImgCache.delete(firstKey);
      }
      clipImgCache.set(clamped, loaded);
    }
    return loaded;
  }

  function ensureOverlays() {
    if (!document.getElementById('mk4-demo-focus-box')) {
      const fb = document.createElement('div');
      fb.id = 'mk4-demo-focus-box';
      const pill = document.createElement('div');
      pill.id = 'mk4-demo-step-pill';
      fb.appendChild(pill);
      document.body.appendChild(fb);
    }
    if (!document.getElementById('mk4-demo-cursor')) {
      const cur = document.createElement('div');
      cur.id = 'mk4-demo-cursor';
      document.body.appendChild(cur);
    }
    if (!document.getElementById('mk4-demo-ripple')) {
      const rip = document.createElement('div');
      rip.id = 'mk4-demo-ripple';
      document.body.appendChild(rip);
    }
    const vidEl = document.getElementById('station-video');
    if (vidEl && !videoCanvas) {
      vidEl.pause();
      vidEl.style.display = 'none';
      videoCanvas = document.createElement('canvas');
      videoCanvas.id = 'station-video-canvas';
      videoCanvas.width = 640;
      videoCanvas.height = 360;
      videoCanvas.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;';
      vidEl.parentNode.insertBefore(videoCanvas, vidEl);
      videoCtx = videoCanvas.getContext('2d');
    }
  }

  // Deterministic Waterfall & Multi-Mode Frequency Map Renderer at time tSec
  function renderDeterministicWaterfall(tSec, cursorPct, bwPx, activeIdx) {
    const canvas = document.getElementById('waterfall-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const specH = 50;
    const wfY = specH + 2;
    const wfH = H - wfY;

    const showOverlay = (currentWfMode === 'waterfall' || currentWfMode === 'bandplan');
    const curEl = document.getElementById('wf-cursor');
    const pbEl = document.getElementById('wf-passband');
    if (curEl) {
      curEl.style.display = showOverlay ? 'block' : 'none';
      curEl.style.left = `${cursorPct.toFixed(2)}%`;
    }
    if (pbEl) {
      pbEl.style.display = showOverlay ? 'block' : 'none';
      pbEl.style.left = `${cursorPct.toFixed(2)}%`;
      pbEl.style.width = `${bwPx.toFixed(1)}px`;
      pbEl.style.marginLeft = `${(-bwPx / 2).toFixed(1)}px`;
    }

    if (typeof drawFrequencyMapExtraModes === 'function' && drawFrequencyMapExtraModes(ctx, W, H, tSec * 1.35, activeIdx)) {
      return;
    }

    ctx.fillStyle = '#04070d';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(43, 56, 78, 0.35)';
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 92) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, specH); ctx.stroke();
    }
    ctx.beginPath(); ctx.moveTo(0, specH / 2); ctx.lineTo(W, specH / 2); ctx.stroke();

    const baseRow = Math.floor(tSec * 30);
    const rngTop = mulberry32(10000 + baseRow);

    ctx.beginPath();
    ctx.moveTo(0, specH);
    const tWave = baseRow * 0.04;
    for (let x = 0; x < W; x++) {
      let val = 0.12 + 0.08 * rngTop() + 0.04 * Math.sin(x * 0.07 + tWave);
      for (let k = 0; k < 6; k++) {
        const cx = (0.14 + k * 0.144) * W;
        const dist = Math.abs(x - cx);
        const bw = k === activeIdx ? 16 : 8;
        if (dist < bw * 2.5) {
          const boost = k === activeIdx ? 0.72 + 0.15 * Math.sin(tWave * 5.0) : 0.38;
          val += boost * Math.exp(-(dist * dist) / (2 * bw * bw));
        }
      }
      val = Math.min(0.98, Math.max(0.05, val));
      const py = specH - val * (specH - 6);
      ctx.lineTo(x, py);
    }
    ctx.lineTo(W, specH);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, 0, 0, specH);
    grad.addColorStop(0, 'rgba(240, 184, 73, 0.55)');
    grad.addColorStop(1, 'rgba(56, 189, 248, 0.05)');
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = '#f0b849';
    ctx.lineWidth = 1.4;
    ctx.stroke();

    // Draw wfH historical rows deterministically
    const imgData = ctx.createImageData(W, wfH);
    const data = imgData.data;
    for (let ry = 0; ry < wfH; ry++) {
      const rowTick = baseRow - ry;
      const rWave = rowTick * 0.04;
      const rngRow = mulberry32(50000 + rowTick * 31);
      const rowOff = ry * W * 4;
      for (let x = 0; x < W; x += 2) {
        let val = 0.12 + 0.08 * rngRow() + 0.04 * Math.sin(x * 0.07 + rWave);
        for (let k = 0; k < 6; k++) {
          const cx = (0.14 + k * 0.144) * W;
          const dist = Math.abs(x - cx);
          const bw = k === activeIdx ? 16 : 8;
          if (dist < bw * 2.5) {
            const boost = k === activeIdx ? 0.72 + 0.15 * Math.sin(rWave * 5.0) : 0.38;
            val += boost * Math.exp(-(dist * dist) / (2 * bw * bw));
          }
        }
        val = Math.min(0.98, Math.max(0.05, val));
        const r = val > 0.65 ? 245 : val > 0.35 ? Math.floor(val * 320) : 12;
        const g = val > 0.65 ? Math.floor(190 + (val - 0.65) * 180) : val > 0.25 ? Math.floor(val * 240) : Math.floor(val * 90);
        const b = val > 0.5 ? Math.floor((val - 0.5) * 300) : Math.floor(40 + val * 190);
        const i0 = rowOff + x * 4;
        data[i0] = r; data[i0 + 1] = g; data[i0 + 2] = b; data[i0 + 3] = 255;
        if (x + 1 < W) {
          data[i0 + 4] = r; data[i0 + 5] = g; data[i0 + 6] = b; data[i0 + 7] = 255;
        }
      }
    }
    ctx.putImageData(imgData, 0, wfY);
  }

  // Deterministic Panel Spectrum & Lissajous Scope Renderer
  function renderDeterministicPanelSpectrum(frameIdx) {
    const canvas = document.getElementById('panel-spectrum-canvas');
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      const tw = Math.round(rect.width);
      const th = Math.round(rect.height);
      if (canvas.width !== tw || canvas.height !== th) {
        canvas.width = tw;
        canvas.height = th;
      }
    }
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const p = currentStation;
    const rng = mulberry32(90000 + frameIdx * 17);

    ctx.fillStyle = '#02050a';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(38, 56, 84, 0.38)';
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 64) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += 38) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }

    if (p && p.decoder) {
      const style = p.decoder.spectrum_style;
      const specW = W - 155;

      ctx.fillStyle = 'rgba(56, 189, 248, 0.06)';
      ctx.fillRect(specW * 0.28, 12, specW * 0.44, H - 24);
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
      ctx.strokeRect(specW * 0.28, 12, specW * 0.44, H - 24);

      ctx.beginPath();
      for (let x = 6; x < specW - 6; x += 3) {
        const u = x / specW;
        let amp = 0.12 + rng() * 0.08;
        if (style === 'cw_narrow') {
          const bend = Math.sin(frameIdx * 0.05) > 0.6 ? -0.045 : 0;
          const d = Math.abs(u - (0.5 + bend));
          const keyOn = (Math.floor(frameIdx / 8) % 3 !== 0) ? 1.0 : 0.25;
          amp += Math.exp(-d * d * 1800) * 0.78 * keyOn;
          amp += Math.exp(-Math.pow(u - 0.62, 2) * 900) * 0.32;
        } else if (style === 'hi_maser') {
          const d = Math.abs(u - 0.44);
          amp += Math.exp(-d * d * 2800) * 0.84;
          amp += Math.exp(-Math.pow(u - 0.56, 2) * 1600) * 0.42;
        } else if (style === 'octal_fsk') {
          const activeTone = (Math.floor(frameIdx / 12) % 8) * 0.035 + 0.36;
          amp += Math.exp(-Math.pow(u - activeTone, 2) * 2200) * 0.82;
          amp += Math.exp(-Math.pow(u - 0.25, 2) * 1900) * 0.48;
        } else {
          const d = Math.abs(u - 0.5);
          amp += Math.exp(-d * d * 1800) * 0.75 + Math.exp(-d * d * 95) * 0.38;
        }
        const py = H - 14 - Math.min(0.92, amp) * (H - 32);
        if (x === 6) ctx.moveTo(x, py);
        else ctx.lineTo(x, py);
      }
      ctx.strokeStyle = '#4ade80';
      ctx.lineWidth = 1.8;
      ctx.stroke();

      ctx.lineTo(specW - 6, H - 14);
      ctx.lineTo(6, H - 14);
      ctx.closePath();
      ctx.fillStyle = 'rgba(74, 222, 128, 0.12)';
      ctx.fill();

      ctx.font = 'bold 10px monospace';
      ctx.fillStyle = '#38bdf8';
      ctx.fillText(`SPECTRUM SCAN: ${p.decoder.signal_type}`, 12, 18);
      ctx.fillStyle = '#f0b849';
      ctx.fillText(`FC: ${formatFreq(p.rf.measured_khz)} (Δf ${p.rf.doppler_hz} Hz)`, 12, H - 4);

      const lx = specW + 8;
      const ly = 10;
      const lw = W - lx - 8;
      const lh = H - 20;
      const lcx = lx + lw / 2;
      const lcy = ly + lh / 2;
      const lr = Math.min(lw, lh) * 0.36;

      ctx.fillStyle = '#040811';
      ctx.fillRect(lx, ly, lw, lh);
      ctx.strokeStyle = '#263854';
      ctx.strokeRect(lx, ly, lw, lh);

      ctx.beginPath();
      ctx.arc(lcx, lcy, lr, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.22)';
      ctx.stroke();

      ctx.beginPath();
      for (let t = 0; t < Math.PI * 2; t += 0.06) {
        let px, py;
        if (style === 'hi_maser') {
          px = lcx + Math.sin(3 * t + frameIdx * 0.05) * lr;
          py = lcy + Math.sin(5 * t) * lr;
        } else if (style === 'octal_fsk') {
          px = lcx + Math.cos(t * 4 + frameIdx * 0.04) * lr * Math.cos(t);
          py = lcy + Math.sin(t * 4 + frameIdx * 0.04) * lr * Math.cos(t);
        } else {
          px = lcx + Math.sin(t + frameIdx * 0.06) * lr;
          py = lcy + Math.sin(2 * t + 0.6) * lr * 0.85;
        }
        if (t === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.strokeStyle = '#f0b849';
      ctx.lineWidth = 1.4;
      ctx.stroke();

      ctx.fillStyle = '#8b9bb4';
      ctx.font = 'bold 8.5px monospace';
      ctx.fillText('PHASE / LISSAJOUS', lx + 8, ly + 12);

      const morseStr = p.decoder.morse_stream + '   •   ';
      const mOff = Math.floor(frameIdx / 5) % morseStr.length;
      const rotated = morseStr.slice(mOff) + morseStr.slice(0, mOff);
      const tickerEl = document.getElementById('cw-morse-ticker');
      if (tickerEl) tickerEl.textContent = rotated;
      const ch = rotated[0];
      const ledEl = document.getElementById('cw-key-led');
      if (ledEl) ledEl.classList.toggle('on', ch === '.' || ch === '-' || ch === '•' || ch === '—');
    }
  }

  // Deterministic Audio Envelope Scope
  function renderDeterministicScope(frameIdx, isPlayingAudio) {
    const canvas = document.getElementById('scope-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const phase = 0.6 + frameIdx * 0.08;
    const rng = mulberry32(70000 + frameIdx * 13);

    ctx.fillStyle = '#030508';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = 'rgba(30, 42, 63, 0.6)';
    ctx.beginPath();
    ctx.moveTo(0, H / 2);
    ctx.lineTo(W, H / 2);
    ctx.stroke();

    ctx.beginPath();
    ctx.strokeStyle = isPlayingAudio ? '#4ade80' : '#38bdf8';
    ctx.lineWidth = isPlayingAudio ? 2.2 : 1.7;

    const env = isPlayingAudio ? 19.5 : 8.5;
    for (let x = 0; x < W; x++) {
      const mod = isPlayingAudio
        ? (Math.sin(x * 0.09 + phase * 3.1) * 0.65 + Math.sin(x * 0.032 - phase * 1.8) * 0.35)
        : (Math.sin(x * 0.06 + phase * 2.2) * Math.cos(x * 0.015 - phase));
      const y = H / 2 + mod * env + (rng() - 0.5) * (isPlayingAudio ? 5.0 : 2.5);
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  function updateFocusAndCursor(targetSel, labelText, cursorTargetSel, clickPulse, tSec) {
    const fb = document.getElementById('mk4-demo-focus-box');
    const pill = document.getElementById('mk4-demo-step-pill');
    const cur = document.getElementById('mk4-demo-cursor');
    const rip = document.getElementById('mk4-demo-ripple');

    if (targetSel) {
      const el = document.querySelector(targetSel);
      if (el) {
        const r = el.getBoundingClientRect();
        if (r.width > 10 && r.height > 10) {
          fb.style.display = 'block';
          const pad = targetSel === '.gor9-console-frame' ? -2 : 4;
          fb.style.left = `${Math.round(r.left - pad)}px`;
          fb.style.top = `${Math.round(r.top - pad)}px`;
          fb.style.width = `${Math.round(r.width + pad * 2)}px`;
          fb.style.height = `${Math.round(r.height + pad * 2)}px`;
          const pulse = 0.72 + 0.28 * Math.sin(tSec * 6.5);
          fb.style.borderColor = `rgba(240, 184, 73, ${pulse.toFixed(2)})`;
          if (pill) {
            pill.textContent = labelText || '';
            pill.style.display = labelText ? 'block' : 'none';
            pill.style.top = (r.top < 42) ? '8px' : '-28px';
            if (targetSel === '#galaxy-modal .modal-card') {
              pill.style.display = 'none';
            } else if (targetSel.includes('modal-card')) {
              pill.style.right = '415px';
              pill.style.left = 'auto';
            } else if (r.left < 450 && r.width < 900) {
              pill.style.left = '6px';
              pill.style.right = 'auto';
            } else {
              pill.style.right = '6px';
              pill.style.left = 'auto';
            }
          }
        } else {
          fb.style.display = 'none';
        }
      } else {
        fb.style.display = 'none';
      }
    } else {
      fb.style.display = 'none';
    }

    if (cursorTargetSel) {
      const cel = document.querySelector(cursorTargetSel);
      if (cel) {
        const cr = cel.getBoundingClientRect();
        if (cr.width > 0 && cr.height > 0) {
          const cx = cr.left + cr.width * 0.5;
          const cy = cr.top + cr.height * 0.5;
          cur.style.display = 'block';
          cur.style.left = `${cx.toFixed(1)}px`;
          cur.style.top = `${cy.toFixed(1)}px`;
          if (clickPulse > 0.01) {
            rip.style.display = 'block';
            rip.style.left = `${cx.toFixed(1)}px`;
            rip.style.top = `${cy.toFixed(1)}px`;
            const scale = 0.6 + clickPulse * 1.4;
            rip.style.transform = `scale(${scale.toFixed(2)})`;
            rip.style.opacity = `${(1.0 - clickPulse).toFixed(2)}`;
          } else {
            rip.style.display = 'none';
          }
          return;
        }
      }
    }
    cur.style.display = 'none';
    rip.style.display = 'none';
  }

  window.__mk4StepAtTime = async function(tSec, frameIdx) {
    ensureOverlays();

    const steps = TIMELINE.steps;
    let step = steps[steps.length - 1];
    for (let i = 0; i < steps.length; i++) {
      if (tSec >= steps[i].start_sec && tSec <= steps[i].end_sec + 0.001) {
        step = steps[i];
        break;
      }
    }

    const u = Math.max(0.0, Math.min(1.0, (tSec - step.start_sec) / Math.max(0.01, step.duration_sec)));
    const sk = step.step_kind;

    // Reset all modals & audio buttons at start of frame evaluation
    toggleTunerModal(false);
    toggleViewportModal(false);
    toggleQslModal(false);
    toggleGalaxyModal(false);
    toggleTowerModal(false);
    setWfMode('waterfall');
    if (typeof setGalMode === 'function') setGalMode('3d-vector');
    if (typeof setModalGalMode === 'function') setModalGalMode('split');
    document.querySelectorAll('.audition-btn').forEach(b => b.classList.remove('playing'));
    document.getElementById('audio-status-label').textContent = 'READY';

    let cursorTarget = null;
    let clickPulse = 0.0;
    let isPlayingAudio = false;
    let sstvCurtainPct = 0.0;
    let customAzimuth = null;
    let customDialIdx = null;
    let customFocusSel = step.active;

    // =========================================================================
    // ACT 1: TELL THEM WHAT YOU'RE GOING TO TELL THEM (OVERVIEW & EXPAND PREVIEW)
    // =========================================================================
    if (sk === 'S01_TELL_OVERVIEW') {
      selectPreset('radio-corrugated');
      setViewportMode('video');
      vfoAngle = 40 + frameIdx * 0.9;
      document.getElementById('vfo-wheel').style.transform = `rotate(${vfoAngle.toFixed(1)}deg)`;
      // Rapidly highlight the 4 bays in sequence inside the overview step!
      if (u < 0.25) customFocusSel = '.gor9-console-frame';
      else if (u < 0.50) customFocusSel = '.top-tuner-strip';
      else if (u < 0.75) customFocusSel = '.workspace-grid > .bay-col:nth-child(1)';
      else customFocusSel = '.workspace-grid > .bay-col:nth-child(2)';
    } else if (sk === 'S02_OVERVIEW_TUNER') {
      selectPreset('radio-corrugated');
      if (u < 0.35) {
        setWfMode('waterfall');
        cursorTarget = '#wf-mode-row .wf-mode-btn[data-wf="bandplan"]';
      } else if (u < 0.65) {
        setWfMode('bandplan');
        cursorTarget = '#btn-expand-tuner';
        clickPulse = (u - 0.35) < 0.12 ? (u - 0.35) / 0.12 : 0.0;
      } else {
        setWfMode('bandplan');
        toggleTunerModal(true);
        customFocusSel = '#tuner-modal .modal-card';
        cursorTarget = '#tuner-modal-canvas';
        clickPulse = (u - 0.65) < 0.12 ? (u - 0.65) / 0.12 : 0.0;
      }
    } else if (sk === 'S03_OVERVIEW_CORRELATOR') {
      selectPreset('radio-corrugated');
      if (u < 0.33) {
        setViewportMode('video');
        cursorTarget = '#vp-btn-spectrum';
      } else if (u < 0.64) {
        setViewportMode('spectrum');
        cursorTarget = '#btn-expand-viewport';
        clickPulse = (u - 0.33) < 0.12 ? (u - 0.33) / 0.12 : 0.0;
      } else {
        setViewportMode('video');
        toggleViewportModal(true);
        customFocusSel = '#viewport-modal .modal-card';
        cursorTarget = '#viewport-modal-canvas';
        clickPulse = (u - 0.64) < 0.12 ? (u - 0.64) / 0.12 : 0.0;
      }
    } else if (sk === 'S04_OVERVIEW_ASTROMETRY') {
      selectPreset('radio-corrugated');
      customAzimuth = 212.4 - 55.0 * Math.sin(u * Math.PI);
      document.getElementById('gal-az-val').textContent = `${customAzimuth.toFixed(1)}°`;
      if (u < 0.30) {
        setGalMode('3d-vector');
        cursorTarget = '#gal-mode-row .wf-mode-btn[data-gmode="sky-scope"]';
      } else if (u < 0.60) {
        setGalMode('sky-scope');
        cursorTarget = '#btn-expand-galaxy';
        clickPulse = (u - 0.30) < 0.12 ? (u - 0.30) / 0.12 : 0.0;
      } else {
        toggleGalaxyModal(true);
        setModalGalMode('split');
        customFocusSel = '#galaxy-modal .modal-card';
        cursorTarget = '#galaxy-modal-canvas';
        clickPulse = (u - 0.60) < 0.12 ? (u - 0.60) / 0.12 : 0.0;
      }
    } else if (sk === 'S05_OVERVIEW_EQSL') {
      selectPreset('radio-corrugated');
      if (u < 0.58) {
        cursorTarget = '#btn-expand-qsl';
      } else {
        toggleQslModal(true);
        customFocusSel = '#qsl-modal .modal-card';
        cursorTarget = '#qsl-modal-img';
        clickPulse = (u - 0.58) < 0.12 ? (u - 0.58) / 0.12 : 0.0;
      }

    // =========================================================================
    // ACT 2: TELL THEM (LIVE OPERATION & EXPANDED MODALS)
    // =========================================================================
    } else if (sk === 'S06_TUNER_PRESETS_BANDS') {
      // Rapidly step across 5 wavebands & presets!
      if (u < 0.20) {
        selectBand('90m');
        cursorTarget = '#band-btn-row .band-pill-btn[data-band="90m"]';
        clickPulse = u < 0.10 ? u / 0.10 : 0.0;
      } else if (u < 0.40) {
        selectBand('41m');
        cursorTarget = '#band-btn-row .band-pill-btn[data-band="41m"]';
        clickPulse = (u - 0.20) < 0.10 ? (u - 0.20) / 0.10 : 0.0;
      } else if (u < 0.60) {
        selectBand('43m');
        cursorTarget = '#band-btn-row .band-pill-btn[data-band="43m"]';
        clickPulse = (u - 0.40) < 0.10 ? (u - 0.40) / 0.10 : 0.0;
      } else if (u < 0.80) {
        selectBand('25m');
        cursorTarget = '#preset-btn-radio-corrugated';
        clickPulse = (u - 0.60) < 0.10 ? (u - 0.60) / 0.10 : 0.0;
      } else {
        selectBand('21cm');
        cursorTarget = '#band-btn-row .band-pill-btn[data-band="21cm"]';
        clickPulse = (u - 0.80) < 0.10 ? (u - 0.80) / 0.10 : 0.0;
      }
    } else if (sk === 'S07_TUNER_DIAL_VERNIER') {
      selectPreset('buoy-n24');
      const spinU = smoothstep(0.05, 0.85, u);
      vfoAngle = 120 + spinU * 720.0;
      document.getElementById('vfo-wheel').style.transform = `rotate(${vfoAngle.toFixed(1)}deg)`;
      customDialIdx = lerp(0.0, 4.8, spinU);
      const doppShift = lerp(-24.0, 0.0, spinU);
      const measKhz = 3890.0 + doppShift / 1000.0;
      document.getElementById('vfo-meas-display').textContent = `${measKhz.toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 3 })} kHz`;
      document.getElementById('vfo-dopp-display').textContent = `${doppShift >= 0 ? '+' : ''}${doppShift.toFixed(1)} Hz`;

      const bwSel = u < 0.30 ? 12000 : (u < 0.55 ? 6000 : (u < 0.78 ? 2400 : 500));
      document.querySelectorAll('#bw-btn-row .mini-hw-btn').forEach(b => {
        b.classList.toggle('active', Number(b.dataset.bw) === bwSel);
      });
      cursorTarget = u < 0.45 ? '#vfo-wheel' : `#bw-btn-row .mini-hw-btn[data-bw="${bwSel}"]`;
      clickPulse = ((u * 4.0) % 1.0) < 0.28 ? ((u * 4.0) % 1.0) / 0.28 : 0.0;
    } else if (sk === 'S08_TUNER_FREQ_MAPS') {
      selectPreset('radio-corrugated');
      if (u < 0.22) {
        setWfMode('waterfall');
        cursorTarget = '#wf-mode-row .wf-mode-btn[data-wf="waterfall"]';
        clickPulse = u < 0.12 ? u / 0.12 : 0.0;
      } else if (u < 0.45) {
        setWfMode('bandplan');
        cursorTarget = '#wf-mode-row .wf-mode-btn[data-wf="bandplan"]';
        clickPulse = (u - 0.22) < 0.12 ? (u - 0.22) / 0.12 : 0.0;
      } else if (u < 0.72) {
        setWfMode('ridges3d');
        cursorTarget = '#wf-mode-row .wf-mode-btn[data-wf="ridges3d"]';
        clickPulse = (u - 0.45) < 0.12 ? (u - 0.45) / 0.12 : 0.0;
      } else {
        setWfMode('doppler');
        cursorTarget = '#wf-mode-row .wf-mode-btn[data-wf="doppler"]';
        clickPulse = (u - 0.72) < 0.12 ? (u - 0.72) / 0.12 : 0.0;
      }
    } else if (sk === 'S09_TUNER_MODAL_EXPAND') {
      if (u < 0.36) selectPreset('radio-corrugated');
      else if (u < 0.70) selectPreset('m33-drift-buoy');
      else selectPreset('trojan-octal');
      toggleTunerModal(true);
      customFocusSel = '#tuner-modal .modal-card';
      cursorTarget = '#tuner-modal-canvas';
      clickPulse = ((u * 3.0) % 1.0) < 0.25 ? ((u * 3.0) % 1.0) / 0.25 : 0.0;
    } else if (sk === 'S10_CORRELATOR_VIDEO_EXPAND') {
      selectPreset('radio-corrugated');
      setViewportMode('video');
      if (u < 0.46) {
        cursorTarget = '#btn-expand-viewport';
        clickPulse = u < 0.14 ? u / 0.14 : 0.0;
      } else {
        toggleViewportModal(true);
        customFocusSel = '#viewport-modal .modal-card';
        cursorTarget = '#viewport-modal-canvas';
        clickPulse = (u - 0.46) < 0.14 ? (u - 0.46) / 0.14 : 0.0;
      }
    } else if (sk === 'S11_CORRELATOR_SPECTRUM_MASER') {
      selectPreset('m33-drift-buoy');
      setViewportMode('spectrum');
      if (u < 0.58) {
        cursorTarget = '#vp-btn-spectrum';
        clickPulse = u < 0.15 ? u / 0.15 : 0.0;
      } else {
        toggleViewportModal(true);
        customFocusSel = '#viewport-modal .modal-card';
        cursorTarget = '#viewport-modal-canvas';
        clickPulse = (u - 0.58) < 0.14 ? (u - 0.58) / 0.14 : 0.0;
      }
    } else if (sk === 'S12_CORRELATOR_CIPHER_CARTRIDGES') {
      selectPreset('trojan-octal');
      setViewportMode('decoder');
      if (u < 0.28) {
        selectTranslationAlg('RAW');
        cursorTarget = '#alg-selector-row .alg-chip[data-alg="RAW"]';
        clickPulse = u < 0.12 ? u / 0.12 : 0.0;
      } else if (u < 0.56) {
        selectTranslationAlg('ALG-01');
        cursorTarget = '#alg-selector-row .alg-chip[data-alg="ALG-01"]';
        clickPulse = (u - 0.28) < 0.12 ? (u - 0.28) / 0.12 : 0.0;
      } else {
        selectTranslationAlg('ALG-02');
        cursorTarget = '#alg-selector-row .alg-chip[data-alg="ALG-02"]';
        clickPulse = (u - 0.56) < 0.12 ? (u - 0.56) / 0.12 : 0.0;
      }
    } else if (sk === 'S13_CORRELATOR_CIPHER_EXPAND_AUDIO') {
      if (u < 0.40) {
        selectPreset('trojan-octal');
        setViewportMode('decoder');
        selectTranslationAlg('ALG-02');
        toggleViewportModal(true);
        customFocusSel = '#viewport-modal .modal-card';
        cursorTarget = '#viewport-modal-canvas';
        clickPulse = u < 0.12 ? u / 0.12 : 0.0;
      } else if (u < 0.70) {
        selectPreset('radio-corrugated');
        setViewportMode('video');
        document.getElementById('btn-play-intercept').classList.add('playing');
        document.getElementById('audio-status-label').textContent = 'PLAYING INTERCEPT';
        isPlayingAudio = true;
        cursorTarget = '#btn-play-intercept';
        clickPulse = (u - 0.40) < 0.12 ? (u - 0.40) / 0.12 : 0.0;
      } else {
        selectPreset('radio-corrugated');
        setViewportMode('video');
        document.getElementById('btn-play-is').classList.add('playing');
        document.getElementById('audio-status-label').textContent = 'PLAYING INTERVAL SIGNAL';
        isPlayingAudio = true;
        cursorTarget = '#btn-play-is';
        clickPulse = (u - 0.70) < 0.12 ? (u - 0.70) / 0.12 : 0.0;
      }
    } else if (sk === 'S14_ASTROMETRY_BEAM_SINPO') {
      selectPreset('radio-corrugated');
      setViewportMode('video');
      customAzimuth = 212.4 - 72.0 * Math.sin(u * Math.PI);
      document.getElementById('gal-az-val').textContent = `${customAzimuth.toFixed(1)}°`;
      const dynPct = 82 + Math.round(14 * Math.sin(tSec * 8.0));
      renderSMeterBar(dynPct);
      if (u < 0.28) {
        setGalMode('3d-vector');
        cursorTarget = '#gal-mode-row .wf-mode-btn[data-gmode="3d-ceres"]';
      } else if (u < 0.56) {
        setGalMode('3d-ceres');
        cursorTarget = '#gal-mode-row .wf-mode-btn[data-gmode="sky-scope"]';
        clickPulse = (u - 0.28) < 0.10 ? (u - 0.28) / 0.10 : 0.0;
      } else if (u < 0.80) {
        setGalMode('sky-scope');
        cursorTarget = '.sinpo-matrix';
        clickPulse = (u - 0.56) < 0.10 ? (u - 0.56) / 0.10 : 0.0;
      } else {
        setGalMode('equirect');
        cursorTarget = '#btn-expand-galaxy';
      }
    } else if (sk === 'S15_ASTROMETRY_GALAXY_MODAL') {
      toggleGalaxyModal(true);
      customFocusSel = '#galaxy-modal .modal-card';
      if (u < 0.35) {
        selectPreset('radio-corrugated');
        setModalGalMode('3d-ceres');
        cursorTarget = '#modal-gal-mode-row .wf-mode-btn[data-mgmode="split"]';
      } else if (u < 0.72) {
        selectPreset('m33-drift-buoy');
        setModalGalMode('split');
        cursorTarget = '#modal-gal-mode-row .wf-mode-btn[data-mgmode="sky-scope"]';
      } else {
        selectPreset('trojan-octal');
        setModalGalMode('sky-scope');
        cursorTarget = '#galaxy-modal-canvas';
      }
      clickPulse = ((u * 3.0) % 1.0) < 0.25 ? ((u * 3.0) % 1.0) / 0.25 : 0.0;
    } else if (sk === 'S16_EQSL_SSTV_WIPE') {
      selectPreset('radio-corrugated');
      setViewportMode('video');
      document.getElementById('btn-play-sstv').classList.add('playing');
      document.getElementById('audio-status-label').textContent = 'DECODING SSTV BURST';
      if (u < 0.20) {
        sstvCurtainPct = 100.0;
        cursorTarget = '#btn-play-sstv';
        clickPulse = u < 0.12 ? u / 0.12 : 0.0;
      } else if (u < 0.82) {
        const wipeU = (u - 0.20) / 0.62;
        const step14 = Math.floor(wipeU * 14.0) / 14.0;
        sstvCurtainPct = Math.max(0.0, (1.0 - step14) * 100.0);
        cursorTarget = '.qsl-img-container';
      } else {
        sstvCurtainPct = 0.0;
        cursorTarget = '#btn-expand-qsl';
      }
    } else if (sk === 'S17_EQSL_MODAL_AND_LOGS') {
      selectPreset('radio-corrugated');
      if (u < 0.55) {
        toggleQslModal(true);
        customFocusSel = '#qsl-modal .modal-card';
        cursorTarget = '#qsl-modal-img';
        clickPulse = u < 0.14 ? u / 0.14 : 0.0;
      } else {
        customFocusSel = '.ghlog-terminal';
        const slotIdx = u < 0.70 ? 0 : (u < 0.85 ? 1 : 2);
        renderStationLogs(currentStation, slotIdx);
        cursorTarget = '#ghlog-entry-text';
        clickPulse = ((u - 0.55) % 0.15) < 0.08 ? 0.6 : 0.0;
      }

    // =========================================================================
    // ACT 3: TELL THEM WHAT YOU TOLD THEM (RAPID VISUAL RECAP)
    // =========================================================================
    } else if (sk === 'S18_RECAP_TUNER_CORRELATOR') {
      if (u < 0.35) {
        selectPreset('radio-corrugated');
        setWfMode('bandplan');
        setViewportMode('video');
        customFocusSel = '.top-tuner-strip';
      } else if (u < 0.68) {
        selectPreset('m33-drift-buoy');
        setWfMode('ridges3d');
        setViewportMode('spectrum');
        customFocusSel = '.workspace-grid > .bay-col:nth-child(1)';
      } else {
        selectPreset('trojan-octal');
        setWfMode('doppler');
        setViewportMode('decoder');
        selectTranslationAlg('ALG-02');
        customFocusSel = '.workspace-grid > .bay-col:nth-child(1)';
      }
    } else if (sk === 'S19_RECAP_ASTROMETRY_EQSL') {
      selectPreset('radio-corrugated');
      if (u < 0.38) {
        toggleGalaxyModal(true);
        customFocusSel = '#galaxy-modal .modal-card';
      } else if (u < 0.74) {
        toggleQslModal(true);
        customFocusSel = '#qsl-modal .modal-card';
      } else {
        customFocusSel = '.workspace-grid > .bay-col:nth-child(3)';
      }
    } else {
      // S20_RECAP_SIGNOFF
      selectPreset('radio-corrugated');
      setWfMode('waterfall');
      setViewportMode('video');
      vfoAngle = 90 + frameIdx * 0.8;
      document.getElementById('vfo-wheel').style.transform = `rotate(${vfoAngle.toFixed(1)}deg)`;
    }

    // Apply deterministic SSTV wipe curtain height
    const curtain = document.getElementById('sstv-wipe-curtain');
    if (curtain) {
      curtain.style.height = `${sstvCurtainPct.toFixed(1)}%`;
    }

    // Update sliding dial
    drawVfoDial(customDialIdx !== null ? customDialIdx : undefined);

    // Calculate waterfall cursor & passband width
    const actIdx = currentStation ? STATIONS_DATA.presets.indexOf(currentStation) : 0;
    let curPct = 14 + actIdx * 14.4;
    let bwPx = 68;
    const activeBwBtn = document.querySelector('#bw-btn-row .mini-hw-btn.active');
    if (activeBwBtn) {
      const bwHz = Number(activeBwBtn.dataset.bw);
      bwPx = bwHz <= 600 ? 22 : bwHz <= 3000 ? 42 : bwHz <= 7000 ? 68 : 115;
    }

    // Render all live canvases deterministically
    renderDeterministicWaterfall(tSec, curPct, bwPx, actIdx);
    renderDeterministicPanelSpectrum(frameIdx);
    renderDeterministicScope(frameIdx, isPlayingAudio);

    if (document.getElementById('tuner-modal').classList.contains('open')) {
      drawTunerModalCanvas(tSec * 1.4);
    }
    if (document.getElementById('viewport-modal').classList.contains('open')) {
      drawViewportModalCanvas(tSec * 1.4);
    }

    displayedAzimuth = customAzimuth !== null ? customAzimuth : targetAzimuth;
    const c1 = document.getElementById('galaxy-map-canvas');
    const c2 = document.getElementById('galaxy-modal-canvas');
    if (c1) drawGalaxyAstrometry(c1, galaxyHitBoxes, tSec * 0.9, false);
    if (c2 && document.getElementById('galaxy-modal').classList.contains('open')) {
      drawGalaxyAstrometry(c2, modalGalaxyHitBoxes, tSec * 0.9, true);
    }

    // Draw deterministic video frame onto #station-video-canvas when in video mode
    if (videoCtx && currentViewportMode === 'video') {
      const clipFrame = await preloadClipFrame(frameIdx + 1);
      if (clipFrame) {
        videoCtx.drawImage(clipFrame, 0, 0, videoCanvas.width, videoCanvas.height);
      }
    }

    updateFocusAndCursor(customFocusSel, step.symbolic, cursorTarget, clickPulse, tSec);
  };

  window.addEventListener('load', () => {
    setTimeout(() => {
      ensureOverlays();
      window.__mk4Ready = true;
    }, 350);
  });
})();
</script>
"""


class _MK4HttpHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, patched_html_bytes: bytes, **kwargs):
        self._patched_html_bytes = patched_html_bytes
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args) -> None:
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/__capture_mk4.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(self._patched_html_bytes)))
            self.end_headers()
            self.wfile.write(self._patched_html_bytes)
            return
        super().do_GET()


class _ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _CDPWebSocket:
    """Minimal RFC 6455 WebSocket client over stdlib socket for Chrome DevTools Protocol."""

    def __init__(self, ws_url: str) -> None:
        # ws://127.0.0.1:<port>/devtools/page/<id>
        rest = ws_url.removeprefix("ws://")
        host_port, path = rest.split("/", 1)
        path = "/" + path
        host, port_s = host_port.split(":")
        self.sock = socket.create_connection((host, int(port_s)), timeout=30.0)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host_port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode("ascii"))
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("CDP WebSocket handshake closed unexpectedly")
            buf += chunk
        self._rx_buf = buf.split(b"\r\n\r\n", 1)[1]
        self._msg_id = 0

    def _recv_exact(self, n: int) -> bytes:
        while len(self._rx_buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("CDP WebSocket closed while reading frame")
            self._rx_buf += chunk
        out = self._rx_buf[:n]
        self._rx_buf = self._rx_buf[n:]
        return out

    def send_json(self, obj: dict) -> None:
        payload = json.dumps(obj).encode("utf-8")
        mask_key = os.urandom(4)
        header = bytearray([0x81])  # FIN + text frame
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack(">H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack(">Q", length))
        header.extend(mask_key)
        masked = bytes(b ^ mask_key[i & 3] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def recv_json(self) -> dict:
        while True:
            b0, b1 = self._recv_exact(2)
            opcode = b0 & 0x0F
            masked = (b1 & 0x80) != 0
            length = b1 & 0x7F
            if length == 126:
                (length,) = struct.unpack(">H", self._recv_exact(2))
            elif length == 127:
                (length,) = struct.unpack(">Q", self._recv_exact(8))
            mask_key = self._recv_exact(4) if masked else b""
            data = self._recv_exact(length)
            if masked:
                data = bytes(b ^ mask_key[i & 3] for i, b in enumerate(data))
            if opcode == 0x8:
                raise RuntimeError("CDP WebSocket closed by peer")
            if opcode == 0x9:  # Ping -> Pong
                pong = bytearray([0x8A, 0x80, 0, 0, 0, 0])
                self.sock.sendall(bytes(pong))
                continue
            if opcode == 0x1:
                return json.loads(data.decode("utf-8"))

    def call(self, method: str, params: dict | None = None) -> dict:
        self._msg_id += 1
        mid = self._msg_id
        self.send_json({"id": mid, "method": method, "params": params or {}})
        while True:
            msg = self.recv_json()
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"CDP error calling {method}: {msg['error']}")
                return msg.get("result", {})

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass


def find_chrome_binary() -> str:
    pw_root = Path.home() / ".cache" / "ms-playwright"
    if pw_root.is_dir():
        for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
            return str(candidate)
    for c in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium"):
        p = shutil.which(c)
        if p:
            return p
    raise RuntimeError("No Chromium binary found")


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def worker_capture_shard(
    wid: int,
    shard: list[tuple[int, float]],
    http_port: int,
    frames_dir: Path,
    state: dict,
    lock: threading.Lock,
) -> None:
    chrome_bin = find_chrome_binary()
    cdp_port = get_free_port()
    tmp_prof = Path(f"/tmp/gor9_mk4_cdp_{os.getpid()}_{wid}")
    shutil.rmtree(tmp_prof, ignore_errors=True)
    tmp_prof.mkdir(parents=True, exist_ok=True)

    url = f"http://127.0.0.1:{http_port}/__capture_mk4.html?capture=1"
    cmd = [
        chrome_bin,
        "--headless=new",
        f"--user-data-dir={tmp_prof}",
        f"--remote-debugging-port={cdp_port}",
        "--remote-allow-origins=*",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--enable-webgl",
        "--ignore-gpu-blocklist",
        "--use-gl=angle",
        "--use-angle=gl",
        "--hide-scrollbars",
        "--mute-audio",
        f"--window-size={CSS_W},{CSS_H}",
        f"--force-device-scale-factor={SCALE_FACTOR:.10f}",
        url,
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws: _CDPWebSocket | None = None
    try:
        # Wait for DevTools HTTP endpoint and find page target
        ws_url = None
        for _ in range(80):
            time.sleep(0.1)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=2.0) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                for t in targets:
                    if t.get("type") == "page" and "__capture_mk4.html" in t.get("url", ""):
                        ws_url = t.get("webSocketDebuggerUrl")
                        break
                if ws_url:
                    break
            except Exception:
                continue
        if not ws_url:
            raise RuntimeError(f"Worker {wid}: Could not connect to CDP on port {cdp_port}")

        ws = _CDPWebSocket(ws_url)
        ws.call("Page.enable")
        ws.call("Runtime.enable")
        ws.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": CSS_W,
                "height": CSS_H,
                "deviceScaleFactor": SCALE_FACTOR,
                "mobile": False,
            },
        )

        # Wait for window.__mk4Ready === true
        for _ in range(60):
            res = ws.call("Runtime.evaluate", {"expression": "Boolean(window.__mk4Ready)", "returnByValue": True})
            if res.get("result", {}).get("value") is True:
                break
            time.sleep(0.1)

        for idx, t_sec in shard:
            out_png = frames_dir / f"frame_{idx + 1:04d}.png"
            if out_png.exists() and out_png.stat().st_size > 10000:
                continue
            ws.call(
                "Runtime.evaluate",
                {
                    "expression": f"window.__mk4StepAtTime({t_sec:.5f}, {idx})",
                    "awaitPromise": True,
                },
            )
            shot = ws.call(
                "Page.captureScreenshot",
                {
                    "format": "png",
                    "captureBeyondViewport": False,
                },
            )
            png_bytes = base64.b64decode(shot["data"])
            out_png.write_bytes(png_bytes)
            with lock:
                state["captured"] += 1
                c = state["captured"]
                total = state["total"]
            if c % 25 == 0 or c == total:
                print(f"  [MK-IV Capture] {c}/{total} frames ({c * 100.0 / total:.1f}%) — latest: frame_{idx + 1:04d}.png", flush=True)
    finally:
        if ws:
            ws.close()
        proc.terminate()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(tmp_prof, ignore_errors=True)


def capture_mk4_frames(
    timeline_doc: dict,
    workers: int = 6,
    clean: bool = False,
    target_indices: list[int] | None = None,
) -> None:
    if clean and FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    clip_count = prepare_station_video_frames()

    orig_html = (DOCS_DIR / "index.html").read_text(encoding="utf-8")
    injected = (
        INJECTED_MK4_DEMO_JS.replace("__TIMELINE_JSON_PLACEHOLDER__", json.dumps(timeline_doc))
        .replace("__CLIP_FRAME_COUNT_PLACEHOLDER__", str(clip_count))
    )
    patched_html = orig_html.replace("</body>", injected + "\n</body>")
    patched_bytes = patched_html.encode("utf-8")

    total_frames = int(timeline_doc["total_frames"])
    if target_indices is not None:
        all_pairs = [(idx, idx / float(FPS)) for idx in target_indices]
    else:
        all_pairs = [(idx, idx / float(FPS)) for idx in range(total_frames)]

    missing_pairs = [
        (idx, t)
        for idx, t in all_pairs
        if not (FRAMES_DIR / f"frame_{idx + 1:04d}.png").exists()
    ]
    if not missing_pairs:
        print(f"All {len(all_pairs)} frames already exist in {FRAMES_DIR}.", flush=True)
        return

    handler = functools.partial(
        _MK4HttpHandler,
        directory=str(DOCS_DIR),
        patched_html_bytes=patched_bytes,
    )
    server = _ThreadedTCPServer(("127.0.0.1", 0), handler)
    http_port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()

    actual_workers = min(workers, len(missing_pairs))
    shards = [missing_pairs[w::actual_workers] for w in range(actual_workers)]
    state = {"captured": len(all_pairs) - len(missing_pairs), "total": len(all_pairs)}
    lock = threading.Lock()

    print(
        f"Capturing {len(missing_pairs)} frames (of {len(all_pairs)}) at {TARGET_W}x{TARGET_H} "
        f"across {actual_workers} parallel Chromium CDP workers...",
        flush=True,
    )
    t0 = time.monotonic()
    threads = []
    for w, shard in enumerate(shards):
        th = threading.Thread(
            target=worker_capture_shard,
            args=(w, shard, http_port, FRAMES_DIR, state, lock),
            daemon=True,
        )
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    server.shutdown()
    server.server_close()
    dt = time.monotonic() - t0
    print(f"Frame capture finished in {dt:.1f}s ({len(missing_pairs) / max(0.1, dt):.1f} fps)", flush=True)


def assemble_mp4_and_metadata(timeline_doc: dict) -> Path:
    audio_wav = OUT_DIR / "gor9_mk4_demo_audio.wav"
    out_mp4 = OUT_DIR / "gor9_mk4_demo.mp4"
    out_thumb = OUT_DIR / "gor9_mk4_demo_thumb.jpg"

    cmd = [
        "/usr/bin/ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-start_number",
        "1",
        "-i",
        str(FRAMES_DIR / "frame_%04d.png"),
        "-i",
        str(audio_wav),
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-b:a",
        "192k",
        "-shortest",
        "-vf",
        "fps=30,setsar=1:1,format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-profile:v",
        "high",
        "-level:v",
        "5.1",
        "-crf",
        "16",
        "-pix_fmt",
        "yuv420p",
        "-colorspace",
        "bt709",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    print(f"Assembling 2560x1440 30fps MP4 -> {out_mp4} ...", flush=True)
    subprocess.run(cmd, check=True)

    # Pick a vivid hero frame (e.g. during CAM_FEED or CODE_DECODER)
    steps = timeline_doc["steps"]
    hero_sec = steps[4]["start_sec"] + 1.5 if len(steps) > 4 else 5.0
    hero_idx = max(1, min(int(timeline_doc["total_frames"]), int(round(hero_sec * FPS))))
    hero_png = FRAMES_DIR / f"frame_{hero_idx:04d}.png"
    if hero_png.exists():
        subprocess.run(
            ["/usr/bin/ffmpeg", "-y", "-v", "quiet", "-i", str(hero_png), "-q:v", "3", str(out_thumb)],
            check=True,
        )
        print(f"Saved Hero Thumbnail -> {out_thumb} (from frame_{hero_idx:04d}.png)", flush=True)

    chapters = []
    for st in steps:
        m = int(st["start_sec"] // 60)
        s = int(st["start_sec"] % 60)
        chapters.append(f"{m}:{s:02d} {st['step_kind']} — {st['symbolic']}")

    yt_path = OUT_DIR / "youtube.json"
    prev_yt = {}
    if yt_path.exists():
        try:
            prev_yt = json.loads(yt_path.read_text(encoding="utf-8"))
        except Exception:
            prev_yt = {}

    yt_meta = {
        "short_code": "MK4-DEMO",
        "g_id": "2736.305",
        "channel": "@GOR-9-station",
        "categoryId": "28",
        "privacyStatus": prev_yt.get("privacyStatus", "unlisted"),
        "title_1080p": "GOR-9 • Hauser Dynamics MK-IV Wideband Barycentric DX Correlator — Console Operations Demo",
        "description": (
            "Component-by-component operational walkthrough of the Hauser Dynamics MK-IV Wideband Barycentric "
            "DX Correlator (3 kHz – 1.5 GHz) aboard Galactic Outpost Radio (GOR-9) on Asteroid 3-5-1.\n\n"
            + "\n".join(chapters)
        ),
        "tags": [
            "GOR-9",
            "Galactic Outpost Radio",
            "Hauser MK-IV",
            "Shortwave",
            "Retro-Futurism",
            "Console Demo",
        ],
        "files": {
            "wide_1080p_mp4": str(out_mp4),
            "thumbnail_16x9_png": str(out_thumb),
            "audio_wav": str(audio_wav),
            "script_scr": str(SCRIPT_SCR),
        },
        "uploads": prev_yt.get("uploads", {}),
        "history": prev_yt.get("history", {}),
    }
    yt_path.write_text(json.dumps(yt_meta, indent=2) + "\n", encoding="utf-8")
    return out_mp4


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Hauser MK-IV Demo Take from videos/mk4_demo/script.scr")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--force-tts", action="store_true")
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--test-frames", action="store_true", help="Render 13 diagnostic keyframes (1 per step)")
    parser.add_argument("--encode-only", action="store_true")
    args = parser.parse_args()

    timeline_doc = build_audio_and_timeline(force_tts=args.force_tts)
    if args.audio_only:
        return

    if args.test_frames:
        # Capture 1 midpoint frame per [screen: ...] step for quick visual inspection
        test_indices = []
        for st in timeline_doc["steps"]:
            mid_t = 0.5 * (st["start_sec"] + st["end_sec"])
            test_indices.append(int(round(mid_t * FPS)))
        capture_mk4_frames(timeline_doc, workers=args.workers, clean=args.clean, target_indices=test_indices)
        return

    if not args.encode_only:
        capture_mk4_frames(timeline_doc, workers=args.workers, clean=args.clean)

    # Verify if any frames were missed and run a quick pass if needed
    capture_mk4_frames(timeline_doc, workers=args.workers, clean=False)
    assemble_mp4_and_metadata(timeline_doc)


if __name__ == "__main__":
    main()
