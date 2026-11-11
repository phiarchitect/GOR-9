"""
Component: Perimeter Standup Broadcast & Telemetry Consoles (7 Octagon Wall Bays + 6 Corner Wedges)
===================================================================================================
Models the 7 standup-height (+1.05m) console bays mounted flush against the
outer octagonal walls (r_wall = 5.15m) directly under the panoramic window
sills (+1.56m), leaving the South bay (270°) clear for the catwalk airlock door,
plus 6 mitered 45° octagonal corner wedge modules uniting the horseshoe.

Realism features:
  - 3-bay 19-inch EIA equipment rack pedestals with recessed rack drawers,
    pull handles, cooling louvers, circuit breakers, framed manufacturer
    nameplates, analog bus meters, and braided coax floor trunks.
  - Dark cushioned leather ergonomic wrist bolsters with machined brass accent
    trim and recessed under-counter LED rack-illumination strips.
  - Sloped tactile switchbank control aprons with cylindrical fluted rotary
    encoders, slotted broadcast fader banks, guarded toggles, backlit legend
    pushbuttons inside dark bezels, and recessed telemetry keyer decks.
  - Deep-set cast-aluminum monitor bezels, 3-sided ATC anti-glare sunhoods,
    central vertical PPM bargraph instrument bridge, and gooseneck task lamps.
"""

