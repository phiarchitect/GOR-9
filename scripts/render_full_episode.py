#!/usr/bin/env python3
"""Render the complete 2560x1440 (1440p QHD) GOR-9 Episode 01 Broadcast Video.

Upgraded Multi-Panel & Shader Edition:
- Frequent panel shifts every 5-8 seconds across all 6 segments (18 distinct visual views).
- Right Column (x=1380..2510): 3 stacked TV-readable Topic Cards where ONLY the active
  spoken topic is highlighted (with a live plasma/scanline card shader and neon border),
  synchronized with the Left Viewport switching to a dedicated indicator/shader/video panel.
- Featured Station & Remote Camera Video Insert System:
  - Checks `assets/flow/<clip>.mp4` placeholder slots first; falls back to animated
    Start/End keyframe camera feeds (`cam02_relay_storm`, `cam44k_quarry`, `cam_n24_shallows`,
    `cam_sw4_bazaar`, `cam00c_barracks`, `cam_vat19_parallelogram`) enhanced with real-time
    NumPy pixel shaders.
- 10 Vectorized NumPy Pixel Shaders:
  1. Magnetospheric Bow-Shock & Solar Wind Plasma Shader (METEO-9 Panel 1A)
  2. 60 kV Triboelectric Lightning & Chromatic Aberration Shader (METEO-9 Panel 1B)
  3. 6-Hydrocoptic Marzelvane #4 Rotor Phase-Wobble & SINPO Shader (METEO-9 Panel 1C)
  4. Quarry 44-K Searchlight & Ceres Spot Curve Shader (ECON-9 Panel 2A)
  5. Canyon Floor Barracks Cryo-Thermal Infrared Sweep Shader (ECON-9 Panel 2B)
  6. Quarantine Buoy 12 Orbital Radar & Customs X-Ray Crate Scanner Shader (ECON-9 Panel 2C)
  7. Titan-Minor N-24 Methane Water-Ripple & Whip-Detuning Waterfall Shader (HAUSER Panel 3A)
  8. Callisto Dome-4 Night-Market Steam & Dipole Blowtorch Plasma Arc Shader (HAUSER Panel 3B)
  9. Intergalactic M-33 3D Phosphor Lissajous Knot & Ming Packet Shader (HAUSER Panel 3C)
  10. Euclid I.34 (G.47) Noise-Floor Hough Transform, Vat 19 LIDAR Scan, Vector Congruence
      Wave-Pulse, and Mud-Rake Sheared Cotter-Pin Forensic Simulator (EUCLID-9 Panels 4A-4C).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATION_DIR = ROOT / "station"
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
PLATES_DIR = STATION_DIR / "plates"
EP_PLATES_DIR = EP_DIR / "plates"
COMP_DIR = STATION_DIR / "rig"
FLOW_DIR = EP_DIR / "clips"
SFX_DIR = STATION_DIR / "sfx"
RENDERS_DIR = EP_DIR / "previews"

W, H = 2560, 1440
FPS = 24

# Pre-computed normalized coordinate grid (SH_H x SH_W) for fast vectorized NumPy shaders
SH_W, SH_H = 320, 320
_GY, _GX = np.mgrid[0:SH_H, 0:SH_W].astype(np.float32)
NX = (_GX / SH_W) * 2.0 - 1.0  # -1.0 .. +1.0
NY = (_GY / SH_H) * 2.0 - 1.0  # -1.0 .. +1.0
NR = np.sqrt(NX ** 2 + NY ** 2)
NTHETA = np.arctan2(NY, NX)


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def build_snow_bank(rng: np.random.Generator, count: int = 8) -> list[np.ndarray]:
    bank = []
    for _ in range(count):
        fine = rng.integers(0, 256, size=(H // 2, W // 2), dtype=np.uint8)
        snow = np.where(fine > 195, 255, np.where(fine < 75, 12, fine)).astype(np.float32)
        snow_full = np.repeat(np.repeat(snow, 2, axis=0), 2, axis=1)
        for _ in range(28):
            ry = int(rng.integers(0, H - 3))
            rx = int(rng.integers(0, W - 400))
            rw = int(rng.integers(80, 400))
            snow_full[ry:ry + 2, rx:rx + rw] = 255.0
        snow_rgb = np.dstack([snow_full * 0.90, snow_full * 0.96, snow_full])
        bank.append(snow_rgb.astype(np.float32))
    return bank


def beacon_pulse(t: float, period: float, phase_offset: float) -> float:
    cyc = ((t + phase_offset) % period) / period
    if cyc < 0.36:
        return float(math.sin((cyc / 0.36) * math.pi) ** 1.6)
    return 0.0


def neon_nine_pulse(t: float) -> float:
    if t < 1.35:
        return 0.0
    cyc = (t * 0.42) % 1.0
    if cyc < 0.62:
        return 0.96 + 0.04 * math.sin(t * 37.0)
    if cyc < 0.67:
        return 0.15
    if cyc < 0.73:
        return 0.92
    if cyc < 0.88:
        return 0.08
    return 0.65 + 0.35 * math.sin(t * 55.0)


def ring_wave_intensity(t: float, ring_idx: int, ding_lock_sec: float) -> float:
    if t < ding_lock_sec:
        if ring_idx == 1 and t > 1.2:
            return 0.22 * (0.5 + 0.5 * math.sin(t * 6.0))
        return 0.0
    onset = ding_lock_sec + (ring_idx - 1) * 0.18
    if t < onset:
        return 0.0
    ramp = min(1.0, (t - onset) / 0.28)
    wave_mod = 0.68 + 0.32 * math.sin((t - ding_lock_sec) * 4.4 - (ring_idx - 1) * 0.95)
    surge = 0.30 * math.exp(-max(0.0, t - onset) / 0.9)
    return float(min(1.35, ramp * wave_mod + surge))


def apply_switch_glitch(frame: Image.Image, dt_since_switch: float, seed: int) -> Image.Image:
    """Apply a crisp 0.20s CRT relay-switch horizontal sync & RGB split glitch when panels shift."""
    if dt_since_switch < 0.0 or dt_since_switch > 0.20:
        return frame
    strength = 1.0 - (dt_since_switch / 0.20)
    arr = np.asarray(frame, dtype=np.uint8).copy()
    rng = np.random.default_rng(seed + int(dt_since_switch * 1000))
    # Horizontal slice shifts inside the left viewport (x=52..1350, y=108..1372)
    for _ in range(int(5 + 10 * strength)):
        by = int(rng.integers(115, 1340))
        bh = int(rng.integers(10, 38))
        shift = int(rng.integers(-80, 81) * strength)
        arr[by:by + bh, 56:1346] = np.roll(arr[by:by + bh, 56:1346], shift, axis=1)
    # Subtle RGB channel split
    split = max(1, int(10 * strength))
    arr[110:1370, 56:1346, 0] = np.roll(arr[110:1370, 56:1346, 0], split, axis=1)
    arr[110:1370, 56:1346, 2] = np.roll(arr[110:1370, 56:1346, 2], -split, axis=1)
    return Image.fromarray(arr, mode="RGB")


def draw_master_top_bar(draw: ImageDraw.ImageDraw, fonts: dict, console_tag: str, panel_tag: str, t: float) -> None:
    """Draw the 2560px top broadcast status bar with active panel indicator."""
    draw.rectangle([0, 0, W, 82], fill=(6, 9, 16))
    draw.line([0, 82, W, 82], fill=(232, 184, 90), width=3)

    pulse_on = (int(t * 2.0) % 2) == 0
    dot_col = (244, 63, 94) if pulse_on else (140, 30, 48)
    draw.rounded_rectangle([28, 14, 194, 68], radius=8, fill=(38, 12, 20), outline=(244, 63, 94), width=2)
    draw.ellipse([46, 30, 68, 52], fill=dot_col)
    draw.text((80, 24), "ON AIR", font=fonts["f26"], fill=(255, 210, 218))

    draw.text((216, 22), "GOR-9 • GALACTIC OUTPOST RADIO", font=fonts["f32"], fill=(232, 184, 90))
    draw.text((865, 25), f"CONSOLE: {console_tag}", font=fonts["f24"], fill=(56, 189, 248))

    p_txt = f"PANEL: {panel_tag}"
    pw = int(draw.textlength(p_txt, font=fonts["f24"])) + 36
    px1 = W - 535
    px0 = px1 - pw
    draw.rounded_rectangle([px0, 16, px1, 66], radius=6, fill=(12, 22, 36), outline=(56, 189, 248), width=2)
    draw.text((px0 + 18, 25), p_txt, font=fonts["f24"], fill=(148, 228, 255))
    draw.text((W - 510, 24), "14,285.7 kHz USB • 0400 UTC", font=fonts["f24"], fill=(190, 206, 224))



def draw_right_topic_stack(
    frame: Image.Image,
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    topics: list[dict],
    active_idx: int,
    t: float,
) -> None:
    """Draw 3 large TV-readable topic cards on the right (x=1380..2510), highlighting active_idx."""
    x0, x1 = 1380, 2510
    card_w = x1 - x0
    slots = [
        (108, 508),
        (538, 938),
        (968, 1368),
    ]
    for idx, (y0, y1) in enumerate(slots):
        if idx >= len(topics):
            break
        tp = topics[idx]
        col = tp["color"]
        is_active = idx == active_idx
        is_done = idx < active_idx
        card_h = y1 - y0

        if is_active:
            # Render a live moving plasma/scanline shimmer shader inside the active card background
            yy = np.linspace(0.0, 1.0, card_h, dtype=np.float32)[:, None]
            xx = np.linspace(0.0, 1.0, card_w, dtype=np.float32)[None, :]
            wave = 0.5 + 0.5 * np.sin(xx * 6.0 - yy * 4.0 - t * 4.2)
            scan = 0.85 + 0.15 * np.sin(yy * 120.0 + t * 12.0)
            bg = np.zeros((card_h, card_w, 3), dtype=np.uint8)
            bg[..., 0] = np.clip(10 + wave * scan * (col[0] * 0.22), 0, 255).astype(np.uint8)
            bg[..., 1] = np.clip(16 + wave * scan * (col[1] * 0.22), 0, 255).astype(np.uint8)
            bg[..., 2] = np.clip(28 + wave * scan * (col[2] * 0.25), 0, 255).astype(np.uint8)
            frame.paste(Image.fromarray(bg, mode="RGB"), (x0, y0))

            # Glowing outer border + left accent bar
            draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=None, outline=col, width=5)
            draw.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=12, fill=None, outline=(255, 255, 255), width=1)
            draw.rectangle([x0, y0 + 16, x0 + 14, y1 - 16], fill=col)

            # Active status badge on top-right of card
            badge_txt = f"◀ ACTIVE PANEL {idx + 1}/3"
            bw = int(draw.textlength(badge_txt, font=fonts["f24"])) + 32
            draw.rounded_rectangle([x1 - bw - 24, y0 + 20, x1 - 24, y0 + 62], radius=6, fill=col)
            draw.text((x1 - bw - 8, y0 + 27), badge_txt, font=fonts["f24"], fill=(6, 10, 18))

            # Active Left-Pointing Connector Arrow linking this card to the Left Viewport
            mid_y = (y0 + y1) // 2
            draw.polygon([(1352, mid_y), (1378, mid_y - 22), (1378, mid_y + 22)], fill=col)

            # High-contrast TV-readable text
            draw.text((x0 + 38, y0 + 26), tp["tag"], font=fonts["f28"], fill=col)
            draw.text((x0 + 38, y0 + 92), tp["big"], font=fonts["f68"], fill=(255, 255, 255))
            draw.text((x0 + 38, y0 + 202), tp["sub1"], font=fonts["f36"], fill=(255, 224, 130))
            draw.text((x0 + 38, y0 + 266), tp["sub2"], font=fonts["f30"], fill=(205, 224, 242))
            if tp.get("sub3"):
                draw.text((x0 + 38, y0 + 324), tp["sub3"], font=fonts["f26"], fill=col)
        else:
            # Dimmed standby / completed card so active card pops immediately
            dim_col = (int(col[0] * 0.38), int(col[1] * 0.38), int(col[2] * 0.38))
            draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(7, 10, 16), outline=dim_col, width=2)
            status_str = "✓ LOGGED" if is_done else f"QUEUE {idx + 1}/3"
            draw.text((x1 - 190, y0 + 26), status_str, font=fonts["f24"], fill=(90, 108, 128))
            draw.text((x0 + 34, y0 + 26), tp["tag"], font=fonts["f28"], fill=dim_col)
            draw.text((x0 + 34, y0 + 92), tp["big"], font=fonts["f68"], fill=(105, 118, 136))
            draw.text((x0 + 34, y0 + 202), tp["sub1"], font=fonts["f36"], fill=(88, 100, 116))
            draw.text((x0 + 34, y0 + 266), tp["sub2"], font=fonts["f30"], fill=(72, 84, 98))


def render_video_insert_frame(
    start_arr: np.ndarray,
    end_arr: np.ndarray | None,
    t: float,
    local_t: float,
    duration: float,
    target_w: int,
    target_h: int,
    shader_mode: str = "none",
    intensity: float = 1.0,
) -> Image.Image:
    """Render an animated remote camera / featured station video insert with shader effects.

    If a pre-rendered Flow MP4 is later placed in `assets/flow/`, this slot hosts it directly;
    otherwise it smoothly tweens and pans across `start_arr` -> `end_arr` and runs a real-time
    NumPy shader (`storm_arc`, `quarry_beam`, `water_ripple`, `bazaar_torch`, `thermal_ir`, `lidar_vat`).
    """
    prog = max(0.0, min(1.0, local_t / max(duration, 0.1)))
    # Smooth ping-pong or forward ease between start_arr and end_arr
    if end_arr is not None:
        blend = 0.5 - 0.5 * math.cos(min(1.0, prog * 1.15) * math.pi)
        base = start_arr * (1.0 - blend) + end_arr * blend
    else:
        base = start_arr.copy()

    # Subtle camera pan/zoom crop (100% -> 108% zoom)
    src_h, src_w = base.shape[:2]
    zoom = 1.0 + 0.07 * math.sin(prog * math.pi * 0.5)
    cw, ch = int(src_w / zoom), int(src_h / zoom)
    cx0 = int((src_w - cw) * (0.35 + 0.30 * math.sin(t * 0.4)))
    cy0 = int((src_h - ch) * (0.40 + 0.20 * math.cos(t * 0.3)))
    cropped = base[cy0:cy0 + ch, cx0:cx0 + cw]
    img_pil = Image.fromarray(np.clip(cropped, 0, 255).astype(np.uint8), mode="RGB").resize(
        (target_w, target_h), Image.Resampling.BILINEAR
    )
    arr = np.asarray(img_pil, dtype=np.float32).copy()

    yy, xx = np.mgrid[0:target_h, 0:target_w].astype(np.float32)
    nx = xx / float(target_w)
    ny = yy / float(target_h)

    if shader_mode == "storm_arc":
        # 60 kV Triboelectric Cyan Plasma Arcs + Dust Squall Shader
        dust = 0.5 + 0.5 * np.sin(nx * 18.0 - t * 9.0 + np.sin(ny * 8.0 + t * 2.0))
        arr[..., 0] = np.clip(arr[..., 0] + dust * 28.0, 0, 255)
        arr[..., 1] = np.clip(arr[..., 1] + dust * 18.0, 0, 255)
        # Branching plasma arc flashes from feedhorn (center-top)
        arc_env = max(0.0, math.sin(t * 11.0) * math.sin(t * 4.7))
        if arc_env > 0.25:
            bolt_x = 0.50 + 0.08 * np.sin(ny * 28.0 + t * 45.0) + 0.03 * np.cos(ny * 65.0 - t * 80.0)
            dist = np.abs(nx - bolt_x) * (1.0 + 1.5 * np.abs(ny - 0.42))
            glow = np.exp(-dist * 55.0) * arc_env * 1.4
            arr[..., 0] = np.clip(arr[..., 0] + glow * 160.0, 0, 255)
            arr[..., 1] = np.clip(arr[..., 1] + glow * 245.0, 0, 255)
            arr[..., 2] = np.clip(arr[..., 2] + glow * 255.0, 0, 255)
            # Chromatic aberration jolt on arc strike
            shift = int(8 * arc_env)
            if shift > 0:
                arr[..., 0] = np.roll(arr[..., 0], shift, axis=1)
                arr[..., 2] = np.roll(arr[..., 2], -shift, axis=1)

    elif shader_mode == "quarry_beam":
        # Sweeping Amber Floodlight Cone & Drifting Silicate Dust Shader
        beam_angle = 0.35 * math.sin(t * 1.8)
        dx = nx - 0.28
        dy = ny - 0.18
        ang = np.arctan2(dy, dx) - (0.65 + beam_angle)
        cone = np.exp(-(ang ** 2) / (2.0 * 0.18 ** 2)) * np.clip(np.sqrt(dx ** 2 + dy ** 2) * 1.5, 0.0, 1.0)
        arr[..., 0] = np.clip(arr[..., 0] + cone * 65.0, 0, 255)
        arr[..., 1] = np.clip(arr[..., 1] + cone * 48.0, 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] + cone * 18.0, 0, 255)

    elif shader_mode == "water_ripple":
        # Methane Shallows Water Surface Ripple Shader on lower 42% of frame + CW interference
        water_mask = np.clip((ny - 0.56) / 0.12, 0.0, 1.0)
        ripple = np.sin(ny * 140.0 - t * 8.5 + np.sin(nx * 24.0 + t * 2.0)) * water_mask
        shift_x = (ripple * 4.5).astype(np.int32)
        # Apply horizontal ripple shimmer and golden-cyan bioluminescent reflection
        arr[..., 1] = np.clip(arr[..., 1] + np.maximum(0.0, ripple) * 28.0 * (1.0 + 0.5 * intensity), 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] + np.maximum(0.0, ripple) * 36.0 * (1.0 + 0.5 * intensity), 0, 255)
        if intensity > 1.1:
            # Silt-strider guy-wire rub RF interference bars
            rf_bar = np.sin(ny * 85.0 + t * 50.0)
            arr = np.clip(arr + rf_bar[..., None] * 18.0, 0, 255)

    elif shader_mode == "bazaar_torch":
        # Rising Night-Market Steam + Rooftop Dipole Blowtorch Plasma Arc Shader
        steam = (0.5 + 0.5 * np.sin(nx * 14.0 + np.sin(ny * 10.0 - t * 3.2))) * np.clip(1.0 - ny, 0.0, 1.0)
        arr[..., 0] = np.clip(arr[..., 0] + steam * 16.0, 0, 255)
        arr[..., 1] = np.clip(arr[..., 1] + steam * 22.0, 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] + steam * 28.0, 0, 255)
        # Rooftop engineer blowtorch plasma flare at (nx=0.29, ny=0.22)
        torch_str = intensity if intensity > 1.1 else (0.35 + 0.25 * math.sin(t * 14.0))
        tdist = np.sqrt((nx - 0.29) ** 2 + ((ny - 0.22) * (target_h / target_w)) ** 2)
        core = np.exp(-(tdist ** 2) / (2.0 * (0.025 * torch_str) ** 2))
        halo = 0.65 * np.exp(-(tdist ** 2) / (2.0 * (0.095 * torch_str) ** 2))
        rays = (
            np.exp(-np.abs(nx - 0.29) * 45.0) * np.exp(-np.abs(ny - 0.22) * 8.0)
            + np.exp(-np.abs(ny - 0.22) * 45.0) * np.exp(-np.abs(nx - 0.29) * 8.0)
        ) * (0.45 * torch_str)
        flare = np.clip(core + halo + rays, 0.0, 1.8)
        arr[..., 0] = np.clip(arr[..., 0] + flare * 180.0, 0, 255)
        arr[..., 1] = np.clip(arr[..., 1] + flare * 240.0, 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] + flare * 255.0, 0, 255)

    elif shader_mode == "thermal_ir":
        # Scanning Cryo-Thermal Infrared Wave across North-24 Canyon Barracks
        scan_y = (t * 0.38) % 1.0
        band = np.exp(-((ny - scan_y) ** 2) / (2.0 * 0.14 ** 2))
        luma = (arr[..., 0] * 0.3 + arr[..., 1] * 0.59 + arr[..., 2] * 0.11) / 255.0
        # False-color thermal palette: cold basalt = deep blue/violet, warm Quonset seams = gold/crimson
        th_r = np.clip(luma * 255.0 * 1.4, 0, 255)
        th_g = np.clip(np.sin(luma * math.pi) * 210.0, 0, 255)
        th_b = np.clip((1.0 - luma) * 255.0 * 1.3, 0, 255)
        arr[..., 0] = arr[..., 0] * (1.0 - 0.65 * band) + th_r * (0.65 * band)
        arr[..., 1] = arr[..., 1] * (1.0 - 0.65 * band) + th_g * (0.65 * band)
        arr[..., 2] = arr[..., 2] * (1.0 - 0.65 * band) + th_b * (0.65 * band)
        # Bright laser scanline at scan_y
        line_m = np.exp(-((ny - scan_y) ** 2) / (2.0 * 0.006 ** 2))
        arr[..., 1] = np.clip(arr[..., 1] + line_m * 180.0, 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] + line_m * 255.0, 0, 255)

    elif shader_mode == "lidar_vat":
        # Sweeping Emerald/Cyan LIDAR Laser Sheet across Brine Evaporation Vat 19
        scan_y = (local_t * 0.28) % 1.0
        laser = np.exp(-((ny - scan_y) ** 2) / (2.0 * 0.008 ** 2))
        grid_x = (np.sin(nx * 90.0) > 0.92).astype(np.float32) * np.exp(-((ny - scan_y) ** 2) / (2.0 * 0.08 ** 2))
        arr[..., 0] = np.clip(arr[..., 0] + laser * 60.0, 0, 255)
        arr[..., 1] = np.clip(arr[..., 1] + (laser * 235.0 + grid_x * 110.0), 0, 255)
        arr[..., 2] = np.clip(arr[..., 2] + (laser * 200.0 + grid_x * 140.0), 0, 255)

    # Subtle CRT scanline finish on video insert
    arr[2::3] *= 0.88
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def shader_magnetosphere_plasma(t: float, target_w: int, target_h: int) -> Image.Image:
    """Shader 1: Sector 9 Magnetospheric Bow-Shock & Solar Wind Plasma Field."""
    # Bow shock parabola centered around (0.15, 0.0)
    bow = NX - 0.35 * (NY ** 2) + 0.15
    shock_wave = np.exp(-(bow ** 2) / 0.035) * (0.75 + 0.25 * np.sin(NY * 14.0 - t * 5.0))
    # Flowing solar wind streamlines from left to right
    wind = 0.5 + 0.5 * np.sin((NX * 7.0 - t * 3.8) + 0.6 * np.sin(NY * 6.0 + t * 1.5))
    wind_gate = np.clip(1.0 - NR * 0.55, 0.1, 1.0)
    # Polar radar sweep
    sweep_ang = (t * 1.65) % (2.0 * math.pi) - math.pi
    d_ang = (NTHETA - sweep_ang + 2.0 * math.pi) % (2.0 * math.pi)
    radar_trail = np.exp(-d_ang * 2.4) * (NR <= 0.92).astype(np.float32)

    r = np.clip(8.0 + shock_wave * 235.0 + wind * wind_gate * 35.0 + radar_trail * 40.0, 0, 255)
    g = np.clip(14.0 + shock_wave * 175.0 + wind * wind_gate * 115.0 + radar_trail * 195.0, 0, 255)
    b = np.clip(26.0 + shock_wave * 90.0 + wind * wind_gate * 185.0 + radar_trail * 130.0, 0, 255)

    rgb = np.dstack([r, g, b]).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)


def shader_marzelvane_rotor(t: float, target_w: int, target_h: int) -> Image.Image:
    """Shader 3: 6-Hydrocoptic Marzelvane Bushing Rotor with #4 Bushing Phase-Wobble Shader."""
    # 6 radial stator lobes; lobe #4 (at angle ~ -2*pi/3) wobbles out of phase!
    rot_ang = NTHETA - t * 2.2
    six_lobes = np.cos(6.0 * rot_ang)
    ring_band = np.exp(-((NR - 0.56) ** 2) / 0.022)
    stator_glow = np.clip(0.5 + 0.5 * six_lobes, 0.0, 1.0) * ring_band

    # Bushing #4 Fault Zone (around angle = +0.85 rad, radius = 0.56)
    b4_ang = 0.75 + 0.18 * math.sin(t * 18.0)
    b4_x = 0.56 * math.cos(b4_ang)
    b4_y = 0.56 * math.sin(b4_ang)
    b4_dist = np.sqrt((NX - b4_x) ** 2 + (NY - b4_y) ** 2)
    wobble_ripples = np.exp(-b4_dist * 3.2) * (0.5 + 0.5 * np.sin(b4_dist * 38.0 - t * 22.0))
    b4_core = np.exp(-(b4_dist ** 2) / 0.015)

    # Inner lotus harmonic field
    inner_field = np.exp(-((NR - 0.25) ** 2) / 0.012) * (0.5 + 0.5 * np.sin(12.0 * NTHETA + t * 8.0))

    r = np.clip(8.0 + stator_glow * 45.0 + wobble_ripples * 244.0 + b4_core * 255.0 + inner_field * 210.0, 0, 255)
    g = np.clip(12.0 + stator_glow * 185.0 + wobble_ripples * 75.0 + b4_core * 140.0 + inner_field * 165.0, 0, 255)
    b = np.clip(22.0 + stator_glow * 245.0 + wobble_ripples * 95.0 + b4_core * 90.0 + inner_field * 70.0, 0, 255)

    rgb = np.dstack([r, g, b]).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)


