"""
Shared 3D geometry primitives, coordinate transforms, UV texture fitting,
and material definitions for the GOR-9 IngeTrazo 0.6.0 component library.
"""

import math
from pathlib import Path

# ── Master Architectural Elevations (v03 Lighthouse Scale) ────────────
BOOTH_Z = 26.0       # Cantilevered Octagonal Broadcast Booth floor (+26.0m above summit pad)
MARZEL_Z = 72.0      # 4 Concentric Marzelvane Emitter Rings (+72.0m)
SPIRE_TOP_Z = 86.5   # Crown Cherenkov Spire tip (+86.5m)

# ── Standard Material Dictionary ─────────────────────────────────────
MATERIALS = {
    "basalt": {"color": (0.14, 0.16, 0.20), "roughness": 0.92, "metallic": 0.08},
    "basalt_dark": {"color": (0.09, 0.10, 0.13), "roughness": 0.95, "metallic": 0.05},
    "basalt_rim": {"color": (0.18, 0.21, 0.26), "roughness": 0.88, "metallic": 0.12},
    "steel": {"color": (0.28, 0.32, 0.38), "roughness": 0.45, "metallic": 0.78},
    "steel_dark": {"color": (0.16, 0.19, 0.23), "roughness": 0.50, "metallic": 0.80},
    "steel_light": {"color": (0.44, 0.49, 0.56), "roughness": 0.38, "metallic": 0.82},
    "brass": {"color": (0.76, 0.56, 0.24), "roughness": 0.30, "metallic": 0.88},
    "copper": {"color": (0.72, 0.42, 0.22), "roughness": 0.35, "metallic": 0.85},
    "amber_glow": {"color": (1.00, 0.65, 0.18), "emissive": True},
    "cyan_glow": {"color": (0.22, 0.92, 1.00), "emissive": True},
    "cyan_core": {"color": (0.65, 0.98, 1.00), "emissive": True},
    "crimson_glow": {"color": (1.00, 0.18, 0.14), "emissive": True},
    "neon_sign": {"color": (1.00, 0.52, 0.12), "emissive": True},
    "booth_floor": {"color": (0.13, 0.15, 0.18), "roughness": 0.65, "metallic": 0.35},
    "desk_hull": {"color": (0.19, 0.22, 0.26), "roughness": 0.48, "metallic": 0.68},
    "desk_trim": {"color": (0.11, 0.13, 0.16), "roughness": 0.40, "metallic": 0.72},
    "desk_leather": {"color": (0.08, 0.09, 0.11), "roughness": 0.74, "metallic": 0.08},
    "bezel_dark": {"color": (0.07, 0.08, 0.10), "roughness": 0.34, "metallic": 0.78},
    "rack_panel": {"color": (0.12, 0.14, 0.17), "roughness": 0.44, "metallic": 0.72},
    "paper_edge": {"color": (0.84, 0.80, 0.72), "roughness": 0.62, "metallic": 0.02},
    "coffee": {"color": (0.06, 0.03, 0.015), "roughness": 0.08, "metallic": 0.05},
    "hab_hull": {"color": (0.24, 0.27, 0.31), "roughness": 0.52, "metallic": 0.62},
    "glass": {
        "color": (0.35, 0.62, 0.78),
        "opacity": 0.16,
        "roughness": 0.10,
        "metallic": 0.10,
    },
}


def create_scene_group(scene, name: str):
    """Create a new IngeTrazo Group with an empty Mesh and append it to scene.groups."""
    from core.group import Group
    from core.mesh import Mesh

    grp = Group(name=name, mesh=Mesh())
    scene.groups.append(grp)
    return grp


def add_face(mesh, pts, attrs: dict):
    from PySide6.QtGui import QVector3D

    qpts = [p if isinstance(p, QVector3D) else QVector3D(*p) for p in pts]
    f = mesh.add_face(qpts)
    if f is not None and attrs:
        f.attrs.update(attrs)
    return f


