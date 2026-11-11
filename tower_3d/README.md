# Relay Station GOR-9 · 3D Tower, Marzelvane Emitters & Octagonal Broadcast Booth

This directory contains the parametric 3D CAD/scene generator for **Relay Station GOR-9** on **Asteroid 3-5-1** (`Acheron Polar Chasm`), built for **IngeTrazo 0.6.0** (with live MCP bridge integration on `127.0.0.1:4763`) alongside the standalone interactive Three.js / WebGL 3D station and broadcast studio viewer in [`docs/tower-3d.html`](file:///home/phi/Sessions/GOR-9/docs/tower-3d.html).

---

## 1. Architectural & Engineering Components

1. **Asteroid 3-5-1 Columnar Basalt Crag (`1_Asteroid_351_Basalt_Crag`)**:
   - Stepped hexagonal and octagonal dark basalt columns forming the polar cliff shelf (`z = -28.0m` to `0.0m`) with an octagonal reinforced steel-and-concrete anchor pad.
2. **Lower Open-Lattice Steel Tower Base (`2_Lower_Steel_Lattice_Base`)**:
   - Tapered 4-leg structural steel truss tower (`z = 0.0m` to `+16.0m`) with cross-braced bays and a central elevator/waveguide core column.
3. **Cantilevered Octagonal ATC Broadcast Booth (`3_Octagonal_Broadcast_Booth`)**:
   - Perched at `z = +16.0m` to `+21.8m` (`Catwalk R = 7.4m`, `Booth R = 5.6m`), featuring a 360-degree wraparound catwalk with twin safety rails, outward-canting trapezoidal double-pane observation windows, warm `2700K` interior tungsten lighting strips, and the rooftop **`GOR-9`** neon sign (steady amber `GOR-` with intermittent blinking `9`).
4. **Upper Lattice Mast & Waveguide Exciter Collars (`4_Upper_Lattice_Mast_And_GuyWires`)**:
   - Tapered upper lattice mast (`z = +21.2m` to `+56.5m`) with two intermediate circular waveguide exciter collars (`z = +33.0m` and `+38.5m`), crimson aviation hazard beacons, and 4 tensioned guy-wires anchored to basalt mooring bollards.
5. **The 4 Concentric "Marzelvane Emitter" Rings (`5_Marzelvane_Emitter_Concentric_Rings`)**:
   - Crowned at `z = +46.5m` around the upper Cherenkov spire:
     - **Marzelvane Ring 1 (Inner Core Emitter)**: `R = 6.5m`, tube radius `0.38m`
     - **Marzelvane Ring 2 (Secondary Phase Emitter)**: `R = 10.5m`, tube radius `0.36m`
     - **Marzelvane Ring 3 (Tertiary Harmonic Emitter)**: `R = 14.5m`, tube radius `0.34m`
     - **Marzelvane Ring 4 (Outer Corona Aperture Emitter)**: `R = 18.8m`, tube radius `0.34m`
   - Equipped with upper and lower Cherenkov cyan corona discharge rings, 16 radial waveguide tension spokes, high-voltage ceramic standoff insulator nodes at every ring intersection, and diagonal mast suspension stays.
6. **Interior 5-Bay Wraparound Console Desk & Overhead Telemetry Monitors (`Console_Bay1..5`)**:
   - True sloped wedge cabinets with 1:1 affine UV-fitted textures (`core.texture.fit_uv_affine`) for all **5 designed GOR-9 interfaces**:
     - **Bay 1 (Center-Port)**: `Hauser MK-IV Wideband DX Correlator` (`mk4_3b_video.png`) + overhead `Wideband FFT Spectrum` (`mk4_3c_spectrum.png`)
     - **Bay 2 (Center-Starboard)**: `Van Allen VA-4 Weather, Propagation & Dilithium Bus` (`va4_1b_squall.png`) + overhead `Galactic Signal Atlas` (`mk4_3c_atlas.png`)
     - **Bay 3 (Starboard-Forward)**: `Van Allen ED-9 Euclidean Geometric Detector` (`ed9_4d_step4.png`) + overhead `Proposition I.45 Construction` (`ed9_4b_step1.png`)
     - **Bay 4 (Starboard-Aft)**: `Bogey-9 Perimeter Trail-Cam & UAP Correlator` (`bogey_4a_frame6.png`) + overhead `NVG Optical Sentinel` (`bogey_4a_nvg.png`)
     - **Bay 5 (Port-Forward)**: `Station Dossier & 2-Sided eQSL Archive` (`dos_3a_n24.png`) + overhead `2-Sided eQSL Reverse` (`dos_3d_octal_back.png`)
   - Riveted **`Hauser Dynamics`** (`hauser_logo.svg`) and **`Van Allen & Sons Switchgear`** (`van_allen_logo.svg`) cast-brass & brushed-gunmetal manufacturer badges on the front console skirts.
7. **Operator Broadcast Desk, Articulated Studio Boom Microphone & Props (`6_Operator_Mic_Logbook_And_Props`)**:
   - Articulated twin-tube studio boom arm with brass friction joints, spider shock-mount cradle, classic side-address broadcast condenser microphone capsule, and illuminated crimson `"ON AIR • 0400 GCT"` tally ring.
   - Clear operator desk space around the microphone featuring the open spiral-bound **Station Logbook**, **2-Sided eQSL Collector Cards**, **`GO-9 SWL 1978` Brass Straight Morse Key**, **Weighted Barycentric VFO Jog Wheel**, and **`GALACTIC OUTPOST 9` Insulated Mug**.

---

## 2. Running the IngeTrazo 0.6.0 Builder & Live Bridge Script

With **IngeTrazo 0.6.0** open and the AI Bridge active on `127.0.0.1:4763`:

```bash
/home/phi/PROJECTS/phi-WORKS/ingetrazo/.venv/bin/python /home/phi/Sessions/GOR-9/tower_3d/build_ingetrazo_tower.py --live
```

This single script:
- Saves [`tower_3d/gor9_tower.igz`](file:///home/phi/Sessions/GOR-9/tower_3d/gor9_tower.igz) and [`tower_3d/gor9_tower.obj`](file:///home/phi/Sessions/GOR-9/tower_3d/gor9_tower.obj)
- Pushes the complete 3D model live into the running **IngeTrazo 0.6.0** viewport
- Renders 4 native `2560×1440` OpenGL viewport captures (`renders/ingetrazo_01..04.png`)
- Captures 5 `2560×1440` WebGL screenshots of [`docs/tower-3d.html`](file:///home/phi/Sessions/GOR-9/docs/tower-3d.html) (`renders/web3d_01..05.png`)