def shader_customs_xray_scanner(t: float, target_w: int, target_h: int) -> Image.Image:
    """Shader 6: Quarantine Buoy 12 Orbital Radar + Customs Backscatter X-Ray Scanner."""
    # Top half (NY < 0): Orbital holding radar around Quarantine Buoy 12
    # Bottom half (NY >= 0): Backscatter X-Ray crate scan morphing Oscillator Tube <-> Brine Tuber
    scan_x = math.sin(t * 2.4) * 0.75
    laser_beam = np.exp(-((NX - scan_x) ** 2) / 0.008)

    # X-ray object silhouette (3 vertical vacuum tubes / tubers inside crate)
    crate_grid = (np.abs( np.sin(NX * 18.0) ) > 0.94) | (np.abs( np.sin(NY * 18.0) ) > 0.94)
    tubes = np.zeros_like(NX)
    for cx_pos in (-0.48, 0.0, 0.48):
        # Morph between straight cylindrical vacuum tube and lumpy brine tuber based on scan_x
        is_tuber = (NX > scan_x).astype(np.float32)
        wobble = is_tuber * 0.06 * np.sin(NY * 16.0 + cx_pos * 5.0)
        td = np.sqrt(((NX - cx_pos + wobble) * 1.8) ** 2 + (NY * 1.15) ** 2)
        filament = np.exp(-((NX - cx_pos) ** 2) / 0.002) * (np.abs(NY) < 0.45).astype(np.float32) * (1.0 - is_tuber)
        body = np.exp(-(td ** 2) / 0.08)
        tubes += body + filament * 1.2

    is_amber_side = (NX > scan_x).astype(np.float32)
    r = np.clip(6.0 + tubes * (40.0 * (1.0 - is_amber_side) + 230.0 * is_amber_side) + laser_beam * 255.0 + crate_grid * 18.0, 0, 255)
    g = np.clip(12.0 + tubes * (215.0 * (1.0 - is_amber_side) + 150.0 * is_amber_side) + laser_beam * 245.0 + crate_grid * 36.0, 0, 255)
    b = np.clip(20.0 + tubes * (245.0 * (1.0 - is_amber_side) + 55.0 * is_amber_side) + laser_beam * 190.0 + crate_grid * 48.0, 0, 255)

    rgb = np.dstack([r, g, b]).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)


def shader_waterfall_spectrogram(t: float, detune_active: bool, mode: str, target_w: int, target_h: int) -> Image.Image:
    """Real-time Shortwave Waterfall Spectrogram Shader for HAUSER MK-IV."""
    # NY: -1 (top, newest) to +1 (bottom, oldest)
    # NX: -1 (low freq) to +1 (high freq)
    time_axis = t * 3.5 - (NY + 1.0) * 1.8
    if mode == "n24_cw":
        # Carrier at NX=0.0 that bends left/down when silt-striders rub guy-wires!
        bend = -0.28 * np.sin(time_axis * 3.2) * np.exp(-((NY) ** 2) / 0.4) if detune_active else 0.02 * np.sin(time_axis * 2.0)
        carrier = np.exp(-((NX - bend) ** 2) / 0.004) * (0.65 + 0.35 * np.sin(time_axis * 14.0))
        sidebands = 0.45 * (np.exp(-((NX - bend - 0.22) ** 2) / 0.008) + np.exp(-((NX - bend + 0.22) ** 2) / 0.008))
        sig = np.clip(carrier + sidebands, 0.0, 1.4)
    else:
        # Pentatonic AM comb + blowtorch broadband plasma burst
        comb = np.zeros_like(NX)
        for h_pos in (-0.55, -0.28, 0.0, 0.28, 0.55):
            vib = 0.03 * np.sin(time_axis * 6.0)
            comb += np.exp(-((NX - h_pos - vib) ** 2) / 0.006)
        torch_burst = (0.85 * np.exp(-((NY + 0.1) ** 2) / 0.18)) if detune_active else 0.0
        sig = np.clip(comb * (0.6 + 0.4 * np.sin(time_axis * 8.0)) + torch_burst, 0.0, 1.5)

    noise = 0.12 + 0.08 * np.sin(NX * 45.0 + time_axis * 19.0) * np.cos(NY * 38.0 - t * 11.0)
    val = np.clip(sig + noise, 0.0, 1.5)

    r = np.clip(8.0 + (val ** 1.6) * 245.0, 0, 255)
    g = np.clip(16.0 + val * 215.0, 0, 255)
    b = np.clip(38.0 + np.sin( np.clip(val, 0.0, 1.0) * math.pi * 0.7 ) * 235.0, 0, 255)
    rgb = np.dstack([r, g, b]).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)