def add_quad(mesh, p0, p1, p2, p3, attrs: dict):
    add_face(mesh, [p0, p1, p2, p3], dict(attrs))


def add_textured_quad(
    mesh,
    p0,
    p1,
    p2,
    p3,
    tex_path: Path,
    color=(0.95, 0.98, 1.0),
    emissive=True,
):
    """Add a quad with an exact 1:1 fitted affine UV map (p0=BL, p1=BR, p2=TR, p3=TL)."""
    from PySide6.QtGui import QVector3D
    from core.texture import fit_uv_affine

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
    add_face(mesh, pts, attrs)


def add_box(mesh, x0, y0, z0, x1, y1, z1, attrs: dict):
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


def add_strut(mesh, p_start, p_end, radius: float, attrs: dict, sides: int = 6):
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
    add_face(mesh, list(reversed(ring_a)), dict(attrs))
    add_face(mesh, ring_b, dict(attrs))


def add_ring_torus(
    mesh,
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


def add_prism(
    mesh,
    cx: float,
    cy: float,
    rad: float,
    z_bot: float,
    z_top: float,
    sides: int = 6,
    rot_rad: float = 0.25,
    taper: float = 1.08,
    mat_top: dict = None,
    mat_side_a: dict = None,
    mat_side_b: dict = None,
):
    """
    Add a polygonal (hexagonal/pentagonal/octagonal) basalt prism or structural drum.
    When building volcanic basalt columns, automatically introduces natural per-corner
    angular/radial irregularity, multi-tier horizontal cooling-joint chisel steps,
    and chamfered/cleaved column crowns so surfaces and silhouettes look organically
    fractured rather than mathematically regular.
    """
    is_basalt = (mat_side_a is None) or (
        mat_side_a.get("roughness", 0.0) >= 0.85 and not mat_side_a.get("emissive", False)
    )
    mat_top = mat_top or MATERIALS["basalt"]
    mat_side_a = mat_side_a or MATERIALS["basalt"]
    mat_side_b = mat_side_b or MATERIALS["basalt_dark"]

    if not is_basalt or (z_top - z_bot) < 2.2:
        top_pts = []
        bot_pts = []
        for i in range(sides):
            ang = 2.0 * math.pi * i / sides + rot_rad
            ca, sa = math.cos(ang), math.sin(ang)
            top_pts.append((cx + rad * ca, cy + rad * sa, z_top))
            bot_pts.append((cx + rad * taper * ca, cy + rad * taper * sa, z_bot))
        for i in range(sides):
            ni = (i + 1) % sides
            shade = mat_side_a if (i % 2 == 0) else mat_side_b
            add_quad(mesh, bot_pts[i], bot_pts[ni], top_pts[ni], top_pts[i], shade)
        add_face(mesh, top_pts, dict(mat_top))
        add_face(mesh, list(reversed(bot_pts)), dict(mat_side_b))
        return

    # Deterministic column hash from (cx, cy, z_top)
    h_seed = int(abs(cx * 137.0 + cy * 293.0 + z_top * 53.0 + rot_rad * 97.0)) & 0xFFFF
    dist_center = math.sqrt(cx * cx + cy * cy)
    # Keep station foundation terraces (R < 25m, z_top in -2.5..0.0) nearly flat on top so buildings sit flush
    is_foundation_pad = dist_center < 25.0 and -2.6 <= z_top <= 0.1

    # 1. Irregular polygonal cross-section angles & per-vertex radial factors (unequal side lengths!)
    step = 2.0 * math.pi / sides
    ax = 0.85 + (((h_seed >> 3) % 100) / 100.0) * 0.30
    ay = 1.0 / ax
    corner_angles = []
    corner_r_mod = []
    for i in range(sides):
        vh = (h_seed * 131 + i * 521 + (i * i) * 97) & 0xFFFF
        ang_jitter = (((vh % 100) / 100.0) - 0.5) * 0.44 * step
        r_jitter = 0.84 + ((((vh >> 6) % 100) / 100.0) * 0.32)
        theta = i * step + rot_rad + ang_jitter
        ux = ax * r_jitter * math.cos(theta)
        uy = ay * r_jitter * math.sin(theta)
        corner_angles.append(math.atan2(uy, ux))
        corner_r_mod.append(math.hypot(ux, uy))

    # 2. Subdivide vertically into stacked volcanic cooling-joint drums with chiseled fracture ledges
    col_h = z_top - z_bot
    num_tiers = max(3, min(11, int(col_h / 12.0) + 2))
    tier_rings = []
    for t_idx in range(num_tiers + 1):
        # Concentrate cooling-joint subdivisions in the upper 95m of tall columns where cameras view the cliffs closely
        lin_t = t_idx / float(num_tiers)
        u_t = 1.0 - math.pow(1.0 - lin_t, 1.35) if col_h > 90.0 else lin_t
        zt = z_bot + col_h * u_t
        base_scale = taper * (1.0 - u_t) + 1.0 * u_t
        # Horizontal cooling-joint pinch-and-swell step & lateral fracture shear at interior tier boundaries
        if 0 < t_idx < num_tiers:
            th = (h_seed + t_idx * 521) & 0xFFFF
            step_scale = 1.0 + (((th % 100) / 100.0) - 0.5) * 0.11
            dx = ((((th // 7) % 100) / 100.0) - 0.5) * rad * 0.065
            dy = ((((th // 13) % 100) / 100.0) - 0.5) * rad * 0.065
        else:
            step_scale = 1.0
            dx, dy = 0.0, 0.0

        ring_pts = []
        for i in range(sides):
            ca, sa = math.cos(corner_angles[i]), math.sin(corner_angles[i])
            # Per-corner spall & chisel variation across cooling-joint tiers
            ch_hash = (h_seed * 73 + t_idx * 389 + i * 613) & 0xFFFF
            corner_spall = (
                1.0 + (((ch_hash % 100) / 100.0) - 0.5) * 0.075
                if (0 < t_idx < num_tiers)
                else 1.0
            )
            rv = rad * base_scale * step_scale * corner_r_mod[i] * corner_spall
            # Cleavage height wave & chiseled step on non-foundation rims
            dz = 0.0
            if t_idx == num_tiers and not is_foundation_pad:
                dz = math.sin(i * 1.9 + h_seed * 0.17) * min(0.42, rad * 0.075)
            elif 0 < t_idx < num_tiers:
                dz = math.cos(i * 1.5 + t_idx * 2.1 + h_seed * 0.11) * min(0.38, rad * 0.065)
            ring_pts.append((cx + dx + rv * ca, cy + dy + rv * sa, zt + dz))
        tier_rings.append(ring_pts)

    # Build vertical facet quads across all cooling-joint tiers
    for t_idx in range(num_tiers):
        r_lo = tier_rings[t_idx]
        r_hi = tier_rings[t_idx + 1]
        for i in range(sides):
            ni = (i + 1) % sides
            shade = mat_side_a if ((i + t_idx) % 2 == 0) else mat_side_b
            add_quad(mesh, r_lo[i], r_lo[ni], r_hi[ni], r_hi[i], shade)

    # 3. Chamfered / Cleaved Basalt Crown Cap at z_top
    top_outer = tier_rings[-1]
    if is_foundation_pad:
        add_face(mesh, top_outer, dict(mat_top))
    else:
        inner_pts = []
        crown_dz = min(0.42, rad * 0.075) * (1.0 if (h_seed % 2 == 0) else -0.55)
        for i in range(sides):
            ox, oy, oz = top_outer[i]
            ix = cx + (ox - cx) * 0.74
            iy = cy + (oy - cy) * 0.74
            iz = oz + crown_dz
            inner_pts.append((ix, iy, iz))
            ni = (i + 1) % sides
            ox_n, oy_n, oz_n = top_outer[ni]
            ix_n = cx + (ox_n - cx) * 0.74
            iy_n = cy + (oy_n - cy) * 0.74
            iz_n = oz_n + crown_dz
            chamfer_mat = MATERIALS["basalt_rim"] if (i % 2 == 0) else mat_top
            add_quad(mesh, (ox, oy, oz), (ox_n, oy_n, oz_n), (ix_n, iy_n, iz_n), (ix, iy, iz), chamfer_mat)
        add_face(mesh, inner_pts, dict(mat_top))

    add_face(mesh, list(reversed(tier_rings[0])), dict(mat_side_b))


def with_channel(mat: dict, channel: str) -> dict:
    """Return a copy of a material dict tagged with an animatable light_channel name."""
    d = dict(mat)
    d["light_channel"] = channel
    return d


def add_craggy_boulder(
    mesh,
    cx: float,
    cy: float,
    cz: float,
    rx: float,
    ry: float,
    rz: float,
    seed: int = 1,
    lat_rings: int = 6,
    lon_segs: int = 12,
    mat_a: dict = None,
    mat_b: dict = None,
    mat_rim: dict = None,
):
    """
    Build a closed 3D craggy carbonaceous-basalt asteroid / boulder polyhedron
    with deterministic faceted ridges, angular fracture planes, and cratered flats.
    """
    mat_a = mat_a or MATERIALS["basalt"]
    mat_b = mat_b or MATERIALS["basalt_dark"]
    mat_rim = mat_rim or MATERIALS["basalt_rim"]

    def _radius_mod(lat_i: int, lon_j: int) -> float:
        h = (lat_i * 73 + lon_j * 151 + seed * 313) & 0xFFFF
        w1 = math.sin(lat_i * 1.7 + lon_j * 1.1 + seed * 0.9) * 0.16
        w2 = math.cos(lat_i * 2.3 - lon_j * 1.9 + seed * 1.7) * 0.12
        crag = ((h % 100) / 100.0 - 0.5) * 0.18
        return max(0.58, 1.0 + w1 + w2 + crag)

    # North & South poles (top & bottom crag tips)
    top_pt = (
        cx + rx * 0.08 * math.sin(seed),
        cy + ry * 0.08 * math.cos(seed),
        cz + rz * (0.92 + 0.08 * math.cos(seed * 1.3)),
    )
    bot_pt = (
        cx - rx * 0.08 * math.cos(seed),
        cy + ry * 0.08 * math.sin(seed),
        cz - rz * (0.94 + 0.06 * math.sin(seed * 1.7)),
    )

    rings = []
    for i in range(1, lat_rings):
        v = i / float(lat_rings)
        phi = math.pi * (0.5 - v)  # +pi/2 down to -pi/2
        cp, sp = math.cos(phi), math.sin(phi)
        ring = []
        for j in range(lon_segs):
            theta = 2.0 * math.pi * j / float(lon_segs) + (i % 2) * (math.pi / lon_segs * 0.35)
            ct, st = math.cos(theta), math.sin(theta)
            rm = _radius_mod(i, j)
            px = cx + rx * rm * cp * ct
            py = cy + ry * rm * cp * st
            pz = cz + rz * rm * sp
            ring.append((px, py, pz))
        rings.append(ring)

    # Top polar cap triangles
    first_ring = rings[0]
    for j in range(lon_segs):
        nj = (j + 1) % lon_segs
        shade = mat_rim if (j % 3 == 0) else (mat_a if j % 2 == 0 else mat_b)
        add_face(mesh, [first_ring[j], first_ring[nj], top_pt], dict(shade))

    # Middle latitude quads
    for i in range(len(rings) - 1):
        r_hi = rings[i]
        r_lo = rings[i + 1]
        for j in range(lon_segs):
            nj = (j + 1) % lon_segs
            if (i + j) % 5 == 0:
                shade = mat_rim
            elif (i + j) % 2 == 0:
                shade = mat_a
            else:
                shade = mat_b
            add_quad(mesh, r_lo[j], r_lo[nj], r_hi[nj], r_hi[j], shade)

    # Bottom polar cap triangles
    last_ring = rings[-1]
    for j in range(lon_segs):
        nj = (j + 1) % lon_segs
        shade = mat_b if (j % 2 == 0) else mat_a
        add_face(mesh, [last_ring[nj], last_ring[j], bot_pt], dict(shade))


def add_caged_ladder(
    mesh,
    x: float,
    y: float,
    z0: float,
    z1: float,
    facing_ang_deg: float = 270.0,
    with_cage: bool = True,
):
    """Add a vertical maintenance ladder with rungs and optional EVA safety cage hoops."""
    ang = math.radians(facing_ang_deg)
    ca, sa = math.cos(ang), math.sin(ang)
    rx, ry = -sa, ca  # lateral rail vector
    rail_w = 0.24

    p_l0 = (x - rail_w * rx, y - rail_w * ry, z0)
    p_l1 = (x - rail_w * rx, y - rail_w * ry, z1)
    p_r0 = (x + rail_w * rx, y + rail_w * ry, z0)
    p_r1 = (x + rail_w * rx, y + rail_w * ry, z1)
    add_strut(mesh, p_l0, p_l1, 0.022, MATERIALS["steel_light"], sides=6)
    add_strut(mesh, p_r0, p_r1, 0.022, MATERIALS["steel_light"], sides=6)

    # Rungs every 0.40m
    num_rungs = max(2, int((z1 - z0) / 0.40))
    for i in range(num_rungs + 1):
        zr = z0 + (z1 - z0) * (i / num_rungs)
        add_strut(
            mesh,
            (x - rail_w * rx, y - rail_w * ry, zr),
            (x + rail_w * rx, y + rail_w * ry, zr),
            0.014,
            MATERIALS["brass"],
            sides=6,
        )

    # Safety cage hoops every 1.6m above z0 + 2.0m
    if with_cage and (z1 - z0) > 2.2:
        cage_cx = x + 0.36 * ca
        cage_cy = y + 0.36 * sa
        z_cage_start = z0 + 1.8
        num_hoops = max(2, int((z1 - z_cage_start) / 1.6))
        for h in range(num_hoops + 1):
            zh = z_cage_start + (z1 - 0.3 - z_cage_start) * (h / num_hoops)
            add_ring_torus(
                mesh,
                cage_cx,
                cage_cy,
                zh,
                0.38,
                0.016,
                MATERIALS["steel"],
                segs=14,
                tube_sides=6,
            )
        # 3 vertical cage straps
        for strap_deg in (-65, 0, 65):
            sa_rad = ang + math.radians(strap_deg)
            sx = cage_cx + 0.38 * math.cos(sa_rad)
            sy = cage_cy + 0.38 * math.sin(sa_rad)
            add_strut(
                mesh,
                (sx, sy, z_cage_start),
                (sx, sy, z1 - 0.3),
                0.012,
                MATERIALS["steel_dark"],
                sides=4,
            )


def add_octahedron_beacon(mesh, cx: float, cy: float, cz: float, r: float, attrs: dict):
    """Add an 8-faced glowing octahedron star/beacon crystal at `(cx, cy, cz)`."""
    top = (cx, cy, cz + r)
    bot = (cx, cy, cz - r)
    ring = [
        (cx + r, cy, cz),
        (cx, cy + r, cz),
        (cx - r, cy, cz),
        (cx, cy - r, cz),
    ]
    for i in range(4):
        ni = (i + 1) % 4
        add_face(mesh, [ring[i], ring[ni], top], dict(attrs))
        add_face(mesh, [ring[ni], ring[i], bot], dict(attrs))


