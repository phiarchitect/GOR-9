#!/usr/bin/env python3
"""Synthesize and assemble the complete GOR-9 Broadcast 01 Master Audio Track (24kHz PCM).

v3.2 — 4-Console Edition:
- Seg 0: Cold Open (CAM-00A Exterior Tower -> Octagonal ATC Control Tower Deck, 42,100 AU in Oort Cloud Sector 9)
- Seg 1: Console 1A — Van Allen VA-4 Oort Propagation & Space Weather (Van Allen & Sons Switchgear)
- Seg 2: Console 1B — Van Allen VA-4 Dilithium Power Bus (Grade-B Dilithium, Ring-Bake De-Icer, Cryo-Toast Foot-Warmers)
- Seg 3: Console 2  — Hauser Dynamics MK-IV Receiver, Decoder Algorithms & Station Log (P-02 N-24, P-01 Radio Corrugated, P-03 M-33 ALG-02, P-04 Trojan Octal ALG-03)
- Seg 4: Console 3  — Bogey-9 Perimeter Trail-Cam (140g UAP Cylinder, zero Euclid)
         Console 4  — Van Allen ED-9 Euclidean Detector (Single Euclid I.34 / G.47 lock on Callisto-South Vat 19 + Mud-Rake Cotter Pin Cover-Up)
- Seg 5: Companion Ledger, Van Allen & Sons Switchgear Underwriter Tag & Canonical Sign-Off (CAM-00D)
- Seg 6: 20-Second O.R.S. 351 Satellite Downlink & Lydian Chime End-Card Outro
"""

from pathlib import Path
import json
import math
import os
import subprocess
import sys
import wave
import numpy as np

sys.path.insert(0, "/home/phi/.gemini/config/skills/dialogue/scripts")
import speak  # noqa: E402

SAMPLE_RATE = 24000
ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
SEG_DIR = EP_DIR / "audio" / "segments"
RENDERS_DIR = EP_DIR / "audio"
SFX_DIR = ROOT / "station" / "sfx"


def save_wav_int16(path: Path, pcm_bytes: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_bytes)


def load_wav_int16(path: Path) -> bytes:
    with wave.open(str(path), "rb") as wf:
        return wf.readframes(wf.getnframes())


def bytes_to_float(pcm_bytes: bytes) -> np.ndarray:
    return np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float64) / 32767.0


def float_to_bytes(arr: np.ndarray) -> bytes:
    pcm = np.clip(arr * 32767.0, -32767.0, 32767.0).astype(np.int16)
    return pcm.tobytes()


def dur_sec(pcm_bytes: bytes) -> float:
    return (len(pcm_bytes) // 2) / SAMPLE_RATE


# C Lydian Scale Frequencies (Hz):
F_C3 = 130.81
F_G3 = 196.00
F_C4 = 261.63
F_D4 = 293.66
F_FS4 = 369.99
F_G4 = 392.00
F_A4 = 440.00
F_C5 = 523.25
F_D5 = 587.33
F_FS5 = 739.99
F_G5 = 783.99
F_B5 = 987.77


def add_at(buf: np.ndarray, clip: np.ndarray, start_sec: float, gain: float = 1.0) -> None:
    """Mix `clip` into `buf` starting at `start_sec` without truncating sustain tails."""
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
    amp: float = 0.22,
    echo_taps: list[tuple[float, float]] | None = None,
) -> np.ndarray:
    """Synthesize a C-Lydian crystal chime note/chord with multi-tap O.R.S. 351 echo and cosine taper."""
    n = int(dur * SAMPLE_RATE)
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
        echo_taps = [(0.38, 0.28), (0.76, 0.14), (1.14, 0.07)]

    echo_buf = sig.copy()
    for delay_sec, tap_gain in echo_taps:
        d_idx = int(delay_sec * SAMPLE_RATE)
        if d_idx < n:
            echo_buf[d_idx:] += sig[: n - d_idx] * tap_gain

    fade_samples = min(int(0.35 * SAMPLE_RATE), n // 4)
    if fade_samples > 0:
        fade_curve = 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, fade_samples)))
        echo_buf[-fade_samples:] *= fade_curve

    return echo_buf


def build_chime_01b_sustained(
    dur: float = 6.80,
    spire_tau: float = 1.95,
    pad_level: float = 0.080,
) -> np.ndarray:
    """Canonical GOR-9 Opening & Sign-Off Chime (1B — 6.80s Deep-Space Long Sustain in C Lydian).
    Maps 1:1 to the 4 concentric Marzelvane Emitter rings + Crown Spire Lock:
      - Ring 1 (0.00s): C4 (261.63 Hz)
      - Ring 2 (0.20s): G4 (392.00 Hz, Perfect 5th)
      - Ring 3 (0.40s): D5 (587.33 Hz, 9th — 'GOR-9')
      - Ring 4 (0.60s): F#5 (739.99 Hz, Lydian #4 lift)
      - Spire  (0.84s): G5 + B5 + D5 + F#4 + G4 + C4 (Full Lock Chord + 5.25s cathedral sustain)
    """
    n = int(dur * SAMPLE_RATE)
    out = np.zeros(n, dtype=np.float64)
    tt = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    pad_attack = 1.0 - np.exp(-tt / 0.32)
    pad_decay = np.exp(-np.maximum(0.0, tt - 0.84) / (spire_tau * 1.15))
    pad_env = pad_attack * pad_decay
    fade_len = int(0.60 * SAMPLE_RATE)
    pad_env[-fade_len:] *= 0.5 * (1.0 + np.cos(np.linspace(0.0, math.pi, fade_len)))

    pad = (
        0.42 * np.sin(2.0 * math.pi * F_C3 * tt)
        + 0.32 * np.sin(2.0 * math.pi * F_G3 * tt)
        + 0.18 * np.sin(2.0 * math.pi * F_D4 * tt)
        + 0.08 * np.sin(2.0 * math.pi * F_FS4 * tt)
    ) * pad_env * pad_level
    out += pad

    events = [
        (0.00, [F_C4, F_C5], 0.95, 0.22),
        (0.20, [F_G4, F_G5], 1.00, 0.23),
        (0.40, [F_D5, F_A4], 1.10, 0.24),
        (0.60, [F_FS5, F_D5], 1.25, 0.25),
        (0.84, [F_G5, F_B5, F_D5, F_FS5 * 0.5, F_G4, F_C4], spire_tau, 0.30),
    ]
    for t0, freqs, tau, amp in events:
        note = crystal_note(
            freqs,
            dur - t0,
            decay_tau=tau,
            amp=amp,
            echo_taps=[(0.38, 0.30), (0.76, 0.16), (1.14, 0.08), (1.52, 0.04)],
        )
        add_at(out, note, t0)

    return np.clip(out, -0.95, 0.95)


