"""
Procedural Seamless Columnar-Basalt PBR Texture Generator (2048x2048)
=====================================================================
Synthesizes four tileable 2048x2048 PBR texture maps for Asteroid 3-5-1's
columnar-basalt cliffs, upland mesas, and chasm monoliths:
  1. `basalt_diffuse.jpg` / `.png`:
     - Deep volcanic charcoal-slate basalt matrix with granular plagioclase,
       pyroxene, and olivine mineral speckle, stepped horizontal cooling-joint
       chisel ledges, and micro-cavity shading inside vesicular gas pits
       (zero artificial spiderweb outlines).
  2. `basalt_normal.jpg` / `.png`:
     - High-contrast 2048x2048 tangent-space normal map encoding tilted hackly
       rock cleavage chips, sawtooth horizontal chisel-mark cooling ledges,
       deep vesicular gas-pocket craters, and high-frequency volcanic grit.
  3. `basalt_bump.jpg` / `.png`:
     - Multi-scale heightfield encoding stepped horizontal fracture shelves,
       hackly spalled rock flakes, and vesicular scoria cavities.
  4. `basalt_roughness.jpg` / `.png`:
     - Micro-surface roughness map with specular-catching cleaved crystal
       facets (0.40-0.56) and matte pitted stone cavities (0.88-0.98).
"""

from pathlib import Path
import numpy as np


