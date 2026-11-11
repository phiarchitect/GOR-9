#!/usr/bin/env python3
"""Build Character Visual Reference Packs (Headshot + Full-Body for Google Flow)
and Synthesize Dry Studio + On-Air RF Voice & Language Samples (24 kHz WAV).

Populates:
- docs/assets/characters/char_<slug>_{headshot,fullbody}.jpg
- docs/assets/audio/voices/voice_<slug>_{dry,rf}.wav
- stations/<station_slug>/characters/ (all visual plates, dry/RF voice WAVs, and CHARACTERS.md)
- docs/data/stations.json & docs/data/stations_data.js
"""

import json
import math
import os
from pathlib import Path
import shutil
import sys
import wave
import numpy as np

try:
    from photon_platform.studio import speak
except ImportError:
    sys.path.insert(0, "/home/phi/PROJECTS/photon-platform/studio/src")
    from photon_platform.studio import speak  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
STATIONS_ROOT = ROOT / "stations"
DATA_JSON = DOCS / "data" / "stations.json"
DATA_JS = DOCS / "data" / "stations_data.js"
CHARS_DIR = DOCS / "assets" / "characters"
VOICES_DIR = DOCS / "assets" / "audio" / "voices"
ARTIFACT_DIR = Path("/home/phi/.gemini/antigravity/brain/4a15bd90-1dea-40db-80d9-26acb50c2eaf")

SAMPLE_RATE = 24000


def save_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(samples, -0.98, 0.98)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def load_wav_float(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32767.0


def bytes_to_float(pcm_bytes: bytes) -> np.ndarray:
    return np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float64) / 32767.0


def bandpass_simple(sig: np.ndarray, low_win: int = 9, high_win: int = 55) -> np.ndarray:
    """Fast time-domain telephone/shortwave bandpass approximation."""
    lp = np.convolve(sig, np.ones(low_win) / low_win, mode="same")
    hp_base = np.convolve(lp, np.ones(high_win) / high_win, mode="same")
    bp = lp - hp_base
    peak = np.max(np.abs(bp)) + 1e-8
    return bp / peak * 0.78


def sync_character_images() -> dict[str, Path]:
    """Copy generated character headshot & fullbody plates from artifact dir to docs/assets/characters/."""
    CHARS_DIR.mkdir(parents=True, exist_ok=True)
    mapping = {
        "char_chen_torch_wei_headshot": "char_chen_torch_wei_headshot.jpg",
        "char_chen_torch_wei_fullbody": "char_chen_torch_wei_fullbody.jpg",
        "char_ah_mei_zhou_headshot": "char_ah_mei_zhou_headshot.jpg",
        "char_ah_mei_zhou_fullbody": "char_ah_mei_zhou_fullbody.jpg",
        "char_cantor_auren7_headshot": "char_cantor_auren7_headshot.jpg",
        "char_cantor_auren7_fullbody": "char_cantor_auren7_fullbody.jpg",
        "char_capt_rafa_headshot": "char_capt_rafa_headshot.jpg",
        "char_capt_rafa_fullbody": "char_capt_rafa_fullbody.jpg",
        "char_zora_kovac_headshot": "char_zora_kovac_headshot.jpg",
        "char_zora_kovac_fullbody": "char_zora_kovac_fullbody.jpg",
        "char_liang_and_arturo_headshot": "char_liang_and_arturo_headshot.jpg",
        "char_liang_and_arturo_fullbody": "char_liang_and_arturo_fullbody.jpg",
        "char_harlon_vance_headshot": "char_harlon_vance_headshot.jpg",
        "char_harlon_vance_fullbody": "char_harlon_vance_fullbody.jpg",
        "char_silt_strider_headshot": "char_silt_strider_headshot.jpg",
        "char_silt_strider_fullbody_clean": "char_silt_strider_fullbody.jpg",
        "char_solene_moreau_headshot": "char_solene_moreau_headshot.jpg",
        "char_solene_moreau_fullbody": "char_solene_moreau_fullbody.jpg",
        "char_vael_choir_headshot_varied": "char_vael_choir_headshot.jpg",
        "char_vael_choir_fullbody_varied": "char_vael_choir_fullbody.jpg",
    }
    synced: dict[str, Path] = {}
    if ARTIFACT_DIR.exists():
        for prefix, dst_name in mapping.items():
            matches = sorted(ARTIFACT_DIR.glob(f"{prefix}_*.jpg"))
            if matches:
                dst = CHARS_DIR / dst_name
                shutil.copy2(matches[-1], dst)
                synced[dst_name] = dst
                print(f"Synced character plate -> {dst.relative_to(ROOT)}")
    return synced


def synth_silt_strider_bio_audio() -> tuple[np.ndarray, np.ndarray]:
    """Synthesize the Kraken Shallows Silt-Strider's piezoelectric throat-sac vocalization
    (clicks + sub-harmonic lagoon call + bio-mimicked 880 Hz CW Morse 'VVV DE TM-N24/B')."""
    dur = 6.2
    n = int(SAMPLE_RATE * dur)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(389024)

    dry = np.zeros(n, dtype=np.float64)

    # 1. Resonant piezoelectric carapace clicks (t = 0.2..1.3s)
    for tc in (0.22, 0.36, 0.48, 0.72, 0.84, 0.94, 1.15):
        i0 = int(tc * SAMPLE_RATE)
        d = int(0.06 * SAMPLE_RATE)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        click = (
            0.6 * np.sin(2.0 * math.pi * 1420.0 * tt)
            + 0.4 * np.sin(2.0 * math.pi * 2380.0 * tt)
        ) * np.exp(-tt / 0.009)
        dry[i0:i0 + d] += click * 0.55

    # 2. Deep bioluminescent throat-sac harmonic call (t = 1.35..2.85s)
    i0 = int(1.35 * SAMPLE_RATE)
    d = int(1.45 * SAMPLE_RATE)
    tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
    f_glide = 220.0 + 95.0 * np.sin(math.pi * tt / 1.45) - 45.0 * (tt / 1.45)
    ph = 2.0 * math.pi * np.cumsum(f_glide) / SAMPLE_RATE
    env = np.sin(math.pi * tt / 1.45) ** 0.7
    call = (
        0.55 * np.sin(ph)
        + 0.30 * np.sin(2.0 * ph + 0.4)
        + 0.15 * np.sin(3.0 * ph)
    ) * env
    dry[i0:i0 + d] += call * 0.65

    # 3. Organic flute-like bio-mimicked Morse 'VVV' (•••— •••— •••—) at ~880 Hz with vibrato (t = 3.05..5.95s)
    morse_notes = [
        # V (•••—)
        (3.10, 0.11), (3.27, 0.11), (3.44, 0.11), (3.62, 0.32),
        # V (•••—)
        (4.12, 0.11), (4.29, 0.11), (4.46, 0.11), (4.64, 0.32),
        # V with -165 Hz capacitive rub bend!
        (5.12, 0.11), (5.29, 0.11), (5.46, 0.52),
    ]
    for idx_m, (t0, dur_m) in enumerate(morse_notes):
        im0 = int(t0 * SAMPLE_RATE)
        dm = min(int(dur_m * SAMPLE_RATE), n - im0)
        tt = np.arange(dm, dtype=np.float64) / SAMPLE_RATE
        vib = 7.5 * np.sin(2.0 * math.pi * 6.2 * tt)
        if idx_m == len(morse_notes) - 1:
            # Downward -165 Hz pitch bend as it rubs the guy-wire
            f_inst = 880.0 + vib - 165.0 * np.sin(math.pi * tt / dur_m)
        else:
            f_inst = 880.0 + vib
        ph_m = 2.0 * math.pi * np.cumsum(f_inst) / SAMPLE_RATE
        env_m = np.sin(math.pi * tt / dur_m) ** 0.45
        flute = (0.72 * np.sin(ph_m) + 0.28 * np.sin(2.0 * ph_m)) * env_m
        dry[im0:im0 + dm] += flute * 0.58

    dry = dry / (np.max(np.abs(dry)) + 1e-8) * 0.85

    # RF Treated version adds Buoy N-24 brass fog-bell clank, methane wave lapping, and 75m HF static
    rf = dry.copy() * 0.80
    noise = np.convolve(rng.normal(0.0, 0.04, size=n), np.ones(11) / 11.0, mode="same")
    for tb in (0.08, 2.92):
        ib = int(tb * SAMPLE_RATE)
        db = min(int(0.75 * SAMPLE_RATE), n - ib)
        tt = np.arange(db, dtype=np.float64) / SAMPLE_RATE
        bell = (
            0.5 * np.sin(2.0 * math.pi * 612.0 * tt)
            + 0.35 * np.sin(2.0 * math.pi * 1148.0 * tt)
        ) * np.exp(-tt / 0.18)
        rf[ib:ib + db] += bell * 0.30
    rf = np.clip(rf + noise, -0.92, 0.92)
    return dry, rf


