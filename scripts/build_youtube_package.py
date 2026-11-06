#!/usr/bin/env python3
"""Generate YouTube metadata (Title, Description, Chapter Markers) and
frame-accurate .srt / .vtt caption files for GOR-9 Broadcast 01 (gor9_ep01.mp4).
"""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
YT_DIR = EP_DIR / "youtube"


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
    s6 = segs.get("seg6_outro")

    cues: list[tuple[float, float, str]] = []

    # --- SEG 0: COLD OPEN ---
    cues.append((0.00, 0.90, "[Shortwave static & carrier acquisition]"))
    cues.append((0.92, 4.25, "This is GOR-9. This is GOR-9."))
    cues.append((4.30, 5.20, "[Harmonic crystal signal-lock chime]"))
    cues.extend(
        split_cues_proportional(
            5.32,
            s0["end_sec"] - 0.35,
            [
                "Galactic Outpost Radio, broadcasting from the High Basalt Shelf Tower\non Asteroid 3-5-1, 42,100 AU out in Oort Cloud Sector 9.",
                "Fourteen-two-eighty-five kilohertz upper sideband.\nZero-four-hundred Galactic Coordinated.",
            ],
        )
    )

    # --- SEG 1: VAN ALLEN VA-4 SPACE WEATHER & PROPAGATION ---
    v1_start = s1["start_sec"] + 0.88
    v1_end = s1["end_sec"] - 0.45
    cues.extend(
        split_cues_proportional(
            v1_start,
            v1_end,
            [
                "On the Van Allen VA-4 Propagation and Power Console—\nbrought to you by Van Allen and Sons Switchgear of Ceres Foundry Seven:",
                "Comet K-Four's ion tail is sweeping azimuth two-twelve,\nopening a clean 24 MHz skip corridor into the Jovian moons.",
                "Closer to home, a 60 kV triboelectric dust squall\nhas engulfed Relay KZ9-Omega—",
                "raising our lower usable frequency by 4 MHz and arcing\nacross the number-four Belt-Master marzelvane bushing.",
                "Expect SINPO two-three-two-two-two.",
            ],
        )
    )

    # --- SEG 2: VAN ALLEN VA-4 DILITHIUM POWER BUS ---
    v2_start = s2["start_sec"] + 0.93
    v2_end = s2["end_sec"] - 0.45
    cues.extend(
        split_cues_proportional(
            v2_start,
            v2_end,
            [
                "On the Dilithium Bus: Grade-B Dilithium pellets rose four percent\non the Ceres Exchange following a dragline cable slowdown at Silicate Quarry 44-K.",
                "With our Van Allen Ring-Bake corona de-icer pulling an extra 4.5 kilowatts,\nwe are stepping Reactor Two down to 12 kilowatts after midnight—",
                "Dormitory Wing B should plug in their Van Allen Cryo-Toast foot-warmers.",
                "Meanwhile, our monthly pellet and vacuum-tube tender remains impounded at Quarantine Buoy Twelve\nafter customs misfiled replacement oscillator tubes as fermented brine tubers.",
            ],
        )
    )

    # --- SEG 3: HAUSER DYNAMICS MK-IV WIDEBAND DX & DECODER ---
    sv3a, sv3b, sv3c, sv3d = s3["sub_views"]
    cues.extend(
        split_cues_proportional(
            sv3a["start_sec"] + 0.88,
            sv3a["vignette_start_sec"] - 0.10,
            [
                "Turning to the Hauser Dynamics Mark-Four Receiver and Galaxy Atlas:",
                "Preset Two—Titan-Minor, 3,890 kilohertz.\nHydrographic Buoy N-24 is transmitting methane tide telemetry,",
            ],
        )
    )
    cues.append((sv3a["vignette_start_sec"], sv3a["vignette_end_sec"], "[3,890 kHz CW telemetry & metallic buoy bell clank]"))
    cues.append(
        (
            sv3a["vignette_end_sec"] + 0.10,
            sv3a["end_sec"] - 0.30,
            "though migratory silt-striders rubbing against the guy-wires\njust detuned the whip antenna by 18 Hertz. eQSL #0882 logged.",
        )
    )

    cues.append(
        (
            sv3b["start_sec"] + 0.28,
            sv3b["vignette_start_sec"] - 0.10,
            "Preset One—Callisto Dome Four, 11,410 kilohertz.\nUnlicensed noodle-market broadcaster Radio Corrugated,",
        )
    )
    cues.append((sv3b["vignette_start_sec"], sv3b["vignette_end_sec"], "[11,410 kHz AM night-market lute & dipole blowtorch spike]"))
    cues.append(
        (
            sv3b["vignette_end_sec"] + 0.10,
            sv3b["end_sec"] - 0.30,
            "peaking at S9+10 right as their engineer hit the rooftop dipole with a blowtorch.",
        )
    )

    cues.extend(
        split_cues_proportional(
            sv3c["start_sec"] + 0.28,
            sv3c["end_sec"] - 0.30,
            [
                "Preset Three—extragalactic, 1,420 MHz on the hydrogen line,\n2.7 million light-years toward M-33.",
                "No video carrier on this band—just a relativistic Doppler Lissajous on the spectrum scan.",
                "Running Translation Algorithm 02 against the raw hex stream decodes Buoy M-33-771:\nstill issuing small-craft advisories for an ammonia sea that evaporated during the Ming Dynasty.",
            ],
        )
    )

    cues.extend(
        split_cues_proportional(
            sv3d["start_sec"] + 0.28,
            sv3d["end_sec"] - 0.45,
            [
                "And on Preset Four, 6,925 kilohertz in the Jupiter Trojans:\nan encrypted base-eight numbers station",
                "where Algorithm 03 just decoded six metric tons of pork-chive dumpling wrappers—\nplus an octal shift key of 13 for those tracking the sector cipher in the station log.",
            ],
        )
    )

    # --- SEG 4: BOGEY-9 TRAIL-CAM & VAN ALLEN ED-9 EUCLIDEAN DETECTOR ---
    st4a, st4b, st4c, st4d = s4["steps"]
    cues.extend(
        split_cues_proportional(
            st4a["start_sec"] + 0.93,
            st4a["end_sec"] - 0.30,
            [
                "Quick check on the Bogey-Nine Perimeter Trail-Cam,\nwhich discriminates ballistic Oort rocks from non-Keplerian visitors right outside our cliff rim.",
                "At 03:41 Galactic, Trail-Cam One on the Acheron North Rim triggered an eight-frame burst\non a mirror-chrome cylinder drifting between two tumbling boulders at 14 m/s—",
                "before executing a 90-degree vertical snap-turn on Frame Five at 140g with zero thruster plume.\nThe Outer Belt Safety Board says it was a vented thermos flask from the Mess Hall.",
            ],
        )
    )
    cues.extend(
        split_cues_proportional(
            st4b["start_sec"] + 0.88,
            st4b["end_sec"] - 0.25,
            [
                "Now to our centerpiece instrument: the Van Allen ED-9 Euclidean Detector—\nsearching for geometric intelligence across the universe.",
                "Natural vacuum produces fractals and thermal static;\nintelligence leaves straight lines, parallel chords, and constructive ratios.",
                "Tonight, our 12-tube Hough Transform correlator locked onto a single 99.998% synthetic signature\nin Callisto-South Brine Evaporation Vat 19: the Unsuspecting Parallelogram.",
            ],
        )
    )
    cues.extend(
        split_cues_proportional(
            st4c["start_sec"] + 0.62,
            st4c["end_sec"] - 0.25,
            [
                "Under inspection-beam sweep Frame Seven, four salt-crust ridges form parallelogram ABDC—\nsatisfying Euclid Book One, Proposition 34:",
                "opposite sides AB and CD, and AC and BD, hold parallel to 0.0002 arcseconds,\nwhile diagonal diameter BC bisects the brine sludge into two congruent triangles.",
            ],
        )
    )
    cues.extend(
        split_cues_proportional(
            st4d["start_sec"] + 0.57,
            st4d["end_sec"] - 0.45,
            [
                "Seven minutes after our Van Allen detector logged the Proposition 34 proof,\nthe Callisto Water Board scrubbed the archive and blamed a motorized mud-rake that lost a cotter pin.",
                "That is one remarkably well-educated mud-rake, folks.",
            ],
        )
    )

    # --- SEG 5: COMING NEXT, VAN ALLEN UNDERWRITER & SIGN-OFF ---
    cues.extend(
        split_cues_proportional(
            s5["start_sec"] + 0.88,
            s5["closing_ding_sec"] - 0.15,
            [
                "On the next broadcast: an uninspected Dilithium barge rendezvous in the tail of Comet K-Four,\nand a suspected rhombus aboard a bulk ice-hauler.",
                "This broadcast is underwritten by Van Allen and Sons Switchgear—\nfrom radiation belts to reactor beds, if it arcs, we clamp it.",
                "From Asteroid 3-5-1 in Oort Cloud Sector 9, this is GOR-9—\nyour eye to the cosmos, ear to the vacuum.",
            ],
        )
    )
    cues.append((s5["closing_ding_sec"], s5["closing_ding_sec"] + 0.90, "[Harmonic crystal sign-off chime]"))
    cues.append((s5["closing_ding_sec"] + 0.95, s5["end_sec"], "[Carrier transitions to O.R.S. 351 orbital downlink]"))

    # --- SEG 6: END CARD & CREDITS OUTRO ---
    if s6:
        cues.extend(
            split_cues_proportional(
                s6["start_sec"] + 0.85,
                s6["start_sec"] + 12.20,
                [
                    "Remember, a like indication on your listening apparatus\ngives us three kilowatts of Dilithium reserve,",
                    "and a subscription gets us one step closer\nto shielding our marzelvane emitters.",
                ],
            )
        )
        cues.append((s6["start_sec"] + 12.30, s6["end_sec"] - 0.50, "[Soft Lydian harmonic chime & orbital carrier]"))

    srt_lines = []
    for idx, (t0, t1, text) in enumerate(cues, start=1):
        srt_lines.append(f"{idx}\n{fmt_srt_time(t0)} --> {fmt_srt_time(t1)}\n{text}\n")
    srt_path = YT_DIR / "gor9_ep01.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    vtt_lines = ["WEBVTT\n"]
    for idx, (t0, t1, text) in enumerate(cues, start=1):
        vtt_lines.append(f"{idx}\n{fmt_vtt_time(t0)} --> {fmt_vtt_time(t1)}\n{text}\n")
    vtt_path = YT_DIR / "gor9_ep01.vtt"
    vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")

    chapters = [
        (0.0, "Cold Open • High Basalt Shelf Tower & ATC Control Room (14,285.7 kHz USB)"),
        (s1["start_sec"], "Van Allen VA-4 • Comet K-4 Skip Corridor, KZ9-Omega Squall & Belt-Master Marzelvane #4"),
        (s2["start_sec"], "Dilithium Bus • Quarry 44-K, Ring-Bake De-Icer, Cryo-Toast Warmers & Brine Tubers"),
        (sv3a["start_sec"], "Hauser Dynamics MK-IV • Titan-Minor Buoy N-24 (3,890 kHz • eQSL #0882)"),
        (sv3b["start_sec"], "Hauser Dynamics MK-IV • Callisto Dome-4 'Radio Corrugated' Blowtorch (11,410 kHz)"),
        (sv3c["start_sec"], "Hauser Dynamics MK-IV • Extragalactic M-33 Ming Drift Buoy (1,420.4 MHz • ALG-02)"),
        (sv3d["start_sec"], "Hauser Dynamics MK-IV • Trojan Octal Numbers Station (6,925 kHz • ALG-03)"),
        (st4a["start_sec"], "Bogey-9 Perimeter Trail-Cam • 140g Mirror-Chrome UAP Cylinder (TRL-01)"),
        (st4b["start_sec"], "Van Allen ED-9 Euclidean Detector • The Unsuspecting Parallelogram (Euclid I.34 / G.47)"),
        (s5["start_sec"], "Coming Next (Ice-Hauler Rhombus), Van Allen Switchgear Underwriter & Sign-Off"),
    ]
    if s6:
        chapters.append((s6["start_sec"], "O.R.S. 351 Orbital Downlink & Station Credits (+3 kW / Marzelvane Shielding)"))
    chapter_block = "\n".join(f"{fmt_yt_chapter(t)} {title}" for t, title in chapters)

    yt_md = f"""# GOR-9 • Broadcast 01 YouTube Upload Package (`@GOR-9-station`)

- **Channel**: `https://www.youtube.com/@GOR-9-station` (`@GOR-9-station`)
- **Galactic Timestamp**: `Epoch 2736.305 • 0400 GCT (Pulsar B1937+21 Barycentric Standard)`
- **Status**: YouTube Advanced Features Enabled (Custom Thumbnails, Chapters, SRT/VTT Captions, External Links, Pinned Comments)

## Title
**GOR-9 • Galactic Outpost Radio: The Unsuspecting Parallelogram (14,285.7 kHz USB • 0400 GCT)**

---

## YouTube Description (Copy-Paste Ready)

```text
This is GOR-9. Galactic Outpost Radio, broadcasting at 50 kilowatts from the High Basalt Shelf Tower on Asteroid 3-5-1, 42,100 AU out in Oort Cloud Sector 9.
14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.
Underwritten by Van Allen & Sons Switchgear (Ceres Foundry #7) — "From radiation belts to reactor beds, if it arcs, we clamp it."

{chapter_block}

Route eQSL cards and SINPO reception reports via Titan Packet Buoy N-24, care of Galactic Outpost Radio, Asteroid 3-5-1, Oort Cloud Sector 9.
From Asteroid 3-5-1 in Oort Cloud Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum.
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
