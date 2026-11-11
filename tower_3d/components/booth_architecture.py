"""
Component: Cantilevered Octagonal Broadcast Booth Architecture (Z = +26.0m)
===========================================================================
Models the octagonal glass-and-steel broadcast observation pod cantilevered
around the continuous lattice tower at Z = 26.0m:
  - 8 heavy under-hull steel support brackets with gusset bracing
  - 360° exterior catwalk deck + guardrails + toe-boards
  - Waist-high outer wall (z = 0 .. +1.56m) with interior acoustic ribbing
    and a shielded window-sill HVAC defroster/light-cove plenum
  - Outward-tilted panoramic observation windows (z = +1.56m .. +4.75m) with
    composite I-beam mullions, bolted brass corner gussets, and upper transoms
  - South Wall (270°) pressurized submarine-style EVA catwalk airlock hatch
    with porthole, 6-spoke brass dogging wheel, and overhead status beacon
  - Radial ceiling trusses, concentric studio light raceways, 8 directional
    hooded studio track-light cans, and beveled operator anti-fatigue floor mats.
"""

import math
from .primitives import (
    BOOTH_Z,
    MATERIALS,
    add_box,
    add_face,
    add_prism,
    add_quad,
    add_ring_torus,
    add_strut,
    create_scene_group,
)
from .tower_structure import tower_half_width