import math
from pathlib import Path
from .primitives import (
    BOOTH_Z,
    MATERIALS,
    add_face,
    add_quad,
    add_strut,
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
        "badge": "hauser_logo.svg",
        "is_master_mic_bay": True,
    },
    {
        "group_name": "05B_Console_Wall_NE_VanAllen_VA4",
        "azimuth_deg": 45.0,
        "width": 3.40,
        "left_screen": "va4_1b_squall.png",
        "right_screen": "mk4_3c_atlas.png",
        "badge": "van_allen_logo.svg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05C_Console_Wall_E_Euclid_ED9",
        "azimuth_deg": 0.0,
        "width": 3.40,
        "left_screen": "ed9_4d_step4.png",
        "right_screen": "ed9_4b_step1.png",
        "badge": "van_allen_logo.svg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05D_Console_Wall_SE_Bogey9_UAP",
        "azimuth_deg": 315.0,
        "width": 3.40,
        "left_screen": "bogey_4a_frame6.png",
        "right_screen": "bogey_4a_nvg.png",
        "badge": "hauser_logo.svg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05E_Console_Wall_NW_Station_Dossier",
        "azimuth_deg": 135.0,
        "width": 3.40,
        "left_screen": "dos_3a_n24.png",
        "right_screen": "dos_3d_octal_back.png",
        "badge": "hauser_logo.svg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05F_Console_Wall_W_Spectrum_Comet",
        "azimuth_deg": 180.0,
        "width": 3.40,
        "left_screen": "mk4_3c_spectrum.png",
        "right_screen": "va4_1a_comet.png",
        "badge": "hauser_logo.svg",
        "is_master_mic_bay": False,
    },
    {
        "group_name": "05G_Console_Wall_SW_Reactor_Rhombus",
        "azimuth_deg": 225.0,
        "width": 3.40,
        "left_screen": "va4_2b_stepdown.png",
        "right_screen": "ed9_5a_rhombus.png",
        "badge": "van_allen_logo.svg",
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

    def add_strut_xf(p0, p1, rad, attrs, sides=8):
        add_strut(mesh, xf(p0), xf(p1), rad, attrs, sides=sides)

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
    y_ped_front = -0.60
    y_wall_back = 0.14
    z_desk_bot = 0.98
    z_desk_top = 1.05

    # ── 1. 3-BAY 19-INCH EIA EQUIPMENT RACK PEDESTAL (z = 0.00 .. 0.98m) ──
    # Recessed dark toe-kick plinth (z = 0.00 .. 0.09m)
    add_box_xf(-hw, y_ped_front + 0.07, 0.00, hw, y_wall_back, 0.09, MATERIALS["bezel_dark"])
    # Main rack cabinet hull (z = 0.09 .. 0.98m)
    add_box_xf(-hw, y_ped_front, 0.09, hw, y_wall_back, z_desk_bot, MATERIALS["desk_hull"])

    # 4 vertical EIA rack stiles dividing the pedestal into 3 bays (Left Rack, Center Instrument/Badge, Right Rack)
    stile_xs = [-hw + 0.04, -0.52, 0.52, hw - 0.04]
    for sx in stile_xs:
        add_box_xf(sx - 0.025, y_ped_front - 0.022, 0.09, sx + 0.025, y_ped_front + 0.01, z_desk_bot, MATERIALS["steel_dark"])
        # Footrest mounting bracket on each vertical rack stile
        add_strut_xf((sx, y_ped_front, 0.23), (sx, y_ped_front - 0.14, 0.23), 0.016, MATERIALS["steel_dark"], sides=6)

    # Heavy tubular brushed-chrome footrest bar (z = 0.23m)
    add_strut_xf((-hw + 0.06, y_ped_front - 0.14, 0.23), (hw - 0.06, y_ped_front - 0.14, 0.23), 0.022, MATERIALS["steel_light"], sides=12)

    # Left & Right 19-Inch Rack Bays: 3 stacked rack-mount chassis drawers with U-handles, cooling louvers & pilot LEDs
    for bay_x0, bay_x1 in [(-hw + 0.08, -0.56), (0.56, hw - 0.08)]:
        for r_idx, (rz0, rz1) in enumerate([(0.13, 0.38), (0.40, 0.66), (0.68, 0.93)]):
            add_box_xf(bay_x0, y_ped_front - 0.012, rz0, bay_x1, y_ped_front + 0.005, rz1, MATERIALS["rack_panel"])
            # Top & bottom rack-unit seam rails
            add_box_xf(bay_x0, y_ped_front - 0.016, rz1 - 0.012, bay_x1, y_ped_front, rz1, MATERIALS["bezel_dark"])
            # Rack pull handles on left and right ears
            rmid_z = 0.5 * (rz0 + rz1)
            for hx in (bay_x0 + 0.05, bay_x1 - 0.05):
                add_strut_xf((hx, y_ped_front - 0.042, rmid_z - 0.055), (hx, y_ped_front - 0.042, rmid_z + 0.055), 0.008, MATERIALS["steel_light"], sides=6)
                add_strut_xf((hx, y_ped_front - 0.012, rmid_z - 0.055), (hx, y_ped_front - 0.042, rmid_z - 0.055), 0.007, MATERIALS["steel"], sides=6)
                add_strut_xf((hx, y_ped_front - 0.012, rmid_z + 0.055), (hx, y_ped_front - 0.042, rmid_z + 0.055), 0.007, MATERIALS["steel"], sides=6)
            # Horizontal cooling louver slots across center of drawer
            for lv in range(3):
                lz = rz0 + 0.055 + lv * 0.055
                add_box_xf(bay_x0 + 0.12, y_ped_front - 0.018, lz, bay_x1 - 0.12, y_ped_front - 0.008, lz + 0.016, MATERIALS["bezel_dark"])
            # Status pilot lamp & circuit breaker toggle
            pilot_mat = MATERIALS["cyan_glow"] if ((r_idx + int(bay_x0 > 0)) % 2 == 0) else MATERIALS["amber_glow"]
            add_box_xf(bay_x1 - 0.10, y_ped_front - 0.022, rmid_z + 0.02, bay_x1 - 0.075, y_ped_front - 0.010, rmid_z + 0.042, pilot_mat)
            add_box_xf(bay_x0 + 0.075, y_ped_front - 0.024, rmid_z, bay_x0 + 0.095, y_ped_front - 0.010, rmid_z + 0.03, MATERIALS["brass"])

    # Center Rack Bay: Beveled Manufacturer Nameplate + Dual Analog Bus Meters + Coax Umbilical Trunk
    add_box_xf(-0.48, y_ped_front - 0.010, 0.13, 0.48, y_ped_front + 0.005, 0.93, MATERIALS["rack_panel"])
    if badge_tex and badge_tex.exists():
        bw = 0.42
        # Extruded dark-steel & brass nameplate bezel frame
        add_box_xf(-bw - 0.025, y_ped_front - 0.024, 0.645, bw + 0.025, y_ped_front - 0.008, 0.915, MATERIALS["bezel_dark"])
        add_box_xf(-bw - 0.012, y_ped_front - 0.028, 0.655, bw + 0.012, y_ped_front - 0.012, 0.905, MATERIALS["brass"])
        add_tex_xf(
            (-bw, y_ped_front - 0.031, 0.665),
            (bw, y_ped_front - 0.031, 0.665),
            (bw, y_ped_front - 0.031, 0.895),
            (-bw, y_ped_front - 0.031, 0.895),
            badge_tex,
            color=(0.94, 0.88, 0.76),
            emissive=False,
        )
    # Dual recessed analog bus meters & patch panel below the nameplate (z = 0.36 .. 0.60m)
    add_box_xf(-0.42, y_ped_front - 0.020, 0.36, 0.42, y_ped_front - 0.008, 0.60, MATERIALS["bezel_dark"])
    for mx, m_glow in [(-0.22, MATERIALS["amber_glow"]), (0.22, MATERIALS["cyan_glow"])]:
        add_strut_xf((mx, y_ped_front - 0.008, 0.48), (mx, y_ped_front - 0.032, 0.48), 0.075, MATERIALS["brass"], sides=12)
        add_strut_xf((mx, y_ped_front - 0.012, 0.48), (mx, y_ped_front - 0.035, 0.48), 0.058, m_glow, sides=12)
    # Braided coaxial umbilical conduits dropping from lower rack into booth floor gland
    for cx_off in (-0.14, 0.14):
        add_strut_xf((cx_off, y_ped_front - 0.02, 0.34), (cx_off, y_ped_front - 0.06, 0.00), 0.024, MATERIALS["steel_dark"], sides=8)
        add_strut_xf((cx_off, y_ped_front - 0.06, 0.00), (cx_off, y_ped_front - 0.06, 0.045), 0.036, MATERIALS["brass"], sides=8)

    # ── 2. ANODIZED COUNTERTOP, CUSHIONED LEATHER WRIST BOLSTER & UNDER-COUNTER TASK LIGHT ──
    # Main standup counter slab (z = 0.98 .. 1.05m)
    add_box_xf(-hw - 0.02, y_front + 0.05, z_desk_bot, hw + 0.02, y_wall_back + 0.04, z_desk_top, MATERIALS["desk_trim"])
    # Machined brass trim strip between desktop and padded leather wrist bolster
    add_box_xf(-hw - 0.022, y_front + 0.038, z_desk_bot + 0.004, hw + 0.022, y_front + 0.052, z_desk_top + 0.006, MATERIALS["brass"])
    # Cushioned dark charcoal leather ergonomic wrist bolster along the front bullnose edge (replaces the giant glowing yellow bar!)
    add_box_xf(-hw - 0.025, y_front - 0.045, z_desk_bot + 0.008, hw + 0.025, y_front + 0.038, z_desk_top + 0.014, MATERIALS["desk_leather"])
    add_box_xf(-hw - 0.022, y_front - 0.056, z_desk_bot + 0.016, hw + 0.022, y_front - 0.045, z_desk_top + 0.006, MATERIALS["desk_leather"])
    # End-cap cheek plates on wrist bolster
    for sx in (-hw - 0.028, hw + 0.025):
        add_box_xf(sx, y_front - 0.056, z_desk_bot, sx + 0.006, y_front + 0.052, z_desk_top + 0.016, MATERIALS["brass"])
    # Subtle recessed amber status tally pips embedded in the brass bolster strip
    for tx_i in range(5):
        tx = -hw * 0.76 + tx_i * (hw * 0.38)
        add_box_xf(tx - 0.028, y_front + 0.040, z_desk_top + 0.004, tx + 0.028, y_front + 0.050, z_desk_top + 0.009, MATERIALS["amber_glow"])
    # Shielded recessed under-counter warm LED strip illuminating the equipment racks below
    add_box_xf(-hw + 0.12, y_ped_front - 0.08, z_desk_bot - 0.014, hw - 0.12, y_ped_front - 0.05, z_desk_bot - 0.002, MATERIALS["amber_glow"])
    add_box_xf(-hw + 0.10, y_ped_front - 0.095, z_desk_bot - 0.022, hw - 0.10, y_ped_front - 0.08, z_desk_bot, MATERIALS["bezel_dark"])

    # ── 3. SLOPED TACTILE SWITCHBANK CONTROL APRON (y = -0.65 .. -0.44m, z = 1.05 .. 1.13m) ──
    ya0, za0 = -0.65, 1.05
    ya1, za1 = -0.44, 1.13
    add_quad_xf((-hw, ya0, za0), (hw, ya0, za0), (hw, ya1, za1), (-hw, ya1, za1), MATERIALS["rack_panel"])
    add_quad_xf((-hw, ya0, za0), (-hw, ya1, za1), (-hw, ya1, 1.05), (-hw, ya0, 1.05), MATERIALS["bezel_dark"])
    add_quad_xf((hw, ya0, za0), (hw, ya0, 1.05), (hw, ya1, 1.05), (hw, ya1, za1), MATERIALS["bezel_dark"])
    # Front lip bezel of the control apron
    add_box_xf(-hw, ya0 - 0.015, 1.05, hw, ya0 + 0.005, 1.064, MATERIALS["bezel_dark"])

    def add_rotary_encoder(kx, u_apron, rad=0.036, h_knob=0.034, cap_mat=None, ring_mat=None):
        ky = ya0 + u_apron * (ya1 - ya0)
        kz = za0 + u_apron * (za1 - za0)
        # Normal to apron points upward and slightly inward (-Y, +Z)
        ny_a, nz_a = -0.35, 0.936
        p_base = (kx, ky, kz)
        p_ring = (kx, ky + ny_a * 0.006, kz + nz_a * 0.006)
        p_skirt = (kx, ky + ny_a * (h_knob * 0.65), kz + nz_a * (h_knob * 0.65))
        p_top = (kx, ky + ny_a * h_knob, kz + nz_a * h_knob)
        if ring_mat:
            add_strut_xf(p_base, p_ring, rad * 1.18, ring_mat, sides=14)
        add_strut_xf(p_ring, p_skirt, rad, MATERIALS["bezel_dark"], sides=14)
        add_strut_xf(p_skirt, p_top, rad * 0.86, cap_mat or MATERIALS["brass"], sides=14)
        # Pointer line on top of rotary knob
        add_box_xf(kx - 0.004, p_top[1] - 0.022, p_top[2] - 0.002, kx + 0.004, p_top[1] + 0.002, p_top[2] + 0.008, MATERIALS["paper_edge"])

    def add_fader_bank(fx_center, num_faders=4):
        bank_w = num_faders * 0.044 + 0.03
        add_box_xf(fx_center - bank_w * 0.5, ya0 + 0.02, za0 + 0.005, fx_center + bank_w * 0.5, ya1 - 0.02, za1 - 0.002, MATERIALS["bezel_dark"])
        for fi in range(num_faders):
            fx = fx_center - (num_faders - 1) * 0.022 + fi * 0.044
            # Recessed slot
            add_quad_xf((fx - 0.004, ya0 + 0.035, za0 + 0.015), (fx + 0.004, ya0 + 0.035, za0 + 0.015), (fx + 0.004, ya1 - 0.035, za1 - 0.005), (fx - 0.004, ya1 - 0.035, za1 - 0.005), MATERIALS["desk_leather"])
            # Fader position along track
            u_f = 0.32 + ((fi * 37 + int(abs(fx_center * 10))) % 5) * 0.11
            fy = ya0 + u_f * (ya1 - ya0)
            fz = za0 + u_f * (za1 - za0)
            f_mat = MATERIALS["crimson_glow"] if fi == num_faders - 1 else (MATERIALS["brass"] if fi == 0 else MATERIALS["steel_light"])
            add_box_xf(fx - 0.014, fy - 0.016, fz + 0.004, fx + 0.014, fy + 0.016, fz + 0.026, f_mat)

    # Populate the sloped control apron with fluted rotary knobs, fader banks, and bezel pushbuttons
    for side_sign in (-1.0, 1.0):
        # Outer & inner VFO / IF gain rotary encoders
        add_rotary_encoder(side_sign * (hw - 0.24), 0.52, rad=0.042, h_knob=0.038, cap_mat=MATERIALS["brass"], ring_mat=MATERIALS["cyan_glow"])
        add_rotary_encoder(side_sign * (hw - 0.42), 0.52, rad=0.032, h_knob=0.030, cap_mat=MATERIALS["steel_light"], ring_mat=MATERIALS["amber_glow"])
        add_rotary_encoder(side_sign * (hw - 0.56), 0.62, rad=0.026, h_knob=0.026, cap_mat=MATERIALS["brass"], ring_mat=None)
        # 4-channel audio/telemetry fader bank on each wing
        add_fader_bank(side_sign * (hw - 0.82), num_faders=4)
        # Matrix of illuminated broadcast selector buttons in dark bezels
        for b_row, u_b in enumerate((0.28, 0.72)):
            by = ya0 + u_b * (ya1 - ya0)
            bz = za0 + u_b * (za1 - za0)
            for b_col in range(5):
                bx = side_sign * (0.20 + b_col * 0.095)
                b_glow = (
                    MATERIALS["crimson_glow"]
                    if (b_row == 1 and b_col == 0)
                    else (MATERIALS["cyan_glow"] if (b_col + b_row) % 2 == 0 else MATERIALS["amber_glow"])
                )
                add_box_xf(bx - 0.028, by - 0.020, bz - 0.002, bx + 0.028, by + 0.020, bz + 0.012, MATERIALS["bezel_dark"])
                add_box_xf(bx - 0.021, by - 0.014, bz + 0.006, bx + 0.021, by + 0.014, bz + 0.020, b_glow)

    # On non-mic bays, add a recessed mechanical telemetry keyboard & trackball turret on the flat desk surface
    if not is_master_mic_bay:
        add_box_xf(-0.34, -0.88, z_desk_top, 0.14, -0.68, z_desk_top + 0.022, MATERIALS["bezel_dark"])
        add_box_xf(-0.31, -0.85, z_desk_top + 0.016, 0.02, -0.71, z_desk_top + 0.030, MATERIALS["rack_panel"])
        add_box_xf(0.04, -0.85, z_desk_top + 0.016, 0.11, -0.71, z_desk_top + 0.030, MATERIALS["desk_trim"])
        # Trackball / rotary shuttle module to the right of the keyboard
        add_box_xf(0.18, -0.86, z_desk_top, 0.36, -0.70, z_desk_top + 0.024, MATERIALS["bezel_dark"])
        add_strut_xf((0.27, -0.78, z_desk_top + 0.018), (0.27, -0.78, z_desk_top + 0.052), 0.048, MATERIALS["brass"], sides=14)
        add_strut_xf((0.27, -0.78, z_desk_top + 0.048), (0.27, -0.78, z_desk_top + 0.056), 0.038, MATERIALS["cyan_glow"], sides=14)

    # ── 4. SLOPED DUAL-MONITOR WEDGE, EXTRUDED BEZELS, SUNHOOD & CENTRAL INSTRUMENT BRIDGE ──
    yb, zb = -0.44, 1.13
    yt, zt = 0.12, 1.555
    yr = 0.16
    # Wedge cabinet sides, face, top & back
    add_quad_xf((-hw, yb, zb), (-hw, yt, zt), (-hw, yr, zt), (-hw, yr, 1.05), MATERIALS["desk_hull"])
    add_quad_xf((hw, yb, zb), (hw, yr, 1.05), (hw, yr, zt), (hw, yt, zt), MATERIALS["desk_hull"])
    add_quad_xf((-hw, yb, zb), (hw, yb, zb), (hw, yt, zt), (-hw, yt, zt), MATERIALS["desk_trim"])
    add_quad_xf((-hw, yt, zt), (hw, yt, zt), (hw, yr, zt), (-hw, yr, zt), MATERIALS["bezel_dark"])
    add_quad_xf((hw, yr, 1.05), (-hw, yr, 1.05), (-hw, yr, zt), (hw, yr, zt), MATERIALS["desk_hull"])

    # Outward normal of the sloped monitor face: dy = yt - yb = 0.56, dz = zt - zb = 0.425
    slope_len = math.hypot(yt - yb, zt - zb)
    s_ny = -(zt - zb) / slope_len
    s_nz = (yt - yb) / slope_len

    def screen_pt(x_val, u_slope, normal_off=0.0):
        sy = yb + u_slope * (yt - yb) + normal_off * s_ny
        sz = zb + u_slope * (zt - zb) + normal_off * s_nz
        return (x_val, sy, sz)

    def add_framed_monitor(x0, x1, u0, u1, tex_path):
        # Screen quad slightly proud of wedge face
        p00 = screen_pt(x0, u0, 0.012)
        p10 = screen_pt(x1, u0, 0.012)
        p11 = screen_pt(x1, u1, 0.012)
        p01 = screen_pt(x0, u1, 0.012)
        add_tex_xf(p00, p10, p11, p01, tex_path)

        # Extruded 4-sided cast-aluminum monitor bezel around the screen
        bw_m = 0.032
        bh_u = 0.048
        # Bottom, Top, Left, Right bezel bars standing +0.028m proud of wedge face
        for bx0, bx1, bu0, bu1 in [
            (x0 - bw_m, x1 + bw_m, u0 - bh_u, u0),
            (x0 - bw_m, x1 + bw_m, u1, u1 + bh_u),
            (x0 - bw_m, x0, u0, u1),
            (x1, x1 + bw_m, u0, u1),
        ]:
            b_f00 = screen_pt(bx0, bu0, 0.028)
            b_f10 = screen_pt(bx1, bu0, 0.028)
            b_f11 = screen_pt(bx1, bu1, 0.028)
            b_f01 = screen_pt(bx0, bu1, 0.028)
            b_b00 = screen_pt(bx0, bu0, 0.002)
            b_b10 = screen_pt(bx1, bu0, 0.002)
            b_b11 = screen_pt(bx1, bu1, 0.002)
            b_b01 = screen_pt(bx0, bu1, 0.002)
            add_quad_xf(b_f00, b_f10, b_f11, b_f01, MATERIALS["bezel_dark"])
            add_quad_xf(b_b00, b_b10, b_f10, b_f00, MATERIALS["steel_dark"])
            add_quad_xf(b_f01, b_f11, b_b11, b_b01, MATERIALS["steel_dark"])
            add_quad_xf(b_b00, b_f00, b_f01, b_b01, MATERIALS["steel_dark"])
            add_quad_xf(b_f10, b_b10, b_b11, b_f11, MATERIALS["steel_dark"])

    u0, u1 = 0.08, 0.91
    scr_gap = 0.14
    scr_w = (width - 0.28 - scr_gap) * 0.5
    lx0, lx1 = -scr_gap * 0.5 - scr_w, -scr_gap * 0.5
    rx0, rx1 = scr_gap * 0.5, scr_gap * 0.5 + scr_w
    add_framed_monitor(lx0, lx1, u0, u1, tex_left)
    add_framed_monitor(rx0, rx1, u0, u1, tex_right)

    # 3-Sided Anti-Glare ATC Sunhood Visor projecting +0.095m outward along top and sides of monitor wedge
    hood_d = 0.095
    ht_l_in = screen_pt(-hw + 0.02, 0.97, 0.005)
    ht_r_in = screen_pt(hw - 0.02, 0.97, 0.005)
    ht_l_out = screen_pt(-hw + 0.02, 0.95, hood_d)
    ht_r_out = screen_pt(hw - 0.02, 0.95, hood_d)
    hb_l_in = screen_pt(-hw + 0.02, 0.04, 0.005)
    hb_r_in = screen_pt(hw - 0.02, 0.04, 0.005)
    hb_l_out = screen_pt(-hw + 0.02, 0.06, hood_d * 0.45)
    hb_r_out = screen_pt(hw - 0.02, 0.06, hood_d * 0.45)
    # Top visor brow (double-sided)
    add_quad_xf(ht_l_in, ht_r_in, ht_r_out, ht_l_out, MATERIALS["bezel_dark"])
    add_quad_xf(ht_l_out, ht_r_out, ht_r_in, ht_l_in, MATERIALS["desk_leather"])
    # Left & Right side glare shields
    add_quad_xf(hb_l_in, ht_l_in, ht_l_out, hb_l_out, MATERIALS["bezel_dark"])
    add_quad_xf(hb_l_out, ht_l_out, ht_l_in, hb_l_in, MATERIALS["bezel_dark"])
    add_quad_xf(ht_r_in, hb_r_in, hb_r_out, ht_r_out, MATERIALS["bezel_dark"])
    add_quad_xf(ht_r_out, hb_r_out, hb_r_in, ht_r_in, MATERIALS["bezel_dark"])

    # Central Vertical Instrument Bridge between Left & Right monitors (VU/PPM bargraphs + Gooseneck Task Lamp)
    br_b0 = screen_pt(-0.042, 0.06, 0.022)
    br_b1 = screen_pt(0.042, 0.06, 0.022)
    br_t1 = screen_pt(0.042, 0.93, 0.022)
    br_t0 = screen_pt(-0.042, 0.93, 0.022)
    add_quad_xf(br_b0, br_b1, br_t1, br_t0, MATERIALS["bezel_dark"])
    # 7-segment dual vertical LED Peak-Program Meters
    for seg_i in range(7):
        u_seg0 = 0.14 + seg_i * 0.095
        u_seg1 = u_seg0 + 0.065
        seg_mat = (
            MATERIALS["crimson_glow"]
            if seg_i >= 5
            else (MATERIALS["amber_glow"] if seg_i >= 3 else MATERIALS["cyan_glow"])
        )
        for ch_x in (-0.018, 0.018):
            s00 = screen_pt(ch_x - 0.009, u_seg0, 0.028)
            s10 = screen_pt(ch_x + 0.009, u_seg0, 0.028)
            s11 = screen_pt(ch_x + 0.009, u_seg1, 0.028)
            s01 = screen_pt(ch_x - 0.009, u_seg1, 0.028)
            add_quad_xf(s00, s10, s11, s01, seg_mat)

    # Articulated Gooseneck Console Task Lamp arching from the top of the center bridge
    gn_base = screen_pt(0.0, 0.90, 0.025)
    gn_mid = (0.0, gn_base[1] - 0.12, gn_base[2] + 0.11)
    gn_tip = (0.0, gn_base[1] - 0.24, gn_base[2] + 0.06)
    add_strut_xf(gn_base, gn_mid, 0.009, MATERIALS["brass"], sides=6)
    add_strut_xf(gn_mid, gn_tip, 0.008, MATERIALS["brass"], sides=6)
    add_strut_xf((gn_tip[0] - 0.035, gn_tip[1], gn_tip[2]), (gn_tip[0] + 0.035, gn_tip[1], gn_tip[2]), 0.018, MATERIALS["bezel_dark"], sides=8)
    add_strut_xf((gn_tip[0] - 0.028, gn_tip[1], gn_tip[2] - 0.008), (gn_tip[0] + 0.028, gn_tip[1], gn_tip[2] - 0.008), 0.011, MATERIALS["amber_glow"], sides=6)


def build_corner_wedge_module(mesh, az_a_deg: float, w_a: float, az_b_deg: float, w_b: float, r_wall: float = 5.15):
    """
    Build a mitered 45° Octagonal Corner Wedge Filler Module bridging the gap between
    adjacent console bays (az_a_deg and az_b_deg), housing an angled Studio Monitor
    Loudspeaker grille and coaxial patchbay.
    """
    def bay_pt(az_deg, lx, ly, lz):
        yaw = math.radians(az_deg - 90.0)
        c, s = math.cos(yaw), math.sin(yaw)
        cx = r_wall * math.cos(math.radians(az_deg))
        cy = r_wall * math.sin(math.radians(az_deg))
        return (cx + lx * c - ly * s, cy + lx * s + ly * c, BOOTH_Z + lz)

    hw_a = w_a * 0.5
    hw_b = w_b * 0.5
    yf_a = -1.18 if abs(az_a_deg - 90.0) < 1.0 else -0.96
    yf_b = -1.18 if abs(az_b_deg - 90.0) < 1.0 else -0.96

    # Bay A right edge (+hw_a) meets Bay B left edge (-hw_b) when going clockwise (decreasing azimuth)
    # 1. Countertop miter triangle/quad & dark leather corner wrist bolster
    p_a_front_top = bay_pt(az_a_deg, hw_a, yf_a, 1.05)
    p_a_back_top = bay_pt(az_a_deg, hw_a, 0.14, 1.05)
    p_b_front_top = bay_pt(az_b_deg, -hw_b, yf_b, 1.05)
    p_b_back_top = bay_pt(az_b_deg, -hw_b, 0.14, 1.05)
    add_quad(mesh, p_a_front_top, p_b_front_top, p_b_back_top, p_a_back_top, MATERIALS["desk_trim"])

    p_a_front_bot = bay_pt(az_a_deg, hw_a, yf_a, 0.98)
    p_b_front_bot = bay_pt(az_b_deg, -hw_b, yf_b, 0.98)
    add_quad(mesh, p_a_front_bot, p_b_front_bot, p_b_front_top, p_a_front_top, MATERIALS["desk_leather"])

    # Brass miter strip & leather bolster bridge
    p_a_bol_0 = bay_pt(az_a_deg, hw_a, yf_a - 0.045, 1.062)
    p_a_bol_1 = bay_pt(az_a_deg, hw_a, yf_a + 0.038, 1.062)
    p_b_bol_0 = bay_pt(az_b_deg, -hw_b, yf_b - 0.045, 1.062)
    p_b_bol_1 = bay_pt(az_b_deg, -hw_b, yf_b + 0.038, 1.062)
    add_quad(mesh, p_a_bol_0, p_b_bol_0, p_b_bol_1, p_a_bol_1, MATERIALS["desk_leather"])

    # 2. Lower Corner Pedestal Skirt (z = 0.09 .. 0.98m)
    p_a_ped_b = bay_pt(az_a_deg, hw_a, -0.60, 0.09)
    p_b_ped_b = bay_pt(az_b_deg, -hw_b, -0.60, 0.09)
    p_a_ped_t = bay_pt(az_a_deg, hw_a, -0.60, 0.98)
    p_b_ped_t = bay_pt(az_b_deg, -hw_b, -0.60, 0.98)
    add_quad(mesh, p_a_ped_b, p_b_ped_b, p_b_ped_t, p_a_ped_t, MATERIALS["desk_hull"])

    # 3. Upper Corner Monitor Wedge Turret & Studio Loudspeaker Grille (z = 1.05 .. 1.555m)
    w_a_b = bay_pt(az_a_deg, hw_a, -0.44, 1.13)
    w_b_b = bay_pt(az_b_deg, -hw_b, -0.44, 1.13)
    w_a_t = bay_pt(az_a_deg, hw_a, 0.12, 1.555)
    w_b_t = bay_pt(az_b_deg, -hw_b, 0.12, 1.555)
    add_quad(mesh, w_a_b, w_b_b, w_b_t, w_a_t, MATERIALS["bezel_dark"])

    # Recessed acoustic speaker grille & status indicator on the corner wedge face
    mid_az = math.radians(0.5 * (az_a_deg + az_b_deg if abs(az_a_deg - az_b_deg) < 180 else az_a_deg + az_b_deg + 360))
    nx, ny = -math.cos(mid_az) * 0.015, -math.sin(mid_az) * 0.015
    spk_pts = [
        (
            0.78 * w_a_b[0] + 0.22 * w_b_t[0] + nx,
            0.78 * w_a_b[1] + 0.22 * w_b_t[1] + ny,
            BOOTH_Z + 1.19,
        ),
        (
            0.22 * w_a_t[0] + 0.78 * w_b_b[0] + nx,
            0.22 * w_a_t[1] + 0.78 * w_b_b[1] + ny,
            BOOTH_Z + 1.19,
        ),
        (
            0.22 * w_a_b[0] + 0.78 * w_b_t[0] + nx,
            0.22 * w_a_b[1] + 0.78 * w_b_t[1] + ny,
            BOOTH_Z + 1.48,
        ),
        (
            0.78 * w_a_t[0] + 0.22 * w_b_b[0] + nx,
            0.78 * w_a_t[1] + 0.22 * w_b_b[1] + ny,
            BOOTH_Z + 1.48,
        ),
    ]
    add_face(mesh, spk_pts, dict(MATERIALS["desk_leather"]))


def build_perimeter_consoles(scene, repo_root: Path):
    consoles_dir = repo_root / "docs" / "assets" / "consoles"
    branding_dir = repo_root / "docs" / "assets" / "branding"
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
            badge_tex=branding_dir / spec["badge"],
            is_master_mic_bay=spec["is_master_mic_bay"],
        )
        groups.append(grp)

    # Build the 6 Octagonal Corner Wedge Filler Modules uniting the 7 perimeter bays
    corner_grp = create_scene_group(scene, "05H_Console_Corner_Wedge_Modules")
    ordered_clockwise = [
        (225.0, 3.40),
        (180.0, 3.40),
        (135.0, 3.40),
        (90.0, 3.50),
        (45.0, 3.40),
        (0.0, 3.40),
        (315.0, 3.40),
    ]
    for idx in range(len(ordered_clockwise) - 1):
        az_a, w_a = ordered_clockwise[idx]
        az_b, w_b = ordered_clockwise[idx + 1]
        build_corner_wedge_module(corner_grp.mesh, az_a, w_a, az_b, w_b, r_wall=5.15)
    groups.append(corner_grp)

    return groups
