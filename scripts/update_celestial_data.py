#!/usr/bin/env python3
"""
Enrich `docs/data/stations.json` and `docs/data/stations_data.js` with:
  - 3D Celestial Sphere local horizon elevations (`local_el_deg`) and unit vectors (`xyz_unit`)
  - 3D Relay Node coordinates (`az_deg`, `el_deg`, `r_norm`, `role`) for all 8 stations
  - Triangulation metrics relative to Sol (`42,100 AU`), Ceres Foundry #7 (`1,840 AU`), and `PSR B1937+21`
  - `celestial_neighbors`: Oort Sector 9 visible planetary neighbors, Ceres Foundry #7, and cosmic anchors
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIONS_JSON = ROOT / "docs" / "data" / "stations.json"
STATIONS_JS = ROOT / "docs" / "data" / "stations_data.js"


def galactic_to_local_el(az_deg: float, gal_lat_deg: float) -> float:
    tilt_curve = 14.0 * math.cos(math.radians(az_deg - 205.0)) + 15.5
    el = gal_lat_deg * 0.55 + tilt_curve
    return round(max(-8.0, min(68.0, el)), 1)


def az_el_to_xyz(az_deg: float, el_deg: float, radius: float = 1.0) -> list[float]:
    az_r = math.radians(az_deg)
    el_r = math.radians(el_deg)
    cos_el = math.cos(el_r)
    x = round(radius * cos_el * math.sin(az_r), 4)
    y = round(radius * cos_el * math.cos(az_r), 4)
    z = round(radius * math.sin(el_r), 4)
    return [x, y, z]


def angular_separation_deg(az1: float, el1: float, az2: float, el2: float) -> float:
    v1 = az_el_to_xyz(az1, el1, 1.0)
    v2 = az_el_to_xyz(az2, el2, 1.0)
    dot = max(-1.0, min(1.0, v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]))
    return round(math.degrees(math.acos(dot)), 1)


def booth_window_for_az(az_deg: float) -> str:
    az = az_deg % 360.0
    if az >= 337.5 or az < 22.5:
        return "North Window • Bay 01 (Hauser MK-IV Master Desk)"
    if 22.5 <= az < 67.5:
        return "North-East Window • Bay 02 (Van Allen VA-4 Desk)"
    if 67.5 <= az < 112.5:
        return "East Chasm Window • Bay 03 (Euclid ED-9 Desk)"
    if 112.5 <= az < 157.5:
        return "South-East Window • Bay 04 (Bogey-9 Trail-Cam)"
    if 157.5 <= az < 202.5:
        return "South Airlock & Catwalk Sector"
    if 202.5 <= az < 247.5:
        return "South-West Coreward Window (Sol–Jovian Duct)"
    if 247.5 <= az < 292.5:
        return "West Window • Bay 07 (3D Spectrum & Ceres Bearing)"
    return "North-West Window • Bay 08 (Station Dossier & L4)"


def main() -> None:
    data = json.loads(STATIONS_JSON.read_text(encoding="utf-8"))
    data["schema_version"] = "2.2.0"

    sol_az, sol_el = 212.4, 22.4
    ceres_az, ceres_el, ceres_au = 272.0, 14.6, 1840.0
    psr_az, psr_el = 57.5, 24.8

    # Update station_meta with triangulation baseline info
    data["station_meta"]["triangulation_baseline"] = {
        "origin": "Asteroid 3-5-1 (GOR-9 High Basalt Shelf • Oort Sector 9)",
        "primary_star": {"id": "sol-oort-star", "name": "Sol (G2V Primary)", "az_deg": sol_az, "local_el_deg": sol_el, "distance_au": 42100.0, "apparent_mag": -3.62},
        "foundry_anchor": {"id": "ceres-foundry-7", "name": "Ceres Foundry #7 (CFS-7 Dwarf Planet Hub)", "az_deg": ceres_az, "local_el_deg": ceres_el, "distance_au": ceres_au, "apparent_mag": 0.4},
        "pulsar_clock": {"id": "psr-b1937", "name": "PSR B1937+21 (Vulpecula Metronome)", "az_deg": psr_az, "local_el_deg": psr_el, "distance_ly": 11700.0, "freq_hz": 641.928262},
    }

    relay_enrichment = {
        "radio-corrugated": [
            {"name": "Jovian Magneto-Tail Duct", "az_deg": 210.0, "el_deg": 18.8, "r_norm": 0.24, "range_label": "42,090 AU (Jovian Flux Tube)", "role": "+14 dB Magnetospheric Waveguide"},
            {"name": "O.R.S. 351 Polar Halo", "az_deg": 176.0, "el_deg": 17.0, "r_norm": 0.11, "range_label": "42.8 km (Local Halo Orbit)", "role": "Near-Field Polar Relay Transponder"},
        ],
        "buoy-n24": [
            {"name": "Cygnus Rift Waveguide", "az_deg": 72.0, "el_deg": 15.2, "r_norm": 0.34, "range_label": "185 ly (Cygnus Ionization Duct)", "role": "Cryo-Tropospheric & ISM Duct"},
            {"name": "O.R.S. 351 Polar Halo", "az_deg": 102.0, "el_deg": 16.4, "r_norm": 0.11, "range_label": "42.8 km (Local Halo Orbit)", "role": "Beverage-to-Booth Phase Feed"},
        ],
        "m33-drift-buoy": [
            {"name": "Perseus Arm Einstein Lens", "az_deg": 131.0, "el_deg": 6.4, "r_norm": 0.68, "range_label": "6,400 ly (Perseus Caustic)", "role": "+28 dB Gravitational Micro-Lens"},
            {"name": "Outer Oort Halo Gate", "az_deg": 133.2, "el_deg": 11.2, "r_norm": 0.28, "range_label": "12,400 AU (Sector 9 Rim)", "role": "21-cm H-I Phase Correlator"},
        ],
        "trojan-octal": [
            {"name": "Ceres-North Shadow Relay", "az_deg": 302.0, "el_deg": 14.2, "r_norm": 0.42, "range_label": "1,920 AU (North of CFS-7)", "role": "Perseus Gap Libration Waveguide"},
            {"name": "Quarantine Buoy 12 (Tartarus)", "az_deg": 304.2, "el_deg": 19.2, "r_norm": 0.25, "range_label": "420 AU (Customs Hold)", "role": "Null-Loop Jammer Rejection Reference"},
        ],
        "pedregal-utility": [
            {"name": "Comet C/2736-K4 Ion Tail", "az_deg": 264.0, "el_deg": 32.5, "r_norm": 0.36, "range_label": "3,700 AU (Cyanogen Coma)", "role": "+11.4 dB Es-Oort Forward-Scatter Mirror"},
        ],
        "kz9-omega": [
            {"name": "Sector 9 Coreward Trunk Duct", "az_deg": 18.6, "el_deg": 14.5, "r_norm": 0.09, "range_label": "680 AU (Meridian Approach)", "role": "Direct 41m Trunk (60 kV Squall Zone)"},
        ],
        "radio-free-hektor": [
            {"name": "Perseus Libration Waveguide", "az_deg": 318.0, "el_deg": 15.6, "r_norm": 0.52, "range_label": "940 ly (Perseus Inner Rim)", "role": "Hop-Track Duct (6440/6445/6435 kHz)"},
            {"name": "Ceres Jammer Null Node", "az_deg": 272.0, "el_deg": 14.6, "r_norm": 0.34, "range_label": "1,840 AU (Ceres Foundry #7)", "role": "Syndicate Jammer (90s Lag / Nulled -34 dB)"},
        ],
        "st-jerome-slag": [
            {"name": "Kaelen-V Crystal Spire", "az_deg": 188.2, "el_deg": 22.8, "r_norm": 0.32, "range_label": "480 ly (Vael-Karun Rim)", "role": "Piezo-Opalescent Tri-Band Resonator"},
            {"name": "O.R.S. 351 Polar Halo", "az_deg": 158.0, "el_deg": 18.0, "r_norm": 0.12, "range_label": "42.8 km (Local Halo Orbit)", "role": "Simultaneous SW + H-I + Optical Lock"},
        ],
    }

    for p in data.get("presets", []):
        gal = p.get("galactic", {})
        slot = p.get("preset_slot", "P-00")
        az = float(gal.get("azimuth_deg", 0.0))
        b_lat = float(gal.get("elevation_deg", 0.0))
        el_local = galactic_to_local_el(az, b_lat)
        if slot == "P-01":
            el_local = 17.2
        elif slot == "P-06":
            el_local = 12.8
        elif slot == "P-07":
            el_local = round(el_local + 4.2, 1)

        gal["local_el_deg"] = el_local
        gal["xyz_unit"] = az_el_to_xyz(az, el_local, 1.0)
        gal["sep_sol_deg"] = angular_separation_deg(az, el_local, sol_az, sol_el)
        gal["sep_ceres_deg"] = angular_separation_deg(az, el_local, ceres_az, ceres_el)
        gal["sep_psr_deg"] = angular_separation_deg(az, el_local, psr_az, psr_el)
        gal["booth_window"] = booth_window_for_az(az)

        # Compute law-of-cosines triangulated distance from Ceres Foundry #7 (1,840 AU)
        r_ly = float(gal.get("range_ly", 1.0))
        r_au = r_ly * 63241.077
        sep_rad = math.radians(gal["sep_ceres_deg"])
        d_ceres_au = math.sqrt(max(1.0, r_au * r_au + ceres_au * ceres_au - 2.0 * r_au * ceres_au * math.cos(sep_rad)))
        if d_ceres_au < 50000:
            d_ceres_lbl = f"{d_ceres_au:,.0f} AU"
        elif r_ly < 10000:
            d_ceres_lbl = f"{d_ceres_au / 63241.077:,.2f} ly"
        else:
            d_ceres_lbl = f"{r_ly / 1e6:.2f} Mly"

        # Parallax angle subtended by the 1,840 AU GOR-9 <-> Ceres baseline
        sin_p = (ceres_au * math.sin(sep_rad)) / max(1.0, d_ceres_au)
        parallax_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_p))))
        if parallax_deg >= 0.1:
            parallax_lbl = f"{parallax_deg:.2f}° ({parallax_deg * 60.0:.1f}')"
        elif parallax_deg * 3600.0 >= 0.01:
            parallax_lbl = f"{parallax_deg * 3600.0:.3f}\""
        else:
            parallax_lbl = f"{parallax_deg * 3.6e6:.2f} mas (Micro-Lens)"

        gal["triangulation"] = {
            "ceres_dist_label": d_ceres_lbl,
            "ceres_sep_deg": gal["sep_ceres_deg"],
            "sol_sep_deg": gal["sep_sol_deg"],
            "psr_sep_deg": gal["sep_psr_deg"],
            "baseline_parallax": parallax_lbl,
            "booth_window": gal["booth_window"],
        }

        if p["id"] in relay_enrichment:
            gal["relay_nodes"] = relay_enrichment[p["id"]]
        for rn in gal.get("relay_nodes", []):
            rn_az = float(rn.get("az_deg", az))
            rn_el = float(rn.get("el_deg", galactic_to_local_el(rn_az, 0.0)))
            rn["el_deg"] = rn_el
            rn["xyz_unit"] = az_el_to_xyz(rn_az, rn_el, 1.0)

    # Build authoritative `celestial_neighbors` catalog
    neighbors = [
        {
            "id": "ceres-foundry-7",
            "slot": "CFS-7",
            "callsign": "CFS-7 / CERES",
            "name": "Ceres Foundry #7 (Dwarf Planet Hub)",
            "subtitle": "Van Allen Switchgear HQ • Dilithium Spot Exchange • Syndicate 6440 Jammer",
            "category": "Oort Planetary Neighbor & Baseline Anchor",
            "visual_type": "dwarf_planet_foundry",
            "status_color": "amber",
            "hex": "#ff9e38",
            "az_deg": 272.0,
            "local_el_deg": 14.6,
            "gal_lat_deg": -2.8,
            "range_au": 1840.0,
            "range_ly": 0.029,
            "range_label": "1,840 AU (0.029 ly Baseline)",
            "radial_norm": 0.34,
            "apparent_mag": "+0.4",
            "apparent_size": "6.8\" Warm Amber Planetary Disk",
            "freq_khz": 10000.0,
            "freq_label": "10,000.0 kHz CFS-7 Beacon / 6,440.0 kHz Jammer",
            "arm": "Outer Foundry & Sector 9 Baseline Belt",
            "appearance_from_gor9": "Appears above the West Basalt Massif (Az 272.0°, El +14.6°) as a resolved warm amber-ochre planetary sphere (m = +0.4). At 40x telescope magnification, glowing orange sodium-slag foundry canyons and the pulsing crimson Syndicate jammer array are visible on its night hemisphere.",
            "triangulation_role": "Primary 1,840 AU Astrometric Triangulation Baseline (GOR-9 ↔ CFS-7). Paired with Sol (Az 212.4°) and PSR B1937+21 (Az 57.5°) to triangulate distances and bearings across Sector 9.",
            "lore": "Relocated industrial headquarters of Van Allen & Sons Switchgear (Foundry #7), trading floor of the Ceres Dilithium Spot Exchange (+4.2%), and site of the automated Syndicate noise-jammer on bearing 272.0° that fires on 6,440 kHz even on silent Thursdays.",
            "relay_nodes": [
                {"name": "Quarantine Buoy 12 (Tartarus)", "az_deg": 292.0, "el_deg": 16.8, "r_norm": 0.21, "range_label": "420 AU", "role": "Customs Telemetry Hop"},
            ],
        },
        {
            "id": "persephone-sedna9",
            "slot": "OORT-P1",
            "callsign": "SEDNA-IX",
            "name": "Persephone • Ringed Oort Cryo-Planet",
            "subtitle": "Detached Sector 9 Ice-Dwarf (2,380 km) with Teal Methane-Ice Rings",
            "category": "Local Oort Planetary Neighbor",
            "visual_type": "ringed_cryo_planet",
            "status_color": "cyan",
            "hex": "#3df0d9",
            "az_deg": 148.5,
            "local_el_deg": 28.4,
            "gal_lat_deg": -12.4,
            "range_au": 0.18,
            "range_ly": 0.0000028,
            "range_label": "0.18 AU (26.9M km Local)",
            "radial_norm": 0.18,
            "apparent_mag": "-1.8",
            "apparent_size": "18.2\" Disk / 44.0\" Ring System",
            "freq_khz": 22.4,
            "freq_label": "22.4 kHz Cryo-Aurora Whisper",
            "arm": "Local Oort Sector 9 Sub-Cluster",
            "appearance_from_gor9": "Our closest planetary neighbor in Sector 9! Visible to the naked eye and spectacular in the booth telescope over the South-East Acheron Chasm (Az 148.5°, El +28.4°) as a crescent teal-emerald cryo-planet encircled by double shimmering methane-ice rings.",
            "triangulation_role": "Near-Field Gravitational Shepherd & Cryo-Albedic Photometric Reference (0.18 AU).",
            "lore": "A 2,380 km detached Oort cryo-planet sharing Sector 9's gravitational shoal with Asteroid 3-5-1. Its double ring system of crystallized methane and cyanogen ice catches distant Sol's light at a 34° phase angle.",
            "relay_nodes": [
                {"name": "O.R.S. 351 Polar Halo", "az_deg": 135.0, "el_deg": 20.2, "r_norm": 0.10, "range_label": "42.8 km", "role": "Optical Limb & Aurora Monitor"},
            ],
        },
        {
            "id": "tartarus-buoy12",
            "slot": "OORT-P2",
            "callsign": "BUOY-12 / TARTARUS",
            "name": "Tartarus Binary Plutoid & Quarantine Buoy 12",
            "subtitle": "Tidally Locked Oort Double-Dwarf • Sector 9 Customs Impound Anchorage",
            "category": "Local Oort Planetary Neighbor",
            "visual_type": "binary_plutoid",
            "status_color": "purple",
            "hex": "#b8a3fa",
            "az_deg": 304.2,
            "local_el_deg": 19.2,
            "gal_lat_deg": 4.6,
            "range_au": 420.0,
            "range_ly": 0.0066,
            "range_label": "420 AU (0.0066 ly NW)",
            "radial_norm": 0.25,
            "apparent_mag": "+1.6",
            "apparent_size": "4.2\" + 1.8\" Binary Dwarf Pair",
            "freq_khz": 4125.0,
            "freq_label": "4,125.0 kHz USB Customs Hold",
            "arm": "Local Oort Sector 9 (NW Corridor)",
            "appearance_from_gor9": "Resolves in the telescope (Az 304.2°, El +19.2°) as a pale slate-violet binary dwarf planet pair revolving around their common barycenter, with the amber beacon of Quarantine Buoy 12 stationed at the L1 Lagrange point between them.",
            "triangulation_role": "NW Mid-Field Ranging Waypoint (420 AU) along the Ceres–Trojan L4 corridor.",
            "lore": "Sector 9 Outer Customs & Quarantine Anchorage. GOR-9's monthly Dilithium pellet and vacuum-tube tender is currently impounded at Quarantine Buoy 12 after customs inspectors misfiled replacement 811A oscillator tubes as 'fermented brine tubers'.",
            "relay_nodes": [
                {"name": "O.R.S. 351 Polar Halo", "az_deg": 295.0, "el_deg": 17.5, "r_norm": 0.11, "range_label": "42.8 km", "role": "Customs Manifest Link"},
            ],
        },
        {
            "id": "quarry-44k",
            "slot": "OORT-Q44",
            "callsign": "QUARRY-44K",
            "name": "Asteroid Silicate Quarry 44-K",
            "subtitle": "Open-Pit Silicate & Grade-B Dilithium Dragline Mining World",
            "category": "Local Oort Industrial Neighbor",
            "visual_type": "mining_asteroid",
            "status_color": "amber",
            "hex": "#f5bf52",
            "az_deg": 288.5,
            "local_el_deg": 9.4,
            "gal_lat_deg": 1.2,
            "range_au": 890.0,
            "range_ly": 0.014,
            "range_label": "890 AU (West Mining Belt)",
            "radial_norm": 0.29,
            "apparent_mag": "+2.8",
            "apparent_size": "2.4\" Floodlit Basalt Crag",
            "freq_khz": 5180.0,
            "freq_label": "5,180.0 kHz Dragline Telemetry",
            "arm": "Local Oort Sector 9 (West Mining Belt)",
            "appearance_from_gor9": "Seen low in the WNW sky (Az 288.5°, El +9.4°) as a jagged carbonaceous asteroid crag illuminated by amber floodlights and a shimmering silicate dust plume kicked up by its cable dragline.",
            "triangulation_role": "Intermediate Ranging Beacon (890 AU) on the GOR-9 ↔ Ceres Foundry #7 baseline.",
            "lore": "Open-pit silicate and Grade-B Dilithium mining operation. A dragline cable slowdown at Pit 44-K triggered a +4.2% surge in Grade-B Dilithium pellets on the Ceres Spot Exchange.",
            "relay_nodes": [
                {"name": "Quarantine Buoy 12 (Tartarus)", "az_deg": 296.0, "el_deg": 14.0, "r_norm": 0.22, "range_label": "420 AU", "role": "Barge Telemetry Relay"},
            ],
        },
        {
            "id": "comet-c2736-k4",
            "slot": "COMET-K4",
            "callsign": "C/2736-K4",
            "name": "Comet C/2736-K4 Ion Tail (Es-Oort)",
            "subtitle": "Active Oort Macro-Comet & Sporadic-Oort Plasma Mirror (+11.4 dB)",
            "category": "Cometary Plasma Reflector",
            "visual_type": "active_comet",
            "status_color": "green",
            "hex": "#40fac7",
            "az_deg": 264.0,
            "local_el_deg": 32.5,
            "gal_lat_deg": 11.5,
            "range_au": 3700.0,
            "range_ly": 0.058,
            "range_label": "3,700 AU (0.058 ly West Shoal)",
            "radial_norm": 0.36,
            "apparent_mag": "-2.4",
            "apparent_size": "6.5° Cyanogen Coma & Double Tail",
            "freq_khz": 6969.5,
            "freq_label": "Es-Oort Forward-Scatter (+11.4 dB)",
            "arm": "Local Oort Shell (West Ice Shoal)",
            "appearance_from_gor9": "Dominates the upper western sky (Az 264.0°, El +32.5°) with a luminous cyan-green cyanogen coma and a 6.5°-long striated ion tail streaming away from Sol.",
            "triangulation_role": "Ionized Cometary Scatter Mirror enabling 3-Watt QRP reception across 3,700 AU.",
            "lore": "Outgassing macro-comet in the West Oort Shoal whose ionized sublimation plume acts as a giant natural radio mirror (+11.4 dB forward-scatter gain) for Capt. Rafa's 3-Watt biscuit-tin weather broadcasts.",
            "relay_nodes": [],
        },
        {
            "id": "ors-351-halo",
            "slot": "ORS-351",
            "callsign": "O.R.S. 351",
            "name": "O.R.S. 351 Polar Halo Relay Satellite",
            "subtitle": "Near-Field Orbital Transponder & CAM-SAT09 Optical Downlook Platform",
            "category": "Local Orbital Relay",
            "visual_type": "orbital_satellite",
            "status_color": "cyan",
            "hex": "#59ebff",
            "az_deg": 125.6,
            "local_el_deg": 16.4,
            "gal_lat_deg": -8.0,
            "range_au": 0.000286,
            "range_ly": 4.5e-9,
            "range_label": "42.8 km (Polar Halo Station)",
            "radial_norm": 0.12,
            "apparent_mag": "-2.4",
            "apparent_size": "Resolved Brass Bus & Solar Wings",
            "freq_khz": 14285.7,
            "freq_label": "14,285.7 kHz / Halo Optical Trunk",
            "arm": "Asteroid 3-5-1 Near-Space Halo",
            "appearance_from_gor9": "Hovers off the South-East Acheron Chasm cliff (Az 125.6°, El +16.4°) as a bright cyan/amber artificial star; telescope zoom reveals its 8-sided brass bus, parabolic dish, copper solar wings, and navigation strobes.",
            "triangulation_role": "Local Relay Hop #1 and remote camera station looking directly back at the GOR-9 lighthouse tower.",
            "lore": "Station-keeping orbital relay satellite positioned off the South Rotational Pole of Asteroid 3-5-1, coupling inner-system waveguides to the 4-Ring Marzelvane array.",
            "relay_nodes": [],
        },
        {
            "id": "sol-oort-star",
            "slot": "SOL-00",
            "callsign": "SOL (G2V)",
            "name": "Sol • The Distant Sun (42,100 AU)",
            "subtitle": "Coreward G2V Primary Star • Apparent Mag -3.62 • 0.665 ly",
            "category": "Primary Cosmic & Astrometric Anchor",
            "visual_type": "g2v_star",
            "status_color": "amber",
            "hex": "#ffedba",
            "az_deg": 212.4,
            "local_el_deg": 22.4,
            "gal_lat_deg": -4.2,
            "range_au": 42100.0,
            "range_ly": 0.665,
            "range_label": "42,100 AU (0.665 ly)",
            "radial_norm": 0.48,
            "apparent_mag": "-3.62",
            "apparent_size": "0.045\" Razor-Sharp Point-Star",
            "freq_khz": 2800000.0,
            "freq_label": "10.7cm Solar Flux: 148.2 SFU",
            "arm": "Orion–Cygnus Spur (Heliocentric Core)",
            "appearance_from_gor9": "At 42,100 AU (0.665 ly), the Sun is an unresolved 0.045-arcsecond point-source—yet at apparent magnitude -3.62 (8x brighter than Sirius), it blazes in the SSW sky with crisp 6-point optical diffraction spikes and silver-gold corona glare.",
            "triangulation_role": "Heliocentric Coordinate Origin (42,100 AU) & Primary Coreward Bearing Reference (Az 212.4°).",
            "lore": "Casts high-contrast directional silver-gold light across Asteroid 3-5-1's columnar basalt cliffs and anchors the Sol–Jovian Magneto-Tail propagation corridor.",
            "relay_nodes": [
                {"name": "Jovian Magneto-Tail Duct", "az_deg": 210.0, "el_deg": 18.8, "r_norm": 0.24, "range_label": "42,095 AU", "role": "Heliospheric Waveguide"},
                {"name": "O.R.S. 351 Polar Halo", "az_deg": 176.0, "el_deg": 17.0, "r_norm": 0.11, "range_label": "42.8 km", "role": "Local Halo Downlink"},
            ],
        },
        {
            "id": "psr-b1937",
            "slot": "PSR-01",
            "callsign": "PSR B1937+21",
            "name": "Vulpecula Millisecond Pulsar",
            "subtitle": "Master Barycentric Station Clock Metronome • 641.928262 Hz",
            "category": "Primary Cosmic & Astrometric Anchor",
            "visual_type": "millisecond_pulsar",
            "status_color": "cyan",
            "hex": "#38f2ff",
            "az_deg": 57.5,
            "local_el_deg": 24.8,
            "gal_lat_deg": -0.3,
            "range_au": 7.4e8,
            "range_ly": 11700.0,
            "range_label": "11,700 ly (3.59 kpc)",
            "radial_norm": 0.84,
            "apparent_mag": "641.928 Hz Pulse",
            "apparent_size": "1.557806 ms Relativistic Jet",
            "freq_khz": 1420405.0,
            "freq_label": "641.928262 Hz Barycentric Lock",
            "arm": "Orion–Cygnus / Sagittarius Edge",
            "appearance_from_gor9": "Appears in the ENE sky (Az 57.5°, El +24.8°) as a cyan-white bipolar relativistic jet beacon flashing in phase-locked 641.928262 Hz timing sync.",
            "triangulation_role": "Master Galactic Coordinated Time (GCT) Clock & Phase-Difference-of-Arrival Reference.",
            "lore": "Because Asteroid 3-5-1's tumbling rotation cannot serve as a civil clock, all GOR-9 consoles lock to the 1.557806 ms barycentric pulse train of PSR B1937+21.",
            "relay_nodes": [],
        },
        {
            "id": "sgr-a-core",
            "slot": "SGR-A*",
            "callsign": "SGR A* CORE",
            "name": "Sagittarius Galactic Center",
            "subtitle": "Milky Way Central Bulge & Great Dust Rift (l = 0.0°, b = 0.0°)",
            "category": "Primary Cosmic & Astrometric Anchor",
            "visual_type": "galactic_core",
            "status_color": "amber",
            "hex": "#ffbd61",
            "az_deg": 18.6,
            "local_el_deg": 18.0,
            "gal_lat_deg": 0.0,
            "range_au": 1.67e9,
            "range_ly": 26480.0,
            "range_label": "26,480 ly (8.12 kpc)",
            "radial_norm": 0.90,
            "apparent_mag": "Galactic Bulge",
            "apparent_size": "24° Golden Bulge & Dark Rift",
            "freq_khz": 1420405.75,
            "freq_label": "Galactic Zero-Meridian (l = 0°)",
            "arm": "Galactic Nucleus (Sagittarius Core)",
            "appearance_from_gor9": "Hangs directly outside the North Master Broadcast Desk window (Az 18.6°, El +18.0°) in permanent hard-vacuum night, completely unattenuated by inner-system zodiacal dust.",
            "triangulation_role": "Galactic Longitude 000.0° Zero-Meridian & Coreward Trunk Bearing.",
            "lore": "Defines the Galactic coordinate frame (R_gal = 8.12 kpc) and the Sagittarius–Coreward trunk corridor through Meridian Relay KZ9-OMEGA.",
            "relay_nodes": [
                {"name": "Meridian Plateau Relay (KZ9-OMEGA)", "az_deg": 18.6, "el_deg": 12.8, "r_norm": 0.16, "range_label": "1,420 AU", "role": "Coreward Trunk Hop #1"},
            ],
        },
    ]

    for nb in neighbors:
        az = float(nb["az_deg"])
        el = float(nb["local_el_deg"])
        nb["xyz_unit"] = az_el_to_xyz(az, el, 1.0)
        nb["sep_sol_deg"] = angular_separation_deg(az, el, sol_az, sol_el)
        nb["sep_ceres_deg"] = angular_separation_deg(az, el, ceres_az, ceres_el)
        nb["sep_psr_deg"] = angular_separation_deg(az, el, psr_az, psr_el)
        nb["booth_window"] = booth_window_for_az(az)
        for rn in nb.get("relay_nodes", []):
            rn["xyz_unit"] = az_el_to_xyz(float(rn["az_deg"]), float(rn["el_deg"]), 1.0)

    data["celestial_neighbors"] = neighbors

    json_text = json.dumps(data, indent=2, ensure_ascii=False)
    STATIONS_JSON.write_text(json_text + "\n", encoding="utf-8")
    STATIONS_JS.write_text(f"window.GOR9_STATIONS_DATA = {json_text};\n", encoding="utf-8")
    print(f"Updated {STATIONS_JSON.name} and {STATIONS_JS.name}: {len(data['presets'])} stations + {len(neighbors)} celestial neighbors/anchors.")


if __name__ == "__main__":
    main()