def shader_m33_lissajous_scope(t: float, target_w: int, target_h: int) -> Image.Image:
    """Shader 9: Deep-Field M-33 Spiral Nebula + 3D Relativistic Phosphor Lissajous Knot."""
    # Spiral galaxy arms in background
    spiral_phase = NTHETA * 2.0 - NR * 9.5 + t * 0.6
    arms = np.exp(-NR * 1.8) * (0.5 + 0.5 * np.cos(spiral_phase))
    core = np.exp(-(NR ** 2) / 0.04)

    r = np.clip(6.0 + arms * 45.0 + core * 210.0, 0, 255)
    g = np.clip(14.0 + arms * 125.0 + core * 235.0, 0, 255)
    b = np.clip(24.0 + arms * 165.0 + core * 195.0, 0, 255)
    rgb = np.dstack([r, g, b]).astype(np.uint8)
    img = Image.fromarray(rgb, mode="RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)
    draw = ImageDraw.Draw(img)

    # Overlay crisp 3D Green/Cyan Phosphor Lissajous Knot
    cx, cy = target_w // 2, target_h // 2
    rad = min(target_w, target_h) * 0.39
    for r_ring in (int(rad * 1.08), int(rad * 0.75), int(rad * 0.42)):
        draw.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], outline=(42, 95, 115), width=2)

    pts = []
    for i in range(280):
        u = (i / 279.0) * 2.0 * math.pi
        lx = math.sin(3.0 * u + t * 1.9) * math.cos(u + t * 0.5)
        ly = math.sin(4.0 * u - t * 1.3)
        pts.append((cx + int(lx * rad), cy + int(ly * rad * 0.85)))
    draw.line(pts, fill=(94, 244, 160), width=5)
    draw.line(pts, fill=(210, 255, 230), width=2)
    return img


def shader_euclid_hough_correlator(t: float, target_w: int, target_h: int) -> Image.Image:
    """Shader 10A: Wideband Noise-Floor Geometric Hough-Transform Correlator Shader."""
    u1 = NY
    u2 = NX * 0.96 - NY * 0.22
    lock = min(1.0, (t % 7.5) / 3.2)
    grid1 = np.exp(-((np.abs(u1) - 0.36) ** 2) / 0.0035)
    grid2 = np.exp(-((np.abs(u2) - 0.44) ** 2) / 0.0035)
    diag = np.exp(-((NX * 0.48 + NY * 0.88) ** 2) / 0.0028) * lock
    fine_noise = 0.5 + 0.5 * np.sin(NX * 85.0 + t * 14.0) * np.cos(NY * 85.0 - t * 11.0)
    radar_sweep = np.exp(-(((NTHETA - ((t * 2.4) % (2 * math.pi) - math.pi)) % (2 * math.pi)) ** 2) / 0.18)

    r = np.clip(7.0 + fine_noise * 24.0 + (grid1 + grid2) * 48.0 + diag * 232.0 + radar_sweep * 25.0, 0, 255)
    g = np.clip(14.0 + fine_noise * 58.0 + (grid1 + grid2) * 189.0 + diag * 184.0 + radar_sweep * 85.0, 0, 255)
    b = np.clip(26.0 + fine_noise * 92.0 + (grid1 + grid2) * 248.0 + diag * 90.0 + radar_sweep * 130.0, 0, 255)
    rgb = np.dstack([r, g, b]).astype(np.uint8)
    img = Image.fromarray(rgb, mode="RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)
    draw = ImageDraw.Draw(img)
    # Overlay crisp Hough accumulator reticles on the 4 emergent vertices A, B, C, D
    pts = [
        (int(target_w * 0.26), int(target_h * 0.32), "LOCK A (0.0002\")"),
        (int(target_w * 0.78), int(target_h * 0.32), "LOCK B (0.0002\")"),
        (int(target_w * 0.18), int(target_h * 0.68), "LOCK C (0.0002\")"),
        (int(target_w * 0.70), int(target_h * 0.68), "LOCK D (0.0002\")"),
    ]
    draw.line([pts[0][:2], pts[1][:2]], fill=(56, 189, 248), width=4)
    draw.line([pts[2][:2], pts[3][:2]], fill=(56, 189, 248), width=4)
    draw.line([pts[0][:2], pts[2][:2]], fill=(56, 189, 248), width=4)
    draw.line([pts[1][:2], pts[3][:2]], fill=(56, 189, 248), width=4)
    draw.line([pts[1][:2], pts[2][:2]], fill=(232, 184, 90), width=5)
    for px, py, _ in pts:
        draw.ellipse([px - 22, py - 22, px + 22, py + 22], outline=(232, 184, 90), width=3)
    return img



def draw_left_viewport_frame(
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    title: str,
    subtitle: str,
    accent: tuple[int, int, int],
    is_video_insert: bool = False,
    slot_tag: str = "",
) -> tuple[int, int, int, int]:
    """Draw the standardized Left Viewport border & header (x=52..1350, y=108..1368)."""
    vx0, vy0, vx1, vy1 = 52, 108, 1350, 1368
    draw.rounded_rectangle([vx0, vy0, vx1, vy1], radius=16, fill=(7, 11, 18), outline=accent, width=4)
    # Top header inside left viewport
    draw.rectangle([vx0 + 4, vy0 + 4, vx1 - 4, vy0 + 86], fill=(10, 16, 28))
    draw.line([vx0 + 4, vy0 + 86, vx1 - 4, vy0 + 86], fill=accent, width=2)
    draw.text((vx0 + 28, vy0 + 24), title, font=fonts["f30"], fill=accent)

    if is_video_insert:
        badge = slot_tag or "VIDEO INSERT • LIVE FEED"
        bw = int(draw.textlength(badge, font=fonts["f24"])) + 48
        draw.rounded_rectangle([vx1 - bw - 20, vy0 + 18, vx1 - 20, vy0 + 68], radius=6, fill=(38, 12, 20), outline=(244, 63, 94), width=2)
        draw.ellipse([vx1 - bw - 4, vy0 + 34, vx1 - bw + 14, vy0 + 52], fill=(244, 63, 94))
        draw.text((vx1 - bw + 22, vy0 + 28), badge, font=fonts["f24"], fill=(255, 215, 220))
    elif subtitle:
        sw = int(draw.textlength(subtitle, font=fonts["f24"]))
        draw.text((vx1 - sw - 24, vy0 + 28), subtitle, font=fonts["f24"], fill=(180, 205, 228))

    return vx0 + 8, vy0 + 90, vx1 - 8, vy1 - 8


def render_seg1_meteo(
    t: float,
    seg_t: float,
    plates: dict[str, np.ndarray],
    fonts: dict,
) -> Image.Image:
    """SEG-1: METEO-9 Space Weather (3 Right Topic Cards -> 3 Distinct Left Shader/Video Panels)."""
    if seg_t < 7.5:
        active_idx = 0
        panel_tag = "1A • BOW-SHOCK PLASMA SHADER"
        dt_sw = seg_t
    elif seg_t < 15.2:
        active_idx = 1
        panel_tag = "1B • CAM-02 RELAY KZ9-OMEGA INSERT"
        dt_sw = seg_t - 7.5
    else:
        active_idx = 2
        panel_tag = "1C • MARZELVANE #4 ROTOR SHADER"
        dt_sw = seg_t - 15.2

    frame = Image.new("RGB", (W, H), (5, 8, 14))
    draw = ImageDraw.Draw(frame)
    draw_master_top_bar(draw, fonts, "METEO-9 • SPACE WEATHER", panel_tag, t)

    topics = [
        {
            "color": (94, 194, 126),
            "tag": "COREWARD LANES • PROPAGATION",
            "big": "SOLAR FLUX 174",
            "sub1": "K-INDEX 2.0 • CALM CORRIDOR",
            "sub2": "PALLAS–JUNO MAGNETOSPHERE NOMINAL",
            "sub3": "◀ LEFT: SOLAR WIND BOW-SHOCK SHADER",
        },
        {
            "color": (244, 63, 94),
            "tag": "MERIDIAN PLATEAU • DUST SQUALL",
            "big": "60 kV ARCING",
            "sub1": "RELAY KZ9-OMEGA ENGULFED",
            "sub2": "TRIBOELECTRIC FEEDHORN DISCHARGE",
            "sub3": "◀ LEFT: LIVE CAM-02 STORM VIDEO INSERT",
        },
        {
            "color": (232, 184, 90),
            "tag": "ENCABULATOR HARDWARE DIAGNOSTIC",
            "big": "#4 MARZELVANE",
            "sub1": "PHASE-WOBBLE IN BUSHING (+4.8°)",
            "sub2": "EXPECT SINPO 2-3-2-2-2",
            "sub3": "◀ LEFT: BUSHING ROTOR & SINPO ANALYZER",
        },
    ]
    draw_right_topic_stack(frame, draw, fonts, topics, active_idx, t)

    if active_idx == 0:
        # Left Panel 1A: Solar Wind Bow-Shock Plasma Shader + Telemetry Bars
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw, fonts, "SECTOR 9 MAGNETOSPHERIC BOW-SHOCK SHADER", "SOLAR WIND: 410 km/s", (94, 194, 126)
        )
        sh_img = shader_magnetosphere_plasma(t, ix1 - ix0, (iy1 - iy0) - 240)
        frame.paste(sh_img, (ix0, iy0))
        # Draw polar range rings & Asteroid 3-5-1 center marker over shader
        pcx, pcy = (ix0 + ix1) // 2, iy0 + ((iy1 - iy0) - 240) // 2
        for rr in (120, 240, 360):
            draw.ellipse([pcx - rr, pcy - rr, pcx + rr, pcy + rr], outline=(160, 235, 210), width=2)
        draw.text((pcx + 18, pcy - 18), "ASTEROID 3-5-1", font=fonts["f26"], fill=(255, 255, 255))

        # Bottom telemetry gauge strip inside Left Panel 1A
        by0 = iy1 - 232
        draw.rectangle([ix0, by0, ix1, iy1], fill=(8, 13, 22))
        draw.line([ix0, by0, ix1, by0], fill=(94, 194, 126), width=3)
        draw.text((ix0 + 28, by0 + 22), "COREWARD SOLAR FLUX: 174 SFU", font=fonts["f42"], fill=(94, 194, 126))
        draw.text((ix0 + 28, by0 + 88), "PLANETARY K-INDEX  : Kp 2.0 [QUIET]", font=fonts["f36"], fill=(255, 255, 255))
        # Animated green bar meter
        for b_i in range(18):
            bx = ix0 + 28 + b_i * 66
            active_bar = b_i < 13
            draw.rectangle([bx, by0 + 150, bx + 52, by0 + 202], fill=(94, 194, 126) if active_bar else (24, 38, 52))

    elif active_idx == 1:
        # Left Panel 1B: Video Insert CAM-02 Relay KZ9-Omega Storm + 60 kV Lightning Shader
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "CAM-02 • RELAY KZ9-OMEGA (MERIDIAN PLATEAU)",
            "",
            (244, 63, 94),
            is_video_insert=True,
            slot_tag="FLOW INSERT • CAM-02 LIVE",
        )
        vid_h = (iy1 - iy0) - 220
        vid_img = render_video_insert_frame(
            plates["cam02_start"],
            plates["cam02_end"],
            t,
            seg_t - 7.5,
            7.7,
            ix1 - ix0,
            vid_h,
            shader_mode="storm_arc",
        )
        frame.paste(vid_img, (ix0, iy0))

        # Bottom high-voltage arc meter
        by0 = iy0 + vid_h
        draw.rectangle([ix0, by0, ix1, iy1], fill=(16, 8, 14))
        draw.line([ix0, by0, ix1, by0], fill=(244, 63, 94), width=3)
        kv_now = 58.4 + 4.8 * math.sin(t * 11.0)
        draw.text((ix0 + 28, by0 + 20), f"FEEDHORN POTENTIAL: {kv_now:04.1f} kV [ARCING]", font=fonts["f42"], fill=(244, 63, 94))
        draw.text((ix0 + 28, by0 + 84), "MERIDIAN PLATEAU TRIBOELECTRIC DUST SQUALL", font=fonts["f32"], fill=(255, 224, 130))
        draw.text((ix0 + 28, by0 + 142), "CARRIER ATTENUATION: -14.2 dB • STATIC DISCHARGE", font=fonts["f28"], fill=(210, 225, 240))

    else:
        # Left Panel 1C: 6-Hydrocoptic Marzelvane #4 Rotor Phase-Wobble Shader + 5-Bar SINPO Analyzer
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw, fonts, "ENCABULATOR TELEMETRY • #4 MARZELVANE ROTOR", "SINPO: 2-3-2-2-2", (232, 184, 90)
        )
        sh_h = (iy1 - iy0) - 340
        sh_img = shader_marzelvane_rotor(t, ix1 - ix0, sh_h)
        frame.paste(sh_img, (ix0, iy0))

        # Overlay bushing labels #1..#6 around rotor
        rcx, rcy = (ix0 + ix1) // 2, iy0 + sh_h // 2
        for b_i in range(6):
            ang = b_i * (math.pi / 3.0) - 0.5
            lx = rcx + int(math.cos(ang) * 255)
            ly = rcy + int(math.sin(ang) * 195)
            is_b4 = (b_i + 1) == 4
            lbl = "#4 WOBBLE!" if is_b4 else f"BUSHING #{b_i + 1}"
            draw.rounded_rectangle([lx - 90, ly - 22, lx + 90, ly + 22], radius=6, fill=(28, 10, 16) if is_b4 else (8, 14, 24), outline=(244, 63, 94) if is_b4 else (56, 189, 248), width=3 if is_b4 else 2)
            draw.text((lx - 76, ly - 14), lbl, font=fonts["f24"], fill=(244, 63, 94) if is_b4 else (180, 220, 245))

        # Bottom 340px: 5-Column SINPO 2-3-2-2-2 LED Spectrum Analyzer
        by0 = iy0 + sh_h
        draw.rectangle([ix0, by0, ix1, iy1], fill=(8, 12, 20))
        draw.line([ix0, by0, ix1, by0], fill=(232, 184, 90), width=3)
        draw.text((ix0 + 28, by0 + 18), "SINPO RECEPTION MATRIX: 2 - 3 - 2 - 2 - 2", font=fonts["f36"], fill=(232, 184, 90))

        sinpo_items = [("S", "SIGNAL", 2), ("I", "INTERF", 3), ("N", "NOISE", 2), ("P", "PROPAG", 2), ("O", "OVERALL", 2)]
        col_w = (ix1 - ix0 - 80) // 5
        for idx_s, (code, name_s, val_s) in enumerate(sinpo_items):
            sx = ix0 + 40 + idx_s * col_w
            draw.text((sx + 20, by0 + 76), f"{code}:{val_s}", font=fonts["f48"], fill=(255, 255, 255))
            draw.text((sx + 18, by0 + 138), name_s, font=fonts["f24"], fill=(160, 185, 210))
            for seg_level in range(1, 6):
                ly_bar = by0 + 305 - seg_level * 28
                lit = seg_level <= val_s
                bcol = (244, 63, 94) if val_s <= 2 else (232, 184, 90)
                draw.rectangle([sx + 12, ly_bar, sx + col_w - 28, ly_bar + 20], fill=bcol if lit else (22, 30, 44))

    return apply_switch_glitch(frame, dt_sw, seed=100 + active_idx)