def build_octagonal_booth(scene):
    grp = create_scene_group(scene, "04_Octagonal_Broadcast_Booth")
    mesh = grp.mesh

    r_booth = 6.20
    r_catwalk = 7.45
    z_floor = BOOTH_Z
    z_sill = BOOTH_Z + 1.56
    z_eave = BOOTH_Z + 4.75
    z_roof = BOOTH_Z + 5.20

    # Studio ON-AIR Crimson-Red Watchroom Lighting (3D neon light bars & chandelier rings)
    booth_warm = {"color": (1.00, 0.002, 0.001), "emissive": True, "light_channel": "booth_glow"}
    booth_neon = {"color": (1.00, 0.002, 0.001), "emissive": True, "light_channel": "booth_glow"}
    # Crystal-clear architectural observation window glass (zero milky/translucent haze!)
    booth_window_glass = {
        "color": (0.85, 0.94, 1.00),
        "roughness": 0.02,
        "metallic": 0.0,
        "opacity": 0.04,
        "emissive": False,
    }
    warm_ceiling_mat = dict(MATERIALS["steel_dark"])
    booth_inner_wall_mat = dict(MATERIALS["desk_hull"])

    oct_angles = [2.0 * math.pi * i / 8.0 + math.pi / 8.0 for i in range(8)]

    # 1. Under-Booth Cantilevered Support Brackets (Z = 23.2m .. 26.0m)
    w_sup = tower_half_width(BOOTH_Z - 2.8)
    for ang in oct_angles:
        ca, sa = math.cos(ang), math.sin(ang)
        p_in = (w_sup * ca, w_sup * sa, BOOTH_Z - 2.8)
        p_out = (r_booth * 0.96 * ca, r_booth * 0.96 * sa, z_floor - 0.15)
        p_mid = (r_booth * 0.62 * ca, r_booth * 0.62 * sa, z_floor - 0.15)
        add_strut(mesh, p_in, p_out, 0.15, MATERIALS["steel"], sides=6)
        add_strut(mesh, p_in, p_mid, 0.11, MATERIALS["steel_dark"], sides=6)

    # 2. Octagonal Floor Slab, Tapered Under-Hull Plenum Skirt & Operator Anti-Fatigue Floor Mats (No exterior balcony!)
    floor_top = [(r_booth * math.cos(a), r_booth * math.sin(a), z_floor) for a in oct_angles]
    floor_bot = [(3.25 * math.cos(a), 3.25 * math.sin(a), z_floor - 1.30) for a in oct_angles]

    add_face(mesh, floor_top, dict(MATERIALS["booth_floor"]))
    add_face(mesh, list(reversed(floor_bot)), dict(MATERIALS["steel_dark"]))

    # Interior octagonal deck inlay + recessed operator walkway anti-fatigue mat ring
    deck_pts = [(5.75 * math.cos(a), 5.75 * math.sin(a), z_floor + 0.02) for a in oct_angles]
    add_face(mesh, deck_pts, dict(MATERIALS["desk_trim"]))

    # Segmented anti-fatigue cushioned operator floor mat ring (R = 2.95m .. 4.15m) with brass safety bevels
    for i in range(8):
        ni = (i + 1) % 8
        a0, a1 = oct_angles[i], oct_angles[ni]
        ca0, sa0 = math.cos(a0), math.sin(a0)
        ca1, sa1 = math.cos(a1), math.sin(a1)
        m_in0 = (2.95 * ca0, 2.95 * sa0, z_floor + 0.028)
        m_in1 = (2.95 * ca1, 2.95 * sa1, z_floor + 0.028)
        m_out1 = (4.15 * ca1, 4.15 * sa1, z_floor + 0.028)
        m_out0 = (4.15 * ca0, 4.15 * sa0, z_floor + 0.028)
        add_quad(mesh, m_in0, m_in1, m_out1, m_out0, MATERIALS["desk_leather"])
        add_strut(mesh, m_in0, m_in1, 0.014, MATERIALS["brass"], sides=6)
        add_strut(mesh, m_out0, m_out1, 0.014, MATERIALS["brass"], sides=6)

        # Tapered octagonal under-hull structural plenum skirt
        add_quad(mesh, floor_bot[i], floor_bot[ni], floor_top[ni], floor_top[i], MATERIALS["steel_dark"])

    # Brass safety ring around the Central Lift Vestibule (R = 2.35m)
    add_ring_torus(mesh, 0.0, 0.0, z_floor + 0.04, 2.35, 0.035, MATERIALS["brass"], segs=32, tube_sides=6)

    # 2B. Central Lift Vestibule (R = 1.15m) with Bi-Parting Brass & Glass Doors facing NORTH (+Y = +1.12m) toward Broadcast Seat
    r_lift = 1.15
    add_ring_torus(mesh, 0.0, 0.0, z_floor + 0.05, r_lift + 0.04, 0.075, MATERIALS["brass"], segs=28, tube_sides=8)
    add_ring_torus(mesh, 0.0, 0.0, z_eave - 0.06, r_lift + 0.04, 0.075, MATERIALS["brass"], segs=28, tube_sides=8)
    add_ring_torus(mesh, 0.0, 0.0, z_floor + 2.34, r_lift + 0.02, 0.036, MATERIALS["brass"], segs=28, tube_sides=8)
    for deg in (-146, -90, -34, 34, 90, 146):
        ang_l = math.radians(deg)
        lx, ly = r_lift * math.sin(ang_l), r_lift * math.cos(ang_l)
        add_strut(
            mesh,
            (lx, ly, z_floor + 0.06),
            (lx, ly, z_eave - 0.06),
            0.052 if abs(deg) == 34 else 0.042,
            MATERIALS["brass"] if abs(deg) == 34 else MATERIALS["steel_dark"],
            sides=8,
        )
    # Bi-parting North-facing lift doors (parted open at x = ±0.52m, y = +1.12m) + overhead floor-indicator dial
    add_box(mesh, -0.74, 1.04, z_floor + 2.24, 0.74, 1.20, z_floor + 2.38, MATERIALS["bezel_dark"])
    add_box(mesh, -0.44, 1.06, z_floor + 2.40, 0.44, 1.20, z_floor + 2.62, MATERIALS["brass"])
    add_box(mesh, -0.38, 1.18, z_floor + 2.44, 0.38, 1.22, z_floor + 2.58, MATERIALS["cyan_glow"])
    for sx_s in (-1.0, 1.0):
        dx = sx_s * 0.52
        add_box(mesh, dx - 0.17, 1.08, z_floor + 0.06, dx + 0.17, 1.14, z_floor + 2.22, MATERIALS["brass"])

    # 3. Waist-High Solid Outer Wall (z = 0 .. +1.56m), Window Sill HVAC Plenum, Composite Mullions & Panoramic Windows
    r_wall_in = 5.85
    r_sill_plenum = 5.56
    r_win_top = 6.45
    u_transom = 0.72
    r_transom = r_booth + u_transom * (r_win_top - r_booth)
    z_transom = z_sill + u_transom * (z_eave - z_sill)

    for i in range(8):
        ni = (i + 1) % 8
        a0, a1 = oct_angles[i], oct_angles[ni]
        ca0, sa0 = math.cos(a0), math.sin(a0)
        ca1, sa1 = math.cos(a1), math.sin(a1)

        w_b0 = (r_booth * ca0, r_booth * sa0, z_floor)
        w_b1 = (r_booth * ca1, r_booth * sa1, z_floor)
        w_s0 = (r_booth * ca0, r_booth * sa0, z_sill)
        w_s1 = (r_booth * ca1, r_booth * sa1, z_sill)
        add_quad(mesh, w_b0, w_b1, w_s1, w_s0, MATERIALS["steel_dark"])

        wi_b0 = (r_wall_in * ca0, r_wall_in * sa0, z_floor)
        wi_b1 = (r_wall_in * ca1, r_wall_in * sa1, z_floor)
        wi_s0 = (r_wall_in * ca0, r_wall_in * sa0, z_sill)
        wi_s1 = (r_wall_in * ca1, r_wall_in * sa1, z_sill)
        add_quad(mesh, wi_b1, wi_b0, wi_s0, wi_s1, booth_inner_wall_mat)
        add_quad(mesh, wi_s0, wi_s1, w_s1, w_s0, MATERIALS["steel_light"])

        # Interior Window-Sill HVAC Defroster Ledge & Shielded Light Cove Trough (r = 5.56 .. 5.85m)
        pl_t0 = (r_sill_plenum * ca0, r_sill_plenum * sa0, z_sill + 0.02)
        pl_t1 = (r_sill_plenum * ca1, r_sill_plenum * sa1, z_sill + 0.02)
        pl_b0 = (r_sill_plenum * ca0, r_sill_plenum * sa0, z_sill - 0.04)
        pl_b1 = (r_sill_plenum * ca1, r_sill_plenum * sa1, z_sill - 0.04)
        add_quad(mesh, pl_t0, pl_t1, wi_s1, wi_s0, MATERIALS["bezel_dark"])
        add_quad(mesh, pl_b1, pl_b0, pl_t0, pl_t1, MATERIALS["steel_dark"])
        cv_t0 = (5.60 * ca0, 5.60 * sa0, z_sill + 0.11)
        cv_t1 = (5.60 * ca1, 5.60 * sa1, z_sill + 0.11)
        add_quad(mesh, pl_t1, pl_t0, cv_t0, cv_t1, MATERIALS["bezel_dark"])

        # Composite I-Beam Window Mullions & Bolted Brass Gussets
        eave0 = (r_win_top * ca0, r_win_top * sa0, z_eave)
        eave1 = (r_win_top * ca1, r_win_top * sa1, z_eave)
        eave_in0 = ((r_win_top - 0.18) * ca0, (r_win_top - 0.18) * sa0, z_eave - 0.04)
        eave_in1 = ((r_win_top - 0.18) * ca1, (r_win_top - 0.18) * sa1, z_eave - 0.04)
        add_strut(mesh, w_b0, w_s0, 0.16, MATERIALS["steel_dark"], sides=6)
        add_strut(mesh, w_s0, eave0, 0.14, MATERIALS["steel_dark"], sides=6)
        add_strut(mesh, wi_s0, eave_in0, 0.065, MATERIALS["steel"], sides=6)
        add_strut(mesh, eave0, eave1, 0.15, MATERIALS["steel_dark"], sides=6)
        add_strut(mesh, eave_in0, eave_in1, 0.075, MATERIALS["bezel_dark"], sides=6)
        add_strut(mesh, (r_wall_in * ca0, r_wall_in * sa0, z_sill - 0.06), (r_wall_in * ca0, r_wall_in * sa0, z_sill + 0.14), 0.095, MATERIALS["brass"], sides=6)
        add_strut(mesh, eave_in0, (eave_in0[0], eave_in0[1], z_eave - 0.18), 0.090, MATERIALS["brass"], sides=6)

        tr0 = (r_transom * ca0, r_transom * sa0, z_transom)
        tr1 = (r_transom * ca1, r_transom * sa1, z_transom)
        add_strut(mesh, tr0, tr1, 0.042, MATERIALS["bezel_dark"], sides=6)

        add_quad(mesh, w_s0, w_s1, eave1, eave0, booth_window_glass)

        add_strut(
            mesh,
            (5.68 * ca0, 5.68 * sa0, z_sill + 0.08),
            (5.68 * ca1, 5.68 * sa1, z_sill + 0.08),
            0.055,
            booth_warm,
            sides=8,
        )
        add_strut(
            mesh,
            (5.95 * ca0, 5.95 * sa0, z_eave - 0.16),
            (5.95 * ca1, 5.95 * sa1, z_eave - 0.16),
            0.085,
            booth_warm,
            sides=8,
        )

        add_strut(
            mesh,
            (1.85 * ca0, 1.85 * sa0, z_eave + 0.08),
            (r_win_top * 0.95 * ca0, r_win_top * 0.95 * sa0, z_eave + 0.08),
            0.085,
            MATERIALS["steel_dark"],
            sides=6,
        )
        add_strut(
            mesh,
            (1.90 * ca0, 1.90 * sa0, z_eave - 0.04),
            (r_win_top * 0.92 * ca0, r_win_top * 0.92 * sa0, z_eave - 0.04),
            0.048,
            MATERIALS["bezel_dark"],
            sides=6,
        )
        sconce_p0 = (2.0 * ca0, 2.0 * sa0, z_eave - 0.10)
        sconce_p1 = (5.6 * ca0, 5.6 * sa0, z_eave - 0.10)
        add_strut(mesh, sconce_p0, sconce_p1, 0.072, booth_warm, sides=8)

        mid_a = 0.5 * (a0 + a1)
        mca, msa = math.cos(mid_a), math.sin(mid_a)
        can_top = (4.20 * mca, 4.20 * msa, z_eave - 0.16)
        can_bot = (4.42 * mca, 4.42 * msa, z_eave - 0.36)
        add_strut(mesh, (4.20 * mca, 4.20 * msa, z_eave - 0.04), can_top, 0.025, MATERIALS["brass"], sides=6)
        add_strut(mesh, can_top, can_bot, 0.078, MATERIALS["bezel_dark"], sides=10)
        add_strut(
            mesh,
            (4.40 * mca, 4.40 * msa, z_eave - 0.34),
            (4.44 * mca, 4.44 * msa, z_eave - 0.38),
            0.062,
            MATERIALS["amber_glow"] if i % 2 == 0 else booth_warm,
            sides=10,
        )

    # Concentric Crimson Watchroom Chandelier Rings + Overhead Steel Raceway Housings
    add_ring_torus(mesh, 0.0, 0.0, z_eave - 0.11, 4.35, 0.095, MATERIALS["bezel_dark"], segs=32, tube_sides=8)
    add_ring_torus(mesh, 0.0, 0.0, z_eave - 0.18, 4.35, 0.11, booth_warm, segs=32, tube_sides=8)
    add_ring_torus(mesh, 0.0, 0.0, z_eave - 0.17, 2.55, 0.085, MATERIALS["bezel_dark"], segs=24, tube_sides=8)
    add_ring_torus(mesh, 0.0, 0.0, z_eave - 0.24, 2.55, 0.095, booth_warm, segs=24, tube_sides=8)

    # 4. Octagonal Booth Roof Cap (No rooftop handrail ring!)
    roof_eave = [(r_win_top * 1.03 * math.cos(a), r_win_top * 1.03 * math.sin(a), z_eave) for a in oct_angles]
    roof_top = [(r_booth * 0.86 * math.cos(a), r_booth * 0.86 * math.sin(a), z_roof) for a in oct_angles]
    for i in range(8):
        ni = (i + 1) % 8
        add_quad(mesh, roof_eave[i], roof_eave[ni], roof_top[ni], roof_top[i], MATERIALS["steel"])
    add_face(mesh, roof_top, dict(MATERIALS["steel_dark"]))
    add_face(mesh, list(reversed(roof_eave)), dict(warm_ceiling_mat))

    return grp
