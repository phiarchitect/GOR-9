"""
Component: Perimeter Standup Broadcast & Telemetry Consoles (7 Octagon Wall Bays)
=================================================================================
Models the 7 standup-height (+1.05m) console bays mounted flush against the
outer octagonal walls (r_wall = 5.15m) directly under the panoramic window
sills (+1.56m), leaving the South bay (270°) clear for the catwalk airlock door.
Each console bay is self-contained and parameterized so individual bays, screen
textures, or physical controls can be updated independently.
"""

import math
from pathlib import Path
from .primitives import (
    BOOTH_Z,
    MATERIALS,
    add_quad,
    add_textured_quad,
    create_scene_group,
)


CONSOLE_BAY_SPECS = [
    {
        "group_name": "05A_Console_Wall_N_Master_MK4",
        "azimuth_deg": 90.0,
        "width": 3.50,
        "left_screen": "mk4_3b_video.png",
        "right_screen": "mk4_3a_decoder.png",
        "badge": "hauser_dynamics_logo.jpg",
        "is_master_mic_bay": True,
    },
    {
        "group_name": "05B_Console_Wall_NE_VanAllen_VA4",
        "azimuth_deg": 45.0,
        "width": 3.40,
        "left_screen": "va4_1b_squall.png",
        "right_screen": "mk4_3c_atlas.png",
        "badge": "van_allen_switchgear_logo.jpg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05C_Console_Wall_E_Euclid_ED9",
        "azimuth_deg": 0.0,
        "width": 3.40,
        "left_screen": "ed9_4d_step4.png",
        "right_screen": "ed9_4b_step1.png",
        "badge": "van_allen_switchgear_logo.jpg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05D_Console_Wall_SE_Bogey9_UAP",
        "azimuth_deg": 315.0,
        "width": 3.40,
        "left_screen": "bogey_4a_frame6.png",
        "right_screen": "bogey_4a_nvg.png",
        "badge": "hauser_dynamics_logo.jpg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05E_Console_Wall_NW_Station_Dossier",
        "azimuth_deg": 135.0,
        "width": 3.40,
        "left_screen": "dos_3a_n24.png",
        "right_screen": "dos_3d_octal_back.png",
        "badge": "hauser_dynamics_logo.jpg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05F_Console_Wall_W_Spectrum_Comet",
        "azimuth_deg": 180.0,
        "width": 3.40,
        "left_screen": "mk4_3c_spectrum.png",
        "right_screen": "va4_1a_comet.png",
        "badge": "hauser_dynamics_logo.jpg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05G_Console_Wall_SW_Reactor_Rhombus",
        "azimuth_deg": 225.0,
        "width": 3.40,
        "left_screen": "va4_2b_stepdown.png",
        "right_screen": "ed9_5a_rhombus.png",
        "badge": "van_allen_switchgear_logo.jpg",
        "is_master_mic_bay": False,
    },
]


