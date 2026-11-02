# GOR-9 • Master Production Specification (`2560×1440` QHD)

**Galactic Outpost Radio (GOR-9)** — Broadcasting from the High Basalt Shelf on **Asteroid 3-5-1 in Sector 9** (`14,285.7 kHz USB` • `0400 UTC`).

Inspired by the 2024 GOR-9 broadcast (`https://www.youtube.com/watch?v=e9MbW45HB9Y`), Glenn Hauser's *World of Radio* shortwave DX logs, Art Bell's *Coast to Coast AM*, and a subtle nod to the *Retro Encabulator*.

---

## 1. Repository & Episode Asset Architecture

```text
/home/phi/PROJECTS/phiarchitect/GOR-9/
├── gor9_ep01.mp4                       # Latest finished 2560x1440 QHD master video (local root hardlink)
├── README.md                           # Station overview, Galactic Time standard, & episode index
├── PRODUCTION_BIBLE.md                 # Full world lore, hardware specs, & Flow/shader documentation
├── station/                            # Shared station-wide assets reused across all episodes
│   ├── branding/                       # @GOR-9-station avatar, YouTube 1440p banner, X header, SVG emblem
│   ├── rig/                            # CAM-00A cliff tower RGBA mattes, 4 apex rings, beacons, O.R.S. 351 & asteroid sprites
│   ├── plates/                         # Recurring station camera plates (CAM-00A..00D, DESK-01, CAM-SAT09)
│   ├── sfx/                            # Shortwave static, squelch bursts, harmonic chimes, sfx_catalog.json
│   └── consoles/                       # Interactive HTML broadcast console templates
├── scripts/                            # Episode synthesis, 1440p QHD shader renderer, YouTube packager & uploader
│   ├── synth_full_episode.py
│   ├── render_full_episode.py
│   ├── build_youtube_package.py
│   └── upload_youtube.py
└── episodes/                           # Self-contained episode folders (sequenced by Episode & Galactic Epoch)
    ├── ep00_2735.215_pilot/            # Episode 00 (July 2024 Pilot • Epoch 2735.215 • 0400 GCT)
    └── ep01_2736.305_parallelogram/    # Episode 01 ("The Unsuspecting Parallelogram" • Epoch 2736.305 • 0400 GCT)
        ├── gor9_ep01.mp4               # Finished 2560x1440 QHD master video right at the episode root
        ├── youtube/                    # One-stop YouTube upload folder (YOUTUBE_METADATA.md, youtube.json, .srt, .vtt, thumbnails)
        ├── script/                     # Broadcast script & ep01_timeline.json
        ├── audio/                      # Full 179.12s master WAV + segments/ (cached Argon III-C WAVs)
        ├── plates/                     # Episode-specific remote camera plates & Euclid I.34 SVG
        ├── clips/                      # 10s generated video+audio insert clips
        └── previews/                   # Rendered QHD preview frames for each console & panel
```

### 1A. Galactic Coordinated Time (`GCT` / Legacy `UTC`) & Polar Shelf Geometry
- **Why No Days or Nights on Asteroid 3-5-1**: Asteroid 3-5-1 (`38 km × 21 km × 16 km`, Pallas–Juno corridor) tumbles every `9h 25m 12s`, but the **High Basalt Shelf Tower Outpost** is anchored at **88.4° South Asteroidal Latitude** on the rim of **Acheron Polar Chasm**—aligned with the asteroid's **South Rotational Pole**. Consequently, the **Galactic Milky Way Core** hangs in permanent deep-space night above the cliff edge while the distant Sun skims perpetually `-1.6°` below the northern crater rim, and **`O.R.S. 351`** holds a stationary polar halo station-keeping position `42.8 km` off the shelf.
- **Physical Time Reference (`PSR B1937+21` — The Vulpecula Metronome)**: Because local asteroid rotation is useless as a civil clock, **Galactic Coordinated Time (`GCT`)** is locked to the barycentric pulse train of millisecond pulsar **`PSR B1937+21`** (`641.928262 Hz`, `1.557806 ms`), where **`1.000 Galactic Cycle`** = `55,462,600` pulsar ticks = `86,400.000` SI seconds (`0000`–`2400 GCT`), and **`1 Galactic Year`** = `365` cycles (`Epoch YYYY.DDD`).

