"""
Component: Continuous 86.5m Steel Lattice Tower & Central Lighthouse Climb Spine
================================================================================
Models:
  1. Continuous 4-leg tapered steel lattice tower (Z = 0.0m .. 78.0m) that
     passes uninterrupted through the floor and ceiling of the Octagonal
     Broadcast Booth (Z = 26.0m .. 31.2m).
  2. Lower Pressurized Personnel Climb / Lift Tube (Z = 0.0m .. 26.0m, r = 1.15m)
     from the Base Airlock Vestibule into the center of the Broadcast Booth.
  3. Booth Interior Central Waveguide Core + Interior Climb Ladder (Z = 26.0m .. 31.2m)
     rising through the booth ceiling hatch.
  4. Upper EVA Caged Maintenance Ladder (Z = 31.2m .. 71.2m) & 3 Circular Grated
     Service Platforms (Z = 45.0m, 58.0m, and the Marzelvane Crown Service
     Gallery at Z = 70.8m) so the keeper can climb all the way to the
     Marzelvane Emitters.
"""

import math
from .primitives import (
    BOOTH_Z,
    MARZEL_Z,
    MATERIALS,
    add_box,
    add_caged_ladder,
    add_prism,
    add_ring_torus,
    add_strut,
    create_scene_group,
    with_channel,
)


def tower_half_width(z: float) -> float:
    """Continuous piecewise-linear half-width of the 4-leg steel lattice tower."""
    if z <= BOOTH_Z:
        t = z / BOOTH_Z
        return 4.60 * (1.0 - t) + 1.92 * t
    else:
        t = min(1.0, (z - BOOTH_Z) / (78.0 - BOOTH_Z))
        return 1.92 * (1.0 - t) + 1.05 * t


