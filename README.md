# GOR-9 • Galactic Outpost Radio (`14,285.7 kHz USB`)

**From Asteroid 3-5-1 in Oort Cloud Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum.**

- **Official YouTube Channel**: [`youtube.com/@GOR-9-station`](https://www.youtube.com/@GOR-9-station)
- **Transmitter Location**: High Basalt Shelf ATC Control Tower (South Rotational Pole, `88.4° S`), Asteroid 3-5-1, Oort Cloud Sector 9 (`42,100 AU` / `0.666 ly` from Sol; plunging cometary ellipse `Q = 42,500 AU → q = 1.22 AU`, `v_r = -42.6 m/s`, `1.39 Myr` to frost-line coma ignition)
- **Carrier & Waveguide**: `14,285.7 kHz` Upper Sideband (`λ = 20.985 m`, `50 kW` Peak / `12 kW` Watch 0 Step-Down via Pebble-Bed Dilithium Reactor #2), biasing Sector 9 of the **12-Station (`GOR-1..12`) Marzelvane Barycentric Flux-Duct Ring**
- **Primary Tower Consoles**:
  - **Hauser MK-IV Wideband Barycentric DX Correlator** (*Hauser Dynamics • Ganymede Orbital Precision Works*)
  - **Celestial Sphere, `5'` Lyot Solar Coronagraph (`4.90"/AU`) & 3D Oort Relay Ring Navigator**
  - **Van Allen VA-4 Heliopause Sounder & 50 kW Dilithium Bus Console** (*Van Allen & Sons Switchgear • Ceres Foundry #7*)
  - **Bogey-9 Perimeter Asteroid Trail-Cam & Non-Keplerian UAP Discriminator**
  - **Van Allen ED-9 Euclidean Detector & Cosmic Geometric Intelligence Correlator** (*1.33-ly VLBI Baseline `GOR-9 ↔ GOR-3`*)
- **Orbital Relay**: Synchronous Polar Halo Satellite **`O.R.S. 351`** (`Alt: 42.8 km`)
- **Time Standard**: **Pulsar Barycentric Time (`PST`)** — Non-terrestrial decimal pulsar clock locked to **`PSR B1937+21`** (`641.928262 Hz`, the *"Vulpecula Metronome"*: `Beats → 6 Watches = 1 Cycle → 10 Cycles = 1 Sweep`). See full physics & ephemeris specification in [`ASTROMETRY_AND_TIME.md`](ASTROMETRY_AND_TIME.md).

---

## 1. Repository & Broadcast Organization

All broadcast productions are self-contained inside `episodes/<broadcast_id>/`, while the interactive companion web consoles live in `docs/` and recurring station-wide hardware rigs, camera plates, sound effects, and channel branding live in `station/`:

```text
GOR-9/
├── gor9_ep01.mp4                       # Latest finished 2560x1440 QHD master broadcast video (local root hardlink)
├── README.md                           # Station overview, Pulsar Time (PST) standard, & broadcast index
├── ASTROMETRY_AND_TIME.md              # Canonical Oort astrometry, 3.10 Myr cometary orbit, Flux-Ducts & PST spec
├── PRODUCTION_BIBLE.md                 # Full world lore, hardware specs, & shader/console documentation
├── docs/                               # Interactive Companion Web Consoles & Station Ledger
│   ├── index.html                      # Hauser MK-IV Wideband DX Receiver, Decoder & Galaxy Signal Atlas
│   ├── celestial-atlas.html            # Sidereal Sky, 2200× Solar Coronagraph, 3D Cometary Orbit & Sweep Roll-Call
│   ├── propagation.html                # Van Allen VA-4 Space Weather, Oort Propagation & Dilithium Bus Console
│   ├── bogey-detector.html             # Bogey-9 Perimeter Asteroid Trail-Cam & UAP Kinematic Correlator
│   ├── euclidean-detector.html         # Van Allen ED-9 Cosmic Geometric Intelligence Correlator
│   ├── station.html                    # Companion DX Ledger, 3D-Flip eQSL Collector Cards & Manufacturer Lore
│   └── data/                           # Canonical JSON & JS schemas (stations v3.0, propagation, bogeys, euclidean)
├── station/                            # Shared station-wide assets reused across all broadcasts
│   ├── branding/                       # @GOR-9-station avatar, banners, Hauser Dynamics & Van Allen Switchgear logos
│   ├── rig/                            # CAM-00A cliff tower RGBA mattes, 4 apex rings, beacons, O.R.S. 351 & asteroid sprites
│   ├── plates/                         # Recurring station camera plates (CAM-00A..00D, ATC Tower Room, UAP Trail-Cams)
│   ├── sfx/                            # Shortwave static, squelch bursts, harmonic chimes, sfx_catalog.json
│   └── consoles/                       # Broadcast console templates
├── scripts/                            # Broadcast synthesis, 1440p QHD shader renderer, artifact builder & uploader
│   ├── update_celestial_data.py        # Computes Keplerian 4.90"/AU Solar orbits, Oort Ring & Sweep Roll-Call data
│   ├── build_station_artifacts.py      # Generates animated eQSL GIFs, UAP burst GIFs, audio suites & JS data bundles
│   ├── synth_full_episode.py           # Synthesizes Argon III-C narration, DX vignettes, clip audio & Lydian chime
│   ├── render_full_episode.py          # Renders 2560x1440 30fps High@L5.1 QHD broadcast video with 10 NumPy shaders
│   ├── build_youtube_package.py        # Generates YOUTUBE_METADATA.md, .srt, .vtt, and chapter markers
│   └── upload_youtube.py               # Automated YouTube Data API v3 uploader for @GOR-9-station
└── episodes/                           # Self-contained broadcast folders (sequenced by Broadcast & Epoch)
    ├── ep00_2735.215_pilot/            # Broadcast 00 (Pilot • Legacy Stamp 2735.215)
    └── ep01_2736.305_parallelogram/    # Broadcast 01 (The Unsuspecting Parallelogram • Legacy Stamp 2736.305)
```

---

## 2. Oort Astrometry & Pulsar Barycentric Time (`PST`)

Full mathematical and worldbuilding details live in [`ASTROMETRY_AND_TIME.md`](ASTROMETRY_AND_TIME.md).

### Where Are We? (`42,100 AU` • `3.10 Myr` Cometary Plunge • `12-Relay` Oort Ring)
- **Unresolved Sky & `5-Arcminute` Solar Core**: From **Asteroid 3-5-1** (`42,100 AU` / `0.666 ly` in Oort Sector 9), `1 AU` subtends **`4.8994 arcseconds`**. The Sun (`Sol`, `Az 212.40°, El +22.40°`) is a razor-sharp magnitude `-3.62` point-star (`0.046"`), and the entire classical planetary system—`Earth (±4.9")`, `Ceres Foundry #7 (±13.6")`, `Jupiter + Callisto & 624 Hektor L4 (±25.5")`, `Saturn + Titan (±47.0")`, out to `Neptune (±2.46')`—fits inside a **5-arcminute Lyot Solar Coronagraph** field. Only detached `90377 Sedna` (`a = 506 AU`, aphelion `937 AU`) loops `1.28°` clear of Sol into the Hills Cloud.
- **Our Own Cometary Destiny**: Originally an `8.64 Myr` outer Oort shard, Asteroid 3-5-1 was torqued `~155 kyr` ago by a grazing M-dwarf star and the vertical Galactic tide onto a steep **`104.2°` retrograde plunging cometary ellipse** (`Q = 42,500 AU → q = 1.22 AU`, orbital period **`P = 3.10 Myr`**). Falling sunward at **`v_r = -42.6 m/s`**, Asteroid 3-5-1 will cross Saturn's `~10 AU` water-ice sublimation frost line and erupt into a Great Comet in **`1.392 million years` (`470,100 Sweeps`)**.
- **Marzelvane Barycentric Flux-Ducts**: `GOR-9` is one of **12 polar trunk outposts (`GOR-1` .. `GOR-12`)** forming an `~84,000 AU` (`1.33 ly`) Oort perimeter shell (paired antipodally with `GOR-3` for `0.0001"` VLBI interferometry). Pumping `50 kW` at `14,285.7 kHz` (`λ = 20.985 m`, resonant with the 4 Marzelvane rings $R = 7.0, 11.5, 16.0, 21.0\text{ m}$) biases barycentric gravitational-magnetic flux filaments into lossless standing-wave ducts—allowing `3 W` pirate tugs, `85 W` Titan buoys, and `180 W` Hektor crawlers to skip live across space without $1/r^2$ inverse-square wipeout or 8-month light-lag.

### Non-Terrestrial Pulsar Time (`PSR B1937+21` • `641.928262 Hz`)
With no Earth horizon, days, weeks, or years at `88.4° S` South Rotational Pole, all 12 Oort trunk stations count decimal pulse multiples of millisecond pulsar **`PSR B1937+21`** (`1.55780645 ms` period; `Epoch 000.000` = `1982.86 CE` Arecibo discovery; current broadcast **`Epoch 254.310 • Watch 0`**):

| `PST` Unit | Exact `PSR B1937+21` Pulses | Relation | Human Feel | Operational Role at GOR-9 |
| :--- | :--- | :--- | :--- | :--- |
| **`1 Beat`** | $10^3$ (`1,000`) | Base console tick | **`1.5578 sec`** | S-meter / waterfall sweep & PST footer heartbeat (`B0000..B9999`) |
| **`1 Watch`** | $10^7$ (`10,000` Beats) | Duty shift | **`4.327 hr`** | Standard operator console watch (`W0` = `12 kW` Quiet DX Watch) |
| **`1 Cycle`** | $6 \times 10^7$ (`6` Watches) | `W0` .. `W5` | **`25.963 hr`** | Deep-space circadian sleep/work cycle |
| **`1 Sweep`** | $6 \times 10^8$ (`10` Cycles) | **Broadcast cadence** | **`10.818 days`** | **GOR-9 Broadcast Roundup interval** (*"Sweep `.300 → .310` Roll-Call"*) |
| **`1 Epoch`** | $6 \times 10^{10}$ (`100` Sweeps) | `1,000` Cycles | **`2.962 yr`** | Major ledger integer (`Epoch 254.310`) |

*(Early prototype broadcasts `ep00_2735.215_pilot` and `ep01_2736.305_parallelogram` carry legacy `2400 GCT` Earth-emulator dial stamps recorded prior to the Sector 9 `PST` cutover.)*

### Local & Planetary Clocks Cross-Indexed on the Hauser MK-IV
- **Asteroid 3-5-1 Tumble-Phase (`T-Phase 0.00..1.00`)**: `9h 25m 12s` equatorial rotation period—used by Silicate Quarry 44-K dragline crews on the equatorial belt.
- **Titan-Minor Tidal Sol (`TSol`)**: `15.945 d` (`1.474 Sweeps`) per Saturnian orbit—governs methane tide tables from Hydrographic Buoy N-24 (`3,890 kHz`).
- **Callisto Dome-4 Synodic Schedule (`J-Dome Time`)**: `16.689 d` (`1.543 Sweeps`) synchronized to Callisto's passage through Jupiter's magnetospheric current sheet (*Radio Corrugated*, `11,410 kHz`).
- **Ming-Era Survey ROM (`Epoch 1580 CE`)**: Legacy clock still transmitted by Intergalactic Sonde `M33-771/R` on `1,420.405 MHz`.