def make_softer_crackle_overlay(duration: float, seed: int = 35109) -> tuple[np.ndarray, list[float]]:
    """Generate softer crackly white-noise overlay that clears smoothly right at the end (the ding)."""
    rng = np.random.default_rng(seed)
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    raw = rng.normal(0.0, 1.0, size=n + 1)
    white = raw[1:] - 0.58 * raw[:-1]
    white /= (np.std(white) + 1e-8)

    env = np.zeros(n, dtype=np.float64)
    for i, ti in enumerate(t):
        progress = ti / duration
        if ti < 0.42:
            e = 0.85 - 0.20 * (ti / 0.42)
        elif progress < 0.48:
            e = 0.48 + 0.14 * math.sin(ti * 19.0)
        elif progress < 0.62:
            e = 0.65
        elif progress < 0.86:
            rem = (0.86 - progress) / (0.86 - 0.62)
            e = 0.42 * (rem ** 1.2)
        else:
            rem = max(0.0, (1.0 - progress) / 0.14)
            e = 0.16 * (rem ** 2.0)
        env[i] = max(0.0, min(1.0, e))

    crackle = np.zeros(n, dtype=np.float64)
    n_ticks = int(duration * 150)
    for pos in rng.integers(0, max(1, n - 20), size=n_ticks):
        d = int(rng.integers(3, 14))
        pol = 1.0 if rng.random() > 0.5 else -1.0
        crackle[pos:pos + d] += pol * float(rng.uniform(0.25, 0.75)) * np.exp(-np.arange(d) / 3.5)

    n_snaps = int(duration * 22)
    for pos in rng.integers(0, max(1, n - 180), size=n_snaps):
        d = int(rng.integers(35, 160))
        burst = rng.normal(0.0, 1.0, size=d)
        crackle[pos:pos + d] += float(rng.uniform(0.20, 0.55)) * np.exp(-np.arange(d) / 30.0) * burst

    static_sig = (white * 0.105 + crackle * 0.22) * env

    fps = 30
    n_frames = int(math.ceil(duration * fps))
    spf = SAMPLE_RATE // fps
    vis_env = []
    for f in range(n_frames):
        s0 = f * spf
        s1 = min(n, (f + 1) * spf)
        if s0 >= n:
            vis_env.append(0.0)
            continue
        base_e = float(np.mean(env[s0:s1]))
        peak_c = float(np.max(np.abs(crackle[s0:s1]))) if s1 > s0 else 0.0
        v = min(1.0, 0.85 * base_e + 0.30 * peak_c)
        if f >= n_frames - 2:
            v = 0.0
        vis_env.append(round(v, 4))

    return static_sig, vis_env


def make_vignette_buoy_n24(duration: float = 2.4) -> bytes:
    """3,890 kHz Titan-Minor Hydrographic Buoy N-24: CW ID + metallic buoy clank + detuning whip rub."""
    rng = np.random.default_rng(3890)
    n = int(SAMPLE_RATE * duration)
    noise = np.convolve(rng.normal(0.0, 0.035, size=n), np.ones(9) / 9.0, mode="same")

    clank = np.zeros(n, dtype=np.float64)
    for tc in (0.15, 1.45):
        idx = int(tc * SAMPLE_RATE)
        d = min(int(0.85 * SAMPLE_RATE), n - idx)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        bell = (
            0.5 * np.sin(2.0 * math.pi * 612.0 * tt)
            + 0.35 * np.sin(2.0 * math.pi * 1148.0 * tt)
            + 0.25 * np.sin(2.0 * math.pi * 1715.0 * tt)
        ) * np.exp(-tt / 0.18)
        clank[idx:idx + d] += bell * 0.22

    tone = np.zeros(n, dtype=np.float64)
    beeps = [
        (0.35, 0.14, 880.0),
        (0.54, 0.08, 880.0),
        (0.66, 0.18, 1040.0),
        (0.92, 0.12, 880.0),
        (1.12, 0.55, 960.0),
        (1.78, 0.14, 780.0),
        (1.98, 0.22, 880.0),
    ]
    for t0, dur_b, freq in beeps:
        i0 = int(t0 * SAMPLE_RATE)
        d = min(int(dur_b * SAMPLE_RATE), n - i0)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        if abs(t0 - 1.12) < 0.05:
            f_inst = freq - 165.0 * np.sin(math.pi * tt / dur_b)
            ph = 2.0 * math.pi * np.cumsum(f_inst) / SAMPLE_RATE
        else:
            ph = 2.0 * math.pi * freq * tt
        env_b = np.sin(math.pi * tt / dur_b) ** 0.25
        tone[i0:i0 + d] += np.sin(ph) * env_b * 0.13

    sig = noise + clank + tone
    return float_to_bytes(np.clip(sig, -0.85, 0.85))


def make_vignette_radio_corrugated(duration: float = 2.4) -> bytes:
    """11,410 kHz Callisto Dome-4 'Radio Corrugated': warbling night-market lute + blowtorch spike."""
    rng = np.random.default_rng(11410)
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    fading = 0.65 + 0.35 * np.sin(2.0 * math.pi * 1.4 * t)
    noise = np.convolve(rng.normal(0.0, 0.03, size=n), np.ones(7) / 7.0, mode="same")

    notes = [
        (0.08, 0.26, 392.0),
        (0.32, 0.24, 440.0),
        (0.54, 0.30, 523.25),
        (0.82, 0.22, 587.33),
        (1.04, 0.28, 523.25),
        (1.30, 0.25, 440.0),
        (1.55, 0.35, 392.0),
    ]
    lute = np.zeros(n, dtype=np.float64)
    for t0, dur_n, f0 in notes:
        i0 = int(t0 * SAMPLE_RATE)
        d = min(int(dur_n * SAMPLE_RATE), n - i0)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        vib = 1.0 + 0.008 * np.sin(2.0 * math.pi * 6.5 * tt)
        wave_n = (
            0.65 * np.sin(2.0 * math.pi * f0 * vib * tt)
            + 0.25 * np.sin(2.0 * math.pi * (2.0 * f0) * vib * tt)
            + 0.10 * np.sin(2.0 * math.pi * (3.0 * f0) * vib * tt)
        ) * np.exp(-tt / 0.11)
        lute[i0:i0 + d] += wave_n * 0.18

    torch = np.zeros(n, dtype=np.float64)
    t_idx = int(1.82 * SAMPLE_RATE)
    t_dur = min(int(0.55 * SAMPLE_RATE), n - t_idx)
    tt = np.arange(t_dur, dtype=np.float64) / SAMPLE_RATE
    env_t = np.sin(math.pi * tt / (t_dur / SAMPLE_RATE)) ** 0.5
    sizzle = rng.normal(0.0, 0.16, size=t_dur) * env_t
    whistle = np.sin(2.0 * math.pi * (1200.0 + 900.0 * tt) * tt) * 0.11 * env_t
    torch[t_idx:t_idx + t_dur] = sizzle + whistle

    sig = noise + lute * fading + torch
    return float_to_bytes(np.clip(sig, -0.85, 0.85))


