# GOR-9 • Master Production Specification (`2560×1440` QHD)

**Galactic Outpost Radio (GOR-9)** — Broadcasting from the High Basalt Shelf on **Asteroid 3-5-1 in Sector 9** (`14,285.7 kHz USB` • `0400 UTC`).

Inspired by the 2024 GOR-9 broadcast (`https://www.youtube.com/watch?v=e9MbW45HB9Y`), Glenn Hauser's *World of Radio* shortwave DX logs, Art Bell's *Coast to Coast AM*, and a subtle nod to the *Retro Encabulator*.

---

## 1. Repository & Broadcast Asset Architecture

```text
/home/phi/PROJECTS/phiarchitect/GOR-9/
├── gor9_ep01.mp4                       # Latest finished 2560x1440 QHD master broadcast video (local root hardlink)
├── README.md                           # Station overview, Galactic Time standard, & broadcast index
├── PRODUCTION_BIBLE.md                 # Full world lore, hardware specs, & Flow/shader documentation
├── docs/                               # Interactive Companion Web Consoles (Hauser MK-IV, Van Allen VA-4, Bogey-9, Dossier)
├── station/                            # Shared station-wide assets reused across all broadcasts
│   ├── branding/                       # @GOR-9-station avatar, banners, Hauser Dynamics & Van Allen Switchgear logos
│   ├── rig/                            # CAM-00A cliff tower RGBA mattes, 4 apex rings, beacons, O.R.S. 351 & asteroid sprites
│   ├── plates/                         # Recurring station camera plates (CAM-00A..00D, ATC Tower Room, UAP Trail-Cams)
│   ├── sfx/                            # Shortwave static, squelch bursts, harmonic chimes, sfx_catalog.json
│   └── consoles/                       # Interactive HTML broadcast console templates
├── scripts/                            # Broadcast synthesis, 1440p QHD shader renderer, YouTube packager & uploader
│   ├── build_station_artifacts.py
│   ├── synth_full_episode.py
│   ├── render_full_episode.py
│   ├── build_youtube_package.py
│   └── upload_youtube.py
└── episodes/                           # Self-contained broadcast folders (sequenced by Broadcast & Galactic Epoch)
    ├── ep00_2735.215_pilot/            # Broadcast 00 (July 2024 Pilot • Epoch 2735.215 • 0400 GCT)
    └── ep01_2736.305_parallelogram/    # Broadcast 01 (Epoch 2736.305 • 0400 GCT)
        ├── gor9_ep01.mp4               # Finished 2560x1440 QHD master broadcast video right at the root
        ├── youtube/                    # One-stop YouTube upload folder (YOUTUBE_METADATA.md, youtube.json, .srt, .vtt, thumbnails)
        ├── script/                     # Broadcast script & ep01_timeline.json
        ├── audio/                      # Full 179.12s master WAV + segments/ (cached Argon III-C WAVs)
        ├── plates/                     # Broadcast-specific remote camera plates & Euclid I.34 SVG
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

## 3. ATC Control Tower Console Suite & Web Interfaces (`docs/` & `2560×1440` QHD)

Inside the **Octagonal ATC Control Tower Deck** (`docs/assets/plates/tower_atc_console_room.jpg`) perched at `42,100 AU` in **Oort Cloud Sector 9**, the entire broadcast program is built around four interconnected hardware consoles and web interfaces in `docs/`:

### View 0 — `CAM-00A` Exterior Cliff-Edge Tower → Octagonal ATC Tower Deck
- **Assets**:
  - Exterior Tower & 4 Concentric Apex Rings: `cam00_tower_outpost_base.jpg`, `cam00_ring_1..4.png`, `cam00_sky_plate_clean.jpg`.
  - Interior ATC Control Room: `docs/assets/plates/tower_atc_console_room.jpg`.
- **Sequence**:
  - `t = 0.0s to 4.3s`: Heavy RF snow clears right on the `[ding-ding]` chime as the 4 concentric Apex Rings ignite sequentially (`Ring 1 → Ring 4`) and the `GOR-9` rooftop neon sign strikes on.
  - Dissolves into the wrap-around **Octagonal ATC Control Tower Deck** showing the overhead Pulsar Clock (`PSR B1937+21 • 0400 GCT`) and the three primary operator consoles (`PROP-IV`, `HAUSER MK-IV`, and `BOGEY-9`).

### Console 1 — `VAN ALLEN VA-4` (Space Weather, Oort Propagation & Dilithium Power Bus)
- **Manufacturer & Broadcast Sponsor**: **Van Allen & Sons Switchgear** (`Est. 1958 Iowa City • Relocated 2412 to Ceres Foundry #7` • Motto: *"From Radiation Belts to Reactor Beds — If It Arcs, We Clamp It."*).
- **Nameplate & Emblem Assets**: `docs/assets/branding/van_allen_switchgear_logo.jpg` (riveted cast-brass & baked-enamel nameplate) and `docs/assets/branding/van_allen_logo.svg` (vector badge).
- **Interactive Console**: `docs/propagation.html` backed by `docs/data/propagation.json` (`docs/data/propagation_data.js`).
- **Left Rack — Oort Space-Weather Indices & 6-Corridor Propagation Matrix (`COR-01`..`COR-06`)**:
  - Live gauges for **Oort $K_p$**, **Comet `C/2736-K4` Ion Tail Density**, **Apex Ring Triboelectric Static (`+60 kV`)**, and **Heliopause $B_z$**.
  - Interactive azimuthal corridors (`Callisto Dome-4`, `Titan-Minor N-24`, `M33 Triangulum`, `Trojan L4`, `Ceres Pedregal`, `Relay KZ9-OMEGA`).
