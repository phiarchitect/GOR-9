"""
Component: Prismatic Columnar-Basalt Monolith & Acheron Chasm (Asteroid 3-5-1)
==============================================================================
Models Asteroid 3-5-1 as a 330-meter-tall hierarchical "Prism of Prisms of Prisms"
of volcanic columnar basalt:
  - Station GOR-9 crowns the highest apex (Z = 0.0m) of the entire prismatic
    asteroid monolith, which plunges 330m down into deep space (Z = -330.0m).
  - Each Large Pillar (Macro-Prism, R = 10.5m .. 16.5m) is constructed as a
    tightly-packed hexagonal lattice assembly of 7 to 19 smaller hexagonal
    basalt pillars that share mostly the same height on each large pillar
    (forming a coherent faceted plateau on each macro-pillar), ringed by a
    3rd scale of slender hexagonal micro-ribs along the outer faces.
  - Concentric stepped macro-pillar rings descend around the Station Crown
    (Tier 0 Crown -> Tier 1 Upper Shoulders -> Tier 2 Mid Palisades ->
    Tier 3 Outer Buttresses -> Tier 4 Deep Ventral Root), while maintaining a
    sheer 50m vertical cliff drop on the East/SE Acheron Chasm face.
"""

import math
from .primitives import (
    MATERIALS,
    add_box,
    add_prism,
    add_ring_torus,
    add_strut,
    create_scene_group,
    with_channel,
)


BASALT_SIDE_COUNTS = (6, 5, 3, 6, 5, 6, 3, 5)
MICRO_SIDE_COUNTS = (5, 3, 6, 5, 3, 6)


def add_macro_basalt_pillar(
    mesh,
    cx: float,
    cy: float,
    macro_rad: float,
    z_bot: float,
    z_top: float,
    hex_rings: int = 2,
    rot_rad: float = 0.0,
    is_flat_terrace: bool = False,
    with_micro_ribs: bool = True,
):
    """
    Build a Large Pillar (Macro-Prism) as an organic Voronoi-like bundle of
    smaller 3-, 5-, and 6-sided basalt pillars (`hex_rings = 2` -> 19 smaller pillars;
    `hex_rings = 1` -> 7 smaller pillars), with randomized column sizes, unequal side
    lengths, and mostly the same height across each Large Pillar plateau, plus a 3rd
    scale of slender 3-, 5-, and 6-sided micro-ribs on the outer perimeter.
    """
    macro_seed = abs(int(cx * 197 + cy * 353 + z_top * 89)) & 0xFFFF
    macro_scale = 0.92 + ((macro_seed % 100) / 100.0) * 0.16
    macro_aspect_x = 0.88 + (((macro_seed >> 4) % 100) / 100.0) * 0.24
    macro_aspect_y = 1.0 / macro_aspect_x
    sub_rad = ((macro_rad * macro_scale) / (2 * hex_rings + 0.82)) * 1.08
    pitch = sub_rad * 1.58
    cos_r = math.cos(rot_rad)
    sin_r = math.sin(rot_rad)
    mats = [MATERIALS["basalt"], MATERIALS["basalt_rim"], MATERIALS["basalt_dark"]]

    for q in range(-hex_rings, hex_rings + 1):
        for r in range(-hex_rings, hex_rings + 1):
            s = -q - r
            h_ring = max(abs(q), abs(r), abs(s))
            if h_ring > hex_rings:
                continue

            cell_hash = (macro_seed + (q + 4) * 313 + (r + 4) * 619 + (q * r) * 109) & 0xFFFF
            j01 = (cell_hash % 100) / 100.0
            j02 = ((cell_hash >> 5) % 100) / 100.0
            j03 = ((cell_hash >> 9) % 100) / 100.0

            lx = (pitch * (q + r * 0.5) + (j02 - 0.5) * sub_rad * 0.34) * macro_aspect_x
            ly = (pitch * (r * 0.8660254) + (j03 - 0.5) * sub_rad * 0.34) * macro_aspect_y
            wx = cx + lx * cos_r - ly * sin_r
            wy = cy + lx * sin_r + ly * cos_r

            if is_flat_terrace:
                sub_z_top = z_top - h_ring * 0.05 - j01 * 0.14
            else:
                sub_z_top = z_top + (j01 - 0.5) * 1.15 - h_ring * 0.25
                if h_ring == hex_rings and (cell_hash % 6 == 0):
                    sub_z_top -= 2.6 + j02 * 3.2

            sub_z_bot = z_bot + h_ring * 9.5 + (j02 - 0.5) * 14.0
            if h_ring == 0:
                sides = 6 if (cell_hash % 2 == 0) else 5
            else:
                sides = BASALT_SIDE_COUNTS[(cell_hash + q * 3 + r * 5) & 7]
            side_area_comp = 1.22 if sides == 3 else (1.05 if sides == 5 else 1.0)
            col_rad = sub_rad * (0.78 + 0.44 * j01) * side_area_comp
            col_mat = MATERIALS["basalt_rim"] if h_ring == 0 else mats[(cell_hash + h_ring) % 3]
            col_rot = rot_rad + j03 * math.pi * 2.0

            add_prism(
                mesh,
                cx=wx,
                cy=wy,
                rad=col_rad,
                z_bot=sub_z_bot,
                z_top=sub_z_top,
                sides=sides,
                rot_rad=col_rot,
                taper=0.98,
                mat_top=col_mat,
            )

            if with_micro_ribs and h_ring == hex_rings and ((q - r + cell_hash) % 2 == 0):
                out_len = math.hypot(lx, ly) or 1.0
                ox = wx + ((lx / out_len) * cos_r - (ly / out_len) * sin_r) * (sub_rad * (0.64 + 0.22 * j02))
                oy = wy + ((lx / out_len) * sin_r + (ly / out_len) * cos_r) * (sub_rad * (0.64 + 0.22 * j02))
                micro_top = sub_z_top - (3.2 + j01 * 4.5 if is_flat_terrace else 1.8 + j01 * 3.8)
                micro_bot = sub_z_bot + 18.0 + j02 * 14.0
                micro_sides = MICRO_SIDE_COUNTS[(cell_hash >> 3) % 6]
                micro_area_comp = 1.24 if micro_sides == 3 else (1.06 if micro_sides == 5 else 1.0)
                if micro_top - micro_bot > 12.0:
                    add_prism(
                        mesh,
                        cx=ox,
                        cy=oy,
                        rad=sub_rad * (0.38 + 0.20 * j03) * micro_area_comp,
                        z_bot=micro_bot,
                        z_top=micro_top,
                        sides=micro_sides,
                        rot_rad=col_rot + 0.4,
                        taper=0.99,
                        mat_top=MATERIALS["basalt_dark"] if (cell_hash % 2 == 0) else MATERIALS["basalt"],
                    )


