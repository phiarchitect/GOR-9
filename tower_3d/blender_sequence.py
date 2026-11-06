#!/usr/bin/env python3
"""
GOR-9 • Blender 5.x Native Scene, Procedural Basalt Shaders & Sequence Generator
================================================================================
Builds a native Blender `.blend` project (`tower_3d/gor9_tower.blend`) directly
from the modular GOR-9 3D component library (`tower_3d/components/`) and renders
either high-resolution `2560x1440` QHD still images (`--still-only`) or smooth
native-24fps MP4 sequences (`tower_3d/renders/sequences/`).

Key Features:
  - 100% Columnar-Basalt Cliff Architecture (`360m`-wide Asteroid 3-5-1) with
    procedural Blender 5.x volcanic basalt rock shaders (horizontal cooling
    striations, macro/micro mineral grain, and normal-mapped rock bump relief).
  - Clean 8K (`8192x4096`) Celestial Sphere World Map (`celestial_sky_clean.png`)
    with pinpoint starfield, Galactic plane, and Sol (`m = -3.62` at `42,100 AU`,
    `Az = 212.4°, El = +22.4°`).
  - Distant 3D Columnar-Basalt Tumbling Asteroids (`R ≈ 570m–610m`) and Orbital
    Relay Satellites (`ORS_351_Satellite` at `R ≈ 410m`, `Relay_Sonde_B` at `R ≈ 490m`).
  - Multi-Channel Sequential Light Choreography (`ring_1..4`, `spire_beacon`,
    `waveguide_low/mid/high`, `reactor_glow`, `hazard_beacons`, `sat_beacon`).
"""

import argparse
import math
import shutil
import sys
import types
from pathlib import Path

import bpy

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


# ── Pure-Python Shim for IngeTrazo & PySide6 inside Blender's Python ──
class _QVector3D:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_tuple(self):
        return (self.x, self.y, self.z)


class _ShimFace:
    __slots__ = ("pts", "attrs")

    def __init__(self, pts):
        self.pts = [p.to_tuple() if isinstance(p, _QVector3D) else tuple(float(c) for c in p) for p in pts]
        self.attrs = {}


class _ShimMesh:
    def __init__(self):
        self.faces = []

    def add_face(self, pts):
        f = _ShimFace(pts)
        self.faces.append(f)
        return f


class _ShimGroup:
    def __init__(self, name: str, mesh: _ShimMesh | None = None):
        self.name = name
        self.mesh = mesh or _ShimMesh()
        self.pivot = None


class _ShimScene:
    def __init__(self):
        self.groups = []


def _install_ingetrazo_shim():
    pyside = types.ModuleType("PySide6")
    qtgui = types.ModuleType("PySide6.QtGui")
    qtgui.QVector3D = _QVector3D
    pyside.QtGui = qtgui
    sys.modules["PySide6"] = pyside
    sys.modules["PySide6.QtGui"] = qtgui

    core_mod = types.ModuleType("core")
    grp_mod = types.ModuleType("core.group")
    grp_mod.Group = _ShimGroup
    mesh_mod = types.ModuleType("core.mesh")
    mesh_mod.Mesh = _ShimMesh
    scene_mod = types.ModuleType("core.scene")
    scene_mod.Scene = _ShimScene
    tex_mod = types.ModuleType("core.texture")
    tex_mod.fit_uv_affine = lambda pts, uvs: uvs

    sys.modules["core"] = core_mod
    sys.modules["core.group"] = grp_mod
    sys.modules["core.mesh"] = mesh_mod
    sys.modules["core.scene"] = scene_mod
    sys.modules["core.texture"] = tex_mod


_install_ingetrazo_shim()

from components import (  # noqa: E402
    BOOTH_Z,
    MARZEL_Z,
    SPIRE_TOP_Z,
    az_el_to_xyz,
    build_base_infrastructure,
    build_celestial_beacons,
    build_companion_boulders,
    build_continuous_tower_and_spine,
    build_furniture_and_props,
    build_marzelvane_emitters,
    build_octagonal_booth,
    build_orbital_satellites,
    build_perimeter_consoles,
    build_prismatic_basalt_terrain,
    build_tumbling_asteroids,
)


def clear_blender_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def set_bsdf_input(bsdf, names, value):
    for name in names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return