### Canonical Plate Mapping (`assets/plates/`)

- **Segment 0 & 5 (`CAM-00` Exterior Station Camera Network — Simplified Single-Tower Outpost & Worldbuilding Angles)**:
  - `cam00_tower_outpost_base.jpg` (Primary `CAM-00A` High Basalt Shelf Broadcast Tower: solitary open-truss steel tower with elevated glass broadcast booth, warm glowing interior & lone operator silhouette, single rooftop parabolic dish, and 4 crimson aviation beacons)
  - `cam00_tower_beacons_off.jpg` (Pixel-locked companion plate with the 4 aviation warning beacons OFF for independent staggered blinking)
  - `cam00_tower_sky_key.jpg` (`#00FF00` chroma-key sky plate for zero-spill alpha matte extraction through the open steel lattice trusses)
  - `cam00b_canyon_overlook.jpg` (`CAM-00B • Acheron Canyon West Rim Overlook`: across-the-canyon wide view looking back at the solitary broadcast tower perched on the cliff rim against the aurora sky)
  - `cam00c_tower_downlook_barracks.jpg` (`CAM-00C • Tower Mast Down-Look`: high-angle surveillance camera mounted on the broadcast tower truss looking steeply down into the deep basalt canyon floor at the **North-24 Quonset Barracks / Dormitory Wing B** and condensation sump)
  - `cam00_aurora_sky_bg.jpg` (Rotating background plate: stars, emerald/violet aurora, teal ringed gas giant)
  - *(Legacy 4-dish array plates retained in `assets/plates/` for archival reference: `cam00_dishes_base.jpg`, `cam00_dishes_beacons_bright.jpg`, `cam00_dishes_sky_key.jpg`, `cam00_dishes_tilted_end.jpg`)*
- **Segment 1 (`CONSOLE 1 • METEO-9` Weather — Relay Station `KZ9-OMEGA` Dust Squall)**:
  - `cam02_relay_storm_start.jpg` ← `gor9_relay_station_storm_1793535224169.jpg`
  - `cam02_relay_storm_end.jpg` ← `gor9_relay_station_storm_end_1793539557937.jpg` (60kV cyan plasma arc leaping from feedhorn to mast)
- **Segment 2 (`CONSOLE 2 • ECON-9` Economics — Asteroid Silicate Quarry `44-K`)**:
  - `cam44k_quarry_start.jpg` ← `gor9_asteroid_slag_webcam_1793536036921.jpg`
  - `cam44k_quarry_end.jpg` ← `gor9_asteroid_slag_webcam_end_1793539574350.jpg` (Dragline bucket dropped into pit with dust plume)
- **Segment 3 (`CONSOLE 3 • HAUSER MK-IV` Detected Broadcasts)**:
  - `cam_n24_shallows_start.jpg` ← `gor9_methane_shallows_start.jpg` (Titan-Minor Buoy N-24 + 3 wading silt-striders)
  - `cam_n24_shallows_end.jpg` ← `gor9_methane_shallows_end.jpg` (Flow End-Keyframe: creatures walk left, lead creature dips head in water)
  - `cam_sw4_bazaar_start.jpg` ← `gor9_orbital_bazaar_cam.jpg` (Callisto Dome-4 Night Market `21:47:03 UTC`)
  - `cam_sw4_bazaar_end.jpg` ← `gor9_orbital_bazaar_end.jpg` (Flow End-Keyframe `21:47:08 UTC`: rising steam, engineer on roof with torch on dipole)
- **Segment 4 (`CONSOLE 4 • EUCLID-9` Signal Detector — "The Unsuspecting Parallelogram")**:
  - `cam_vat19_parallelogram.jpg` ← `gor9_unsuspecting_parallelogram_cam.jpg` (Flashlight inspection cam of `I.34` parallelogram in salt crust)
  - `cam04_crater_dish.jpg` ← `gor9_crater_anomaly_cam.jpg` (Backup lunar crater dish feed)