- **Center Monitor — 360° Magnetospheric Polar Radar & Oblique Ionogram**:
  - **360° Polar Radar (`#propPolarCanvas`)**: Displays the Heliopause Bow-Shock (`118.4 AU`), sweeping Cometary Ion Tail `C/2736-K4` plasma duct (`Az 212°`), and the red `60 kV` triboelectric dust squall over `KZ9-OMEGA` (`Az 349°`, `SINPO 2-3-2-2-2`).
  - **Oblique Ionogram & MUF/LUF Passband Curve (`#ionogramCanvas`)**: Plots the usable frequency window (`3.1–24.5 MHz` on the Jovian skip corridor; LUF raised `+4.2 MHz` during the dust squall).
- **Right Rack — 50 kW Pebble-Bed Dilithium Reactor #2 & Van Allen Switchgear Bus**:
  - Real-time load breakdown (`48.4 / 50.0 kW`), **Van Allen `"Pebble-Dropper"` Mk II Hopper**, **Van Allen `"Ring-Bake"` CD-400 Corona De-Icer (`+4.5 kW`)**, **Van Allen `"Belt-Master"` MV-6 Marzelvane Surge Clamp**, midnight step-down to `12 kW` (**Van Allen `"Cryo-Toast 900"`** foot-warmers in Dormitory Wing B), and the **Ceres Spot Exchange Ticker** (**Grade-B Dilithium Pellets `+4.2%`**).

### Console 2 — `HAUSER MK-IV` (Wideband DX Receiver, Galaxy Atlas, Code/Telemetry Decoder & Station `LOG`)
- **Manufacturer**: **Hauser Dynamics** (`Est. 2026 Enid • Ganymede Orbital Precision Works` • Motto: *"Every Carrier in the Noise — 3 kHz to 1.5 GHz."*).
- **Nameplate & Emblem Assets**: `docs/assets/branding/hauser_dynamics_logo.jpg` (satin-silver & anodized gunmetal optical reticle nameplate) and `docs/assets/branding/hauser_logo.svg` (vector badge).
- **Interactive Console**: `docs/index.html` & `docs/station.html` backed by `docs/data/stations.json` (`docs/data/stations_data.js`).
- **Top Rack**:
  - **Tactile Illuminated Preset Bank (`P-01`..`P-06`)**, **Barycentric VFO Synthesizer & Metallic Jog Wheel**, and **Live Waterfall Spectrogram + S-Meter (`S1–S9+40 dB`)**.
