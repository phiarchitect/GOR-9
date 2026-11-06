#!/usr/bin/env python3
"""
GOR-9 • Oort Cloud Sector 9 Celestial Sphere, Planetary Neighbors & Signal Atlas
================================================================================
Maps the astronomical sky, local Oort Cloud planetary neighbors, triangulation
reference anchors (`Sol`, `Ceres Foundry #7`, `PSR B1937+21`), and all 8 deep-space
signal bearings from `docs/data/stations.json` onto a unified 3D Celestial Sphere
around Asteroid 3-5-1 (`GOR-9`, `42,100 AU` / `0.665 ly` from Sol).

Astrophysical & Worldbuilding Model of the Oort Sector 9 Sky:
-------------------------------------------------------------
1. **Sol (The Distant Sun at 42,100 AU / 0.665 ly)**:
   - Apparent magnitude: `m = -26.74 + 5 * log10(42100) = -3.62`
   - Angular diameter: `~0.045 arcseconds` (an unresolved, razor-sharp stellar point-source,
     roughly 8x brighter than Sirius and nearly as bright as Venus from Earth).
   - Bearing: `Az = 212.4°` (Coreward Sol–Jovian Duct), local elevation `+22.4°` above the
     SSW horizon, casting crisp silver-gold directional light across the basalt cliffs.
2. **Ceres Foundry #7 (`CFS-7` • Dwarf Planet Hub & Primary Triangulation Baseline)**:
   - Bearing: `Az = 272.0°`, local elevation `+14.6°` (`1,840 AU` West-Coreward in the outer
     Foundry/Syndicate belt). Home to Van Allen & Sons Switchgear (Foundry #7), the Ceres
     Dilithium Spot Exchange, and the automated `6,440 kHz` Syndicate jammer.
   - Forms the primary **1,840 AU Astrometric Triangulation Baseline** with `GOR-9` and `Sol`
     (`59.6°` angular separation from Sol) used to range and triangulate local Oort vessels
     and deep-space relay hops. Appears in telescope view as a warm amber-ochre dwarf planet
     (`m = +0.4`) with glowing sodium-slag foundry canyons on its night hemisphere.
3. **Local Oort Sector 9 Planetary Neighbors (Visible Resolved Disks in the Sky)**:
   - **Persephone / 90377 Sedna-IX (`Az = 148.5°, El = +28.4°`, `0.18 AU`)**: Detached Oort
     ringed ice-dwarf (`2,380 km` diameter) with a shimmering teal-emerald methane-ice ring
     system (`44"` span, `m = -1.8`), visible from the booth windows over the SE chasm as a
     crescent ringed cryo-planet.
   - **Tartarus / Orcus-Vanth IX & Quarantine Buoy 12 (`Az = 304.2°, El = +19.2°`, `420 AU`)**:
     Tidally locked binary Oort dwarf planet pair where Quarantine Buoy 12 is moored (and
     where GOR-9's monthly Dilithium pellet & 811A tube tender is impounded).
   - **Silicate Quarry 44-K (`Az = 288.5°, El = +9.4°`, `890 AU`)**: Industrial open-pit
     silicate and Grade-B Dilithium mining planetoid on the Ceres–Trojan trade corridor.
   - **Comet C/2736-K4 (`Az = 264.0°, El = +32.5°`, `3,700 AU`)**: Active Oort macro-comet
     with a `6.5°`-wide cyanogen-green ionized coma & plasma tail (`+11.4 dB` Es-Oort scatter).
   - **O.R.S. 351 Polar Halo (`Az = 125.6°, El = +16.4°`, `42.8 km`)**: Local station-keeping
     orbital relay satellite and remote camera platform (`CAM-SAT09`) off Acheron Chasm.
"""

import json
import math
import random
from pathlib import Path

from .primitives import add_octahedron_beacon, add_ring_torus, add_strut, create_scene_group


def galactic_to_local_el(az_deg: float, gal_lat_deg: float) -> float:
    """
    Convert Galactic plane inclination `b` (`gal_lat_deg`) into local horizon
    elevation `el_deg` above Asteroid 3-5-1's High Basalt Shelf (88.4° S pole).
    """
    tilt_curve = 14.0 * math.cos(math.radians(az_deg - 205.0)) + 15.5
    el = gal_lat_deg * 0.55 + tilt_curve
    return round(max(-8.0, min(68.0, el)), 1)


