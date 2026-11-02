#!/usr/bin/env python3
"""Move /home/phi/Sessions/GOR-9 to /home/phi/PROJECTS/phiarchitect/GOR-9
and leave a symlink at /home/phi/Sessions/GOR-9 so both paths resolve cleanly.
"""

from pathlib import Path
import shutil

SRC = Path("/home/phi/Sessions/GOR-9")
DST = Path("/home/phi/PROJECTS/phiarchitect/GOR-9")


def main() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    if SRC.exists() and not SRC.is_symlink():
        if DST.exists():
            shutil.rmtree(DST)
        shutil.move(str(SRC), str(DST))
        SRC.symlink_to(DST)
        print(f"Moved {SRC} -> {DST} and created symlink {SRC} -> {DST}")
    else:
        print(f"Already at {DST}")


if __name__ == "__main__":
    main()
