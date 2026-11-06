"""
Component & Design Study: GOR-9 Chamfered Stencil + Marzelvane Rings & Vertical Tower Sign
==========================================================================================
Implements the user-selected Bottom-Left Chamfered Octagonal Stencil typography
(`G O R  [Marzelvane Rings]  9`) with:
  1. `GLYPH_STROKES_STENCIL`: 45°-chamfered octagonal block letterforms (`G`, `O`,
     `R`, `9`) with true physical stencil-bridge breaks.
  2. `add_gor9_vertical_tower_sign_3d(...)`: Mounts the vertically stacked 3D
     channel-letter & neon sign (`G` / `O` / `R` / `[4 Concentric Marzelvane Rings]` / `9`)
     along the upper tower lattice spine (`Z = +33.5m .. +62.5m`), facing both out
     over the sheer 52m basalt cliff (`Az = -28°` ESE) and toward the opposite
     upland Base Compound (`Az = +152°` WNW).
  3. `generate_design_study_sheets(...)`: Renders two high-resolution (`2560x1600`)
     design study boards:
       - `gor9_logo_design_study.png`: 6 variations (`V1`–`V6`) experimenting with
         the **Marzelvane Rings** in the separator position (where the blue dot was
         in the Bottom-Left stencil lockup).
       - `gor9_logo_brand_applications.png`: Vertical Tower Stack variations (`T1`–`T4`)
         and unified station touchpoints (Vertical Tower Beacon, Heavy Industrial
         Hull Stencil, Boom-Mic Cube & ON-AIR Plaque, Console Telemetry Bug).
"""

from __future__ import annotations

import math
from pathlib import Path

from .primitives import (
    MATERIALS,
    add_quad,
    add_strut,
)


# ── Chamfered Octagonal Stencil Glyph Strokes (True Stencil Bridge Breaks) ──
# Normalized glyph coordinates: u in [0.0, 1.0] (left->right), v in [0.0, 1.0] (bottom->top).
# Each glyph is split at u ≈ 0.50 on top/bottom horizontal bars to form authentic
# heavy-industrial stencil bridges matching the Bottom-Left design.
GLYPH_STROKES_STENCIL = {
    "G": [
        # Left half: top-left bar, left vertical spine, bottom-left bar
        [
            (0.43, 0.94),
            (0.24, 0.94),
            (0.08, 0.76),
            (0.08, 0.24),
            (0.24, 0.06),
            (0.43, 0.06),
        ],
        # Top-right cap & upper-right chamfer
        [
            (0.57, 0.94),
            (0.76, 0.94),
            (0.92, 0.76),
        ],
        # Lower-right hook & inward horizontal spur
        [
            (0.57, 0.06),
            (0.78, 0.06),
            (0.92, 0.24),
            (0.92, 0.50),
            (0.54, 0.50),
        ],
    ],
    "O": [
        # Left half of chamfered octagon
        [
            (0.43, 0.94),
            (0.24, 0.94),
            (0.08, 0.76),
            (0.08, 0.24),
            (0.24, 0.06),
            (0.43, 0.06),
        ],
        # Right half of chamfered octagon
        [
            (0.57, 0.94),
            (0.76, 0.94),
            (0.92, 0.76),
            (0.92, 0.24),
            (0.76, 0.06),
            (0.57, 0.06),
        ],
    ],
    "R": [
        # Left vertical spine + top-left bar
        [
            (0.10, 0.04),
            (0.10, 0.94),
            (0.43, 0.94),
        ],
        # Right half of upper P-loop
        [
            (0.57, 0.94),
            (0.74, 0.94),
            (0.90, 0.78),
            (0.90, 0.62),
            (0.74, 0.50),
            (0.57, 0.50),
        ],
        # Mid-left crossbar segment
        [
            (0.10, 0.50),
            (0.43, 0.50),
        ],
        # Diagonal kick leg
        [
            (0.56, 0.48),
            (0.92, 0.04),
        ],
    ],
    "9": [
        # Upper-left bowl half
        [
            (0.43, 0.94),
            (0.24, 0.94),
            (0.08, 0.78),
            (0.08, 0.64),
            (0.24, 0.50),
            (0.43, 0.50),
        ],
        # Right spine + upper-right & lower-right chamfers
        [
            (0.57, 0.94),
            (0.76, 0.94),
            (0.90, 0.78),
            (0.90, 0.24),
            (0.74, 0.06),
            (0.57, 0.06),
        ],
        # Mid-right bar link
        [
            (0.57, 0.50),
            (0.88, 0.50),
        ],
        # Lower-left base tail
        [
            (0.43, 0.06),
            (0.18, 0.06),
        ],
    ],
}


