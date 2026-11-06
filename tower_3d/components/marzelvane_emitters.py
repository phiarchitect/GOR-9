"""
Component: 4 Concentric Marzelvane Emitter Rings & Crown Cherenkov Spire
========================================================================
Models the horizontal toroidal phased-array antenna crown at MARZEL_Z = 72.0m
and the Cherenkov spire tip at SPIRE_TOP_Z = 86.5m:
  - Central Harmonic Phase-Splitter Hub at Z = 72.0m (accessible from the
    Z = 70.8m Marzelvane Service Gallery platform directly beneath it)
  - 4 Concentric Horizontal Marzelvane Emitter Rings (R = 7.0, 11.5, 16.0, 21.0m)
    with brushed brass outer containment tori and glowing cyan Cherenkov cores
  - 16 Radial Waveguide Spokes + 64 Ceramic Standoff Nodes (16 × 4 rings)
  - 16 Upper & Lower Diagonal Suspension Stays
  - Crown Cherenkov Spire rising to Z = 86.5m.
"""

import math
from .primitives import (
    MARZEL_Z,
    MATERIALS,
    SPIRE_TOP_Z,
    add_box,
    add_prism,
    add_ring_torus,
    add_strut,
    create_scene_group,
    with_channel,
)


RING_RADII = [7.0, 11.5, 16.0, 21.0]


