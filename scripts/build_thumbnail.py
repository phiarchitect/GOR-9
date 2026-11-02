#!/usr/bin/env python3
"""Parameterized YouTube Thumbnail Generator & Branding Template for GOR-9.

Produces series-consistent 16:9 YouTube thumbnails (1920x1080 <2MB JPG + 2560x1440 master)
with locked GOR-9 station branding (ON AIR pill, GOR-9 callsign header, frequency pill,
episode number badge, high-contrast headline typography, and geometric/camera inset).

Usage:
  python scripts/build_thumbnail.py
  python scripts/build_thumbnail.py --ep "02" --line1 "BASE-EIGHT" --line2 "DUMPLING STATION" --tag "TROJAN L4 • 6,440 kHz"
"""

import argparse
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PLATES_DIR = ROOT / "assets" / "plates"
COMP_DIR = ROOT / "assets" / "composited"
RENDERS_DIR = ROOT / "renders"

W, H = 1920, 1080


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def build_tower_composite(target_w: int, target_h: int) -> Image.Image:
    """Composite the cliff-edge concentric-ring tower over the ringed-planet cosmic sky."""
    sky = Image.open(PLATES_DIR / "cam00_sky_plate_clean.jpg").convert("RGB").resize(
        (target_w, target_h), Image.Resampling.LANCZOS
    )
    sky_crop = np.asarray(sky, dtype=np.float32).copy()

    # Composite main-belt asteroid sprites onto the deep-space galactic sky
    for sp_idx, sz, rx, ry, br in [
        (4, (130, 115), 0.14, 0.24, 0.80),
        (2, (165, 134), 0.78, 0.15, 0.82),
        (1, (68, 68), 0.22, 0.43, 0.72),
    ]:
        sp_path = COMP_DIR / f"asteroid_sprite_{sp_idx}.png"
        if sp_path.exists():
            sp_img = Image.open(sp_path).convert("RGBA").resize(sz, Image.Resampling.LANCZOS)
            sp_arr = np.asarray(sp_img, dtype=np.float32)
            sp_a = sp_arr[..., 3:4] / 255.0
            sp_pre = sp_arr[..., :3] * sp_a * br
            ax, ay = int(target_w * rx), int(target_h * ry)
            if ax + sz[0] <= target_w and ay + sz[1] <= target_h:
                roi = sky_crop[ay:ay + sz[1], ax:ax + sz[0]]
                sky_crop[ay:ay + sz[1], ax:ax + sz[0]] = roi * (1.0 - sp_a) + sp_pre

    fg_off = Image.open(COMP_DIR / "cam00_tower_fg_off.png").convert("RGBA").resize(
        (target_w, target_h), Image.Resampling.LANCZOS
    )
    rings = Image.open(COMP_DIR / "cam00_tower_rings_only.png").convert("RGBA").resize(
        (target_w, target_h), Image.Resampling.LANCZOS
    )
    beacons = Image.open(COMP_DIR / "cam00_tower_beacons_only.png").convert("RGBA").resize(
        (target_w, target_h), Image.Resampling.LANCZOS
    )

    fg_arr = np.asarray(fg_off, dtype=np.float32)
    a_off = fg_arr[..., 3:4] / 255.0
    comp = sky_crop * (1.0 - a_off) + fg_arr[..., :3] * a_off

    r_arr = np.asarray(rings, dtype=np.float32)
    a_r = r_arr[..., 3:4] / 255.0
    comp = np.clip(comp + r_arr[..., :3] * a_r * 1.15, 0.0, 255.0)

    b_arr = np.asarray(beacons, dtype=np.float32)
    a_b = b_arr[..., 3:4] / 255.0
    comp = np.clip(comp + b_arr[..., :3] * a_b * 1.25, 0.0, 255.0)
    return Image.fromarray(comp.astype(np.uint8), mode="RGB")