def render_seg2_econ(
    t: float,
    seg_t: float,
    plates: dict[str, np.ndarray],
    fonts: dict,
) -> Image.Image:
    """SEG-2: ECON-9 Outpost Economics (3 Right Topic Cards -> 3 Distinct Left Panels)."""
    if seg_t < 8.2:
        active_idx = 0
        panel_tag = "2A • CAM-44K QUARRY & CERES SPOT"
        dt_sw = seg_t
    elif seg_t < 15.8:
        active_idx = 1
        panel_tag = "2B • CAM-00C BARRACKS THERMAL IR"
        dt_sw = seg_t - 8.2
    else:
        active_idx = 2
        panel_tag = "2C • BUOY 12 CUSTOMS X-RAY SCAN"
        dt_sw = seg_t - 15.8

    frame = Image.new("RGB", (W, H), (5, 8, 14))
    draw = ImageDraw.Draw(frame)
    draw_master_top_bar(draw, fonts, "ECON-9 • OUTPOST ECONOMICS", panel_tag, t)

    topics = [
        {
            "color": (94, 194, 126),
            "tag": "GRADE-B DEUTERIUM PELLETS",
            "big": "+4.2% CERES SPOT",
            "sub1": "QUARRY 44-K DRAGLINE SLOWDOWN",
            "sub2": "SHIFT OUTPUT DROPPED 18%",
            "sub3": "◀ LEFT: CAM-44K INSERT & SPOT CURVE",
        },
        {
            "color": (56, 189, 248),
            "tag": "PEBBLE-BED REACTOR #2 STEP-DOWN",
            "big": "12 kW NIGHT CAP",
            "sub1": "DORM WING B: PLUG IN FOOT-WARMERS",
            "sub2": "NORTH-24 CANYON BARRACKS AT 11°C",
            "sub3": "◀ LEFT: CAM-00C THERMAL INFRARED SCAN",
        },
        {
            "color": (244, 63, 94),
            "tag": "QUARANTINE BUOY 12 CUSTOMS HOLD",
            "big": "MV PERSEVERANCE",
            "sub1": "6 CRATES: OSCILLATOR TUBES",
            "sub2": "MISFILED AS \"FERMENTED BRINE TUBERS\"",
            "sub3": "◀ LEFT: CUSTOMS X-RAY CRATE SCANNER",
        },
    ]
    draw_right_topic_stack(frame, draw, fonts, topics, active_idx, t)

    if active_idx == 0:
        # Left Panel 2A: Video Insert CAM-44K Silicate Quarry + Animated Ceres Spot Curve
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "CAM-44K • SILICATE QUARRY DRAGLINE PIT",
            "",
            (94, 194, 126),
            is_video_insert=True,
            slot_tag="FLOW INSERT • CAM-44K LIVE",
        )
        vid_h = (iy1 - iy0) - 360
        vid_img = render_video_insert_frame(
            plates["cam44k_start"],
            plates["cam44k_end"],
            t,
            seg_t,
            8.2,
            ix1 - ix0,
            vid_h,
            shader_mode="quarry_beam",
        )
        frame.paste(vid_img, (ix0, iy0))

        # Bottom 360px: Ceres Spot Exchange Step-Line Shader Graph
        by0 = iy0 + vid_h
        draw.rectangle([ix0, by0, ix1, iy1], fill=(7, 13, 18))
        draw.line([ix0, by0, ix1, by0], fill=(94, 194, 126), width=3)
        draw.text((ix0 + 28, by0 + 18), "CERES SPOT EXCHANGE • DEUTERIUM (+4.2%)", font=fonts["f36"], fill=(94, 194, 126))

        # Draw animated step-line curve
        pts = []
        gw = ix1 - ix0 - 80
        for i in range(40):
            u = i / 39.0
            px = ix0 + 40 + int(u * gw)
            spike = 1.0 / (1.0 + math.exp(-(u - 0.58) * 18.0))
            py = by0 + 290 - int(spike * 155 + 16 * math.sin(u * 15.0 + t * 3.0))
            pts.append((px, py))
        draw.line(pts, fill=(94, 194, 126), width=6)
        draw.text((ix0 + 40, by0 + 305), "00:00 UTC          02:00 UTC          03:15 CABLE FAULT          04:00 UTC", font=fonts["f24"], fill=(170, 205, 190))

    elif active_idx == 1:
        # Left Panel 2B: CAM-00C Canyon Floor Barracks with Cryo-Thermal Infrared Shader + Reactor Gauge
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "CAM-00C • NORTH-24 BARRACKS [THERMAL IR SCAN]",
            "",
            (56, 189, 248),
            is_video_insert=True,
            slot_tag="TOWER CAM-00C • -240m",
        )
        vid_h = (iy1 - iy0) - 250
        # Crop centered on the 3 Quonset huts in the canyon floor
        b_crop = plates["cam00c_barracks"][100:1370, 900:2000]
        vid_img = render_video_insert_frame(
            b_crop,
            None,
            t,
            seg_t - 8.2,
            7.6,
            ix1 - ix0,
            vid_h,
            shader_mode="thermal_ir",
        )
        frame.paste(vid_img, (ix0, iy0))

        # Target reticle on Dormitory Wing B
        rx, ry = ix0 + 640, iy0 + 520
        r_pulse = 95 + int(12 * math.sin(t * 6.0))
        draw.ellipse([rx - r_pulse, ry - r_pulse, rx + r_pulse, ry + r_pulse], outline=(56, 189, 248), width=4)
        draw.text((rx - 130, ry + r_pulse + 12), "DORM WING B: 11.2°C", font=fonts["f28"], fill=(148, 228, 255))

        # Bottom 250px: Pebble-Bed Reactor #2 Step-Down Bar
        by0 = iy0 + vid_h
        draw.rectangle([ix0, by0, ix1, iy1], fill=(8, 14, 24))
        draw.line([ix0, by0, ix1, by0], fill=(56, 189, 248), width=3)
        step_p = min(1.0, max(0.0, (seg_t - 8.5) / 3.5))
        kw_now = 50.0 - 38.0 * step_p
        draw.text((ix0 + 28, by0 + 20), f"REACTOR #2 OUTPUT: {kw_now:04.1f} kW USB", font=fonts["f44"], fill=(232, 184, 90) if kw_now > 15 else (56, 189, 248))
        draw.text((ix0 + 28, by0 + 88), "ADVISORY: PLUG IN AUXILIARY FOOT-WARMERS", font=fonts["f32"], fill=(255, 255, 255))
        bar_w = int((ix1 - ix0 - 60) * (kw_now / 50.0))
        draw.rectangle([ix0 + 28, by0 + 150, ix1 - 32, by0 + 206], outline=(56, 189, 248), width=3)
        draw.rectangle([ix0 + 32, by0 + 154, ix0 + 32 + bar_w, by0 + 202], fill=(56, 189, 248))

    else:
        # Left Panel 2C: Quarantine Buoy 12 Orbital Radar + Customs Backscatter X-Ray Crate Scanner
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw, fonts, "QUARANTINE BUOY 12 • CUSTOMS X-RAY SCANNER", "TARIFF 409-B", (244, 63, 94)
        )
        sh_h = (iy1 - iy0) - 260
        sh_img = shader_customs_xray_scanner(t, ix1 - ix0, sh_h)
        frame.paste(sh_img, (ix0, iy0))

        # Overlay labels on X-Ray Scanner: Left = ACTUAL (807-B OSCILLATOR TUBES), Right = DECLARED (BRINE TUBERS)
        draw.rounded_rectangle([ix0 + 24, iy0 + 24, ix0 + 560, iy0 + 110], radius=8, fill=(8, 18, 28), outline=(56, 189, 248), width=3)
        draw.text((ix0 + 44, iy0 + 36), "X-RAY ACTUAL: 807-B TUBES", font=fonts["f28"], fill=(56, 189, 248))
        draw.text((ix0 + 44, iy0 + 72), "TRANSMITTER CATHODE SPARES", font=fonts["f24"], fill=(210, 230, 245))

        draw.rounded_rectangle([ix1 - 590, iy0 + 24, ix1 - 24, iy0 + 110], radius=8, fill=(28, 10, 16), outline=(244, 63, 94), width=3)
        draw.text((ix1 - 570, iy0 + 36), "MANIFEST ERR: BRINE TUBERS", font=fonts["f28"], fill=(244, 63, 94))
        draw.text((ix1 - 570, iy0 + 72), "AGRICULTURAL HOLD • DAY 11", font=fonts["f24"], fill=(255, 215, 220))

        # Bottom 260px: Impound Dossier
        by0 = iy0 + sh_h
        draw.rectangle([ix0, by0, ix1, iy1], fill=(16, 8, 12))
        draw.line([ix0, by0, ix1, by0], fill=(244, 63, 94), width=3)
        draw.text((ix0 + 28, by0 + 22), "IMPOUNDED: TENDER MV PERSEVERANCE-4", font=fonts["f42"], fill=(244, 63, 94))
        draw.text((ix0 + 28, by0 + 88), "ACTUAL  : 6 CRATES • 807-B OSCILLATOR TUBES", font=fonts["f32"], fill=(56, 189, 248))
        draw.text((ix0 + 28, by0 + 142), "MISFILED: \"FERMENTED BRINE TUBERS\" (FORM 409-B)", font=fonts["f32"], fill=(232, 184, 90))

    return apply_switch_glitch(frame, dt_sw, seed=200 + active_idx)


def get_clip_frame(clip_frames: list[Image.Image], clip_t: float, target_w: int, target_h: int) -> Image.Image:
    """Return the exact 24fps frame from a loaded MP4 clip at clip_t seconds."""
    if not clip_frames:
        return Image.new("RGB", (target_w, target_h), (8, 12, 20))
    idx = max(0, min(len(clip_frames) - 1, int(round(clip_t * FPS))))
    img = clip_frames[idx]
    if img.size != (target_w, target_h):
        return img.resize((target_w, target_h), Image.Resampling.BILINEAR)
    return img