- **Segment 5 (`CONSOLE 5 • SCHED-9` & Studio Bunker Views)**:
  - `desk01_hauser_receiver.jpg` ← `gor9_listening_desk_hauser.jpg` (Operator desk inside elevated tower booth with green vector scope, logbook, and GALACTIC OUTPOST 9 mug)
  - `bunker_window_dishes.jpg` ← `gor9_bunker_window_dishes.jpg`

---

## 1B. Worldbuilding, Outpost Geography & Channel Branding (`Asteroid 3-5-1 • Sector 9`)

To maintain visual and narrative continuity across all **GOR-9** broadcasts, the physical layout of Outpost Nine on **Asteroid 3-5-1** (`Rotation Period: 4h 19m`) and its channel identity are defined as follows:

1. **Deep-Space Main-Belt Setting (No Nearby Planet — Drifting Asteroid Sprites)**:
   - **Asteroid 3-5-1** is an independent, irregular carbonaceous-basalt body in deep interplanetary space (`Sector 9`, Pallas–Juno corridor)—**not** orbiting any planet (otherwise it would be a moon).
   - Its night sky opens directly onto the unobstructed **Galactic Milky Way core** (`assets/plates/cam00_sky_plate_clean.jpg`), accompanied by smaller weathered main-belt rock fragments (**asteroid sprites** `assets/composited/asteroid_sprite_1..4.png` extracted from `assets/plates/asteroid_sprites_sheet_key.jpg`) drifting at subtle parallax velocities across the deep-space starfield.
2. **The High Basalt Shelf Cliff-Edge Tower (`CAM-00A` • Elevation `+85m` on the Sheer Precipice)**:
   - Inspired by the original 2024 GOR-9 opening still (`slides/01-intro/intro-01.webp`), the station is a **solitary open-lattice steel broadcast tower perched right at the sheer, precipitous edge of a towering columnar basalt cliff** plunging down into the dark Acheron Canyon chasm (`assets/plates/cam00_tower_outpost_base.jpg`).
   - **Elevated Octagonal Broadcast Booth (`DESK-01`)**: Cantilevered halfway up the steel trusswork is the glass-walled octagonal broadcast booth. Through the wide angled windows, warm `2700K` tungsten light reveals the **lone silhouette of the night-shift operator** seated at the console with a boom microphone. No other personnel are outside on the cliff shelf.
   - **Illuminated `GOR-9` Neon Call-Letter Sign (with Blinking `9`)**: Mounted atop the front roof edge of the elevated booth are bold vintage-industrial illuminated channel letters reading **`GOR-9`**. When the station warms up (`t = 1.15s`), **`GOR-`** strikes on in steady warm amber neon while the **`9`** digit flickers and blinks on its own slightly erratic relay cycle.
   - **Vertical Lattice Mast & 4 Concentric Apex Rings (No Parabolic Dish)**: Rising straight above the booth is a tapered 3-sided steel lattice vertical radio mast crowned at its apex by a horizontal spider-web emitter assembly of **4 nested concentric circular rings supported by radial spokes**. During standby (`assets/plates/cam00_tower_beacons_off.jpg`), the 4 concentric rings are dark unlit steel; right at the `[ding-ding]` signal lock (`t = 4.30s`), **Ring 1 → Ring 2 → Ring 3 → Ring 4 ignite sequentially from inner ring to outer ring** (`assets/composited/cam00_ring_1..4.png`) and pulse outward in traveling radial waves.
   - **Staggered Asynchronous Warning Beacons**: Three crimson aviation obstruction beacons (`mast_top` @ `2.30s`, `booth_left` @ `3.10s`, `booth_right` @ `2.75s`) blink on independent, non-overlapping schedules—never all at the same time.
3. **Wide Canyon Rim & Close-Up Booth Views (`CAM-00B`)**:
   - Wide canyon-rim perspective (`assets/plates/cam00b_canyon_rim_wide.jpg`) and tighter telephoto angle (`assets/plates/cam00b_closeup_tower.jpg`) showing the cliff-edge tower, glowing `GOR-9` neon rooftop sign, and concentric-ring mast against the Galactic Milky Way and drifting main-belt asteroid fragments.
