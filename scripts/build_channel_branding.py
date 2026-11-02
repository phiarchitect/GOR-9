#!/usr/bin/env python3
"""Generate the GOR-9 Channel Branding Suite for YouTube and X.

Outputs in assets/branding/ and renders/branding/:
  1. assets/branding/gor9_logo_mark.svg         (Scalable vector emblem)
  2. renders/branding/gor9_avatar_800x800.png   (YouTube / X profile avatar)
  3. renders/branding/gor9_youtube_banner_2560x1440.jpg (YouTube banner with 1546x423 safe zone)
  4. renders/branding/gor9_x_header_1500x500.jpg        (X / Twitter 3:1 header banner)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PLATES_DIR = ROOT / "assets" / "plates"
BRAND_ASSETS = ROOT / "assets" / "branding"
BRAND_RENDERS = ROOT / "renders" / "branding"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def get_font(size: int, sans: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_SANS if sans else FONT_BOLD
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    <radialGradient id="bgGlow" cx="50%" cy="38%" r="52%">
      <stop offset="0%" stop-color="#183848" stop-opacity="0.95"/>
      <stop offset="55%" stop-color="#091520" stop-opacity="0.98"/>
      <stop offset="100%" stop-color="#04070B" stop-opacity="1"/>
    </radialGradient>
    <radialGradient id="apexFlare" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="1"/>
      <stop offset="35%" stop-color="#FFF0B8" stop-opacity="0.85"/>
      <stop offset="70%" stop-color="#6CE6FF" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#6CE6FF" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Deep Space Background -->
  <rect width="800" height="800" fill="url(#bgGlow)"/>

  <!-- Outer Cosmic Halo Arch -->
  <circle cx="400" cy="400" r="336" fill="none" stroke="#F4DF9E" stroke-width="7" stroke-opacity="0.88" filter="url(#glow)"/>
  <circle cx="400" cy="400" r="276" fill="none" stroke="#F4DF9E" stroke-width="2.5" stroke-opacity="0.42"/>
  <circle cx="400" cy="400" r="222" fill="none" stroke="#F4DF9E" stroke-width="2" stroke-opacity="0.30"/>

  <!-- 4 Concentric Signal Rings around Antenna Apex (cx=400, cy=255) -->
  <g filter="url(#glow)">
    <circle cx="400" cy="255" r="142" fill="none" stroke="#8CEEFF" stroke-width="4.5" stroke-opacity="0.92"/>
    <circle cx="400" cy="255" r="110" fill="none" stroke="#9CF4FF" stroke-width="4.5" stroke-opacity="0.95"/>
    <circle cx="400" cy="255" r="78"  fill="none" stroke="#B8F8FF" stroke-width="4.5" stroke-opacity="0.98"/>
    <circle cx="400" cy="255" r="46"  fill="none" stroke="#FFF4C8" stroke-width="5"   stroke-opacity="1.0"/>
  </g>

  <!-- 4-Point Crosshair Signal Lock Star Flare -->
  <circle cx="400" cy="255" r="42" fill="url(#apexFlare)"/>
  <polygon points="400,72 407,246 588,255 407,264 400,410 393,264 212,255 393,246" fill="#FFF7D6" filter="url(#glow)"/>

  <!-- Tapered Open-Lattice Radio Tower + Elevated Octagonal Booth -->
  <g stroke="#081018" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <!-- Upper Vertical Mast -->
    <line x1="400" y1="245" x2="400" y2="430" stroke-width="9"/>
    <line x1="382" y1="430" x2="400" y2="275"/>
    <line x1="418" y1="430" x2="400" y2="275"/>
    <line x1="387" y1="380" x2="413" y2="380" stroke-width="5"/>
    <line x1="391" y1="335" x2="409" y2="335" stroke-width="5"/>

    <!-- Lower Lattice Legs below Booth -->
    <line x1="366" y1="496" x2="328" y2="642" stroke-width="11"/>
    <line x1="434" y1="496" x2="472" y2="642" stroke-width="11"/>
    <line x1="400" y1="496" x2="400" y2="642" stroke-width="7"/>
    <!-- Cross Bracing -->
    <line x1="356" y1="532" x2="444" y2="532" stroke-width="6"/>
    <line x1="344" y1="582" x2="456" y2="582" stroke-width="6"/>
    <line x1="366" y1="496" x2="444" y2="532" stroke-width="5"/>
    <line x1="434" y1="496" x2="356" y2="532" stroke-width="5"/>
    <line x1="356" y1="532" x2="456" y2="582" stroke-width="5"/>
    <line x1="444" y1="532" x2="344" y2="582" stroke-width="5"/>
    <line x1="344" y1="582" x2="472" y2="642" stroke-width="6"/>
    <line x1="456" y1="582" x2="328" y2="642" stroke-width="6"/>
  </g>

  <!-- Cantilevered Octagonal Broadcast Booth -->
  <polygon points="332,448 468,448 452,498 348,498" fill="#0B131C" stroke="#1E3346" stroke-width="4"/>
  <!-- Warm Glowing Booth Window -->
  <polygon points="356,458 444,458 436,486 364,486" fill="#FFB347"/>
  <!-- Lone Operator Silhouette -->
  <circle cx="408" cy="469" r="6" fill="#120D08"/>
  <path d="M398,486 C398,476 418,476 418,486 Z" fill="#120D08"/>
  <!-- Neon GOR-9 Rooftop Sign -->
  <text x="400" y="440" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="26" fill="#FFB84D" filter="url(#glow)">GOR-9</text>

  <!-- Curved Asteroid 3-5-1 Horizon -->
  <path d="M90,695 Q400,590 710,695 L710,800 L90,800 Z" fill="#04070B"/>
  <path d="M90,695 Q400,590 710,695" fill="none" stroke="#5CA4B8" stroke-width="4" stroke-opacity="0.75"/>

  <!-- Main Callsign Emblem Text -->
  <text x="400" y="736" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-weight="900" font-size="76" letter-spacing="4" fill="#FFF3C4">GOR-9</text>
</svg>
"""


