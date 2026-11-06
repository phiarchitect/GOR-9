window.GOR9_STATIONS_DATA = {
  "schema_version": "2.2.0",
  "station_meta": {
    "callsign": "GOR-9",
    "name": "Galactic Outpost Radio",
    "motto": "Your eye to the cosmos, ear to the vacuum.",
    "location": "High Basalt Shelf (88.4° S Rotational Pole), Asteroid 3-5-1, Oort Cloud Sector 9",
    "distance_sol_au": 42100,
    "galactic_coords": {
      "arm": "Orion–Cygnus Spur (Outer Oort Frontier)",
      "gal_lon_deg": 0.0,
      "gal_lat_deg": 0.0,
      "dist_sgr_a_kpc": 8.12,
      "pulsar_ref": {
        "name": "PSR B1937+21 (Vulpecula Metronome)",
        "gal_lon_deg": 57.51,
        "gal_lat_deg": -0.29,
        "distance_ly": 11700
      }
    },
    "carrier_khz": 14285.7,
    "carrier_mode": "USB",
    "broadcast_time_gct": "0400 GCT",
    "clock_standard": "PSR B1937+21 (641.928262 Hz Vulpecula Pulsar Barycentric Lock)",
    "power_plant": {
      "primary": "Pebble-Bed Dilithium Reactor #2",
      "fuel": "Grade-B Dilithium Pellets (Oort Spot Index +4.2%)",
      "peak_output_kw": 50.0,
      "night_stepdown_kw": 12.0,
      "pellet_reserve_pct": 91.4,
      "bus_voltage_kv": 14.8
    },
    "consoles": [
      {
        "id": "HAUSER-MK4",
        "name": "Hauser MK-IV Wideband DX Correlator",
        "role": "Primary Deep-Space Signal Receiver, Preset Synthesizer, Galactic Astrometry Vector Scope, Live Video/Audio Demodulator & In-Stream SSTV QSL Decoder"
      },
      {
        "id": "PROP-IV",
        "name": "Oort Magnetospheric & Interstellar Propagation Station",
        "role": "360° Sector 9 Polar Radar, Solar/Interstellar Flux (SFU), K-Index, Cometary Tail Ionization & Relay Phaser Diagnostics"
      },
      {
        "id": "EUCLID-9",
        "name": "Euclid-9 Sub-Noise Geometric Discriminator",
        "role": "Scans carrier phase-noise and planetary surface feeds for non-random Euclidean constructions (G-Index)"
      }
    ],
    "triangulation_baseline": {
      "origin": "Asteroid 3-5-1 (GOR-9 High Basalt Shelf • Oort Sector 9)",
      "primary_star": {
        "id": "sol-oort-star",
        "name": "Sol (G2V Primary)",
        "az_deg": 212.4,
        "local_el_deg": 22.4,
        "distance_au": 42100.0,
        "apparent_mag": -3.62
      },
      "foundry_anchor": {
        "id": "ceres-foundry-7",
        "name": "Ceres Foundry #7 (CFS-7 Dwarf Planet Hub)",
        "az_deg": 272.0,
        "local_el_deg": 14.6,
        "distance_au": 1840.0,
        "apparent_mag": 0.4
      },
      "pulsar_clock": {
        "id": "psr-b1937",
        "name": "PSR B1937+21 (Vulpecula Metronome)",
        "az_deg": 57.5,
        "local_el_deg": 24.8,
        "distance_ly": 11700.0,
        "freq_hz": 641.928262
      }
    }
  },
  "presets": [
    {
      "id": "radio-corrugated",
      "preset_slot": "P-01",
      "featured_prototype": true,
      "callsign": "SW4-CORR",
      "name": "Radio Corrugated",
      "subtitle": "Callisto Dome-4 Night Market Pirate Broadcaster",
      "category": "Unlicensed Market Pirate",
      "status": "LOCKED • LIVE VIDEO + AUDIO",
      "status_color": "amber",
      "origin": {
        "body": "Callisto Dome-4 (Sol-Jovian Corridor via Oort Gate)",
        "site": "Dome-4 Sub-Level 3 Corrugated Roofline",
        "coordinates": "14.2° N, 112.8° W (Callisto Synodic Grid)",
        "distance": "0.66 Light-Years (42,095 AU • Coreward Sol Bearing)",
        "local_clock": "J-Dome Synodic (21:46:01 Local / 0400 GCT)"
      },
      "galactic": {
        "sector": "Orion Spur • Sol-Jovian Coreward Corridor",
        "arm": "Orion–Cygnus Spur",
        "azimuth_deg": 212.4,
        "elevation_deg": -4.2,
        "range_ly": 0.665,
        "range_label": "0.66 ly (42,095 AU)",
        "radial_norm": 0.36,
        "relay_nodes": [
          {
            "name": "Jovian Magneto-Tail Duct",
            "az_deg": 210.0,
            "el_deg": 18.8,
            "r_norm": 0.24,
            "range_label": "42,090 AU (Jovian Flux Tube)",
            "role": "+14 dB Magnetospheric Waveguide",
            "xyz_unit": [
              -0.4733,
              -0.8198,
              0.3223
            ]
          },
          {
            "name": "O.R.S. 351 Polar Halo",
            "az_deg": 176.0,
            "el_deg": 17.0,
            "r_norm": 0.11,
            "range_label": "42.8 km (Local Halo Orbit)",
            "role": "Near-Field Polar Relay Transponder",
            "xyz_unit": [
              0.0667,
              -0.954,
              0.2924
            ]
          }
        ],
        "local_el_deg": 17.2,
        "xyz_unit": [
          -0.5119,
          -0.8066,
          0.2957
        ],
        "sep_sol_deg": 5.2,
        "sep_ceres_deg": 57.2,
        "sep_psr_deg": 131.4,
        "booth_window": "South-West Coreward Window (Sol–Jovian Duct)",
        "triangulation": {
          "ceres_dist_label": "41,088 AU",
          "ceres_sep_deg": 57.2,
          "sol_sep_deg": 5.2,
          "psr_sep_deg": 131.4,
          "baseline_parallax": "2.16° (129.4')",
          "booth_window": "South-West Coreward Window (Sol–Jovian Duct)"
        }
      },
      "rf": {
        "frequency_khz": 11410.0,
        "measured_khz": 11410.042,
        "doppler_hz": 42.0,
        "band": "25m SWBC / Oort Relay Duct",
        "mode": "AM-W",
        "filter_bw_hz": 6000,
        "tx_power_watts": 350,
        "tx_power_label": "350 W (Unlicensed Sodium-Lamp Bus Tap)",
        "antenna": "Half-Wave Galvanized Pipe Dipole (Torch-Soldered Live)",
        "relay_path": "Via O.R.S. 351 Polar Halo + Jovian Magneto-Tail Duct",
        "sinpo": {
          "s": 4,
          "i": 3,
          "n": 4,
          "p": 3,
          "o": 4
        },
        "s_meter": "S9+18 dB",
        "s_meter_pct": 86,
        "hauser_index": "Q-8.4",
        "peak_modulation_db": "+18.4 dB [BLOWTORCH SPIKE]",
        "dx_shorthand": [
          "OSOB",
          "PIRATE",
          "TORCH-MOD",
          "QSL CONFIRMED"
        ]
      },
      "hardware_dossier": {
        "transmitter": "Modified surplus Callisto Ice-Harvester PA deck (2x ceramic tetrodes in Class-C AM plate modulation), tapping 440V three-phase power off the Dome-4 streetlamp transformer after 2100 J-Dome time.",
        "feedline_anomaly": "High standing-wave ratio (SWR 3.8:1) due to noodle-stall grease condensation on the open-wire feeder. At 0401:18 GCT, station engineer climbed onto the corrugated arch with an oxy-acetylene blowtorch to braze the center insulator while the transmitter remained at full carrier—producing an 18.4 dB plasma-arc overmodulation spike heard all the way to the Oort Cloud.",
        "receive_antenna_at_gor9": "High Basalt Shelf 4-Ring Apex Phased Array (Beam 212.4°)"
      },
      "media": {
        "video_src": "assets/clips/radio_corrugated_blowtorch.mp4",
        "poster_src": "assets/plates/qsl_plate_radio_corrugated.jpg",
        "alt_plate_src": "assets/plates/qsl_plate_radio_corrugated_kiss.jpg",
        "cam_id": "CAM-104 • CALLISTO DOME-4 SEC FEED",
        "hud_banner": "PEAK OVERMODULATION: +18.4 dB [BLOWTORCH ON DIPOLE]",
        "audio_intercept_src": "assets/audio/intercept_radio_corrugated.wav",
        "interval_signal_src": "assets/audio/is_radio_corrugated.wav",
        "sstv_burst_src": "assets/audio/sstv_radio_corrugated.wav",
        "interval_signal_name": "Electric Night-Market Lute & Wok-Bell 5-Tone Loop",
        "languages": [
          "Port-Cantonese",
          "Mandarin",
          "Jovian Dock Patois"
        ],
        "transcript_excerpt": "[Warbling pentatonic electric lute] ... 'Aquí Radio Corrugated, eleven-four-ten on your dial! Fresh broth at Stall 19, docking bay three customs sweep delayed—hold the ladder, Chen, I'm hitting the center insulator with the torch—' [CRACKLING PLASMA ARC +18.4 dB]",
        "qsl_plate_src": "assets/plates/qsl_plate_radio_corrugated.jpg",
        "qsl_plate_b_src": "assets/plates/qsl_plate_radio_corrugated_kiss.jpg",
        "flow_plates": [
          "assets/plates/flow_callisto_market_architecture.jpg",
          "assets/plates/qsl_plate_radio_corrugated.jpg",
          "assets/plates/qsl_plate_radio_corrugated_kiss.jpg"
        ]
      },
      "qsl": {
        "qsl_number": "QSL #0165-RC",
        "gif_src": "assets/qsl/qsl_radio_corrugated.gif",
        "protocol": "SSTV-ROBOT24 / SUB-AUDIBLE FSK STAMP (1,900 Hz)",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0401 GCT",
        "motto": "SOLDER HOT, BROTH HOTTER — NO ROMANCE WITHOUT DILITHIUM",
        "signer": "Eng. Chen 'Torch' Wei, Chief RF & Noodle Operator",
        "collector_tier": "TIER I • UNLICENSED BLOWTORCH EDITION (#14 of 351)",
        "verification_hash": "0x8F4E-11410-CORR-G47",
        "embedded_clue": "Frame 7 arc-flash duration encodes octal group [3-5-1 / 0-4-7] in sub-carrier phase shift."
      },
      "decoder": {
        "has_live_video": true,
        "default_view": "video",
        "signal_type": "AM-W VOICE + SUB-AUDIBLE 1.9 kHz FSK ARC TELEMETRY",
        "spectrum_style": "am_torch",
        "required_algorithm": "ALG-03",
        "algorithm_name": "ALG-03 • JOVIAN DOCK PATOIS & SUB-CARRIER ARC TRANSLATOR",
        "morse_stream": "-.-. --- .-. .-. / .---- .---- ....- .---- ----- / .- .-. -.-. / ...-- ..... .----",
        "raw_rx_lines": [
          "04:01:12.04  AM-CARRIER: 11,410.042 kHz • 60Hz SODIUM BALLAST HUM (-24 dBc)",
          "04:01:14.80  PATOIS-RX : 'Hoi Stall 19! Ngoh dei gaan-dok Bay 3 customs sweep迟咗!'",
          "04:01:18.22  PLASMA-ARC: [SWR 3.8:1 -> 1.1:1] +18.4 dB TORCH BRAZE OVERMODULATION",
          "04:01:19.90  FSK-1900Hz: SUB-BAND OCTAL BURST [0351 : 0047 : 0312] EJECTED"
        ],
        "translated_lines": [
          "[TRANSLATED PATOIS]: 'Stall 19 broth is hot! Docking Bay 3 customs sweep delayed 40 minutes!'",
          "[HARDWARE EVENT]: Eng. Chen brazed live dipole insulator with oxy-acetylene torch (+18.4 dB spike)",
          "[DECODED SUB-CARRIER]: Plasma arc duration modulated 1,900 Hz FSK with Octal [351 • 047]",
          "[CROSS-REFERENCE]: Group 047 matches Trojan L4 Cipher -> Euclid Prop I.34 (Parallelogram Bisection)"
        ],
        "telemetry_metrics": [
          {
            "label": "FEEDLINE SWR",
            "value": "3.8 → 1.2",
            "unit": "LIVE TORCH BRAZE",
            "pct": 78,
            "alert": true
          },
          {
            "label": "ARC MODULATION",
            "value": "+18.4 dB",
            "unit": "PLASMA OVERMOD",
            "pct": 94,
            "alert": true
          },
          {
            "label": "BALLAST HUM",
            "value": "60.0 Hz",
            "unit": "440V STREETLAMP TAP",
            "pct": 60,
            "alert": false
          },
          {
            "label": "SUB-FSK BAUD",
            "value": "150 Bd",
            "unit": "1,900 Hz TONE SHIFT",
            "pct": 52,
            "alert": false
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0401 GCT",
          "entry": "** CALLISTO DOME-4 [non-Oort]. 11410.042 AM, Epoch 2736.305 at 0401 GCT, unlicensed noodle-market broadcaster 'Radio Corrugated' S9+18 dB via Jovian magneto-duct into Oort Sector 9 (Az 212.4°); warbling night-market lute and rapid port chatter in Cantonese/Patois, peaking +18.4 dB right as their engineer hit the rooftop dipole center-insulator with an oxy-acetylene blowtorch. Unsolicited animated eQSL #0165-RC decoded in sub-band FSK tail! (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.298",
          "gct": "0354 GCT",
          "entry": "** CALLISTO DOME-4. 11410.038 AM, Epoch 2736.298 at 0354 GCT, JBA carrier with heavy 60-Hz sodium-ballast hum until streetlamps dimmed at 0358; S7 music and stall ads, but cut off abruptly at 0412 when harbor patrol swept Sub-Level 3 (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.284",
          "gct": "0405 GCT",
          "entry": "** CALLISTO DOME-4. 11409.985 AM, Epoch 2736.284 at 0405 GCT, first tentative log of this unlicensed market rig drifting +57 Hz upward as the tetrode PA warmed up; OM announcer reading black-market Grade-B Dilithium barter rates between noodle orders. SINPO 3-3-3-2-3 (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ],
      "station_folder": "sw4-corr_radio-corrugated",
      "characters": [
        {
          "name": "Chen 'Torch' Wei (陳偉)",
          "role": "Chief RF Engineer, Rooftop Brazier & Co-Host",
          "species_or_type": "Human (3rd-Gen Callisto Dome Dockworker)",
          "languages": "Port-Cantonese, Mandarin, Jovian Dock Patois",
          "dialect_notes": "Rapid-fire Cantonese syntax peppered with Russian/Spanish airlock slang and vacuum-tube part numbers.",
          "voice_profile": {
            "tts_voice": "Fenrir (Pitch +2st, Brisk Energetic)",
            "cadence": "165 WPM, laughing over sizzling broth & 60 Hz transformer hum",
            "dsp_chain": "300–2800 Hz AM-Wide bandpass + +18.4 dB plasma arc clipping"
          },
          "signature_quote": "Hold the mic, Mei-Ling—give me a kiss for luck before I hit the center insulator with the oxy-torch!",
          "bio": "Former Ganymede ice-harvester radar technician who runs Stall 19 ('Hand-Pulled Beef Broth & Surplus Tetrodes') with his partner Mei-Ling. Built Radio Corrugated out of a salvaged ice-harvester PA deck tapping 440V off the municipal sodium streetlamps after 2100 local time.",
          "slug": "chen_torch_wei",
          "headshot_src": "assets/characters/char_chen_torch_wei_headshot.jpg",
          "fullbody_src": "assets/characters/char_chen_torch_wei_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_chen_torch_wei_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_chen_torch_wei_rf.wav",
          "language_sample_transcript": "Wei! Callisto Dome-Four Night Market, Stall Nineteen on eleven-four-ten kilohertz! Hao le, Ah-Mei, pass me the silver-copper brazing rod—watch the plate current climb eighteen decibels when I touch the torch to the radiator!",
          "phonetic_and_conlang_notes": "Callisto Dome-4 Dock Patois: blends Cantonese/Mandarin night-market exclamations ('Wei!', 'Hao le!') with vacuum-tube RF slang."
        },
        {
          "name": "Mei-Ling Lin (林美玲)",
          "role": "Night-Market Announcer, Contraband Price Ticker & Co-Host",
          "species_or_type": "Human (Callisto Dome-4 Native)",
          "languages": "Port-Cantonese, English, Mandarin, Jovian Dock Patois",
          "dialect_notes": "Musical, conspiratorial late-night DJ delivery; switches seamlessly between soup specials, romance dedications, and customs patrol warnings.",
          "voice_profile": {
            "tts_voice": "Kore / Aoede (Warm, Nimble, Conspiratorial)",
            "cadence": "155 WPM with electric night-market lute backing",
            "dsp_chain": "AM plate-modulation warmth + selective ionospheric fade"
          },
          "signature_quote": "Aquí Radio Corrugated, eleven-four-ten on your dial! Fresh broth at Stall 19, and no romance without Dilithium!",
          "bio": "Co-founder of Radio Corrugated and Chen's partner on the corrugated rooftop. Curates the station's legendary pentatonic electric-lute tapes and encodes black-market Grade-B Dilithium barter rates into the nightly noodle menu.",
          "slug": "ah_mei_zhou",
          "headshot_src": "assets/characters/char_ah_mei_zhou_headshot.jpg",
          "fullbody_src": "assets/characters/char_ah_mei_zhou_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_ah_mei_zhou_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_ah_mei_zhou_rf.wav",
          "language_sample_transcript": "Lai la, lai la! Fresh star-anise bone broth and hand-pulled noodles at Stall Nineteen! Chen Wei, put down that plasma torch before you splatter twenty kilohertz across the whole market—come kiss the chef first!",
          "phonetic_and_conlang_notes": "Musical night-market vendor cadence ('Lai la, lai la!') with warm domestic banter over sizzling broth."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "Sub-Level 3 of Callisto Dome-4 is a labyrinth of wet corrugated-iron roofs, venting steam pipes, and neon noodle stalls where independent tug crews trade contraband vacuum tubes and dodge Jovian Authority customs sweeps.",
        "spectrum_gimmick_title": "Live Blowtorch Plasma-Arc Overmodulation (+18.4 dB) & Rooftop Romance",
        "hauser_commentary": "Callisto Dome-4 on 11410.042—drifting up 42 Hz every time downstairs fires up the noodle cauldron. Co-hosts Chen and Mei-Ling reading docking-bay contraband prices until 0401, when the carrier jumped 18 dB in a violent plasma buzz right as Chen hit the dipole center-insulator with his blowtorch and kissed Mei-Ling on the roof.",
        "qsl_postcard_style": "Pirate Couple Rooftop Snapshot Postcard (inspired by Radio Andorra & Voice of Pancho Villa)",
        "qsl_animation_notes": "2-frame Kodachrome action sequence: Chen and Mei-Ling grin with the blowtorch and noodle bowl, then lean in and kiss on the rooftop while the blowtorch erupts in a cyan-white plasma arc against the copper dipole!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Caught S9+18 dB blowtorch spike at 0401 GCT as Chen brazed the live rooftop dipole and kissed Mei-Ling; decoded octal group [351 • 047] in the arc's sub-band FSK tail."
          },
          {
            "stage": "Broadcast 02 (The Customs Raid)",
            "summary": "Harbor Patrol cuts power to Sub-Level 3 streetlamps at 0408 GCT; the couple switches to emergency bicycle-dynamo power (18 Watts) while directing listeners to Quarantine Buoy 12."
          },
          {
            "stage": "Broadcast 03 (The Tube Barter)",
            "summary": "Chen and Mei-Ling offer an autographed Tier-I Blowtorch QSL and three crates of pickled radish to whichever outpost smuggles two 811A oscillator tubes past Buoy 12."
          }
        ]
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_callisto_market_architecture.jpg",
          "role": "16:9 Architectural & Street Background Plate (Flow)",
          "caption": "Callisto Dome-4 Sub-Level 3 Night Market canyon beneath rusted geodesic dome arches, steaming noodle stalls, and rooftop copper dipole arrays."
        },
        {
          "src": "assets/plates/qsl_plate_radio_corrugated.jpg",
          "role": "16:9 Character Keyframe A (Flow)",
          "caption": "Chen 'Torch' Wei and Mei-Ling grinning on the corrugated roof with oxy-acetylene blowtorch, vintage chrome mic, and steaming noodle bowl."
        },
        {
          "src": "assets/plates/qsl_plate_radio_corrugated_kiss.jpg",
          "role": "16:9 Character Keyframe B (Flow)",
          "caption": "Chen and Mei-Ling kissing on the rooftop as the blowtorch sparks a +18.4 dB cyan-white plasma arc on the live copper dipole."
        }
      ]
    },
    {
      "id": "buoy-n24",
      "preset_slot": "P-02",
      "featured_prototype": false,
      "callsign": "TM-N24/B",
      "name": "Hydrographic Buoy N-24",
      "subtitle": "Titan-Minor Methane Shallows Automated Tidal Beacon",
      "category": "Automated Hydrographic Utility",
      "status": "NO VIDEO • CW + TELEMETRY",
      "status_color": "cyan",
      "origin": {
        "body": "Titan-Minor (Cygnus-Rift Hydrocarbon Colony Moon)",
        "site": "Kraken North Shallows • Tripod Mooring N-24",
        "coordinates": "64.8° N, 019.4° E (Tidal Grid)",
        "distance": "412 Light-Years (Cygnus Rift Bearing 074.5°)",
        "local_clock": "TSol 14.82 (Dawn Methane Mist / 0400 GCT)"
      },
      "galactic": {
        "sector": "Orion–Cygnus Drift • Kraken Hydrocarbon Basin",
        "arm": "Orion–Cygnus Spur (Spinward)",
        "azimuth_deg": 74.5,
        "elevation_deg": 6.8,
        "range_ly": 412.0,
        "range_label": "412 ly (0.13 kpc)",
        "radial_norm": 0.56,
        "relay_nodes": [
          {
            "name": "Cygnus Rift Waveguide",
            "az_deg": 72.0,
            "el_deg": 15.2,
            "r_norm": 0.34,
            "range_label": "185 ly (Cygnus Ionization Duct)",
            "role": "Cryo-Tropospheric & ISM Duct",
            "xyz_unit": [
              0.9178,
              0.2982,
              0.2622
            ]
          },
          {
            "name": "O.R.S. 351 Polar Halo",
            "az_deg": 102.0,
            "el_deg": 16.4,
            "r_norm": 0.11,
            "range_label": "42.8 km (Local Halo Orbit)",
            "role": "Beverage-to-Booth Phase Feed",
            "xyz_unit": [
              0.9384,
              -0.1995,
              0.2823
            ]
          }
        ],
        "local_el_deg": 10.1,
        "xyz_unit": [
          0.9487,
          0.2631,
          0.1754
        ],
        "sep_sol_deg": 127.5,
        "sep_ceres_deg": 149.8,
        "sep_psr_deg": 21.8,
        "booth_window": "East Chasm Window • Bay 03 (Euclid ED-9 Desk)",
        "triangulation": {
          "ceres_dist_label": "412.03 ly",
          "ceres_sep_deg": 149.8,
          "sol_sep_deg": 127.5,
          "psr_sep_deg": 21.8,
          "baseline_parallax": "7.327\"",
          "booth_window": "East Chasm Window • Bay 03 (Euclid ED-9 Desk)"
        }
      },
      "rf": {
        "frequency_khz": 3890.0,
        "measured_khz": 3889.835,
        "doppler_hz": -165.0,
        "band": "75m Utility / Cryo-Tropospheric Duct",
        "mode": "CW/USB",
        "filter_bw_hz": 2400,
        "tx_power_watts": 85,
        "tx_power_label": "85 W (Strontium-90 RTG Thermocouple)",
        "antenna": "6.4m Vertical Whip with 3 Stainless Guy-Wires",
        "relay_path": "Cygnus Rift Ionospheric Bounce → O.R.S. 351",
        "sinpo": {
          "s": 3,
          "i": 4,
          "n": 3,
          "p": 3,
          "o": 3
        },
        "s_meter": "S7 / S8",
        "s_meter_pct": 64,
        "hauser_index": "Q-7.1",
        "peak_modulation_db": "-165 Hz CARRIER BEND [FAUNA RUB]",
        "dx_shorthand": [
          "SAWA",
          "UTILITY",
          "FAUNA-QRM",
          "85W RTG"
        ]
      },
      "hardware_dossier": {
        "transmitter": "Sealed titanium capsule housing an 85-watt solid-state synthesizer and mechanical brass fog-bell acoustic transducer, powered since 2689 by a Strontium-90 RTG.",
        "feedline_anomaly": "Every local morning at TSol dawn, a herd of tall 4-meter wading silt-striders migrates past Mooring N-24 and rubs their carapace plates against the stainless-steel guy-wires, detuning the vertical whip capacitive hat by -165 Hz.",
        "receive_antenna_at_gor9": "Acheron Chasm 2km North/South Beverage Wire (Az 074.5°)"
      },
      "media": {
        "video_src": "assets/clips/buoy_n24_methane.mp4",
        "poster_src": "assets/plates/flow_n24_onboard_pov_a.jpg",
        "alt_plate_src": "assets/plates/flow_n24_onboard_rub_b.jpg",
        "cam_id": "BUOY TM-N24/B • ONBOARD MASTHEAD CAM POV",
        "hud_banner": "NO VIDEO CARRIER • CW MORSE + METHANE TIDE TELEMETRY",
        "audio_intercept_src": "assets/audio/intercept_buoy_n24.wav",
        "interval_signal_src": "assets/audio/is_buoy_n24.wav",
        "sstv_burst_src": "assets/audio/sstv_buoy_n24.wav",
        "interval_signal_name": "Double Submerged Brass Bell Clank + 880 Hz FSK Pip",
        "languages": [
          "French (Automated Speech ROM)",
          "ITU Morse CW"
        ],
        "transcript_excerpt": "[Metallic buoy bell CLANK] 'VVV DE TM-N24/B... Marée de méthane secteur nord: quatre virgule deux mètres... [CARRIER BENDS DOWNWARD -165 Hz AS SILT-STRIDER RUBS WHIP] ...vent nul...'",
        "qsl_plate_src": "assets/plates/flow_n24_onboard_pov_a.jpg",
        "qsl_plate_b_src": "assets/plates/flow_n24_onboard_rub_b.jpg",
        "flow_plates": [
          "assets/plates/flow_n24_onboard_pov_a.jpg",
          "assets/plates/flow_n24_onboard_rub_b.jpg"
        ]
      },
      "qsl": {
        "qsl_number": "QSL #0089-N24",
        "gif_src": "assets/qsl/qsl_buoy_n24.gif",
        "protocol": "CW-HELLSCHREIBER / FSK RASTER BURST",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0348 GCT",
        "motto": "LA MER DE MÉTHANE NE DORT JAMAIS • 85 WATTS SUR L'HORIZON",
        "signer": "Automated Bureau Hydrographique de Titan-Minor",
        "collector_tier": "TIER II • EXOTIC BEACON EDITION (#42 of 200)",
        "verification_hash": "0x3890-N24B-TSOL-771",
        "embedded_clue": "The -165 Hz guy-wire pitch bend occurs at intervals of 3, 5, and 8 seconds."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "ITU MORSE CW (18 WPM) + FRENCH HYDROGRAPHIC ROM",
        "spectrum_style": "cw_narrow",
        "required_algorithm": "ALG-01",
        "algorithm_name": "ALG-01 • ITU MORSE CW & FRENCH HYDRO-ROM TRANSLATOR",
        "morse_stream": "...- ...- ...- / -.. . / - -- -....- -. ..--- ....- / -- .- .-. . . / ....- .-.-.- ..--- --",
        "raw_rx_lines": [
          "03:48:02.10  CW-KEY : •••— •••— •••—  —•• •  — —— —••••— —• ••——— ••••—  —•••",
          "03:48:04.45  ROM-FR : MAREE DE METHANE SECTEUR NORD: QUATRE VIRGULE DEUX METRES",
          "03:48:07.12  FSK-TLM: [CAP_HAT=159.4pF] Δf = -165.0 Hz (INTERVALS: 3s, 5s, 8s)",
          "03:48:09.80  ROM-FR : DENSITE 0.424 g/cm³ • VENT NUL • BALISE SECOURS 85W SR-90"
        ],
        "translated_lines": [
          "[CW MORSE ID]: 'VVV DE TM-N24/B' — Titan-Minor Mooring N-24 (85W Backup RTG Beacon)",
          "[HYDRO TRANSLATION]: North Sector Liquid Methane Tide = 4.20 meters • Surface Wind = Calm",
          "[TELEMETRY UNPACK]: Capacitive hat detuned -165.0 Hz by 4m Silt-Strider carapace on Guy-Wire #2",
          "[FIBONACCI RUB CADENCE]: Carapace rub intervals [3s, 5s, 8s] confirm natural fauna migration"
        ],
        "telemetry_metrics": [
          {
            "label": "METHANE TIDE",
            "value": "4.20 m",
            "unit": "KRAKEN SHALLOWS",
            "pct": 68,
            "alert": false
          },
          {
            "label": "WHIP DETUNE",
            "value": "-165.0 Hz",
            "unit": "GUY-WIRE FAUNA RUB",
            "pct": 88,
            "alert": true
          },
          {
            "label": "CW KEY SPEED",
            "value": "18.0 WPM",
            "unit": "880 Hz BFO OFFSET",
            "pct": 45,
            "alert": false
          },
          {
            "label": "SR-90 RTG BUS",
            "value": "85.0 W",
            "unit": "BACKUP RIG ACTIVE",
            "pct": 85,
            "alert": false
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0348 GCT",
          "entry": "** TITAN-MINOR [Cygnus Drift]. 3890.0 USB/CW, Epoch 2736.305 at 0348 GCT, Hydrographic Buoy N-24 (Az 074.5°, 412 ly) reciting French methane tide tables at S7/S8, thought to be 1 kW main beacon but confirmed as the 85-watt backup RTG rig! Periodic -165 Hz downward carrier warble whenever migratory silt-striders rub against the guy-wires, detuning the whip antenna (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.292",
          "gct": "0350 GCT",
          "entry": "** TITAN-MINOR. 3890.000 CW, Epoch 2736.292 at 0350 GCT, clean 18 WPM Morse ID 'VVV DE TM-N24/B' and double brass fog-bell clank, zero carrier bend today as the methane tide was high (5.1m) and the silt-strider herd stayed on the southern mudflats (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.275",
          "gct": "0344 GCT",
          "entry": "** TITAN-MINOR. 3889.835 USB, Epoch 2736.275 at 0344 GCT, initially logged as an unstable VFO on 75m utility band before correlating the -165 Hz capacitive detune with local TSol dawn fauna migration on Tripod Mooring N-24 (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ],
      "station_folder": "tm-n24_buoy-n24",
      "characters": [
        {
          "name": "Automate Hydrographique 'Mariette-4'",
          "role": "1980s-Style French Speech-Synthesis Tide ROM",
          "species_or_type": "Solid-State Speech Synthesizer (Installed 2689 GCT)",
          "languages": "French (Formal Maritime Hydrographic Standard) + 18 WPM ITU Morse",
          "dialect_notes": "Clipped, hypnotic LPC-synthesized Parisian French reciting methane tide heights and barometric density.",
          "voice_profile": {
            "tts_voice": "Leda (French Maritime LPC Filter)",
            "cadence": "Measured 115 WPM robotic cadence punctuated by double brass fog-bell clanks",
            "dsp_chain": "LPC formant quantizer + -165 Hz capacitive pitch-bend warble"
          },
          "signature_quote": "VVV DE TM-N24/B... Marée de méthane secteur nord: quatre virgule deux mètres... vent nul...",
          "bio": "Programmed fifty years ago by the colonial Bureau Hydrographique de Titan-Minor and sealed inside a titanium capsule powered by an 85-watt Strontium-90 RTG.",
          "slug": "mariette4_rom",
          "headshot_src": "assets/plates/flow_n24_onboard_pov_a.jpg",
          "fullbody_src": "assets/plates/flow_n24_onboard_rub_b.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_mariette4_rom_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_mariette4_rom_rf.wav",
          "language_sample_transcript": "V-V-V de T-M-N-vingt-quatre barre B. Bureau Hydrographique de Titan-Mineur. Marée de méthane secteur nord: quatre virgule deux mètres. Densité: zéro virgule quatre-deux-quatre. Vent nul.",
          "phonetic_and_conlang_notes": "Formal French Maritime Hydrographic Standard ('Marée de méthane secteur nord') synthesized with LPC formant stepping."
        },
        {
          "name": "The Kraken Shallows Silt-Strider Herd",
          "role": "Bio-Capacitive Antenna Modulators ('The Singing Guy-Wires')",
          "species_or_type": "Indigenous 4-Meter Cryo-Wading Fauna (Strideria krakenensis)",
          "languages": "Bio-Capacitive Theremin Glissandos (-165 Hz Chord Harmonics)",
          "dialect_notes": "Resonant chitinous throat-sacs rubbing directly against warm RF-energized stainless-steel guy-wires at Fibonacci intervals (3s, 5s, 8s).",
          "voice_profile": {
            "tts_voice": "Synthesized Bio-Theremin & Whale-Harmonic Resonator",
            "cadence": "Slow dawn chorus synchronized with local TSol methane low tide",
            "dsp_chain": "Capacitive hat detuning (-165 Hz) + cryo-tropospheric ducting"
          },
          "signature_quote": "[Submerged brass bell CLANK -> haunting -165 Hz three-voice theremin chord]",
          "bio": "Discovering that the 85W RF current warms Mooring N-24's stainless guy-wires by 12°C in the freezing methane mist, the herd gathers every morning so individual striders can rub their long iridescent necks right up against the taut cable—turning the 6.4m whip antenna into an interstellar theremin.",
          "slug": "silt_strider",
          "headshot_src": "assets/characters/char_silt_strider_headshot.jpg",
          "fullbody_src": "assets/characters/char_silt_strider_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_silt_strider_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_silt_strider_rf.wav",
          "language_sample_transcript": "[Bio-Acoustic Call]: Piezoelectric carapace clicks -> 220 Hz throat-sac lagoon resonance -> 880 Hz vocalized Morse mimicry ('VVV' with -165 Hz guy-wire rub bend).",
          "phonetic_and_conlang_notes": "Non-human bio-acoustic communication: combines 1.4 kHz chitinous clicks, 220 Hz methane-lagoon throat-sac calls, and learned 880 Hz ITU Morse mimicry."
        },
        {
          "name": "Dr. Hélène Moreau",
          "role": "QSL Verifier & Field Xenobiologist (Ganymede Trust)",
          "species_or_type": "Human (Xenobiology Trust Archivist)",
          "languages": "French, English",
          "dialect_notes": "Academic, enthusiastic field naturalist who signs the official QSL cards based on listener harmonic counts.",
          "voice_profile": {
            "tts_voice": "Aoede (French-Accented English)",
            "cadence": "135 WPM",
            "dsp_chain": "Clean studio sideband"
          },
          "signature_quote": "Look at the buoy's mast-camera feed: the matriarch is rubbing her neck right against Guy-Wire Number Two!",
          "bio": "Monitors the onboard masthead inspection camera bolted to Buoy N-24 and issues official Bureau Hydrographique telemetry & wildlife QSL cards to DXers who report the herd's seasonal migration.",
          "slug": "solene_moreau",
          "headshot_src": "assets/characters/char_solene_moreau_headshot.jpg",
          "fullbody_src": "assets/characters/char_solene_moreau_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_solene_moreau_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_solene_moreau_rf.wav",
          "language_sample_transcript": "Ici Solène Moreau, station acoustique Kraken-Nord. Listen closely to the hydrophone—the Silt-Strider isn't just rubbing its neck against Guy-Wire Number Two for the warmth. Its throat-sac is singing the buoy's Morse code back to the lagoon!",
          "phonetic_and_conlang_notes": "Bilingual French-Québécois / English scientific field log recorded on portable hydrophone tape."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "Kraken North Shallows on Titan-Minor is a mirror-calm expanse of liquid hydrocarbons shrouded in twilight mist. Because Buoy N-24 is an unstaffed autonomous beacon, the only camera in the shallows is bolted directly to the buoy's own upper steel tripod—looking down past its amber Fresnel lamp and taut stainless guy-wire.",
        "spectrum_gimmick_title": "Biological Capacitive-Hat Theremin (-165 Hz Fauna Guy-Wire Rub)",
        "hauser_commentary": "Titan-Minor on 3890 kilohertz. Automated French tide tables at 0348, followed by that unmistakable downward pitch-bend of 165 Hertz—captured on the buoy's own mast-mounted camera as a Silt-Strider walks right up and rubs its neck against the warm stainless-steel guy-wire!",
        "qsl_postcard_style": "Bureau Hydrographique Onboard Mast-Cam & Telemetry Verification Card",
        "qsl_animation_notes": "Seen from the camera bolted to Buoy N-24 itself: in Frame B, a bioluminescent Silt-Strider walks right up to the foreground guy-wire and rubs its neck against the cable, sending cyan capacitive sparks up the wire as the amber Fresnel lamp flashes!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Logged on 3890 kHz CW/USB; onboard mast-cam confirms a Silt-Strider rubbing directly against Guy-Wire #2, causing -165 Hz pitch bends every 3, 5, and 8 seconds."
          },
          {
            "stage": "Broadcast 02 (The Herd Multiplies)",
            "summary": "Seven Silt-Striders gather during a methane neap tide, detuning the beacon by a full -440 Hz into a minor-seventh chord that triggers GOR-9's Euclidean harmonic detector."
          },
          {
            "stage": "Broadcast 03 (The Mimicry)",
            "summary": "Dr. Moreau confirms the herd has begun vocally mimicking the buoy's 18 WPM Morse ID ('VVV DE TM-N24/B') even when the transmitter steps down!"
          }
        ]
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_n24_onboard_pov_a.jpg",
          "role": "16:9 Onboard Buoy Mast-Cam POV Keyframe A (Flow)",
          "caption": "Shot FROM the camera bolted to Buoy N-24 looking past its own salt-crusted steel bracket, amber Fresnel lamp, and diagonal stainless-steel guy-wire as three Silt-Striders wade across the shallows."
        },
        {
          "src": "assets/plates/flow_n24_onboard_rub_b.jpg",
          "role": "16:9 Onboard Buoy Mast-Cam POV Keyframe B (Flow)",
          "caption": "One of the bioluminescent Silt-Striders walks right up to the foreground stainless-steel guy-wire and physically rubs its neck against the taut cable, triggering a cyan capacitive shimmer and -165 Hz pitch bend!"
        }
      ]
    },
    {
      "id": "m33-drift-buoy",
      "preset_slot": "P-03",
      "featured_prototype": false,
      "callsign": "M33-771/R",
      "name": "Autonomous Sonde M33-771",
      "subtitle": "Deep-Field Industrial Telemetry Sonde (1420 MHz)",
      "category": "Relic Deep-Space Beacon",
      "status": "NO VIDEO • H-I TELEMETRY",
      "status_color": "green",
      "origin": {
        "body": "Veyra-3 Alkali Salt Basin (M-33 Triangulum Spur)",
        "site": "Pelagic & Deep-Field Sonde DS-771-04",
        "coordinates": "Gal Lon 133.6°, Gal Lat -31.3° (RA 01h 33m 50.9s)",
        "distance": "2.73 Million Light-Years (Extragalactic Micro-Lens)",
        "local_clock": "Survey Epoch +712 Yrs (Barycentric Lock)"
      },
      "galactic": {
        "sector": "Extragalactic Local Group • M-33 Triangulum Spur",
        "arm": "Beyond Outer Perseus Rim (Micro-Lens Aperture)",
        "azimuth_deg": 133.6,
        "elevation_deg": -31.3,
        "range_ly": 2730000.0,
        "range_label": "2.73 Mly (837 kpc)",
        "radial_norm": 0.92,
        "relay_nodes": [
          {
            "name": "Perseus Arm Einstein Lens",
            "az_deg": 131.0,
            "el_deg": 6.4,
            "r_norm": 0.68,
            "range_label": "6,400 ly (Perseus Caustic)",
            "role": "+28 dB Gravitational Micro-Lens",
            "xyz_unit": [
              0.75,
              -0.652,
              0.1115
            ]
          },
          {
            "name": "Outer Oort Halo Gate",
            "az_deg": 133.2,
            "el_deg": 11.2,
            "r_norm": 0.28,
            "range_label": "12,400 AU (Sector 9 Rim)",
            "role": "21-cm H-I Phase Correlator",
            "xyz_unit": [
              0.7151,
              -0.6715,
              0.1942
            ]
          }
        ],
        "local_el_deg": 2.8,
        "xyz_unit": [
          0.7233,
          -0.6888,
          0.0488
        ],
        "sep_sol_deg": 78.6,
        "sep_ceres_deg": 135.3,
        "sep_psr_deg": 76.2,
        "booth_window": "South-East Window • Bay 04 (Bogey-9 Trail-Cam)",
        "triangulation": {
          "ceres_dist_label": "2.73 Mly",
          "ceres_sep_deg": 135.3,
          "sol_sep_deg": 78.6,
          "psr_sep_deg": 76.2,
          "baseline_parallax": "1.55 mas (Micro-Lens)",
          "booth_window": "South-East Window • Bay 04 (Bogey-9 Trail-Cam)"
        }
      },
      "rf": {
        "frequency_khz": 1420405.751,
        "measured_khz": 1420225.751,
        "doppler_hz": -180000.0,
        "band": "21cm Neutral Hydrogen Hyperfine Line (H-I)",
        "mode": "H-I FSK",
        "filter_bw_hz": 500,
        "tx_power_watts": 4.2,
        "tx_power_label": "4.2 W (Decay-Mode Americium Trickle Cell)",
        "antenna": "Parabolic Horn Canted 34° in Salt Crust",
        "relay_path": "Gravitational Micro-Lens Corridor → Sector 9 Apex Ring 4",
        "sinpo": {
          "s": 2,
          "i": 5,
          "n": 3,
          "p": 2,
          "o": 3
        },
        "s_meter": "S4 (JBA)",
        "s_meter_pct": 38,
        "hauser_index": "Q-9.6",
        "peak_modulation_db": "DOPPLER DRIFT: -180.0 kHz [LISSAJOUS LOCK]",
        "dx_shorthand": [
          "JBA",
          "OSOB",
          "RELIC-700Y",
          "4.2W QRP"
        ]
      },
      "hardware_dossier": {
        "transmitter": "700-year-old ceramic-cavity maser transponder (Model DS-771 Mk.IV) locked to the 1,420.405 MHz hydrogen line. Its mechanical barometer reed corroded shut centuries ago during a Force-8 gale, locking its telemetry buffer into an eternal storm warning.",
        "feedline_anomaly": "The buoy hull rests high and dry on a baked white polygon salt flat where the ammonia sea evaporated four centuries ago, yet its solar-assisted trickle cell still fires a 4.2-watt packet every 90 seconds.",
        "receive_antenna_at_gor9": "Apex Concentric Ring #4 + Cryo-Maser Preamp (Az 133.6°)"
      },
      "media": {
        "video_src": "assets/clips/m33_drift_buoy.mp4",
        "poster_src": "assets/plates/flow_m33_onboard_cam_a.jpg",
        "alt_plate_src": "assets/plates/flow_m33_onboard_cam_b.jpg",
        "cam_id": "SONDE DS-771-04 • ONBOARD HORIZON CAM POV",
        "hud_banner": "NO VIDEO CARRIER • 21cm H-I SPECTRUM & SONDE TELEMETRY",
        "audio_intercept_src": "assets/audio/intercept_m33_drift.wav",
        "interval_signal_src": "assets/audio/is_m33_drift.wav",
        "sstv_burst_src": "assets/audio/sstv_m33_drift.wav",
        "interval_signal_name": "21-cm Hydrogen Maser Calibration Pip & Barometric Tone",
        "languages": [
          "Barycentric Binary-FSK",
          "Synthetic Telemetry Vocoder"
        ],
        "transcript_excerpt": "[Eerie whistling maser harmonic] 'PACKET M33-771... UNIT DS-771-04... SMALL CRAFT ADVISORY: AMMONIA SEA SECTOR 4... SWELLS 6 METERS... [ACTUAL SEA STATUS: DRY ALKALI SALT CRUST]'",
        "qsl_plate_src": "assets/plates/flow_m33_onboard_cam_a.jpg",
        "qsl_plate_b_src": "assets/plates/flow_m33_onboard_cam_b.jpg",
        "flow_plates": [
          "assets/plates/flow_m33_onboard_cam_a.jpg",
          "assets/plates/flow_m33_onboard_cam_b.jpg"
        ]
      },
      "qsl": {
        "qsl_number": "QSL #0001-M33",
        "gif_src": "assets/qsl/qsl_m33_drift.gif",
        "protocol": "H-I PHASE-SHIFT LISSAJOUS TELEMETRY",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0402 GCT",
        "motto": "BEWARE THE PHANTOM SWELL • 4.2 WATTS ACROSS ETERNITY",
        "signer": "Auto-Acknowledge Telemetry ROM v1.04 (Sonde DS-771-04)",
        "collector_tier": "TIER S • INTERGALACTIC RELIC QSL #1 (#1 of 12)",
        "verification_hash": "0x1420-M33R-DS771",
        "embedded_clue": "Lissajous phase ratio 3:5:1 aligns with the South Rotational Pole of Asteroid 3-5-1."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "21cm H-I BINARY-FSK + DEEP-FIELD SONDE TELEMETRY ROM",
        "spectrum_style": "hi_maser",
        "required_algorithm": "ALG-03",
        "algorithm_name": "ALG-03 • 21-CM H-I FSK & BAROMETRIC SONDE TELEMETRY UNPACKER",
        "morse_stream": "-- ...-- ...-- / -....- --... --... .---- / -.. ... --... --... .---- / -.. .-. -.-- / ... .- .-.. -",
        "raw_rx_lines": [
          "04:02:01.00  H-I FSK : [0x1420:0x0771] Δf = -180.000 kHz • LISSAJOUS RATIO 3:5:1",
          "04:02:03.40  SONDE-ID: [UNIT DS-771-04] VEYRA-3 BASIN • BARO_REED=942.0 mbar (STUCK=1)",
          "04:02:06.15  WX-WARN : FORCE-8 GALE ADVISORY • SWELLS 6.0m • SMALL CRAFT BEWARE",
          "04:02:08.90  SALT-TLM: HULL_TILT=34.2° • MOISTURE_PCT=0.00% • AM241_CELL=4.20W"
        ],
        "translated_lines": [
          "[SONDE ID DS-771-04]: 'Veyra-3 Drift Sonde M33-771 • Barometer reed locked at 942 mbar'",
          "[AUTOMATED GALE WARNING]: 'Ammonia Sea Force-8 Gale • 6-Meter Swells • Small Craft Beware!'",
          "[SENSOR REALITY CHECK]: Moisture = 0.00% (Ammonia sea evaporated centuries ago; hull canted 34° in dry salt)",
          "[GEOMETRIC PHASE CLUE]: Maser Lissajous harmonic ratio [3 : 5 : 1] points directly to Outpost Nine (Asteroid 3-5-1)"
        ],
        "telemetry_metrics": [
          {
            "label": "BAROMETER REED",
            "value": "942 mbar",
            "unit": "REED CORRODED SHUT",
            "pct": 95,
            "alert": true
          },
          {
            "label": "ACTUAL SEA LEVEL",
            "value": "0.00 m",
            "unit": "DRY SALT CRUST",
            "pct": 4,
            "alert": true
          },
          {
            "label": "DOPPLER SHIFT",
            "value": "-180.0 kHz",
            "unit": "M-33 APPROACH",
            "pct": 74,
            "alert": false
          },
          {
            "label": "AM-241 CELL",
            "value": "4.20 W",
            "unit": "700-YR TRICKLE",
            "pct": 42,
            "alert": false
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0402 GCT",
          "entry": "** INTERGALACTIC [M-33]. 1420405.751 H-I (Δf -180 kHz), Epoch 2736.305 at 0402 GCT, JBA S4 carrier on the cryo-maser preamp (Gal Lon 133.6°, Lat -31.3°); 700-year-old drift-buoy M33-771 still dutifully issuing small-craft warnings for an ammonia sea that evaporated during the Ming Dynasty. Only 4.2 watts! (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.260",
          "gct": "0408 GCT",
          "entry": "** INTERGALACTIC [M-33]. 1420225.751 H-I, Epoch 2736.260 at 0408 GCT, Perseus gravitational micro-lens aligned for 11 minutes, bringing M33-771 up from noise floor to S4; decoded archaic Survey-Era barometer packet stuck at 942 mbar with 0.00% ambient moisture (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.210",
          "gct": "0359 GCT",
          "entry": "** INTERGALACTIC [M-33]. 1420225.800 H-I, Epoch 2736.210 at 0359 GCT, faint maser flute interval signal detected on Apex Ring #4; Lissajous phase scope locked onto a 3:5:1 harmonic ratio matching Asteroid 3-5-1 rotational pole (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ],
      "station_folder": "m33-771_drift-buoy",
      "characters": [
        {
          "name": "DS-771 Mk.IV Telemetry Sequencer (Unit #04)",
          "role": "Autonomous Deep-Field Crustal & Meteorological Sonde",
          "species_or_type": "Industrial Solid-State 21-cm H-I Telemetry Transponder (Pelagic & Deep-Field Telemetry Works)",
          "languages": "Barycentric Binary-FSK + Synthetic Industrial Telemetry Voice-ID",
          "dialect_notes": "Crisp, metallic industrial telemetry vocoder reading barometric reed registers and solar-capacitor bus voltage over a 5-note maser calibration pip.",
          "voice_profile": {
            "tts_voice": "Charon (Industrial Sonde Telemetry Vocoder)",
            "cadence": "95 WPM automated frame readout locked to 3:5:1 Lissajous sync",
            "dsp_chain": "21-cm H-I Doppler shift (-180 kHz) + 4.2W maser cavity ring"
          },
          "signature_quote": "[SONDE DS-771-04]: BUS 28.4V • BARO REED STUCK: FORCE-8 GALE WARNING • AMBIENT HUMIDITY 0.00% ALKALI SALT.",
          "bio": "Manufactured by Pelagic & Deep-Field Telemetry Works and air-dropped into the Veyra-3 Alkali Basin in the M-33 Triangulum Spur during the First Deep-Field Survey centuries ago. Its mechanical barometer reed corroded shut in a Force-8 gale long before the ammonia sea evaporated into dry white polygonal salt crust, leaving its trickle solar-RTG bus firing a 4.2-watt gale warning every 90 seconds.",
          "slug": "ds771_sonde",
          "headshot_src": "assets/plates/flow_m33_onboard_cam_a.jpg",
          "fullbody_src": "assets/plates/flow_m33_onboard_cam_b.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_ds771_sonde_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_ds771_sonde_rf.wav",
          "language_sample_transcript": "Deep-Field Survey Telemetry Unit D-S-seven-seven-one dash zero-four. Veyra-Three Basin. Barometer reed: nine-four-two millibars, locked. Warning: Force-Eight gale, six-meter swells. Ambient moisture: zero point zero zero percent dry alkali salt.",
          "phonetic_and_conlang_notes": "Deep-Field Survey Telemetry Protocol: deterministic alphanumeric register readout locked to the 21-cm Hydrogen line."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "A blindingly white polygonal alkali-salt desert on an uninhabited world in the M-33 Triangulum Spur (2.73 million light-years away). Nobody is out there to photograph the buoy—the only visual feed comes from the wide-angle inspection camera bolted directly to the sonde's own weathered yellow steel sensor boom.",
        "spectrum_gimmick_title": "2.73-Mly Gravitational Micro-Lens QRP (4.2W Industrial Sonde on 21-cm Hydrogen Line)",
        "hauser_commentary": "Extragalactic on 1420.405 MHz (minus 180 kHz Doppler): autonomous industrial drift-sonde M33-771 (Model DS-771 Mk.IV) brought up to S4 by a Perseus gravitational micro-lens—still dutifully issuing Force-8 marine gale warnings for an ammonia sea that dried up centuries ago, while its onboard horizon camera looks out past its own yellow sensor boom across bone-dry white salt flats! Only 4.2 watts!",
        "qsl_postcard_style": "Industrial Device Identification & CAD Schematic Card (Pelagic & Deep-Field Telemetry Works)",
        "qsl_animation_notes": "Industrial device verification card: left panel displays the orthographic CAD engineering schematic and serial plate of Sonde DS-771 Mk.IV with blinking telemetry nodes; right panel shows its onboard horizon camera POV as the helical whip antenna fires a cyan-green 4.2W burst and an ion dust-devil sweeps the salt flat!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Decoded Sonde DS-771-04 frame: barometer reed stuck at 942 mbar gale warning while onboard horizon cam shows 0.00% dry polygonal salt crust."
          },
          {
            "stage": "Broadcast 02 (Tracks on the Salt)",
            "summary": "Onboard horizon camera frame B captures fresh vehicle/foot tracks and a localized ion vortex right in front of the sonde's yellow sensor boom—and the tilt sensor resets from 34.2° to 0.0°!"
          }
        ]
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_m33_onboard_cam_a.jpg",
          "role": "16:9 Onboard Sonde Horizon-Cam POV Keyframe A (Flow)",
          "caption": "Shot FROM the wide-angle camera bolted to Autonomous Telemetry Sonde M33-771 (Model DS-771 Mk.IV), showing its own yellow steel sensor boom, aluminum RF box, solar panel, and helical whip antenna looking out across the dry white polygonal salt sea."
        },
        {
          "src": "assets/plates/flow_m33_onboard_cam_b.jpg",
          "role": "16:9 Onboard Sonde Horizon-Cam POV Keyframe B (Flow)",
          "caption": "Active 4.2W transmission burst: the sonde's foreground helical whip antenna and status LED glow cyan-green while an electrostatic ion dust-devil whirls across the alkali salt flats."
        }
      ]
    },
    {
      "id": "trojan-octal",
      "preset_slot": "P-04",
      "featured_prototype": false,
      "callsign": "E08-OCTAL",
      "name": "Trojan L4 'Three-Five-Octal'",
      "subtitle": "Unlisted Base-8 Numbers Station & Cipher Beacon",
      "category": "Numbers Station / Cipher",
      "status": "NO VIDEO • BASE-8 CIPHER",
      "status_color": "red",
      "origin": {
        "body": "Perseus-Trojan Lagrange Swarm L4 (Shard #624-Hektor)",
        "site": "Unmarked Carbonaceous Cavity Array",
        "coordinates": "Gal Lon 318.4°, Gal Lat +02.1° (L4 Libration Zone)",
        "distance": "2,480 Light-Years (Perseus Gap Bearing 318.4°)",
        "local_clock": "GCT Pulsar Direct (No Local Solar Day)"
      },
      "galactic": {
        "sector": "Perseus Arm Inner Rim • L4 Trojan Shard Swarm",
        "arm": "Perseus Arm",
        "azimuth_deg": 318.4,
        "elevation_deg": 2.1,
        "range_ly": 2480.0,
        "range_label": "2,480 ly (0.76 kpc)",
        "radial_norm": 0.72,
        "relay_nodes": [
          {
            "name": "Ceres-North Shadow Relay",
            "az_deg": 302.0,
            "el_deg": 14.2,
            "r_norm": 0.42,
            "range_label": "1,920 AU (North of CFS-7)",
            "role": "Perseus Gap Libration Waveguide",
            "xyz_unit": [
              -0.8221,
              0.5137,
              0.2453
            ]
          },
          {
            "name": "Quarantine Buoy 12 (Tartarus)",
            "az_deg": 304.2,
            "el_deg": 19.2,
            "r_norm": 0.25,
            "range_label": "420 AU (Customs Hold)",
            "role": "Null-Loop Jammer Rejection Reference",
            "xyz_unit": [
              -0.7811,
              0.5308,
              0.3289
            ]
          }
        ],
        "local_el_deg": 11.1,
        "xyz_unit": [
          -0.6515,
          0.7338,
          0.1925
        ],
        "sep_sol_deg": 100.2,
        "sep_ceres_deg": 45.3,
        "sep_psr_deg": 93.4,
        "booth_window": "North-West Window • Bay 08 (Station Dossier & L4)",
        "triangulation": {
          "ceres_dist_label": "2,479.98 ly",
          "ceres_sep_deg": 45.3,
          "sol_sep_deg": 100.2,
          "psr_sep_deg": 93.4,
          "baseline_parallax": "1.720\"",
          "booth_window": "North-West Window • Bay 08 (Station Dossier & L4)"
        }
      },
      "rf": {
        "frequency_khz": 6440.0,
        "measured_khz": 6440.0,
        "doppler_hz": 0.0,
        "band": "46m Out-of-Band ('No-No' Boundary Channel)",
        "mode": "USB-OCT",
        "filter_bw_hz": 2400,
        "tx_power_watts": 1200,
        "tx_power_label": "1.2 kW (Pulsed Capacitor Bank)",
        "antenna": "Slot-Cut Basalt Cavity Radiator",
        "relay_path": "Perseus Gap Waveguide + Oort Cometary Scatter",
        "sinpo": {
          "s": 4,
          "i": 2,
          "n": 4,
          "p": 4,
          "o": 3
        },
        "s_meter": "S9+10 dB",
        "s_meter_pct": 78,
        "hauser_index": "H-9.2",
        "peak_modulation_db": "641.9 Hz SUB-AUDIBLE HETERODYNE [SAH]",
        "dx_shorthand": [
          "NO-NO FREQ",
          "NUMBERS",
          "QRM-JAM",
          "SAH-641Hz"
        ]
      },
      "hardware_dossier": {
        "transmitter": "Zero-drift pulsar-disciplined USB exciter operating on 6,440.000 kHz—a restricted boundary channel between utility and broadcast allocations.",
        "feedline_anomaly": "Transmits Mon/Wed/Fri/Sun only at 0355–0415 GCT. Curiously, on Thursdays—when E08-OCTAL is off the air—an automated Syndicate noise-jammer on Ceres still fires up at 0355 GCT to jam the empty frequency.",
        "receive_antenna_at_gor9": "East/West Null Loop (Nulling Jammer at 272°, Main Lobe 318.4°)"
      },
      "media": {
        "video_src": "assets/clips/m33_drift_buoy.mp4",
        "poster_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
        "alt_plate_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
        "cam_id": "OCTAL-8 • BASE-8 CIPHER & MANIFEST CORRELATOR",
        "hud_banner": "NO VIDEO CARRIER • BASE-8 NUMBERS STREAM: 047 • 312 • 771 • 351",
        "audio_intercept_src": "assets/audio/intercept_trojan_octal.wav",
        "interval_signal_src": "assets/audio/is_trojan_octal.wav",
        "sstv_burst_src": "assets/audio/sstv_trojan_octal.wav",
        "interval_signal_name": "Ascending 5-Note Lydian Glockenspiel + 641.9 Hz Pulsar Hum",
        "languages": [
          "Synthesized Mandarin/Spanish Hybrid",
          "Base-8 Octal Groups"
        ],
        "transcript_excerpt": "[5-note glockenspiel chime x3] 'Attention: Three-Five-Octal. Three-Five-Octal. Group count eight: 047... 312... 771... 351... 015... 220...' (Decoded manifest: 6.0 metric tons of pork-chive dumpling wrappers + octal shift key 13.)",
        "qsl_plate_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
        "qsl_plate_b_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
        "flow_plates": [
          "assets/plates/flow_hektor_canyon_architecture.jpg"
        ]
      },
      "qsl": {
        "qsl_number": "QSL #0008-OCT",
        "gif_src": "assets/qsl/qsl_trojan_octal.gif",
        "protocol": "UNSOLICITED PHANTOM BURST (NO RETURN ADDRESS)",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0404 GCT",
        "motto": "EIGHT DIGITS IN THE DOUGH • SIX METRIC TONS IN THE HOLD",
        "signer": "UNSIGNED [STAMPED WITH OCTAL SHIFT KEY 015₈ = 13₁₀]",
        "collector_tier": "TIER S • PHANTOM NUMBERS eQSL (#8 of 64)",
        "verification_hash": "0x0644-OCT8-351-015",
        "embedded_clue": "Octal shift key 015 (decimal 13) unlocks the Sector 9 Quarantine Buoy 12 cargo manifest."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "BASE-8 OCTAL NUMBERS + CW KEYER + 641.9 Hz PULSAR SAH",
        "spectrum_style": "octal_fsk",
        "required_algorithm": "ALG-02",
        "algorithm_name": "ALG-02 • BASE-8 OCTAL NUMBERS & CARGO MANIFEST DECRYPTOR",
        "morse_stream": "----- ....- --... / ...-- .---- ..--- / --... --... .---- / ...-- ..... .---- / ----- .---- .....",
        "raw_rx_lines": [
          "04:04:00.00  IS-GLOCK: [5-NOTE LYDIAN CHIME x3] • SAH SUB-TONE = 641.928 Hz",
          "04:04:03.12  YL-VOICE: 'ATTENTION: THREE-FIVE-OCTAL • GROUP COUNT EIGHT'",
          "04:04:06.50  OCTAL-RX: 047  •  312  •  771  •  351  •  015  •  220  •  144  •  015",
          "04:04:10.05  QRM-NULL: CERES SYNDICATE JAMMER NULLED -34 dB ON BEARING 272.0°"
        ],
        "translated_lines": [
          "[MANIFEST DECRYPT]: '6.0 Metric Tons Pork & Chive Dumpling Wrappers (8 pleats per 351g dough)'",
          "[SECTOR CIPHER KEY]: Octal Group 015₈ (Decimal Shift Key = 13) -> Unlocks Sector 9 Log Cipher",
          "[COORDINATE PAYLOAD]: Group 351₈ -> Asteroid 3-5-1 (Outpost Nine) • Group 771₈ -> M33-771 Relic Maser Sync",
          "[JAMMER ANOMALY]: Automated Ceres Syndicate jammer fires at 0355 GCT even on scheduled silent Thursdays"
        ],
        "telemetry_metrics": [
          {
            "label": "CIPHER RADIX",
            "value": "BASE-8",
            "unit": "3-DIGIT OCTAL GRPS",
            "pct": 80,
            "alert": true
          },
          {
            "label": "PULSAR SAH LOCK",
            "value": "641.93 Hz",
            "unit": "PSR B1937+21 SYNC",
            "pct": 100,
            "alert": false
          },
          {
            "label": "JAMMER NULL",
            "value": "-34.0 dB",
            "unit": "CERES QRM @ 272°",
            "pct": 72,
            "alert": true
          },
          {
            "label": "OCTAL SHIFT KEY",
            "value": "KEY = 13",
            "unit": "6.0t DUMPLING CARGO",
            "pct": 92,
            "alert": true
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0404 GCT",
          "entry": "** TROJAN L4 [Perseus Rim]. 6440.000 USB, Epoch 2736.305 at 0404 GCT, unlicensed numbers station 'Three-Five-Octal' S9+10 on a no-no boundary frequency (Az 318.4°, 2,480 ly); YL synth voice reading 3-digit base-8 groups (claimed by L4 miners to be dumpling recipes). Note: yesterday (its day off), strong automated jamming still came on at 0355 GCT over an empty channel! (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.301",
          "gct": "0355 GCT",
          "entry": "** TROJAN L4. 6440.000 USB, Epoch 2736.301 at 0355 GCT, E08-OCTAL silent on its scheduled off-day, yet the automated Ceres Syndicate noise-jammer still fired up at 0355 sharp on bearing 272.0° to jam the empty frequency for 20 minutes! (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.289",
          "gct": "0400 GCT",
          "entry": "** TROJAN L4. 6440.000 USB, Epoch 2736.289 at 0400 GCT, ascending 5-note Lydian glockenspiel interval signal locked to a 641.928 Hz pulsar sub-tone; octal group [047 • 034] correlated with Euclid Prop I.34 parallelogram bisection (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ],
      "station_folder": "e08-octal_vulpecula-buzzer",
      "characters": [
        {
          "name": "Synthesizer Unit 'YL-8' (The Octal Voice)",
          "role": "Automated Base-8 Cipher Reader",
          "species_or_type": "1990s ROM Speech Chip (Spanish/Mandarin Hybrid Phonemes)",
          "languages": "Base-8 Octal Digits (0–7) in Hybrid Mandarin/Spanish",
          "dialect_notes": "Cold, hypnotic, uninflected female voice reading 3-digit octal groups over a 641.928 Hz pulsar hum.",
          "voice_profile": {
            "tts_voice": "Kore (Flat Monotone Cipher Filter)",
            "cadence": "60 WPM rhythmic 3-digit groups following 5-note Lydian glockenspiel",
            "dsp_chain": "USB narrowband 2.4 kHz + 641.9 Hz sub-audible heterodyne"
          },
          "signature_quote": "Attention: Three-Five-Octal. Group count eight: 047... 312... 771... 351... 015...",
          "bio": "The public face of E08-OCTAL on the restricted 6,440 kHz boundary channel. Because its optical tonewheel broke in 2719, the operators have to hold a live studio condenser mic up to a mechanical glockenspiel and speaker box.",
          "slug": "yl8_octal",
          "headshot_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
          "fullbody_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_yl8_octal_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_yl8_octal_rf.wav",
          "language_sample_transcript": "Atención: Tres, Cinco, Octal. Attention: Three, Five, Octal. Group count eight. Zero-four-seven. Three-one-two. Seven-seven-one. Three-five-one. Zero-one-five. Fin de transmisión.",
          "phonetic_and_conlang_notes": "Bilingual Spanish/English Base-8 (Octal 0–7) cryptographic numbers-station cadence."
        },
        {
          "name": "'Old Liang' & 'Arturo' (The Open-Mic Caretakers)",
          "role": "Bickering Bunker Custodians & Dumpling Makers",
          "species_or_type": "Humans (Retired L4 Lagrange Cipher Clerks)",
          "languages": "Shandong Mandarin & Porteño Spanish",
          "dialect_notes": "Muffled background arguments, coughing, clanking space-heaters, and whistling tea-kettles accidentally picked up whenever they forget to mute the glockenspiel mic.",
          "voice_profile": {
            "tts_voice": "Puck & Orus (Muffled Room-Mic Distance Filter)",
            "cadence": "Grumpy domestic bickering behind the deadly-serious numbers broadcast",
            "dsp_chain": "High-pass room reverb + kettle whistle @ 2,150 Hz"
          },
          "signature_quote": "[Behind the cipher voice]: 'Arturo, turn off the kettle, the red mic light is on!' — 'No, eight pleats per wrapper, three-five-one grams of dough!'",
          "bio": "Stationed inside Canyon Bunker #624-Hektor for twenty years with six metric tons of frozen dumpling wrappers and a code-book they use to coordinate tax-free provisions across Sector 9.",
          "slug": "liang_and_arturo",
          "headshot_src": "assets/characters/char_liang_and_arturo_headshot.jpg",
          "fullbody_src": "assets/characters/char_liang_and_arturo_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_liang_and_arturo_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_liang_and_arturo_rf.wav",
          "language_sample_transcript": "Arturo, apaga la pava, the red microphone light is on! Qué micrófono ni ocho cuartos, Old Liang! I told you, eight pleats per dumpling wrapper, three-hundred-fifty-one grams of dough!",
          "phonetic_and_conlang_notes": "Bunker Caretaker Spanglish: domestic Porteño Spanish & English argument accidentally broadcast behind the octal cipher."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "Hidden inside a terraced basalt canyon bunker beneath a giant curtain antenna array on Hektor. Like Russia's UVB-76 ('The Buzzer') and Cuba's HM01, the station mixes eerie cryptographic numbers with accidental live-mic comedy from the two old caretakers living inside the transmitter room.",
        "spectrum_gimmick_title": "Out-of-Band Base-8 Numbers + Accidental Open Studio Mic (UVB-76 Homage)",
        "hauser_commentary": "On the no-no boundary frequency of 6440 USB, 'Three-Five-Octal' was sending its usual base-eight groups—until 0404 GCT, when the studio mic picked up someone kicking a metal space-heater, a tea-kettle whistling, and a muffled voice muttering 'no, eight pleats per wrapper.'",
        "qsl_postcard_style": "Stark Cryptic Trefoil Emblem & Buff Cardstock Card (inspired by Red Mercury Labs & 4VEH Haiti)",
        "qsl_animation_notes": "The 3-5-1 trefoil blades flash while octal groups typewrite across the center; on Frame 5 an open-mic whistling tea-kettle pops up before a red 'STAMPED: KEY 015' rubber stamp slams over it.",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Decoded octal manifest for 6.0 metric tons of pork-chive dumpling wrappers + octal shift key 015 (decimal 13)."
          },
          {
            "stage": "Broadcast 02 (The Open-Mic Incident)",
            "summary": "At 0404 GCT, Old Liang drops the mechanical glockenspiel mallet; for 45 seconds listeners hear a whistling kettle and an argument about Quarantine Buoy 12."
          }
        ]
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_hektor_canyon_architecture.jpg",
          "role": "16:9 Canyon Bunker & Curtain-Antenna Background Plate (Flow)",
          "caption": "Brutalist concrete-and-steel terraced mining canyon on Shard #624-Hektor, crowned by the high-power shortwave curtain antenna array on the canyon rim."
        }
      ]
    },
    {
      "id": "pedregal-utility",
      "preset_slot": "P-05",
      "featured_prototype": false,
      "callsign": "XE9-PED/U",
      "name": "Pedregal Oort Weather Utility",
      "subtitle": "Out-of-Band Pirate Maritime/Cometary Frost Forecast",
      "category": "Pirate Utility",
      "status": "NO VIDEO • 3W QRP TELEMETRY",
      "status_color": "amber",
      "origin": {
        "body": "Inner Oort Cometary Staging Shoal (Sector 9 West)",
        "site": "Independent Ice-Tender 'Boca del Río'",
        "coordinates": "Gal Lon 264.0°, Gal Lat +11.5° (Oort Shell 38,400 AU)",
        "distance": "0.058 Light-Years (3,700 AU • Local Oort Scatter)",
        "local_clock": "0400 GCT Daily Window (0402–0415 GCT Only)"
      },
      "galactic": {
        "sector": "Oort Cloud Sector 9 West • Cometary Ice Shoal",
        "arm": "Local Oort Shell (Inner Rim)",
        "azimuth_deg": 264.0,
        "elevation_deg": 11.5,
        "range_ly": 0.058,
        "range_label": "3,700 AU (0.058 ly)",
        "radial_norm": 0.22,
        "relay_nodes": [
          {
            "name": "Comet C/2736-K4 Ion Tail",
            "az_deg": 264.0,
            "el_deg": 32.5,
            "r_norm": 0.36,
            "range_label": "3,700 AU (Cyanogen Coma)",
            "role": "+11.4 dB Es-Oort Forward-Scatter Mirror",
            "xyz_unit": [
              -0.8388,
              -0.0882,
              0.5373
            ]
          }
        ],
        "local_el_deg": 29.0,
        "xyz_unit": [
          -0.8698,
          -0.0914,
          0.4848
        ],
        "sep_sol_deg": 46.6,
        "sep_ceres_deg": 16.2,
        "sep_psr_deg": 120.5,
        "booth_window": "West Window • Bay 07 (3D Spectrum & Ceres Bearing)",
        "triangulation": {
          "ceres_dist_label": "1,969 AU",
          "ceres_sep_deg": 16.2,
          "sol_sep_deg": 46.6,
          "psr_sep_deg": 120.5,
          "baseline_parallax": "15.11° (906.7')",
          "booth_window": "West Window • Bay 07 (3D Spectrum & Ceres Bearing)"
        }
      },
      "rf": {
        "frequency_khz": 6969.5,
        "measured_khz": 6969.512,
        "doppler_hz": 12.0,
        "band": "43m Out-of-Band Pirate Trench",
        "mode": "USB",
        "filter_bw_hz": 2400,
        "tx_power_watts": 3,
        "tx_power_label": "3 W (Salvaged Dilithium-Foil Thermopile)",
        "antenna": "End-Fed Longwire Strung Between Ice-Saw Derricks",
        "relay_path": "Direct Oort Cometary Dust Scatter",
        "sinpo": {
          "s": 3,
          "i": 4,
          "n": 3,
          "p": 4,
          "o": 3
        },
        "s_meter": "S6 / S7",
        "s_meter_pct": 55,
        "hauser_index": "Q-7.9",
        "peak_modulation_db": "3.0 WATTS PEP [PIRATE UTILITY]",
        "dx_shorthand": [
          "PIRATE UTILITY",
          "3W QRP",
          "QSL #1",
          "OUT-OF-BAND"
        ]
      },
      "hardware_dossier": {
        "transmitter": "3-watt homebrew SSB transceiver built inside a biscuit tin. If a ham goes out-of-band and plays rock music, we call it a pirate; when XE9-PED goes out-of-band on 6,969.5 USB to read official methane-frost and sublimation forecasts for independent ice-harvesters, that makes him a Pirate Utility.",
        "feedline_anomaly": "Remarkable 3,700 AU reach on just 3 watts thanks to forward-scatter off ionized cometary tails.",
        "receive_antenna_at_gor9": "Acheron Chasm East/West Loop (Az 264.0°)"
      },
      "media": {
        "video_src": "assets/clips/buoy_n24_methane.mp4",
        "poster_src": "assets/plates/qsl_plate_pedregal_rafa.jpg",
        "alt_plate_src": "assets/plates/qsl_plate_pedregal_rafa_wave.jpg",
        "cam_id": "QRP COMETARY SCATTER & BAROMETRIC UNPACKER",
        "hud_banner": "NO VIDEO CARRIER • 3.0W QRP ICE-TUG WEATHER & DILITHIUM INDEX",
        "audio_intercept_src": "assets/audio/intercept_pedregal.wav",
        "interval_signal_src": "assets/audio/is_pedregal.wav",
        "sstv_burst_src": "assets/audio/sstv_pedregal.wav",
        "interval_signal_name": "Acoustic Guitar Harmonic & Barometer Click",
        "languages": [
          "Spanish",
          "Oort Tug-Crew Spanglish"
        ],
        "transcript_excerpt": "'Aviso meteorológico para los remolcadores de hielo en el Sector Nueve... presión de sublimación en aumento... Radio Pedregal, tres vatios de potencia...'",
        "qsl_plate_src": "assets/plates/qsl_plate_pedregal_rafa.jpg",
        "qsl_plate_b_src": "assets/plates/qsl_plate_pedregal_rafa_wave.jpg",
        "flow_plates": [
          "assets/plates/flow_pedregal_bridge_pov.jpg",
          "assets/plates/qsl_plate_pedregal_rafa.jpg",
          "assets/plates/qsl_plate_pedregal_rafa_wave.jpg"
        ]
      },
      "qsl": {
        "qsl_number": "QSL #0001-PED",
        "gif_src": "assets/qsl/qsl_pedregal.gif",
        "protocol": "SLOW-SCAN PACKET STAMP",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0411 GCT",
        "motto": "3 WATTS FOR THE ICE FLEET • PIRATE UTILITY OF SECTOR 9",
        "signer": "Capt. Rafael 'Rafa' Rodríguez, MV Boca del Río",
        "collector_tier": "TIER I • 3-WATT QRP MIRACLE QSL #1 (#1 of 50)",
        "verification_hash": "0x6969-PEDU-3WQRP",
        "embedded_clue": "Barometer millibar readings match the Dilithium Spot Exchange curve."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "3W QRP USB VOICE + CW BAROMETRIC MILLIBAR TABLE",
        "spectrum_style": "qrp_scatter",
        "required_algorithm": "ALG-04",
        "algorithm_name": "ALG-04 • CRYO-TELEMETRY & OORT TUG SPANGLISH UNPACKER",
        "morse_stream": "-..- . ----. -....- .--. . -.. / ...-- .-- / -- -... .- .-. / .---- ----- ....- ..---",
        "raw_rx_lines": [
          "04:11:02.18  CW-PREAMBLE: —••— • ————• —••••— •——• • —•• / •••— —•— •••",
          "04:11:05.40  SPANGLISH  : 'Aviso pa los ice-tugs en Shoal 44-K: frost-plume subiendo a +14.2 Pa!'",
          "04:11:08.75  MBAR-TABLE : [SHOAL-A: 1042.4] [SHOAL-B: 1046.8] [SHOAL-C: 1051.2] (+4.2%)",
          "04:11:11.90  QRP-STATUS : TX=3.0W PEP (BISCUIT-TIN RIG) • COMETARY TAIL SCATTER +11 dB"
        ],
        "translated_lines": [
          "[WEATHER TRANSLATION]: 'Advisory for independent ice-tugs in Shoal 44-K: sublimation plume rising to +14.2 Pa'",
          "[PIRATE UTILITY STATUS]: Out-of-band on 6,969.5 kHz USB delivering official frost safety tables on 3.0 Watts",
          "[TELEMETRY UNPACK]: Barometric millibar sequence [1042.4 -> 1046.8 -> 1051.2] encodes Grade-B Dilithium Spot (+4.2%)",
          "[PELLET DROP ALERT]: Capt. Rafa is signaling an uninspected Dilithium pellet barge caches near Comet C/2736-K4!"
        ],
        "telemetry_metrics": [
          {
            "label": "TX OUTPUT",
            "value": "3.00 W",
            "unit": "BISCUIT-TIN QRP",
            "pct": 18,
            "alert": false
          },
          {
            "label": "SUBLIMATION",
            "value": "+14.2 Pa",
            "unit": "COMET C/2736-K4",
            "pct": 76,
            "alert": true
          },
          {
            "label": "BARO / SPOT",
            "value": "1051.2 mb",
            "unit": "DILITHIUM +4.2%",
            "pct": 92,
            "alert": true
          },
          {
            "label": "SCATTER GAIN",
            "value": "+11.4 dB",
            "unit": "IONIZED TAIL BOUNCE",
            "pct": 66,
            "alert": false
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0411 GCT",
          "entry": "** OORT SHOAL WEST. 6969.5 USB, Epoch 2736.305 at 0402-0415 GCT only, 'Pedregal Radio' (Az 264.0°, 3,700 AU) reading Spanish cometary frost and sublimation forecasts for independent ice-boats. If a ham goes out of band and plays rock music we call it a pirate, so going out of band to read ice-tug weather makes him a Pirate Utility! Received QSL #1 confirming power is only 3 watts! (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.295",
          "gct": "0406 GCT",
          "entry": "** OORT SHOAL WEST. 6969.512 USB, Epoch 2736.295 at 0406 GCT, Capt. Rafa on MV Boca del Río reporting a +14.2 Pa sublimation plume near Comet C/2736-K4; signal peaked S7 via forward-scatter off the comet's ionized dust tail (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.280",
          "gct": "0414 GCT",
          "entry": "** OORT SHOAL WEST. 6969.500 USB, Epoch 2736.280 at 0414 GCT, acoustic guitar harmonic interval signal followed by CW millibar tables [1042.4 -> 1046.8 -> 1051.2] that track the Oort Grade-B Dilithium Spot Index to 0.1% (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ],
      "station_folder": "xe9-ped_boca-del-rio",
      "characters": [
        {
          "name": "Capt. Rafael 'Rafa' Rodríguez",
          "role": "Skipper of Ice-Tender MV Boca del Río & 'Pirate Utility' Broadcaster",
          "species_or_type": "Human (Independent Cryo-Sea & Cometary Ice-Harvester)",
          "languages": "Veracruz Spanish & Tug-Crew Spanglish",
          "dialect_notes": "Warm, folksy, coastal Mexican cadence mixed with cryo-barometric terminology and acoustic guitar chords.",
          "voice_profile": {
            "tts_voice": "Puck / Fenrir (Warm Veracruz Spanish-Inflected)",
            "cadence": "140 WPM relaxed wheelhouse delivery with nylon-string guitar harmonic intro",
            "dsp_chain": "3-Watt QRP SSB biscuit-tin exciter + cometary ion-tail forward-scatter flutter"
          },
          "signature_quote": "Buenas madrugadas a toda la flota hielera en el Sector Nueve... tres vatios desde mi lata de galletas danesas, ¡pero con corazón de cincuenta kilovatios!",
          "bio": "When the Sector 9 Meteorology Bureau stopped broadcasting Spanish-language ice-pack warnings to save reactor power, Capt. Rafa built a 3-watt SSB transmitter inside a round blue Danish butter-cookie tin and went out-of-band on 6,969.5 kHz USB every night from 0402 to 0415 GCT.",
          "slug": "capt_rafa",
          "headshot_src": "assets/characters/char_capt_rafa_headshot.jpg",
          "fullbody_src": "assets/characters/char_capt_rafa_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_capt_rafa_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_capt_rafa_rf.wav",
          "language_sample_transcript": "Buenas madrugadas a toda la flota hielera del Sector Nueve! This is Captain Rafa aboard the Boca del Río on sixty-nine-sixty-nine point five. Three watts coming out of my Danish butter-cookie tin, pero con corazón de cincuenta kilovatios!",
          "phonetic_and_conlang_notes": "Veracruz Maritime Spanish & Oort Ice-Fleet Spanglish ('flota hielera', 'lata de galletas danesas')."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "The Pedregal Ice-Shoal is worked by dozens of family-owned ice-tugs navigating dark sub-glacial seas and emerald icebergs beneath active comet tails. Capt. Rafa's wheelhouse aboard MV Boca del Río is the unofficial town square and weather bureau for the entire fleet.",
        "spectrum_gimmick_title": "3-Watt Biscuit-Tin QRP 'Pirate Utility' via Cometary Ion-Tail Scatter",
        "hauser_commentary": "At 0411 on 6969.5 USB, Capt. Rafa aboard the ice-tender Boca del Río with his nightly frost forecast. If a ham goes out of band and plays rock music we call it a pirate; going out of band on 3 watts to read official ice-tug weather makes him a Pirate Utility! Proud to hold QSL #1 from his butter-cookie-tin rig.",
        "qsl_postcard_style": "Homemade Wheelhouse Snapshot & Clip-Art Tower Postcard (inspired by Voice of Pancho Villa)",
        "qsl_animation_notes": "2-frame wheelhouse action: Capt. Rafa raises his hand in a big warm wave while the vacuum tube atop his blue cookie-tin transmitter flares golden-orange and the clip-art '3W BIG SIGNAL!' tower radiates!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Received QSL #1 confirming 3.0 Watts PEP from a Danish butter-cookie tin; millibar readings secretly track Grade-B Dilithium spot prices."
          },
          {
            "stage": "Broadcast 02 (The Geyser Rescue)",
            "summary": "Rafa stays on the air past 0415 GCT on battery power to guide three ice-barges around a violent +22 Pa sublimation eruption."
          }
        ]
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_pedregal_bridge_pov.jpg",
          "role": "16:9 Bridge-Window Ice-Sea Background Plate (Flow)",
          "caption": "View from the frosted forward bridge windows of MV Boca del Río looking out over its ice-crusted steel bow and radar mast across a dark sea of glowing emerald icebergs and a cyan comet tail."
        },
        {
          "src": "assets/plates/qsl_plate_pedregal_rafa.jpg",
          "role": "16:9 Character Keyframe A (Flow)",
          "caption": "Capt. Rafa Rodríguez in his warm timber-lined wheelhouse holding his 3W blue Danish butter-cookie-tin SSB transmitter."
        },
        {
          "src": "assets/plates/qsl_plate_pedregal_rafa_wave.jpg",
          "role": "16:9 Character Keyframe B (Flow)",
          "caption": "Capt. Rafa raising his left hand in a big warm wave while the vacuum tube atop his cookie-tin rig flares bright gold."
        }
      ]
    },
    {
      "id": "kz9-omega",
      "preset_slot": "P-06",
      "featured_prototype": false,
      "callsign": "KZ9-OMEGA",
      "name": "Relay Station KZ9-OMEGA",
      "subtitle": "Meridian Plateau High-Power Sector Relay (60 kV Squall)",
      "category": "Sector Trunk Relay",
      "status": "SPLATTER ±30 kHz • DRM FAULT",
      "status_color": "red",
      "origin": {
        "body": "Asteroid 19-Meridian (Sagittarius-Coreward Trunk Hop #1)",
        "site": "Meridian Plateau Ridge • Twin Parabolic Array",
        "coordinates": "Gal Lon 018.6°, Gal Lat -01.4° (Meridian Ridge)",
        "distance": "0.022 Light-Years (1,420 AU • Coreward Trunk Hop)",
        "local_clock": "0400 GCT (Engulfed in Triboelectric Squall)"
      },
      "galactic": {
        "sector": "Sagittarius–Coreward Trunk Corridor • Meridian Plateau",
        "arm": "Local Oort Trunk (Toward Sgr A* Core)",
        "azimuth_deg": 18.6,
        "elevation_deg": -1.4,
        "range_ly": 0.022,
        "range_label": "1,420 AU (0.022 ly)",
        "radial_norm": 0.16,
        "relay_nodes": [
          {
            "name": "Sector 9 Coreward Trunk Duct",
            "az_deg": 18.6,
            "el_deg": 14.5,
            "r_norm": 0.09,
            "range_label": "680 AU (Meridian Approach)",
            "role": "Direct 41m Trunk (60 kV Squall Zone)",
            "xyz_unit": [
              0.3088,
              0.9176,
              0.2504
            ]
          }
        ],
        "local_el_deg": 12.8,
        "xyz_unit": [
          0.311,
          0.9242,
          0.2215
        ],
        "sep_sol_deg": 142.3,
        "sep_ceres_deg": 102.3,
        "sep_psr_deg": 38.6,
        "booth_window": "North Window • Bay 01 (Hauser MK-IV Master Desk)",
        "triangulation": {
          "ceres_dist_label": "2,532 AU",
          "ceres_sep_deg": 102.3,
          "sol_sep_deg": 142.3,
          "psr_sep_deg": 38.6,
          "baseline_parallax": "45.23° (2713.9')",
          "booth_window": "North Window • Bay 01 (Hauser MK-IV Master Desk)"
        }
      },
      "rf": {
        "frequency_khz": 7140.0,
        "measured_khz": 7140.31,
        "doppler_hz": 310.0,
        "band": "41m Sector Trunk Relay",
        "mode": "DRM-9",
        "filter_bw_hz": 15000,
        "tx_power_watts": 50000,
        "tx_power_label": "50 kW (Dilithium Bus — Capacitor Fault)",
        "antenna": "Twin 18m Parabolic Dishes + Lattice Mast",
        "relay_path": "Direct Sector 9 Trunk Line (Splattering ±30 kHz)",
        "sinpo": {
          "s": 2,
          "i": 3,
          "n": 2,
          "p": 2,
          "o": 2
        },
        "s_meter": "S9+40 dB (SPLATTER)",
        "s_meter_pct": 96,
        "hauser_index": "Q-4.2",
        "peak_modulation_db": "60 kV FEEDHORN ARC • 60 kHz BANDWIDTH SPLATTER",
        "dx_shorthand": [
          "SPLATTER ±30kHz",
          "NOV CITED",
          "60kV ARC",
          "WINDHOWL"
        ]
      },
      "hardware_dossier": {
        "transmitter": "50 kW Continental-Apex Dilithium Trunk Transmitter. Currently cited by the Sector 9 Spectrum Bureau for splattering a 60-kHz-wide signal across 7,110–7,170 kHz due to a ruptured oil capacitor and 60 kV triboelectric dust arcing.",
        "feedline_anomaly": "60-kilovolt silicate dust squall is leaping directly from the right dish feedhorn to the lattice mast, inducing +4.8° phase-wobble in the #4 Marzelvane bushing and long hours of S9+40 dead-air windhowl.",
        "receive_antenna_at_gor9": "Attenuated -20 dB Pad on Apex Ring #1 (Az 018.6°)"
      },
      "media": {
        "video_src": "assets/clips/radio_corrugated_blowtorch.mp4",
        "poster_src": "assets/plates/flow_kz9_mast_pov_a.jpg",
        "alt_plate_src": "assets/plates/flow_kz9_mast_pov_b.jpg",
        "cam_id": "KZ9-OMEGA • TOWER #1 HIGH-MAST INSPECTION CAM",
        "hud_banner": "60 kV TRIBOELECTRIC ARC • BANDWIDTH SPLATTER: 60.0 kHz",
        "audio_intercept_src": "assets/audio/intercept_kz9_omega.wav",
        "interval_signal_src": "assets/audio/is_kz9_omega.wav",
        "sstv_burst_src": "assets/audio/sstv_kz9_omega.wav",
        "interval_signal_name": "60 kV Plasma Arc Snap & Dead-Air Silicate Windhowl",
        "languages": [
          "DRM-9 Telemetry Framing",
          "Triboelectric Windhowl"
        ],
        "transcript_excerpt": "[S9+40 DEAD-AIR SILICATE WINDHOWL] ... [60 kV CYAN PLASMA ARC SNAP] ... 'KZ9-OMEGA AUTOMATIC FAULT ID: MARZELVANE #4 PHASE WOBBLE +4.8 DEG...'",
        "qsl_plate_src": "assets/plates/flow_kz9_mast_pov_a.jpg",
        "qsl_plate_b_src": "assets/plates/flow_kz9_mast_pov_b.jpg",
        "flow_plates": [
          "assets/plates/flow_kz9_mast_pov_a.jpg",
          "assets/plates/flow_kz9_mast_pov_b.jpg"
        ]
      },
      "qsl": {
        "qsl_number": "QSL #0409-KZ9",
        "gif_src": "assets/qsl/qsl_kz9_omega.gif",
        "protocol": "FAULT-TELEMETRY AUTO-EJECT STAMP",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0400 GCT",
        "motto": "50 KILOWATTS THROUGH THE DUST — MIND THE 60 kHz SPLATTER",
        "signer": "Automated Fault Logger • Meridian Plateau",
        "collector_tier": "TIER II • FCC/SECTOR VIOLATION NOTICE EDITION (#99 of 250)",
        "verification_hash": "0x7140-KZ9O-ARC60KV",
        "embedded_clue": "Arc discharge intervals match the quarantine hold clock at Buoy 12."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "DRM-9 FAULT TELEMETRY + 60 kHz SPLATTER + CW AUTO-ID",
        "spectrum_style": "splatter_60khz",
        "required_algorithm": "ALG-04",
        "algorithm_name": "ALG-04 • DRM-9 FAULT DIAGNOSTIC & SPLATTER UNPACKER",
        "morse_stream": "-.- --.. ----. -....- --- -- . --. .- / ..-. .- ..- .-.. - / -- .- .-. --.. . .-.. ...- .- -. . / ....-",
        "raw_rx_lines": [
          "04:00:04.12  CW-FAULT: —•— ——•• ————•  —•—• •—•—• •—•• —  [NOV-2736-88 CITED]",
          "04:00:06.85  DRM9-HEX: [0x7140] BW_OCCUPIED=60.4kHz (7110-7170 kHz SPLATTER)",
          "04:00:09.10  ARC-DET : FEEDHORN_R -> MAST_LATTICE = 60.2 kV TRIBOELECTRIC SNAP",
          "04:00:12.44  MECH-TLM: MARZELVANE_BUSHING_04 PHASE_WOBBLE = +4.82° [OIL_CAP_RUPTURE]"
        ],
        "translated_lines": [
          "[SPECTRUM CITATION]: Station KZ9-OMEGA splattering ±30 kHz across 41m band due to blown filter capacitor",
          "[HIGH-VOLTAGE HAZARD]: 60.2 kV silicate dust discharge arcing across right parabolic dish feedhorn every 4.2s",
          "[MECHANICAL TELEMETRY]: #4 Hydrocoptic Marzelvane bushing exhibiting +4.82° phase wobble under wind load",
          "[HIDDEN RELAY TIMING]: Arc snap intervals synchronize with Quarantine Hold Buoy 12 telemetry window"
        ],
        "telemetry_metrics": [
          {
            "label": "SPLATTER BW",
            "value": "60.4 kHz",
            "unit": "7110–7170 kHz",
            "pct": 98,
            "alert": true
          },
          {
            "label": "FEEDHORN ARC",
            "value": "60.2 kV",
            "unit": "SILICATE SQUALL",
            "pct": 94,
            "alert": true
          },
          {
            "label": "MARZELVANE #4",
            "value": "+4.82°",
            "unit": "PHASE WOBBLE",
            "pct": 82,
            "alert": true
          },
          {
            "label": "CARRIER LEVEL",
            "value": "S9+40 dB",
            "unit": "50 kW DILITHIUM",
            "pct": 96,
            "alert": false
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0400 GCT",
          "entry": "** MERIDIAN PLATEAU. 7140.310 DRM-9, Epoch 2736.305 at 0400 GCT, Relay KZ9-OMEGA (Az 018.6°, 1,420 AU) engulfed in a 60 kV electrostatic dust squall; S9+40 of dead-air windhowl and plasma arc snaps, slurping out ±30 kHz (7110-7170) due to a blown oil capacitor and #4 Marzelvane phase-wobble (+4.8°). SINPO 2-3-2-2-2 (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.296",
          "gct": "0352 GCT",
          "entry": "** MERIDIAN PLATEAU. 7140.190 DRM-9, Epoch 2736.296 at 0352 GCT, Sector 9 Spectrum Bureau issued Notice of Violation NOV-2736-88 to KZ9-OMEGA after its PA oil filter capacitor ruptured, widening its 41m trunk passband from 15 kHz to 60.4 kHz (Operator, Asteroid 3-5-1, GOR-9)"
        },
        {
          "epoch": "2736.281",
          "gct": "0410 GCT",
          "entry": "** MERIDIAN PLATEAU. 7140.000 DRM-9, Epoch 2736.281 at 0410 GCT, prior to the silicate squall, KZ9-OMEGA was relaying inner-ring cargo manifests at S9+25 dB before telemetry began flagging +1.9° wobble on the #4 Marzelvane bushing (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ],
      "station_folder": "kz9-omega_meridian-relay",
      "characters": [
        {
          "name": "Harlan 'Sparky' Vance (via Remote DRM-9 Fault Logger)",
          "role": "Remote Relay Telemetry & Fault Auditor",
          "species_or_type": "Human (Continental-Apex Field Contractor)",
          "languages": "Midwestern American English + DRM-9 Hex Fault Framing",
          "dialect_notes": "Dry, exhausted deadpan voice recorded onto the automated fault-telemetry channel between 60 kV plasma arc snaps and S9+40 silicate windhowl.",
          "voice_profile": {
            "tts_voice": "Orus (Dry Weary Engineer)",
            "cadence": "125 WPM interrupted by 60 kV arc discharges every 4.2 seconds",
            "dsp_chain": "60 kHz wide splatter distortion + triboelectric static crashes"
          },
          "signature_quote": "KZ9-Omega automated fault log: the #4 Belt-Master marzelvane bushing is wobbling four-point-eight degrees, the oil capacitor is ruptured, and we are splattering sixty kilohertz across the whole forty-one-meter band. Do not send further citations.",
          "bio": "Monitors unstaffed Meridian Plateau Trunk Hop #1 via its tower-mounted inspection camera during a six-week planetary silicate dust storm while waiting for replacement filter capacitors impounded at Quarantine Buoy 12.",
          "slug": "harlon_vance",
          "headshot_src": "assets/characters/char_harlon_vance_headshot.jpg",
          "fullbody_src": "assets/characters/char_harlon_vance_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_harlon_vance_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_harlon_vance_rf.wav",
          "language_sample_transcript": "This is Chief Engineer Harlon Vance at Meridian Relay KZ9-Omega on seventy-one-forty. Do not cite us for sixty-kilohertz splatter! We are in a Force-Nine silicate dust storm, the marzelvane bushings are wobbling four point eight degrees, and Tower One just took a sixty-kilovolt arc!",
          "phonetic_and_conlang_notes": "Corporate High-Voltage Switchgear Jargon ('marzelvane bushings', 'sixty-kilohertz splatter', 'ceramic standoff')."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "The Meridian Silicate Plateau on planet Aurelia-IV is a vast, unstaffed desert plain where boiling ochre dust storms generate 60-kilovolt triboelectric potentials across exposed antenna steelwork. The only camera on site is bolted high up on the main relay tower looking down across its ceramic feedline insulators.",
        "spectrum_gimmick_title": "50 kW Capacitor Rupture Splattering ±30 kHz (WTWW / Radio Havana Windhowl Homage)",
        "hauser_commentary": "Automated Relay KZ9-Omega on 7140—cited by the Spectrum Bureau for coming on early and splattering a 60-kHz-wide signal from 7110 to 7170 because of a ruptured capacitor and a 60 kV dust squall arcing across the tower's ceramic insulators. Mostly S9+40 of dead-air silicate windhowl.",
        "qsl_postcard_style": "Corporate Hardware Underwriter & Tower-Cam Telemetry Card (Van Allen Switchgear)",
        "qsl_animation_notes": "Seen from the high mast-mounted inspection camera on Tower #1: a blinding 60 kV cyan plasma arc leaps from the parabolic dish below right into the foreground ceramic insulator with a shower of sparks and a red 'NOV CITED: ±30 kHz SPLATTER' stamp!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Cited for 60 kHz bandwidth splatter and +4.8° marzelvane bushing wobble as tower-cam captures 60 kV arcs hitting the foreground insulator."
          },
          {
            "stage": "Broadcast 02 (The Broken Phaser Lobe)",
            "summary": "Directional night-pattern phaser fails completely, accidentally beaming internal Syndicate customs audio 42,000 AU backward into GOR-9's lap."
          }
        ]
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_kz9_mast_pov_a.jpg",
          "role": "16:9 Onboard Tower-Mast Inspection Cam Keyframe A (Flow)",
          "caption": "Shot FROM the high-mounted inspection camera bolted to Tower #1 of Relay KZ9-OMEGA, showing the tower's own steel cross-bracing, copper grounding strap, and ceramic standoff insulators looking down at the twin 18m dishes as an ochre silicate dust wall rolls in."
        },
        {
          "src": "assets/plates/flow_kz9_mast_pov_b.jpg",
          "role": "16:9 Onboard Tower-Mast Inspection Cam Keyframe B (Flow)",
          "caption": "As the silicate dust storm engulfs the plateau below, a blinding 60 kV cyan-white plasma arc leaps from the lower parabolic dish right into the foreground ceramic standoff insulator, showering orange sparks!"
        }
      ]
    },
    {
      "id": "radio-free-hektor",
      "station_folder": "rfh-hop_radio-free-hektor",
      "preset_slot": "P-07",
      "featured_prototype": false,
      "callsign": "RFH-HOP",
      "name": "Radio Free Hektor",
      "subtitle": "Trojan L4 Frequency-Hopping Accordion Rebel Crawler",
      "category": "Frequency-Hopping Pirate",
      "status": "HOPPING ±5 kHz • JAMMER LATE",
      "status_color": "green",
      "origin": {
        "body": "Trojan L4 Asteroid Swarm (Shard #624-Hektor)",
        "site": "Mobile Silicate Blast-Crawler 'Balkan Star' (Crater-to-Crater)",
        "coordinates": "Gal Lon 319.1°, Gal Lat +02.4° (Mobile Crawler Track)",
        "distance": "2,482 Light-Years (Perseus-Trojan Corridor)",
        "local_clock": "Mon/Wed/Fri/Sun Only (Thursdays Off for Mahjong)"
      },
      "galactic": {
        "sector": "Perseus Arm Inner Rim • L4 Trojan Shard Swarm",
        "arm": "Perseus Arm",
        "azimuth_deg": 322.0,
        "elevation_deg": 2.4,
        "range_ly": 2482.0,
        "range_label": "2,482 ly (0.76 kpc)",
        "radial_norm": 0.75,
        "relay_nodes": [
          {
            "name": "Perseus Libration Waveguide",
            "az_deg": 318.0,
            "el_deg": 15.6,
            "r_norm": 0.52,
            "range_label": "940 ly (Perseus Inner Rim)",
            "role": "Hop-Track Duct (6440/6445/6435 kHz)",
            "xyz_unit": [
              -0.6445,
              0.7158,
              0.2689
            ]
          },
          {
            "name": "Ceres Jammer Null Node",
            "az_deg": 272.0,
            "el_deg": 14.6,
            "r_norm": 0.34,
            "range_label": "1,840 AU (Ceres Foundry #7)",
            "role": "Syndicate Jammer (90s Lag / Nulled -34 dB)",
            "xyz_unit": [
              -0.9671,
              0.0338,
              0.2521
            ]
          }
        ],
        "local_el_deg": 14.7,
        "xyz_unit": [
          -0.5955,
          0.7622,
          0.2538
        ],
        "sep_sol_deg": 101.7,
        "sep_ceres_deg": 48.3,
        "sep_psr_deg": 88.7,
        "booth_window": "North-West Window • Bay 08 (Station Dossier & L4)",
        "triangulation": {
          "ceres_dist_label": "2,481.98 ly",
          "ceres_sep_deg": 48.3,
          "sol_sep_deg": 101.7,
          "psr_sep_deg": 88.7,
          "baseline_parallax": "1.805\"",
          "booth_window": "North-West Window • Bay 08 (Station Dossier & L4)"
        }
      },
      "rf": {
        "frequency_khz": 6445.0,
        "measured_khz": 6445.0,
        "doppler_hz": -15.0,
        "band": "46m Hopping Trench (6440 → 6445 → 6435 kHz)",
        "mode": "USB-HOP",
        "filter_bw_hz": 2800,
        "tx_power_watts": 180,
        "tx_power_label": "180 W (Crawler Diesel-Cell Alternator)",
        "antenna": "4.5m Spring-Loaded Whip on Crawler Engine Hood",
        "relay_path": "Perseus Waveguide (Evading Ceres Noise-Blanketer)",
        "sinpo": {
          "s": 4,
          "i": 4,
          "n": 4,
          "p": 3,
          "o": 4
        },
        "s_meter": "S8 / S9",
        "s_meter_pct": 74,
        "hauser_index": "H-9.4",
        "peak_modulation_db": "QSY ±5 kHz EVERY 6 MIN [JAMMER MISSED]",
        "dx_shorthand": [
          "FREQ-HOP",
          "PIRATE",
          "THU-GHOST-JAM",
          "ACCORDION"
        ]
      },
      "hardware_dossier": {
        "transmitter": "180-watt surplus blast-crawler transceiver modified with a three-crystal rotary turret switch (`6440 / 6445 / 6435 kHz`) bolted next to the driver's clutch.",
        "feedline_anomaly": "Every 6 minutes Zora clicks the crystal turret to hop ±5 kHz ahead of the Ceres Syndicate's automated noise-jammer, which takes 90 seconds to retune its cavity filters. Hilariously, on Thursdays—when the crew takes the night off—the Syndicate jammer still fires up at 0355 GCT to jam 6440 kHz for 20 minutes of empty vacuum.",
        "receive_antenna_at_gor9": "East/West Null Loop (Tracking 6435–6445 kHz Hop Window)"
      },
      "media": {
        "video_src": "assets/clips/m33_drift_buoy.mp4",
        "poster_src": "assets/plates/qsl_plate_radio_free_hektor.jpg",
        "alt_plate_src": "assets/plates/qsl_plate_radio_free_hektor_b.jpg",
        "qsl_plate_src": "assets/plates/qsl_plate_radio_free_hektor.jpg",
        "qsl_plate_b_src": "assets/plates/qsl_plate_radio_free_hektor_b.jpg",
        "cam_id": "HOP-TRACKER • 6440/6445/6435 kHz & JAMMER OFFSET",
        "hud_banner": "QSY HOP ACTIVE: 6445.0 kHz • SYNDICATE JAMMER STUCK ON 6440.0 kHz",
        "audio_intercept_src": "assets/audio/intercept_radio_free_hektor.wav",
        "interval_signal_src": "assets/audio/is_radio_free_hektor.wav",
        "sstv_burst_src": "assets/audio/sstv_radio_free_hektor.wav",
        "interval_signal_name": "Balkan Electric Accordion Polka Riff + Turret Click",
        "languages": [
          "Serbo-Croatian Miner Patois",
          "English",
          "Union Cipher"
        ],
        "transcript_excerpt": "[Lively red accordion polka] 'Attention Shard 624! Syndicate jammer warming up on 6440—everybody turn your VFO up five kilohertz to 6445 on the count of three—CLICK!' [JAMMER ROARS ON OLD FREQUENCY]"
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_hektor_canyon_architecture.jpg",
          "role": "16:9 Canyon City & Crawler Switchback Background Plate (Flow)",
          "caption": "Deep terraced basalt canyon city on Hektor with a yellow tracked blast-crawler descending the canyon switchback beneath the rim curtain array."
        },
        {
          "src": "assets/plates/qsl_plate_radio_free_hektor.jpg",
          "role": "16:9 Character Keyframe A (Flow)",
          "caption": "Zora 'Bellows' Kovač sitting on yellow tracked Crawler X-74 playing her red accordion."
        },
        {
          "src": "assets/plates/qsl_plate_radio_free_hektor_b.jpg",
          "role": "16:9 Character Keyframe B (Flow)",
          "caption": "Zora throwing both gloved hands up in a huge laugh and wave as the crawler whip antenna blazes green/gold on 6445 kHz."
        }
      ],
      "qsl": {
        "qsl_number": "QSL #0074-RFH",
        "gif_src": "assets/qsl/qsl_radio_free_hektor.gif",
        "protocol": "FREQUENCY-AGILE 3-HOP SSTV STAMP",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0406 GCT",
        "motto": "HOP FASTER THAN THE JAMMER — THURSDAYS OFF FOR MAHJONG",
        "signer": "Zora 'Bellows' Kovač, Crawler X-74 Blast-Engineers Union",
        "collector_tier": "TIER I • 3-HOP REBEL EDITION (#19 of 100)",
        "verification_hash": "0x6445-RFH-HOP3-X74",
        "embedded_clue": "Hop intervals (6m, 10m, 16m) and Thursday ghost-jamming expose the Ceres Syndicate's fixed cron timer."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "3-CRYSTAL HOPPING USB + ACCORDION INTERVAL + JAMMER TELEMETRY",
        "spectrum_style": "octal_fsk",
        "required_algorithm": "ALG-02",
        "algorithm_name": "ALG-02 • FREQUENCY-HOP TRACKER & UNION MANIFEST TRANSLATOR",
        "morse_stream": ".-. ..-. .... / --.- ... -.-- / -.... ....- ....- ..... / .--- .- -- / -- .. ... ...",
        "raw_rx_lines": [
          "04:00:02.00  HOP-01  : 6,440.000 kHz USB • ZORA ACCORDION ID + BLAST SCHEDULE",
          "04:05:58.40  QSY-CMD : 'Turret click +5 kHz -> 6,445.000 kHz NOW!'",
          "04:06:01.15  JAM-LAG : CERES JAMMER FIRED ON OLD FREQ (6,440.0 kHz) — 90s LATE!",
          "04:06:10.00  THU-NOTE: THURSDAY OFF-AIR LOG CONFIRMS 20m EMPTY-CHANNEL JAMMING"
        ],
        "translated_lines": [
          "[HOP TRACKER]: Radio Free Hektor jumped 6440 -> 6445 kHz at 0406 GCT with zero packet loss",
          "[JAMMER ANALYSIS]: Ceres Syndicate noise-blanketer locked onto 6440 kHz 90 seconds after QSY",
          "[UNION BULLETIN]: Quarry 44-K dragline slowdown extended until Dilithium hazard pay increases 8%",
          "[GHOST JAMMING]: On silent Thursdays, Syndicate AI still jams empty 6440 kHz from 0355–0415 GCT"
        ],
        "telemetry_metrics": [
          {
            "label": "ACTIVE HOP",
            "value": "6445 kHz",
            "unit": "+5 kHz TURRET QSY",
            "pct": 85,
            "alert": false
          },
          {
            "label": "JAMMER LAG",
            "value": "90.0 sec",
            "unit": "STUCK ON 6440 kHz",
            "pct": 92,
            "alert": true
          },
          {
            "label": "CRAWLER PWR",
            "value": "180 W",
            "unit": "X-74 ALTERNATOR",
            "pct": 60,
            "alert": false
          },
          {
            "label": "THU JAMMING",
            "value": "EMPTY CH",
            "unit": "AI CRON BUG",
            "pct": 98,
            "alert": true
          }
        ]
      },
      "characters": [
        {
          "name": "Zora 'Bellows' Kovač",
          "role": "Crawler X-74 Operator, Accordionist & Rebel Announcer",
          "species_or_type": "Human (Retired Silicate Blast-Engineer)",
          "languages": "Serbo-Croatian, English, Trojan Miner Patois",
          "dialect_notes": "Boisterous, fearless laugh; punctuates every union bulletin and frequency hop with a triumphant Balkan accordion chord.",
          "voice_profile": {
            "tts_voice": "Kore / Aoede (Boisterous Slavic Accent)",
            "cadence": "150 WPM over live red Welmeister accordion riffs",
            "dsp_chain": "180W mobile whip USB + rotary crystal turret click"
          },
          "signature_quote": "Ceres Syndicate jammer is warming up its tubes on 6440, comrades—reach for the big knob and hop up five kilohertz with Zora!",
          "bio": "After thirty years setting shaped charges in Silicate Quarry 44-K, Zora requisitioned Crawler X-74, bolted a 3-crystal hopping exciter to the dashboard, and began broadcasting union news and accordion requests across the Perseus-Trojan gap.",
          "slug": "zora_kovac",
          "headshot_src": "assets/characters/char_zora_kovac_headshot.jpg",
          "fullbody_src": "assets/characters/char_zora_kovac_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_zora_kovac_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_zora_kovac_rf.wav",
          "language_sample_transcript": "Dobro jutro, slobodna braćo na Hektoru! Good morning free miners of Shard Six-Two-Four, this is Zora on Radio Free Hektor! I see the Ceres jammer warming up on sixty-four-forty—too slow, boys! Hold onto your accordion, we're hopping to sixty-four-forty-five right now!",
          "phonetic_and_conlang_notes": "Trojan L4 Rebel Patois: Balkan Serbo-Croatian greetings ('Dobro jutro, slobodna braćo!') mixed with frequency-hopping pirate calls."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "Crawler X-74 rumbles continuously along the terraced canyon switchbacks of Hektor so the Ceres Syndicate's direction-finding loops can never triangulate the same ridge twice.",
        "spectrum_gimmick_title": "Manual 3-Crystal Frequency Hopping (±5 kHz) & Thursday Ghost-Jamming (North Korea 7200 kHz Homage)",
        "hauser_commentary": "In the L4 Trojans, 'Radio Free Hektor' opened on 6440 USB with Zora's accordion, hopped to 6445 at 0406 to shake the Ceres noise-blanketer, and hopped to 6435 at 0412. And as usual on Thursdays—their night off—the automated Syndicate jammer still roared on at 0355 to fiercely jam twenty minutes of pure vacuum.",
        "qsl_postcard_style": "Retro Gouache Pirate Crawler & Accordion Postcard (inspired by Radio Spaceshuttle International)",
        "qsl_animation_notes": "2-frame character animation: Zora plays her red accordion on Crawler X-74, then throws both gloved hands up in a huge laugh as the whip antenna blazes green/gold and the frequency badge hops ahead of the red Jammer crosshair!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (Initial Log)",
            "summary": "Logged 3-step frequency hop (6440/6445/6435 kHz) and documented the Thursday 0355 GCT ghost-jamming on an empty channel."
          },
          {
            "stage": "Broadcast 02 (The Jammer Harmonic)",
            "summary": "Zora tricks the Syndicate jammer into chasing her onto 6450 kHz, accidentally jamming the Syndicate's own automated ore-barge dispatch channel!"
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0406 GCT",
          "entry": "** TROJAN L4 [Perseus Rim]. 6440 -> 6445 -> 6435 USB, Epoch 2736.305 at 0400-0418 GCT, mobile rebel pirate 'Radio Free Hektor' (180W on Crawler X-74); YL Zora playing live accordion and calling a +5 kHz QSY every 6 minutes while the automated Ceres Syndicate noise-jammer lumbered 90 seconds behind her! Note: on Thursday (their scheduled mahjong night off), the Syndicate jammer still came on at 0355 GCT to jam an empty frequency! (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ]
    },
    {
      "id": "st-jerome-slag",
      "station_folder": "vjb-3x_st-jerome-slag",
      "preset_slot": "P-08",
      "featured_prototype": false,
      "callsign": "VJB-3X",
      "name": "Vael-Vihara Harmonic Spire",
      "subtitle": "Planet Kaelen-V Ethereal Monolithic Sanctuary & Tri-Band Spire",
      "category": "Multi-Spectrum Planetary Sanctuary",
      "status": "3-BAND HARMONIC SPIRE LOCK",
      "status_color": "amber",
      "origin": {
        "body": "Planet Kaelen-V (Opalescent Mist Chasms of Vael-Karun)",
        "site": "Sanctuary of the Fluted Shell & Golden Harmonic Spire",
        "coordinates": "Gal Lon 188.2°, Gal Lat -14.6° (Vael-Karun Nebula Rim)",
        "distance": "1,140 Light-Years (Orion-Perseus Inter-Arm Sanctuary)",
        "local_clock": "0400 GCT Twin-Moon Convergence Bow"
      },
      "galactic": {
        "sector": "Orion-Perseus Inter-Arm • Kaelen-V Planetary Sanctuary",
        "arm": "Orion–Cygnus Spur",
        "azimuth_deg": 188.2,
        "elevation_deg": -14.6,
        "range_ly": 1140.0,
        "range_label": "1,140 ly (0.35 kpc)",
        "radial_norm": 0.48,
        "relay_nodes": [
          {
            "name": "Kaelen-V Crystal Spire",
            "az_deg": 188.2,
            "el_deg": 22.8,
            "r_norm": 0.32,
            "range_label": "480 ly (Vael-Karun Rim)",
            "role": "Piezo-Opalescent Tri-Band Resonator",
            "xyz_unit": [
              -0.1315,
              -0.9124,
              0.3875
            ]
          },
          {
            "name": "O.R.S. 351 Polar Halo",
            "az_deg": 158.0,
            "el_deg": 18.0,
            "r_norm": 0.12,
            "range_label": "42.8 km (Local Halo Orbit)",
            "role": "Simultaneous SW + H-I + Optical Lock",
            "xyz_unit": [
              0.3563,
              -0.8818,
              0.309
            ]
          }
        ],
        "local_el_deg": 20.9,
        "xyz_unit": [
          -0.1332,
          -0.9247,
          0.3567
        ],
        "sep_sol_deg": 22.5,
        "sep_ceres_deg": 79.2,
        "sep_psr_deg": 113.8,
        "booth_window": "South Airlock & Catwalk Sector",
        "triangulation": {
          "ceres_dist_label": "1,139.99 ly",
          "ceres_sep_deg": 79.2,
          "sol_sep_deg": 22.5,
          "psr_sep_deg": 113.8,
          "baseline_parallax": "5.171\"",
          "booth_window": "South Airlock & Catwalk Sector"
        }
      },
      "rf": {
        "frequency_khz": 9290.0,
        "measured_khz": 9290.118,
        "doppler_hz": 118.0,
        "band": "31m SW + 21cm H-I + 632nm Optical (Simultaneous!)",
        "mode": "PIM-3X",
        "filter_bw_hz": 4000,
        "tx_power_watts": 1200,
        "tx_power_label": "1.2 kW Piezo-Crystalline Chasm Array",
        "antenna": "Colossal Needle-Thin Golden-Brass Harmonic Spire & Suspended Rings",
        "relay_path": "Piezo-Opalescent Crustal Intermodulation ('Crystal-Spire Effect')",
        "sinpo": {
          "s": 4,
          "i": 4,
          "n": 4,
          "p": 4,
          "o": 4
        },
        "s_meter": "S9 (3 BANDS!)",
        "s_meter_pct": 84,
        "hauser_index": "Q-9.6",
        "peak_modulation_db": "3-SPECTRUM HARMONIC SPIRE [SW + H-I + OPTICAL]",
        "dx_shorthand": [
          "VAEL-VIHARA",
          "PIM-3X",
          "ALIEN-MONKS",
          "3-SPECTRUM"
        ]
      },
      "hardware_dossier": {
        "transmitter": "Across the violet-mist chasm on the ethereal planet Kaelen-V rises a monolithic sanctuary of fluted white-alabaster parabolic shells, crowned at its apex by a colossal needle-thin golden-brass harmonic antenna spire with suspended geometric resonance rings.",
        "feedline_anomaly": "The sanctuary's fluted shells act as giant acoustic-to-electromagnetic parabolic horns coupled to the planet's piezo-opalescent crystal arches. Every twilight at 0400 GCT when the two tall, pearlescent-skinned alien ascetics (Auren-7 and Vael-9) bow in unison on the obsidian terrace, the golden spire ignites in a luminous corona that radiates simultaneously on 9,290 kHz shortwave, 1,420.4 MHz Hydrogen line, and 632 nm optical!",
        "receive_antenna_at_gor9": "Simultaneous Lock: Apex Ring #2 (9290 kHz) + Cryo-Maser (21cm)"
      },
      "media": {
        "video_src": "assets/clips/m33_drift_buoy.mp4",
        "poster_src": "assets/plates/qsl_plate_alien_monastery_a.jpg",
        "alt_plate_src": "assets/plates/qsl_plate_alien_monastery_b.jpg",
        "qsl_plate_src": "assets/plates/qsl_plate_alien_monastery_a.jpg",
        "qsl_plate_b_src": "assets/plates/qsl_plate_alien_monastery_b.jpg",
        "cam_id": "KAELEN-V • TERRACE ARCHIVE & HARMONIC SPIRE VIEW",
        "hud_banner": "VAEL-VIHARA SPIRE: 9290 kHz SW + 1420 MHz H-I + OPTICAL CORONA",
        "audio_intercept_src": "assets/audio/intercept_st_jerome_slag.wav",
        "interval_signal_src": "assets/audio/is_st_jerome_slag.wav",
        "sstv_burst_src": "assets/audio/sstv_st_jerome_slag.wav",
        "interval_signal_name": "Alabaster Shell Call-and-Response & 5-Voice Polyphonic Peace Resonator",
        "languages": [
          "Kaelen Call-and-Response Liturgical",
          "5-Voice Polyphonic Choir & Galactic Peace Benediction"
        ],
        "transcript_excerpt": "[ONE — Lead Cantor Auren-7]: 'Vael-kora... auren-shi... Tune the fluted shells of Kaelen-Five.' [MANY — 5-Voice Choir simultaneously]: 'Tal-vihara... shanti-vel... Our resonators bring peace to the galaxy... Three spectrums as one, peace to every listening world.'"
      },
      "flow_plates": [
        {
          "src": "assets/plates/flow_alien_monastery_vista.jpg",
          "role": "16:9 Ethereal Alien Planet & Sanctuary Vista (Flow Clean Background)",
          "caption": "Empty obsidian-and-crystal terrace overlooking the opalescent mineral arches, violet mist chasm, and fluted white-alabaster alien monastery with its colossal golden-brass antenna spire."
        },
        {
          "src": "assets/plates/qsl_plate_alien_monastery_a.jpg",
          "role": "16:9 Alien Monks Keyframe A — Standing on Terrace (Flow)",
          "caption": "Three Kaelen-V monastic cantors of contrasting builds, heights, and skin tones standing on the obsidian terrace: towering barrel-chested obsidian-indigo Basso Profundo Vael-9, tall opalescent pearl-lavender Lead Cantor Auren-7, and petite golden-honey Soprano novice Kora-5."
        },
        {
          "src": "assets/plates/qsl_plate_alien_monastery_b.jpg",
          "role": "16:9 Alien Monks Keyframe B — Bowing as Spire Ignites (Flow)",
          "caption": "All three contrasting Kaelen-V monks turn and bow gracefully in unison with palms pressed together as the colossal golden-brass spire in the distance blazes with concentric golden-amber harmonic rings."
        },
        {
          "src": "assets/characters/char_vael_choir_fullbody.jpg",
          "role": "16:9 Choir of the Fluted Shells & Golden Resonator Sphere (Flow)",
          "caption": "All five Kaelen-V cantors standing in a sacred semicircle beneath the suspended golden-brass armillary resonator—each varying in stature, cranial resonance structure, and skin tone according to their vocal register (obsidian-indigo Bass, terracotta-mahogany Contralto, pearl-lavender Baritone, seafoam-jade Tenor, and petite golden-honey Soprano)."
        },
        {
          "src": "assets/plates/flow_kaelen_planet_architecture.jpg",
          "role": "16:9 Secondary Planetary Sanctuary Vista (Flow)",
          "caption": "High-altitude geothermal mineral pools and cliffside bell-viaducts in the lower valleys of Kaelen-V."
        }
      ],
      "qsl": {
        "qsl_number": "QSL #0319-VJB",
        "gif_src": "assets/qsl/qsl_st_jerome_slag.gif",
        "protocol": "KAELEN-V HARMONIC SPIRE TRI-BAND QSL",
        "dimensions": "384×240 • 10-Frame Postcard eQSL GIF",
        "issue_epoch": "2736.305 • 0400 GCT",
        "motto": "WHERE THE FLUTED SHELLS SING — OUR RESONATORS BRING PEACE TO THE GALAXY",
        "signer": "Cantor Auren-7 & The Choir of the Fluted Shells, Vael-Vihara (Kaelen-V)",
        "collector_tier": "TIER I • OPALESCENT ARCHIVE EDITION (#7 of 77)",
        "verification_hash": "0x9290-VJB3-KAELEN",
        "embedded_clue": "When the ascetics chant in One-to-Many call-and-response and bow in unison, the golden spire radiates concentric harmonic rings that they believe calm stellar static and bring peace to the galaxy."
      },
      "decoder": {
        "has_live_video": false,
        "default_view": "decoder",
        "signal_type": "3-BAND PIEZO-CRYSTALLINE HARMONIC (9290 kHz SW + 21cm H-I + OPTICAL)",
        "spectrum_style": "hi_maser",
        "required_algorithm": "ALG-01",
        "algorithm_name": "ALG-01 • PIEZO-SPIRE INTERMODULATION & POLYPHONIC CHOIR UNPACKER",
        "morse_stream": "...- .--- -... / ...-- -..- / ----. ..--- ----. ----- / ...- .- . .-.. / ... .--. .. .-. .",
        "raw_rx_lines": [
          "04:00:01.10  CALL-ONE : CANTOR AUREN-7 SOLO INVOCATION ('VAEL-KORA... AUREN-SHI...')",
          "04:00:03.45  RESP-MANY: 5-VOICE CHOIR UNISON ('OUR RESONATORS BRING PEACE TO THE GALAXY')",
          "04:00:05.80  BAND-2 HI: 1,420.405 MHz 21-cm OVERTONE (FLUTED ALABASTER SHELL HORN)",
          "04:00:08.20  BAND-3 OP: GOLDEN SPIRE CORONA ('PROPORTIO DIVINA 3:5:1 • SHANTI-VEL')"
        ],
        "translated_lines": [
          "[ONE-TO-MANY CHANT]: Lead Cantor Auren-7 calls out; 4 Choir Cantors answer in simultaneous harmony!",
          "[GALACTIC DOCTRINE]: The order believes their resonators dissolve war and static, bringing peace to the galaxy",
          "[MULTI-SPECTRUM LOCK]: Simultaneous lock on 9290 kHz SW, 1420 MHz H-I, and 632 nm optical corona!",
          "[QSL POLICY]: Cantor Auren-7 & the Choir of the Fluted Shells issue QSL #0319-VJB to peaceful listeners"
        ],
        "telemetry_metrics": [
          {
            "label": "SW BAND",
            "value": "9290 kHz",
            "unit": "31m HARMONIC",
            "pct": 84,
            "alert": true
          },
          {
            "label": "H-I BAND",
            "value": "1420 MHz",
            "unit": "21cm SHELL HORN",
            "pct": 76,
            "alert": true
          },
          {
            "label": "VOICES",
            "value": "1 -> 5",
            "unit": "CALL & CHOIR",
            "pct": 96,
            "alert": false
          },
          {
            "label": "RESONATOR",
            "value": "3:5:1",
            "unit": "GALACTIC PEACE",
            "pct": 98,
            "alert": true
          }
        ]
      },
      "characters": [
        {
          "name": "Lead Cantor Auren-7 (One-to-Many Call & Response)",
          "role": "First Voice of the Resonator & Call-and-Response Leader",
          "species_or_type": "Kaelen-V Ethereal Humanoid (Pearlescent-Skinned Acoustic Ascetic)",
          "languages": "Kaelen Liturgical Invocation + Interstellar Peace Benediction",
          "dialect_notes": "Intones the solitary modal call ('One') into the suspended golden-brass resonator sphere, immediately answered in simultaneous 4-part harmonic unison by the Choir ('Many').",
          "voice_profile": {
            "tts_voice": "Argon III-C (Lead Call) -> Charon + Leda + Kore + Orus (4-Voice Choir Response)",
            "cadence": "92 WPM antiphonal call-and-response over 3:5:8 crystal-arch overtones",
            "dsp_chain": "Antiphonal One-to-Many spatializer + Fluted Alabaster Shell reverb + 3-band spire exciter"
          },
          "signature_quote": "Where the stars are torn by static, let our golden spire tune the void... Tal-vihara, shanti-vel: our resonators bring peace to the galaxy.",
          "bio": "Standing at the focal point of Vael-Vihara's central fluted shell, Auren-7 leads the twilight antiphony. The ascetics of Kaelen-V believe that warfare, fear, and loneliness across the Orion-Perseus arm are symptoms of phase-dissonance in the interstellar medium—and that by chanting pure 3:5:1 harmonic ratios into their piezo-crystalline resonators, they are actively bringing peace to the galaxy.",
          "slug": "cantor_auren7",
          "headshot_src": "assets/characters/char_cantor_auren7_headshot.jpg",
          "fullbody_src": "assets/characters/char_cantor_auren7_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_cantor_auren7_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_cantor_auren7_rf.wav",
          "language_sample_transcript": "[ONE — Lead Cantor Auren-7]: \"Vael-kora... auren-shi... Tune the fluted shells of Kaelen-Five.\" [MANY — 4-Voice Choir Simultaneously]: \"Tal-vihara... shanti-vel... Our resonators bring peace to the galaxy.\" [ONE — Lead Cantor Auren-7]: \"Where the stars are divided by dissonance, let the Great Spire harmonize the void.\" [MANY — All 5 Voices in Unison]: \"O-ma-ru Vael-Kaelen... Three spectrums as one... Peace to every listening world.\"",
          "phonetic_and_conlang_notes": "Antiphonal One-to-Many Liturgical Chant: Lead Cantor ('One', Argon III-C) intones the Kaelenic call into the golden resonator, answered simultaneously by four distinct individual voices ('Many': Charon, Leda, Kore, Orus) time-aligned in a 3:5:8 harmonic triad."
        },
        {
          "name": "The Choir of the Fluted Shells (Simultaneous Multi-Voice Chanting)",
          "role": "Circle of Five Resonator Cantors (Vael-9, Leda-3, Auren-7, Orus-8 & Kora-5)",
          "species_or_type": "5-Voice Kaelen-V Polyphonic Monastic Ensemble (5 Distinct Vocal/Anatomical Morphs)",
          "languages": "Simultaneous 5-Voice Kaelen Polyphony & Overlapping Canon",
          "dialect_notes": "Five distinct individual voices chanting simultaneously—each monk's stature, cranial flute geometry, chest cavity, and skin tone corresponding to their vocal register.",
          "voice_profile": {
            "tts_voice": "5 Individual Voices Simultaneously (Charon + Leda + Kore + Aoede + Argon III-C)",
            "cadence": "Simultaneous layered canon & 5-part choral unison (220/330/366/440/550 Hz chord)",
            "dsp_chain": "5-voice stereo/binaural choir spread + harmonic resonator vocoder bed + parabolic horn reverb"
          },
          "signature_quote": "O-ma-ru Vael-Kaelen... Five voices as one shell, three spectrums as one spire—radiating peace to every listening world.",
          "bio": "In the Order of the Fluted Shell, each cantor's physical morphology, stature, and skin tone match their acoustic register: Vael-9 (Basso Profundo, Charon) is a towering, barrel-chested elder with a wide fluted cranial dome and deep obsidian-indigo slate skin; Leda-3 (Contralto, Leda) is fuller-figured and round-faced with warm terracotta-mahogany brown skin; Auren-7 (Lead Baritone, Argon III-C) is tall and regal with opalescent pearl-lavender skin; Orus-8 (Lyric Tenor, Orus/Aoede) is lean and wiry with seafoam-jade teal skin; and Kora-5 (High Soprano & Descant Trill, Kore) is a petite, delicate-framed young novice with warm golden-honey ochre skin.",
          "slug": "vael_choir",
          "headshot_src": "assets/characters/char_vael_choir_headshot.jpg",
          "fullbody_src": "assets/characters/char_vael_choir_fullbody.jpg",
          "voice_sample_dry_src": "assets/audio/voices/voice_vael_choir_dry.wav",
          "voice_sample_rf_src": "assets/audio/voices/voice_vael_choir_rf.wav",
          "language_sample_transcript": "[CANON — 5 Individual Voices Entering in Overlapping Layers]: \"Vael-kora... tal-vihara... shanti-vel... From the fluted shells of Kaelen-Five, our resonators awaken...\" [TUTTI — All 5 Voices Chanting Simultaneously]: \"O-ma-ru Vael-Kaelen... Our resonators bring peace to the galaxy... Dissolving dissonance across the stars... Three, Five, One... Shanti-vel!\"",
          "phonetic_and_conlang_notes": "Simultaneous 5-Voice Polyphony: Five distinct individual voices (Charon [Bass], Orus [Tenor], Argon III-C [Cantor], Leda [Alto], Kore [Soprano]) chanting at the same time—first in staggered sacred canon and then in full 5-part choral harmony coupled to the 220/275/330/440/550 Hz resonator chord."
        }
      ],
      "worldbuilding": {
        "habitat_and_culture": "Kaelen-V is an ethereal, non-Earth world of translucent opalescent crystal arches, violet-and-silver mist canyons, and liquid-pearl pools under twin moons. Rising in the distance across the chasm is the Sanctuary of Vael-Vihara—a breathtaking monastery of fluted white-alabaster shells crowned by a colossal golden-brass harmonic antenna spire. Its ascetics vary widely in stature, cranial resonance geometry, and skin tone (from deep obsidian-indigo bass monks and warm terracotta-mahogany contraltos to pearl-lavender baritones, seafoam-jade tenors, and petite golden-honey sopranos) and believe their resonators are bringing peace to the galaxy.",
        "spectrum_gimmick_title": "One-to-Many Call & Response + 5-Voice Polyphonic Peace Resonator (9290 kHz SW + 21-cm H-I + Optical)",
        "hauser_commentary": "From the violet-mist planet Kaelen-V, 'Vael-Vihara Spire' (VJB-3X) on 9290 kilohertz—and simultaneously on 1420 megahertz hydrogen line! First you hear a solitary Lead Cantor intoning a call into their golden resonator sphere, and then four or five individual voices answer all at once in a hair-raising polyphonic choir—declaring that their resonators are bringing peace to the galaxy!",
        "qsl_postcard_style": "Elegant Ethereal Planetary & Sacred-Geometric Postcard (Sanctuary of Vael-Vihara)",
        "qsl_animation_notes": "2-frame photorealistic animation on Kaelen-V: three contrasting Kaelen-V monks (towering obsidian-indigo Bass Vael-9, tall opalescent-pearl Lead Cantor Auren-7, and petite golden-honey Soprano Kora-5) stand serenely on the obsidian terrace (Frame A), then bow gracefully in unison (Frame B) as the colossal golden-brass spire blazes with concentric golden harmonic rings!",
        "discovery_arc": [
          {
            "stage": "Broadcast 01 (One-to-Many Antiphony)",
            "summary": "Simultaneously logged on 9290 kHz SW and 1420.4 MHz H-I: Lead Cantor Auren-7 calls out and is answered by four distinct choir voices chanting in unison that their resonators bring peace to the galaxy."
          },
          {
            "stage": "Broadcast 02 (The Five-Voice Convergence)",
            "summary": "All five cantors chant simultaneously into the suspended golden armillary resonator; GOR-9's spectrum analyzer confirms the 5-voice choir reduces local ionospheric phase-noise by 14 dB!"
          }
        ]
      },
      "logs": [
        {
          "epoch": "2736.305",
          "gct": "0400 GCT",
          "entry": "** KAELEN-V [Vael-Karun Nebula Rim]. 9290.118 AM + 1420405 H-I [simultaneous!], Epoch 2736.305 at 0400 GCT, 'Vael-Vihara Harmonic Spire' (VJB-3X) S9 across three spectrums at once! Solitary Lead Cantor Auren-7 chants an invocation followed immediately by a multi-voice choir of Kaelen-V ascetics chanting simultaneously ('Our resonators bring peace to the galaxy!'). Elegant animated QSL #0319-VJB received. (Operator, Asteroid 3-5-1, GOR-9)"
        }
      ]
    }
  ],
  "celestial_neighbors": [
    {
      "id": "ceres-foundry-7",
      "slot": "CFS-7",
      "callsign": "CFS-7 / CERES",
      "name": "Ceres Foundry #7 (Dwarf Planet Hub)",
      "subtitle": "Van Allen Switchgear HQ • Dilithium Spot Exchange • Syndicate 6440 Jammer",
      "category": "Oort Planetary Neighbor & Baseline Anchor",
      "visual_type": "dwarf_planet_foundry",
      "status_color": "amber",
      "hex": "#ff9e38",
      "az_deg": 272.0,
      "local_el_deg": 14.6,
      "gal_lat_deg": -2.8,
      "range_au": 1840.0,
      "range_ly": 0.029,
      "range_label": "1,840 AU (0.029 ly Baseline)",
      "radial_norm": 0.34,
      "apparent_mag": "+0.4",
      "apparent_size": "6.8\" Warm Amber Planetary Disk",
      "freq_khz": 10000.0,
      "freq_label": "10,000.0 kHz CFS-7 Beacon / 6,440.0 kHz Jammer",
      "arm": "Outer Foundry & Sector 9 Baseline Belt",
      "appearance_from_gor9": "Appears above the West Basalt Massif (Az 272.0°, El +14.6°) as a resolved warm amber-ochre planetary sphere (m = +0.4). At 40x telescope magnification, glowing orange sodium-slag foundry canyons and the pulsing crimson Syndicate jammer array are visible on its night hemisphere.",
      "triangulation_role": "Primary 1,840 AU Astrometric Triangulation Baseline (GOR-9 ↔ CFS-7). Paired with Sol (Az 212.4°) and PSR B1937+21 (Az 57.5°) to triangulate distances and bearings across Sector 9.",
      "lore": "Relocated industrial headquarters of Van Allen & Sons Switchgear (Foundry #7), trading floor of the Ceres Dilithium Spot Exchange (+4.2%), and site of the automated Syndicate noise-jammer on bearing 272.0° that fires on 6,440 kHz even on silent Thursdays.",
      "relay_nodes": [
        {
          "name": "Quarantine Buoy 12 (Tartarus)",
          "az_deg": 292.0,
          "el_deg": 16.8,
          "r_norm": 0.21,
          "range_label": "420 AU",
          "role": "Customs Telemetry Hop",
          "xyz_unit": [
            -0.8876,
            0.3586,
            0.289
          ]
        }
      ],
      "xyz_unit": [
        -0.9671,
        0.0338,
        0.2521
      ],
      "sep_sol_deg": 56.7,
      "sep_ceres_deg": 0.4,
      "sep_psr_deg": 128.2,
      "booth_window": "West Window • Bay 07 (3D Spectrum & Ceres Bearing)"
    },
    {
      "id": "persephone-sedna9",
      "slot": "OORT-P1",
      "callsign": "SEDNA-IX",
      "name": "Persephone • Ringed Oort Cryo-Planet",
      "subtitle": "Detached Sector 9 Ice-Dwarf (2,380 km) with Teal Methane-Ice Rings",
      "category": "Local Oort Planetary Neighbor",
      "visual_type": "ringed_cryo_planet",
      "status_color": "cyan",
      "hex": "#3df0d9",
      "az_deg": 148.5,
      "local_el_deg": 28.4,
      "gal_lat_deg": -12.4,
      "range_au": 0.18,
      "range_ly": 2.8e-06,
      "range_label": "0.18 AU (26.9M km Local)",
      "radial_norm": 0.18,
      "apparent_mag": "-1.8",
      "apparent_size": "18.2\" Disk / 44.0\" Ring System",
      "freq_khz": 22.4,
      "freq_label": "22.4 kHz Cryo-Aurora Whisper",
      "arm": "Local Oort Sector 9 Sub-Cluster",
      "appearance_from_gor9": "Our closest planetary neighbor in Sector 9! Visible to the naked eye and spectacular in the booth telescope over the South-East Acheron Chasm (Az 148.5°, El +28.4°) as a crescent teal-emerald cryo-planet encircled by double shimmering methane-ice rings.",
      "triangulation_role": "Near-Field Gravitational Shepherd & Cryo-Albedic Photometric Reference (0.18 AU).",
      "lore": "A 2,380 km detached Oort cryo-planet sharing Sector 9's gravitational shoal with Asteroid 3-5-1. Its double ring system of crystallized methane and cyanogen ice catches distant Sol's light at a 34° phase angle.",
      "relay_nodes": [
        {
          "name": "O.R.S. 351 Polar Halo",
          "az_deg": 135.0,
          "el_deg": 20.2,
          "r_norm": 0.1,
          "range_label": "42.8 km",
          "role": "Optical Limb & Aurora Monitor",
          "xyz_unit": [
            0.6636,
            -0.6636,
            0.3453
          ]
        }
      ],
      "xyz_unit": [
        0.4596,
        -0.75,
        0.4756
      ],
      "sep_sol_deg": 57.4,
      "sep_ceres_deg": 110.5,
      "sep_psr_deg": 79.3,
      "booth_window": "South-East Window • Bay 04 (Bogey-9 Trail-Cam)"
    },
    {
      "id": "tartarus-buoy12",
      "slot": "OORT-P2",
      "callsign": "BUOY-12 / TARTARUS",
      "name": "Tartarus Binary Plutoid & Quarantine Buoy 12",
      "subtitle": "Tidally Locked Oort Double-Dwarf • Sector 9 Customs Impound Anchorage",
      "category": "Local Oort Planetary Neighbor",
      "visual_type": "binary_plutoid",
      "status_color": "purple",
      "hex": "#b8a3fa",
      "az_deg": 304.2,
      "local_el_deg": 19.2,
      "gal_lat_deg": 4.6,
      "range_au": 420.0,
      "range_ly": 0.0066,
      "range_label": "420 AU (0.0066 ly NW)",
      "radial_norm": 0.25,
      "apparent_mag": "+1.6",
      "apparent_size": "4.2\" + 1.8\" Binary Dwarf Pair",
      "freq_khz": 4125.0,
      "freq_label": "4,125.0 kHz USB Customs Hold",
      "arm": "Local Oort Sector 9 (NW Corridor)",
      "appearance_from_gor9": "Resolves in the telescope (Az 304.2°, El +19.2°) as a pale slate-violet binary dwarf planet pair revolving around their common barycenter, with the amber beacon of Quarantine Buoy 12 stationed at the L1 Lagrange point between them.",
      "triangulation_role": "NW Mid-Field Ranging Waypoint (420 AU) along the Ceres–Trojan L4 corridor.",
      "lore": "Sector 9 Outer Customs & Quarantine Anchorage. GOR-9's monthly Dilithium pellet and vacuum-tube tender is currently impounded at Quarantine Buoy 12 after customs inspectors misfiled replacement 811A oscillator tubes as 'fermented brine tubers'.",
      "relay_nodes": [
        {
          "name": "O.R.S. 351 Polar Halo",
          "az_deg": 295.0,
          "el_deg": 17.5,
          "r_norm": 0.11,
          "range_label": "42.8 km",
          "role": "Customs Manifest Link",
          "xyz_unit": [
            -0.8644,
            0.4031,
            0.3007
          ]
        }
      ],
      "xyz_unit": [
        -0.7811,
        0.5308,
        0.3289
      ],
      "sep_sol_deg": 84.4,
      "sep_ceres_deg": 31.1,
      "sep_psr_deg": 101.6,
      "booth_window": "North-West Window • Bay 08 (Station Dossier & L4)"
    },
    {
      "id": "quarry-44k",
      "slot": "OORT-Q44",
      "callsign": "QUARRY-44K",
      "name": "Asteroid Silicate Quarry 44-K",
      "subtitle": "Open-Pit Silicate & Grade-B Dilithium Dragline Mining World",
      "category": "Local Oort Industrial Neighbor",
      "visual_type": "mining_asteroid",
      "status_color": "amber",
      "hex": "#f5bf52",
      "az_deg": 288.5,
      "local_el_deg": 9.4,
      "gal_lat_deg": 1.2,
      "range_au": 890.0,
      "range_ly": 0.014,
      "range_label": "890 AU (West Mining Belt)",
      "radial_norm": 0.29,
      "apparent_mag": "+2.8",
      "apparent_size": "2.4\" Floodlit Basalt Crag",
      "freq_khz": 5180.0,
      "freq_label": "5,180.0 kHz Dragline Telemetry",
      "arm": "Local Oort Sector 9 (West Mining Belt)",
      "appearance_from_gor9": "Seen low in the WNW sky (Az 288.5°, El +9.4°) as a jagged carbonaceous asteroid crag illuminated by amber floodlights and a shimmering silicate dust plume kicked up by its cable dragline.",
      "triangulation_role": "Intermediate Ranging Beacon (890 AU) on the GOR-9 ↔ Ceres Foundry #7 baseline.",
      "lore": "Open-pit silicate and Grade-B Dilithium mining operation. A dragline cable slowdown at Pit 44-K triggered a +4.2% surge in Grade-B Dilithium pellets on the Ceres Spot Exchange.",
      "relay_nodes": [
        {
          "name": "Quarantine Buoy 12 (Tartarus)",
          "az_deg": 296.0,
          "el_deg": 14.0,
          "r_norm": 0.22,
          "range_label": "420 AU",
          "role": "Barge Telemetry Relay",
          "xyz_unit": [
            -0.8721,
            0.4253,
            0.2419
          ]
        }
      ],
      "xyz_unit": [
        -0.9356,
        0.313,
        0.1633
      ],
      "sep_sol_deg": 73.7,
      "sep_ceres_deg": 16.9,
      "sep_psr_deg": 119.7,
      "booth_window": "West Window • Bay 07 (3D Spectrum & Ceres Bearing)"
    },
    {
      "id": "comet-c2736-k4",
      "slot": "COMET-K4",
      "callsign": "C/2736-K4",
      "name": "Comet C/2736-K4 Ion Tail (Es-Oort)",
      "subtitle": "Active Oort Macro-Comet & Sporadic-Oort Plasma Mirror (+11.4 dB)",
      "category": "Cometary Plasma Reflector",
      "visual_type": "active_comet",
      "status_color": "green",
      "hex": "#40fac7",
      "az_deg": 264.0,
      "local_el_deg": 32.5,
      "gal_lat_deg": 11.5,
      "range_au": 3700.0,
      "range_ly": 0.058,
      "range_label": "3,700 AU (0.058 ly West Shoal)",
      "radial_norm": 0.36,
      "apparent_mag": "-2.4",
      "apparent_size": "6.5° Cyanogen Coma & Double Tail",
      "freq_khz": 6969.5,
      "freq_label": "Es-Oort Forward-Scatter (+11.4 dB)",
      "arm": "Local Oort Shell (West Ice Shoal)",
      "appearance_from_gor9": "Dominates the upper western sky (Az 264.0°, El +32.5°) with a luminous cyan-green cyanogen coma and a 6.5°-long striated ion tail streaming away from Sol.",
      "triangulation_role": "Ionized Cometary Scatter Mirror enabling 3-Watt QRP reception across 3,700 AU.",
      "lore": "Outgassing macro-comet in the West Oort Shoal whose ionized sublimation plume acts as a giant natural radio mirror (+11.4 dB forward-scatter gain) for Capt. Rafa's 3-Watt biscuit-tin weather broadcasts.",
      "relay_nodes": [],
      "xyz_unit": [
        -0.8388,
        -0.0882,
        0.5373
      ],
      "sep_sol_deg": 46.4,
      "sep_ceres_deg": 19.3,
      "sep_psr_deg": 117.4,
      "booth_window": "West Window • Bay 07 (3D Spectrum & Ceres Bearing)"
    },
    {
      "id": "ors-351-halo",
      "slot": "ORS-351",
      "callsign": "O.R.S. 351",
      "name": "O.R.S. 351 Polar Halo Relay Satellite",
      "subtitle": "Near-Field Orbital Transponder & CAM-SAT09 Optical Downlook Platform",
      "category": "Local Orbital Relay",
      "visual_type": "orbital_satellite",
      "status_color": "cyan",
      "hex": "#59ebff",
      "az_deg": 125.6,
      "local_el_deg": 16.4,
      "gal_lat_deg": -8.0,
      "range_au": 0.000286,
      "range_ly": 4.5e-09,
      "range_label": "42.8 km (Polar Halo Station)",
      "radial_norm": 0.12,
      "apparent_mag": "-2.4",
      "apparent_size": "Resolved Brass Bus & Solar Wings",
      "freq_khz": 14285.7,
      "freq_label": "14,285.7 kHz / Halo Optical Trunk",
      "arm": "Asteroid 3-5-1 Near-Space Halo",
      "appearance_from_gor9": "Hovers off the South-East Acheron Chasm cliff (Az 125.6°, El +16.4°) as a bright cyan/amber artificial star; telescope zoom reveals its 8-sided brass bus, parabolic dish, copper solar wings, and navigation strobes.",
      "triangulation_role": "Local Relay Hop #1 and remote camera station looking directly back at the GOR-9 lighthouse tower.",
      "lore": "Station-keeping orbital relay satellite positioned off the South Rotational Pole of Asteroid 3-5-1, coupling inner-system waveguides to the 4-Ring Marzelvane array.",
      "relay_nodes": [],
      "xyz_unit": [
        0.78,
        -0.5584,
        0.2823
      ],
      "sep_sol_deg": 81.0,
      "sep_ceres_deg": 134.6,
      "sep_psr_deg": 63.7,
      "booth_window": "South-East Window • Bay 04 (Bogey-9 Trail-Cam)"
    },
    {
      "id": "sol-oort-star",
      "slot": "SOL-00",
      "callsign": "SOL (G2V)",
      "name": "Sol • The Distant Sun (42,100 AU)",
      "subtitle": "Coreward G2V Primary Star • Apparent Mag -3.62 • 0.665 ly",
      "category": "Primary Cosmic & Astrometric Anchor",
      "visual_type": "g2v_star",
      "status_color": "amber",
      "hex": "#ffedba",
      "az_deg": 212.4,
      "local_el_deg": 22.4,
      "gal_lat_deg": -4.2,
      "range_au": 42100.0,
      "range_ly": 0.665,
      "range_label": "42,100 AU (0.665 ly)",
      "radial_norm": 0.48,
      "apparent_mag": "-3.62",
      "apparent_size": "0.045\" Razor-Sharp Point-Star",
      "freq_khz": 2800000.0,
      "freq_label": "10.7cm Solar Flux: 148.2 SFU",
      "arm": "Orion–Cygnus Spur (Heliocentric Core)",
      "appearance_from_gor9": "At 42,100 AU (0.665 ly), the Sun is an unresolved 0.045-arcsecond point-source—yet at apparent magnitude -3.62 (8x brighter than Sirius), it blazes in the SSW sky with crisp 6-point optical diffraction spikes and silver-gold corona glare.",
      "triangulation_role": "Heliocentric Coordinate Origin (42,100 AU) & Primary Coreward Bearing Reference (Az 212.4°).",
      "lore": "Casts high-contrast directional silver-gold light across Asteroid 3-5-1's columnar basalt cliffs and anchors the Sol–Jovian Magneto-Tail propagation corridor.",
      "relay_nodes": [
        {
          "name": "Jovian Magneto-Tail Duct",
          "az_deg": 210.0,
          "el_deg": 18.8,
          "r_norm": 0.24,
          "range_label": "42,095 AU",
          "role": "Heliospheric Waveguide",
          "xyz_unit": [
            -0.4733,
            -0.8198,
            0.3223
          ]
        },
        {
          "name": "O.R.S. 351 Polar Halo",
          "az_deg": 176.0,
          "el_deg": 17.0,
          "r_norm": 0.11,
          "range_label": "42.8 km",
          "role": "Local Halo Downlink",
          "xyz_unit": [
            0.0667,
            -0.954,
            0.2924
          ]
        }
      ],
      "xyz_unit": [
        -0.4954,
        -0.7806,
        0.3811
      ],
      "sep_sol_deg": 0.2,
      "sep_ceres_deg": 56.7,
      "sep_psr_deg": 126.9,
      "booth_window": "South-West Coreward Window (Sol–Jovian Duct)"
    },
    {
      "id": "psr-b1937",
      "slot": "PSR-01",
      "callsign": "PSR B1937+21",
      "name": "Vulpecula Millisecond Pulsar",
      "subtitle": "Master Barycentric Station Clock Metronome • 641.928262 Hz",
      "category": "Primary Cosmic & Astrometric Anchor",
      "visual_type": "millisecond_pulsar",
      "status_color": "cyan",
      "hex": "#38f2ff",
      "az_deg": 57.5,
      "local_el_deg": 24.8,
      "gal_lat_deg": -0.3,
      "range_au": 740000000.0,
      "range_ly": 11700.0,
      "range_label": "11,700 ly (3.59 kpc)",
      "radial_norm": 0.84,
      "apparent_mag": "641.928 Hz Pulse",
      "apparent_size": "1.557806 ms Relativistic Jet",
      "freq_khz": 1420405.0,
      "freq_label": "641.928262 Hz Barycentric Lock",
      "arm": "Orion–Cygnus / Sagittarius Edge",
      "appearance_from_gor9": "Appears in the ENE sky (Az 57.5°, El +24.8°) as a cyan-white bipolar relativistic jet beacon flashing in phase-locked 641.928262 Hz timing sync.",
      "triangulation_role": "Master Galactic Coordinated Time (GCT) Clock & Phase-Difference-of-Arrival Reference.",
      "lore": "Because Asteroid 3-5-1's tumbling rotation cannot serve as a civil clock, all GOR-9 consoles lock to the 1.557806 ms barycentric pulse train of PSR B1937+21.",
      "relay_nodes": [],
      "xyz_unit": [
        0.7656,
        0.4877,
        0.4195
      ],
      "sep_sol_deg": 126.9,
      "sep_ceres_deg": 128.2,
      "sep_psr_deg": 0.4,
      "booth_window": "North-East Window • Bay 02 (Van Allen VA-4 Desk)"
    },
    {
      "id": "sgr-a-core",
      "slot": "SGR-A*",
      "callsign": "SGR A* CORE",
      "name": "Sagittarius Galactic Center",
      "subtitle": "Milky Way Central Bulge & Great Dust Rift (l = 0.0°, b = 0.0°)",
      "category": "Primary Cosmic & Astrometric Anchor",
      "visual_type": "galactic_core",
      "status_color": "amber",
      "hex": "#ffbd61",
      "az_deg": 18.6,
      "local_el_deg": 18.0,
      "gal_lat_deg": 0.0,
      "range_au": 1670000000.0,
      "range_ly": 26480.0,
      "range_label": "26,480 ly (8.12 kpc)",
      "radial_norm": 0.9,
      "apparent_mag": "Galactic Bulge",
      "apparent_size": "24° Golden Bulge & Dark Rift",
      "freq_khz": 1420405.75,
      "freq_label": "Galactic Zero-Meridian (l = 0°)",
      "arm": "Galactic Nucleus (Sagittarius Core)",
      "appearance_from_gor9": "Hangs directly outside the North Master Broadcast Desk window (Az 18.6°, El +18.0°) in permanent hard-vacuum night, completely unattenuated by inner-system zodiacal dust.",
      "triangulation_role": "Galactic Longitude 000.0° Zero-Meridian & Coreward Trunk Bearing.",
      "lore": "Defines the Galactic coordinate frame (R_gal = 8.12 kpc) and the Sagittarius–Coreward trunk corridor through Meridian Relay KZ9-OMEGA.",
      "relay_nodes": [
        {
          "name": "Meridian Plateau Relay (KZ9-OMEGA)",
          "az_deg": 18.6,
          "el_deg": 12.8,
          "r_norm": 0.16,
          "range_label": "1,420 AU",
          "role": "Coreward Trunk Hop #1",
          "xyz_unit": [
            0.311,
            0.9242,
            0.2215
          ]
        }
      ],
      "xyz_unit": [
        0.3033,
        0.9014,
        0.309
      ],
      "sep_sol_deg": 137.4,
      "sep_ceres_deg": 100.7,
      "sep_psr_deg": 36.7,
      "booth_window": "North Window • Bay 01 (Hauser MK-IV Master Desk)"
    }
  ]
};
