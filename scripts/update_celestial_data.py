#!/usr/bin/env python3
"""
Enrich `docs/data/stations.json` and `docs/data/stations_data.js` with true Oort-scale astrometry:
  - True Solar System 5-arcminute core (`4.8994"/AU` from 42,100 AU): Callisto (`SW4-CORR`),
    Ceres (`CFS-7`), 624 Hektor / Trojan L4 (`E08-OCTAL`, `RFH-HOP`), and Titan (`TM-N24/B`)
    placed on their real Keplerian orbits around `Sol` (`Az 212.40°, El +22.40°`).
  - `solar_system_orbits`: 10 true Keplerian planetary & dwarf-planet orbits (`Earth` 1.0 AU
    out to `90377 Sedna` 506 AU / 937 AU aphelion) with velocity vectors and angular radii.
  - `gor9_orbit`: Asteroid 3-5-1's own perturbed long-period cometary infall trajectory
    (`Q = 42,500 AU -> q = 1.22 AU`, `P = 3.10 Myr`, `-42.6 m/s`, `1.39 Myr` to frost-line coma).
  - `oort_relay_ring`: All 12 polar trunk relay stations (`GOR-1` .. `GOR-12`) forming the
    ~84,000 AU (`1.33 ly`) Barycentric Flux-Duct Perimeter & Euclidean VLBI Interferometer.
  - `pulsar_time` & `sweep_roundup_log`: Non-terrestrial `PSR B1937+21` Pulsar Barycentric Time
    (`Epoch 254.310 • Watch 0`, Beats -> 6 Watches = 1 Cycle -> 10 Cycles = 1 Sweep).
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIONS_JSON = ROOT / "docs" / "data" / "stations.json"
STATIONS_JS = ROOT / "docs" / "data" / "stations_data.js"

ARCSEC_PER_AU = 206264.806 / 42100.0  # 4.8994015 arcseconds per AU at 42,100 AU
AU_PER_LY = 63241.077
SOL_AZ = 212.4000
SOL_EL = 22.4000
SOL_DIST_AU = 42100.0
ECLIPTIC_TILT_DEG = 58.0  # Viewing angle onto Solar System ecliptic from GOR-9 (88.4° S Oort Sector 9)
ECLIPTIC_PA_DEG = -24.0   # Position angle of ecliptic major axis on local sky


def galactic_to_local_el(az_deg: float, gal_lat_deg: float) -> float:
    tilt_curve = 14.0 * math.cos(math.radians(az_deg - 205.0)) + 15.5
    el = gal_lat_deg * 0.55 + tilt_curve
    return round(max(-8.0, min(68.0, el)), 2)


def az_el_to_xyz(az_deg: float, el_deg: float, radius: float = 1.0) -> list[float]:
    az_r = math.radians(az_deg)
    el_r = math.radians(el_deg)
    cos_el = math.cos(el_r)
    x = round(radius * cos_el * math.sin(az_r), 5)
    y = round(radius * cos_el * math.cos(az_r), 5)
    z = round(radius * math.sin(el_r), 5)
    return [x, y, z]


def xyz_to_az_el(x: float, y: float, z: float) -> tuple[float, float, float]:
    r = math.sqrt(x * x + y * y + z * z)
    if r < 1e-9:
        return 0.0, 0.0, 0.0
    az = math.degrees(math.atan2(x, y)) % 360.0
    el = math.degrees(math.asin(max(-1.0, min(1.0, z / r))))
    return round(az, 4), round(el, 4), round(r, 2)


def angular_separation_deg(az1: float, el1: float, az2: float, el2: float) -> float:
    v1 = az_el_to_xyz(az1, el1, 1.0)
    v2 = az_el_to_xyz(az2, el2, 1.0)
    dot = max(-1.0, min(1.0, v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]))
    return round(math.degrees(math.acos(dot)), 4)


def booth_window_for_az(az_deg: float) -> str:
    az = az_deg % 360.0
    if az >= 337.5 or az < 22.5:
        return "North Window • Bay 01 (Master Show Cockpit)"
    if 22.5 <= az < 67.5:
        return "North-East Window • Bay 02 (Van Allen VA-4 Bus)"
    if 67.5 <= az < 112.5:
        return "East Chasm Window • Bay 03 (Euclid ED-9 Engine)"
    if 112.5 <= az < 157.5:
        return "South-East Window • Bay 04 (Bogey-9 Sentinel)"
    if 157.5 <= az < 202.5:
        return "South Catwalk & Pulsar Reference Sector"
    if 202.5 <= az < 247.5:
        return "South-West Coreward Window (Sol 5' Coronagraph Lock)"
    if 247.5 <= az < 292.5:
        return "West Massif Window (Oort West Shoal & Quarry)"
    return "North-West Window (Hauser MK-IV & Tartarus Hold)"


def kepler_sky_offset_arcsec(
    a_au: float,
    e: float,
    inc_deg: float,
    node_deg: float,
    arg_peri_deg: float,
    true_anom_deg: float,
) -> tuple[float, float, float, float]:
    """
    Project a heliocentric Keplerian position (AU) onto GOR-9's sky plane around Sol,
    returning (d_az_arcsec, d_el_arcsec, r_helio_au, radial_depth_au).
    """
    nu = math.radians(true_anom_deg)
    r_au = (a_au * (1.0 - e * e)) / (1.0 + e * math.cos(nu))
    u = math.radians(arg_peri_deg) + nu
    om = math.radians(node_deg)
    inc = math.radians(inc_deg)

    # Heliocentric ecliptic Cartesian (AU)
    xh = r_au * (math.cos(om) * math.cos(u) - math.sin(om) * math.sin(u) * math.cos(inc))
    yh = r_au * (math.sin(om) * math.cos(u) + math.cos(om) * math.sin(u) * math.cos(inc))
    zh = r_au * (math.sin(u) * math.sin(inc))

    # Tilt ecliptic by ECLIPTIC_TILT_DEG relative to line of sight and rotate by ECLIPTIC_PA_DEG
    tilt = math.radians(ECLIPTIC_TILT_DEG)
    pa = math.radians(ECLIPTIC_PA_DEG)
    sx0 = xh
    sy0 = yh * math.sin(tilt) + zh * math.cos(tilt)
    depth = yh * math.cos(tilt) - zh * math.sin(tilt)

    sx = sx0 * math.cos(pa) - sy0 * math.sin(pa)
    sy = sx0 * math.sin(pa) + sy0 * math.cos(pa)

    return (
        round(sx * ARCSEC_PER_AU, 3),
        round(sy * ARCSEC_PER_AU, 3),
        round(r_au, 4),
        round(depth, 3),
    )


def sky_pos_from_sol_offset(d_az_arcsec: float, d_el_arcsec: float) -> tuple[float, float]:
    cos_el = math.cos(math.radians(SOL_EL))
    az = (SOL_AZ + (d_az_arcsec / 3600.0) / max(0.2, cos_el)) % 360.0
    el = SOL_EL + (d_el_arcsec / 3600.0)
    return round(az, 5), round(el, 5)


def main() -> None:
    data = json.loads(STATIONS_JSON.read_text(encoding="utf-8"))
    data["schema_version"] = "3.0.0"

    # ── 1. Pulsar Barycentric Time (`PST`) Specification ──────────────────────
    data["pulsar_time"] = {
        "standard_code": "PST",
        "standard_name": "Pulsar Barycentric Time (Vulpecula Millisecond Standard)",
        "reference_pulsar": "PSR B1937+21 (J1939+2134)",
        "pulse_freq_hz": 641.928262,
        "pulse_period_ms": 1.55780645,
        "zero_epoch_origin": "Epoch 000.000 = 1982.86 CE (Arecibo First Millisecond Lock)",
        "units": {
            "beat_pulses": 1000,
            "beat_seconds": 1.557806,
            "watch_beats": 10000,
            "watch_pulses": 10000000,
            "watch_hours_si": 4.3272,
            "cycle_watches": 6,
            "cycle_pulses": 60000000,
            "cycle_hours_si": 25.9634,
            "sweep_cycles": 10,
            "sweep_pulses": 600000000,
            "sweep_days_si": 10.8181,
            "epoch_sweeps": 100,
            "epoch_cycles": 1000,
            "epoch_years_si": 2.9618,
        },
        "current_broadcast": {
            "epoch": "254.310",
            "previous_sweep": "254.300",
            "watch": 0,
            "watch_name": "Watch 0 • Quiet DX & Sweep Roundup (12 kW Reactor Step-Down)",
            "sign_on_beat": "0000",
            "display_stamp": "EPOCH 254.310 • W0 • B0000 PST",
        },
    }

    # ── 2. Asteroid 3-5-1 (`GOR-9`) Cometary Infall Orbit ─────────────────────
    data["gor9_orbit"] = {
        "body": "Asteroid 3-5-1 (Oort Sector 9 Polar Shelf)",
        "orbit_class": "Perturbed Long-Period Retrograde Oort Comet (Pre-Active Crust)",
        "current_r_au": 42100.0,
        "aphelion_q_max_au": 42500.0,
        "perihelion_q_min_au": 1.22,
        "semi_major_axis_au": 21250.61,
        "eccentricity": 0.9999426,
        "inclination_deg": 104.2,
        "unperturbed_circular_period_yr": 8638000,
        "perturbed_cometary_period_yr": 3098000,
        "infall_half_period_yr": 1549000,
        "perturbation_event": "Grazing M-dwarf stellar tide + Galactic disk vertical torque (~155 kyr ago)",
        "radial_velocity_ms": -42.6,
        "tangential_velocity_ms": 11.4,
        "local_escape_velocity_ms": 205.2,
        "saturn_frost_line_au": 9.58,
        "coma_ignition_eta_yr": 1392000,
        "coma_ignition_eta_sweeps": 470100,
        "actuarial_note": "Van Allen & Sons Switchgear lease valid until 10.0 AU water-ice sublimation threshold (ETA 1.39 Myr).",
    }

    # ── 3. True Solar System Keplerian Orbits (`4.8994"/AU` around Sol) ───────
    orbits_raw = [
        {
            "id": "orbit-earth",
            "name": "Earth (Terra)",
            "short": "TERRA",
            "a_au": 1.000,
            "e": 0.0167,
            "inc_deg": 0.00,
            "node_deg": 0.0,
            "arg_peri_deg": 102.9,
            "true_anom_deg": 42.0,
            "period_yr": 1.000,
            "v_kms": 29.78,
            "mag": "+18.2",
            "hex": "#60a5fa",
            "tier": "inner",
            "hosted_stations": [],
            "note": "1.00 AU reference ring (±4.90\" from Sol); deep inside coronagraph inner zone.",
        },
        {
            "id": "orbit-mars",
            "name": "Mars",
            "short": "MARS",
            "a_au": 1.524,
            "e": 0.0934,
            "inc_deg": 1.85,
            "node_deg": 49.6,
            "arg_peri_deg": 286.5,
            "true_anom_deg": 195.0,
            "period_yr": 1.881,
            "v_kms": 24.07,
            "mag": "+20.6",
            "hex": "#f87171",
            "tier": "inner",
            "hosted_stations": [],
            "note": "Inner boundary of Main Asteroid Belt (±7.47\" from Sol).",
        },
        {
            "id": "orbit-ceres",
            "name": "1 Ceres (Foundry #7 Hub)",
            "short": "CERES • CFS-7",
            "a_au": 2.767,
            "e": 0.0758,
            "inc_deg": 10.59,
            "node_deg": 80.3,
            "arg_peri_deg": 73.6,
            "true_anom_deg": 298.0,
            "period_yr": 4.603,
            "v_kms": 17.90,
            "mag": "+23.8",
            "hex": "#f59e0b",
            "tier": "inner",
            "hosted_stations": ["CFS-7 (10.0 MHz Beacon / 6,440 kHz Jammer)"],
            "note": "Van Allen & Sons Switchgear HQ, Dilithium Exchange & automated 6,440 kHz Syndicate Jammer aimed at 624 Hektor.",
        },
        {
            "id": "orbit-jupiter",
            "name": "Jupiter + Callisto & Trojan L4/L5",
            "short": "JUPITER / L4",
            "a_au": 5.204,
            "e": 0.0489,
            "inc_deg": 1.31,
            "node_deg": 100.5,
            "arg_peri_deg": 273.9,
            "true_anom_deg": 134.0,
            "period_yr": 11.862,
            "v_kms": 13.07,
            "mag": "+15.4",
            "hex": "#ffae2b",
            "tier": "gas",
            "hosted_stations": ["SW4-CORR (Callisto)", "E08-OCTAL (624 Hektor L4)", "RFH-HOP (624 Hektor L4)"],
            "note": "Dominant ±25.5\" magnetospheric duct anchor; 624 Hektor leads Jupiter by +60° at L4.",
        },
        {
            "id": "orbit-saturn",
            "name": "Saturn + Titan (Kraken Mare)",
            "short": "SATURN / TITAN",
            "a_au": 9.583,
            "e": 0.0565,
            "inc_deg": 2.49,
            "node_deg": 113.7,
            "arg_peri_deg": 339.4,
            "true_anom_deg": 318.0,
            "period_yr": 29.457,
            "v_kms": 9.68,
            "mag": "+17.1",
            "hex": "#38e8ff",
            "tier": "gas",
            "hosted_stations": ["TM-N24/B (Titan Buoy N-24 • 3,890 kHz)"],
            "note": "±47.0\" water-ice sublimation boundary; hosts Hydrographic Buoy N-24 on Titan (15.945-day TSol tide).",
        },
        {
            "id": "orbit-uranus",
            "name": "Uranus",
            "short": "URANUS",
            "a_au": 19.191,
            "e": 0.0472,
            "inc_deg": 0.77,
            "node_deg": 74.0,
            "arg_peri_deg": 96.9,
            "true_anom_deg": 72.0,
            "period_yr": 84.02,
            "v_kms": 6.80,
            "mag": "+20.1",
            "hex": "#67e8f9",
            "tier": "kuiper",
            "hosted_stations": [],
            "note": "Outer ice-giant waveguide marker (±1.57' from Sol).",
        },
        {
            "id": "orbit-neptune",
            "name": "Neptune",
            "short": "NEPTUNE",
            "a_au": 30.070,
            "e": 0.0086,
            "inc_deg": 1.77,
            "node_deg": 131.8,
            "arg_peri_deg": 273.2,
            "true_anom_deg": 228.0,
            "period_yr": 164.8,
            "v_kms": 5.43,
            "mag": "+21.0",
            "hex": "#3b82f6",
            "tier": "kuiper",
            "hosted_stations": [],
            "note": "Classical Solar System outer rim (±2.46' = 4.9' diameter around Sol).",
        },
        {
            "id": "orbit-pluto",
            "name": "134340 Pluto–Charon",
            "short": "PLUTO",
            "a_au": 39.482,
            "e": 0.2488,
            "inc_deg": 17.16,
            "node_deg": 110.3,
            "arg_peri_deg": 113.8,
            "true_anom_deg": 64.0,
            "period_yr": 247.9,
            "v_kms": 4.67,
            "mag": "+26.8",
            "hex": "#a78bfa",
            "tier": "kuiper",
            "hosted_stations": [],
            "note": "3:2 Neptunian resonance dwarf planet; inclined 17.2° (±3.22' from Sol).",
        },
        {
            "id": "orbit-eris",
            "name": "136199 Eris (Scattered Disk)",
            "short": "ERIS",
            "a_au": 67.864,
            "e": 0.4361,
            "inc_deg": 44.04,
            "node_deg": 36.0,
            "arg_peri_deg": 151.6,
            "true_anom_deg": 168.0,
            "period_yr": 559.1,
            "v_kms": 3.43,
            "mag": "+27.4",
            "hex": "#c084fc",
            "tier": "kuiper",
            "hosted_stations": [],
            "note": "Steep 44.0° scattered-disk orbit extending to 97.5 AU (8.0' from Sol).",
        },
        {
            "id": "orbit-sedna",
            "name": "90377 Sedna (Inner Oort / Hills Gate)",
            "short": "SEDNA • H1",
            "a_au": 506.0,
            "e": 0.8496,
            "inc_deg": 11.93,
            "node_deg": 144.5,
            "arg_peri_deg": 311.3,
            "true_anom_deg": 145.0,
            "period_yr": 11380.0,
            "v_kms": 1.32,
            "mag": "+29.1",
            "hex": "#4ade80",
            "tier": "hills",
            "hosted_stations": ["SEDNA-H1 (Inner Hills Trunk Repeater)"],
            "note": "Extreme detached sednoid (q = 76 AU, Q = 937 AU); aphelion reaches 1.28° from Sol!",
        },
    ]

    for orb in orbits_raw:
        d_az, d_el, r_now, depth = kepler_sky_offset_arcsec(
            orb["a_au"],
            orb["e"],
            orb["inc_deg"],
            orb["node_deg"],
            orb["arg_peri_deg"],
            orb["true_anom_deg"],
        )
        az_now, el_now = sky_pos_from_sol_offset(d_az, d_el)
        orb["angular_radius_arcsec"] = round(orb["a_au"] * ARCSEC_PER_AU, 2)
        orb["aphelion_arcsec"] = round(orb["a_au"] * (1.0 + orb["e"]) * ARCSEC_PER_AU, 2)
        orb["current_offset_arcsec"] = [d_az, d_el]
        orb["current_r_helio_au"] = r_now
        orb["az_deg"] = az_now
        orb["local_el_deg"] = el_now
        orb["period_sweeps"] = round(orb["period_yr"] * 365.25 / 10.8181, 1)

    data["solar_system_orbits"] = orbits_raw

    # Compute Trojan L4 (+60° ahead of Jupiter, i = 18.18° for 624 Hektor) & L5 (-60° behind)
    jup = next(o for o in orbits_raw if o["id"] == "orbit-jupiter")
    hektor_daz, hektor_del, hektor_r, hektor_depth = kepler_sky_offset_arcsec(
        5.257, 0.023, 18.18, 342.8, 178.9, (jup["true_anom_deg"] + 60.0) % 360.0
    )
    hektor_az, hektor_el = sky_pos_from_sol_offset(hektor_daz, hektor_del)

    l5_daz, l5_del, _, _ = kepler_sky_offset_arcsec(
        5.204, 0.048, 4.2, 100.5, 273.9, (jup["true_anom_deg"] - 60.0) % 360.0
    )
    l5_az, l5_el = sky_pos_from_sol_offset(l5_daz, l5_del)

    ceres_orb = next(o for o in orbits_raw if o["id"] == "orbit-ceres")
    sat_orb = next(o for o in orbits_raw if o["id"] == "orbit-saturn")
    sedna_orb = next(o for o in orbits_raw if o["id"] == "orbit-sedna")

    data["trojan_swarms"] = {
        "L4_hektor": {
            "name": "624 Hektor • Jupiter L4 Trojan Swarm (+60° Greek Camp)",
            "d_az_arcsec": hektor_daz,
            "d_el_arcsec": hektor_del,
            "az_deg": hektor_az,
            "local_el_deg": hektor_el,
            "r_helio_au": hektor_r,
        },
        "L5_patroclus": {
            "name": "617 Patroclus • Jupiter L5 Trojan Swarm (-60° Trojan Camp)",
            "d_az_arcsec": l5_daz,
            "d_el_arcsec": l5_del,
            "az_deg": l5_az,
            "local_el_deg": l5_el,
        },
    }

    # ── 4. 12-Sector Oort Perimeter Trunk Relay Ring (`GOR-1` .. `GOR-12`) ───
    # Sol sits at (x_s, y_s, z_s) relative to GOR-9 at (0, 0, 0):
    sol_vec = az_el_to_xyz(SOL_AZ, SOL_EL, SOL_DIST_AU)
    oort_relays = []
    # Golden-spiral / dodecahedral distribution around Sol at ~41,000 - 44,500 AU
    relay_specs = [
        ("GOR-1", "Sector 1 • Boreal Apex Trunk", 41800, 12.0, 62.0),
        ("GOR-2", "Sector 2 • Cygnus Frontier Trunk", 43200, 74.0, 28.0),
        ("GOR-3", "Sector 3 • Antipodal VLBI Partner", 41800, (SOL_AZ + 180.0) % 360.0, -SOL_EL),
        ("GOR-4", "Sector 4 • Perseus Gate Trunk", 44100, 138.0, 34.0),
        ("GOR-5", "Sector 5 • Orion Spur Trunk", 40900, 198.0, 44.0),
        ("GOR-6", "Sector 6 • Vela Deep Trunk", 43600, 256.0, 22.0),
        ("GOR-7", "Sector 7 • Centaurus Trunk", 42400, 314.0, 31.0),
        ("GOR-8", "Sector 8 • West Hand-Off Peer", 41900, 25.0, -24.0),
        ("GOR-9", "Sector 9 • Acheron Polar Shelf (US)", 42100, None, None),
        ("GOR-10", "Sector 10 • East Hand-Off Peer", 42700, 88.0, -32.0),
        ("GOR-11", "Sector 11 • Sculptor South Trunk", 43900, 154.0, -48.0),
        ("GOR-12", "Sector 12 • Sagittarius South Trunk", 41200, 295.0, -38.0),
    ]
    for code, title, r_sol_au, helio_lon, helio_lat in relay_specs:
        if code == "GOR-9":
            oort_relays.append({
                "id": code.lower(),
                "callsign": code,
                "name": title,
                "is_self": True,
                "helio_r_au": SOL_DIST_AU,
                "dist_from_gor9_au": 0.0,
                "az_deg": 0.0,
                "local_el_deg": -90.0,
                "local_xyz_au": [0.0, 0.0, 0.0],
                "carrier_khz": 14285.7,
                "role": "Active Broadcast & Sector 9 Flux-Duct Bias Hub (50 kW / 12 kW W0)",
            })
            continue
        if code == "GOR-3":
            # Antipodal across Sol from GOR-9! Sol is at +sol_vec from GOR-9, so GOR-3 is at ~2 * sol_vec
            rx = sol_vec[0] * 1.992 + 420.0
            ry = sol_vec[1] * 1.992 - 310.0
            rz = sol_vec[2] * 1.992 + 280.0
        else:
            hv = az_el_to_xyz(helio_lon, helio_lat, r_sol_au)
            rx = sol_vec[0] + hv[0]
            ry = sol_vec[1] + hv[1]
            rz = sol_vec[2] + hv[2]
        az_r, el_r, dist_r = xyz_to_az_el(rx, ry, rz)
        oort_relays.append({
            "id": code.lower(),
            "callsign": code,
            "name": title,
            "is_self": False,
            "helio_r_au": r_sol_au,
            "dist_from_gor9_au": round(dist_r, 0),
            "az_deg": round(az_r, 2),
            "local_el_deg": round(el_r, 2),
            "local_xyz_au": [round(rx, 1), round(ry, 1), round(rz, 1)],
            "carrier_khz": round(14000.0 + int(code.split("-")[1]) * 31.7, 1),
            "role": (
                "1.33-ly Antipodal VLBI Euclidean Interferometer Partner"
                if code == "GOR-3"
                else ("Adjacent Lateral Ring Trunk Peer" if code in ("GOR-8", "GOR-10") else "Outer Oort 50 kW Flux-Duct Perimeter Node")
            ),
        })
    data["oort_relay_ring"] = oort_relays

    # ── 5. Update `station_meta` & Reconcile All 8 Intercepted Stations ──────
    baseline_az, baseline_el, baseline_au = 18.6, 12.8, 1420.0  # Meridian KZ9-OMEGA 1,420 AU local Oort baseline
    psr_az, psr_el = 57.5, 24.8

    data["station_meta"]["broadcast_time_gct"] = "EPOCH 254.310 • W0"
    data["station_meta"]["clock_standard"] = "PSR B1937+21 Pulsar Barycentric Time (641.928262 Hz • 6 Watches/Cycle • 10 Cycles/Sweep)"
    data["station_meta"]["triangulation_baseline"] = {
        "origin": "Asteroid 3-5-1 (GOR-9 Polar Shelf • 42,100 AU • Infall -42.6 m/s)",
        "primary_star": {"id": "sol-oort-star", "name": "Sol & 5' Solar System Core", "az_deg": SOL_AZ, "local_el_deg": SOL_EL, "distance_au": SOL_DIST_AU, "apparent_mag": -3.62},
        "foundry_anchor": {"id": "kz9-omega", "name": "Meridian Trunk KZ9-OMEGA (Local Oort Baseline)", "az_deg": baseline_az, "local_el_deg": baseline_el, "distance_au": baseline_au, "apparent_mag": 16.4},
        "vlbi_partner": {"id": "gor-3", "name": "GOR-3 Antipodal Oort Relay (1.33 ly VLBI)", "az_deg": SOL_AZ, "local_el_deg": SOL_EL, "distance_au": 83900.0},
        "pulsar_clock": {"id": "psr-b1937", "name": "PSR B1937+21 (Vulpecula Metronome)", "az_deg": psr_az, "local_el_deg": psr_el, "distance_ly": 11700.0, "freq_hz": 641.928262},
    }

    # Reconcile Solar System vs Oort vs Interstellar station coordinates!
    station_coord_overrides = {
        "radio-corrugated": {
            "body": "Callisto Dome-4 (Jupiter Orbit • 5.20 AU from Sol)",
            "distance": "42,096.8 AU (0.666 ly • ±25.5\" off Sol via Jovian Flux-Duct)",
            "local_clock": "J-Dome Synodic 0.84 • Epoch 254.310 W0",
            "sector": "Solar System 5' Core • Jovian Magnetosphere (5.20 AU)",
            "arm": "Heliocentric Inner Core (4.90\"/AU)",
            "az_deg": jup["az_deg"],
            "el_deg": jup["local_el_deg"],
            "range_au": 42096.8,
            "range_ly": round(42096.8 / AU_PER_LY, 5),
            "range_label": "42,097 AU (±25.5\" off Sol)",
            "orbit_id": "orbit-jupiter",
            "sol_offset_arcsec": jup["current_offset_arcsec"],
            "relay_path": "Jovian Magneto-Tail → Sedna H1 → GOR-9 Marzelvane Biased Duct",
        },
        "buoy-n24": {
            "body": "Titan • Kraken Mare (Saturn Orbit • 9.58 AU from Sol)",
            "distance": "42,106.4 AU (0.666 ly • ±47.0\" off Sol via Kronian Flux-Duct)",
            "local_clock": "TSol 14.82 (15.945d Saturnian Tide) • Epoch 254.310 W0",
            "sector": "Solar System 5' Core • Saturnian System (9.58 AU)",
            "arm": "Heliocentric Inner Core (4.90\"/AU)",
            "az_deg": sat_orb["az_deg"],
            "el_deg": sat_orb["local_el_deg"],
            "range_au": 42106.4,
            "range_ly": round(42106.4 / AU_PER_LY, 5),
            "range_label": "42,106 AU (±47.0\" off Sol)",
            "orbit_id": "orbit-saturn",
            "sol_offset_arcsec": sat_orb["current_offset_arcsec"],
            "relay_path": "Kronian Flux-Tube → Heliopause Gate → GOR-9 80m Beverage/Ring Duct",
        },
        "trojan-octal": {
            "body": "624 Hektor • Jupiter Trojan L4 (+60° Ahead of Jupiter • 5.26 AU)",
            "distance": "42,102.1 AU (0.666 ly • ±25.8\" off Sol via L4 Libration Duct)",
            "local_clock": "Hektor Spin 6.92h • Epoch 254.310 W0",
            "sector": "Solar System 5' Core • Jupiter L4 Greek Camp (5.26 AU)",
            "arm": "Heliocentric Inner Core (4.90\"/AU)",
            "az_deg": hektor_az,
            "el_deg": hektor_el,
            "range_au": 42102.1,
            "range_ly": round(42102.1 / AU_PER_LY, 5),
            "range_label": "42,102 AU (Jupiter L4 • ±25.8\")",
            "orbit_id": "orbit-jupiter",
            "sol_offset_arcsec": [hektor_daz, hektor_del],
            "relay_path": "Jupiter L4 Libration Filament → Tartarus Null-Loop → GOR-9",
        },
        "radio-free-hektor": {
            "body": "624 Hektor Ridge • Jupiter Trojan L4 (+60° • 5.26 AU)",
            "distance": "42,102.1 AU (0.666 ly • ±25.8\" off Sol; Jammed from Ceres 2.77 AU)",
            "local_clock": "Crawler X-74 Shift • Epoch 254.310 W0",
            "sector": "Solar System 5' Core • Jupiter L4 Greek Camp (5.26 AU)",
            "arm": "Heliocentric Inner Core (4.90\"/AU)",
            "az_deg": round(hektor_az + 0.0008, 5),
            "el_deg": round(hektor_el + 0.0005, 5),
            "range_au": 42102.1,
            "range_ly": round(42102.1 / AU_PER_LY, 5),
            "range_label": "42,102 AU (Jupiter L4 • ±25.8\")",
            "orbit_id": "orbit-jupiter",
            "sol_offset_arcsec": [round(hektor_daz + 1.8, 2), round(hektor_del + 1.4, 2)],
            "relay_path": "L4 Hop-Track Filament (Ceres 2.77 AU Jammer Nulled -34 dB) → GOR-9",
        },
        "pedregal-utility": {
            "range_au": 3700.0,
            "range_ly": round(3700.0 / AU_PER_LY, 5),
            "range_label": "3,700 AU (Oort West Shoal)",
            "local_clock": "MV Boca del Río Watch 0 • Epoch 254.310",
        },
        "kz9-omega": {
            "range_au": 1420.0,
            "range_ly": round(1420.0 / AU_PER_LY, 5),
            "range_label": "1,420 AU (Sector 9 Feeder)",
            "local_clock": "Meridian Fault Watch 0 • Epoch 254.310",
        },
        "st-jerome-slag": {
            "range_au": 1140.0 * AU_PER_LY,
            "range_ly": 1140.0,
            "range_label": "1,140 ly (Kaelen-V Filament)",
            "local_clock": "Vael Harmonic Canon • Epoch 254.310 W0",
        },
        "m33-drift-buoy": {
            "range_au": 2.73e6 * AU_PER_LY,
            "range_ly": 2730000.0,
            "range_label": "2.73 Mly (M-33 H-I Caustic)",
            "local_clock": "Survey-Era ROM Clock • Epoch 254.310 W0",
        },
    }

    relay_enrichment = {
        "radio-corrugated": [
            {"name": "Sedna Hills Gate (SEDNA-H1)", "az_deg": sedna_orb["az_deg"], "el_deg": sedna_orb["local_el_deg"], "range_au": 41320.0, "r_norm": 0.44, "range_label": "780 AU from Sol (Sedna Gate)", "role": "+14 dB Heliospheric Flux-Duct Entry"},
            {"name": "O.R.S. 351 Polar Halo", "az_deg": 176.0, "el_deg": 17.0, "range_au": 0.000286, "r_norm": 0.08, "range_label": "42.8 km (Polar Halo)", "role": "Near-Field Phase Downlink"},
        ],
        "buoy-n24": [
            {"name": "Sedna Hills Gate (SEDNA-H1)", "az_deg": sedna_orb["az_deg"], "el_deg": sedna_orb["local_el_deg"], "range_au": 41320.0, "r_norm": 0.44, "range_label": "780 AU from Sol", "role": "Kronian-to-Oort Standing-Wave Duct"},
            {"name": "Acheron 2km Beverage Wire", "az_deg": 212.0, "el_deg": 12.0, "range_au": 0.000013, "r_norm": 0.05, "range_label": "2.0 km Basalt Rim", "role": "Low-Noise Cryo Receive Feed"},
        ],
        "trojan-octal": [
            {"name": "Quarantine Buoy 12 (Tartarus)", "az_deg": 304.2, "el_deg": 19.2, "range_au": 420.0, "r_norm": 0.24, "range_label": "420 AU (Sector 9 NW)", "role": "Ceres Jammer Phase-Null Reference"},
        ],
        "radio-free-hektor": [
            {"name": "Ceres 6440 Jammer (2.77 AU)", "az_deg": ceres_orb["az_deg"], "el_deg": ceres_orb["local_el_deg"], "range_au": 42098.4, "r_norm": 0.48, "range_label": "2.77 AU off Sol (±13.6\")", "role": "Syndicate Jammer (90s Lag / Nulled -34 dB)"},
            {"name": "Quarantine Buoy 12 (Tartarus)", "az_deg": 304.2, "el_deg": 19.2, "range_au": 420.0, "r_norm": 0.24, "range_label": "420 AU", "role": "Orthogonal Beverage Null Reference"},
        ],
        "pedregal-utility": [
            {"name": "Comet C/2736-K4 Cyanogen Tail", "az_deg": 264.0, "el_deg": 32.5, "range_au": 3700.0, "r_norm": 0.34, "range_label": "3,700 AU (West Shoal)", "role": "+11.4 dB Es-Oort Forward-Scatter Mirror"},
        ],
        "kz9-omega": [
            {"name": "Sector 9 Meridian Duct", "az_deg": 18.6, "el_deg": 12.8, "range_au": 710.0, "r_norm": 0.18, "range_label": "710 AU Mid-Span", "role": "41m Trunk (60 kV Silicate Squall)"},
        ],
        "st-jerome-slag": [
            {"name": "GOR-11 South Trunk Relay", "az_deg": 182.0, "el_deg": 19.4, "range_au": 48200.0, "r_norm": 0.52, "range_label": "48,200 AU (Oort Sector 11)", "role": "Inter-Arm Barycentric Filament Lock"},
        ],
        "m33-drift-buoy": [
            {"name": "Perseus Arm Einstein Micro-Lens", "az_deg": 131.0, "el_deg": 6.4, "range_au": 6400.0 * AU_PER_LY, "r_norm": 0.78, "range_label": "6,400 ly (Perseus Caustic)", "role": "+28 dB Gravitational Lens + H-I Filament"},
            {"name": "GOR-4 Perseus Gate Relay", "az_deg": 134.5, "el_deg": 11.2, "range_au": 46500.0, "r_norm": 0.50, "range_label": "46,500 AU (Oort Sector 4)", "role": "21-cm Cryo-Maser Correlator"},
        ],
    }

    for p in data.get("presets", []):
        gal = p.get("galactic", {})
        ov = station_coord_overrides.get(p["id"], {})
        if "body" in ov:
            p["origin"]["body"] = ov["body"]
        if "distance" in ov:
            p["origin"]["distance"] = ov["distance"]
        if "local_clock" in ov:
            p["origin"]["local_clock"] = ov["local_clock"]
        if "sector" in ov:
            gal["sector"] = ov["sector"]
        if "arm" in ov:
            gal["arm"] = ov["arm"]
        if "relay_path" in ov:
            p["rf"]["relay_path"] = ov["relay_path"]

        az = float(ov.get("az_deg", gal.get("azimuth_deg", 0.0)))
        b_lat = float(gal.get("elevation_deg", 0.0))
        el_local = float(ov.get("el_deg", galactic_to_local_el(az, b_lat)))

        r_au = float(ov.get("range_au", float(gal.get("range_ly", 1.0)) * AU_PER_LY))
        r_ly = float(ov.get("range_ly", r_au / AU_PER_LY))

        # Logarithmic radial norm for 3D display: log10(max(1, r_au)) mapped cleanly [0.08 .. 0.96]
        log_au = math.log10(max(1.0, r_au))
        r_norm = round(min(0.96, max(0.10, 0.075 * log_au + 0.08)), 3)

        gal["azimuth_deg"] = az
        gal["local_el_deg"] = el_local
        gal["range_au"] = round(r_au, 2)
        gal["range_ly"] = r_ly
        gal["range_label"] = ov.get("range_label", gal.get("range_label", ""))
        gal["radial_norm"] = r_norm
        gal["orbit_id"] = ov.get("orbit_id")
        gal["sol_offset_arcsec"] = ov.get("sol_offset_arcsec")
        gal["xyz_unit"] = az_el_to_xyz(az, el_local, 1.0)
        gal["sep_sol_deg"] = angular_separation_deg(az, el_local, SOL_AZ, SOL_EL)
        gal["sep_ceres_deg"] = angular_separation_deg(az, el_local, baseline_az, baseline_el)
        gal["sep_psr_deg"] = angular_separation_deg(az, el_local, psr_az, psr_el)
        gal["booth_window"] = booth_window_for_az(az)

        # Law-of-cosines triangulation against 1,420 AU Meridian Baseline
        sep_rad = math.radians(gal["sep_ceres_deg"])
        d_base_au = math.sqrt(max(1.0, r_au * r_au + baseline_au * baseline_au - 2.0 * r_au * baseline_au * math.cos(sep_rad)))
        if d_base_au < 90000:
            d_base_lbl = f"{d_base_au:,.0f} AU"
        elif r_ly < 10000:
            d_base_lbl = f"{d_base_au / AU_PER_LY:,.1f} ly"
        else:
            d_base_lbl = f"{r_ly / 1e6:.2f} Mly"

        sin_p = (baseline_au * math.sin(sep_rad)) / max(1.0, d_base_au)
        parallax_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_p))))
        if parallax_deg >= 0.1:
            parallax_lbl = f"{parallax_deg:.2f}°"
        elif parallax_deg * 3600.0 >= 0.01:
            parallax_lbl = f"{parallax_deg * 3600.0:.2f}\""
        else:
            parallax_lbl = f"{parallax_deg * 3.6e6:.2f} mas (VLBI)"

        gal["triangulation"] = {
            "ceres_dist_label": d_base_lbl,
            "ceres_sep_deg": round(gal["sep_ceres_deg"], 2),
            "sol_sep_deg": round(gal["sep_sol_deg"], 4),
            "psr_sep_deg": round(gal["sep_psr_deg"], 2),
            "baseline_parallax": parallax_lbl,
            "booth_window": gal["booth_window"],
        }

        if p["id"] in relay_enrichment:
            gal["relay_nodes"] = relay_enrichment[p["id"]]
        for rn in gal.get("relay_nodes", []):
            rn_az = float(rn.get("az_deg", az))
            rn_el = float(rn.get("el_deg", el_local))
            rn["el_deg"] = rn_el
            rn["xyz_unit"] = az_el_to_xyz(rn_az, rn_el, 1.0)

    # ── 6. Realistic Unresolved Celestial & Relay Catalog (`celestial_neighbors`) ──
    neighbors = [
        {
            "id": "sol-oort-star",
            "slot": "SOL-00",
            "callsign": "SOL (G2V CORE)",
            "name": "Sol & 5-Arcminute Solar System Core",
            "subtitle": "G2V Primary Star (m = -3.62 • 42,100 AU) + 10 Nested Keplerian Orbits (4.90\"/AU)",
            "category": "Heliocentric Origin & Coronagraph Target",
            "visual_type": "g2v_star",
            "status_color": "amber",
            "hex": "#ffedba",
            "az_deg": SOL_AZ,
            "local_el_deg": SOL_EL,
            "gal_lat_deg": -4.2,
            "range_au": SOL_DIST_AU,
            "range_ly": round(SOL_DIST_AU / AU_PER_LY, 5),
            "range_label": "42,100 AU (0.666 ly)",
            "radial_norm": 0.44,
            "apparent_mag": "-3.62",
            "apparent_size": "0.046\" Point-Star (5.0' Planetary Core)",
            "orbit_id": "orbit-earth",
            "freq_khz": 14285.7,
            "freq_label": "10.7cm Flux: 148.2 SFU • Heliospheric Trunk",
            "arm": "Heliocentric Core (Orion–Cygnus Spur)",
            "appearance_from_gor9": "At 42,100 AU, the Sun is a razor-sharp 0.046\" point-star blazing at magnitude -3.62. Engaging the 2000× Solar Coronagraph masks Sol's glare and reveals the hairline Keplerian ellipses of Earth (±4.9\"), Ceres (±13.6\"), Jupiter & L4 Trojans (±25.5\"), and Saturn (±47.0\").",
            "triangulation_role": "Heliocentric Coordinate Origin; target of Asteroid 3-5-1's -42.6 m/s cometary plunge (ETA 1.39 Myr).",
            "lore": "All classical planets and inner colonies lie packed within 2.5 arcminutes of Sol, linked live to GOR-9 via Marzelvane-biased heliospheric flux-ducts.",
            "relay_nodes": [
                {"name": "Sedna Hills Gate (SEDNA-H1)", "az_deg": sedna_orb["az_deg"], "el_deg": sedna_orb["local_el_deg"], "range_au": 41320.0, "r_norm": 0.42, "range_label": "780 AU off Sol", "role": "Inner-Oort Flux-Duct Mouth"},
            ],
        },
        {
            "id": "ceres-foundry-7",
            "slot": "CFS-7",
            "callsign": "1 CERES / CFS-7",
            "name": "Ceres Foundry #7 (Main Asteroid Belt • 2.77 AU)",
            "subtitle": "Van Allen Switchgear HQ • Dilithium Spot Exchange • Syndicate 6440 Jammer",
            "category": "Solar System Dwarf Planet (Coronagraph Core)",
            "visual_type": "point_body",
            "status_color": "amber",
            "hex": "#f59e0b",
            "az_deg": ceres_orb["az_deg"],
            "local_el_deg": ceres_orb["local_el_deg"],
            "gal_lat_deg": -4.2,
            "range_au": 42098.4,
            "range_ly": round(42098.4 / AU_PER_LY, 5),
            "range_label": "2.77 AU off Sol (±13.6\" • 42,098 AU)",
            "radial_norm": 0.44,
            "apparent_mag": "+23.8",
            "apparent_size": "Unresolved Point (±13.6\" Orbit, i = 10.6°)",
            "orbit_id": "orbit-ceres",
            "sol_offset_arcsec": ceres_orb["current_offset_arcsec"],
            "freq_khz": 10000.0,
            "freq_label": "10,000.0 kHz CFS-7 Std / 6,440.0 kHz Jammer",
            "arm": "Solar System Main Belt (2.77 AU)",
            "appearance_from_gor9": "Completely hidden in Sol's glare on wide views; under 2000× Coronagraph lock, Ceres tracks along a 10.6°-inclined hairline ellipse ±13.6 arcseconds from the occulted Sun at 17.9 km/s.",
            "triangulation_role": "Inner-Belt Industrial Hub; radiates the automated 6,440 kHz noise-jammer outward toward 624 Hektor (Jupiter L4).",
            "lore": "Headquarters of Van Allen & Sons Switchgear (Foundry #7) and the Ceres Grade-B Dilithium Exchange (+4.2% this Sweep).",
            "relay_nodes": [
                {"name": "Sedna Hills Gate (SEDNA-H1)", "az_deg": sedna_orb["az_deg"], "el_deg": sedna_orb["local_el_deg"], "range_au": 41320.0, "r_norm": 0.42, "range_label": "780 AU off Sol", "role": "Heliospheric Trunk Hop"},
            ],
        },
        {
            "id": "sedna-hills-relay",
            "slot": "SEDNA-H1",
            "callsign": "90377 SEDNA / H1",
            "name": "Sedna Inner-Hills Trunk Gate (76–937 AU)",
            "subtitle": "Detached Sednoid Stepping-Stone Relay • 11,380-Year Eccentric Loop",
            "category": "Hills Cloud & Sednoid Trunk Node",
            "visual_type": "point_body",
            "status_color": "green",
            "hex": "#4ade80",
            "az_deg": sedna_orb["az_deg"],
            "local_el_deg": sedna_orb["local_el_deg"],
            "gal_lat_deg": -4.8,
            "range_au": 41320.0,
            "range_ly": round(41320.0 / AU_PER_LY, 5),
            "range_label": "780 AU off Sol (1.28° Aphelion Loop)",
            "radial_norm": 0.43,
            "apparent_mag": "+29.1",
            "apparent_size": "Unresolved Point (1.28° Eccentric Orbit)",
            "orbit_id": "orbit-sedna",
            "sol_offset_arcsec": sedna_orb["current_offset_arcsec"],
            "freq_khz": 14285.7,
            "freq_label": "14,285.7 kHz Heliospheric Mouth Repeater",
            "arm": "Inner Hills Cloud (506 AU Semi-Major)",
            "appearance_from_gor9": "Point-source tracking along a dramatic 1.28°-wide eccentric ellipse bridging the 5' Kuiper core out into the Hills Cloud.",
            "triangulation_role": "Primary impedance-matching repeater coupling the Solar System magnetotail into Sector 9's Marzelvane flux-duct.",
            "lore": "Uncrewed isotope-powered Marzelvane collar anchored on 90377 Sedna, funneling low-wattage inner-planet HF traffic across the 41,000 AU gap to GOR-9.",
            "relay_nodes": [],
        },
        {
            "id": "tartarus-buoy12",
            "slot": "BUOY-12",
            "callsign": "TARTARUS / Q-12",
            "name": "Tartarus Plutoid & Quarantine Buoy 12",
            "subtitle": "Local Sector 9 Customs Impound Anchorage (420 AU NW)",
            "category": "Local Oort Sector 9 Neighbor",
            "visual_type": "point_body",
            "status_color": "purple",
            "hex": "#b8a3fa",
            "az_deg": 304.2,
            "local_el_deg": 19.2,
            "gal_lat_deg": 4.6,
            "range_au": 420.0,
            "range_ly": round(420.0 / AU_PER_LY, 5),
            "range_label": "420 AU (Sector 9 Customs Hold)",
            "radial_norm": 0.27,
            "apparent_mag": "+15.2",
            "apparent_size": "0.008\" Unresolved Point + L1 Strobe",
            "freq_khz": 4125.0,
            "freq_label": "4,125.0 kHz USB Customs Manifest",
            "arm": "Oort Sector 9 (NW Approach)",
            "appearance_from_gor9": "Faint +15.2 mag point of light at Az 304.2°, El +19.2°; phase-interferometry separates the binary plutoid's 0.008\" barycenter wobble.",
            "triangulation_role": "Near-sector phase reference used to null out the Ceres 6,440 kHz Syndicate jammer.",
            "lore": "Sector 9 customs hold where GOR-9's replacement 811A oscillator tubes remain impounded as 'fermented brine tubers'.",
            "relay_nodes": [],
        },
        {
            "id": "quarry-44k",
            "slot": "QRY-44K",
            "callsign": "QUARRY-44K",
            "name": "Silicate & Dilithium Quarry 44-K",
            "subtitle": "Oort Sector 9 Dragline Mining Asteroid (890 AU WNW)",
            "category": "Local Oort Sector 9 Neighbor",
            "visual_type": "point_body",
            "status_color": "amber",
            "hex": "#f5bf52",
            "az_deg": 288.5,
            "local_el_deg": 9.4,
            "gal_lat_deg": 1.2,
            "range_au": 890.0,
            "range_ly": round(890.0 / AU_PER_LY, 5),
            "range_label": "890 AU (Sector 9 West Crag)",
            "radial_norm": 0.30,
            "apparent_mag": "+17.4",
            "apparent_size": "Unresolved Point (5,180 kHz Carrier)",
            "freq_khz": 5180.0,
            "freq_label": "5,180.0 kHz Dragline Load Telemetry",
            "arm": "Oort Sector 9 (West Shoal)",
            "appearance_from_gor9": "Stellar pinpoint low over the West Basalt Massif (Az 288.5°, El +9.4°); sodium floodlight modulation detectable photometrically during Watch 1–3 shifts.",
            "triangulation_role": "890 AU west-corridor telemetry node.",
            "lore": "Open-pit silicate and Grade-B Dilithium quarry whose dragline cable slowdown pushed pellet spot prices up +4.2% this Sweep.",
            "relay_nodes": [],
        },
        {
            "id": "gor-8-trunk",
            "slot": "GOR-08",
            "callsign": "RELAY GOR-8",
            "name": "Sister Outpost GOR-8 (Oort Sector 8 Trunk)",
            "subtitle": "50 kW Lateral Oort Perimeter Relay Peer (31,400 AU)",
            "category": "Oort 12-Station Relay Ring",
            "visual_type": "relay_peer",
            "status_color": "cyan",
            "hex": "#38bdf8",
            "az_deg": next(r["az_deg"] for r in oort_relays if r["callsign"] == "GOR-8"),
            "local_el_deg": max(6.5, abs(next(r["local_el_deg"] for r in oort_relays if r["callsign"] == "GOR-8"))),
            "gal_lat_deg": -8.4,
            "range_au": next(r["dist_from_gor9_au"] for r in oort_relays if r["callsign"] == "GOR-8"),
            "range_ly": round(next(r["dist_from_gor9_au"] for r in oort_relays if r["callsign"] == "GOR-8") / AU_PER_LY, 3),
            "range_label": f"{next(r['dist_from_gor9_au'] for r in oort_relays if r['callsign'] == 'GOR-8'):,.0f} AU (Oort Ring Peer)",
            "radial_norm": 0.42,
            "apparent_mag": "RF Beacon",
            "apparent_size": "Point Source • 14,253.6 kHz DRM-9",
            "freq_khz": 14253.6,
            "freq_label": "14,253.6 kHz Lateral Ring Trunk",
            "arm": "Outer Oort 12-Relay Perimeter Shell",
            "appearance_from_gor9": "Optically invisible dark basalt spire across the Oort shell; blazes at S9+25 dB on the 20m lateral ring waveguide.",
            "triangulation_role": "Port-side neighbor in the 12-station Oort Relay Ring (`GOR-1..12`), handing off lateral store-and-forward mail packets.",
            "lore": "Identical 86.5m 4-ring Marzelvane tower anchored in Sector 8; shares Watch 0 pulsar clock calibration and VLBI fringe sync with GOR-9 and GOR-10.",
            "relay_nodes": [],
        },
        {
            "id": "ors-351-halo",
            "slot": "ORS-351",
            "callsign": "O.R.S. 351",
            "name": "O.R.S. 351 Polar Halo Transponder",
            "subtitle": "Station-Keeping Orbital Relay & Remote Kiwis/SDR (42.8 km)",
            "category": "Near-Field Station Hardware",
            "visual_type": "orbital_satellite",
            "status_color": "cyan",
            "hex": "#59ebff",
            "az_deg": 125.6,
            "local_el_deg": 16.4,
            "gal_lat_deg": -8.0,
            "range_au": 0.000286,
            "range_ly": 4.5e-9,
            "range_label": "42.8 km (Polar Halo Station)",
            "radial_norm": 0.10,
            "apparent_mag": "-2.4",
            "apparent_size": "m = -2.4 Artificial Point Strobe",
            "freq_khz": 14285.7,
            "freq_label": "14,285.7 kHz / Halo Quiet SDR",
            "arm": "Asteroid 3-5-1 Near-Space Halo",
            "appearance_from_gor9": "Steady magnitude -2.4 artificial star poised 16.4° above the South-East Acheron Chasm cliff.",
            "triangulation_role": "Provides quiet-zone remote SDR reception 42.8 km clear of Reactor #2 switching hash, plus CAM-SAT09 optical downlook.",
            "lore": "Station-keeping polar relay satellite locked off Asteroid 3-5-1's 88.4° S rotational pole.",
            "relay_nodes": [],
        },
        {
            "id": "psr-b1937",
            "slot": "PSR-01",
            "callsign": "PSR B1937+21",
            "name": "Vulpecula Millisecond Pulsar (Master Clock)",
            "subtitle": "641.928262 Hz Barycentric Metronome • 11,700 ly",
            "category": "Cosmic Clock & Astrometric Anchor",
            "visual_type": "millisecond_pulsar",
            "status_color": "cyan",
            "hex": "#38f2ff",
            "az_deg": psr_az,
            "local_el_deg": psr_el,
            "gal_lat_deg": -0.3,
            "range_au": 11700.0 * AU_PER_LY,
            "range_ly": 11700.0,
            "range_label": "11,700 ly (3.59 kpc)",
            "radial_norm": 0.80,
            "apparent_mag": "641.928 Hz RF",
            "apparent_size": "Point Radio/Optical Tick (1.5578 ms)",
            "freq_khz": 1420405.0,
            "freq_label": "641.928262 Hz PST Master Lock",
            "arm": "Orion–Sagittarius Interface",
            "appearance_from_gor9": "Unresolved point-source in Vulpecula (Az 057.5°, El +24.8°) whose 641.928262 Hz pulse train disciplines every oscillator at Outpost Nine.",
            "triangulation_role": "Defines Pulsar Barycentric Time (`1 Beat = 1,000 pulses = 1.5578s`; `1 Watch = 10^7 pulses`; `1 Sweep = 6×10^8 pulses`).",
            "lore": "Discovered at Arecibo in 1982 (`Epoch 000.000`); replaces planetary days, weeks, and years across the entire Oort Relay Ring.",
            "relay_nodes": [],
        },
        {
            "id": "sgr-a-core",
            "slot": "SGR-A*",
            "callsign": "SGR A* (l = 0°)",
            "name": "Sagittarius Galactic Center",
            "subtitle": "Galactic Zero-Meridian Origin • 26,480 ly (8.12 kpc)",
            "category": "Cosmic Clock & Astrometric Anchor",
            "visual_type": "galactic_core",
            "status_color": "amber",
            "hex": "#ffbd61",
            "az_deg": 18.6,
            "local_el_deg": 18.0,
            "gal_lat_deg": 0.0,
            "range_au": 26480.0 * AU_PER_LY,
            "range_ly": 26480.0,
            "range_label": "26,480 ly (8.12 kpc)",
            "radial_norm": 0.86,
            "apparent_mag": "Compact RF Core",
            "apparent_size": "Point Radio Source in Starry Bulge",
            "freq_khz": 1420405.75,
            "freq_label": "Galactic Zero-Meridian (l = 0.0°)",
            "arm": "Galactic Nucleus",
            "appearance_from_gor9": "Positioned outside the North Cockpit window (Az 018.6°, El +18.0°) amidst the dense stellar dust lanes of the Sagittarius Milky Way.",
            "triangulation_role": "Defines Galactic Longitude 000.0° and the vertical Galactic Tide vector currently nudging Asteroid 3-5-1 toward perihelion.",
            "lore": "Inertial directional anchor for the 12-Sector Oort Perimeter Ring.",
            "relay_nodes": [],
        },
    ]

    for nb in neighbors:
        az = float(nb["az_deg"])
        el = float(nb["local_el_deg"])
        nb["xyz_unit"] = az_el_to_xyz(az, el, 1.0)
        nb["sep_sol_deg"] = angular_separation_deg(az, el, SOL_AZ, SOL_EL)
        nb["sep_ceres_deg"] = angular_separation_deg(az, el, baseline_az, baseline_el)
        nb["sep_psr_deg"] = angular_separation_deg(az, el, psr_az, psr_el)
        nb["booth_window"] = booth_window_for_az(az)
        for rn in nb.get("relay_nodes", []):
            rn["xyz_unit"] = az_el_to_xyz(float(rn["az_deg"]), float(rn["el_deg"]), 1.0)

    data["celestial_neighbors"] = neighbors

    # ── 7. Alphabetical Sweep `.300 -> .310` Traffic & DX Roll-Call ───────────
    data["sweep_roundup_log"] = [
        {
            "seq": 1,
            "territory": "ACHERON HALO",
            "target_id": "ors-351-halo",
            "zoom": 1,
            "freq": "14,285.7 kHz",
            "sinpo": "5-5-5-5-5",
            "summary": "O.R.S. 351 polar transponder nominal at 42.8 km; Trail-Cam TRL-01 logged 140g non-Keplerian cylinder snap-turn.",
        },
        {
            "seq": 2,
            "territory": "CALLISTO DOME-4",
            "target_id": "radio-corrugated",
            "zoom": 2000,
            "freq": "11,410.0 kHz AM",
            "sinpo": "4-4-3-4-4",
            "summary": "Unlicensed 'Radio Corrugated' (+25.5\" off Sol, 5.20 AU) peaked S9+18 dB via Jovian flux-duct during live dipole blowtorch braze.",
        },
        {
            "seq": 3,
            "territory": "CERES BELT",
            "target_id": "ceres-foundry-7",
            "zoom": 2000,
            "freq": "10,000 / 6,440 kHz",
            "sinpo": "5-2-4-4-3",
            "summary": "Foundry #7 (±13.6\" off Sol, 2.77 AU): Grade-B Dilithium +4.2%; Syndicate 6,440 kHz jammer fired on empty channel Cycle .306.",
        },
        {
            "seq": 4,
            "territory": "COMET K4 SHOAL",
            "target_id": "pedregal-utility",
            "zoom": 6,
            "freq": "6,969.5 kHz USB",
            "sinpo": "3-4-3-3-3",
            "summary": "3-Watt 'Pirate Utility' XE9-PED/U on MV Boca del Río (3,700 AU) forward-scattered +11.4 dB off Comet K4's cyanogen tail.",
        },
        {
            "seq": 5,
            "territory": "HEKTOR L4 (CIPHER)",
            "target_id": "trojan-octal",
            "zoom": 2000,
            "freq": "6,440.0 kHz OCT",
            "sinpo": "4-3-4-4-3",
            "summary": "Jupiter L4 (+60° lead on 5.26 AU ring): base-8 station E08-OCTAL leaked live caretaker mic + Euclid I.34 octal group [047•034].",
        },
        {
            "seq": 6,
            "territory": "HEKTOR L4 (REBEL)",
            "target_id": "radio-free-hektor",
            "zoom": 2000,
            "freq": "6,445.0 kHz HOP",
            "sinpo": "4-2-4-3-4",
            "summary": "Zora's 180W Crawler X-74 on 624 Hektor out-hopped Ceres Foundry jammer by 90s; nulled -34 dB via Tartarus reference.",
        },
        {
            "seq": 7,
            "territory": "KAELEN-V RIM",
            "target_id": "st-jerome-slag",
            "zoom": 6,
            "freq": "9,290.0 kHz + H-I",
            "sinpo": "4-5-4-4-4",
            "summary": "Vael-Vihara Spire (1,140 ly via GOR-11 filament) received simultaneously on 31m shortwave and 21-cm Hydrogen hyperfine.",
        },
        {
            "seq": 8,
            "territory": "MERIDIAN TRUNK",
            "target_id": "kz9-omega",
            "zoom": 6,
            "freq": "7,140.3 kHz DRM-9",
            "sinpo": "2-3-2-2-2",
            "summary": "Feeder Relay KZ9-OMEGA (1,420 AU) hit by 60 kV silicate squall; ruptured PA oil capacitor splattering ±30 kHz.",
        },
        {
            "seq": 9,
            "territory": "OORT RING PEER",
            "target_id": "gor-8-trunk",
            "zoom": 2,
            "freq": "14,253.6 kHz DRM-9",
            "sinpo": "5-5-4-5-5",
            "summary": "Sister Trunk GOR-8 (31,400 AU) & antipodal GOR-3 (83,900 AU) locked 1.33-ly VLBI baseline for ED-9 Vat 19 parallelogram proof.",
        },
        {
            "seq": 10,
            "territory": "QUARRY 44-K",
            "target_id": "quarry-44k",
            "zoom": 6,
            "freq": "5,180.0 kHz FSK",
            "sinpo": "4-4-3-4-4",
            "summary": "Sector 9 West Crag (890 AU) logged cable drum slip on Pit 44-K dragline during Watch 2 shift.",
        },
        {
            "seq": 11,
            "territory": "SEDNA HILLS GATE",
            "target_id": "sedna-hills-relay",
            "zoom": 40,
            "freq": "14,285.7 kHz MUX",
            "sinpo": "5-5-4-5-5",
            "summary": "90377 Sedna repeater (780 AU off Sol on 1.28° loop) relayed 412 store-and-forward inner-system packets this Sweep.",
        },
        {
            "seq": 12,
            "territory": "TARTARUS HOLD",
            "target_id": "tartarus-buoy12",
            "zoom": 6,
            "freq": "4,125.0 kHz USB",
            "sinpo": "4-4-4-4-4",
            "summary": "Quarantine Buoy 12 (420 AU NW) still holding GOR-9's 811A oscillator tubes under 'fermented brine tuber' tariff.",
        },
        {
            "seq": 13,
            "territory": "TITAN SHALLOWS",
            "target_id": "buoy-n24",
            "zoom": 2000,
            "freq": "3,890.0 kHz CW",
            "sinpo": "3-4-3-3-3",
            "summary": "Saturn VI (±47.0\" off Sol, 9.58 AU): 85W Buoy TM-N24/B detuned -165 Hz at TSol dawn by wading silt-striders on guy-wire #2.",
        },
        {
            "seq": 14,
            "territory": "TRIANGULUM M-33",
            "target_id": "m33-drift-buoy",
            "zoom": 6,
            "freq": "1,420.405 MHz H-I",
            "sinpo": "2-4-2-3-2",
            "summary": "4.2W Sonde M33-771/R (2.73 Mly via Perseus Einstein caustic) copied S4 issuing advisories for a dry ammonia basin.",
        },
    ]

    json_text = json.dumps(data, indent=2, ensure_ascii=False)
    STATIONS_JSON.write_text(json_text + "\n", encoding="utf-8")
    STATIONS_JS.write_text(f"window.GOR9_STATIONS_DATA = {json_text};\n", encoding="utf-8")
    print(
        f"Updated {STATIONS_JSON.name} & {STATIONS_JS.name} (v3.0.0): "
        f"{len(data['presets'])} stations, {len(orbits_raw)} Solar System orbits, "
        f"{len(oort_relays)} Oort Ring relays, {len(data['sweep_roundup_log'])} Sweep Roll-Call entries."
    )


if __name__ == "__main__":
    main()