def build_marzelvane_emitters(scene):
    grp = create_scene_group(scene, "07_Marzelvane_Emitters_And_Spire")
    mesh = grp.mesh

    ring_glow_mats = [
        with_channel(MATERIALS["cyan_glow"], f"ring_{i + 1}") for i in range(4)
    ]
    ring_core_mats = [
        with_channel(MATERIALS["cyan_core"], f"ring_{i + 1}") for i in range(4)
    ]
    spire_glow = with_channel(MATERIALS["cyan_glow"], "spire_beacon")
    spire_core = with_channel(MATERIALS["cyan_core"], "spire_beacon")
    outer_amber = with_channel(MATERIALS["amber_glow"], "ring_4")

    # 1. Central Harmonic Phase-Splitter Hub at MARZEL_Z = 72.0m
    # (Sits 1.2m above the Z = 70.8m Marzelvane Crown Service Gallery Platform so
    # the keeper can service the 16 radial waveguide feed couplings at chest height!)
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=1.55,
        z_bot=MARZEL_Z - 0.65,
        z_top=MARZEL_Z + 0.65,
        sides=16,
        rot_rad=0.0,
        taper=0.96,
        mat_top=MATERIALS["brass"],
        mat_side_a=MATERIALS["copper"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    add_ring_torus(mesh, 0.0, 0.0, MARZEL_Z, 1.68, 0.16, ring_glow_mats[0], segs=32, tube_sides=8)

    # 4 Cardinal EVA Catwalk Spokes extending from the Z=70.8m Service Gallery out to the R=7.0m inner ring
    for i in range(4):
        ang = i * math.pi * 0.5
        ca, sa = math.cos(ang), math.sin(ang)
        add_strut(
            mesh,
            (3.1 * ca, 3.1 * sa, MARZEL_Z - 1.20),
            (7.0 * ca, 7.0 * sa, MARZEL_Z - 1.20),
            0.14,
            MATERIALS["steel_dark"],
            sides=6,
        )
        # Handrail struts along the 4 cardinal EVA service bridges
        rx, ry = -sa * 0.28, ca * 0.28
        for side in (-1.0, 1.0):
            add_strut(
                mesh,
                (3.2 * ca + side * rx, 3.2 * sa + side * ry, MARZEL_Z - 0.25),
                (6.9 * ca + side * rx, 6.9 * sa + side * ry, MARZEL_Z - 0.25),
                0.025,
                MATERIALS["steel_light"],
                sides=6,
            )

    # 2. Four Concentric Horizontal Marzelvane Emitter Rings (R = 7.0, 11.5, 16.0, 21.0m)
    for r_idx, rad in enumerate(RING_RADII):
        z_ring = MARZEL_Z + r_idx * 0.12
        segs = 36 + r_idx * 8
        # Outer structural brass phase-guide ring
        add_ring_torus(
            mesh,
            0.0,
            0.0,
            z_ring,
            rad,
            0.22 - r_idx * 0.015,
            MATERIALS["brass"],
            segs=segs,
            tube_sides=8,
        )
        # Upper & lower glowing cyan Cherenkov plasma rings (tagged per ring_1..ring_4)
        add_ring_torus(
            mesh,
            0.0,
            0.0,
            z_ring + 0.18,
            rad,
            0.145,
            ring_glow_mats[r_idx],
            segs=segs,
            tube_sides=6,
        )
        add_ring_torus(
            mesh,
            0.0,
            0.0,
            z_ring - 0.18,
            rad,
            0.130,
            ring_core_mats[r_idx],
            segs=segs,
            tube_sides=6,
        )

    # 3. 16 Radial Waveguide Spokes + 64 Ceramic Standoff Nodes + Vertical Dipole Elements
    for s_i in range(16):
        ang = 2.0 * math.pi * s_i / 16.0
        ca, sa = math.cos(ang), math.sin(ang)

        # Primary radial waveguide boom from hub (r=1.4m) out to outer ring (r=21.3m)
        p_in = (1.40 * ca, 1.40 * sa, MARZEL_Z)
        p_out = (21.35 * ca, 21.35 * sa, MARZEL_Z + 0.36)
        add_strut(
            mesh,
            p_in,
            p_out,
            0.095 if (s_i % 2 == 0) else 0.065,
            MATERIALS["steel_light"] if (s_i % 2 == 0) else MATERIALS["copper"],
            sides=6,
        )

        # Ceramic Standoff Node + Vertical Phase Dipole at each of the 4 ring intersections
        for r_idx, rad in enumerate(RING_RADII):
            z_r = MARZEL_Z + r_idx * 0.12
            nx, ny = rad * ca, rad * sa
            # Vertical dipole element piercing the ring node
            dip_h = 0.85 + r_idx * 0.12
            add_strut(
                mesh,
                (nx, ny, z_r - dip_h),
                (nx, ny, z_r + dip_h),
                0.055,
                MATERIALS["steel_light"],
                sides=6,
            )
            # Glowing cyan dipole tips (tagged with their ring's light_channel)
            add_box(mesh, nx - 0.13, ny - 0.13, z_r + dip_h, nx + 0.13, ny + 0.13, z_r + dip_h + 0.28, ring_core_mats[r_idx])
            add_box(
                mesh,
                nx - 0.12,
                ny - 0.12,
                z_r - dip_h - 0.24,
                nx + 0.12,
                ny + 0.12,
                z_r - dip_h,
                outer_amber if (r_idx == 3 and s_i % 4 == 0) else ring_glow_mats[r_idx],
            )

        # Upper & Lower Diagonal Suspension Stays on the 8 primary spokes
        if s_i % 2 == 0:
            # Upper suspension cable from Spire Collar (Z = 80.5m) to Ring 3 (R = 16.0m) and Ring 4 (R = 21.0m)
            add_strut(
                mesh,
                (0.55 * ca, 0.55 * sa, MARZEL_Z + 8.5),
                (16.0 * ca, 16.0 * sa, MARZEL_Z + 0.24),
                0.032,
                MATERIALS["steel_light"],
                sides=6,
            )
            add_strut(
                mesh,
                (0.45 * ca, 0.45 * sa, MARZEL_Z + 10.5),
                (21.0 * ca, 21.0 * sa, MARZEL_Z + 0.36),
                0.032,
                MATERIALS["steel_light"],
                sides=6,
            )
            # Lower compression strut from Tower Collar (Z = 65.5m) to Ring 2 (R = 11.5m) and Ring 3 (R = 16.0m)
            add_strut(
                mesh,
                (1.15 * ca, 1.15 * sa, MARZEL_Z - 6.5),
                (11.5 * ca, 11.5 * sa, MARZEL_Z + 0.12),
                0.048,
                MATERIALS["steel"],
                sides=6,
            )
            add_strut(
                mesh,
                (1.15 * ca, 1.15 * sa, MARZEL_Z - 6.5),
                (16.0 * ca, 16.0 * sa, MARZEL_Z + 0.24),
                0.042,
                MATERIALS["steel_dark"],
                sides=6,
            )

    # 4. Crown Cherenkov Spire (Z = 72.0m .. 86.5m)
    add_strut(mesh, (0.0, 0.0, MARZEL_Z), (0.0, 0.0, SPIRE_TOP_Z - 0.6), 0.32, MATERIALS["brass"], sides=12)
    add_strut(mesh, (0.0, 0.0, MARZEL_Z + 5.5), (0.0, 0.0, SPIRE_TOP_Z), 0.22, spire_core, sides=10)

    # 5 Graduated Corona Rings climbing the Crown Spire
    for c_i in range(5):
        zc = MARZEL_Z + 3.0 + c_i * 2.4
        rc = 1.35 - c_i * 0.18
        add_ring_torus(mesh, 0.0, 0.0, zc, rc, 0.10, spire_glow, segs=24, tube_sides=6)
        add_ring_torus(mesh, 0.0, 0.0, zc - 0.18, rc * 0.85, 0.05, MATERIALS["brass"], segs=20, tube_sides=6)

    # Blazing Apex Cherenkov Beacon Orb at SPIRE_TOP_Z = 86.5m
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=0.68,
        z_bot=SPIRE_TOP_Z - 0.65,
        z_top=SPIRE_TOP_Z + 0.55,
        sides=12,
        rot_rad=0.0,
        taper=0.78,
        mat_top=spire_core,
        mat_side_a=spire_glow,
        mat_side_b=spire_core,
    )

    return grp

