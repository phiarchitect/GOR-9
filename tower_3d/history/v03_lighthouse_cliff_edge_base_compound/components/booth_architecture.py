"""
Component: Cantilevered Octagonal Broadcast Booth Architecture (Z = +26.0m)
===========================================================================
Models the octagonal glass-and-steel broadcast observation pod cantilevered
around the continuous lattice tower at Z = 26.0m:
  - 8 heavy under-hull steel support brackets
  - 360° exterior catwalk deck + guardrails
  - Waist-high outer wall (z = 0 .. +1.56m) sized for standup perimeter consoles
  - Outward-tilted panoramic observation windows (z = +1.56m .. +4.75m)
  - Radial ceiling trusses, warm amber overhead sconces, roof EVA walkway ring,
    and rooftop 'GOR-9' neon beacon frame.
"""

import math
from .primitives import (
    BOOTH_Z,
    MATERIALS,
    add_box,
    add_face,
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

    # 2. Octagonal Floor Slab & Exterior 360° Catwalk Deck
    floor_top = [(r_booth * math.cos(a), r_booth * math.sin(a), z_floor) for a in oct_angles]
    floor_bot = [(r_booth * 0.94 * math.cos(a), r_booth * 0.94 * math.sin(a), z_floor - 0.38) for a in oct_angles]
    cat_top = [(r_catwalk * math.cos(a), r_catwalk * math.sin(a), z_floor - 0.05) for a in oct_angles]
    cat_bot = [(r_catwalk * math.cos(a), r_catwalk * math.sin(a), z_floor - 0.24) for a in oct_angles]

    add_face(mesh, floor_top, dict(MATERIALS["booth_floor"]))
    add_face(mesh, list(reversed(floor_bot)), dict(MATERIALS["steel_dark"]))

    # Interior dark octagonal anti-fatigue deck inlay
    deck_pts = [(5.75 * math.cos(a), 5.75 * math.sin(a), z_floor + 0.02) for a in oct_angles]
    add_face(mesh, deck_pts, dict(MATERIALS["desk_trim"]))

    # Brass safety ring around the central lattice tower penetration (R = 2.65m)
    add_ring_torus(mesh, 0.0, 0.0, z_floor + 0.04, 2.65, 0.045, MATERIALS["brass"], segs=32, tube_sides=6)

    for i in range(8):
        ni = (i + 1) % 8
        add_quad(mesh, floor_bot[i], floor_bot[ni], floor_top[ni], floor_top[i], MATERIALS["steel"])
        # Catwalk ring quad
        add_quad(mesh, floor_top[i], floor_top[ni], cat_top[ni], cat_top[i], MATERIALS["steel_dark"])
        add_quad(mesh, cat_bot[i], cat_bot[ni], cat_top[ni], cat_top[i], MATERIALS["steel"])

        # Catwalk guardrail posts & rails
        p_rail0 = (r_catwalk * 0.98 * math.cos(oct_angles[i]), r_catwalk * 0.98 * math.sin(oct_angles[i]), z_floor - 0.05)
        p_rail1 = (r_catwalk * 0.98 * math.cos(oct_angles[ni]), r_catwalk * 0.98 * math.sin(oct_angles[ni]), z_floor - 0.05)
        add_strut(mesh, p_rail0, (p_rail0[0], p_rail0[1], z_floor + 1.05), 0.04, MATERIALS["steel_light"], sides=6)
        add_strut(
            mesh,
            (p_rail0[0], p_rail0[1], z_floor + 1.05),
            (p_rail1[0], p_rail1[1], z_floor + 1.05),
            0.035,
            MATERIALS["steel_light"],
            sides=6,
        )
        add_strut(
            mesh,
            (p_rail0[0], p_rail0[1], z_floor + 0.52),
            (p_rail1[0], p_rail1[1], z_floor + 0.52),
            0.025,
            MATERIALS["steel"],
            sides=6,
        )

    # 3. Waist-High Solid Outer Wall (z = 0 .. +1.56m) & Outward-Tilted Panoramic Windows
    r_wall_in = 5.85
    r_win_top = 6.45  # outward-tilted observation glass
    for i in range(8):
        ni = (i + 1) % 8
        a0, a1 = oct_angles[i], oct_angles[ni]
        ca0, sa0 = math.cos(a0), math.sin(a0)
        ca1, sa1 = math.cos(a1), math.sin(a1)

        # Lower knee-wall (exterior & interior faces up to z_sill = +1.56m)
        w_b0 = (r_booth * ca0, r_booth * sa0, z_floor)
        w_b1 = (r_booth * ca1, r_booth * sa1, z_floor)
        w_s0 = (r_booth * ca0, r_booth * sa0, z_sill)
        w_s1 = (r_booth * ca1, r_booth * sa1, z_sill)
        add_quad(mesh, w_b0, w_b1, w_s1, w_s0, MATERIALS["steel_dark"])

        wi_b0 = (r_wall_in * ca0, r_wall_in * sa0, z_floor)
        wi_b1 = (r_wall_in * ca1, r_wall_in * sa1, z_floor)
        wi_s0 = (r_wall_in * ca0, r_wall_in * sa0, z_sill)
        wi_s1 = (r_wall_in * ca1, r_wall_in * sa1, z_sill)
        add_quad(mesh, wi_b1, wi_b0, wi_s0, wi_s1, MATERIALS["desk_hull"])
        # Window sill capledge at z_sill (+1.56m)
        add_quad(mesh, wi_s0, wi_s1, w_s1, w_s0, MATERIALS["steel_light"])

        # Heavy corner structural mullions (tilted outward from sill to eave)
        eave0 = (r_win_top * ca0, r_win_top * sa0, z_eave)
        eave1 = (r_win_top * ca1, r_win_top * sa1, z_eave)
        add_strut(mesh, w_b0, w_s0, 0.14, MATERIALS["steel"], sides=6)
        add_strut(mesh, w_s0, eave0, 0.12, MATERIALS["steel"], sides=6)
        add_strut(mesh, eave0, eave1, 0.13, MATERIALS["steel_dark"], sides=6)

        # Panoramic semi-transparent observation window pane (leave South airlock door bay i=5 slightly framed)
        add_quad(mesh, w_s0, w_s1, eave1, eave0, MATERIALS["glass"])

        # Radial interior ceiling I-beam truss + warm amber sconce strip
        add_strut(
            mesh,
            (1.85 * ca0, 1.85 * sa0, z_eave + 0.08),
            (r_win_top * 0.95 * ca0, r_win_top * 0.95 * sa0, z_eave + 0.08),
            0.09,
            MATERIALS["steel_dark"],
            sides=6,
        )
        sconce_p0 = (3.4 * ca0, 3.4 * sa0, z_eave + 0.02)
        sconce_p1 = (5.0 * ca0, 5.0 * sa0, z_eave + 0.02)
        add_strut(mesh, sconce_p0, sconce_p1, 0.04, MATERIALS["amber_glow"], sides=6)

    # 4. Octagonal Booth Roof Cap & EVA Roof Service Walkway
    roof_eave = [(r_win_top * 1.03 * math.cos(a), r_win_top * 1.03 * math.sin(a), z_eave) for a in oct_angles]
    roof_top = [(r_booth * 0.86 * math.cos(a), r_booth * 0.86 * math.sin(a), z_roof) for a in oct_angles]
    for i in range(8):
        ni = (i + 1) % 8
        add_quad(mesh, roof_eave[i], roof_eave[ni], roof_top[ni], roof_top[i], MATERIALS["steel"])
    add_face(mesh, roof_top, dict(MATERIALS["steel_dark"]))
    add_face(mesh, list(reversed(roof_eave)), dict(MATERIALS["desk_trim"]))

    # Rooftop EVA Safety Handrail Ring around the upper climb hatch so the keeper can walk on the roof
    add_ring_torus(mesh, 0.0, 0.0, z_roof + 0.95, 3.25, 0.04, MATERIALS["steel_light"], segs=16, tube_sides=6)
    add_ring_torus(mesh, 0.0, 0.0, z_roof + 0.48, 3.25, 0.03, MATERIALS["brass"], segs=16, tube_sides=6)
    for i in range(8):
        ang = oct_angles[i]
        rx, ry = 3.25 * math.cos(ang), 3.25 * math.sin(ang)
        add_strut(mesh, (rx, ry, z_roof), (rx, ry, z_roof + 0.98), 0.035, MATERIALS["steel_light"], sides=6)

    # 5. Rooftop 'GOR-9' Amber Neon Station Beacon Frame (North-facing eave)
    sign_y = r_booth * 0.78
    sign_z0 = z_roof + 0.15
    add_box(mesh, -2.1, sign_y - 0.12, sign_z0, 2.1, sign_y + 0.12, sign_z0 + 1.05, MATERIALS["steel_dark"])
    add_box(mesh, -1.9, sign_y + 0.10, sign_z0 + 0.18, 1.9, sign_y + 0.18, sign_z0 + 0.88, MATERIALS["neon_sign"])

    return grp
