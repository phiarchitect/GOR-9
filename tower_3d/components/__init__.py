"""
Modular 3D Component Library for the GOR-9 Deep-Space Lighthouse & Broadcast Station
====================================================================================
Each component builds a distinct architectural or studio layer in IngeTrazo 0.6.0:
  - primitives: Shared geometry primitives, UV texture fitting, and materials
  - terrain_basalt: Vast prismatic basalt summit promontory & horizon crags
  - base_infrastructure: Keeper's Habitat, Dilithium Reactor #2, Van Allen Switchyard, Cryo/Winch
  - tower_structure: Continuous 86.5m steel lattice tower, pressurized climb tube, and EVA caged climb spine
  - booth_architecture: Cantilevered octagonal broadcast booth (+26.0m), catwalk, windows, roof beacon
  - consoles: 7 standup-height (+1.05m) perimeter console bays tucked under the window sills (+1.56m)
  - furniture_props: 3 tall rolling broadcast stools, articulated boom mic, eQSL card, logbook, Morse key
  - marzelvane_emitters: 4 concentric Marzelvane Emitter rings (+72.0m) and Cherenkov Spire (+86.5m)
"""

from .primitives import BOOTH_Z, MARZEL_Z, MATERIALS, SPIRE_TOP_Z
from .terrain_basalt import build_prismatic_basalt_terrain
from .base_infrastructure import build_base_infrastructure
from .tower_structure import build_continuous_tower_and_spine, tower_half_width
from .booth_architecture import build_octagonal_booth
from .consoles import CONSOLE_BAY_SPECS, build_perimeter_consoles, build_single_perimeter_console
from .furniture_props import build_furniture_and_props, build_rolling_broadcast_stool
from .marzelvane_emitters import RING_RADII, build_marzelvane_emitters
from .celestial_sphere import (
    az_el_to_equirect_uv,
    az_el_to_xyz,
    build_celestial_beacons,
    generate_celestial_maps,
    load_celestial_catalog,
)
from .asteroids_satellites import (
    build_companion_boulders,
    build_orbital_satellites,
    build_tumbling_asteroids,
)

__all__ = [
    "BOOTH_Z",
    "MARZEL_Z",
    "SPIRE_TOP_Z",
    "MATERIALS",
    "RING_RADII",
    "CONSOLE_BAY_SPECS",
    "tower_half_width",
    "build_prismatic_basalt_terrain",
    "build_base_infrastructure",
    "build_continuous_tower_and_spine",
    "build_octagonal_booth",
    "build_perimeter_consoles",
    "build_single_perimeter_console",
    "build_furniture_and_props",
    "build_rolling_broadcast_stool",
    "build_marzelvane_emitters",
    "az_el_to_equirect_uv",
    "az_el_to_xyz",
    "build_celestial_beacons",
    "generate_celestial_maps",
    "load_celestial_catalog",
    "build_companion_boulders",
    "build_tumbling_asteroids",
    "build_orbital_satellites",
]

