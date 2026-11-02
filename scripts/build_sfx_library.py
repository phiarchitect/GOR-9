#!/usr/bin/env python3
"""Build the GOR-9 Crackly White-Noise & RF Static Sound Library (24kHz 16-bit PCM).

Also extracts the pure 24kHz Argon III-C Cold Open voice track from
renders/cam00_cold_open_mix.wav (if not already saved to renders/cam00_voice_pure_24k.wav)
and assembles the updated renders/cam00_cold_open_mix.wav with the new crackly
white-noise camera boot sequence and frame-accurate visual crackle envelope.
"""

from pathlib import Path
import json
import math
import wave
import numpy as np

SAMPLE_RATE = 24000
ROOT = Path(__file__).resolve().parent.parent
SFX_DIR = ROOT / "assets" / "sfx"
RENDERS_DIR = ROOT / "renders"


def save_wav(path: Path, samples_float: np.ndarray) -> None:
    """Save float64/float32 [-1.0, 1.0] mono array as 24kHz 16-bit WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(samples_float * 32767.0, -32767.0, 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def make_crisp_white_noise(n: int, rng: np.random.Generator, pre_emphasis: float = 0.55) -> np.ndarray:
    """Generate crisp, airy white/blue noise with high-frequency pre-emphasis."""
    raw = rng.normal(0.0, 1.0, size=n + 1)
    # First-order high-shelf difference boosts crisp high-frequency sizzle (3kHz-11kHz)
    crisp = raw[1:] - pre_emphasis * raw[:-1]
    crisp /= (np.std(crisp) + 1e-8)
    return crisp


def add_poisson_crackles(
    sig: np.ndarray,
    rng: np.random.Generator,
    rate_hz: float = 160.0,
    snap_rate_hz: float = 26.0,
    amp_ticks: float = 0.55,
    amp_snaps: float = 0.75,
) -> np.ndarray:
    """Overlay needle-sharp sferic ticks and multi-millisecond electrostatic crackle bursts."""
    n = len(sig)
    out = sig.copy()

    # 1. Fine needle-sharp bipolar ticks (0.2ms - 0.8ms)
    n_ticks = int((n / SAMPLE_RATE) * rate_hz)
    tick_positions = rng.integers(0, max(1, n - 24), size=n_ticks)
    for pos in tick_positions:
        dur = int(rng.integers(3, 16))
        polarity = 1.0 if rng.random() > 0.5 else -1.0
        strength = float(rng.uniform(0.35, 1.0)) * amp_ticks * polarity
        t_env = np.exp(-np.arange(dur) / 3.5)
        # Alternating high-frequency impulse
        osc = np.cos(np.arange(dur) * math.pi * float(rng.uniform(0.45, 0.85)))
        out[pos:pos + dur] += strength * t_env * osc

    # 2. Medium electrostatic crackle snaps (2ms - 10ms frying bursts)
    n_snaps = int((n / SAMPLE_RATE) * snap_rate_hz)
    snap_positions = rng.integers(0, max(1, n - 300), size=n_snaps)
    for pos in snap_positions:
        dur = int(rng.integers(45, 240))
        strength = float(rng.uniform(0.4, 1.0)) * amp_snaps
        t_env = np.exp(-np.arange(dur) / float(rng.uniform(18.0, 65.0)))
        burst = make_crisp_white_noise(dur, rng, pre_emphasis=0.75)
        out[pos:pos + dur] += strength * t_env * burst

    return out


def gen_cam_boot_crackle(rng: np.random.Generator) -> tuple[np.ndarray, list[float]]:
    """Generate the 2.70s Camera Crackle-In sound effect + 30fps visual static envelope."""
    duration = 2.70
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    # Base crisp white noise
    white = make_crisp_white_noise(n, rng, pre_emphasis=0.62) * 0.22

    # Stuttering carrier-hunt envelope:
    # Starts heavy (0.0-0.55s), briefly clears (0.55-0.85s), heavy burst (0.85-1.20s),
    # half-clear (1.20-1.60s), final sharp crackle surge (1.60-2.05s), then snaps clean at 2.45s
    env = np.zeros(n, dtype=np.float64)
    for i, ti in enumerate(t):
        if ti < 0.52:
            e = 0.95
        elif ti < 0.82:
            # First momentary image glimpse
            e = 0.22 + 0.15 * math.sin(ti * 45.0)
        elif ti < 1.18:
            # Heavy sync breakup burst
            e = 0.92
        elif ti < 1.58:
            # Second longer glimpse
            e = 0.18 + 0.10 * math.cos(ti * 60.0)
        elif ti < 1.98:
            # Sharp high-voltage static crackle before lock
            e = 0.85 * math.exp(-(ti - 1.60) * 1.2)
        elif ti < 2.42:
            # Rapidly clearing sputter
            e = 0.28 * math.pow(max(0.0, 1.0 - (ti - 1.98) / 0.44), 1.8)
        else:
            e = 0.0
        env[i] = max(0.0, min(1.0, e))

    sig = white * env
    crackle_layer = add_poisson_crackles(
        np.zeros(n), rng, rate_hz=220.0, snap_rate_hz=38.0, amp_ticks=0.55, amp_snaps=0.65
    )
    sig += crackle_layer * np.power(env, 0.7)

    # Add a subtle relay lock click at t = 2.44s
    click_idx = int(2.44 * SAMPLE_RATE)
    click_dur = 90
    sig[click_idx:click_idx + click_dur] += (
        np.exp(-np.arange(click_dur) / 14.0)
        * np.sin(np.arange(click_dur) * 0.65)
        * 0.42
    )

    sig = np.clip(sig * 0.65, -0.92, 0.92)

    # Compute 30fps visual static envelope from the envelope + high-frequency energy
    fps = 30
    n_frames = int(duration * fps)
    spf = SAMPLE_RATE // fps
    vis_env = []
    for f in range(n_frames):
        chunk = sig[f * spf:(f + 1) * spf]
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        peak = float(np.max(np.abs(chunk)))
        base_e = float(np.mean(env[f * spf:(f + 1) * spf]))
        v = min(1.0, 0.65 * base_e + 0.85 * rms + 0.25 * peak)
        if f * (1.0 / fps) >= 2.45:
            v = 0.0
        vis_env.append(round(v, 4))

    return sig, vis_env


def gen_white_noise_crackle_loop(rng: np.random.Generator, duration: float = 4.0) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    sig = make_crisp_white_noise(n, rng, pre_emphasis=0.65) * 0.16
    sig = add_poisson_crackles(sig, rng, rate_hz=190.0, snap_rate_hz=30.0, amp_ticks=0.45, amp_snaps=0.55)
    return np.clip(sig * 0.65, -0.9, 0.9)


def gen_squelch_burst(rng: np.random.Generator, duration: float = 0.80) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    env = np.exp(-t / 0.22) * (0.6 + 0.4 * np.cos(t * 55.0))
    sig = make_crisp_white_noise(n, rng, pre_emphasis=0.70) * 0.28 * env
    sig = add_poisson_crackles(sig, rng, rate_hz=260.0, snap_rate_hz=45.0, amp_ticks=0.55, amp_snaps=0.65) * env
    # Relay click at start
    sig[:80] += np.exp(-np.arange(80) / 12.0) * np.sin(np.arange(80) * 0.8) * 0.55
    return np.clip(sig * 0.75, -0.92, 0.92)


def gen_triboelectric_arc(rng: np.random.Generator, duration: float = 1.50) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    # 60Hz/120Hz plasma buzz modulation + sharp frying white noise crackle
    buzz_mod = 0.45 + 0.55 * np.abs(np.sin(2.0 * math.pi * 60.0 * t))
    env = np.sin(np.clip(t / duration, 0.0, 1.0) * math.pi) ** 0.6
    sig = make_crisp_white_noise(n, rng, pre_emphasis=0.80) * 0.24 * buzz_mod * env
    sig = add_poisson_crackles(sig, rng, rate_hz=340.0, snap_rate_hz=60.0, amp_ticks=0.65, amp_snaps=0.80) * env
    return np.clip(sig * 0.70, -0.92, 0.92)


def gen_geiger_ionospheric(rng: np.random.Generator, duration: float = 3.0) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    sig = make_crisp_white_noise(n, rng, pre_emphasis=0.50) * 0.07
    sig = add_poisson_crackles(sig, rng, rate_hz=110.0, snap_rate_hz=14.0, amp_ticks=0.60, amp_snaps=0.45)
    return np.clip(sig * 0.70, -0.90, 0.90)


def gen_carrier_drop_signoff(rng: np.random.Generator, duration: float = 3.0) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    # Ramps up from 0 into stuttering bursts, then fades out at the end
    ramp = np.clip(t / 1.4, 0.0, 1.0) ** 1.3
    tail_fade = np.clip((duration - t) / 0.7, 0.0, 1.0)
    env = ramp * tail_fade
    sig = make_crisp_white_noise(n, rng, pre_emphasis=0.65) * 0.22 * env
    sig = add_poisson_crackles(sig, rng, rate_hz=200.0, snap_rate_hz=32.0, amp_ticks=0.50, amp_snaps=0.60) * env
    return np.clip(sig * 0.70, -0.92, 0.92)


def main() -> None:
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Preserve pure 24kHz Argon III-C voice portion from cam00_cold_open_mix.wav (from t=1.80s onward)
    mix_wav = RENDERS_DIR / "cam00_cold_open_mix.wav"
    pure_voice_wav = RENDERS_DIR / "cam00_voice_pure_24k.wav"
    if not pure_voice_wav.exists() and mix_wav.exists():
        with wave.open(str(mix_wav), "rb") as wf:
            raw_bytes = wf.readframes(wf.getnframes())
        # In earlier synth_cold_open.py, lead_in was 1.80s (1.80 * 24000 * 2 = 86400 bytes)
        voice_part = raw_bytes[int(1.80 * SAMPLE_RATE) * 2:]
        with wave.open(str(pure_voice_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(voice_part)
        print(f"Extracted pure 24kHz Argon III-C voice track -> {pure_voice_wav}")

    rng = np.random.default_rng(90351)

    # 2. Generate the 6-file Crackly White-Noise & RF Static Library
    boot_sig, vis_env = gen_cam_boot_crackle(rng)
    save_wav(SFX_DIR / "crackle_cam_boot_2p8s.wav", boot_sig)

    save_wav(SFX_DIR / "white_noise_crackle_loop_4s.wav", gen_white_noise_crackle_loop(rng))
    save_wav(SFX_DIR / "shortwave_squelch_burst_0p8s.wav", gen_squelch_burst(rng))
    save_wav(SFX_DIR / "triboelectric_arc_crackle_1p5s.wav", gen_triboelectric_arc(rng))
    save_wav(SFX_DIR / "geiger_ionospheric_crackle_3s.wav", gen_geiger_ionospheric(rng))
    save_wav(SFX_DIR / "carrier_drop_signoff_3s.wav", gen_carrier_drop_signoff(rng))

    catalog = {
        "sample_rate": SAMPLE_RATE,
        "cam00_boot_visual_envelope_30fps": vis_env,
        "files": [
            {
                "name": "crackle_cam_boot_2p8s.wav",
                "duration_sec": 2.70,
                "description": "Crackly white-noise camera boot & stuttering carrier lock (drives CAM-00 visual crackle-in)",
            },
            {
                "name": "white_noise_crackle_loop_4s.wav",
                "duration_sec": 4.00,
                "description": "Crisp broadband white-noise hiss + dense needle-sharp Poisson sferic crackles",
            },
            {
                "name": "shortwave_squelch_burst_0p8s.wav",
                "duration_sec": 0.80,
                "description": "Rotary relay click + sharp crackly white-noise burst for console/camera switching",
            },
            {
                "name": "triboelectric_arc_crackle_1p5s.wav",
                "duration_sec": 1.50,
                "description": "60 kV electrostatic dust-storm coronal plasma arc crackle (Relay KZ9-OMEGA)",
            },
            {
                "name": "geiger_ionospheric_crackle_3s.wav",
                "duration_sec": 3.00,
                "description": "High-altitude ionospheric hiss with sharp cosmic-ray Geiger ticks",
            },
            {
                "name": "carrier_drop_signoff_3s.wav",
                "duration_sec": 3.00,
                "description": "Carrier breakup into crackly white-noise snow for broadcast sign-off",
            },
        ],
    }
    catalog_path = SFX_DIR / "sfx_catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Generated 6 crackly white-noise SFX files in {SFX_DIR} + {catalog_path}")

    # 3. Splice crackle_cam_boot_2p8s.wav + pure 24kHz Argon III-C voice into renders/cam00_cold_open_mix.wav
    if pure_voice_wav.exists():
        with wave.open(str(pure_voice_wav), "rb") as wf:
            voice_bytes = wf.readframes(wf.getnframes())
        boot_pcm = np.clip(boot_sig * 32767.0, -32767.0, 32767.0).astype(np.int16).tobytes()
        combined = boot_pcm + voice_bytes
        with wave.open(str(mix_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(combined)
        total_dur = (len(combined) // 2) / SAMPLE_RATE
        print(f"Updated {mix_wav} with 2.70s crackly white-noise boot + pure Argon III-C voice ({total_dur:.2f}s total)")


if __name__ == "__main__":
    main()
