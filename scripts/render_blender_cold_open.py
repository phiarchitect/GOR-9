#!/usr/bin/env python3
"""Render the GOR-9 Cold Open (Version 2: Blender 5.3 Eevee) synced to
`episodes/ep01_2736.305_parallelogram/audio/cam00_cold_open_mix.wav` (21.62s)
and encode to 2560x1440 QHD High@L5.1 MP4 (`gor9_cold_open_blender.mp4`)
following the GEOMETOR VIDEO_PIPELINE.md specification.

Choreography matching the WebGL Cold Open (`gor9_cold_open_webgl.mp4`):
  - Act I (0.00s .. 13.60s): Fixed dramatic view from below the basalt cliffs looking up
      0.00s .. 0.35s : Dark station in deep-space starlight
      0.35s .. 1.20s : Base compound (Reactor #2, Habitat, Pad beacons) & Tower spine power-up
      0.85s .. 2.35s : Raised 3D 'G / O / R / ◎ / 9' vertical sign animates (G -> O -> R -> ◎ -> 9 -> ALL LIT)
      2.35s .. 3.35s : 4 concentric Marzelvane Emitter rings power on in standby
      3.45s .. 4.00s : Octagonal Broadcast Booth crimson ON-AIR lights strike on
      4.18s .. 8.98s : Marzelvane Burst synced 1:1 to 1B C-Lydian Chime (Ring 1..4 -> Spire Lock & Expanding Shockwaves)
      8.98s .. 13.60s: Full Station On-Air Below-Cliff Hero Hold
  - Act II (13.60s .. 21.62s): Cut inside the refined Octagonal Broadcast Booth
      13.60s .. 17.60s: Wide Interior Booth (perimeter standup consoles, Van Allen & Hauser badges, stools)
      17.60s .. 21.62s: Operator Broadcast Desk POV (Master MK-IV console, CM-78 boom mic, logbook, Morse key)
"""

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import bpy

REPO_ROOT = Path(__file__).resolve().parent.parent
TOWER_3D_DIR = REPO_ROOT / "tower_3d"
EP_DIR = REPO_ROOT / "episodes" / "ep01_2736.305_parallelogram"
COLD_OPEN_WAV = EP_DIR / "audio" / "cam00_cold_open_mix.wav"
SLIDES_DIR = EP_DIR / "slides_cold_open_blender"
OUT_BLENDER_MP4 = EP_DIR / "gor9_cold_open_blender.mp4"
OUT_BLENDER_THUMB = EP_DIR / "gor9_cold_open_blender_thumb.jpg"

if str(TOWER_3D_DIR) not in sys.path:
    sys.path.insert(0, str(TOWER_3D_DIR))

