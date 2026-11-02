#!/usr/bin/env python3
"""Synthesize and assemble the complete GOR-9 Episode 01 Master Audio Track (24kHz PCM).

Features:
1. Reuses or synthesizes each narrative segment in uninterrupted Argon III-C
   (voice_xdhacg1pn1cq) calls at 24,000 Hz so the voice matches the Euclid productions.
2. Implements Phi's Cold Open direction:
   - Softer crackly white-noise static starts at t=0.0s while the camera crackles in.
   - At t=0.45s, "This is G-O-R 9. This is G-O-R 9." begins UNDER the static.
   - As the second "This is G-O-R 9" finishes, the static and visual snow clear right
     into the crystal-clear [ding-ding] chime (indicating Signal Lock).
   - "Galactic Outpost Radio, broadcasting from the High Basalt Shelf..." continues
     on a crystal-clear locked carrier.
3. Synthesizes the two shortwave DX audio vignettes in Segment 3 (Buoy N-24 on 3,890 kHz
   and Radio Corrugated on 11,410 kHz) and records exact segment/sub-step timestamps
   to renders/ep01_timeline.json for the 2560x1440 full-episode video renderer and
   interactive HTML studio console.
"""

from pathlib import Path
import json
import math
import os
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


def make_ding_ding_pcm() -> bytes:
    """Two-note harmonic crystal interval signal (Signal Lock indicator) at 24kHz PCM."""
    note1 = speak.make_harmonic_bell_pcm([528.0, 792.0], duration=0.32, amp=0.15)
    gap = speak.silence_pcm(0.06)
    note2 = speak.make_harmonic_bell_pcm([440.0, 880.0], duration=0.52, amp=0.16)
    return note1 + gap + note2


def make_softer_crackle_overlay(duration: float, seed: int = 35109) -> tuple[np.ndarray, list[float]]:
    """Generate softer crackly white-noise overlay that clears smoothly right at the end (the ding)."""
    rng = np.random.default_rng(seed)
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    # Crisp high-shelf white noise
    raw = rng.normal(0.0, 1.0, size=n + 1)
    white = raw[1:] - 0.58 * raw[:-1]
    white /= (np.std(white) + 1e-8)

    # Envelope: starts noticeable during initial 0.45s before voice, drops slightly so voice
    # cuts clearly through the static during "This is G-O-R 9. This is G-O-R 9.", with a couple
    # of brief tuning sputters, then clears to 0.0 right as we reach the [ding-ding] lock chime!
    env = np.zeros(n, dtype=np.float64)
    for i, ti in enumerate(t):
        progress = ti / duration
        if ti < 0.42:
            # Before voice starts: initial carrier acquisition static
            e = 0.85 - 0.20 * (ti / 0.42)
        elif progress < 0.48:
            # First "This is G-O-R 9." under static
            e = 0.48 + 0.14 * math.sin(ti * 19.0)
        elif progress < 0.62:
            # Brief carrier surge between the two "This is G-O-R 9" calls
            e = 0.65
        elif progress < 0.86:
            # Second "This is G-O-R 9." — static steadily clearing as tuner locks in
            rem = (0.86 - progress) / (0.86 - 0.62)
            e = 0.42 * (rem ** 1.2)
        else:
            # Final 14% before [ding-ding]: rapid snap to crystal-clear lock
            rem = max(0.0, (1.0 - progress) / 0.14)
            e = 0.16 * (rem ** 2.0)
        env[i] = max(0.0, min(1.0, e))

    # Add fine Poisson crackle ticks & micro-snaps scaled down so it's never too loud
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

    # Overall amplitude is gentle (~0.11 white noise + ~0.18 crackle peaks) so voice is front-and-center
    static_sig = (white * 0.105 + crackle * 0.22) * env

    # Also compute 30fps visual static envelope for this exact duration (from t=0 to ding_start)
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