def shortwave_receiver_chain(
    sig: np.ndarray,
    rng: np.random.Generator,
    drive: float = 2.35,
    noise_floor: float = 0.068,
    qsb_depth: float = 0.38,
    qsb_rate_hz: float = 0.34,
    qrn_crashes: int = 5,
    low_win: int = 8,
    high_win: int = 40,
) -> np.ndarray:
    """Authentic shortwave / deep-space communications receiver IF & AGC processor:
    1. Narrowband ceramic IF bandpass filter (low_win..high_win)
    2. Ionospheric skywave multipath comb-filtering & selective fading (QSB)
    3. Asymmetric vacuum-tube / diode detector saturation (drive)
    4. Receiver AGC pumping (noise floor rushes up between words/phrases and ducks on loud peaks!)
    5. Crackling atmospheric/nebula static crashes (QRN)
    """
    n = len(sig)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    # 1. Narrowband IF bandpass
    bp = bandpass_simple(sig, low_win, high_win)

    # 2. Selective fading (QSB): time-varying skywave multipath delay (0.6ms..2.1ms)
    delay_sec = 0.0013 + 0.00075 * np.sin(2.0 * math.pi * qsb_rate_hz * t + 0.9)
    idx_base = np.arange(n, dtype=np.float64)
    idx_del = np.clip(idx_base - delay_sec * SAMPLE_RATE, 0, n - 1)
    skywave = np.interp(idx_del, idx_base, bp)
    qsb_env = (1.0 - qsb_depth * 0.5) + (qsb_depth * 0.5) * np.sin(
        2.0 * math.pi * qsb_rate_hz * t + 0.4 * np.sin(2.0 * math.pi * 0.11 * t)
    )
    faded = (bp * 0.72 + skywave * 0.48) * qsb_env

    # 3. Hard tube/diode detector compression & harmonic grit
    saturated = np.tanh(faded * drive + 0.14 * (faded ** 2))

    # 4. Receiver AGC envelope detector: boosts quiet sections & breathes noise floor in pauses!
    win_agc = int(0.18 * SAMPLE_RATE)
    sig_env = np.convolve(np.abs(saturated), np.ones(win_agc) / win_agc, mode="same")
    sig_env = sig_env / (np.max(sig_env) + 1e-8)
    # AGC gain clamps down on loud peaks and opens wide (+6 dB) during pauses
    agc_gain = 1.0 / (0.42 + 0.85 * sig_env)
    compressed_voice = saturated * agc_gain * 0.56

    # 5. Band-limited HF static floor + QRN crackling static bursts modulated by AGC!
    raw_noise = rng.normal(0.0, 1.0, size=n)
    hf_noise = bandpass_simple(raw_noise, low_win=6, high_win=44) * noise_floor
    # Add random crackling QRN static crashes
    for _ in range(qrn_crashes):
        ic = int(rng.uniform(0.03, 0.95) * n)
        dc = min(int(rng.uniform(0.08, 0.32) * SAMPLE_RATE), n - ic)
        if dc > 0:
            tt = np.arange(dc, dtype=np.float64) / SAMPLE_RATE
            crash_env = np.sin(math.pi * tt / (dc / SAMPLE_RATE)) ** 0.5
            spiky = rng.normal(0.0, 1.0, size=dc) * (np.abs(rng.normal(0.0, 1.0, size=dc)) > 0.85)
            hf_noise[ic:ic + dc] += spiky * crash_env * (noise_floor * 2.8)

    # Noise breathes up when signal envelope drops (classic shortwave AGC rush!)
    noise_pumped = hf_noise * (0.55 + 0.95 * (1.0 - 0.65 * sig_env))

    out = compressed_voice + noise_pumped
    peak = np.max(np.abs(out)) + 1e-8
    return np.clip(out / peak * 0.90, -0.92, 0.92)


