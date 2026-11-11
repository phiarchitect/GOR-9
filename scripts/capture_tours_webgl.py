#!/usr/bin/env python3
"""Capture the 30.00 fps WebGL 'Drone Tour' and 'Satellite Orbit (One Pass)' videos
from `docs/tower-3d.html` (without modifying `docs/tower-3d.html` on disk),
synthesize bespoke 30.00s Generative C-Lydian Broadcast Soundtracks with 3 synchronized
Marzelvane 4-Ring + Spire Lock Cherenkov Bursts, and encode each into its own folder
at native 2560x1440 QHD (High@L5.1, 30.00 fps CFR, Rec.709, +faststart).

Output Folders:
  1. Drone Tour:
     - /home/phi/PROJECTS/phiarchitect/GOR-9/videos/drone_tour/
  2. Satellite Orbit (One Full 360° Pass of O.R.S. 351):
     - /home/phi/PROJECTS/phiarchitect/GOR-9/videos/satellite_orbit/
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import math
import os
import shutil
import socketserver
import struct
import subprocess
import threading
import time
import wave
import zlib
from pathlib import Path
import numpy as np

SAMPLE_RATE = 24000
FPS = 30
DURATION = 30.00
TOTAL_FRAMES = int(round(DURATION * FPS))  # 900 frames at 30.00 fps

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
VIDEOS_DIR = ROOT / "videos"

# C-Lydian & G-Lydian Crystal Frequencies (Hz)
F_C2 = 65.41
F_G2 = 98.00
F_A2 = 110.00
F_B2 = 123.47
F_C3 = 130.81
F_D3 = 146.83
F_E3 = 164.81
F_FS3 = 185.00
F_G3 = 196.00
F_A3 = 220.00
F_B3 = 246.94
F_C4 = 261.63
F_D4 = 293.66
F_E4 = 329.63
F_FS4 = 369.99
F_G4 = 392.00
F_A4 = 440.00
F_B4 = 493.88
F_C5 = 523.25
F_CS5 = 554.37
F_D5 = 587.33
F_E5 = 659.25
F_FS5 = 739.99
F_G5 = 783.99
F_A5 = 880.00
F_B5 = 987.77
F_C6 = 1046.50
F_D6 = 1174.66
F_FS6 = 1479.98
F_G6 = 1567.98


# ═══════════════════════════════════════════════════════════════════════════
# 1. GENERATIVE C-LYDIAN SOUNDTRACK & 3-BURST CHIME SYNTHESIZER (24 kHz PCM)
# ═══════════════════════════════════════════════════════════════════════════

def save_wav(path: Path, arr: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(arr * 32767.0, -32767.0, 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def add_at(buf: np.ndarray, clip: np.ndarray, start_sec: float, gain: float = 1.0) -> None:
    i0 = int(round(start_sec * SAMPLE_RATE))
    if i0 < 0 or i0 >= len(buf):
        return
    d = min(len(clip), len(buf) - i0)
    buf[i0 : i0 + d] += clip[:d] * gain


def crystal_note(
    freqs: list[float],
    dur: float,
    decay_tau: float = 1.25,
    attack_tau: float = 0.008,
    amp: float = 0.20,
    echo_taps: list[tuple[float, float]] | None = None,
) -> np.ndarray:
    """Synthesize a C-Lydian harmonic crystal chime note/chord with O.R.S. 351 multi-tap echo."""
    n = max(1, int(dur * SAMPLE_RATE))
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    env = (1.0 - np.exp(-t / attack_tau)) * np.exp(-t / decay_tau)

    sig = np.zeros(n, dtype=np.float64)
    weights = [1.0 / (1.0 + 0.35 * idx) for idx in range(len(freqs))]
    w_sum = sum(weights)

    for w, f in zip(weights, freqs):
        partial = (
            0.70 * np.sin(2.0 * math.pi * f * t)
            + 0.21 * np.sin(2.0 * math.pi * (2.0 * f) * t) * np.exp(-t / (decay_tau * 0.52))
            + 0.09 * np.sin(2.0 * math.pi * (3.002 * f) * t) * np.exp(-t / (decay_tau * 0.25))
        )
        sig += (w / w_sum) * partial

    sig = sig * env * amp

    if echo_taps is None:
        echo_taps = [(0.375, 0.28), (0.750, 0.14), (1.125, 0.07)]

    echo_buf = sig.copy()
    for delay_sec, tap_gain in echo_taps:
        d_idx = int(delay_sec * SAMPLE_RATE)
        if d_idx < n:
            echo_buf[d_idx:] += sig[: n - d_idx] * tap_gain

    fade_samples = min(int(0.30 * SAMPLE_RATE), n // 4)
    if fade_samples > 0:
        fade_curve = 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, fade_samples)))
        echo_buf[-fade_samples:] *= fade_curve

    return echo_buf


def synth_warm_pad_chord(
    freqs: list[float],
    dur: float,
    attack_sec: float = 1.2,
    release_sec: float = 1.8,
    amp: float = 0.065,
    shimmer_hz: float = 0.35,
) -> np.ndarray:
    """Warm analog-style fifths/Lydian pad chord with gentle chorus detune and slow filter shimmer."""
    n = int(dur * SAMPLE_RATE)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    att = np.minimum(1.0, t / max(0.05, attack_sec))
    att = 0.5 - 0.5 * np.cos(att * math.pi)
    rel = np.minimum(1.0, (dur - t) / max(0.05, release_sec))
    rel = 0.5 - 0.5 * np.cos(np.clip(rel, 0.0, 1.0) * math.pi)
    env = att * rel

    sig = np.zeros(n, dtype=np.float64)
    for idx, f in enumerate(freqs):
        w = 1.0 / (1.0 + 0.28 * idx)
        mod = 0.85 + 0.15 * np.sin(2.0 * math.pi * shimmer_hz * t + idx * 0.9)
        voice = (
            0.62 * np.sin(2.0 * math.pi * f * t)
            + 0.22 * np.sin(2.0 * math.pi * (f * 1.0018) * t + 0.4)
            + 0.16 * np.sin(2.0 * math.pi * (f * 2.0) * t) * mod
        )
        sig += w * voice

    sig /= max(1.0, len(freqs) * 0.55)
    return sig * env * amp


def synth_marzelvane_burst_chime(
    variant: int = 0,
    dur: float = 5.80,
    ring_step: float = 0.20,
    spire_lock_offset: float = 0.84,
) -> np.ndarray:
    """Synthesize a 4-Ring + Spire Lock Marzelvane Burst Chime + Cherenkov plasma whoosh."""
    n = int(dur * SAMPLE_RATE)
    out = np.zeros(n, dtype=np.float64)
    tt = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    t1 = 0.00
    t2 = ring_step
    t3 = ring_step * 2.0
    t4 = ring_step * 3.0
    t_lock = spire_lock_offset

    if variant == 0:
        # Classic C-Lydian 4-Ring + Spire Lock
        events = [
            (t1, [F_C4, F_C5], 0.95, 0.20),
            (t2, [F_G4, F_G5], 1.00, 0.21),
            (t3, [F_D5, F_A4], 1.10, 0.22),
            (t4, [F_FS5, F_D5], 1.25, 0.23),
            (t_lock, [F_G5, F_B5, F_D5, F_FS4, F_G4, F_C4], 1.65, 0.28),
        ]
        pad_freqs = [F_C3, F_G3, F_D4, F_FS4]
    elif variant == 1:
        # G-Lydian / High Spire Modulation
        events = [
            (t1, [F_G4, F_D5], 0.95, 0.20),
            (t2, [F_A4, F_E5], 1.00, 0.21),
            (t3, [F_B4, F_FS5], 1.10, 0.22),
            (t4, [F_D5, F_A5], 1.25, 0.23),
            (t_lock, [F_B5, F_G5, F_FS5, F_D5, F_G4, F_G3], 1.65, 0.28),
        ]
        pad_freqs = [F_G2, F_D3, F_A3, F_FS4]
    else:
        # Grand Double-Octave C-Lydian Cathedral Finale Burst
        events = [
            (t1, [F_C4, F_G4, F_C5], 1.15, 0.21),
            (t2, [F_G4, F_D5, F_G5], 1.20, 0.22),
            (t3, [F_D5, F_A5, F_D6], 1.30, 0.23),
            (t4, [F_FS5, F_B5, F_FS6], 1.45, 0.24),
            (t_lock, [F_C6, F_G5, F_FS5, F_D5, F_B4, F_G4, F_C3], 2.15, 0.30),
        ]
        pad_freqs = [F_C2, F_C3, F_G3, F_D4, F_FS4, F_B4]

    pad_attack = 1.0 - np.exp(-tt / 0.28)
    pad_decay = np.exp(-np.maximum(0.0, tt - t_lock) / 1.95)
    pad_env = pad_attack * pad_decay
    fade_len = int(0.55 * SAMPLE_RATE)
    pad_env[-fade_len:] *= 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, fade_len)))

    for f in pad_freqs:
        out += np.sin(2.0 * math.pi * f * tt) * (0.065 / len(pad_freqs)) * pad_env * 3.2

    for t0, freqs, tau, amp in events:
        note = crystal_note(
            freqs,
            dur - t0,
            decay_tau=tau,
            amp=amp,
            echo_taps=[(0.375, 0.30), (0.750, 0.16), (1.125, 0.08), (1.500, 0.04)],
        )
        add_at(out, note, t0)

    # Subtle Cherenkov shockwave plasma shimmer right at Spire Lock (t_lock .. t_lock + 2.50s)
    rng = np.random.default_rng(3510 + variant)
    raw = rng.normal(0.0, 1.0, size=n + 1)
    shimmer_noise = raw[1:] - 0.72 * raw[:-1]
    shimmer_noise /= np.std(shimmer_noise) + 1e-8
    sw_env = np.zeros(n, dtype=np.float64)
    sw_start = max(0.0, t_lock - 0.04)
    sw_dur = 2.60
    for i, ti in enumerate(tt):
        if sw_start <= ti <= sw_start + sw_dur:
            p = min(1.0, max(0.0, (ti - sw_start) / sw_dur))
            sw_env[i] = math.sin(p * math.pi) * ((1.0 - p) ** 1.3) * 0.032
    out += shimmer_noise * sw_env

    return out


def build_generative_lydian_score(mode: str, duration: float = 30.00) -> np.ndarray:
    """Generate a generative C-Lydian soundtrack for 'drone_tour', 'drone_loop', 'satellite_orbit', 'booth_tour', or 'booth_loop'."""
    n_total = int(round(duration * SAMPLE_RATE))
    is_loop_mode = mode in ("booth_loop", "drone_loop")
    # Allocate extra tail buffer so loop modes can wrap reverb/pad tails seamlessly across the loop boundary
    n_alloc = n_total + (int(2.5 * SAMPLE_RATE) if is_loop_mode else 0)
    master = np.zeros(n_alloc, dtype=np.float64)
    seed_map = {"drone_tour": 9001, "drone_loop": 9054, "satellite_orbit": 9351, "booth_tour": 9026, "booth_loop": 9024}
    rng = np.random.default_rng(seed_map.get(mode, 9351))

    # 1. Evolving C-Lydian harmonic pad progression across `duration`:
    if mode == "booth_tour":
        pad_schedule = [
            (0.0, 9.5, [F_C3, F_G3, F_D4, F_E4, F_FS4, F_B4], 0.068),
            (7.5, 9.5, [F_G2, F_D3, F_A3, F_B3, F_E4, F_FS4], 0.070),
            (15.0, 9.5, [F_E3, F_B3, F_D4, F_FS4, F_G4, F_A4], 0.070),
            (22.5, 8.5, [F_G2, F_D3, F_G3, F_B3, F_D4, F_FS4, F_A4], 0.072),
            (29.0, 7.0, [F_C2, F_C3, F_G3, F_D4, F_FS4, F_B4, F_E5], 0.078),
        ]
    elif mode == "booth_loop":
        pad_schedule = [
            (0.0, 14.5, [F_C3, F_G3, F_D4, F_E4, F_FS4, F_B4], 0.068),
            (12.0, 14.5, [F_G2, F_D3, F_A3, F_B3, F_E4, F_FS4], 0.070),
            (24.0, 14.5, [F_E3, F_B3, F_D4, F_FS4, F_G4, F_A4], 0.070),
            (36.0, 14.5, [F_C2, F_C3, F_G3, F_D4, F_FS4, F_B4, F_E5], 0.074),
        ]
    elif mode == "drone_loop":
        pad_schedule = [
            (0.0, 11.5, [F_C3, F_G3, F_D4, F_E4, F_FS4, F_B4], 0.070),
            (9.0, 11.5, [F_G2, F_D3, F_A3, F_B3, F_E4, F_FS4], 0.072),
            (18.0, 11.5, [F_E3, F_B3, F_D4, F_FS4, F_G4, F_A4], 0.072),
            (27.0, 11.5, [F_G2, F_D3, F_G3, F_B3, F_D4, F_FS4, F_A4], 0.072),
            (36.0, 11.5, [F_D3, F_A3, F_E4, F_FS4, F_B4, F_D5], 0.074),
            (45.0, 11.5, [F_C2, F_C3, F_G3, F_D4, F_FS4, F_B4, F_E5], 0.078),
        ]
    else:
        pad_schedule = [
            (0.0, 9.5, [F_C3, F_G3, F_D4, F_E4, F_FS4, F_B4], 0.072),
            (7.5, 10.0, [F_G2, F_D3, F_A3, F_B3, F_E4, F_FS4], 0.074),
            (15.5, 8.5, [F_E3, F_B3, F_D4, F_FS4, F_G4, F_A4], 0.072),
            (22.0, 8.0, [F_C2, F_C3, F_G3, F_D4, F_FS4, F_B4, F_E5], 0.080),
        ]
    for t_start, seg_dur, freqs, amp in pad_schedule:
        pad_clip = synth_warm_pad_chord(
            freqs,
            seg_dur,
            attack_sec=1.6,
            release_sec=2.0,
            amp=amp,
            shimmer_hz=0.32 if mode in ("drone_tour", "drone_loop") else (0.26 if mode in ("booth_tour", "booth_loop") else 0.22),
        )
        add_at(master, pad_clip, t_start)

    # 2. Generative C-Lydian Crystal Arpeggiator & Barycentric Bass Pulse
    scale_low = [F_C3, F_D3, F_E3, F_FS3, F_G3, F_A3, F_B3]
    scale_mid = [F_C4, F_D4, F_E4, F_FS4, F_G4, F_A4, F_B4, F_C5, F_D5, F_E5, F_FS5, F_G5]

    if mode == "drone_tour":
        # Propulsive, soaring eighth-note C-Lydian motif with gentle contemplation during Booth & Ring detail orbits
        arp_pattern = [0, 4, 7, 6, 4, 8, 10, 7, 1, 5, 8, 11, 9, 7, 6, 4]
        step_sec = 0.25
        n_steps = int((duration - 1.2) / step_sec)
        for s in range(n_steps):
            t_note = 0.25 + s * step_sec
            # Duck slightly during the Grand Finale Burst (20.6s .. 23.6s)
            in_burst_head = 20.5 <= t_note <= 23.6
            vel = 0.052 if in_burst_head else (0.112 if s % 4 == 0 else (0.086 if s % 2 == 0 else 0.066))

            deg = arp_pattern[s % len(arp_pattern)]
            if (s // 8) % 2 == 1 and s % 3 == 1:
                deg = (deg + int(rng.choice([-1, 1, 2]))) % len(scale_mid)

            f_main = scale_mid[deg]
            freqs = [f_main]
            if s % 4 == 0:
                freqs.append(scale_mid[max(0, deg - 3)])
            note_clip = crystal_note(
                freqs,
                dur=1.45,
                decay_tau=0.58 if s % 2 == 0 else 0.38,
                attack_tau=0.006,
                amp=vel,
                echo_taps=[(0.375, 0.24), (0.750, 0.11)],
            )
            add_at(master, note_clip, t_note)

            # Deep barycentric bass pulse on bar downbeats (every 8 eighth-notes = 2.0s)
            if s % 8 == 0:
                bass_roots = [F_C2, F_G2, F_D3, F_A2, F_C2, F_G2, F_E3, F_G2]
                b_freq = bass_roots[(s // 8) % len(bass_roots)]
                bass_clip = crystal_note(
                    [b_freq, b_freq * 2.0],
                    dur=1.90,
                    decay_tau=0.85,
                    attack_tau=0.018,
                    amp=0.11,
                    echo_taps=[(0.50, 0.15)],
                )
                add_at(master, bass_clip, t_note)

        # Grand Finale 4-Ring Power-Up (t = 20.60s: Ring 1..4 at +0.00, +0.45, +0.90, +1.35s)
        # & Spire Lock Barycentric Burst Climax at t = 22.55s (+1.95s) as the drone flies away wide!
        chime_clip = synth_marzelvane_burst_chime(
            variant=2,
            dur=8.80,
            ring_step=0.45,
            spire_lock_offset=1.95,
        )
        add_at(master, chime_clip, 20.60, gain=0.96)
    elif mode == "drone_loop":
        # Seamless 54.00s Inverse-Keplerian Elliptical Drone Loop:
        #   - Propulsive 0.25s arpeggio during the 3 fast outer apoapsis swings (0..4.2s, 13.0..19.2s, 28.0..34.2s, 43.0..54.0s)
        #   - Slows to spacious 0.50s crystalline inspection chords during the 3 close periapsis bypasses:
        #       Bypass #1 (4.20s..13.00s): Octagonal Broadcast Booth (+26.0m)
        #       Bypass #2 (19.20s..28.00s): Vertical "G / O / R / ◎ / 9" Neon Sign (+39m..+52m)
        #       Bypass #3 (34.20s..43.00s): 4-Ring Hydrocoptic Marzelvane Crown (+72.0m)
        #   - Single Finale Barycentric Cherenkov Burst at t = 43.20s (Spire Lock at 45.15s) as drone speeds out to wide Apoapsis #3!
        arp_pattern = [0, 4, 7, 6, 4, 8, 10, 7, 1, 5, 8, 11, 9, 7, 6, 4]
        step_sec = 0.25
        n_steps = int(round(duration / step_sec))
        for s in range(n_steps):
            t_note = s * step_sec
            in_periapsis = (4.20 <= t_note <= 13.00) or (19.20 <= t_note <= 28.00) or (34.20 <= t_note <= 43.00)
            # During slow periapsis inspection passes, play every 2nd step (0.50s half-tempo) with richer sustain!
            if in_periapsis and (s % 2 == 1):
                continue
            in_burst_head = 43.0 <= t_note <= 46.8
            vel = 0.048 if in_burst_head else (0.108 if s % 4 == 0 else (0.084 if s % 2 == 0 else 0.064))

            deg = arp_pattern[s % len(arp_pattern)]
            if (s // 8) % 2 == 1 and s % 4 == 2:
                deg = (deg + 2) % len(scale_mid)
            f_main = scale_mid[deg]
            freqs = [f_main, scale_low[deg % len(scale_low)]] if (in_periapsis or s % 4 == 0) else [f_main]
            note_clip = crystal_note(
                freqs,
                dur=2.10 if in_periapsis else 1.45,
                decay_tau=0.82 if in_periapsis else (0.56 if s % 2 == 0 else 0.38),
                attack_tau=0.008,
                amp=vel,
                echo_taps=[(0.375, 0.24), (0.750, 0.11)],
            )
            add_at(master, note_clip, t_note)

            if s % 8 == 0:
                bass_roots = [F_C2, F_G2, F_D3, F_A2, F_E3, F_G2]
                b_freq = bass_roots[(s // 8) % len(bass_roots)]
                bass_clip = crystal_note(
                    [b_freq, b_freq * 2.0],
                    dur=2.30,
                    decay_tau=0.95,
                    attack_tau=0.020,
                    amp=0.102,
                    echo_taps=[(0.50, 0.15)],
                )
                add_at(master, bass_clip, t_note)

        # Bypass #1 (Booth, 7.60s): Warm Broadcast Booth HUD & Pulsar telemetry lock chord
        booth_chime = crystal_note(
            [F_C5, F_E5, F_G5, F_B5, F_FS5],
            dur=3.20,
            decay_tau=1.35,
            attack_tau=0.020,
            amp=0.115,
            echo_taps=[(0.40, 0.25), (0.80, 0.12)],
        )
        add_at(master, booth_chime, 7.60)

        # Bypass #2 (Vertical Sign "G / O / R / ◎ / 9", 20.00s..26.00s): 5-step rising neon sequence bells
        sign_notes = [F_C5, F_E5, F_G5, F_B5, F_D6]
        for idx_s, f_s in enumerate(sign_notes):
            s_bell = crystal_note(
                [f_s, f_s * 0.5],
                dur=1.90,
                decay_tau=0.75,
                attack_tau=0.005,
                amp=0.088,
                echo_taps=[(0.35, 0.22)],
            )
            add_at(master, s_bell, 20.20 + idx_s * 1.25)

        # Bypass #3 (4-Ring Marzelvane Crown, 37.80s): High Cherenkov harmonic shimmer chord
        crown_shimmer = crystal_note(
            [F_D5, F_FS5, F_B5, F_D6, F_FS6],
            dur=3.50,
            decay_tau=1.45,
            attack_tau=0.024,
            amp=0.118,
            echo_taps=[(0.42, 0.26), (0.84, 0.14)],
        )
        add_at(master, crown_shimmer, 37.80)

        # Single Finale 4-Ring Power-Up (t = 43.20s) & Spire Lock Barycentric Cherenkov Burst (t = 45.15s)!
        chime_clip = synth_marzelvane_burst_chime(
            variant=2,
            dur=8.40,
            ring_step=0.45,
            spire_lock_offset=1.95,
        )
        add_at(master, chime_clip, 43.20, gain=0.95)
    elif mode == "booth_tour":
        # Watchroom Interior 36.0s Soundtrack:
        # Warm C-Lydian console arpeggio + bay-specific hardware acoustic signatures
        booth_motif = [0, 3, 4, 7, 6, 4, 2, 4, 7, 10, 9, 7, 6, 4, 1, 4]
        step_sec = 0.30
        n_steps = int((duration - 1.4) / step_sec)
        for s in range(n_steps):
            t_note = 0.30 + s * step_sec
            in_burst_head = 27.9 <= t_note <= 31.2
            vel = 0.048 if in_burst_head else (0.104 if s % 4 == 0 else (0.080 if s % 2 == 0 else 0.062))

            deg = booth_motif[s % len(booth_motif)]
            if (s // 8) % 2 == 1 and s % 4 == 2:
                deg = (deg + 2) % len(scale_mid)
            f_main = scale_mid[deg]
            freqs = [f_main, scale_low[deg % len(scale_low)]] if s % 4 == 0 else [f_main]
            note_clip = crystal_note(
                freqs,
                dur=1.55,
                decay_tau=0.62 if s % 2 == 0 else 0.42,
                attack_tau=0.008,
                amp=vel,
                echo_taps=[(0.30, 0.22), (0.60, 0.10)],
            )
            add_at(master, note_clip, t_note)

            if s % 8 == 0:
                bass_roots = [F_C2, F_G2, F_D3, F_E3, F_G2, F_C2]
                b_freq = bass_roots[(s // 8) % len(bass_roots)]
                bass_clip = crystal_note(
                    [b_freq, b_freq * 2.0],
                    dur=2.10,
                    decay_tau=0.90,
                    attack_tau=0.020,
                    amp=0.10,
                    echo_taps=[(0.45, 0.14)],
                )
                add_at(master, bass_clip, t_note)

        # (a) North Desk Morse Key ("GO-9 SWL 1978") CW crystal pips at 6.2s..8.4s ("G O 9")
        cw_offsets = [(6.20, 0.18), (6.44, 0.18), (6.68, 0.07), (6.95, 0.18), (7.19, 0.18), (7.43, 0.18), (7.75, 0.18), (7.99, 0.18)]
        for t_cw, cw_d in cw_offsets:
            cw_pip = crystal_note([F_FS5, F_FS6], dur=cw_d + 0.25, decay_tau=0.12, attack_tau=0.003, amp=0.055, echo_taps=[(0.18, 0.16)])
            add_at(master, cw_pip, t_cw)

        # (b) East Bay (ED-9 Euclidean Vector Plotter) brass verification bell chime at 15.60s
        ed9_bell = crystal_note(
            [F_G5, F_D6, F_FS6, F_B5],
            dur=2.80,
            decay_tau=1.10,
            attack_tau=0.004,
            amp=0.14,
            echo_taps=[(0.32, 0.26), (0.64, 0.12)],
        )
        add_at(master, ed9_bell, 15.60)

        # (c) South Bay (PSR B1937+21 Pulsar Metronome & 3D Armillary Sphere) phase-lock ticks at 21.2s..24.4s
        for p_idx in range(8):
            t_p = 21.20 + p_idx * 0.40
            p_tick = crystal_note([641.93, 1283.86], dur=0.35, decay_tau=0.09, attack_tau=0.003, amp=0.048, echo_taps=[(0.20, 0.15)])
            add_at(master, p_tick, t_p)

        # (d) West Bay (Marzelvane HV-4 Klystron Exciter) 4-Ring Power-Up (t = 28.00s) & Spire Lock Burst (t = 29.80s)
        chime_clip = synth_marzelvane_burst_chime(
            variant=2,
            dur=7.60,
            ring_step=0.40,
            spire_lock_offset=1.80,
        )
        add_at(master, chime_clip, 28.00, gain=0.92)
    elif mode == "booth_loop":
        # Seamless 48.00s Unhurried Watchroom Rounds & Star-Shift Loop:
        # 120 periodic steps (120 * 0.40s = 48.00s) + Solar Window Shimmer, ED-9 Bell, Pulsar Ticks & West Burst!
        loop_motif = [0, 4, 7, 6, 4, 3, 4, 7, 10, 9, 7, 6, 4, 2, 4, 6]
        step_sec = 0.40
        n_steps = int(round(duration / step_sec))
        for s in range(n_steps):
            t_note = s * step_sec
            in_burst_head = 39.2 <= t_note <= 43.0
            vel = 0.046 if in_burst_head else (0.098 if s % 4 == 0 else (0.075 if s % 2 == 0 else 0.058))

            deg = loop_motif[s % len(loop_motif)]
            if (s // 8) % 2 == 1 and s % 4 == 2:
                deg = (deg + 2) % len(scale_mid)
            f_main = scale_mid[deg]
            freqs = [f_main, scale_low[deg % len(scale_low)]] if s % 4 == 0 else [f_main]
            note_clip = crystal_note(
                freqs,
                dur=1.85,
                decay_tau=0.72 if s % 2 == 0 else 0.48,
                attack_tau=0.010,
                amp=vel,
                echo_taps=[(0.40, 0.22), (0.80, 0.10)],
            )
            add_at(master, note_clip, t_note)

            if s % 8 == 0:
                bass_roots = [F_C2, F_G2, F_D3, F_E3, F_G2]
                b_freq = bass_roots[(s // 8) % len(bass_roots)]
                bass_clip = crystal_note(
                    [b_freq, b_freq * 2.0],
                    dur=2.60,
                    decay_tau=1.10,
                    attack_tau=0.024,
                    amp=0.096,
                    echo_taps=[(0.50, 0.14)],
                )
                add_at(master, bass_clip, t_note)

        # (a) Window Look-Up #1 (6.20s..9.80s): Looking out NE/East Panoramic Window at the Shifting Sun (SOL)
        solar_chord = crystal_note(
            [F_D5, F_FS5, F_A5, F_B5, F_D6],
            dur=3.40,
            decay_tau=1.45,
            attack_tau=0.030,
            amp=0.115,
            echo_taps=[(0.42, 0.26), (0.84, 0.14)],
        )
        add_at(master, solar_chord, 7.20)

        # (b) Console Stop #2 (12.40s..15.80s): Perpendicular Inspection of East ED-9 Vector CRT & Brass Flatbed Plotter
        ed9_bell = crystal_note(
            [F_G5, F_D6, F_FS6, F_B5],
            dur=3.00,
            decay_tau=1.20,
            attack_tau=0.004,
            amp=0.135,
            echo_taps=[(0.38, 0.25), (0.76, 0.12)],
        )
        add_at(master, ed9_bell, 13.80)

        # (c) Console Stop #3 (24.40s..27.80s) & Window Look-Up #3 (30.80s..34.00s): South Armillary & Pulsar PSR B1937+21
        for p_idx in range(8):
            t_p = 30.60 + p_idx * 0.45
            p_tick = crystal_note([641.93, 1283.86], dur=0.38, decay_tau=0.10, attack_tau=0.003, amp=0.050, echo_taps=[(0.22, 0.16)])
            add_at(master, p_tick, t_p)

        # (d) Console Stop #4 (36.80s..40.20s) & Window Look-Up #4 (42.40s..45.20s): West HV-4 Klystron Burst
        chime_clip = synth_marzelvane_burst_chime(
            variant=2,
            dur=7.40,
            ring_step=0.40,
            spire_lock_offset=1.80,
        )
        add_at(master, chime_clip, 39.40, gain=0.92)
    else:
        # Satellite Orbit: Crystalline zero-gravity C-Lydian / F-Lydian celestial counterpoint
        # + Van Allen Cyan/Amber strobe telemetry harmonic pips (every 0.80s = 1.25 Hz)
        orbit_motif = [4, 7, 10, 11, 9, 7, 5, 8, 11, 7, 6, 4, 2, 6, 8, 10]
        step_sec = 0.3333
        n_steps = int((duration - 1.4) / step_sec)
        for s in range(n_steps):
            t_note = 0.30 + s * step_sec
            in_burst_head = any(abs(t_note - b_t) < 0.95 for b_t in (2.5, 12.5, 22.5))
            vel = 0.050 if in_burst_head else (0.110 if s % 3 == 0 else 0.078)

            deg = orbit_motif[s % len(orbit_motif)]
            if (s // 6) % 2 == 1 and s % 4 == 2:
                deg = (deg + 2) % len(scale_mid)
            f_main = scale_mid[deg]
            freqs = [f_main, f_main * 0.5] if s % 3 == 0 else [f_main]
            note_clip = crystal_note(
                freqs,
                dur=1.85,
                decay_tau=0.75,
                attack_tau=0.010,
                amp=vel,
                echo_taps=[(0.42, 0.28), (0.84, 0.15), (1.26, 0.07)],
            )
            add_at(master, note_clip, t_note)

        # Van Allen Strobe Beacon harmonic telemetry pips synced to `Math.floor(t * 1.25) % 2` (every 0.80s)
        for b_idx in range(int(duration * 1.25)):
            t_strobe = b_idx * 0.80
            if t_strobe >= duration - 0.6:
                break
            # Alternating Cyan (high F#5/B5 harmonic ping) & Amber (warm D5/G4 fifth ping)
            is_cyan = (b_idx % 2) == 0
            pip_freqs = [F_FS5, F_B5] if is_cyan else [F_D5, F_G4]
            pip = crystal_note(
                pip_freqs,
                dur=0.55,
                decay_tau=0.16,
                attack_tau=0.004,
                amp=0.042,
                echo_taps=[(0.24, 0.18)],
            )
            add_at(master, pip, t_strobe)

        # Overlay the 3 Synchronized Orbital Marzelvane 4-Ring + Spire Lock Bursts!
        burst_schedule = [
            (2.00, 0, 5.80),
            (12.00, 1, 5.80),
            (22.00, 2, 7.60),
        ]
        for t_b, variant, b_dur in burst_schedule:
            chime_clip = synth_marzelvane_burst_chime(variant=variant, dur=b_dur)
            add_at(master, chime_clip, t_b, gain=0.95)

    if is_loop_mode:
        # Wrap the post-duration reverb/pad tail onto the head of the loop and apply a 40ms micro-crossfade for zero-seam looping
        tail = master[n_total:]
        master = master[:n_total].copy()
        master[: len(tail)] += tail
        xf = int(0.04 * SAMPLE_RATE)
        if xf > 0:
            w = np.linspace(0.0, 1.0, xf)
            head_orig = master[:xf].copy()
            master[:xf] = head_orig * w + master[-xf:] * (1.0 - w)
            master[-xf:] = master[-xf:] * w + head_orig * (1.0 - w)
    else:
        # 4. Soft fade-in (0..0.35s) and smooth cosine fade-out (last 1.20s)
        fade_in = int(0.35 * SAMPLE_RATE)
        master[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
        fade_out = int(1.20 * SAMPLE_RATE)
        master[-fade_out:] *= 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, fade_out)))

    # Soft peak limiting so chords never clip
    peak = float(np.max(np.abs(master)))
    if peak > 0.92:
        master *= 0.92 / peak

    return np.clip(master, -0.95, 0.95)


# ═══════════════════════════════════════════════════════════════════════════
# 2. IN-MEMORY WEBGL 30FPS CAPTURE ENGINE FOR DRONE TOUR & SATELLITE ORBIT
# ═══════════════════════════════════════════════════════════════════════════

INJECTED_TOUR_JS = r"""
    // ═════════════════════════════════════════════════════════════════
    // DETERMINISTIC 30FPS CAMERA PATH & SATELLITE ORBIT CAPTURE ENGINE
    // (Loads per-project videos/<project>/camera_path.json in memory
    //  without modifying docs/tower-3d.html on disk)
    // ═════════════════════════════════════════════════════════════════
    let _lastHudState = -1;

    function evalMonotonicCubic(xs, ys, xQuery, isPeriodicSlope) {
      const n = xs.length;
      const dxs = [];
      const dys = [];
      const ms = [];
      for (let i = 0; i < n - 1; i++) {
        const dx = xs[i + 1] - xs[i];
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
      const coordSys = cfg.coordinate_system || 'tower_cylindrical';
      const angleScale = (cfg.angle_unit === 'deg' || cfg.angle_unit === 'degrees') ? (Math.PI / 180.0) : 1.0;
      const origin = cfg.origin || [0.0, 0.0, 0.0];
      const ox = origin[0] || 0.0;
      const oy = origin[1] || 0.0;
      const oz = origin[2] || 0.0;

      if (coordSys === 'tower_cylindrical' || coordSys === 'cylindrical') {
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
        // Spherical orbit (camAz, camEl, camR) around target (lookX, lookY, lookZ) — ideal for reactors, pellets, artifacts
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

    function setTourStateAtTime(mode, t, duration) {
      const cfg = typeof CAMERA_PATH_CONFIG !== 'undefined' ? CAMERA_PATH_CONFIG : { mode, duration, is_loop: false };
      const targetW = typeof STUDIO_TARGET_W !== 'undefined' ? STUDIO_TARGET_W : 2560;
      const targetH = typeof STUDIO_TARGET_H !== 'undefined' ? STUDIO_TARGET_H : 1440;

      // Hide HTML HUD overlays for clean 16:9 QHD cinema capture
      const defaultSelectors = ['.top-nav', '#hud-left', '#hud-right', '#hud-bottom', '.hud-overlay', '.ui-panel'];
      const customSelectors = cfg.hide_selectors || [];
      for (const sel of defaultSelectors.concat(customSelectors)) {
        document.querySelectorAll(sel).forEach((el) => {
          el.style.display = 'none';
        });
      }

      // Universal Model Animation Hook: if the 3D model defines `window.setModelStateAtTime(t, duration, cfg)`
      // or `window.setModelTime(t, duration, cfg)`, invoke it at exact frame time `t`!
      if (typeof window.setModelStateAtTime === 'function') {
        window.setModelStateAtTime(t, duration, cfg);
      } else if (typeof window.setModelTime === 'function') {
        window.setModelTime(t, duration, cfg);
      }

      // If this is NOT `tower-3d.html` (e.g., Dilithium Reactor, Pellets, or another 3D model),
      // apply the evaluated camera pose directly and render the Three.js scene!
      if (typeof marzelRings === 'undefined' || typeof ors351Sat === 'undefined') {
        const pose = evalCameraPathPose(cfg, t, duration);
        camera.fov = pose.fov;
        camera.aspect = targetW / targetH;
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
        if (renderer.domElement.width !== targetW || renderer.domElement.height !== targetH) {
          renderer.setPixelRatio(1);
          renderer.setSize(targetW, targetH, false);
        }
        renderer.render(scene, camera);
        return;
      }

      // Ensure Station, Tower, and Booth ON AIR lights are 100% energized
      matTowerAmber.color.setHex(0xffaa2b);
      matTowerCyan.color.setHex(0x38e8ff);
      matTowerSpireCore.color.setHex(0xb8f8ff);
      matTowerCrimson.color.setHex(0xff1408);
      towerStructureLight.intensity = 5.5;
      habLight.intensity = 4.5;
      reactorLight.intensity = 6.0;

      matBoothRedGlow.color.setHex(0xe60804);
      matCrimsonGlow.color.setHex(0xff1408);
      matMicTally.color.setHex(0xff1408);
      boothInKneeMats.forEach((m) => {
        m.emissiveIntensity = 0.08;
      });
      ceilingSoffit.material.emissiveIntensity = 0.12;
      boothWarmLight.intensity = 7.5;
      deskFillLight.intensity = 3.8;
      boothBeaconLight.intensity = 12.0;

      const isBoothLoop = mode === 'booth_loop';
      const isDroneLoop = mode === 'drone_loop';
      const isLoop = !!cfg.is_loop || isBoothLoop || isDroneLoop;
      const loopPhase = (t / duration) * Math.PI * 2.0;

      // 1. O.R.S. 351 Satellite Position
      if (isBoothLoop) {
        // In 'booth_loop' mode: periodic halo drift across the South/SW panoramic window at t = 30.8s..34.0s (loopPhase ≈ 4.19 rad)!
        const satAz = 3.68 + 0.36 * Math.sin(loopPhase - 1.0472);
        const satElY = BOOTH_Y + 92.0 + 18.0 * Math.cos(loopPhase);
        ors351Sat.position.set(385.0 * Math.sin(satAz), satElY, -385.0 * Math.cos(satAz));
        ors351Sat.lookAt(satOrbitCenter);
        ors351Sat.updateMatrixWorld(true);
      } else {
        const satPhase = (mode === 'satellite_orbit' || isLoop)
          ? (t / duration) * Math.PI * 2.0
          : t * 0.12;
        ors351Sat.position
          .copy(satOrbitCenter)
          .addScaledVector(satOrbitU1, satOrbitR * Math.cos(satPhase))
          .addScaledVector(satOrbitU2, satOrbitR * Math.sin(satPhase));
        ors351Sat.lookAt(satOrbitCenter);
        ors351Sat.updateMatrixWorld(true);
      }

      // 2. Camera Trajectory from videos/<project>/camera_path.json
      if (cfg.coordinate_system === 'satellite_locked' || mode === 'satellite_orbit') {
        const satCam = cfg.satellite_cam || {};
        camera.fov = satCam.fov || 42.0;
        camera.updateProjectionMatrix();
        camera.position.copy(satCamLocalPos).applyMatrix4(ors351Sat.matrixWorld);
        controls.target.copy(satCamLocalTarget).applyMatrix4(ors351Sat.matrixWorld);
      } else {
        const pose = evalCameraPathPose(cfg, t, duration);
        camera.fov = pose.fov;
        camera.updateProjectionMatrix();
        camera.position.set(pose.camX, pose.camY, pose.camZ);
        controls.target.set(pose.targetX, pose.targetY, pose.targetZ);
      }

      // 3. Asynchronous Console Screen Cycling inside the Broadcast Booth (periodic in loop modes)
      const cState = isLoop ? (Math.floor((t / duration) * 16.0) % 4) : (Math.floor(t / 2.5) % 4);
      if (_lastHudState !== cState && typeof renderBroadcastShowDashboard === 'function') {
        _lastHudState = cState;
        renderBroadcastShowDashboard(cState);
      }
      CONSOLE_BAYS.forEach((bay, bIdx) => {
        if (bay.machineType === 'broadcast_cockpit_3screen') return;
        const idx = isLoop
          ? (Math.floor((t / duration) * 12.0 + bIdx) % bay.screens.length)
          : (Math.floor(t / bay.cyclePeriod + bIdx) % bay.screens.length);
        if (bay.screenStateIdx !== idx && bay.screenTextures && bay.screenTextures[idx] && bay.screenMat) {
          bay.screenStateIdx = idx;
          bay.screenMat.map = bay.screenTextures[idx];
          bay.screenMat.needsUpdate = true;
        }
      });

      // 4. Synchronized Marzelvane 4-Ring Power-Up & Barycentric Cherenkov Burst!
      const isDrone = cfg.coordinate_system === 'tower_cylindrical' || mode === 'drone_tour' || mode === 'drone_loop';
      const isBooth = mode === 'booth_tour';
      const burstCfg = cfg.bursts || {};
      const burstStarts = burstCfg.starts || (mode === 'drone_tour' ? [20.60] : (mode === 'drone_loop' ? [43.20] : (isBooth ? [28.00] : (isBoothLoop ? [39.40] : [2.00, 12.00, 22.00]))));
      const isSingleFinale = burstStarts.length === 1 || isDrone || isBooth || isLoop;
      const burstDur = burstCfg.duration || (isDrone ? 7.80 : (isBooth ? 7.40 : (isBoothLoop ? 7.40 : 5.60)));
      const ringStep = burstCfg.ring_step || (isDrone ? 0.45 : (isBooth ? 0.40 : (isBoothLoop ? 0.40 : 0.20)));
      const spireLockOffset = burstCfg.spire_lock_offset || (isDrone ? 1.95 : (isBooth ? 1.80 : (isBoothLoop ? 1.80 : 0.84)));
      let activeBt = -1.0;
      let activeBurstIdx = -1;
      for (let bi = 0; bi < burstStarts.length; bi++) {
        const dtB = t - burstStarts[bi];
        if (dtB >= 0.0 && dtB <= burstDur) {
          activeBt = dtB;
          activeBurstIdx = bi;
          break;
        }
      }

      let climaxFlash = 0.0;
      let coreSurge = 0.0;
      if (activeBt >= 0.0) {
        if (activeBt >= spireLockOffset - 0.06) {
          const rise = smoothstep(spireLockOffset - 0.06, spireLockOffset + 0.20, activeBt);
          const dtAfter = Math.max(0.0, activeBt - (spireLockOffset + 0.20));
          const fall = Math.exp(-dtAfter / 2.25) * (1.0 - smoothstep(burstDur - 1.20, burstDur, activeBt));
          climaxFlash = rise * fall * (isSingleFinale || activeBurstIdx === 2 ? 1.22 : 1.0);
        }
        coreSurge = smoothstep(0.0, 0.28, activeBt) * (1.0 - smoothstep(burstDur - 1.40, burstDur, activeBt));
      }

      const satBoost = mode === 'satellite_orbit' ? 1.35 : 1.0;
      const idlePhase = isLoop ? (loopPhase * 29.0) : (t * 3.4);
      let totalRingEnergy = 0.0;

      marzelRings.forEach((ring, rIdx) => {
        const idleWave = 0.5 + 0.5 * Math.sin(idlePhase - ring.phaseOffset);
        let ringCharge = 0.0;
        let ignFlash = 0.0;
        let spokeSurge = 0.0;

        if (activeBt >= 0.0) {
          const tRingNote = rIdx * ringStep;
          const tRingFull = tRingNote + (isSingleFinale ? 0.34 : 0.18);
          const rampUp = smoothstep(tRingNote, tRingFull, activeBt);
          const dtHold = Math.max(0.0, activeBt - spireLockOffset);
          const coolDown = Math.exp(-dtHold / (2.25 + rIdx * 0.22)) * (1.0 - smoothstep(burstDur - 1.20, burstDur, activeBt));
          ringCharge = rampUp * coolDown;

          if (activeBt >= tRingNote && activeBt <= tRingFull + 0.32) {
            ignFlash = Math.sin(smoothstep(tRingNote, tRingFull + 0.32, activeBt) * Math.PI);
          }
          if (activeBt >= tRingNote - 0.12 && activeBt <= tRingFull + 0.16) {
            spokeSurge = Math.sin(smoothstep(tRingNote - 0.12, tRingFull + 0.16, activeBt) * Math.PI);
          }
        }

        const e = Math.min(1.6, ringCharge + 0.72 * ignFlash + 0.90 * climaxFlash);
        totalRingEnergy += e;

        const w = Math.min(1.0, idleWave * 0.65 + e * 0.85);
        const whiteMix = Math.min(1.0, 0.58 * ringCharge + 0.78 * ignFlash + 0.88 * climaxFlash);

        ring.glowMatTop.color.setRGB(
          Math.min(1.0, 0.18 + 0.45 * w + 0.55 * whiteMix),
          Math.min(1.0, 0.82 + 0.18 * w + 0.18 * whiteMix),
          1.0
        );
        ring.glowMatBot.color.setRGB(
          Math.min(1.0, 0.35 + 0.55 * w + 0.40 * whiteMix),
          Math.min(1.0, 0.92 + 0.08 * w + 0.08 * whiteMix),
          1.0
        );
        const tubeScale = (1.0 + 0.80 * ringCharge + 0.70 * ignFlash + 0.90 * climaxFlash) * satBoost;
        ring.glowTop.scale.set(1.0, 1.0, tubeScale);
        ring.glowBot.scale.set(1.0, 1.0, tubeScale);

        ring.innerHaloMat.opacity = Math.min(
          0.62,
          (0.10 + 0.06 * idleWave + 0.28 * ringCharge + 0.20 * ignFlash + 0.24 * climaxFlash) * satBoost
        );
        ring.innerHaloMat.color.setRGB(
          Math.min(1.0, 0.26 + 0.66 * whiteMix),
          Math.min(1.0, 0.90 + 0.10 * whiteMix),
          1.0
        );
        const innerScale = 1.0 + 0.42 * ringCharge + 0.52 * ignFlash + 0.68 * climaxFlash;
        ring.innerHalo.scale.set(1.0, 1.0, innerScale);

        ring.outerHaloMat.opacity = Math.min(
          0.38,
          (0.04 + 0.02 * idleWave + 0.16 * ringCharge + 0.12 * ignFlash + 0.16 * climaxFlash) * satBoost
        );
        const outerScale = 1.0 + 0.55 * ringCharge + 0.65 * ignFlash + 0.90 * climaxFlash;
        ring.outerHalo.scale.set(1.0, 1.0, outerScale);

        ring.superHaloMat.opacity = Math.min(
          0.22,
          (0.08 * ringCharge + 0.10 * ignFlash + 0.14 * climaxFlash) * satBoost
        );
        const superScale = 1.0 + 0.55 * ringCharge + 1.05 * climaxFlash;
        ring.superHalo.scale.set(1.0, 1.0, superScale);

        ring.spokeGlowMat.opacity = Math.min(
          0.90,
          0.08 + 0.45 * ringCharge + 0.62 * spokeSurge + 0.42 * climaxFlash
        );
        ring.spokeGlowMat.color.setRGB(
          Math.min(1.0, 0.25 + 0.75 * (spokeSurge + climaxFlash)),
          0.95,
          1.0
        );

        ring.tipMat.color.setRGB(
          Math.min(1.0, 0.55 + 0.45 * (ringCharge + ignFlash + climaxFlash)),
          Math.min(1.0, 0.94 + 0.06 * ringCharge),
          1.0
        );
        ring.tipSpriteMat.opacity = Math.min(
          0.96,
          0.38 + 0.10 * idleWave + 0.48 * ringCharge + 0.32 * ignFlash + 0.34 * climaxFlash
        );
        const spScale =
          (0.86 + 0.14 * idleWave + 1.45 * ringCharge + 1.20 * ignFlash + 1.60 * climaxFlash) * satBoost;
        ring.tipSprites.forEach((sp, sIdx) => {
          const mult = sIdx % 2 === 0 ? 1.0 : 0.82;
          sp.scale.set(spScale * mult, spScale * mult, 1.0);
        });
      });

      const meanRingEnergy = totalRingEnergy * 0.25;
      const idleHubPulse = 0.5 + 0.5 * Math.sin(idlePhase);
      hubCoreGlowMat.opacity = Math.min(0.82, 0.15 + 0.06 * idleHubPulse + 0.38 * coreSurge + 0.44 * climaxFlash);
      spireAuraMat.opacity = Math.min(0.55, 0.05 + 0.03 * idleHubPulse + 0.20 * meanRingEnergy + 0.36 * climaxFlash);

      const hubScale = hubFlare.baseScale * satBoost * (0.95 + 0.10 * idleHubPulse + 1.15 * coreSurge + 1.75 * climaxFlash);
      hubFlare.sprite.scale.set(hubScale, hubScale, 1.0);
      hubFlare.mat.opacity = Math.min(0.90, hubFlare.baseOpacity + 0.32 * coreSurge + 0.40 * climaxFlash);

      const midScale = midSpireFlare.baseScale * satBoost * (0.95 + 0.10 * idleHubPulse + 0.95 * meanRingEnergy + 1.85 * climaxFlash);
      midSpireFlare.sprite.scale.set(midScale, midScale, 1.0);
      midSpireFlare.mat.opacity = Math.min(0.88, midSpireFlare.baseOpacity + 0.28 * meanRingEnergy + 0.42 * climaxFlash);

      const apexScale = apexSpireFlare.baseScale * satBoost * (0.95 + 0.12 * idleHubPulse + 1.05 * meanRingEnergy + 2.45 * climaxFlash);
      apexSpireFlare.sprite.scale.set(apexScale, apexScale, 1.0);
      apexSpireFlare.mat.opacity = Math.min(0.92, apexSpireFlare.baseOpacity + 0.28 * meanRingEnergy + 0.42 * climaxFlash);

      // Expanding Barycentric Shockwave Rings & Spherical Discharge Wave!
      const maxSwRad = mode === 'satellite_orbit' ? 115.0 : 82.0;
      const swDur = (isDrone || isLoop) ? 3.80 : 3.10;
      marzelShockwaves.forEach((sw, swIdx) => {
        const swStart = spireLockOffset + swIdx * 0.40;
        if (activeBt >= swStart && activeBt <= swStart + swDur) {
          const p = (activeBt - swStart) / swDur;
          const easeOut = 1.0 - Math.pow(1.0 - p, 1.65);
          const rad = 4.5 + maxSwRad * easeOut;
          sw.mesh.visible = true;
          sw.mesh.scale.set(rad, rad, 1.3 + 5.6 * p);
          sw.mesh.position.y = (swIdx - 0.5) * 3.0 * p;
          sw.mat.opacity = Math.sin(p * Math.PI) * Math.pow(1.0 - p, 0.85) * (mode === 'satellite_orbit' ? 0.65 : 0.56);
        } else {
          sw.mesh.visible = false;
          sw.mat.opacity = 0.0;
        }
      });

      const spDur = (isDrone || isLoop) ? 3.90 : 3.25;
      if (activeBt >= spireLockOffset && activeBt <= spireLockOffset + spDur) {
        const spP = (activeBt - spireLockOffset) / spDur;
        const spRad = 5.0 + (maxSwRad * 0.92) * (1.0 - Math.pow(1.0 - spP, 1.65));
        burstSphereMesh.visible = true;
        burstSphereMesh.scale.set(spRad, spRad * 0.62, spRad);
        burstSphereMat.opacity = Math.sin(spP * Math.PI) * Math.pow(1.0 - spP, 1.10) * (mode === 'satellite_orbit' ? 0.26 : 0.22);
      } else {
        burstSphereMesh.visible = false;
        burstSphereMat.opacity = 0.0;
      }

      marzelLight.intensity = 13.0 + 3.5 * Math.sin(idlePhase) + 28.0 * meanRingEnergy + 58.0 * climaxFlash;
      marzelBurstLight.intensity = 24.0 * meanRingEnergy + 115.0 * climaxFlash;

      // 5. Vertical "G / O / R / ◎ / 9" Sign Animated Sequence!
      //    Locks all 5 slots bright during the peak of each Marzelvane Burst, and runs the
      //    animated G -> O -> R -> ◎ -> 9 -> ALL LIT sequence between bursts!
      if (climaxFlash > 0.18) {
        const boost = Math.min(1.25, 0.95 + 0.30 * climaxFlash);
        signSlotMats.forEach((sm) => {
          sm.face.color.setRGB(0.88 * boost, 0.03 * boost, 0.0);
          sm.core.color.setRGB(1.0, 0.12 * boost, 0.04 * boost);
          sm.retGlow.color.setRGB(0.25 * boost, 0.94 * boost, 1.0);
          sm.retCore.color.setRGB(0.76 * boost, 0.98 * boost, 1.0);
        });
        signLightESE.color.setHex(0xff0804);
        signLightWNW.color.setHex(0xff0804);
        signLightESE.position.y = 42.0;
        signLightWNW.position.y = 42.0;
        signLightESE.intensity = 11.0 * boost;
        signLightWNW.intensity = 11.0 * boost;
      } else {
        const seqRate = isDroneLoop ? (24.0 / duration) : (isBoothLoop ? (56.0 / duration) : 2.4);
        const seqTimer = t * seqRate;
        const step = Math.floor(seqTimer) % 8;
        const subPhase = seqTimer - Math.floor(seqTimer);
        const slotPulse = 0.88 + 0.12 * Math.sin(subPhase * Math.PI);

        if (step <= 4) {
          // Progressive build-up: G -> G+O -> G+O+R -> G+O+R+◎ -> G+O+R+◎+9
          signSlotMats.forEach((sm, idx) => {
            const b = idx === step ? slotPulse : (idx < step ? 0.84 : 0.12);
            sm.face.color.setRGB(0.88 * b, 0.025 * b, 0.0);
            sm.core.color.setRGB(1.0 * b, 0.10 * b, 0.03 * b);
            sm.retGlow.color.setRGB(0.22 * b, 0.91 * b, 1.0 * b);
            sm.retCore.color.setRGB(0.72 * b, 0.97 * b, 1.0 * b);
          });
          const activeY = SIGN_SLOT_Y[step];
          const isRingStep = step === 3;
          signLightESE.color.setHex(isRingStep ? 0x38e8ff : 0xff0804);
          signLightWNW.color.setHex(isRingStep ? 0x38e8ff : 0xff0804);
          signLightESE.position.y = activeY;
          signLightWNW.position.y = activeY;
          signLightESE.intensity = 8.5 * slotPulse;
          signLightWNW.intensity = 8.5 * slotPulse;
        } else if (step === 5 || step === 6) {
          // All 5 slots lit together
          const allB = 0.94 + 0.06 * Math.sin(isLoop ? (loopPhase * 22.0) : (t * 6.0));
          signSlotMats.forEach((sm) => {
            sm.face.color.setRGB(0.88 * allB, 0.025 * allB, 0.0);
            sm.core.color.setRGB(1.0 * allB, 0.10 * allB, 0.03 * allB);
            sm.retGlow.color.setRGB(0.22 * allB, 0.91 * allB, 1.0 * allB);
            sm.retCore.color.setRGB(0.72 * allB, 0.97 * allB, 1.0 * allB);
          });
          signLightESE.color.setHex(0xff0804);
          signLightWNW.color.setHex(0xff0804);
          signLightESE.position.y = 42.0;
          signLightWNW.position.y = 42.0;
          signLightESE.intensity = 9.5 * allB;
          signLightWNW.intensity = 9.5 * allB;
        } else {
          // Step 7: Marzelvane reticle rings (◎) solo pulse before next cycle
          const ringB = 0.94;
          signSlotMats.forEach((sm) => {
            sm.face.color.setRGB(0.18, 0.01, 0.0);
            sm.core.color.setRGB(0.24, 0.02, 0.01);
            sm.retGlow.color.setRGB(0.22 * ringB, 0.91 * ringB, 1.0 * ringB);
            sm.retCore.color.setRGB(0.72 * ringB, 0.97 * ringB, 1.0 * ringB);
          });
          signLightESE.color.setHex(0x38e8ff);
          signLightWNW.color.setHex(0x38e8ff);
          signLightESE.position.y = SIGN_SLOT_Y[3];
          signLightWNW.position.y = SIGN_SLOT_Y[3];
          signLightESE.intensity = 7.5;
          signLightWNW.intensity = 7.5;
        }
      }

      // 6. Van Allen Cyan (#38e8ff) & Amber (#ffaa2b) Satellite Strobe Beacons (1.25 Hz alternating blink)
      const blinkSlot = isLoop ? (Math.floor((t / duration) * 68.0) % 2) : (Math.floor(t * 1.25) % 2);
      const cyanOn = blinkSlot === 0 ? 1.0 : 0.0;
      const amberOn = blinkSlot === 1 ? 1.0 : 0.0;
      if (cyanOn > 0.5) {
        satCyanBeaconMat.color.setHex(0x38e8ff);
        satAmberBeaconMat.color.setHex(0x221608);
      } else {
        satCyanBeaconMat.color.setHex(0x0a1e24);
        satAmberBeaconMat.color.setHex(0xffaa2b);
      }
      orbitalSatellites.forEach((sat) => {
        const distToCam = camera.position.distanceTo(sat.group.position);
        const isDistantView = distToCam > 60.0;
        const bodyDistFactor = isDistantView
          ? Math.min(3.4, 1.15 + (distToCam - 60.0) * 0.008)
          : 0.72;
        const towerFacingDistFactor = isDistantView
          ? Math.min(7.8, 2.4 + (distToCam - 60.0) * 0.022)
          : 0.60;

        sat.cyanFlares.forEach((fl) => {
          const df = fl.isTowerFacing ? towerFacingDistFactor : bodyDistFactor;
          const s = fl.baseScale * df;
          fl.sprite.scale.set(s, s, 1.0);
          fl.mat.opacity = (fl.isTowerFacing ? (isDistantView ? 0.90 : 0.36) : 0.52) * cyanOn;
        });
        sat.amberFlares.forEach((fl) => {
          const df = fl.isTowerFacing ? towerFacingDistFactor : bodyDistFactor;
          const s = fl.baseScale * df;
          fl.sprite.scale.set(s, s, 1.0);
          fl.mat.opacity = (fl.isTowerFacing ? (isDistantView ? 0.90 : 0.36) : 0.52) * amberOn;
        });
        sat.amberLights[0].intensity = 2.8 * amberOn;
        sat.amberLights[1].intensity = 2.0 * amberOn;
        sat.cyanLights[0].intensity = 2.8 * cyanOn;
        sat.cyanLights[1].intensity = 2.0 * cyanOn;
      });

      // 7. Asteroid Sidereal Spin, Pulsar Armillary Spin & Tumbling Main-Belt Asteroids
      const spinAngle = isDroneLoop ? (0.18 * Math.sin(loopPhase)) : (isBoothLoop ? (0.30 * Math.sin(loopPhase - 1.0472)) : (t * 0.018));
      skyGroup.rotation.y = -spinAngle;
      skyGroup.rotation.x = isLoop ? (0.042 * Math.sin(loopPhase)) : (0.038 * Math.sin(spinAngle * 0.5));
      const starMapUVShift = isLoop
        ? (((t / duration) % 1.0 + 1.0) % 1.0)
        : (((spinAngle / (Math.PI * 2.0)) % 1.0 + 1.0) % 1.0);
      starMapPanTextures.forEach((stTex) => {
        stTex.offset.x = starMapUVShift;
      });
      if (armillarySpinGroup) {
        armillarySpinGroup.rotation.y = isLoop ? (-loopPhase * 2.0) : (-t * 0.45);
      }
      driftingAsteroids.forEach((a, idx) => {
        if (isLoop) {
          a.mesh.rotation.x = idx * 0.7 + loopPhase * (idx % 2 === 0 ? 1.0 : -1.0);
          a.mesh.rotation.y = idx * 1.3 + loopPhase * 1.0;
        } else {
          a.mesh.rotation.x = idx * 0.7 + t * a.rx * 30.0;
          a.mesh.rotation.y = idx * 1.3 + t * a.ry * 30.0;
        }
      });

      controls.enableDamping = false;
      if (renderer.domElement.width !== 2560 || renderer.domElement.height !== 1440) {
        renderer.setPixelRatio(1);
        renderer.setSize(2560, 1440, false);
      }
      camera.aspect = 2560 / 1440;
      camera.updateProjectionMatrix();
      controls.update();
      renderer.render(scene, camera);
    }

    async function runTourCapture() {
      const params = new URLSearchParams(window.location.search);
      const mode = params.get('mode') || 'drone_tour';
      const fps = parseFloat(params.get('fps') || '30');
      const duration = parseFloat(params.get('dur') || '30.0');
      const wid = params.get('wid') || '0';
      const pairsStr = params.get('pairs') || '';
      const pairs = pairsStr
        ? pairsStr.split(',').map((s) => {
            const [idxS, tS] = s.split(':');
            return { idx: parseInt(idxS, 10), t: parseFloat(tS) };
          })
        : [];

      // Wait for all Three.js textures and showQuadImages to finish loading
      await new Promise((resolve) => {
        let settled = false;
        const done = () => {
          if (!settled) {
            settled = true;
            setTimeout(resolve, 600);
          }
        };
        THREE.DefaultLoadingManager.onLoad = done;
        setTimeout(done, 2400);
      });
      _lastHudState = -1;

      // Upgrade shockwave rings & discharge sphere to high-segment geometry for 30fps radiation
      if (typeof marzelShockwaves !== 'undefined') {
        marzelShockwaves.forEach((sw) => {
          sw.mesh.geometry.dispose();
          sw.mesh.geometry = new THREE.TorusGeometry(1.0, 0.040, 32, 128);
        });
      }
      if (typeof burstSphereMesh !== 'undefined') {
        burstSphereMesh.geometry.dispose();
        burstSphereMesh.geometry = new THREE.SphereGeometry(1.0, 64, 48);
      }

      const cfg = typeof CAMERA_PATH_CONFIG !== 'undefined' ? CAMERA_PATH_CONFIG : { mode };
      // Ensure circular CRT scopes in East (ED-9 Vector Scope) & SE (Bogey-9 PPI Scope) sit proud of their dark barrels,
      // and when hide_interior_legs is enabled (or in booth/close-up drone modes) clear the 4 interior diagonal leg cylinders (y = 26.0..28.9m, R ≈ 2.65m) so all 8 console bays have an unobstructed view
      if ((cfg.hide_interior_legs || mode === 'booth_tour' || mode === 'booth_loop' || mode === 'drone_loop') && typeof towerGroup !== 'undefined') {
        towerGroup.children.forEach((ch) => {
          const r = Math.hypot(ch.position.x, ch.position.z);
          if (r > 1.5 && ch.position.y > BOOTH_Y + 0.05 && ch.position.y < BOOTH_Y + 2.95) {
            ch.visible = false;
          }
        });
      }
      function makeRadialCoronaTex(rCol, gCol, bCol) {
        const cnv = document.createElement('canvas');
        cnv.width = 256;
        cnv.height = 256;
        const ctx = cnv.getContext('2d');
        const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 126);
        g.addColorStop(0.00, 'rgba(255, 255, 255, 1.0)');
        g.addColorStop(0.09, 'rgba(255, 252, 240, 0.96)');
        g.addColorStop(0.18, `rgba(${rCol}, ${gCol}, ${bCol}, 0.82)`);
        g.addColorStop(0.36, `rgba(${rCol}, ${gCol}, ${bCol}, 0.34)`);
        g.addColorStop(0.64, `rgba(${rCol}, ${gCol}, ${bCol}, 0.09)`);
        g.addColorStop(0.88, `rgba(${rCol}, ${gCol}, ${bCol}, 0.018)`);
        g.addColorStop(1.00, 'rgba(0, 0, 0, 0.0)');
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, 256, 256);
        const tex = new THREE.CanvasTexture(cnv);
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.needsUpdate = true;
        return tex;
      }
      // Redraw satBeaconFlareTex.image in-place without crosshair bars so GPU texture has zero crosshairs
      if (typeof satBeaconFlareTex !== 'undefined' && satBeaconFlareTex.image) {
        const sCnv = satBeaconFlareTex.image;
        const sCtx = sCnv.getContext('2d');
        const w = sCnv.width || 128;
        const h = sCnv.height || 128;
        sCtx.clearRect(0, 0, w, h);
        const sg = sCtx.createRadialGradient(w * 0.5, h * 0.5, 0, w * 0.5, h * 0.5, w * 0.5);
        sg.addColorStop(0.00, 'rgba(255, 255, 255, 1.0)');
        sg.addColorStop(0.16, 'rgba(240, 252, 255, 0.92)');
        sg.addColorStop(0.42, 'rgba(160, 225, 255, 0.38)');
        sg.addColorStop(1.00, 'rgba(0, 0, 0, 0.0)');
        sCtx.fillStyle = sg;
        sCtx.fillRect(0, 0, w, h);
        satBeaconFlareTex.needsUpdate = true;
      }
      const satCleanGlowTex = makeRadialCoronaTex(235, 250, 255);
      if (typeof satGroup !== 'undefined') {
        satGroup.traverse((obj) => {
          if (obj.isSprite && obj.material) {
            obj.material.map = satCleanGlowTex;
            obj.material.needsUpdate = true;
          }
        });
      }
      if (typeof orbitalSatellites !== 'undefined') {
        orbitalSatellites.forEach((sat) => {
          sat.cyanFlares.forEach((fl) => {
            fl.mat.map = satCleanGlowTex;
            fl.mat.needsUpdate = true;
          });
          sat.amberFlares.forEach((fl) => {
            fl.mat.map = satCleanGlowTex;
            fl.mat.needsUpdate = true;
          });
        });
      }
      if (mode === 'booth_loop' && typeof skyGroup !== 'undefined') {
        // Build natural circular radial Solar Corona (SOL m=-3.62) & Pulsar Halo (PSR B1937+21) window beacons
        const solarCoronaTex = makeRadialCoronaTex(255, 204, 88);
        const pulsarCoronaTex = makeRadialCoronaTex(64, 234, 255);

        // 1. Blazing Distant Sun (SOL m = -3.62) at az0 = 53.5°, el = 13.8°, r = 1220m (transits NE/East window at t = 6.2..9.8s!)
        const solPos = celestialToVec3(53.5, 13.8, 1220);
        const solDisk = new THREE.Mesh(
          new THREE.SphereGeometry(13.5, 32, 24),
          new THREE.MeshBasicMaterial({ color: 0xfffef2, fog: false })
        );
        solDisk.position.copy(solPos);
        skyGroup.add(solDisk);
        const solChromosphere = new THREE.Mesh(
          new THREE.SphereGeometry(19.5, 32, 24),
          new THREE.MeshBasicMaterial({
            color: 0xffcc55,
            transparent: true,
            opacity: 0.45,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            fog: false,
          })
        );
        solChromosphere.position.copy(solPos);
        skyGroup.add(solChromosphere);
        const solGlowOuter = new THREE.Sprite(
          new THREE.SpriteMaterial({
            map: solarCoronaTex,
            color: 0xffcf68,
            transparent: true,
            opacity: 0.90,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            fog: false,
          })
        );
        solGlowOuter.position.copy(solPos);
        solGlowOuter.scale.set(250, 250, 1);
        skyGroup.add(solGlowOuter);

        // Reposition driftingAsteroids[0] near the solar transit path so a columnar-basalt asteroid drifts past the NE/East window!
        if (driftingAsteroids.length > 0) {
          const astPos0 = celestialToVec3(61.5, 11.8, 145);
          driftingAsteroids[0].mesh.position.copy(astPos0);
        }

        // 2. Millisecond Pulsar Beacon (PSR B1937+21) at az0 = 207.5°, el = 14.8°, r = 1220m (transits South/SW window at t = 30.8..34.0s, 154° away from SOL!)
        const psrPos = celestialToVec3(207.5, 14.8, 1220);
        const psrDisk = new THREE.Mesh(
          new THREE.SphereGeometry(7.5, 24, 20),
          new THREE.MeshBasicMaterial({ color: 0xe6feff, fog: false })
        );
        psrDisk.position.copy(psrPos);
        skyGroup.add(psrDisk);
        const psrGlow = new THREE.Sprite(
          new THREE.SpriteMaterial({
            map: pulsarCoronaTex,
            color: 0x38e8ff,
            transparent: true,
            opacity: 0.86,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            fog: false,
          })
        );
        psrGlow.position.copy(psrPos);
        psrGlow.scale.set(175, 175, 1);
        skyGroup.add(psrGlow);

        if (driftingAsteroids.length > 1) {
          const astPos1 = celestialToVec3(216.5, 12.4, 155);
          driftingAsteroids[1].mesh.position.copy(astPos1);
        }
      }
      if (typeof consolesGroup !== 'undefined') {
        const slopeTilt = 0.56;
        const ny = Math.sin(slopeTilt);
        const nz = Math.cos(slopeTilt);
        consolesGroup.traverse((obj) => {
          if (obj.isMesh && obj.geometry && obj.geometry.type === 'CircleGeometry') {
            if (Math.abs(obj.position.x - (-0.98)) < 0.05) {
              // East ED-9 Circular Vector CRT Scope (push +0.024m along slope normal proud of scopeBarrel)
              obj.position.y += 0.024 * ny;
              obj.position.z += 0.024 * nz;
              if (obj.parent) {
                obj.parent.children.forEach((sib) => {
                  if (sib.isMesh && sib.geometry && sib.geometry.type === 'TorusGeometry' && Math.abs(sib.position.x - obj.position.x) < 0.05) {
                    sib.position.y += 0.022 * ny;
                    sib.position.z += 0.022 * nz;
                  }
                });
              }
            } else if (Math.abs(obj.position.x - (-0.04)) < 0.05) {
              // SE Bogey-9 Circular Desk PPI Radar Scope (push +0.012m up proud of ppiTub)
              obj.position.y += 0.012;
              obj.position.z += 0.004;
              if (obj.parent) {
                obj.parent.children.forEach((sib) => {
                  if (sib.isMesh && sib.geometry && sib.geometry.type === 'TorusGeometry' && Math.abs(sib.position.x - obj.position.x) < 0.05) {
                    sib.position.y += 0.010;
                    sib.position.z += 0.003;
                  }
                });
              }
            }
          }
        });
      }

      // Force exact 2560x1440 (16:9 QHD) WebGL canvas dimensions
      renderer.setPixelRatio(1);
      renderer.setSize(2560, 1440, false);
      camera.aspect = 2560 / 1440;
      camera.updateProjectionMatrix();

      const gl = renderer.getContext();
      const pixelBuf = new Uint8Array(2560 * 1440 * 4);
      await fetch(`/__js_log`, { method: 'POST', body: `wid=${wid} ready, rendering ${pairs.length} frames at 2560x1440` });
      for (let i = 0; i < pairs.length; i++) {
        const { idx, t } = pairs[i];
        setTourStateAtTime(mode, t, duration);
        gl.finish();
        gl.readPixels(0, 0, 2560, 1440, gl.RGBA, gl.UNSIGNED_BYTE, pixelBuf);
        for (let attempt = 0; attempt < 5; attempt++) {
          try {
            const resp = await fetch(`/__raw_rgba/${idx}`, { method: 'POST', body: pixelBuf });
            if (resp.ok) break;
          } catch (err) {
            await new Promise((r) => setTimeout(r, 80 * (attempt + 1)));
          }
        }
      }
      for (let attempt = 0; attempt < 5; attempt++) {
        try {
          await fetch(`/__done/${wid}`, { method: 'POST' });
          break;
        } catch (err) {
          await new Promise((r) => setTimeout(r, 80));
        }
      }
    }

    runTourCapture().catch((err) => {
      fetch('/__js_log', { method: 'POST', body: 'JS_ERR: ' + String((err && err.stack) || err) });
    });
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


class _TourCaptureHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(
        self,
        *args,
        directory: str,
        frames_dir: Path,
        camera_path_cfg: dict,
        done_event: threading.Event,
        expected_workers: int,
        state: dict,
        lock: threading.Lock,
        **kwargs,
    ):
        self._frames_dir = frames_dir
        self._camera_path_cfg = camera_path_cfg
        self._done_event = done_event
        self._expected_workers = expected_workers
        self._state = state
        self._lock = lock
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args) -> None:
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/__capture_tour.html"):
            model_rel = self._camera_path_cfg.get("model", "docs/tower-3d.html")
            model_path = (ROOT / model_rel).resolve() if not Path(model_rel).is_absolute() else Path(model_rel)
            orig_html = model_path.read_text(encoding="utf-8")
            patched = orig_html.replace(
                "window.addEventListener('resize'",
                "window.addEventListener('__disabled_resize'",
            )
            cfg_js = f"    const CAMERA_PATH_CONFIG = {json.dumps(self._camera_path_cfg)};\n"
            if "    animate();\n  </script>" in patched:
                patched = patched.replace(
                    "    animate();\n  </script>",
                    cfg_js + INJECTED_TOUR_JS + "\n  </script>",
                    1,
                )
            elif "</script>" in patched:
                idx = patched.rfind("</script>")
                patched = patched[:idx] + "\n" + cfg_js + INJECTED_TOUR_JS + "\n" + patched[idx:]
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
                png_bytes = _rgba_bottom_up_to_png_bytes(data, 2560, 1440)
                out_path = self._frames_dir / f"frame_{idx + 1:04d}.png"
                out_path.write_bytes(png_bytes)
                with self._lock:
                    self._state["captured"] = self._state.get("captured", 0) + 1
                    self._state["last_capture_ts"] = time.monotonic()
                    c = self._state["captured"]
                    tf = self._state.get("total_frames", TOTAL_FRAMES)
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


