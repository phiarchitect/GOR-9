#!/usr/bin/env python3
"""Build the GOR-9 Station Archive, Per-Station Folders, Worldbuilding Docs, Audio, and Unique Postcard QSL GIFs.

Each intercepted station has:
1. Its own self-contained directory under `stations/<station_slug>/` (`station.json`, `WORLDBUILDING.md`, `plates/`, `qsl/`, `audio/`).
2. Rich character & entity profiles (including languages, dialects, TTS voice casting, and multi-episode discovery arcs).
3. A uniquely designed, clunky animated postcard QSL GIF (`docs/assets/qsl/qsl_*.gif`) inspired by Glenn Hauser's QSL archive (`worldofradio.com/QSL.html`)—featuring multi-frame character actions (couple kissing, monks bowing, captain waving, etc.), bold call letters, clear location text, and zero text overlap.
"""

from pathlib import Path
import json
import math
import shutil
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
STATIONS_ROOT = ROOT / "stations"
DATA_PATH = DOCS / "data" / "stations.json"
QSL_DIR = DOCS / "assets" / "qsl"
AUDIO_DIR = DOCS / "assets" / "audio"
PLATES_DIR = DOCS / "assets" / "plates"
EP1_SEG_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram" / "audio" / "segments"
BRAIN_DIR = Path("/home/phi/.gemini/antigravity/brain/4a15bd90-1dea-40db-80d9-26acb50c2eaf")

SAMPLE_RATE = 24000
W, H = 384, 240
N_FRAMES = 10


def sync_generated_plates() -> None:
    """Copy all Frame A, Frame B, and Flow 16:9 background plates from artifact directory into docs/assets/plates/."""
    PLATES_DIR.mkdir(parents=True, exist_ok=True)
    plate_prefixes = [
        "qsl_plate_radio_corrugated",
        "qsl_plate_radio_corrugated_kiss",
        "qsl_plate_radio_free_hektor",
        "qsl_plate_radio_free_hektor_b",
        "qsl_plate_st_jerome_slag",
        "qsl_plate_monastery_a",
        "qsl_plate_monastery_b",
        "qsl_plate_monastery_elegant_a",
        "qsl_plate_monastery_elegant_b",
        "qsl_plate_alien_monastery_a",
        "qsl_plate_alien_monastery_b",
        "qsl_plate_pedregal_rafa",
        "qsl_plate_pedregal_rafa_wave",
        "qsl_plate_m33_ming_buoy",
        "qsl_plate_m33_ming_buoy_b",
        "flow_kaelen_planet_architecture",
        "flow_alien_monastery_vista",
        "flow_m33_onboard_cam_a",
        "flow_m33_onboard_cam_b",
        "flow_n24_onboard_pov_a",
        "flow_n24_onboard_pov_b",
        "flow_n24_onboard_rub_b",
        "flow_kz9_mast_pov_a",
        "flow_kz9_mast_pov_b",
        "flow_callisto_market_architecture",
        "flow_hektor_canyon_architecture",
        "flow_pedregal_bridge_pov",
    ]
    if not BRAIN_DIR.exists():
        return
    for prefix in plate_prefixes:
        # Prefer _varied_<timestamp>.jpg if present, otherwise exact <prefix>_<timestamp>.jpg
        varied = sorted(BRAIN_DIR.glob(f"{prefix}_varied_*.jpg"))
        matches = varied if varied else sorted(
            p for p in BRAIN_DIR.glob(f"{prefix}_*.jpg")
            if p.stem[len(prefix) + 1:].isdigit()
        )
        if matches:
            dst = PLATES_DIR / f"{prefix}.jpg"
            shutil.copy2(matches[-1], dst)
            print(f"Synced generated postcard plate -> {dst.relative_to(ROOT)}")


def save_wav(path: Path, arr: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(arr * 32767.0, -32767.0, 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def load_wav_float(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32767.0


def load_font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if serif:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def quantize_clunky(img: Image.Image, colors: int = 96) -> Image.Image:
    """Quantize frame with retro indexed palette for an authentic clunky eQSL GIF feel."""
    return img.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT)


def draw_outlined_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple,
    outline: tuple = (0, 0, 0, 245),
    width: int = 2,
    anchor: str | None = None,
) -> None:
    x, y = xy
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx * dx + dy * dy > 0 and abs(dx) + abs(dy) <= width + 1:
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


# ==============================================================================
# 8 BESPOKE POSTCARD QSL GIF RENDERERS (WITH FRAME A / FRAME B POSES)
# ==============================================================================

def render_qsl_radio_corrugated(preset: dict) -> list[Image.Image]:
    """1. SW4-CORR (Radio Corrugated): Pirate Couple Rooftop Snapshot (Chen & Mei-Ling).
    Frames 0..4: Grinning with blowtorch & noodle bowl.
    Frames 5..9: Couple leans in and kisses on the roof while the blowtorch sparks a cyan-white plasma arc!
    """
    p_a = DOCS / "assets/plates/qsl_plate_radio_corrugated.jpg"
    p_b = DOCS / "assets/plates/qsl_plate_radio_corrugated_kiss.jpg"
    img_a = Image.open(p_a).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    img_b = Image.open(p_b if p_b.exists() else p_a).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)

    f_call = load_font(20, bold=True)
    f_name = load_font(12, bold=True)
    f_loc = load_font(11, bold=True)
    f_small = load_font(10, bold=True)

    frames: list[Image.Image] = []
    for idx in range(N_FRAMES):
        is_kiss = idx >= 5
        img = (img_b if is_kiss else img_a).copy()
        draw = ImageDraw.Draw(img, "RGBA")

        # Vintage Kodachrome cream postcard border
        draw.rectangle([0, 0, W - 1, H - 1], outline=(244, 236, 216, 255), width=5)
        draw.rectangle([5, 5, W - 6, H - 6], outline=(40, 28, 18, 220), width=1)

        # Concentric radio waves radiating from the copper dipole (126, 62)
        ant_x, ant_y = 126, 62
        for ring_i in range(2):
            r = 16 + ((idx * 10 + ring_i * 26) % 58)
            col = (56, 235, 255, 220) if is_kiss else (255, 225, 65, 200)
            draw.arc([ant_x - r, ant_y - r, ant_x + r, ant_y + r], start=200, end=340, fill=col, width=2)

        # Top-Right Compact Neon Pirate Badge
        draw.rectangle([W - 196, 10, W - 10, 56], fill=(18, 10, 24, 228), outline=(255, 70, 140, 255), width=2)
        draw_outlined_text(draw, (W - 103, 13), "SW4-CORR", f_call, fill=(255, 220, 60), anchor="ma")
        draw_outlined_text(draw, (W - 103, 38), "RADIO CORRUGATED", f_name, fill=(255, 110, 185), anchor="ma")

        # Action Tag in lower-left above strip
        if is_kiss:
            draw.rectangle([10, H - 64, 178, H - 40], fill=(35, 10, 24, 235), outline=(255, 90, 165, 255), width=2)
            draw.text((94, H - 52), "♥ +18dB TORCH KISS!", font=f_small, fill=(255, 190, 225), anchor="mm")
        else:
            draw.rectangle([10, H - 64, 178, H - 40], fill=(18, 24, 34, 230), outline=(56, 235, 255, 255), width=2)
            draw.text((94, H - 52), "★ STALL 19 • 350W", font=f_small, fill=(110, 245, 255), anchor="mm")

        # Bottom Postcard Bar (Zero Overlap)
        draw.rectangle([5, H - 34, W - 6, H - 5], fill=(15, 11, 18, 240))
        draw.line([5, H - 34, W - 6, H - 34], fill=(255, 190, 60, 255), width=2)
        draw.text((12, H - 19), "CALLISTO DOME-4 MARKET", font=f_loc, fill=(255, 245, 220), anchor="lm")
        draw.text((W - 12, H - 19), "11410 kHz AM", font=f_loc, fill=(56, 235, 255), anchor="rm")

        frames.append(quantize_clunky(img, colors=96))
    return frames