def make_vignette_buoy_n24(duration: float = 2.6) -> bytes:
    """3,890 kHz Titan-Minor Hydrographic Buoy N-24: CW ID + metallic buoy clank + detuning whip rub."""
    rng = np.random.default_rng(3890)
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    # Band-limited shortwave background hiss
    noise = np.convolve(rng.normal(0.0, 0.035, size=n), np.ones(9) / 9.0, mode="same")

    # Metallic buoy bell clank at t=0.15s and t=1.45s
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

    # FSK / CW telemetry tones that bend downward when silt-strider rubs the guy-wire (t=1.1s..2.2s)
    tone = np.zeros(n, dtype=np.float64)
    beeps = [
        (0.35, 0.14, 880.0),
        (0.54, 0.08, 880.0),
        (0.66, 0.18, 1040.0),
        (0.92, 0.12, 880.0),
        (1.12, 0.55, 960.0),  # Guy-wire rub detunes this carrier!
        (1.78, 0.14, 780.0),
        (1.98, 0.22, 880.0),
    ]
    for t0, dur_b, freq in beeps:
        i0 = int(t0 * SAMPLE_RATE)
        d = min(int(dur_b * SAMPLE_RATE), n - i0)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        # If this is the guy-wire rub note, bend frequency downward & add metallic scrape
        if abs(t0 - 1.12) < 0.05:
            f_inst = freq - 165.0 * np.sin(math.pi * tt / dur_b)
            ph = 2.0 * math.pi * np.cumsum(f_inst) / SAMPLE_RATE
        else:
            ph = 2.0 * math.pi * freq * tt
        env_b = np.sin(math.pi * tt / dur_b) ** 0.25
        tone[i0:i0 + d] += np.sin(ph) * env_b * 0.13

    sig = noise + clank + tone
    return float_to_bytes(np.clip(sig, -0.85, 0.85))


def make_vignette_radio_corrugated(duration: float = 2.6) -> bytes:
    """11,410 kHz Callisto Dome-4 'Radio Corrugated': warbling night-market lute + blowtorch spike."""
    rng = np.random.default_rng(11410)
    n = int(SAMPLE_RATE * duration)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE

    # AM ionospheric fading envelope
    fading = 0.65 + 0.35 * np.sin(2.0 * math.pi * 1.4 * t)
    noise = np.convolve(rng.normal(0.0, 0.03, size=n), np.ones(7) / 7.0, mode="same")

    # Pentatonic plucked synth-lute notes (Callisto Dome-4 night market broadcast)
    notes = [
        (0.08, 0.26, 392.0),   # G4
        (0.32, 0.24, 440.0),   # A4
        (0.54, 0.30, 523.25),  # C5
        (0.82, 0.22, 587.33),  # D5
        (1.04, 0.28, 523.25),  # C5
        (1.30, 0.25, 440.0),   # A4
        (1.55, 0.35, 392.0),   # G4
    ]
    lute = np.zeros(n, dtype=np.float64)
    for t0, dur_n, f0 in notes:
        i0 = int(t0 * SAMPLE_RATE)
        d = min(int(dur_n * SAMPLE_RATE), n - i0)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        # Slight shortwave SSB mistuning vibrato
        vib = 1.0 + 0.008 * np.sin(2.0 * math.pi * 6.5 * tt)
        wave_n = (
            0.65 * np.sin(2.0 * math.pi * f0 * vib * tt)
            + 0.25 * np.sin(2.0 * math.pi * (2.0 * f0) * vib * tt)
            + 0.10 * np.sin(2.0 * math.pi * (3.0 * f0) * vib * tt)
        ) * np.exp(-tt / 0.11)
        lute[i0:i0 + d] += wave_n * 0.18

    # At t=1.82s: engineer hits the dipole with a blowtorch! (frying plasma arc + carrier whistle spike)
    torch = np.zeros(n, dtype=np.float64)
    t_idx = int(1.82 * SAMPLE_RATE)
    t_dur = min(int(0.68 * SAMPLE_RATE), n - t_idx)
    tt = np.arange(t_dur, dtype=np.float64) / SAMPLE_RATE
    env_t = np.sin(math.pi * tt / (t_dur / SAMPLE_RATE)) ** 0.5
    sizzle = rng.normal(0.0, 0.16, size=t_dur) * env_t
    whistle = np.sin(2.0 * math.pi * (1200.0 + 900.0 * tt) * tt) * 0.11 * env_t
    torch[t_idx:t_idx + t_dur] = sizzle + whistle

    sig = noise + lute * fading + torch
    return float_to_bytes(np.clip(sig, -0.85, 0.85))