- **Left Viewport — Multi-Mode Signal Monitor**:
  - **Live Cam Feed Mode (`📺 LIVE CAM FEED`)**: Used when a station carries video (`P-02` Titan-Minor Buoy `N-24` on `3,890 kHz` with wading silt-striders; `P-01` Callisto Dome-4 *Radio Corrugated* on `11,410 kHz` with rooftop dipole blowtorch).
  - **No-Video Spectrum & Code/Telemetry Decoder Mode (`📈 3D SPECTRUM & PHASE SCAN` + `📟 CODE & TELEMETRY DECODER`)**: Automatically engages on audio/telemetry-only carriers (`P-03` Intergalactic `M-33` Drift Buoy on `1,420.405 MHz` and `P-04` Trojan L4 Octal Numbers Station `E08-L4` on `6,925 kHz`). Displays a live FFT + XY Lissajous phase scope, scrolling CW Morse ticker, 4-channel telemetry gauges, and interactive **Translation Algorithms (`ALG-01`..`ALG-04`)** that decode raw hex/octal streams into plaintext on screen.
- **Center Bay — Galactic Signal Vector Atlas**:
  - Logarithmic polar radar centered on **GOR-9 (`Oort Sector 9 • 42,100 AU`)** plotting the exact azimuthal bearing and distance (`AU` / `ly` / `Mly`) to each station.
- **Right Bay — Digital Burst eQSL Collector Card & Multi-Entry `LOG`**:
  - Displays the station's animated 4-frame low-res `.gif` **eQSL signature card** (`QSL #0882-N24`, `QSL #0165-RC`, `QSL #0004-M33`, `QSL #0311-T8`) and the chronological **`LOG`** (3 historical operator log entries per station + live quick-add).

### Console 3 — `BOGEY-9` (Perimeter Asteroid Trail-Cam & Non-Keplerian UAP Discriminator)
- **Interactive Console**: `docs/bogey-detector.html` backed by `docs/data/bogeys.json` (`docs/data/bogeys_data.js`).
- **Left Rack — Motion Gate Triggers & 360° Perimeter Keplerian vs. Bogey Radar**:
  - Plots 14 green ballistic Keplerian rocks against **3 crimson non-Keplerian UAP bogeys** (`UAP-2736-A`, `UAP-2736-B`, `UAP-2736-C`) with zero Euclidean references—pure kinematic trajectory discrimination.
- **Center Monitor — 8-Frame Trail-Cam Burst `.GIF` & Forensic Frame Stepper (`FRM 01`..`FRM 08`)**:
  - **Broadcast 01 Featured Sighting (`TRL-01 • Acheron North Rim`)**: Starlight CMOS 8-frame burst (`docs/assets/uap/bogey_01_cylinder.gif`) of an 18-meter mirror-chrome cylinder drifting between two tumbling boulders at `14.2 m/s` before executing an instantaneous `90.00°` vertical snap-turn (`140g`) on `FRM 05` with zero thruster plume—blamed by the Outer Belt Safety Board on a vented Mess Hall thermos flask.

### Console 4 — `VAN ALLEN ED-9` (Euclidean Detector & Cosmic Geometric Intelligence Correlator)
- **Manufacturer**: **Van Allen & Sons Switchgear • SETI & Constructive Geometry Division (`Ceres Foundry #7`)** — *"Because Vacuum Makes Fractals, Not Parallelograms."*
- **Interactive Console**: `docs/euclidean-detector.html` backed by `docs/data/euclidean.json` (`docs/data/euclidean_data.js`).
- **Left Rack — 12-Tube Hough Transform Noise-Floor Accumulator & Candidate Queue**:
  - Live `(\rho, \theta)` Hough Transform scope (`#houghCanvas`) separating thermal noise and fractal crater walls from synthetic straight chords, parallel lines, and constructive ratios.
  - **Broadcast 01 Featured Detection (Single Euclid Lock in Video)**: **`EUC-2736-01` — Callisto-South Brine Evaporation Vat 19 (Frame 7): *"The Unsuspecting Parallelogram"* (`Euclid I.34 / G.47`)** (`99.998%` synthetic certainty). *(Two secondary detections—`EUC-2736-02` Ice-Hauler Rhombus `Def. I.22` and `EUC-2736-03` Crater Dish `III.31`—are queued in the web console for future broadcasts).*