def build_prismatic_basalt_terrain(scene):
    grp = create_scene_group(scene, "01_Basalt_Promontory_Terrain")
    mesh = grp.mesh

    # ── TIER 0: SUMMIT CROWN & HEADLAND COMPOUND MACRO-PILLARS (Z_top = -0.45m .. -3.40m, Z_bot = -255m .. -330m) ──
    # 0A. Central Apex Macro-Pillar Directly Supporting Station GOR-9 (Z = -0.45m down to -330.0m!)
    add_macro_basalt_pillar(
        mesh,
        cx=0.0,
        cy=0.0,
        macro_rad=12.6,
        z_bot=-330.0,
        z_top=-0.45,
        hex_rings=2,
        rot_rad=0.0,
        is_flat_terrace=True,
        with_micro_ribs=True,
    )

    # Sheer East/SE/NE Acheron Chasm Cliff-Face Organ-Pipe Ribs (3-, 5-, and 6-sided irregular ribs clinging to the 50m drop)
    cliff_ribs = [
        (10.8, 0.0, 2.7, -11.5, -240.0, 5),
        (10.2, -4.8, 2.4, -14.0, -230.0, 6),
        (10.2, 4.8, 2.8, -13.0, -230.0, 3),
        (12.4, -2.4, 2.1, -23.5, -210.0, 5),
        (12.4, 2.4, 2.5, -25.0, -210.0, 6),
        (11.5, -7.6, 2.6, -19.0, -215.0, 3),
        (11.5, 7.6, 2.3, -21.0, -215.0, 5),
        (14.0, 0.0, 2.3, -34.0, -195.0, 3),
        (13.6, -5.2, 1.9, -36.5, -190.0, 6),
        (13.6, 5.2, 2.2, -35.5, -190.0, 5),
    ]
    for idx, (cx, cy, rad, z_top, z_bot, sides) in enumerate(cliff_ribs):
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=rad,
            z_bot=z_bot,
            z_top=z_top,
            sides=sides,
            rot_rad=idx * 0.47,
            taper=0.98,
            mat_top=MATERIALS["basalt_rim"] if (idx % 2 == 0) else MATERIALS["basalt"],
        )

    # 0B. Surrounding Headland Compound Macro-Pillars (note: Three.js +Z = South = Ingetrazo -Y)
    crown_compound_macro_pillars = [
        (-15.2, -6.5, 12.2, -300.0, -1.60, 2, 0.12),   # SW Keeper's Habitat Plateau Macro-Pillar
        (-15.2, 11.8, 12.4, -300.0, -1.80, 2, 0.28),   # NW Dilithium Reactor #2 & Switchyard Macro-Pillar
        (-24.8, 2.2, 11.4, -285.0, -1.95, 2, 0.42),    # West Headland Spine Macro-Pillar
        (-20.8, 18.5, 10.6, -275.0, -1.75, 2, 0.18),   # NW Guy-Wire & Trail-Cam Macro-Pillar
        (-20.0, -18.2, 10.6, -275.0, -1.70, 2, 0.35),  # SW Guy-Wire Macro-Pillar
        (-1.5, -15.2, 11.0, -280.0, -1.80, 2, 0.22),   # South Cryo-Condenser & Winch Shoulder Macro-Pillar
        (-2.0, 15.6, 10.5, -275.0, -2.10, 2, 0.08),    # North Rim Shoulder Macro-Pillar
        (13.5, 13.8, 8.4, -255.0, -3.40, 1, 0.30),     # NE Cliff-Edge Guy-Wire Pinnacle Macro-Pillar
        (13.5, -13.8, 8.4, -255.0, -3.40, 1, 0.15),    # SE Cliff-Edge Guy-Wire Pinnacle Macro-Pillar
    ]
    for cx, cy, m_rad, z_bot, z_top, rings, rot in crown_compound_macro_pillars:
        add_macro_basalt_pillar(
            mesh,
            cx=cx,
            cy=cy,
            macro_rad=m_rad,
            z_bot=z_bot,
            z_top=z_top,
            hex_rings=rings,
            rot_rad=rot,
            is_flat_terrace=True,
            with_micro_ribs=True,
        )

    # ── TIER 1: UPPER PRISMATIC SHOULDER RING OF LARGE PILLARS (12 Macro-Pillars, R = 36m .. 48m) ──
    tier1_macro_pillars = [
        (34.0, 0.0, 13.5, -260.0, -49.5, 2, 0.10),
        (31.0, -19.5, 13.2, -255.0, -46.0, 2, 0.28),
        (31.0, 19.5, 13.2, -255.0, -47.0, 2, 0.44),
        (14.0, -34.5, 14.2, -265.0, -14.5, 2, 0.18),
        (14.0, 34.5, 14.2, -265.0, -15.5, 2, 0.36),
        (-8.0, -37.0, 14.6, -270.0, -11.5, 2, 0.52),
        (-8.0, 37.0, 14.6, -270.0, -12.5, 2, 0.08),
        (-29.5, -31.0, 14.8, -275.0, -10.5, 2, 0.24),
        (-29.5, 31.0, 14.8, -275.0, -11.0, 2, 0.40),
        (-43.0, -14.5, 15.2, -280.0, -13.5, 2, 0.15),
        (-43.0, 14.5, 15.2, -280.0, -14.0, 2, 0.33),
        (-46.5, 0.0, 15.0, -285.0, -16.0, 2, 0.48),
    ]
    for cx, cy, m_rad, z_bot, z_top, rings, rot in tier1_macro_pillars:
        add_macro_basalt_pillar(
            mesh,
            cx=cx,
            cy=cy,
            macro_rad=m_rad,
            z_bot=z_bot,
            z_top=z_top,
            hex_rings=rings,
            rot_rad=rot,
            is_flat_terrace=False,
            with_micro_ribs=True,
        )

    # ── TIER 2: MID-MONOLITH HEXAGONAL PALISADE RING (16 Macro-Pillars, R = 58m .. 76m) ──
    for i in range(16):
        ang_deg = (360.0 * i) / 16.0
        ang = math.radians(ang_deg)
        is_chasm = ang_deg < 48.0 or ang_deg > 312.0
        is_shoulder = (48.0 <= ang_deg < 85.0) or (275.0 < ang_deg <= 312.0)
        dist = (58.0 if is_chasm else 66.0) + (i % 3) * 4.2
        cx = dist * math.cos(ang) - 6.0
        cy = dist * math.sin(ang)
        m_rad = 14.2 + (i % 3) * 1.4
        if is_chasm:
            z_top = -62.0 - (i % 3) * 4.5
        elif is_shoulder:
            z_top = -26.0 - (i % 3) * 5.0
        else:
            z_top = -30.0 - (i % 4) * 5.5
        z_bot = -210.0 - (i % 4) * 14.0
        add_macro_basalt_pillar(
            mesh,
            cx=cx,
            cy=cy,
            macro_rad=m_rad,
            z_bot=z_bot,
            z_top=z_top,
            hex_rings=2,
            rot_rad=ang * 0.5 + 0.12,
            is_flat_terrace=False,
            with_micro_ribs=True,
        )

    # ── TIER 3: OUTER PRISMATIC BUTTRESS SKIRT RING (18 Macro-Pillars, R = 84m .. 104m) ──
    for i in range(18):
        ang_deg = (360.0 * i) / 18.0 + 10.0
        ang = math.radians(ang_deg)
        is_chasm = ang_deg < 52.0 or ang_deg > 308.0
        dist = (82.0 if is_chasm else 90.0) + (i % 3) * 5.0
        cx = dist * math.cos(ang) - 8.0
        cy = dist * math.sin(ang)
        m_rad = 12.8 + (i % 3) * 1.3
        z_top = (-78.0 - (i % 3) * 6.0) if is_chasm else (-54.0 - (i % 4) * 7.5)
        z_bot = -150.0 - (i % 4) * 12.0
        add_macro_basalt_pillar(
            mesh,
            cx=cx,
            cy=cy,
            macro_rad=m_rad,
            z_bot=z_bot,
            z_top=z_top,
            hex_rings=1,
            rot_rad=ang * 0.35,
            is_flat_terrace=False,
            with_micro_ribs=True,
        )

    # ── TIER 4: DEEP VENTRAL ROOT PRISM ASSEMBLIES (Extending the Central Monolith Core down to Z = -325m) ──
    for k in range(6):
        ka = (2.0 * math.pi * k) / 6.0 + math.pi / 6.0
        dist = 24.0 + (k % 2) * 8.0
        rx = math.cos(ka) * dist - 6.0
        ry = math.sin(ka) * dist
        root_bot = -325.0 + (k % 3) * 14.0
        add_macro_basalt_pillar(
            mesh,
            cx=rx,
            cy=ry,
            macro_rad=13.5,
            z_bot=root_bot,
            z_top=-75.0,
            hex_rings=1,
            rot_rad=ka,
            is_flat_terrace=False,
            with_micro_ribs=True,
        )

    # ── TIER 5: FLANKING DETACHED PRISMATIC SEA-STACK MONOLITHS IN CHASM ABYSS ──
    sea_stacks = [
        (114.0, 64.0, 11.5, -185.0, -42.0, 1),
        (122.0, -62.0, 12.0, -195.0, -46.0, 1),
        (86.0, 96.0, 10.8, -175.0, -38.0, 1),
        (74.0, -102.0, 11.2, -180.0, -40.0, 1),
    ]
    for idx, (cx, cy, m_rad, z_bot, z_top, rings) in enumerate(sea_stacks):
        add_macro_basalt_pillar(
            mesh,
            cx=cx,
            cy=cy,
            macro_rad=m_rad,
            z_bot=z_bot,
            z_top=z_top,
            hex_rings=rings,
            rot_rad=idx * 0.4,
            is_flat_terrace=False,
            with_micro_ribs=True,
        )

    # ── 6. Reinforced Octagonal Concrete & Steel Cliff-Edge Foundation Pad (Z = -0.45m .. +0.35m) ──
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

    hazard_amber = with_channel(MATERIALS["amber_glow"], "hazard_beacons")
    hazard_crimson = with_channel(MATERIALS["crimson_glow"], "hazard_beacons")
    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0 + math.pi / 8.0
        bx, by = 8.8 * math.cos(ang), 8.8 * math.sin(ang)
        add_box(mesh, bx - 0.18, by - 0.18, 0.0, bx + 0.18, by + 0.18, 0.35, MATERIALS["steel_dark"])
        add_box(mesh, bx - 0.12, by - 0.12, 0.35, bx + 0.12, by + 0.12, 0.56, hazard_amber)

    # ── 7. Four Guy-Wire Basalt Anchor Bollards ──
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
            z_bot=-54.0,
            z_top=az,
            sides=6,
            rot_rad=0.3,
            taper=0.92,
            mat_top=MATERIALS["steel_dark"],
        )
        add_box(mesh, ax - 0.65, ay - 0.65, az, ax + 0.65, ay + 0.65, az + 1.1, MATERIALS["steel"])
        add_ring_torus(mesh, ax, ay, az + 1.15, 0.35, 0.08, MATERIALS["brass"], segs=12, tube_sides=6)

    # ── 8. Bogey-9 Perimeter Trail-Cam Tripods (TRL-01..03) overlooking the Cliff & Chasm ──
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
        add_box(mesh, tx - 0.12, ty - 0.12, tz + 3.05, tx + 0.12, ty + 0.12, tz + 3.28, hazard_crimson)

    return grp