def render_qsl_buoy_n24(preset: dict) -> list[Image.Image]:
    """2. TM-N24/B (Hydrographic Buoy N-24): Onboard Buoy Mast-Cam & Bureau Hydrographique Telemetry Card.
    Frames 0..4: Onboard buoy camera looking past its own steel bracket, amber Fresnel lamp, and diagonal guy-wire at the Silt-Striders.
    Frames 5..9: One of the Silt-Striders walks right up to the foreground stainless-steel guy-wire and physically rubs its neck against the cable!
    """
    p_a_path = DOCS / "assets/plates/flow_n24_onboard_pov_a.jpg"
    p_b_path = DOCS / "assets/plates/flow_n24_onboard_rub_b.jpg"
    p_start = Image.open(p_a_path if p_a_path.exists() else DOCS / "assets/plates/cam_n24_shallows_start.jpg").convert("RGB")
    p_end = Image.open(p_b_path if p_b_path.exists() else p_a_path).convert("RGB")

    f_call = load_font(19, bold=True)
    f_hdr = load_font(11, bold=True)
    f_loc = load_font(11, bold=True)
    f_note = load_font(9, bold=True)

    frames: list[Image.Image] = []

    for idx in range(N_FRAMES):
        is_rub = idx >= 5
        raw_scene = p_end if is_rub else p_start
        scene = raw_scene.resize((W - 16, H - 66), Image.Resampling.LANCZOS)

        card = Image.new("RGB", (W, H), (242, 239, 228))
        card.paste(scene, (8, 34))
        draw = ImageDraw.Draw(card, "RGBA")

        draw.rectangle([2, 2, W - 3, H - 3], outline=(18, 48, 89, 255), width=2)
        draw.rectangle([8, 34, W - 8, H - 32], outline=(18, 48, 89, 255), width=2)

        # Top Official Header on Cream Cardstock
        draw.ellipse([10, 5, 32, 27], fill=(18, 48, 89, 255), outline=(212, 160, 40, 255), width=2)
        draw.line([21, 9, 21, 23], fill=(245, 242, 232, 255), width=2)
        draw.arc([14, 13, 28, 24], start=15, end=165, fill=(245, 242, 232, 255), width=2)
        draw.text((38, 17), "BUREAU HYDROGRAPHIQUE", font=f_hdr, fill=(18, 48, 89), anchor="lm")
        draw.text((W - 10, 17), "TM-N24/B", font=f_call, fill=(180, 45, 35), anchor="rm")

        # Subtle HUD Telemetry Pill in Top-Left of Onboard Cam View
        if is_rub:
            draw.rectangle([14, 40, 198, 60], fill=(10, 32, 48, 225), outline=(80, 245, 255, 255), width=1)
            draw.text((106, 50), "WIRE #2 RUB: -165 Hz BEND", font=f_note, fill=(110, 250, 255), anchor="mm")
        else:
            draw.rectangle([14, 40, 178, 60], fill=(12, 24, 38, 210), outline=(212, 160, 40, 220), width=1)
            draw.text((96, 50), "MAST-CAM • VVV 18 WPM", font=f_note, fill=(255, 230, 120), anchor="mm")

        # Bottom Postcard Bar (Clean, No Overlap)
        draw.rectangle([8, H - 30, W - 8, H - 5], fill=(18, 48, 89, 255))
        draw.line([236, H - 30, 236, H - 5], fill=(245, 242, 232, 255), width=2)
        draw.text((14, H - 17), "TITAN-MINOR SHALLOWS", font=f_loc, fill=(255, 255, 255), anchor="lm")
        draw.text((W - 14, H - 17), "3890 kHz • 85W", font=f_loc, fill=(255, 220, 95), anchor="rm")
        draw.point((12 + idx * 14, H - 7), fill=(15, 42, 80, 255))

        frames.append(quantize_clunky(card, colors=96))
    return frames


def render_qsl_m33_drift(preset: dict) -> list[Image.Image]:
    """3. M33-771/R (Autonomous Sonde M33-771): Industrial Device Identification & Telemetry Card.
    Left Panel: Orthographic CAD schematic of Model DS-771 Mk.IV Sonde + riveted industrial nameplate.
    Right Panel: Onboard wide-angle horizon camera bolted to the sonde (Frame A: standby salt flat; Frame B: active 4.2W whip burst & ion dust-devil).
    """
    p_a_path = DOCS / "assets/plates/flow_m33_onboard_cam_a.jpg"
    p_b_path = DOCS / "assets/plates/flow_m33_onboard_cam_b.jpg"
    cam_a = Image.open(p_a_path).convert("RGB").resize((216, 158), Image.Resampling.LANCZOS)
    cam_b = Image.open(p_b_path if p_b_path.exists() else p_a_path).convert("RGB").resize((216, 158), Image.Resampling.LANCZOS)

    f_call = load_font(16, bold=True)
    f_hdr = load_font(10, bold=True)
    f_loc = load_font(11, bold=True)
    f_tiny = load_font(9, bold=True)

    frames: list[Image.Image] = []
    for idx in range(N_FRAMES):
        is_burst = idx >= 5
        # Industrial dark-slate anodized chassis card
        card = Image.new("RGB", (W, H), (22, 28, 36))
        draw = ImageDraw.Draw(card, "RGBA")

        # Outer hazard-yellow & steel-gray industrial frame
        draw.rectangle([0, 0, W - 1, H - 1], outline=(234, 179, 8, 255), width=3)
        draw.rectangle([4, 4, W - 5, H - 5], outline=(71, 85, 105, 255), width=1)

        # Top Industrial Manufacturer Header
        draw.rectangle([5, 5, W - 6, 35], fill=(15, 20, 28, 255))
        draw.line([5, 35, W - 6, 35], fill=(234, 179, 8, 255), width=2)
        # Deep-Field Survey Octagonal Industrial Logo
        draw.regular_polygon((21, 20, 11), n_sides=8, fill=(234, 179, 8, 255), outline=(255, 255, 255, 255))
        draw.text((21, 20), "DS", font=f_tiny, fill=(15, 20, 28), anchor="mm")
        draw.text((37, 14), "DEEP-FIELD SURVEY TELEMETRY", font=f_hdr, fill=(234, 179, 8), anchor="lm")
        draw.text((37, 26), "DEV ID: SONDE DS-771 Mk.IV", font=f_tiny, fill=(148, 163, 184), anchor="lm")
        draw.text((W - 10, 20), "M33-771/R", font=f_call, fill=(56, 235, 190), anchor="rm")

        # LEFT PANEL (x=8..154, y=40..198): Orthographic CAD Schematic of Sonde Device
        draw.rectangle([8, 40, 154, 198], fill=(14, 26, 40, 255), outline=(56, 189, 248, 200), width=1)
        # Blueprint grid lines
        for gx in range(24, 154, 24):
            draw.line([gx, 41, gx, 197], fill=(24, 46, 68, 255), width=1)
        for gy in range(56, 198, 24):
            draw.line([9, gy, 153, gy], fill=(24, 46, 68, 255), width=1)

        # Draw Orthographic Sonde Diagram (Center x=81)
        sx = 81
        # Helical whip antenna at top (y=48..88)
        whip_col = (56, 255, 200, 255) if is_burst else (125, 211, 252, 230)
        draw.line([sx, 48, sx, 88], fill=whip_col, width=2)
        for wy in range(52, 86, 6):
            draw.arc([sx - 6, wy - 3, sx + 6, wy + 3], start=0, end=360, fill=whip_col, width=1)
        # Expanding RF ring around schematic whip tip on every frame
        r_rad = 6 + ((idx * 5) % 22)
        draw.arc([sx - r_rad, 50 - r_rad, sx + r_rad, 50 + r_rad], start=190, end=350, fill=whip_col, width=2)

        # Yellow sensor boom sticking out to right (y=92) + camera lens icon
        draw.rectangle([sx - 22, 88, sx + 38, 95], fill=(234, 179, 8, 230), outline=(255, 255, 255, 200), width=1)
        # Pressurized telemetry sphere/drum (y=95..130)
        draw.ellipse([sx - 22, 94, sx + 22, 132], fill=(30, 58, 82, 255), outline=(125, 211, 252, 255), width=2)
        # Solar panels & tripod legs (y=126..152)
        draw.line([sx - 16, 126, sx - 34, 150], fill=(148, 163, 184, 255), width=2)
        draw.line([sx + 16, 126, sx + 34, 150], fill=(148, 163, 184, 255), width=2)
        draw.line([sx, 132, sx, 150], fill=(148, 163, 184, 255), width=2)
        draw.line([sx - 40, 150, sx + 40, 150], fill=(100, 116, 139, 255), width=1)

        # Riveted Spec Plate at bottom of Left Panel
        draw.rectangle([12, 154, 150, 194], fill=(20, 24, 30, 255), outline=(234, 179, 8, 220), width=1)
        draw.text((16, 163), "SN: DS-771-04 • 4.2W", font=f_tiny, fill=(250, 204, 21), anchor="lm")
        draw.text((16, 175), "REED: 942mb [STUCK]", font=f_tiny, fill=(248, 113, 113), anchor="lm")
        st_txt = "TX: 1420.4 MHz ACTIVE" if is_burst else "TX: CAPACITOR CHARGE"
        st_col = (74, 222, 128) if is_burst else (148, 163, 184)
        draw.text((16, 187), st_txt, font=f_tiny, fill=st_col, anchor="lm")

        # RIGHT PANEL (x=160..376, y=40..198): Onboard Sonde Horizon Camera POV
        card.paste(cam_b if is_burst else cam_a, (160, 40))
        draw.rectangle([160, 40, 376, 198], outline=(234, 179, 8, 255) if is_burst else (100, 116, 139, 255), width=2)
        draw.rectangle([164, 44, 314, 60], fill=(12, 18, 26, 220), outline=(56, 235, 190, 220), width=1)
        cam_lbl = "ONBOARD CAM: 4.2W BURST" if is_burst else "ONBOARD CAM: SALT FLAT"
        draw.text((239, 52), cam_lbl, font=f_tiny, fill=(110, 250, 210), anchor="mm")

        # Bottom Industrial Bar (Zero Overlap)
        draw.rectangle([5, H - 32, W - 6, H - 5], fill=(15, 20, 28, 255))
        draw.line([5, H - 32, W - 6, H - 32], fill=(234, 179, 8, 255), width=2)
        draw.text((12, H - 18), "M-33 VEYRA-3 ALKALI BASIN", font=f_loc, fill=(241, 245, 249), anchor="lm")
        draw.text((W - 12, H - 18), "1420 MHz • 4.2W", font=f_loc, fill=(56, 235, 190), anchor="rm")

        frames.append(quantize_clunky(card, colors=96))
    return frames