from blender_sequence import (  # noqa: E402
    BOOTH_Z,
    MARZEL_Z,
    SPIRE_TOP_Z,
    build_blender_material,
    clear_blender_scene,
    configure_render_settings,
    import_ingetrazo_scene_to_blender,
    set_bsdf_input,
    setup_world_and_lighting,
)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge1 <= edge0:
        return 1.0 if x >= edge1 else 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def split_sign_slots_by_z(
    tower_obj: bpy.types.Object,
    mat_cache: dict,
    channel_materials: dict[str, list],
) -> None:
    """Split the vertical G / O / R / ◎ / 9 sign polygons on `04_Continuous_Tower_And_Spine`
    into 5 independent slot channels (`sign_slot_0` .. `sign_slot_4`) by their Z elevation
    (`Z = 37.8m .. 53.4m`) so the sign steps G -> O -> R -> ◎ -> 9 during power-up.
    """
    if not tower_obj or not tower_obj.data:
        return
    mesh = tower_obj.data

    # Create per-slot materials for G(0), O(1), R(2), ◎(3), 9(4)
    slot_Bounds = [
        (49.8, 56.0),  # 0: G
        (46.5, 49.8),  # 1: O
        (43.2, 46.5),  # 2: R
        (40.4, 43.2),  # 3: ◎ (Marzelvane Rings)
        (37.2, 40.4),  # 4: 9
    ]

    mat_index_by_name: dict[str, int] = {m.name: idx for idx, m in enumerate(mesh.materials) if m}

    def get_or_add_mat_index(bmat: bpy.types.Material) -> int:
        if bmat.name in mat_index_by_name:
            return mat_index_by_name[bmat.name]
        idx = len(mesh.materials)
        mesh.materials.append(bmat)
        mat_index_by_name[bmat.name] = idx
        return idx

    slot_mats = {}
    for s_idx in range(5):
        face_m = build_blender_material(
            {"color": (1.00, 0.002, 0.001), "emissive": True, "light_channel": f"sign_slot_{s_idx}_face"},
            mat_cache,
            channel_materials,
            "Sign_Slot",
        )
        core_m = build_blender_material(
            {"color": (1.00, 0.005, 0.001), "emissive": True, "light_channel": f"sign_slot_{s_idx}_core"},
            mat_cache,
            channel_materials,
            "Sign_Slot",
        )
        cyan_g = build_blender_material(
            {"color": (0.02, 0.72, 1.00), "emissive": True, "light_channel": f"sign_slot_{s_idx}_cyan_glow"},
            mat_cache,
            channel_materials,
            "Sign_Slot",
        )
        cyan_c = build_blender_material(
            {"color": (0.35, 0.92, 1.00), "emissive": True, "light_channel": f"sign_slot_{s_idx}_cyan_core"},
            mat_cache,
            channel_materials,
            "Sign_Slot",
        )
        slot_mats[s_idx] = {
            "face": get_or_add_mat_index(face_m),
            "core": get_or_add_mat_index(core_m),
            "cyan_glow": get_or_add_mat_index(cyan_g),
            "cyan_core": get_or_add_mat_index(cyan_c),
        }

    for poly in mesh.polygons:
        if poly.material_index >= len(mesh.materials):
            continue
        cur_mat = mesh.materials[poly.material_index]
        if not cur_mat:
            continue
        mname = cur_mat.name
        if not any(tag in mname for tag in ("sign_glow", "sign_core_glow", "sign_cyan_glow", "sign_cyan_core")):
            continue
        zc = poly.center.z
        # Skip the full-height vertical border bars (which span z_bot..z_top with center ~45.6m and height > 10m)
        zs = [mesh.vertices[vi].co.z for vi in poly.vertices]
        if max(zs) - min(zs) > 6.0:
            continue
        target_slot = None
        for s_idx, (z0, z1) in enumerate(slot_Bounds):
            if z0 <= zc <= z1:
                target_slot = s_idx
                break
        if target_slot is None:
            continue
        if "sign_core_glow" in mname:
            poly.material_index = slot_mats[target_slot]["core"]
        elif "sign_glow" in mname:
            poly.material_index = slot_mats[target_slot]["face"]
        elif "sign_cyan_core" in mname:
            poly.material_index = slot_mats[target_slot]["cyan_core"]
        elif "sign_cyan_glow" in mname:
            poly.material_index = slot_mats[target_slot]["cyan_glow"]