def _add_3d_ribbon_stroke(
    mesh,
    pts_2d: list[tuple[float, float]],
    origin_xyz: tuple[float, float, float],
    right_vec: tuple[float, float, float],
    up_vec: tuple[float, float, float],
    fwd_vec: tuple[float, float, float],
    half_w: float,
    depth: float,
    mat_front: dict,
    mat_housing: dict,
    mat_neon_core: dict,
):
    """
    Extrude a 2D polyline `pts_2d` (in meters relative to `origin_xyz`) into a
    3D architectural channel-letter bar with:
      - A dark steel 3D backing channel (`depth` thick)
      - A wide glowing front face (`half_w` half-width)
      - A raised central neon-tube filament (`mat_neon_core`) on the front face
        so the letterform stays razor-sharp even at high bloom/emission.
    """
    ox, oy, oz = origin_xyz
    rx, ry, rz = right_vec
    ux, uy, uz = up_vec
    fx, fy, fz = fwd_vec

    def to_world(u_m: float, v_m: float, z_off: float) -> tuple[float, float, float]:
        return (
            ox + u_m * rx + v_m * ux + z_off * fx,
            oy + u_m * ry + v_m * uy + z_off * fy,
            oz + u_m * rz + v_m * uz + z_off * fz,
        )

    for i in range(len(pts_2d) - 1):
        u0, v0 = pts_2d[i]
        u1, v1 = pts_2d[i + 1]
        du, dv = u1 - u0, v1 - v0
        seg_len = math.hypot(du, dv)
        if seg_len < 1e-4:
            continue
        tu, tv = du / seg_len, dv / seg_len
        nu, nv = -tv, tu

        # Extend internal miter joins slightly, keep stencil break ends crisp
        ext0 = half_w * 0.42 if i > 0 else half_w * 0.12
        ext1 = half_w * 0.42 if i < len(pts_2d) - 2 else half_w * 0.12
        su0, sv0 = u0 - tu * ext0, v0 - tv * ext0
        su1, sv1 = u1 + tu * ext1, v1 + tv * ext1

        c0 = (su0 - nu * half_w, sv0 - nv * half_w)
        c1 = (su1 - nu * half_w, sv1 - nv * half_w)
        c2 = (su1 + nu * half_w, sv1 + nv * half_w)
        c3 = (su0 + nu * half_w, sv0 + nv * half_w)

        zf = depth * 0.5
        zb = -depth * 0.5
        f0, f1, f2, f3 = [to_world(u, v, zf) for (u, v) in (c0, c1, c2, c3)]
        b0, b1, b2, b3 = [to_world(u, v, zb) for (u, v) in (c0, c1, c2, c3)]

        add_quad(mesh, f0, f1, f2, f3, mat_front)
        add_quad(mesh, b3, b2, b1, b0, mat_housing)
        add_quad(mesh, b0, b1, f1, f0, mat_housing)
        add_quad(mesh, b1, b2, f2, f1, mat_housing)
        add_quad(mesh, b2, b3, f3, f2, mat_housing)
        add_quad(mesh, b3, b0, f0, f3, mat_housing)

        p_tube0 = to_world(u0, v0, zf + half_w * 0.30)
        p_tube1 = to_world(u1, v1, zf + half_w * 0.30)
        add_strut(mesh, p_tube0, p_tube1, half_w * 0.36, mat_neon_core, sides=6)


def _add_3d_marzelvane_ring_emblem(
    mesh,
    center_xyz: tuple[float, float, float],
    right_vec: tuple[float, float, float],
    up_vec: tuple[float, float, float],
    fwd_vec: tuple[float, float, float],
    outer_radius: float,
    depth: float,
    mat_cyan_ring: dict,
    mat_cyan_core: dict,
    mat_amber_face: dict,
    mat_amber_core: dict,
    mat_housing: dict,
):
    """
    Build the 3D Marzelvane Rings emblem in the separator slot between `GOR` and `9`:
      - 4 concentric glowing cyan Cherenkov rings (matching the 4 Marzelvane emitter
        ring proportions: r_frac = 0.34, 0.55, 0.77, 1.00) with dark-steel channel backing
      - 4 cardinal waveguide spoke ticks (0°, 90°, 180°, 270°)
      - Central phase-splitter cyan/white core beacon
      - Left & right flanking amber stencil bracket bars (`═ ◎ ═`).
    """
    cx, cy, cz = center_xyz
    rx, ry, rz = right_vec
    ux, uy, uz = up_vec
    fx, fy, fz = fwd_vec

    # Dark-steel octagonal backing bezel behind the Marzelvane rings so the 4 concentric
    # cyan rings have high-contrast dark separation and don't bleed through from the opposite sign
    bezel_pts = []
    bezel_r = outer_radius * 1.10
    for k in range(16):
        ba = 2.0 * math.pi * k / 16.0
        bu = bezel_r * math.cos(ba)
        bv = bezel_r * math.sin(ba)
        bezel_pts.append(
            (
                cx + bu * rx + bv * ux - (depth * 0.15) * fx,
                cy + bu * ry + bv * uy - (depth * 0.15) * fy,
                cz + bu * rz + bv * uz - (depth * 0.15) * fz,
            )
        )
    from .primitives import add_face

    add_face(mesh, bezel_pts, dict(mat_housing))
    add_face(mesh, list(reversed(bezel_pts)), dict(mat_housing))

    # 4 Concentric Marzelvane Rings in the vertical plane of the sign (V4 Spoke Reticle)
    ring_fracs = (0.28, 0.52, 0.76, 1.00)
    for r_idx, r_frac in enumerate(ring_fracs):
        rad = outer_radius * r_frac
        segs = 20 if r_idx < 2 else 28
        tube_r = outer_radius * (0.055 if r_idx == 3 else 0.042)
        mat_r = mat_cyan_core if r_idx == 0 else mat_cyan_ring
        ring_pts = []
        for s in range(segs + 1):
            a = 2.0 * math.pi * s / segs
            u = rad * math.cos(a)
            v = rad * math.sin(a)
            ring_pts.append(
                (
                    cx + u * rx + v * ux + (depth * 0.45) * fx,
                    cy + u * ry + v * uy + (depth * 0.45) * fy,
                    cz + u * rz + v * uz + (depth * 0.45) * fz,
                )
            )
        for s in range(segs):
            add_strut(mesh, ring_pts[s], ring_pts[s + 1], tube_r, mat_r, sides=6)

    # 4 Cardinal radial waveguide spokes (0°, 90°, 180°, 270°)
    for ang_deg in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang_deg)
        r0 = outer_radius * 0.20
        r1 = outer_radius * 1.08
        p0 = (
            cx + (r0 * math.cos(a)) * rx + (r0 * math.sin(a)) * ux + (depth * 0.38) * fx,
            cy + (r0 * math.cos(a)) * ry + (r0 * math.sin(a)) * uy + (depth * 0.38) * fy,
            cz + (r0 * math.cos(a)) * rz + (r0 * math.sin(a)) * uz + (depth * 0.38) * fz,
        )
        p1 = (
            cx + (r1 * math.cos(a)) * rx + (r1 * math.sin(a)) * ux + (depth * 0.38) * fx,
            cy + (r1 * math.cos(a)) * ry + (r1 * math.sin(a)) * uy + (depth * 0.38) * fy,
            cz + (r1 * math.cos(a)) * rz + (r1 * math.sin(a)) * uz + (depth * 0.38) * fz,
        )
        add_strut(mesh, p0, p1, outer_radius * 0.028, mat_cyan_ring, sides=6)

    # 8 Perimeter ceramic standoff nodes around the outer ring (matching V4!)
    for node_deg in range(0, 360, 45):
        na = math.radians(node_deg)
        nu = outer_radius * math.cos(na)
        nv = outer_radius * math.sin(na)
        np0 = (
            cx + nu * rx + nv * ux + (depth * 0.35) * fx,
            cy + nu * ry + nv * uy + (depth * 0.35) * fy,
            cz + nu * rz + nv * uz + (depth * 0.35) * fz,
        )
        np1 = (
            cx + nu * rx + nv * ux + (depth * 0.62) * fx,
            cy + nu * ry + nv * uy + (depth * 0.62) * fy,
            cz + nu * rz + nv * uz + (depth * 0.62) * fz,
        )
        add_strut(mesh, np0, np1, outer_radius * 0.055, mat_cyan_core, sides=6)

    # Central glowing red-orange phase-splitter hub dot (matching V4!)
    p_core0 = (cx, cy, cz)
    p_core1 = (cx + depth * 0.65 * fx, cy + depth * 0.65 * fy, cz + depth * 0.65 * fz)
    add_strut(mesh, p_core0, p_core1, outer_radius * 0.13, mat_amber_core, sides=8)

    # Flanking intense red-orange stencil side-tabs (`- [Marzelvane Rings] -`)
    for side in (-1.0, 1.0):
        u_in = side * outer_radius * 1.16
        u_out = side * outer_radius * 1.48
        _add_3d_ribbon_stroke(
            mesh=mesh,
            pts_2d=[(u_in, 0.0), (u_out, 0.0)],
            origin_xyz=center_xyz,
            right_vec=right_vec,
            up_vec=up_vec,
            fwd_vec=fwd_vec,
            half_w=outer_radius * 0.13,
            depth=depth,
            mat_front=mat_amber_face,
            mat_housing=mat_housing,
            mat_neon_core=mat_amber_core,
        )