def _attach_procedural_basalt_shader(nodes, links, bsdf, base_rgb: tuple[float, float, float]):
    """
    Build a hyper-rough 3D procedural + UV Tangent-Space Normal-Mapped Columnar-Basalt shader:
      1. 2048x2048 Tangent-Space Normal Map (`basalt_normal.png`, `Strength = 2.35`) encoding
         tilted hackly rock cleavage chips, sawtooth horizontal chisel ledges, and vesicular pits.
      2. Chained into two 3D Object-Space Procedural Bump nodes with physically calibrated
         world-space distances (`Distance = 0.16m` for macro cooling-joint chisel ribs and
         `Distance = 0.055m` for high-frequency 15-octave volcanic scoria grit).
      3. Granular mineral-speckled volcanic slate albedo (`basalt_diffuse.png` + 3D rock tint)
         with zero artificial spiderweb outlines—all light/dark contrast comes from true
         3D displacement and surface normal relief catching raking starlight!
    """
    r, g, b = base_rgb
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1500, 0)

    renders_dir = SCRIPT_DIR / "renders"
    diff_path = renders_dir / "basalt_diffuse.png"
    norm_path = renders_dir / "basalt_normal.png"
    bump_path = renders_dir / "basalt_bump.png"
    rough_path = renders_dir / "basalt_roughness.png"

    # A. 3D Coordinate Turbulence Warp
    warp_noise = nodes.new(type="ShaderNodeTexNoise")
    warp_noise.location = (-1260, 240)
    warp_noise.inputs["Scale"].default_value = 0.85
    warp_noise.inputs["Detail"].default_value = 10.0
    warp_noise.inputs["Roughness"].default_value = 0.82
    links.new(tex_coord.outputs["Object"], warp_noise.inputs["Vector"])

    warp_scale = nodes.new(type="ShaderNodeVectorMath")
    warp_scale.location = (-1060, 240)
    warp_scale.operation = "SCALE"
    warp_scale.inputs["Scale"].default_value = 0.55
    links.new(warp_noise.outputs["Color"], warp_scale.inputs["Vector"])

    warped_obj = nodes.new(type="ShaderNodeVectorMath")
    warped_obj.location = (-860, 180)
    warped_obj.operation = "ADD"
    links.new(tex_coord.outputs["Object"], warped_obj.inputs[0])
    links.new(warp_scale.outputs["Vector"], warped_obj.inputs[1])

    # B. 3D Horizontal Cooling-Joint Chisel Striations & Spalled Ledges
    striae_map = nodes.new(type="ShaderNodeMapping")
    striae_map.location = (-860, -80)
    striae_map.inputs["Scale"].default_value = (0.34, 0.34, 2.85)
    links.new(warped_obj.outputs["Vector"], striae_map.inputs["Vector"])

    noise_striae = nodes.new(type="ShaderNodeTexNoise")
    noise_striae.location = (-640, -80)
    noise_striae.inputs["Scale"].default_value = 1.35
    noise_striae.inputs["Detail"].default_value = 15.0
    noise_striae.inputs["Roughness"].default_value = 0.90
    if "Distortion" in noise_striae.inputs:
        noise_striae.inputs["Distortion"].default_value = 0.48
    links.new(striae_map.outputs["Vector"], noise_striae.inputs["Vector"])

    # C. 3D High-Frequency Volcanic Scoria Grit & Vesicular Pitting
    noise_grit = nodes.new(type="ShaderNodeTexNoise")
    noise_grit.location = (-640, -340)
    noise_grit.inputs["Scale"].default_value = 18.5
    noise_grit.inputs["Detail"].default_value = 15.0
    noise_grit.inputs["Roughness"].default_value = 0.94
    if "Distortion" in noise_grit.inputs:
        noise_grit.inputs["Distortion"].default_value = 0.32
    links.new(tex_coord.outputs["Object"], noise_grit.inputs["Vector"])

    # D. 2048x2048 UV Tangent-Space Normal Map -> Chained into 3D Macro & Micro Bump Nodes
    base_normal_socket = None
    if norm_path.exists():
        tex_norm = nodes.new(type="ShaderNodeTexImage")
        tex_norm.location = (-640, -620)
        img_norm = bpy.data.images.load(str(norm_path), check_existing=True)
        if hasattr(img_norm, "colorspace_settings"):
            img_norm.colorspace_settings.name = "Non-Color"
        tex_norm.image = img_norm
        links.new(tex_coord.outputs["UV"], tex_norm.inputs["Vector"])

        norm_map_node = nodes.new(type="ShaderNodeNormalMap")
        norm_map_node.location = (-340, -620)
        norm_map_node.inputs["Strength"].default_value = 2.35
        links.new(tex_norm.outputs["Color"], norm_map_node.inputs["Color"])
        base_normal_socket = norm_map_node.outputs["Normal"]

    if bump_path.exists():
        tex_bump = nodes.new(type="ShaderNodeTexImage")
        tex_bump.location = (-640, -880)
        img_bump = bpy.data.images.load(str(bump_path), check_existing=True)
        if hasattr(img_bump, "colorspace_settings"):
            img_bump.colorspace_settings.name = "Non-Color"
        tex_bump.image = img_bump
        links.new(tex_coord.outputs["UV"], tex_bump.inputs["Vector"])

        uv_bump_mix = nodes.new(type="ShaderNodeMath")
        uv_bump_mix.location = (-160, -360)
        uv_bump_mix.operation = "MULTIPLY_ADD"
        uv_bump_mix.inputs[1].default_value = 0.65
        links.new(tex_bump.outputs["Color"], uv_bump_mix.inputs[0])
        links.new(noise_grit.outputs["Fac"], uv_bump_mix.inputs[2])
        micro_height_out = uv_bump_mix.outputs["Value"]
    else:
        micro_height_out = noise_grit.outputs["Fac"]

    bump_macro = nodes.new(type="ShaderNodeBump")
    bump_macro.location = (-20, -140)
    bump_macro.inputs["Strength"].default_value = 0.95
    bump_macro.inputs["Distance"].default_value = 0.16
    links.new(noise_striae.outputs["Fac"], bump_macro.inputs["Height"])
    if base_normal_socket is not None:
        links.new(base_normal_socket, bump_macro.inputs["Normal"])

    bump_micro = nodes.new(type="ShaderNodeBump")
    bump_micro.location = (200, -220)
    bump_micro.inputs["Strength"].default_value = 0.92
    bump_micro.inputs["Distance"].default_value = 0.055
    links.new(micro_height_out, bump_micro.inputs["Height"])
    links.new(bump_macro.outputs["Normal"], bump_micro.inputs["Normal"])
    if "Normal" in bsdf.inputs:
        links.new(bump_micro.outputs["Normal"], bsdf.inputs["Normal"])

    # E. Granular Weathered Volcanic Basalt Albedo (zero painted spiderweb lines!)
    tint_scale = max(0.65, min(1.48, (r + g + b) / 0.46))
    col_ramp = nodes.new(type="ShaderNodeValToRGB")
    col_ramp.location = (-360, 120)
    elts = col_ramp.color_ramp.elements
    elts[0].position = 0.20
    elts[0].color = (r * 0.62, g * 0.64, b * 0.68, 1.0)
    elts[1].position = 0.80
    elts[1].color = (
        min(1.0, r * 1.48 + 0.02),
        min(1.0, g * 1.48 + 0.02),
        min(1.0, b * 1.54 + 0.03),
        1.0,
    )
    links.new(noise_striae.outputs["Fac"], col_ramp.inputs["Fac"])

    if diff_path.exists():
        tex_diff = nodes.new(type="ShaderNodeTexImage")
        tex_diff.location = (-380, 380)
        tex_diff.image = bpy.data.images.load(str(diff_path), check_existing=True)
        links.new(tex_coord.outputs["UV"], tex_diff.inputs["Vector"])

        vec_mul = nodes.new(type="ShaderNodeVectorMath")
        vec_mul.location = (-60, 220)
        vec_mul.operation = "MULTIPLY"
        links.new(tex_diff.outputs["Color"], vec_mul.inputs[0])
        links.new(col_ramp.outputs["Color"], vec_mul.inputs[1])

        vec_scale = nodes.new(type="ShaderNodeVectorMath")
        vec_scale.location = (140, 220)
        vec_scale.operation = "SCALE"
        vec_scale.inputs["Scale"].default_value = 1.90 * tint_scale
        links.new(vec_mul.outputs["Vector"], vec_scale.inputs["Vector"])
        links.new(vec_scale.outputs["Vector"], bsdf.inputs["Base Color"])
    else:
        links.new(col_ramp.outputs["Color"], bsdf.inputs["Base Color"])

    # F. Roughness Map + 3D Grit Modulation
    if rough_path.exists():
        tex_rough = nodes.new(type="ShaderNodeTexImage")
        tex_rough.location = (-340, -880)
        img_rough = bpy.data.images.load(str(rough_path), check_existing=True)
        if hasattr(img_rough, "colorspace_settings"):
            img_rough.colorspace_settings.name = "Non-Color"
        tex_rough.image = img_rough
        links.new(tex_coord.outputs["UV"], tex_rough.inputs["Vector"])
        links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        rough_ramp = nodes.new(type="ShaderNodeValToRGB")
        rough_ramp.location = (-40, -560)
        r_elts = rough_ramp.color_ramp.elements
        r_elts[0].position = 0.20
        r_elts[0].color = (0.96, 0.96, 0.96, 1.0)
        r_elts[1].position = 0.80
        r_elts[1].color = (0.42, 0.42, 0.42, 1.0)
        links.new(noise_grit.outputs["Fac"], rough_ramp.inputs["Fac"])
        links.new(rough_ramp.outputs["Color"], bsdf.inputs["Roughness"])