def render_seg3_hauser(
    t: float,
    seg_t: float,
    plates: dict[str, np.ndarray],
    clips: dict[str, list[Image.Image]],
    fonts: dict,
) -> Image.Image:
    """SEG-3: HAUSER MK-IV Correlator (3 Featured Station Cards -> 3 Live 1280x720 MP4 Video Inset Windows + Bottom Telemetry Deck)."""
    if seg_t < 15.47:
        active_idx = 0
        panel_tag = "3A • TITAN-MINOR N-24 VIDEO INSET"
        dt_sw = seg_t
    elif seg_t < 26.98:
        active_idx = 1
        panel_tag = "3B • CALLISTO DOME-4 VIDEO INSET"
        dt_sw = seg_t - 15.47
    else:
        active_idx = 2
        panel_tag = "3C • M-33 SALT FLATS VIDEO INSET"
        dt_sw = seg_t - 26.98

    frame = Image.new("RGB", (W, H), (5, 8, 14))
    draw = ImageDraw.Draw(frame)
    draw_master_top_bar(draw, fonts, "HAUSER MK-IV • WIDEBAND DX", panel_tag, t)

    topics = [
        {
            "color": (56, 189, 248),
            "tag": "INTERCEPT #1 • 3,890 kHz CW/USB",
            "big": "TITAN-MINOR N-24",
            "sub1": "METHANE TIDE TABLE TELEMETRY",
            "sub2": "SILT-STRIDERS DETUNING WHIP GUY-WIRES",
            "sub3": "◀ LEFT: LIVE CAM-N24 VIDEO INSET + WATERFALL",
        },
        {
            "color": (232, 184, 90),
            "tag": "INTERCEPT #2 • 11,410 kHz AM",
            "big": "RADIO CORRUGATED",
            "sub1": "CALLISTO DOME-4 NOODLE MARKET",
            "sub2": "ENGINEER HIT DIPOLE WITH BLOWTORCH",
            "sub3": "◀ LEFT: LIVE CAM-104 VIDEO INSET + AM SCOPE",
        },
        {
            "color": (94, 194, 126),
            "tag": "INTERCEPT #3 • 1,420.405 MHz H-I",
            "big": "M-33 DRIFT BUOY",
            "sub1": "700-YEAR MING DYNASTY TELEMETRY",
            "sub2": "AMMONIA SEA EVAPORATED 1580 CE",
            "sub3": "◀ LEFT: LIVE CAM-08 VIDEO INSET + LISSAJOUS",
        },
    ]
    draw_right_topic_stack(frame, draw, fonts, topics, active_idx, t)

    if active_idx == 0:
        # Left Panel 3A: 1280x720 Inset Video Clip (Buoy_bobbing_in_methane_sea) + Bottom CW Waterfall Shader
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "FEATURED STATION • 3,890 kHz TITAN-MINOR N-24",
            "",
            (56, 189, 248),
            is_video_insert=True,
            slot_tag="LIVE INSET • CAM-N24",
        )
        vid_w = ix1 - ix0
        vid_h = 720
        if clips.get("n24"):
            # Synced 1:1 with clip_3a audio starting at seg_t = 2.80s
            if seg_t < 2.80:
                clip_t = seg_t
            elif seg_t < 12.80:
                clip_t = seg_t - 2.80
            else:
                clip_t = 7.30 + (seg_t - 12.80)
            vid_img = get_clip_frame(clips["n24"], clip_t, vid_w, vid_h)
        else:
            vid_img = render_video_insert_frame(
                plates["n24_start"], plates["n24_end"], t, seg_t, 15.47, vid_w, vid_h, shader_mode="water_ripple"
            )
        frame.paste(vid_img, (ix0, iy0))
        draw.rectangle([ix0, iy0, ix1, iy0 + vid_h], outline=(56, 189, 248), width=2)

        # Bottom Deck (y=924..1360): Real-Time Waterfall Spectrogram Shader showing carrier bending during guy-wire rub
        by0 = iy0 + vid_h + 6
        wf_h = iy1 - by0
        wf_img = shader_waterfall_spectrogram(t, detune_active=(seg_t >= 6.8), mode="n24_cw", target_w=vid_w, target_h=wf_h)
        frame.paste(wf_img, (ix0, by0))
        draw.line([ix0, by0, ix1, by0], fill=(56, 189, 248), width=3)
        draw.rectangle([ix0 + 16, by0 + 14, ix0 + 910, by0 + 68], fill=(6, 10, 18), outline=(56, 189, 248), width=2)
        status_str = "WHIP ANTENNA DETUNING: Δf = -165 Hz [GUY-WIRE RUB]" if seg_t >= 6.8 else "3,890.0 kHz CW CARRIER • METHANE TIDE PACKETS"
        draw.text((ix0 + 30, by0 + 24), status_str, font=fonts["f28"], fill=(244, 63, 94) if seg_t >= 6.8 else (56, 189, 248))

    elif active_idx == 1:
        # Left Panel 3B: 1280x720 Inset Video Clip (Engineer_hits_antenna_with_blowtorch) + Bottom AM Overmodulation Shader
        local_t = seg_t - 15.47
        in_torch = local_t >= 4.5
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "FEATURED • 11,410 kHz RADIO CORRUGATED",
            "",
            (232, 184, 90),
            is_video_insert=True,
            slot_tag="LIVE INSET • CAM-104",
        )
        vid_w = ix1 - ix0
        vid_h = 720
        if clips.get("sw4"):
            # Synced 1:1 with clip_3b audio starting at local_t = 1.48s
            clip_t = local_t if local_t < 1.48 else (local_t - 1.48)
            vid_img = get_clip_frame(clips["sw4"], clip_t, vid_w, vid_h)
        else:
            vid_img = render_video_insert_frame(
                plates["sw4_start"], plates["sw4_end"], t, local_t, 11.51, vid_w, vid_h, shader_mode="bazaar_torch"
            )
        frame.paste(vid_img, (ix0, iy0))
        draw.rectangle([ix0, iy0, ix1, iy0 + vid_h], outline=(244, 63, 94) if in_torch else (232, 184, 90), width=3)

        # Bottom Deck (y=924..1360): Pentatonic AM Waterfall & Blowtorch Spike Shader
        by0 = iy0 + vid_h + 6
        wf_h = iy1 - by0
        wf_img = shader_waterfall_spectrogram(t, detune_active=in_torch, mode="bazaar_am", target_w=vid_w, target_h=wf_h)
        frame.paste(wf_img, (ix0, by0))
        draw.line([ix0, by0, ix1, by0], fill=(232, 184, 90), width=3)
        draw.rectangle([ix0 + 16, by0 + 14, ix0 + 930, by0 + 68], fill=(6, 10, 18), outline=(244, 63, 94) if in_torch else (232, 184, 90), width=2)
        b_txt = "PEAK OVERMODULATION: +18.4 dB [BLOWTORCH ON DIPOLE]" if in_torch else "11,410 kHz AM • PENTATONIC NIGHT-MARKET CARRIER"
        draw.text((ix0 + 30, by0 + 24), b_txt, font=fonts["f28"], fill=(244, 63, 94) if in_torch else (232, 184, 90))

    else:
        # Left Panel 3C: 1280x720 Inset Video Clip (Drift-buoy_resting_on_salt_flats) + Bottom Lissajous & Ming Decoder
        local_t = seg_t - 26.98
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "FEATURED • 1,420.405 MHz M-33 DRIFT BUOY",
            "",
            (94, 194, 126),
            is_video_insert=True,
            slot_tag="LIVE INSET • CAM-08",
        )
        vid_w = ix1 - ix0
        vid_h = 720
        if clips.get("m33"):
            clip_t = max(0.0, local_t - 0.35)
            vid_img = get_clip_frame(clips["m33"], clip_t, vid_w, vid_h)
        else:
            vid_img = shader_m33_lissajous_scope(t, vid_w, vid_h)
        frame.paste(vid_img, (ix0, iy0))
        draw.rectangle([ix0, iy0, ix1, iy0 + vid_h], outline=(94, 194, 126), width=2)

        # Bottom Deck (y=924..1360): Split between 3D Phosphor Lissajous Scope (left 410px) and Ming Packet Decoder (right)
        by0 = iy0 + vid_h + 6
        deck_h = iy1 - by0
        draw.rectangle([ix0, by0, ix1, iy1], fill=(6, 12, 16))
        draw.line([ix0, by0, ix1, by0], fill=(94, 194, 126), width=3)

        liss_w = 420
        liss_img = shader_m33_lissajous_scope(t, liss_w, deck_h)
        frame.paste(liss_img, (ix0, by0))
        draw.line([ix0 + liss_w, by0, ix0 + liss_w, iy1], fill=(94, 194, 126), width=3)

        tx0 = ix0 + liss_w + 26
        draw.text((tx0, by0 + 28), "PACKET ID: M33-BUOY-771", font=fonts["f34"], fill=(94, 194, 126))
        draw.text((tx0, by0 + 86), "LAUNCH EPOCH: 1368–1644 CE (MING)", font=fonts["f30"], fill=(195, 230, 210))
        draw.text((tx0, by0 + 150), "SMALL CRAFT WARNING: AMMONIA SEA", font=fonts["f32"], fill=(255, 255, 255))
        draw.text((tx0, by0 + 212), "SEA DEPTH: 0.00 m [EVAPORATED]", font=fonts["f32"], fill=(232, 184, 90))
        draw.text((tx0, by0 + 276), "RTG CORE : 204.2 K • CADENCE: 14.2s", font=fonts["f26"], fill=(160, 205, 185))
        draw.text((tx0, by0 + 332), "DOPPLER  : Δf = -180 kHz (1,420.4 MHz)", font=fonts["f26"], fill=(56, 189, 248))

    return apply_switch_glitch(frame, dt_sw, seed=300 + active_idx)



