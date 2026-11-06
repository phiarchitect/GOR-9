#!/usr/bin/env python3
"""
GOR-9 Deep-Space Lighthouse, Base Compound, Octagonal Booth & Marzelvane Emitters
=================================================================================
Assembles the modular 3D components from `tower_3d.components` into an
IngeTrazo 0.6.0 scene (`gor9_tower.igz` + `.obj`/`.mtl`), and optionally pushes
the model live over the IngeTrazo AI TCP Bridge (`127.0.0.1:4763`) to render
2560x1440 QHD studio views.
"""

import argparse
import os
import sys
from pathlib import Path

INGETRAZO_ROOT = Path("/home/phi/PROJECTS/phi-WORKS/ingetrazo")
if str(INGETRAZO_ROOT) not in sys.path:
    sys.path.insert(0, str(INGETRAZO_ROOT))
if str(INGETRAZO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(INGETRAZO_ROOT / "scripts"))

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tower_3d.components import (
    BOOTH_Z,
    MARZEL_Z,
    SPIRE_TOP_Z,
    build_base_infrastructure,
    build_celestial_beacons,
    build_companion_boulders,
    build_continuous_tower_and_spine,
    build_furniture_and_props,
    build_marzelvane_emitters,
    build_octagonal_booth,
    build_orbital_satellites,
    build_perimeter_consoles,
    build_prismatic_basalt_terrain,
    build_tumbling_asteroids,
)


def build_gor9_scene(scene, repo_root: Path):
    """Build all modular architectural, asteroid, orbital, and celestial beacon layers into `scene`."""
    engineer_group = None
    for g in list(scene.groups):
        if getattr(g, "is_guide", False) or g.name == "Engineer":
            engineer_group = g
            break

    scene.clear()
    build_prismatic_basalt_terrain(scene)
    build_base_infrastructure(scene)
    build_continuous_tower_and_spine(scene)
    build_octagonal_booth(scene)
    build_perimeter_consoles(scene, repo_root)
    build_furniture_and_props(scene, repo_root, engineer_group=engineer_group)
    build_marzelvane_emitters(scene)
    build_companion_boulders(scene)
    build_tumbling_asteroids(scene)
    build_orbital_satellites(scene)
    build_celestial_beacons(scene, repo_root)
    scene.version += 1


LIVE_BRIDGE_CODE = r"""
import math
import sys
from pathlib import Path
from PySide6.QtGui import QVector3D

repo_root = Path("/home/phi/Sessions/GOR-9")
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import importlib
import tower_3d.components.primitives as _p
import tower_3d.components.terrain_basalt as _tb
import tower_3d.components.base_infrastructure as _bi
import tower_3d.components.tower_structure as _ts
import tower_3d.components.booth_architecture as _ba
import tower_3d.components.consoles as _co
import tower_3d.components.furniture_props as _fp
import tower_3d.components.marzelvane_emitters as _me
import tower_3d.components.asteroids_satellites as _as
import tower_3d.components as _comp
import tower_3d.build_ingetrazo_tower as _b

for _mod in (_p, _tb, _bi, _ts, _ba, _co, _fp, _me, _as, _comp, _b):
    importlib.reload(_mod)

_b.build_gor9_scene(scene, repo_root)
BOOTH_Z = _p.BOOTH_Z
MARZEL_Z = _p.MARZEL_Z

renders_dir = repo_root / "tower_3d" / "renders"
renders_dir.mkdir(parents=True, exist_ok=True)

# 1. Standup Broadcast Desk & Perimeter Consoles POV (looking North & NE across mic, logbook, rolling stool & under-window consoles)
viewport.camera.target = QVector3D(0.35, 4.25, BOOTH_Z + 1.25)
viewport.camera.distance = 2.15
viewport.camera.yaw = math.radians(-72.0)
viewport.camera.pitch = math.radians(10.0)
viewport.camera.fov = 60.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_01_operator_booth_pov.png"))

# 2. Booth Wide Interior (from West walkway showing Continuous Center Lattice Tower + Climb Ladder + Perimeter Standup Consoles + Rolling Stools)
viewport.camera.target = QVector3D(1.15, 2.85, BOOTH_Z + 1.25)
viewport.camera.distance = 4.75
viewport.camera.yaw = math.radians(-147.3)
viewport.camera.pitch = math.radians(12.0)
viewport.camera.fov = 62.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_02_booth_wide.png"))

# 3. Low-Angle Cliff-Edge Hero Look-Up (from Acheron Chasm below the cliff lip looking UP at the 48m basalt cliff & 86.5m Lighthouse!)
viewport.camera.target = QVector3D(0.0, 0.0, 34.0)
viewport.camera.distance = 122.0
viewport.camera.yaw = math.radians(-38.0)
viewport.camera.pitch = math.radians(-18.0)
viewport.camera.fov = 52.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_03_exterior_full_tower.png"))

# 4. Marzelvane Emitters Crown (+72.0m) & EVA Climb Service Gallery (+70.8m) — Looking UP into the 4 Concentric Rings & Spire
viewport.camera.target = QVector3D(0.0, 0.0, MARZEL_Z + 1.5)
viewport.camera.distance = 44.0
viewport.camera.yaw = math.radians(-42.0)
viewport.camera.pitch = math.radians(-14.0)
viewport.camera.fov = 50.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_04_marzelvane_emitters.png"))

# 5. Headland Base Infrastructure Compound & Cliff Precipice (Habitat, Transfer Tunnel, Reactor #2, Chasm Winch Crane & Basalt Cliffs)
viewport.camera.target = QVector3D(-3.5, -1.5, 4.0)
viewport.camera.distance = 58.0
viewport.camera.yaw = math.radians(-62.0)
viewport.camera.pitch = math.radians(18.0)
viewport.camera.fov = 50.0
viewport.update()
viewport.render_image(2560, 1440).save(str(renders_dir / "ingetrazo_05_base_compound_basalt_crag.png"))

# Leave the user's live IngeTrazo viewport parked on the Low-Angle Cliff-Edge Look-Up view!
viewport.camera.target = QVector3D(0.0, 0.0, 34.0)
viewport.camera.distance = 122.0
viewport.camera.yaw = math.radians(-38.0)
viewport.camera.pitch = math.radians(-18.0)
viewport.camera.fov = 52.0
viewport.update()

result = {"groups": [g.name for g in scene.groups], "renders": 5}
"""