def apply_station_rf_dsp(dry: np.ndarray, dsp_key: str) -> np.ndarray:
    """Transform a clean studio dry voice sample into an authentic on-air RF broadcast intercept."""
    n = len(dry)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    rng = np.random.default_rng(abs(hash(dsp_key)) % (2**31 - 1))

    if dsp_key == "sw4_torch":
        # +18.4 dB overmodulated AM blowtorch + heavy tube compression + sizzling plasma torch arc!
        mixed = dry.copy()
        t_arc = max(0.5, (n / SAMPLE_RATE) - 2.2)
        ia = int(t_arc * SAMPLE_RATE)
        da = min(int(1.25 * SAMPLE_RATE), n - ia)
        if da > 0:
            tt = np.arange(da, dtype=np.float64) / SAMPLE_RATE
            env_a = np.sin(math.pi * tt / (da / SAMPLE_RATE)) ** 0.5
            sizzle = rng.normal(0.0, 0.28, size=da) * env_a
            whistle = np.sin(2.0 * math.pi * (1100.0 + 750.0 * tt) * tt) * 0.16 * env_a
            mixed[ia:ia + da] += sizzle + whistle
        return shortwave_receiver_chain(mixed, rng, drive=2.85, noise_floor=0.072, qsb_depth=0.35, qrn_crashes=6)

    if dsp_key == "sw4_ah_mei":
        # Warm Callisto night-market AM broadcast + pentatonic electric lute chord + shortwave QSB/static
        lute = np.zeros(n, dtype=np.float64)
        for t0, f0 in [(0.05, 392.0), (0.28, 440.0), (0.52, 523.25), (0.76, 587.33)]:
            i0 = int(t0 * SAMPLE_RATE)
            d = min(int(0.32 * SAMPLE_RATE), n - i0)
            if d > 0:
                tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
                lute[i0:i0 + d] += np.sin(2.0 * math.pi * f0 * tt) * np.exp(-tt / 0.12) * 0.20
        return shortwave_receiver_chain(dry + lute, rng, drive=2.45, noise_floor=0.065, qsb_depth=0.32, qrn_crashes=5)

    if dsp_key == "n24_mariette":
        # 1980s French LPC speech ROM + -165 Hz capacitive pitch bend + 75m maritime HF static
        q_step = 3
        bp_q = np.repeat(dry[::q_step], q_step)[:n]
        f_carrier = 880.0 - 165.0 * (0.5 + 0.5 * np.sin(2.0 * math.pi * 0.35 * t))
        cw_under = np.sin(2.0 * math.pi * np.cumsum(f_carrier) / SAMPLE_RATE) * 0.08
        return shortwave_receiver_chain(bp_q + cw_under, rng, drive=2.30, noise_floor=0.075, qsb_depth=0.40, qrn_crashes=6)

    if dsp_key == "n24_solene":
        # Field hydrophone tape recorder + Silt-Strider lagoon resonance + USB shortwave link compression
        lagoon = np.sin(2.0 * math.pi * 240.0 * t + 1.5 * np.sin(2.0 * math.pi * 0.8 * t)) * 0.05
        return shortwave_receiver_chain(dry + lagoon, rng, drive=2.10, noise_floor=0.058, qsb_depth=0.28, qrn_crashes=4)

    if dsp_key == "m33_ds771":
        # 21-cm H-I Deep-Field Sonde 4.2W QRP via 2.73-Mly gravitational lens: heavy cosmic hiss & FSK ring!
        ring_mod = 0.72 + 0.28 * np.cos(2.0 * math.pi * 75.0 * t)
        maser_chord = (
            0.05 * np.sin(2.0 * math.pi * 432.0 * t)
            + 0.035 * np.sin(2.0 * math.pi * 720.0 * t)
        )
        return shortwave_receiver_chain(dry * ring_mod + maser_chord, rng, drive=2.50, noise_floor=0.085, qsb_depth=0.45, qrn_crashes=7)

    if dsp_key == "e08_yl8":
        # Cold numbers-station USB filter + 641.928 Hz pulsar buzzer hum + 5-note Lydian glockenspiel intro
        hum = (
            0.065 * np.sin(2.0 * math.pi * 641.928 * t)
            + 0.035 * np.sin(2.0 * math.pi * 320.964 * t)
        )
        chime = np.zeros(n, dtype=np.float64)
        for idx_c, f_c in enumerate([523.25, 587.33, 659.25, 739.99, 783.99]):
            ic = int(idx_c * 0.22 * SAMPLE_RATE)
            dc = min(int(0.28 * SAMPLE_RATE), n - ic)
            if dc > 0:
                tt = np.arange(dc, dtype=np.float64) / SAMPLE_RATE
                chime[ic:ic + dc] += np.sin(2.0 * math.pi * f_c * tt) * np.exp(-tt / 0.09) * 0.18
        return shortwave_receiver_chain(dry + hum + chime, rng, drive=2.40, noise_floor=0.070, qsb_depth=0.36, qrn_crashes=6)

    if dsp_key == "e08_caretakers":
        # Open studio mic room-reverb + whistling stainless-steel tea-kettle @ 2,150 Hz + USB static!
        delay = int(0.065 * SAMPLE_RATE)
        echo = np.zeros_like(dry)
        if delay < n:
            echo[delay:] = dry[:-delay] * 0.38
        kettle_f = 2120.0 + 45.0 * np.sin(2.0 * math.pi * 0.4 * t) + 12.0 * np.sin(2.0 * math.pi * 8.0 * t)
        kettle = np.sin(2.0 * math.pi * np.cumsum(kettle_f) / SAMPLE_RATE) * 0.065
        return shortwave_receiver_chain(dry + echo + kettle, rng, drive=2.35, noise_floor=0.072, qsb_depth=0.35, qrn_crashes=5)

    if dsp_key == "pedregal_rafa":
        # 3-Watt cookie-tin QRP SSB filter + nylon-string guitar arpeggio + cometary ion-tail flutter!
        flutter = 0.68 + 0.32 * np.sin(2.0 * math.pi * 3.1 * t + 0.7 * np.sin(2.0 * math.pi * 0.8 * t))
        guitar = np.zeros(n, dtype=np.float64)
        for idx_g, f_g in enumerate([220.0, 277.18, 329.63, 440.0]):
            ig = int(idx_g * 0.24 * SAMPLE_RATE)
            dg = min(int(0.55 * SAMPLE_RATE), n - ig)
            if dg > 0:
                tt = np.arange(dg, dtype=np.float64) / SAMPLE_RATE
                guitar[ig:ig + dg] += (
                    0.7 * np.sin(2.0 * math.pi * f_g * tt)
                    + 0.3 * np.sin(2.0 * math.pi * 2.0 * f_g * tt)
                ) * np.exp(-tt / 0.22) * 0.20
        return shortwave_receiver_chain(dry * flutter + guitar, rng, drive=2.55, noise_floor=0.082, qsb_depth=0.45, qrn_crashes=7)

    if dsp_key == "kz9_vance":
        # 50 kW over-driven AM relay + 120 Hz power supply hum + 60 kV plasma-arc splatter burst!
        hum_120 = 0.055 * np.sin(2.0 * math.pi * 120.0 * t)
        mixed = dry + hum_120
        ia = int(min(n * 0.65, n - SAMPLE_RATE))
        da = min(int(0.95 * SAMPLE_RATE), n - ia)
        if da > 0:
            tt = np.arange(da, dtype=np.float64) / SAMPLE_RATE
            arc_env = np.sin(math.pi * tt / (da / SAMPLE_RATE)) ** 0.4
            arc = (
                rng.normal(0.0, 0.35, size=da)
                + 0.18 * np.sin(2.0 * math.pi * 1840.0 * tt)
            ) * arc_env
            mixed[ia:ia + da] += arc
        return shortwave_receiver_chain(mixed, rng, drive=2.90, noise_floor=0.075, qsb_depth=0.34, qrn_crashes=6)

    if dsp_key == "rfh_zora":
        # Balkan button-accordion chord riff + Ceres Syndicate noise-jammer + VFO frequency-hop chirp!
        acc = np.zeros(n, dtype=np.float64)
        for idx_a, f_a in enumerate([293.66, 349.23, 440.0, 466.16, 554.37, 440.0]):
            ia = int(idx_a * 0.20 * SAMPLE_RATE)
            da = min(int(0.19 * SAMPLE_RATE), n - ia)
            if da > 0:
                tt = np.arange(da, dtype=np.float64) / SAMPLE_RATE
                reed = (
                    0.55 * np.sin(2.0 * math.pi * f_a * tt)
                    + 0.45 * np.sin(2.0 * math.pi * (f_a * 1.004) * tt)
                ) * 0.16
                acc[ia:ia + da] += reed
        mixed = dry + acc
        ih = max(0, n - int(0.65 * SAMPLE_RATE))
        dh = n - ih
        if dh > 0:
            tt = np.arange(dh, dtype=np.float64) / SAMPLE_RATE
            f_hop = 700.0 + 1800.0 * (tt / (dh / SAMPLE_RATE))
            mixed[ih:] += np.sin(2.0 * math.pi * np.cumsum(f_hop) / SAMPLE_RATE) * 0.22
        return shortwave_receiver_chain(mixed, rng, drive=2.45, noise_floor=0.074, qsb_depth=0.38, qrn_crashes=6)

    if dsp_key == "vjb_auren7":
        # 1,140-ly Tri-Band Piezo-Spire Intercept (9290.118 kHz SW + 1420 MHz H-I):
        # Parabolic shell reflections + 118 Hz Doppler carrier beat + piezo-corona crackle on loud gong/choir peaks
        # + authentic shortwave IF tube compression, selective fading (QSB), and AGC noise pumping!
        delay1 = int(0.048 * SAMPLE_RATE)
        delay2 = int(0.115 * SAMPLE_RATE)
        rev = dry.copy() * 0.82
        if delay1 < n:
            rev[delay1:] += dry[:-delay1] * 0.28
        if delay2 < n:
            rev[delay2:] += dry[:-delay2] * 0.16
        # 118 Hz Doppler carrier offset beat-note + 220 Hz piezo-arch sub-harmonic
        carrier_beat = (
            0.032 * np.sin(2.0 * math.pi * 118.0 * t)
            + 0.020 * np.sin(2.0 * math.pi * 220.0 * t)
        )
        # Piezo-spire corona crackle triggered whenever the gong/choir hits high amplitude
        env_peak = np.convolve(np.abs(rev), np.ones(480) / 480.0, mode="same")
        corona_gate = np.clip((env_peak - 0.32) * 2.5, 0.0, 1.0)
        corona_crackle = rng.normal(0.0, 0.085, size=n) * corona_gate
        return shortwave_receiver_chain(
            rev + carrier_beat + corona_crackle,
            rng,
            drive=2.35,
            noise_floor=0.068,
            qsb_depth=0.40,
            qsb_rate_hz=0.28,
            qrn_crashes=6,
            low_win=7,
            high_win=42,
        )

    return shortwave_receiver_chain(dry, rng)