def _attach_procedural_metal_bump(nodes, links, bsdf):
    """Add brushed-anodized / powder-coat micro-relief to console cabinets, bezels, steel, and brass."""
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-560, -180)
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-360, -180)
    noise.inputs["Scale"].default_value = 18.5
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.68
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])

    bump = nodes.new(type="ShaderNodeBump")
    bump.location = (-140, -180)
    bump.inputs["Strength"].default_value = 0.09
    bump.inputs["Distance"].default_value = 0.008
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _attach_procedural_leather_bump(nodes, links, bsdf):
    """Add fine pebble-grain leather micro-relief to console wrist bolsters, stool cushions, and mats."""
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-560, -180)
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-360, -180)
    noise.inputs["Scale"].default_value = 44.0
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.78
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])

    bump = nodes.new(type="ShaderNodeBump")
    bump.location = (-140, -180)
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.004
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def build_blender_material(
    attrs: dict,
    mat_cache: dict,
    channel_materials: dict[str, list],
    group_name: str = "",
):
    color = tuple(round(float(c), 4) for c in attrs.get("color", (0.5, 0.5, 0.5)))
    roughness = round(float(attrs.get("roughness", 0.5)), 3)
    metallic = round(float(attrs.get("metallic", 0.2)), 3)
    opacity = round(float(attrs.get("opacity", 1.0)), 3)
    emissive = bool(attrs.get("emissive", False))
    light_channel = str(attrs.get("light_channel", ""))
    tex_info = attrs.get("texture") or {}
    tex_path = tex_info.get("path", "") if isinstance(tex_info, dict) else ""

    key = (
        color,
        roughness,
        metallic,
        opacity,
        emissive,
        tex_path,
        light_channel,
        group_name if opacity < 0.95 else "",
    )
    if key in mat_cache:
        return mat_cache[key]

    tag = light_channel or (Path(tex_path).stem if tex_path else group_name)
    mat_name = f"GOR9_{tag}_{len(mat_cache)}"
    bmat = bpy.data.materials.new(name=mat_name)
    bmat.use_nodes = True
    nodes = bmat.node_tree.nodes
    links = bmat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type="ShaderNodeOutputMaterial")
    out_node.location = (400, 0)

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.name = "Principled BSDF"
    bsdf.location = (80, 0)
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    r, g, b = color
    set_bsdf_input(bsdf, ["Base Color"], (r, g, b, 1.0))
    set_bsdf_input(bsdf, ["Roughness"], roughness)
    set_bsdf_input(bsdf, ["Metallic"], metallic)

    is_cherenkov = emissive and b > 0.85 and g > 0.70
    is_crimson = emissive and r > 0.85 and g < 0.30
    is_rock_group = any(k in group_name for k in ("Basalt", "Boulder", "Asteroid"))
    is_basalt = is_rock_group and (not emissive) and (not tex_path) and roughness >= 0.85 and metallic <= 0.15
    is_leather = (not emissive) and (not tex_path) and (0.68 <= roughness < 0.84) and metallic <= 0.15

    if tex_path and Path(tex_path).exists():
        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.location = (-320, 0)
        tex_node.image = bpy.data.images.load(str(tex_path), check_existing=True)
        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        if "Emission Color" in bsdf.inputs:
            links.new(tex_node.outputs["Color"], bsdf.inputs["Emission Color"])
        elif "Emission" in bsdf.inputs:
            links.new(tex_node.outputs["Color"], bsdf.inputs["Emission"])
        if emissive:
            # Glossy CRT / plasma console monitor glass
            set_bsdf_input(bsdf, ["Emission Strength"], 1.95)
            set_bsdf_input(bsdf, ["Roughness"], 0.05)
            set_bsdf_input(bsdf, ["Specular IOR Level", "Specular"], 0.75)
            set_bsdf_input(bsdf, ["Coat Weight", "Clearcoat"], 0.55)
            set_bsdf_input(bsdf, ["Coat Roughness", "Clearcoat Roughness"], 0.03)
        else:
            # Physical printed logbook paper, eQSL cards, and engraved metal badges
            set_bsdf_input(bsdf, ["Emission Strength"], 0.35)
            set_bsdf_input(bsdf, ["Roughness"], 0.42)
    elif emissive:
        # Set Base Color to black and Specular to 0 on emissive neon/beacon surfaces so external
        # directional sunlight does not add white specular/diffuse washout to deep crimson red!
        set_bsdf_input(bsdf, ["Base Color"], (0.0, 0.0, 0.0, 1.0))
        set_bsdf_input(bsdf, ["Specular IOR Level", "Specular"], 0.0)
        set_bsdf_input(bsdf, ["Roughness"], 1.0)
        set_bsdf_input(bsdf, ["Emission Color", "Emission"], (r, g, b, 1.0))
        if light_channel in ("booth_window_glow", "booth_wall_glow"):
            strength = 0.85
        elif light_channel == "booth_ceiling_glow":
            strength = 2.2
        elif light_channel == "sign_glow":
            strength = 1.65
        elif light_channel == "sign_core_glow":
            strength = 2.85
        elif light_channel in ("booth_glow", "hab_glow"):
            strength = 2.4
        elif group_name == "Celestial_Beacons":
            strength = 12.0
        elif is_cherenkov:
            strength = 10.0
        elif is_crimson:
            strength = 2.5
        else:
            strength = 6.0
        set_bsdf_input(bsdf, ["Emission Strength"], strength)
    elif is_basalt:
        _attach_procedural_basalt_shader(nodes, links, bsdf, color)
    elif is_leather and opacity >= 0.95:
        _attach_procedural_leather_bump(nodes, links, bsdf)
    elif metallic >= 0.30 and opacity >= 0.95:
        _attach_procedural_metal_bump(nodes, links, bsdf)

    if opacity < 0.95:
        if hasattr(bmat, "blend_method"):
            bmat.blend_method = "BLEND"
        if hasattr(bmat, "surface_render_method"):
            bmat.surface_render_method = "BLENDED"
        bmat.use_backface_culling = False
        set_bsdf_input(bsdf, ["Alpha"], opacity)
        set_bsdf_input(bsdf, ["Transmission Weight", "Transmission"], 0.0)
        set_bsdf_input(bsdf, ["Specular IOR Level", "Specular"], 0.35)
        set_bsdf_input(bsdf, ["Roughness"], 0.02)

    mat_cache[key] = bmat
    if light_channel:
        channel_materials.setdefault(light_channel, []).append((bmat, bsdf, color))
    return bmat


