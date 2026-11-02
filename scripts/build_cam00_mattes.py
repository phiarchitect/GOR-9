#!/usr/bin/env python3
"""Pre-compute zero-spill 2560x1440 transparent PNG foreground plates for CAM-00.

Builds the Cliff-Edge Concentric-Ring Antenna & Neon Call-Sign Outpost rig:
  - cam00_tower_fg_off.png: Zero-spill RGBA cutout of the cliff-edge tower,
    elevated booth with lone operator silhouette, dark unlit 'GOR-9' rooftop sign,
    and dark unlit radial-spoke concentric rings at the antenna apex.
  - cam00_tower_rings_only.png + cam00_ring_1..4.png: Clean RGBA layers for the
    4 glowing concentric plasma rings at the apex of the antenna so they ignite
    sequentially from inner ring to outer ring as the station powers up.
  - cam00_tower_beacons_only.png: Clean RGBA layer containing ONLY the 3 crimson
    aviation warning beacons AND the warm amber 'GOR-9' neon rooftop sign, gated
    by alpha_struct so zero background Milky Way sky ever bleeds through.
"""

import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PLATES_DIR = ROOT / "assets" / "plates"
OUT_DIR = ROOT / "assets" / "composited"
TARGET_SIZE = (2560, 1440)


def load_rgb(path: Path) -> np.ndarray:
    img = Image.open(path).convert("RGB").resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    return np.asarray(img, dtype=np.float32)