def add_gor9_vertical_tower_sign_3d(
    mesh,
    azimuth_deg: float,
    r_mount_bot: float = 2.74,
    r_mount_top: float = 2.40,
    z_bot: float = 37.8,
    z_top: float = 53.4,
    char_width: float = 1.95,
):
    """
    Build a vertically stacked 3D open-truss tower sign along the lower portion
    of the upper steel lattice tower (`Z = +31.8m .. +47.4m`, sitting immediately
    above the Octagonal Broadcast Booth roof and leaving ~25m of open lattice
    below the Z = +72.0m Marzelvane Emitter Rings so it never visually competes
    with the crown even from steep low-angle chasm views):
      Top to Bottom Stack:
        1. `G`  (Chamfered Octagonal Stencil)
        2. `O`  (Chamfered Octagonal Stencil)
        3. `R`  (Chamfered Octagonal Stencil)
        4. `[MARZELVANE RINGS V4]`  (4 Concentric Cyan Rings + 4 Spokes + 8 Nodes + Red Core)
        5. `9`  (Chamfered Octagonal Stencil)
    Mounted on an open vertical structural steel ladder-truss cantilevered outside
    the square tower lattice envelope along `azimuth_deg` (Sign #1 at `-28°` ESE
    facing the sheer 52m basalt cliff; Sign #2 at `+152°` WNW on the opposite side).
    """
    ang = math.radians(azimuth_deg)
    fx, fy, fz = math.cos(ang), math.sin(ang), 0.0
    # Viewer's left-to-right reading axis when looking at the sign from outside
    rx, ry, rz = -fy, fx, 0.0
    ux, uy, uz = 0.0, 0.0, 1.0

    mat_housing = MATERIALS["steel_dark"]
    mat_truss = MATERIALS["steel"]
    # Deep crimson-red broadcast neon channel face & core (pure linear R with minimal G/B)
    mat_face = {
        "color": (1.00, 0.002, 0.001),
        "emissive": True,
        "light_channel": "sign_glow",
    }
    mat_tube = {
        "color": (1.00, 0.005, 0.001),
        "emissive": True,
        "light_channel": "sign_core_glow",
    }
    mat_cyan_ring = {
        "color": (0.02, 0.72, 1.00),
        "emissive": True,
        "light_channel": "sign_cyan_glow",
    }
    mat_cyan_core = {
        "color": (0.35, 0.92, 1.00),
        "emissive": True,
        "light_channel": "sign_cyan_core",
    }

    total_h = z_top - z_bot

    def r_at_z(z_val: float) -> float:
        t = max(0.0, min(1.0, (z_val - z_bot) / max(1e-4, total_h)))
        return r_mount_bot * (1.0 - t) + r_mount_top * t

    # 1. Open Vertical Structural Steel Ladder-Truss Frame Cantilevered Outside the Tower Lattice
    half_truss_w = char_width * 0.56
    frame_back_off = -0.14
    for side in (-1.0, 1.0):
        u_rail = side * half_truss_w
        r0 = r_at_z(z_bot) + frame_back_off
        r1 = r_at_z(z_top) + frame_back_off
        p_bot = (r0 * fx + u_rail * rx, r0 * fy + u_rail * ry, z_bot - 0.25)
        p_top = (r1 * fx + u_rail * rx, r1 * fy + u_rail * ry, z_top + 0.25)
        add_strut(mesh, p_bot, p_top, 0.048, mat_truss, sides=6)

        # Deep red vertical neon border bar framing the left & right edges
        p_nbot = ((r0 + 0.10) * fx + (u_rail * 1.04) * rx, (r0 + 0.10) * fy + (u_rail * 1.04) * ry, z_bot - 0.12)
        p_ntop = ((r1 + 0.10) * fx + (u_rail * 1.04) * rx, (r1 + 0.10) * fy + (u_rail * 1.04) * ry, z_top + 0.12)
        add_strut(mesh, p_nbot, p_ntop, 0.022, mat_face, sides=6)

    # Horizontal truss rungs & cantilevered standoff brackets tying back into the tower lattice
    n_rungs = 8
    for k in range(n_rungs):
        zk = z_bot + (k / (n_rungs - 1)) * total_h
        rk = r_at_z(zk) + frame_back_off
        p_left = (rk * fx - half_truss_w * rx, rk * fy - half_truss_w * ry, zk)
        p_right = (rk * fx + half_truss_w * rx, rk * fy + half_truss_w * ry, zk)
        add_strut(mesh, p_left, p_right, 0.034, mat_truss, sides=6)
        if k % 2 == 0:
            for side in (-1.0, 1.0):
                p_out = (rk * fx + side * half_truss_w * rx, rk * fy + side * half_truss_w * ry, zk)
                p_in = ((rk - 1.05) * fx + side * (half_truss_w * 0.68) * rx, (rk - 1.05) * fy + side * (half_truss_w * 0.68) * ry, zk)
                add_strut(mesh, p_out, p_in, 0.036, mat_housing, sides=6)

    # 2. Vertically Stacked 3D Chamfered Octagonal Stencil Letters + V4 Marzelvane Spoke Reticle:
    #    Positioned lower (`Z = 31.8m .. 47.4m`) and compact (`1.95m x 2.42m`)
    char_h = 2.42
    stroke_half_w = 0.155
    channel_depth = 0.20

    vertical_slots = [
        ("G", z_bot + total_h * 0.89),
        ("O", z_bot + total_h * 0.675),
        ("R", z_bot + total_h * 0.46),
        ("MARZEL", z_bot + total_h * 0.265),
        ("9", z_bot + total_h * 0.08),
    ]

    for token, z_center in vertical_slots:
        r_here = r_at_z(z_center)
        if token == "MARZEL":
            center_xyz = (r_here * fx, r_here * fy, z_center)
            _add_3d_marzelvane_ring_emblem(
                mesh=mesh,
                center_xyz=center_xyz,
                right_vec=(rx, ry, rz),
                up_vec=(ux, uy, uz),
                fwd_vec=(fx, fy, fz),
                outer_radius=char_width * 0.34,
                depth=channel_depth,
                mat_cyan_ring=mat_cyan_ring,
                mat_cyan_core=mat_cyan_core,
                mat_amber_face=mat_face,
                mat_amber_core=mat_tube,
                mat_housing=mat_housing,
            )
            continue

        z0_glyph = z_center - char_h * 0.5
        u_left = -char_width * 0.5
        glyph_origin = (
            r_here * fx + u_left * rx,
            r_here * fy + u_left * ry,
            z0_glyph,
        )
        strokes = GLYPH_STROKES_STENCIL.get(token, [])
        for stroke in strokes:
            pts_m = [(u * char_width, v * char_h) for (u, v) in stroke]
            _add_3d_ribbon_stroke(
                mesh=mesh,
                pts_2d=pts_m,
                origin_xyz=glyph_origin,
                right_vec=(rx, ry, rz),
                up_vec=(ux, uy, uz),
                fwd_vec=(fx, fy, fz),
                half_w=stroke_half_w,
                depth=channel_depth,
                mat_front=mat_face,
                mat_housing=mat_housing,
                mat_neon_core=mat_tube,
            )


