"""
Component: Broadcast Studio Furniture, Articulated Boom Mic & Operator Desk Props
=================================================================================
Models:
  1. Three tall rolling broadcast draft stools with 5-star caster bases,
     chrome foot-rings (+0.28m), cushioned swivel seats (+0.76m), and low
     lumbar backrests positioned around the perimeter standup consoles.
  2. The North Master Broadcast Desk microphone & operator props:
     - Articulated brass pantograph studio boom arm
     - Spider shock-mount + vintage condenser mic capsule + glowing crimson
       'ON AIR • 0400 GCT' tally ring
     - Open paper Station Logbook & 2-sided physical eQSL card
     - Brass Morse key, weighted VFO tuning flywheel, and insulated station mug.
"""

import math
from pathlib import Path
from .primitives import (
    BOOTH_Z,
    MATERIALS,
    add_box,
    add_ring_torus,
    add_strut,
    add_textured_quad,
    create_scene_group,
)


def build_rolling_broadcast_stool(mesh, sx: float, sy: float, z_floor: float, facing_deg: float = 90.0):
    """Build a tall standup-desk rolling broadcast stool (seat at +0.76m, chrome foot-ring at +0.28m)."""
    # Pneumatic center column (up to tall stool seat height z = +0.75m)
    add_strut(mesh, (sx, sy, z_floor + 0.06), (sx, sy, z_floor + 0.75), 0.038, MATERIALS["steel"], sides=10)
    # Signature tall-stool chrome circular foot-ring at z = +0.28m
    add_ring_torus(mesh, sx, sy, z_floor + 0.28, 0.22, 0.014, MATERIALS["steel_light"], segs=24, tube_sides=6)
    for sp in range(4):
        a = math.pi * 0.5 * sp
        add_strut(
            mesh,
            (sx, sy, z_floor + 0.28),
            (sx + 0.22 * math.cos(a), sy + 0.22 * math.sin(a), z_floor + 0.28),
            0.010,
            MATERIALS["steel_dark"],
        )
    # 5-star caster legs + rolling caster wheels
    for leg_i in range(5):
        lang = 2.0 * math.pi * leg_i / 5.0 + math.radians(facing_deg)
        lx = sx + 0.34 * math.cos(lang)
        ly = sy + 0.34 * math.sin(lang)
        add_strut(mesh, (sx, sy, z_floor + 0.11), (lx, ly, z_floor + 0.05), 0.022, MATERIALS["steel"])
        add_strut(mesh, (lx, ly, z_floor + 0.01), (lx, ly, z_floor + 0.05), 0.028, MATERIALS["desk_trim"], sides=8)

    # Round padded swivel seat cushion at z = +0.74m..0.81m
    add_strut(mesh, (sx, sy, z_floor + 0.74), (sx, sy, z_floor + 0.81), 0.22, MATERIALS["desk_trim"], sides=20)
    add_ring_torus(mesh, sx, sy, z_floor + 0.80, 0.20, 0.018, MATERIALS["amber_glow"], segs=20, tube_sides=6)

    # Low ergonomic lumbar support crescent on the back of the stool
    f_rad = math.radians(facing_deg)
    bx = sx - 0.20 * math.cos(f_rad)
    by = sy - 0.20 * math.sin(f_rad)
    add_strut(mesh, (bx, by, z_floor + 0.76), (bx, by, z_floor + 0.94), 0.022, MATERIALS["steel"])
    add_box(mesh, bx - 0.14, by - 0.08, z_floor + 0.90, bx + 0.14, by + 0.08, z_floor + 1.02, MATERIALS["desk_hull"])


