"""
Component: Prismatic Basalt Cliff-Edge Headland & Acheron Chasm (Asteroid 3-5-1)
================================================================================
Positions the GOR-9 Lighthouse right at the sheer precipice of a 48-meter-tall
columnar basalt cliff headland:
  - Beneath the tower (x = 0, y = 0): Towering 48m-tall vertical hexagonal &
    pentagonal basalt columns plunging straight down to the chasm floor (Z = -48m).
  - West / South-West / North-West (Behind the Tower): Broad, gravity-bearing
    upland basalt promontory & stepped terraces supporting the Keeper's Habitat,
    Dilithium Reactor #2, and Cryo-Condenser compound.
  - East / South-East / North-East / North (In Front of the Tower): Sheer
    cliff drop-off into the deep Acheron Chasm (Z = -44m .. -48m), allowing
    dramatic low-angle cameras from the chasm looking UP at the cliff face
    and the 86.5m tower soaring overhead.
"""

import math
from .primitives import (
    MATERIALS,
    add_box,
    add_prism,
    add_ring_torus,
    add_strut,
    create_scene_group,
)


def build_prismatic_basalt_terrain(scene):
    grp = create_scene_group(scene, "01_Basalt_Promontory_Terrain")
    mesh = grp.mesh

    # ── 1. Sheer 48m Headland Cliff Promentory Core (Directly Under the Tower) ──
    # Central octagonal basalt monolith rising 48m from the chasm floor (Z = -48m to -0.45m)
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=9.8,
        z_bot=-48.0,
        z_top=-0.45,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=1.10,
        mat_top=MATERIALS["basalt_rim"],
    )

    # Tightly-packed vertical hexagonal & pentagonal cliff-face columns ringing the headland nose
    # On the cliff side (+X, -Y, +Y), these form a sheer, striated 48m vertical basalt wall!
    headland_cliff_columns = [
        # Cliff-edge face columns (East, SE, NE, North — sheer 48m drop to chasm!)
        (7.8, 0.0, 4.4, -0.55, 6, 0.10),
        (6.4, -5.8, 4.2, -0.70, 6, 0.35),
        (5.8, 6.2, 4.3, -0.65, 5, 0.20),
        (0.5, -8.2, 4.6, -0.60, 6, 0.08),
        (0.5, 8.2, 4.5, -0.60, 6, 0.25),
        # Lower stepped buttress ribs clinging to the sheer cliff face (Z = -48m to -14m / -22m)
        (11.2, -2.5, 3.6, -16.0, 6, 0.18),
        (10.5, 3.8, 3.4, -19.5, 5, 0.40),
        (8.8, -9.2, 3.8, -14.5, 6, 0.12),
        (8.5, 9.5, 3.5, -18.0, 6, 0.30),
        (13.8, 0.5, 3.2, -28.0, 6, 0.22),
        (12.2, -6.8, 3.3, -26.0, 5, 0.05),
        # Back-side columns merging into the upland plateau (West, SW, NW)
        (-7.2, 6.2, 5.2, -0.55, 6, 0.15),
        (-9.4, 0.0, 5.6, -0.50, 6, 0.50),
        (-7.0, -6.8, 5.4, -0.52, 5, 0.33),
    ]
    for cx, cy, rad, z_top, sides, rot in headland_cliff_columns:
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-48.0,
            z_top=z_top,
            sides=sides,
            rot_rad=rot,
            taper=1.08,
        )

    # ── 2. Upland Headland Terraces Behind the Tower (West / SW / NW / South) ──
    # (A) South-West Keeper's Habitat Terrace (Z = -1.6m)
    hab_terrace_prisms = [
        (-14.5, -5.5, 7.4, -1.60, 6, 0.0),
        (-20.0, -10.0, 6.8, -1.65, 6, 0.3),
        (-11.5, -14.0, 6.8, -1.65, 5, 0.2),
        (-22.5, -2.0, 6.2, -1.90, 6, 0.4),
    ]
    for cx, cy, rad, z_top, sides, rot in hab_terrace_prisms:
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-48.0,
            z_top=z_top,
            sides=sides,
            rot_rad=rot,
            taper=1.10,
            mat_top=MATERIALS["basalt_rim"],
        )

    # (B) North-West Dilithium Reactor #2 & Van Allen Switchyard Terrace (Z = -1.8m)
    # Placed on the NW upland shelf behind the cliff edge so the East/SE chasm cliff is 100% open!
    reactor_terrace_prisms = [
        (-14.5, 11.5, 7.8, -1.80, 6, 0.15),
        (-21.0, 15.0, 6.6, -1.85, 6, 0.45),
        (-8.0, 15.5, 6.4, -1.85, 5, 0.10),
        (-21.5, 7.5, 6.2, -2.10, 6, 0.25),
    ]
    for cx, cy, rad, z_top, sides, rot in reactor_terrace_prisms:
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-48.0,
            z_top=z_top,
            sides=sides,
            rot_rad=rot,
            taper=1.10,
            mat_top=MATERIALS["basalt_rim"],
        )

    # (C) South Cliff-Shoulder Cryo-Condenser & Winch Terrace (Z = -1.8m, right beside the South cliff lip)
    south_terrace_prisms = [
        (-2.5, -15.5, 6.6, -1.80, 6, 0.22),
        (4.2, -14.2, 5.2, -1.85, 6, 0.40),
        (-7.5, -20.5, 6.0, -2.20, 5, 0.12),
    ]
    for cx, cy, rad, z_top, sides, rot in south_terrace_prisms:
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-48.0,
            z_top=z_top,
            sides=sides,
            rot_rad=rot,
            taper=1.10,
            mat_top=MATERIALS["basalt_rim"],
        )

    # ── 3. Vast Upland Basalt Crag Rising Behind the Headland (West Arc: 115° .. 255°) ──
    # Forms the massive gravity-bearing asteroid mountain massif behind the lighthouse
    for i in range(22):
        ang_deg = 112.0 + (146.0 * i / 21.0)
        ang = math.radians(ang_deg)
        dist = 32.0 + (i % 3) * 11.5
        cx = dist * math.cos(ang)
        cy = dist * math.sin(ang)
        rad = 7.5 + (i % 4) * 2.2
        # Upland rises slightly higher toward the West massif crest (+1.5m .. +8.5m)
        z_top = -1.0 + (i % 4) * 2.2 + (dist - 32.0) * 0.12
        sides = 6 if (i % 3 != 0) else 5
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-48.0,
            z_top=z_top,
            sides=sides,
            rot_rad=ang * 0.7,
            taper=1.12,
            mat_top=MATERIALS["basalt_rim"] if (i % 3 == 0) else MATERIALS["basalt"],
        )

    # ── 4. Deep Acheron Chasm Floor Below the Cliff Edge (East / SE / NE Arc: -105° .. +105°) ──
    # Low, sunken hexagonal basalt talus columns at Z = -45m .. -34m so looking UP from the chasm
    # gives a completely unobstructed view of the sheer 48m cliff face and the 86.5m tower!
    for i in range(26):
        ang_deg = -102.0 + (204.0 * i / 25.0)
        ang = math.radians(ang_deg)
        dist = 24.0 + (i % 4) * 14.0
        cx = dist * math.cos(ang)
        cy = dist * math.sin(ang)
        rad = 5.8 + (i % 4) * 2.0
        z_top = -35.5 - (i % 3) * 3.2
        sides = 6 if (i % 2 == 0) else 5
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-54.0,
            z_top=z_top,
            sides=sides,
            rot_rad=i * 0.37,
            taper=1.08,
            mat_top=MATERIALS["basalt_dark"],
        )

    # Dramatic Distant Sea-Stack Basalt Needles far across the Acheron Chasm (R = 88..125m)
    distant_sea_stacks = [
        (92.0, 58.0, 9.5, -14.0, 6),
        (105.0, -48.0, 10.5, -16.0, 5),
        (68.0, 86.0, 8.5, -12.0, 6),
        (55.0, -92.0, 9.2, -15.0, 6),
    ]
    for cx, cy, rad, z_top, sides in distant_sea_stacks:
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=-54.0,
            z_top=z_top,
            sides=sides,
            rot_rad=0.25,
            taper=1.15,
            mat_top=MATERIALS["basalt_rim"],
        )

    # ── 5. Reinforced Octagonal Concrete & Steel Cliff-Edge Foundation Pad (Z = -0.45m .. +0.35m) ──
    # Cantilevers slightly out over the sheer East/SE basalt cliff edge!
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=9.4,
        z_bot=-0.45,
        z_top=0.0,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=1.02,
        mat_top=MATERIALS["steel_dark"],
        mat_side_a=MATERIALS["steel_dark"],
        mat_side_b=MATERIALS["steel"],
    )
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=6.4,
        z_bot=0.0,
        z_top=0.35,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=1.0,
        mat_top=MATERIALS["steel"],
        mat_side_a=MATERIALS["steel"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    # Heavy under-pad steel cliff-cantilever brackets bracing the East/SE overhang against the basalt cliff wall
    for cliff_ang_deg in (-67.5, -22.5, 22.5, 67.5):
        ca = math.cos(math.radians(cliff_ang_deg))
        sa = math.sin(math.radians(cliff_ang_deg))
        add_strut(
            mesh,
            (6.2 * ca, 6.2 * sa, -4.8),
            (9.0 * ca, 9.0 * sa, -0.35),
            0.24,
            MATERIALS["steel"],
            sides=6,
        )

    # Amber perimeter hazard beacons + cliff-edge safety railing along the sheer East/North precipice
    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0 + math.pi / 8.0
        bx, by = 8.8 * math.cos(ang), 8.8 * math.sin(ang)
        add_box(mesh, bx - 0.18, by - 0.18, 0.0, bx + 0.18, by + 0.18, 0.35, MATERIALS["steel_dark"])
        add_box(mesh, bx - 0.12, by - 0.12, 0.35, bx + 0.12, by + 0.12, 0.52, MATERIALS["amber_glow"])

    # ── 6. Four Guy-Wire Basalt Anchor Bollards ──
    # Two on the West upland terraces (-19.5, ±19.5) and two on dramatic cliff-edge pinnacle buttresses (+14.5, ±14.5)
    anchor_coords = [
        (14.5, 14.5, -4.5),     # NE Cliff-Edge Pinnacle Buttress
        (-19.5, 19.5, -1.8),    # NW Upland Terrace Bollard
        (-19.5, -19.5, -1.6),   # SW Upland Terrace Bollard
        (14.5, -14.5, -4.5),    # SE Cliff-Edge Pinnacle Buttress
    ]
    for ax, ay, az in anchor_coords:
        add_prism(
            mesh,
            cx=ax,
            cy=ay,
            rad=2.8,
            z_bot=-48.0,
            z_top=az,
            sides=6,
            rot_rad=0.3,
            taper=1.08,
            mat_top=MATERIALS["steel_dark"],
        )
        add_box(mesh, ax - 0.65, ay - 0.65, az, ax + 0.65, ay + 0.65, az + 1.1, MATERIALS["steel"])
        add_ring_torus(mesh, ax, ay, az + 1.15, 0.35, 0.08, MATERIALS["brass"], segs=12, tube_sides=6)

    # ── 7. Bogey-9 Perimeter Trail-Cam Tripods (TRL-01..03) overlooking the Cliff & Chasm ──
    trail_cams = [
        (14.5, 14.5, -3.4, "TRL-01"),   # NE Cliff Pinnacle Sentinel
        (-25.0, 18.0, -1.8, "TRL-02"),  # NW Upland Ridge Sentinel
        (4.5, -15.5, -1.8, "TRL-03"),   # South Cliff Lip Sentinel
    ]
    for tx, ty, tz, _label in trail_cams:
        for leg_i in range(3):
            la = 2.0 * math.pi * leg_i / 3.0
            add_strut(
                mesh,
                (tx + 0.9 * math.cos(la), ty + 0.9 * math.sin(la), tz - 0.4),
                (tx, ty, tz + 1.6),
                0.04,
                MATERIALS["steel_light"],
                sides=6,
            )
        add_strut(mesh, (tx, ty, tz + 1.4), (tx, ty, tz + 2.8), 0.05, MATERIALS["steel"], sides=6)
        add_box(mesh, tx - 0.32, ty - 0.22, tz + 2.6, tx + 0.32, ty + 0.22, tz + 3.05, MATERIALS["desk_hull"])
        add_box(mesh, tx - 0.12, ty - 0.12, tz + 3.05, tx + 0.12, ty + 0.12, tz + 3.28, MATERIALS["crimson_glow"])

    return grp
