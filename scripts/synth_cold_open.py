#!/usr/bin/env python3
"""Synthesize the GOR-9 Cold Open in a SINGLE uninterrupted Argon III-C (voice_xdhacg1pn1cq)
TTS call—matching the exact voice timbre and prosody of the Euclid productions—and insert
the pure 24kHz harmonic crystal [ding-ding] chime into the natural pause after
'This is G-O-R 9. This is G-O-R 9.' with zero ffmpeg amix distortion.
"""

from pathlib import Path
import math
import os
import struct
import sys
import wave
import numpy as np

sys.path.insert(0, "/home/phi/.gemini/config/skills/dialogue/scripts")
import speak  # noqa: E402

SAMPLE_RATE = speak.SAMPLE_RATE
WORK_DIR = Path("/home/phi/PROJECTS/phiarchitect/GOR-9")


def make_ding_ding_pcm() -> bytes:
    """Two-note harmonic crystal interval signal (Fifth -> Octave) at 24kHz PCM."""
    note1 = speak.make_harmonic_bell_pcm([528.0, 792.0], duration=0.32, amp=0.15)
    gap = speak.silence_pcm(0.06)
    note2 = speak.make_harmonic_bell_pcm([440.0, 880.0], duration=0.52, amp=0.16)
    return note1 + gap + note2


def make_clean_tuning_lead_in(duration: float = 1.8) -> bytes:
    """Subtle, clean 24kHz synthesized shortwave heterodyne lock that finishes BEFORE voice starts."""
    n = int(SAMPLE_RATE * duration)
    rng = np.random.default_rng(3519)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    # Gentle band-limited static fade-out + heterodyne sweep locking to zero-beat
    fade_in = np.minimum(1.0, t / 0.25)
    fade_out = np.power(np.clip(1.0 - t / duration, 0.0, 1.0), 1.6)
    env = fade_in * fade_out
    noise = rng.normal(0.0, 0.035, size=n)
    # Simple moving-average bandpass feel
    noise = np.convolve(noise, np.ones(7) / 7.0, mode="same")
    # Sweeping heterodyne whistle (1400 Hz -> 440 Hz)
    phase = 2.0 * math.pi * (1400.0 * t - 480.0 * (t ** 2) / duration)
    whistle = np.sin(phase) * 0.028 * env
    sig = np.clip((noise * env + whistle) * 32767.0, -32767, 32767).astype(np.int16)
    return sig.tobytes()


def find_pause_after_opening(pcm_bytes: bytes) -> tuple[int, float]:
    """Find the natural sentence pause after 'This is G-O-R 9. This is G-O-R 9.' (between 2.2s and 4.4s)."""
    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    win = int(0.04 * SAMPLE_RATE)  # 40ms window
    s_min = int(2.1 * SAMPLE_RATE)
    s_max = min(len(samples) - win, int(4.5 * SAMPLE_RATE))

    # Compute RMS envelope in 10ms steps
    step = int(0.01 * SAMPLE_RATE)
    best_idx = int(3.1 * SAMPLE_RATE)
    best_rms = 1e9
    for idx in range(s_min, s_max, step):
        rms = float(np.sqrt(np.mean(samples[idx:idx + win] ** 2)))
        if rms < best_rms:
            best_rms = rms
            best_idx = idx + win // 2

    byte_offset = best_idx * 2  # 2 bytes per int16 sample
    return byte_offset, best_idx / SAMPLE_RATE


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set")

    profile = speak.load_profile()
    voice_id = profile["voice_id"]
    model = profile.get("model", "gemini-3.8-flash-tts")
    style_str = profile["styles"]["brisk"]

    # Single uninterrupted sentence block so Argon III-C uses the exact Euclid voice timbre
    full_text = (
        "This is G-O-R 9. This is G-O-R 9. "
        "Galactic Outpost Radio, broadcasting from the High Basalt Shelf on Asteroid 3-5-1 in Sector 9. "
        "Fourteen-two-eighty-five kilohertz upper sideband. Zero-four-hundred Galactic Coordinated."
    )

    raw_pcm = speak.synth_pcm_bytes(voice_id, full_text, style_str, model, api_key)
    split_byte, split_sec = find_pause_after_opening(raw_pcm)
    print(f"Found natural sentence pause after 'This is G-O-R 9. This is G-O-R 9.' at {split_sec:.2f}s")

    lead_in = make_clean_tuning_lead_in(1.80)
    intro_bell = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:context"]["freqs"],
        duration=0.45,
        amp=0.14,
    )
    ding_ding = make_ding_ding_pcm()
    outro_bell = speak.make_harmonic_bell_pcm(
        profile["bells"]["bell:proposition"]["freqs"],
        duration=0.55,
        amp=0.14,
    )

    part_a = raw_pcm[:split_byte]
    part_b = raw_pcm[split_byte:]

    final_pcm = (
        lead_in
        + intro_bell
        + speak.silence_pcm(0.12)
        + part_a
        + speak.silence_pcm(0.10)
        + ding_ding
        + speak.silence_pcm(0.12)
        + part_b
        + speak.silence_pcm(0.25)
        + outro_bell
        + speak.silence_pcm(0.60)
    )

    out_wav = WORK_DIR / "renders" / "cam00_cold_open_mix.wav"
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(final_pcm)

    total_sec = (len(final_pcm) // 2) / SAMPLE_RATE
    ding_start_sec = 1.80 + 0.45 + 0.12 + split_sec + 0.10
    print(f"Saved pure 24kHz Argon III-C Cold Open WAV: {out_wav} ({total_sec:.2f}s, ding-ding at {ding_start_sec:.2f}s)")


if __name__ == "__main__":
    main()