def render_qsl_trojan_octal(preset: dict) -> list[Image.Image]:
    """4. E08-OCTAL (The Vulpecula Buzzer / Three-Five-Octal): Cryptic Emblem & Typographic Card.
    Features giant stencil call letters, 3-5-1 trefoil emblem, typewriter octal groups, and an accidental
    open-mic whistling tea-kettle that gets slammed with a red KEY 015 stamp!
    """
    f_huge = load_font(25, bold=True)
    f_call = load_font(19, bold=True)
    f_type = load_font(12, bold=True)
    f_loc = load_font(11, bold=True)
    f_small = load_font(10, bold=True)

    octal_groups = ["047", "312", "771", "351", "015", "220"]
    frames: list[Image.Image] = []

    for idx in range(N_FRAMES):
        card = Image.new("RGB", (W, H), (236, 218, 172))
        arr = np.array(card, dtype=np.float32)
        for y in range(0, H, 3):
            arr[y, :, :] *= 0.94
        card = Image.fromarray(arr.astype(np.uint8))
        draw = ImageDraw.Draw(card, "RGBA")

        draw.rectangle([4, 4, W - 5, H - 5], outline=(24, 18, 16, 255), width=3)
        draw.rectangle([9, 9, W - 10, H - 10], outline=(168, 24, 28, 255), width=1)

        # Top crimson header block
        draw.rectangle([10, 10, W - 11, 46], fill=(155, 18, 24, 255))
        draw.text((W // 2, 28), "THREE - FIVE - OCTAL", font=f_call, fill=(255, 235, 180), anchor="mm")

        # Left & Right Giant Call Letters (4VEH homage)
        draw.text((18, 70), "E08", font=f_huge, fill=(20, 16, 16))
        draw.text((18, 102), "OCT", font=f_huge, fill=(155, 18, 24))

        draw.text((W - 18, 70), "6440", font=f_huge, fill=(20, 16, 16), anchor="ra")
        draw.text((W - 18, 102), "kHz", font=f_huge, fill=(155, 18, 24), anchor="ra")

        # Center Emblem Box: Trefoil with '3 - 5 - 1'
        cx, cy = W // 2, 98
        draw.rectangle([104, 52, W - 104, 146], fill=(26, 20, 22, 255), outline=(155, 18, 24, 255), width=2)
        blade_angles = [(30, 90, "3"), (150, 210, "5"), (270, 330, "1")]
        for b_i, (a0, a1, digit) in enumerate(blade_angles):
            is_lit = (idx % 3) == b_i
            b_col = (245, 65, 75, 255) if is_lit else (95, 28, 32, 255)
            draw.pieslice([cx - 36, cy - 36, cx + 36, cy + 36], start=a0, end=a1, fill=b_col, outline=(255, 215, 120, 255))
            mid_rad = math.radians((a0 + a1) / 2.0)
            lx = int(cx + math.cos(mid_rad) * 22)
            ly = int(cy + math.sin(mid_rad) * 22)
            draw.text((lx, ly), digit, font=f_type, fill=(255, 255, 255) if is_lit else (220, 180, 150), anchor="mm")
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 215, 90, 255), outline=(20, 16, 16, 255), width=2)

        # Typewriter Octal Stream Box
        n_show = min(len(octal_groups), 1 + (idx * len(octal_groups)) // 7)
        typed_str = "GRP: " + " • ".join(octal_groups[:n_show])
        draw.rectangle([18, 154, W - 18, 184], fill=(248, 240, 215, 255), outline=(24, 18, 16, 255), width=2)
        draw.text((26, 169), typed_str, font=f_type, fill=(20, 16, 16), anchor="lm")

        # Accidental Open-Mic Tea Kettle + CLASSIFIED Stamp!
        if idx >= 5:
            draw.rectangle([W - 148, 146, W - 16, 190], fill=(255, 245, 150, 250), outline=(20, 16, 16, 255), width=2)
            draw.text((W - 82, 159), "⚠ KETTLE MIC OPEN!", font=f_small, fill=(180, 20, 20), anchor="mm")
            draw.text((W - 82, 176), "\"8 PLEATS!\"", font=f_type, fill=(20, 16, 16), anchor="mm")
        if idx >= 8:
            draw.rectangle([W - 154, 144, W - 14, 192], fill=(190, 20, 28, 232), outline=(255, 255, 255, 255), width=2)
            draw.text((W - 84, 168), "STAMPED: KEY 015", font=f_type, fill=(255, 245, 200), anchor="mm")

        # Bottom Location & Power Bar (Zero Overlap)
        draw.rectangle([10, H - 38, W - 11, H - 10], fill=(24, 18, 16, 255))
        draw.text((18, H - 24), "TROJAN L4 • SHARD #624", font=f_loc, fill=(245, 225, 180), anchor="lm")
        draw.text((W - 18, H - 24), "1.2 kW USB", font=f_loc, fill=(255, 110, 110), anchor="rm")

        frames.append(quantize_clunky(card, colors=64))
    return frames


def render_qsl_pedregal(preset: dict) -> list[Image.Image]:
    """5. XE9-PED/U (Pedregal Oort Weather Utility): Homemade Wheelhouse Snapshot & Clip-Art Tower Postcard.
    Frames 0..4: Capt. Rafa grins holding his blue cookie-tin transmitter.
    Frames 5..9: Capt. Rafa raises his left hand in a big warm wave while the vacuum tube flares bright gold!
    """
    p_a = DOCS / "assets/plates/qsl_plate_pedregal_rafa.jpg"
    p_b = DOCS / "assets/plates/qsl_plate_pedregal_rafa_wave.jpg"
    photo_a = Image.open(p_a).convert("RGB").resize((W - 116, H - 64), Image.Resampling.LANCZOS)
    photo_b = Image.open(p_b if p_b.exists() else p_a).convert("RGB").resize((W - 116, H - 64), Image.Resampling.LANCZOS)

    f_call = load_font(18, bold=True)
    f_sub = load_font(11, bold=True)
    f_loc = load_font(11, bold=True)
    f_tiny = load_font(9, bold=True)

    frames: list[Image.Image] = []

    for idx in range(N_FRAMES):
        is_waving = idx >= 5
        card = Image.new("RGB", (W, H), (250, 248, 242))
        card.paste(photo_b if is_waving else photo_a, (106, 36))
        draw = ImageDraw.Draw(card, "RGBA")

        draw.rectangle([2, 2, W - 3, H - 3], outline=(14, 116, 144, 255), width=3)
        draw.rectangle([106, 36, W - 10, H - 28], outline=(20, 35, 50, 255), width=2)

        # Top Banner (Clean, No Overlap)
        draw.rectangle([5, 5, W - 6, 32], fill=(14, 116, 144, 255))
        draw.text((12, 18), "XE9-PED/U • RADIO PEDREGAL", font=f_call, fill=(255, 240, 100), anchor="lm")
        draw.text((W - 12, 18), "QSL #1", font=f_sub, fill=(255, 255, 255), anchor="rm")

        # Left Sidebar: Clip-Art Radio Tower ("3W BIG SIGNAL!" homage to Pancho Villa QSL)
        tx_c, ty_top = 54, 62
        draw.line([tx_c, ty_top, tx_c - 22, 146], fill=(25, 30, 40, 255), width=2)
        draw.line([tx_c, ty_top, tx_c + 22, 146], fill=(25, 30, 40, 255), width=2)
        for y_bar in (82, 102, 122, 140):
            hw = int((y_bar - ty_top) * 0.25)
            draw.line([tx_c - hw, y_bar, tx_c + hw, y_bar], fill=(25, 30, 40, 255), width=2)
        draw.ellipse([tx_c - 4, ty_top - 4, tx_c + 4, ty_top + 4], fill=(220, 38, 38, 255))

        for r_i in range(3):
            r_w = 10 + ((idx * 6 + r_i * 12) % 34)
            w_col = (234, 88, 12, 255) if is_waving else (14, 116, 144, 255)
            draw.arc([tx_c - r_w, ty_top - r_w, tx_c + r_w, ty_top + r_w], start=195, end=345, fill=w_col, width=2)

        if is_waving:
            draw.rectangle([8, 152, 100, 174], fill=(254, 240, 138, 255), outline=(202, 138, 4, 255), width=2)
            draw.text((54, 163), "3W BIG SIGNAL!", font=f_tiny, fill=(153, 27, 27), anchor="mm")
        else:
            draw.rectangle([8, 152, 100, 174], fill=(220, 252, 231, 255), outline=(22, 101, 52, 255), width=2)
            draw.text((54, 163), "COOKIE-TIN QRP", font=f_tiny, fill=(22, 101, 52), anchor="mm")

        draw.text((54, 188), "Capt. Rafa", font=f_sub, fill=(14, 116, 144), anchor="mm")
        draw.text((54, 201), "PIRATE UTILITY", font=f_tiny, fill=(180, 83, 9), anchor="mm")

        # Bottom Postcard Bar (Zero Overlap)
        draw.rectangle([5, H - 26, W - 6, H - 5], fill=(20, 35, 50, 255))
        draw.text((12, H - 15), "MV BOCA DEL RÍO • OORT 9W", font=f_loc, fill=(255, 255, 255), anchor="lm")
        draw.text((W - 12, H - 15), "6969.5 kHz • 3W", font=f_loc, fill=(103, 232, 249), anchor="rm")

        frames.append(quantize_clunky(card, colors=96))
    return frames


def render_qsl_kz9_omega(preset: dict) -> list[Image.Image]:
    """6. KZ9-OMEGA (Relay Station KZ9-OMEGA): Onboard Tower #1 Mast-Cam POV & Violation Stamp Card.
    Frames 0..4: Onboard Tower #1 inspection camera looking down past steel truss & ceramic insulators at the twin 18m dishes.
    Frames 5..9: 60 kV cyan plasma arc leaps from lower dish into the foreground ceramic standoff insulator with 2px shake & red NOV stamp!
    """
    p_calm = DOCS / "assets/plates/flow_kz9_mast_pov_a.jpg"
    p_arc = DOCS / "assets/plates/flow_kz9_mast_pov_b.jpg"
    if not p_calm.exists():
        p_calm = DOCS / "assets/plates/cam02_relay_storm_start.jpg"
    if not p_arc.exists():
        p_arc = DOCS / "assets/plates/cam02_relay_storm_end.jpg"

    img_calm = Image.open(p_calm).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    img_arc = Image.open(p_arc).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    img_calm = ImageEnhance.Contrast(img_calm).enhance(1.12)
    img_arc = ImageEnhance.Contrast(img_arc).enhance(1.18)

    f_call = load_font(19, bold=True)
    f_corp = load_font(9, bold=True)
    f_loc = load_font(11, bold=True)
    f_stamp = load_font(10, bold=True)

    frames: list[Image.Image] = []

    for idx in range(N_FRAMES):
        is_arc = idx >= 5
        src = img_arc if is_arc else img_calm
        if is_arc and idx % 2 == 1:
            arr = np.roll(np.array(src), shift=(-1, 2), axis=(0, 1))
            img = Image.fromarray(arr)
        else:
            img = src.copy()

        draw = ImageDraw.Draw(img, "RGBA")
        draw.rectangle([0, 0, W - 1, H - 1], outline=(235, 175, 55, 255), width=4)

        # Invisible 1px frame-uniqueness marker in bottom border so all 10 frames are distinct
        draw.point((12 + idx * 4, H - 5), fill=(30 + idx * 10, 35, 45, 255))

        # Top Corporate Nameplate Banner (Zero Overlap)
        draw.rectangle([4, 4, W - 5, 40], fill=(18, 22, 30, 242))
        draw.line([4, 40, W - 5, 40], fill=(235, 175, 55, 255), width=2)

        gx, gy = 22, 22
        draw.ellipse([gx - 12, gy - 12, gx + 12, gy + 12], fill=(40, 30, 14, 255), outline=(240, 184, 73, 255), width=2)
        draw.text((gx, gy), "VA", font=f_stamp, fill=(240, 184, 73), anchor="mm")
        draw.text((40, 15), "VAN ALLEN SWITCHGEAR", font=f_corp, fill=(240, 184, 73), anchor="lm")
        draw.text((40, 29), "TOWER #1 MAST-CAM POV", font=f_corp, fill=(180, 195, 215), anchor="lm")
        draw.text((W - 12, 22), "KZ9-OMEGA", font=f_call, fill=(255, 255, 255), anchor="rm")

        if is_arc:
            draw.rectangle([12, H - 66, 224, H - 38], fill=(165, 18, 32, 238), outline=(255, 220, 220, 255), width=2)
            draw.text((118, H - 52), "⚠ NOV CITED: ±30 kHz SPLATTER", font=f_stamp, fill=(255, 245, 190), anchor="mm")

        # Bottom Postcard Bar (Zero Overlap)
        draw.rectangle([4, H - 34, W - 5, H - 4], fill=(18, 22, 30, 245))
        draw.line([4, H - 34, W - 5, H - 34], fill=(235, 175, 55, 255), width=2)
        draw.text((12, H - 19), "AURELIA-IV • MERIDIAN", font=f_loc, fill=(255, 245, 220), anchor="lm")
        draw.text((W - 12, H - 19), "7140 kHz • 50 kW", font=f_loc, fill=(80, 240, 255), anchor="rm")

        frames.append(quantize_clunky(img, colors=96))
    return frames


def render_qsl_radio_free_hektor(preset: dict) -> list[Image.Image]:
    """7. RFH-HOP (Radio Free Hektor): Frequency-Hopping Rebel Accordion Crawler Postcard.
    Frames 0..4: Zora squeezing red accordion on Crawler X-74 (6440 kHz).
    Frames 5..9: Zora throws both hands up laughing/waving as antenna blazes green/gold and hops to 6445 kHz!
    """
    p_a = DOCS / "assets/plates/qsl_plate_radio_free_hektor.jpg"
    p_b = DOCS / "assets/plates/qsl_plate_radio_free_hektor_b.jpg"
    img_a = Image.open(p_a).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    img_b = Image.open(p_b if p_b.exists() else p_a).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)

    f_call = load_font(15, bold=True)
    f_hop = load_font(11, bold=True)
    f_loc = load_font(11, bold=True)
    f_small = load_font(9, bold=True)

    hops = [
        (78, 66, "6440 kHz"),
        (86, 120, "6445 kHz"),
    ]
    frames: list[Image.Image] = []

    for idx in range(N_FRAMES):
        is_hop = idx >= 5
        img = (img_b if is_hop else img_a).copy()
        draw = ImageDraw.Draw(img, "RGBA")

        draw.rectangle([0, 0, W - 1, H - 1], outline=(250, 204, 21, 255), width=5)
        draw.rectangle([5, 5, W - 6, H - 6], outline=(15, 20, 28, 255), width=2)

        # Expanding whip-antenna radio waves at top-right (304, 48)
        ax, ay = 304, 48
        for r_i in range(2):
            rad = 12 + ((idx * 9 + r_i * 20) % 44)
            col = (74, 222, 128, 225) if is_hop else (250, 204, 21, 200)
            draw.arc([ax - rad, ay - rad, ax + rad, ay + rad], start=130, end=260, fill=col, width=2)

        # Top Pirate Header Banner (Generous spacing between title and 180W)
        draw.rectangle([6, 6, W - 7, 35], fill=(20, 16, 12, 238))
        draw.line([6, 35, W - 7, 35], fill=(250, 204, 21, 255), width=2)
        draw.text((12, 20), "RFH-HOP • RADIO FREE HEKTOR", font=f_call, fill=(250, 204, 21), anchor="lm")
        draw.text((W - 12, 20), "180W", font=f_hop, fill=(74, 222, 128), anchor="rm")

        # Hopping Frequency Badge vs. Late Syndicate Jammer Crosshair!
        cur_hop_i = 1 if is_hop else 0
        prev_hop_i = 0 if is_hop else 1

        hx, hy, h_freq = hops[cur_hop_i]
        draw.rectangle([hx - 54, hy - 14, hx + 54, hy + 14], fill=(16, 48, 28, 240), outline=(74, 222, 128, 255), width=2)
        draw.text((hx, hy - 4), f"HOP: {h_freq}", font=f_hop, fill=(134, 239, 172), anchor="mm")
        sub_txt = "★ ZORA WAVING!" if is_hop else "♫ ACCORDION LIVE"
        draw.text((hx, hy + 8), sub_txt, font=f_small, fill=(255, 240, 130), anchor="mm")

        jx, jy, j_freq = hops[prev_hop_i]
        draw.ellipse([jx - 18, jy - 18, jx + 18, jy + 18], outline=(244, 63, 94, 240), width=2)
        draw.line([jx - 24, jy, jx + 24, jy], fill=(244, 63, 94, 240), width=2)
        draw.line([jx, jy - 24, jx, jy + 24], fill=(244, 63, 94, 240), width=2)
        draw_outlined_text(draw, (jx, jy + 22), f"JAMMER @ {j_freq}", f_small, fill=(255, 130, 140), anchor="ma")

        # Bottom Postcard Strip (Zero Overlap)
        draw.rectangle([6, H - 34, W - 7, H - 6], fill=(20, 16, 12, 245))
        draw.line([6, H - 34, W - 7, H - 34], fill=(250, 204, 21, 255), width=2)
        draw.text((12, H - 20), "TROJAN L4 • SHARD #624", font=f_loc, fill=(255, 255, 255), anchor="lm")
        draw.text((W - 12, H - 20), "6435–6445 kHz", font=f_loc, fill=(74, 222, 128), anchor="rm")

        frames.append(quantize_clunky(img, colors=96))
    return frames