- **Center Monitor — Dual Optical Surveillance + Constructive Euclidean Vector Scope**:
  - Overlays the live constructive proof of **Euclid Book I, Proposition 34 (`G.47`)** onto `docs/assets/plates/cam_vat19_parallelogram.jpg`: opposite sides `AB || CD` and `AC || BD` holding parallel to `0.0002 arcsec`, and diameter `BC` bisecting the salt sludge into two congruent triangles (`△ABC ≅ △DCB`), accompanied by a 4-Step Proof & Cover-Up Stepper and the Callisto Water Board's broken mud-rake cotter pin excuse.

### Console 5 — Companion Station Dossier, 3D Collector Cards & Horizon Sign-Off (`CAM-00D`)
- **Interactive Web Dossier**: `docs/station.html` featuring 3D-flip **eQSL Collector Cards** (`Front Artwork` ↔ `Back Transmitter Dossier`), the **Outpost Nine Hardware Manufacturers & Broadcast Underwriters (`Hauser Dynamics` & `Van Allen & Sons Switchgear`)** showcase, and full multi-entry `LOG` tables, dissolving out to `CAM-00D` (`cam00d_closing_horizon_rings.jpg`) for the mandatory station sign-off.

---

## 4. Master Broadcast Script (v3.2 — 4-Console Edition with Van Allen ED-9 Euclidean Detector)

Canonical file: `episodes/ep01_2736.305_parallelogram/script/gor9_ep01_script.txt`

### 0. COLD OPEN (`CAM-00A` Exterior Tower → `ATC TOWER DECK`)
`[bell:context]`
**HOST:**
This is **GOR-9**. `<pause>` This is **GOR-9**, `<pause>` **Galactic Outpost Radio**, broadcasting from the High Basalt Shelf Tower on **Asteroid 3-5-1**, `<pause>` forty-two thousand one hundred astronomical units out in **Oort Cloud Sector 9**. `<pause>` Fourteen-two-eighty-five kilohertz upper sideband. Zero-four-hundred Galactic Coordinated.

### 1. SPACE WEATHER, OORT PROPAGATION & DILITHIUM POWER (`CONSOLE 1: VAN ALLEN VA-4`)
`[bell:construction]`
**HOST:**
On the **Van Allen V-A-Four Propagation and Power Console**—brought to you by **Van Allen and Sons Switchgear** of Ceres Foundry Seven: `<pause>`
Comet **K-Four**'s ion tail is sweeping azimuth two-twelve, opening a clean twenty-four megahertz skip corridor into the Jovian moons. `<pause>`
Closer to home, a sixty-kilovolt triboelectric dust squall has engulfed Relay **K-Z-9 Omega**—raising our lower usable frequency by four megahertz and arcing across the number-four **Belt-Master marzelvane bushing**. `<pause>` Expect **SINPO two-three-two-two-two**.

`[bell:proposition]`
**HOST:**
On the **Dilithium Bus**: `<pause>`
Grade-B **Dilithium pellets** rose four percent on the Ceres Exchange following a dragline cable slowdown at Silicate Quarry **44-K**. `<pause>` With our **Van Allen Ring-Bake corona de-icer** pulling an extra four-point-five kilowatts, we are stepping **Reactor Two** down to twelve kilowatts after midnight—Dormitory Wing B should plug in their **Van Allen Cryo-Toast foot-warmers**. `<pause>`
Meanwhile, our monthly pellet and vacuum-tube tender remains impounded at Quarantine Buoy Twelve after customs misfiled replacement oscillator tubes as *fermented brine tubers*.

### 2. GALACTIC DX INTERCEPTS, DECODER ALGORITHMS & STATION LOG (`CONSOLE 2: HAUSER MK-IV`)
`[bell:context]`
**HOST:**
Turning to the **Hauser Dynamics Mark-Four Receiver** and **Galaxy Atlas**: `<pause>`
**Preset Two**—Titan-Minor, three-eight-ninety kilohertz. Hydrographic Buoy **N-24** is transmitting methane tide telemetry, `<pause>` `<pause>` though migratory silt-striders rubbing against the guy-wires just detuned the whip antenna by eighteen Hertz. **E-QSL zero-eight-eight-two** logged. `<pause>`