def capture_web_renders(repo_root: Path):
    """Capture 2560x1440 screenshots of docs/tower-3d.html across camera presets."""
    import functools
    import http.server
    import shutil
    import socketserver
    import subprocess
    import threading

    docs_dir = repo_root / "docs"
    renders_dir = repo_root / "tower_3d" / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(docs_dir))

    class QuietTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with QuietTCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        browser_bin = (
            shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )
        if not browser_bin:
            pw_root = Path.home() / ".cache" / "ms-playwright"
            if pw_root.is_dir():
                for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
                    browser_bin = str(candidate)
                    break

        shots = [
            ("satellite_pov", "web3d_01_satellite_pov.png"),
            ("chasm_cliff", "web3d_02_chasm_cliff.png"),
            ("vertical_sign", "web3d_03_vertical_sign_booth.png"),
            ("cliff_compound", "web3d_04_cliff_compound.png"),
            ("operator_pov", "web3d_05_operator_booth_pov.png"),
            ("booth_wide", "web3d_06_booth_wide.png"),
        ]
        if browser_bin:
            for cam_key, fname in shots:
                out_file = renders_dir / fname
                url = f"http://127.0.0.1:{port}/tower-3d.html?cam={cam_key}"
                cmd = [
                    browser_bin,
                    "--headless",
                    "--no-sandbox",
                    "--enable-webgl",
                    "--ignore-gpu-blocklist",
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--window-size=2560,1440",
                    "--virtual-time-budget=4500",
                    f"--screenshot={out_file}",
                    url,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                print(f"Captured WebGL 3D view: {out_file}")
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Build GOR-9 3D Lighthouse Station in IngeTrazo 0.6.0")
    parser.add_argument("--live", action="store_true", help="Push directly to running IngeTrazo MCP bridge (127.0.0.1:4763)")
    parser.add_argument("--skip-web", action="store_true", help="Skip headless browser capture of docs/tower-3d.html")
    args = parser.parse_args()

    out_dir = REPO_ROOT / "tower_3d"
    out_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from core.scene import Scene
    from formats.igz import save_scene
    from formats.obj import save_obj

    _app = QApplication.instance() or QApplication(sys.argv)
    scene = Scene()
    build_gor9_scene(scene, REPO_ROOT)

    igz_path = out_dir / "gor9_tower.igz"
    obj_path = out_dir / "gor9_tower.obj"
    save_scene(scene, igz_path)
    save_obj(scene, obj_path)
    total_faces = sum(len(g.mesh.faces) for g in scene.groups)
    print(f"Saved IngeTrazo project: {igz_path} ({len(scene.groups)} groups, {total_faces} faces)")
    print(f"Saved Wavefront OBJ:     {obj_path}")

    if args.live:
        import ingetrazo_mcp
        resp = ingetrazo_mcp._bridge("run_python", {"code": LIVE_BRIDGE_CODE})
        print("Live IngeTrazo 0.6.0 response:", resp)

    if not args.skip_web:
        capture_web_renders(REPO_ROOT)


if __name__ == "__main__":
    main()
