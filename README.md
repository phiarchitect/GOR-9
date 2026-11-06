# GOR-9 • Galactic Outpost Radio (`14,285.7 kHz USB`)

**From Asteroid 3-5-1 in Oort Cloud Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum.**

- **Official YouTube Channel**: [`youtube.com/@GOR-9-station`](https://www.youtube.com/@GOR-9-station)
- **Transmitter Location**: High Basalt Shelf ATC Control Tower (South Rotational Pole, `88.4° S`), Asteroid 3-5-1, Oort Cloud Sector 9 (`42,100 AU` / `0.66 ly` from Sol)
- **Carrier**: `14,285.7 kHz` Upper Sideband (`50 kW` Peak / `12 kW` Night-Shift Step-Down via Pebble-Bed Dilithium Reactor #2)
- **Primary Tower Consoles**:
  - **Hauser MK-IV Wideband Barycentric DX Correlator** (*Hauser Dynamics • Ganymede Orbital Precision Works*)
  - **Van Allen VA-4 Heliopause Sounder & 50 kW Dilithium Bus Console** (*Van Allen & Sons Switchgear • Ceres Foundry #7*)
  - **Bogey-9 Perimeter Asteroid Trail-Cam & Non-Keplerian UAP Discriminator**
  - **Van Allen ED-9 Euclidean Detector & Cosmic Geometric Intelligence Correlator** (*Van Allen & Sons Switchgear • SETI Division*)
- **Orbital Relay**: Synchronous Polar Halo Satellite **`O.R.S. 351`** (`Alt: 42.8 km`)
- **Time Standard**: **Galactic Coordinated Time (`GCT` / legacy dial `UTC`)** — Barycentric millisecond pulsar standard locked to **`PSR B1937+21`** (`641.928262 Hz`, the *"Vulpecula Metronome"*).

---

## 1. Repository & Broadcast Organization

All broadcast productions are self-contained inside `episodes/<broadcast_id>/`, while the interactive companion web consoles live in `docs/` and recurring station-wide hardware rigs, camera plates, sound effects, and channel branding live in `station/`:

```text
GOR-9/
├── gor9_ep01.mp4                       # Latest finished 2560x1440 QHD master broadcast video (local root hardlink)
├── README.md                           # Station overview, Galactic Time standard, & broadcast index
├── PRODUCTION_BIBLE.md                 # Full world lore, hardware specs, & shader/console documentation
├── docs/                               # Interactive Companion Web Consoles & Station Ledger
│   ├── index.html                      # Hauser MK-IV Wideband DX Receiver, Decoder & Galaxy Signal Atlas
│   ├── propagation.html                # Van Allen VA-4 Space Weather, Oort Propagation & Dilithium Bus Console
│   ├── bogey-detector.html             # Bogey-9 Perimeter Asteroid Trail-Cam & UAP Kinematic Correlator
│   ├── euclidean-detector.html         # Van Allen ED-9 Cosmic Geometric Intelligence Correlator
│   ├── station.html                    # Companion DX Ledger, 3D-Flip eQSL Collector Cards & Manufacturer Lore
│   └── data/                           # Canonical JSON & JS schemas (stations, propagation, bogeys, euclidean, logs)
├── station/                            # Shared station-wide assets reused across all broadcasts
│   ├── branding/                       # @GOR-9-station avatar, banners, Hauser Dynamics & Van Allen Switchgear logos
│   ├── rig/                            # CAM-00A cliff tower RGBA mattes, 4 apex rings, beacons, O.R.S. 351 & asteroid sprites
│   ├── plates/                         # Recurring station camera plates (CAM-00A..00D, ATC Tower Room, UAP Trail-Cams)
│   ├── sfx/                            # Shortwave static, squelch bursts, harmonic chimes, sfx_catalog.json
│   └── consoles/                       # Broadcast console templates
├── scripts/                            # Broadcast synthesis, 1440p QHD shader renderer, artifact builder & uploader
│   ├── build_station_artifacts.py      # Generates animated eQSL GIFs, UAP burst GIFs, audio suites & JS data bundles
│   ├── synth_full_episode.py           # Synthesizes Argon III-C narration, DX vignettes, clip audio & Lydian chime
│   ├── render_full_episode.py          # Renders 2560x1440 30fps High@L5.1 QHD broadcast video with 10 NumPy shaders
│   ├── build_youtube_package.py        # Generates YOUTUBE_METADATA.md, .srt, .vtt, and chapter markers
│   └── upload_youtube.py               # Automated YouTube Data API v3 uploader for @GOR-9-station
└── episodes/                           # Self-contained broadcast folders (sequenced by Broadcast & Galactic Epoch)
    ├── ep00_2735.215_pilot/            # Broadcast 00 (July 2024 Pilot • Epoch 2735.215 • 0400 GCT)
    │   ├── GOR-9.mp4                   # Finished pilot broadcast video at root (local)
    │   ├── youtube/                    # Captions (.srt, .vtt), metadata (.json, .tsv), thumbnail
    │   ├── script/                     # Original broadcast script & MLT timeline
    │   ├── audio/                      # Original pilot narration track
    │   └── slides/                     # Original pilot plates & animation loops
    └── ep01_2736.305_parallelogram/    # Broadcast 01 (Epoch 2736.305 • 0400 GCT)
        ├── gor9_ep01.mp4               # Finished 2560x1440 QHD master broadcast video right at the root (local)
        ├── youtube/                    # One-stop YouTube upload folder:
        │   ├── YOUTUBE_METADATA.md     # Copy-paste Title, Description, Chapters & checklist
        │   ├── youtube.json            # Uploaded YouTube video ID & Studio URL manifest
        │   ├── gor9_ep01.srt           # Frame-accurate SubRip closed captions
        │   ├── gor9_ep01.vtt           # Frame-accurate WebVTT closed captions
        │   ├── gor9_ep01_thumbnail_split.jpg
        │   └── gor9_ep01_thumbnail_tower.jpg
        ├── script/                     # Broadcast script (gor9_ep01_script.txt) & ep01_timeline.json
        ├── audio/                      # Full master WAV + segments/ (cached Argon III-C WAVs)
        ├── plates/                     # Broadcast-specific remote camera plates & Euclid SVG
        ├── clips/                      # 10s generated video+audio insert clips (N-24, Blowtorch, M-33, etc.)
        └── previews/                   # Rendered QHD preview frames for each console & panel
```

---

## 2. Galactic Coordinated Time (`GCT`) — What Are We Relative To?

Out on **Asteroid 3-5-1** in **Oort Cloud Sector 9 (`42,100 AU` from Sol)**, there is no planetary horizon day/night and no Earth calendar:
- Asteroid 3-5-1 is a `38 km × 21 km × 16 km` carbonaceous-basalt shard with an erratic **9.42-hour axial tumble (`P_rot = 9h 25m 12s`)**.
- To prevent the 50 kW concentric-ring emitter and the `O.R.S. 351` orbital relay link from sweeping wildly across the sky every 4.7 hours, the **High Basalt Shelf Tower Outpost** is anchored at **88.4° South Asteroidal Latitude** on the rim of **Acheron Polar Chasm**—aligned with the asteroid's **South Rotational Pole**.
- Because the tower sits at the south rotational pole, the **Galactic Milky Way Core (Sagittarius–Scorpius)** hangs in permanent deep-space night above the cliff precipice while the distant Sun is a faint magnitude `-18.5` pinprick skimming `-1.6°` below the northern crater rim, and **`O.R.S. 351`** maintains a stationary polar halo station-keeping position `42.8 km` off the shelf.

### The Pulsar Barycentric Clock (`PSR B1937+21`)
Instead of tying clocks to any spinning planet or tumbling rock, all Oort, Jovian, Saturnian, and Trojan stations lock their oscillators to **Galactic Coordinated Time (`GCT`)**—often still stamped `UTC` on vintage Hauser MK-IV receiver bezels:

1. **Physical Reference (`The Vulpecula Metronome`)**:
   - Locked to the barycentric arrival of pulses from millisecond pulsar **`PSR B1937+21` (`J1939+2134`)** in Vulpecula, which rotates at **`641.928262 Hz`** (`1.557806 ms` per pulse—more stable than most atomic clocks), cross-indexed against the **Galactic Center (`Sagittarius A*`)** and the **21-cm Hydrogen Hyperfine Line (`1,420.405751 MHz`)**.
2. **The Standard Galactic Cycle (`2400 GCT`)**:
   - **1.000 Galactic Cycle** = exactly **`55,462,600` pulsar ticks** (`86,400.000` SI seconds), divided into 24 Galactic Hours (`0000` to `2400 GCT`) so human crews living inside dark basalt mines, domes, and outposts maintain a stable circadian rhythm:
     - `0000 – 0800 GCT`: **Night Shift / Deep-Space DX Watch** (Reactor #2 stepped down to `12 kW`; GOR-9 signs on at **`0400 GCT`** when interplanetary solar-wind ionization reaches its quietest trough).
     - `0800 – 1600 GCT`: **Primary Quarry & Dragline Shift** (Silicate Quarry 44-K & Ceres Spot Exchange open).
     - `1600 – 2400 GCT`: **Maintenance, Feedhorn De-Sputtering & Buoy Telemetry Poll**.
3. **Broadcast Epoch Sequencing (`Epoch YYYY.DDD • 0400 GCT`)**:
   - **1 Galactic Year** = `365` Standard Cycles (`.001` to `.365`).
   - Every GOR-9 broadcast advances monotonically along this timeline:

| Broadcast | Folder | Galactic Timestamp | Broadcast Title & Key Anomalies |
| :--- | :--- | :--- | :--- |
| **BCAST 00** | [`episodes/ep00_2735.215_pilot/`](file:///home/phi/Sessions/GOR-9/episodes/ep00_2735.215_pilot) | **`2735.215 • 0400 GCT`** | *Pilot Broadcast* — Carina-Sagittarius Cochrane flux, Kuiper asteroid traffic, BorgCoin, Crab Nebula rogue AI, binary neutron star waves. |
| **BCAST 01** | [`episodes/ep01_2736.305_parallelogram/`](file:///home/phi/Sessions/GOR-9/episodes/ep01_2736.305_parallelogram) | **`2736.305 • 0400 GCT`** | *The Unsuspecting Parallelogram* — Van Allen VA-4 Comet K4 skip duct, KZ9-Omega 60 kV squall & Belt-Master marzelvane #4; Grade-B Dilithium pellets (+4%), Ring-Bake de-icer & Cryo-Toast foot-warmers; Hauser MK-IV intercepts (Buoy N-24, Radio Corrugated blowtorch, M-33 Ming drift-buoy via ALG-02, Trojan Octal numbers via ALG-03); Bogey-9 Trail-Cam 140g UAP cylinder; Van Allen ED-9 Euclidean Detector single lock on Callisto-South Vat 19 (`Euclid I.34 / G.47` Parallelogram & mud-rake cotter pin cover-up). |
| **BCAST 02** *(Next)* | `episodes/ep02_2736.312_.../` | **`2736.312 • 0400 GCT`** | *Planned*: Comet C/2736-K4 uninspected Dilithium barge rendezvous (`Pedregal 1051.2 mbar` code) & a suspected rhombus (`Euclid Def. I.22`) aboard bulk ice-hauler *MV Cryogenic-9*. |

### Local & Planetary Time Systems Referenced on the Hauser MK-IV
When GOR-9 intercepts transmissions from across the solar system and beyond, operators translate their local clocks against `GCT`:
- **Asteroid 3-5-1 Local Tumble-Phase (`T-Phase 0.00..1.00`)**: `9h 25m 12s` equatorial rotation period (`2.548 tumbles` per `GCT` cycle)—used by Silicate Quarry 44-K dragline crews on the equatorial belt to time low-gravity slag throws.
- **Titan-Minor Tidal Sol (`TSol`)**: `15.945 GCT cycles` per Saturnian orbit—governs the methane tide tables recited by Hydrographic Buoy N-24 on `3,890 kHz`.
- **Callisto Dome-4 Synodic Schedule (`J-Dome Time`)**: `16.689 GCT cycles` synchronized to Callisto's passage through Jupiter's magnetospheric current sheet (when Dome-4 dims its sodium streetlamps for the "Night Market" and *Radio Corrugated* fires up on `11,410 kHz`).
- **Ming-Era Terra Ephemeris (`Epoch 1580 CE`)**: Legacy terrestrial clock still broadcast by the 700-year-old Intergalactic M-33 drift-buoy on `1,420.405 MHz`.