def draw_euclid_overlay(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, fonts: dict) -> None:
    """Draw the luminous Euclid I.34 (G.47) Parallelogram vector construction with equality ticks."""
    # Parallelogram vertices relative to (cx, cy)
    pA = (int(cx - 170 * scale), int(cy - 115 * scale))
    pB = (int(cx + 210 * scale), int(cy - 115 * scale))
    pC = (int(cx - 225 * scale), int(cy + 115 * scale))
    pD = (int(cx + 155 * scale), int(cy + 115 * scale))

    # Diameter BC in Solar Gold (#e8b85a)
    draw.line([pB, pC], fill=(232, 184, 90), width=max(4, int(7 * scale)))

    # Outer parallelogram walls in Steel Blue / Assertion Green
    for p1, p2 in [(pA, pB), (pC, pD)]:
        draw.line([p1, p2], fill=(96, 165, 250), width=max(4, int(7 * scale)))
    for p1, p2 in [(pA, pC), (pB, pD)]:
        draw.line([p1, p2], fill=(56, 189, 248), width=max(4, int(7 * scale)))

    # Green equality ticks on AB / CD (single tick) and AC / BD (double tick)
    for m_x, m_y in [((pA[0] + pB[0]) // 2, (pA[1] + pB[1]) // 2), ((pC[0] + pD[0]) // 2, (pC[1] + pD[1]) // 2)]:
        draw.line([m_x, m_y - int(18 * scale), m_x, m_y + int(18 * scale)], fill=(94, 194, 126), width=5)

    for m_x, m_y in [((pA[0] + pC[0]) // 2, (pA[1] + pC[1]) // 2), ((pB[0] + pD[0]) // 2, (pB[1] + pD[1]) // 2)]:
        for off in (-7, 7):
            draw.line([m_x - int(16 * scale), m_y + off, m_x + int(16 * scale), m_y + off], fill=(94, 194, 126), width=4)

    # Vertex points & labels
    for pt, lbl, ox, oy in [(pA, "A", -28, -34), (pB, "B", 14, -34), (pC, "C", -30, 8), (pD, "D", 14, 8)]:
        r = max(6, int(9 * scale))
        draw.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=(232, 184, 90), outline=(8, 11, 18), width=2)
        draw.text((pt[0] + ox, pt[1] + oy), lbl, font=fonts["v_lbl"], fill=(255, 255, 255))


def draw_brand_frame(
    canvas: Image.Image,
    ep_num: str,
    freq_str: str,
    line1: str,
    line2: str,
    sub_tag: str,
    fonts: dict,
) -> None:
    """Apply the locked GOR-9 series branding header, episode badge, and bottom headline block."""
    d = ImageDraw.Draw(canvas, "RGBA")

    # 1. Outer Broadcast Bezel Border
    d.rectangle([0, 0, W - 1, H - 1], outline=(232, 184, 90, 220), width=6)
    d.rectangle([10, 10, W - 11, H - 11], outline=(56, 189, 248, 140), width=2)

    # 2. Top-Left Locked Series Brand Header Bar
    d.rectangle([28, 28, 1120, 118], fill=(8, 11, 18, 235), outline=(232, 184, 90, 255), width=3)
    # ON AIR red badge
    d.rectangle([48, 46, 212, 100], fill=(244, 63, 94, 55), outline=(244, 63, 94, 255), width=3)
    d.ellipse([66, 62, 88, 84], fill=(244, 63, 94, 255))
    d.text((98, 55), "ON AIR", font=fonts["pill"], fill=(255, 200, 210, 255))

    # GOR-9 Station Call
    d.text((234, 42), "GOR-9 • GALACTIC OUTPOST RADIO", font=fonts["brand"], fill=(232, 184, 90, 255))
    d.text((236, 82), f"ASTEROID 3-5-1 • SECTOR 9 • {freq_str}", font=fonts["sub_hdr"], fill=(56, 189, 248, 255))

    # 3. Top-Right Episode Number Pill
    d.rectangle([W - 350, 28, W - 28, 118], fill=(12, 18, 28, 238), outline=(94, 194, 126, 255), width=3)
    d.text((W - 322, 42), f"BROADCAST #{ep_num}", font=fonts["ep"], fill=(94, 194, 126, 255))
    d.text((W - 322, 82), "0400 UTC LOG", font=fonts["sub_hdr"], fill=(226, 232, 240, 255))

    # 4. Bottom Dark Gradient Scrim for Mobile-Readable Headline Typography
    scrim = Image.new("RGBA", (W, 390), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for y in range(390):
        alpha = int(242 * ((y / 390.0) ** 1.35))
        sd.line([0, y, W, y], fill=(6, 8, 14, alpha))
    canvas.paste(scrim, (0, H - 390), scrim)

    # 5. Sub-Tag Pill above Headline
    tag_w = max(460, len(sub_tag) * 19 + 54)
    d.rectangle([42, H - 310, 42 + tag_w, H - 252], fill=(14, 22, 34, 240), outline=(56, 189, 248, 255), width=3)
    d.text((66, H - 297), sub_tag, font=fonts["tag"], fill=(56, 189, 248, 255))

    # 6. Two-Line High-Impact Thumbnail Headline (with dark drop-shadow stroke)
    for ox, oy in [(-4, 4), (4, 4), (-3, -3), (3, -3), (0, 5)]:
        d.text((42 + ox, H - 238 + oy), line1, font=fonts["h1_top"], fill=(4, 6, 10, 255))
        d.text((42 + ox, H - 134 + oy), line2, font=fonts["h1_bot"], fill=(4, 6, 10, 255))

    d.text((42, H - 238), line1, font=fonts["h1_top"], fill=(248, 250, 252, 255))
    d.text((42, H - 134), line2, font=fonts["h1_bot"], fill=(232, 184, 90, 255))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GOR-9 branded YouTube thumbnails.")
    parser.add_argument("--ep", default="01", help="Episode number badge")
    parser.add_argument("--freq", default="14,285.7 kHz USB", help="Station frequency string")
    parser.add_argument("--line1", default="THE UNSUSPECTING", help="Primary headline line 1 (White)")
    parser.add_argument("--line2", default="PARALLELOGRAM", help="Primary headline line 2 (Solar Gold)")
    parser.add_argument(
        "--tag",
        default="EUCLID I.34 (G.47) • CALLISTO BRINE VAT 19",
        help="Accent telemetry pill above headline",
    )
    args = parser.parse_args()

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)

    fonts = {
        "brand": load_font(34, bold=True),
        "ep": load_font(32, bold=True),
        "pill": load_font(26, bold=True),
        "sub_hdr": load_font(20, bold=True),
        "tag": load_font(26, bold=True),
        "h1_top": load_font(84, bold=True),
        "h1_bot": load_font(96, bold=True),
        "v_lbl": load_font(26, bold=True),
        "card_hdr": load_font(22, bold=True),
    }

    tower_comp = build_tower_composite(W, H)
    vat_img = Image.open(PLATES_DIR / "cam_vat19_parallelogram.jpg").convert("RGB")

    # =========================================================================
    # VARIANT A: Split-Screen ("Outpost Tower + Vat 19 Euclid I.34 Scope Card")
    # =========================================================================
    thumb_a = tower_comp.copy()

    # Right-side framed Forensic Scope Card (x: 1120..1884, y: 144..880)
    card_w, card_h = 764, 736
    vat_resized = vat_img.resize((card_w, card_h), Image.Resampling.LANCZOS)
    vat_arr = np.asarray(vat_resized, dtype=np.float32) * 0.78
    vat_card = Image.fromarray(vat_arr.astype(np.uint8), mode="RGB")

    thumb_a.paste(vat_card, (1120, 144))
    da = ImageDraw.Draw(thumb_a, "RGBA")
    da.rectangle([1120, 144, 1884, 880], outline=(56, 189, 248, 255), width=4)
    da.rectangle([1120, 144, 1884, 198], fill=(10, 15, 24, 235), outline=(56, 189, 248, 255), width=2)
    da.text((1144, 158), "CAM-VAT19 • EUCLID SIGNAL DETECTOR (I.34)", font=fonts["card_hdr"], fill=(232, 184, 90, 255))

    # Overlay glowing Euclid I.34 Parallelogram aligned with the Vat 19 salt-crust card
    draw_euclid_overlay(da, cx=1502, cy=528, scale=0.95, fonts=fonts)

    # Draw locked series branding & headline
    draw_brand_frame(thumb_a, args.ep, args.freq, args.line1, args.line2, args.tag, fonts)

    path_a = RENDERS_DIR / "gor9_ep01_thumbnail_split.jpg"
    thumb_a.save(path_a, quality=93)
    print(f"Saved Split Thumbnail: {path_a} ({path_a.stat().st_size // 1024} KB)")

    # =========================================================================
    # VARIANT B: Full-Bleed Tower Outpost + Floating Cosmic Euclid Radar Scope
    # =========================================================================
    thumb_b = tower_comp.copy()
    db = ImageDraw.Draw(thumb_b, "RGBA")

    # Circular / Octagonal HUD Scope in the upper-right nebula sky (center: 1470, 460)
    scx, scy, sr = 1470, 465, 295
    db.ellipse([scx - sr - 10, scy - sr - 10, scx + sr + 10, scy + sr + 10], fill=(8, 12, 20, 195), outline=(232, 184, 90, 240), width=4)
    db.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], outline=(56, 189, 248, 180), width=2)
    db.line([scx - sr, scy, scx + sr, scy], fill=(56, 189, 248, 70), width=1)
    db.line([scx, scy - sr, scx, scy + sr], fill=(56, 189, 248, 70), width=1)

    draw_euclid_overlay(db, cx=scx + 10, cy=scy + 5, scale=1.08, fonts=fonts)
    db.text((scx - 165, scy - sr + 28), "EUCLID-9 • PROP. I.34", font=fonts["card_hdr"], fill=(94, 194, 126, 255))
    db.text((scx - 145, scy + sr - 54), "Δθ = 0.0002 ARCSEC", font=fonts["card_hdr"], fill=(232, 184, 90, 255))

    draw_brand_frame(thumb_b, args.ep, args.freq, args.line1, args.line2, args.tag, fonts)

    path_b = RENDERS_DIR / "gor9_ep01_thumbnail_tower.jpg"
    thumb_b.save(path_b, quality=93)
    print(f"Saved Tower Thumbnail: {path_b} ({path_b.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