def synth_or_load_segment(seg_id: str, text: str, profile: dict, api_key: str | None) -> bytes:
    """Load cached 24kHz PCM WAV from renders/segments/{seg_id}.wav or synthesize via Argon III-C."""
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


def build_cold_open_from_pure_voice(pure_voice_bytes: bytes) -> tuple[bytes, dict]:
    """Build the new Cold Open where 'This is G-O-R 9. This is G-O-R 9.' starts UNDER softer static,
    and the static clears right at the [ding-ding] chime (indicating signal lock).
    """
    # Let's inspect the structure of renders/cam00_voice_pure_24k.wav created earlier:
    #   0.00s - 0.45s: intro_bell
    #   0.45s - 0.57s: 0.12s silence
    #   0.57s - 3.85s: part_a ("This is G-O-R 9. This is G-O-R 9.") [split_sec = 3.28s]
    #   3.85s - 3.95s: 0.10s silence
    #   3.95s - 4.85s: ding_ding (0.90s)
    #   4.85s - 4.97s: 0.12s silence
    #   4.97s - end  : part_b ("Galactic Outpost Radio...") + outro_bell + 0.60s silence
    # Wait: let's remove the trailing outro_bell from pure_voice_bytes so Segment 1 can have its own clean transition!
    # In synth_cold_open.py, the end of pure_voice_bytes had:
    #   + speak.silence_pcm(0.25) + outro_bell (0.55s) + speak.silence_pcm(0.60) = 1.40s at the tail.
    # Let's trim the last 1.15s (removing outro_bell + extra tail) so Cold Open ends cleanly after "Zero-four-hundred Galactic Coordinated."!
    trim_bytes = int(1.15 * SAMPLE_RATE) * 2
    core_voice_bytes = pure_voice_bytes[:-trim_bytes]

    # Prepend a brief 0.35s initial static pad before intro_bell + "This is G-O-R 9",
    # so the voice call starts right at t = 0.35 + 0.57 = 0.92s under the static!
    pre_pad_sec = 0.35
    pre_pad_bytes = speak.silence_pcm(pre_pad_sec)
    full_cold_voice = pre_pad_bytes + core_voice_bytes
    voice_flt = bytes_to_float(full_cold_voice)

    # In core_voice_bytes, [ding-ding] starts at 0.45 + 0.12 + 3.28 + 0.10 = 3.95s.
    # With pre_pad_sec = 0.35s, [ding-ding] starts at t = 4.30s!
    ding_start_sec = pre_pad_sec + 3.95
    ding_end_sec = ding_start_sec + 0.90

    # Generate softer crackly white-noise static from t = 0.00s to t = ding_start_sec (4.30s),
    # clearing right as [ding-ding] rings!
    static_sig, vis_env = make_softer_crackle_overlay(ding_start_sec)
    mixed_flt = voice_flt.copy()
    n_stat = min(len(mixed_flt), len(static_sig))
    mixed_flt[:n_stat] = np.clip(mixed_flt[:n_stat] + static_sig[:n_stat], -0.95, 0.95)

    cold_open_pcm = float_to_bytes(mixed_flt)

    # Update assets/sfx/sfx_catalog.json with the new 4.30s (129 frames @ 30fps) visual crackle envelope
    catalog_path = SFX_DIR / "sfx_catalog.json"
    if catalog_path.exists():
        cat = json.loads(catalog_path.read_text(encoding="utf-8"))
        cat["cam00_boot_visual_envelope_30fps"] = vis_env
        cat["ding_lock_time_sec"] = round(ding_start_sec, 3)
        catalog_path.write_text(json.dumps(cat, indent=2), encoding="utf-8")

    # Also save updated crackle_cam_boot_2p8s.wav with the softer level
    with wave.open(str(SFX_DIR / "crackle_cam_boot_2p8s.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(float_to_bytes(static_sig))

    meta = {
        "voice_start_sec": round(pre_pad_sec + 0.57, 3),
        "ding_lock_sec": round(ding_start_sec, 3),
        "ding_end_sec": round(ding_end_sec, 3),
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

    # 1. Build updated Cold Open (Segment 0) from cached pure 24kHz Argon III-C voice
    pure_voice_wav = RENDERS_DIR / "cam00_voice_pure_24k.wav"
    if not pure_voice_wav.exists():
        raise RuntimeError(f"Expected {pure_voice_wav} to exist from synth_cold_open.py")

    pure_voice_bytes = load_wav_int16(pure_voice_wav)
    seg0_pcm, seg0_meta = build_cold_open_from_pure_voice(pure_voice_bytes)

    # Save updated standalone Cold Open mix (with a brief 0.5s tail pad for standalone playback)
    standalone_cold = seg0_pcm + speak.silence_pcm(0.50)
    save_wav_int16(RENDERS_DIR / "cam00_cold_open_mix.wav", standalone_cold)
    print(
        f"Updated Cold Open mix: {RENDERS_DIR / 'cam00_cold_open_mix.wav'} "
        f"({dur_sec(standalone_cold):.2f}s, voice under static at {seg0_meta['voice_start_sec']}s, "
        f"clears at [ding-ding] signal lock {seg0_meta['ding_lock_sec']}s)"
    )

    # 2. Synthesize (or load cached) Segments 1 - 5 in Argon III-C
    segments_spec = [
        (
            "seg1_weather",
            "Space Weather, with emphasis on Sector 9. "
            "Coreward lanes are calm—solar flux one-seventy-four, K-index two. "
            "Locally, an electrostatic dust squall on the Meridian Plateau has engulfed Relay K-Z-9 Omega. "
            "Sixty-kilovolt triboelectric arcing across the feedhorn is causing minor phase-wobble in the "
            "number-four marzelvane bushing. Expect SINPO two-three-two-two-two.",
        ),
        (
            "seg2_econ",
            "Outpost Economics. "
            "Grade-B Deuterium pellets rose four percent today following a dragline cable slowdown at "
            "Silicate Quarry 44-K. Outpost Nine will step Reactor Two down to twelve kilowatts after midnight; "
            "Dormitory B should plug in auxiliary foot-warmers. "
            "Meanwhile, our monthly supply tender remains impounded at Quarantine Buoy Twelve after customs "
            "misfiled replacement oscillator tubes as fermented brine tubers.",
        ),
        (
            "seg3a_hauser_titan",
            "On the Hauser Correlator: "
            "Titan-Minor, three-eight-ninety kilohertz. Hydrographic Buoy N-24 reciting methane tide tables,",
        ),
        (
            "seg3a_hauser_titan_tail",
            "while migratory silt-striders rub against the guy-wires, detuning the whip antenna.",
        ),
        (
            "seg3b_hauser_callisto",
            "Callisto Dome Four, eleven-four-ten kilohertz. Unlicensed noodle-market broadcaster Radio Corrugated,",
        ),
        (
            "seg3b_hauser_callisto_tail",
            "peaking right as their engineer hit the dipole with a blowtorch.",
        ),
        (
            "seg3c_hauser_m33",
            "And Intergalactic, M-Thirty-Three: a seven-hundred-year-old drift-buoy still issuing small-craft "
            "warnings for an ammonia sea that evaporated in the Ming Dynasty.",
        ),
        (
            "seg4a_euclid_sighting",
            "Finally, a late-night alert on the Euclid Signal Detector, which scans the noise floor for signs "
            "of geometric intelligence. "
            "At zero-three-twelve UTC, inside unmanned Brine Evaporation Vat Nineteen on Callisto-South, "
            "the detector locked onto Frame Seven: an unsuspecting parallelogram in the salt crust.",
        ),
        (
            "seg4b_euclid_construction",
            "Opposite sides parallel to two ten-thousandths of an arcsecond—A-B to C-D, A-C to B-D—and "
            "somebody drew the diameter B-C, bisecting the sludge into two congruent triangles.",
        ),
        (
            "seg4c_euclid_punchline",
            "The Water Board claims a motorized mud-rake lost a cotter pin and dragged sideways. "
            "It's always a broken cotter pin, folks.",
        ),
        (
            "seg5_sched_signoff",
            "On the next broadcast: an unlicensed numbers station in the Trojans reciting dumpling recipes "
            "in base-eight, and a suspected rhombus aboard an ice-hauler. "
            "From Asteroid 3-5-1 in Sector 9, this is G-O-R 9—your eye to the cosmos, ear to the vacuum.",
        ),
        (
            "seg6_outro_credits",
            "Remember, a like indication on your listening apparatus gives us three kilowatts, "
            "and a subscription gets us one step closer to upgrading our marzelvane emitters.",
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
    ding_ding = make_ding_ding_pcm()
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

    # --- SEG 0: COLD OPEN (CAM-00) ---
    seg0_start = cursor_sec
    append_chunk(seg0_pcm)
    append_chunk(speak.silence_pcm(0.35))
    seg0_end = cursor_sec
    timeline_events.append({
        "id": "seg0_cold_open",
        "console": "CAM-00",
        "title": "CAM-00 • HIGH BASALT SHELF TOWER OUTPOST",
        "start_sec": round(seg0_start, 3),
        "end_sec": round(seg0_end, 3),
        "voice_start_sec": seg0_meta["voice_start_sec"],
        "ding_lock_sec": seg0_meta["ding_lock_sec"],
        "subtitle": "This is GOR-9. This is GOR-9 [ding-ding] Galactic Outpost Radio, broadcasting from the High Basalt Shelf on Asteroid 3-5-1 in Sector 9.",
    })

    # --- SEG 1: SPACE WEATHER (CONSOLE 1: METEO-9) ---
    seg1_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_construction)
    append_chunk(speak.silence_pcm(0.15))
    append_chunk(seg_pcm_map["seg1_weather"])
    append_chunk(speak.silence_pcm(0.45))
    seg1_end = cursor_sec
    timeline_events.append({
        "id": "seg1_weather",
        "console": "METEO-9",
        "title": "CONSOLE 1 • METEO-9 • SECTOR 9 MAGNETOSPHERIC RADAR",
        "start_sec": round(seg1_start, 3),
        "end_sec": round(seg1_end, 3),
        "subtitle": "Space Weather, with emphasis on Sector 9. Coreward lanes are calm—solar flux 174, K-index 2. Locally, an electrostatic dust squall on the Meridian Plateau has engulfed Relay KZ9-OMEGA (60 kV arcing, marzelvane #4 phase-wobble, SINPO 2-3-2-2-2).",
    })

    # --- SEG 2: OUTPOST ECONOMICS (CONSOLE 2: ECON-9) ---
    seg2_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_proposition)
    append_chunk(speak.silence_pcm(0.15))
    append_chunk(seg_pcm_map["seg2_econ"])
    append_chunk(speak.silence_pcm(0.45))
    seg2_end = cursor_sec
    timeline_events.append({
        "id": "seg2_econ",
        "console": "ECON-9",
        "title": "CONSOLE 2 • ECON-9 • CERES SPOT EXCHANGE & REACTOR STEP-DOWN",
        "start_sec": round(seg2_start, 3),
        "end_sec": round(seg2_end, 3),
        "subtitle": "Outpost Economics: Grade-B Deuterium pellets +4% following Quarry 44-K dragline slowdown. Reactor #2 stepping down to 12 kW after midnight. Supply tender held at Quarantine Buoy 12 ('fermented brine tubers').",
    })

    # --- SEG 3: DETECTED BROADCASTS (CONSOLE 3: HAUSER MK-IV) ---
    seg3_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_context)
    append_chunk(speak.silence_pcm(0.15))

    # Sub-view 3A: Titan-Minor Buoy N-24 (3,890 kHz)
    sub3a_start = seg3_start
    append_chunk(seg_pcm_map["seg3a_hauser_titan"])
    append_chunk(speak.silence_pcm(0.10))
    vig3a_start = cursor_sec
    append_chunk(vig_n24)
    vig3a_end = cursor_sec
    append_chunk(speak.silence_pcm(0.10))
    append_chunk(seg_pcm_map["seg3a_hauser_titan_tail"])
    append_chunk(speak.silence_pcm(0.35))
    sub3a_end = cursor_sec

    # Sub-view 3B: Callisto Dome Four "Radio Corrugated" (11,410 kHz)
    sub3b_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(seg_pcm_map["seg3b_hauser_callisto"])
    append_chunk(speak.silence_pcm(0.10))
    vig3b_start = cursor_sec
    append_chunk(vig_bazaar)
    vig3b_end = cursor_sec
    append_chunk(speak.silence_pcm(0.10))
    append_chunk(seg_pcm_map["seg3b_hauser_callisto_tail"])
    append_chunk(speak.silence_pcm(0.35))
    sub3b_end = cursor_sec

    # Sub-view 3C: Intergalactic M-33 Drift Buoy (1,420.405 MHz)
    sub3c_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(seg_pcm_map["seg3c_hauser_m33"])
    append_chunk(speak.silence_pcm(0.45))
    sub3c_end = cursor_sec
    seg3_end = cursor_sec

    timeline_events.append({
        "id": "seg3_hauser",
        "console": "HAUSER-MK4",
        "title": "CONSOLE 3 • HAUSER MK-IV CORRELATOR • DX LOGS",
        "start_sec": round(seg3_start, 3),
        "end_sec": round(seg3_end, 3),
        "sub_views": [
            {
                "id": "3a_titan_n24",
                "freq_khz": 3890.0,
                "label": "3,890 kHz CW • TITAN-MINOR BUOY N-24",
                "start_sec": round(sub3a_start, 3),
                "end_sec": round(sub3a_end, 3),
                "vignette_start_sec": round(vig3a_start, 3),
                "vignette_end_sec": round(vig3a_end, 3),
                "subtitle": "On the Hauser Correlator: Titan-Minor, 3,890 kHz. Hydrographic Buoy N-24 reciting methane tide tables, while migratory silt-striders rub against the guy-wires, detuning the whip antenna.",
            },
            {
                "id": "3b_callisto_bazaar",
                "freq_khz": 11410.0,
                "label": "11,410 kHz AM • CALLISTO DOME-4 'RADIO CORRUGATED'",
                "start_sec": round(sub3b_start, 3),
                "end_sec": round(sub3b_end, 3),
                "vignette_start_sec": round(vig3b_start, 3),
                "vignette_end_sec": round(vig3b_end, 3),
                "subtitle": "Callisto Dome Four, 11,410 kHz. Unlicensed noodle-market broadcaster Radio Corrugated, peaking right as their engineer hit the dipole with a blowtorch.",
            },
            {
                "id": "3c_m33_buoy",
                "freq_khz": 1420405.0,
                "label": "1,420.405 MHz • INTERGALACTIC M-33 DRIFT BUOY",
                "start_sec": round(sub3c_start, 3),
                "end_sec": round(sub3c_end, 3),
                "subtitle": "And Intergalactic, M-33: a 700-year-old drift-buoy still issuing small-craft warnings for an ammonia sea that evaporated in the Ming Dynasty.",
            },
        ],
    })

    # --- SEG 4: EUCLID SIGNAL DETECTOR (CONSOLE 4: EUCLID-9) ---
    seg4_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_insight)
    append_chunk(speak.silence_pcm(0.15))
    step4a_start = seg4_start
    append_chunk(seg_pcm_map["seg4a_euclid_sighting"])
    append_chunk(speak.silence_pcm(0.25))
    step4a_end = cursor_sec

    step4b_start = cursor_sec
    append_chunk(bell_construction)
    append_chunk(speak.silence_pcm(0.12))
    append_chunk(seg_pcm_map["seg4b_euclid_construction"])
    append_chunk(speak.silence_pcm(0.25))
    step4b_end = cursor_sec

    step4c_start = cursor_sec
    append_chunk(bell_punchline)
    append_chunk(speak.silence_pcm(0.12))
    append_chunk(seg_pcm_map["seg4c_euclid_punchline"])
    append_chunk(speak.silence_pcm(0.45))
    step4c_end = cursor_sec
    seg4_end = cursor_sec

    timeline_events.append({
        "id": "seg4_euclid",
        "console": "EUCLID-9",
        "title": "CONSOLE 4 • EUCLID-9 • THE UNSUSPECTING PARALLELOGRAM (I.34 / G.47)",
        "start_sec": round(seg4_start, 3),
        "end_sec": round(seg4_end, 3),
        "steps": [
            {
                "id": "4a_sighting",
                "start_sec": round(step4a_start, 3),
                "end_sec": round(step4a_end, 3),
                "subtitle": "Euclid Signal Detector alert (03:12 UTC): inside unmanned Brine Evaporation Vat 19 on Callisto-South, Frame 7 locked onto an unsuspecting parallelogram in the salt crust.",
            },
            {
                "id": "4b_construction",
                "start_sec": round(step4b_start, 3),
                "end_sec": round(step4b_end, 3),
                "subtitle": "Opposite sides parallel to 0.0002 arcsec (AB || CD, AC || BD)—and somebody drew the diameter BC, bisecting the sludge into two congruent triangles (Euclid I.34 / G.47).",
            },
            {
                "id": "4c_punchline",
                "start_sec": round(step4c_start, 3),
                "end_sec": round(step4c_end, 3),
                "subtitle": "The Water Board claims a motorized mud-rake lost a cotter pin and dragged sideways. It's always a broken cotter pin, folks.",
            },
        ],
    })

    # --- SEG 5: ON THE NEXT BROADCAST & SIGN-OFF (SCHED-9 -> CAM-00) ---
    seg5_start = cursor_sec
    append_chunk(soft_squelch)
    append_chunk(bell_context)
    append_chunk(speak.silence_pcm(0.15))

    # Split seg5 visually: first 62% on SCHED-9 teaser card, last 38% returning to CAM-00 exterior tower
    seg5_voice_dur = dur_sec(seg_pcm_map["seg5_sched_signoff"])
    cam00_return_sec = cursor_sec + seg5_voice_dur * 0.62

    append_chunk(seg_pcm_map["seg5_sched_signoff"])
    append_chunk(speak.silence_pcm(0.15))
    closing_ding_sec = cursor_sec
    append_chunk(ding_ding)
    append_chunk(speak.silence_pcm(0.35))
    seg5_end = cursor_sec
    timeline_events.append({
        "id": "seg5_signoff",
        "console": "SCHED-9",
        "title": "CONSOLE 5 • SCHED-9 & SIGN-OFF -> CAM-00 TOWER",
        "start_sec": round(seg5_start, 3),
        "cam00_return_sec": round(cam00_return_sec, 3),
        "closing_ding_sec": round(closing_ding_sec, 3),
        "end_sec": round(seg5_end, 3),
        "subtitle": "On the next broadcast: an unlicensed numbers station in the Trojans reciting dumpling recipes in base-8, and a suspected rhombus aboard an ice-hauler. From Asteroid 3-5-1 in Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum.",
    })

    # --- SEG 6: 20-SECOND END-CARD OUTRO & CREDITS (O.R.S. 351 SATELLITE DOWNLINK) ---
    seg6_start = cursor_sec
    outro_dur = 20.0
    n_out = int(outro_dur * SAMPLE_RATE)
    tt_out = np.arange(n_out, dtype=np.float64) / SAMPLE_RATE

    # Generate a dreamy cosmic shortwave interval-signal musical chime bed (Lydian/Pythagorean fifths)
    chime_bed = np.zeros(n_out, dtype=np.float64)
    # Warm sub-pad (C3 + G3 + D4 gentle breathing harmonic drone)
    pad = (
        0.35 * np.sin(2.0 * math.pi * 130.81 * tt_out)
        + 0.25 * np.sin(2.0 * math.pi * 196.00 * tt_out)
        + 0.18 * np.sin(2.0 * math.pi * 293.66 * tt_out)
    ) * (0.55 + 0.45 * np.sin(2.0 * math.pi * 0.18 * tt_out))
    chime_bed += pad * 0.08

    # Crystalline celesta/bell arpeggio notes across the 20s outro
    motif_freqs = [
        261.63,  # C4
        392.00,  # G4
        587.33,  # D5
        659.25,  # E5
        783.99,  # G5
        880.00,  # A5
        739.99,  # F#5 (Lydian fourth)
        987.77,  # B5
        783.99,  # G5
        659.25,  # E5
        587.33,  # D5
        392.00,  # G4
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
        # Bell envelope with soft attack and singing exponential decay
        env_n = (1.0 - np.exp(-tn / 0.012)) * np.exp(-tn / 0.72)
        tone_n = (
            0.68 * np.sin(2.0 * math.pi * f_n * tn)
            + 0.22 * np.sin(2.0 * math.pi * (2.0 * f_n) * tn) * np.exp(-tn / 0.35)
            + 0.10 * np.sin(2.0 * math.pi * (3.002 * f_n) * tn) * np.exp(-tn / 0.18)
        ) * env_n
        chime_bed[i0_n:i0_n + d_n] += tone_n * 0.16
        # Dotted-eighth tape echo (0.46s delay)
        i_echo = i0_n + int(0.46 * SAMPLE_RATE)
        if i_echo < n_out:
            d_e = min(d_n, n_out - i_echo)
            chime_bed[i_echo:i_echo + d_e] += tone_n[:d_e] * 0.07

    # Final resolving harmonic chord at t = 16.5s..20.0s (C4 + G4 + D5 + E5 + B5)
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

    # Overlay the Argon III-C outro narration starting at +0.85s into the 20s outro
    outro_voice_flt = bytes_to_float(seg_pcm_map["seg6_outro_credits"])
    v_start_idx = int(0.85 * SAMPLE_RATE)
    v_end_idx = min(n_out, v_start_idx + len(outro_voice_flt))
    v_len = v_end_idx - v_start_idx

    # Duck the musical chime softly (0.55x) while narration is speaking, then let it bloom (1.15x) after voice ends
    duck_env = np.ones(n_out, dtype=np.float64) * 1.15
    duck_env[max(0, v_start_idx - int(0.2 * SAMPLE_RATE)):min(n_out, v_end_idx + int(0.3 * SAMPLE_RATE))] = 0.55
    # Smooth fade-in and fade-out at the very end
    fade_out_len = int(2.0 * SAMPLE_RATE)
    duck_env[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)
    outro_mix = chime_bed * duck_env
    outro_mix[v_start_idx:v_end_idx] += outro_voice_flt[:v_len]

    # Add a very soft 1.2s carrier tail at the final second
    append_chunk(float_to_bytes(np.clip(outro_mix, -0.95, 0.95)))
    seg6_end = cursor_sec
    timeline_events.append({
        "id": "seg6_outro",
        "console": "ORS-351",
        "title": "O.R.S. 351 • ORBITAL SATELLITE DOWNLINK & END CARDS",
        "start_sec": round(seg6_start, 3),
        "end_sec": round(seg6_end, 3),
        "subtitle": "Remember, a like indication on your listening apparatus gives us three kilowatts, and a subscription gets us one step closer to upgrading our marzelvane emitters.",
    })


    master_pcm = b"".join(master_chunks)

    # Mix real video clip audio from episodes/ep01_2736.305_parallelogram/clips/ into Segment 3
    import subprocess
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

    # 3A: Titan-Minor Buoy N-24 (clip starts at sub3a_start + 2.80s)
    clip_3a = load_clip_audio("Buoy_bobbing*.mp4")
    if clip_3a is not None:
        t0_3a = sub3a_start + 2.80
        i0 = int(t0_3a * SAMPLE_RATE)
        n_c = min(len(clip_3a), len(master_flt) - i0)
        for k in range(n_c):
            t_abs = (i0 + k) / SAMPLE_RATE
            # Swell up during vignette break (vig3a_start..vig3a_end), duck under narrator voice
            gain = 0.85 if (vig3a_start - 0.15 <= t_abs <= vig3a_end + 0.15) else 0.30
            master_flt[i0 + k] += clip_3a[k] * gain

    # 3B: Callisto Dome-4 Noodle Market "Radio Corrugated" Blowtorch (clip starts at sub3b_start + 1.48s)
    clip_3b = load_clip_audio("Engineer_hits_antenna*.mp4")
    if clip_3b is not None:
        # Tone down the synthetic vig_bazaar slightly so the real blowtorch explosion & crowd reaction shine
        v0 = int(vig3b_start * SAMPLE_RATE)
        v1 = int(vig3b_end * SAMPLE_RATE)
        master_flt[v0:v1] *= 0.35

        t0_3b = sub3b_start + 1.48
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

    # 3C: Intergalactic M-33 Drift Buoy on Salt Flats (clip starts at sub3c_start + 0.35s)
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
        "episode": "GOR-9 • Episode 01 (2560x1440 QHD Reboot)",
        "galactic_epoch": "2736.305",
        "galactic_time": "0400 GCT (Pulsar B1937+21 Barycentric Standard)",
        "sample_rate": SAMPLE_RATE,
        "total_duration_sec": round(cursor_sec, 3),
        "segments": timeline_events,
    }
    timeline_path = EP_DIR / "script" / "ep01_timeline.json"
    timeline_path.write_text(json.dumps(timeline_doc, indent=2), encoding="utf-8")
    print(f"Saved Full Episode Master WAV (with live clip audio): {master_wav_path} ({cursor_sec:.2f}s)")
    print(f"Saved Timeline Manifest: {timeline_path}")



if __name__ == "__main__":
    main()
