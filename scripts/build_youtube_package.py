#!/usr/bin/env python3
"""Generate YouTube metadata (Title, Description, Chapter Markers, Tags) and
frame-accurate .srt / .vtt caption files for GOR-9 Episode 01 (gor9_ep01_full_demo.mp4).
"""

from pathlib import Path
import json
import wave

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
YT_DIR = EP_DIR / "youtube"
SEG_DIR = EP_DIR / "audio" / "segments"


def wav_dur(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def fmt_srt_time(sec: float) -> str:
    ms = int(round(sec * 1000.0))
    hh = ms // 3600000
    ms %= 3600000
    mm = ms // 60000
    ms %= 60000
    ss = ms // 1000
    ms %= 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def fmt_vtt_time(sec: float) -> str:
    return fmt_srt_time(sec).replace(",", ".")


def fmt_yt_chapter(sec: float) -> str:
    tot = int(round(sec))
    mm = tot // 60
    ss = tot % 60
    return f"{mm}:{ss:02d}"


def split_cues_proportional(start_sec: float, end_sec: float, lines: list[str]) -> list[tuple[float, float, str]]:
    """Split [start_sec, end_sec] across lines proportionally to character count."""
    total_chars = sum(max(1, len(line)) for line in lines)
    dur = max(0.2, end_sec - start_sec)
    cues = []
    cur = start_sec
    for i, line in enumerate(lines):
        w = max(1, len(line)) / total_chars
        nxt = end_sec if i == len(lines) - 1 else (cur + dur * w)
        cues.append((round(cur, 3), round(nxt - 0.04, 3), line))
        cur = nxt
    return cues


def main() -> None:
    YT_DIR.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((EP_DIR / "script" / "ep01_timeline.json").read_text(encoding="utf-8"))
    segs = {s["id"]: s for s in timeline["segments"]}

    s0 = segs["seg0_cold_open"]
    s1 = segs["seg1_weather"]
    s2 = segs["seg2_econ"]
    s3 = segs["seg3_hauser"]
    s4 = segs["seg4_euclid"]
    s5 = segs["seg5_signoff"]

    cues: list[tuple[float, float, str]] = []

    # --- SEG 0: COLD OPEN (0.00s - 17.32s) ---
    cues.append((0.00, 0.90, "[Shortwave static & carrier acquisition]"))
    cues.append((0.92, 4.25, "This is GOR-9. This is GOR-9."))
    cues.append((4.30, 5.20, "[Harmonic crystal signal-lock chime]"))
    cues.extend(
        split_cues_proportional(
            5.32,
            s0["end_sec"] - 0.35,
            [
                "Galactic Outpost Radio, broadcasting from the High Basalt Shelf\non Asteroid 3-5-1 in Sector 9.",
                "Fourteen-two-eighty-five kilohertz upper sideband.\nZero-four-hundred Galactic Coordinated.",
            ],
        )
    )

    # --- SEG 1: SPACE WEATHER (17.32s - 40.73s) ---
    v1_start = s1["start_sec"] + 0.88  # after soft squelch (0.28s) + bell (0.45s) + 0.15s
    v1_end = s1["end_sec"] - 0.45
    cues.extend(
        split_cues_proportional(
            v1_start,
            v1_end,
            [
                "Space Weather, with emphasis on Sector 9.",
                "Coreward lanes are calm—solar flux one-seventy-four, K-index two.",
                "Locally, an electrostatic dust squall on the Meridian Plateau\nhas engulfed Relay KZ9-Omega.",
                "Sixty-kilovolt triboelectric arcing across the feedhorn is causing\nminor phase-wobble in the number-four marzelvane bushing.",
                "Expect SINPO two-three-two-two-two.",
            ],
        )
    )

    # --- SEG 2: OUTPOST ECONOMICS (40.73s - 64.99s) ---
    v2_start = s2["start_sec"] + 0.93
    v2_end = s2["end_sec"] - 0.45
    cues.extend(
        split_cues_proportional(
            v2_start,
            v2_end,
            [
                "Outpost Economics.",
                "Grade-B Deuterium pellets rose four percent today following\na dragline cable slowdown at Silicate Quarry 44-K.",
                "Outpost Nine will step Reactor Two down to twelve kilowatts after midnight;\nDormitory B should plug in auxiliary foot-warmers.",
                "Meanwhile, our monthly supply tender remains impounded at Quarantine Buoy Twelve\nafter customs misfiled replacement oscillator tubes as fermented brine tubers.",
            ],
        )
    )

    # --- SEG 3: HAUSER CORRELATOR (64.99s - 102.74s) ---
    sv3a, sv3b, sv3c = s3["sub_views"]
    # 3A
    cues.extend(
        split_cues_proportional(
            sv3a["start_sec"] + 0.88,
            sv3a["vignette_start_sec"] - 0.10,
            [
                "On the Hauser Correlator: Titan-Minor, three-eight-ninety kilohertz.",
                "Hydrographic Buoy N-24 reciting methane tide tables,",
            ],
        )
    )
    cues.append((sv3a["vignette_start_sec"], sv3a["vignette_end_sec"], "[3,890 kHz CW telemetry & metallic buoy bell clank]"))
    cues.append(
        (
            sv3a["vignette_end_sec"] + 0.10,
            sv3a["end_sec"] - 0.35,
            "while migratory silt-striders rub against the guy-wires,\ndetuning the whip antenna.",
        )
    )

    # 3B
    cues.append(
        (
            sv3b["start_sec"] + 0.28,
            sv3b["vignette_start_sec"] - 0.10,
            "Callisto Dome Four, eleven-four-ten kilohertz.\nUnlicensed noodle-market broadcaster Radio Corrugated,",
        )
    )
    cues.append((sv3b["vignette_start_sec"], sv3b["vignette_end_sec"], "[11,410 kHz AM night-market lute & dipole blowtorch spike]"))
    cues.append(
        (
            sv3b["vignette_end_sec"] + 0.10,
            sv3b["end_sec"] - 0.35,
            "peaking right as their engineer hit the dipole with a blowtorch.",
        )
    )

    # 3C
    cues.extend(
        split_cues_proportional(
            sv3c["start_sec"] + 0.28,
            sv3c["end_sec"] - 0.45,
            [
                "And Intergalactic, M-Thirty-Three: a seven-hundred-year-old drift-buoy",
                "still issuing small-craft warnings for an ammonia sea\nthat evaporated in the Ming Dynasty.",
            ],
        )
    )

    # --- SEG 4: EUCLID SIGNAL DETECTOR (102.74s - 141.36s) ---
    st4a, st4b, st4c = s4["steps"]
    cues.extend(
        split_cues_proportional(
            st4a["start_sec"] + 0.93,
            st4a["end_sec"] - 0.25,
            [
                "Finally, a late-night alert on the Euclid Signal Detector,\nwhich scans the noise floor for signs of geometric intelligence.",
                "At zero-three-twelve UTC, inside unmanned Brine Evaporation Vat Nineteen\non Callisto-South, the detector locked onto Frame Seven:",
                "an unsuspecting parallelogram in the salt crust.",
            ],
        )
    )
    cues.extend(
        split_cues_proportional(
            st4b["start_sec"] + 0.57,
            st4b["end_sec"] - 0.25,
            [
                "Opposite sides parallel to two ten-thousandths of an arcsecond—\nA-B to C-D, A-C to B-D—",
                "and somebody drew the diameter B-C,\nbisecting the sludge into two congruent triangles.",
            ],
        )
    )
    cues.extend(
        split_cues_proportional(
            st4c["start_sec"] + 0.57,
            st4c["end_sec"] - 0.45,
            [
                "The Water Board claims a motorized mud-rake\nlost a cotter pin and dragged sideways.",
                "It's always a broken cotter pin, folks.",
            ],
        )
    )

    # --- SEG 5: ON THE NEXT BROADCAST & SIGN-OFF ---
    cues.extend(
        split_cues_proportional(
            s5["start_sec"] + 0.88,
            s5["closing_ding_sec"] - 0.15,
            [
                "On the next broadcast: an unlicensed numbers station in the Trojans\nreciting dumpling recipes in base-eight,",
                "and a suspected rhombus aboard an ice-hauler.",
                "From Asteroid 3-5-1 in Sector 9, this is GOR-9—\nyour eye to the cosmos, ear to the vacuum.",
            ],
        )
    )
    cues.append((s5["closing_ding_sec"], s5["closing_ding_sec"] + 0.90, "[Harmonic crystal sign-off chime]"))
    cues.append((s5["closing_ding_sec"] + 0.95, s5["end_sec"], "[Carrier transitions to O.R.S. 351 orbital downlink]"))

    # --- SEG 6: END CARD & CREDITS OUTRO (159.12s - 179.12s) ---
    s6 = segs.get("seg6_outro")
    if s6:
        cues.extend(
            split_cues_proportional(
                s6["start_sec"] + 0.85,
                s6["start_sec"] + 11.40,
                [
                    "Remember, a like indication on your listening apparatus\ngives us three kilowatts,",
                    "and a subscription gets us one step closer\nto upgrading our marzelvane emitters.",
                ],
            )
        )
        cues.append((s6["start_sec"] + 11.50, s6["end_sec"] - 0.50, "[Soft Lydian harmonic chime & orbital carrier]"))

    # Write SRT
    srt_lines = []
    for idx, (t0, t1, text) in enumerate(cues, start=1):
        srt_lines.append(f"{idx}\n{fmt_srt_time(t0)} --> {fmt_srt_time(t1)}\n{text}\n")
    srt_path = YT_DIR / "gor9_ep01.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    # Write VTT
    vtt_lines = ["WEBVTT\n"]
    for idx, (t0, t1, text) in enumerate(cues, start=1):
        vtt_lines.append(f"{idx}\n{fmt_vtt_time(t0)} --> {fmt_vtt_time(t1)}\n{text}\n")
    vtt_path = YT_DIR / "gor9_ep01.vtt"
    vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")

    # Build YouTube Metadata & Chapters (concise, in-world, no tags)
    chapters = [
        (0.0, "Cold Open • High Basalt Shelf Tower (14,285.7 kHz USB)"),
        (s1["start_sec"], "Space Weather • Relay KZ9-Omega & Marzelvane #4 Phase-Wobble"),
        (s2["start_sec"], "Outpost Economics • Quarry 44-K, Reactor #2 & Fermented Brine Tubers"),
        (sv3a["start_sec"], "Wideband Correlator • Titan-Minor Buoy N-24 (3,890 kHz)"),
        (sv3b["start_sec"], "Wideband Correlator • Callisto Dome-4 'Radio Corrugated' (11,410 kHz)"),
        (sv3c["start_sec"], "Wideband Correlator • Intergalactic M-33 Drift Buoy (1,420.4 MHz)"),
        (s4["start_sec"], "Euclid Signal Detector • The Unsuspecting Parallelogram (Book I, Prop. 34)"),
        (s5["start_sec"], "On the Next Broadcast & Sign-Off"),
    ]
    if s6:
        chapters.append((s6["start_sec"], "O.R.S. 351 Orbital Downlink & Station Credits (+3 kW / Marzelvane Upgrade)"))
    chapter_block = "\n".join(f"{fmt_yt_chapter(t)} {title}" for t, title in chapters)

    yt_md = f"""# GOR-9 • Episode 01 YouTube Upload Package (`@GOR-9-station`)

- **Channel**: `https://www.youtube.com/@GOR-9-station` (`@GOR-9-station`)
- **Galactic Timestamp**: `Epoch 2736.305 • 0400 GCT (Pulsar B1937+21 Barycentric Standard)`
- **Status**: YouTube Advanced Features Enabled (Custom Thumbnails, Chapters, SRT/VTT Captions, External Links, Pinned Comments)

## Title
**GOR-9 • Galactic Outpost Radio: The Unsuspecting Parallelogram (14,285.7 kHz USB • 0400 GCT)**

---

## YouTube Description (Copy-Paste Ready)

```text
This is GOR-9. Galactic Outpost Radio, broadcasting at 50 kilowatts from the High Basalt Shelf on Asteroid 3-5-1 in Sector 9.
14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.

{chapter_block}

Route physical QSL cards and SINPO reception reports via Titan Packet Buoy N-24, care of Galactic Outpost Radio, Asteroid 3-5-1, Sector 9.
From Asteroid 3-5-1 in Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum.
```

---

## Upload Assets (All in `episodes/ep01_2736.305_parallelogram/`)
- **Video (`2560×1440` QHD MP4)**: `episodes/ep01_2736.305_parallelogram/gor9_ep01.mp4` (also linked at repo root `gor9_ep01.mp4`)
- **Custom Thumbnails (`1280×720` JPG)**: `youtube/gor9_ep01_thumbnail_split.jpg` / `youtube/gor9_ep01_thumbnail_tower.jpg`
- **SRT Captions**: `youtube/gor9_ep01.srt`
- **WebVTT Captions**: `youtube/gor9_ep01.vtt`
"""
    yt_path = YT_DIR / "YOUTUBE_METADATA.md"
    yt_path.write_text(yt_md, encoding="utf-8")
    print(f"Saved {srt_path}, {vtt_path}, and {yt_path}")


if __name__ == "__main__":
    main()