def _tileable_fbm(
    res: int,
    octaves: list[tuple[int, float, float]],
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Generate seamless tileable 2D anisotropic fractal noise via FFT synthesis.
    Each octave is `(freq_u, freq_v, amp)`.
    """
    acc = np.zeros((res, res), dtype=np.float32)
    ky = np.fft.fftfreq(res) * res
    kx = np.fft.fftfreq(res) * res
    KX, KY = np.meshgrid(kx, ky)

    for fu, fv, amp in octaves:
        su = max(1.0, float(fu) * 0.65)
        sv = max(1.0, float(fv) * 0.65)
        r2 = (KX / su) ** 2 + (KY / sv) ** 2
        ring = np.exp(-0.5 * r2) * ((KX * KX + KY * KY) > 0)
        phases = rng.uniform(0.0, 2.0 * np.pi, size=(res, res)).astype(np.float32)
        spec = ring * (np.cos(phases) + 1j * np.sin(phases))
        field = np.fft.ifft2(spec).real.astype(np.float32)
        std = float(np.std(field)) or 1.0
        acc += (field / std) * amp

    mn, mx = float(acc.min()), float(acc.max())
    return (acc - mn) / max(1e-6, mx - mn)


def _tileable_hackly_facets(
    res: int,
    n_cells: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute seamless toroidal Voronoi rock-chip terraces with per-facet planar
    tilt slopes so each spalled rock flake has a distinct 3D cleavage plane
    without dark spiderweb outlines.
    Returns `(f1_norm, edge_norm, tilted_height)` in `[0, 1]`.
    """
    pts = rng.uniform(0.0, 1.0, size=(n_cells, 2)).astype(np.float32)
    cell_elev = rng.uniform(0.0, 1.0, size=(n_cells,)).astype(np.float32)
    cell_slope_u = rng.uniform(-3.2, 3.2, size=(n_cells,)).astype(np.float32)
    cell_slope_v = rng.uniform(-3.2, 3.2, size=(n_cells,)).astype(np.float32)

    work_res = min(res, 512)
    u = np.linspace(0.0, 1.0, work_res, endpoint=False, dtype=np.float32)
    U, V = np.meshgrid(u, u)

    f1 = np.full((work_res, work_res), 1e9, dtype=np.float32)
    f2 = np.full((work_res, work_res), 1e9, dtype=np.float32)
    best_id = np.zeros((work_res, work_res), dtype=np.int32)
    best_du = np.zeros((work_res, work_res), dtype=np.float32)
    best_dv = np.zeros((work_res, work_res), dtype=np.float32)

    for idx in range(n_cells):
        px, py = pts[idx]
        du = U - px
        du = np.where(du > 0.5, du - 1.0, np.where(du < -0.5, du + 1.0, du))
        dv = V - py
        dv = np.where(dv > 0.5, dv - 1.0, np.where(dv < -0.5, dv + 1.0, dv))
        d = np.sqrt(du * du + dv * dv)

        mask1 = d < f1
        f2 = np.where(mask1, f1, np.minimum(f2, d))
        f1 = np.where(mask1, d, f1)
        best_id = np.where(mask1, idx, best_id)
        best_du = np.where(mask1, du, best_du)
        best_dv = np.where(mask1, dv, best_dv)

    edge = f2 - f1
    edge_norm = np.clip(edge / max(1e-6, float(np.percentile(edge, 95))), 0.0, 1.0)
    f1_norm = np.clip(f1 / max(1e-6, float(np.percentile(f1, 95))), 0.0, 1.0)

    # Tilted cleavage plane per rock chip: base elevation + planar tilt across the chip
    tilt_h = (
        cell_elev[best_id]
        + cell_slope_u[best_id] * best_du
        + cell_slope_v[best_id] * best_dv
    )
    t_min, t_max = float(np.percentile(tilt_h, 1.0)), float(np.percentile(tilt_h, 99.0))
    tilt_h = np.clip((tilt_h - t_min) / max(1e-6, t_max - t_min), 0.0, 1.0)

    if work_res != res:
        # Smooth bilinear upsampling via FFT or separable linear interpolation so facet planes stay crisp
        scale = res // work_res
        f1_norm = np.repeat(np.repeat(f1_norm, scale, axis=0), scale, axis=1)
        edge_norm = np.repeat(np.repeat(edge_norm, scale, axis=0), scale, axis=1)
        tilt_h = np.repeat(np.repeat(tilt_h, scale, axis=0), scale, axis=1)

    return f1_norm, edge_norm, tilt_h


def _save_qimage_rgb(arr_uint8: np.ndarray, paths: list[Path], quality: int = 95):
    from PySide6.QtGui import QImage

    h, w, _ = arr_uint8.shape
    contig = np.ascontiguousarray(arr_uint8)
    qimg = QImage(contig.data, w, h, w * 3, QImage.Format.Format_RGB888)
    for p in paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        qimg.save(str(p), None, quality)


def generate_basalt_textures(repo_root: Path, res: int = 2048) -> dict[str, Path]:
    """Generate seamless 2048x2048 diffuse, normal, bump, and roughness maps for rough columnar basalt."""
    rng = np.random.default_rng(35199)

    u = np.linspace(0.0, 1.0, res, endpoint=False, dtype=np.float32)
    U, V = np.meshgrid(u, u)

    # 1. Multi-scale isotropic & anisotropic FBM rock fields
    fbm_macro = _tileable_fbm(
        res,
        [(2, 2, 1.0), (4, 4, 0.85), (8, 8, 0.65), (16, 16, 0.45)],
        rng,
    )
    fbm_med = _tileable_fbm(
        res,
        [(12, 12, 1.0), (24, 24, 0.85), (48, 48, 0.70), (96, 96, 0.55)],
        rng,
    )
    fbm_grit = _tileable_fbm(
        res,
        [(64, 64, 1.0), (128, 128, 0.90), (256, 256, 0.78), (512, 512, 0.65), (768, 768, 0.50)],
        rng,
    )
    # Horizontal chisel-band noise (stretched horizontally along U, compressed vertically along V)
    fbm_chisel_bands = _tileable_fbm(
        res,
        [(3, 18, 1.0), (6, 36, 0.85), (12, 72, 0.65), (24, 144, 0.45)],
        rng,
    )
    # Vertical plumose fracture striae (stretched vertically along V)
    fbm_plumose = _tileable_fbm(
        res,
        [(28, 4, 1.0), (56, 8, 0.75), (112, 16, 0.55)],
        rng,
    )

    # 2. Warped Hackly Cleavage Chips (tilted stone flakes without spiderweb outlines)
    f1_meso, edge_meso, tilt_meso = _tileable_hackly_facets(res, 150, rng)
    f1_micro, edge_micro, tilt_micro = _tileable_hackly_facets(res, 480, rng)

    # Displace the Voronoi facet lookup coordinates by medium/grit FBM so chip boundaries are rough & craggy
    shift_u = ((fbm_med - 0.5) * 42.0 + (fbm_grit - 0.5) * 14.0).astype(np.int32)
    shift_v = ((fbm_macro - 0.5) * 42.0 + (fbm_grit - 0.5) * 14.0).astype(np.int32)
    iy = (np.arange(res)[:, None] + shift_v) % res
    ix = (np.arange(res)[None, :] + shift_u) % res
    warped_tilt_meso = tilt_meso[iy, ix]
    warped_tilt_micro = tilt_micro[iy, ix]
    warped_edge_meso = edge_meso[iy, ix]

    # 3. Stepped Horizontal Chisel-Mark Cooling Ledges (sawtooth volcanic cooling shelves)
    v_chisel = V + (fbm_macro - 0.5) * 0.16 + (fbm_med - 0.5) * 0.055
    chisel_phase = (v_chisel * 9.0) % 1.0
    # Sawtooth terrace step broken up laterally by fbm_macro so ledges start and stop organically
    ledge_mask = np.clip((fbm_macro - 0.25) * 1.6, 0.15, 1.0)
    sawtooth_ledge = (1.0 - np.power(chisel_phase, 0.45)) * ledge_mask
    # Sharp horizontal fracture groove at the base of each chisel step
    chisel_groove = 1.0 - 0.55 * ledge_mask * np.exp(-((chisel_phase / 0.045) ** 2))

    # 4. Dense Multi-Scale Vesicular Gas Pitting (volcanic scoria pores & spalled craters)
    pit_med_field = _tileable_fbm(res, [(45, 45, 1.0), (90, 90, 0.85), (180, 180, 0.7)], rng)
    pit_fine_field = _tileable_fbm(res, [(140, 140, 1.0), (280, 280, 0.9), (560, 560, 0.8)], rng)
    pits_med = np.where(pit_med_field < 0.28, (pit_med_field / 0.28) ** 2.2, 1.0)
    pits_fine = np.where(pit_fine_field < 0.32, (pit_fine_field / 0.32) ** 2.4, 1.0)
    vesicular_pits = 0.58 * pits_med + 0.42 * pits_fine

    # Fine hairline rock-spall cleavage cracks (subtle & sharp, not wide painted bands)
    spall_crack = 1.0 - 0.45 * np.exp(-((warped_edge_meso / 0.018) ** 2))

    # ── 5. Synthesize Master Rough Basalt Heightfield [0..1] ──
    height = (
        0.26 * warped_tilt_meso
        + 0.16 * warped_tilt_micro
        + 0.20 * fbm_chisel_bands
        + 0.14 * sawtooth_ledge
        + 0.12 * fbm_med
        + 0.12 * fbm_grit
        + 0.06 * fbm_plumose
    )
    height = height * chisel_groove * spall_crack * (0.52 + 0.48 * vesicular_pits)
    h_min, h_max = float(np.percentile(height, 0.5)), float(np.percentile(height, 99.5))
    height = np.clip((height - h_min) / max(1e-6, h_max - h_min), 0.0, 1.0)

    # ── 6. Synthesize High-Impact Tangent-Space Normal Map (2048x2048) ──
    # Combine macro chisel/ledge gradients + steep micro grit/vesicle gradients
    macro_dh_dx = (np.roll(height, -2, axis=1) - np.roll(height, 2, axis=1)) * 0.25
    macro_dh_dy = (np.roll(height, -2, axis=0) - np.roll(height, 2, axis=0)) * 0.25
    micro_surface = 0.45 * height + 0.35 * fbm_grit + 0.20 * vesicular_pits
    micro_dh_dx = (np.roll(micro_surface, -1, axis=1) - np.roll(micro_surface, 1, axis=1)) * 0.5
    micro_dh_dy = (np.roll(micro_surface, -1, axis=0) - np.roll(micro_surface, 1, axis=0)) * 0.5

    normal_strength = 18.5
    nx = -(macro_dh_dx * 0.55 + micro_dh_dx * 0.45) * normal_strength
    ny = (macro_dh_dy * 0.55 + micro_dh_dy * 0.45) * normal_strength
    nz = np.ones_like(nx)
    n_len = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx /= n_len
    ny /= n_len
    nz /= n_len

    norm_r = np.clip((nx * 0.5 + 0.5) * 255.0, 0.0, 255.0).astype(np.uint8)
    norm_g = np.clip((ny * 0.5 + 0.5) * 255.0, 0.0, 255.0).astype(np.uint8)
    norm_b = np.clip((nz * 0.5 + 0.5) * 255.0, 0.0, 255.0).astype(np.uint8)
    normal_rgb = np.stack([norm_r, norm_g, norm_b], axis=-1)

    # ── 7. Synthesize Granular Volcanic Basalt Diffuse Map (Zero Painted Spiderwebs!) ──
    # Fine salt-and-pepper mineral speckle (plagioclase laths + dark augite/magnetite + warm olivine)
    mineral_speckle = (fbm_grit - 0.5) * 28.0 + (warped_tilt_micro - 0.5) * 16.0
    cavity_ao = np.clip(0.48 + 0.52 * vesicular_pits, 0.42, 1.0) * chisel_groove * spall_crack
    ledge_highlight = np.clip((height - 0.62) / 0.38, 0.0, 1.0)
    olivine_tint = np.clip((fbm_macro - 0.55) * 2.2 * fbm_med, 0.0, 1.0)

    base_r = 30.0 + 38.0 * height + mineral_speckle + 16.0 * ledge_highlight + 14.0 * olivine_tint
    base_g = 35.0 + 43.0 * height + mineral_speckle * 1.05 + 19.0 * ledge_highlight + 9.0 * olivine_tint
    base_b = 43.0 + 52.0 * height + mineral_speckle * 1.12 + 24.0 * ledge_highlight + 3.0 * olivine_tint

    r_ch = np.clip(base_r * cavity_ao, 10.0, 148.0).astype(np.uint8)
    g_ch = np.clip(base_g * cavity_ao, 12.0, 158.0).astype(np.uint8)
    b_ch = np.clip(base_b * cavity_ao, 15.0, 176.0).astype(np.uint8)
    diffuse_rgb = np.stack([r_ch, g_ch, b_ch], axis=-1)

    # ── 8. Synthesize Bump & Roughness Maps ──
    bump_u8 = np.clip(height * 255.0, 0.0, 255.0).astype(np.uint8)
    bump_rgb = np.stack([bump_u8, bump_u8, bump_u8], axis=-1)

    rough = 0.84 - 0.32 * ledge_highlight - 0.14 * height + 0.18 * (1.0 - vesicular_pits)
    rough = np.clip(rough, 0.38, 0.98)
    rough_u8 = (rough * 255.0).astype(np.uint8)
    rough_rgb = np.stack([rough_u8, rough_u8, rough_u8], axis=-1)

    plates_dir = repo_root / "docs" / "assets" / "plates"
    renders_dir = repo_root / "tower_3d" / "renders"

    diffuse_jpg = plates_dir / "basalt_diffuse.jpg"
    normal_jpg = plates_dir / "basalt_normal.jpg"
    bump_jpg = plates_dir / "basalt_bump.jpg"
    rough_jpg = plates_dir / "basalt_roughness.jpg"

    _save_qimage_rgb(diffuse_rgb, [diffuse_jpg, renders_dir / "basalt_diffuse.png"], quality=95)
    _save_qimage_rgb(normal_rgb, [normal_jpg, renders_dir / "basalt_normal.png"], quality=95)
    _save_qimage_rgb(bump_rgb, [bump_jpg, renders_dir / "basalt_bump.png"], quality=95)
    _save_qimage_rgb(rough_rgb, [rough_jpg, renders_dir / "basalt_roughness.png"], quality=95)

    return {
        "diffuse": diffuse_jpg,
        "normal": normal_jpg,
        "bump": bump_jpg,
        "roughness": rough_jpg,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    out = generate_basalt_textures(root)
    for k, v in out.items():
        print(f"Generated {k}: {v}")