def az_el_to_xyz(az_deg: float, el_deg: float, radius: float = 1.0) -> tuple[float, float, float]:
    """Convert `(Azimuth deg, Elevation deg, radius)` to Z-up `(x, y, z)`."""
    az_r = math.radians(az_deg)
    el_r = math.radians(el_deg)
    cos_el = math.cos(el_r)
    x = radius * cos_el * math.sin(az_r)
    y = radius * cos_el * math.cos(az_r)
    z = radius * math.sin(el_r)
    return (x, y, z)


def angular_separation_deg(az1: float, el1: float, az2: float, el2: float) -> float:
    """Compute great-circle angular separation (in degrees) between two sky bearings."""
    v1 = az_el_to_xyz(az1, el1, 1.0)
    v2 = az_el_to_xyz(az2, el2, 1.0)
    dot = max(-1.0, min(1.0, v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]))
    return round(math.degrees(math.acos(dot)), 1)


def load_celestial_catalog(repo_root: Path) -> list[dict]:
    """Build the authoritative catalog of celestial landmarks, Oort neighbors, and signal bearings."""
    catalog = [
        {
            "id": "sol-oort-star",
            "code": "SOL (m = -3.62)",
            "name": "Sol • The Distant Sun (42,100 AU)",
            "subtitle": "Coreward G2V Primary • Apparent Mag -3.62 • 0.665 ly",
            "category": "star",
            "body_type": "g2v_star",
            "az_deg": 212.4,
            "gal_lat_deg": -4.2,
            "local_el_deg": 22.4,
            "range_au": 42100.0,
            "range_ly": 0.665,
            "range_label": "42,100 AU (0.665 ly)",
            "radial_3d": 0.48,
            "freq_label": "10.7cm Flux: 148.2 SFU",
            "apparent_size": "0.045\" Point-Star (m = -3.62)",
            "triangulation_role": "Primary Heliocentric Origin & Optical/Flux Reference",
            "color": (1.0, 0.93, 0.72),
            "hex": "#ffedba",
        },
        {
            "id": "ceres-foundry-7",
            "code": "CERES FOUNDRY #7",
            "name": "Ceres Foundry #7 (CFS-7 Dwarf Planet Hub)",
            "subtitle": "Van Allen Switchgear HQ • Dilithium Spot Exchange • Syndicate Jammer",
            "category": "planet",
            "body_type": "dwarf_planet_foundry",
            "az_deg": 272.0,
            "gal_lat_deg": -2.8,
            "local_el_deg": 14.6,
            "range_au": 1840.0,
            "range_ly": 0.029,
            "range_label": "1,840 AU (0.029 ly Baseline)",
            "radial_3d": 0.34,
            "freq_label": "10.0 MHz CFS-7 Beacon / 6440 Jammer",
            "apparent_size": "6.8\" Amber Disk (m = +0.4)",
            "triangulation_role": "Primary 1,840 AU Triangulation Baseline & Foundry Reference",
            "color": (1.0, 0.62, 0.22),
            "hex": "#ff9e38",
        },
        {
            "id": "persephone-sedna9",
            "code": "PERSEPHONE (SEDNA-IX)",
            "name": "Persephone • Ringed Oort Cryo-Planet",
            "subtitle": "Detached Sector 9 Ice-Dwarf (2,380 km) with Teal Methane Rings",
            "category": "planet",
            "body_type": "ringed_cryo_planet",
            "az_deg": 148.5,
            "gal_lat_deg": -12.4,
            "local_el_deg": 28.4,
            "range_au": 0.18,
            "range_ly": 0.0000028,
            "range_label": "0.18 AU (26.9M km Local)",
            "radial_3d": 0.18,
            "freq_label": "22.4 kHz Cryo-Aurora Whisper",
            "apparent_size": "18.2\" Disk / 44\" Rings (m = -1.8)",
            "triangulation_role": "Closest Planetary Neighbor • Resolved Crescent & Ring Plane",
            "color": (0.24, 0.94, 0.85),
            "hex": "#3df0d9",
        },
        {
            "id": "tartarus-buoy12",
            "code": "TARTARUS / BUOY 12",
            "name": "Tartarus Binary Plutoid & Quarantine Buoy 12",
            "subtitle": "Tidally Locked Oort Double-Dwarf • Customs Impound Anchorage",
            "category": "planet",
            "body_type": "binary_plutoid",
            "az_deg": 304.2,
            "gal_lat_deg": 4.6,
            "local_el_deg": 19.2,
            "range_au": 420.0,
            "range_ly": 0.0066,
            "range_label": "420 AU (Sector 9 Customs)",
            "radial_3d": 0.25,
            "freq_label": "4,125.0 kHz USB Customs Hold",
            "apparent_size": "4.2\" + 1.8\" Binary Pair (m = +1.6)",
            "triangulation_role": "Outer Customs Checkpoint (Pellet & 811A Tube Tender Impounded)",
            "color": (0.72, 0.64, 0.98),
            "hex": "#b8a3fa",
        },
        {
            "id": "quarry-44k",
            "code": "QUARRY 44-K",
            "name": "Asteroid Silicate Quarry 44-K",
            "subtitle": "Open-Pit Silicate & Grade-B Dilithium Dragline Mining World",
            "category": "planet",
            "body_type": "mining_asteroid",
            "az_deg": 288.5,
            "gal_lat_deg": 1.2,
            "local_el_deg": 9.4,
            "range_au": 890.0,
            "range_ly": 0.014,
            "range_label": "890 AU (West Mining Belt)",
            "radial_3d": 0.29,
            "freq_label": "5,180.0 kHz Dragline Telemetry",
            "apparent_size": "2.4\" Amber Floodlit Crag",
            "triangulation_role": "Sector 9 Industrial Ore & Dilithium Supply Node",
            "color": (0.96, 0.75, 0.32),
            "hex": "#f5bf52",
        },
        {
            "id": "ors-351-halo",
            "code": "O.R.S. 351 HALO",
            "name": "O.R.S. 351 Polar Halo Relay Satellite",
            "subtitle": "Local Orbital Relay Transponder & CAM-SAT09 Optical Platform",
            "category": "relay",
            "body_type": "orbital_satellite",
            "az_deg": 125.6,
            "gal_lat_deg": -8.0,
            "local_el_deg": 16.4,
            "range_au": 0.000286,
            "range_ly": 4.5e-9,
            "range_label": "42.8 km (Polar Halo Orbit)",
            "radial_3d": 0.12,
            "freq_label": "Local Uplink / Halo Trunk",
            "apparent_size": "Artificial Star (m = -2.4)",
            "triangulation_role": "Near-Field Relay Hop #1 & Downlook Camera Anchor",
            "color": (0.35, 0.92, 1.0),
            "hex": "#59ebff",
        },
        {
            "id": "psr-b1937",
            "code": "PSR B1937+21",
            "name": "Vulpecula Millisecond Pulsar",
            "subtitle": "Barycentric Station Clock Reference • 641.928262 Hz",
            "category": "pulsar",
            "body_type": "millisecond_pulsar",
            "az_deg": 57.5,
            "gal_lat_deg": -0.3,
            "local_el_deg": 24.8,
            "range_au": 7.4e8,
            "range_ly": 11700.0,
            "range_label": "11,700 ly (3.59 kpc)",
            "radial_3d": 0.84,
            "freq_label": "641.928 Hz Metronome",
            "apparent_size": "1.557 ms Barycentric Pulse",
            "triangulation_role": "Galactic Coordinated Time (GCT) & Phase-Lock Reference",
            "color": (0.22, 0.95, 1.0),
            "hex": "#38f2ff",
        },
        {
            "id": "sgr-a-core",
            "code": "SGR A* CORE",
            "name": "Sagittarius Galactic Center",
            "subtitle": "Milky Way Central Bulge & Dust Rift (l = 0°, b = 0°)",
            "category": "galactic",
            "body_type": "galactic_core",
            "az_deg": 18.6,
            "gal_lat_deg": 0.0,
            "local_el_deg": 18.0,
            "range_au": 1.67e9,
            "range_ly": 26480.0,
            "range_label": "26,480 ly (8.12 kpc)",
            "radial_3d": 0.90,
            "freq_label": "Galactic Equator (l = 0°)",
            "apparent_size": "24° Golden Bulge & Rift",
            "triangulation_role": "Galactic Longitude 000.0° Zero-Meridian Anchor",
            "color": (1.0, 0.74, 0.38),
            "hex": "#ffbd61",
        },
    ]

    stations_path = repo_root / "docs" / "data" / "stations.json"
    palette_by_slot = {
        "P-01": ("#ffae2b", (1.0, 0.68, 0.17)),
        "P-02": ("#38eaff", (0.22, 0.92, 1.00)),
        "P-03": ("#c084fc", (0.75, 0.52, 0.99)),
        "P-04": ("#f43f5e", (0.96, 0.25, 0.37)),
        "P-05": ("#4ade80", (0.29, 0.87, 0.50)),
        "P-06": ("#facc15", (0.98, 0.80, 0.08)),
        "P-07": ("#fb7185", (0.98, 0.44, 0.52)),
        "P-08": ("#60a5fa", (0.38, 0.65, 0.98)),
    }

    if stations_path.exists():
        data = json.loads(stations_path.read_text())
        for p in data.get("presets", []):
            gal = p.get("galactic", {})
            rf = p.get("rf", {})
            slot = p.get("preset_slot", "P-00")
            az = float(gal.get("azimuth_deg", 0.0))
            b_lat = float(gal.get("elevation_deg", 0.0))
            el_local = galactic_to_local_el(az, b_lat)
            if slot == "P-01":
                el_local = 17.2
            elif slot == "P-06":
                el_local = 12.8
            elif slot == "P-07":
                el_local = el_local + 4.2

            hex_col, rgb_col = palette_by_slot.get(slot, ("#38eaff", (0.22, 0.92, 1.0)))
            khz = float(rf.get("frequency_khz", 0.0))
            freq_str = f"{khz / 1000.0:.3f} MHz" if khz >= 100000 else f"{khz:,.1f} kHz"
            r_ly = float(gal.get("range_ly", 1.0))

            catalog.append(
                {
                    "id": p.get("id", slot),
                    "slot": slot,
                    "callsign": p.get("callsign", ""),
                    "code": f"{slot} • {p.get('callsign', '')}",
                    "name": p.get("name", ""),
                    "subtitle": p.get("origin", {}).get("body", ""),
                    "category": "signal",
                    "body_type": "station_node",
                    "az_deg": az,
                    "gal_lat_deg": b_lat,
                    "local_el_deg": el_local,
                    "range_ly": r_ly,
                    "range_au": round(r_ly * 63241.077, 1),
                    "range_label": gal.get("range_label", ""),
                    "radial_3d": float(gal.get("radial_norm", 0.55)),
                    "freq_label": f"{freq_str} {rf.get('mode', '')}",
                    "arm": gal.get("arm", ""),
                    "relay_nodes": gal.get("relay_nodes", []),
                    "color": rgb_col,
                    "hex": hex_col,
                }
            )

    sol_ref = next(x for x in catalog if x["id"] == "sol-oort-star")
    ceres_ref = next(x for x in catalog if x["id"] == "ceres-foundry-7")
    psr_ref = next(x for x in catalog if x["id"] == "psr-b1937")

    for item in catalog:
        item["xyz_unit"] = az_el_to_xyz(item["az_deg"], item["local_el_deg"], 1.0)
        item["sep_sol_deg"] = angular_separation_deg(
            item["az_deg"], item["local_el_deg"], sol_ref["az_deg"], sol_ref["local_el_deg"]
        )
        item["sep_ceres_deg"] = angular_separation_deg(
            item["az_deg"], item["local_el_deg"], ceres_ref["az_deg"], ceres_ref["local_el_deg"]
        )
        item["sep_psr_deg"] = angular_separation_deg(
            item["az_deg"], item["local_el_deg"], psr_ref["az_deg"], psr_ref["local_el_deg"]
        )
    return catalog