class _ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def find_chrome_binary() -> str:
    pw_root = Path.home() / ".cache" / "ms-playwright"
    if pw_root.is_dir():
        for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
            return str(candidate)
    for c in ("google-chrome", "google-chrome-stable", "chromium-browser", "chromium", "/usr/bin/google-chrome", "/usr/bin/chromium"):
        p = shutil.which(c)
        if p:
            return p
    raise RuntimeError("No Chromium/Chrome binary found.")


def purge_torn_frames(frames_dir: Path, mode: str, audit_only: bool = False) -> list[int]:
    """Detect and optionally delete frames affected by headless window resize tears (duplicate top-32-row CRC groups)."""
    if not frames_dir.exists():
        return []
    row_stride = 1 + 2560 * 4  # filter byte (0) + 2560 * 4 RGBA bytes = 10241
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


def capture_mode_frames(
    mode: str,
    frames_dir: Path,
    camera_path_cfg: dict,
    duration: float,
    fps: int,
    clean: bool = False,
    workers: int = 3,
    target_indices: list[int] | None = None,
) -> None:
    if clean and frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    total_frames = int(round(duration * fps))
    if target_indices is not None:
        all_pairs = [(idx, idx / float(fps)) for idx in target_indices]
    else:
        all_pairs = [(idx, idx / float(fps)) for idx in range(total_frames)]
    chrome_bin = find_chrome_binary()

    for pass_num in range(1, 15):
        missing_pairs = [
            (idx, t)
            for idx, t in all_pairs
            if not (frames_dir / f"frame_{idx + 1:04d}.png").exists()
        ]
        if not missing_pairs:
            break

        actual_workers = min(workers, len(missing_pairs))
        shards = [missing_pairs[w::actual_workers] for w in range(actual_workers)]

        done_event = threading.Event()
        lock = threading.Lock()
        state = {
            "captured": len(all_pairs) - len(missing_pairs),
            "total_frames": len(all_pairs),
            "done_workers": 0,
            "last_capture_ts": time.monotonic(),
        }
        handler = functools.partial(
            _TourCaptureHTTPHandler,
            directory=str(DOCS_DIR),
            frames_dir=frames_dir,
            camera_path_cfg=camera_path_cfg,
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
            f"[{mode} Pass {pass_num}] Capturing {len(missing_pairs)} missing frames "
            f"(of {len(all_pairs)}) across {actual_workers} parallel WebGL workers on port {port}...",
            flush=True,
        )

        procs = []
        profiles = []
        for w, shard in enumerate(shards):
            tmp_profile = Path(f"/tmp/gor9_{mode}_profile_{os.getpid()}_{pass_num}_{w}")
            if tmp_profile.exists() and not tmp_profile.is_dir():
                tmp_profile.unlink(missing_ok=True)
            tmp_profile.mkdir(parents=True, exist_ok=True)
            profiles.append(tmp_profile)
            pairs_q = ",".join(f"{idx}:{t:.4f}" for idx, t in shard)
            url = (
                f"http://127.0.0.1:{port}/__capture_tour.html"
                f"?mode={mode}&fps={fps}&dur={duration:.2f}&wid={w}&pairs={pairs_q}"
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
                "--window-size=2560,1560",
                url,
            ]
            procs.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

        try:
            start_ts = time.monotonic()
            while not done_event.wait(timeout=0.5):
                now = time.monotonic()
                if now - start_ts > 600.0:
                    print(f"  [{mode} Pass {pass_num}] Pass timeout (600s) reached.", flush=True)
                    break
                if all(p.poll() is not None for p in procs):
                    break
                with lock:
                    idle_s = now - state.get("last_capture_ts", start_ts)
                    captured_now = state.get("captured", 0)
                if captured_now >= len(all_pairs):
                    break
                if idle_s > 180.0:
                    print(f"  [{mode} Pass {pass_num}] Workers idle for {idle_s:.1f}s; cycling pass...", flush=True)
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