def build_furniture_and_props(scene, repo_root: Path, engineer_group=None):
    grp = create_scene_group(scene, "06_Studio_Furniture_Mic_And_Props")
    mesh = grp.mesh

    consoles_dir = repo_root / "docs" / "assets" / "consoles"
    plates_dir = repo_root / "docs" / "assets" / "plates"
    z_desk = BOOTH_Z + 1.05

    # 1. Articulated Broadcast Studio Boom Arm & Shock-Mounted Condenser Microphone
    base_pt = (-0.58, 4.58, z_desk)
    elbow_pt = (-0.36, 4.34, z_desk + 0.52)
    mic_top = (-0.06, 4.14, z_desk + 0.38)
    add_box(
        mesh,
        base_pt[0] - 0.06,
        base_pt[1] - 0.06,
        base_pt[2],
        base_pt[0] + 0.06,
        base_pt[1] + 0.06,
        base_pt[2] + 0.09,
        MATERIALS["brass"],
    )
    add_strut(mesh, base_pt, elbow_pt, 0.020, MATERIALS["steel"])
    add_strut(
        mesh,
        (base_pt[0] + 0.03, base_pt[1], base_pt[2]),
        (elbow_pt[0] + 0.03, elbow_pt[1], elbow_pt[2]),
        0.014,
        MATERIALS["steel_dark"],
    )
    add_box(
        mesh,
        elbow_pt[0] - 0.035,
        elbow_pt[1] - 0.035,
        elbow_pt[2] - 0.035,
        elbow_pt[0] + 0.035,
        elbow_pt[1] + 0.035,
        elbow_pt[2] + 0.035,
        MATERIALS["brass"],
    )
    add_strut(mesh, elbow_pt, mic_top, 0.018, MATERIALS["steel"])

    # Condenser microphone capsule + glowing crimson "ON AIR • 0400 GCT" tally ring + shock cradle
    mic_bot = (mic_top[0], mic_top[1], mic_top[2] - 0.20)
    add_strut(mesh, mic_top, mic_bot, 0.042, MATERIALS["brass"], sides=12)
    add_ring_torus(mesh, mic_top[0], mic_top[1], mic_top[2] - 0.04, 0.048, 0.012, MATERIALS["crimson_glow"], segs=16, tube_sides=6)
    add_ring_torus(mesh, mic_top[0], mic_top[1], mic_top[2] - 0.10, 0.072, 0.008, MATERIALS["steel"], segs=16, tube_sides=6)
    add_ring_torus(mesh, mic_top[0], mic_top[1], mic_top[2] - 0.15, 0.072, 0.008, MATERIALS["steel"], segs=16, tube_sides=6)

    # 2. Open Spiral-Bound Station Logbook & 2-Sided eQSL Card on clear standup desk space around the mic
    add_textured_quad(
        mesh,
        (-0.36, 4.06, z_desk + 0.012),
        (0.18, 4.06, z_desk + 0.012),
        (0.18, 4.44, z_desk + 0.012),
        (-0.36, 4.44, z_desk + 0.012),
        consoles_dir / "dos_3d_octal_back.png",
    )
    add_textured_quad(
        mesh,
        (-0.82, 4.08, z_desk + 0.012),
        (-0.48, 4.12, z_desk + 0.012),
        (-0.50, 4.34, z_desk + 0.012),
        (-0.84, 4.30, z_desk + 0.012),
        plates_dir / "qsl_plate_radio_corrugated_kiss.jpg",
    )

    # 3. Brass Straight Morse Key ("GO-9 SWL 1978")
    add_box(mesh, 0.28, 4.08, z_desk, 0.46, 4.32, z_desk + 0.04, MATERIALS["brass"])
    add_strut(mesh, (0.37, 4.28, z_desk + 0.05), (0.37, 4.04, z_desk + 0.07), 0.015, MATERIALS["brass"])
    add_box(mesh, 0.33, 4.01, z_desk + 0.06, 0.41, 4.08, z_desk + 0.09, MATERIALS["desk_trim"])

    # 4. Weighted Barycentric VFO Jog Wheel
    add_strut(mesh, (0.64, 4.24, z_desk), (0.64, 4.24, z_desk + 0.07), 0.095, MATERIALS["steel"], sides=16)
    add_ring_torus(mesh, 0.64, 4.24, z_desk + 0.07, 0.085, 0.012, MATERIALS["cyan_glow"], segs=16, tube_sides=6)

    # 5. "GALACTIC OUTPOST 9" Insulated Stainless Mug
    add_strut(mesh, (0.92, 4.14, z_desk), (0.92, 4.14, z_desk + 0.16), 0.055, MATERIALS["amber_glow"], sides=12)
    add_strut(mesh, (0.92, 4.14, z_desk + 0.02), (0.92, 4.14, z_desk + 0.14), 0.057, MATERIALS["steel_dark"], sides=12)

    # 6. Three Tall Rolling Broadcast Stools at the North, NE, and NW Standup Consoles
    build_rolling_broadcast_stool(mesh, 0.32, 3.35, BOOTH_Z, 90.0)
    build_rolling_broadcast_stool(mesh, 2.35, 2.35, BOOTH_Z, 45.0)
    build_rolling_broadcast_stool(mesh, -2.35, 2.35, BOOTH_Z, 135.0)

    # 7. Reposition the Engineer scale figure so they stand naturally at the North Broadcast Mic
    if engineer_group is not None:
        from PySide6.QtGui import QMatrix4x4

        m_eng = QMatrix4x4()
        m_eng.translate(-0.48, 3.38, BOOTH_Z + 0.04)
        engineer_group.transform = m_eng
        scene.groups.append(engineer_group)

    return grp
