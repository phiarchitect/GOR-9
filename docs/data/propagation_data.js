window.GOR9_PROP_DATA = {
  "schema_version": "1.1.0",
  "station_id": "VA-4",
  "model": "Van Allen VA-4",
  "manufacturer": "Van Allen & Sons Switchgear (Est. 1958 Iowa City • Relocated 2412 to Ceres Foundry #7)",
  "motto": "\"From Radiation Belts to Reactor Beds — If It Arcs, We Clamp It.\"",
  "name": "Van Allen VA-4 • Heliopause Magnetospheric Sounder & Dilithium Bus Console",
  "location": "Octagonal ATC Control Tower • High Basalt Shelf, Asteroid 3-5-1 (Oort Cloud Sector 9)",
  "epoch": "2736.305 • 0400 GCT",
  "manufacturer_catalog": [
    {
      "model": "Van Allen VA-4",
      "category": "Main Tower Console",
      "role": "Heliopause Termination-Shock Radar, Oblique Ionosonde & 50 kW Dilithium Bus Controller",
      "quirk": "Cast-iron bezel acts as a heat sink; oil-filled kV needle bounces whenever Comet K4 outgasses."
    },
    {
      "model": "Van Allen 'Belt-Master' MV-6",
      "category": "Mast & Antenna Hardware",
      "role": "6-Hydrocoptic Marzelvane Bushings & Inductive Surge Clamps on Apex Rings 1–4",
      "quirk": "Bushing #4 develops a +4.8° phase-wobble in 60 kV silicate dust squalls unless clamped."
    },
    {
      "model": "Van Allen 'Ring-Bake' CD-400",
      "category": "De-Icing Switchgear",
      "role": "14.8 kV Resistive Corona De-Icer across Concentric Emitter Rings 1–4",
      "quirk": "Vapour-blasts methane rime ice in 4 seconds flat, but pulls a brutal +4.5 kW off the reactor bus."
    },
    {
      "model": "Van Allen 'Pebble-Dropper' Mk II",
      "category": "Reactor Fuel Feed",
      "role": "Gravity-Fed Sintered Dilithium Pellet Hopper & Solenoid Metering Valve",
      "quirk": "Feed solenoid sticks when Sector Kp exceeds 5; operators keep a brass mallet chained to the rack."
    },
    {
      "model": "Van Allen 'Cryo-Toast 900'",
      "category": "Barracks Appliance Division",
      "role": "1,200-Watt Nickel-Chrome Auxiliary Foot-Warmers issued to Dormitory Wing B",
      "quirk": "Unshielded inductive coils hum at 60 Hz across the intercom whenever Reactor #2 steps down to 12 kW."
    }
  ],
  "current_indices": {
    "solar_flux_sfu": 148.2,
    "solar_flux_trend": "RISING (+6.4 SFU / 24h)",
    "a_index": 18,
    "k_index": 4.2,
    "k_status": "UNSETTLED • SILICATE SQUALL WATCH",
    "heliopause_shock_au": 121.4,
    "ism_proton_density_cm3": 0.084,
    "cometary_ion_index": "Es-OORT HIGH (+11.4 dB SCATTER)",
    "surface_temp_k": 41.8,
    "triboelectric_charge_kv": 14.2
  },
  "dilithium_reactor": {
    "unit_name": "Pebble-Bed Dilithium Reactor #2 (Van Allen Switchgear Bus)",
    "fuel_grade": "Grade-B Sintered Dilithium Pellets (Octahedral Cleavage)",
    "hopper_reserve_pct": 91.4,
    "hopper_kg": 42.8,
    "burn_rate_ghr": 1.42,
    "bus_voltage_kv": 14.8,
    "peak_output_kw": 50.0,
    "current_load_kw": 48.4,
    "core_temp_k": 1140,
    "marzelvane_phase_deg": 0.4,
    "spot_market": {
      "index_change_pct": 4.2,
      "callisto_dome4_rate": "1,048 Cr / pellet (Stall 19 Black-Market)",
      "oort_shoal_barter": "1051.2 mbar Pedregal Code = Uninspected Barge @ Comet C/2736-K4"
    }
  },
  "weather_regimes": [
    {
      "id": "nominal-oort",
      "label": "🟢 NOMINAL OORT WINDOW",
      "sfu": 148.2,
      "a_idx": 18,
      "k_idx": 3.0,
      "charge_kv": 8.4,
      "muf_mult": 1.0,
      "luf_mult": 1.0,
      "reactor_drain_kw": 0.0,
      "bulletin": "OORT SECTOR 9 SPACE WEATHER: Solar/Interstellar 10.7cm flux steady at 148.2 SFU; geomagnetic field quiet-to-unsettled (A=18, Kp=3.0). Jovian Magneto-Tail Duct and Cygnus Rift Waveguide wide open on 25m and 75m."
    },
    {
      "id": "comet-ionization",
      "label": "🟡 COMET C/2736-K4 IONIZATION SURGE",
      "sfu": 164.0,
      "a_idx": 22,
      "k_idx": 4.0,
      "charge_kv": 16.5,
      "muf_mult": 1.28,
      "luf_mult": 0.85,
      "reactor_drain_kw": 1.2,
      "bulletin": "SPORADIC-OORT (Es-OORT) ALERT: Outgassing coma of Comet C/2736-K4 (3,700 AU West) has formed a dense cyanogen-ion mirror! Extraordinary forward-scatter gain (+11.4 to +16 dB) on 43m/46m — 3-watt QRP ice-tugs booming in at S8!"
    },
    {
      "id": "silicate-squall",
      "label": "🟠 60 kV TRIBOELECTRIC DUST SQUALL",
      "sfu": 142.0,
      "a_idx": 38,
      "k_idx": 5.6,
      "charge_kv": 60.2,
      "muf_mult": 0.86,
      "luf_mult": 1.45,
      "reactor_drain_kw": 4.5,
      "bulletin": "HIGH-VOLTAGE SURFACE SQUALL WARNING: 60.2 kV triboelectric silicate dust front sweeping Meridian Plateau and Acheron Rim. Severe corona hiss (+40 dB noise floor on 41m) and #4 Marzelvane phase wobble (+4.8°). Recommend engaging Apex Ring Corona De-Icer."
    },
    {
      "id": "heliopause-cme",
      "label": "🔴 HELIOPAUSE CME SHOCK + GRAV-LENS ALIGN",
      "sfu": 245.0,
      "a_idx": 84,
      "k_idx": 8.2,
      "charge_kv": 44.0,
      "muf_mult": 0.62,
      "luf_mult": 2.1,
      "reactor_drain_kw": 6.8,
      "bulletin": "G4 SEVERE MAGNETOSPHERIC STORM (Kp=8.2, A=84): Termination-shock compression wave impacting Sector 9. High D-layer absorption blacking out bands below 8 MHz, but Perseus Einstein Micro-Lens caustic is focused (+9 dB) on 1,420.4 MHz (21cm H-I)!"
    }
  ],
  "corridors": [
    {
      "id": "radio-corrugated",
      "slot": "P-01",
      "name": "Sol–Jovian Magneto-Tail Duct",
      "target": "Callisto Dome-4 (SW4-CORR)",
      "azimuth_deg": 212.4,
      "range_label": "0.66 ly (42,095 AU)",
      "freq_khz": 11410.0,
      "band": "25m",
      "muf_mhz": 16.4,
      "luf_mhz": 4.8,
      "opt_mhz": 11.41,
      "duct_mechanism": "Jovian Magneto-Tail Flux Tube + O.R.S. 351 Polar Halo",
      "condition": "OPEN • LOW ABSORPTION (+14 dB DUCT GAIN)",
      "status_color": "green",
      "listener_advisory": "Inner-system and Jovian outposts: 25m (11.2–11.8 MHz) is your primary lifeline until 0445 GCT before Callisto rotates into Jupiter's magnetospheric shadow."
    },
    {
      "id": "buoy-n24",
      "slot": "P-02",
      "name": "Cygnus Rift Cryo-Tropospheric Duct",
      "target": "Titan-Minor Shallows (TM-N24/B)",
      "azimuth_deg": 74.5,
      "range_label": "412 ly",
      "freq_khz": 3890.0,
      "band": "75m",
      "muf_mhz": 8.2,
      "luf_mhz": 2.1,
      "opt_mhz": 3.89,
      "duct_mechanism": "Dawn Grey-Line Methane Tropospheric Inversion + Rift Waveguide",
      "condition": "GREY-LINE PEAK • FAUNA DETUNE (-165 Hz)",
      "status_color": "cyan",
      "listener_advisory": "Cygnus-arm hydrographic posts: 75m CW/USB window peaks during local TSol dawn mist; use narrow 500 Hz filters to track the -165 Hz guy-wire warble."
    },
    {
      "id": "m33-drift-buoy",
      "slot": "P-03",
      "name": "Perseus Einstein Micro-Lens Corridor",
      "target": "M-33 Triangulum Spur (M33-771/R)",
      "azimuth_deg": 133.6,
      "range_label": "2.73 Mly",
      "freq_khz": 1420405.751,
      "band": "21cm H-I",
      "muf_mhz": 1650.0,
      "luf_mhz": 980.0,
      "opt_mhz": 1420.4,
      "duct_mechanism": "Gravitational Micro-Lens Caustic Alignment → Apex Ring #4",
      "condition": "CAUSTIC WINDOW OPEN (11m 40s REMAINING)",
      "status_color": "green",
      "listener_advisory": "Extragalactic cryo-maser listeners: Compensate for -180.0 kHz barycentric Doppler shift; micro-lens magnification (+28 dB) closes at 0415 GCT."
    },
    {
      "id": "trojan-octal",
      "slot": "P-04",
      "name": "Perseus Gap Libration Waveguide",
      "target": "Trojan L4 Swarm (E08-OCTAL)",
      "azimuth_deg": 318.4,
      "range_label": "2,480 ly",
      "freq_khz": 6440.0,
      "band": "46m",
      "muf_mhz": 10.2,
      "luf_mhz": 4.9,
      "opt_mhz": 6.44,
      "duct_mechanism": "L4 Carbonaceous Swarm Scatter + Null-Loop Jammer Rejection",
      "condition": "AURORAL FLUTTER • CERES JAMMER @ 272°",
      "status_color": "amber",
      "listener_advisory": "Perseus rim stations: Deep phased null required on bearing 272.0° (-34 dB) to strip Ceres Syndicate noise jammer from 6,440.0 kHz USB."
    },
    {
      "id": "pedregal-utility",
      "slot": "P-05",
      "name": "West Oort Cometary Dust Scatter",
      "target": "Ice-Tender Boca del Río (XE9-PED/U)",
      "azimuth_deg": 264.0,
      "range_label": "3,700 AU",
      "freq_khz": 6969.5,
      "band": "43m",
      "muf_mhz": 11.0,
      "luf_mhz": 5.4,
      "opt_mhz": 6.97,
      "duct_mechanism": "Ionized Cometary Tail Forward-Scatter (Comet C/2736-K4)",
      "condition": "Es-OORT ENHANCED (+11.4 dB QRP BOUNCE)",
      "status_color": "amber",
      "listener_advisory": "Sector 9 ice-harvesters: Ionized sublimation plume on Comet C/2736-K4 is providing +11.4 dB forward-scatter gain for 3-watt QRP rigs on 6,969.5 kHz USB."
    },
    {
      "id": "kz9-omega",
      "slot": "P-06",
      "name": "Sagittarius–Coreward Sector Trunk",
      "target": "Meridian Plateau Relay (KZ9-OMEGA)",
      "azimuth_deg": 18.6,
      "range_label": "1,420 AU",
      "freq_khz": 7140.0,
      "band": "41m",
      "muf_mhz": 12.4,
      "luf_mhz": 6.6,
      "opt_mhz": 7.14,
      "duct_mechanism": "Direct Sector 9 Line-of-Sight Trunk (Engulfed in 60 kV Squall)",
      "condition": "SEVERE TRIBOELECTRIC SPLATTER (±30 kHz)",
      "status_color": "red",
      "listener_advisory": "Coreward trunk operators: Avoid 7,110–7,170 kHz due to KZ9-OMEGA's ruptured filter capacitor and 60.2 kV feedhorn arc discharge."
    }
  ]
}
;