def import_ingetrazo_scene_to_blender(
    sky_hud: bool = False,
) -> tuple[dict[str, bpy.types.Object], dict[str, list]]:
    """Build the modular IngeTrazo scene in memory and convert each group into a Blender Object."""
    igz_scene = _ShimScene()
    build_prismatic_basalt_terrain(igz_scene)
    build_base_infrastructure(igz_scene)
    build_continuous_tower_and_spine(igz_scene)
    build_octagonal_booth(igz_scene)
    build_perimeter_consoles(igz_scene, REPO_ROOT)
    build_furniture_and_props(igz_scene, REPO_ROOT)
    build_marzelvane_emitters(igz_scene)
    build_companion_boulders(igz_scene)
    build_tumbling_asteroids(igz_scene)
    build_orbital_satellites(igz_scene)
    if sky_hud:
        build_celestial_beacons(igz_scene, REPO_ROOT, radius=420.0)

    mat_cache = {}
    channel_materials: dict[str, list] = {}
    objects_by_name = {}

    for grp in igz_scene.groups:
        mesh_data = grp.mesh
        if not mesh_data.faces:
            continue

        pivot = getattr(grp, "pivot", None)
        px, py, pz = pivot if pivot is not None else (0.0, 0.0, 0.0)

        verts = []
        faces = []
        face_records = []
        for f in mesh_data.faces:
            if len(f.pts) < 3:
                continue
            start_idx = len(verts)
            if pivot is not None:
                verts.extend((vx - px, vy - py, vz - pz) for (vx, vy, vz) in f.pts)
            else:
                verts.extend(f.pts)
            faces.append(list(range(start_idx, start_idx + len(f.pts))))
            face_records.append(f)

        bmesh_data = bpy.data.meshes.new(grp.name)
        bobj = bpy.data.objects.new(grp.name, bmesh_data)
        if pivot is not None:
            bobj.location = (px, py, pz)
        bpy.context.collection.objects.link(bobj)
        bmesh_data.from_pydata(verts, [], faces)

        local_mat_map = {}
        uv_layer = bmesh_data.uv_layers.new(name="UVMap")
        basalt_vgroup = bobj.vertex_groups.new(name="Basalt_Rock_Verts")
        basalt_vert_weights: dict[int, float] = {}

        for poly_idx, f in enumerate(face_records):
            if poly_idx >= len(bmesh_data.polygons):
                break
            bmat = build_blender_material(f.attrs, mat_cache, channel_materials, grp.name)
            if bmat.name not in local_mat_map:
                local_mat_map[bmat.name] = len(bmesh_data.materials)
                bmesh_data.materials.append(bmat)
            poly = bmesh_data.polygons[poly_idx]
            poly.material_index = local_mat_map[bmat.name]

            f_rough = float(f.attrs.get("roughness", 0.5))
            f_metal = float(f.attrs.get("metallic", 0.2))
            f_emissive = bool(f.attrs.get("emissive", False))
            is_rock_grp = any(k in grp.name for k in ("Basalt", "Boulder", "Asteroid"))
            f_is_basalt = is_rock_grp and (not f_emissive) and ("texture" not in f.attrs) and f_rough >= 0.85 and f_metal <= 0.15

            if "texture" in f.attrs and len(poly.loop_indices) == 4:
                quad_uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
                for loop_idx, uv in zip(poly.loop_indices, quad_uvs):
                    uv_layer.data[loop_idx].uv = uv
            else:
                # World-scale triplanar UV mapping (11.5m per tile) so basalt columns & crags
                # wrap horizontal cooling joints along Z and planar fracture caps across X/Y
                nx, ny, nz = poly.normal.x, poly.normal.y, poly.normal.z
                uv_scale = 11.5
                for loop_idx in poly.loop_indices:
                    v_idx = bmesh_data.loops[loop_idx].vertex_index
                    vx, vy, vz = verts[v_idx]
                    wx, wy, wz = vx + px, vy + py, vz + pz
                    if f_is_basalt:
                        # Taper displacement weight near the top foundation pad so buildings sit flush
                        if wz > -0.8 and math.hypot(wx, wy) < 22.0:
                            basalt_vert_weights[v_idx] = 0.18
                        else:
                            basalt_vert_weights[v_idx] = 1.0
                    if abs(nz) >= 0.68:
                        u_coord = wx / uv_scale
                        v_coord = wy / uv_scale
                    elif abs(nx) >= abs(ny):
                        u_coord = wy / uv_scale
                        v_coord = wz / uv_scale
                    else:
                        u_coord = wx / uv_scale
                        v_coord = wz / uv_scale
                    uv_layer.data[loop_idx].uv = (u_coord, v_coord)

        bmesh_data.update()
        if basalt_vert_weights:
            for v_idx, w_val in basalt_vert_weights.items():
                basalt_vgroup.add([v_idx], w_val, "REPLACE")

            # Subdivide basalt prism faces with SIMPLE subdivision (preserving sharp 3/5/6-sided edges)
            # and apply 3D continuous rock displacement so faces and silhouettes are physically craggy!
            sub_mod = bobj.modifiers.new(name="Basalt_Simple_Subdiv", type="SUBSURF")
            sub_mod.subdivision_type = "SIMPLE"
            sub_mod.levels = 2
            sub_mod.render_levels = 2

            for axis_idx, (axis_name, n_scale, strength) in enumerate(
                [("X", 2.6, 0.46), ("Y", 2.6, 0.46), ("Z", 1.65, 0.34)]
            ):
                tex_name = f"GOR9_Basalt_Crag_{axis_name}"
                dtex = bpy.data.textures.get(tex_name)
                if dtex is None:
                    dtex = bpy.data.textures.new(name=tex_name, type="CLOUDS")
                    dtex.noise_scale = n_scale
                    dtex.noise_depth = 6
                    if hasattr(dtex, "nabla"):
                        dtex.nabla = 0.03 + axis_idx * 0.01
                disp_mod = bobj.modifiers.new(name=f"Basalt_Crag_{axis_name}", type="DISPLACE")
                disp_mod.texture = dtex
                disp_mod.direction = axis_name
                disp_mod.texture_coords = "GLOBAL"
                disp_mod.mid_level = 0.5
                disp_mod.strength = strength
                disp_mod.vertex_group = "Basalt_Rock_Verts"

        objects_by_name[grp.name] = bobj

    return objects_by_name, channel_materials