def synth_or_load_segment(seg_id: str, text: str, profile: dict, api_key: str | None) -> bytes:
    """Load cached 24kHz PCM WAV from audio/segments/{seg_id}.wav or synthesize via Argon III-C."""
    SEG_DIR.mkdir(parents=True, exist_ok=True)
    wav_path = SEG_DIR / f"{seg_id}.wav"
    if wav_path.exists():
        print(f"  [cached] {seg_id} -> {wav_path.name}")
        return load_wav_int16(wav_path)

    if not api_key:
        raise RuntimeError(f"Missing cached {wav_path} and no GEMINI_API_KEY/GOOGLE_API_KEY set")

    voice_id = profile["voice_id"]
    model = profile.get("model", "gemini-3.8-flash-tts")
    style_str = profile["styles"]["brisk"]
    print(f"  [synth]  {seg_id} ({len(text.split())} words) via {voice_id}...")
    pcm = speak.synth_pcm_bytes(voice_id, text, style_str, model, api_key)
    save_wav_int16(wav_path, pcm)
    return pcm


def build_cold_open_v32(profile: dict, api_key: str | None) -> tuple[bytes, dict]:
    """Build the v3.2 Cold Open with the 1B 6.80s C-Lydian Marzelvane 4-Ring + Spire Lock Chime
    sustaining uninterrupted underneath Argon III-C's station identification.
    """
    pure_voice_wav = RENDERS_DIR / "cam00_voice_pure_24k.wav"
    if not pure_voice_wav.exists():
        raise RuntimeError(f"Expected {pure_voice_wav} to exist")
    pure_voice = bytes_to_float(load_wav_int16(pure_voice_wav))
    # Dry "This is G-O-R 9. This is G-O-R 9." (0.57s .. 3.85s of cam00_voice_pure_24k.wav)
    callsign_voice = pure_voice[int(0.57 * SAMPLE_RATE) : int(3.85 * SAMPLE_RATE)]

    post_ding_text = (
        "Galactic Outpost Radio, broadcasting from the High Basalt Shelf Tower on Asteroid 3-5-1, "
        "forty-two thousand one hundred astronomical units out in Oort Cloud Sector 9. "
        "Fourteen-two-eighty-five kilohertz upper sideband. Zero-four-hundred Galactic Coordinated."
    )
    post_ding_voice = bytes_to_float(synth_or_load_segment("v32_seg0_post_ding", post_ding_text, profile, api_key))

    # Build canonical 1B (6.80s Deep-Space Long Sustain) chime and save to station/sfx/
    chime_1b = build_chime_01b_sustained(dur=6.80, spire_tau=1.95, pad_level=0.080)
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    save_wav_int16(SFX_DIR / "gor9_opening_chime_lydian_6p8s.wav", float_to_bytes(chime_1b))

    t_intro_bell = 0.30
    t_callsign = 0.85
    callsign_dur = len(callsign_voice) / SAMPLE_RATE
    t_chime = t_callsign + callsign_dur + 0.05  # 4.18s
    t_spire_lock = t_chime + 0.84               # 5.02s
    voice_reentry_offset = 1.55
    t_post_voice = t_chime + voice_reentry_offset  # 5.73s
    post_dur = len(post_ding_voice) / SAMPLE_RATE

    total_dur = t_post_voice + post_dur + 0.15
    n_total = int(math.ceil(total_dur * SAMPLE_RATE))
    master = np.zeros(n_total, dtype=np.float64)

    # 1. Opening C4-G4-D5 fifths bell (rings out for 2.40s under callsign without cutoff)
    intro_bell = crystal_note(
        [F_C4, F_G4, F_D5],
        dur=2.40,
        decay_tau=0.75,
        amp=0.19,
        echo_taps=[(0.38, 0.22), (0.76, 0.10)],
    )
    add_at(master, intro_bell, t_intro_bell)

    # 2. Callsign voice: "This is G-O-R 9. This is G-O-R 9."
    add_at(master, callsign_voice, t_callsign)

    # 3. 1B Marzelvane 4-Ring + Spire Lock Chime (6.80s, sustaining for 5.25s underneath post_ding_voice)
    chime_shaped = chime_1b.copy()
    reentry_idx = int(voice_reentry_offset * SAMPLE_RATE)
    if reentry_idx < len(chime_shaped):
        trans_len = min(int(0.18 * SAMPLE_RATE), len(chime_shaped) - reentry_idx)
        duck_curve = np.ones(len(chime_shaped), dtype=np.float64)
        duck_curve[reentry_idx : reentry_idx + trans_len] = np.linspace(1.0, 0.88, trans_len)
        duck_curve[reentry_idx + trans_len :] = 0.88
        chime_shaped *= duck_curve
    add_at(master, chime_shaped, t_chime)

    # 4. Post-ding voice: "Galactic Outpost Radio, broadcasting from..."
    add_at(master, post_ding_voice, t_post_voice)

    # 5. Soft shortwave static bed that clears right as the Spire Lock chord blooms
    static_sig, vis_env = make_softer_crackle_overlay(t_spire_lock + 0.15)
    add_at(master, static_sig, 0.0)

    cold_open_pcm = float_to_bytes(np.clip(master, -0.95, 0.95))

    catalog_path = SFX_DIR / "sfx_catalog.json"
    if catalog_path.exists():
        cat = json.loads(catalog_path.read_text(encoding="utf-8"))
        cat["cam00_boot_visual_envelope_30fps"] = vis_env
        cat["ding_lock_time_sec"] = round(t_chime, 3)
        cat["spire_lock_time_sec"] = round(t_spire_lock, 3)
        files_list = [f for f in cat.get("files", []) if f.get("name") != "gor9_opening_chime_lydian_6p8s.wav"]
        files_list.insert(
            0,
            {
                "name": "gor9_opening_chime_lydian_6p8s.wav",
                "duration_sec": 6.80,
                "description": "Canonical GOR-9 C-Lydian Opening & Sign-Off Chime (1B: 4 Marzelvane Rings C4-G4-D5-F#5 + G5 Spire Lock with 5.25s cathedral sustain)",
            },
        )
        cat["files"] = files_list
        catalog_path.write_text(json.dumps(cat, indent=2), encoding="utf-8")

    meta = {
        "voice_start_sec": round(t_callsign, 3),
        "ding_lock_sec": round(t_chime, 3),
        "spire_lock_sec": round(t_spire_lock, 3),
        "ding_end_sec": round(t_post_voice, 3),
        "duration_sec": round(dur_sec(cold_open_pcm), 3),
    }
    return cold_open_pcm, meta