# ── 2D Brand & Marzelvane Ring Separator Design Study Generator ──────────────

def _draw_stencil_gor_9_base(ax, slots, y0: float, h: float, lw: float = 13.5, plate_bg: str = "#1a222d"):
    """Draw the Chamfered Octagonal Stencil `G`, `O`, `R`, and `9` glyphs onto `ax`."""
    for ch, x0, w in slots:
        if ch not in GLYPH_STROKES_STENCIL:
            continue
        for stroke in GLYPH_STROKES_STENCIL[ch]:
            xs = [x0 + u * w for (u, _v) in stroke]
            ys = [y0 + v * h for (_u, v) in stroke]
            ax.plot(xs, ys, color="#ff6a00", lw=lw + 5.0, solid_capstyle="butt", solid_joinstyle="miter", alpha=0.22, zorder=3)
            ax.plot(xs, ys, color="#ffaa2b", lw=lw, solid_capstyle="butt", solid_joinstyle="miter", zorder=4)
            ax.plot(xs, ys, color="#ffe299", lw=1.8, solid_capstyle="butt", solid_joinstyle="miter", alpha=0.85, zorder=5)


def _draw_marzelvane_separator_2d(ax, cx: float, cy: float, radius: float, variant_id: str, zorder_base: int = 6):
    """
    Draw one of the 6 Marzelvane Ring separator variations (`V1`–`V6`) at `(cx, cy)`
    in the space between `GOR` and `9` (where the blue dot was in Bottom-Left).
    """
    import matplotlib.patches as mpatches

    # Flanking short amber stencil hyphen tabs on left & right of the Marzelvane rings
    for side in (-1.0, 1.0):
        x_in = cx + side * radius * 1.15
        x_out = cx + side * radius * 1.48
        ax.plot([x_in, x_out], [cy, cy], color="#ffaa2b", lw=7.5, solid_capstyle="butt", zorder=zorder_base)

    if variant_id == "V1":
        # V1: 4 Concentric Plan-View Marzelvane Rings (exact 7 : 11.5 : 16 : 21 proportions) + glowing core
        for r_frac, lw_r, col_r in (
            (1.00, 3.4, "#38eaff"),
            (0.76, 2.4, "#38eaff"),
            (0.55, 2.0, "#38eaff"),
            (0.33, 1.8, "#99f6ff"),
        ):
            c = mpatches.Circle((cx, cy), radius=radius * r_frac, fill=False, edgecolor=col_r, lw=lw_r, zorder=zorder_base + 1)
            ax.add_patch(c)
        ax.scatter([cx], [cy], s=65, color="#ffffff", edgecolors="#38eaff", linewidths=2.0, zorder=zorder_base + 3)

    elif variant_id == "V2":
        # V2: Tilted Perspective 4-Ring Elliptical Crown + Central Cherenkov Spire Needle
        ax.plot([cx, cx], [cy - radius * 1.10, cy + radius * 1.25], color="#ffaa2b", lw=3.0, zorder=zorder_base)
        ax.plot([cx - radius * 0.55, cx, cx + radius * 0.55], [cy - radius * 1.05, cy + radius * 0.45, cy - radius * 1.05], color="#7b93b0", lw=1.6, zorder=zorder_base)
        for r_frac, lw_r, col_r in (
            (1.05, 3.0, "#38eaff"),
            (0.78, 2.2, "#38eaff"),
            (0.54, 1.8, "#66f2ff"),
            (0.30, 1.5, "#ffffff"),
        ):
            ell = mpatches.Ellipse(
                (cx, cy + radius * 0.12),
                width=radius * 2.15 * r_frac,
                height=radius * 0.82 * r_frac,
                fill=False,
                edgecolor=col_r,
                lw=lw_r,
                zorder=zorder_base + 2,
            )
            ax.add_patch(ell)
        ax.scatter([cx], [cy + radius * 1.25], s=50, color="#99f8ff", edgecolors="#ffffff", zorder=zorder_base + 4)

    elif variant_id == "V3":
        # V3: Chamfered Octagonal Stencil-Matched Concentric Rings (with stencil break cuts!)
        for r_frac, lw_r, col_r in (
            (1.00, 3.6, "#38eaff"),
            (0.68, 2.6, "#38eaff"),
            (0.38, 2.0, "#99f6ff"),
        ):
            oct_r = mpatches.RegularPolygon(
                (cx, cy),
                numVertices=8,
                radius=radius * r_frac,
                orientation=math.pi / 8.0,
                fill=False,
                edgecolor=col_r,
                lw=lw_r,
                zorder=zorder_base + 1,
            )
            ax.add_patch(oct_r)
        # Vertical stencil break-cut through the octagonal rings matching G, O, R, 9
        ax.plot([cx, cx], [cy - radius * 1.12, cy + radius * 1.12], color="#1e252f", lw=4.2, zorder=zorder_base + 2)
        loz = mpatches.RegularPolygon((cx, cy), numVertices=8, radius=radius * 0.18, orientation=math.pi / 8.0, facecolor="#99f8ff", edgecolor="#ffffff", lw=1.2, zorder=zorder_base + 3)
        ax.add_patch(loz)

    elif variant_id == "V4":
        # V4: 4 Concentric Rings + 4 Cardinal Waveguide Spokes + 8 Diagonal Standoff Nodes
        for r_frac, lw_r, col_r in (
            (1.00, 3.2, "#38eaff"),
            (0.75, 2.2, "#38eaff"),
            (0.52, 1.8, "#38eaff"),
            (0.28, 1.6, "#ffffff"),
        ):
            c = mpatches.Circle((cx, cy), radius=radius * r_frac, fill=False, edgecolor=col_r, lw=lw_r, zorder=zorder_base + 1)
            ax.add_patch(c)
        for ang_deg in (0, 90, 180, 270):
            a = math.radians(ang_deg)
            ax.plot(
                [cx + radius * 0.22 * math.cos(a), cx + radius * 1.08 * math.cos(a)],
                [cy + radius * 0.22 * math.sin(a), cy + radius * 1.08 * math.sin(a)],
                color="#70f3ff",
                lw=2.0,
                zorder=zorder_base + 2,
            )
        node_xs = [cx + radius * math.cos(math.radians(a)) for a in range(0, 360, 45)]
        node_ys = [cy + radius * math.sin(math.radians(a)) for a in range(0, 360, 45)]
        ax.scatter(node_xs, node_ys, s=16, color="#ffffff", edgecolors="#38eaff", zorder=zorder_base + 3)
        ax.scatter([cx], [cy], s=55, color="#ffaa2b", edgecolors="#ffffff", linewidths=1.5, zorder=zorder_base + 4)

    elif variant_id == "V5":
        # V5: Side-Elevation Stacked Emitter Array (4 Horizontal Cherenkov Tiers + Vertical Waveguide)
        ax.plot([cx, cx], [cy - radius * 1.05, cy + radius * 1.15], color="#ffaa2b", lw=3.2, zorder=zorder_base + 1)
        tier_specs = [
            (-0.62, 0.58, 3.2, "#38eaff"),
            (-0.20, 0.86, 3.6, "#38eaff"),
            (0.22, 1.06, 4.2, "#66f2ff"),
            (0.64, 0.74, 3.2, "#99f8ff"),
        ]
        for y_off, w_frac, lw_t, col_t in tier_specs:
            ty = cy + y_off * radius
            hw = w_frac * radius
            ax.plot([cx - hw, cx + hw], [ty, ty], color=col_t, lw=lw_t, solid_capstyle="round", zorder=zorder_base + 2)
            ax.scatter([cx - hw, cx + hw], [ty, ty], s=18, color="#ffffff", zorder=zorder_base + 3)
        ax.scatter([cx], [cy + radius * 1.15], s=45, color="#ffffff", edgecolors="#38eaff", zorder=zorder_base + 4)

    elif variant_id == "V6":
        # V6: Heavy Twin-Torus Stencil Emblem (Ultra-Bold Dual Cyan Rings + Amber Core for Long-Range Legibility)
        outer_c = mpatches.Circle((cx, cy), radius=radius * 0.96, fill=False, edgecolor="#38eaff", lw=5.5, zorder=zorder_base + 1)
        inner_c = mpatches.Circle((cx, cy), radius=radius * 0.52, fill=False, edgecolor="#88f6ff", lw=3.8, zorder=zorder_base + 2)
        ax.add_patch(outer_c)
        ax.add_patch(inner_c)
        # 4 diagonal stencil bridge cuts across outer ring
        for ang_deg in (45, 135, 225, 315):
            a = math.radians(ang_deg)
            ax.plot(
                [cx + radius * 0.76 * math.cos(a), cx + radius * 1.12 * math.cos(a)],
                [cy + radius * 0.76 * math.sin(a), cy + radius * 1.12 * math.sin(a)],
                color="#1e252f",
                lw=3.8,
                zorder=zorder_base + 3,
            )
        core_hex = mpatches.RegularPolygon((cx, cy), numVertices=6, radius=radius * 0.22, orientation=0.0, facecolor="#ffaa2b", edgecolor="#ffffff", lw=1.4, zorder=zorder_base + 4)
        ax.add_patch(core_hex)


