"""
Component: Broadcast Studio Furniture, Pantograph Boom Mic & Tactile Operator Desk Props
========================================================================================
Models:
  1. Three tall rolling broadcast studio stools with 5-star cast-aluminum bases,
     dual-wheel hooded casters, telescoping pneumatic columns, height-adjustment
     levers, chrome foot-rings (+0.28m), dark leather swivel seats (+0.76m) with
     brass welt seams, and curved 3-segment ergonomic lumbar backrests.
  2. The North Master Broadcast Desk microphone & tactile operator props:
     - Weighted cylindrical turret clamp + dual-tube scissor pantograph boom arm
       with tension springs and brass friction-lock thumbscrews.
     - Hauser CM-78 large-diaphragm condenser microphone in an elastic spider
       shock-mount cradle, gooseneck mesh pop-filter, and backlit 'ON AIR' tally flag.
     - 3D open spiral-bound Station Logbook with raised paper page blocks, wire
       spiral binding, and a machined brass drafting pen.
     - 3D card-stock eQSL collector cards.
     - Stepped brass straight Morse key ('GO-9 SWL 1978') with slate insulator
       base, binding posts, pivot trunnions, and round Bakelite finger knob.
     - Machined Barycentric VFO flywheel controller with cast-aluminum housing,
       optical encoder ring, and finger-dimple spinner cup.
     - Hollow insulated 'GALACTIC OUTPOST 9' stainless mug with dark coffee
       surface and 3D C-handle, plus circumaural studio monitor headphones.
"""

import math
from pathlib import Path
from .primitives import (
    BOOTH_Z,
    MATERIALS,
    add_box,
    add_face,
    add_quad,
    add_ring_torus,
    add_strut,
    add_textured_quad,
    create_scene_group,
)


