#!/usr/bin/env python3
"""Capture all 2560x1440 (16:9 QHD) HTML console states for GOR-9 Broadcast 01."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

try:
    from photon_platform.studio.svg_utils import find_chrome
except ImportError:
    sys.path.insert(0, "/home/phi/PROJECTS/photon-platform/studio/src")
    from photon_platform.studio.svg_utils import find_chrome  # noqa: E402

CHROME = str(find_chrome())
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram" / "console_plates"

CAPTURE_SPECS = [
    # SEG-0: Octagonal ATC Control Tower Deck & Makers Modal
    ("tower_modal", f"file://{DOCS}/index.html?id=buoy-n24&modal=tower&sstv=instant&capture=1"),

    # SEG-1: Console 1 — Van Allen VA-4 Space Weather & Propagation
    ("va4_1a_comet", f"file://{DOCS}/propagation.html?regime=1&corridor=0&peak=1&deicer=0&clamp=1&capture=1"),
    ("va4_1b_squall", f"file://{DOCS}/propagation.html?regime=2&corridor=5&peak=1&deicer=0&clamp=1&capture=1"),
    ("va4_1c_clamp", f"file://{DOCS}/propagation.html?regime=2&corridor=5&peak=1&deicer=1&clamp=1&capture=1"),

    # SEG-2: Console 1B — Van Allen VA-4 Dilithium Power Bus
    ("va4_2a_spot", f"file://{DOCS}/propagation.html?regime=1&corridor=1&peak=1&deicer=0&clamp=1&capture=1"),
    ("va4_2b_stepdown", f"file://{DOCS}/propagation.html?regime=0&corridor=1&peak=0&deicer=1&clamp=1&capture=1"),
    ("va4_2c_quarantine", f"file://{DOCS}/propagation.html?regime=3&corridor=4&peak=1&deicer=1&clamp=1&capture=1"),

    # SEG-3: Console 2 — Hauser Dynamics MK-IV & Station Dossiers
    ("mk4_3a_video", f"file://{DOCS}/index.html?id=buoy-n24&mode=video&sstv=instant&capture=1"),
    ("mk4_3a_decoder", f"file://{DOCS}/index.html?id=buoy-n24&mode=decoder&sstv=instant&capture=1"),
    ("dos_3a_n24", f"file://{DOCS}/station.html?id=buoy-n24&capture=1"),

    ("mk4_3b_video", f"file://{DOCS}/index.html?id=radio-corrugated&mode=video&sstv=instant&capture=1"),
    ("mk4_3b_decoder", f"file://{DOCS}/index.html?id=radio-corrugated&mode=decoder&sstv=instant&capture=1"),

    ("mk4_3c_spectrum", f"file://{DOCS}/index.html?id=m33-drift-buoy&mode=spectrum&sstv=instant&capture=1"),
    ("mk4_3c_decoder", f"file://{DOCS}/index.html?id=m33-drift-buoy&mode=decoder&sstv=instant&capture=1"),
    ("mk4_3c_atlas", f"file://{DOCS}/index.html?id=m33-drift-buoy&modal=galaxy&sstv=instant&capture=1"),

    ("mk4_3d_decoder", f"file://{DOCS}/index.html?id=trojan-octal&mode=decoder&sstv=instant&capture=1"),
    ("dos_3d_octal_back", f"file://{DOCS}/station.html?id=trojan-octal&flip=1&capture=1"),

    # SEG-4A: Console 3 — Bogey-9 Trail-Cam & UAP Detector (Strictly Kinematic)
    ("bogey_4a_gif", f"file://{DOCS}/bogey-detector.html?bogey=0&mode=gif&filter=raw&vector=1&capture=1"),
    ("bogey_4a_frame6", f"file://{DOCS}/bogey-detector.html?bogey=0&mode=forensic&frame=6&filter=raw&vector=1&capture=1"),
    ("bogey_4a_nvg", f"file://{DOCS}/bogey-detector.html?bogey=0&mode=forensic&frame=6&filter=nvg&vector=1&capture=1"),

    # SEG-4B..4D: Console 4 — Van Allen ED-9 Euclidean Detector (Single Detection: Vat 19 Parallelogram I.34)
    ("ed9_4b_step1", f"file://{DOCS}/euclidean-detector.html?det=0&step=0&capture=1"),
    ("ed9_4c_step2", f"file://{DOCS}/euclidean-detector.html?det=0&step=1&capture=1"),
    ("ed9_4c_step3", f"file://{DOCS}/euclidean-detector.html?det=0&step=2&capture=1"),
    ("ed9_4d_step4", f"file://{DOCS}/euclidean-detector.html?det=0&step=3&capture=1"),

    # SEG-5: Coming Next on Van Allen ED-9 (The Ice-Hauler Rhombus Def. I.22)
    ("ed9_5a_rhombus", f"file://{DOCS}/euclidean-detector.html?next=1&step=2&capture=1"),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    only_names = set(sys.argv[1:])
    chrome_env = os.environ.copy()
    chrome_env["HOME"] = "/tmp"
    chrome_env["XDG_CONFIG_HOME"] = "/tmp/.config"
    chrome_env["XDG_CACHE_HOME"] = "/tmp/.cache"

    for name, url in CAPTURE_SPECS:
        if only_names and name not in only_names:
            continue
        out_path = OUT_DIR / f"{name}.png"
        cmd = [
            CHROME,
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--use-gl=angle",
            "--use-angle=gl",
            "--hide-scrollbars",
            "--window-size=1920,1080",
            "--force-device-scale-factor=1.3333333333",
            "--virtual-time-budget=600",
            f"--screenshot={out_path}",
            url,
        ]
        res = subprocess.run(cmd, timeout=20, capture_output=True, text=True, env=chrome_env)
        if res.returncode != 0:
            raise RuntimeError(f"Failed capturing {name}: {res.stderr}")
        print(f"  [captured] {name}.png (2560x1440)")


if __name__ == "__main__":
    main()
