#!/usr/bin/env python3
"""Copy all 17 generated plates from the source brain directory into assets/plates/
and synthesize the Cold Open Argon III-C voice clips.
"""

from pathlib import Path
import shutil
import subprocess

BRAIN_DIR = Path("/home/phi/.gemini/antigravity/brain/9de40682-2e96-4746-8ad1-e0cbd4857be7")
WORK_DIR = Path("/home/phi/Sessions/GOR-9")
SPEAK_PY = Path("/home/phi/.gemini/config/skills/dialogue/scripts/speak.py")

PLATE_MAP = {
    "gor9_dish_array_twilight_1793535213870.jpg": "cam00_dishes_base.jpg",
    "gor9_dish_array_beacons_bright_1793540097747.jpg": "cam00_dishes_beacons_bright.jpg",
    "gor9_dish_array_sky_key_1793538860535.jpg": "cam00_dishes_sky_key.jpg",
    "gor9_dish_array_tilted_end_1793539544120.jpg": "cam00_dishes_tilted_end.jpg",
    "gor9_aurora_sky_bg_1793538812795.jpg": "cam00_aurora_sky_bg.jpg",
    "gor9_relay_station_storm_1793535224169.jpg": "cam02_relay_storm_start.jpg",
    "gor9_relay_station_storm_end_1793539557937.jpg": "cam02_relay_storm_end.jpg",
    "gor9_asteroid_slag_webcam_1793536036921.jpg": "cam44k_quarry_start.jpg",
    "gor9_asteroid_slag_webcam_end_1793539574350.jpg": "cam44k_quarry_end.jpg",
    "gor9_methane_shallows_cam_1793536047202.jpg": "cam_n24_shallows_start.jpg",
    "gor9_methane_shallows_end_1793538822969.jpg": "cam_n24_shallows_end.jpg",
    "gor9_orbital_bazaar_cam_1793536058104.jpg": "cam_sw4_bazaar_start.jpg",
    "gor9_orbital_bazaar_end_1793539587591.jpg": "cam_sw4_bazaar_end.jpg",
    "gor9_unsuspecting_parallelogram_cam_1793537120845.jpg": "cam_vat19_parallelogram.jpg",
    "gor9_crater_anomaly_cam_1793535243211.jpg": "cam04_crater_dish.jpg",
    "gor9_listening_desk_hauser_1793536068284.jpg": "desk01_hauser_receiver.jpg",
    "gor9_bunker_window_dishes_1793535234095.jpg": "bunker_window_dishes.jpg",
}


def main() -> None:
    plates_dir = WORK_DIR / "assets" / "plates"
    renders_dir = WORK_DIR / "renders"
    plates_dir.mkdir(parents=True, exist_ok=True)
    renders_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src_name, dst_name in PLATE_MAP.items():
        src_path = BRAIN_DIR / src_name
        dst_path = plates_dir / dst_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            copied += 1
            print(f"Copied {src_name} -> {dst_name}")
        else:
            print(f"WARNING: Missing {src_path}")
    print(f"Total plates copied: {copied}/{len(PLATE_MAP)}")

    if SPEAK_PY.exists():
        try:
            subprocess.run(
                [
                    "python3",
                    str(SPEAK_PY),
                    "This is GOR-9. This is GOR-9.",
                    "-o",
                    str(renders_dir / "cam00_voice_a.wav"),
                ],
                check=True,
            )
            subprocess.run(
                [
                    "python3",
                    str(SPEAK_PY),
                    "Galactic Outpost Radio, broadcasting from the High Basalt Shelf on Asteroid 3-5-1 in Sector 9. Fourteen-two-eighty-five kilohertz upper sideband. Zero-four-hundred Galactic Coordinated.",
                    "-o",
                    str(renders_dir / "cam00_voice_b.wav"),
                ],
                check=True,
            )
        except Exception as exc:
            print(f"Note: TTS synthesis skipped ({exc})")


if __name__ == "__main__":
    main()
