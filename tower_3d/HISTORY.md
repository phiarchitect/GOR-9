# GOR-9 • 3D Station, Marzelvane Emitters & Broadcast Booth Evolution Log

Every major architectural milestone of the 3D station model is preserved in [`tower_3d/history/`](file:///home/phi/Sessions/GOR-9/tower_3d/history) via [`snapshot_version.py`](file:///home/phi/Sessions/GOR-9/tower_3d/snapshot_version.py), including the parametric IngeTrazo 0.6.0 generator (`build_ingetrazo_tower.py`), native `.igz` and `.obj` geometry, the interactive Three.js WebGL studio (`tower-3d.html`), and all `2560×1440` renders.

---

## Milestone Archive

### `v01_initial_island_consoles` — Initial 5-Bay Island Console & 4-Ring Marzelvane Crown
- **Date**: `2026-11-04`
- **Key Features**:
  - Connected Antigravity MCP to live **IngeTrazo 0.6.0** (`127.0.0.1:4763`).
  - Built initial 9-column basalt shelf, lower steel lattice base (`z = 0m..16m`), cantilevered octagonal broadcast booth (`z = +16m..+21.8m`), upper lattice mast (`z = +21.2m..+56m`), and **4 concentric Marzelvane Emitter rings** (`z = +46.5m`, $R = 6.5, 10.5, 14.5, 18.8\text{ m}$).
  - Interior featured a seated-height (`0.78m`) 5-bay wraparound console island in the middle of the room with suspended mid-window overhead monitors, plus an operator bridge desk with the articulated boom microphone.
- **Critique / Lessons Learned**:
  - The steel tower lattice stopped at the booth floor (`+16m`) and resumed at the roof (`+21.2m`) rather than running continuously through the booth.
  - The consoles floated inside the room with overhead monitors partially occluding the windows, rather than sitting around the outside octagonal walls just under the window sills at standup desk height.

---

### `v02_perimeter_standup_continuous_truss` — Continuous Tower Truss, Outer-Wall Standup Consoles & Rolling Stools
- **Date**: `2026-11-04`
- **Archive Path**: [`tower_3d/history/v02_perimeter_standup_continuous_truss/`](file:///home/phi/Sessions/GOR-9/tower_3d/history/v02_perimeter_standup_continuous_truss)
- **Key Features**:
  1. **Continuous Tower Structure Through the Booth**:
     - The 4-leg tapered steel lattice tower (`0m → 52m`), horizontal girts, diagonal X-bracing, and central octagonal coaxial waveguide/helical bus mast (`r = 0.24m` with 4 glowing cyan Cherenkov conduits) run **uninterrupted through the floor and ceiling** of the octagonal broadcast booth.
  2. **Perimeter Standup Consoles Tucked Under the Windows**:
     - Raised the octagonal window sill to `z = +1.56m` above the booth floor and mounted all 7 console bays flush against the **outside walls of the octagon (`r = 5.15m`)** at **standup desk height (`+1.05m`)**.
     - Dual side-by-side `16:9` console screens sit on a low-profile sloped wedge (`+1.05m .. +1.55m`) tucked directly under the panoramic window sills, leaving the outward-tilted observation windows 100% unobstructed.
  3. **Master Broadcast Desk & Tall Rolling Stools**:
     - Placed the articulated studio boom microphone (`ON AIR • 0400 GCT` crimson tally ring), open station logbook, 2-sided eQSL card, brass Morse key (`GO-9 SWL 1978`), weighted VFO wheel, and insulated mug on the North standup desk (`y_desk = +1.05m`).
     - Added **3 tall ergonomic rolling broadcast/drafting stools** with chrome circular foot-rings (`+0.28m`), 5-star caster bases, and swivel cushions (`+0.78m`).

---

### `v03_lighthouse_cliff_edge_base_compound` — Modular Components, 86.5m Cliff-Edge Lighthouse, Base Compound & Reset Low-Angle Cameras
- **Date**: `2026-11-04`
- **Archive Path**: [`tower_3d/history/v03_lighthouse_cliff_edge_base_compound/`](file:///home/phi/Sessions/GOR-9/tower_3d/history/v03_lighthouse_cliff_edge_base_compound)
- **Key Features**:
  1. **Modular Component Architecture ([`tower_3d/components/`](file:///home/phi/Sessions/GOR-9/tower_3d/components))**:
     - Split the 3D scene generator into 8 dedicated component modules: [`primitives.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/primitives.py), [`terrain_basalt.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/terrain_basalt.py), [`base_infrastructure.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/base_infrastructure.py), [`tower_structure.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/tower_structure.py), [`booth_architecture.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/booth_architecture.py), [`consoles.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/consoles.py), [`furniture_props.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/furniture_props.py), and [`marzelvane_emitters.py`](file:///home/phi/Sessions/GOR-9/tower_3d/components/marzelvane_emitters.py).
  2. **Sheer 48m Columnar Basalt Cliff Edge & Acheron Chasm Promontory**:
     - Positioned the `86.5m` lighthouse tower right at the **sheer East/SE precipice edge** of the 48m-tall vertical hexagonal/pentagonal basalt cliff columns (`z = -48.0m .. 0.0m`), with cantilevered steel foundation brackets anchored directly into the cliff face and the deep Acheron Chasm floor (`z = -54m .. -35m`) dropping away below.
     - Added the upland basalt mountain massif rising behind the headland (`112° .. 258°`), chasm sea-stack needles, 4 basalt guy-wire anchor bollards, and 3 Bogey-9 Trail-Cam tripods (`TRL-01..03`).
  3. **Taller `86.5m` Lighthouse Proportions & Full EVA Climb Spine to the Marzelvane Emitters**:
     - Raised the cantilevered Octagonal Broadcast Booth to `BOOTH_Z = 26.0m`, the 4 concentric **Marzelvane Emitter rings** (`R = 7.0, 11.5, 16.0, 21.0m`) to `MARZEL_Z = 72.0m`, and the Crown Cherenkov Spire to `SPIRE_TOP_Z = 86.5m` (`134.5m` total vertical relief from the `-48.0m` cliff base to the `+86.5m` spire tip).
     - Added the lower pressurized personnel climb tube (`z = 2.8m .. 26.0m`), interior booth climb ladder (`z = 26.0m .. 31.2m`), and upper **EVA Caged Climb Ladder (`z = 31.2m .. 72.0m`)** with 3 intermediate circular grated service platforms (`+45.0m`, `+58.0m`, and the **Marzelvane Crown Service Gallery at `+70.8m`** with 4 radial catwalk bridges out to the inner emitter ring).
  4. **Headland Base Infrastructure Compound (`z = -1.8m .. 0.0m`)**:
     - **SW Terrace**: Pressurized Keeper's Habitat & Workshop Quonset (`(-14.8, -6.2, -1.6m)`) connected to the central climb tube by an enclosed pressurized transfer tunnel (`z = +1.15m`).
     - **NW Terrace**: Recessed **50 kW Pebble-Bed Dilithium Reactor #2** with 6 glowing vertical radiator wings, Van Allen HVDC step-down transformer switchyard, and twin armored busbar conduits feeding the tower base.
     - **SE Cliff Edge**: Cryo-Condenser Spheres (`He-3` / `D2`) and a **Cantilevered Chasm Supply Winch Crane** overhanging the sheer cliff precipice with its hoist cable dropping down to `z = -18.8m`.
  5. **Reset Camera Settings for the Cliff-Edge Model Proportions**:
     - Updated all camera presets in both [`build_ingetrazo_tower.py`](file:///home/phi/Sessions/GOR-9/tower_3d/build_ingetrazo_tower.py) and [`docs/tower-3d.html`](file:///home/phi/Sessions/GOR-9/docs/tower-3d.html) (`1–8` hotkeys), including the low-angle chasm look-up shot positioned out in front of the cliff looking up at the 48m vertical basalt columns and `86.5m` lighthouse tower.