CHARACTER_VOICE_SPECS = [
    {
        "station_id": "radio-corrugated",
        "char_index": 0,
        "slug": "chen_torch_wei",
        "headshot": "assets/characters/char_chen_torch_wei_headshot.jpg",
        "fullbody": "assets/characters/char_chen_torch_wei_fullbody.jpg",
        "voice_id": "Orus",
        "style": "speaking in a lively, raspy, warm night-market shortwave pirate cadence, shifting smoothly between Cantonese-Mandarin dock greetings and enthusiastic English RF tinker jargon",
        "dsp_key": "sw4_torch",
        "script": (
            "Wei! Callisto Dome-Four Night Market, Stall Nineteen on eleven-four-ten kilohertz! "
            "Hao le, Ah-Mei, pass me the silver-copper brazing rod—watch the plate current climb "
            "eighteen decibels when I touch the torch to the radiator!"
        ),
        "phonetic_and_conlang_notes": "Callisto Dome-4 Dock Patois: blends Cantonese/Mandarin night-market exclamations ('Wei!', 'Hao le!') with vacuum-tube RF slang.",
    },
    {
        "station_id": "radio-corrugated",
        "char_index": 1,
        "slug": "ah_mei_zhou",
        "headshot": "assets/characters/char_ah_mei_zhou_headshot.jpg",
        "fullbody": "assets/characters/char_ah_mei_zhou_fullbody.jpg",
        "voice_id": "Aoede",
        "style": "speaking warmly, playfully, and melodically like a bustling night-market noodle chef teasing her husband on a live shortwave broadcast",
        "dsp_key": "sw4_ah_mei",
        "script": (
            "Lai la, lai la! Fresh star-anise bone broth and hand-pulled noodles at Stall Nineteen! "
            "Chen Wei, put down that plasma torch before you splatter twenty kilohertz across the whole market—come kiss the chef first!"
        ),
        "phonetic_and_conlang_notes": "Musical night-market vendor cadence ('Lai la, lai la!') with warm domestic banter over sizzling broth.",
    },
    {
        "station_id": "buoy-n24",
        "char_index": 0,
        "slug": "mariette4_rom",
        "headshot": "assets/plates/flow_n24_onboard_pov_a.jpg",
        "fullbody": "assets/plates/flow_n24_onboard_rub_b.jpg",
        "voice_id": "Leda",
        "style": "speaking in a clipped, measured, hypnotic 1980s French maritime speech-synthesizer cadence reciting official hydrographic tide tables",
        "dsp_key": "n24_mariette",
        "script": (
            "V-V-V de T-M-N-vingt-quatre barre B. Bureau Hydrographique de Titan-Mineur. "
            "Marée de méthane secteur nord: quatre virgule deux mètres. "
            "Densité: zéro virgule quatre-deux-quatre. Vent nul."
        ),
        "phonetic_and_conlang_notes": "Formal French Maritime Hydrographic Standard ('Marée de méthane secteur nord') synthesized with LPC formant stepping.",
    },
    {
        "station_id": "buoy-n24",
        "char_index": 1,
        "slug": "silt_strider",
        "headshot": "assets/characters/char_silt_strider_headshot.jpg",
        "fullbody": "assets/characters/char_silt_strider_fullbody.jpg",
        "voice_id": "BIO_SYNTH",
        "style": "bio-acoustic piezoelectric carapace clicks and vocalized 880 Hz Morse mimicry",
        "dsp_key": "n24_strider",
        "script": "[Bio-Acoustic Call]: Piezoelectric carapace clicks -> 220 Hz throat-sac lagoon resonance -> 880 Hz vocalized Morse mimicry ('VVV' with -165 Hz guy-wire rub bend).",
        "phonetic_and_conlang_notes": "Non-human bio-acoustic communication: combines 1.4 kHz chitinous clicks, 220 Hz methane-lagoon throat-sac calls, and learned 880 Hz ITU Morse mimicry.",
    },
    {
        "station_id": "buoy-n24",
        "char_index": 2,
        "slug": "solene_moreau",
        "headshot": "assets/characters/char_solene_moreau_headshot.jpg",
        "fullbody": "assets/characters/char_solene_moreau_fullbody.jpg",
        "voice_id": "Kore",
        "style": "speaking in a hushed, fascinated French-inflected scientific field-recording voice, as if whispering into a reel-to-reel hydrophone recorder at twilight",
        "dsp_key": "n24_solene",
        "script": (
            "Ici Solène Moreau, station acoustique Kraken-Nord. Listen closely to the hydrophone—the Silt-Strider "
            "isn't just rubbing its neck against Guy-Wire Number Two for the warmth. Its throat-sac is singing the buoy's Morse code back to the lagoon!"
        ),
        "phonetic_and_conlang_notes": "Bilingual French-Québécois / English scientific field log recorded on portable hydrophone tape.",
    },
    {
        "station_id": "m33-drift-buoy",
        "char_index": 0,
        "slug": "ds771_sonde",
        "headshot": "assets/plates/flow_m33_onboard_cam_a.jpg",
        "fullbody": "assets/plates/flow_m33_onboard_cam_b.jpg",
        "voice_id": "Charon",
        "style": "speaking in a flat, metallic, uninflected automated telemetry transponder vocoder cadence reading barometric sensor registers",
        "dsp_key": "m33_ds771",
        "script": (
            "Deep-Field Survey Telemetry Unit D-S-seven-seven-one dash zero-four. Veyra-Three Basin. "
            "Barometer reed: nine-four-two millibars, locked. Warning: Force-Eight gale, six-meter swells. "
            "Ambient moisture: zero point zero zero percent dry alkali salt."
        ),
        "phonetic_and_conlang_notes": "Deep-Field Survey Telemetry Protocol: deterministic alphanumeric register readout locked to the 21-cm Hydrogen line.",
    },
    {
        "station_id": "trojan-octal",
        "char_index": 0,
        "slug": "yl8_octal",
        "headshot": "assets/plates/flow_hektor_canyon_architecture.jpg",
        "fullbody": "assets/plates/flow_hektor_canyon_architecture.jpg",
        "voice_id": "Kore",
        "style": "speaking in a cold, hypnotic, uninflected shortwave numbers-station monotone reading three-digit octal cipher groups",
        "dsp_key": "e08_yl8",
        "script": (
            "Atención: Tres, Cinco, Octal. Attention: Three, Five, Octal. "
            "Group count eight. Zero-four-seven. Three-one-two. Seven-seven-one. Three-five-one. Zero-one-five. Fin de transmisión."
        ),
        "phonetic_and_conlang_notes": "Bilingual Spanish/English Base-8 (Octal 0–7) cryptographic numbers-station cadence.",
    },
    {
        "station_id": "trojan-octal",
        "char_index": 1,
        "slug": "liang_and_arturo",
        "headshot": "assets/characters/char_liang_and_arturo_headshot.jpg",
        "fullbody": "assets/characters/char_liang_and_arturo_fullbody.jpg",
        "voice_id": "Puck",
        "style": "speaking like two grumpy, excitable old bunker caretakers bickering in Spanglish over a whistling tea-kettle and dumpling dough without realizing the studio mic is live",
        "dsp_key": "e08_caretakers",
        "script": (
            "Arturo, apaga la pava, the red microphone light is on! "
            "Qué micrófono ni ocho cuartos, Old Liang! I told you, eight pleats per dumpling wrapper, three-hundred-fifty-one grams of dough!"
        ),
        "phonetic_and_conlang_notes": "Bunker Caretaker Spanglish: domestic Porteño Spanish & English argument accidentally broadcast behind the octal cipher.",
    },
    {
        "station_id": "pedregal-utility",
        "char_index": 0,
        "slug": "capt_rafa",
        "headshot": "assets/characters/char_capt_rafa_headshot.jpg",
        "fullbody": "assets/characters/char_capt_rafa_fullbody.jpg",
        "voice_id": "Fenrir",
        "style": "speaking in a warm, jovial, folksy coastal Mexican Spanish and English ice-tug captain voice, full of heart and camaraderie",
        "dsp_key": "pedregal_rafa",
        "script": (
            "Buenas madrugadas a toda la flota hielera del Sector Nueve! "
            "This is Captain Rafa aboard the Boca del Río on sixty-nine-sixty-nine point five. "
            "Three watts coming out of my Danish butter-cookie tin, pero con corazón de cincuenta kilovatios!"
        ),
        "phonetic_and_conlang_notes": "Veracruz Maritime Spanish & Oort Ice-Fleet Spanglish ('flota hielera', 'lata de galletas danesas').",
    },
    {
        "station_id": "kz9-omega",
        "char_index": 0,
        "slug": "harlon_vance",
        "headshot": "assets/characters/char_harlon_vance_headshot.jpg",
        "fullbody": "assets/characters/char_harlon_vance_fullbody.jpg",
        "voice_id": "Orus",
        "style": "speaking in a frazzled, sleep-deprived, defensive corporate relay engineer voice on the verge of high-voltage panic",
        "dsp_key": "kz9_vance",
        "script": (
            "This is Chief Engineer Harlon Vance at Meridian Relay KZ9-Omega on seventy-one-forty. "
            "Do not cite us for sixty-kilohertz splatter! We are in a Force-Nine silicate dust storm, "
            "the marzelvane bushings are wobbling four point eight degrees, and Tower One just took a sixty-kilovolt arc!"
        ),
        "phonetic_and_conlang_notes": "Corporate High-Voltage Switchgear Jargon ('marzelvane bushings', 'sixty-kilohertz splatter', 'ceramic standoff').",
    },
    {
        "station_id": "radio-free-hektor",
        "char_index": 0,
        "slug": "zora_kovac",
        "headshot": "assets/characters/char_zora_kovac_headshot.jpg",
        "fullbody": "assets/characters/char_zora_kovac_fullbody.jpg",
        "voice_id": "Aoede",
        "style": "speaking in a fiery, laughing, defiant Balkan-inflected rebel pirate radio voice full of joy and mischief",
        "dsp_key": "rfh_zora",
        "script": (
            "Dobro jutro, slobodna braćo na Hektoru! Good morning free miners of Shard Six-Two-Four, this is Zora on Radio Free Hektor! "
            "I see the Ceres jammer warming up on sixty-four-forty—too slow, boys! Hold onto your accordion, we're hopping to sixty-four-forty-five right now!"
        ),
        "phonetic_and_conlang_notes": "Trojan L4 Rebel Patois: Balkan Serbo-Croatian greetings ('Dobro jutro, slobodna braćo!') mixed with frequency-hopping pirate calls.",
    },
    {
        "station_id": "st-jerome-slag",
        "char_index": 0,
        "slug": "cantor_auren7",
        "headshot": "assets/characters/char_cantor_auren7_headshot.jpg",
        "fullbody": "assets/characters/char_cantor_auren7_fullbody.jpg",
        "voice_id": "KAELEN_CALL_RESPONSE",
        "style": "antiphonal One-to-Many call and response chanting between Lead Cantor Auren-7 and the 4-voice Choir of the Fluted Shells",
        "dsp_key": "vjb_auren7",
        "script": (
            "[ONE — Lead Cantor Auren-7]: \"Vael-kora... auren-shi... Tune the fluted shells of Kaelen-Five.\" "
            "[MANY — 4-Voice Choir Simultaneously]: \"Tal-vihara... shanti-vel... Our resonators bring peace to the galaxy.\" "
            "[ONE — Lead Cantor Auren-7]: \"Where the stars are divided by dissonance, let the Great Spire harmonize the void.\" "
            "[MANY — All 5 Voices in Unison]: \"O-ma-ru Vael-Kaelen... Three spectrums as one... Peace to every listening world.\""
        ),
        "phonetic_and_conlang_notes": (
            "Antiphonal One-to-Many Liturgical Chant: Lead Cantor ('One', Argon III-C) intones the Kaelenic call into the golden resonator, "
            "answered simultaneously by four distinct individual voices ('Many': Charon, Leda, Kore, Orus) time-aligned in a 3:5:8 harmonic triad."
        ),
    },
    {
        "station_id": "st-jerome-slag",
        "char_index": 1,
        "slug": "vael_choir",
        "headshot": "assets/characters/char_vael_choir_headshot.jpg",
        "fullbody": "assets/characters/char_vael_choir_fullbody.jpg",
        "voice_id": "KAELEN_POLYPHONIC_CHOIR",
        "style": "simultaneous 5-voice polyphonic monastic choir chanting in staggered canon and choral unison around the golden resonator sphere",
        "dsp_key": "vjb_auren7",
        "script": (
            "[CANON — 5 Individual Voices Entering in Overlapping Layers]: \"Vael-kora... tal-vihara... shanti-vel... From the fluted shells of Kaelen-Five, our resonators awaken...\" "
            "[TUTTI — All 5 Voices Chanting Simultaneously]: \"O-ma-ru Vael-Kaelen... Our resonators bring peace to the galaxy... Dissolving dissonance across the stars... Three, Five, One... Shanti-vel!\""
        ),
        "phonetic_and_conlang_notes": (
            "Simultaneous 5-Voice Polyphony: Five distinct individual voices (Charon [Bass], Orus [Tenor], Argon III-C [Cantor], Leda [Alto], Kore [Soprano]) "
            "chanting at the same time—first in staggered sacred canon and then in full 5-part choral harmony coupled to the 220/275/330/440/550 Hz resonator chord."
        ),
    },
]