def save_straight_rgba(premult_rgb: np.ndarray, out_path: Path) -> np.ndarray:
    alpha = np.clip(np.max(premult_rgb, axis=-1) / 255.0, 0.0, 1.0)
    straight_rgb = np.clip(
        premult_rgb / np.maximum(alpha[..., None], 1e-5),
        0.0,
        255.0,
    )
    rgba = np.dstack([
        straight_rgb.astype(np.uint8),
        np.round(alpha * 255.0).astype(np.uint8),
    ])
    Image.fromarray(rgba, mode="RGBA").save(out_path, optimize=False)
    return alpha


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    on_rgb = load_rgb(PLATES_DIR / "cam00_tower_outpost_base.jpg")
    off_rgb = load_rgb(PLATES_DIR / "cam00_tower_beacons_off.jpg")
    key_rgb = load_rgb(PLATES_DIR / "cam00_tower_sky_key.jpg")

    # 1. Structural alpha from #00FF00 key plate (including open steel lattice trusses & dark apex rings)
    r_k, g_k, b_k = key_rgb[..., 0], key_rgb[..., 1], key_rgb[..., 2]
    green_excess = g_k - np.maximum(r_k, b_k)
    alpha_struct = 1.0 - np.clip((green_excess - 26.0) / 86.0, 0.0, 1.0)

    # Clean semi-transparent silhouette edges
    edge_factor = np.where(alpha_struct < 0.92, np.power(np.clip(alpha_struct, 0.0, 1.0), 0.42), 1.0)
    off_rgb_clean = np.clip(off_rgb * edge_factor[..., None], 0.0, 255.0)

    fg_off_rgba = np.dstack([
        off_rgb_clean.astype(np.uint8),
        np.round(alpha_struct * 255.0).astype(np.uint8),
    ])
    off_path = OUT_DIR / "cam00_tower_fg_off.png"
    Image.fromarray(fg_off_rgba, mode="RGBA").save(off_path, optimize=False)
    Image.fromarray(fg_off_rgba, mode="RGBA").save(OUT_DIR / "cam00_fg_dim.png", optimize=False)
    print(f"Saved {off_path} ({TARGET_SIZE[0]}x{TARGET_SIZE[1]})")

    # 2. Full luminous delta (on_rgb - off_rgb)
    delta = np.maximum(0.0, on_rgb - off_rgb)
    yy, xx = np.mgrid[0:TARGET_SIZE[1], 0:TARGET_SIZE[0]]

    # 2A. Extract the 4 glowing concentric rings at the antenna apex
    hub_cx, hub_cy = 1280.0, 288.0
    aspect = 0.395
    ell_r = np.sqrt((xx - hub_cx) ** 2 + ((yy - hub_cy) / aspect) ** 2)

    ring_disk_mask = (
        np.clip((ell_r - 150.0) / 25.0, 0.0, 1.0)
        * (1.0 - np.clip((ell_r - 485.0) / 25.0, 0.0, 1.0))
        * (yy <= 510).astype(np.float32)
    )
    ring_lum = np.max(delta, axis=-1)
    ring_gate = np.clip((ring_lum - 36.0) / 55.0, 0.0, 1.0) * ring_disk_mask
    rings_premult = np.clip(delta * ring_gate[..., None] * 1.28, 0.0, 255.0)

    rings_path = OUT_DIR / "cam00_tower_rings_only.png"
    save_straight_rgba(rings_premult, rings_path)
    print(f"Saved {rings_path}")

    # Decompose the 4 concentric apex rings by elliptical radius from hub
    band_edges = [
        ("ring_1", 150.0, 265.0),
        ("ring_2", 245.0, 335.0),
        ("ring_3", 315.0, 395.0),
        ("ring_4", 375.0, 510.0),
    ]
    ring_meta = []
    for idx, (rname, r_in, r_out) in enumerate(band_edges, start=1):
        w_in = np.clip((ell_r - (r_in - 12.0)) / 24.0, 0.0, 1.0)
        w_out = 1.0 - np.clip((ell_r - (r_out - 12.0)) / 24.0, 0.0, 1.0)
        band_mask = (w_in * w_out).astype(np.float32)
        sub_premult = rings_premult * band_mask[..., None]
        sub_path = OUT_DIR / f"cam00_{rname}.png"
        save_straight_rgba(sub_premult, sub_path)
        ring_meta.append({"id": rname, "index": idx, "r_in": r_in, "r_out": r_out, "file": sub_path.name})
        print(f"Saved {sub_path.name} (elliptical r={r_in:.0f}..{r_out:.0f})")

    # 2B. Extract ONLY the 'GOR-9' neon rooftop sign gated by alpha_struct (zero sky bleed!)
    # Search y in [640, 760], x in [1150, 1410] where alpha_struct > 0.35
    sign_zone = ((xx >= 1150) & (xx <= 1410) & (yy >= 640) & (yy <= 760)).astype(np.float32)
    warm_delta = np.maximum(delta[..., 0], delta[..., 1] * 0.95)
    # Gate by alpha_struct so background sky pixels (alpha_struct == 0) cannot bleed through
    struct_neon_gate = np.clip((warm_delta - 18.0) / 28.0, 0.0, 1.0) * np.clip(alpha_struct * 1.25, 0.0, 1.0) * sign_zone
    beacon_premult = np.clip(on_rgb * struct_neon_gate[..., None] * 1.15, 0.0, 255.0)

    # Find exact bounding box of the detected 'GOR-9' neon sign
    ys, xs = np.where(struct_neon_gate > 0.25)
    if len(xs) > 0:
        sx0, sx1 = int(np.min(xs)), int(np.max(xs))
        sy0, sy1 = int(np.min(ys)), int(np.max(ys))
    else:
        sx0, sx1, sy0, sy1 = 1205, 1358, 678, 728
    print(f"Detected GOR-9 neon pixels: x={sx0}..{sx1}, y={sy0}..{sy1}")

    # Find exact booth roof left and right corners from alpha_struct in y in [710, 790]
    roof_ys, roof_xs = np.where((alpha_struct > 0.6) & (yy >= 720) & (yy <= 775) & (xx >= 1050) & (xx <= 1510))
    if len(roof_xs) > 0:
        left_x = int(np.min(roof_xs)) + 14
        right_x = int(np.max(roof_xs)) - 14
        roof_y_left = int(np.min(yy[(alpha_struct > 0.6) & ( np.abs(xx - left_x) <= 4 ) & (yy >= 700) & (yy <= 790)]))
        roof_y_right = int(np.min(yy[(alpha_struct > 0.6) & ( np.abs(xx - right_x) <= 4 ) & (yy >= 700) & (yy <= 790)]))
    else:
        left_x, roof_y_left = 1138, 738
        right_x, roof_y_right = 1422, 738

    beacon_coords = [
        ("mast_top", 1280, 285),
        ("booth_left", left_x, roof_y_left - 4),
        ("booth_right", right_x, roof_y_right - 4),
    ]
    beacon_boxes = []
    for name, bx, by in beacon_coords:
        bdist = np.sqrt((xx - float(bx)) ** 2 + (yy - float(by)) ** 2)
        core = np.exp(-(bdist ** 2) / (2.0 * 3.8 ** 2))
        halo = 0.48 * np.exp(-(bdist ** 2) / (2.0 * 11.0 ** 2))
        outer = 0.14 * np.exp(-(bdist ** 2) / (2.0 * 22.0 ** 2))
        bglow = np.clip(core + halo + outer, 0.0, 1.0)
        beacon_premult[..., 0] = np.clip(beacon_premult[..., 0] + bglow * 255.0, 0.0, 255.0)
        beacon_premult[..., 1] = np.clip(beacon_premult[..., 1] + core * 130.0 + halo * 26.0, 0.0, 255.0)
        beacon_premult[..., 2] = np.clip(beacon_premult[..., 2] + core * 100.0 + halo * 20.0, 0.0, 255.0)
        pad = 36
        beacon_boxes.append({
            "id": name,
            "cx": bx,
            "cy": by,
            "x": bx - pad,
            "y": by - pad,
            "w": pad * 2,
            "h": pad * 2,
        })
        print(f"Beacon {name}: center=({bx}, {by})")

    beacons_path = OUT_DIR / "cam00_tower_beacons_only.png"
    alpha_beacon = save_straight_rgba(beacon_premult, beacons_path)
    print(f"Saved {beacons_path}")

    # Save full combined bright plate for cam00_fg_bright.png
    struct_premult = off_rgb_clean * alpha_struct[..., None]
    total_premult = np.clip(struct_premult + rings_premult + beacon_premult, 0.0, 255.0)
    alpha_rings = np.clip(np.max(rings_premult, axis=-1) / 255.0, 0.0, 1.0)
    alpha_total = np.clip(
        alpha_struct + np.maximum(alpha_rings, alpha_beacon) * (1.0 - alpha_struct),
        0.0,
        1.0,
    )
    straight_bright = np.clip(total_premult / np.maximum(alpha_total[..., None], 1e-5), 0.0, 255.0)
    fg_bright_rgba = np.dstack([
        straight_bright.astype(np.uint8),
        np.round(alpha_total * 255.0).astype(np.uint8),
    ])
    Image.fromarray(fg_bright_rgba, mode="RGBA").save(OUT_DIR / "cam00_fg_bright.png", optimize=False)

    # Split 'GOR-9' neon rooftop sign box into 'GOR-' (left 76%) and '9' (right 24%)
    split_x = int(sx0 + (sx1 - sx0) * 0.76)
    neon_boxes = {
        "gor_prefix": {
            "id": "gor_prefix",
            "x": sx0 - 8,
            "y": sy0 - 8,
            "w": (split_x - (sx0 - 8)),
            "h": (sy1 - sy0) + 16,
        },
        "gor_nine": {
            "id": "gor_nine",
            "x": split_x,
            "y": sy0 - 8,
            "w": (sx1 + 8) - split_x,
            "h": (sy1 - sy0) + 16,
        },
    }
    print(f"Neon GOR- prefix box: {neon_boxes['gor_prefix']}")
    print(f"Neon '9' digit box:   {neon_boxes['gor_nine']}")

    # 3. Extract the 4 RGBA asteroid sprites from asteroid_sprites_sheet_key.jpg
    ast_sheet_path = PLATES_DIR / "asteroid_sprites_sheet_key.jpg"
    asteroid_meta = []
    if ast_sheet_path.exists():
        ast_rgb = load_rgb(ast_sheet_path)
        quads = [
            (1, 0, 1280, 0, 720),
            (2, 1280, 2560, 0, 720),
            (3, 0, 1280, 720, 1440),
            (4, 1280, 2560, 720, 1440),
        ]
        for idx, qx0, qx1, qy0, qy1 in quads:
            sub = ast_rgb[qy0:qy1, qx0:qx1].copy()
            r_a, g_a, b_a = sub[..., 0], sub[..., 1], sub[..., 2]
            g_exc = g_a - np.maximum(r_a, b_a)
            a_mask = 1.0 - np.clip((g_exc - 22.0) / 80.0, 0.0, 1.0)
            # Despill green channel completely
            sub[..., 1] = np.where(g_exc > 0.0, np.maximum(r_a, b_a), g_a)
            # Darken outer 2px edge slightly for seamless deep-space compositing
            edge_f = np.where(a_mask < 0.90, np.power(np.clip(a_mask, 0.0, 1.0), 0.55), 1.0)
            sub_clean = np.clip(sub * edge_f[..., None], 0.0, 255.0)
            ays, axs = np.where(a_mask > 0.05)
            if len(axs) > 0:
                ax0 = max(0, int(np.min(axs)) - 8)
                ax1 = min(sub.shape[1], int(np.max(axs)) + 9)
                ay0 = max(0, int(np.min(ays)) - 8)
                ay1 = min(sub.shape[0], int(np.max(ays)) + 9)
                rgba_crop = np.dstack([
                    sub_clean[ay0:ay1, ax0:ax1].astype(np.uint8),
                    np.round(a_mask[ay0:ay1, ax0:ax1] * 255.0).astype(np.uint8),
                ])
                sp_path = OUT_DIR / f"asteroid_sprite_{idx}.png"
                Image.fromarray(rgba_crop, mode="RGBA").save(sp_path, optimize=False)
                asteroid_meta.append({
                    "id": f"asteroid_{idx}",
                    "file": sp_path.name,
                    "w": int(ax1 - ax0),
                    "h": int(ay1 - ay0),
                })
                print(f"Saved {sp_path.name} ({ax1 - ax0}x{ay1 - ay0})")

    with open(OUT_DIR / "cam00_beacons_meta.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "beacons": beacon_boxes,
                "neon": neon_boxes,
                "apex_rings": {
                    "hub_cx": hub_cx,
                    "hub_cy": hub_cy,
                    "aspect": aspect,
                    "bands": ring_meta,
                },
                "asteroid_sprites": asteroid_meta,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