def create_blender_shockwaves() -> tuple[list[tuple[bpy.types.Object, bpy.types.Node]], tuple[bpy.types.Object, bpy.types.Node], tuple[bpy.types.Object, bpy.types.Node]]:
    """Create 3 high-segment expanding Cherenkov shockwave torus rings, a 3D geodesic
    wireframe energy lattice, and a spherical plasma shell at Z = MARZEL_Z (+72.0m).
    """
    shockwaves = []
    ring_tilts = [
        (0.0, 0.0, 0.0),
        (math.radians(14.0), math.radians(-10.0), 0.0),
        (math.radians(-12.0), math.radians(15.0), 0.0),
    ]
    for idx in range(3):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=1.0,
            minor_radius=0.014,
            major_segments=128,
            minor_segments=20,
            location=(0.0, 0.0, MARZEL_Z),
            rotation=ring_tilts[idx],
        )
        sw_obj = bpy.context.active_object
        sw_obj.name = f"GOR9_Shockwave_Ring_{idx}"

        bmat = bpy.data.materials.new(name=f"GOR9_Shockwave_Mat_{idx}")
        bmat.use_nodes = True
        if hasattr(bmat, "blend_method"):
            bmat.blend_method = "BLEND"
        if hasattr(bmat, "surface_render_method"):
            bmat.surface_render_method = "BLENDED"
        nodes = bmat.node_tree.nodes
        links = bmat.node_tree.links
        nodes.clear()
        out_n = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], out_n.inputs["Surface"])
        set_bsdf_input(bsdf, ["Base Color"], (0.0, 0.0, 0.0, 1.0))
        set_bsdf_input(bsdf, ["Specular IOR Level", "Specular"], 0.0)
        set_bsdf_input(bsdf, ["Roughness"], 1.0)
        ring_col = (0.45, 0.96, 1.0, 1.0) if idx == 0 else (0.18, 0.88, 1.0, 1.0)
        set_bsdf_input(bsdf, ["Emission Color", "Emission"], ring_col)
        set_bsdf_input(bsdf, ["Emission Strength"], 0.0)
        set_bsdf_input(bsdf, ["Alpha"], 0.0)
        sw_obj.data.materials.append(bmat)
        sw_obj.hide_render = True
        shockwaves.append((sw_obj, bsdf))

    # Geodesic Wireframe Barycentric Wavefront Lattice (crisp 3D spherical lattice wave)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=3,
        radius=1.0,
        location=(0.0, 0.0, MARZEL_Z),
    )
    wf_obj = bpy.context.active_object
    wf_obj.name = "GOR9_Burst_Wireframe_Sphere"
    wf_mod = wf_obj.modifiers.new(name="Burst_Lattice_Wire", type="WIREFRAME")
    wf_mod.thickness = 0.0085
    if hasattr(wf_mod, "use_even_offset"):
        wf_mod.use_even_offset = False
    wf_mat = bpy.data.materials.new(name="GOR9_Burst_Wire_Mat")
    wf_mat.use_nodes = True
    if hasattr(wf_mat, "blend_method"):
        wf_mat.blend_method = "BLEND"
    if hasattr(wf_mat, "surface_render_method"):
        wf_mat.surface_render_method = "BLENDED"
    nodes = wf_mat.node_tree.nodes
    links = wf_mat.node_tree.links
    nodes.clear()
    out_n = nodes.new(type="ShaderNodeOutputMaterial")
    wf_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    links.new(wf_bsdf.outputs["BSDF"], out_n.inputs["Surface"])
    set_bsdf_input(wf_bsdf, ["Base Color"], (0.0, 0.0, 0.0, 1.0))
    set_bsdf_input(wf_bsdf, ["Specular IOR Level", "Specular"], 0.0)
    set_bsdf_input(wf_bsdf, ["Roughness"], 1.0)
    set_bsdf_input(wf_bsdf, ["Emission Color", "Emission"], (0.30, 0.94, 1.0, 1.0))
    set_bsdf_input(wf_bsdf, ["Emission Strength"], 0.0)
    set_bsdf_input(wf_bsdf, ["Alpha"], 0.0)
    wf_obj.data.materials.append(wf_mat)
    wf_obj.hide_render = True

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64,
        ring_count=32,
        radius=1.0,
        location=(0.0, 0.0, MARZEL_Z),
    )
    sp_obj = bpy.context.active_object
    sp_obj.name = "GOR9_Burst_Sphere"
    sp_mat = bpy.data.materials.new(name="GOR9_Burst_Sphere_Mat")
    sp_mat.use_nodes = True
    if hasattr(sp_mat, "blend_method"):
        sp_mat.blend_method = "BLEND"
    if hasattr(sp_mat, "surface_render_method"):
        sp_mat.surface_render_method = "BLENDED"
    nodes = sp_mat.node_tree.nodes
    links = sp_mat.node_tree.links
    nodes.clear()
    out_n = nodes.new(type="ShaderNodeOutputMaterial")
    sp_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    links.new(sp_bsdf.outputs["BSDF"], out_n.inputs["Surface"])
    set_bsdf_input(sp_bsdf, ["Base Color"], (0.0, 0.0, 0.0, 1.0))
    set_bsdf_input(sp_bsdf, ["Specular IOR Level", "Specular"], 0.0)
    set_bsdf_input(sp_bsdf, ["Roughness"], 1.0)
    set_bsdf_input(sp_bsdf, ["Emission Color", "Emission"], (0.20, 0.88, 1.0, 1.0))
    set_bsdf_input(sp_bsdf, ["Emission Strength"], 0.0)
    set_bsdf_input(sp_bsdf, ["Alpha"], 0.0)
    sp_obj.data.materials.append(sp_mat)
    sp_obj.hide_render = True

    return shockwaves, (sp_obj, sp_bsdf), (wf_obj, wf_bsdf)


def set_channel_state(
    channel_materials: dict[str, list],
    channel_name: str,
    strength: float,
    cscale: float = 1.0,
) -> None:
    keep_dark_base = any(
        k in channel_name
        for k in ("sign_", "booth_glow", "booth_window_glow", "booth_wall_glow", "booth_ceiling_glow")
    )
    is_off = strength <= 0.001
    for _bmat, bsdf, base_rgb in channel_materials.get(channel_name, []):
        r0, g0, b0 = base_rgb
        em_in = bsdf.inputs.get("Emission Strength")
        col_in = bsdf.inputs.get("Base Color")
        em_col_in = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if em_in is not None:
            em_in.default_value = 0.0 if is_off else float(strength)
        if col_in is not None:
            if keep_dark_base or is_off:
                col_in.default_value = (0.015, 0.015, 0.018, 1.0)
            else:
                col_in.default_value = (
                    min(1.0, r0 * cscale),
                    min(1.0, g0 * cscale),
                    min(1.0, b0 * cscale),
                    1.0,
                )
        if em_col_in is not None:
            if is_off:
                em_col_in.default_value = (0.0, 0.0, 0.0, 1.0)
            else:
                em_col_in.default_value = (
                    min(1.0, r0 * max(0.15, cscale)),
                    min(1.0, g0 * max(0.15, cscale)),
                    min(1.0, b0 * max(0.15, cscale)),
                    1.0,
                )


def set_light_energy(lights_by_name: dict[str, bpy.types.Object], name: str, energy: float) -> None:
    lobj = lights_by_name.get(name)
    if lobj and lobj.data:
        lobj.data.energy = float(energy)