def synth_character_voice(voice_id: str, text: str, style: str, api_key: str) -> bytes:
    """Synthesize 24 kHz 16-bit mono PCM via Gemini TTS (supports both 3.8 interactions & 2.5 prebuilt voices)."""
    import base64
    import urllib.request

    if not voice_id.startswith("voice_"):
        # Try gemini-2.5-flash-preview-tts for distinct named prebuilt voices (Orus, Aoede, Leda, Kore, Charon, Puck, Fenrir)
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"
            prompt_text = f"[{style}] {text}"
            payload = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": voice_id}
                        }
                    },
                },
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            for cand in body.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    inl = part.get("inlineData", {})
                    if inl.get("data"):
                        return base64.b64decode(inl["data"])
        except Exception as exc:
            print(f"  [fallback to 3.8 interactions for {voice_id}: {exc}]")

    try:
        return speak.synth_pcm_bytes(
            voice_id=voice_id,
            text=text,
            style=style,
            model="gemini-3.8-flash-tts",
            api_key=api_key,
        )
    except Exception:
        return speak.synth_pcm_bytes(
            voice_id="voice_xdhacg1pn1cq",
            text=text,
            style=style,
            model="gemini-3.8-flash-tts",
            api_key=api_key,
        )


# ==============================================================================
# KAELEN-V MULTI-VOICE CHANTING & CALL-AND-RESPONSE ENGINE
# ==============================================================================

STEMS_DIR = VOICES_DIR / "stems"


def trim_silence(arr: np.ndarray, thresh: float = 0.015) -> np.ndarray:
    """Trim leading and trailing silence so multiple individual voices align on syllable onset."""
    if len(arr) == 0:
        return arr
    env = np.convolve(np.abs(arr), np.ones(240) / 240.0, mode="same")
    idx = np.where(env > thresh)[0]
    if len(idx) == 0:
        return arr
    pad = int(0.03 * SAMPLE_RATE)
    i0 = max(0, int(idx[0]) - pad)
    i1 = min(len(arr), int(idx[-1]) + pad)
    return arr[i0:i1]


def resample_to_length(arr: np.ndarray, target_len: int) -> np.ndarray:
    """Time-align an individual voice stem to target_len so multiple voices chant syllables in unison."""
    if len(arr) == 0 or target_len <= 0:
        return np.zeros(max(1, target_len), dtype=np.float64)
    if len(arr) == target_len:
        return arr.copy()
    x_old = np.linspace(0.0, 1.0, num=len(arr), endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_len, endpoint=True)
    return np.interp(x_new, x_old, arr)


def make_kaelen_gong(fund_hz: float = 110.0, duration: float = 3.2, amp: float = 0.36) -> np.ndarray:
    """Synthesize a deep, resonant Kaelen-V Bronze & Opalescent-Crystal Sanctuary Gong!

    Includes:
    - Padded wooden mallet strike transient (95 Hz -> 42 Hz pitch drop)
    - Deep fundamental + sub-octave body (fund_hz & 0.5 * fund_hz)
    - Classic post-strike gong swell/bloom (t^0.40 * exp(-t/tau)) across Golden Ratio
      inharmonic bronze modes (1.00x, 1.342x, 1.618x, 2.144x, 2.761x, 3.412x) with FM shimmer.
    """
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    # 1. Padded mallet strike thump (first 90ms)
    f_mallet = 42.0 + 65.0 * np.exp(-t / 0.022)
    mallet = np.sin(2.0 * math.pi * np.cumsum(f_mallet) / SAMPLE_RATE) * np.exp(-t / 0.055) * 0.55

    # 2. Deep fundamental & sub-octave resonance
    sub_env = (1.0 - np.exp(-t / 0.015)) * np.exp(-t / (duration * 0.55))
    body = (
        0.58 * np.sin(2.0 * math.pi * fund_hz * t)
        + 0.34 * np.sin(2.0 * math.pi * (0.5 * fund_hz) * t)
        + 0.22 * np.sin(2.0 * math.pi * (1.5 * fund_hz) * t)
    ) * sub_env

    # 3. Blooming inharmonic bronze & crystal gong modes ("bwooom-shimmer" swell after strike)
    swell_env = ((t + 0.015) ** 0.42) * np.exp(-t / (duration * 0.36))
    swell_env = swell_env / (np.max(swell_env) + 1e-8)
    modes = [
        (1.342, 0.32, 2.1),
        (1.61803, 0.28, 3.4),  # Golden Ratio mode
        (2.144, 0.20, 4.7),
        (2.761, 0.14, 6.2),
        (3.412, 0.09, 7.8),
    ]
    shimmer = np.zeros(n, dtype=np.float64)
    for ratio, weight, beat_hz in modes:
        fm = 0.45 * np.sin(2.0 * math.pi * (fund_hz * 0.71) * t) * np.exp(-t / 0.85)
        wobble = 1.0 + 0.003 * np.sin(2.0 * math.pi * beat_hz * t)
        ph = 2.0 * math.pi * np.cumsum(fund_hz * ratio * wobble) / SAMPLE_RATE + fm
        shimmer += weight * np.sin(ph)

    gong = mallet + body + shimmer * swell_env * 0.75
    gong = gong / (np.max(np.abs(gong)) + 1e-8) * amp
    return gong