def setup_world_and_lighting(sky_hud: bool = False) -> dict[str, bpy.types.Object]:
    """
    Create the Oort Cloud Sector 9 Celestial Sphere World Shader using our
    8192x4096 equirectangular environment texture (`celestial_sky_clean.png`)
    and lock the primary directional Sun lamp to Sol's exact Oort-Cloud vector
    (`Az = 212.4°, El = +22.4°`, m = -3.62).
    """
    world = bpy.data.worlds.new("GOR9_DeepSpace_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out_node = nodes.new(type="ShaderNodeOutputWorld")
    out_node.location = (520, 0)

    bg_node = nodes.new(type="ShaderNodeBackground")
    bg_node.location = (280, 0)
    bg_node.inputs["Strength"].default_value = 1.95
    links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])

    sky_filename = "celestial_sky_annotated.png" if sky_hud else "celestial_sky_clean.png"
    sky_tex_path = SCRIPT_DIR / "renders" / sky_filename

    if sky_tex_path.exists():
        env_tex = nodes.new(type="ShaderNodeTexEnvironment")
        env_tex.location = (-120, 120)
        env_tex.image = bpy.data.images.load(str(sky_tex_path), check_existing=True)
        links.new(env_tex.outputs["Color"], bg_node.inputs["Color"])
    else:
        bg_node.inputs["Color"].default_value = (0.02, 0.04, 0.08, 1.0)

    lights_by_name: dict[str, bpy.types.Object] = {}

    # 1. SOL AT 42,100 AU (m = -3.62): Crisp Directional Starlight at Az = 212.4°, El = +22.4°
    sol_origin = bpy.data.objects.new("Sol_Target_Origin", None)
    sol_origin.location = (0.0, 0.0, BOOTH_Z)
    bpy.context.collection.objects.link(sol_origin)

    sun_data = bpy.data.lights.new(name="Sol_Oort_Star_Light", type="SUN")
    sun_data.energy = 3.9
    sun_data.color = (1.0, 0.96, 0.86)
    if hasattr(sun_data, "angle"):
        sun_data.angle = math.radians(0.12)
    sun_obj = bpy.data.objects.new(name="Sol_Oort_Star_Light", object_data=sun_data)
    sun_obj.location = az_el_to_xyz(212.4, 22.4, 420.0)
    bpy.context.collection.objects.link(sun_obj)
    sun_track = sun_obj.constraints.new(type="TRACK_TO")
    sun_track.target = sol_origin
    sun_track.track_axis = "TRACK_NEGATIVE_Z"
    sun_track.up_axis = "UP_Y"
    lights_by_name["Sol_Oort_Star_Light"] = sun_obj

    # 2. Galactic Core / Pulsar Rim Fill Light from ENE/SE (Az = 68°, El = +24°) to rake across the sheer East basalt cliff!
    fill_data = bpy.data.lights.new(name="Galactic_Core_Fill", type="SUN")
    fill_data.energy = 1.75
    fill_data.color = (0.72, 0.88, 1.0)
    fill_data.use_shadow = False
    fill_obj = bpy.data.objects.new(name="Galactic_Core_Fill", object_data=fill_data)
    fill_obj.location = az_el_to_xyz(68.0, 24.0, 420.0)
    bpy.context.collection.objects.link(fill_obj)
    fill_track = fill_obj.constraints.new(type="TRACK_TO")
    fill_track.target = sol_origin
    fill_track.track_axis = "TRACK_NEGATIVE_Z"
    fill_track.up_axis = "UP_Y"
    lights_by_name["Galactic_Core_Fill"] = fill_obj

    # 3. Chasm & Ventral Keel Starlight Bounce Fill (from SE below horizon so the 52m basalt cliff & keel are richly lit)
    keel_data = bpy.data.lights.new(name="Asteroid_Keel_Fill", type="SUN")
    keel_data.energy = 0.85
    keel_data.color = (0.52, 0.70, 0.92)
    keel_data.use_shadow = False
    keel_obj = bpy.data.objects.new(name="Asteroid_Keel_Fill", object_data=keel_data)
    keel_obj.location = az_el_to_xyz(118.0, -28.0, 420.0)
    bpy.context.collection.objects.link(keel_obj)
    keel_track = keel_obj.constraints.new(type="TRACK_TO")
    keel_track.target = sol_origin
    keel_track.track_axis = "TRACK_NEGATIVE_Z"
    keel_track.up_axis = "UP_Y"
    lights_by_name["Asteroid_Keel_Fill"] = keel_obj

    # 4. Point Lights for Animatable Station Landmarks & Booth Console Task Lighting
    point_specs = [
        ("Marzelvane_Crown_Light", (0.0, 0.0, MARZEL_Z + 1.2), (0.22, 0.92, 1.0), 18000.0),
        ("Spire_Beacon_Light", (0.0, 0.0, SPIRE_TOP_Z + 0.6), (0.55, 0.96, 1.0), 6500.0),
        ("Waveguide_Pulse_Light", (0.0, 0.0, 6.0), (0.25, 0.95, 1.0), 8500.0),
        ("Booth_Interior_Warm_Light", (0.0, 0.0, BOOTH_Z + 3.4), (1.0, 0.02, 0.008), 3200.0),
        ("Booth_Watchroom_NE", (3.8, 3.8, BOOTH_Z + 2.8), (1.0, 0.02, 0.008), 1800.0),
        ("Booth_Watchroom_NW", (-3.8, 3.8, BOOTH_Z + 2.8), (1.0, 0.02, 0.008), 1800.0),
        ("Booth_Watchroom_SW", (-3.8, -3.8, BOOTH_Z + 2.8), (1.0, 0.02, 0.008), 1800.0),
        ("Booth_Watchroom_SE", (3.8, -3.8, BOOTH_Z + 2.8), (1.0, 0.02, 0.008), 1800.0),
        # Warm tungsten-amber console gooseneck & studio track task lights (casting crisp shadows on brass, steel & leather)
        ("Booth_North_Desk_Task", (0.12, 3.65, BOOTH_Z + 1.88), (1.0, 0.74, 0.46), 280.0),
        ("Booth_Console_Task_NE", (2.85, 2.85, BOOTH_Z + 1.88), (1.0, 0.68, 0.40), 190.0),
        ("Booth_Console_Task_NW", (-2.85, 2.85, BOOTH_Z + 1.88), (1.0, 0.68, 0.40), 170.0),
        ("Booth_Console_Task_E", (3.85, 0.0, BOOTH_Z + 1.88), (1.0, 0.64, 0.36), 150.0),
        ("Booth_Console_Task_W", (-3.85, 0.0, BOOTH_Z + 1.88), (1.0, 0.64, 0.36), 120.0),
        ("Booth_Core_Cyan_Light", (0.0, 0.0, BOOTH_Z + 2.2), (0.22, 0.92, 1.0), 220.0),
        ("Cliff_Face_UpLight", (24.0, -6.0, -22.0), (0.42, 0.76, 1.0), 18000.0),
        ("Reactor_Yard_Light", (-15.0, 11.8, 3.8), (1.0, 0.50, 0.10), 4200.0),
        ("Habitat_Quonset_Light", (-14.8, -6.2, 3.2), (1.0, 0.55, 0.14), 2400.0),
        ("ORS351_Spot_Light", (351.0, -251.0, 57.5), (0.75, 0.92, 1.0), 1200.0),
    ]
    for name, loc, col, energy in point_specs:
        pdata = bpy.data.lights.new(name=name, type="POINT")
        pdata.energy = energy
        pdata.color = col
        is_desk_task = "Task" in name
        pdata.shadow_soft_size = 0.22 if is_desk_task else 1.5
        pdata.use_shadow = name in ("Marzelvane_Crown_Light", "Booth_Interior_Warm_Light", "Booth_North_Desk_Task")
        pobj = bpy.data.objects.new(name=name, object_data=pdata)
        pobj.location = loc
        bpy.context.collection.objects.link(pobj)
        lights_by_name[name] = pobj

    return lights_by_name


def _keyframe_channel(
    channel_materials: dict[str, list],
    channel_name: str,
    keyframes: list[tuple[int, float, float]],
):
    entries = channel_materials.get(channel_name, [])
    keep_dark_base = channel_name in (
        "sign_glow",
        "sign_core_glow",
        "sign_cyan_glow",
        "sign_cyan_core",
        "booth_glow",
        "booth_window_glow",
        "booth_wall_glow",
        "booth_ceiling_glow",
    )
    for _bmat, bsdf, base_rgb in entries:
        r0, g0, b0 = base_rgb
        em_in = bsdf.inputs.get("Emission Strength")
        col_in = bsdf.inputs.get("Base Color")
        em_col_in = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        for frame, strength, cscale in keyframes:
            if em_in is not None:
                em_in.default_value = float(strength)
                em_in.keyframe_insert(data_path="default_value", frame=frame)
            if col_in is not None and not keep_dark_base:
                col_in.default_value = (
                    min(1.0, r0 * cscale),
                    min(1.0, g0 * cscale),
                    min(1.0, b0 * cscale),
                    1.0,
                )
                col_in.keyframe_insert(data_path="default_value", frame=frame)
            if em_col_in is not None:
                em_col_in.default_value = (
                    min(1.0, r0 * max(0.25, cscale)),
                    min(1.0, g0 * max(0.25, cscale)),
                    min(1.0, b0 * max(0.25, cscale)),
                    1.0,
                )
                em_col_in.keyframe_insert(data_path="default_value", frame=frame)


def _keyframe_light_energy(
    lights_by_name: dict[str, bpy.types.Object],
    light_name: str,
    keyframes: list[tuple[int, float]],
):
    lobj = lights_by_name.get(light_name)
    if not lobj or not lobj.data:
        return
    ldata = lobj.data
    for frame, energy in keyframes:
        ldata.energy = float(energy)
        ldata.keyframe_insert(data_path="energy", frame=frame)