def set_blender_state_at_time(
    t: float,
    cam_obj: bpy.types.Object,
    target_empty: bpy.types.Object,
    channel_materials: dict[str, list],
    lights_by_name: dict[str, bpy.types.Object],
    shockwaves: list,
    burst_sphere: tuple,
    burst_wireframe: tuple,
) -> None:
    """Set the exact deterministic Blender scene state at timestamp `t` (seconds)."""
    # ── 0. CAMERA CHOREOGRAPHY ──
    # Act I (0.00s .. 13.60s): Fixed dramatic view from below the basalt cliffs looking up
    #   Framed with a 16.0mm wide-angle lens and Z=+31.5m target so the full +86.0m spire,
    #   all 4 Marzelvane rings, the expanding Cherenkov burst sphere, the raised +37.8m..+53.4m
    #   G/O/R/◎/9 sign, the Octagonal Booth, and the craggy basalt cliff have generous headroom.
    # Act II (13.60s .. 21.62s): Cut inside the refined Octagonal Broadcast Booth
    is_interior = t >= 13.60
    if not is_interior:
        cam_obj.location = (74.0, -52.0, -14.0)
        target_empty.location = (-2.0, 1.0, 31.5)
        cam_obj.data.lens = 16.0
    elif t < 17.60:
        # Wide Interior Booth (North Master Desk, NE Van Allen Bay, E Euclid Bay, rolling stools, center column)
        p_pan = smoothstep(13.60, 17.60, t)
        cam_obj.location = (
            -1.65 + (1.38 - 1.65) * (-p_pan),
            2.28 + (2.16 - 2.28) * p_pan,
            BOOTH_Z + 1.80,
        )
        target_empty.location = (1.15, 3.08, BOOTH_Z + 1.22)
        cam_obj.data.lens = 20.0
    else:
        # Operator Broadcast Desk POV (Master MK-IV console, CM-78 boom mic, 3D logbook, Morse key, Hauser badge)
        p_pov = smoothstep(17.60, 21.62, t)
        cam_obj.location = (
            -0.35 + 0.55 * p_pov,
            2.34,
            BOOTH_Z + 1.54,
        )
        target_empty.location = (-0.10, 4.44, BOOTH_Z + 1.17)
        cam_obj.data.lens = 21.0

    # Prevent Eevee shadow buffer overflow (2048 max) by only casting shadows from relevant lights per act
    scene = bpy.context.scene
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 8 if is_interior else 4
    crown_light = lights_by_name.get("Marzelvane_Crown_Light")
    if crown_light and crown_light.data:
        crown_light.data.use_shadow = not is_interior
    warm_light = lights_by_name.get("Booth_Interior_Warm_Light")
    if warm_light and warm_light.data:
        warm_light.data.use_shadow = False

    # ── 1. DARK STATION -> BASE COMPOUND & TOWER SPINE POWER-UP (t = 0.35s .. 1.20s) ──
    p_tower = smoothstep(0.35, 1.20, t)
    set_channel_state(channel_materials, "reactor_glow", 0.0 if t < 0.35 else (0.4 + 15.6 * p_tower), 0.2 + 0.8 * p_tower)
    set_channel_state(channel_materials, "hab_glow", 0.0 if t < 0.35 else (0.2 + 7.8 * p_tower), 0.2 + 0.8 * p_tower)
    set_channel_state(channel_materials, "hazard_beacons", 0.3 + 15.5 * p_tower, 0.3 + 0.7 * p_tower)
    set_channel_state(channel_materials, "waveguide_low", 0.0 if t < 0.35 else (0.2 + 14.0 * p_tower), 0.2 + 0.8 * p_tower)
    set_channel_state(channel_materials, "waveguide_mid", 0.0 if t < 0.50 else (0.2 + 15.0 * smoothstep(0.50, 1.25, t)), 0.2 + 0.8 * p_tower)
    set_channel_state(channel_materials, "waveguide_high", 0.0 if t < 0.65 else (0.2 + 16.0 * smoothstep(0.65, 1.35, t)), 0.2 + 0.8 * p_tower)
    set_light_energy(lights_by_name, "Reactor_Yard_Light", 80.0 + 7500.0 * p_tower)
    set_light_energy(lights_by_name, "Habitat_Quonset_Light", 50.0 + 2400.0 * p_tower)
    set_light_energy(lights_by_name, "Waveguide_Pulse_Light", 60.0 + 9500.0 * p_tower)

    # ── 2. RAISED VERTICAL 'G / O / R / ◎ / 9' SIGN ANIMATES (t = 0.85s .. 2.35s) ──
    # Unlit slots have exact 0.0 emission so each letter (G -> O -> R -> ◎ -> 9) ignites cleanly in sequence!
    if t < 0.85:
        set_channel_state(channel_materials, "sign_glow", 0.0, 0.0)
        set_channel_state(channel_materials, "sign_core_glow", 0.0, 0.0)
        set_channel_state(channel_materials, "sign_cyan_glow", 0.0, 0.0)
        set_channel_state(channel_materials, "sign_cyan_core", 0.0, 0.0)
        for s_idx in range(5):
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_face", 0.0, 0.0)
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_core", 0.0, 0.0)
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_glow", 0.0, 0.0)
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_core", 0.0, 0.0)
    elif t < 2.35:
        seq_phase = (t - 0.85) / 0.30
        active_step = min(4, int(math.floor(seq_phase)))
        sub_p = seq_phase - active_step
        pulse = 0.92 + 0.18 * math.sin(sub_p * math.pi)
        # Keep the full-height vertical side rails dark until all 5 slots finish stepping at 2.35s
        set_channel_state(channel_materials, "sign_glow", 0.0, 0.0)
        set_channel_state(channel_materials, "sign_core_glow", 0.0, 0.0)
        for s_idx in range(5):
            if s_idx > active_step:
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_face", 0.0, 0.0)
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_core", 0.0, 0.0)
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_glow", 0.0, 0.0)
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_core", 0.0, 0.0)
            else:
                b = pulse if s_idx == active_step else 0.90
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_face", 2.20 * b, b)
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_core", 3.80 * b, b)
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_glow", 3.10 * b, b)
                set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_core", 5.20 * b, b)
    else:
        set_channel_state(channel_materials, "sign_glow", 2.10, 1.0)
        set_channel_state(channel_materials, "sign_core_glow", 3.60, 1.0)
        set_channel_state(channel_materials, "sign_cyan_glow", 3.10, 1.0)
        set_channel_state(channel_materials, "sign_cyan_core", 5.20, 1.0)
        for s_idx in range(5):
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_face", 2.10, 1.0)
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_core", 3.60, 1.0)
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_glow", 3.10, 1.0)
            set_channel_state(channel_materials, f"sign_slot_{s_idx}_cyan_core", 5.20, 1.0)

    # ── 3. MARZELVANE POWER ON (2.35s .. 3.35s) & 5. MARZELVANE BURST ON 1B CHIME (4.18s .. 9.20s) ──
    chime_start = 4.18
    spire_lock_time = 5.02
    burst_end = 9.20
    climax_flash = 0.0
    if chime_start <= t <= burst_end and t >= spire_lock_time - 0.04:
        rise = smoothstep(spire_lock_time - 0.04, spire_lock_time + 0.16, t)
        dt_after = max(0.0, t - (spire_lock_time + 0.16))
        fall = math.exp(-dt_after / 1.85) * (1.0 - smoothstep(8.20, burst_end, t))
        climax_flash = rise * fall

    total_ring_energy = 0.0
    for r_idx in range(4):
        p_standby = smoothstep(2.35 + r_idx * 0.16, 2.75 + r_idx * 0.16, t)
        ring_charge = 0.0
        ign_flash = 0.0
        if chime_start <= t <= burst_end:
            t_note = chime_start + r_idx * 0.20
            t_full = t_note + 0.18
            ramp = smoothstep(t_note, t_full, t)
            dt_hold = max(0.0, t - spire_lock_time)
            cool = math.exp(-dt_hold / (2.0 + r_idx * 0.20)) * (1.0 - smoothstep(8.20, burst_end, t))
            ring_charge = ramp * cool
            if t_note <= t <= t_full + 0.28:
                ign_flash = math.sin(smoothstep(t_note, t_full + 0.28, t) * math.pi)
        e = min(1.6, ring_charge + 0.75 * ign_flash + 0.90 * climax_flash)
        total_ring_energy += e
        if t < 2.35 + r_idx * 0.16:
            set_channel_state(channel_materials, f"ring_{r_idx + 1}", 0.0, 0.0)
        else:
            strength = 12.0 * p_standby + 28.0 * ring_charge + 22.0 * ign_flash + 32.0 * climax_flash
            cscale = max(0.25, min(1.0, 0.25 + 0.65 * p_standby + 0.50 * e))
            set_channel_state(channel_materials, f"ring_{r_idx + 1}", strength, cscale)

    p_marzel_master = smoothstep(2.35, 3.30, t)
    mean_ring_energy = total_ring_energy * 0.25
    spire_strength = 0.0 if t < 2.35 else (14.0 * p_marzel_master + 20.0 * mean_ring_energy + 42.0 * climax_flash)
    set_channel_state(channel_materials, "spire_beacon", spire_strength, max(0.20, p_marzel_master))
    set_light_energy(
        lights_by_name,
        "Marzelvane_Crown_Light",
        100.0 + 16000.0 * p_marzel_master + 28000.0 * mean_ring_energy + 55000.0 * climax_flash,
    )
    set_light_energy(
        lights_by_name,
        "Spire_Beacon_Light",
        50.0 + 6000.0 * p_marzel_master + 14000.0 * mean_ring_energy + 32000.0 * climax_flash,
    )

    # Expanding Barycentric Shockwave Rings, Geodesic Lattice & Spherical Shell (t >= 5.02s)
    for sw_idx, (sw_obj, sw_bsdf) in enumerate(shockwaves):
        sw_start = spire_lock_time + sw_idx * 0.42
        sw_dur = 3.05
        if sw_start <= t <= sw_start + sw_dur:
            p = (t - sw_start) / sw_dur
            ease_out = 1.0 - math.pow(1.0 - p, 1.65)
            rad = 4.5 + 56.0 * ease_out
            sw_obj.hide_render = False
            sw_obj.scale = (rad, rad, rad * 0.42)
            sw_obj.location = (0.0, 0.0, MARZEL_Z + (sw_idx - 0.5) * 3.2 * p)
            env = math.sin(p * math.pi) * math.pow(1.0 - p, 0.72)
            alpha = min(0.92, env * 0.88)
            set_bsdf_input(sw_bsdf, ["Alpha"], alpha)
            set_bsdf_input(sw_bsdf, ["Emission Strength"], 36.0 * env)
        else:
            sw_obj.hide_render = True
            set_bsdf_input(sw_bsdf, ["Alpha"], 0.0)
            set_bsdf_input(sw_bsdf, ["Emission Strength"], 0.0)

    sp_obj, sp_bsdf = burst_sphere
    wf_obj, wf_bsdf = burst_wireframe
    if spire_lock_time <= t <= spire_lock_time + 3.20:
        sp_p = (t - spire_lock_time) / 3.20
        sp_rad = 5.0 + 52.0 * (1.0 - math.pow(1.0 - sp_p, 1.65))
        sp_env = math.sin(sp_p * math.pi) * math.pow(1.0 - sp_p, 0.95)
        sp_obj.hide_render = False
        sp_obj.scale = (sp_rad, sp_rad, sp_rad * 0.62)
        sp_alpha = sp_env * 0.22
        set_bsdf_input(sp_bsdf, ["Alpha"], sp_alpha)
        set_bsdf_input(sp_bsdf, ["Emission Strength"], 18.0 * sp_env)

        wf_obj.hide_render = False
        wf_obj.scale = (sp_rad * 1.02, sp_rad * 1.02, sp_rad * 0.64)
        wf_obj.rotation_euler = (0.15 * sp_p, -0.22 * sp_p, 0.45 * sp_p)
        set_bsdf_input(wf_bsdf, ["Alpha"], min(0.85, sp_env * 0.78))
        set_bsdf_input(wf_bsdf, ["Emission Strength"], 28.0 * sp_env)
    else:
        sp_obj.hide_render = True
        set_bsdf_input(sp_bsdf, ["Alpha"], 0.0)
        set_bsdf_input(sp_bsdf, ["Emission Strength"], 0.0)
        wf_obj.hide_render = True
        set_bsdf_input(wf_bsdf, ["Alpha"], 0.0)
        set_bsdf_input(wf_bsdf, ["Emission Strength"], 0.0)

    # ── 4. BROADCAST BOOTH 'ON AIR' RED LIGHTS STRIKE ON (t = 3.45s .. 3.95s) ──
    p_on_air = smoothstep(3.45, 3.95, t)
    if 3.48 <= t <= 3.68:
        p_on_air = min(1.25, p_on_air + 0.35 * math.sin(((t - 3.48) / 0.20) * math.pi))
    if t < 3.45:
        set_channel_state(channel_materials, "booth_glow", 0.0, 0.0)
        set_channel_state(channel_materials, "booth_wall_glow", 0.0, 0.0)
        set_channel_state(channel_materials, "booth_ceiling_glow", 0.0, 0.0)
        set_light_energy(lights_by_name, "Booth_Interior_Warm_Light", 0.0)
        for w_name in ("Booth_Watchroom_NE", "Booth_Watchroom_NW", "Booth_Watchroom_SW", "Booth_Watchroom_SE"):
            set_light_energy(lights_by_name, w_name, 0.0)
    elif not is_interior:
        # Exterior below-cliff view: strong crimson beacon glow through the octagonal windows
        set_channel_state(channel_materials, "booth_glow", 2.25 * p_on_air, min(1.0, p_on_air))
        set_channel_state(channel_materials, "booth_wall_glow", 0.90 * p_on_air, min(1.0, p_on_air))
        set_channel_state(channel_materials, "booth_ceiling_glow", 1.90 * p_on_air, min(1.0, p_on_air))
        set_light_energy(lights_by_name, "Booth_Interior_Warm_Light", 3200.0 * p_on_air)
        for w_name in ("Booth_Watchroom_NE", "Booth_Watchroom_NW", "Booth_Watchroom_SW", "Booth_Watchroom_SE"):
            set_light_energy(lights_by_name, w_name, 1800.0 * p_on_air)
    else:
        # Interior Broadcast Booth view: balanced warm studio task lights + subtle crimson watchroom rim
        # so the CRT monitors, brass Hauser & Van Allen plates, CM-78 mic, and starry windows are crystal clear!
        set_channel_state(channel_materials, "booth_glow", 1.15, 0.85)
        set_channel_state(channel_materials, "booth_wall_glow", 0.28, 0.65)
        set_channel_state(channel_materials, "booth_ceiling_glow", 0.95, 0.80)
        set_light_energy(lights_by_name, "Booth_Interior_Warm_Light", 140.0)
        for w_name in ("Booth_Watchroom_NE", "Booth_Watchroom_NW", "Booth_Watchroom_SW", "Booth_Watchroom_SE"):
            set_light_energy(lights_by_name, w_name, 85.0)
        set_light_energy(lights_by_name, "Booth_North_Desk_Task", 380.0)
        set_light_energy(lights_by_name, "Booth_Console_Task_NE", 260.0)
        set_light_energy(lights_by_name, "Booth_Console_Task_NW", 240.0)
        set_light_energy(lights_by_name, "Booth_Console_Task_E", 210.0)
        set_light_energy(lights_by_name, "Booth_Console_Task_W", 180.0)
        set_light_energy(lights_by_name, "Booth_Core_Cyan_Light", 310.0)


