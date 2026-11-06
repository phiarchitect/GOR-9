#!/usr/bin/env python3
"""Render the complete 2560x1440 (16:9 QHD) GOR-9 Broadcast 01 Video using the HTML Console Interfaces.

Features:
- Uses the actual 2560x1440 HTML console renders from `docs/` (`propagation.html`, `index.html`,
  `station.html`, `bogey-detector.html`, `euclidean-detector.html`) captured in `console_plates/`.
- Strict 16:9 YouTube Bottom Control Safe-Zone: all console panels, lower-third banners, proof steps,
  and end-screen cards sit above y = 1220 (top ~84% of the 1440p frame). The bottom safe zone
  (y = 1268..1440) renders a non-essential brushed-metal ATC rack desk bezel & ambient carrier trace
  so YouTube popup player controls never obscure any console content.
- Live 24fps viewport compositing inside the HTML consoles:
  - Live `.mp4` video feeds (`Buoy_bobbing*.mp4`, `Engineer_hits_antenna*.mp4`) inside Hauser MK-IV
    `#station-video` and `station.html` `#dos-video`.
  - Progressive 10-frame animated SSTV eQSL GIFs inside `#qsl-gif-img`.
  - Scrolling phosphor waterfall inside Hauser MK-IV `#waterfall-canvas`.
  - Live 8-frame animated `bogey_01_cylinder.gif` trail-cam burst inside Bogey-9 `#burstGifView`.
  - Pulsing corner-bracket focus highlights synced to each spoken segment and sub-step.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATION_DIR = ROOT / "station"
DOCS_DIR = ROOT / "docs"
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
PLATES_DIR = STATION_DIR / "plates"
EP_PLATES_DIR = EP_DIR / "plates"
CONSOLE_PLATES_DIR = EP_DIR / "console_plates"
COMP_DIR = STATION_DIR / "rig"
RENDERS_DIR = EP_DIR / "previews"

W, H = 2560, 1440
FPS = 24


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
    """Apply a crisp 0.18s CRT relay-switch horizontal sync & RGB split glitch when console views shift."""
    if dt_since_switch < 0.0 or dt_since_switch > 0.18:
        return frame
    strength = 1.0 - (dt_since_switch / 0.18)
    arr = np.asarray(frame, dtype=np.uint8).copy()
    rng = np.random.default_rng(seed + int(dt_since_switch * 1000))
    for _ in range(int(4 + 8 * strength)):
        by = int(rng.integers(90, 1200))
        bh = int(rng.integers(8, 32))
        shift = int(rng.integers(-60, 61) * strength)
        arr[by:by + bh, 24:W - 24] = np.roll(arr[by:by + bh, 24:W - 24], shift, axis=1)
    split = max(1, int(8 * strength))
    arr[90:1220, 24:W - 24, 0] = np.roll(arr[90:1220, 24:W - 24, 0], split, axis=1)
    arr[90:1220, 24:W - 24, 2] = np.roll(arr[90:1220, 24:W - 24, 2], -split, axis=1)
    return Image.fromarray(arr, mode="RGB")


def draw_safezone_chassis_bezel(
    draw: ImageDraw.ImageDraw,
    t: float,
    accent_col: tuple[int, int, int] = (240, 184, 73),
) -> None:
    """Draw a subtle, non-essential brushed-metal ATC rack desk bezel in the bottom 16:9 YouTube safe zone (y=1272..1440).

    Contains zero essential text or controls so YouTube's popup scrub bar and player buttons can cover it freely.
    """
    y0 = 1272
    draw.line([0, y0, W, y0], fill=(32, 45, 68), width=2)
    draw.rectangle([0, y0 + 2, W, H], fill=(6, 9, 15))
    # Subtle horizontal brushed rack ribs
    for ry in range(y0 + 18, H - 12, 22):
        draw.line([48, ry, W - 48, ry], fill=(11, 16, 26), width=1)
    # Decorative rack bolts on left and right
    for bx in (26, W - 26):
        for by in (y0 + 36, y0 + 128):
            draw.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(16, 23, 36), outline=(42, 56, 82), width=2)
    # Subtle decorative carrier heartbeat wave in the center of the desk rail
    pts = []
    mid_y = y0 + 84
    for x in range(680, W - 680, 16):
        u = (x - 680) / (W - 1360)
        env = math.sin(u * math.pi)
        wy = mid_y + int(10.0 * env * math.sin(x * 0.035 - t * 6.5) * math.cos(x * 0.011 + t * 2.1))
        pts.append((x, wy))
    if len(pts) > 1:
        dim_col = (max(18, accent_col[0] // 4), max(24, accent_col[1] // 4), max(32, accent_col[2] // 4))
        draw.line(pts, fill=dim_col, width=2)


def draw_focus_brackets(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    t: float,
    label: str | None = None,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None,
) -> None:
    """Draw pulsing corner brackets around the active panel on an HTML console."""
    x0, y0, x1, y1 = box
    pulse = 0.65 + 0.35 * math.sin(t * 6.0)
    col = (
        int(min(255, color[0] * (0.75 + 0.25 * pulse))),
        int(min(255, color[1] * (0.75 + 0.25 * pulse))),
        int(min(255, color[2] * (0.75 + 0.25 * pulse))),
    )
    # Outer subtle border
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, outline=col, width=2)
    # Corner L-brackets
    cl = 26
    w = 4
    # Top-left
    draw.line([x0 - 2, y0 - 2, x0 + cl, y0 - 2], fill=col, width=w)
    draw.line([x0 - 2, y0 - 2, x0 - 2, y0 + cl], fill=col, width=w)
    # Top-right
    draw.line([x1 - cl, y0 - 2, x1 + 2, y0 - 2], fill=col, width=w)
    draw.line([x1 + 2, y0 - 2, x1 + 2, y0 + cl], fill=col, width=w)
    # Bottom-left
    draw.line([x0 - 2, y1 + 2, x0 + cl, y1 + 2], fill=col, width=w)
    draw.line([x0 - 2, y1 - cl, x0 - 2, y1 + 2], fill=col, width=w)
    # Bottom-right
    draw.line([x1 - cl, y1 + 2, x1 + 2, y1 + 2], fill=col, width=w)
    draw.line([x1 + 2, y1 - cl, x1 + 2, y1 + 2], fill=col, width=w)

    if label and font is not None:
        tw = int(draw.textlength(label, font=font)) + 20
        bx0 = min(x1 - tw, max(x0 + 8, x1 - tw - 8))
        by0 = max(6, y0 - 28)
        draw.rounded_rectangle([bx0, by0, bx0 + tw, by0 + 26], radius=4, fill=(8, 12, 22), outline=col, width=2)
        draw.text((bx0 + 10, by0 + 4), label, font=font, fill=col)


def load_gif_frames(gif_path: Path, size: tuple[int, int]) -> list[Image.Image]:
    if not gif_path.exists():
        return []
    im = Image.open(gif_path)
    frames = []
    try:
        while True:
            frames.append(im.convert("RGB").resize(size, Image.Resampling.NEAREST))
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return frames


def composite_mk4_live_elements(
    base_img: Image.Image,
    t: float,
    seg_local_t: float,
    clip_frames: list[Image.Image] | None = None,
    qsl_frames: list[Image.Image] | None = None,
    scroll_waterfall: bool = True,
) -> Image.Image:
    """Composite live 24fps video, scrolling waterfall, and progressive SSTV eQSL GIF onto a Hauser MK-IV plate."""
    frame = base_img.copy()

    # 1. Scroll the Wideband Phosphor Waterfall (x=996..2513, y=198..341)
    if scroll_waterfall:
        wf_crop = base_img.crop((996, 198, 2513, 341))
        wf_arr = np.asarray(wf_crop, dtype=np.uint8)
        shift_y = int(t * 28.0) % wf_arr.shape[0]
        wf_scrolled = np.roll(wf_arr, shift_y, axis=0)
        frame.paste(Image.fromarray(wf_scrolled, mode="RGB"), (996, 198))

    # 2. Composite live video clip inside #station-video (x=34..953, y=440..758) while preserving top/bottom HUD strips
    if clip_frames:
        vid_f = clip_frames[int(t * FPS) % len(clip_frames)]
        # Keep top HUD (y=440..492) and bottom HUD (y=708..758) from the HTML capture, replace middle y=492..708
        # and blend 75% on top/bottom HUD background so the HUD pills remain crisp!
        vid_mid = vid_f.crop((0, 52, 919, 268))
        frame.paste(vid_mid, (34, 492))

    # 3. Composite animated SSTV eQSL GIF inside #qsl-gif-img (x=1845..2516, y=435..699 -> 671x264)
    if qsl_frames:
        q_idx = min(len(qsl_frames) - 1, int(seg_local_t * 2.2) % len(qsl_frames))
        q_img = qsl_frames[q_idx]
        # Progressive SSTV scanline wipe during first 4.5s of viewing the station
        wipe_pct = min(1.0, seg_local_t / 4.2)
        if wipe_pct < 0.99:
            q_arr = np.asarray(q_img, dtype=np.uint8).copy()
            wh = q_arr.shape[0]
            cut_y = int(wh * wipe_pct)
            if cut_y < wh:
                q_arr[cut_y:, :, :] = (q_arr[cut_y:, :, :] * 0.18).astype(np.uint8)
                if cut_y >= 2:
                    q_arr[cut_y - 2:cut_y, :, 0] = 56
                    q_arr[cut_y - 2:cut_y, :, 1] = 189
                    q_arr[cut_y - 2:cut_y, :, 2] = 248
            frame.paste(Image.fromarray(q_arr, mode="RGB"), (1845, 435))
        else:
            frame.paste(q_img, (1845, 435))

    return frame


def render_pan_zoom_plate(
    plate_arr: np.ndarray,
    t: float,
    seg_t: float,
    dur: float,
) -> Image.Image:
    """Subtle cinematic pan/zoom on a 2560x1440 exterior camera plate."""
    u = max(0.0, min(1.0, seg_t / max(dur, 0.1)))
    zoom = 1.04 + 0.04 * u
    zw, zh = int(W * zoom), int(H * zoom)
    pil_p = Image.fromarray(np.clip(plate_arr, 0, 255).astype(np.uint8), mode="RGB").resize(
        (zw, zh), Image.Resampling.BILINEAR
    )
    x0 = int((zw - W) * (0.5 + 0.35 * math.sin(t * 0.15)))
    y0 = int((zh - H) * 0.5)
    return pil_p.crop((x0, y0, x0 + W, y0 + H))


def draw_top_broadcast_bar(
    frame: Image.Image,
    draw: ImageDraw.ImageDraw,
    fonts: dict,
    console_tag: str,
    panel_tag: str,
    t: float,
) -> None:
    """Draw top broadcast bar for exterior camera plates (CAM-00A/B/D and O.R.S. 351)."""
    draw.rectangle([0, 0, W, 74], fill=(6, 9, 16))
    draw.line([0, 74, W, 74], fill=(232, 184, 90), width=3)

    pulse_on = (int(t * 2.0) % 2) == 0
    dot_col = (244, 63, 94) if pulse_on else (140, 30, 48)
    draw.rounded_rectangle([24, 12, 184, 62], radius=8, fill=(38, 12, 20), outline=(244, 63, 94), width=2)
    draw.ellipse([40, 26, 60, 46], fill=dot_col)
    draw.text((72, 21), "ON AIR", font=fonts["f24"], fill=(255, 210, 218))

    draw.text((206, 19), "GOR-9 • GALACTIC OUTPOST RADIO", font=fonts["f30"], fill=(232, 184, 90))
    draw.text((830, 22), f"FEED: {console_tag}", font=fonts["f22"], fill=(56, 189, 248))

    p_txt = f"VIEW: {panel_tag}"
    pw = int(draw.textlength(p_txt, font=fonts["f22"])) + 32
    px1 = W - 510
    px0 = px1 - pw
    draw.rounded_rectangle([px0, 14, px1, 60], radius=6, fill=(12, 22, 36), outline=(56, 189, 248), width=2)
    draw.text((px0 + 16, 22), p_txt, font=fonts["f22"], fill=(148, 228, 255))
    draw.text((W - 490, 22), "14,285.7 kHz USB • 0400 GCT", font=fonts["f22"], fill=(190, 206, 224))


def main() -> None:
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    tl_path = EP_DIR / "script" / "ep01_timeline.json"
    master_wav = EP_DIR / "audio" / "gor9_ep01_full_master.wav"
    out_mp4 = EP_DIR / "gor9_ep01.mp4"
    root_mp4 = ROOT / "gor9_ep01.mp4"

    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    segs = {s["id"]: s for s in tl["segments"]}
    total_dur = float(tl["total_duration_sec"])
    total_frames = int(math.ceil(total_dur * FPS))

    ding_lock_sec = float(segs["seg0_cold_open"]["ding_lock_sec"])
    t_seg1 = float(segs["seg1_weather"]["start_sec"])
    t_seg2 = float(segs["seg2_econ"]["start_sec"])
    t_seg3 = float(segs["seg3_hauser"]["start_sec"])
    t_seg4 = float(segs["seg4_euclid"]["start_sec"])
    t_seg5 = float(segs["seg5_signoff"]["start_sec"])
    t_seg6 = float(segs["seg6_outro"]["start_sec"])

    sub_views_3 = segs["seg3_hauser"]["sub_views"]
    steps_4 = segs["seg4_euclid"]["steps"]
    cam00_return_sec = float(segs["seg5_signoff"]["cam00_return_sec"])
    closing_ding_sec = float(segs["seg5_signoff"]["closing_ding_sec"])

    print(f"Rendering GOR-9 Broadcast 01 (HTML Console Edition): {total_dur:.2f}s ({total_frames} frames @ {FPS}fps)...")

    # Compute static envelope for Cold Open from master WAV
    import wave

    with wave.open(str(master_wav), "rb") as wf:
        sr = wf.getframerate()
        n_s0 = min(wf.getnframes(), int(sr * 22.0))
        raw_pcm = wf.readframes(n_s0)
        s0_audio = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32) / 32768.0
        if wf.getnchannels() == 2:
            s0_audio = s0_audio.reshape(-1, 2).mean(axis=1)

    vis_env_30 = []
    for i in range(int(22.0 * 30)):
        t_cur = i / 30.0
        if t_cur < 0.85:
            s_val = 0.78 - 0.35 * (t_cur / 0.85)
        elif t_cur < ding_lock_sec - 0.15:
            u = (t_cur - 0.85) / max(0.1, ding_lock_sec - 1.0)
            s_val = 0.42 * (1.0 - 0.65 * u) + 0.16 * max(0.0, math.sin(t_cur * 9.5))
        elif t_cur < ding_lock_sec + 0.35:
            s_val = 0.25 * max(0.0, 1.0 - (t_cur - (ding_lock_sec - 0.15)) / 0.5)
        else:
            s_val = 0.0
        vis_env_30.append(float(max(0.0, min(1.0, s_val))))

    fonts = {
        "f18": load_font(18, bold=True),
        "f20": load_font(20, bold=True),
        "f22": load_font(22, bold=True),
        "f24": load_font(24, bold=True),
        "f26": load_font(26, bold=True),
        "f28": load_font(28, bold=True),
        "f30": load_font(30, bold=True),
        "f34": load_font(34, bold=True),
        "f40": load_font(40, bold=True),
        "f44": load_font(44, bold=True),
    }

    # Load all pre-captured 2560x1440 HTML Console Plates
    cplates: dict[str, Image.Image] = {}
    for png_path in sorted(CONSOLE_PLATES_DIR.glob("*.png")):
        cplates[png_path.stem] = Image.open(png_path).convert("RGB")
    print(f"  [consoles] loaded {len(cplates)} HTML console states from {CONSOLE_PLATES_DIR}")

    # Load CAM-00A rig for Cold Open (0..11.8s)
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

    ast_specs = [
        (2, (155, 125), 2140.0, 185.0, -14.5, 4.2, 0.84),
        (4, (115, 102), 230.0, 560.0, 16.0, -5.5, 0.80),
        (3, (84, 85), 480.0, 210.0, 11.5, 6.8, 0.76),
        (1, (72, 72), 2480.0, 470.0, -195.0, -18.5, 0.94),
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
        "cam44k_start": load_plate("cam44k_quarry_start.jpg"),
        "cam00c_barracks": load_plate("cam00c_tower_downlook_barracks.jpg"),
        "sat09": load_plate("cam_sat09_orbital_downlook.jpg"),
        "closing_bg": load_plate("cam00d_closing_horizon_rings.jpg"),
    }

    # Pre-scale PiP inserts for SEG-2 (Quarry 44-K and Barracks Downlook placed in safe area x=36..526, y=905..1185)
    pip_quarry = Image.fromarray(plates["cam44k_start"].astype(np.uint8)).resize((480, 260), Image.Resampling.BILINEAR)
    pip_barracks = Image.fromarray(plates["cam00c_barracks"].astype(np.uint8)).resize((480, 260), Image.Resampling.BILINEAR)

    # Load live 24fps video clips for Hauser MK-IV (#station-video: 919x318) and Dossier (#dos-video: 507x250)
    clips_dir = EP_DIR / "clips"

    def load_clip_frames(pattern: str, w_clip: int, h_clip: int) -> list[Image.Image]:
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

    mk4_clips = {
        "n24": load_clip_frames("Buoy_bobbing*.mp4", 919, 318),
        "sw4": load_clip_frames("Engineer_hits_antenna*.mp4", 919, 318),
    }
    dos_clips = {
        "n24": load_clip_frames("Buoy_bobbing*.mp4", 507, 250),
    }

    # Load animated SSTV eQSL GIFs (671x264) and Bogey-9 Trail-Cam burst GIF (1489x419)
    qsl_dir = DOCS_DIR / "assets" / "qsl"
    qsl_gifs = {
        "n24": load_gif_frames(qsl_dir / "qsl_buoy_n24.gif", (671, 264)),
        "sw4": load_gif_frames(qsl_dir / "qsl_radio_corrugated.gif", (671, 264)),
        "m33": load_gif_frames(qsl_dir / "qsl_m33_drift.gif", (671, 264)),
        "oct": load_gif_frames(qsl_dir / "qsl_trojan_octal.gif", (671, 264)),
    }
    bogey_gif_frames = load_gif_frames(DOCS_DIR / "assets" / "uap" / "bogey_01_cylinder.gif", (1489, 419))
    print(f"  [gifs] loaded {len(bogey_gif_frames)} bogey frames and {len(qsl_gifs)} animated eQSL GIFs")

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
            # =========================================================================
            # SEG-0: COLD OPEN (0.00s .. 20.91s)
            # =========================================================================
            if t < 11.8:
                cx = int(max_dx * (0.85 - 0.70 * (t / max(t_seg1, 1.0))))
                cy = int(max_dy * (0.30 + 0.35 * math.sin(t * 0.08)))
                cx = max(0, min(max_dx, cx))
                cy = max(0, min(max_dy, cy))
                sky_crop = sky_arr[cy:cy + H, cx:cx + W].copy()

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
                draw_top_broadcast_bar(pil_frame, draw, fonts, "CAM-00A • HIGH BASALT SHELF TOWER", "0A • CLIFF PRECIPICE", t)
                # Positioned in 16:9 safe zone (y = 990..1156, leaving bottom 284px clear for YouTube controls)
                draw.rounded_rectangle([48, 990, 1080, 1156], radius=10, fill=(6, 10, 18), outline=(232, 184, 90), width=3)
                draw.text((74, 1010), "HIGH BASALT SHELF TOWER", font=fonts["f44"], fill=(232, 184, 90))
                draw.text((74, 1068), "ASTEROID 3-5-1 • OORT CLOUD SECTOR 9 (42,100 AU)", font=fonts["f28"], fill=(241, 245, 249))
                draw.text((74, 1110), "50 kW CARRIER • 14,285.7 kHz UPPER SIDEBAND", font=fonts["f24"], fill=(56, 189, 248))
                if abs(t - 6.2) < 0.03:
                    pil_frame.save(RENDERS_DIR / "preview_seg0_sat.jpg", quality=92)

            elif t < 15.8:
                pil_frame = render_pan_zoom_plate(plates["cam00b_wide"], t, t - 11.8, 4.0)
                draw = ImageDraw.Draw(pil_frame)
                draw_top_broadcast_bar(pil_frame, draw, fonts, "CAM-00B • ACHERON CANYON RIM OVERLOOK", "0B • CANYON TELEPHOTO", t)
                draw.rounded_rectangle([48, 990, 1080, 1156], radius=10, fill=(6, 10, 18), outline=(56, 189, 248), width=3)
                draw.text((74, 1010), "14,285.7 kHz USB [LOCKED]", font=fonts["f44"], fill=(56, 189, 248))
                draw.text((74, 1068), "OORT CLOUD SECTOR 9 • 42,100 AU FROM SOL", font=fonts["f28"], fill=(241, 245, 249))
                draw.text((74, 1110), "SOUTH ROTATIONAL POLE • ELEVATED ATC TOWER", font=fonts["f24"], fill=(232, 184, 90))
                pil_frame = apply_switch_glitch(pil_frame, t - 11.8, seed=11)

            else:
                # 15.8s .. 20.91s: Actual HTML Console Modal — Octagonal ATC Control Deck & Hardware Makers
                pil_frame = cplates["tower_modal"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                draw_focus_brackets(draw, (496, 278, 2064, 1025), (240, 184, 73), t, "OCTAGONAL ATC CONTROL TOWER DECK", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, t - 15.8, seed=14)

        elif t < t_seg2:
            # =========================================================================
            # SEG-1: CONSOLE 1 — VAN ALLEN VA-4 SPACE WEATHER & PROPAGATION (20.91s .. 50.92s)
            # =========================================================================
            seg_t = t - t_seg1
            if seg_t < 10.0:
                pil_frame = cplates["va4_1a_comet"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (74, 222, 128))
                # Highlight Comet K-4 Regime & Oblique Ionogram
                draw_focus_brackets(draw, (530, 212, 1988, 725), (74, 222, 128), t, "COMET K-4 IONIZATION • 24 MHz SKIP DUCT", fonts["f18"])
                draw_focus_brackets(draw, (28, 560, 514, 1044), (56, 189, 248), t)
                pil_frame = apply_switch_glitch(pil_frame, seg_t, seed=21)
            elif seg_t < 20.0:
                pil_frame = cplates["va4_1b_squall"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                # Highlight 60 kV Triboelectric Dust Squall & KZ9-Omega Corridor
                draw_focus_brackets(draw, (2004, 212, 2532, 456), (240, 184, 73), t, "60 kV TRIBOELECTRIC SQUALL • KZ9-OMEGA", fonts["f18"])
                draw_focus_brackets(draw, (530, 660, 1988, 868), (56, 189, 248), t)
                pil_frame = apply_switch_glitch(pil_frame, seg_t - 10.0, seed=22)
            else:
                pil_frame = cplates["va4_1c_clamp"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                # Highlight #4 Belt-Master MV-6 Surge Clamp & Van Allen Underwriter Nameplate
                draw_focus_brackets(draw, (2004, 468, 2532, 1222), (240, 184, 73), t, "VAN ALLEN #4 BELT-MASTER MV-6 CLAMP", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, seg_t - 20.0, seed=23)

            if abs(seg_t - 3.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg1_panel1a.jpg", quality=92)
            elif abs(seg_t - 13.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg1_meteo.jpg", quality=92)
            elif abs(seg_t - 23.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg1_panel1c.jpg", quality=92)

        elif t < t_seg3:
            # =========================================================================
            # SEG-2: CONSOLE 1B — VAN ALLEN VA-4 DILITHIUM POWER BUS (50.92s .. 85.58s)
            # =========================================================================
            seg_t = t - t_seg2
            if seg_t < 11.5:
                pil_frame = cplates["va4_2a_spot"].copy()
                # Composite Quarry 44-K PiP in bottom-left safe area (x=28..508, y=932..1192)
                pil_frame.paste(pip_quarry, (28, 932))
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                draw_focus_brackets(draw, (28, 932, 508, 1192), (56, 189, 248), t, "CAM-44K • CERES QUARRY SLOWDOWN", fonts["f18"])
                draw_focus_brackets(draw, (2004, 845, 2532, 988), (240, 184, 73), t, "DILITHIUM SPOT +4.2% • REACTOR #2", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, seg_t, seed=31)
            elif seg_t < 23.0:
                pil_frame = cplates["va4_2b_stepdown"].copy()
                # Composite Barracks Downlook PiP in bottom-left safe area (x=28..508, y=932..1192)
                pil_frame.paste(pip_barracks, (28, 932))
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (74, 222, 128))
                draw_focus_brackets(draw, (28, 932, 508, 1192), (74, 222, 128), t, "CAM-00C • BARRACKS CRYO-TOAST 900", fonts["f18"])
                draw_focus_brackets(draw, (2004, 670, 2532, 1222), (240, 184, 73), t, "RING-BAKE +4.5 kW • NIGHT STEPDOWN", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, seg_t - 11.5, seed=32)
            else:
                pil_frame = cplates["va4_2c_quarantine"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (251, 113, 133))
                draw_focus_brackets(draw, (28, 868, 514, 962), (251, 113, 133), t, "QUARANTINE BUOY 12 • ICE-TENDER", fonts["f18"])
                draw_focus_brackets(draw, (2004, 845, 2532, 988), (56, 189, 248), t, "UNINSPECTED PELLET BARGE ALERT", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, seg_t - 23.0, seed=33)

            if abs(seg_t - 4.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg2_panel2a.jpg", quality=92)
            elif abs(seg_t - 15.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg2_econ.jpg", quality=92)
            elif abs(seg_t - 26.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg2_panel2c.jpg", quality=92)

        elif t < t_seg4:
            # =========================================================================
            # SEG-3: CONSOLE 2 — HAUSER DYNAMICS MK-IV & STATION DOSSIERS (85.58s .. 167.37s)
            # =========================================================================
            seg_t = t - t_seg3
            t_3b = float(sub_views_3[1]["start_sec"])
            t_3c = float(sub_views_3[2]["start_sec"])
            t_3d = float(sub_views_3[3]["start_sec"])

            if t < t_3b:
                # 3A: Preset P-02 • 3,890 kHz CW • Titan-Minor Hydrographic Buoy N-24 (85.58s .. 110.72s)
                local_t = t - float(sub_views_3[0]["start_sec"])
                if local_t < 9.5:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3a_video"], t, local_t, mk4_clips["n24"], qsl_gifs["n24"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (56, 189, 248))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (56, 189, 248), t, "P-02 • TITAN-MINOR BUOY N-24 OPTIC", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=41)
                elif local_t < 18.2:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3a_decoder"], t, local_t, None, qsl_gifs["n24"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (56, 189, 248))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (240, 184, 73), t, "ALG-01 • -165 Hz FAUNA GUY-WIRE DETUNE", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 9.5, seed=42)
                else:
                    pil_frame = cplates["dos_3a_n24"].copy()
                    if dos_clips["n24"]:
                        pil_frame.paste(dos_clips["n24"][int(t * FPS) % len(dos_clips["n24"])], (934, 309))
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                    draw_focus_brackets(draw, (214, 210, 878, 956), (240, 184, 73), t, "COLLECTOR CARD • QSL #0089-N24", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 18.2, seed=43)

            elif t < t_3c:
                # 3B: Preset P-01 • 11,410 kHz AM-W • Callisto Dome-4 Radio Corrugated (110.72s .. 126.06s)
                local_t = t - t_3b
                if local_t < 8.5:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3b_video"], t, local_t, mk4_clips["sw4"], qsl_gifs["sw4"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (240, 184, 73), t, "CAM-104 • ROOFTOP DIPOLE BLOWTORCH", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=44)
                else:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3b_decoder"], t, local_t, None, qsl_gifs["sw4"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (251, 113, 133), t, "S9+18 dB • +18.4 dB PLASMA ARC SPIKE", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 8.5, seed=45)

            elif t < t_3d:
                # 3C: Preset P-03 • 1,420.406 MHz H-I • Ming-Era Drift Buoy M33-771 (126.06s .. 150.72s)
                local_t = t - t_3c
                if local_t < 9.0:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3c_spectrum"], t, local_t, None, qsl_gifs["m33"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (74, 222, 128))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (74, 222, 128), t, "21cm H-I • DOPPLER LISSAJOUS LOCK", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=46)
                elif local_t < 18.5:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3c_decoder"], t, local_t, None, qsl_gifs["m33"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (74, 222, 128))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (240, 184, 73), t, "ALG-03 • MING 1580 CE DRY SALT BASIN", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 9.0, seed=47)
                else:
                    pil_frame = cplates["mk4_3c_atlas"].copy()
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (56, 189, 248))
                    draw_focus_brackets(draw, (458, 250, 2102, 1052), (74, 222, 128), t, "2.73 Mly • M-33 TRIANGULUM GALAXY SPUR", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 18.5, seed=48)

            else:
                # 3D: Preset P-04 • 6,440 kHz USB-OCT • Trojan L4 'Three-Five-Octal' (150.72s .. 167.37s)
                local_t = t - t_3d
                if local_t < 9.5:
                    pil_frame = composite_mk4_live_elements(
                        cplates["mk4_3d_decoder"], t, local_t, None, qsl_gifs["oct"]
                    )
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (251, 113, 133))
                    draw_focus_brackets(draw, (28, 412, 960, 766), (251, 113, 133), t, "ALG-02 • 6.0t DUMPLING WRAPPERS + KEY 13", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=49)
                else:
                    pil_frame = cplates["dos_3d_octal_back"].copy()
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (56, 189, 248))
                    draw_focus_brackets(draw, (214, 210, 878, 956), (56, 189, 248), t, "REVERSE DOSSIER • OCTAL SHIFT KEY 13", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 9.5, seed=50)

            if abs(seg_t - 7.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg3_panel3a.jpg", quality=92)
            elif abs(seg_t - 30.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg3_hauser.jpg", quality=92)
            elif abs(seg_t - 50.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg3_panel3c.jpg", quality=92)

        elif t < t_seg5:
            # =========================================================================
            # SEG-4: CONSOLE 3 (BOGEY-9) & CONSOLE 4 (VAN ALLEN ED-9) (167.37s .. 264.90s)
            # =========================================================================
            seg_t = t - t_seg4
            t_4b = float(steps_4[1]["start_sec"])
            t_4c = float(steps_4[2]["start_sec"])
            t_4d = float(steps_4[3]["start_sec"])

            if t < t_4b:
                # 4A: CONSOLE 3 — BOGEY-9 TRAIL-CAM & UAP DETECTOR (167.37s .. 196.92s)
                local_t = t - float(steps_4[0]["start_sec"])
                if local_t < 10.5:
                    pil_frame = cplates["bogey_4a_gif"].copy()
                    if bogey_gif_frames:
                        bf = bogey_gif_frames[int(t * 6.0) % len(bogey_gif_frames)]
                        pil_frame.paste(bf, (520, 377))
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (251, 113, 133))
                    draw_focus_brackets(draw, (504, 212, 2024, 912), (251, 113, 133), t, "TRL-01 • LIVE 8-FRAME BURST (140g SNAP)", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=61)
                elif local_t < 20.5:
                    pil_frame = cplates["bogey_4a_frame6"].copy()
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (56, 189, 248))
                    draw_focus_brackets(draw, (2040, 212, 2532, 718), (251, 113, 133), t, "KEPLERIAN FIT: FAILED • ZERO PLUME", fonts["f18"])
                    draw_focus_brackets(draw, (504, 212, 2024, 912), (56, 189, 248), t)
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 10.5, seed=62)
                else:
                    pil_frame = cplates["bogey_4a_nvg"].copy()
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (74, 222, 128))
                    draw_focus_brackets(draw, (518, 998, 2010, 1044), (240, 184, 73), t, "MESS HALL THERMOS FLASK COVER STORY", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 20.5, seed=63)

            elif t < t_4c:
                # 4B: CONSOLE 4 — VAN ALLEN ED-9 EUCLIDEAN DETECTOR STEP 1 (196.92s .. 229.49s)
                local_t = t - t_4b
                pil_frame = cplates["ed9_4b_step1"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                if local_t < 16.0:
                    draw_focus_brackets(draw, (28, 492, 502, 922), (240, 184, 73), t, "12-TUBE HOUGH ACCUMULATOR • SNR +94.2 dB", fonts["f18"])
                    draw_focus_brackets(draw, (2034, 712, 2532, 1106), (56, 189, 248), t, "VAN ALLEN ED-9 • ASTROMETRIC SETI", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=64)
                else:
                    draw_focus_brackets(draw, (518, 152, 2018, 868), (56, 189, 248), t, "STEP 1 • VAT 19 PARALLEL RIDGE LOCK", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 16.0, seed=65)

            elif t < t_4d:
                # 4C: CONSOLE 4 — VAN ALLEN ED-9 EUCLIDEAN DETECTOR STEPS 2 & 3 (229.49s .. 251.44s)
                local_t = t - t_4c
                if local_t < 11.0:
                    pil_frame = cplates["ed9_4c_step2"].copy()
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                    draw_focus_brackets(draw, (518, 152, 2018, 868), (240, 184, 73), t, "STEP 2 • DIAMETER BC BISECTION (G.47)", fonts["f18"])
                    pil_frame = apply_switch_glitch(pil_frame, local_t, seed=66)
                else:
                    pil_frame = cplates["ed9_4c_step3"].copy()
                    draw = ImageDraw.Draw(pil_frame)
                    draw_safezone_chassis_bezel(draw, t, (74, 222, 128))
                    draw_focus_brackets(draw, (518, 152, 2018, 868), (74, 222, 128), t, "STEP 3 • EUCLID I.34 CONGRUENCE LOCK", fonts["f18"])
                    draw_focus_brackets(draw, (2034, 152, 2532, 700), (74, 222, 128), t)
                    pil_frame = apply_switch_glitch(pil_frame, local_t - 11.0, seed=67)

            else:
                # 4D: CONSOLE 4 — VAN ALLEN ED-9 STEP 4 WATER BOARD COVER-UP (251.44s .. 264.90s)
                local_t = t - t_4d
                pil_frame = cplates["ed9_4d_step4"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                draw_focus_brackets(draw, (518, 668, 2018, 868), (240, 184, 73), t, "STEP 4 • CALLISTO WATER BOARD COVER-UP", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, local_t, seed=68)

            if abs(seg_t - 8.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg4_panel4a1.jpg", quality=92)
            elif abs(seg_t - 70.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg4_euclid.jpg", quality=92)
            elif abs(seg_t - 90.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg4_panel4c.jpg", quality=92)

        elif t < t_seg6:
            # =========================================================================
            # SEG-5: COMING NEXT RHOMBUS PREVIEW, UNDERWRITER, & CAM-00D SIGN-OFF (264.90s .. 289.26s)
            # =========================================================================
            seg_t = t - t_seg5
            if t < 272.5:
                # 5A: Coming Next on Van Allen ED-9 — The Ice-Hauler Rhombus (Euclid Def. I.22 / G.38)
                pil_frame = cplates["ed9_5a_rhombus"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (56, 189, 248))
                draw_focus_brackets(draw, (28, 340, 502, 466), (56, 189, 248), t, "NEXT BROADCAST • SECTOR 7 DEPOT", fonts["f18"])
                draw_focus_brackets(draw, (518, 152, 2018, 868), (240, 184, 73), t, "COMING NEXT • THE ICE-HAULER RHOMBUS (DEF. I.22)", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, seg_t, seed=71)
            elif t < cam00_return_sec:
                # 5B: Broadcast Underwriter Showcase — Van Allen & Sons Switchgear + Hauser Dynamics
                pil_frame = cplates["tower_modal"].copy()
                draw = ImageDraw.Draw(pil_frame)
                draw_safezone_chassis_bezel(draw, t, (240, 184, 73))
                draw_focus_brackets(draw, (1282, 875, 2036, 1008), (240, 184, 73), t, "UNDERWRITER • VAN ALLEN & SONS SWITCHGEAR", fonts["f18"])
                pil_frame = apply_switch_glitch(pil_frame, t - 272.5, seed=72)
            else:
                # 5C: CAM-00D Exterior Horizon Sign-Off with [ding-ding] ring wave
                pil_frame = render_pan_zoom_plate(plates["closing_bg"], t, t - cam00_return_sec, t_seg6 - cam00_return_sec)
                if t >= closing_ding_sec - 0.1:
                    arr_c = np.asarray(pil_frame, dtype=np.float32)
                    pulse_c = math.exp(-max(0.0, t - closing_ding_sec) / 0.8)
                    arr_c = np.clip(arr_c * (1.0 + 0.25 * pulse_c), 0, 255).astype(np.uint8)
                    pil_frame = Image.fromarray(arr_c, mode="RGB")
                draw = ImageDraw.Draw(pil_frame)
                draw_top_broadcast_bar(pil_frame, draw, fonts, "CAM-00D • SOUTH POLAR HORIZON & APEX RINGS", "5C • SIGN-OFF", t)
                # Positioned in 16:9 safe zone (y = 970..1156)
                draw.rounded_rectangle([48, 970, 1280, 1156], radius=10, fill=(6, 10, 18), outline=(240, 184, 73), width=3)
                draw.text((74, 992), "GOR-9 • GALACTIC OUTPOST RADIO", font=fonts["f44"], fill=(240, 184, 73))
                draw.text((74, 1052), "YOUR EYE TO THE COSMOS • EAR TO THE VACUUM", font=fonts["f28"], fill=(56, 189, 248))
                draw.text((74, 1098), "ASTEROID 3-5-1 • OORT CLOUD SECTOR 9 • 14,285.7 kHz USB", font=fonts["f24"], fill=(241, 245, 249))
                pil_frame = apply_switch_glitch(pil_frame, t - cam00_return_sec, seed=73)

            if abs(seg_t - 3.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg5_panel5a.jpg", quality=92)
            elif abs(seg_t - 10.0) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg5_sched.jpg", quality=92)

        else:
            # =========================================================================
            # SEG-6: O.R.S. 351 ORBITAL DOWNLINK & YOUTUBE END-SCREEN (289.26s .. 309.26s)
            # =========================================================================
            seg_t = t - t_seg6
            pil_frame = render_pan_zoom_plate(plates["sat09"], t, seg_t, 20.0)
            draw = ImageDraw.Draw(pil_frame)
            draw_top_broadcast_bar(pil_frame, draw, fonts, "O.R.S. 351 • ORBITAL RELAY SATELLITE DOWNLOOK", "6A • END CARD", t)

            # Left & Right YouTube End-Screen Card Frames positioned in top safe zone (y = 220..760)
            draw.rounded_rectangle([140, 220, 1180, 760], radius=16, fill=(8, 13, 24), outline=(240, 184, 73), width=4)
            draw.text((185, 255), "NEXT BROADCAST • EPOCH 2736.312", font=fonts["f28"], fill=(240, 184, 73))
            draw.text((185, 305), "THE ICE-HAULER RHOMBUS (EUCLID DEF. I.22)", font=fonts["f24"], fill=(56, 189, 248))
            rhom_thumb = cplates["ed9_5a_rhombus"].resize((960, 360), Image.Resampling.BILINEAR)
            pil_frame.paste(rhom_thumb, (180, 365))

            draw.rounded_rectangle([1380, 220, 2420, 760], radius=16, fill=(8, 13, 24), outline=(74, 222, 128), width=4)
            draw.text((1425, 255), "SUBSCRIBE TO GOR-9 RELAY", font=fonts["f28"], fill=(74, 222, 128))
            draw.text((1425, 305), "LIKE = +3 kW DILITHIUM • SUBSCRIBE = MARZELVANE SHIELD", font=fonts["f22"], fill=(241, 245, 249))
            va4_thumb = cplates["va4_1a_comet"].resize((960, 360), Image.Resampling.BILINEAR)
            pil_frame.paste(va4_thumb, (1420, 365))

            # Bottom telemetry banner placed safely above YouTube controls (y = 920..1140)
            draw.rounded_rectangle([140, 920, 2420, 1140], radius=12, fill=(6, 10, 18), outline=(56, 189, 248), width=3)
            draw.text((185, 948), "O.R.S. 351 POLAR HALO ORBIT • ALTITUDE 420 km ABOVE ASTEROID 3-5-1", font=fonts["f34"], fill=(56, 189, 248))
            draw.text((185, 1012), "UNDERWRITTEN BY VAN ALLEN & SONS SWITCHGEAR • RECEIVERS BY HAUSER DYNAMICS", font=fonts["f26"], fill=(240, 184, 73))
            draw.text((185, 1066), "INTERACTIVE CONSOLES & eQSL ARCHIVE: GEOMETOR / GOR-9 STATION WEB", font=fonts["f24"], fill=(74, 222, 128))

            if abs(seg_t - 7.5) < 0.03:
                pil_frame.save(RENDERS_DIR / "preview_seg6_outro.jpg", quality=92)

        proc.stdin.write(pil_frame.tobytes())

    proc.stdin.close()
    proc.wait()
    if not root_mp4.exists() or not root_mp4.samefile(out_mp4):
        shutil.copy2(out_mp4, root_mp4)
    print(f"Done! Full Broadcast 01 saved to: {out_mp4} and {root_mp4}")


if __name__ == "__main__":
    main()