4. **North-24 Canyon Floor Barracks & Condensation Sump (`CAM-00C` • Elevation `-240m` Gorge Floor)**:
   - A downward-angled surveillance camera mounted high on the broadcast tower girder looking steeply down into the sheltered bottom of the basalt canyon (`assets/plates/cam00c_tower_downlook_barracks.jpg`).
   - Three weathered corrugated Quonset domes (**Dormitory Wing A, Dormitory Wing B, and Mess/Hydroponics**) are linked by pressurized corrugated airlock tunnels beside a vertical atmospheric condensation sump tank venting faint white vapor. During `ECON-9`, when **Pebble-Bed Reactor #2** steps down from `50 kW` to `12 kW` after midnight, the console cuts live to `CAM-00C` as **Dormitory Wing B** is advised to plug in auxiliary foot-warmers.
5. **Remote Horizon Sign-Off Camera & Canonical Station Sign-Off (`CAM-00D` • `4.5 km` Across the Asteroid Horizon)**:
   - Inspired by the original 2024 closing slide (`slides/DALL·E 2024-07-26 08.52.10...webp`), `CAM-00D` looks across the dark curved horizon of Asteroid 3-5-1 toward the central silhouette of the vertical lattice radio tower (`assets/plates/cam00d_closing_horizon_rings.jpg`). Centered on the antenna spire tip is a brilliant **4-point star crosshair flare**, surrounded by **4 concentric cyan-white signal circles** and a **sweeping pale-gold outer horizon halo arch**.
   - **Mandatory Spoken & Visual Sign-Off on Every Broadcast**:
     > **`"From Asteroid 3-5-1 in Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum."`**
6. **Official Channel Distribution & Branding Suite (`https://www.youtube.com/@GOR-9-station`)**:
   - **Official YouTube Channel**: `https://www.youtube.com/@GOR-9-station` (Handle: `@GOR-9-station`).
   - **YouTube Advanced Features Enabled**: Full support for custom `2560×1440` thumbnails, external description links, pinned comments, chapter markers (`0:00`), `.srt`/`.vtt` closed captions, community posts, Shorts, and unrestricted daily broadcast uploads.
   - **Master Vector Emblem (`assets/branding/gor9_logo_mark.svg`)** & **800×800 Avatar (`renders/branding/gor9_avatar_800x800.png`)**: Built directly from the `CAM-00D` vertical tower + crosshair flare + 4 concentric signal rings + outer golden halo.
   - **YouTube Channel Banner (`renders/branding/gor9_youtube_banner_2560x1440.jpg`)**: `2560×1440` panorama with a `1546×423` centered TV/Desktop/Mobile safe zone featuring the tagline **`YOUR EYE TO THE COSMOS, EAR TO THE VACUUM.`**
   - **X Header Banner (`renders/branding/gor9_x_header_1500x500.jpg`)**: `1500×500` (3:1) header featuring the cliff-edge concentric-ring tower on the right and bold channel typography on the left.

---

## 2. Google Flow Tween Specifications (Start/End Keyframe Pairs & Prompts)

Each keyframe pair below was generated with pixel-locked camera registration via `ImagePaths`. When dropping these Start/End pairs into **Google Flow** (Veo 2 / Frame-to-Frame Interpolation, `16:9`, `5 seconds`), use the exact prompts below:

### Flow Tween 1 — Titan-Minor Buoy `N-24` & Wading Silt-Striders (Primary Flow Shot)
- **Start Frame**: `assets/plates/cam_n24_shallows_start.jpg`
- **End Frame**: `assets/plates/cam_n24_shallows_end.jpg`
- **Flow Prompt**:
  > `Fixed stationary trail-camera mounted on a coastal pier. Zero camera movement. Three tall, slender, long-legged alien wading creatures walk slowly and gracefully from right to left through calm, mirror-like shallow water in golden morning mist past the rusted N-24 buoy. Gentle concentric ripples spread around their legs in the reflective water as the lead creature smoothly lowers its long neck to sip from the surface. Low-key atmospheric wildlife surveillance footage.`
