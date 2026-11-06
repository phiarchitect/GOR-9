#!/usr/bin/env python3
"""
Build the complete 3D Relay Station GOR-9 Tower, Concentric Marzelvane Emitter
Array & Octagonal Broadcast Booth in IngeTrazo 0.6.0 (headless or live via TCP
bridge 127.0.0.1:4763).

Architecture & Features Included:
  1. Asteroid 3-5-1 Columnar Basalt Cliff Shelf ("Acheron Polar Chasm")
  2. Continuous Tapered Open-Lattice Steel Tower (z = 0m to +52m) running
     UNINTERRUPTED right through the floor and ceiling of the Octagonal Booth,
     including the 4 heavy corner legs, horizontal girts, diagonal X-bracing,
     and continuous central octagonal waveguide/elevator core column.
  3. Cantilevered Octagonal ATC Broadcast Booth (z = +16m to +21.8m)
     with 360-degree wraparound catwalk, safety railings, outward-canting
     trapezoidal observation windows (z_sill = +1.56m to z_eave = +4.35m),
     interior ceiling trusses, and rooftop "GOR-9" neon sign.
  4. Perimeter Standup-Height Broadcast Consoles (z_desk = +1.05m) mounted
     around the OUTSIDE WALLS of the octagon, tucked directly under the
     panoramic window sills (z = +1.05m to +1.55m), with 1:1 UV-fitted
     textures for all GOR-9 interfaces:
       - North Wall (Center):      Hauser MK-IV Wideband Correlator + Decoder
       - North-East Wall (Stbd 1): Van Allen VA-4 Propagation + Galactic Atlas
       - East Wall (Stbd 2):       Van Allen ED-9 Euclidean Detector
       - South-East Wall (Stbd 3): Hauser Bogey-9 Perimeter Trail-Cam & UAP
       - North-West Wall (Port 1): Station Dossier & 2-Sided QSL Collector View
       - West Wall (Port 2):       3D Spectrum Scan & Comet C/2184-K2 Telemetry
       - South-West Wall (Port 3): Dilithium Step-Down & Rhombus Preview
  5. Master Broadcast Operator Station & Rolling Stools:
       - Articulated studio boom microphone with glowing crimson "ON AIR • 0400 GCT"
         tally ring on the North standup desk with generous space around the mic
       - Open Station Logbook, 2-Sided eQSL Cards, Brass Morse Key ("GO-9 SWL 1978"),
         Weighted Barycentric VFO Jog Wheel, and "GALACTIC OUTPOST 9" Mug
       - 3 Tall Rolling Broadcast/Drafting Stools with chrome foot-rings and 5-caster bases
"""

import argparse
import math
import os
import sys
from pathlib import Path

INGETRAZO_ROOT = Path("/home/phi/PROJECTS/phi-WORKS/ingetrazo")
if str(INGETRAZO_ROOT) not in sys.path:
    sys.path.insert(0, str(INGETRAZO_ROOT))
if str(INGETRAZO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(INGETRAZO_ROOT / "scripts"))