**Preset One**—Callisto Dome Four, eleven-four-ten kilohertz. Unlicensed noodle-market broadcaster *Radio Corrugated*, `<pause>` `<pause>` peaking at S-nine plus ten right as their engineer hit the rooftop dipole with a blowtorch. `<pause>`

**Preset Three**—extragalactic, fourteen-twenty megahertz on the hydrogen line, two-point-seven million light-years toward **M-Thirty-Three**. `<pause>` No video carrier on this band—just a relativistic Doppler Lissajous on the spectrum scan. Running **Translation Algorithm Zero-Two** against the raw hex stream decodes Buoy **M-33-771**: `<pause>` still issuing small-craft advisories for an ammonia sea that evaporated during the Ming Dynasty. `<pause>`

And on **Preset Four**, six-nine-two-five kilohertz in the Jupiter Trojans: an encrypted base-eight numbers station where **Algorithm Zero-Three** just decoded six metric tons of pork-chive dumpling wrappers—plus an octal shift key of thirteen for those tracking the sector cipher in the station log.

### 3. PERIMETER ASTEROID TRAIL-CAM (`CONSOLE 3: BOGEY-9`)
`[bell:insight]`
**HOST:**
Quick check on the **Bogey-Nine Perimeter Trail-Cam**, which discriminates ballistic Oort rocks from non-Keplerian visitors right outside our cliff rim. `<pause>`
At zero-three-forty-one Galactic, **Trail-Cam One** on the Acheron North Rim triggered an eight-frame burst on a mirror-chrome cylinder drifting between two tumbling boulders at fourteen meters per second—before executing a ninety-degree vertical snap-turn on Frame Five at one-hundred-forty G's with zero thruster plume. `<pause>` The Outer Belt Safety Board says it was a vented thermos flask from the Mess Hall.

### 4. COSMIC GEOMETRIC INTELLIGENCE CORRELATOR (`CONSOLE 4: VAN ALLEN ED-9 EUCLIDEAN DETECTOR`)
`[bell:construction]`
**HOST:**
Now to our centerpiece instrument: `<pause>` the **Van Allen E-D-Nine Euclidean Detector**—searching for geometric intelligence across the universe. `<pause>` Natural vacuum produces fractals and thermal static; intelligence leaves straight lines, parallel chords, and constructive ratios. `<pause>`
Tonight, our twelve-tube Hough Transform correlator locked onto a single ninety-nine-point-nine-nine-eight percent synthetic signature in the maintenance feed from **Callisto-South Brine Evaporation Vat Nineteen**: `<pause>` what we are calling **the Unsuspecting Parallelogram**.

`[bell:proposition]`
**HOST:**
Under inspection-beam sweep Frame Seven, four salt-crust ridges form parallelogram **A-B-D-C**—satisfying **Euclid Book One, Proposition Thirty-Four**: `<pause>` opposite sides **A-B** and **C-D**, and **A-C** and **B-D**, hold parallel to two ten-thousandths of an arcsecond, while diagonal diameter **B-C** bisects the brine sludge into two congruent triangles of equal area.

`[bell:punchline]`
**HOST:**
Seven minutes after our Van Allen detector logged the Proposition Thirty-Four proof, the Callisto Water Board scrubbed the archive and blamed a motorized mud-rake that lost a cotter pin. `<pause>`
That is one remarkably well-educated mud-rake, folks.

### 5. COMPANION LEDGER, UNDERWRITER TAG & SIGN-OFF (`STATION DOSSIER` → `CAM-00D`)
`[bell:context]`
**HOST:**
All six **e-QSL collector cards**, raw telemetry streams, and our **Euclidean Detector plates** are posted on the Outpost Nine companion ledger—and we are holding a suspected rhombus aboard a bulk ice-hauler in the queue for a future broadcast. `<pause>`
This broadcast is underwritten by **Van Allen and Sons Switchgear**—*from radiation belts to reactor beds, if it arcs, we clamp it.* `<pause>`
From **Asteroid 3-5-1 in Oort Cloud Sector 9**, `<pause>` this is **GOR-9**—**your eye to the cosmos, ear to the vacuum**.

`[bell:insight]`
**HOST:**
Remember, a like indication on your listening apparatus gives us three kilowatts of Dilithium reserve, `<pause>` and a subscription gets us one step closer to shielding our marzelvane emitters.