def add_circular_service_platform(mesh, z_elev: float, plat_r: float, inner_r: float = 0.55):
    """Add an octagonal grated EVA service platform with safety handrails around the upper tower."""
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=plat_r,
        z_bot=z_elev - 0.16,
        z_top=z_elev,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=1.0,
        mat_top=MATERIALS["booth_floor"],
        mat_side_a=MATERIALS["steel"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    # Brass safety toe-kick & top/mid guardrail rings
    add_ring_torus(mesh, 0.0, 0.0, z_elev + 0.06, plat_r - 0.08, 0.04, MATERIALS["brass"], segs=16, tube_sides=6)
    add_ring_torus(mesh, 0.0, 0.0, z_elev + 0.55, plat_r - 0.08, 0.03, MATERIALS["steel_light"], segs=16, tube_sides=6)
    add_ring_torus(mesh, 0.0, 0.0, z_elev + 1.08, plat_r - 0.08, 0.04, MATERIALS["steel_light"], segs=16, tube_sides=6)
    # 8 vertical handrail stanchions + amber perimeter marker beacons
    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0 + math.pi / 8.0
        px = (plat_r - 0.08) * math.cos(ang)
        py = (plat_r - 0.08) * math.sin(ang)
        add_strut(mesh, (px, py, z_elev), (px, py, z_elev + 1.10), 0.03, MATERIALS["steel_light"], sides=6)
        if i % 2 == 0:
            add_box(mesh, px - 0.08, py - 0.08, z_elev + 1.10, px + 0.08, py + 0.08, z_elev + 1.24, MATERIALS["amber_glow"])


def build_continuous_tower_and_spine(scene):
    grp = create_scene_group(scene, "03_Continuous_Tower_And_Climb_Spine")
    mesh = grp.mesh

    # ── 1. Continuous 4-Leg Steel Lattice Tower (Z = 0.0m .. 78.0m) ──────────
    z_levels = [
        0.0,
        4.2,
        8.5,
        13.0,
        17.5,
        22.0,
        BOOTH_Z,          # 26.0m (Booth Floor)
        BOOTH_Z + 5.2,    # 31.2m (Booth Ceiling)
        36.0,
        40.5,
        45.0,             # Lower Exciter Service Platform
        49.5,
        54.0,
        58.0,             # Upper Phase-Lock Service Platform
        62.5,
        67.0,
        70.8,             # Marzelvane Service Gallery Platform
        74.5,
        78.0,
    ]
    signs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    for b_idx in range(len(z_levels) - 1):
        z0 = z_levels[b_idx]
        z1 = z_levels[b_idx + 1]
        w0 = tower_half_width(z0)
        w1 = tower_half_width(z1)
        in_booth = abs(z0 - BOOTH_Z) < 0.05 and abs(z1 - (BOOTH_Z + 5.2)) < 0.05

        corners0 = [(sx * w0, sy * w0, z0) for sx, sy in signs]
        corners1 = [(sx * w1, sy * w1, z1) for sx, sy in signs]
        leg_r = 0.16 if z0 < BOOTH_Z else (0.145 if in_booth else 0.125)

        for i in range(4):
            ni = (i + 1) % 4
            # Continuous main corner leg
            add_strut(mesh, corners0[i], corners1[i], leg_r, MATERIALS["steel"], sides=6)
            # Horizontal ring girt at top of bay
            add_strut(mesh, corners1[i], corners1[ni], leg_r * 0.68, MATERIALS["steel_dark"], sides=6)

            if in_booth:
                # Inside the Broadcast Booth: keep lower 3.0m clear walk-through portal,
                # add architectural K-brace gussets in upper 2.2m (z = +3.0m .. +5.2m)
                z_portal = BOOTH_Z + 3.05
                w_portal = tower_half_width(z_portal)
                p_i = (signs[i][0] * w_portal, signs[i][1] * w_portal, z_portal)
                p_ni = (signs[ni][0] * w_portal, signs[ni][1] * w_portal, z_portal)
                mid_top = (
                    0.5 * (corners1[i][0] + corners1[ni][0]),
                    0.5 * (corners1[i][1] + corners1[ni][1]),
                    z1,
                )
                add_strut(mesh, p_i, p_ni, 0.075, MATERIALS["steel_dark"], sides=6)
                add_strut(mesh, p_i, mid_top, 0.068, MATERIALS["steel_light"], sides=6)
                add_strut(mesh, p_ni, mid_top, 0.068, MATERIALS["steel_light"], sides=6)
                # Floor & ceiling structural brass penetration collars
                c0x, c0y, _ = corners0[i]
                c1x, c1y, _ = corners1[i]
                add_box(mesh, c0x - 0.25, c0y - 0.25, BOOTH_Z + 0.01, c0x + 0.25, c0y + 0.25, BOOTH_Z + 0.20, MATERIALS["brass"])
                add_box(mesh, c1x - 0.23, c1y - 0.23, z1 - 0.22, c1x + 0.23, c1y + 0.23, z1 - 0.02, MATERIALS["brass"])
            else:
                # Exterior X-bracing on all 4 faces
            	add_strut(mesh, corners0[i], corners1[ni], leg_r * 0.50, MATERIALS["steel_light"], sides=6)
            	add_strut(mesh, corners0[ni], corners1[i], leg_r * 0.50, MATERIALS["steel_light"], sides=6)

    wg_low = with_channel(MATERIALS["cyan_glow"], "waveguide_low")
    wg_mid = with_channel(MATERIALS["cyan_glow"], "waveguide_mid")
    wg_high = with_channel(MATERIALS["cyan_glow"], "waveguide_high")

    # ── 2. Lower Pressurized Personnel Climb / Lift Tube (Z = 0.0m .. 26.0m) ──
    # Connects Base Airlock Vestibule to the floor of the Octagonal Broadcast Booth
    add_strut(mesh, (0.0, 0.0, 2.8), (0.0, 0.0, BOOTH_Z - 0.2), 1.12, MATERIALS["hab_hull"], sides=12)
    for z_ring in range(4, int(BOOTH_Z), 3):
        add_ring_torus(mesh, 0.0, 0.0, float(z_ring), 1.18, 0.07, MATERIALS["steel_light"], segs=18, tube_sides=6)
        # Glowing Cherenkov energy collar every 6m along the lower tube
        if z_ring % 6 == 4:
            add_ring_torus(mesh, 0.0, 0.0, float(z_ring) + 0.25, 1.24, 0.085, wg_low, segs=18, tube_sides=6)
        # Warm amber vertical viewport slits on North & South faces of the pressurized tube
        if z_ring % 6 == 1:
            add_box(mesh, -0.14, 1.08, z_ring + 0.4, 0.14, 1.18, z_ring + 1.8, MATERIALS["amber_glow"])
            add_box(mesh, -0.14, -1.18, z_ring + 0.4, 0.14, -1.08, z_ring + 1.8, MATERIALS["amber_glow"])

    # Exterior backup EVA Caged Ladder alongside the lower pressurized tube (West side)
    add_caged_ladder(mesh, x=-1.28, y=0.0, z0=3.2, z1=BOOTH_Z - 0.4, facing_ang_deg=180.0, with_cage=True)

    # ── 3. Booth Interior Central Waveguide Core & Climb Ladder (Z = 26.0m .. 31.2m) ──
    # Floor arrival hatch collar where the keeper steps out of the central climb tube
    add_ring_torus(mesh, 0.0, 0.0, BOOTH_Z + 0.06, 1.15, 0.09, MATERIALS["brass"], segs=24, tube_sides=8)
    add_ring_torus(mesh, 0.0, 0.0, BOOTH_Z + 0.14, 0.72, 0.06, MATERIALS["steel_dark"], segs=24, tube_sides=6)

    # Central copper coaxial waveguide column passing through the center of the booth
    add_strut(mesh, (0.0, 0.0, BOOTH_Z), (0.0, 0.0, BOOTH_Z + 5.2), 0.40, MATERIALS["copper"], sides=14)
    for z_off in (0.65, 1.65, 2.65, 3.65, 4.55):
        add_ring_torus(mesh, 0.0, 0.0, BOOTH_Z + z_off, 0.50, 0.045, MATERIALS["brass"], segs=20, tube_sides=6)
        add_ring_torus(mesh, 0.0, 0.0, BOOTH_Z + z_off, 0.44, 0.035, wg_low, segs=20, tube_sides=6)

    # Interior Climb Ladder inside the booth (West side of central waveguide, rising to ceiling EVA hatch)
    add_caged_ladder(
        mesh,
        x=-0.56,
        y=0.0,
        z0=BOOTH_Z + 0.05,
        z1=BOOTH_Z + 5.25,
        facing_ang_deg=180.0,
        with_cage=False,
    )
    # Ceiling EVA Hatch Coaming Ring (allows climbing out onto the booth roof)
    add_ring_torus(mesh, -0.35, 0.0, BOOTH_Z + 5.12, 0.65, 0.08, MATERIALS["brass"], segs=20, tube_sides=6)

    # ── 4. Upper Coaxial Waveguide & Full EVA Climb Spine to Marzelvane Emitters (Z = 31.2m .. 78.0m) ──
    add_strut(mesh, (0.0, 0.0, BOOTH_Z + 5.2), (0.0, 0.0, 78.0), 0.42, MATERIALS["copper"], sides=12)

    # Periodic cyan Cherenkov phase-lock rings up the upper spine (split into mid & high pulse zones)
    for z_c in range(34, 72, 4):
        wg_mat = wg_mid if z_c < 54 else wg_high
        add_ring_torus(mesh, 0.0, 0.0, float(z_c), 0.66, 0.095, wg_mat, segs=20, tube_sides=6)
        add_ring_torus(mesh, 0.0, 0.0, float(z_c) - 0.22, 0.62, 0.05, MATERIALS["brass"], segs=20, tube_sides=6)

    # Three Circular Grated Service Platforms along the upper climb to the Marzelvane Emitters:
    #   (A) Z = 36.0m: Lower Exciter & Sign Service Landing (positioned below the Z = 37.8m..53.4m vertical tower sign)
    #   (B) Z = 58.0m: Upper Harmonic Phase-Lock Interior Rest Landing (above the vertical tower sign)
    #   (C) Z = 70.8m: Marzelvane Crown Service Gallery (directly below the 4 Emitter Rings at 72.0m)
    add_circular_service_platform(mesh, z_elev=36.0, plat_r=1.52)
    add_circular_service_platform(mesh, z_elev=58.0, plat_r=1.32)
    add_circular_service_platform(mesh, z_elev=MARZEL_Z - 1.2, plat_r=3.35)

    # Exciter tuning drums at the two intermediate service platforms
    for z_exc in (36.0, 58.0):
        exc_mat = wg_mid if z_exc < 52.0 else wg_high
        add_prism(
            mesh,
            cx=0.0,
            cy=0.0,
            rad=0.92,
            z_bot=z_exc + 0.1,
            z_top=z_exc + 1.45,
            sides=8,
            rot_rad=math.pi / 8.0,
            taper=0.92,
            mat_top=MATERIALS["brass"],
            mat_side_a=MATERIALS["steel_dark"],
            mat_side_b=MATERIALS["steel"],
        )
        add_ring_torus(mesh, 0.0, 0.0, z_exc + 0.8, 1.08, 0.10, exc_mat, segs=20, tube_sides=6)

    # Continuous Caged EVA Climb Ladder Flights from Booth Roof (+31.6m) all the way to Marzelvane Gallery (+70.8m)
    add_caged_ladder(mesh, x=-0.72, y=0.0, z0=BOOTH_Z + 5.6, z1=36.0, facing_ang_deg=180.0, with_cage=True)
    add_caged_ladder(mesh, x=0.0, y=-0.72, z0=36.0, z1=58.0, facing_ang_deg=270.0, with_cage=True)
    add_caged_ladder(mesh, x=-0.72, y=0.0, z0=58.0, z1=MARZEL_Z - 1.2, facing_ang_deg=180.0, with_cage=True)

    # Diagonal Structural Guy Cables from Tower Elevations (+25.5m and +58.0m) to the 4 Basalt Anchor Bollards
    anchor_coords = [
        (14.5, -14.5, -3.4),    # SE Cliff-Edge Pinnacle Buttress (matches signs[1] = (+1, -1))
        (-19.5, -19.5, -0.5),   # SW Upland Terrace Bollard (matches signs[0] = (-1, -1))
        (14.5, 14.5, -3.4),     # NE Cliff-Edge Pinnacle Buttress (matches signs[2] = (+1, +1))
        (-19.5, 19.5, -0.7),    # NW Upland Terrace Bollard (matches signs[3] = (-1, +1))
    ]
    guy_signs = [(1, -1), (-1, -1), (1, 1), (-1, 1)]
    w_booth_bot = tower_half_width(BOOTH_Z - 0.5)
    w_upper_guy = tower_half_width(58.0)
    for idx, (ax, ay, az) in enumerate(anchor_coords):
        sx, sy = guy_signs[idx]
        add_strut(
            mesh,
            (sx * w_booth_bot, sy * w_booth_bot, BOOTH_Z - 0.5),
            (ax, ay, az),
            0.042,
            MATERIALS["steel_light"],
            sides=6,
        )
        add_strut(
            mesh,
            (sx * w_upper_guy, sy * w_upper_guy, 58.0),
            (ax, ay, az),
            0.035,
            MATERIALS["steel_light"],
            sides=6,
        )

    # ── 5. Twin Vertically Stacked 3D 'G / O / R / [Marzelvane Rings] / 9' Tower Signs ──
    #   - Sign #1: Mounted on the cliff-facing side of the upper tower spine (ESE, Az = -28°)
    #   - Sign #2: Mounted on the exact opposite side of the upper tower spine (WNW, Az = +152°)
    #   - Raised ~2 letter heights (+6.0m) above the booth roof to Z = +37.8m .. +53.4m
    from .logo_gor9 import add_gor9_vertical_tower_sign_3d

    add_gor9_vertical_tower_sign_3d(
        mesh=mesh,
        azimuth_deg=-28.0,
        r_mount_bot=2.74,
        r_mount_top=2.40,
        z_bot=37.8,
        z_top=53.4,
        char_width=1.95,
    )
    add_gor9_vertical_tower_sign_3d(
        mesh=mesh,
        azimuth_deg=152.0,
        r_mount_bot=2.74,
        r_mount_top=2.40,
        z_bot=37.8,
        z_top=53.4,
        char_width=1.95,
    )

    return grp