def overlay_at(base: np.ndarray, overlay: np.ndarray, start_sec: float, gain: float = 1.0) -> np.ndarray:
    """Mix `overlay * gain` into `base` starting at `start_sec` (extending `base` if needed)."""
    i0 = max(0, int(start_sec * SAMPLE_RATE))
    end_idx = i0 + len(overlay)
    if end_idx > len(base):
        padded = np.zeros(end_idx, dtype=np.float64)
        padded[:len(base)] = base
        base = padded
    base[i0:end_idx] += overlay * gain
    return base


def extract_little_trill_and_flourish() -> tuple[np.ndarray, np.ndarray]:
    """Extract the funny high-pitched alien reed/flute flourish and the beloved little trill at the end
    from the cached Kore/Leda stems so we can sprinkle them in occasionally and at the finale!"""
    kore_canon_p = STEMS_DIR / "vjb_canon_kore.wav"
    kore_tutti_p = STEMS_DIR / "vjb_tutti_kore.wav"

    # 1. Occasional mid-piece mystical reed flourish (1.35s soft fade-in/out)
    if kore_canon_p.exists():
        raw_c = load_wav_float(kore_canon_p)
        # Grab a lively 1.35s snippet around t=2.2..3.55s and shape with a smooth bell window
        i0 = min(int(2.2 * SAMPLE_RATE), max(0, len(raw_c) - int(1.5 * SAMPLE_RATE)))
        seg = raw_c[i0:i0 + int(1.35 * SAMPLE_RATE)].copy()
        win = np.sin(math.pi * np.linspace(0.0, 1.0, len(seg))) ** 1.4
        flourish = (seg / (np.max(np.abs(seg)) + 1e-8)) * win * 0.22
    else:
        flourish = np.zeros(int(1.2 * SAMPLE_RATE), dtype=np.float64)

    # 2. The signature "little trill at the end"!
    # When the 108s Kore stem was compressed 6.3x in the original run, the last ~15 seconds of `vjb_canon_kore.wav`
    # and the tail of `vjb_tutti_kore.wav` became that delightful, funny little warbling trill at the end!
    if kore_canon_p.exists():
        raw_c = load_wav_float(kore_canon_p)
        tail_raw = raw_c[int(len(raw_c) * 0.84):]
        # Compress by ~6.2x just like the original run so it produces the exact same funny little trill!
        trill_len = int(1.85 * SAMPLE_RATE)
        trill_c = resample_to_length(tail_raw, trill_len)
        if kore_tutti_p.exists():
            raw_t = load_wav_float(kore_tutti_p)
            tail_t = raw_t[int(len(raw_t) * 0.62):int(len(raw_t) * 0.96)]
            trill_t = resample_to_length(tail_t, trill_len)
            trill = 0.55 * trill_c + 0.45 * trill_t
        else:
            trill = trill_c
        win_t = np.sin(math.pi * np.linspace(0.0, 1.0, len(trill))) ** 0.75
        trill = (trill / (np.max(np.abs(trill)) + 1e-8)) * win_t * 0.34
    else:
        trill = np.zeros(int(1.5 * SAMPLE_RATE), dtype=np.float64)

    return flourish, trill


def get_or_synth_stem(stem_id: str, voice_id: str, text: str, style: str, api_key: str | None) -> np.ndarray:
    """Fetch cached individual voice stem WAV or synthesize via Gemini TTS.
    Cleans any runaway >25s TTS instrument tails so the main choir voices stay warm and natural."""
    STEMS_DIR.mkdir(parents=True, exist_ok=True)
    stem_path = STEMS_DIR / f"{stem_id}.wav"
    if stem_path.exists():
        arr = load_wav_float(stem_path)
    else:
        if not api_key:
            raise RuntimeError(f"API key required to synthesize missing choir stem: {stem_id}")
        print(f"  [choir-stem] Synthesizing {stem_id} ({voice_id})...")
        pcm = synth_character_voice(voice_id=voice_id, text=text, style=style, api_key=api_key)
        arr = bytes_to_float(pcm)
        save_wav(stem_path, arr)

    trimmed = trim_silence(arr)

    # If a TTS stem hallucinated a 90s-290s high-pitched instrument drone after the speech:
    # 1) Cap to the actual spoken/chanted window (~15s for resp2, ~18s for canon, ~23s for tutti)
    # 2) Gently low-pass if it contains a loud >900 Hz continuous tone so the voices dominate cleanly
    max_vocal_sec = 23.0 if "tutti" in stem_id else (18.0 if "canon" in stem_id else 15.0)
    if len(trimmed) > int(max_vocal_sec * SAMPLE_RATE):
        trimmed = trimmed[:int(max_vocal_sec * SAMPLE_RATE)]
        # Fade out last 0.25s smoothly
        fade_n = int(0.25 * SAMPLE_RATE)
        trimmed[-fade_n:] *= np.linspace(1.0, 0.0, fade_n)

    if stem_id in ("vjb_canon_kore", "vjb_tutti_leda", "vjb_tutti_kore"):
        # Smooth out harsh >950 Hz continuous whistle while keeping warm vocal formants
        trimmed = np.convolve(trimmed, np.ones(15) / 15.0, mode="same")

    peak = np.max(np.abs(trimmed)) + 1e-8
    return trimmed / peak * 0.82


def layer_simultaneous_choir(
    stems: list[tuple[np.ndarray, float, float, float]],
    chord_freqs: list[float],
    resonator_level: float = 0.09,
) -> np.ndarray:
    """Combine multiple distinct individual voice stems into a simultaneous multi-voice choir!

    Each item in `stems` is `(stem_array, pitch_ratio, onset_offset_sec, gain)`.
    All stems are time-warped to a unified choral phrase length so their words lock together,
    shifted slightly in pitch/register (`pitch_ratio`) and human micro-timing (`onset_offset_sec`),
    and coupled to a warm, low-register vocal-envelope-driven harmonic resonator chord (`chord_freqs`).
    """
    base_lengths = [len(s[0]) for s in stems if len(s[0]) > 0]
    if not base_lengths:
        return np.zeros(SAMPLE_RATE, dtype=np.float64)
    target_phrase_len = int(np.median(base_lengths))
    max_offset = int(max(s[2] for s in stems) * SAMPLE_RATE)
    total_len = target_phrase_len + max_offset + int(0.35 * SAMPLE_RATE)

    choir_mix = np.zeros(total_len, dtype=np.float64)
    for stem_arr, pitch_ratio, offset_sec, gain in stems:
        aligned = resample_to_length(stem_arr, target_phrase_len)
        t_local = np.arange(target_phrase_len, dtype=np.float64) / SAMPLE_RATE
        delay_mod = (1.0 - pitch_ratio) * 0.012 * np.sin(2.0 * math.pi * 1.8 * t_local)
        idx_f = np.clip(np.arange(target_phrase_len, dtype=np.float64) + delay_mod * SAMPLE_RATE, 0, target_phrase_len - 1)
        voiced = np.interp(idx_f, np.arange(target_phrase_len, dtype=np.float64), aligned)

        i0 = int(offset_sec * SAMPLE_RATE)
        choir_mix[i0:i0 + target_phrase_len] += voiced * gain

    choir_mix = choir_mix / (np.max(np.abs(choir_mix)) + 1e-8) * 0.82

    # Warm, low-register Kaelenic Resonator Sphere chord (purely envelope-following, never piercing)
    t = np.arange(total_len, dtype=np.float64) / SAMPLE_RATE
    win = int(0.055 * SAMPLE_RATE)
    vocal_env = np.convolve(np.abs(choir_mix), np.ones(win) / win, mode="same")
    vocal_env = vocal_env / (np.max(vocal_env) + 1e-8)

    chord_wave = np.zeros(total_len, dtype=np.float64)
    for k, f0 in enumerate(chord_freqs):
        shimmer = 1.0 + 0.002 * math.sin(k + 1.0) * np.sin(2.0 * math.pi * (0.5 + 0.12 * k) * t)
        ph = 2.0 * math.pi * np.cumsum(f0 * shimmer) / SAMPLE_RATE
        chord_wave += np.sin(ph) / max(1, len(chord_freqs))

    resonator_bed = chord_wave * (0.10 + 0.90 * vocal_env) * resonator_level
    combined = choir_mix + resonator_bed
    # Smooth cathedral reflections inside the fluted alabaster shell
    out = combined.copy() * 0.82
    for d_sec, g_rev in [(0.038, 0.24), (0.089, 0.16), (0.155, 0.10)]:
        id_samp = int(d_sec * SAMPLE_RATE)
        if id_samp < total_len:
            out[id_samp:] += combined[:-id_samp] * g_rev

    return out / (np.max(np.abs(out)) + 1e-8) * 0.86


