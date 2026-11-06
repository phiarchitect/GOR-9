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
    """Add a polygonal (hexagonal/pentagonal/octagonal) basalt prism or structural drum."""
    mat_top = mat_top or MATERIALS["basalt"]
    mat_side_a = mat_side_a or MATERIALS["basalt"]
    mat_side_b = mat_side_b or MATERIALS["basalt_dark"]
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