def make_soft_switch_squelch() -> bytes:
    """Gentle, low-level camera/console relay switch squelch (0.28s) so transitions feel tactile."""
    squelch_path = SFX_DIR / "shortwave_squelch_burst_0p8s.wav"
    if squelch_path.exists():
        raw = bytes_to_float(load_wav_int16(squelch_path))
        n = min(len(raw), int(0.28 * SAMPLE_RATE))
        fade = np.linspace(1.0, 0.0, n)
        return float_to_bytes(raw[:n] * fade * 0.28)
    return speak.silence_pcm(0.20)


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        env_file = Path("/home/phi/.photon/.env")
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip().removeprefix("export ").strip()
                if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip("'\"")
                    break
    profile = speak.load_profile()

    # 1. Build Cold Open (Segment 0)
    seg0_pcm, seg0_meta = build_cold_open_v32(profile, api_key)
    standalone_cold = seg0_pcm + speak.silence_pcm(0.50)
    save_wav_int16(RENDERS_DIR / "cam00_cold_open_mix.wav", standalone_cold)
    print(
        f"Updated Cold Open mix: {RENDERS_DIR / 'cam00_cold_open_mix.wav'} "
        f"({dur_sec(standalone_cold):.2f}s, voice under static at {seg0_meta['voice_start_sec']}s, "
        f"clears at [ding-ding] signal lock {seg0_meta['ding_lock_sec']}s)"
    )

    # 2. Synthesize (or load cached) v3.2 Segments 1 - 6 in Argon III-C
    segments_spec = [
        (
            "v32_seg1_weather",
            "On the Van Allen V-A-Four Propagation and Power Console—brought to you by Van Allen and Sons "
            "Switchgear of Ceres Foundry Seven: "
            "Comet K-Four's ion tail is sweeping azimuth two-twelve, opening a clean twenty-four megahertz "
            "skip corridor into the Jovian moons. "
            "Closer to home, a sixty-kilovolt triboelectric dust squall has engulfed Relay K-Z-9 Omega—raising "
            "our lower usable frequency by four megahertz and arcing across the number-four Belt-Master "
            "marzelvane bushing. Expect SINPO two-three-two-two-two.",
        ),
        (
            "v32_seg2_dilithium",
            "On the Dilithium Bus: "
            "Grade-B Dilithium pellets rose four percent on the Ceres Exchange following a dragline cable "
            "slowdown at Silicate Quarry 44-K. With our Van Allen Ring-Bake corona de-icer pulling an extra "
            "four-point-five kilowatts, we are stepping Reactor Two down to twelve kilowatts after midnight—"
            "Dormitory Wing B should plug in their Van Allen Cryo-Toast foot-warmers. "
            "Meanwhile, our monthly pellet and vacuum-tube tender remains impounded at Quarantine Buoy Twelve "
            "after customs misfiled replacement oscillator tubes as fermented brine tubers.",
        ),
        (
            "v32_seg3a_titan_intro",
            "Turning to the Hauser Dynamics Mark-Four Receiver and Galaxy Atlas: "
            "Preset Two—Titan-Minor, three-eight-ninety kilohertz. Hydrographic Buoy N-24 is transmitting "
            "methane tide telemetry,",
        ),
        (
            "v32_seg3a_titan_tail",
            "though migratory silt-striders rubbing against the guy-wires just detuned the whip antenna by "
            "eighteen Hertz. E-QSL zero-eight-eight-two logged.",
        ),
        (
            "v32_seg3b_callisto_intro",
            "Preset One—Callisto Dome Four, eleven-four-ten kilohertz. Unlicensed noodle-market broadcaster "
            "Radio Corrugated,",
        ),
        (
            "v32_seg3b_callisto_tail",
            "peaking at S-nine plus ten right as their engineer hit the rooftop dipole with a blowtorch.",
        ),
        (
            "v32_seg3c_m33",
            "Preset Three—extragalactic, fourteen-twenty megahertz on the hydrogen line, two-point-seven "
            "million light-years toward M-Thirty-Three. No video carrier on this band—just a relativistic "
            "Doppler Lissajous on the spectrum scan. Running Translation Algorithm Zero-Two against the raw "
            "hex stream decodes Buoy M-33-771: still issuing small-craft advisories for an ammonia sea that "
            "evaporated during the Ming Dynasty.",
        ),
        (
            "v32_seg3d_trojan",
            "And on Preset Four, six-nine-two-five kilohertz in the Jupiter Trojans: an encrypted base-eight "
            "numbers station where Algorithm Zero-Three just decoded six metric tons of pork-chive dumpling "
            "wrappers—plus an octal shift key of thirteen for those tracking the sector cipher in the station log.",
        ),
        (
            "v32_seg4a_bogey",
            "Quick check on the Bogey-Nine Perimeter Trail-Cam, which discriminates ballistic Oort rocks from "
            "non-Keplerian visitors right outside our cliff rim. "
            "At zero-three-forty-one Galactic, Trail-Cam One on the Acheron North Rim triggered an eight-frame "
            "burst on a mirror-chrome cylinder drifting between two tumbling boulders at fourteen meters per "
            "second—before executing a ninety-degree vertical snap-turn on Frame Five at one-hundred-forty G's "
            "with zero thruster plume. The Outer Belt Safety Board says it was a vented thermos flask from the Mess Hall.",
        ),
        (
            "v32_seg4b_ed9_sighting",
            "Now to our centerpiece instrument: the Van Allen E-D-Nine Euclidean Detector—searching for "
            "geometric intelligence across the universe. Natural vacuum produces fractals and thermal static; "
            "intelligence leaves straight lines, parallel chords, and constructive ratios. "
            "Tonight, our twelve-tube Hough Transform correlator locked onto a single ninety-nine-point-nine-"
            "nine-eight percent synthetic signature in the maintenance feed from Callisto-South Brine "
            "Evaporation Vat Nineteen: what we are calling the Unsuspecting Parallelogram.",
        ),
        (
            "v32_seg4c_ed9_proof",
            "Under inspection-beam sweep Frame Seven, four salt-crust ridges form parallelogram A-B-D-C—"
            "satisfying Euclid Book One, Proposition Thirty-Four: opposite sides A-B and C-D, and A-C and B-D, "
            "hold parallel to two ten-thousandths of an arcsecond, while diagonal diameter B-C bisects the "
            "brine sludge into two congruent triangles of equal area.",
        ),
        (
            "v32_seg4d_ed9_punchline",
            "Seven minutes after our Van Allen detector logged the Proposition Thirty-Four proof, the Callisto "
            "Water Board scrubbed the archive and blamed a motorized mud-rake that lost a cotter pin. "
            "That is one remarkably well-educated mud-rake, folks.",
        ),
        (
            "v32_seg5_signoff",
            "On the next broadcast: an uninspected Dilithium barge rendezvous in the tail of Comet K-Four, "
            "and a suspected rhombus aboard a bulk ice-hauler. "
            "This broadcast is underwritten by Van Allen and Sons Switchgear—from radiation belts to reactor "
            "beds, if it arcs, we clamp it. "
            "From Asteroid 3-5-1 in Oort Cloud Sector 9, this is G-O-R 9—your eye to the cosmos, ear to the vacuum.",
        ),
        (
            "v32_seg6_outro",
            "Remember, a like indication on your listening apparatus gives us three kilowatts of Dilithium "
            "reserve, and a subscription gets us one step closer to shielding our marzelvane emitters.",
        ),
    ]

    seg_pcm_map: dict[str, bytes] = {}
    for seg_id, text in segments_spec:
        seg_pcm_map[seg_id] = synth_or_load_segment(seg_id, text, profile, api_key)

    # 3. Assemble full master audio track & build exact timeline metadata
    bell_construction = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:construction"]["freqs"], duration=0.45, amp=0.14
    )
    bell_proposition = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:proposition"]["freqs"], duration=0.50, amp=0.14
    )
    bell_context = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:context"]["freqs"], duration=0.45, amp=0.14
    )
    bell_insight = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:insight"]["freqs"], duration=0.50, amp=0.14
    )
    bell_punchline = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:punchline"]["freqs"], duration=0.45, amp=0.14
    )
    chime_1b_flt = build_chime_01b_sustained(dur=6.80, spire_tau=1.95, pad_level=0.080)
    soft_squelch = make_soft_switch_squelch()

    vig_n24 = make_vignette_buoy_n24(2.40)
    vig_bazaar = make_vignette_radio_corrugated(2.40)
    save_wav_int16(SEG_DIR / "vignette_buoy_n24.wav", vig_n24)
    save_wav_int16(SEG_DIR / "vignette_radio_corrugated.wav", vig_bazaar)

    master_chunks: list[bytes] = []
    cursor_sec = 0.0
    timeline_events: list[dict] = []

    def append_chunk(pcm: bytes) -> float:
        nonlocal cursor_sec
        master_chunks.append(pcm)
        d = dur_sec(pcm)
        cursor_sec += d
        return cursor_sec

    # --- SEG 0: COLD OPEN (CAM-00A -> ATC CONTROL TOWER ROOM) ---
    seg0_start = cursor_sec
    append_chunk(seg0_pcm)
    append_chunk(speak.silence_pcm(0.35))
    seg0_end = cursor_sec
    timeline_events.append({
        "id": "seg0_cold_open",
        "console": "CAM-00",
        "title": "CAM-00 • HIGH BASALT SHELF TOWER & ATC CONTROL ROOM",
        "start_sec": round(seg0_start, 3),
        "end_sec": round(seg0_end, 3),
        "voice_start_sec": seg0_meta["voice_start_sec"],
        "ding_lock_sec": seg0_meta["ding_lock_sec"],
        "subtitle": "This is GOR-9. This is GOR-9 [ding-ding] Galactic Outpost Radio, broadcasting from the High Basalt Shelf Tower on Asteroid 3-5-1, 42,100 AU out in Oort Cloud Sector 9. 14,285 kHz USB. 0400 Galactic Coordinated.",
    })

    # --- SEG 1: SPACE WEATHER & OORT PROPAGATION (CONSOLE 1A: VAN ALLEN VA-4) ---
    seg1_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_construction)
    append_chunk(speak.silence_pcm(0.15))
    append_chunk(seg_pcm_map["v32_seg1_weather"])
    append_chunk(speak.silence_pcm(0.45))
    seg1_end = cursor_sec
    timeline_events.append({
        "id": "seg1_weather",
        "console": "VAN-ALLEN-VA4",
        "title": "CONSOLE 1 • VAN ALLEN VA-4 • OORT PROPAGATION & SPACE WEATHER",
        "start_sec": round(seg1_start, 3),
        "end_sec": round(seg1_end, 3),
        "subtitle": "On the Van Allen VA-4 Propagation and Power Console—brought to you by Van Allen and Sons Switchgear: Comet K-4's ion tail opens a 24 MHz skip corridor to the Jovian moons; a 60 kV triboelectric dust squall at Relay KZ9-Omega arcs across the #4 Belt-Master marzelvane bushing (SINPO 2-3-2-2-2).",
    })

    # --- SEG 2: DILITHIUM POWER BUS (CONSOLE 1B: VAN ALLEN VA-4) ---
    seg2_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_proposition)
    append_chunk(speak.silence_pcm(0.15))
    append_chunk(seg_pcm_map["v32_seg2_dilithium"])
    append_chunk(speak.silence_pcm(0.45))
    seg2_end = cursor_sec
    timeline_events.append({
        "id": "seg2_econ",
        "console": "VAN-ALLEN-BUS",
        "title": "CONSOLE 1B • VAN ALLEN VA-4 • 50 kW DILITHIUM POWER BUS",
        "start_sec": round(seg2_start, 3),
        "end_sec": round(seg2_end, 3),
        "subtitle": "On the Dilithium Bus: Grade-B Dilithium pellets +4% on the Ceres Exchange (Quarry 44-K slowdown). With the Van Allen Ring-Bake corona de-icer pulling +4.5 kW, Reactor #2 steps down to 12 kW after midnight (plug in Van Allen Cryo-Toast foot-warmers). Tender held at Quarantine Buoy 12 ('fermented brine tubers').",
    })

    # --- SEG 3: GALACTIC DX INTERCEPTS & DECODER ALGORITHMS (CONSOLE 2: HAUSER MK-IV) ---
    seg3_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_context)
    append_chunk(speak.silence_pcm(0.15))

    # Sub-view 3A: Preset 2 — Titan-Minor Buoy N-24 (3,890 kHz)
    sub3a_start = seg3_start
    append_chunk(seg_pcm_map["v32_seg3a_titan_intro"])
    append_chunk(speak.silence_pcm(0.10))
    vig3a_start = cursor_sec
    append_chunk(vig_n24)
    vig3a_end = cursor_sec
    append_chunk(speak.silence_pcm(0.10))
    append_chunk(seg_pcm_map["v32_seg3a_titan_tail"])
    append_chunk(speak.silence_pcm(0.30))
    sub3a_end = cursor_sec

    # Sub-view 3B: Preset 1 — Callisto Dome Four "Radio Corrugated" (11,410 kHz)
    sub3b_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(seg_pcm_map["v32_seg3b_callisto_intro"])
    append_chunk(speak.silence_pcm(0.10))
    vig3b_start = cursor_sec
    append_chunk(vig_bazaar)
    vig3b_end = cursor_sec
    append_chunk(speak.silence_pcm(0.10))
    append_chunk(seg_pcm_map["v32_seg3b_callisto_tail"])
    append_chunk(speak.silence_pcm(0.30))
    sub3b_end = cursor_sec

    # Sub-view 3C: Preset 3 — Extragalactic M-33 Drift Buoy (1,420.405 MHz + ALG-02)
    sub3c_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(seg_pcm_map["v32_seg3c_m33"])
    append_chunk(speak.silence_pcm(0.30))
    sub3c_end = cursor_sec

    # Sub-view 3D: Preset 4 — Jupiter Trojans Octal Numbers Station (6,925 kHz + ALG-03)
    sub3d_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(seg_pcm_map["v32_seg3d_trojan"])
    append_chunk(speak.silence_pcm(0.45))
    sub3d_end = cursor_sec
    seg3_end = cursor_sec

    timeline_events.append({
        "id": "seg3_hauser",
        "console": "HAUSER-MK4",
        "title": "CONSOLE 2 • HAUSER DYNAMICS MK-IV • GALAXY ATLAS & DECODER",
        "start_sec": round(seg3_start, 3),
        "end_sec": round(seg3_end, 3),
        "sub_views": [
            {
                "id": "3a_titan_n24",
                "freq_khz": 3890.0,
                "label": "P-02 • 3,890 kHz CW • TITAN-MINOR BUOY N-24",
                "start_sec": round(sub3a_start, 3),
                "end_sec": round(sub3a_end, 3),
                "vignette_start_sec": round(vig3a_start, 3),
                "vignette_end_sec": round(vig3a_end, 3),
                "subtitle": "Turning to the Hauser Dynamics MK-IV Receiver: Preset Two—Titan-Minor, 3,890 kHz. Hydrographic Buoy N-24 is transmitting methane tide telemetry, though migratory silt-striders rubbing against the guy-wires just detuned the whip antenna by 18 Hz. eQSL #0882 logged.",
            },
            {
                "id": "3b_callisto_bazaar",
                "freq_khz": 11410.0,
                "label": "P-01 • 11,410 kHz AM • CALLISTO DOME-4 'RADIO CORRUGATED'",
                "start_sec": round(sub3b_start, 3),
                "end_sec": round(sub3b_end, 3),
                "vignette_start_sec": round(vig3b_start, 3),
                "vignette_end_sec": round(vig3b_end, 3),
                "subtitle": "Preset One—Callisto Dome Four, 11,410 kHz. Unlicensed noodle-market broadcaster Radio Corrugated, peaking at S9+10 right as their engineer hit the rooftop dipole with a blowtorch.",
            },
            {
                "id": "3c_m33_buoy",
                "freq_khz": 1420405.0,
                "label": "P-03 • 1,420.405 MHz • EXTRAGALACTIC M-33 DRIFT BUOY [ALG-02]",
                "start_sec": round(sub3c_start, 3),
                "end_sec": round(sub3c_end, 3),
                "subtitle": "Preset Three—extragalactic, 1,420 MHz on the hydrogen line toward M-33. No video carrier—just a relativistic Doppler Lissajous on the spectrum scan. Translation Algorithm 02 decodes Buoy M-33-771: still issuing small-craft advisories for an ammonia sea that evaporated during the Ming Dynasty.",
            },
            {
                "id": "3d_trojan_octal",
                "freq_khz": 6925.0,
                "label": "P-04 • 6,925 kHz USB • TROJAN OCTAL NUMBERS STATION [ALG-03]",
                "start_sec": round(sub3d_start, 3),
                "end_sec": round(sub3d_end, 3),
                "subtitle": "And on Preset Four, 6,925 kHz in the Jupiter Trojans: an encrypted base-8 numbers station where Algorithm 03 just decoded six metric tons of pork-chive dumpling wrappers—plus an octal shift key of 13 for those tracking the sector cipher in the station log.",
            },
        ],
    })

    # --- SEG 4: BOGEY-9 TRAIL-CAM -> VAN ALLEN ED-9 EUCLIDEAN DETECTOR ---
    seg4_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_insight)
    append_chunk(speak.silence_pcm(0.15))

    # Step 4A: Console 3 — Bogey-9 Perimeter Trail-Cam (No Euclid!)
    step4a_start = seg4_start
    append_chunk(seg_pcm_map["v32_seg4a_bogey"])
    append_chunk(speak.silence_pcm(0.30))
    step4a_end = cursor_sec

    # Step 4B: Console 4 — Van Allen ED-9 Euclidean Detector (Hough Correlator & Vat 19 Lock)
    step4b_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_construction)
    append_chunk(speak.silence_pcm(0.15))
    append_chunk(seg_pcm_map["v32_seg4b_ed9_sighting"])
    append_chunk(speak.silence_pcm(0.25))
    step4b_end = cursor_sec

    # Step 4C: Van Allen ED-9 Constructive Proof (Euclid I.34 / G.47)
    step4c_start = cursor_sec
    append_chunk(bell_proposition)
    append_chunk(speak.silence_pcm(0.12))
    append_chunk(seg_pcm_map["v32_seg4c_ed9_proof"])
    append_chunk(speak.silence_pcm(0.25))
    step4c_end = cursor_sec

    # Step 4D: Van Allen ED-9 Broken Mud-Rake Cotter Pin Cover-Up
    step4d_start = cursor_sec
    append_chunk(bell_punchline)
    append_chunk(speak.silence_pcm(0.12))
    append_chunk(seg_pcm_map["v32_seg4d_ed9_punchline"])
    append_chunk(speak.silence_pcm(0.45))
    step4d_end = cursor_sec
    seg4_end = cursor_sec

    timeline_events.append({
        "id": "seg4_euclid",
        "console": "VAN-ALLEN-ED9",
        "title": "CONSOLE 3 BOGEY-9 TRAIL-CAM & CONSOLE 4 VAN ALLEN ED-9 EUCLIDEAN DETECTOR",
        "start_sec": round(seg4_start, 3),
        "end_sec": round(seg4_end, 3),
        "steps": [
            {
                "id": "4a_bogey_trailcam",
                "start_sec": round(step4a_start, 3),
                "end_sec": round(step4a_end, 3),
                "subtitle": "Bogey-9 Perimeter Trail-Cam (03:41 GCT): Trail-Cam One on the Acheron North Rim triggered an 8-frame burst on a mirror-chrome cylinder drifting at 14 m/s before executing a 90° vertical snap-turn at 140g with zero thruster plume (blamed on a vented Mess Hall thermos flask).",
            },
            {
                "id": "4b_ed9_sighting",
                "start_sec": round(step4b_start, 3),
                "end_sec": round(step4b_end, 3),
                "subtitle": "Van Allen ED-9 Euclidean Detector—searching for geometric intelligence across the universe: our 12-tube Hough Transform correlator locked onto a single 99.998% synthetic signature in Callisto-South Brine Evaporation Vat 19: the Unsuspecting Parallelogram.",
            },
            {
                "id": "4c_ed9_proof",
                "start_sec": round(step4c_start, 3),
                "end_sec": round(step4c_end, 3),
                "subtitle": "Under inspection-beam sweep Frame 7, four salt-crust ridges form parallelogram ABDC (Euclid I.34 / G.47): opposite sides AB || CD and AC || BD hold parallel to 0.0002 arcsec, while diameter BC bisects the sludge into two congruent triangles.",
            },
            {
                "id": "4d_ed9_punchline",
                "start_sec": round(step4d_start, 3),
                "end_sec": round(step4d_end, 3),
                "subtitle": "Seven minutes after our Van Allen detector logged the Proposition 34 proof, the Callisto Water Board scrubbed the archive and blamed a motorized mud-rake that lost a cotter pin. That is one remarkably well-educated mud-rake, folks.",
            },
        ],
    })

    # --- SEG 5: COMPANION LEDGER, UNDERWRITER TAG & SIGN-OFF (STATION DOSSIER -> CAM-00D) ---
    seg5_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_context)
    append_chunk(speak.silence_pcm(0.15))

    seg5_voice_dur = dur_sec(seg_pcm_map["v32_seg5_signoff"])
    cam00_return_sec = cursor_sec + seg5_voice_dur * 0.62

    append_chunk(seg_pcm_map["v32_seg5_signoff"])
    append_chunk(speak.silence_pcm(0.10))
    closing_ding_sec = cursor_sec
    seg5_chime_head_samples = int(1.55 * SAMPLE_RATE)
    append_chunk(float_to_bytes(chime_1b_flt[:seg5_chime_head_samples]))
    seg5_end = cursor_sec
    timeline_events.append({
        "id": "seg5_signoff",
        "console": "SCHED-9",
        "title": "COMING NEXT, VAN ALLEN UNDERWRITER & CAM-00D SIGN-OFF",
        "start_sec": round(seg5_start, 3),
        "cam00_return_sec": round(cam00_return_sec, 3),
        "closing_ding_sec": round(closing_ding_sec, 3),
        "end_sec": round(seg5_end, 3),
        "subtitle": "On the next broadcast: an uninspected Dilithium barge rendezvous in the tail of Comet K-Four, and a suspected rhombus aboard a bulk ice-hauler. This broadcast is underwritten by Van Allen and Sons Switchgear—from radiation belts to reactor beds, if it arcs, we clamp it. From Asteroid 3-5-1 in Oort Cloud Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum.",
    })

    # --- SEG 6: 20-SECOND END-CARD OUTRO & CREDITS (O.R.S. 351 SATELLITE DOWNLINK) ---
    seg6_start = cursor_sec
    outro_dur = 20.0
    n_out = int(outro_dur * SAMPLE_RATE)
    tt_out = np.arange(n_out, dtype=np.float64) / SAMPLE_RATE

    chime_bed = np.zeros(n_out, dtype=np.float64)
    # Carry the remaining 5.25s sustain tail of the Seg 5 closing 1B chime seamlessly into Seg 6
    closing_tail = chime_1b_flt[seg5_chime_head_samples:] * 0.85
    chime_bed[: len(closing_tail)] += closing_tail
    pad = (
        0.35 * np.sin(2.0 * math.pi * 130.81 * tt_out)
        + 0.25 * np.sin(2.0 * math.pi * 196.00 * tt_out)
        + 0.18 * np.sin(2.0 * math.pi * 293.66 * tt_out)
    ) * (0.55 + 0.45 * np.sin(2.0 * math.pi * 0.18 * tt_out))
    chime_bed += pad * 0.08

    motif_freqs = [
        261.63, 392.00, 587.33, 659.25, 783.99, 880.00,
        739.99, 987.77, 783.99, 659.25, 587.33, 392.00,
    ]
    step_sec = 0.62
    for idx_n in range(28):
        t_note = 0.25 + idx_n * step_sec
        if t_note >= outro_dur - 1.5:
            break
        f_n = motif_freqs[idx_n % len(motif_freqs)]
        i0_n = int(t_note * SAMPLE_RATE)
        d_n = min(int(2.2 * SAMPLE_RATE), n_out - i0_n)
        tn = np.arange(d_n, dtype=np.float64) / SAMPLE_RATE
        env_n = (1.0 - np.exp(-tn / 0.012)) * np.exp(-tn / 0.72)
        tone_n = (
            0.68 * np.sin(2.0 * math.pi * f_n * tn)
            + 0.22 * np.sin(2.0 * math.pi * (2.0 * f_n) * tn) * np.exp(-tn / 0.35)
            + 0.10 * np.sin(2.0 * math.pi * (3.002 * f_n) * tn) * np.exp(-tn / 0.18)
        ) * env_n
        chime_bed[i0_n:i0_n + d_n] += tone_n * 0.16
        i_echo = i0_n + int(0.46 * SAMPLE_RATE)
        if i_echo < n_out:
            d_e = min(d_n, n_out - i_echo)
            chime_bed[i_echo:i_echo + d_e] += tone_n[:d_e] * 0.07

    i_res = int(16.2 * SAMPLE_RATE)
    d_res = n_out - i_res
    tr = np.arange(d_res, dtype=np.float64) / SAMPLE_RATE
    env_res = (1.0 - np.exp(-tr / 0.04)) * np.exp(-tr / 1.45)
    chord_res = (
        0.30 * np.sin(2.0 * math.pi * 261.63 * tr)
        + 0.25 * np.sin(2.0 * math.pi * 392.00 * tr)
        + 0.20 * np.sin(2.0 * math.pi * 587.33 * tr)
        + 0.15 * np.sin(2.0 * math.pi * 659.25 * tr)
        + 0.10 * np.sin(2.0 * math.pi * 987.77 * tr)
    ) * env_res
    chime_bed[i_res:] += chord_res * 0.22

    outro_voice_flt = bytes_to_float(seg_pcm_map["v32_seg6_outro"])
    v_start_idx = int(0.85 * SAMPLE_RATE)
    v_end_idx = min(n_out, v_start_idx + len(outro_voice_flt))
    v_len = v_end_idx - v_start_idx

    duck_env = np.ones(n_out, dtype=np.float64) * 1.15
    duck_env[max(0, v_start_idx - int(0.2 * SAMPLE_RATE)):min(n_out, v_end_idx + int(0.3 * SAMPLE_RATE))] = 0.55
    fade_out_len = int(2.0 * SAMPLE_RATE)
    duck_env[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)
    outro_mix = chime_bed * duck_env
    outro_mix[v_start_idx:v_end_idx] += outro_voice_flt[:v_len]

    append_chunk(float_to_bytes(np.clip(outro_mix, -0.95, 0.95)))
    seg6_end = cursor_sec
    timeline_events.append({
        "id": "seg6_outro",
        "console": "ORS-351",
        "title": "O.R.S. 351 • ORBITAL SATELLITE DOWNLINK & END CARDS",
        "start_sec": round(seg6_start, 3),
        "end_sec": round(seg6_end, 3),
        "subtitle": "Remember, a like indication on your listening apparatus gives us three kilowatts of Dilithium reserve, and a subscription gets us one step closer to shielding our marzelvane emitters.",
    })

    master_pcm = b"".join(master_chunks)

    # Mix real video clip audio from episodes/ep01_2736.305_parallelogram/clips/ into Segment 3
    clips_dir = EP_DIR / "clips"
    master_flt = bytes_to_float(master_pcm)

    def load_clip_audio(pattern: str) -> np.ndarray | None:
        matches = sorted(clips_dir.glob(pattern))
        if not matches:
            return None
        raw = subprocess.check_output(
            ["ffmpeg", "-v", "quiet", "-i", str(matches[0]), "-f", "s16le", "-ac", "1", "-ar", str(SAMPLE_RATE), "-"]
        )
        return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32767.0

    clip_3a = load_clip_audio("Buoy_bobbing*.mp4")
    if clip_3a is not None:
        t0_3a = max(sub3a_start, vig3a_start - 4.50)
        i0 = int(t0_3a * SAMPLE_RATE)
        n_c = min(len(clip_3a), len(master_flt) - i0)
        for k in range(n_c):
            t_abs = (i0 + k) / SAMPLE_RATE
            gain = 0.85 if (vig3a_start - 0.15 <= t_abs <= vig3a_end + 0.15) else 0.30
            master_flt[i0 + k] += clip_3a[k] * gain

    clip_3b = load_clip_audio("Engineer_hits_antenna*.mp4")
    if clip_3b is not None:
        v0 = int(vig3b_start * SAMPLE_RATE)
        v1 = int(vig3b_end * SAMPLE_RATE)
        master_flt[v0:v1] *= 0.35

        t0_3b = max(sub3b_start, vig3b_start - 5.20)
        i0 = int(t0_3b * SAMPLE_RATE)
        n_c = min(len(clip_3b), len(master_flt) - i0)
        for k in range(n_c):
            t_abs = (i0 + k) / SAMPLE_RATE
            if vig3b_start - 0.35 <= t_abs <= vig3b_end + 0.25:
                gain = 1.05
            elif t_abs < vig3b_start - 0.35:
                gain = 0.38
            else:
                gain = 0.30
            master_flt[i0 + k] += clip_3b[k] * gain

    clip_3c = load_clip_audio("Drift-buoy*.mp4")
    if clip_3c is not None:
        t0_3c = sub3c_start + 0.35
        i0 = int(t0_3c * SAMPLE_RATE)
        n_c = min(len(clip_3c), len(master_flt) - i0)
        master_flt[i0:i0 + n_c] += clip_3c[:n_c] * 0.45

    master_pcm = float_to_bytes(np.clip(master_flt, -0.96, 0.96))
    master_wav_path = RENDERS_DIR / "gor9_ep01_full_master.wav"
    save_wav_int16(master_wav_path, master_pcm)

    timeline_doc = {
        "broadcast": "GOR-9 • Broadcast 01 (2560x1440 QHD — 4-Console Edition)",
        "galactic_epoch": "2736.305",
        "galactic_time": "0400 GCT (Pulsar B1937+21 Barycentric Standard)",
        "sample_rate": SAMPLE_RATE,
        "total_duration_sec": round(cursor_sec, 3),
        "segments": timeline_events,
    }
    timeline_path = EP_DIR / "script" / "ep01_timeline.json"
    timeline_path.write_text(json.dumps(timeline_doc, indent=2), encoding="utf-8")
    print(f"Saved Full Broadcast Master WAV (with live clip audio): {master_wav_path} ({cursor_sec:.2f}s)")
    print(f"Saved Timeline Manifest: {timeline_path}")


if __name__ == "__main__":
    main()