def render_seg4_euclid(
    t: float,
    seg_t: float,
    plates: dict[str, np.ndarray],
    fonts: dict,
) -> Image.Image:
    """SEG-4: EUCLID-9 Geometric Signal Detector (3 Right Proof Cards -> 4 Dynamic Left Panels)."""
    if seg_t < 7.2:
        active_idx = 0
        sub_mode = "4A-1 • NOISE-FLOOR HOUGH SHADER"
        dt_sw = seg_t
    elif seg_t < 19.1:
        active_idx = 0
        sub_mode = "4A-2 • CAM-VAT19 LIDAR SCAN"
        dt_sw = seg_t - 7.2
    elif seg_t < 30.8:
        active_idx = 1
        sub_mode = "4B • GEOMETOR I.34 PROOF SHADER"
        dt_sw = seg_t - 19.1
    else:
        active_idx = 2
        sub_mode = "4C • MUD-RAKE COTTER-PIN SIM"
        dt_sw = seg_t - 30.8

    frame = Image.new("RGB", (W, H), (5, 8, 14))
    draw = ImageDraw.Draw(frame)
    draw_master_top_bar(draw, fonts, "EUCLID-9 • GEOMETRIC SIGNAL DETECTOR", sub_mode, t)

    topics = [
        {
            "color": (56, 189, 248),
            "tag": "ACT I • THE SIGHTING (03:12 UTC)",
            "big": "BOOK I • PROP. 34",
            "sub1": "CALLISTO-SOUTH BRINE VAT 19",
            "sub2": "PARALLELOGRAM ABDC IN SALT CRUST",
            "sub3": "◀ LEFT: NOISE CORRELATOR & VAT-19 LIDAR",
        },
        {
            "color": (232, 184, 90),
            "tag": "ACT II • GEOMETRIC CONSTRUCTION (G.47)",
            "big": "AB || CD • AC || BD",
            "sub1": "DIAMETER BC BISECTS THE SLUDGE",
            "sub2": "CONGRUENT TRIANGLES: TRI ABC ≅ TRI DCB",
            "sub3": "◀ LEFT: GEOMETOR I.34 CONGRUENCE SHADER",
        },
        {
            "color": (244, 63, 94),
            "tag": "ACT III • CALLISTO WATER BOARD CLAIM",
            "big": "BROKEN COTTER PIN",
            "sub1": "MUD-RAKE #7 DRAGGED SIDEWAYS?",
            "sub2": "PRECISION: 0.0002 ARCSEC (Q.E.D.)",
            "sub3": "◀ LEFT: KINEMATIC RAKE DRAG SIMULATOR",
        },
    ]
    draw_right_topic_stack(frame, draw, fonts, topics, active_idx, t)

    if seg_t < 7.2:
        # Left Panel 4A-1: Wideband Noise-Floor Geometric Hough Correlator Shader
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw, fonts, "EUCLID SIGNAL DETECTOR • NOISE-FLOOR CORRELATOR", "SCANNING CALLISTO-SOUTH", (56, 189, 248)
        )
        sh_h = (iy1 - iy0) - 220
        sh_img = shader_euclid_hough_correlator(t, ix1 - ix0, sh_h)
        frame.paste(sh_img, (ix0, iy0))
        by0 = iy0 + sh_h
        draw.rectangle([ix0, by0, ix1, iy1], fill=(8, 14, 24))
        draw.line([ix0, by0, ix1, by0], fill=(56, 189, 248), width=3)
        draw.text((ix0 + 28, by0 + 22), "GEOMETRIC INTELLIGENCE FILTER: G-INDEX G.47", font=fonts["f36"], fill=(56, 189, 248))
        draw.text((ix0 + 28, by0 + 82), "ANGULAR PARALLELISM LOCK: Δθ = 0.0002 ARCSEC", font=fonts["f34"], fill=(255, 255, 255))
        draw.text((ix0 + 28, by0 + 140), "SOURCE LOCKING: UNMANNED BRINE EVAPORATION VAT 19...", font=fonts["f28"], fill=(232, 184, 90))

    elif seg_t < 19.1:
        # Left Panel 4A-2: Video Insert CAM-VAT19 Salt-Crust Parallelogram with LIDAR Laser Scan Shader
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "CAM-VAT19 • CALLISTO-SOUTH BRINE VAT 19 (FRAME 7)",
            "",
            (56, 189, 248),
            is_video_insert=True,
            slot_tag="VAT-19 OPTICAL + LIDAR",
        )
        vid_img = render_video_insert_frame(
            plates["vat19"],
            None,
            t,
            seg_t - 7.2,
            11.9,
            ix1 - ix0,
            iy1 - iy0,
            shader_mode="lidar_vat",
        )
        frame.paste(vid_img, (ix0, iy0))

        # Progressive corner reticles A, B, C, D locking onto the salt-crust parallelogram
        pA = (ix0 + 305, iy0 + 365)
        pB = (ix0 + 995, iy0 + 365)
        pC = (ix0 + 195, iy0 + 825)
        pD = (ix0 + 885, iy0 + 825)
        lock_p = min(1.0, max(0.0, (seg_t - 9.0) / 3.5))
        if lock_p > 0.05:
            draw.line([pA, pB], fill=(56, 189, 248), width=8)
            draw.line([pC, pD], fill=(56, 189, 248), width=8)
            draw.line([pA, pC], fill=(96, 165, 250), width=8)
            draw.line([pB, pD], fill=(96, 165, 250), width=8)
        for pt, lbl in [(pA, "A"), (pB, "B"), (pC, "C"), (pD, "D")]:
            draw.ellipse([pt[0] - 18, pt[1] - 18, pt[0] + 18, pt[1] + 18], outline=(232, 184, 90), width=4)
            draw.text((pt[0] + 24, pt[1] - 24), lbl, font=fonts["f42"], fill=(255, 255, 255))

    elif seg_t < 30.8:
        # Left Panel 4B: Pure Dark-Mode GEOMETOR Euclid I.34 (G.47) Vector Proof & Congruence Shader
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw, fonts, "GEOMETOR SCOPE • EUCLID I.34 (G.47) BISECTION", "TRI ABC ≅ TRI DCB", (232, 184, 90)
        )
        # Subtle dimmed Vat-19 texture at 22% under dark geometric proof canvas
        bg_vat = (plates["vat19"][100:1300, 200:1400].astype(np.float32) * 0.22).astype(np.uint8)
        bg_pil = Image.fromarray(bg_vat, mode="RGB").resize((ix1 - ix0, iy1 - iy0), Image.Resampling.BILINEAR)
        # Add pulsing green/blue triangle congruence shader inside ABC and DCB
        ov = Image.new("RGBA", (ix1 - ix0, iy1 - iy0), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(ov)

        pA = (280, 310)
        pB = (1040, 310)
        pC = (170, 860)
        pD = (930, 860)
        # Golden construction circles from G.47 (0338.g1.svg homage)
        for center_pt, rad_c in [(pA, 380), (pB, 560), (pC, 560), (pD, 380)]:
            odraw.ellipse(
                [center_pt[0] - rad_c, center_pt[1] - rad_c, center_pt[0] + rad_c, center_pt[1] + rad_c],
                outline=(232, 184, 90, 75),
                width=2,
            )

        # Animated interior congruence fill for triangles ABC and DCB
        pulse_a = int(55 + 35 * math.sin(t * 4.5))
        pulse_b = int(55 + 35 * math.cos(t * 4.5))
        odraw.polygon([pA, pB, pC], fill=(56, 189, 248, pulse_a))
        odraw.polygon([pD, pC, pB], fill=(94, 194, 126, pulse_b))

        # Outer parallel walls AB || CD and AC || BD
        odraw.line([pA, pB], fill=(96, 165, 250, 255), width=10)
        odraw.line([pC, pD], fill=(96, 165, 250, 255), width=10)
        odraw.line([pA, pC], fill=(56, 189, 248, 255), width=10)
        odraw.line([pB, pD], fill=(56, 189, 248, 255), width=10)

        # Equality tick marks (single green tick on AB/CD, double green tick on AC/BD)
        for mx, my in [((pA[0] + pB[0]) // 2, (pA[1] + pB[1]) // 2), ((pC[0] + pD[0]) // 2, (pC[1] + pD[1]) // 2)]:
            odraw.line([mx, my - 30, mx, my + 30], fill=(94, 194, 126, 255), width=7)
        for mx, my in [((pA[0] + pC[0]) // 2, (pA[1] + pC[1]) // 2), ((pB[0] + pD[0]) // 2, (pB[1] + pD[1]) // 2)]:
            for off in (-11, 11):
                odraw.line([mx - 28, my + off, mx + 28, my + off], fill=(94, 194, 126, 255), width=6)

        # Progressive solar-gold diameter BC
        diag_p = min(1.0, max(0.0, (seg_t - 19.5) / 2.2))
        cur_x = int(pB[0] + (pC[0] - pB[0]) * diag_p)
        cur_y = int(pB[1] + (pC[1] - pB[1]) * diag_p)
        odraw.line([pB, (cur_x, cur_y)], fill=(232, 184, 90, 255), width=12)

        comp_pil = Image.alpha_composite(bg_pil.convert("RGBA"), ov).convert("RGB")
        frame.paste(comp_pil, (ix0, iy0))

        for pt, lbl, ox, oy in [(pA, "A", -45, -55), (pB, "B", 22, -55), (pC, "C", -48, 16), (pD, "D", 22, 16)]:
            vx, vy = ix0 + pt[0], iy0 + pt[1]
            draw.ellipse([vx - 14, vy - 14, vx + 14, vy + 14], fill=(232, 184, 90), outline=(6, 10, 18), width=3)
            draw.text((vx + ox, vy + oy), lbl, font=fonts["f44"], fill=(255, 255, 255))

        # Bottom theorem banner inside Left Panel 4B
        draw.rectangle([ix0, iy1 - 155, ix1, iy1], fill=(8, 13, 22))
        draw.line([ix0, iy1 - 155, ix1, iy1 - 155], fill=(232, 184, 90), width=3)
        draw.text((ix0 + 28, iy1 - 135), "ALT. ANGLES ∠ABC = ∠BCD & ∠BCA = ∠CDB (I.29)", font=fonts["f32"], fill=(232, 184, 90))
        draw.text((ix0 + 28, iy1 - 75), "BY ASA (I.26): TRI ABC ≅ TRI DCB • BISECTED Q.E.D.", font=fonts["f34"], fill=(94, 194, 126))

    else:
        # Left Panel 4C: Motorized Mud-Rake #7 Kinematic Simulator & Sheared Cotter-Pin Cover-Up
        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw, fonts, "FORENSIC SIM • MUD-RAKE #7 SHEARED COTTER PIN", "WATER BOARD CLAIM", (244, 63, 94)
        )
        # Top half: Kinematic comparison (Actual 0.0002" Euclid I.34 vs Chaotic Broken Cotter-Pin Drag)
        draw.rectangle([ix0, iy0, ix1, iy0 + 680], fill=(9, 13, 22))
        # Grid lines
        for gx in range(ix0 + 60, ix1, 80):
            draw.line([gx, iy0 + 20, gx, iy0 + 660], fill=(20, 30, 46), width=1)
        for gy in range(iy0 + 40, iy0 + 660, 80):
            draw.line([ix0 + 20, gy, ix1 - 20, gy], fill=(20, 30, 46), width=1)

        draw.text((ix0 + 36, iy0 + 28), "SIMULATION A: BROKEN COTTER PIN #4B (CHAOTIC DRAG)", font=fonts["f28"], fill=(244, 63, 94))
        # Draw wobbling chaotic mud-rake path in red
        wob_pts = []
        for i in range(50):
            u = i / 49.0
            wx = ix0 + 80 + int(u * 1100)
            wy = iy0 + 190 + int(55 * math.sin(u * 19.0 + t * 5.0) + 30 * math.cos(u * 37.0 - t * 8.0))
            wob_pts.append((wx, wy))
        draw.line(wob_pts, fill=(244, 63, 94), width=6)

        draw.text((ix0 + 36, iy0 + 340), "OBSERVED VAT-19 TRACE: EUCLID I.34 (0.0002 ARCSEC)", font=fonts["f28"], fill=(56, 189, 248))
        # Draw razor-straight parallelogram + diameter in cyan/gold
        sa, sb, sc, sd = (ix0 + 160, iy0 + 420), (ix0 + 1120, iy0 + 420), (ix0 + 90, iy0 + 610), (ix0 + 1050, iy0 + 610)
        draw.line([sa, sb], fill=(56, 189, 248), width=6)
        draw.line([sc, sd], fill=(56, 189, 248), width=6)
        draw.line([sa, sc], fill=(56, 189, 248), width=6)
        draw.line([sb, sd], fill=(56, 189, 248), width=6)
        draw.line([sb, sc], fill=(232, 184, 90), width=6)

        # Bottom half: Official Water Board Cover-Up Stamp & Odds Readout
        by0 = iy0 + 685
        draw.rectangle([ix0, by0, ix1, iy1], fill=(18, 9, 14))
        draw.line([ix0, by0, ix1, by0], fill=(244, 63, 94), width=3)
        draw.text((ix0 + 32, by0 + 26), "CALLISTO WATER BOARD VERDICT:", font=fonts["f32"], fill=(232, 184, 90))
        draw.text((ix0 + 32, by0 + 82), "\"LOST A COTTER PIN & DRAGGED SIDEWAYS\"", font=fonts["f44"], fill=(255, 255, 255))
        draw.text((ix0 + 32, by0 + 162), "ODDS OF RANDOM COTTER-PIN I.34: 1 IN 10^14", font=fonts["f34"], fill=(56, 189, 248))
        draw.rounded_rectangle([ix0 + 32, by0 + 235, ix1 - 32, iy1 - 28], radius=10, fill=(38, 12, 20), outline=(244, 63, 94), width=3)
        draw.text((ix0 + 64, by0 + 258), "OPERATOR NOTE: \"IT'S ALWAYS A BROKEN COTTER PIN, FOLKS.\"", font=fonts["f30"], fill=(255, 215, 220))

    return apply_switch_glitch(frame, dt_sw, seed=400 + int(seg_t))


def render_seg5_closing(
    t: float,
    seg_t: float,
    closing_bg: np.ndarray,
    fonts: dict,
) -> Image.Image:
    """SEG-5: SCHED-9 Next Broadcast Console (0..9.2s) -> CAM-00D Horizon Sign-Off (9.2s..end)."""
    if seg_t < 9.2:
        # Sub-View 5A: SCHED-9 Next Broadcast Dossier Console (with 3 Right Cards + Left Base-8/Rhombus Shader)
        active_idx = 0 if seg_t < 5.0 else 1
        panel_tag = "5A-1 • TROJAN BASE-8 MATRIX" if active_idx == 0 else "5A-2 • ICE-HAULER RHOMBUS RADAR"
        dt_sw = seg_t if active_idx == 0 else (seg_t - 5.0)

        frame = Image.new("RGB", (W, H), (5, 8, 14))
        draw = ImageDraw.Draw(frame)
        draw_master_top_bar(draw, fonts, "SCHED-9 • NEXT BROADCAST DOSSIER", panel_tag, t)

        topics = [
            {
                "color": (56, 189, 248),
                "tag": "NEXT BROADCAST • 0430 UTC • 6,440 kHz",
                "big": "BASE-8 DUMPLINGS",
                "sub1": "TROJAN L4 NUMBERS STATION",
                "sub2": "OCTAL PLEAT-COUNT TELEMETRY",
                "sub3": "◀ LEFT: LIVE BASE-8 DECODER MATRIX",
            },
            {
                "color": (232, 184, 90),
                "tag": "GEOMETRIC ANOMALY ALERT • OUTER BELT",
                "big": "ICE-HAULER RHOMBUS",
                "sub1": "SUSPECTED EQUILATERAL FOUR-SIDED FIGURE",
                "sub2": "EUCLID DEF. I.22 • NON-RIGHT ANGLES",
                "sub3": "◀ LEFT: RHOMBUS WIREFRAME TARGET SCOPE",
            },
            {
                "color": (94, 194, 126),
                "tag": "QSL & CARRIER SIGN-OFF • SECTOR 9",
                "big": "GOR-9 • 14,285.7",
                "sub1": "YOUR EYE TO THE COSMOS",
                "sub2": "EAR TO THE VACUUM • ASTEROID 3-5-1",
                "sub3": "◀ NEXT: CAM-00D HORIZON SIGN-OFF",
            },
        ]
        draw_right_topic_stack(frame, draw, fonts, topics, active_idx, t)

        ix0, iy0, ix1, iy1 = draw_left_viewport_frame(
            draw,
            fonts,
            "TROJAN L4 SWARM • BASE-8 OCTAL DUMPLING CIPHER" if active_idx == 0 else "OUTER BELT RADAR • ICE-HAULER RHOMBUS TARGET",
            "6,440 kHz USB" if active_idx == 0 else "EUCLID DEF. I.22",
            (56, 189, 248) if active_idx == 0 else (232, 184, 90),
        )
        if active_idx == 0:
            # Base-8 Octal Matrix Shader & Dumpling Recipe Decoder
            sh_img = shader_magnetosphere_plasma(t * 1.4, ix1 - ix0, iy1 - iy0)
            frame.paste(sh_img, (ix0, iy0))
            draw.rectangle([ix0 + 40, iy0 + 40, ix1 - 40, iy1 - 40], fill=(6, 11, 20), outline=(56, 189, 248), width=3)
            oct_rows = [
                "0o74 0o12 0o55  ->  FLOUR: 370g / HYDRATION: 52%",
                "0o22 0o60 0o17  ->  CHIVE & BRINE SHRIMP FILLING",
                "0o31 0o44 0o20  ->  18 CRIMPS PER DUMPLING (BASE-8: 22)",
                "0o77 0o04 0o11  ->  STEAM AT 104 kPa FOR 0o07 MINUTES",
                "0o15 0o33 0o62  ->  CHILI OIL & BLACK VINEGAR DIP",
            ]
            draw.text((ix0 + 76, iy0 + 76), "INTERCEPTED TROJAN L4 OCTAL TRANSMISSION:", font=fonts["f34"], fill=(232, 184, 90))
            for r_i, line_str in enumerate(oct_rows):
                ly = iy0 + 175 + r_i * 155
                hi = r_i == (int(t * 2.5) % len(oct_rows))
                draw.rounded_rectangle([ix0 + 72, ly, ix1 - 72, ly + 125], radius=10, fill=(14, 26, 42) if hi else (9, 15, 24), outline=(56, 189, 248) if hi else (32, 50, 72), width=3 if hi else 2)
                draw.text((ix0 + 100, ly + 42), line_str, font=fonts["f32"], fill=(255, 255, 255) if hi else (165, 195, 220))
        else:
            # Rotating Equiangular/Equilateral Wireframe Rhombus Scope
            sh_img = shader_euclid_hough_correlator(t * 1.3, ix1 - ix0, iy1 - iy0)
            frame.paste(sh_img, (ix0, iy0))
            rcx, rcy = (ix0 + ix1) // 2, (iy0 + iy1) // 2 - 40
            ang = 0.25 * math.sin(t * 2.2)
            dx1, dy1 = int(420 * math.cos(ang)), int(420 * math.sin(ang))
            dx2, dy2 = int(-240 * math.sin(ang)), int(240 * math.cos(ang))
            r_pts = [(rcx + dx1, rcy + dy1), (rcx + dx2, rcy + dy2), (rcx - dx1, rcy - dy1), (rcx - dx2, rcy - dy2)]
            draw.polygon(r_pts, outline=(232, 184, 90), width=8)
            draw.line([r_pts[0], r_pts[2]], fill=(56, 189, 248), width=4)
            draw.line([r_pts[1], r_pts[3]], fill=(56, 189, 248), width=4)
            draw.rectangle([ix0 + 40, iy1 - 210, ix1 - 40, iy1 - 30], fill=(8, 12, 20), outline=(232, 184, 90), width=3)
            draw.text((ix0 + 70, iy1 - 185), "TARGET: BULK ICE-HAULER 'MV CRYOGENIC-9'", font=fonts["f36"], fill=(232, 184, 90))
            draw.text((ix0 + 70, iy1 - 115), "4 EQUAL SIDES (AB = BC = CD = DA) • DIAGONALS PERPENDICULAR", font=fonts["f28"], fill=(255, 255, 255))

        return apply_switch_glitch(frame, dt_sw, seed=500 + active_idx)

    # Sub-View 5B (seg_t >= 9.2s): Full-Screen CAM-00D Remote Horizon Sign-Off with Radial Wave Shader
    frame = Image.fromarray(closing_bg.copy(), mode="RGB")
    draw = ImageDraw.Draw(frame)
    draw_master_top_bar(draw, fonts, "CAM-00D • REMOTE HORIZON SIGN-OFF", "5B • CARRIER HORIZON", t)

    acx, acy = 1280, 495
    for wave_i in range(4):
        phase = ((t * 0.48 + wave_i * 0.25) % 1.0)
        r_wave = int(45 + phase * 360)
        alpha_w = 1.0 - phase
        if alpha_w > 0.15:
            col_w = (
                int(140 * alpha_w + 60),
                int(235 * alpha_w + 20),
                int(255 * alpha_w),
            )
            draw.ellipse([acx - r_wave, acy - r_wave, acx + r_wave, acy + r_wave], outline=col_w, width=3)

    draw.rounded_rectangle([320, 1045, W - 320, 1395], radius=18, fill=(5, 8, 15), outline=(232, 184, 90), width=4)

    t1 = "GOR-9: 14,285.7 kHz USB"
    w1 = draw.textlength(t1, font=fonts["f76"])
    draw.text(((W - w1) / 2, 1068), t1, font=fonts["f76"], fill=(255, 243, 196))

    t2 = "YOUR EYE TO THE COSMOS, EAR TO THE VACUUM."
    w2 = draw.textlength(t2, font=fonts["f48"])
    draw.text(((W - w2) / 2, 1174), t2, font=fonts["f48"], fill=(255, 232, 140))

    t3 = "FROM ASTEROID 3-5-1 IN SECTOR 9 • THIS IS GOR-9"
    w3 = draw.textlength(t3, font=fonts["f34"])
    draw.text(((W - w3) / 2, 1252), t3, font=fonts["f34"], fill=(232, 184, 90))

    t4 = "QSL VIA TITAN PACKET BUOY N-24 • MAIN BELT DEEP SPACE"
    w4 = draw.textlength(t4, font=fonts["f26"])
    draw.text(((W - w4) / 2, 1322), t4, font=fonts["f26"], fill=(180, 200, 220))

    return apply_switch_glitch(frame, seg_t - 9.2, seed=550)


def render_seg6_outro(
    t: float,
    seg_t: float,
    sat_plate: np.ndarray,
    closing_bg: np.ndarray,
    fonts: dict,
) -> Image.Image:
    """SEG-6 (20.0s End-Card & Credits Outro):
    - Right Half (x=1300..2560): Unobstructed dark galactic starfield reserved for YouTube End Cards.
    - Top-Left (x=48..1260, y=104..856): Live Orbital Satellite Downlink (O.R.S. 351) looking down at the GOR-9 tower.
    - Bottom-Left (x=48..1260, y=874..1396): Station Credits & Engineering Dossier + Harmonic Chime Visualizer.
    """
    # Base canvas: use darkened starfield from closing_bg on the right so YouTube End Cards pop cleanly
    bg_arr = closing_bg.astype(np.float32).copy()
    # Gently dim the tower in the center-right of closing_bg so the right half is pure deep-space starfield
    bg_arr[:, 1180:] *= 0.28
    bg_arr[:, :1180] *= 0.35
    frame = Image.fromarray(np.clip(bg_arr, 0, 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(frame)

    draw_master_top_bar(
        draw,
        fonts,
        "O.R.S. 351 • ORBITAL DOWNLINK",
        "END CARD & CREDITS • +3 kW / LIKE",
        t,
    )

    # Subtle, unobtrusive top header on the Right Half (leaving y=165..1380 100% clear for YouTube End Cards)
    rx0, rx1 = 1310, W - 48
    draw.text(
        (rx0 + 20, 112),
        "YOUTUBE.COM/@GOR-9-STATION • SUBSCRIPTION & ARCHIVE ARRAY",
        font=fonts["f26"],
        fill=(95, 130, 165),
    )
    # Minimal corner ticks around the YouTube End Card safe zone
    ec_x0, ec_y0, ec_x1, ec_y1 = 1310, 158, W - 48, H - 44
    tick_col = (36, 58, 82)
    for cx_t, cy_t, dx_t, dy_t in [
        (ec_x0, ec_y0, 32, 32),
        (ec_x1, ec_y0, -32, 32),
        (ec_x0, ec_y1, 32, -32),
        (ec_x1, ec_y1, -32, -32),
    ]:
        draw.line([(cx_t, cy_t), (cx_t + dx_t, cy_t)], fill=tick_col, width=2)
        draw.line([(cx_t, cy_t), (cx_t, cy_t + dy_t)], fill=tick_col, width=2)

    # =========================================================================
    # TOP-LEFT (x=48..1260, y=104..856): O.R.S. 351 ORBITAL SATELLITE DOWNLINK
    # =========================================================================
    sx0, sy0, sx1, sy1 = 48, 104, 1260, 856
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=12, fill=(7, 12, 20), outline=(56, 189, 248), width=3)
    draw.rectangle([sx0 + 3, sy0 + 3, sx1 - 3, sy0 + 54], fill=(12, 24, 40))
    draw.line([sx0, sy0 + 54, sx1, sy0 + 54], fill=(56, 189, 248), width=2)
    draw.ellipse([sx0 + 18, sy0 + 17, sx0 + 38, sy0 + 37], fill=(94, 194, 126))
    draw.text((sx0 + 50, sy0 + 12), "CAM-SAT09 • O.R.S. 351 ORBITAL DOWNLINK (ALT 42.8 km)", font=fonts["f28"], fill=(241, 245, 249))
    draw.text((sx1 - 220, sy0 + 14), "SYNC LOCKED", font=fonts["f24"], fill=(94, 194, 126))

    vw = (sx1 - sx0) - 8
    vh = (sy1 - sy0) - 58 - 108  # Leave 108px at bottom of card for +3 kW & Marzelvane telemetry bar
    vx0, vy0 = sx0 + 4, sy0 + 56

    # Slow orbital pan/zoom on cam_sat09_orbital_downlook.jpg
    prog = min(1.0, max(0.0, seg_t / 20.0))
    zoom = 1.0 + 0.05 * prog
    src_h, src_w = sat_plate.shape[:2]
    crop_w = int(src_w / zoom)
    crop_h = int(src_h / zoom)
    cx0 = int((src_w - crop_w) * (0.45 + 0.20 * math.sin(seg_t * 0.18)))
    cy0 = int((src_h - crop_h) * (0.35 - 0.15 * prog))
    cx0 = max(0, min(src_w - crop_w, cx0))
    cy0 = max(0, min(src_h - crop_h, cy0))

    sat_crop = sat_plate[cy0:cy0 + crop_h, cx0:cx0 + crop_w].copy()
    # Gentle harmonic shimmer on the glowing apex rings region (top-center of the tower)
    ring_shimmer = 1.0 + 0.12 * math.sin(t * 5.0)
    ry1 = int(crop_h * 0.36)
    rx0_s, rx1_s = int(crop_w * 0.25), int(crop_w * 0.72)
    sat_crop[:ry1, rx0_s:rx1_s] = np.clip(sat_crop[:ry1, rx0_s:rx1_s] * ring_shimmer, 0.0, 255.0)

    sat_pil = Image.fromarray(np.clip(sat_crop, 0, 255).astype(np.uint8), mode="RGB").resize(
        (vw, vh), Image.Resampling.BILINEAR
    )
    sat_draw = ImageDraw.Draw(sat_pil)
    sat_draw.rounded_rectangle([vw - 445, vh - 54, vw - 14, vh - 12], radius=6, fill=(6, 11, 20), outline=(232, 184, 90), width=2)
    sat_draw.text((vw - 428, vh - 45), "OUTPOST GOR-9 • 14,285.7 kHz USB", font=fonts["f24"], fill=(232, 184, 90))

    frame.paste(sat_pil, (vx0, vy0))

    # Telemetry Call-to-Action Bar inside bottom of Top-Left card (synced with Argon III-C narration)
    bar_y0 = vy0 + vh + 2
    draw.rectangle([vx0, bar_y0, sx1 - 4, sy1 - 4], fill=(9, 16, 28))
    draw.line([sx0, bar_y0, sx1, bar_y0], fill=(56, 189, 248), width=2)

    like_active = 1.0 <= seg_t <= 8.5
    sub_active = seg_t >= 5.8
    like_col = (94, 194, 126) if like_active else (56, 189, 248)
    sub_col = (232, 184, 90) if sub_active else (160, 185, 210)

    draw.ellipse([sx0 + 22, bar_y0 + 18, sx0 + 38, bar_y0 + 34], fill=like_col)
    draw.text(
        (sx0 + 50, bar_y0 + 12),
        "[+3.0 kW] LIKE INDICATION: +3 KILOWATTS TO REACTOR #2 (12 → 15 kW)",
        font=fonts["f28"],
        fill=like_col,
    )
    draw.ellipse([sx0 + 22, bar_y0 + 60, sx0 + 38, bar_y0 + 76], fill=sub_col)
    draw.text(
        (sx0 + 50, bar_y0 + 54),
        "[UPGRADE] SUBSCRIPTION: MARZELVANE EMITTER UPGRADE FUND [ACTIVE]",
        font=fonts["f28"],
        fill=sub_col,
    )

    # =========================================================================
    # BOTTOM-LEFT (x=48..1260, y=874..1396): STATION CREDITS & CHIME VISUALIZER
    # =========================================================================
    cx0_c, cy0_c, cx1_c, cy1_c = 48, 874, 1260, 1396
    draw.rounded_rectangle([cx0_c, cy0_c, cx1_c, cy1_c], radius=12, fill=(7, 11, 20), outline=(232, 184, 90), width=3)
    draw.rectangle([cx0_c + 3, cy0_c + 3, cx1_c - 3, cy0_c + 54], fill=(24, 20, 12))
    draw.line([cx0_c, cy0_c + 54, cx1_c, cy0_c + 54], fill=(232, 184, 90), width=2)
    draw.text(
        (cx0_c + 24, cy0_c + 12),
        "GOR-9 • SECTOR 9 BROADCAST CREDITS & ENGINEERING DOSSIER",
        font=fonts["f28"],
        fill=(232, 184, 90),
    )

    credits_rows = [
        ("EXECUTIVE PRODUCER & ARCHITECT", "phi ARCHITECT  •  @GOR-9-station", (255, 243, 196)),
        ("NIGHT-SHIFT VOICE & OPERATOR", "ARGON III-C  •  24.0 kHz CARRIER", (56, 189, 248)),
        ("GEOMETRIC SIGNAL DETECTOR", "GEOMETOR  •  EUCLID BOOK I PROP. 34 (G.47)", (94, 194, 126)),
        ("SHORTWAVE DX CORRELATOR", "HAUSER MK-IV  •  TURBO-ENCABULATOR #4", (232, 184, 90)),
        ("POWER & ORBITAL TELEMETRY", "REACTOR #2 (12 kW)  •  O.R.S. 351 RELAY", (195, 215, 235)),
    ]
    active_credit = int(seg_t / 3.8) % len(credits_rows)
    for idx_cr, (role_lbl, val_lbl, col_cr) in enumerate(credits_rows):
        ry = cy0_c + 68 + idx_cr * 86
        is_hi = idx_cr == active_credit
        bg_cr = (15, 25, 42) if is_hi else (10, 15, 26)
        out_cr = col_cr if is_hi else (28, 42, 62)
        draw.rounded_rectangle([cx0_c + 20, ry, cx0_c + 915, ry + 74], radius=8, fill=bg_cr, outline=out_cr, width=2)
        draw.text((cx0_c + 38, ry + 8), role_lbl, font=fonts["f24"], fill=(150, 175, 205))
        draw.text((cx0_c + 38, ry + 36), val_lbl, font=fonts["f28"], fill=col_cr if is_hi else (235, 242, 250))

    # Right sub-box inside Bottom-Left Credits Panel: Generated Harmonic Chime Visualizer
    vx0_c, vy0_c, vx1_c, vy1_c = cx0_c + 932, cy0_c + 68, cx1_c - 20, cy1_c - 22
    draw.rounded_rectangle([vx0_c, vy0_c, vx1_c, vy1_c], radius=8, fill=(9, 15, 26), outline=(56, 189, 248), width=2)
    draw.text((vx0_c + 18, vy0_c + 14), "HARMONIC CHIME", font=fonts["f24"], fill=(56, 189, 248))
    draw.text((vx0_c + 18, vy0_c + 44), "LYDIAN 5THS", font=fonts["f24"], fill=(232, 184, 90))

    # 8 animated harmonic bell bars dancing softly to the 0.62s chime step cadence
    n_bars = 8
    bw_c = 22
    gap_c = 8
    base_by = vy1_c - 52
    max_bh = 250
    for b_i in range(n_bars):
        bx = vx0_c + 20 + b_i * (bw_c + gap_c)
        note_ph = (seg_t - 0.25 - b_i * 0.15) % 1.85
        env_bar = math.exp(-max(0.0, note_ph) / 0.55) if note_ph >= 0 else 0.2
        osc = 0.25 + 0.75 * env_bar * (0.6 + 0.4 * math.sin(t * (3.2 + b_i * 0.7)))
        bh_val = int(max(18, min(max_bh, max_bh * osc)))
        b_col = (56, 189, 248) if b_i % 2 == 0 else (232, 184, 90)
        draw.rectangle([bx, base_by - bh_val, bx + bw_c, base_by], fill=b_col)

    draw.text((vx0_c + 18, vy1_c - 38), "432 / 528 Hz", font=fonts["f24"], fill=(94, 194, 126))

    return apply_switch_glitch(frame, seg_t, seed=600)


def main() -> None:
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    FLOW_DIR.mkdir(parents=True, exist_ok=True)
    master_wav = EP_DIR / "audio" / "gor9_ep01_full_master.wav"
    out_mp4 = EP_DIR / "gor9_ep01.mp4"

    timeline = json.loads((EP_DIR / "script" / "ep01_timeline.json").read_text(encoding="utf-8"))
    duration = float(timeline["total_duration_sec"])
    total_frames = int(duration * FPS)

    seg_starts = {item["id"]: float(item["start_sec"]) for item in timeline["segments"]}
    t_seg1 = seg_starts.get("seg1_weather", 17.32)
    t_seg2 = seg_starts.get("seg2_econ", 40.73)
    t_seg3 = seg_starts.get("seg3_hauser", 64.99)
    t_seg4 = seg_starts.get("seg4_euclid", 102.74)
    t_seg5 = seg_starts.get("seg5_signoff", 141.36)
    t_seg6 = seg_starts.get("seg6_outro", 159.12)

    catalog = json.loads((SFX_DIR / "sfx_catalog.json").read_text(encoding="utf-8"))
    vis_env_30 = catalog["cam00_boot_visual_envelope_30fps"]
    ding_lock_sec = float(catalog.get("ding_lock_time_sec", 4.30))

    print(f"Rendering full episode (19-panel shader + end-card edition): {total_frames} frames ({duration:.2f}s @ {FPS}fps, {W}x{H}) -> {out_mp4}")

    fonts = {
        "f24": load_font(24, bold=True),
        "f26": load_font(26, bold=True),
        "f28": load_font(28, bold=True),
        "f30": load_font(30, bold=True),
        "f32": load_font(32, bold=True),
        "f34": load_font(34, bold=True),
        "f36": load_font(36, bold=True),
        "f38": load_font(38, bold=True),
        "f42": load_font(42, bold=True),
        "f44": load_font(44, bold=True),
        "f48": load_font(48, bold=True),
        "f54": load_font(54, bold=True),
        "f68": load_font(68, bold=True),
        "f76": load_font(76, bold=True),
        "f84": load_font(84, bold=True),
        "f120": load_font(120, bold=True),
    }

    # Load CAM-00A rig
    sky_w, sky_h = int(W * 1.12), int(H * 1.12)
    sky_img = Image.open(PLATES_DIR / "cam00_sky_plate_clean.jpg").convert("RGB").resize(
        (sky_w, sky_h), Image.Resampling.LANCZOS
    )
    sky_arr = np.asarray(sky_img, dtype=np.float32)

    fg_off_img = Image.open(COMP_DIR / "cam00_tower_fg_off.png").convert("RGBA")
    beacons_img = Image.open(COMP_DIR / "cam00_tower_beacons_only.png").convert("RGBA")
    meta = json.loads((COMP_DIR / "cam00_beacons_meta.json").read_text(encoding="utf-8"))
    beacons_meta = meta["beacons"]
    neon_meta = meta["neon"]

    fg_off_arr = np.asarray(fg_off_img, dtype=np.float32)
    alpha_off = fg_off_arr[..., 3:4] / 255.0
    premult_off = fg_off_arr[..., :3] * alpha_off

    beacons_arr = np.asarray(beacons_img, dtype=np.float32)
    alpha_b_all = beacons_arr[..., 3:4] / 255.0
    premult_b_all = beacons_arr[..., :3] * alpha_b_all

    ring_layers = []
    for idx in range(1, 5):
        r_img = Image.open(COMP_DIR / f"cam00_ring_{idx}.png").convert("RGBA")
        r_arr = np.asarray(r_img, dtype=np.float32)
        r_alpha = r_arr[..., 3:4] / 255.0
        ring_layers.append((idx, (r_arr[60:515, 750:1810, :3] * r_alpha[60:515, 750:1810])))

    # 4 background asteroids moving in 4 DIFFERENT directions, with #1 moving VERY FAST across the sky!
    ast_specs = [
        (2, (155, 125), 2140.0, 185.0, -14.5, 4.2, 0.84),    # Upper-right -> lower-left
        (4, (115, 102), 230.0, 560.0, 16.0, -5.5, 0.80),     # Lower-left  -> upper-right
        (3, (84, 85), 480.0, 210.0, 11.5, 6.8, 0.76),        # Upper-left  -> lower-right
        (1, (72, 72), 2480.0, 470.0, -195.0, -18.5, 0.94),   # VERY FAST bolide streaking right -> upper-left!
    ]
    asteroid_sprites = []
    for sp_idx, sz, x0, y0, vx, vy, br in ast_specs:
        sp_path = COMP_DIR / f"asteroid_sprite_{sp_idx}.png"
        if sp_path.exists():
            sp_img = Image.open(sp_path).convert("RGBA").resize(sz, Image.Resampling.LANCZOS)
            sp_arr = np.asarray(sp_img, dtype=np.float32)
            sp_a = sp_arr[..., 3:4] / 255.0
            sp_pre = sp_arr[..., :3] * sp_a * br
            asteroid_sprites.append((sz[0], sz[1], x0, y0, vx, vy, sp_a, sp_pre))

    # Load Orbital Relay Satellite (O.R.S. 351) sprite for steady synchronous orbit in Opening Scene (CAM-00A)
    sat_sprite_path = COMP_DIR / "satellite_ors351_sprite.png"
    sat_sprite_data = None
    if sat_sprite_path.exists():
        sat_sz = (154, 110)
        sat_s_img = Image.open(sat_sprite_path).convert("RGBA").resize(sat_sz, Image.Resampling.LANCZOS)
        sat_s_arr = np.asarray(sat_s_img, dtype=np.float32)
        sat_s_a = sat_s_arr[..., 3:4] / 255.0
        sat_s_pre = sat_s_arr[..., :3] * sat_s_a * 0.90
        sat_sprite_data = (sat_sz[0], sat_sz[1], 280, 130, sat_s_a, sat_s_pre)

    schedules = {
        "mast_top": (2.30, 0.15),
        "booth_left": (3.10, 1.25),
        "booth_right": (2.75, 2.05),
    }

    def load_plate(name: str) -> np.ndarray:
        p = EP_PLATES_DIR / name if (EP_PLATES_DIR / name).exists() else PLATES_DIR / name
        return np.asarray(
            Image.open(p).convert("RGB").resize((W, H), Image.Resampling.LANCZOS),
            dtype=np.float32,
        )

    plates = {
        "cam00b_wide": load_plate("cam00b_canyon_rim_wide.jpg"),
        "desk01": load_plate("desk01_hauser_receiver.jpg"),
        "cam02_start": load_plate("cam02_relay_storm_start.jpg"),
        "cam02_end": load_plate("cam02_relay_storm_end.jpg"),
        "cam44k_start": load_plate("cam44k_quarry_start.jpg"),
        "cam44k_end": load_plate("cam44k_quarry_end.jpg"),
        "cam00c_barracks": load_plate("cam00c_tower_downlook_barracks.jpg"),
        "n24_start": load_plate("cam_n24_shallows_start.jpg"),
        "n24_end": load_plate("cam_n24_shallows_end.jpg"),
        "sw4_start": load_plate("cam_sw4_bazaar_start.jpg"),
        "sw4_end": load_plate("cam_sw4_bazaar_end.jpg"),
        "vat19": load_plate("cam_vat19_parallelogram.jpg"),
        "sat09": load_plate("cam_sat09_orbital_downlook.jpg"),
    }
    closing_bg = np.asarray(
        Image.open(PLATES_DIR / "cam00d_closing_horizon_rings.jpg").convert("RGB").resize((W, H), Image.Resampling.LANCZOS),
        dtype=np.uint8,
    )

    clips_dir = EP_DIR / "clips"

    def load_clip_frames(pattern: str, w_clip: int = 1282, h_clip: int = 720) -> list[Image.Image]:
        matches = sorted(clips_dir.glob(pattern))
        if not matches:
            return []
        raw = subprocess.check_output(
            [
                "ffmpeg", "-v", "quiet",
                "-i", str(matches[0]),
                "-vf", f"scale={w_clip}:{h_clip}",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
            ]
        )
        frame_bytes = w_clip * h_clip * 3
        n_f = len(raw) // frame_bytes
        print(f"  [clip] loaded {matches[0].name} ({n_f} frames @ {w_clip}x{h_clip})")
        return [
            Image.frombytes("RGB", (w_clip, h_clip), raw[i * frame_bytes:(i + 1) * frame_bytes])
            for i in range(n_f)
        ]

    clips = {
        "n24": load_clip_frames("Buoy_bobbing*.mp4"),
        "sw4": load_clip_frames("Engineer_hits_antenna*.mp4"),
        "m33": load_clip_frames("Drift-buoy*.mp4"),
    }

    rng = np.random.default_rng(3519)
    snow_bank = build_snow_bank(rng, count=8)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(master_wav),
        "-c:a", "aac",
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        "-shortest",
        "-vf", "fps=30,setsar=1:1,noise=alls=2:allf=t,format=yuv420p",
        "-vsync", "cfr",
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "fast",
        "-profile:v", "high",
        "-level:v", "5.1",
        "-crf", "16",
        "-maxrate", "16M",
        "-bufsize", "32M",
        "-g", "30",
        "-keyint_min", "30",
        "-sc_threshold", "0",
        "-bf", "2",
        "-flags", "+cgop",
        "-colorspace", "bt709",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        "-color_range", "tv",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    max_dx = sky_w - W
    max_dy = sky_h - H

    for frame_idx in range(total_frames):
        t = frame_idx / FPS

        if t < t_seg1:
            # SEG-0: 3 Exterior/Booth Camera Switches (CAM-00A Cliff Wide -> CAM-00B Canyon Rim -> DESK-01 Booth)
            if t < 11.2:
                cx = int(max_dx * (0.85 - 0.70 * (t / max(t_seg1, 1.0))))
                cy = int(max_dy * (0.30 + 0.35 * math.sin(t * 0.08)))
                cx = max(0, min(max_dx, cx))
                cy = max(0, min(max_dy, cy))
                sky_crop = sky_arr[cy:cy + H, cx:cx + W].copy()

                # Composite 4 multi-directional background asteroids (with #1 streaking very fast across the sky)
                for sw, sh, ax0, ay0, avx, avy, sp_a, sp_pre in asteroid_sprites:
                    ax = int(round(ax0 + avx * t))
                    ay = int(round(ay0 + avy * t))
                    x_s0, y_s0 = max(0, ax), max(0, ay)
                    x_s1, y_s1 = min(W, ax + sw), min(H, ay + sh)
                    if x_s1 > x_s0 and y_s1 > y_s0:
                        sx0_i, sy0_i = x_s0 - ax, y_s0 - ay
                        sx1_i, sy1_i = sx0_i + (x_s1 - x_s0), sy0_i + (y_s1 - y_s0)
                        roi = sky_crop[y_s0:y_s1, x_s0:x_s1]
                        sky_crop[y_s0:y_s1, x_s0:x_s1] = (
                            roi * (1.0 - sp_a[sy0_i:sy1_i, sx0_i:sx1_i]) + sp_pre[sy0_i:sy1_i, sx0_i:sx1_i]
                        )

                # Composite Orbital Relay Satellite (O.R.S. 351) in a STEADY synchronous position in orbit above the asteroid
                if sat_sprite_data is not None:
                    sat_w, sat_h, sat_x0, sat_y0, sat_a, sat_pre = sat_sprite_data
                    sx_p = sat_x0 + int(round(1.5 * math.sin(t * 0.9)))
                    sy_p = sat_y0 + int(round(1.2 * math.cos(t * 1.1)))
                    roi_s = sky_crop[sy_p:sy_p + sat_h, sx_p:sx_p + sat_w]
                    sky_crop[sy_p:sy_p + sat_h, sx_p:sx_p + sat_w] = roi_s * (1.0 - sat_a) + sat_pre

                comp = sky_crop * (1.0 - alpha_off) + premult_off

                apex_slice = comp[60:515, 750:1810]
                for r_idx, r_premult in ring_layers:
                    w_ring = ring_wave_intensity(t, r_idx, ding_lock_sec)
                    if w_ring > 0.01:
                        apex_slice = np.clip(apex_slice + r_premult * w_ring, 0.0, 255.0)
                comp[60:515, 750:1810] = apex_slice

                if t >= 1.15:
                    gor_w = min(1.0, (t - 1.15) / 0.25) * (0.95 + 0.05 * math.sin(t * 24.0))
                    gp = neon_meta["gor_prefix"]
                    gx0, gy0, gw, gh = gp["x"], gp["y"], gp["w"], gp["h"]
                    comp[gy0:gy0 + gh, gx0:gx0 + gw] = np.clip(
                        comp[gy0:gy0 + gh, gx0:gx0 + gw] + premult_b_all[gy0:gy0 + gh, gx0:gx0 + gw] * gor_w,
                        0.0,
                        255.0,
                    )
                    n9_w = neon_nine_pulse(t)
                    if n9_w > 0.01:
                        gn = neon_meta["gor_nine"]
                        nx0, ny0, nw, nh = gn["x"], gn["y"], gn["w"], gn["h"]
                        comp[ny0:ny0 + nh, nx0:nx0 + nw] = np.clip(
                            comp[ny0:ny0 + nh, nx0:nx0 + nw] + premult_b_all[ny0:ny0 + nh, nx0:nx0 + nw] * n9_w,
                            0.0,
                            255.0,
                        )

                for b in beacons_meta:
                    bid = b["id"]
                    period, ph_off = schedules.get(bid, (2.8, 0.0))
                    p = beacon_pulse(t, period, ph_off)
                    if p > 0.01:
                        x0, y0, bw, bh = b["x"], b["y"], b["w"], b["h"]
                        x1, y1 = min(W, x0 + bw), min(H, y0 + bh)
                        b_pre = premult_b_all[y0:y1, x0:x1] * p
                        comp[y0:y1, x0:x1] = np.clip(comp[y0:y1, x0:x1] + b_pre, 0.0, 255.0)

                idx_30 = int(t * 30)
                s = vis_env_30[idx_30] if idx_30 < len(vis_env_30) else 0.0
                if s > 0.01:
                    desat = min(1.0, s * 1.1)
                    if desat > 0.05:
                        luma = comp[..., 0:1] * 0.299 + comp[..., 1:2] * 0.587 + comp[..., 2:3] * 0.114
                        comp = comp * (1.0 - desat) + luma * desat
                    n_tears = int(6 + 20 * s)
                    for _ in range(n_tears):
                        by = int(rng.integers(80, H - 50))
                        bh = int(rng.integers(8, 42))
                        shift_x = int(rng.integers(-150, 151) * (s ** 1.2))
                        comp[by:by + bh] = np.roll(comp[by:by + bh], shift_x, axis=1)
                    snow_frame = snow_bank[frame_idx % len(snow_bank)]
                    sy_shift = int(rng.integers(0, H))
                    snow_rolled = np.roll(snow_frame, sy_shift, axis=0)
                    snow_op = min(0.88, (s ** 0.85) * 0.90)
                    comp = comp * (1.0 - snow_op) + snow_rolled * snow_op

                pil_frame = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8), mode="RGB")
                draw = ImageDraw.Draw(pil_frame)
                # Subtle pulsing cyan transponder beacon on the dish of the steady O.R.S. 351 satellite
                if sat_sprite_data is not None and t >= ding_lock_sec:
                    sat_w, sat_h, sat_x0, sat_y0, _, _ = sat_sprite_data
                    bc_x = sat_x0 + int(sat_w * 0.34)
                    bc_y = sat_y0 + int(sat_h * 0.82)
                    if math.sin(t * 5.5) > 0.0:
                        draw.ellipse([bc_x - 3, bc_y - 3, bc_x + 3, bc_y + 3], fill=(56, 189, 248))

                draw_master_top_bar(draw, fonts, "CAM-00A • HIGH BASALT SHELF TOWER", "0A • CLIFF PRECIPICE", t)
                draw.rounded_rectangle([48, H - 210, 980, H - 44], radius=10, fill=(6, 10, 18), outline=(232, 184, 90), width=3)
                draw.text((74, H - 190), "HIGH BASALT SHELF", font=fonts["f44"], fill=(232, 184, 90))
                draw.text((74, H - 130), "ASTEROID 3-5-1 • ELEVATED TOWER BOOTH", font=fonts["f30"], fill=(241, 245, 249))
                draw.text((74, H - 86), "50 kW CARRIER • 14,285.7 kHz UPPER SIDEBAND", font=fonts["f26"], fill=(56, 189, 248))
                if abs(t - 6.2) < 0.03:
                    pil_frame.save(RENDERS_DIR / "preview_seg0_sat.jpg", quality=92)

            elif t < 14.3:
                # Camera Switch 0B: CAM-00B Canyon Rim Wide / Telephoto Push-In on the Booth
                pil_frame = render_video_insert_frame(plates["cam00b_wide"], None, t, t - 11.2, 3.1, W, H)
                draw = ImageDraw.Draw(pil_frame)
                draw_master_top_bar(draw, fonts, "CAM-00B • ACHERON CANYON RIM OVERLOOK", "0B • CANYON TELEPHOTO", t)
                draw.rounded_rectangle([48, H - 210, 1040, H - 44], radius=10, fill=(6, 10, 18), outline=(56, 189, 248), width=3)
                draw.text((74, H - 190), "14,285.7 kHz USB [LOCKED]", font=fonts["f44"], fill=(56, 189, 248))
                draw.text((74, H - 130), "SECTOR 9 • PALLAS–JUNO MAIN-BELT CORRIDOR", font=fonts["f30"], fill=(241, 245, 249))
                draw.text((74, H - 86), "ELEVATED OCTAGONAL BOOTH • NIGHT SHIFT ON AIR", font=fonts["f26"], fill=(232, 184, 90))
                pil_frame = apply_switch_glitch(pil_frame, t - 11.2, seed=11)

            else:
                # Camera Switch 0C: DESK-01 Interior Elevated Booth Receiver Desk + Live Scope Shader
                pil_frame = render_video_insert_frame(plates["desk01"], None, t, t - 14.3, 3.0, W, H)
                draw = ImageDraw.Draw(pil_frame)
                draw_master_top_bar(draw, fonts, "DESK-01 • INTERIOR ELEVATED TOWER BOOTH", "0C • OPERATOR CONSOLE", t)
                draw.rounded_rectangle([48, H - 210, 1060, H - 44], radius=10, fill=(6, 10, 18), outline=(94, 194, 126), width=3)
                draw.text((74, H - 190), "0400 GALACTIC COORDINATED", font=fonts["f44"], fill=(94, 194, 126))
                draw.text((74, H - 130), "BOOTH DESK-01 • HAUSER MK-IV & EUCLID-9 ONLINE", font=fonts["f30"], fill=(241, 245, 249))
                draw.text((74, H - 86), "TRANSFERRING TO TELEMETRY CONSOLE DECK...", font=fonts["f26"], fill=(232, 184, 90))
                pil_frame = apply_switch_glitch(pil_frame, t - 14.3, seed=14)

        elif t < t_seg2:
            seg_t = t - t_seg1
            pil_frame = render_seg1_meteo(t, seg_t, plates, fonts)
            if abs(seg_t - 3.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg1_panel1a.jpg", quality=92)
            elif abs(seg_t - 11.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg1_meteo.jpg", quality=92)
            elif abs(seg_t - 19.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg1_panel1c.jpg", quality=92)

        elif t < t_seg3:
            seg_t = t - t_seg2
            pil_frame = render_seg2_econ(t, seg_t, plates, fonts)
            if abs(seg_t - 4.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg2_panel2a.jpg", quality=92)
            elif abs(seg_t - 12.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg2_econ.jpg", quality=92)
            elif abs(seg_t - 19.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg2_panel2c.jpg", quality=92)

        elif t < t_seg4:
            seg_t = t - t_seg3
            pil_frame = render_seg3_hauser(t, seg_t, plates, clips, fonts)
            if abs(seg_t - 7.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg3_panel3a.jpg", quality=92)
            elif abs(seg_t - 20.3) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg3_hauser.jpg", quality=92)
            elif abs(seg_t - 31.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg3_panel3c.jpg", quality=92)

        elif t < t_seg5:
            seg_t = t - t_seg4
            pil_frame = render_seg4_euclid(t, seg_t, plates, fonts)
            if abs(seg_t - 3.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg4_panel4a1.jpg", quality=92)
            elif abs(seg_t - 24.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg4_euclid.jpg", quality=92)
            elif abs(seg_t - 34.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg4_panel4c.jpg", quality=92)

        elif t < t_seg6:
            seg_t = t - t_seg5
            pil_frame = render_seg5_closing(t, seg_t, closing_bg, fonts)
            if abs(seg_t - 3.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg5_panel5a.jpg", quality=92)
            elif abs(seg_t - 13.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg5_sched.jpg", quality=92)

        else:
            seg_t = t - t_seg6
            pil_frame = render_seg6_outro(t, seg_t, plates["sat09"], closing_bg, fonts)
            if abs(seg_t - 7.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg6_outro.jpg", quality=92)

        proc.stdin.write(pil_frame.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"Done! Full episode saved to: {out_mp4}")


if __name__ == "__main__":
    main()