def _build_blender_cold_open_steps(burst_fps: int = 24) -> list[tuple[float, float, str]]:
    """Build deterministic Cold Open steps for Blender."""
    steps: list[tuple[float, float, str]] = [
        (0.15, 0.40, "000: Dark station in deep-space starlight"),
        (0.60, 0.25, "001: Base compound & Reactor #2 power-up"),
        (0.80, 0.25, "002: Tower climb spine full power"),
        (1.00, 0.30, "003: Sign Step 1 [G]"),
        (1.30, 0.30, "004: Sign Step 2 [G · O]"),
        (1.60, 0.30, "005: Sign Step 3 [G · O · R]"),
        (1.90, 0.30, "006: Sign Step 4 [G · O · R · ◎]"),
        (2.20, 0.30, "007: Sign Step 5 [G · O · R · ◎ · 9]"),
        (2.55, 0.45, "008: Full GOR-9 Sign locked + Inner Marzelvane rings power on"),
        (3.05, 0.55, "009: All 4 Marzelvane rings powered on in standby"),
        (3.58, 0.30, "010: Octagonal Broadcast Booth crimson ON AIR strike peak"),
        (3.95, 0.48, "011: Octagonal Broadcast Booth crimson ON AIR steady"),
    ]
    dt = 1.0 / float(burst_fps)
    num_burst_frames = int(round(4.80 * burst_fps))
    for i in range(num_burst_frames):
        t_sample = round(4.18 + i * dt, 5)
        steps.append((t_sample, round(dt, 6), f"Burst frame {i + 1:03d} (t={t_sample:.3f}s)"))
    steps.extend(
        [
            (9.50, 4.62, "Full Station On-Air Below-Cliff Hero Hold"),
            (14.20, 2.00, "Interior Broadcast Booth Wide — Van Allen & Hauser Consoles (1)"),
            (16.20, 2.00, "Interior Broadcast Booth Wide — Van Allen & Hauser Consoles (2)"),
            (18.20, 2.00, "Interior Operator Broadcast Desk POV — CM-78 Mic, Logbook & Hauser Badge (1)"),
            (20.20, 2.02, "Interior Operator Broadcast Desk POV — CM-78 Mic, Logbook & Hauser Badge (2)"),
        ]
    )
    return steps


