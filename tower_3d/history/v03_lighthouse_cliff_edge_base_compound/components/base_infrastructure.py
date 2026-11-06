"""
Component: Headland Base Infrastructure Compound (Asteroid 3-5-1 Cliff Edge)
============================================================================
Models the off-grid survival & broadcast power compound perched on the
stepped basalt headland terraces behind and beside the GOR-9 cliff-edge tower:
  1. Pressurized Keeper's Habitat & Workshop Quonset (SW Headland Terrace) +
     enclosed pressurized transfer tunnel into the central Lighthouse Climb Tube.
  2. 50 kW Pebble-Bed Dilithium Reactor #2 Containment Vault, 6 Vertical
     Vacuum Radiator Fins, and Van Allen HVDC Step-Down Switchyard (NW Headland Terrace).
  3. Superconducting Cryo-Condenser Tanks & Cliff-Edge Chasm Supply Winch Crane
     (South-East Cliff Shoulder, overhanging the sheer 48m drop into Acheron Chasm).
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


def build_base_infrastructure(scene):
    grp = create_scene_group(scene, "02_Base_Infrastructure_Compound")
    mesh = grp.mesh

    # ── 1. Pressurized Keeper's Habitat & Workshop Quonset (SW Headland Terrace) ──
    hab_cx, hab_cy, hab_z0 = -14.8, -6.2, -1.60
    add_prism(
        mesh,
        cx=hab_cx,
        cy=hab_cy,
        rad=4.4,
        z_bot=hab_z0,
        z_top=hab_z0 + 3.4,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=0.96,
        mat_top=MATERIALS["steel"],
        mat_side_a=MATERIALS["hab_hull"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    add_prism(
        mesh,
        cx=hab_cx,
        cy=hab_cy,
        rad=2.4,
        z_bot=hab_z0 + 3.4,
        z_top=hab_z0 + 4.4,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=0.82,
        mat_top=MATERIALS["steel_light"],
        mat_side_a=MATERIALS["steel"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0
        wx = hab_cx + 4.25 * math.cos(ang)
        wy = hab_cy + 4.25 * math.sin(ang)
        add_box(
            mesh,
            wx - 0.35,
            wy - 0.35,
            hab_z0 + 1.5,
            wx + 0.35,
            wy + 0.35,
            hab_z0 + 2.2,
            MATERIALS["amber_glow"],
        )

    # Secondary Workshop Annex Quonset (South-West of Habitat)
    add_box(
        mesh,
        hab_cx - 6.2,
        hab_cy - 5.2,
        hab_z0,
        hab_cx - 1.2,
        hab_cy - 1.8,
        hab_z0 + 2.6,
        MATERIALS["hab_hull"],
    )
    add_box(
        mesh,
        hab_cx - 5.8,
        hab_cy - 4.8,
        hab_z0 + 2.6,
        hab_cx - 1.6,
        hab_cy - 2.2,
        hab_z0 + 3.0,
        MATERIALS["steel"],
    )

    # Enclosed Pressurized Transfer Tunnel from Keeper's Habitat to Central Climb Tube (Z = +1.15m)
    tunnel_p0 = (hab_cx + 3.2, hab_cy + 1.4, 1.15)
    tunnel_p1 = (-1.1, -0.5, 1.15)
    add_strut(mesh, tunnel_p0, tunnel_p1, 1.05, MATERIALS["hab_hull"], sides=8)
    for t in (0.15, 0.38, 0.62, 0.85):
        rx = tunnel_p0[0] + (tunnel_p1[0] - tunnel_p0[0]) * t
        ry = tunnel_p0[1] + (tunnel_p1[1] - tunnel_p0[1]) * t
        rz = 1.15
        add_ring_torus(mesh, rx, ry, rz, 1.12, 0.08, MATERIALS["steel_light"], segs=12, tube_sides=6)
        add_strut(mesh, (rx - 0.6, ry, -1.6), (rx - 0.6, ry, rz - 0.8), 0.12, MATERIALS["steel_dark"], sides=6)
        add_strut(mesh, (rx + 0.6, ry, -1.6), (rx + 0.6, ry, rz - 0.8), 0.12, MATERIALS["steel_dark"], sides=6)

    # Central Base Airlock Vestibule Collar at foot of the Lighthouse Climb Spine (Z = 0.0 .. +3.2m)
    add_prism(
        mesh,
        cx=0.0,
        cy=0.0,
        rad=2.15,
        z_bot=0.0,
        z_top=3.2,
        sides=8,
        rot_rad=math.pi / 8.0,
        taper=0.95,
        mat_top=MATERIALS["steel"],
        mat_side_a=MATERIALS["hab_hull"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    add_ring_torus(mesh, 0.0, 0.0, 3.2, 2.08, 0.12, MATERIALS["brass"], segs=16, tube_sides=6)

    # ── 2. 50 kW Pebble-Bed Dilithium Reactor #2 & Van Allen Switchyard (NW Headland Terrace) ──
    reac_cx, reac_cy, reac_z0 = -15.0, 11.8, -1.80
    add_prism(
        mesh,
        cx=reac_cx,
        cy=reac_cy,
        rad=3.6,
        z_bot=reac_z0,
        z_top=reac_z0 + 4.2,
        sides=6,
        rot_rad=0.15,
        taper=0.92,
        mat_top=MATERIALS["steel_dark"],
        mat_side_a=MATERIALS["steel"],
        mat_side_b=MATERIALS["steel_dark"],
    )
    add_ring_torus(
        mesh,
        reac_cx,
        reac_cy,
        reac_z0 + 4.35,
        2.5,
        0.18,
        MATERIALS["cyan_glow"],
        segs=24,
        tube_sides=8,
    )
    add_prism(
        mesh,
        cx=reac_cx,
        cy=reac_cy,
        rad=1.9,
        z_bot=reac_z0 + 4.2,
        z_top=reac_z0 + 4.9,
        sides=6,
        rot_rad=0.15,
        taper=0.85,
        mat_top=MATERIALS["steel_light"],
    )

    # 6 Vertical High-Emissivity Thermal Radiator Wings (West of Reactor)
    for r_i in range(6):
        ry = reac_cy - 3.75 + r_i * 1.5
        add_strut(
            mesh,
            (reac_cx - 2.8, ry, reac_z0 + 1.0),
            (reac_cx - 6.4, ry, reac_z0 + 1.0),
            0.11,
            MATERIALS["copper"],
            sides=6,
        )
        add_box(
            mesh,
            reac_cx - 6.2,
            ry - 0.08,
            reac_z0 + 1.0,
            reac_cx - 3.2,
            ry + 0.08,
            reac_z0 + 6.4,
            MATERIALS["steel_dark"],
        )
        add_strut(
            mesh,
            (reac_cx - 6.2, ry, reac_z0 + 6.45),
            (reac_cx - 3.2, ry, reac_z0 + 6.45),
            0.09,
            MATERIALS["brass"],
            sides=6,
        )

    # Van Allen HVDC Step-Down Switchyard (Between Reactor & Tower on NW Terrace)
    sw_cx, sw_cy, sw_z0 = -8.2, 13.5, -1.80
    add_box(
        mesh,
        sw_cx - 2.6,
        sw_cy - 2.2,
        sw_z0,
        sw_cx + 2.6,
        sw_cy + 2.2,
        sw_z0 + 2.4,
        MATERIALS["desk_hull"],
    )
    for b_i in (-1.4, 0.0, 1.4):
        bx = sw_cx + b_i
        add_strut(
            mesh,
            (bx, sw_cy, sw_z0 + 2.4),
            (bx, sw_cy, sw_z0 + 4.8),
            0.22,
            MATERIALS["steel_light"],
            sides=8,
        )
        for ring_z in (2.9, 3.5, 4.1):
            add_ring_torus(
                mesh,
                bx,
                sw_cy,
                sw_z0 + ring_z,
                0.34,
                0.06,
                MATERIALS["brass"],
                segs=12,
                tube_sides=6,
            )
        add_ring_torus(
            mesh,
            bx,
            sw_cy,
            sw_z0 + 4.75,
            0.28,
            0.06,
            MATERIALS["cyan_glow"],
            segs=12,
            tube_sides=6,
        )

    # Dual Armored Copper HVDC Feeder Conduits snaking from Switchyard into Tower Base Spine
    for dx_off in (-0.45, 0.45):
        add_strut(
            mesh,
            (sw_cx + 1.2 + dx_off, sw_cy - 2.0, 0.55),
            (dx_off, 1.6, 0.85),
            0.18,
            MATERIALS["copper"],
            sides=8,
        )

    # ── 3. Cryo-Condenser Tanks & Cliff-Edge Chasm Supply Winch Crane (South Cliff Shoulder) ──
    cryo_z0 = -1.80
    for c_idx, (cx, cy) in enumerate([(-2.8, -14.2), (-6.2, -16.8)]):
        add_prism(
            mesh,
            cx=cx,
            cy=cy,
            rad=2.1,
            z_bot=cryo_z0 + 0.8,
            z_top=cryo_z0 + 3.6,
            sides=8,
            rot_rad=c_idx * 0.4,
            taper=0.92,
            mat_top=MATERIALS["steel_light"],
            mat_side_a=MATERIALS["steel_light"],
            mat_side_b=MATERIALS["steel"],
        )
        for l_i in range(4):
            la = math.pi / 4.0 + l_i * math.pi / 2.0
            add_strut(
                mesh,
                (cx + 1.7 * math.cos(la), cy + 1.7 * math.sin(la), cryo_z0),
                (cx + 1.4 * math.cos(la), cy + 1.4 * math.sin(la), cryo_z0 + 1.2),
                0.10,
                MATERIALS["steel_dark"],
                sides=6,
            )
        add_ring_torus(mesh, cx, cy, cryo_z0 + 3.7, 1.1, 0.08, MATERIALS["cyan_glow"], segs=16, tube_sides=6)

    # Cryogenic Superconducting Feedline Pipe into Tower Base
    add_strut(mesh, (-2.8, -14.2, 0.4), (-0.8, -1.6, 0.7), 0.14, MATERIALS["steel_light"], sides=6)

    # Cantilevered Chasm Supply Winch & Jib Crane right on the SE Cliff Lip (+4.8, -12.8)
    # Overhangs the sheer 48m basalt cliff face to hoist cargo straight up from the chasm!
    crane_x, crane_y, crane_z0 = 4.8, -12.8, -1.80
    add_strut(mesh, (crane_x, crane_y, crane_z0), (crane_x, crane_y, crane_z0 + 6.8), 0.24, MATERIALS["steel"], sides=8)
    jib_tip = (crane_x + 6.5, crane_y - 3.5, crane_z0 + 8.8)
    add_strut(mesh, (crane_x, crane_y, crane_z0 + 5.8), jib_tip, 0.16, MATERIALS["brass"], sides=6)
    add_strut(mesh, (crane_x, crane_y, crane_z0 + 6.8), jib_tip, 0.06, MATERIALS["steel_light"], sides=6)
    # Long hoist cable dropping down past the sheer cliff edge into the chasm (to Z = -18m)
    add_strut(mesh, jib_tip, (jib_tip[0], jib_tip[1], -18.0), 0.04, MATERIALS["steel_light"], sides=6)
    add_box(
        mesh,
        jib_tip[0] - 0.35,
        jib_tip[1] - 0.35,
        -18.8,
        jib_tip[0] + 0.35,
        jib_tip[1] + 0.35,
        -18.0,
        MATERIALS["amber_glow"],
    )

    return grp