def build_gor9_scene(scene, repo_root: Path):
    """Populate an IngeTrazo Scene with the complete GOR-9 Tower, Marzelvane Emitters & Perimeter Standup Broadcast Booth."""
    from PySide6.QtGui import QVector3D
    from core.mesh import Mesh
    from core.group import Group
    from core.texture import fit_uv_affine

    # Keep the Engineer scale figure if present, or reposition at the North standup desk
    engineer_group = None
    for g in list(scene.groups):
        if getattr(g, "is_guide", False) or g.name == "Engineer":
            engineer_group = g
            break

    scene.clear()
    consoles_dir = repo_root / "docs" / "assets" / "consoles"
    plates_dir = repo_root / "docs" / "assets" / "plates"

    # Booth elevation floor
    BOOTH_Z = 16.0

    # ── Helper Primitives ─────────────────────────────────────────────
    def _add_face(mesh: Mesh, pts, attrs: dict):
        f = mesh.add_face(pts)
        if f is not None and attrs:
            f.attrs.update(attrs)
        return f

    def add_quad(mesh: Mesh, p0, p1, p2, p3, attrs: dict):
        _add_face(
            mesh,
            [QVector3D(*p0), QVector3D(*p1), QVector3D(*p2), QVector3D(*p3)],
            dict(attrs),
        )

    def add_textured_quad(
        mesh: Mesh,
        p0,
        p1,
        p2,
        p3,
        tex_path: Path,
        color=(0.95, 0.98, 1.0),
        emissive=True,
    ):
        """Add a quad with an exact 1:1 fitted affine UV map (p0=BL, p1=BR, p2=TR, p3=TL)."""
        pts = [QVector3D(*p0), QVector3D(*p1), QVector3D(*p2), QVector3D(*p3)]
        attrs = {"color": color, "emissive": emissive}
        if tex_path and tex_path.exists():
            uvw = fit_uv_affine(
                pts,
                [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
            )
            tex_dict = {"path": str(tex_path), "sw": 1.0, "sh": 1.0}
            if uvw:
                tex_dict["uvw"] = uvw
            attrs["texture"] = tex_dict
        _add_face(mesh, pts, attrs)

    def add_box(mesh: Mesh, x0, y0, z0, x1, y1, z1, attrs: dict):
        p000 = (x0, y0, z0)
        p100 = (x1, y0, z0)
        p110 = (x1, y1, z0)
        p010 = (x0, y1, z0)
        p001 = (x0, y0, z1)
        p101 = (x1, y0, z1)
        p111 = (x1, y1, z1)
        p011 = (x0, y1, z1)
        add_quad(mesh, p000, p010, p110, p100, attrs)  # bottom
        add_quad(mesh, p001, p101, p111, p011, attrs)  # top
        add_quad(mesh, p000, p100, p101, p001, attrs)  # south (-Y)
        add_quad(mesh, p100, p110, p111, p101, attrs)  # east (+X)
        add_quad(mesh, p110, p010, p011, p111, attrs)  # north (+Y)
        add_quad(mesh, p010, p000, p001, p011, attrs)  # west (-X)

    def add_strut(mesh: Mesh, p_start, p_end, radius: float, attrs: dict, sides: int = 6):
        ax, ay, az = p_start
        bx, by, bz = p_end
        dx, dy, dz = bx - ax, by - ay, bz - az
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length < 1e-5:
            return
        ux, uy, uz = dx / length, dy / length, dz / length
        if abs(uz) < 0.9:
            rx, ry, rz = -uy, ux, 0.0
        else:
            rx, ry, rz = 0.0, -uz, uy
        rl = math.sqrt(rx * rx + ry * ry + rz * rz)
        rx, ry, rz = rx / rl, ry / rl, rz / rl
        sx = uy * rz - uz * ry
        sy = uz * rx - ux * rz
        sz = ux * ry - uy * rx

        ring_a = []
        ring_b = []
        for i in range(sides):
            ang = 2.0 * math.pi * i / sides
            ca, sa = math.cos(ang), math.sin(ang)
            ox = radius * (ca * rx + sa * sx)
            oy = radius * (ca * ry + sa * sy)
            oz = radius * (ca * rz + sa * sz)
            ring_a.append((ax + ox, ay + oy, az + oz))
            ring_b.append((bx + ox, by + oy, bz + oz))

        for i in range(sides):
            ni = (i + 1) % sides
            add_quad(mesh, ring_a[i], ring_a[ni], ring_b[ni], ring_b[i], attrs)
        _add_face(mesh, [QVector3D(*p) for p in reversed(ring_a)], dict(attrs))
        _add_face(mesh, [QVector3D(*p) for p in ring_b], dict(attrs))

    def add_ring_torus(
        mesh: Mesh,
        cx,
        cy,
        cz,
        major_r: float,
        minor_r: float,
        attrs: dict,
        segs: int = 36,
        tube_sides: int = 8,
    ):
        rings = []
        for i in range(segs):
            theta = 2.0 * math.pi * i / segs
            ct, st = math.cos(theta), math.sin(theta)
            loop = []
            for j in range(tube_sides):
                phi = 2.0 * math.pi * j / tube_sides
                cp, sp = math.cos(phi), math.sin(phi)
                r = major_r + minor_r * cp
                x = cx + r * ct
                y = cy + r * st
                z = cz + minor_r * sp
                loop.append((x, y, z))
            rings.append(loop)
        for i in range(segs):
            ni = (i + 1) % segs
            for j in range(tube_sides):
                nj = (j + 1) % tube_sides
                add_quad(
                    mesh,
                    rings[i][j],
                    rings[ni][j],
                    rings[ni][nj],
                    rings[i][nj],
                    attrs,
                )

    # ── Materials ─────────────────────────────────────────────────────
    mat_basalt = {"color": (0.14, 0.16, 0.20), "roughness": 0.92, "metallic": 0.08}
    mat_basalt_dark = {"color": (0.09, 0.10, 0.13), "roughness": 0.95, "metallic": 0.05}
    mat_steel = {"color": (0.28, 0.32, 0.38), "roughness": 0.45, "metallic": 0.78}
    mat_steel_dark = {"color": (0.16, 0.19, 0.23), "roughness": 0.50, "metallic": 0.80}
    mat_brass = {"color": (0.76, 0.56, 0.24), "roughness": 0.30, "metallic": 0.88}
    mat_amber_glow = {"color": (1.00, 0.65, 0.18), "emissive": True}
    mat_cyan_glow = {"color": (0.22, 0.92, 1.00), "emissive": True}
    mat_cyan_core = {"color": (0.65, 0.98, 1.00), "emissive": True}
    mat_crimson_glow = {"color": (1.00, 0.18, 0.14), "emissive": True}
    mat_neon_sign = {"color": (1.00, 0.52, 0.12), "emissive": True}
    mat_booth_floor = {"color": (0.13, 0.15, 0.18), "roughness": 0.65, "metallic": 0.35}
    mat_desk_hull = {"color": (0.19, 0.22, 0.26), "roughness": 0.48, "metallic": 0.68}
    mat_desk_trim = {"color": (0.11, 0.13, 0.16), "roughness": 0.40, "metallic": 0.72}
    mat_glass = {
        "color": (0.35, 0.62, 0.78),
        "opacity": 0.16,
        "roughness": 0.10,
        "metallic": 0.10,
    }

    # ══════════════════════════════════════════════════════════════════
    # 1. ASTEROID 3-5-1 COLUMNAR BASALT CLIFF ("ACHERON POLAR CHASM")
    # ══════════════════════════════════════════════════════════════════
    basalt_mesh = Mesh()
    columns = [
        (0.0, 0.0, 12.5, -18.0, 0.0, 8),
        (-9.0, -5.0, 7.2, -22.0, -1.2, 6),
        (9.5, -4.5, 6.8, -21.0, -0.8, 6),
        (-7.5, 8.0, 7.0, -24.0, -1.5, 6),
        (8.0, 7.5, 7.5, -23.0, -1.0, 6),
        (-16.0, 1.5, 6.5, -26.0, -3.5, 6),
        (16.5, 1.0, 6.2, -26.0, -3.2, 6),
        (0.0, -14.0, 7.0, -25.0, -2.5, 6),
        (0.0, 14.5, 6.5, -28.0, -4.0, 6),
    ]
    for cx, cy, rad, z_bot, z_top, sides in columns:
        top_pts = []
        bot_pts = []
        for i in range(sides):
            ang = 2.0 * math.pi * i / sides + 0.25
            px = cx + rad * math.cos(ang)
            py = cy + rad * math.sin(ang)
            top_pts.append((px, py, z_top))
            bot_pts.append((px * 1.12, py * 1.12, z_bot))
        for i in range(sides):
            ni = (i + 1) % sides
            shade = mat_basalt if (i % 2 == 0) else mat_basalt_dark
            add_quad(basalt_mesh, bot_pts[i], bot_pts[ni], top_pts[ni], top_pts[i], shade)
        _add_face(basalt_mesh, [QVector3D(*p) for p in top_pts], dict(mat_basalt))

    # Concrete & steel anchor pad at z = 0
    pad_r = 7.4
    pad_pts_b = []
    pad_pts_t = []
    for i in range(8):
        ang = 2.0 * math.pi * i / 8 + math.pi / 8
        pad_pts_b.append((pad_r * math.cos(ang), pad_r * math.sin(ang), -0.4))
        pad_pts_t.append((pad_r * 0.95 * math.cos(ang), pad_r * 0.95 * math.sin(ang), 0.35))
    for i in range(8):
        ni = (i + 1) % 8
        add_quad(basalt_mesh, pad_pts_b[i], pad_pts_b[ni], pad_pts_t[ni], pad_pts_t[i], mat_steel_dark)
    _add_face(basalt_mesh, [QVector3D(*p) for p in pad_pts_t], dict(mat_steel_dark))
    scene.groups.append(Group(name="1_Asteroid_351_Basalt_Crag", mesh=basalt_mesh))

    # ══════════════════════════════════════════════════════════════════
    # 2. CONTINUOUS STEEL LATTICE TOWER STRUCTURE (z = 0.0m to +52.0m)
    #    Runs UNINTERRUPTED right through the floor and ceiling of the
    #    Octagonal Broadcast Booth!
    # ══════════════════════════════════════════════════════════════════
    tower_mesh = Mesh()
    tower_levels = [
        (0.0, 4.20),
        (4.0, 3.60),
        (8.0, 3.05),
        (12.0, 2.55),
        (BOOTH_Z, 2.10),        # Booth floor (z = 16.0m)
        (BOOTH_Z + 2.6, 1.88),  # Mid-booth structural truss ring (z = 18.6m)
        (BOOTH_Z + 5.2, 1.68),  # Booth roof ceiling penetration (z = 21.2m)
        (26.0, 1.45),
        (31.0, 1.25),
        (36.0, 1.05),
        (41.0, 0.88),
        (46.5, 0.72),           # Marzelvane Emitter Hub
        (52.0, 0.52),
    ]
    for lv_idx in range(len(tower_levels) - 1):
        z0, r0 = tower_levels[lv_idx]
        z1, r1 = tower_levels[lv_idx + 1]
        in_booth = (z0 >= BOOTH_Z - 0.1) and (z1 <= BOOTH_Z + 5.3)
        leg_rad = 0.19 if z0 < BOOTH_Z else (0.135 if in_booth else 0.14)
        girt_rad = 0.13 if z0 < BOOTH_Z else (0.085 if in_booth else 0.09)
        diag_rad = 0.095 if z0 < BOOTH_Z else (0.060 if in_booth else 0.07)

        corners0 = [(r0 * sx, r0 * sy, z0) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        corners1 = [(r1 * sx, r1 * sy, z1) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        for i in range(4):
            ni = (i + 1) % 4
            # Continuous 4 main corner legs
            add_strut(tower_mesh, corners0[i], corners1[i], leg_rad, mat_steel)
            # Horizontal perimeter girts
            add_strut(tower_mesh, corners1[i], corners1[ni], girt_rad, mat_steel_dark)
            # Continuous X-bracing diagonals on all 4 tower faces
            add_strut(tower_mesh, corners0[i], corners1[ni], diag_rad, mat_steel_dark)
            add_strut(tower_mesh, corners0[ni], corners1[i], diag_rad, mat_steel_dark)

    # Continuous central octagonal waveguide & helical bus column from z = 0m through booth to z = 44m
    add_strut(tower_mesh, (0.0, 0.0, 0.0), (0.0, 0.0, 44.0), 0.24, mat_steel_dark, sides=8)
    # Glowing vertical Cherenkov waveguide bus conduits along the 4 cardinal faces of the core inside the booth
    for ang_deg in (0, 90, 180, 270):
        rad_a = math.radians(ang_deg)
        wx, wy = 0.28 * math.cos(rad_a), 0.28 * math.sin(rad_a)
        add_strut(tower_mesh, (wx, wy, BOOTH_Z), (wx, wy, BOOTH_Z + 5.2), 0.025, mat_cyan_glow, sides=6)

    # Two intermediate circular waveguide exciter collars above the booth (z = 33.0m, 38.5m)
    for exc_z, exc_r in [(33.0, 3.2), (38.5, 2.6)]:
        add_ring_torus(tower_mesh, 0.0, 0.0, exc_z, exc_r, 0.16, mat_steel, segs=24, tube_sides=6)
        add_ring_torus(tower_mesh, 0.0, 0.0, exc_z + 0.18, exc_r, 0.08, mat_cyan_glow, segs=24, tube_sides=6)
        for sp_i in range(8):
            ang = 2.0 * math.pi * sp_i / 8
            add_strut(
                tower_mesh,
                (0.0, 0.0, exc_z),
                (exc_r * math.cos(ang), exc_r * math.sin(ang), exc_z),
                0.06,
                mat_steel_dark,
            )

    # Central Cherenkov spire above mast (z = +44m to +57.5m)
    add_strut(tower_mesh, (0.0, 0.0, 44.0), (0.0, 0.0, 56.5), 0.24, mat_steel, sides=8)
    add_strut(tower_mesh, (0.0, 0.0, 53.0), (0.0, 0.0, 57.5), 0.15, mat_cyan_core, sides=8)

    # Aviation hazard beacons + 4 tensioned guy-wires to basalt anchors
    for bz in (28.0, 41.0, 52.0):
        add_box(tower_mesh, -0.38, -0.38, bz - 0.30, 0.38, 0.38, bz + 0.30, mat_crimson_glow)
    anchors = [(-14.5, -11.5, -1.5), (14.5, -11.5, -1.2), (13.5, 12.5, -1.8), (-13.5, 12.5, -1.6)]
    for idx, (ax, ay, az) in enumerate(anchors):
        sx = -1 if idx in (0, 3) else 1
        sy = -1 if idx in (0, 1) else 1
        add_strut(tower_mesh, (ax, ay, az), (1.05 * sx, 1.05 * sy, 36.0), 0.045, mat_steel_dark, sides=4)
        add_box(tower_mesh, ax - 0.5, ay - 0.5, az - 0.4, ax + 0.5, ay + 0.5, az + 0.7, mat_brass)

    scene.groups.append(Group(name="2_Continuous_Steel_Lattice_Tower", mesh=tower_mesh))

    # ══════════════════════════════════════════════════════════════════
    # 3. CANTILEVERED OCTAGONAL ATC BROADCAST BOOTH (z = +16.0m to +21.8m)
    #    Window sill at z = BOOTH_Z + 1.56m so the standup consoles sit
    #    snugly around the outside walls just under the windows!
    # ══════════════════════════════════════════════════════════════════
    booth_mesh = Mesh()
    z_floor = BOOTH_Z
    z_sill = BOOTH_Z + 1.56
    z_eave = BOOTH_Z + 4.40
    z_roof = BOOTH_Z + 5.20

    catwalk_r = 7.45
    booth_r_floor = 5.60
    booth_r_sill = 5.82
    booth_r_eave = 6.60
    booth_r_roof = 6.95

    def oct_ring(radius, z):
        pts = []
        for i in range(8):
            ang = 2.0 * math.pi * i / 8 + math.pi / 8
            pts.append((radius * math.cos(ang), radius * math.sin(ang), z))
        return pts

    cw_bot = oct_ring(catwalk_r, z_floor - 0.28)
    cw_top = oct_ring(catwalk_r, z_floor)
    fl_top = oct_ring(booth_r_floor, z_floor + 0.04)
    sill_ring = oct_ring(booth_r_sill, z_sill)
    eave_ring = oct_ring(booth_r_eave, z_eave)
    roof_ring = oct_ring(booth_r_roof, z_roof)
    roof_cap = oct_ring(2.38, z_roof + 0.42)

    for i in range(8):
        ni = (i + 1) % 8
        add_quad(booth_mesh, cw_bot[i], cw_bot[ni], cw_top[ni], cw_top[i], mat_steel_dark)
        add_quad(booth_mesh, fl_top[i], fl_top[ni], cw_top[ni], cw_top[i], mat_steel)
        # Cantilevered under-deck support trusses tied back to the continuous tower legs
        ang_v = 2.0 * math.pi * i / 8 + math.pi / 8
        add_strut(
            booth_mesh,
            (2.25 * math.cos(ang_v), 2.25 * math.sin(ang_v), z_floor - 2.6),
            cw_bot[i],
            0.16,
            mat_steel,
        )
        # Catwalk safety posts & twin hand-rails
        p_post_b = cw_top[i]
        p_post_t = (cw_top[i][0], cw_top[i][1], z_floor + 1.10)
        p_next_t = (cw_top[ni][0], cw_top[ni][1], z_floor + 1.10)
        p_mid_a = (cw_top[i][0], cw_top[i][1], z_floor + 0.55)
        p_mid_b = (cw_top[ni][0], cw_top[ni][1], z_floor + 0.55)
        add_strut(booth_mesh, p_post_b, p_post_t, 0.045, mat_steel)
        add_strut(booth_mesh, p_post_t, p_next_t, 0.04, mat_steel)
        add_strut(booth_mesh, p_mid_a, p_mid_b, 0.03, mat_steel_dark)

        # Outer Octagonal Knee-Wall Bulkhead (from floor z_floor to window sill z_sill = +1.56m)
        add_quad(booth_mesh, fl_top[i], fl_top[ni], sill_ring[ni], sill_ring[i], mat_steel_dark)
        add_quad(booth_mesh, sill_ring[i], sill_ring[ni], fl_top[ni], fl_top[i], mat_desk_trim)
        add_strut(booth_mesh, sill_ring[i], sill_ring[ni], 0.08, mat_steel)

        # Sloped structural corner window mullions + upper transceiver bar
        add_strut(booth_mesh, sill_ring[i], eave_ring[i], 0.11, mat_steel_dark)
        mid_w_a = (
            0.28 * sill_ring[i][0] + 0.72 * eave_ring[i][0],
            0.28 * sill_ring[i][1] + 0.72 * eave_ring[i][1],
            0.28 * z_sill + 0.72 * z_eave,
        )
        mid_w_b = (
            0.28 * sill_ring[ni][0] + 0.72 * eave_ring[ni][0],
            0.28 * sill_ring[ni][1] + 0.72 * eave_ring[ni][1],
            0.28 * z_sill + 0.72 * z_eave,
        )
        add_strut(booth_mesh, mid_w_a, mid_w_b, 0.04, mat_steel_dark)

        # Observation window panes (leave South bay i=5 open for interior wide camera sightlines)
        if i != 5:
            add_quad(booth_mesh, sill_ring[i], sill_ring[ni], eave_ring[ni], eave_ring[i], mat_glass)

        # Roof fascia & pitched octagonal roof
        add_quad(booth_mesh, eave_ring[i], eave_ring[ni], roof_ring[ni], roof_ring[i], mat_steel_dark)
        add_quad(booth_mesh, roof_ring[i], roof_ring[ni], roof_cap[ni], roof_cap[i], mat_steel)
        # Interior radial ceiling ribs tying the octagon eaves into the continuous tower frame
        add_strut(booth_mesh, eave_ring[i], roof_cap[i], 0.085, mat_steel_dark)

    _add_face(booth_mesh, [QVector3D(*p) for p in fl_top], dict(mat_booth_floor))
    _add_face(booth_mesh, [QVector3D(*p) for p in reversed(cw_bot)], dict(mat_steel_dark))

    # Warm amber architectural light strips along the booth ceiling perimeter
    for i in range(8):
        ni = (i + 1) % 8
        p_a = (0.82 * eave_ring[i][0], 0.82 * eave_ring[i][1], z_eave - 0.08)
        p_b = (0.82 * eave_ring[ni][0], 0.82 * eave_ring[ni][1], z_eave - 0.08)
        add_strut(booth_mesh, p_a, p_b, 0.045, mat_amber_glow)

    # Rooftop "GOR-9" Illuminated Neon Sign (mounted on North & South roof eaves)
    sign_z0 = z_roof + 0.15
    sign_z1 = z_roof + 1.85
    for sign_y in (-5.6, 5.6):
        add_box(booth_mesh, -3.5, sign_y - 0.12, sign_z0, 3.5, sign_y + 0.12, sign_z1, mat_steel_dark)
        # G
        add_box(booth_mesh, -3.1, sign_y - 0.18, sign_z0 + 0.25, -2.1, sign_y + 0.18, sign_z0 + 0.42, mat_neon_sign)
        add_box(booth_mesh, -3.1, sign_y - 0.18, sign_z1 - 0.42, -2.1, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        add_box(booth_mesh, -3.1, sign_y - 0.18, sign_z0 + 0.25, -2.9, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        add_box(booth_mesh, -2.3, sign_y - 0.18, sign_z0 + 0.25, -2.1, sign_y + 0.18, sign_z0 + 0.95, mat_neon_sign)
        # O
        add_box(booth_mesh, -1.7, sign_y - 0.18, sign_z0 + 0.25, -0.7, sign_y + 0.18, sign_z0 + 0.42, mat_neon_sign)
        add_box(booth_mesh, -1.7, sign_y - 0.18, sign_z1 - 0.42, -0.7, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        add_box(booth_mesh, -1.7, sign_y - 0.18, sign_z0 + 0.25, -1.5, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        add_box(booth_mesh, -0.9, sign_y - 0.18, sign_z0 + 0.25, -0.7, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        # R
        add_box(booth_mesh, -0.3, sign_y - 0.18, sign_z0 + 0.25, -0.1, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        add_box(booth_mesh, -0.3, sign_y - 0.18, sign_z1 - 0.42, 0.7, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        add_box(booth_mesh, -0.3, sign_y - 0.18, sign_z0 + 0.80, 0.7, sign_y + 0.18, sign_z0 + 0.96, mat_neon_sign)
        add_box(booth_mesh, 0.5, sign_y - 0.18, sign_z0 + 0.25, 0.7, sign_y + 0.18, sign_z1 - 0.25, mat_neon_sign)
        # Dash
        add_box(booth_mesh, 1.0, sign_y - 0.18, sign_z0 + 0.78, 1.6, sign_y + 0.18, sign_z0 + 0.95, mat_neon_sign)
        # 9
        add_box(booth_mesh, 1.9, sign_y - 0.18, sign_z1 - 0.42, 2.9, sign_y + 0.18, sign_z1 - 0.25, mat_amber_glow)
        add_box(booth_mesh, 1.9, sign_y - 0.18, sign_z0 + 0.78, 2.9, sign_y + 0.18, sign_z0 + 0.95, mat_amber_glow)
        add_box(booth_mesh, 1.9, sign_y - 0.18, sign_z0 + 0.25, 2.9, sign_y + 0.18, sign_z0 + 0.42, mat_amber_glow)
        add_box(booth_mesh, 1.9, sign_y - 0.18, sign_z0 + 0.78, 2.1, sign_y + 0.18, sign_z1 - 0.25, mat_amber_glow)
        add_box(booth_mesh, 2.7, sign_y - 0.18, sign_z0 + 0.25, 2.9, sign_y + 0.18, sign_z1 - 0.25, mat_amber_glow)

    scene.groups.append(Group(name="3_Octagonal_Broadcast_Booth", mesh=booth_mesh))

    # ══════════════════════════════════════════════════════════════════
    # 4. THE 4 CONCENTRIC "MARZELVANE EMITTER" RINGS (z = +46.5m)
    # ══════════════════════════════════════════════════════════════════
    marzel_mesh = Mesh()
    marzel_z = 46.5
    marzelvane_radii = [
        (6.5, 0.38),   # Ring 1: Inner Core Marzelvane Emitter
        (10.5, 0.36),  # Ring 2: Secondary Phase Marzelvane Emitter
        (14.5, 0.34),  # Ring 3: Tertiary Harmonic Marzelvane Emitter
        (18.8, 0.34),  # Ring 4: Outer Corona Aperture Marzelvane Emitter
    ]
    for r_ring, tube_r in marzelvane_radii:
        add_ring_torus(marzel_mesh, 0.0, 0.0, marzel_z, r_ring, tube_r, mat_steel_dark, segs=40, tube_sides=8)
        add_ring_torus(
            marzel_mesh,
            0.0,
            0.0,
            marzel_z + tube_r * 0.85,
            r_ring,
            tube_r * 0.48,
            mat_cyan_glow,
            segs=40,
            tube_sides=6,
        )
        add_ring_torus(
            marzel_mesh,
            0.0,
            0.0,
            marzel_z - tube_r * 0.85,
            r_ring,
            tube_r * 0.42,
            mat_cyan_core,
            segs=40,
            tube_sides=6,
        )

    num_spokes = 16
    outer_r = marzelvane_radii[-1][0]
    for i in range(num_spokes):
        ang = 2.0 * math.pi * i / num_spokes
        ca, sa = math.cos(ang), math.sin(ang)
        add_strut(
            marzel_mesh,
            (0.65 * ca, 0.65 * sa, marzel_z),
            (outer_r * ca, outer_r * sa, marzel_z),
            0.09,
            mat_steel,
            sides=6,
        )
        for r_ring, _ in marzelvane_radii:
            nx, ny = r_ring * ca, r_ring * sa
            add_box(
                marzel_mesh,
                nx - 0.34,
                ny - 0.34,
                marzel_z - 0.48,
                nx + 0.34,
                ny + 0.34,
                marzel_z + 0.48,
                mat_amber_glow if (i % 2 == 0) else mat_brass,
            )
        if i % 2 == 0:
            add_strut(
                marzel_mesh,
                (0.5 * ca, 0.5 * sa, marzel_z + 6.5),
                (outer_r * ca, outer_r * sa, marzel_z),
                0.055,
                mat_cyan_glow,
                sides=4,
            )
            add_strut(
                marzel_mesh,
                (0.75 * ca, 0.75 * sa, marzel_z - 6.0),
                (14.5 * ca, 14.5 * sa, marzel_z),
                0.055,
                mat_steel,
                sides=4,
            )

    scene.groups.append(Group(name="4_Marzelvane_Emitter_Concentric_Rings", mesh=marzel_mesh))

    # ══════════════════════════════════════════════════════════════════
    # 5. PERIMETER STANDUP CONSOLES AROUND THE OUTSIDE OCTAGON WALLS
    #    Mounted flush against the outer octagonal knee-walls (r_wall = 5.16m),
    #    at standup desk height (z_desk = +1.05m), with dual sloped 16:9
    #    console displays tucked directly under the window sills (z_sill = +1.56m)!
    # ══════════════════════════════════════════════════════════════════
    def build_perimeter_wall_console(
        width: float,
        left_tex_file: str,
        right_tex_file: str,
        badge_tex_file: str,
        wall_normal_deg: float,
        is_master_mic_bay: bool = False,
    ) -> Mesh:
        """
        Build a standup-height perimeter console bay flush against the octagon outer wall.
        Local coordinates:
          - Origin (0, 0, 0) is on the booth floor at the center of the flat outer wall (r_wall = 5.15m).
          - +Y points OUTWARD toward the octagon wall & window sill.
          - -Y points INWARD toward the booth center & standing operator.
          - +X points along the wall to the operator's right.
          - +Z points UP from the booth floor.
        """
        m = Mesh()
        hw = width * 0.5

        # Wall midpoint at r_wall = 5.15m; local +Y aligns with wall_normal_deg
        # Since local +Y is at angle wall_normal_deg, local +X is at (wall_normal_deg - 90 deg)
        yaw_rad = math.radians(wall_normal_deg - 90.0)
        c, s = math.cos(yaw_rad), math.sin(yaw_rad)
        r_wall = 5.15
        cx = r_wall * math.cos(math.radians(wall_normal_deg))
        cy = r_wall * math.sin(math.radians(wall_normal_deg))
        cz = BOOTH_Z

        def xf(pt):
            lx, ly, lz = pt
            return (cx + lx * c - ly * s, cy + lx * s + ly * c, cz + lz)

        def add_quad_xf(p0, p1, p2, p3, attrs):
            add_quad(m, xf(p0), xf(p1), xf(p2), xf(p3), attrs)

        def add_tex_xf(p0, p1, p2, p3, tex_path, color=(0.95, 0.98, 1.0), emissive=True):
            add_textured_quad(m, xf(p0), xf(p1), xf(p2), xf(p3), tex_path, color=color, emissive=emissive)

        def add_box_xf(x0, y0, z0, x1, y1, z1, attrs):
            p000, p100, p110, p010 = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
            p001, p101, p111, p011 = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
            add_quad_xf(p000, p010, p110, p100, attrs)
            add_quad_xf(p001, p101, p111, p011, attrs)
            add_quad_xf(p000, p100, p101, p001, attrs)
            add_quad_xf(p100, p110, p111, p101, attrs)
            add_quad_xf(p110, p010, p011, p111, attrs)
            add_quad_xf(p010, p000, p001, p011, attrs)

        # Standup desk geometry:
        # Desk surface height: z = 0.98m .. 1.05m
        # Front edge of standup counter: y = -1.05m (inward), extending back to outer wall y = +0.08m
        y_front = -1.18 if is_master_mic_bay else -0.96
        y_ped_front = -0.62
        y_wall_back = 0.10
        z_desk_bot = 0.98
        z_desk_top = 1.05

        # 1. Recessed lower equipment pedestal (leaves deep knee/foot clearance for standup & rolling stools)
        add_box_xf(-hw, y_ped_front, 0.04, hw, y_wall_back, z_desk_bot, mat_desk_hull)
        # Footrest bar along the lower pedestal at z = 0.24m
        add_box_xf(-hw + 0.08, y_ped_front - 0.14, 0.22, hw - 0.08, y_ped_front - 0.08, 0.26, mat_steel)
        # Standup counter top slab (z = 0.98m to 1.05m)
        add_box_xf(-hw - 0.03, y_front, z_desk_bot, hw + 0.03, y_wall_back + 0.04, z_desk_top, mat_desk_trim)
        # Warm amber illuminated wrist bolster along front standup edge
        add_box_xf(-hw - 0.02, y_front - 0.03, z_desk_bot + 0.01, hw + 0.02, y_front + 0.03, z_desk_top + 0.015, mat_amber_glow)

        # 2. Low-Profile Sloped Monitor Wedge Cabinet TUCKED DIRECTLY UNDER THE WINDOW SILL (z = 1.05m to 1.55m)
        #    Bottom front bezel edge at (y = -0.44, z = 1.05), sloping up & back to window sill at (y = +0.12, z = 1.55)
        yb, zb = -0.44, 1.05
        yt, zt = 0.12, 1.55
        yr = 0.16
        add_quad_xf((-hw, yb, zb), (-hw, yt, zt), (-hw, yr, zt), (-hw, yr, zb), mat_desk_hull)
        add_quad_xf((hw, yb, zb), (hw, yr, zb), (hw, yr, zt), (hw, yt, zt), mat_desk_hull)
        add_quad_xf((-hw, yb, zb), (hw, yb, zb), (hw, yt, zt), (-hw, yt, zt), mat_desk_trim)
        add_quad_xf((-hw, yt, zt), (hw, yt, zt), (hw, yr, zt), (-hw, yr, zt), mat_desk_hull)
        add_quad_xf((hw, yr, zb), (-hw, yr, zb), (-hw, yr, zt), (hw, yr, zt), mat_desk_hull)

        # 3. Twin Side-by-Side 16:9 Console Screens on the sloped under-window wedge
        #    Each screen is ~1.52m wide x 0.66m sloped height, sitting 2cm proud of the sloped face
        u0, u1 = 0.07, 0.93
        sy0 = yb + u0 * (yt - yb) - 0.020
        sz0 = zb + u0 * (zt - zb) + 0.012
        sy1 = yb + u1 * (yt - yb) - 0.020
        sz1 = zb + u1 * (zt - zb) + 0.012

        scr_gap = 0.06
        scr_w = (width - 0.24 - scr_gap) * 0.5
        # Left Screen
        lx0, lx1 = - scr_gap * 0.5 - scr_w, -scr_gap * 0.5
        add_tex_xf(
            (lx0, sy0, sz0),
            (lx1, sy0, sz0),
            (lx1, sy1, sz1),
            (lx0, sy1, sz1),
            consoles_dir / left_tex_file,
        )
        # Right Screen
        rx0, rx1 = scr_gap * 0.5, scr_gap * 0.5 + scr_w
        add_tex_xf(
            (rx0, sy0, sz0),
            (rx1, sy0, sz0),
            (rx1, sy1, sz1),
            (rx0, sy1, sz1),
            consoles_dir / right_tex_file,
        )

        # 4. Physical Rotary Tuning Knobs & Illuminated Pushbuttons on the standup counter apron
        if not is_master_mic_bay:
            for kx in (-width * 0.36, -width * 0.18, width * 0.18, width * 0.36):
                add_box_xf(kx - 0.045, -0.64, z_desk_top, kx + 0.045, -0.55, z_desk_top + 0.055, mat_brass)
            for bx_i in range(8):
                bx = -width * 0.38 + bx_i * (width * 0.108)
                glow = mat_cyan_glow if (bx_i % 2 == 0) else mat_amber_glow
                add_box_xf(bx - 0.03, -0.78, z_desk_top, bx + 0.03, -0.72, z_desk_top + 0.03, glow)

        # 5. Riveted Manufacturer Nameplate on the recessed pedestal front skirt
        if badge_tex_file:
            bw = 0.42
            add_tex_xf(
                (-bw, y_ped_front - 0.01, 0.68),
                (bw, y_ped_front - 0.01, 0.68),
                (bw, y_ped_front - 0.01, 0.90),
                (-bw, y_ped_front - 0.01, 0.90),
                plates_dir / badge_tex_file,
                color=(0.95, 0.85, 0.65),
                emissive=True,
            )

        return m

    # 7 Perimeter Standup Console Bays around the outside walls of the Octagonal Booth!
    # Octagon wall outward normals:
    #   90 deg  = North (+Y)       : Master Broadcast Desk + Hauser MK-IV
    #   45 deg  = North-East       : Van Allen VA-4 Propagation + Galactic Signal Atlas
    #   0 deg   = East (+X)        : Van Allen ED-9 Euclidean Detector
    #   315 deg = South-East       : Hauser Bogey-9 Perimeter Trail-Cam & UAP
    #   135 deg = North-West       : Station Dossier & 2-Sided QSL Collector Archive
    #   180 deg = West (-X)        : 3D Spectrum Scan & Comet C/2184-K2 Telemetry
    #   225 deg = South-West       : Reactor Step-Down & Euclidean Rhombus Preview
    perimeter_bays = [
        (
            "Console_Wall_N_Master_MK4",
            3.50,
            "mk4_3b_video.png",
            "mk4_3a_decoder.png",
            "hauser_dynamics_logo.jpg",
            90.0,
            True,
        ),
        (
            "Console_Wall_NE_VanAllen_VA4",
            3.40,
            "va4_1b_squall.png",
            "mk4_3c_atlas.png",
            "van_allen_switchgear_logo.jpg",
            45.0,
            False,
        ),
        (
            "Console_Wall_E_Euclid_ED9",
            3.40,
            "ed9_4d_step4.png",
            "ed9_4b_step1.png",
            "van_allen_switchgear_logo.jpg",
            0.0,
            False,
        ),
        (
            "Console_Wall_SE_Bogey9_UAP",
            3.40,
            "bogey_4a_frame6.png",
            "bogey_4a_nvg.png",
            "hauser_dynamics_logo.jpg",
            315.0,
            False,
        ),
        (
            "Console_Wall_NW_Station_Dossier",
            3.40,
            "dos_3a_n24.png",
            "dos_3d_octal_back.png",
            "hauser_dynamics_logo.jpg",
            135.0,
            False,
        ),
        (
            "Console_Wall_W_Spectrum_Comet",
            3.40,
            "mk4_3c_spectrum.png",
            "va4_1a_comet.png",
            "hauser_dynamics_logo.jpg",
            180.0,
            False,
        ),
        (
            "Console_Wall_SW_Reactor_Rhombus",
            3.40,
            "va4_2b_stepdown.png",
            "ed9_5a_rhombus.png",
            "van_allen_switchgear_logo.jpg",
            225.0,
            False,
        ),
    ]

    for cname, cw, left_png, right_png, badge_jpg, norm_deg, is_master in perimeter_bays:
        cmesh = build_perimeter_wall_console(cw, left_png, right_png, badge_jpg, norm_deg, is_master)
        scene.groups.append(Group(name=cname, mesh=cmesh))

    # ══════════════════════════════════════════════════════════════════
    # 6. STANDUP BROADCAST MIC RIG, DESK PROPS & ROLLING STOOLS
    #    Mounted on the North Perimeter Standup Desk (y = 3.97m .. 5.15m,
    #    z_desk = BOOTH_Z + 1.05m), plus 3 tall rolling broadcast stools!
    # ══════════════════════════════════════════════════════════════════
    props_mesh = Mesh()
    z_desk = BOOTH_Z + 1.05

    # 1. Articulated Broadcast Studio Boom Arm & Shock-Mounted Condenser Microphone
    #    Mounted on the standup desk at x = -0.58m, y = 4.55m, reaching toward the operator at (x = -0.08, y = 4.12)
    base_pt = (-0.58, 4.58, z_desk)
    elbow_pt = (-0.36, 4.34, z_desk + 0.52)
    mic_top = (-0.06, 4.14, z_desk + 0.38)
    add_box(
        props_mesh,
        base_pt[0] - 0.06,
        base_pt[1] - 0.06,
        base_pt[2],
        base_pt[0] + 0.06,
        base_pt[1] + 0.06,
        base_pt[2] + 0.09,
        mat_brass,
    )
    add_strut(props_mesh, base_pt, elbow_pt, 0.020, mat_steel)
    add_strut(
        props_mesh,
        (base_pt[0] + 0.03, base_pt[1], base_pt[2]),
        (elbow_pt[0] + 0.03, elbow_pt[1], elbow_pt[2]),
        0.014,
        mat_steel_dark,
    )
    add_box(
        props_mesh,
        elbow_pt[0] - 0.035,
        elbow_pt[1] - 0.035,
        elbow_pt[2] - 0.035,
        elbow_pt[0] + 0.035,
        elbow_pt[1] + 0.035,
        elbow_pt[2] + 0.035,
        mat_brass,
    )
    add_strut(props_mesh, elbow_pt, mic_top, 0.018, mat_steel)
    # Condenser microphone capsule + glowing crimson "ON AIR • 0400 GCT" tally ring + shock cradle
    mic_bot = (mic_top[0], mic_top[1], mic_top[2] - 0.20)
    add_strut(props_mesh, mic_top, mic_bot, 0.042, mat_brass, sides=12)
    add_ring_torus(props_mesh, mic_top[0], mic_top[1], mic_top[2] - 0.04, 0.048, 0.012, mat_crimson_glow, segs=16, tube_sides=6)
    add_ring_torus(props_mesh, mic_top[0], mic_top[1], mic_top[2] - 0.10, 0.072, 0.008, mat_steel, segs=16, tube_sides=6)
    add_ring_torus(props_mesh, mic_top[0], mic_top[1], mic_top[2] - 0.15, 0.072, 0.008, mat_steel, segs=16, tube_sides=6)

    # 2. Open Spiral-Bound Station Logbook & 2-Sided eQSL Card on clear standup desk space around the mic
    add_textured_quad(
        props_mesh,
        (-0.36, 4.06, z_desk + 0.012),
        (0.18, 4.06, z_desk + 0.012),
        (0.18, 4.44, z_desk + 0.012),
        (-0.36, 4.44, z_desk + 0.012),
        consoles_dir / "dos_3d_octal_back.png",
    )
    add_textured_quad(
        props_mesh,
        (-0.82, 4.08, z_desk + 0.012),
        (-0.48, 4.12, z_desk + 0.012),
        (-0.50, 4.34, z_desk + 0.012),
        (-0.84, 4.30, z_desk + 0.012),
        plates_dir / "qsl_plate_radio_corrugated_kiss.jpg",
    )

    # 3. Brass Straight Morse Key ("GO-9 SWL 1978")
    add_box(props_mesh, 0.28, 4.08, z_desk, 0.46, 4.32, z_desk + 0.04, mat_brass)
    add_strut(props_mesh, (0.37, 4.28, z_desk + 0.05), (0.37, 4.04, z_desk + 0.07), 0.015, mat_brass)
    add_box(props_mesh, 0.33, 4.01, z_desk + 0.06, 0.41, 4.08, z_desk + 0.09, mat_desk_trim)

    # 4. Weighted Barycentric VFO Jog Wheel
    add_strut(props_mesh, (0.64, 4.24, z_desk), (0.64, 4.24, z_desk + 0.07), 0.095, mat_steel, sides=16)
    add_ring_torus(props_mesh, 0.64, 4.24, z_desk + 0.07, 0.085, 0.012, mat_cyan_glow, segs=16, tube_sides=6)

    # 5. "GALACTIC OUTPOST 9" Insulated Stainless Mug
    add_strut(props_mesh, (0.92, 4.14, z_desk), (0.92, 4.14, z_desk + 0.16), 0.055, mat_amber_glow, sides=12)
    add_strut(props_mesh, (0.92, 4.14, z_desk + 0.02), (0.92, 4.14, z_desk + 0.14), 0.057, mat_steel_dark, sides=12)

    # 6. Tall Rolling Broadcast/Drafting Stools (for the standup perimeter desk!)
    def add_rolling_stool(sx: float, sy: float, facing_deg: float):
        # Pneumatic center column (up to tall stool seat height z = +0.76m)
        add_strut(props_mesh, (sx, sy, BOOTH_Z + 0.06), (sx, sy, BOOTH_Z + 0.75), 0.038, mat_steel, sides=10)
        # Signature tall-stool chrome circular foot-ring at z = +0.28m
        add_ring_torus(props_mesh, sx, sy, BOOTH_Z + 0.28, 0.22, 0.014, mat_steel, segs=24, tube_sides=6)
        for sp in range(4):
            a = math.pi * 0.5 * sp
            add_strut(
                props_mesh,
                (sx, sy, BOOTH_Z + 0.28),
                (sx + 0.22 * math.cos(a), sy + 0.22 * math.sin(a), BOOTH_Z + 0.28),
                0.010,
                mat_steel_dark,
            )
        # 5-star caster legs + rolling caster wheels
        for leg_i in range(5):
            lang = 2.0 * math.pi * leg_i / 5 + math.radians(facing_deg)
            lx = sx + 0.34 * math.cos(lang)
            ly = sy + 0.34 * math.sin(lang)
            add_strut(props_mesh, (sx, sy, BOOTH_Z + 0.11), (lx, ly, BOOTH_Z + 0.05), 0.022, mat_steel)
            # Rolling caster wheel
            add_strut(props_mesh, (lx, ly, BOOTH_Z + 0.01), (lx, ly, BOOTH_Z + 0.05), 0.028, mat_desk_trim, sides=8)
        # Round padded swivel seat cushion at z = +0.74m..0.81m
        add_strut(props_mesh, (sx, sy, BOOTH_Z + 0.74), (sx, sy, BOOTH_Z + 0.81), 0.22, mat_desk_trim, sides=20)
        add_ring_torus(props_mesh, sx, sy, BOOTH_Z + 0.80, 0.20, 0.018, mat_amber_glow, segs=20, tube_sides=6)
        # Low ergonomic lumbar support crescent on the back of the stool
        f_rad = math.radians(facing_deg)
        bx = sx - 0.20 * math.cos(f_rad)
        by = sy - 0.20 * math.sin(f_rad)
        add_strut(props_mesh, (bx, by, BOOTH_Z + 0.76), (bx, by, BOOTH_Z + 0.94), 0.022, mat_steel)
        add_box(props_mesh, bx - 0.14, by - 0.08, BOOTH_Z + 0.90, bx + 0.14, by + 0.08, BOOTH_Z + 1.02, mat_desk_hull)

    # Place 3 tall rolling broadcast stools around the standup perimeter desk:
    add_rolling_stool(0.32, 3.35, 90.0)     # Stool 1 at North Master Broadcast Mic & MK-IV bay
    add_rolling_stool(2.35, 2.35, 45.0)     # Stool 2 at North-East Van Allen VA-4 bay
    add_rolling_stool(-2.35, 2.35, 135.0)   # Stool 3 at North-West Station Dossier bay

    scene.groups.append(Group(name="6_Standup_Mic_Props_And_Rolling_Stools", mesh=props_mesh))

    # Reposition the Engineer scale figure so they stand naturally at the North Broadcast Mic!
    if engineer_group is not None:
        from PySide6.QtGui import QMatrix4x4
        m_eng = QMatrix4x4()
        m_eng.translate(-0.48, 3.38, BOOTH_Z + 0.04)
        engineer_group.transform = m_eng
        scene.groups.append(engineer_group)

    scene.version += 1


LIVE_BRIDGE_CODE = """
import sys, math
from pathlib import Path
repo_root = Path("/home/phi/Sessions/GOR-9")
if str(repo_root / "tower_3d") not in sys.path:
    sys.path.insert(0, str(repo_root / "tower_3d"))
import importlib
import build_ingetrazo_tower
importlib.reload(build_ingetrazo_tower)

build_ingetrazo_tower.build_gor9_scene(scene, repo_root)
from PySide6.QtGui import QVector3D

renders_dir = repo_root / "tower_3d" / "renders"
renders_dir.mkdir(parents=True, exist_ok=True)

# 1. Standup Broadcast Desk & Perimeter Consoles POV (looking North & NE across mic, logbook, rolling stool & under-window consoles)
viewport.camera.target = QVector3D(0.35, 4.25, 17.25)
viewport.camera.distance = 2.15
viewport.camera.yaw = math.radians(-72.0)
viewport.camera.pitch = math.radians(10.0)
viewport.camera.fov = 60.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_01_operator_booth_pov.png"))

# 2. Booth Wide Interior (from West walkway showing Continuous Center Lattice Tower through the booth + Perimeter Standup Consoles under windows + Rolling Stools)
viewport.camera.target = QVector3D(1.15, 2.85, 17.25)
viewport.camera.distance = 4.75
viewport.camera.yaw = math.radians(-147.3)
viewport.camera.pitch = math.radians(12.0)
viewport.camera.fov = 62.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_02_booth_wide.png"))

# 3. Full Exterior Tower, Asteroid Crag & 4 Concentric Marzelvane Emitter Rings
viewport.camera.target = QVector3D(0.0, 0.0, 26.0)
viewport.camera.distance = 68.0
viewport.camera.yaw = math.radians(-64.0)
viewport.camera.pitch = math.radians(12.0)
viewport.camera.fov = 48.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_03_exterior_full_tower.png"))

# 4. Close-Up of the 4 Concentric Marzelvane Emitter Rings
viewport.camera.target = QVector3D(0.0, 0.0, 46.5)
viewport.camera.distance = 36.0
viewport.camera.yaw = math.radians(-55.0)
viewport.camera.pitch = math.radians(24.0)
viewport.camera.fov = 48.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_04_marzelvane_emitters.png"))

# Leave the user's live IngeTrazo viewport framed on the Booth Wide Interior showing the continuous tower & perimeter consoles!
viewport.camera.target = QVector3D(1.15, 2.85, 17.25)
viewport.camera.distance = 4.75
viewport.camera.yaw = math.radians(-147.3)
viewport.camera.pitch = math.radians(12.0)
viewport.camera.fov = 62.0
viewport.update()
result = {"groups": [g.name for g in scene.groups], "renders": 4}
"""


def capture_web_renders(repo_root: Path):
    """Capture 2560x1440 screenshots of docs/tower-3d.html across camera presets."""
    import functools
    import http.server
    import shutil
    import socketserver
    import subprocess
    import threading

    docs_dir = repo_root / "docs"
    renders_dir = repo_root / "tower_3d" / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(docs_dir))

    class QuietTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        browser_bin = (
            shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )
        if not browser_bin:
            pw_root = Path.home() / ".cache" / "ms-playwright"
            if pw_root.is_dir():
                for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
                    browser_bin = str(candidate)
                    break

        shots = [
            ("operator_pov", "web3d_01_operator_booth_pov.png"),
            ("booth_wide", "web3d_02_booth_wide.png"),
            ("mic_desk_closeup", "web3d_03_mic_desk_closeup.png"),
            ("exterior_tower", "web3d_04_exterior_tower_marzelvane.png"),
            ("marzelvane_crown", "web3d_05_marzelvane_emitters_crown.png"),
        ]
        if browser_bin:
            for cam_key, fname in shots:
                out_file = renders_dir / fname
                url = f"http://127.0.0.1:{port}/tower-3d.html?cam={cam_key}"
                cmd = [
                    browser_bin,
                    "--headless",
                    "--no-sandbox",
                    "--enable-webgl",
                    "--ignore-gpu-blocklist",
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--window-size=2560,1440",
                    "--virtual-time-budget=2500",
                    f"--screenshot={out_file}",
                    url,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                print(f"Captured WebGL 3D view: {out_file}")
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Build GOR-9 3D Tower & Marzelvane Emitters in IngeTrazo 0.6.0")
    parser.add_argument("--live", action="store_true", help="Push directly to running IngeTrazo MCP bridge (127.0.0.1:4763)")
    parser.add_argument("--skip-web", action="store_true", help="Skip headless browser capture of docs/tower-3d.html")
    args = parser.parse_args()

    repo_root = Path("/home/phi/Sessions/GOR-9")
    out_dir = repo_root / "tower_3d"
    out_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from core.scene import Scene
    from formats.igz import save_scene
    from formats.obj import save_obj

    _app = QApplication.instance() or QApplication(sys.argv)
    scene = Scene()
    build_gor9_scene(scene, repo_root)

    igz_path = out_dir / "gor9_tower.igz"
    obj_path = out_dir / "gor9_tower.obj"
    save_scene(scene, igz_path)
    save_obj(scene, obj_path)
    print(f"Saved IngeTrazo project: {igz_path}")
    print(f"Saved Wavefront OBJ:     {obj_path}")

    if args.live:
        import ingetrazo_mcp
        resp = ingetrazo_mcp._bridge("run_python", {"code": LIVE_BRIDGE_CODE})
        print("Live IngeTrazo 0.6.0 response:", resp)

    if not args.skip_web:
        capture_web_renders(repo_root)


if __name__ == "__main__":
    main()