- **Why Flow**: Organic multi-legged creature locomotion + water surface ripples and reflections.

### Flow Tween 2 — Callisto Dome-4 Night Market ("Radio Corrugated")
- **Start Frame**: `assets/plates/cam_sw4_bazaar_start.jpg`
- **End Frame**: `assets/plates/cam_sw4_bazaar_end.jpg`
- **Flow Prompt**:
  > `Fixed high-angle CCTV surveillance camera inside an industrial spaceport dome market at night. Static camera mount. Thick white cooking steam billows upward from the street-level noodle stalls, pedestrians walk unhurriedly along the central metal grating walkway, lanterns sway slightly, and the radio technician standing on the corrugated metal roof in the center raises a bright glowing welding torch to solder the dipole antenna mast.`
- **Why Flow**: Rising volumetric steam, crowd movement, and rooftop torch spark.

### Flow Tween 3 — Asteroid Silicate Quarry `44-K` Dragline Excavator
- **Start Frame**: `assets/plates/cam44k_quarry_start.jpg`
- **End Frame**: `assets/plates/cam44k_quarry_end.jpg`
- **Flow Prompt**:
  > `Fixed wide-angle industrial security camera mounted behind a steel truss overlooking a night-shift open-pit asteroid mine. Static camera. The colossal crane boom slews slowly to the left and lowers the heavy cable-suspended dragline bucket into the central pit, kicking up a billowing cloud of amber floodlit silicate dust in low gravity while dump trucks crawl forward along the lower spiral terrace.`
- **Fallback Non-Flow Option**: Slow Ken Burns pan + 2-fps security-cam cross-step with a dust sprite overlay.

### Flow Tween 4 — Relay Station `KZ9-OMEGA` Electrostatic Dust Storm
- **Start Frame**: `assets/plates/cam02_relay_storm_start.jpg`
- **End Frame**: `assets/plates/cam02_relay_storm_end.jpg`
- **Flow Prompt**:
  > `Fixed remote weather camera view of two industrial parabolic satellite dishes and a guy-wired lattice radio tower on a rust plateau during a violent ochre dust storm. Thick orange dust clouds billow rapidly from left to right across the station base while crackling cyan St. Elmo's fire static builds on the antenna tips and a bright cyan high-voltage plasma arc leaps from the right dish feedhorn to the lattice mast.`
- **Fallback Non-Flow Option**: Rapid programmatic stutter-flash (`8–12 Hz` arc flicker between Start and End plates synced to horizontal RF static tear bars).

### Flow Tween 5 — High Basalt Shelf Dish Slew (Sign-Off Shot Only)
- **Start Frame**: `assets/plates/cam00_dishes_beacons_bright.jpg`
- **End Frame**: `assets/plates/cam00_dishes_tilted_end.jpg`
- **Flow Prompt**:
  > `Fixed wide-angle exterior camera on a dark basalt ridge. Static camera. All four giant white parabolic radio telescope dishes slowly and mechanically tilt upward in unison toward the zenith while red aviation warning beacons pulse on the tower tips and the small wheeled rover on the lower catwalk road drives slowly to the left.`

---

## 3. Console & Layered Animation Technical Specs (`2560×1440` @ 60fps)

All views render at **`2560×1440`** (`devicePixelRatio: 1`, `16:9`) inside a unified dark-mode broadcast architecture (`#080a0f` obsidian background, `1px solid #262d3d` structural bezels, `JetBrains Mono` telemetry typography).

### View 0 — `CAM-00` Opening Exterior Webcam (Programmatic Layered Composite — Zero Flow)
- **Assets**:
  - Background Sky: `cam00_aurora_sky_bg.jpg`
  - Foreground Dim: `cam00_dishes_base.jpg`
  - Foreground Bright Beacons: `cam00_dishes_beacons_bright.jpg`
  - Chroma Key Mask: `cam00_dishes_sky_key.jpg`
