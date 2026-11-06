"""
Component: Companion Basalt Monoliths, Distant Tumbling Asteroids & Relay Satellites
====================================================================================
Models the 3D orbital environment surrounding Asteroid 3-5-1 in Oort Cloud Sector 9:
  1. Stationary Gravitationally-Bound Companion Basalt Monoliths (`09_Companion_Boulders`):
     Two cleaved, double-ended hexagonal/pentagonal columnar-basalt fragments held in
     rubble-pile gravitational equilibrium off the eastern chasm flanks (~260m out).
  2. Distant Tumbling 3D Columnar-Basalt Asteroids (`10_Tumbling_Asteroid_1..3`):
     Clustered volcanic basalt shards far out at 650m–740m range with local `grp.pivot`
     centers so Blender can keyframe them rolling and flipping in deep space.
  3. Distant Orbital Relay Satellites (`13_ORS_351_Satellite` at `(354, -253, 56)`
     where the onboard `satellite_pov_wide` camera is mounted on its forward optical
     deck at `(348, -248, 58)`, and `14_Relay_Sonde_B` at `(-420, -310, 240)`).
"""

import math
from .primitives import (
    MARZEL_Z,
    MATERIALS,
    add_box,
    add_face,
    add_octahedron_beacon,
    add_prism,
    add_ring_torus,
    add_strut,
    create_scene_group,
    with_channel,
)


def _add_columnar_basalt_shard_asteroid(
    mesh,
    cx: float,
    cy: float,
    cz: float,
    rad: float,
    half_h: float,
    seed: int,
    ring_count: int = 7,
):
    """
    Build a free-floating 3D columnar-basalt asteroid / companion monolith out of
    interlocking hexagonal & pentagonal basalt columns with stepped upper & lower
    cleavage facets.
    """
    add_prism(
        mesh,
        cx=cx,
        cy=cy,
        rad=rad * 0.60,
        z_bot=cz,
        z_top=cz + half_h,
        sides=6,
        rot_rad=seed * 0.31,
        taper=1.02,
        mat_top=MATERIALS["basalt_rim"],
    )
    add_prism(
        mesh,
        cx=cx,
        cy=cy,
        rad=rad * 0.62,
        z_bot=cz - half_h * 1.08,
        z_top=cz,
        sides=6,
        rot_rad=seed * 0.31,
        taper=0.88,
        mat_top=MATERIALS["basalt_dark"],
    )

    for i in range(ring_count):
        ang = (2.0 * math.pi * i / ring_count) + seed * 0.17
        dist = rad * (0.54 + 0.08 * ((i + seed) % 2))
        px = cx + dist * math.cos(ang)
        py = cy + dist * math.sin(ang)
        prad = rad * (0.44 + 0.07 * ((i + seed) % 3))
        z_hi = cz + half_h * (0.42 + 0.44 * ((i * 3 + seed) % 4) / 3.0)
        z_lo = cz - half_h * (0.42 + 0.46 * ((i * 5 + seed) % 4) / 3.0)
        sides = 6 if ((i + seed) % 3 != 0) else 5
        mat_t = MATERIALS["basalt_rim"] if (i % 2 == 0) else MATERIALS["basalt"]
        add_prism(
            mesh,
            cx=px,
            cy=py,
            rad=prad,
            z_bot=cz,
            z_top=z_hi,
            sides=sides,
            rot_rad=ang + 0.2,
            taper=1.02,
            mat_top=mat_t,
        )
        add_prism(
            mesh,
            cx=px,
            cy=py,
            rad=prad * 1.02,
            z_bot=z_lo,
            z_top=cz,
            sides=sides,
            rot_rad=ang + 0.2,
            taper=0.88,
            mat_top=MATERIALS["basalt_dark"],
        )


def build_companion_boulders(scene):
    """
    Build 2 stationary columnar-basalt companion monoliths held in gravitational
    equilibrium beyond the outer chasm flanks (~260m–270m from the tower).
    """
    grp = create_scene_group(scene, "09_Companion_Boulders")
    mesh = grp.mesh

    # Companion Monolith A: East-Southeast beyond the chasm rim (R ≈ 262m)
    _add_columnar_basalt_shard_asteroid(
        mesh,
        cx=245.0,
        cy=-88.0,
        cz=-38.0,
        rad=9.2,
        half_h=12.5,
        seed=101,
        ring_count=7,
    )

    # Companion Monolith B: North-East beyond the chasm rim (R ≈ 269m)
    _add_columnar_basalt_shard_asteroid(
        mesh,
        cx=195.0,
        cy=185.0,
        cz=-22.0,
        rad=10.5,
        half_h=14.0,
        seed=202,
        ring_count=7,
    )

    return grp