def synth_kaelen_call_and_response(api_key: str | None) -> np.ndarray:
    """Build `voice_cantor_auren7_dry.wav`: One-to-Many Call & Response Chanting with Sanctuary Gongs,
    an occasional high-pitched alien reed flourish, and the beloved little trill at the end!"""
    chant_style_lead = (
        "chanting in a serene, resonant, rhythmic monastic call with sacred stillness and elongated vowels, "
        "like a high cantor intoning a prayer into a glowing crystal resonator"
    )
    chant_style_choir = (
        "chanting in a slow, solemn, unified monastic choir cadence with elongated vowels and steady rhythm, "
        "intoning a sacred benediction of peace across the galaxy"
    )

    call1_text = "Vael-kora... auren-shi... Tune the fluted shells of Kaelen-Five."
    resp1_text = "Tal-vihara... shanti-vel... Our resonators bring peace to the galaxy."
    call2_text = "Where the stars are divided by dissonance, let the Great Spire harmonize the void."
    resp2_text = "O-ma-ru Vael-Kaelen... Three spectrums as one... Peace to every listening world."

    lead_call1 = get_or_synth_stem("vjb_call1_lead", "voice_xdhacg1pn1cq", call1_text, chant_style_lead, api_key)
    lead_call2 = get_or_synth_stem("vjb_call2_lead", "voice_xdhacg1pn1cq", call2_text, chant_style_lead, api_key)

    r1_charon = get_or_synth_stem("vjb_resp1_charon", "Charon", resp1_text, chant_style_choir, api_key)
    r1_leda = get_or_synth_stem("vjb_resp1_leda", "Leda", resp1_text, chant_style_choir, api_key)
    r1_kore = get_or_synth_stem("vjb_resp1_kore", "Kore", resp1_text, chant_style_choir, api_key)
    r1_orus = get_or_synth_stem("vjb_resp1_orus", "Orus", resp1_text, chant_style_choir, api_key)

    choir_resp1 = layer_simultaneous_choir(
        stems=[
            (r1_charon, 0.965, 0.000, 0.95),
            (r1_orus,   0.988, 0.022, 0.92),
            (r1_leda,   1.008, 0.041, 0.95),
            (r1_kore,   1.032, 0.058, 0.88),
        ],
        chord_freqs=[110.0, 165.0, 220.0, 275.0],
        resonator_level=0.08,
    )

    r2_lead = get_or_synth_stem("vjb_resp2_lead", "voice_xdhacg1pn1cq", resp2_text, chant_style_choir, api_key)
    r2_charon = get_or_synth_stem("vjb_resp2_charon", "Charon", resp2_text, chant_style_choir, api_key)
    r2_leda = get_or_synth_stem("vjb_resp2_leda", "Leda", resp2_text, chant_style_choir, api_key)
    r2_kore = get_or_synth_stem("vjb_resp2_kore", "Kore", resp2_text, chant_style_choir, api_key)
    r2_aoede = get_or_synth_stem("vjb_resp2_aoede", "Aoede", resp2_text, chant_style_choir, api_key)

    choir_resp2 = layer_simultaneous_choir(
        stems=[
            (r2_lead,   1.000, 0.000, 1.00),
            (r2_charon, 0.960, 0.018, 0.94),
            (r2_leda,   1.010, 0.035, 0.92),
            (r2_aoede,  0.985, 0.052, 0.88),
            (r2_kore,   1.038, 0.068, 0.86),
        ],
        chord_freqs=[110.0, 165.0, 220.0, 275.0, 330.0],
        resonator_level=0.09,
    )

    lead_call1_spaced = layer_simultaneous_choir([(lead_call1, 1.0, 0.0, 1.0)], [110.0, 220.0], resonator_level=0.05)
    lead_call2_spaced = layer_simultaneous_choir([(lead_call2, 1.0, 0.0, 1.0)], [110.0, 183.3], resonator_level=0.05)

    # Extract occasional high-pitch flourish and the beloved little trill at the end!
    flourish, end_trill = extract_little_trill_and_flourish()

    # Deep Kaelen-V Sanctuary Gongs!
    gong_open = make_kaelen_gong(fund_hz=110.0, duration=3.0, amp=0.38)
    gong_resp1 = make_kaelen_gong(fund_hz=146.8, duration=2.8, amp=0.32)
    gong_mid = make_kaelen_gong(fund_hz=98.0, duration=3.2, amp=0.38)
    gong_resp2 = make_kaelen_gong(fund_hz=130.8, duration=2.8, amp=0.32)
    gong_finale = (
        make_kaelen_gong(fund_hz=82.5, duration=3.8, amp=0.36)
        + make_kaelen_gong(fund_hz=165.0, duration=3.8, amp=0.22)
    )

    # Sprinkle the occasional high-pitched flourish right at the end of Choir Response 1,
    # and place the beloved little trill right at the end of Choir Response 2 as the Finale Gong rings!
    choir_resp1 = overlay_at(choir_resp1, gong_resp1, 0.0, gain=0.85)
    choir_resp1 = overlay_at(choir_resp1, flourish, max(0.5, len(choir_resp1) / SAMPLE_RATE - 1.5), gain=0.75)

    choir_resp2 = overlay_at(choir_resp2, gong_resp2, 0.0, gain=0.85)
    trill_start = max(0.5, len(choir_resp2) / SAMPLE_RATE - 0.9)
    choir_resp2 = overlay_at(choir_resp2, end_trill, trill_start, gain=0.95)
    choir_resp2 = overlay_at(choir_resp2, gong_finale, trill_start + 0.35, gain=0.95)

    lead_call1_with_gong = overlay_at(lead_call1_spaced, gong_open, 0.0, gain=0.92)
    lead_call2_with_gong = overlay_at(lead_call2_spaced, gong_mid, 0.0, gain=0.92)

    gap = np.zeros(int(0.30 * SAMPLE_RATE), dtype=np.float64)
    full_seq = np.concatenate([
        lead_call1_with_gong,
        gap,
        choir_resp1,
        gap,
        lead_call2_with_gong,
        gap,
        choir_resp2,
    ])
    return full_seq / (np.max(np.abs(full_seq)) + 1e-8) * 0.86