- **Compositing Pipeline (`scripts/build_cam00_mattes.py` + HTML5 `<canvas>` / `scripts/render_cam00_test.py`)**:
  1. **Zero-Spill Alpha Matte**: Compute per-pixel green excess from `cam00_dishes_sky_key.jpg`:
     $$\alpha(x,y) = 1.0 - \text{clamp}\left(\frac{G(x,y) - \max(R(x,y), B(x,y)) - 35}{95},\ 0.0,\ 1.0\right)$$
     Apply $\alpha(x,y)$ directly to the un-spilled RGB channels of `cam00_dishes_base.jpg` and `cam00_dishes_beacons_bright.jpg` → save `assets/composited/cam00_fg_dim.png` and `assets/composited/cam00_fg_bright.png`.
  2. **Asteroid 3-5-1 Rotation Motion (Background Layer)**:
     Scale `cam00_aurora_sky_bg.jpg` to `130%` (`3328×1872`) behind the foreground cutout. Translate continuously at `vx = -22 px/s`, `vy = +7 px/s` with a subtle orbital roll (`+0.25 deg/s`) so the aurora ribbons, starfield, and ringed gas giant drift smoothly behind the dishes and steel trusswork.
  3. **Beacon Strobe Pulse (Foreground Layer)**:
     Render `cam00_fg_dim.png` at `opacity: 1.0`, and overlay `cam00_fg_bright.png` modulated by $p(t) = \sin^4(\pi \cdot 0.85 t)$ so the crimson/amber tower beacons and rover strobe flash realistically.
  4. **Tuning-In Static & HUD Overlay**:
     - `t = 0.0s to 3.2s`: Heavy RF snow (`70%` decaying to `4%`), horizontal sync-jitter (`±18px`), and an animated tuning bar sweeping from `14,240.0 kHz` until locking onto **`14,285.7 kHz USB`** right on the `[ding-ding]` chime.
     - Lower-third HUD badge: `CAM-00 • HIGH BASALT SHELF • ASTEROID 3-5-1 • SECTOR 9 • ROTATION: 4h 19m`.

### Console 1 — `METEO-9` (Space Weather & Sector 9 Propagation)
- **Left Column (`42%` width) — Sector 9 Magnetospheric Polar Radar**:
  - Animated SVG polar radar (`360°` sweep every `4.0s`) with concentric range rings (`Coreward Lanes`, `Meridian Plateau`, `Perseus Spur`, `Asteroid 3-5-1`).
  - Pulsing red/amber hazard contour over `KZ9-OMEGA` (`60 kV TRIBOELECTRIC SQUALL`).
  - Telemetry readouts:
    - `COREWARD LANES: SOLAR FLUX 174 SFU • K-INDEX 2 [QUIET]`
    - `SECTOR 9 LOCAL: 60 kV DUST SQUALL • SINPO 2-3-2-2-2`
    - `HARDWARE TELEMETRY: MARZELVANE #4 PHASE-WOBBLE (+4.8°)`
- **Right Column (`58%` width) — Remote Feed `CAM-02 • RELAY KZ9-OMEGA (7,140 kHz)`**:
  - Alternates `cam02_relay_storm_start.jpg` and `cam02_relay_storm_end.jpg` with synchronized horizontal CRT tear bars whenever the cyan plasma arc strikes the tower.

### Console 2 — `ECON-9` (Outpost Economics, Power & Customs Ledger)
- **Left Column (`44%` width)**:
  - **Panel 2A — Ceres Spot Exchange Chart**: Animated SVG step-line graph plotting **Grade-B Deuterium Pellets (`+4.2%`)** spiking sharply at `03:00 UTC` with callout: `QUARRY 44-K CABLE SLOWDOWN`.
  - **Panel 2B — Outpost Power Rationing**: Bar gauge stepping **Pebble-Bed Reactor #2** down from `50 kW` to `12 kW USB`, with amber advisory pill: `DORMITORY WING B: PLUG IN AUXILIARY FOOT-WARMERS`.
  - **Panel 2C — Quarantine Buoy 12 Customs Hold (Day 11)**: Orbital holding-pattern vector loop for supply tender *MV Perseverance-4*, highlighting the manifest error: `TARIFF 409-B ERR: OSCILLATOR TUBES MISFILED AS "FERMENTED BRINE TUBERS"`.