def animate_station_elements(
    objects_by_name: dict[str, bpy.types.Object],
    channel_materials: dict[str, list],
    lights_by_name: dict[str, bpy.types.Object],
    total_frames: int,
):
    def f_at(norm_t: float) -> int:
        return max(1, min(total_frames, int(round(1 + norm_t * (total_frames - 1)))))

    marzel_obj = objects_by_name.get("07_Marzelvane_Emitters_And_Spire") or objects_by_name.get("Marzelvane_Emitters")
    if marzel_obj:
        marzel_obj.rotation_mode = "XYZ"
        marzel_obj.rotation_euler = (0.0, 0.0, 0.0)
        marzel_obj.keyframe_insert(data_path="rotation_euler", frame=1)
        marzel_obj.rotation_euler = (0.0, 0.0, math.radians(36.0))
        marzel_obj.keyframe_insert(data_path="rotation_euler", frame=total_frames)

    tumble_specs = [
        ("10_Tumbling_Asteroid_1", (55.0, -38.0, 72.0), (5.0, -4.0, 2.0)),
        ("11_Tumbling_Asteroid_2", (-48.0, 62.0, -54.0), (-4.5, 5.0, -2.5)),
        ("12_Tumbling_Asteroid_3", (64.0, 42.0, -68.0), (-5.0, -3.5, 2.5)),
    ]
    for obj_name, (rx_deg, ry_deg, rz_deg), (dx, dy, dz) in tumble_specs:
        aobj = objects_by_name.get(obj_name)
        if aobj:
            loc0 = tuple(aobj.location)
            aobj.rotation_mode = "XYZ"
            aobj.rotation_euler = (0.0, 0.0, 0.0)
            aobj.keyframe_insert(data_path="rotation_euler", frame=1)
            aobj.keyframe_insert(data_path="location", frame=1)

            aobj.rotation_euler = (
                math.radians(rx_deg),
                math.radians(ry_deg),
                math.radians(rz_deg),
            )
            aobj.location = (loc0[0] + dx, loc0[1] + dy, loc0[2] + dz)
            aobj.keyframe_insert(data_path="rotation_euler", frame=total_frames)
            aobj.keyframe_insert(data_path="location", frame=total_frames)

    for sat_name, drift in [
        ("13_ORS_351_Satellite", (-2.0, 1.5, 0.6)),
        ("14_Relay_Sonde_B", (4.0, -3.0, 1.2)),
    ]:
        sobj = objects_by_name.get(sat_name)
        if sobj:
            loc0 = tuple(sobj.location)
            sobj.keyframe_insert(data_path="location", frame=1)
            sobj.location = (loc0[0] + drift[0], loc0[1] + drift[1], loc0[2] + drift[2])
            sobj.keyframe_insert(data_path="location", frame=total_frames)

    # Studio ON-AIR Crimson-Red Broadcast Booth watchroom glow (calibrated for deep saturated red!)
    _keyframe_channel(
        channel_materials,
        "booth_glow",
        [
            (f_at(0.00), 1.8, 1.00),
            (f_at(0.50), 2.2, 1.00),
            (f_at(1.00), 2.0, 1.00),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "booth_wall_glow",
        [
            (f_at(0.00), 0.75, 1.00),
            (f_at(0.50), 0.95, 1.00),
            (f_at(1.00), 0.85, 1.00),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "booth_ceiling_glow",
        [
            (f_at(0.00), 1.6, 1.00),
            (f_at(0.50), 2.0, 1.00),
            (f_at(1.00), 1.8, 1.00),
        ],
    )

    _keyframe_channel(
        channel_materials,
        "hab_glow",
        [
            (f_at(0.00), 7.5, 1.00),
            (f_at(0.50), 8.5, 1.00),
            (f_at(1.00), 8.0, 1.00),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "sign_glow",
        [
            (f_at(0.00), 1.35, 1.00),
            (f_at(0.50), 1.65, 1.00),
            (f_at(1.00), 1.50, 1.00),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "sign_core_glow",
        [
            (f_at(0.00), 2.3, 1.00),
            (f_at(0.50), 2.8, 1.00),
            (f_at(1.00), 2.5, 1.00),
        ],
    )

    _keyframe_channel(
        channel_materials,
        "sign_cyan_glow",
        [
            (f_at(0.00), 2.2, 1.00),
            (f_at(0.50), 2.6, 1.00),
            (f_at(1.00), 2.4, 1.00),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "sign_cyan_core",
        [
            (f_at(0.00), 3.6, 1.00),
            (f_at(0.50), 4.2, 1.00),
            (f_at(1.00), 3.9, 1.00),
        ],
    )



    _keyframe_channel(
        channel_materials,
        "reactor_glow",
        [
            (f_at(0.00), 0.8, 0.28),
            (f_at(0.14), 16.0, 1.00),
            (f_at(0.65), 12.0, 0.90),
            (f_at(0.74), 26.0, 1.00),
            (f_at(1.00), 14.0, 0.95),
        ],
    )
    _keyframe_light_energy(
        lights_by_name,
        "Reactor_Yard_Light",
        [
            (f_at(0.00), 800.0),
            (f_at(0.14), 8500.0),
            (f_at(0.65), 5500.0),
            (f_at(0.74), 12000.0),
            (f_at(1.00), 6500.0),
        ],
    )

    _keyframe_channel(
        channel_materials,
        "waveguide_low",
        [
            (f_at(0.00), 0.15, 0.18),
            (f_at(0.08), 22.0, 1.00),
            (f_at(0.24), 8.5, 0.80),
            (f_at(0.72), 28.0, 1.00),
            (f_at(1.00), 12.0, 0.90),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "waveguide_mid",
        [
            (f_at(0.00), 0.10, 0.16),
            (f_at(0.10), 0.15, 0.18),
            (f_at(0.16), 24.0, 1.00),
            (f_at(0.32), 9.0, 0.82),
            (f_at(0.73), 30.0, 1.00),
            (f_at(1.00), 13.0, 0.90),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "waveguide_high",
        [
            (f_at(0.00), 0.10, 0.16),
            (f_at(0.16), 0.15, 0.18),
            (f_at(0.22), 26.0, 1.00),
            (f_at(0.38), 10.0, 0.85),
            (f_at(0.74), 32.0, 1.00),
            (f_at(1.00), 14.0, 0.92),
        ],
    )

    wg_light = lights_by_name.get("Waveguide_Pulse_Light")
    if wg_light and wg_light.data:
        wg_keyframes = [
            (f_at(0.00), (0.0, 0.0, 3.0), 500.0),
            (f_at(0.08), (0.0, 0.0, 18.0), 14000.0),
            (f_at(0.16), (0.0, 0.0, 44.0), 18000.0),
            (f_at(0.24), (0.0, 0.0, 71.5), 22000.0),
            (f_at(0.66), (0.0, 0.0, 32.0), 4000.0),
            (f_at(0.74), (0.0, 0.0, 72.0), 28000.0),
            (f_at(1.00), (0.0, 0.0, 58.0), 9000.0),
        ]
        for frame, loc, nrg in wg_keyframes:
            wg_light.location = loc
            wg_light.keyframe_insert(data_path="location", frame=frame)
            wg_light.data.energy = nrg
            wg_light.data.keyframe_insert(data_path="energy", frame=frame)

    ring_timings = [
        ("ring_1", 0.20, 0.25, 0.32),
        ("ring_2", 0.31, 0.36, 0.43),
        ("ring_3", 0.42, 0.47, 0.54),
        ("ring_4", 0.53, 0.58, 0.65),
    ]
    for r_chan, t_off, t_peak, t_settle in ring_timings:
        _keyframe_channel(
            channel_materials,
            r_chan,
            [
                (f_at(0.00), 0.04, 0.14),
                (f_at(t_off), 0.06, 0.15),
                (f_at(t_peak), 28.0, 1.00),
                (f_at(t_settle), 13.5, 0.88),
                (f_at(0.68), 14.0, 0.90),
                (f_at(0.76), 38.0, 1.00),
                (f_at(0.86), 16.0, 0.92),
                (f_at(0.93), 26.0, 1.00),
                (f_at(1.00), 18.5, 0.95),
            ],
        )

    _keyframe_channel(
        channel_materials,
        "spire_beacon",
        [
            (f_at(0.00), 0.08, 0.16),
            (f_at(0.62), 0.25, 0.22),
            (f_at(0.70), 42.0, 1.00),
            (f_at(0.78), 46.0, 1.00),
            (f_at(0.88), 15.0, 0.88),
            (f_at(0.94), 34.0, 1.00),
            (f_at(1.00), 20.0, 0.94),
        ],
    )
    _keyframe_light_energy(
        lights_by_name,
        "Marzelvane_Crown_Light",
        [
            (f_at(0.00), 600.0),
            (f_at(0.20), 1200.0),
            (f_at(0.25), 9500.0),
            (f_at(0.36), 17500.0),
            (f_at(0.47), 26000.0),
            (f_at(0.58), 35000.0),
            (f_at(0.76), 62000.0),
            (f_at(0.88), 28000.0),
            (f_at(0.94), 44000.0),
            (f_at(1.00), 32000.0),
        ],
    )
    _keyframe_light_energy(
        lights_by_name,
        "Spire_Beacon_Light",
        [
            (f_at(0.00), 250.0),
            (f_at(0.64), 600.0),
            (f_at(0.74), 32000.0),
            (f_at(0.86), 8000.0),
            (f_at(0.94), 24000.0),
            (f_at(1.00), 12000.0),
        ],
    )

    _keyframe_channel(
        channel_materials,
        "hazard_beacons",
        [
            (f_at(0.00), 2.5, 0.55),
            (f_at(0.18), 18.0, 1.00),
            (f_at(0.36), 2.5, 0.55),
            (f_at(0.54), 18.0, 1.00),
            (f_at(0.74), 24.0, 1.00),
            (f_at(0.88), 3.0, 0.60),
            (f_at(1.00), 16.0, 1.00),
        ],
    )
    _keyframe_channel(
        channel_materials,
        "sat_beacon",
        [
            (f_at(0.00), 18.0, 1.00),
            (f_at(0.22), 1.5, 0.35),
            (f_at(0.44), 22.0, 1.00),
            (f_at(0.66), 1.5, 0.35),
            (f_at(0.82), 26.0, 1.00),
            (f_at(1.00), 14.0, 0.90),
        ],
    )


SHOT_DEFINITIONS = {
    "chasm_basalt_cliff_hero": {
        "description": "Low-angle look-up from the Acheron Chasm showing the sheer 52m hexagonal columnar-basalt cliff wall, warm-lit Broadcast Booth, and 86.5m lighthouse tower",
        "lens": 18.0,
        "keyframes": [
            (0.0, (66.0, -46.0, -16.0), (-2.0, 1.0, 25.0)),
            (0.5, (64.0, -45.0, -14.0), (-2.0, 1.0, 26.0)),
            (1.0, (62.0, -44.0, -12.0), (-2.0, 1.0, 27.0)),
        ],
    },
    "basalt_cliff_closeup": {
        "description": "Close-up inspection of the rough-hewn 3-, 5-, and 6-sided columnar-basalt prisms, stepped horizontal chisel ledges, and vesicular rock relief on the sheer East/SE cliff",
        "lens": 28.0,
        "keyframes": [
            (0.0, (44.0, -32.0, -9.0), (-4.0, 2.0, -6.0)),
            (0.5, (42.0, -30.0, -7.5), (-4.0, 2.0, -4.5)),
            (1.0, (40.0, -28.0, -6.0), (-4.0, 2.0, -3.0)),
        ],
    },
    "power_sequence_lock": {
        "description": "Cliff-edge & Headland Base Compound view across the stepped 3/5/6-sided Macro-Pillar assemblies, warm-lit Booth, and 86.5m lighthouse",
        "lens": 18.0,
        "keyframes": [
            (0.0, (92.0, -70.0, 12.0), (-5.0, 2.0, 18.0)),
            (0.5, (90.0, -71.0, 13.0), (-5.0, 2.5, 19.0)),
            (1.0, (88.0, -72.0, 14.0), (-5.0, 3.0, 20.0)),
        ],
    },
    "booth_rooftop_sign_hero": {
        "description": "Medium close-up of the ON-AIR red Octagonal Broadcast Booth (+26.0m) and the raised 3D 'G / O / R / ◎ / 9' vertical tower sign (+37.8m..+53.4m, two letter heights above the booth roof)",
        "lens": 24.0,
        "keyframes": [
            (0.0, (34.5, -19.2, 36.5), (0.0, 0.0, 39.2)),
            (0.5, (33.0, -18.5, 37.5), (0.0, 0.0, 39.6)),
            (1.0, (31.5, -17.8, 38.5), (0.0, 0.0, 40.0)),
        ],
    },



    "satellite_pov_wide": {
        "description": "O.R.S. 351 Relay Satellite POV (~438m range, with satellite dish & bus in lower-left foreground) viewing the entire 500m-wide Columnar-Basalt Asteroid 3-5-1 & lighthouse",
        "lens": 22.0,
        "keyframes": [
            (0.0, (361.0, -250.5, 62.2), (-25.0, 15.0, -18.0)),
            (0.5, (360.0, -249.8, 62.4), (-25.0, 15.0, -17.0)),
            (1.0, (359.0, -249.1, 62.6), (-25.0, 15.0, -16.0)),
        ],
    },
    "chasm_crane_up": {
        "description": "Low-angle chasm crane-up past the sheer 52m columnar basalt cliff to the 86.5m lighthouse tower",
        "lens": 18.0,
        "keyframes": [
            (0.0, (78.0, -56.0, -22.0), (-2.0, 0.0, 4.0)),
            (0.5, (68.0, -48.0, -4.0), (0.0, 0.0, 26.0)),
            (1.0, (56.0, -38.0, 22.0), (0.0, 0.0, 52.0)),
        ],
    },
    "celestial_sweep": {
        "description": "Panoramic sweep from the NE chasm rim looking past the lighthouse toward the Distant Sun (Sol, m=-3.62 at Az 212.4°)",
        "lens": 18.0,
        "keyframes": [
            (0.0, (42.0, 52.0, 14.0), (-12.0, -24.0, 44.0)),
            (0.5, (34.0, 56.0, 18.0), (-16.0, -28.0, 52.0)),
            (1.0, (24.0, 58.0, 22.0), (-22.0, -26.0, 58.0)),
        ],
    },
    "marzelvane_orbit": {
        "description": "High-altitude orbit around the 4 concentric Marzelvane Emitter rings (+72.0m) & EVA Climb Gallery",
        "lens": 24.0,
        "keyframes": [
            (0.0, (38.0, -28.0, 60.0), (0.0, 0.0, 73.5)),
            (0.5, (20.0, -42.0, 76.0), (0.0, 0.0, 72.5)),
            (1.0, (-18.0, -38.0, 84.0), (0.0, 0.0, 71.5)),
        ],
    },
    "base_compound_flyby": {
        "description": "Tracking fly-by across the Headland Base Compound (Habitat Quonset, Reactor #2 & Chasm Winch Crane)",
        "lens": 22.0,
        "keyframes": [
            (0.0, (-36.0, -30.0, 14.0), (-8.0, 0.0, 2.0)),
            (0.5, (-10.0, -36.0, 11.0), (-5.0, 1.0, 3.0)),
            (1.0, (22.0, -32.0, 8.5), (-3.0, 0.0, 4.0)),
        ],
    },
    "booth_interior_pan": {
        "description": "Operator-level close-up pan inside the Octagonal Broadcast Booth (+26.0m) across the North Master Console, pantograph boom mic, 3D logbook, Morse key, VFO flywheel, and 19-inch equipment racks",
        "lens": 21.0,
        "keyframes": [
            (0.0, (-0.75, 2.35, BOOTH_Z + 1.56), (-0.35, 4.45, BOOTH_Z + 1.18)),
            (0.5, (0.18, 2.30, BOOTH_Z + 1.54), (-0.10, 4.45, BOOTH_Z + 1.18)),
            (1.0, (0.68, 2.38, BOOTH_Z + 1.52), (-0.05, 4.42, BOOTH_Z + 1.16)),
        ],
    },
    "booth_wide_interior": {
        "description": "Wide interior view of the Octagonal Broadcast Booth showing the North Master Broadcast Desk, NE Van Allen Bay, E Euclid Bay, corner speaker wedges, rolling stools, and lattice tower",
        "lens": 20.0,
        "keyframes": [
            (0.0, (-1.65, 2.28, BOOTH_Z + 1.82), (1.10, 3.12, BOOTH_Z + 1.24)),
            (0.5, (-1.52, 2.22, BOOTH_Z + 1.78), (1.18, 3.08, BOOTH_Z + 1.22)),
            (1.0, (-1.38, 2.16, BOOTH_Z + 1.75), (1.25, 3.04, BOOTH_Z + 1.20)),
        ],
    },
}


def setup_animated_camera(shot_name: str, frames: int) -> bpy.types.Object:
    spec = SHOT_DEFINITIONS[shot_name]

    for old_name in ("GOR9_Shot_Cam", "GOR9_Shot_Target"):
        if old_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[old_name], do_unlink=True)

    target_empty = bpy.data.objects.new("GOR9_Shot_Target", None)
    target_empty.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(target_empty)

    cam_data = bpy.data.cameras.new("GOR9_Shot_Cam")
    cam_data.lens = spec["lens"]
    cam_data.clip_start = 0.15
    cam_data.clip_end = 2500.0
    cam_obj = bpy.data.objects.new("GOR9_Shot_Cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target_empty
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    bpy.context.scene.camera = cam_obj

    for t_norm, cam_loc, tgt_loc in spec["keyframes"]:
        f = max(1, min(frames, int(round(1 + t_norm * (frames - 1)))))
        cam_obj.location = cam_loc
        cam_obj.keyframe_insert(data_path="location", frame=f)
        target_empty.location = tgt_loc
        target_empty.keyframe_insert(data_path="location", frame=f)

    return cam_obj


def configure_render_settings(width: int, height: int, fps: int, frames: int):
    scene = bpy.context.scene
    for engine_candidate in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"):
        try:
            scene.render.engine = engine_candidate
            break
        except Exception:
            continue

    # Use Khronos PBR Neutral (or Standard) instead of AgX so pure crimson red (1, 0, 0)
    # stays deep saturated red instead of shifting to AgX salmon-orange!
    if hasattr(scene, "view_settings"):
        for vt in ("Khronos PBR Neutral", "Filmic", "Standard"):
            try:
                scene.view_settings.view_transform = vt
                break
            except Exception:
                continue

    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frames

    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = 16


def encode_frames_to_mp4(frames_dir: Path, mp4_path: Path, fps: int, interpolate_fps: int = 24):
    import subprocess

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%04d.png"),
    ]
    if interpolate_fps > fps:
        cmd.extend(["-vf", f"minterpolate=fps={interpolate_fps}:mi_mode=blend"])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "16",
            str(mp4_path),
        ]
    )
    subprocess.run(cmd, check=True)
    print(f"[Blender] Encoded MP4 sequence ({fps} fps -> {max(fps, interpolate_fps)} fps) -> {mp4_path}")


def render_shot(
    shot_name: str,
    out_dir: Path,
    width: int,
    height: int,
    fps: int,
    frames: int,
    still_only: bool = False,
    still_frame: int | None = None,
    reencode_only: bool = False,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    still_path = out_dir / f"blender_{shot_name}_hero.png"

    if still_only:
        setup_animated_camera(shot_name, frames)
        configure_render_settings(width, height, fps, frames)
        scene = bpy.context.scene
        target_frame = still_frame if still_frame is not None else max(1, min(frames, int(round(1 + 0.76 * (frames - 1)))))
        scene.frame_set(target_frame)
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(still_path)
        bpy.ops.render.render(write_still=True)
        print(f"[Blender] Rendered hero still (frame {target_frame}/{frames}) -> {still_path}")
        return still_path, None

    frames_dir = out_dir / f"frames_{shot_name}"

    if not reencode_only:
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
        frames_dir.mkdir(parents=True, exist_ok=True)

        setup_animated_camera(shot_name, frames)
        configure_render_settings(width, height, fps, frames)

        scene = bpy.context.scene
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(frames_dir / "frame_")
        bpy.ops.render.render(animation=True)

    hero_frame = still_frame if still_frame is not None else max(1, min(frames, int(round(1 + 0.76 * (frames - 1)))))
    hero_png = frames_dir / f"frame_{hero_frame:04d}.png"
    if not hero_png.exists():
        hero_png = frames_dir / f"frame_{max(1, frames // 2):04d}.png"
    if hero_png.exists():
        shutil.copy2(hero_png, still_path)
        print(f"[Blender] Saved hero still (frame {hero_frame}) -> {still_path}")

    mp4_path = out_dir / f"blender_{shot_name}.mp4"
    encode_frames_to_mp4(frames_dir, mp4_path, fps=fps, interpolate_fps=24)
    return still_path, mp4_path


def main():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Render GOR-9 Blender 5.x stills & sequences")
    parser.add_argument("--shot", default="chasm_basalt_cliff_hero,power_sequence_lock,satellite_pov_wide", help="Shot name(s) or 'all'")
    parser.add_argument("--frames", type=int, default=72, help="Number of timeline frames (default 72 = 3.0s at 24 fps)")
    parser.add_argument("--fps", type=int, default=24, help="Native frames per second (default 24 fps)")
    parser.add_argument("--width", type=int, default=2560, help="Render width (default 2560 QHD)")
    parser.add_argument("--height", type=int, default=1440, help="Render height (default 1440 QHD)")
    parser.add_argument("--still-only", action="store_true", help="Render only single hero still image(s) for rapid visual tuning")
    parser.add_argument("--still-frame", type=int, default=None, help="Specific timeline frame to render in --still-only mode")
    parser.add_argument("--reencode-only", action="store_true", help="Re-encode existing PNG frames at new FPS without re-rendering")
    parser.add_argument("--sky-hud", action="store_true", help="Use annotated celestial sphere sky map with signal callsigns & reticles")
    parser.add_argument("--save-blend", default=str(SCRIPT_DIR / "gor9_tower.blend"), help="Path to save .blend file")
    args = parser.parse_args(argv)

    out_dir = SCRIPT_DIR / "renders" / "sequences"
    shots = list(SHOT_DEFINITIONS.keys()) if args.shot == "all" else [s.strip() for s in args.shot.split(",") if s.strip()]

    if args.reencode_only:
        for shot in shots:
            render_shot(shot, out_dir, args.width, args.height, args.fps, args.frames, reencode_only=True)
        return

    clear_blender_scene()
    objects_by_name, channel_materials = import_ingetrazo_scene_to_blender(sky_hud=args.sky_hud)
    lights_by_name = setup_world_and_lighting(sky_hud=args.sky_hud)
    animate_station_elements(objects_by_name, channel_materials, lights_by_name, args.frames)

    setup_animated_camera(shots[0], args.frames)
    configure_render_settings(args.width, args.height, args.fps, args.frames)
    if args.save_blend:
        blend_path = Path(args.save_blend)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        print(f"[Blender] Saved native Blender project -> {blend_path}")

    for shot in shots:
        render_shot(
            shot,
            out_dir,
            args.width,
            args.height,
            args.fps,
            args.frames,
            still_only=args.still_only,
            still_frame=args.still_frame,
        )

    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.save_blend)))


if __name__ == "__main__":
    main()