def az_el_to_equirect_uv(az_deg: float, el_deg: float) -> tuple[float, float]:
    """
    Map `(az_deg, el_deg)` to Blender's `ShaderNodeTexEnvironment` equirectangular `(u, v)`.
      - `u = (0.25 + az_deg / 360.0) % 1.0`
      - `v = 0.5 + el_deg / 180.0` (with `v=0` at bottom `-90°` and `v=1` at top `+90°`)
    """
    u = (0.25 + (az_deg / 360.0)) % 1.0
    v = max(0.0, min(1.0, 0.5 + (el_deg / 180.0)))
    return (u, v)


def build_celestial_beacons(scene, repo_root: Path, radius: float = 420.0):
    """
    Add physical 3D celestial beacons (the distant Oort Sun star-cross at Az 212.4°,
    Ceres Foundry #7, Persephone ringed cryo-planet, Vulpecula Pulsar, and 8 glowing
    signal-bearing markers) on a `R = 420m` sky dome.
    """
    grp = create_scene_group(scene, "Celestial_Beacons")
    mesh = grp.mesh
    catalog = load_celestial_catalog(repo_root)

    for item in catalog:
        x, y, z = az_el_to_xyz(item["az_deg"], item["local_el_deg"], radius)
        mat = {"color": item["color"], "emissive": True}

        if item["id"] == "sol-oort-star":
            add_octahedron_beacon(mesh, x, y, z, 4.2, {"color": (1.0, 0.98, 0.90), "emissive": True})
            spike_len = 26.0
            add_strut(mesh, (x - spike_len, y, z), (x + spike_len, y, z), 0.32, mat)
            add_strut(mesh, (x, y - spike_len, z), (x, y + spike_len, z), 0.32, mat)
            add_strut(mesh, (x, y, z - spike_len * 0.85), (x, y, z + spike_len * 0.85), 0.32, mat)
            add_ring_torus(mesh, x, y, z, 7.5, 0.28, mat, segs=24)
        elif item["id"] == "persephone-sedna9":
            # Ringed Oort cryo-planet neighbor
            add_octahedron_beacon(mesh, x, y, z, 3.0, mat)
            add_ring_torus(mesh, x, y, z, 6.8, 0.35, mat, segs=24)
            add_ring_torus(mesh, x, y, z, 9.2, 0.20, mat, segs=24)
        elif item["id"] == "ceres-foundry-7":
            # Ceres Foundry #7 baseline anchor
            add_octahedron_beacon(mesh, x, y, z, 2.8, mat)
            add_ring_torus(mesh, x, y, z, 5.8, 0.28, mat, segs=20)
        elif item["category"] == "signal":
            add_octahedron_beacon(mesh, x, y, z, 2.2, mat)
            add_ring_torus(mesh, x, y, z, 4.8, 0.22, mat, segs=16)
        elif item["category"] == "pulsar":
            add_octahedron_beacon(mesh, x, y, z, 2.5, mat)
            add_strut(mesh, (x, y, z - 14.0), (x, y, z + 14.0), 0.25, mat)