def encode_qhd_mp4_from_frames(
    frames_dir: Path,
    audio_wav: Path,
    out_mp4: Path,
    out_thumb: Path,
    thumb_frame_idx: int,
    duration: float,
    fps: int = 30,
) -> None:
    """Encode native 2560x1440 30.00 fps PNG sequence + WAV audio to QHD High@L5.1 MP4 per STUDIO.md."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "/usr/bin/ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-start_number",
        "1",
        "-i",
        str(frames_dir / "frame_%04d.png"),
        "-i",
        str(audio_wav),
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True)
    print(f"Encoded 2560x1440 MP4 (direct ffmpeg) -> {out_mp4}", flush=True)

    hero_png = frames_dir / f"frame_{thumb_frame_idx:04d}.png"
    if hero_png.exists():
        subprocess.run(
            ["/usr/bin/ffmpeg", "-y", "-i", str(hero_png), "-q:v", "4", str(out_thumb)],
            check=True,
        )
        print(f"Exported Hero Thumbnail -> {out_thumb}", flush=True)


def ensure_tour_youtube_json(out_dir: Path, mode: str, cfg: dict | None = None) -> Path:
    yt_path = out_dir / "youtube.json"
    if mode == "drone_tour":
        meta = {
            "short_code": "DRONE-TOUR",
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": "GOR-9 • High Basalt Shelf Tower 360° Inspection Drone Tour (14,285.7 kHz USB • 0400 GCT)",
            "description": (
                "Autonomous 360° telemetry inspection flight around the 86.5m High Basalt Shelf Broadcast Tower "
                "on Asteroid 3-5-1, 42,100 AU out in Oort Cloud Sector 9.\n"
                "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
                "0:00 Acheron Chasm Approach & Octagonal Broadcast Booth Detail Orbit (+26.0m)\n"
                "0:11 Vertical G/O/R/◎/9 Sign Ascent & 4-Ring Marzelvane Crown Detail Orbit (+72.0m)\n"
                "0:21 Fly-Away Standoff & 50 kW Barycentric Cherenkov Shockwave Burst"
            ),
            "tags": ["GOR-9", "Galactic Outpost Radio", "Marzelvane", "Shortwave", "Sci-Fi"],
            "files": {
                "wide_1080p_mp4": str(out_dir / "gor9_drone_tour.mp4"),
                "thumbnail_16x9_png": str(out_dir / "gor9_drone_tour_thumb.jpg"),
            },
            "uploads": {},
            "history": {},
        }
    elif mode == "drone_loop":
        meta = {
            "short_code": "DRONE-LOOP",
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": "GOR-9 • Inverse-Keplerian Elliptical Drone Orbit Seamless Loop (14,285.7 kHz USB • 0400 GCT)",
            "description": (
                "Seamless 54-second Inverse-Keplerian elliptical inspection drone loop around the 86.5m High Basalt Shelf "
                "Broadcast Tower on Asteroid 3-5-1, 42,100 AU out in Oort Cloud Sector 9.\n"
                "Unlike a comet that accelerates at periapsis, the camera drone slows down on close approach to take in "
                "the architectural details across 3 ascending periapsis bypasses, and accelerates out into "
                "wide elliptical apoapsis turns over Acheron Chasm before the finale 50 kW Marzelvane burst.\n"
                "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
                "0:00 Apoapsis Dive & Bypass #1: Close-Up Orbit Past the +26.0m Booth Catwalk, 3D Armillary & Consoles\n"
                "0:13 Fast Elliptical Swing #1 & Bypass #2: Close-Up Ascent Past the Vertical G/O/R/◎/9 Neon Sign & Caged EVA Ladder\n"
                "0:28 Fast Elliptical Swing #2 & Bypass #3: Close-Up Orbit Past the +72.0m 4-Ring Marzelvane Waveguides & Phase-Splitter Hub\n"
                "0:43 Fast Fly-Away to Wide Chasm Vantage & Single Finale 50 kW Barycentric Cherenkov Burst"
            ),
            "tags": ["GOR-9", "Galactic Outpost Radio", "Marzelvane", "Shortwave", "Sci-Fi", "Loop"],
            "files": {
                "wide_1080p_mp4": str(out_dir / "gor9_drone_loop.mp4"),
                "thumbnail_16x9_png": str(out_dir / "gor9_drone_loop_thumb.jpg"),
            },
            "uploads": {},
            "history": {},
        }
    elif mode == "booth_tour":
        meta = {
            "short_code": "BOOTH-TOUR",
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": "GOR-9 • Octagonal Broadcast Booth 360° Interior Watchroom Tour (14,285.7 kHz USB • 0400 GCT)",
            "description": (
                "Inside the +26.0m Octagonal Broadcast Booth atop the High Basalt Shelf Tower on Asteroid 3-5-1, "
                "42,100 AU out in Oort Cloud Sector 9.\n"
                "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
                "0:00 Central Glass Lift Emergence & North 3-Screen Master Broadcast Cockpit (0°)\n"
                "0:04 Desk Props Glide: Hauser CM-78 Mic, Station Logbook, GO-9 Brass Morse Key & VFO Flywheel\n"
                "0:09 NE (+45°) Van Allen VA-4 Switchboard & East (+90°) ED-9 Brass Flatbed Vector Plotter\n"
                "0:18 SE (+135°) Bogey-9 Radar Sentinel & South (180°) 3D Brass Armillary Nav-Deck\n"
                "0:25 SW (-135°) Dual Reel-to-Reel Tape Archive & West (-90°) HV-4 Klystron Exciter Burst\n"
                "0:32 NW (-45°) Hauser MK-IV Receiver & Return to Master Show Director HUD"
            ),
            "tags": ["GOR-9", "Galactic Outpost Radio", "Marzelvane", "Shortwave", "Sci-Fi"],
            "files": {
                "wide_1080p_mp4": str(out_dir / "gor9_booth_tour.mp4"),
                "thumbnail_16x9_png": str(out_dir / "gor9_booth_tour_thumb.jpg"),
            },
            "uploads": {},
            "history": {},
        }
    elif mode == "booth_loop":
        meta = {
            "short_code": "BOOTH-LOOP",
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": "GOR-9 • Watchroom Rounds & Star/Solar Shift Seamless Loop (14,285.7 kHz USB • 0400 GCT)",
            "description": (
                "Seamless 48-second watchroom rounds loop inside the +26.0m Octagonal Broadcast Booth on Asteroid 3-5-1, "
                "stopping at the telemetry consoles and gazing out through the panoramic windows as the Sun, "
                "Millisecond Pulsar PSR B1937+21, O.R.S. 351, and the Milky Way shift across the Oort Cloud sky.\n"
                "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
                "0:00 North Master Broadcast Cockpit & Show Director HUD (Perpendicular Console Tilt)\n"
                "0:06 NE/East Panoramic Window Look-Up #1: Blazing Solar Corona (SOL) & Tumbling Basalt Asteroid Shift\n"
                "0:12 East (+90°) ED-9 Euclidean Vector Scope & Brass Flatbed Plotter (Perpendicular Console Tilt)\n"
                "0:24 South (180°) 3D Armillary Sphere & Panoramic Window Look-Up #2: Pulsar PSR B1937+21 & O.R.S. 351 Transit\n"
                "0:36 West (-90°) HV-4 Klystron Exciter Tubes & West/NW Window 50 kW Marzelvane Cherenkov Sky Burst"
            ),
            "tags": ["GOR-9", "Galactic Outpost Radio", "Marzelvane", "Shortwave", "Sci-Fi", "Loop"],
            "files": {
                "wide_1080p_mp4": str(out_dir / "gor9_booth_loop.mp4"),
                "thumbnail_16x9_png": str(out_dir / "gor9_booth_loop_thumb.jpg"),
            },
            "uploads": {},
            "history": {},
        }
    elif mode == "satellite_orbit":
        meta = {
            "short_code": "SAT-ORBIT",
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": "GOR-9 • O.R.S. 351 Satellite Orbit Over Asteroid 3-5-1 (14,285.7 kHz USB • 0400 GCT)",
            "description": (
                "One complete 360° orbital reconnaissance pass of O.R.S. 351 (415m altitude) over the High Basalt Shelf "
                "and 50 kW Marzelvane Broadcast Spire on Asteroid 3-5-1 in Oort Cloud Sector 9.\n"
                "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
                "0:00 High Basalt Shelf Acquisition & Orbital Burst #1 (3.00s)\n"
                "0:10 Deep-Space Terminator Pass & Orbital Burst #2 (13.00s)\n"
                "0:20 Perigee Downlink Lock & Orbital Burst #3 (23.00s)"
            ),
            "tags": ["GOR-9", "Galactic Outpost Radio", "Marzelvane", "Shortwave", "Sci-Fi"],
            "files": {
                "wide_1080p_mp4": str(out_dir / "gor9_satellite_orbit.mp4"),
                "thumbnail_16x9_png": str(out_dir / "gor9_satellite_orbit_thumb.jpg"),
            },
            "uploads": {},
            "history": {},
        }
    else:
        cfg = cfg or {}
        mp4_name = cfg.get("mp4_name", f"gor9_{mode}.mp4")
        thumb_name = cfg.get("thumb_name", f"gor9_{mode}_thumb.jpg")
        meta = {
            "short_code": cfg.get("short_code", mode.upper().replace("_", "-")),
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": cfg.get("title", f"GOR-9 • {mode.replace('_', ' ').title()} (14,285.7 kHz USB • 0400 GCT)"),
            "description": cfg.get("description", f"GOR-9 3D telemetry flythrough ({mode})."),
            "tags": ["GOR-9", "Galactic Outpost Radio", "Marzelvane", "Shortwave", "Sci-Fi"],
            "files": {
                "wide_1080p_mp4": str(out_dir / mp4_name),
                "thumbnail_16x9_png": str(out_dir / thumb_name),
            },
            "uploads": {},
            "history": {},
        }
    if yt_path.exists():
        try:
            existing = json.loads(yt_path.read_text(encoding="utf-8"))
            if existing.get("uploads"):
                meta["uploads"] = existing["uploads"]
            if existing.get("history"):
                meta["history"] = existing["history"]
        except Exception:
            pass
    yt_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return yt_path


def load_camera_path_jobs(base_dir: Path) -> list[dict]:
    """Discover all video project directories in videos/<slug>/ containing a camera_path.json file."""
    preferred_order = ["drone_tour", "drone_loop", "satellite_orbit", "booth_tour", "booth_loop"]
    discovered: dict[str, dict] = {}
    for path_file in sorted(base_dir.glob("*/camera_path.json")):
        folder = path_file.parent.name
        cfg = json.loads(path_file.read_text(encoding="utf-8"))
        mode = cfg.get("mode", folder)
        discovered[mode] = {
            "mode": mode,
            "folder_name": folder,
            "path_file": path_file,
            "cfg": cfg,
            "duration": float(cfg.get("duration", 30.0)),
            "fps": int(cfg.get("fps", FPS)),
            "mp4_name": cfg.get("mp4_name", f"gor9_{mode}.mp4"),
            "wav_name": cfg.get("wav_name", f"gor9_{mode}_audio.wav"),
            "thumb_name": cfg.get("thumb_name", f"gor9_{mode}_thumb.jpg"),
            "thumb_frame": int(cfg.get("thumb_frame", 1)),
            "test_frames": cfg.get("test_frames", [0, 120, 240, 360]),
        }
    ordered: list[dict] = []
    for m in preferred_order:
        if m in discovered:
            ordered.append(discovered.pop(m))
    for m in sorted(discovered.keys()):
        ordered.append(discovered[m])
    return ordered


def main() -> None:
    import sys

    base_dir = VIDEOS_DIR
    jobs = load_camera_path_jobs(base_dir)
    available_modes = [j["mode"] for j in jobs]

    parser = argparse.ArgumentParser(
        description="Capture 3D WebGL video projects defined by per-project videos/<slug>/camera_path.json files in native 2560x1440 QHD."
    )
    parser.add_argument("--only", choices=available_modes if available_modes else None, default=None, help="Run only the specified video project slug")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--test-frames", action="store_true", help="Render diagnostic keyframes defined in camera_path.json")
    parser.add_argument("--daemon", action="store_true", help="Detach and run full capture + MP4 encode in background")
    parser.add_argument("--status", action="store_true", help="Show current frame count and tail of render log")
    parser.add_argument("--scaffold-only", action="store_true", help="Create videos/<mode>/ folders, youtube.json, and WAV audio without rendering frames.")
    parser.add_argument("--encode-only", action="store_true", help="Encode MP4 from existing frames in videos/<mode>/frames/.")
    parser.add_argument("--repair-torn", action="store_true", help="Purge resize-torn frames and re-render only missing frames.")
    parser.add_argument("--audit-only", action="store_true", help="Audit frames for resize tear without modifying files.")
    args = parser.parse_args()

    if args.status:
        for job in jobs:
            if args.only and job["mode"] != args.only:
                continue
            mode = job["mode"]
            job_dur = job["duration"]
            job_fps = job["fps"]
            job_total_frames = int(round(job_dur * job_fps))
            out_dir = base_dir / job["folder_name"]
            frames_dir = out_dir / "frames"
            mp4_path = out_dir / job["mp4_name"]
            log_file = out_dir / "render.log"
            n_frames = len(list(frames_dir.glob("frame_*.png"))) if frames_dir.exists() else 0
            mp4_info = f"{mp4_path.stat().st_size / (1024*1024):.2f} MB" if mp4_path.exists() else "not yet encoded"
            print(f"[{mode} Status] Path: {job['path_file'].name} | Frames: {n_frames}/{job_total_frames} | MP4: {mp4_info}")
            if log_file.exists():
                lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                print("--- Last 15 log lines ---")
                for ln in lines[-15:]:
                    print(ln)
        return

    if args.daemon:
        target_mode = args.only or "drone_tour"
        out_dir = base_dir / target_mode
        out_dir.mkdir(parents=True, exist_ok=True)
        log_file = out_dir / "render.log"
        child_args = [sys.executable, str(Path(__file__).resolve())]
        for a in sys.argv[1:]:
            if a != "--daemon":
                child_args.append(a)
        with open(log_file, "a", encoding="utf-8") as lf:
            proc = subprocess.Popen(
                child_args,
                stdout=lf,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
        print(f"Spawned background {target_mode} render daemon PID={proc.pid}, logging to {log_file}")
        return

    for job in jobs:
        if args.only and job["mode"] != args.only:
            continue

        mode = job["mode"]
        cfg = job["cfg"]
        job_dur = job["duration"]
        job_fps = job["fps"]
        job_total_frames = int(round(job_dur * job_fps))
        out_dir = base_dir / job["folder_name"]
        frames_dir = out_dir / "frames"
        out_dir.mkdir(parents=True, exist_ok=True)
        frames_dir.mkdir(parents=True, exist_ok=True)
        ensure_tour_youtube_json(out_dir, mode, cfg)

        if args.audit_only:
            purge_torn_frames(frames_dir, mode, audit_only=True)
            continue

        wav_path = out_dir / job["wav_name"]
        mp4_path = out_dir / job["mp4_name"]
        thumb_path = out_dir / job["thumb_name"]

        if not wav_path.exists() or args.clean:
            print(f"\n=== [{mode.upper()}] Synthesizing {job_dur:.2f}s Generative C-Lydian Score -> {wav_path} ===", flush=True)
            score_samples = build_generative_lydian_score(mode=mode, duration=job_dur)
            save_wav(wav_path, score_samples)

        if args.scaffold_only:
            print(f"=== [{mode.upper()}] Scaffolded project directory -> {out_dir} ===", flush=True)
            continue

        if args.test_frames:
            test_indices = job["test_frames"]
            capture_mode_frames(
                mode=mode,
                frames_dir=frames_dir,
                camera_path_cfg=cfg,
                duration=job_dur,
                fps=job_fps,
                clean=args.clean,
                workers=args.workers,
                target_indices=test_indices,
            )
            return

        if args.repair_torn:
            purge_torn_frames(frames_dir, mode, audit_only=False)

        if not args.encode_only:
            print(
                f"=== [{mode.upper()}] Capturing {job_total_frames} WebGL {job_fps}fps Frames (2560x1440) "
                f"from {job['path_file']} -> {frames_dir} ===",
                flush=True,
            )
            capture_mode_frames(
                mode=mode,
                frames_dir=frames_dir,
                camera_path_cfg=cfg,
                duration=job_dur,
                fps=job_fps,
                clean=args.clean,
                workers=args.workers,
            )

        print(f"=== [{mode.upper()}] Encoding 2560x1440 QHD MP4 -> {mp4_path} ===", flush=True)
        encode_qhd_mp4_from_frames(
            frames_dir=frames_dir,
            audio_wav=wav_path,
            out_mp4=mp4_path,
            out_thumb=thumb_path,
            thumb_frame_idx=job["thumb_frame"],
            duration=job_dur,
            fps=job_fps,
        )


if __name__ == "__main__":
    main()