def synth_kaelen_polyphonic_choir(api_key: str | None) -> np.ndarray:
    """Build `voice_vael_choir_dry.wav`: Simultaneous 5-Voice Polyphonic Choir Chanting
    with deep Sanctuary Gongs, an occasional high-pitched reed flourish, and the little trill at the end!"""
    canon_style = (
        "chanting in a hypnotic, flowing, sacred polyphonic canon with rich sustained vowels and serene devotion"
    )
    canon_text = "Vael-kora... tal-vihara... shanti-vel... From the fluted shells of Kaelen-Five, our resonators awaken."

    tutti_text = (
        "O-ma-ru Vael-Kaelen... Our resonators bring peace to the galaxy... "
        "Dissolving dissonance across the stars... Three, Five, One... Shanti-vel!"
    )

    c_charon = get_or_synth_stem("vjb_canon_charon", "Charon", canon_text, canon_style, api_key)
    c_orus = get_or_synth_stem("vjb_canon_orus", "Orus", canon_text, canon_style, api_key)
    c_leda = get_or_synth_stem("vjb_canon_leda", "Leda", canon_text, canon_style, api_key)
    c_kore = get_or_synth_stem("vjb_canon_kore", "Kore", canon_text, canon_style, api_key)
    c_lead = get_or_synth_stem("vjb_canon_lead", "voice_xdhacg1pn1cq", canon_text, canon_style, api_key)

    # Part 1: Staggered Canon (voices enter at 0.0s, 0.55s, 1.10s, 1.65s, 2.20s and chant simultaneously!)
    part1_canon = layer_simultaneous_choir(
        stems=[
            (c_charon, 0.960, 0.00, 0.95),
            (c_leda,   1.012, 0.55, 0.92),
            (c_orus,   0.985, 1.10, 0.92),
            (c_kore,   1.032, 1.65, 0.65),
            (c_lead,   1.000, 2.20, 0.98),
        ],
        chord_freqs=[110.0, 165.0, 220.0, 275.0],
        resonator_level=0.08,
    )

    t_lead = get_or_synth_stem("vjb_tutti_lead", "voice_xdhacg1pn1cq", tutti_text, canon_style, api_key)
    t_charon = get_or_synth_stem("vjb_tutti_charon", "Charon", tutti_text, canon_style, api_key)
    t_leda = get_or_synth_stem("vjb_tutti_leda", "Leda", tutti_text, canon_style, api_key)
    t_kore = get_or_synth_stem("vjb_tutti_kore", "Kore", tutti_text, canon_style, api_key)
    t_aoede = get_or_synth_stem("vjb_tutti_aoede", "Aoede", tutti_text, canon_style, api_key)

    # Part 2: All 5 individual voices locked together chanting simultaneously!
    part2_tutti = layer_simultaneous_choir(
        stems=[
            (t_lead,   1.000, 0.000, 1.00),
            (t_charon, 0.958, 0.019, 0.95),
            (t_leda,   1.014, 0.037, 0.85),
            (t_aoede,  0.984, 0.054, 0.92),
            (t_kore,   1.038, 0.071, 0.78),
        ],
        chord_freqs=[110.0, 165.0, 220.0, 275.0, 330.0],
        resonator_level=0.09,
    )

    flourish, end_trill = extract_little_trill_and_flourish()

    gong_open = make_kaelen_gong(fund_hz=98.0, duration=3.4, amp=0.40)
    gong_canon_accent = make_kaelen_gong(fund_hz=146.8, duration=2.6, amp=0.28)
    gong_mid = make_kaelen_gong(fund_hz=110.0, duration=3.4, amp=0.40)
    gong_finale = (
        make_kaelen_gong(fund_hz=82.5, duration=4.0, amp=0.38)
        + make_kaelen_gong(fund_hz=123.75, duration=4.0, amp=0.24)
    )

    # Add opening gong + occasional mid-canon gong & brief high-pitch flourish
    part1_canon = overlay_at(part1_canon, gong_open, 0.0, gain=0.95)
    part1_canon = overlay_at(part1_canon, gong_canon_accent, 2.20, gain=0.80)
    part1_canon = overlay_at(part1_canon, flourish, max(1.0, len(part1_canon) / SAMPLE_RATE - 1.6), gain=0.80)

    # Add mid-section gong + signature little trill at the end + double finale gong!
    part2_tutti = overlay_at(part2_tutti, gong_mid, 0.0, gain=0.95)
    t_end = max(1.0, len(part2_tutti) / SAMPLE_RATE - 0.95)
    part2_tutti = overlay_at(part2_tutti, end_trill, t_end, gain=1.0)
    part2_tutti = overlay_at(part2_tutti, gong_finale, t_end + 0.30, gain=0.95)

    gap = np.zeros(int(0.28 * SAMPLE_RATE), dtype=np.float64)
    full_choir = np.concatenate([part1_canon, gap, part2_tutti])
    return full_choir / (np.max(np.abs(full_choir)) + 1e-8) * 0.86


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    sync_character_images()
    VOICES_DIR.mkdir(parents=True, exist_ok=True)

    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    presets_by_id = {p["id"]: p for p in data["presets"]}

    for spec in CHARACTER_VOICE_SPECS:
        slug = spec["slug"]
        dry_path = VOICES_DIR / f"voice_{slug}_dry.wav"
        rf_path = VOICES_DIR / f"voice_{slug}_rf.wav"

        if spec["voice_id"] == "BIO_SYNTH":
            print(f"[bio-synth] Generating Silt-Strider vocalization -> {dry_path.name}")
            dry_arr, rf_arr = synth_silt_strider_bio_audio()
            save_wav(dry_path, dry_arr)
            save_wav(rf_path, rf_arr)
        elif spec["voice_id"] == "KAELEN_CALL_RESPONSE":
            print(f"[choir-antiphony] Building One-to-Many Call & Response -> {dry_path.name}")
            dry_arr = synth_kaelen_call_and_response(api_key)
            save_wav(dry_path, dry_arr)
            rf_arr = apply_station_rf_dsp(dry_arr, spec["dsp_key"])
            save_wav(rf_path, rf_arr)
            print(f"[rf-dsp]    Generated {rf_path.name} ({len(rf_arr)/SAMPLE_RATE:.1f}s)")
        elif spec["voice_id"] == "KAELEN_POLYPHONIC_CHOIR":
            print(f"[choir-polyphony] Building 5-Voice Simultaneous Choir -> {dry_path.name}")
            dry_arr = synth_kaelen_polyphonic_choir(api_key)
            save_wav(dry_path, dry_arr)
            rf_arr = apply_station_rf_dsp(dry_arr, spec["dsp_key"])
            save_wav(rf_path, rf_arr)
            print(f"[rf-dsp]    Generated {rf_path.name} ({len(rf_arr)/SAMPLE_RATE:.1f}s)")
        else:
            if not dry_path.exists():
                if not api_key:
                    raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY required for TTS synthesis")
                print(f"[tts-synth] {slug} via {spec['voice_id']}...")
                pcm_bytes = synth_character_voice(
                    voice_id=spec["voice_id"],
                    text=spec["script"],
                    style=spec["style"],
                    api_key=api_key,
                )
                dry_arr = bytes_to_float(pcm_bytes)
                save_wav(dry_path, dry_arr)
            else:
                print(f"[cached]    {dry_path.name}")
                dry_arr = load_wav_float(dry_path)

            rf_arr = apply_station_rf_dsp(dry_arr, spec["dsp_key"])
            save_wav(rf_path, rf_arr)
            print(f"[rf-dsp]    Generated {rf_path.name} ({len(rf_arr)/SAMPLE_RATE:.1f}s)")

        # Attach visual and audio sample paths to the character entry in stations.json
        p = presets_by_id.get(spec["station_id"])
        if p and "characters" in p and spec["char_index"] < len(p["characters"]):
            c = p["characters"][spec["char_index"]]
            c["slug"] = slug
            c["headshot_src"] = spec["headshot"]
            c["fullbody_src"] = spec["fullbody"]
            c["voice_sample_dry_src"] = f"assets/audio/voices/voice_{slug}_dry.wav"
            c["voice_sample_rf_src"] = f"assets/audio/voices/voice_{slug}_rf.wav"
            c["language_sample_transcript"] = spec["script"]
            c["phonetic_and_conlang_notes"] = spec["phonetic_and_conlang_notes"]

        # Copy character assets into stations/<station_folder>/characters/
        if p and p.get("station_folder"):
            s_char_dir = STATIONS_ROOT / p["station_folder"] / "characters"
            s_char_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dry_path, s_char_dir / dry_path.name)
            shutil.copy2(rf_path, s_char_dir / rf_path.name)
            for img_rel in (spec["headshot"], spec["fullbody"]):
                img_p = DOCS / img_rel
                if img_p.exists():
                    shutil.copy2(img_p, s_char_dir / img_p.name)

    DATA_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    js_payload = "window.GOR9_STATIONS_DATA = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n"
    DATA_JS.write_text(js_payload, encoding="utf-8")
    print(f"Updated {DATA_JSON.relative_to(ROOT)} and {DATA_JS.relative_to(ROOT)} with character visuals & voice samples!")


if __name__ == "__main__":
    main()