- **Right Column (`56%` width) — Remote Feed `CAM-44K • SILICATE QUARRY 44-K`**:
  - Plays Quarry `44-K` dragline feed (`cam44k_quarry_start.jpg` → `cam44k_quarry_end.jpg`).

### Console 3 — `HAUSER MK-IV` (Detected Broadcasts: Galactic & Intergalactic)
- **Top Receiver Rack (`220px` height)**:
  - Full-width **Hauser Mk-IV Sliding Vernier Tuning Dial** (`3,000 kHz` to `1,500 MHz`) with warm amber backlighting, live canvas waterfall spectrogram, **Hauser Index (`H-8.4`)** readout, and red hairline cursor.
- **Main Signal Monitor (`1156px` height — 3 Sub-Views)**:
  - **Sub-View 3a (`3,890 kHz CW/Voice` — Titan-Minor Buoy `N-24`)**: `cam_n24_shallows_start.jpg` ↔ `cam_n24_shallows_end.jpg` + French methane tide table telemetry.
  - **Sub-View 3b (`11,410 kHz AM` — Callisto Dome-4 *"Radio Corrugated"*)**: `cam_sw4_bazaar_start.jpg` ↔ `cam_sw4_bazaar_end.jpg` + AM envelope meter spiking on rooftop dipole blowtorch.
  - **Sub-View 3c (`1,420.405 MHz, Δf -180 kHz` — Intergalactic M-33 Triangulum Spur)**: Green-phosphor circular vector oscilloscope tracing a drifting Doppler Lissajous figure while decoding packet text: `BUOY M33-771 (EPOCH -700 YRS): SMALL CRAFT ADVISORY — AMMONIA SEA SECTOR 4 [SEA STATUS: EVAPORATED 1580 CE]`.

### Console 4 — `EUCLID-9` (The Euclid Signal Detector — "The Unsuspecting Parallelogram")
- **Left Column (`48%` width) — `CAM-VAT19 • CALLISTO-SOUTH BRINE EVAPORATION VAT 19`**:
  - Displays `cam_vat19_parallelogram.jpg` with slow forensic push-in (`100% → 114%` scale) and animated cyan target reticles (`#38bdf8`) snapping onto corners `A`, `B`, `C`, `D` of the salt-crust figure.
- **Right Column (`52%` width) — Live `euclid_step` Vector Scope (`assets/euclid/0338.g1.svg` • `G.47` / `I.34`)**:
  - **Step 4a (The Sighting — `[bell:insight]`)**: Outer parallelogram walls `/ A B /`, `/ C D /`, `/ A C /`, `/ B D /` lock in **Steel Blue** (`#60a5fa`).
  - **Step 4b (The Diameter & Congruent Bisection — `[bell:construction]`)**: Diameter `/ B C /` ignites in **Solar Gold** (`#e8b85a`); triangles `< A B C >` and `< D C B >` glow **Assertion Green** (`#5ec27e`); single and double green equality ticks stamp onto opposite sides.
  - **Step 4c (The Cover-Up — `[bell:punchline]`)**: Blinking amber official notice banner: `CALLISTO WATER BOARD PRESS RELEASE: "MOTORIZED MUD-RAKE LOST A COTTER PIN AND DRAGGED SIDEWAYS."`

### Console 5 — `SCHED-9` ("On the Next Broadcast..." & Sign-Off → Return to `CAM-00`)
- **Sub-View 5a (`2:28–2:40`)**: Next Broadcast Teaser Card + Titan Packet Buoy QSL Card alongside `desk01_hauser_receiver.jpg`.
- **Sub-View 5b (`2:40–2:50`)**: Dissolves back to full-screen **`CAM-00` Exterior Station Webcam** (`cam00_dishes_tilted_end.jpg` masked over rotating `cam00_aurora_sky_bg.jpg`), plays closing `[ding-ding]` chime, and ramps RF snow to `100%`.

---

## 4. Master Broadcast Script (v2.0 — 308 Words • ~2:50 Runtime)