def build_tumbling_asteroids(scene):
    """
    Build 3 distant 3D columnar-basalt asteroids (at R ≈ 640m–740m range, well clear
    of the tower centerline) with `grp.pivot` centers for multi-axis tumbling in Blender.
    """
    tumbling_specs = [
        # (name, (cx, cy, cz), rad, half_h, seed)
        ("10_Tumbling_Asteroid_1", (-540.0, 95.0, 145.0), 8.5, 11.5, 401),
        ("11_Tumbling_Asteroid_2", (-145.0, 625.0, 195.0), 9.5, 13.0, 502),
        ("12_Tumbling_Asteroid_3", (485.0, 445.0, 125.0), 8.0, 11.0, 603),
    ]
    groups = []
    for name, (cx, cy, cz), rad, half_h, seed in tumbling_specs:
        grp = create_scene_group(scene, name)
        try:
            grp.pivot = (cx, cy, cz)
        except AttributeError:
            pass
        _add_columnar_basalt_shard_asteroid(
            grp.mesh,
            cx=cx,
            cy=cy,
            cz=cz,
            rad=rad,
            half_h=half_h,
            seed=seed,
            ring_count=7,
        )
        groups.append(grp)
    return groups


def _build_single_satellite(
    mesh,
    cx: float,
    cy: float,
    cz: float,
    aim_target: tuple[float, float, float] = (0.0, 0.0, MARZEL_Z),
    scale: float = 1.0,
):
    sat_cyan = with_channel(MATERIALS["cyan_core"], "sat_beacon")
    sat_crimson = with_channel(MATERIALS["crimson_glow"], "sat_beacon")
    sat_amber = with_channel(MATERIALS["amber_glow"], "sat_beacon")

    tx, ty, tz = aim_target
    dx, dy, dz = tx - cx, ty - cy, tz - cz
    dist = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    fx, fy, fz = dx / dist, dy / dist, dz / dist
    wx, wy, wz = -fy, fx, 0.0
    wl = math.sqrt(wx * wx + wy * wy) or 1.0
    wx, wy = wx / wl, wy / wl
    ux = wy * fz - wz * fy
    uy = wz * fx - wx * fz
    uz = wx * fy - wy * fx

    bus_r = 1.15 * scale
    bus_h = 2.40 * scale
    add_prism(
        mesh,
        cx=cx,
        cy=cy,
        rad=bus_r,
        z_bot=cz - bus_h * 0.5,
        z_top=cz + bus_h * 0.5,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=0.94,
        mat_top=MATERIALS["brass"],
        mat_side_a=MATERIALS["brass"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    add_ring_torus(mesh, cx, cy, cz + bus_h * 0.35, bus_r * 1.04, 0.09 * scale, MATERIALS["copper"], segs=16, tube_sides=6)
    add_ring_torus(mesh, cx, cy, cz - bus_h * 0.35, bus_r * 1.04, 0.09 * scale, MATERIALS["steel_light"], segs=16, tube_sides=6)

    dish_cx = cx + fx * (1.35 * scale)
    dish_cy = cy + fy * (1.35 * scale)
    dish_cz = cz + fz * (1.35 * scale)
    dish_r = 2.10 * scale
    dish_segs = 16
    rim_pts = []
    hub_pts = []
    for i in range(dish_segs):
        ang = 2.0 * math.pi * i / dish_segs
        ca, sa = math.cos(ang), math.sin(ang)
        rx_dir = ca * wx + sa * ux
        ry_dir = ca * wy + sa * uy
        rz_dir = ca * wz + sa * uz
        rim_pts.append(
            (
                dish_cx + fx * (0.45 * scale) + dish_r * rx_dir,
                dish_cy + fy * (0.45 * scale) + dish_r * ry_dir,
                dish_cz + fz * (0.45 * scale) + dish_r * rz_dir,
            )
        )
        hub_pts.append(
            (
                dish_cx + 0.32 * dish_r * rx_dir,
                dish_cy + 0.32 * dish_r * ry_dir,
                dish_cz + 0.32 * dish_r * rz_dir,
            )
        )
    for i in range(dish_segs):
        ni = (i + 1) % dish_segs
        mat_panel = MATERIALS["steel_light"] if (i % 2 == 0) else MATERIALS["steel"]
        add_face(mesh, [hub_pts[i], hub_pts[ni], rim_pts[ni], rim_pts[i]], dict(mat_panel))
        add_face(mesh, [rim_pts[i], rim_pts[ni], hub_pts[ni], hub_pts[i]], dict(MATERIALS["steel_dark"]))

    feed_pt = (
        dish_cx + fx * (1.85 * scale),
        dish_cy + fy * (1.85 * scale),
        dish_cz + fz * (1.85 * scale),
    )
    add_strut(mesh, (cx, cy, cz), feed_pt, 0.08 * scale, MATERIALS["brass"], sides=6)
    for t_i in range(3):
        idx = (t_i * dish_segs) // 3
        add_strut(mesh, rim_pts[idx], feed_pt, 0.04 * scale, MATERIALS["steel_light"], sides=6)
    add_octahedron_beacon(mesh, feed_pt[0], feed_pt[1], feed_pt[2], 0.24 * scale, sat_cyan)

    wing_span = 7.8 * scale
    wing_chord = 1.15 * scale
    for side in (-1.0, 1.0):
        p_root = (cx + side * wx * (bus_r * 0.95), cy + side * wy * (bus_r * 0.95), cz)
        p_tip = (cx + side * wx * wing_span, cy + side * wy * wing_span, cz)
        add_strut(mesh, p_root, p_tip, 0.075 * scale, MATERIALS["brass"], sides=6)

        for pan_i in range(4):
            r0 = (1.55 + pan_i * 1.52) * scale
            r1 = r0 + 1.36 * scale
            c0x, c0y = cx + side * wx * r0, cy + side * wy * r0
            c1x, c1y = cx + side * wx * r1, cy + side * wy * r1
            px_off = fx * (wing_chord * 0.35)
            py_off = fy * (wing_chord * 0.35)
            pz_off = wing_chord * 0.85
            q0 = (c0x - px_off, c0y - py_off, cz - pz_off)
            q1 = (c1x - px_off, c1y - py_off, cz - pz_off)
            q2 = (c1x + px_off, c1y + py_off, cz + pz_off)
            q3 = (c0x + px_off, c0y + py_off, cz + pz_off)
            add_face(mesh, [q0, q1, q2, q3], dict(MATERIALS["steel_dark"]))
            add_face(mesh, [q3, q2, q1, q0], dict(MATERIALS["copper"]))

        add_box(
            mesh,
            p_tip[0] - 0.18 * scale,
            p_tip[1] - 0.18 * scale,
            p_tip[2] - 0.18 * scale,
            p_tip[0] + 0.18 * scale,
            p_tip[1] + 0.18 * scale,
            p_tip[2] + 0.18 * scale,
            sat_crimson if side < 0 else sat_cyan,
        )

    aft_tip = (
        cx - fx * (4.2 * scale),
        cy - fy * (4.2 * scale),
        cz - fz * (4.2 * scale) - 0.6 * scale,
    )
    add_strut(mesh, (cx, cy, cz), aft_tip, 0.055 * scale, MATERIALS["steel_light"], sides=6)
    add_octahedron_beacon(mesh, aft_tip[0], aft_tip[1], aft_tip[2], 0.22 * scale, sat_amber)

    dorsal_tip = (cx, cy, cz + 3.4 * scale)
    add_strut(mesh, (cx, cy, cz + bus_h * 0.5), dorsal_tip, 0.04 * scale, MATERIALS["brass"], sides=6)
    add_octahedron_beacon(mesh, dorsal_tip[0], dorsal_tip[1], dorsal_tip[2], 0.26 * scale, sat_crimson)


def build_orbital_satellites(scene):
    """
    Build two distant 3D orbital relay satellites:
      - `13_ORS_351_Satellite` at SE orbital station `(354, -253, 56)` (`R ≈ 439m`),
        where the `satellite_pov_wide` onboard camera is mounted on its forward
        optical gimbal at `(348, -248, 58)` looking directly at Asteroid 3-5-1!
      - `14_Relay_Sonde_B` at distant WSW station `(-420, -310, 240)` (`R ≈ 574m`).
    """
    grp_ors = create_scene_group(scene, "13_ORS_351_Satellite")
    try:
        grp_ors.pivot = (354.0, -253.0, 56.0)
    except AttributeError:
        pass
    _build_single_satellite(
        grp_ors.mesh,
        cx=354.0,
        cy=253.0 * -1.0,
        cz=56.0,
        aim_target=(0.0, 0.0, MARZEL_Z),
        scale=1.10,
    )

    grp_sonde = create_scene_group(scene, "14_Relay_Sonde_B")
    try:
        grp_sonde.pivot = (-420.0, -310.0, 240.0)
    except AttributeError:
        pass
    _build_single_satellite(
        grp_sonde.mesh,
        cx=-420.0,
        cy=-310.0,
        cz=240.0,
        aim_target=(0.0, 0.0, MARZEL_Z),
        scale=1.25,
    )

    return [grp_ors, grp_sonde]