def build_rolling_broadcast_stool(mesh, sx: float, sy: float, z_floor: float, facing_deg: float = 90.0):
    """Build an ergonomic tall standup-desk rolling broadcast stool (seat at +0.76m, foot-ring at +0.28m)."""
    f_rad = math.radians(facing_deg)
    fx, fy = math.cos(f_rad), math.sin(f_rad)
    rx, ry = fy, -fx

    # 1. Telescoping pneumatic center column (outer dark sleeve + inner chrome piston)
    add_strut(mesh, (sx, sy, z_floor + 0.05), (sx, sy, z_floor + 0.38), 0.042, MATERIALS["bezel_dark"], sides=12)
    add_strut(mesh, (sx, sy, z_floor + 0.36), (sx, sy, z_floor + 0.73), 0.032, MATERIALS["steel_light"], sides=12)

    # 2. Chrome circular foot-ring at z = +0.28m with 4 radial spokes & central locking collar
    add_strut(mesh, (sx, sy, z_floor + 0.255), (sx, sy, z_floor + 0.305), 0.048, MATERIALS["bezel_dark"], sides=10)
    add_ring_torus(mesh, sx, sy, z_floor + 0.28, 0.22, 0.013, MATERIALS["steel_light"], segs=24, tube_sides=8)
    for sp in range(4):
        a = math.pi * 0.5 * sp + f_rad
        add_strut(
            mesh,
            (sx, sy, z_floor + 0.28),
            (sx + 0.22 * math.cos(a), sy + 0.22 * math.sin(a), z_floor + 0.28),
            0.009,
            MATERIALS["steel_dark"],
            sides=6,
        )

    # 3. 5-star cast-aluminum base legs + dual-wheel hooded studio casters
    for leg_i in range(5):
        lang = 2.0 * math.pi * leg_i / 5.0 + f_rad
        lx = sx + 0.35 * math.cos(lang)
        ly = sy + 0.35 * math.sin(lang)
        add_strut(mesh, (sx, sy, z_floor + 0.11), (lx, ly, z_floor + 0.055), 0.022, MATERIALS["steel_light"], sides=8)
        # Caster stem & hooded wheel pair
        add_strut(mesh, (lx, ly, z_floor + 0.032), (lx, ly, z_floor + 0.060), 0.016, MATERIALS["steel_dark"], sides=8)
        wx, wy = -math.sin(lang) * 0.018, math.cos(lang) * 0.018
        add_strut(
            mesh,
            (lx - wx, ly - wy, z_floor + 0.024),
            (lx + wx, ly + wy, z_floor + 0.024),
            0.024,
            MATERIALS["bezel_dark"],
            sides=10,
        )

    # 4. Under-seat steel mounting pan + pneumatic height-adjustment lever paddle
    add_strut(mesh, (sx, sy, z_floor + 0.715), (sx, sy, z_floor + 0.742), 0.175, MATERIALS["bezel_dark"], sides=16)
    lev_p0 = (sx + 0.08 * rx, sy + 0.08 * ry, z_floor + 0.725)
    lev_p1 = (sx + 0.25 * rx - 0.04 * fx, sy + 0.25 * ry - 0.04 * fy, z_floor + 0.705)
    add_strut(mesh, lev_p0, lev_p1, 0.007, MATERIALS["steel_light"], sides=6)
    add_strut(
        mesh,
        (lev_p1[0] - 0.02 * rx, lev_p1[1] - 0.02 * ry, lev_p1[2]),
        (lev_p1[0] + 0.02 * rx, lev_p1[1] + 0.02 * ry, lev_p1[2]),
        0.013,
        MATERIALS["brass"],
        sides=6,
    )

    # 5. Thick upholstered dark leather swivel seat cushion (z = +0.74m..0.81m) with subtle brass welt seam
    add_strut(mesh, (sx, sy, z_floor + 0.740), (sx, sy, z_floor + 0.808), 0.215, MATERIALS["desk_leather"], sides=20)
    add_ring_torus(mesh, sx, sy, z_floor + 0.802, 0.208, 0.008, MATERIALS["brass"], segs=20, tube_sides=6)

    # 6. Curved 3-Segment Ergonomic Lumbar Backrest mounted behind the seat (never clipping the seat cushion!)
    sp_0 = (sx - 0.15 * fx, sy - 0.15 * fy, z_floor + 0.725)
    sp_1 = (sx - 0.265 * fx, sy - 0.265 * fy, z_floor + 0.765)
    sp_2 = (sx - 0.275 * fx, sy - 0.275 * fy, z_floor + 0.965)
    add_strut(mesh, sp_0, sp_1, 0.018, MATERIALS["steel_dark"], sides=8)
    add_strut(mesh, sp_1, sp_2, 0.018, MATERIALS["steel_dark"], sides=8)

    # Build curved 3-panel lumbar cushion wrapping around the operator's lower back (z = +0.89m..+1.03m)
    z_b0, z_b1 = z_floor + 0.89, z_floor + 1.03
    arc_pts_in = []
    arc_pts_out = []
    for u_ang in (-0.52, -0.18, 0.18, 0.52):
        # Center of lumbar arc is slightly forward toward seat center, radius ~0.25m
        ca, sa = math.cos(u_ang), math.sin(u_ang)
        px_in = sx - (0.02 + 0.235 * ca) * fx + (0.235 * sa) * rx
        py_in = sy - (0.02 + 0.235 * ca) * fy + (0.235 * sa) * ry
        px_out = sx - (0.02 + 0.272 * ca) * fx + (0.272 * sa) * rx
        py_out = sy - (0.02 + 0.272 * ca) * fy + (0.272 * sa) * ry
        arc_pts_in.append((px_in, py_in))
        arc_pts_out.append((px_out, py_out))

    for seg in range(3):
        xi0, yi0 = arc_pts_in[seg]
        xi1, yi1 = arc_pts_in[seg + 1]
        xo0, yo0 = arc_pts_out[seg]
        xo1, yo1 = arc_pts_out[seg + 1]
        # Front cushioned leather face (facing operator)
        add_quad(mesh, (xi0, yi0, z_b0), (xi1, yi1, z_b0), (xi1, yi1, z_b1), (xi0, yi0, z_b1), MATERIALS["desk_leather"])
        # Rear molded shell face
        add_quad(mesh, (xo1, yo1, z_b0), (xo0, yo0, z_b0), (xo0, yo0, z_b1), (xo1, yo1, z_b1), MATERIALS["bezel_dark"])
        # Top & bottom edges
        add_quad(mesh, (xi0, yi0, z_b1), (xi1, yi1, z_b1), (xo1, yo1, z_b1), (xo0, yo0, z_b1), MATERIALS["desk_leather"])
        add_quad(mesh, (xo0, yo0, z_b0), (xo1, yo1, z_b0), (xi1, yi1, z_b0), (xi0, yi0, z_b0), MATERIALS["bezel_dark"])
    # Left & right end caps of lumbar backrest
    add_quad(
        mesh,
        (arc_pts_out[0][0], arc_pts_out[0][1], z_b0),
        (arc_pts_in[0][0], arc_pts_in[0][1], z_b0),
        (arc_pts_in[0][0], arc_pts_in[0][1], z_b1),
        (arc_pts_out[0][0], arc_pts_out[0][1], z_b1),
        MATERIALS["desk_leather"],
    )
    add_quad(
        mesh,
        (arc_pts_in[3][0], arc_pts_in[3][1], z_b0),
        (arc_pts_out[3][0], arc_pts_out[3][1], z_b0),
        (arc_pts_out[3][0], arc_pts_out[3][1], z_b1),
        (arc_pts_in[3][0], arc_pts_in[3][1], z_b1),
        MATERIALS["desk_leather"],
    )