### 0. COLD OPEN (`0:00–0:18` • `CAM-00` Exterior Webcam)
*(3s of shortwave tuning static & heterodyne whistle -> locks onto carrier)*
**HOST:**
This is **GOR-9**. This is **GOR-9** `[ding-ding]` **Galactic Outpost Radio**, broadcasting from the High Basalt Shelf on **Asteroid 3-5-1** in **Sector 9**. Fourteen-two-eighty-five kilohertz upper sideband. Zero-four-hundred Galactic Coordinated.

### 1. WEATHER REPORT (`0:18–0:42` • `CONSOLE 1: METEO-9`)
`[bell:construction]`
**HOST:**
**Space Weather**, with emphasis on **Sector 9**.
Coreward lanes are calm—solar flux one-seventy-four, K-index two.
Locally, an electrostatic dust squall on the Meridian Plateau has engulfed Relay **KZ9-OMEGA**. Sixty-kilovolt triboelectric arcing across the feedhorn is causing minor phase-wobble in the number-four marzelvane bushing. Expect **SINPO two-three-two-two-two**.

### 2. ECONOMICS & SUPPLY (`0:42–1:10` • `CONSOLE 2: ECON-9`)
`[bell:proposition]`
**HOST:**
**Outpost Economics**.
Grade-B **Deuterium pellets** rose four percent today following a dragline cable slowdown at Silicate Quarry **44-K**. Outpost Nine will step Reactor Two down to twelve kilowatts after midnight; Dormitory B should plug in auxiliary foot-warmers.
Meanwhile, our monthly supply tender remains impounded at Quarantine Buoy Twelve after customs misfiled replacement oscillator tubes as *fermented brine tubers*.

### 3. DETECTED BROADCASTS (`1:10–1:48` • `CONSOLE 3: HAUSER MK-IV`)
`[bell:context]`
**HOST:**
On the **Hauser Correlator**:
**TITAN-MINOR**, three-eight-ninety kilohertz. Hydrographic Buoy **N-24** reciting methane tide tables...
*(3s clip: synthesized French numbers + metallic clank)*
...while migratory silt-striders rub against the guy-wires, detuning the whip antenna.

**CALLISTO DOME FOUR**, eleven-four-ten kilohertz. Unlicensed noodle-market broadcaster *Radio Corrugated*...
*(3s clip: warbling night-market lute + rapid port chatter)*
...peaking right as their engineer hit the dipole with a blowtorch.

And **INTERGALACTIC**, M-Thirty-Three: a seven-hundred-year-old drift-buoy still issuing small-craft warnings for an ammonia sea that evaporated in the Ming Dynasty.

### 4. THE EUCLID SIGNAL DETECTOR (`1:48–2:28` • `CONSOLE 4: EUCLID-9`)
`[bell:insight]`
**HOST:**
Finally... a late-night alert on the **Euclid Signal Detector**, which scans the noise floor for signs of geometric intelligence.
At zero-three-twelve UTC, inside unmanned **Brine Evaporation Vat Nineteen** on Callisto-South, the detector locked onto Frame Seven: an **unsuspecting parallelogram** in the salt crust.
`[bell:construction]`
Opposite sides parallel to two ten-thousandths of an arcsecond (`A-B` to `C-D`, `A-C` to `B-D`)—and somebody drew the diameter **B-C**, bisecting the sludge into two congruent triangles (`G.47`).
`[bell:punchline]`
The Water Board claims a motorized mud-rake lost a cotter pin and dragged sideways.
It’s always a broken cotter pin, folks.

### 5. "ON THE NEXT BROADCAST..." & SIGN-OFF (`2:28–2:50` • `CONSOLE 5: SCHED-9` → `CAM-00D`)
`[bell:context]`
**HOST:**
**On the next broadcast**: an unlicensed numbers station in the Trojans reciting dumpling recipes in base-eight, and a suspected **rhombus** aboard an ice-hauler.
From **Asteroid 3-5-1 in Sector 9**... this is **GOR-9**—**your eye to the cosmos, ear to the vacuum**.
*( `[ding-ding]` -> carrier fades into static)*
