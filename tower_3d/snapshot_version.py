#!/usr/bin/env python3
"""
Snapshot the current state of the GOR-9 3D Tower & Broadcast Booth model
into `tower_3d/history/<version_slug>/`, preserving:
  - `build_ingetrazo_tower.py` (IngeTrazo 0.6.0 parametric builder)
  - `gor9_tower.igz`, `gor9_tower.obj`, `gor9_tower.mtl` (3D geometry & UV textures)
  - `tower-3d.html` (Interactive Three.js WebGL studio)
  - `renders/*.png` (All IngeTrazo 0.6.0 and WebGL 2560x1440 viewport renders)
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path


def snapshot(version_slug: str, summary: str = "") -> Path:
    tower_dir = Path(__file__).resolve().parent
    repo_root = tower_dir.parent
    hist_dir = tower_dir / "history" / version_slug
    renders_dst = hist_dir / "renders"
    renders_dst.mkdir(parents=True, exist_ok=True)

    files_to_copy = [
        tower_dir / "build_ingetrazo_tower.py",
        tower_dir / "gor9_tower.igz",
        tower_dir / "gor9_tower.obj",
        tower_dir / "gor9_tower.mtl",
        repo_root / "docs" / "tower-3d.html",
    ]
    for src in files_to_copy:
        if src.exists():
            shutil.copy2(src, hist_dir / src.name)

    comp_src = tower_dir / "components"
    if comp_src.is_dir():
        comp_dst = hist_dir / "components"
        if comp_dst.exists():
            shutil.rmtree(comp_dst)
        shutil.copytree(comp_src, comp_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    renders_src = tower_dir / "renders"
    if renders_src.is_dir():
        for png in sorted(renders_src.glob("*.png")):
            shutil.copy2(png, renders_dst / png.name)

    meta_file = hist_dir / "SNAPSHOT.md"
    ts = datetime.now().astimezone().isoformat(timespec="seconds")
    meta_file.write_text(
        f"# Snapshot: `{version_slug}`\n\n"
        f"- **Timestamp**: `{ts}`\n"
        f"- **Summary**: {summary or '3D Station, Marzelvane Emitters & Broadcast Booth milestone'}\n"
        f"- **Archived Files**: `build_ingetrazo_tower.py`, `components/*.py`, `gor9_tower.igz`, `gor9_tower.obj`, `tower-3d.html`, and `{len(list(renders_dst.glob('*.png')))}` renders.\n"
    )
    print(f"Snapshotted 3D model -> {hist_dir}")
    return hist_dir


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tower_3d/snapshot_version.py <version_slug> [summary]")
        sys.exit(1)
    slug = sys.argv[1]
    desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    snapshot(slug, desc)