def assemble_concat_qhd_mp4(
    slide_pngs: list[Path],
    durations: list[float],
    audio_wav: Path,
    out_mp4: Path,
) -> None:
    concat_file = out_mp4.parent / f"_{out_mp4.stem}_concat.txt"
    lines = []
    total_dur = 0.0
    for png, dur in zip(slide_pngs, durations):
        d = max(0.01, dur)
        total_dur += d
        lines.append(f"file '{png.resolve()}'")
        lines.append(f"duration {d:.6f}")
    lines.append(f"file '{slide_pngs[-1].resolve()}'")
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    cmd = [
        "/usr/bin/ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(audio_wav),
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-b:a",
        "192k",
        "-shortest",
        "-t",
        f"{total_dur:.3f}",
        "-vsync",
        "vfr",
        "-c:v",
        "libx264",
        "-crf",
        "16",
        "-preset",
        "slow",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True)
    print(f"[Blender Cold Open] Encoded 2560x1440 QHD High@L5.1 MP4 -> {out_mp4}")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Render GOR-9 Blender 5.3 Cold Open")
    parser.add_argument("--test-frames", action="store_true", help="Render 6 diagnostic frames only")
    parser.add_argument("--burst-fps", type=int, default=24, help="FPS during the 4.8s Marzelvane burst (default 24)")
    parser.add_argument("--width", type=int, default=1920, help="Render width (upscaled with lanczos to 2560)")
    parser.add_argument("--height", type=int, default=1080, help="Render height (upscaled with lanczos to 1440)")
    parser.add_argument("--clean", action="store_true", help="Clear existing rendered frames")
    args = parser.parse_args(argv)

    t0 = time.time()
    clear_blender_scene()
    objects_by_name, channel_materials = import_ingetrazo_scene_to_blender(sky_hud=False)
    lights_by_name = setup_world_and_lighting(sky_hud=False)

    # Optimize basalt subdivision render level to 1 for fast multi-frame animation rendering
    for obj in objects_by_name.values():
        for mod in obj.modifiers:
            if mod.type == "SUBSURF":
                mod.levels = 1
                mod.render_levels = 1

    # Split vertical sign into 5 independently addressable slots (G, O, R, ◎, 9)
    mat_cache: dict = {}
    tower_obj = objects_by_name.get("04_Continuous_Tower_And_Spine")
    if tower_obj:
        split_sign_slots_by_z(tower_obj, mat_cache, channel_materials)

    shockwaves, burst_sphere, burst_wireframe = create_blender_shockwaves()

    # Create camera & target empty
    target_empty = bpy.data.objects.new("GOR9_ColdOpen_Target", None)
    bpy.context.collection.objects.link(target_empty)
    cam_data = bpy.data.cameras.new("GOR9_ColdOpen_Cam")
    cam_data.lens = 16.0
    cam_data.clip_start = 0.15
    cam_data.clip_end = 2500.0
    cam_obj = bpy.data.objects.new("GOR9_ColdOpen_Cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target_empty
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    bpy.context.scene.camera = cam_obj

    configure_render_settings(args.width, args.height, 30, 1)
    scene = bpy.context.scene
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 8
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 15

    if args.test_frames:
        test_dir = EP_DIR / "previews" / "cold_open_blender_test"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_times = [0.15, 1.30, 3.85, 5.45, 14.50, 18.50]
        for idx, t_val in enumerate(test_times):
            f_start = time.time()
            set_blender_state_at_time(
                t_val,
                cam_obj,
                target_empty,
                channel_materials,
                lights_by_name,
                shockwaves,
                burst_sphere,
                burst_wireframe,
            )
            out_png = test_dir / f"frame_{idx:04d}.png"
            scene.render.filepath = str(out_png)
            bpy.ops.render.render(write_still=True)
            print(f"  [Blender test] frame {idx + 1}/{len(test_times)} (t={t_val:.2f}s) in {time.time() - f_start:.2f}s -> {out_png.name}")
        return

    steps = _build_blender_cold_open_steps(burst_fps=args.burst_fps)
    if args.clean and SLIDES_DIR.exists():
        shutil.rmtree(SLIDES_DIR, ignore_errors=True)
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)

    slide_pngs: list[Path] = []
    durations: list[float] = []
    for idx, (t_val, dur, desc) in enumerate(steps):
        out_png = SLIDES_DIR / f"frame_{idx:04d}.png"
        slide_pngs.append(out_png)
        durations.append(dur)
        if out_png.exists():
            continue
        f_start = time.time()
        set_blender_state_at_time(
            t_val,
            cam_obj,
            target_empty,
            channel_materials,
            lights_by_name,
            shockwaves,
            burst_sphere,
            burst_wireframe,
        )
        scene.render.filepath = str(out_png)
        bpy.ops.render.render(write_still=True)
        if (idx + 1) % 10 == 0 or idx == len(steps) - 1:
            print(
                f"  [Blender Cold Open] {idx + 1}/{len(steps)} (t={t_val:.2f}s, {time.time() - f_start:.2f}s/f, elapsed={time.time() - t0:.1f}s)"
            )

    assemble_concat_qhd_mp4(slide_pngs, durations, COLD_OPEN_WAV, OUT_BLENDER_MP4)
    # Export custom thumbnail from the Marzelvane burst climax frame (t ~ 5.5s -> idx ~ 42)
    thumb_src = slide_pngs[min(len(slide_pngs) - 1, 42)]
    subprocess.run(
        ["/usr/bin/ffmpeg", "-y", "-i", str(thumb_src), "-q:v", "4", str(OUT_BLENDER_THUMB)],
        check=True,
    )
    print(f"[Blender Cold Open] Exported thumbnail -> {OUT_BLENDER_THUMB}")


if __name__ == "__main__":
    main()