def render_qsl_st_jerome_slag(preset: dict) -> list[Image.Image]:
    """8. VJB-3X (Vael-Vihara Harmonic Spire on Planet Kaelen-V): Ethereal Alien Sanctuary & Bowing Monks Card.
    Frames 0..4: Two tall, slender, pearlescent alien monks stand serenely on a crystal terrace; fluted alabaster monastery & giant golden spire in the distance.
    Frames 5..9: Both ethereal alien monks bow gracefully in unison as the distant monastery spire ignites with golden harmonic light rings!
    """
    p_a = DOCS / "assets/plates/qsl_plate_alien_monastery_a.jpg"
    p_b = DOCS / "assets/plates/qsl_plate_alien_monastery_b.jpg"
    img_a = Image.open(p_a).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    img_b = Image.open(p_b if p_b.exists() else p_a).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)

    f_call = load_font(18, bold=True, serif=True)
    f_loc = load_font(10, bold=True)
    f_tag = load_font(9, bold=True)

    frames: list[Image.Image] = []

    for idx in range(N_FRAMES):
        is_bowing = idx >= 5
        img = (img_b if is_bowing else img_a).copy()
        draw = ImageDraw.Draw(img, "RGBA")

        # Elegant Sacred-Geometric Gold-Leaf Border (No heavy woodblock or cartoon rings)
        gold_outer = (228, 192, 112, 235) if not is_bowing else (255, 222, 135, 250)
        draw.rectangle([0, 0, W - 1, H - 1], outline=(18, 16, 28, 255), width=4)
        draw.rectangle([4, 4, W - 5, H - 5], outline=gold_outer, width=1)

        # Invisible 1px frame-uniqueness marker in bottom border so all 10 frames remain distinct
        draw.point((14 + idx * 4, H - 9), fill=(25 + idx * 10, 22, 38, 255))

        # Top-Left Translucent Obsidian & Gold-Leaf Cartouche (Leaves the distant spire & monks completely unobstructed)
        draw.rectangle([10, 10, 148, 52], fill=(16, 14, 28, 218), outline=gold_outer, width=1)
        draw.text((79, 23), "VJB-3X", font=f_call, fill=(250, 224, 150), anchor="mm")
        sub_txt = "✦ CONVERGENCE BOW" if is_bowing else "VAEL-VIHARA SPIRE"
        sub_col = (135, 245, 210) if is_bowing else (210, 198, 235)
        draw.text((79, 41), sub_txt, font=f_tag, fill=sub_col, anchor="mm")

        # Bottom Translucent Obsidian & Gold-Leaf Strip (Zero Overlap)
        draw.rectangle([10, H - 32, W - 10, H - 8], fill=(16, 14, 28, 228), outline=gold_outer, width=1)
        draw.text((18, H - 20), "KAELEN-V • VAEL-VIHARA SANCTUARY", font=f_loc, fill=(242, 234, 218), anchor="lm")
        draw.text((W - 18, H - 20), "9290 kHz • 3-BAND", font=f_loc, fill=(250, 215, 125), anchor="rm")

        frames.append(quantize_clunky(img, colors=96))
    return frames