def generate_design_study_sheets(out_dir: Path) -> tuple[Path, Path]:
    """
    Generate two high-resolution (`2560x1600`) design study boards:
      1. `gor9_logo_design_study.png`: 6 variations (`V1`–`V6`) of the Bottom-Left
         Chamfered Octagonal Stencil (`G O R  [Marzelvane Rings]  9`) experimenting
         with Marzelvane Rings in the blue-dot separator position.
      2. `gor9_logo_brand_applications.png`: Vertical Stacked Tower Sign variations
         (`G / O / R / [Marzelvane] / 9`) and unified station applications.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)

    # ── BOARD 1: 6 Marzelvane Ring Separator Variations (Bottom-Left Stencil Base) ──
    fig = plt.figure(figsize=(25.6, 16.0), dpi=100, facecolor="#070a10")
    fig.suptitle(
        "G O R  ◎  9   •   MARZELVANE RING SEPARATOR STUDY  (CHAMFERED OCTAGONAL STENCIL)",
        color="#ffaa33",
        fontsize=20,
        fontweight="bold",
        fontfamily="monospace",
        y=0.965,
    )
    fig.text(
        0.5,
        0.935,
        "Based on Bottom-Left Industrial Stencil Lockup — Experimenting with 6 Marzelvane Ring Geometries in the Separator Slot Between 'GOR' and '9'",
        color="#8fa8c8",
        fontsize=12,
        fontfamily="monospace",
        ha="center",
    )

    variants = [
        (
            "V1",
            "V1  •  4-RING PLANAR CONCENTRIC ARRAY  (TOP-DOWN ORTHOGRAPHIC)",
            "Exact 4-ring Marzelvane radial proportions (7 : 11.5 : 16 : 21m) + white-cyan phase-splitter core.\nCleanest geometric bullseye between 'GOR' and '9'.",
        ),
        (
            "V2",
            "V2  •  TILTED PERSPECTIVE ELLIPTICAL CROWN + SPIRE",
            "Foreshortened 3D perspective of the 4 horizontal Cherenkov rings pierced by the vertical spire & stays.\nImmediately evokes the silhouette of the lighthouse crown.",
        ),
        (
            "V3",
            "V3  •  OCTAGONAL STENCIL-MATCHED RINGS  (WITH STENCIL BRIDGE CUT)",
            "Concentric 45°-chamfered octagonal cyan rings bisected by the same vertical stencil bridge as G, O, R, 9.\n100% unified typographic & spray-stencil geometry.",
        ),
        (
            "V4",
            "V4  •  WAVEGUIDE SPOKE RETICLE & CERAMIC STANDOFF NODES  [MOUNTED IN 3D]",
            "4 concentric cyan rings + 4 cardinal waveguide feed spokes + 8 perimeter ceramic insulator nodes.\nEngineered for the 3D vertical tower sign & close-up hardware plaques.",
        ),
        (
            "V5",
            "V5  •  SIDE-ELEVATION 4-TIER PHASED STACK",
            "Orthographic side profile of 4 horizontal glowing emitter bars stacked along the vertical copper spine.\nEchoes vintage radio resistor/capacitor schematic symbols.",
        ),
        (
            "V6",
            "V6  •  HEAVY TWIN-TORUS STENCIL EMBLEM  (HIGH-CONTRAST / SMALL SCALE)",
            "Ultra-bold dual concentric cyan rings with diagonal stencil bridges and a hexagonal amber dilithium core.\nReads effortlessly from 400m+ orbital range or on small crew patches.",
        ),
    ]

    for idx, (vid, title, desc) in enumerate(variants):
        row = idx // 2
        col = idx % 2
        ax = fig.add_axes([0.04 + col * 0.48, 0.62 - row * 0.285, 0.44, 0.235], facecolor="#0b1019")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#ff9e22" if vid in ("V1", "V4") else "#233246")
            spine.set_linewidth(2.2 if vid in ("V1", "V4") else 1.2)

        ax.set_xlim(0.0, 10.0)
        ax.set_ylim(0.0, 4.2)
        ax.set_aspect("equal")
        ax.axis("off")

        # Industrial dark-slate stencil plate (matching Bottom-Left Panel 3!)
        plate = mpatches.Rectangle((0.35, 0.65), 9.30, 2.85, facecolor="#1e252f", edgecolor="#56667a", lw=2.0, zorder=1)
        ax.add_patch(plate)
        # Hazard chevron strip along bottom of plate
        for hx in range(10):
            stripe = mpatches.Polygon(
                [
                    [0.35 + hx * 0.93, 0.65],
                    [0.81 + hx * 0.93, 0.65],
                    [1.02 + hx * 0.93, 0.98],
                    [0.56 + hx * 0.93, 0.98],
                ],
                closed=True,
                facecolor="#e68a1e" if hx % 2 == 0 else "#12161d",
                zorder=2,
            )
            ax.add_patch(stripe)

        # Draw Chamfered Octagonal Stencil G, O, R, and 9
        slots = [
            ("G", 1.15, 1.32),
            ("O", 2.75, 1.32),
            ("R", 4.35, 1.32),
            ("9", 7.55, 1.32),
        ]
        _draw_stencil_gor_9_base(ax, slots, y0=1.35, h=1.82, lw=12.5, plate_bg="#1e252f")

        # Draw the Marzelvane Ring Separator variation in the gap between R (ends at 5.67) and 9 (starts at 7.55) -> center = 6.61
        _draw_marzelvane_separator_2d(ax, cx=6.61, cy=2.26, radius=0.52, variant_id=vid, zorder_base=6)

        ax.text(
            0.35,
            3.72,
            title,
            color="#ffba49" if vid in ("V1", "V4") else "#38eaff",
            fontsize=12.2,
            fontweight="bold",
            fontfamily="monospace",
        )
        ax.text(
            0.35,
            0.08,
            desc,
            color="#9cb3ce",
            fontsize=9.3,
            fontfamily="monospace",
            va="bottom",
        )

    study_path = out_dir / "gor9_logo_design_study.png"
    fig.savefig(study_path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)

    # ── BOARD 2: Vertical Stacked Tower Sign & Unified Station Brand Sheet ──
    fig2 = plt.figure(figsize=(25.6, 16.0), dpi=100, facecolor="#070a10")
    fig2.suptitle(
        "G O R  ◎  9   •   VERTICAL TOWER SIGN STACK & UNIFIED BRAND SYSTEM",
        color="#ffaa33",
        fontsize=20,
        fontweight="bold",
        fontfamily="monospace",
        y=0.965,
    )
    fig2.text(
        0.5,
        0.935,
        "1) Vertically Stacked Tower Lattice Sign Variations (G / O / R / ◎ / 9)   2) Industrial Hull Stencil   3) Studio Mic Cube   4) Mission Patch & HUD",
        color="#8fa8c8",
        fontsize=12,
        fontfamily="monospace",
        ha="center",
    )

    # Panel 1 (Left Half, Full Height): 3 Vertical Stacked Tower Sign Variations Side-by-Side (`T1: V1 Planar`, `T2: V2 Elliptical`, `T3: V4 Spoke Reticle`)
    ax1 = fig2.add_axes([0.04, 0.06, 0.44, 0.84], facecolor="#090d15")
    for spine in ax1.spines.values():
        spine.set_visible(True)
        spine.set_color("#ff9e22")
        spine.set_linewidth(2.0)
    ax1.set_xlim(0.0, 10.0)
    ax1.set_ylim(0.0, 15.2)
    ax1.set_aspect("equal")
    ax1.axis("off")

    ax1.text(
        0.35,
        14.55,
        "1. VERTICALLY STACKED TOWER LATTICE SIGN  (UPPER SPINE +33.4m .. +63.4m)",
        color="#38eaff",
        fontsize=12.5,
        fontweight="bold",
        fontfamily="monospace",
    )
    ax1.text(
        0.35,
        14.08,
        "Mounted on Cliff-Facing Lattice (ESE -28°) & Opposite Upland Lattice (WNW +152°) • Replaces Booth Roof Sign",
        color="#ffba49",
        fontsize=9.8,
        fontfamily="monospace",
    )

    tower_cols = [
        (1.95, "T1 • PLANAR 4-RING", "V1"),
        (5.00, "T2 • TILTED CROWN", "V2"),
        (8.05, "T3 • SPOKE RETICLE [3D]", "V4"),
    ]
    for cx_col, col_label, m_var in tower_cols:
        # Draw tapered steel tower lattice behind the vertical sign stack
        ax1.plot([cx_col - 0.92, cx_col - 0.68], [1.4, 13.1], color="#324154", lw=3.0, zorder=1)
        ax1.plot([cx_col + 0.92, cx_col + 0.68], [1.4, 13.1], color="#324154", lw=3.0, zorder=1)
        # X-bracing bays
        z_bays = [1.4, 3.3, 5.2, 7.1, 9.0, 10.9, 12.8]
        for b_i in range(len(z_bays) - 1):
            zb0, zb1 = z_bays[b_i], z_bays[b_i + 1]
            w0 = 0.92 - 0.24 * ((zb0 - 1.4) / 11.7)
            w1 = 0.92 - 0.24 * ((zb1 - 1.4) / 11.7)
            ax1.plot([cx_col - w0, cx_col + w1], [zb0, zb1], color="#253242", lw=1.6, zorder=1)
            ax1.plot([cx_col + w0, cx_col - w1], [zb0, zb1], color="#253242", lw=1.6, zorder=1)
            ax1.plot([cx_col - w1, cx_col + w1], [zb1, zb1], color="#324154", lw=2.0, zorder=1)

        # Open vertical sign ladder-truss rails & warm amber side border tubes
        for s_side in (-1.0, 1.0):
            ax1.plot([cx_col + s_side * 0.86, cx_col + s_side * 0.86], [1.7, 12.8], color="#ff7b00", lw=2.2, zorder=2)

        # Draw Octagonal Booth Roof silhouette at bottom (Z = +31.2m) & Marzelvane Crown at top (Z = +72.0m)
        booth_cap = mpatches.Polygon(
            [[cx_col - 1.25, 0.85], [cx_col + 1.25, 0.85], [cx_col + 1.02, 1.40], [cx_col - 1.02, 1.40]],
            closed=True,
            facecolor="#241a12",
            edgecolor="#ff9e22",
            lw=1.8,
            zorder=2,
        )
        ax1.add_patch(booth_cap)

        # Stack: G (top), O, R, [Marzelvane Rings], 9 (bottom)
        char_w_v = 1.36
        char_h_v = 1.65
        v_stack = [
            ("G", 10.90),
            ("O", 8.75),
            ("R", 6.60),
            ("MARZEL", 4.95),
            ("9", 2.15),
        ]
        for tok, y_slot in v_stack:
            if tok == "MARZEL":
                _draw_marzelvane_separator_2d(ax1, cx=cx_col, cy=y_slot, radius=0.52, variant_id=m_var, zorder_base=6)
            else:
                _draw_stencil_gor_9_base(ax1, [(tok, cx_col - char_w_v * 0.5, char_w_v)], y0=y_slot, h=char_h_v, lw=9.5)

        ax1.text(
            cx_col,
            13.40,
            col_label,
            color="#ffba49" if m_var == "V4" else "#38eaff",
            fontsize=10.5,
            fontweight="bold",
            fontfamily="monospace",
            ha="center",
        )
        ax1.text(
            cx_col,
            0.42,
            "BOOTH ROOF (+31.2m)",
            color="#8fa8c8",
            fontsize=8.2,
            fontfamily="monospace",
            ha="center",
        )

    # Panel 2 (Top-Right): Selected Heavy Industrial Hull Stencil (with Marzelvane Rings!)
    ax2 = fig2.add_axes([0.52, 0.50, 0.44, 0.40], facecolor="#090d15")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6.2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.text(
        0.2,
        5.72,
        "2. HEAVY INDUSTRIAL HULL STENCIL  (CHAMFERED STENCIL + MARZELVANE RINGS)",
        color="#38eaff",
        fontsize=12.0,
        fontweight="bold",
        fontfamily="monospace",
    )
    hull_plate = mpatches.Rectangle((0.4, 1.0), 9.2, 4.2, facecolor="#1e252f", edgecolor="#56667a", lw=2.5, zorder=1)
    ax2.add_patch(hull_plate)
    for hx in range(10):
        stripe = mpatches.Polygon(
            [[0.4 + hx * 0.92, 1.0], [0.86 + hx * 0.92, 1.0], [1.1 + hx * 0.92, 1.48], [0.64 + hx * 0.92, 1.48]],
            closed=True,
            facecolor="#e68a1e" if hx % 2 == 0 else "#12161d",
            zorder=2,
        )
        ax2.add_patch(stripe)
    stencil_slots = [("G", 1.15, 1.32), ("O", 2.75, 1.32), ("R", 4.35, 1.32), ("9", 7.55, 1.32)]
    _draw_stencil_gor_9_base(ax2, stencil_slots, y0=2.65, h=1.85, lw=12.5)
    _draw_marzelvane_separator_2d(ax2, cx=6.61, cy=3.57, radius=0.54, variant_id="V4", zorder_base=6)
    ax2.text(
        5.0,
        1.98,
        "PHOTON PLATFORM  •  ASTEROID 3-5-1  •  DILITHIUM CORE #2",
        color="#9cb3ce",
        fontsize=10.5,
        fontweight="bold",
        fontfamily="monospace",
        ha="center",
    )
    ax2.text(
        5.0,
        0.42,
        "Primary Horizontal Brand Lockup for Reactor #2, Winch Crane, O.R.S. 351 Hull & Equipment Cases",
        color="#8fa8c8",
        fontsize=9.5,
        fontfamily="monospace",
        ha="center",
    )

    # Panel 3 (Bottom-Right): Studio Boom-Mic Cube, ON-AIR Plaque & Console Telemetry Bug (all using Stencil + Marzelvane Rings)
    ax3 = fig2.add_axes([0.52, 0.06, 0.44, 0.40], facecolor="#090d15")
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 6.2)
    ax3.set_aspect("equal")
    ax3.axis("off")
    ax3.text(
        0.2,
        5.72,
        "3. STUDIO BOOM-MIC CUBE, ON-AIR PLAQUE & CONSOLE TELEMETRY BUG",
        color="#38eaff",
        fontsize=12.0,
        fontweight="bold",
        fontfamily="monospace",
    )
    # Boom-mic shaft & cube flag on left
    ax3.plot([2.35, 2.35], [0.55, 5.15], color="#708299", lw=9, solid_capstyle="round", zorder=1)
    mic_head = mpatches.FancyBboxPatch((1.82, 4.15), 1.06, 1.0, boxstyle="round,pad=0.16", facecolor="#2a3442", edgecolor="#8fa8c8", lw=2.2, zorder=2)
    ax3.add_patch(mic_head)
    flag_box = mpatches.FancyBboxPatch((0.55, 1.85), 3.60, 1.75, boxstyle="round,pad=0.08", facecolor="#141b24", edgecolor="#ff9e22", lw=2.8, zorder=3)
    ax3.add_patch(flag_box)
    mic_slots = [("G", 0.80, 0.52), ("O", 1.44, 0.52), ("R", 2.08, 0.52), ("9", 3.38, 0.52)]
    _draw_stencil_gor_9_base(ax3, mic_slots, y0=2.62, h=0.72, lw=5.2)
    _draw_marzelvane_separator_2d(ax3, cx=2.99, cy=2.98, radius=0.22, variant_id="V1", zorder_base=6)
    ax3.text(2.35, 2.12, "351.9 GHz • OORT SEC-9", color="#38eaff", fontsize=8.5, fontweight="bold", fontfamily="monospace", ha="center", zorder=6)

    # Studio ON-AIR & Console Telemetry Plaque on right
    plaque = mpatches.FancyBboxPatch((4.85, 1.25), 4.75, 3.85, boxstyle="round,pad=0.12", facecolor="#101620", edgecolor="#38eaff", lw=2.2, zorder=2)
    ax3.add_patch(plaque)
    plaque_slots = [("G", 5.30, 0.68), ("O", 6.12, 0.68), ("R", 6.94, 0.68), ("9", 8.62, 0.68)]
    _draw_stencil_gor_9_base(ax3, plaque_slots, y0=3.75, h=0.95, lw=6.8)
    _draw_marzelvane_separator_2d(ax3, cx=8.12, cy=4.22, radius=0.28, variant_id="V4", zorder_base=6)

    on_air_box = mpatches.FancyBboxPatch((5.30, 2.35), 3.85, 0.95, boxstyle="round,pad=0.06", facecolor="#2b0c0c", edgecolor="#ff3322", lw=2.2, zorder=4)
    ax3.add_patch(on_air_box)
    ax3.text(7.22, 2.82, "●  O N   A I R  ●", color="#ff4433", fontsize=15.5, fontweight="bold", fontfamily="monospace", ha="center", va="center", zorder=5)
    ax3.text(7.22, 1.68, "CARRIER: LOCKED  •  LOC: 42,100 AU", color="#88e8ff", fontsize=8.8, fontfamily="monospace", ha="center", zorder=5)
    ax3.text(5.0, 0.42, "Unified Chamfered Stencil + Marzelvane Rings across Physical & Digital Touchpoints", color="#8fa8c8", fontsize=9.5, fontfamily="monospace", ha="center")

    apps_path = out_dir / "gor9_logo_brand_applications.png"
    fig2.savefig(apps_path, dpi=100, facecolor=fig2.get_facecolor())
    plt.close(fig2)

    return study_path, apps_path


if __name__ == "__main__":
    renders_dir = Path(__file__).resolve().parent.parent / "renders"
    p1, p2 = generate_design_study_sheets(renders_dir)
    print(f"Generated GOR-9 design study boards:\n  {p1}\n  {p2}")