def main() -> None:
    BRAND_ASSETS.mkdir(parents=True, exist_ok=True)
    BRAND_RENDERS.mkdir(parents=True, exist_ok=True)

    # 1. Write scalable SVG logo mark
    svg_path = BRAND_ASSETS / "gor9_logo_mark.svg"
    svg_path.write_text(SVG_LOGO, encoding="utf-8")
    print(f"Saved {svg_path}")

    # 2. Build 800x800 Avatar from gor9_channel_logo_emblem.jpg
    emblem = Image.open(PLATES_DIR / "gor9_channel_logo_emblem.jpg").convert("RGB")
    avatar = emblem.resize((800, 800), Image.Resampling.LANCZOS)
    avatar_path = BRAND_RENDERS / "gor9_avatar_800x800.png"
    avatar.save(avatar_path, optimize=True)
    print(f"Saved {avatar_path}")

    # 3. Build YouTube Channel Banner (2560x1440 with 1546x423 safe zone: x=507..2053, y=508..931)
    closing_bg = Image.open(PLATES_DIR / "cam00d_closing_horizon_rings.jpg").convert("RGB").resize(
        (2560, 1440), Image.Resampling.LANCZOS
    )
    yt_banner = closing_bg.copy().convert("RGBA")

    # Darken center safe band slightly so channel typography pops on all devices
    band_overlay = Image.new("RGBA", (2560, 1440), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(band_overlay)
    # Soft dark glass panel inside safe area on the left/right of central tower
    bdraw.rounded_rectangle(
        (530, 540, 2030, 900),
        radius=18,
        fill=(5, 9, 16, 178),
        outline=(110, 228, 255, 190),
        width=3,
    )
    # Inner gold trim line
    bdraw.rounded_rectangle(
        (542, 552, 2018, 888),
        radius=12,
        fill=None,
        outline=(244, 212, 138, 120),
        width=2,
    )
    yt_banner = Image.alpha_composite(yt_banner, band_overlay)

    # Place circular emblem badge on the left of the safe zone
    badge_size = 280
    badge = emblem.resize((badge_size, badge_size), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", (badge_size, badge_size), 0)
    ImageDraw.Draw(mask).ellipse((4, 4, badge_size - 4, badge_size - 4), fill=255)
    yt_banner.paste(badge, (575, 580), mask)

    ydraw = ImageDraw.Draw(yt_banner)
    ydraw.ellipse((575, 580, 575 + badge_size, 580 + badge_size), outline=(244, 212, 138, 230), width=4)

    # Typography inside safe zone (x=890..1990, y=565..875)
    f_call = get_font(86, sans=True)
    f_sub = get_font(34, sans=False)
    f_freq = get_font(28, sans=False)
    f_tag = get_font(26, sans=False)

    # ON AIR pill
    ydraw.rounded_rectangle((895, 582, 1085, 628), radius=6, fill=(52, 12, 18, 240), outline=(255, 75, 85, 255), width=2)
    ydraw.ellipse((912, 595, 932, 615), fill=(255, 64, 76, 255))
    ydraw.text((944, 590), "ON AIR", font=get_font(24), fill=(255, 230, 230, 255))
    ydraw.text((1110, 590), "14,285.7 kHz USB • ASTEROID 3-5-1 • SECTOR 9", font=f_freq, fill=(132, 228, 255, 255))

    # Main Title
    ydraw.text((895, 636), "GOR-9", font=f_call, fill=(255, 243, 196, 255))
    ydraw.text((1245, 662), "• GALACTIC OUTPOST RADIO", font=get_font(44, sans=True), fill=(242, 246, 252, 255))

    # Divider
    ydraw.line((895, 748, 1980, 748), fill=(110, 228, 255, 130), width=2)

    # Tagline from original closing slide
    ydraw.text((895, 768), "YOUR EYE TO THE COSMOS, EAR TO THE VACUUM.", font=f_sub, fill=(245, 194, 92, 255))
    ydraw.text((895, 822), "SPACE WEATHER • OUTPOST ECONOMICS • WIDEBAND DX • EUCLID SIGNAL DETECTOR", font=f_tag, fill=(180, 206, 224, 255))

    yt_path = BRAND_RENDERS / "gor9_youtube_banner_2560x1440.jpg"
    yt_banner.convert("RGB").save(yt_path, quality=92, optimize=True)
    print(f"Saved {yt_path}")

    # 4. Build X (Twitter) Header Banner (1500x500) using Cliff-Edge Concentric-Ring Tower
    cliff_img = Image.open(PLATES_DIR / "cam00_tower_outpost_base.jpg").convert("RGB")
    # Scale to 1680x945 and crop 1500x500 with tower shifted slightly right of center (no seams!)
    cliff_scaled = cliff_img.resize((1680, 945), Image.Resampling.LANCZOS)
    x_banner = cliff_scaled.crop((0, 42, 1500, 542)).convert("RGBA")

    # Smooth dark gradient on left 48% for crisp typography
    grad = Image.new("RGBA", (1500, 500), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for x in range(740):
        alpha = int(210 * max(0.0, 1.0 - (x / 740.0) ** 1.6))
        gdraw.line([(x, 0), (x, 500)], fill=(5, 8, 14, alpha))
    x_banner = Image.alpha_composite(x_banner, grad)

    xdraw = ImageDraw.Draw(x_banner)
    # Border frame
    xdraw.rectangle((6, 6, 1493, 493), outline=(244, 200, 108, 170), width=2)

    # Top-left callsign block (keeping bottom-left y > 320 clear for X circular profile avatar)
    xdraw.rounded_rectangle((48, 42, 212, 82), radius=5, fill=(52, 12, 18, 240), outline=(255, 75, 85, 255), width=2)
    xdraw.ellipse((64, 53, 82, 71), fill=(255, 64, 76, 255))
    xdraw.text((92, 49), "ON AIR", font=get_font(21), fill=(255, 230, 230, 255))
    xdraw.text((230, 50), "14,285.7 kHz USB • ASTEROID 3-5-1", font=get_font(22), fill=(132, 228, 255, 255))

    xdraw.text((48, 96), "GOR-9", font=get_font(78, sans=True), fill=(255, 243, 196, 255))
    xdraw.text((48, 184), "GALACTIC OUTPOST RADIO", font=get_font(34, sans=True), fill=(242, 246, 252, 255))
    xdraw.text((48, 236), "YOUR EYE TO THE COSMOS, EAR TO THE VACUUM.", font=get_font(22), fill=(245, 194, 92, 255))
    xdraw.text((48, 274), "STAY TUNED. STAY CURIOUS.", font=get_font(20), fill=(176, 204, 224, 255))

    x_path = BRAND_RENDERS / "gor9_x_header_1500x500.jpg"
    x_banner.convert("RGB").save(x_path, quality=92, optimize=True)
    print(f"Saved {x_path}")


if __name__ == "__main__":
    main()