def generate_celestial_maps(repo_root: Path, out_dir: Path | None = None) -> dict[str, Path]:
    """
    Render the high-resolution equirectangular sky maps (`celestial_sky_clean.png`,
    `celestial_sky_annotated.png`) and the `2560x1440` QHD Celestial Signal & Neighbor
    Atlas chart (`celestial_signal_chart.png`) using PySide6 `QImage`/`QPainter`,
    and sync web-ready maps to `docs/assets/plates/`.
    """
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import (
        QColor,
        QFont,
        QGuiApplication,
        QImage,
        QLinearGradient,
        QPainter,
        QPainterPath,
        QPen,
        QRadialGradient,
    )

    _app = QGuiApplication.instance() or QGuiApplication([])

    if out_dir is None:
        out_dir = repo_root / "tower_3d" / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    web_plates_dir = repo_root / "docs" / "assets" / "plates"
    web_plates_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_celestial_catalog(repo_root)

    # ── 1. Render Base 8192x4096 (8K) Equirectangular Sky (`celestial_sky_clean.png`) ──
    W, H = 8192, 4096
    clean_img = QImage(W, H, QImage.Format_RGB32)
    clean_img.fill(QColor(2, 4, 8))

    p = QPainter(clean_img)
    p.setRenderHint(QPainter.Antialiasing, True)

    # Subtle vertical deep-space gradient
    bg_grad = QLinearGradient(0, 0, 0, H)
    bg_grad.setColorAt(0.0, QColor(1, 2, 5))
    bg_grad.setColorAt(0.45, QColor(3, 6, 13))
    bg_grad.setColorAt(0.50, QColor(5, 10, 20))
    bg_grad.setColorAt(0.58, QColor(3, 6, 11))
    bg_grad.setColorAt(1.0, QColor(1, 2, 4))
    p.fillRect(0, 0, W, H, bg_grad)

    # Subtle Milky Way Galactic Band & Dust Clouds along the Galactic Plane curve
    rng = random.Random(35109)
    p.setPen(Qt.NoPen)
    for step in range(520):
        az = (step / 520.0) * 360.0
        el = galactic_to_local_el(az, 0.0) + rng.uniform(-6.0, 6.0)
        u, v = az_el_to_equirect_uv(az, el)
        px = u * W
        py = (1.0 - v) * H

        dist_sgr = min(abs(az - 18.6), 360.0 - abs(az - 18.6))
        bulge_boost = math.exp(-((dist_sgr / 42.0) ** 2))
        rad = rng.uniform(90.0, 260.0) * (1.0 + 0.45 * bulge_boost)

        grad = QRadialGradient(QPointF(px, py), rad)
        if bulge_boost > 0.35:
            c_mid = QColor(42, 34, 56, int(14 + 20 * bulge_boost))
        else:
            c_mid = QColor(16, 28, 50, rng.randint(8, 16))
        grad.setColorAt(0.0, c_mid)
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(grad)
        p.drawEllipse(QPointF(px, py), rad, rad * 0.6)

    # 18,000 Pinpoint Spectral Stars
    spectral_colors = [
        QColor(180, 212, 255),  # O/B blue-white
        QColor(228, 240, 255),  # A white-blue
        QColor(255, 252, 246),  # F white
        QColor(255, 240, 200),  # G yellow-white
        QColor(255, 208, 150),  # K amber
        QColor(255, 170, 130),  # M red giant
    ]
    for i in range(18000):
        if i < 8000:
            az_s = rng.uniform(0.0, 360.0)
            el_s = galactic_to_local_el(az_s, 0.0) + rng.gauss(0.0, 11.5)
            u, v = az_el_to_equirect_uv(az_s, el_s)
        else:
            u = rng.random()
            el_s = math.degrees(math.asin(rng.uniform(-0.98, 0.98)))
            v = 0.5 + el_s / 180.0

        px, py = u * W, (1.0 - v) * H
        col = QColor(rng.choice(spectral_colors))
        mag_roll = rng.random()
        if mag_roll < 0.015:
            r_star = rng.uniform(1.2, 1.7)
            halo = QRadialGradient(QPointF(px, py), r_star * 2.6)
            c_halo = QColor(col)
            c_halo.setAlpha(75)
            halo.setColorAt(0.0, c_halo)
            halo.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(halo)
            p.drawEllipse(QPointF(px, py), r_star * 2.6, r_star * 2.6)
            p.setBrush(QColor(255, 255, 255))
            p.drawEllipse(QPointF(px, py), r_star * 0.75, r_star * 0.75)
        elif mag_roll < 0.16:
            col.setAlpha(rng.randint(175, 240))
            p.setBrush(col)
            r_star = rng.uniform(0.75, 1.25)
            p.drawEllipse(QPointF(px, py), r_star, r_star)
        else:
            col.setAlpha(rng.randint(65, 165))
            p.setBrush(col)
            r_star = rng.uniform(0.45, 0.85)
            p.drawEllipse(QPointF(px, py), r_star, r_star)

    # ── Draw SOL at 42,100 AU (m = -3.62): Crisp Stellar Point-Source (no comet or resolved planets) ──
    sol_item = next(x for x in catalog if x["id"] == "sol-oort-star")
    u_sol, v_sol = az_el_to_equirect_uv(sol_item["az_deg"], sol_item["local_el_deg"])
    sx, sy = u_sol * W, (1.0 - v_sol) * H

    sol_glow = QRadialGradient(QPointF(sx, sy), 18.0)
    sol_glow.setColorAt(0.0, QColor(255, 255, 250, 255))
    sol_glow.setColorAt(0.18, QColor(255, 244, 210, 180))
    sol_glow.setColorAt(0.45, QColor(255, 215, 135, 55))
    sol_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.setBrush(sol_glow)
    p.drawEllipse(QPointF(sx, sy), 18.0, 18.0)
    p.setBrush(QColor(255, 255, 255))
    p.drawEllipse(QPointF(sx, sy), 2.6, 2.6)

    p.end()


    clean_path = out_dir / "celestial_sky_clean.png"
    clean_img.save(str(clean_path))

    # Save 4K web-ready JPEG to docs/assets/plates/celestial_sky_clean.jpg
    web_clean_img = clean_img.scaled(4096, 2048, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    web_clean_img.save(str(web_plates_dir / "celestial_sky_clean.jpg"), "JPG", 92)

    # ── 2. Render Annotated Equirectangular Sky (`celestial_sky_annotated.png`, 4096x2048) ──
    W, H = 4096, 2048
    annot_img = web_clean_img.copy()
    pa = QPainter(annot_img)
    pa.setRenderHint(QPainter.Antialiasing, True)

    # Subtle azimuth & elevation coordinate grid
    grid_pen = QPen(QColor(56, 234, 255, 36), 1.2, Qt.DashLine)
    pa.setPen(grid_pen)
    for el_g in (-30, 0, 30, 60):
        _, vg = az_el_to_equirect_uv(0.0, el_g)
        yg = (1.0 - vg) * H
        pa.drawLine(0, int(yg), W, int(yg))

    for az_g in range(0, 360, 30):
        ug, _ = az_el_to_equirect_uv(az_g, 0.0)
        xg = int(ug * W)
        pa.drawLine(xg, int(H * 0.12), xg, int(H * 0.88))

    # Galactic Plane curve
    gal_path = QPainterPath()
    pts_gal = []
    for step in range(361):
        az_s = float(step)
        el_s = galactic_to_local_el(az_s, 0.0)
        u_s, v_s = az_el_to_equirect_uv(az_s, el_s)
        pts_gal.append((u_s * W, (1.0 - v_s) * H))
    pts_gal.sort(key=lambda pt: pt[0])
    for idx_pt, (gx, gy) in enumerate(pts_gal):
        if idx_pt == 0:
            gal_path.moveTo(gx, gy)
        else:
            gal_path.lineTo(gx, gy)
    pa.setPen(QPen(QColor(245, 158, 11, 75), 2.0, Qt.DotLine))
    pa.setBrush(Qt.NoBrush)
    pa.drawPath(gal_path)

    # Draw Sol <-> Ceres Foundry #7 Triangulation Baseline Arc on Annotated Map (wrapping cleanly across 270° seam)
    cer_item = next(x for x in catalog if x["id"] == "ceres-foundry-7")
    u_sol2, v_sol2 = az_el_to_equirect_uv(sol_item["az_deg"], sol_item["local_el_deg"])
    u_cer2, v_cer2 = az_el_to_equirect_uv(cer_item["az_deg"], cer_item["local_el_deg"])
    y_sol2 = (1.0 - v_sol2) * H
    y_cer2 = (1.0 - v_cer2) * H
    y_seam = y_sol2 + (y_cer2 - y_sol2) * ((1.0 - u_sol2) / ((1.0 - u_sol2) + u_cer2))
    pa.setPen(QPen(QColor(255, 158, 56, 150), 1.8, Qt.DashDotLine))
    pa.drawLine(QPointF(u_sol2 * W, y_sol2), QPointF(W, y_seam))
    pa.drawLine(QPointF(0, y_seam), QPointF(u_cer2 * W, y_cer2))

    font_code = QFont("DejaVu Sans Mono", 14, QFont.Bold)
    font_sub = QFont("DejaVu Sans Mono", 10, QFont.Normal)

    label_offsets = {
        "sol-oort-star": (30, -16),
        "P-01": (24, 24),
        "P-08": (-365, -14),
        "ceres-foundry-7": (24, 18),
        "P-05": (-395, 18),
        "quarry-44k": (22, 34),
        "tartarus-buoy12": (24, -22),
        "P-04": (24, 20),
        "P-07": (24, -28),
        "sgr-a-core": (22, -24),
        "P-06": (22, 22),
        "persephone-sedna9": (26, -18),
        "ors-351-halo": (-355, -18),
    }

    for item in catalog:
        u, v = az_el_to_equirect_uv(item["az_deg"], item["local_el_deg"])
        cx, cy = u * W, (1.0 - v) * H
        qcol = QColor(item["hex"])

        pa.setPen(QPen(qcol, 2.3))
        pa.setBrush(Qt.NoBrush)
        r_ret = 24.0 if item["id"] == "sol-oort-star" else (20.0 if item["category"] == "planet" else 15.0)
        pa.drawEllipse(QPointF(cx, cy), r_ret, r_ret)
        if item["category"] == "planet":
            pa.drawEllipse(QPointF(cx, cy), r_ret * 0.65, r_ret * 0.65)
        pa.drawLine(QPointF(cx - r_ret - 7, cy), QPointF(cx - r_ret + 4, cy))
        pa.drawLine(QPointF(cx + r_ret - 4, cy), QPointF(cx + r_ret + 7, cy))
        pa.drawLine(QPointF(cx, cy - r_ret - 7), QPointF(cx, cy - r_ret + 4))
        pa.drawLine(QPointF(cx, cy + r_ret - 4), QPointF(cx, cy + r_ret + 7))

        key = item.get("slot") or item["id"]
        dx_lbl, dy_lbl = label_offsets.get(key, (-355 if u > 0.88 else 22, -14))
        lx = cx + dx_lbl
        ly = cy + dy_lbl

        pa.setFont(font_code)
        pa.setPen(qcol)
        pa.drawText(QPointF(lx, ly), f"{item['code']} [AZ {item['az_deg']:.1f}°]")
        pa.setFont(font_sub)
        pa.setPen(QColor(215, 232, 248, 225))
        pa.drawText(QPointF(lx, ly + 15), f"{item['name'][:34]} • {item['range_label']}")

    pa.end()
    annot_path = out_dir / "celestial_sky_annotated.png"
    annot_img.save(str(annot_path))
    annot_img.save(str(web_plates_dir / "celestial_sky_annotated.jpg"), "JPG", 92)

    # ── 3. Render 2560x1440 QHD Station Wall-Chart (`celestial_signal_chart.png`) ──
    CW, CH = 2560, 1440
    chart = QImage(CW, CH, QImage.Format_RGB32)
    chart.fill(QColor(6, 10, 18))

    pc = QPainter(chart)
    pc.setRenderHint(QPainter.Antialiasing, True)
    pc.setRenderHint(QPainter.SmoothPixmapTransform, True)

    pc.fillRect(0, 0, CW, 76, QColor(12, 18, 30))
    pc.setPen(QPen(QColor(45, 68, 98), 2))
    pc.drawLine(0, 76, CW, 76)

    pc.setFont(QFont("DejaVu Sans Mono", 18, QFont.Bold))
    pc.setPen(QColor(245, 158, 11))
    pc.drawText(
        28,
        34,
        "GOR-9 • OORT SECTOR 9 CELESTIAL SPHERE, CERES FOUNDRY #7 BASELINE, OORT NEIGHBORS & SIGNAL ATLAS",
    )
    pc.setFont(QFont("DejaVu Sans Mono", 11, QFont.Normal))
    pc.setPen(QColor(56, 234, 255))
    pc.drawText(
        28,
        59,
        "ORIGIN: ASTEROID 3-5-1 (42,100 AU FROM SOL) • TRIANGULATION BASELINE: CERES FOUNDRY #7 (AZ 272.0° • 1,840 AU) • PULSAR CLOCK: PSR B1937+21",
    )

    sky_rect = QRectF(28, 90, CW - 56, 890)
    pc.drawImage(sky_rect, annot_img)
    pc.setPen(QPen(QColor(56, 234, 255, 140), 2))
    pc.setBrush(Qt.NoBrush)
    pc.drawRect(sky_rect)

    pc.setFont(QFont("DejaVu Sans Mono", 11, QFont.Bold))
    for card_lbl, az_c in (
        ("N • 000° (MASTER BROADCAST DESK)", 0.0),
        ("E • 090° (ACHERON CHASM CLIFF)", 90.0),
        ("S • 180° (CATWALK AIRLOCK)", 180.0),
        ("W • 270° (CERES FOUNDRY & MASSIF)", 270.0),
    ):
        u_c, _ = az_el_to_equirect_uv(az_c, 0.0)
        cx_c = sky_rect.left() + u_c * sky_rect.width()
        cx_c = max(sky_rect.left() + 155, min(sky_rect.right() - 155, cx_c))
        pc.fillRect(QRectF(cx_c - 152, sky_rect.bottom() - 30, 304, 24), QColor(8, 14, 24, 230))
        pc.setPen(QColor(245, 158, 11))
        pc.drawText(QRectF(cx_c - 152, sky_rect.bottom() - 30, 304, 24), Qt.AlignCenter, card_lbl)

    # Bottom 16-card Celestial, Planetary Neighbor & Signal Bearing Table (4x4)
    table_top = 994
    cols = 4
    rows = 4
    card_w = (CW - 56 - (cols - 1) * 12) / cols
    card_h = (CH - table_top - 16 - (rows - 1) * 8) / rows

    featured_ids = [
        "sol-oort-star",
        "ceres-foundry-7",
        "persephone-sedna9",
        "tartarus-buoy12",
        "quarry-44k",
        "psr-b1937",
        "sgr-a-core",
        "ors-351-halo",
        "radio-corrugated",
        "buoy-n24",
        "m33-drift-buoy",
        "trojan-octal",
        "pedregal-utility",
        "kz9-omega",
        "radio-free-hektor",
        "st-jerome-slag",
    ]
    cat_by_id = {x["id"]: x for x in catalog}
    featured_items = [cat_by_id[k] for k in featured_ids if k in cat_by_id]

    for idx_item, item in enumerate(featured_items[:16]):
        r_idx = idx_item // cols
        c_idx = idx_item % cols
        bx = 28 + c_idx * (card_w + 12)
        by = table_top + r_idx * (card_h + 8)
        rect = QRectF(bx, by, card_w, card_h)

        pc.fillRect(rect, QColor(11, 17, 28))
        pc.setPen(QPen(QColor(item["hex"]), 1.8))
        pc.drawRect(rect)

        pc.setFont(QFont("DejaVu Sans Mono", 11, QFont.Bold))
        pc.setPen(QColor(item["hex"]))
        pc.drawText(QPointF(bx + 10, by + 20), f"{item['code']} — {item['name'][:34]}")

        pc.setFont(QFont("DejaVu Sans Mono", 9, QFont.Normal))
        pc.setPen(QColor(220, 232, 245))
        pc.drawText(
            QPointF(bx + 10, by + 40),
            f"AZ {item['az_deg']:05.1f}° | EL {item['local_el_deg']:+05.1f}° | {item['range_label']} | ΔCeres {item['sep_ceres_deg']:.1f}°",
        )
        pc.setPen(QColor(148, 163, 184))
        pc.drawText(QPointF(bx + 10, by + 58), f"{item['freq_label']} • {item['subtitle'][:48]}")

    pc.end()
    chart_path = out_dir / "celestial_signal_chart.png"
    chart.save(str(chart_path))
    chart.save(str(web_plates_dir / "celestial_signal_chart.jpg"), "JPG", 92)

    return {
        "clean": clean_path,
        "annotated": annot_path,
        "chart": chart_path,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    paths = generate_celestial_maps(root)
    for k, v in paths.items():
        print(f"Generated {k}: {v}")