def build_furniture_and_props(scene, repo_root: Path, engineer_group=None):
    grp = create_scene_group(scene, "06_Studio_Furniture_Mic_And_Props")
    mesh = grp.mesh

    consoles_dir = repo_root / "docs" / "assets" / "consoles"
    plates_dir = repo_root / "docs" / "assets" / "plates"
    z_desk = BOOTH_Z + 1.05

    # ── 1. ARTICULATED DUAL-TUBE PANTOGRAPH BOOM ARM & HAUSER CM-78 CONDENSER MIC ──
    base_pt = (-0.58, 4.58, z_desk)
    elbow_pt = (-0.36, 4.34, z_desk + 0.52)
    mic_top = (-0.06, 4.14, z_desk + 0.38)

    # Machined cylindrical turret desk mount (replacing boxy cube base)
    add_strut(mesh, base_pt, (base_pt[0], base_pt[1], base_pt[2] + 0.045), 0.056, MATERIALS["bezel_dark"], sides=14)
    add_strut(
        mesh,
        (base_pt[0], base_pt[1], base_pt[2] + 0.045),
        (base_pt[0], base_pt[1], base_pt[2] + 0.092),
        0.042,
        MATERIALS["brass"],
        sides=14,
    )
    add_ring_torus(mesh, base_pt[0], base_pt[1], base_pt[2] + 0.046, 0.048, 0.008, MATERIALS["brass"], segs=16, tube_sides=6)

    # Lower scissor pantograph twin parallel linkage tubes + external tension spring
    low_a0 = (base_pt[0] - 0.014, base_pt[1], base_pt[2] + 0.082)
    low_a1 = (elbow_pt[0] - 0.014, elbow_pt[1], elbow_pt[2] - 0.012)
    low_b0 = (base_pt[0] + 0.018, base_pt[1], base_pt[2] + 0.072)
    low_b1 = (elbow_pt[0] + 0.018, elbow_pt[1], elbow_pt[2] - 0.022)
    add_strut(mesh, low_a0, low_a1, 0.012, MATERIALS["steel_light"], sides=8)
    add_strut(mesh, low_b0, low_b1, 0.011, MATERIALS["steel_dark"], sides=8)
    add_strut(
        mesh,
        (base_pt[0] - 0.032, base_pt[1], base_pt[2] + 0.095),
        (elbow_pt[0] - 0.028, elbow_pt[1], elbow_pt[2] - 0.08),
        0.007,
        MATERIALS["brass"],
        sides=6,
    )

    # Cylindrical elbow hinge yoke + brass friction-lock thumbscrew knob
    add_strut(
        mesh,
        (elbow_pt[0] - 0.034, elbow_pt[1], elbow_pt[2]),
        (elbow_pt[0] + 0.034, elbow_pt[1], elbow_pt[2]),
        0.028,
        MATERIALS["bezel_dark"],
        sides=12,
    )
    add_strut(
        mesh,
        (elbow_pt[0] + 0.034, elbow_pt[1], elbow_pt[2]),
        (elbow_pt[0] + 0.054, elbow_pt[1], elbow_pt[2]),
        0.022,
        MATERIALS["brass"],
        sides=12,
    )

    # Upper scissor pantograph twin linkage tubes to mic wrist
    up_a0 = (elbow_pt[0] - 0.012, elbow_pt[1], elbow_pt[2] + 0.012)
    up_a1 = (mic_top[0] - 0.012, mic_top[1], mic_top[2] + 0.018)
    up_b0 = (elbow_pt[0] + 0.012, elbow_pt[1], elbow_pt[2] - 0.010)
    up_b1 = (mic_top[0] + 0.012, mic_top[1], mic_top[2] - 0.004)
    add_strut(mesh, up_a0, up_a1, 0.011, MATERIALS["steel_light"], sides=8)
    add_strut(mesh, up_b0, up_b1, 0.009, MATERIALS["steel_dark"], sides=8)
    # Wrist swivel collar
    add_strut(
        mesh,
        (mic_top[0], mic_top[1], mic_top[2] - 0.01),
        (mic_top[0], mic_top[1], mic_top[2] + 0.025),
        0.022,
        MATERIALS["brass"],
        sides=10,
    )

    # Backlit rectangular "ON AIR • 0400 GCT" acrylic tally blade mounted on top of the mic yoke
    add_box(
        mesh,
        mic_top[0] - 0.052,
        mic_top[1] - 0.012,
        mic_top[2] + 0.024,
        mic_top[0] + 0.052,
        mic_top[1] + 0.012,
        mic_top[2] + 0.034,
        MATERIALS["bezel_dark"],
    )
    add_box(
        mesh,
        mic_top[0] - 0.048,
        mic_top[1] - 0.008,
        mic_top[2] + 0.034,
        mic_top[0] + 0.048,
        mic_top[1] + 0.008,
        mic_top[2] + 0.064,
        MATERIALS["crimson_glow"],
    )

    # Hauser CM-78 Side-Address Broadcast Condenser Microphone (stepped brass chassis + dark mesh headbasket)
    mx, my, mz = mic_top
    add_strut(mesh, (mx, my, mz - 0.010), (mx, my, mz - 0.085), 0.035, MATERIALS["brass"], sides=16)
    add_strut(mesh, (mx, my, mz - 0.085), (mx, my, mz - 0.115), 0.038, MATERIALS["bezel_dark"], sides=16)
    add_strut(mesh, (mx, my, mz - 0.115), (mx, my, mz - 0.195), 0.035, MATERIALS["steel_dark"], sides=16)
    add_strut(mesh, (mx, my, mz - 0.195), (mx, my, mz - 0.212), 0.036, MATERIALS["brass"], sides=16)
    # Glowing crimson ON-AIR tally ring around upper mic body
    add_ring_torus(mesh, mx, my, mz - 0.045, 0.040, 0.009, MATERIALS["crimson_glow"], segs=20, tube_sides=8)

    # Elastic Spider Shock-Mount Cradle (dual outer suspension rings + 8 diagonal elastic cords)
    for ring_z in (mz - 0.095, mz - 0.155):
        add_ring_torus(mesh, mx, my, ring_z, 0.068, 0.006, MATERIALS["steel_light"], segs=20, tube_sides=6)
        for cord_i in range(4):
            ca = math.pi * 0.5 * cord_i + 0.35
            add_strut(
                mesh,
                (mx + 0.068 * math.cos(ca), my + 0.068 * math.sin(ca), ring_z),
                (mx + 0.036 * math.cos(ca + 0.4), my + 0.036 * math.sin(ca + 0.4), ring_z + 0.012),
                0.004,
                MATERIALS["bezel_dark"],
                sides=4,
            )
    # Vertical shock-mount frame bars on left & right of spider cradle
    for s_sign in (-1.0, 1.0):
        add_strut(
            mesh,
            (mx + s_sign * 0.068, my, mz - 0.162),
            (mx + s_sign * 0.068, my, mz - 0.088),
            0.007,
            MATERIALS["steel_light"],
            sides=6,
        )

    # Circular Mesh Pop-Filter Screen on gooseneck arm in front of condenser capsule (y = my - 0.068)
    pf_x, pf_y, pf_z = mx, my - 0.072, mz - 0.150
    add_strut(mesh, (mx - 0.025, my, mz - 0.020), (mx - 0.055, my - 0.050, mz - 0.085), 0.005, MATERIALS["brass"], sides=6)
    add_strut(mesh, (mx - 0.055, my - 0.050, mz - 0.085), (pf_x - 0.048, pf_y, pf_z), 0.005, MATERIALS["brass"], sides=6)
    # Pop-filter hoop & thin acoustic nylon disk in X-Z plane facing operator (-Y)
    pf_segs = 16
    pf_front = []
    pf_back = []
    for pi in range(pf_segs):
        pa = 2.0 * math.pi * pi / pf_segs
        px_r = pf_x + 0.048 * math.cos(pa)
        pz_r = pf_z + 0.048 * math.sin(pa)
        pf_front.append((px_r, pf_y - 0.004, pz_r))
        pf_back.append((px_r, pf_y + 0.004, pz_r))
    add_face(mesh, pf_front, dict(MATERIALS["bezel_dark"]))
    add_face(mesh, list(reversed(pf_back)), dict(MATERIALS["bezel_dark"]))
    for pi in range(pf_segs):
        npi = (pi + 1) % pf_segs
        add_quad(mesh, pf_front[pi], pf_front[npi], pf_back[npi], pf_back[pi], MATERIALS["brass"])

    # ── 2. 3D OPEN SPIRAL-BOUND STATION LOGBOOK, BRASS PEN & 2-SIDED eQSL CARDS ──
    # Hardbound dark leatherette cover slab (z = +0.002 .. +0.012m)
    add_box(mesh, -0.37, 4.05, z_desk + 0.001, 0.19, 4.45, z_desk + 0.011, MATERIALS["desk_leather"])
    # Raised cream paper page blocks on Left and Right halves (z = +0.011 .. +0.022m)
    add_box(mesh, -0.355, 4.062, z_desk + 0.011, -0.096, 4.438, z_desk + 0.022, MATERIALS["paper_edge"])
    add_box(mesh, -0.084, 4.062, z_desk + 0.011, 0.175, 4.438, z_desk + 0.022, MATERIALS["paper_edge"])
    # Top printed logbook spread
    add_textured_quad(
        mesh,
        (-0.355, 4.062, z_desk + 0.023),
        (0.175, 4.062, z_desk + 0.023),
        (0.175, 4.438, z_desk + 0.023),
        (-0.355, 4.438, z_desk + 0.023),
        consoles_dir / "dos_3d_octal_back.png",
        color=(0.94, 0.94, 0.92),
        emissive=False,
    )
    # 9 spiral wire binding rings along the center spine (x = -0.09)
    for sp_i in range(9):
        spy = 4.085 + sp_i * 0.041
        add_strut(mesh, (-0.104, spy, z_desk + 0.024), (-0.076, spy, z_desk + 0.024), 0.005, MATERIALS["steel_light"], sides=6)

    # Machined Brass Drafting Pen resting diagonally beside the logbook
    add_strut(mesh, (0.20, 4.10, z_desk + 0.008), (0.24, 4.29, z_desk + 0.008), 0.006, MATERIALS["brass"], sides=8)
    add_strut(mesh, (0.195, 4.075, z_desk + 0.008), (0.20, 4.10, z_desk + 0.008), 0.003, MATERIALS["steel_light"], sides=6)

    # 3D eQSL Collector Card Stack on the left side of the desk
    add_box(mesh, -0.85, 4.07, z_desk + 0.001, -0.51, 4.31, z_desk + 0.007, MATERIALS["paper_edge"])
    qsl_pts_top = [
        (-0.82, 4.08, z_desk + 0.012),
        (-0.48, 4.12, z_desk + 0.012),
        (-0.50, 4.34, z_desk + 0.012),
        (-0.84, 4.30, z_desk + 0.012),
    ]
    qsl_pts_bot = [(x, y, z_desk + 0.006) for (x, y, _) in qsl_pts_top]
    for qi in range(4):
        nqi = (qi + 1) % 4
        add_quad(mesh, qsl_pts_bot[qi], qsl_pts_bot[nqi], qsl_pts_top[nqi], qsl_pts_top[qi], MATERIALS["paper_edge"])
    add_textured_quad(
        mesh,
        qsl_pts_top[0],
        qsl_pts_top[1],
        qsl_pts_top[2],
        qsl_pts_top[3],
        plates_dir / "qsl_plate_radio_corrugated_kiss.jpg",
        color=(0.95, 0.92, 0.88),
        emissive=False,
    )

    # ── 3. HEAVY BRASS STRAIGHT MORSE KEY ("GO-9 SWL 1978") ──
    # Beveled dark slate insulator base + stepped machined brass sub-base
    add_box(mesh, 0.27, 4.06, z_desk, 0.47, 4.34, z_desk + 0.018, MATERIALS["bezel_dark"])
    add_box(mesh, 0.285, 4.075, z_desk + 0.018, 0.455, 4.325, z_desk + 0.036, MATERIALS["brass"])
    # Rear binding post terminals & pivot trunnion standards
    for bpx in (0.32, 0.42):
        add_strut(mesh, (bpx, 4.29, z_desk + 0.036), (bpx, 4.29, z_desk + 0.062), 0.012, MATERIALS["brass"], sides=8)
    for tpx in (0.335, 0.405):
        add_box(mesh, tpx - 0.008, 4.19, z_desk + 0.036, tpx + 0.008, 4.22, z_desk + 0.068, MATERIALS["brass"])
    add_strut(mesh, (0.325, 4.205, z_desk + 0.056), (0.415, 4.205, z_desk + 0.056), 0.007, MATERIALS["steel_light"], sides=8)
    # Tapered brass key lever + round Bakelite paddle knob
    add_strut(mesh, (0.37, 4.28, z_desk + 0.052), (0.37, 4.02, z_desk + 0.066), 0.011, MATERIALS["brass"], sides=8)
    add_strut(mesh, (0.37, 4.02, z_desk + 0.058), (0.37, 4.02, z_desk + 0.078), 0.035, MATERIALS["desk_leather"], sides=14)
    add_strut(mesh, (0.37, 4.02, z_desk + 0.078), (0.37, 4.02, z_desk + 0.083), 0.016, MATERIALS["brass"], sides=10)

    # ── 4. MACHINED BARYCENTRIC VFO FLYWHEEL CONTROLLER ──
    vx, vy = 0.64, 4.24
    # Cast-aluminum base enclosure
    add_box(mesh, vx - 0.115, vy - 0.115, z_desk, vx + 0.115, vy + 0.115, z_desk + 0.022, MATERIALS["bezel_dark"])
    # Recessed Cherenkov-cyan optical encoder scale ring
    add_ring_torus(mesh, vx, vy, z_desk + 0.024, 0.094, 0.007, MATERIALS["cyan_glow"], segs=24, tube_sides=6)
    # Heavy brushed-steel flywheel drum + brass chamfer bezel + eccentric finger-dimple cup
    add_strut(mesh, (vx, vy, z_desk + 0.022), (vx, vy, z_desk + 0.066), 0.086, MATERIALS["steel_light"], sides=20)
    add_ring_torus(mesh, vx, vy, z_desk + 0.066, 0.078, 0.007, MATERIALS["brass"], segs=20, tube_sides=6)
    add_strut(mesh, (vx + 0.038, vy - 0.028, z_desk + 0.064), (vx + 0.038, vy - 0.028, z_desk + 0.073), 0.020, MATERIALS["bezel_dark"], sides=12)

    # ── 5. HOLLOW INSULATED "GALACTIC OUTPOST 9" STAINLESS MUG WITH COFFEE & C-HANDLE ──
    mx_mug, my_mug = 0.92, 4.14
    # Brushed steel bottom base + matte charcoal body + copper band + stainless lip
    add_strut(mesh, (mx_mug, my_mug, z_desk), (mx_mug, my_mug, z_desk + 0.024), 0.053, MATERIALS["steel_light"], sides=16)
    add_strut(mesh, (mx_mug, my_mug, z_desk + 0.024), (mx_mug, my_mug, z_desk + 0.138), 0.055, MATERIALS["bezel_dark"], sides=16)
    add_strut(mesh, (mx_mug, my_mug, z_desk + 0.062), (mx_mug, my_mug, z_desk + 0.096), 0.056, MATERIALS["copper"], sides=16)
    add_ring_torus(mesh, mx_mug, my_mug, z_desk + 0.140, 0.051, 0.006, MATERIALS["steel_light"], segs=16, tube_sides=6)
    # Glossy dark coffee liquid surface slightly recessed inside the top of the mug
    add_strut(mesh, (mx_mug, my_mug, z_desk + 0.132), (mx_mug, my_mug, z_desk + 0.139), 0.047, MATERIALS["coffee"], sides=16)
    # 3D C-shaped side handle on the +X side of the mug
    add_strut(mesh, (mx_mug + 0.052, my_mug, z_desk + 0.115), (mx_mug + 0.088, my_mug, z_desk + 0.115), 0.008, MATERIALS["bezel_dark"], sides=6)
    add_strut(mesh, (mx_mug + 0.052, my_mug, z_desk + 0.045), (mx_mug + 0.088, my_mug, z_desk + 0.045), 0.008, MATERIALS["bezel_dark"], sides=6)
    add_strut(mesh, (mx_mug + 0.088, my_mug, z_desk + 0.045), (mx_mug + 0.088, my_mug, z_desk + 0.115), 0.009, MATERIALS["bezel_dark"], sides=6)

    # ── 6. STUDIO BROADCAST MONITOR HEADPHONES (Resting on Left Wing of North Desk) ──
    hx, hy = -1.08, 4.18
    for ear_dx, ear_dy in [(-0.075, -0.02), (0.075, 0.02)]:
        ex, ey = hx + ear_dx, hy + ear_dy
        add_strut(mesh, (ex, ey, z_desk + 0.002), (ex, ey, z_desk + 0.024), 0.048, MATERIALS["desk_leather"], sides=14)
        add_strut(mesh, (ex, ey, z_desk + 0.024), (ex, ey, z_desk + 0.042), 0.042, MATERIALS["bezel_dark"], sides=14)
        add_ring_torus(mesh, ex, ey, z_desk + 0.025, 0.045, 0.005, MATERIALS["brass"], segs=14, tube_sides=6)
    # Arched spring-steel headband connecting the two earcups flat on the desk
    hb_pts = [
        (hx - 0.075, hy - 0.02, z_desk + 0.028),
        (hx - 0.055, hy + 0.085, z_desk + 0.032),
        (hx + 0.015, hy + 0.115, z_desk + 0.034),
        (hx + 0.075, hy + 0.02, z_desk + 0.028),
    ]
    for hi in range(len(hb_pts) - 1):
        add_strut(mesh, hb_pts[hi], hb_pts[hi + 1], 0.010, MATERIALS["desk_leather"], sides=6)

    # ── 7. THREE TALL ROLLING BROADCAST STOOLS AT NORTH, NE, AND NW CONSOLES ──
    build_rolling_broadcast_stool(mesh, 0.32, 3.35, BOOTH_Z, 90.0)
    build_rolling_broadcast_stool(mesh, 2.35, 2.35, BOOTH_Z, 45.0)
    build_rolling_broadcast_stool(mesh, -2.35, 2.35, BOOTH_Z, 135.0)

    # 8. Reposition the Engineer scale figure so they stand naturally at the North Broadcast Mic
    if engineer_group is not None:
        from PySide6.QtGui import QMatrix4x4

        m_eng = QMatrix4x4()
        m_eng.translate(-0.48, 3.38, BOOTH_Z + 0.04)
        engineer_group.transform = m_eng
        scene.groups.append(engineer_group)

    return grp