RENDERER_DISPATCH = {
    "radio-corrugated": render_qsl_radio_corrugated,
    "buoy-n24": render_qsl_buoy_n24,
    "m33-drift-buoy": render_qsl_m33_drift,
    "trojan-octal": render_qsl_trojan_octal,
    "pedregal-utility": render_qsl_pedregal,
    "kz9-omega": render_qsl_kz9_omega,
    "radio-free-hektor": render_qsl_radio_free_hektor,
    "st-jerome-slag": render_qsl_st_jerome_slag,
}


def build_qsl_gif(preset: dict) -> Path:
    """Render a unique postcard QSL animated GIF for a station and save to docs/assets/qsl/."""
    pid = preset["id"]
    renderer = RENDERER_DISPATCH.get(pid, render_qsl_radio_corrugated)
    frames = renderer(preset)

    out_path = DOCS / preset["qsl"]["gif_src"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=160,
        loop=0,
        optimize=False,
    )
    print(f"Generated unique Postcard QSL GIF: {out_path.relative_to(ROOT)} ({out_path.stat().st_size // 1024} KB)")
    return out_path


# ==============================================================================
# AUDIO SYNTHESIS (INTERVAL SIGNALS, SSTV BURSTS, & INTERCEPTS)
# ==============================================================================

def make_sstv_burst(seed: int = 11410, duration: float = 2.0) -> np.ndarray:
    """Synthesize an authentic Robot-36 / FSK QSL verification burst (1900Hz leader + scanline chirps)."""
    rng = np.random.default_rng(seed)
    n = int(SAMPLE_RATE * duration)
    sig = np.zeros(n, dtype=np.float64)

    header_notes = [
        (0.00, 0.18, 1900.0),
        (0.18, 0.04, 1200.0),
        (0.22, 0.18, 1900.0),
        (0.40, 0.03, 1200.0),
        (0.43, 0.03, 1100.0),
        (0.46, 0.03, 1300.0),
        (0.49, 0.03, 1100.0),
        (0.52, 0.03, 1200.0),
    ]
    for t0, dur, f in header_notes:
        i0 = int(t0 * SAMPLE_RATE)
        d = min(int(dur * SAMPLE_RATE), n - i0)
        tt = np.arange(d, dtype=np.float64) / SAMPLE_RATE
        sig[i0:i0 + d] += 0.28 * np.sin(2.0 * math.pi * f * tt)

    t_scan = 0.56
    line_dur = 0.088
    while t_scan < duration - 0.05:
        i0 = int(t_scan * SAMPLE_RATE)
        d = min(int(line_dur * SAMPLE_RATE), n - i0)
        sync_samples = min(d, int(0.009 * SAMPLE_RATE))
        f_line = np.full(d, 1200.0, dtype=np.float64)
        if d > sync_samples:
            u = np.linspace(0.0, 1.0, d - sync_samples)
            f_lum = 1500.0 + 750.0 * (
                0.5
                + 0.3 * np.sin(2.0 * math.pi * 3.0 * u + rng.uniform(0, 6.28))
                + 0.2 * np.cos(2.0 * math.pi * 7.0 * u)
            )
            f_line[sync_samples:] = f_lum
        ph = 2.0 * math.pi * np.cumsum(f_line) / SAMPLE_RATE
        sig[i0:i0 + d] += 0.24 * np.sin(ph)
        t_scan += line_dur

    hiss = np.convolve(rng.normal(0.0, 0.025, size=n), np.ones(7) / 7.0, mode="same")
    return np.clip(sig + hiss, -0.85, 0.85)


