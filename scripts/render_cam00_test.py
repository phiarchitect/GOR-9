#!/usr/bin/env python3
"""Render a 2560x1440 (1440p QHD) MP4 of the Cliff-Edge Concentric-Ring CAM-00 Cold Open.

Features:
- Cliff-Edge Open-Lattice Broadcast Tower perched on the sheer columnar basalt precipice
  above Acheron Canyon, set against the moving ringed-planet cosmic sky.
- Illuminated 'GOR-9' neon rooftop sign where 'GOR-' glows steadily after ignition and
  the '9' blinks/flickers on its own relay cadence.
- 3 independent crimson aviation warning beacons (mast_top, booth_left, booth_right)
  blinking on staggered, asynchronous schedules.
- 4 concentric plasma rings at the antenna apex (cam00_ring_1..4.png) that power up
  sequentially from inner ring to outer ring right at the [ding-ding] signal lock (t=4.30s)
  and pulse outward in traveling radial waves.
- Large, TV-readable HUD typography.
"""

from pathlib import Path
import json
import math
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PLATES_DIR = ROOT / "assets" / "plates"
COMP_DIR = ROOT / "assets" / "composited"
SFX_DIR = ROOT / "assets" / "sfx"
RENDERS_DIR = ROOT / "renders"

W, H = 2560, 1440
FPS = 30


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def get_wav_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def build_snow_bank(rng: np.random.Generator, count: int = 10) -> list[np.ndarray]:
    """Pre-compute a bank of 2560x1440 high-contrast crackly white-noise snow frames."""
    bank = []
    for _ in range(count):
        fine = rng.integers(0, 256, size=(H // 2, W // 2), dtype=np.uint8)
        snow = np.where(fine > 195, 255, np.where(fine < 75, 12, fine)).astype(np.float32)
        snow_full = np.repeat(np.repeat(snow, 2, axis=0), 2, axis=1)
        for _ in range(30):
            ry = int(rng.integers(0, H - 3))
            rx = int(rng.integers(0, W - 400))
            rw = int(rng.integers(80, 400))
            snow_full[ry:ry + 2, rx:rx + rw] = 255.0
        snow_rgb = np.dstack([snow_full * 0.90, snow_full * 0.96, snow_full])
        bank.append(snow_rgb.astype(np.float32))
    return bank


def build_static_hud() -> Image.Image:
    """Create the 2560x1440 TV-readable broadcast HUD overlay (RGBA)."""
    hud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(hud)

    f_bar_big = load_font(30, bold=True)
    f_bar_med = load_font(24, bold=True)
    f_card_h1 = load_font(44, bold=True)
    f_card_h2 = load_font(28, bold=True)

    # Top Master Broadcast Bar (height 78px for 10-foot TV legibility)
    draw.rectangle([0, 0, W, 78], fill=(8, 12, 20, 235))
    draw.line([0, 78, W, 78], fill=(232, 184, 90, 180), width=3)

    # ON AIR Pill
    draw.rounded_rectangle([28, 14, 188, 64], radius=6, fill=(244, 63, 94, 55), outline=(244, 63, 94, 255), width=2)
    draw.ellipse([44, 29, 64, 49], fill=(244, 63, 94, 255))
    draw.text((76, 22), "ON AIR", font=f_bar_med, fill=(255, 205, 212, 255))

    draw.text((214, 20), "GOR-9 • GALACTIC OUTPOST RADIO", font=f_bar_big, fill=(232, 184, 90, 255))
    draw.text((940, 24), "ASTEROID 3-5-1 • SECTOR 9 • 0400 UTC", font=f_bar_med, fill=(203, 213, 225, 255))

    # Lower-Left Station Callout (TV-Sized)
    draw.rounded_rectangle([48, H - 210, 960, H - 44], radius=10, fill=(6, 10, 18, 215), outline=(232, 184, 90, 190), width=3)
    draw.text((74, H - 190), "HIGH BASALT SHELF", font=f_card_h1, fill=(232, 184, 90, 255))
    draw.text((74, H - 130), "ASTEROID 3-5-1 • ELEVATED TOWER BOOTH", font=f_card_h2, fill=(241, 245, 249, 255))
    draw.text((74, H - 88), "50 kW CARRIER • 14,285.7 kHz UPPER SIDEBAND", font=f_bar_med, fill=(56, 189, 248, 255))

    return hud


def beacon_pulse(t: float, period: float, phase_offset: float) -> float:
    """Compute a staggered aviation obstruction beacon pulse."""
    cyc = ((t + phase_offset) % period) / period
    if cyc < 0.36:
        return float(math.sin((cyc / 0.36) * math.pi) ** 1.6)
    return 0.0


def neon_nine_pulse(t: float) -> float:
    """Classic slightly-faulty neon tube blink/flicker for the '9' in GOR-9."""
    if t < 1.35:
        return 0.0
    # 2.4-second cycle: steady on for 65%, quick double-wink, brief off, strike back on
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
    """Sequential inner-to-outer ignition at ding_lock_sec + outward traveling wave pulse."""
    # Pre-lock warm-up: faint inner ring glow while calling under static
    if t < ding_lock_sec:
        if ring_idx == 1 and t > 1.2:
            return 0.22 * (0.5 + 0.5 * math.sin(t * 6.0))
        return 0.0
    # Staggered ignition: ring 1 at +0.00s, ring 2 at +0.18s, ring 3 at +0.36s, ring 4 at +0.54s
    onset = ding_lock_sec + (ring_idx - 1) * 0.18
    if t < onset:
        return 0.0
    ramp = min(1.0, (t - onset) / 0.28)
    # Outward traveling radial wave across the 4 rings
    wave_mod = 0.68 + 0.32 * math.sin((t - ding_lock_sec) * 4.4 - (ring_idx - 1) * 0.95)
    # Initial lock surge during first 1.2s after ding
    surge = 0.30 * math.exp(-max(0.0, t - onset) / 0.9)
    return float(min(1.35, ramp * wave_mod + surge))


def main() -> None:
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    out_wav = RENDERS_DIR / "cam00_cold_open_mix.wav"
    out_mp4 = RENDERS_DIR / "cam00_opening_test.mp4"

    catalog = json.loads((SFX_DIR / "sfx_catalog.json").read_text(encoding="utf-8"))
    vis_env = catalog["cam00_boot_visual_envelope_30fps"]
    ding_lock_sec = float(catalog.get("ding_lock_time_sec", 4.30))

    duration = get_wav_duration(out_wav)
    total_frames = int(duration * FPS)
    print(f"Rendering {total_frames} frames ({duration:.2f}s @ {FPS}fps, {W}x{H}) -> {out_mp4}")

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

    # Load the 4 concentric apex ring layers (cam00_ring_1..4.png)
    ring_layers = []
    for idx in range(1, 5):
        r_img = Image.open(COMP_DIR / f"cam00_ring_{idx}.png").convert("RGBA")
        r_arr = np.asarray(r_img, dtype=np.float32)
        r_alpha = r_arr[..., 3:4] / 255.0
        # Crop to upper apex region y=60..515, x=750..1810 for fast compositing
        ring_layers.append((idx, (r_arr[60:515, 750:1810, :3] * r_alpha[60:515, 750:1810])))

    # Load and scale the 4 RGBA drifting main-belt asteroid sprites
    ast_specs = [
        (2, (155, 125), 2060.0, 210.0, -3.2, -0.8, 0.82),
        (4, (115, 102), 340.0, 390.0, 2.6, 0.6, 0.78),
        (3, (84, 85), 2240.0, 560.0, -2.1, 0.5, 0.74),
        (1, (58, 58), 520.0, 660.0, 1.6, -0.4, 0.68),
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

    schedules = {
        "mast_top": (2.30, 0.15),
        "booth_left": (3.10, 1.25),
        "booth_right": (2.75, 2.05),
    }

    hud_img = build_static_hud()
    hud_arr = np.asarray(hud_img, dtype=np.float32)
    alpha_hud = hud_arr[..., 3:4] / 255.0
    premult_hud = hud_arr[..., :3] * alpha_hud

    scanline_mult = np.ones((H, 1, 1), dtype=np.float32)
    scanline_mult[3::4, 0, 0] = 0.86

    rng = np.random.default_rng(3519)
    snow_bank = build_snow_bank(rng, count=10)

    f_freq = load_font(34, bold=True)
    f_lock = load_font(28, bold=True)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(out_wav),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out_mp4),
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    max_dx = sky_w - W
    max_dy = sky_h - H

    for frame_idx in range(total_frames):
        t = frame_idx / FPS

        # 1. Slow cosmic sky drift behind the cliff-edge tower & through open trusses
        cx = int(max_dx * (0.85 - 0.70 * (t / max(duration, 1.0))))
        cy = int(max_dy * (0.30 + 0.35 * math.sin(t * 0.08)))
        cx = max(0, min(max_dx, cx))
        cy = max(0, min(max_dy, cy))
        sky_crop = sky_arr[cy:cy + H, cx:cx + W].copy()

        # 1B. Composite drifting main-belt asteroid sprites onto the galactic sky
        for sw, sh, ax0, ay0, avx, avy, sp_a, sp_pre in asteroid_sprites:
            ax = int(round(ax0 + avx * t))
            ay = int(round(ay0 + avy * t))
            if 0 <= ax and ax + sw <= W and 0 <= ay and ay + sh <= H:
                roi = sky_crop[ay:ay + sh, ax:ax + sw]
                sky_crop[ay:ay + sh, ax:ax + sw] = roi * (1.0 - sp_a) + sp_pre

        # Composite base cliff-edge tower (rings & neon off) over moving sky
        comp = sky_crop * (1.0 - alpha_off) + premult_off

        # 2. Animate the 4 concentric plasma rings at the antenna apex
        apex_slice = comp[60:515, 750:1810]
        for r_idx, r_premult in ring_layers:
            w_ring = ring_wave_intensity(t, r_idx, ding_lock_sec)
            if w_ring > 0.01:
                apex_slice = np.clip(apex_slice + r_premult * w_ring, 0.0, 255.0)
        comp[60:515, 750:1810] = apex_slice

        # 3. Animate 'GOR-' neon prefix (steady after t=1.2s) and blinking '9' neon digit
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

        # 4. Independently blink each of the 3 crimson warning beacons
        for b in beacons_meta:
            bid = b["id"]
            period, ph_off = schedules.get(bid, (2.8, 0.0))
            p = beacon_pulse(t, period, ph_off)
            if p > 0.01:
                x0, y0, bw, bh = b["x"], b["y"], b["w"], b["h"]
                x1, y1 = min(W, x0 + bw), min(H, y0 + bh)
                b_pre = premult_b_all[y0:y1, x0:x1] * p
                comp[y0:y1, x0:x1] = np.clip(comp[y0:y1, x0:x1] + b_pre, 0.0, 255.0)

        # 5. Audio-driven Camera Crackle-In (0.0s -> ding_lock_sec = 4.30s)
        s = vis_env[frame_idx] if frame_idx < len(vis_env) else 0.0
        if s > 0.01:
            desat = min(1.0, s * 1.1)
            if desat > 0.05:
                luma = comp[..., 0:1] * 0.299 + comp[..., 1:2] * 0.587 + comp[..., 2:3] * 0.114
                comp = comp * (1.0 - desat) + luma * desat

            n_tears = int(6 + 22 * s)
            for _ in range(n_tears):
                by = int(rng.integers(78, H - 50))
                bh = int(rng.integers(8, 42))
                shift_x = int(rng.integers(-150, 151) * (s ** 1.2))
                comp[by:by + bh] = np.roll(comp[by:by + bh], shift_x, axis=1)

            snow_frame = snow_bank[frame_idx % len(snow_bank)]
            sy_shift = int(rng.integers(0, H))
            snow_rolled = np.roll(snow_frame, sy_shift, axis=0)
            snow_op = min(0.88, (s ** 0.85) * 0.90)
            comp = comp * (1.0 - snow_op) + snow_rolled * snow_op

        # Apply subtle CRT scanlines & composite HUD
        comp = comp * scanline_mult
        comp = comp * (1.0 - alpha_hud) + premult_hud

        frame_uint8 = np.clip(comp, 0, 255).astype(np.uint8)
        pil_frame = Image.fromarray(frame_uint8, mode="RGB")
        draw = ImageDraw.Draw(pil_frame)

        if t < ding_lock_sec:
            drift = math.sin(t * 29.0) * 14.2 * (1.0 - t / ding_lock_sec)
            freq_val = 14285.7 + drift
            draw.text((W - 580, 20), f"{freq_val:07.1f} kHz [TUNING]", font=f_freq, fill=(244, 63, 94))
        else:
            draw.text((W - 580, 20), "14,285.7 kHz USB [LOCK]", font=f_freq, fill=(56, 189, 248))

        if abs(t - 1.80) < 0.02:
            pil_frame.save(RENDERS_DIR / "cam00_preview_crackle.jpg", quality=92)
        elif abs(t - 3.60) < 0.02:
            pil_frame.save(RENDERS_DIR / "cam00_preview_dim.jpg", quality=92)
        elif abs(t - 6.20) < 0.02:
            pil_frame.save(RENDERS_DIR / "cam00_preview_bright.jpg", quality=92)

        proc.stdin.write(pil_frame.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"Done! Video saved to: {out_mp4}")


if __name__ == "__main__":
    main()