def build_single_perimeter_console(
    mesh,
    azimuth_deg: float,
    r_wall: float,
    width: float,
    tex_left: Path,
    tex_right: Path,
    badge_tex: Path = None,
    is_master_mic_bay: bool = False,
):
    """
    Build a standup-height perimeter console bay flush against the octagon outer wall.
    Local coordinates:
      - Origin (0, 0, 0) is on the booth floor at the center of the flat outer wall (r_wall = 5.15m).
      - +Y points OUTWARD toward the octagon wall & window sill.
      - -Y points INWARD toward the booth center & standing operator.
      - +X points along the wall to the operator's right.
      - +Z points UP from the booth floor.
    """
    hw = width * 0.5
    yaw_rad = math.radians(azimuth_deg - 90.0)
    c, s = math.cos(yaw_rad), math.sin(yaw_rad)
    cx = r_wall * math.cos(math.radians(azimuth_deg))
    cy = r_wall * math.sin(math.radians(azimuth_deg))
    cz = BOOTH_Z

    def xf(pt):
        lx, ly, lz = pt
        return (cx + lx * c - ly * s, cy + lx * s + ly * c, cz + lz)

    def add_quad_xf(p0, p1, p2, p3, attrs):
        add_quad(mesh, xf(p0), xf(p1), xf(p2), xf(p3), attrs)

    def add_tex_xf(p0, p1, p2, p3, tex_path, color=(0.95, 0.98, 1.0), emissive=True):
        add_textured_quad(mesh, xf(p0), xf(p1), xf(p2), xf(p3), tex_path, color=color, emissive=emissive)

    def add_box_xf(x0, y0, z0, x1, y1, z1, attrs):
        p000, p100, p110, p010 = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
        p001, p101, p111, p011 = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
        add_quad_xf(p000, p010, p110, p100, attrs)
        add_quad_xf(p001, p101, p111, p011, attrs)
        add_quad_xf(p000, p100, p101, p001, attrs)
        add_quad_xf(p100, p110, p111, p101, attrs)
        add_quad_xf(p110, p010, p011, p111, attrs)
        add_quad_xf(p010, p000, p001, p011, attrs)

    y_front = -1.18 if is_master_mic_bay else -0.96
    y_ped_front = -0.62
    y_wall_back = 0.10
    z_desk_bot = 0.98
    z_desk_top = 1.05

    # 1. Recessed lower equipment pedestal + standup footrest bar at z = 0.24m
    add_box_xf(-hw, y_ped_front, 0.04, hw, y_wall_back, z_desk_bot, MATERIALS["desk_hull"])
    add_box_xf(-hw + 0.08, y_ped_front - 0.14, 0.22, hw - 0.08, y_ped_front - 0.08, 0.26, MATERIALS["steel"])
    # Standup counter top slab (z = 0.98m to 1.05m) + amber wrist bolster
    add_box_xf(-hw - 0.03, y_front, z_desk_bot, hw + 0.03, y_wall_back + 0.04, z_desk_top, MATERIALS["desk_trim"])
    add_box_xf(-hw - 0.02, y_front - 0.03, z_desk_bot + 0.01, hw + 0.02, y_front + 0.03, z_desk_top + 0.015, MATERIALS["amber_glow"])

    # 2. Low-Profile Sloped Monitor Wedge Cabinet TUCKED DIRECTLY UNDER THE WINDOW SILL (z = 1.05m to 1.55m)
    yb, zb = -0.44, 1.05
    yt, zt = 0.12, 1.55
    yr = 0.16
    add_quad_xf((-hw, yb, zb), (-hw, yt, zt), (-hw, yr, zt), (-hw, yr, zb), MATERIALS["desk_hull"])
    add_quad_xf((hw, yb, zb), (hw, yr, zb), (hw, yr, zt), (hw, yt, zt), MATERIALS["desk_hull"])
    add_quad_xf((-hw, yb, zb), (hw, yb, zb), (hw, yt, zt), (-hw, yt, zt), MATERIALS["desk_trim"])
    add_quad_xf((-hw, yt, zt), (hw, yt, zt), (hw, yr, zt), (-hw, yr, zt), MATERIALS["desk_hull"])
    add_quad_xf((hw, yr, zb), (-hw, yr, zb), (-hw, yr, zt), (hw, yr, zt), MATERIALS["desk_hull"])

    # 3. Twin Side-by-Side 16:9 Console Screens on the sloped under-window wedge
    u0, u1 = 0.07, 0.93
    sy0 = yb + u0 * (yt - yb) - 0.020
    sz0 = zb + u0 * (zt - zb) + 0.012
    sy1 = yb + u1 * (yt - yb) - 0.020
    sz1 = zb + u1 * (zt - zb) + 0.012

    scr_gap = 0.06
    scr_w = (width - 0.24 - scr_gap) * 0.5
    lx0, lx1 = -scr_gap * 0.5 - scr_w, -scr_gap * 0.5
    add_tex_xf((lx0, sy0, sz0), (lx1, sy0, sz0), (lx1, sy1, sz1), (lx0, sy1, sz1), tex_left)

    rx0, rx1 = scr_gap * 0.5, scr_gap * 0.5 + scr_w
    add_tex_xf((rx0, sy0, sz0), (rx1, sy0, sz0), (rx1, sy1, sz1), (rx0, sy1, sz1), tex_right)

    # 4. Physical Rotary Tuning Knobs & Illuminated Pushbuttons on the standup counter apron
    if not is_master_mic_bay:
        for kx in (-width * 0.36, -width * 0.18, width * 0.18, width * 0.36):
            add_box_xf(kx - 0.045, -0.64, z_desk_top, kx + 0.045, -0.55, z_desk_top + 0.055, MATERIALS["brass"])
        for bx_i in range(8):
            bx = -width * 0.38 + bx_i * (width * 0.108)
            glow = MATERIALS["cyan_glow"] if (bx_i % 2 == 0) else MATERIALS["amber_glow"]
            add_box_xf(bx - 0.03, -0.78, z_desk_top, bx + 0.03, -0.72, z_desk_top + 0.03, glow)

    # 5. Riveted Manufacturer Nameplate on the recessed pedestal front skirt
    if badge_tex and badge_tex.exists():
        bw = 0.42
        add_tex_xf(
            (-bw, y_ped_front - 0.01, 0.68),
            (bw, y_ped_front - 0.01, 0.68),
            (bw, y_ped_front - 0.01, 0.90),
            (-bw, y_ped_front - 0.01, 0.90),
            badge_tex,
            color=(0.95, 0.85, 0.65),
            emissive=True,
        )


def build_perimeter_consoles(scene, repo_root: Path):
    consoles_dir = repo_root / "docs" / "assets" / "consoles"
    plates_dir = repo_root / "docs" / "assets" / "plates"
    groups = []
    for spec in CONSOLE_BAY_SPECS:
        grp = create_scene_group(scene, spec["group_name"])
        build_single_perimeter_console(
            grp.mesh,
            azimuth_deg=spec["azimuth_deg"],
            r_wall=5.15,
            width=spec["width"],
            tex_left=consoles_dir / spec["left_screen"],
            tex_right=consoles_dir / spec["right_screen"],
            badge_tex=plates_dir / spec["badge"],
            is_master_mic_bay=spec["is_master_mic_bay"],
        )
        groups.append(grp)
    return groups