def make_interval_and_intercept(preset: dict) -> tuple[Path, Path, Path]:
    """Generate Interval Signal WAV, SSTV Burst WAV, and Extended Intercept WAV for a station."""
    pid = preset["id"]
    rng = np.random.default_rng(int(preset["rf"]["frequency_khz"]))

    dur_is = 4.2
    n_is = int(SAMPLE_RATE * dur_is)
    t = np.arange(n_is, dtype=np.float64) / SAMPLE_RATE
    is_sig = np.zeros(n_is, dtype=np.float64)

    if pid == "radio-corrugated":
        notes = [
            (0.15, 0.42, 392.0),
            (0.60, 0.42, 440.0),
            (1.05, 0.45, 523.25),
            (1.55, 0.55, 587.33),
            (2.15, 0.85, 783.99),
            (3.10, 0.45, 587.33),
            (3.58, 0.55, 523.25),
        ]
        for t0, d, f in notes:
            i0 = int(t0 * SAMPLE_RATE)
            m = min(int(d * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            vib = 3.2 * np.sin(2.0 * math.pi * 5.8 * tt)
            pluck = (
                0.55 * np.sin(2.0 * math.pi * (f + vib) * tt)
                + 0.28 * np.sin(2.0 * math.pi * 2.0 * (f + vib) * tt)
                + 0.14 * np.sin(2.0 * math.pi * 3.0 * (f + vib) * tt)
            ) * np.exp(-tt / 0.24)
            is_sig[i0:i0 + m] += pluck * 0.34
    elif pid == "buoy-n24":
        for tc in (0.2, 0.65, 2.1, 2.55):
            i0 = int(tc * SAMPLE_RATE)
            m = min(int(0.8 * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            bell = (
                0.5 * np.sin(2.0 * math.pi * 612.0 * tt)
                + 0.35 * np.sin(2.0 * math.pi * 1148.0 * tt)
                + 0.25 * np.sin(2.0 * math.pi * 1715.0 * tt)
            ) * np.exp(-tt / 0.19)
            is_sig[i0:i0 + m] += bell * 0.30
        f_theremin = 880.0 - 82.5 * (1.0 - np.cos(2.0 * math.pi * 0.55 * t))
        ph_th = 2.0 * math.pi * np.cumsum(f_theremin) / SAMPLE_RATE
        is_sig += 0.16 * np.sin(ph_th) * (0.5 + 0.5 * np.sin(2.0 * math.pi * 0.25 * t))
    elif pid == "m33-drift-buoy":
        melody = [
            (0.15, 0.70, 659.25),
            (0.88, 0.70, 783.99),
            (1.62, 0.85, 987.77),
            (2.50, 0.70, 880.00),
            (3.22, 0.85, 659.25),
        ]
        for t0, d, f in melody:
            i0 = int(t0 * SAMPLE_RATE)
            m = min(int(d * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            env = np.sin(math.pi * tt / d) ** 0.45
            flute = (
                0.7 * np.sin(2.0 * math.pi * (f + 4.0 * np.sin(2 * math.pi * 4.5 * tt)) * tt)
                + 0.2 * np.sin(2.0 * math.pi * 2.0 * f * tt)
            ) * env
            is_sig[i0:i0 + m] += flute * 0.30
    elif pid == "trojan-octal":
        chimes = [
            (0.15, 0.45, 523.25),
            (0.55, 0.45, 587.33),
            (0.95, 0.45, 659.25),
            (1.35, 0.45, 739.99),
            (1.75, 0.85, 783.99),
            (2.75, 0.45, 523.25),
            (3.15, 0.45, 739.99),
            (3.55, 0.60, 1046.50),
        ]
        for t0, d, f in chimes:
            i0 = int(t0 * SAMPLE_RATE)
            m = min(int(d * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            ch = (0.65 * np.sin(2 * math.pi * f * tt) + 0.35 * np.sin(2 * math.pi * 2.76 * f * tt)) * np.exp(-tt / 0.22)
            is_sig[i0:i0 + m] += ch * 0.30
        is_sig += 0.045 * np.sin(2.0 * math.pi * 641.928 * t)
    elif pid == "pedregal-utility":
        chords = [(0.2, 0.9, 329.63), (0.5, 0.9, 440.0), (0.8, 1.1, 554.37), (2.2, 0.9, 440.0), (2.6, 1.2, 659.25)]
        for t0, d, f in chords:
            i0 = int(t0 * SAMPLE_RATE)
            m = min(int(d * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            is_sig[i0:i0 + m] += 0.26 * (np.sin(2 * math.pi * f * tt) + 0.4 * np.sin(4 * math.pi * f * tt)) * np.exp(-tt / 0.32)
    elif pid == "radio-free-hektor":
        acc_notes = [
            (0.10, 0.32, 440.0, 554.37),
            (0.45, 0.32, 493.88, 659.25),
            (0.80, 0.40, 523.25, 659.25),
            (1.25, 0.55, 587.33, 739.99),
            (1.90, 0.32, 659.25, 880.00),
            (2.28, 0.32, 587.33, 739.99),
            (2.65, 0.65, 440.00, 659.25),
            (3.45, 0.60, 440.00, 880.00),
        ]
        for t0, d, f1, f2 in acc_notes:
            i0 = int(t0 * SAMPLE_RATE)
            m = min(int(d * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            reed = (
                0.45 * np.sin(2 * math.pi * f1 * tt)
                + 0.35 * np.sin(2 * math.pi * (f1 * 1.003) * tt)
                + 0.30 * np.sin(2 * math.pi * f2 * tt)
                + 0.18 * np.sin(2 * math.pi * 2.0 * f1 * tt)
            ) * (1.0 - np.exp(-tt / 0.03)) * np.exp(-tt / (d * 1.1))
            is_sig[i0:i0 + m] += reed * 0.32
    elif pid == "st-jerome-slag":
        # Tibetan singing-bowl + harmonic throat-chant overtone rectified through stupa diode
        for tb in (0.25, 1.65, 3.05):
            i0 = int(tb * SAMPLE_RATE)
            m = min(int(1.25 * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            bowl = (
                0.55 * np.sin(2 * math.pi * 256.0 * tt)
                + 0.35 * np.sin(2 * math.pi * 384.0 * tt)
                + 0.25 * np.sin(2 * math.pi * 512.0 * tt)
                + 0.18 * np.sin(2 * math.pi * 768.0 * tt)
            ) * np.exp(-tt / 0.55)
            rectified = np.where(bowl > 0, bowl * 1.25, bowl * 0.35)
            is_sig[i0:i0 + m] += rectified * 0.32
    else:
        is_sig += 0.08 * np.sin(2.0 * math.pi * 120.0 * t) * (0.6 + 0.4 * np.sin(2.0 * math.pi * 8.0 * t))
        for ta in (0.45, 1.65, 2.95):
            i0 = int(ta * SAMPLE_RATE)
            m = min(int(0.35 * SAMPLE_RATE), n_is - i0)
            tt = np.arange(m, dtype=np.float64) / SAMPLE_RATE
            arc = rng.normal(0.0, 0.45, size=m) * np.exp(-tt / 0.09)
            is_sig[i0:i0 + m] += arc

    hiss = np.convolve(rng.normal(0.0, 0.028, size=n_is), np.ones(9) / 9.0, mode="same")
    fade = 0.78 + 0.22 * np.sin(2.0 * math.pi * 0.45 * t)
    is_final = np.clip((is_sig + hiss) * fade, -0.88, 0.88)

    is_path = DOCS / preset["media"]["interval_signal_src"]
    save_wav(is_path, is_final)

    sstv_arr = make_sstv_burst(seed=int(preset["rf"]["frequency_khz"]))
    sstv_path = DOCS / preset["media"]["sstv_burst_src"]
    save_wav(sstv_path, sstv_arr)

    voices_dir = DOCS / "assets" / "audio" / "voices"
    vignette_arr = np.zeros(int(SAMPLE_RATE * 2.6), dtype=np.float64)
    if pid == "st-jerome-slag" and (voices_dir / "voice_cantor_auren7_rf.wav").exists():
        # Build a dramatic 34s On-Air DX Tuning & Tri-Band Spire Lock Intercept:
        # 1) 1.8s VFO tuning heterodyne sweep (2,100 Hz -> 0 Hz zero-beat lock) through heavy shortwave static
        n_tune = int(1.8 * SAMPLE_RATE)
        tt = np.arange(n_tune, dtype=np.float64) / SAMPLE_RATE
        f_het = 2100.0 * np.exp(-tt / 0.42) + 118.0
        vfo_whistle = np.sin(2.0 * math.pi * np.cumsum(f_het) / SAMPLE_RATE) * 0.24 * np.exp(-tt / 1.1)
        tune_static = rng.normal(0.0, 0.16, size=n_tune) * np.linspace(1.0, 0.45, n_tune)
        vfo_lock = np.clip(vfo_whistle + tune_static, -0.88, 0.88)

        # 2) First 27s of the Call & Response RF intercept + last 5.5s of the 5-Voice Choir RF finale (with the little trill & gong!)
        rf_call = load_wav_float(voices_dir / "voice_cantor_auren7_rf.wav")
        call_excerpt = rf_call[:min(len(rf_call), int(27.5 * SAMPLE_RATE))]
        if (voices_dir / "voice_vael_choir_rf.wav").exists():
            rf_choir = load_wav_float(voices_dir / "voice_vael_choir_rf.wav")
            finale_excerpt = rf_choir[max(0, len(rf_choir) - int(6.5 * SAMPLE_RATE)):]
            vignette_core = np.concatenate([vfo_lock, call_excerpt, finale_excerpt])
        else:
            vignette_core = np.concatenate([vfo_lock, call_excerpt])

        # Add extra deep-space 31m + 21cm cross-band selective fading and AGC grit for the main receiver intercept
        tv = np.arange(len(vignette_core), dtype=np.float64) / SAMPLE_RATE
        deep_qsb = 0.72 + 0.28 * np.sin(2.0 * math.pi * 0.22 * tv)
        extra_static = np.convolve(rng.normal(0.0, 0.055, size=len(tv)), np.ones(7) / 7.0, mode="same")
        vignette_arr = np.tanh((vignette_core * deep_qsb + extra_static) * 1.45) * 0.86
    elif pid == "radio-corrugated" and (EP1_SEG_DIR / "vignette_radio_corrugated.wav").exists():
        vignette_arr = load_wav_float(EP1_SEG_DIR / "vignette_radio_corrugated.wav")
    elif pid == "buoy-n24" and (EP1_SEG_DIR / "vignette_buoy_n24.wav").exists():
        vignette_arr = load_wav_float(EP1_SEG_DIR / "vignette_buoy_n24.wav")
    elif preset.get("characters") and preset["characters"][0].get("voice_sample_rf_src"):
        rf_p = DOCS / preset["characters"][0]["voice_sample_rf_src"]
        if rf_p.exists():
            vignette_arr = load_wav_float(rf_p)
    else:
        tv = np.arange(len(vignette_arr), dtype=np.float64) / SAMPLE_RATE
        carrier_het = 0.04 * np.sin(2.0 * math.pi * 1020.0 * tv)
        fsk = 0.16 * np.sin(2.0 * math.pi * (740.0 + 170.0 * np.sign(np.sin(2.0 * math.pi * 6.5 * tv))) * tv)
        vignette_arr = carrier_het + fsk + np.convolve(rng.normal(0.0, 0.035, size=len(tv)), np.ones(9) / 9.0, mode="same")

    full_intercept = np.concatenate([is_final[:int(SAMPLE_RATE * 2.8)], vignette_arr, sstv_arr[:int(SAMPLE_RATE * 1.4)]])
    intercept_path = DOCS / preset["media"]["audio_intercept_src"]
    save_wav(intercept_path, full_intercept)
    return is_path, sstv_path, intercept_path


# ==============================================================================
# PER-STATION FOLDER & WORLDBUILDING GENERATOR (`stations/<station_slug>/`)
# ==============================================================================

def build_station_folder(preset: dict, qsl_gif_path: Path, audio_paths: tuple[Path, Path, Path]) -> None:
    """Populate dedicated `stations/<station_slug>/` directory with station.json, WORLDBUILDING.md, plates, qsl, and audio."""
    slug = preset["station_folder"]
    s_dir = STATIONS_ROOT / slug
    (s_dir / "plates").mkdir(parents=True, exist_ok=True)
    (s_dir / "qsl").mkdir(parents=True, exist_ok=True)
    (s_dir / "audio").mkdir(parents=True, exist_ok=True)

    (s_dir / "station.json").write_text(json.dumps(preset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    shutil.copy2(qsl_gif_path, s_dir / "qsl" / qsl_gif_path.name)
    for ap in audio_paths:
        if ap.exists():
            shutil.copy2(ap, s_dir / "audio" / ap.name)

    for key in ("poster_src", "alt_plate_src", "qsl_plate_src", "qsl_plate_b_src"):
        rel = preset["media"].get(key)
        if rel:
            src_p = DOCS / rel
            if src_p.exists():
                shutil.copy2(src_p, s_dir / "plates" / src_p.name)

    flow_plate_lines = []
    for fp_rel in preset["media"].get("flow_plates", []):
        src_p = DOCS / fp_rel
        if src_p.exists():
            shutil.copy2(src_p, s_dir / "plates" / src_p.name)
            flow_plate_lines.append(f"- **[`plates/{src_p.name}`](./plates/{src_p.name})** (`16:9` Flow Reference Plate)")

    wb = preset.get("worldbuilding", {})
    chars = preset.get("characters", [])
    (s_dir / "characters").mkdir(parents=True, exist_ok=True)
    char_lines = []
    for c in chars:
        hs_rel = c.get("headshot_src")
        fb_rel = c.get("fullbody_src")
        dry_rel = c.get("voice_sample_dry_src")
        rf_rel = c.get("voice_sample_rf_src")
        for asset_rel in (hs_rel, fb_rel, dry_rel, rf_rel):
            if asset_rel:
                src_p = DOCS / asset_rel
                if src_p.exists():
                    shutil.copy2(src_p, s_dir / "characters" / src_p.name)

        c_block = [
            f"### 👤 {c['name']} — *{c['role']}*",
            f"- **Species / Type**: {c['species_or_type']}",
            f"- **Languages & Dialect**: {c['languages']} (*{c['dialect_notes']}*)",
        ]
        if c.get("phonetic_and_conlang_notes"):
            c_block.append(f"- **Phonetics & Conlang Spec**: {c['phonetic_and_conlang_notes']}")
        c_block.extend([
            f"- **Voice & TTS Casting**: `{c['voice_profile']['tts_voice']}` • {c['voice_profile']['cadence']} ({c['voice_profile']['dsp_chain']})",
            f"- **Signature Quote / On-Air Catchphrase**: *\"{c['signature_quote']}\"*",
            f"- **Backstory**: {c['bio']}",
        ])
        if hs_rel or fb_rel:
            vis_links = []
            if hs_rel:
                hs_name = Path(hs_rel).name
                vis_links.append(f"[`characters/{hs_name}`](./characters/{hs_name}) (16:9 Headshot)")
            if fb_rel:
                fb_name = Path(fb_rel).name
                vis_links.append(f"[`characters/{fb_name}`](./characters/{fb_name}) (16:9 Full-Body Cyclorama)")
            c_block.append(f"- **Google Flow Visual Reference Plates**: {' • '.join(vis_links)}")
        if c.get("language_sample_transcript"):
            c_block.append(f"- **Recorded Voice & Language Sample Transcript**: *\"{c['language_sample_transcript']}\"*")
        if dry_rel or rf_rel:
            wav_links = []
            if dry_rel:
                dry_name = Path(dry_rel).name
                wav_links.append(f"[`characters/{dry_name}`](./characters/{dry_name}) (Dry Studio Voice)")
            if rf_rel:
                rf_name = Path(rf_rel).name
                wav_links.append(f"[`characters/{rf_name}`](./characters/{rf_name}) (On-Air RF Intercept)")
            c_block.append(f"- **Voice & Language Audio Samples (`24 kHz WAV`)**: {' • '.join(wav_links)}")
        c_block.append("")
        char_lines.extend(c_block)

    arc_lines = []
    for beat in wb.get("discovery_arc", []):
        arc_lines.append(f"- **{beat['stage']}**: {beat['summary']}")

    log_lines = []
    for lg in preset.get("logs", []):
        log_lines.append(f"- **`Epoch {lg['epoch']} ({lg['gct']})`**: {lg['entry']}")

    md_content = "\n".join([
        f"# {preset['callsign']} • {preset['name']}",
        f"**{preset['subtitle']}** (`{preset['rf']['frequency_khz']} kHz {preset['rf']['mode']}` • `{preset['rf']['tx_power_label']}`)",
        "",
        "---",
        "",
        "## 1. Place & Habitat (`QTH`)",
        f"- **Celestial Body / Sector**: {preset['origin']['body']}",
        f"- **Transmitter Site**: {preset['origin']['site']} (`{preset['origin']['coordinates']}`)",
        f"- **Distance & Bearing from GOR-9**: {preset['origin']['distance']} (`Azimuth {preset['galactic']['azimuth_deg']}°`)",
        f"- **Local Environment & Culture**: {wb.get('habitat_and_culture', '')}",
        "",
        "## 2. Characters, Entities & Voice Casting (`characters/`)",
        *char_lines,
        "## 3. Spectrum Behavior & Technical Anomaly",
        f"- **Primary Gimmick**: **{wb.get('spectrum_gimmick_title', preset['category'])}**",
        f"- **Transmitter Hardware**: {preset['hardware_dossier']['transmitter']}",
        f"- **Signal Anomaly**: {preset['hardware_dossier']['feedline_anomaly']}",
        f"- **What Glenn Hauser / GOR-9 Says About Them**:",
        f"  > *\"{wb.get('hauser_commentary', preset['logs'][0]['entry'])}\"*",
        "",
        "## 4. Serialized Discovery Arc (Across Broadcasts)",
        *arc_lines,
        "",
        "## 5. Postcard QSL Card Design (`qsl/" + qsl_gif_path.name + "`)",
        f"- **QSL Serial**: `{preset['qsl']['qsl_number']}` ({preset['qsl']['collector_tier']})",
        f"- **Postcard Archetype**: {wb.get('qsl_postcard_style', preset['qsl']['dimensions'])}",
        f"- **Clunky GIF Animation**: {wb.get('qsl_animation_notes', preset['qsl']['embedded_clue'])}",
        f"- **Card Motto**: *\"{preset['qsl']['motto']}\"*",
        f"- **Signer**: {preset['qsl']['signer']}",
        "",
        "## 6. Flow 16:9 Scene, Character & Onboard POV Plates (`plates/`)",
        *flow_plate_lines,
        "",
        "## 7. Chronological GOR-9 DX Logs",
        *log_lines,
        "",
    ])
    (s_dir / "WORLDBUILDING.md").write_text(md_content, encoding="utf-8")


def build_stations_master_readme(presets: list[dict]) -> None:
    """Create `stations/README.md` indexing all station folders, characters, languages, visual plates, and voice WAVs."""
    rows = []
    char_rows = []
    for p in presets:
        slug = p["station_folder"]
        qsl_name = Path(p["qsl"]["gif_src"]).name
        rows.append(
            f"| `{p['preset_slot']}` | **[`{p['callsign']}`](./{slug}/WORLDBUILDING.md)** — {p['name']} | "
            f"`{p['rf']['frequency_khz']} kHz {p['rf']['mode']}` | {p['origin']['body']} | "
            f"{p.get('worldbuilding', {}).get('spectrum_gimmick_title', p['category'])} | "
            f"[`{qsl_name}`](./{slug}/qsl/{qsl_name}) |"
        )
        for c in p.get("characters", []):
            hs_link = f"[Headshot](./{slug}/characters/{Path(c['headshot_src']).name})" if c.get("headshot_src") else "—"
            fb_link = f"[Full-Body](./{slug}/characters/{Path(c['fullbody_src']).name})" if c.get("fullbody_src") else "—"
            dry_link = f"[Dry WAV](./{slug}/characters/{Path(c['voice_sample_dry_src']).name})" if c.get("voice_sample_dry_src") else "—"
            rf_link = f"[RF WAV](./{slug}/characters/{Path(c['voice_sample_rf_src']).name})" if c.get("voice_sample_rf_src") else "—"
            char_rows.append(
                f"| **{c['name']}** | `{p['callsign']}` ({p['name']}) | {c['role']} | "
                f"{c['languages']} | `{c['voice_profile']['tts_voice']}` | {hs_link} • {fb_link} | {dry_link} • {rf_link} |"
            )

    readme = "\n".join([
        "# GOR-9 Intercepted Stations, Worldbuilding & Character Registry",
        "",
        "Each station intercepted by **GOR-9 (Galactic Outpost Radio)** lives in its own self-contained folder under `stations/<station_slug>/` with:",
        "- `station.json` — Complete RF, decoder, character, and QSL metadata",
        "- `WORLDBUILDING.md` — Deep habitat lore, character bios, voice/language specs, and multi-episode discovery arcs",
        "- `characters/` — 16:9 Google Flow character reference sheets (Headshot + Full-Body Cyclorama) and 24 kHz Voice/Language samples (`*_dry.wav` + `*_rf.wav`)",
        "- `plates/` — Custom Frame A / Frame B postcard illustrations, scene backgrounds, and onboard POV camera plates",
        "- `qsl/` — Uniquely designed, clunky animated postcard QSL GIF (`384×240`, 10 frames) inspired by Glenn Hauser's QSL archive (`worldofradio.com/QSL.html`)",
        "- `audio/` — Signature Interval Signal WAV, Sub-Band SSTV Burst WAV, and Shortwave Intercept WAV",
        "",
        "---",
        "",
        "## 1. Station Directory",
        "",
        "| Slot | Callsign & Station Folder | Frequency & Mode | Location (`QTH`) | Spectrum Gimmick / Category | Postcard QSL GIF |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
        *rows,
        "",
        "---",
        "",
        "## 2. Character, Creature & Voice Casting Matrix",
        "",
        "| Character / Entity | Station | Role | Languages & Dialect | TTS Voice | Flow Reference Plates | Voice & Language WAVs |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        *char_rows,
        "",
    ])
    STATIONS_ROOT.mkdir(parents=True, exist_ok=True)
    (STATIONS_ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"Generated master station registry: {(STATIONS_ROOT / 'README.md').relative_to(ROOT)}")


def build_ghlogs_txt(data: dict) -> None:
    """Compile plain-text Glenn Hauser style DX logs from stations.json."""
    meta = data["station_meta"]
    lines = [
        "========================================================================",
        f" {meta['callsign']} • {meta['name'].upper()} — WEEKLY OORT CLOUD DX LOG ROUNDUP",
        f" Location : {meta['location']}",
        f" Carrier  : {meta['carrier_khz']} kHz {meta['carrier_mode']} • {meta['broadcast_time_gct']}",
        f" Clock    : {meta['clock_standard']}",
        f" Reactor  : {meta['power_plant']['primary']} ({meta['power_plant']['fuel']})",
        "========================================================================",
        "",
        "DX / SWL / DEEP-SPACE INTERCEPT LOGS (Alphabetical by Sector/Body):",
        "",
    ]
    for p in data["presets"]:
        for log in p.get("logs", []):
            lines.append(log["entry"])
            lines.append("")

    lines.extend([
        "------------------------------------------------------------------------",
        "PROPAGATION OUTLOOK (OORT SECTOR 9 / PROP-IV):",
        "Coreward Sol lanes quiet (Solar Flux 174 SFU, K-Index 2). Local Meridian",
        "Plateau experiencing 60 kV triboelectric silicate dust squall at KZ9-OMEGA.",
        "Grade-B Dilithium Pellet reserves at 91.4% ahead of 0000 GCT step-down.",
        "Standard disclaimer.",
        "========================================================================",
    ])
    out_txt = DOCS / "data" / "ghlogs_2736_305.txt"
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated raw DX log file: {out_txt.relative_to(ROOT)}")


def main() -> None:
    sync_generated_plates()
    raw_json = DATA_PATH.read_text(encoding="utf-8")
    data = json.loads(raw_json)
    js_path = DOCS / "data" / "stations_data.js"
    js_path.write_text(f"window.GOR9_STATIONS_DATA = {raw_json};\n", encoding="utf-8")
    print(f"Generated JS data bundle: {js_path.relative_to(ROOT)}")

    for preset in data["presets"]:
        qsl_path = build_qsl_gif(preset)
        audio_paths = make_interval_and_intercept(preset)
        if "station_folder" in preset:
            build_station_folder(preset, qsl_path, audio_paths)

    build_stations_master_readme(data["presets"])
    build_ghlogs_txt(data)


if __name__ == "__main__":
    main()
