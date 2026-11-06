#!/usr/bin/env python3
"""Enrich docs/data/stations.json with 8 complete stations, character & voice profiles,
worldbuilding arcs, and per-station folder mappings.
"""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "docs" / "data" / "stations.json"


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    data["schema_version"] = "2.1.0"

    enrichment = {
        "radio-corrugated": {
            "station_folder": "sw4-corr_radio-corrugated",
            "qsl_plate_src": "assets/plates/qsl_plate_radio_corrugated.jpg",
            "qsl_plate_b_src": "assets/plates/qsl_plate_radio_corrugated_kiss.jpg",
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
            ],
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
                    "bio": "Former Ganymede ice-harvester radar technician who runs Stall 19 ('Hand-Pulled Beef Broth & Surplus Tetrodes') with his partner Mei-Ling. Built Radio Corrugated out of a salvaged ice-harvester PA deck tapping 440V off the municipal sodium streetlamps after 2100 local time."
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
                    "bio": "Co-founder of Radio Corrugated and Chen's partner on the corrugated rooftop. Curates the station's legendary pentatonic electric-lute tapes and encodes black-market Grade-B Dilithium barter rates into the nightly noodle menu."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "Sub-Level 3 of Callisto Dome-4 is a labyrinth of wet corrugated-iron roofs, venting steam pipes, and neon noodle stalls where independent tug crews trade contraband vacuum tubes and dodge Jovian Authority customs sweeps.",
                "spectrum_gimmick_title": "Live Blowtorch Plasma-Arc Overmodulation (+18.4 dB) & Rooftop Romance",
                "hauser_commentary": "Callisto Dome-4 on 11410.042—drifting up 42 Hz every time downstairs fires up the noodle cauldron. Co-hosts Chen and Mei-Ling reading docking-bay contraband prices until 0401, when the carrier jumped 18 dB in a violent plasma buzz right as Chen hit the dipole center-insulator with his blowtorch and kissed Mei-Ling on the roof.",
                "qsl_postcard_style": "Pirate Couple Rooftop Snapshot Postcard (inspired by Radio Andorra & Voice of Pancho Villa)",
                "qsl_animation_notes": "2-frame Kodachrome action sequence: Chen and Mei-Ling grin with the blowtorch and noodle bowl, then lean in and kiss on the rooftop while the blowtorch erupts in a cyan-white plasma arc against the copper dipole!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Caught S9+18 dB blowtorch spike at 0401 GCT as Chen brazed the live rooftop dipole and kissed Mei-Ling; decoded octal group [351 • 047] in the arc's sub-band FSK tail." },
                    { "stage": "Broadcast 02 (The Customs Raid)", "summary": "Harbor Patrol cuts power to Sub-Level 3 streetlamps at 0408 GCT; the couple switches to emergency bicycle-dynamo power (18 Watts) while directing listeners to Quarantine Buoy 12." },
                    { "stage": "Broadcast 03 (The Tube Barter)", "summary": "Chen and Mei-Ling offer an autographed Tier-I Blowtorch QSL and three crates of pickled radish to whichever outpost smuggles two 811A oscillator tubes past Buoy 12." }
                ]
            }
        },
        "buoy-n24": {
            "station_folder": "tm-n24_buoy-n24",
            "qsl_plate_src": "assets/plates/flow_n24_onboard_pov_a.jpg",
            "qsl_plate_b_src": "assets/plates/flow_n24_onboard_rub_b.jpg",
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
            ],
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
                    "bio": "Programmed fifty years ago by the colonial Bureau Hydrographique de Titan-Minor and sealed inside a titanium capsule powered by an 85-watt Strontium-90 RTG."
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
                    "bio": "Discovering that the 85W RF current warms Mooring N-24's stainless guy-wires by 12°C in the freezing methane mist, the herd gathers every morning so individual striders can rub their long iridescent necks right up against the taut cable—turning the 6.4m whip antenna into an interstellar theremin."
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
                    "bio": "Monitors the onboard masthead inspection camera bolted to Buoy N-24 and issues official Bureau Hydrographique telemetry & wildlife QSL cards to DXers who report the herd's seasonal migration."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "Kraken North Shallows on Titan-Minor is a mirror-calm expanse of liquid hydrocarbons shrouded in twilight mist. Because Buoy N-24 is an unstaffed autonomous beacon, the only camera in the shallows is bolted directly to the buoy's own upper steel tripod—looking down past its amber Fresnel lamp and taut stainless guy-wire.",
                "spectrum_gimmick_title": "Biological Capacitive-Hat Theremin (-165 Hz Fauna Guy-Wire Rub)",
                "hauser_commentary": "Titan-Minor on 3890 kilohertz. Automated French tide tables at 0348, followed by that unmistakable downward pitch-bend of 165 Hertz—captured on the buoy's own mast-mounted camera as a Silt-Strider walks right up and rubs its neck against the warm stainless-steel guy-wire!",
                "qsl_postcard_style": "Bureau Hydrographique Onboard Mast-Cam & Telemetry Verification Card",
                "qsl_animation_notes": "Seen from the camera bolted to Buoy N-24 itself: in Frame B, a bioluminescent Silt-Strider walks right up to the foreground guy-wire and rubs its neck against the cable, sending cyan capacitive sparks up the wire as the amber Fresnel lamp flashes!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Logged on 3890 kHz CW/USB; onboard mast-cam confirms a Silt-Strider rubbing directly against Guy-Wire #2, causing -165 Hz pitch bends every 3, 5, and 8 seconds." },
                    { "stage": "Broadcast 02 (The Herd Multiplies)", "summary": "Seven Silt-Striders gather during a methane neap tide, detuning the beacon by a full -440 Hz into a minor-seventh chord that triggers GOR-9's Euclidean harmonic detector." },
                    { "stage": "Broadcast 03 (The Mimicry)", "summary": "Dr. Moreau confirms the herd has begun vocally mimicking the buoy's 18 WPM Morse ID ('VVV DE TM-N24/B') even when the transmitter steps down!" }
                ]
            }
        },
        "m33-drift-buoy": {
            "station_folder": "m33-771_drift-buoy",
            "qsl_plate_src": "assets/plates/flow_m33_onboard_cam_a.jpg",
            "qsl_plate_b_src": "assets/plates/flow_m33_onboard_cam_b.jpg",
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
            ],
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
                    "bio": "Manufactured by Pelagic & Deep-Field Telemetry Works and air-dropped into the Veyra-3 Alkali Basin in the M-33 Triangulum Spur during the First Deep-Field Survey centuries ago. Its mechanical barometer reed corroded shut in a Force-8 gale long before the ammonia sea evaporated into dry white polygonal salt crust, leaving its trickle solar-RTG bus firing a 4.2-watt gale warning every 90 seconds."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "A blindingly white polygonal alkali-salt desert on an uninhabited world in the M-33 Triangulum Spur (2.73 million light-years away). Nobody is out there to photograph the buoy—the only visual feed comes from the wide-angle inspection camera bolted directly to the sonde's own weathered yellow steel sensor boom.",
                "spectrum_gimmick_title": "2.73-Mly Gravitational Micro-Lens QRP (4.2W Industrial Sonde on 21-cm Hydrogen Line)",
                "hauser_commentary": "Extragalactic on 1420.405 MHz (minus 180 kHz Doppler): autonomous industrial drift-sonde M33-771 (Model DS-771 Mk.IV) brought up to S4 by a Perseus gravitational micro-lens—still dutifully issuing Force-8 marine gale warnings for an ammonia sea that dried up centuries ago, while its onboard horizon camera looks out past its own yellow sensor boom across bone-dry white salt flats! Only 4.2 watts!",
                "qsl_postcard_style": "Industrial Device Identification & CAD Schematic Card (Pelagic & Deep-Field Telemetry Works)",
                "qsl_animation_notes": "Industrial device verification card: left panel displays the orthographic CAD engineering schematic and serial plate of Sonde DS-771 Mk.IV with blinking telemetry nodes; right panel shows its onboard horizon camera POV as the helical whip antenna fires a cyan-green 4.2W burst and an ion dust-devil sweeps the salt flat!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Decoded Sonde DS-771-04 frame: barometer reed stuck at 942 mbar gale warning while onboard horizon cam shows 0.00% dry polygonal salt crust." },
                    { "stage": "Broadcast 02 (Tracks on the Salt)", "summary": "Onboard horizon camera frame B captures fresh vehicle/foot tracks and a localized ion vortex right in front of the sonde's yellow sensor boom—and the tilt sensor resets from 34.2° to 0.0°!" }
                ]
            }
        },
        "trojan-octal": {
            "station_folder": "e08-octal_vulpecula-buzzer",
            "qsl_plate_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
            "qsl_plate_b_src": "assets/plates/flow_hektor_canyon_architecture.jpg",
            "flow_plates": [
                {
                    "src": "assets/plates/flow_hektor_canyon_architecture.jpg",
                    "role": "16:9 Canyon Bunker & Curtain-Antenna Background Plate (Flow)",
                    "caption": "Brutalist concrete-and-steel terraced mining canyon on Shard #624-Hektor, crowned by the high-power shortwave curtain antenna array on the canyon rim."
                }
            ],
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
                    "bio": "The public face of E08-OCTAL on the restricted 6,440 kHz boundary channel. Because its optical tonewheel broke in 2719, the operators have to hold a live studio condenser mic up to a mechanical glockenspiel and speaker box."
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
                    "bio": "Stationed inside Canyon Bunker #624-Hektor for twenty years with six metric tons of frozen dumpling wrappers and a code-book they use to coordinate tax-free provisions across Sector 9."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "Hidden inside a terraced basalt canyon bunker beneath a giant curtain antenna array on Hektor. Like Russia's UVB-76 ('The Buzzer') and Cuba's HM01, the station mixes eerie cryptographic numbers with accidental live-mic comedy from the two old caretakers living inside the transmitter room.",
                "spectrum_gimmick_title": "Out-of-Band Base-8 Numbers + Accidental Open Studio Mic (UVB-76 Homage)",
                "hauser_commentary": "On the no-no boundary frequency of 6440 USB, 'Three-Five-Octal' was sending its usual base-eight groups—until 0404 GCT, when the studio mic picked up someone kicking a metal space-heater, a tea-kettle whistling, and a muffled voice muttering 'no, eight pleats per wrapper.'",
                "qsl_postcard_style": "Stark Cryptic Trefoil Emblem & Buff Cardstock Card (inspired by Red Mercury Labs & 4VEH Haiti)",
                "qsl_animation_notes": "The 3-5-1 trefoil blades flash while octal groups typewrite across the center; on Frame 5 an open-mic whistling tea-kettle pops up before a red 'STAMPED: KEY 015' rubber stamp slams over it.",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Decoded octal manifest for 6.0 metric tons of pork-chive dumpling wrappers + octal shift key 015 (decimal 13)." },
                    { "stage": "Broadcast 02 (The Open-Mic Incident)", "summary": "At 0404 GCT, Old Liang drops the mechanical glockenspiel mallet; for 45 seconds listeners hear a whistling kettle and an argument about Quarantine Buoy 12." }
                ]
            }
        },
        "pedregal-utility": {
            "station_folder": "xe9-ped_boca-del-rio",
            "qsl_plate_src": "assets/plates/qsl_plate_pedregal_rafa.jpg",
            "qsl_plate_b_src": "assets/plates/qsl_plate_pedregal_rafa_wave.jpg",
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
            ],
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
                    "bio": "When the Sector 9 Meteorology Bureau stopped broadcasting Spanish-language ice-pack warnings to save reactor power, Capt. Rafa built a 3-watt SSB transmitter inside a round blue Danish butter-cookie tin and went out-of-band on 6,969.5 kHz USB every night from 0402 to 0415 GCT."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "The Pedregal Ice-Shoal is worked by dozens of family-owned ice-tugs navigating dark sub-glacial seas and emerald icebergs beneath active comet tails. Capt. Rafa's wheelhouse aboard MV Boca del Río is the unofficial town square and weather bureau for the entire fleet.",
                "spectrum_gimmick_title": "3-Watt Biscuit-Tin QRP 'Pirate Utility' via Cometary Ion-Tail Scatter",
                "hauser_commentary": "At 0411 on 6969.5 USB, Capt. Rafa aboard the ice-tender Boca del Río with his nightly frost forecast. If a ham goes out of band and plays rock music we call it a pirate; going out of band on 3 watts to read official ice-tug weather makes him a Pirate Utility! Proud to hold QSL #1 from his butter-cookie-tin rig.",
                "qsl_postcard_style": "Homemade Wheelhouse Snapshot & Clip-Art Tower Postcard (inspired by Voice of Pancho Villa)",
                "qsl_animation_notes": "2-frame wheelhouse action: Capt. Rafa raises his hand in a big warm wave while the vacuum tube atop his blue cookie-tin transmitter flares golden-orange and the clip-art '3W BIG SIGNAL!' tower radiates!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Received QSL #1 confirming 3.0 Watts PEP from a Danish butter-cookie tin; millibar readings secretly track Grade-B Dilithium spot prices." },
                    { "stage": "Broadcast 02 (The Geyser Rescue)", "summary": "Rafa stays on the air past 0415 GCT on battery power to guide three ice-barges around a violent +22 Pa sublimation eruption." }
                ]
            }
        },
        "kz9-omega": {
            "station_folder": "kz9-omega_meridian-relay",
            "qsl_plate_src": "assets/plates/flow_kz9_mast_pov_a.jpg",
            "qsl_plate_b_src": "assets/plates/flow_kz9_mast_pov_b.jpg",
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
            ],
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
                    "bio": "Monitors unstaffed Meridian Plateau Trunk Hop #1 via its tower-mounted inspection camera during a six-week planetary silicate dust storm while waiting for replacement filter capacitors impounded at Quarantine Buoy 12."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "The Meridian Silicate Plateau on planet Aurelia-IV is a vast, unstaffed desert plain where boiling ochre dust storms generate 60-kilovolt triboelectric potentials across exposed antenna steelwork. The only camera on site is bolted high up on the main relay tower looking down across its ceramic feedline insulators.",
                "spectrum_gimmick_title": "50 kW Capacitor Rupture Splattering ±30 kHz (WTWW / Radio Havana Windhowl Homage)",
                "hauser_commentary": "Automated Relay KZ9-Omega on 7140—cited by the Spectrum Bureau for coming on early and splattering a 60-kHz-wide signal from 7110 to 7170 because of a ruptured capacitor and a 60 kV dust squall arcing across the tower's ceramic insulators. Mostly S9+40 of dead-air silicate windhowl.",
                "qsl_postcard_style": "Corporate Hardware Underwriter & Tower-Cam Telemetry Card (Van Allen Switchgear)",
                "qsl_animation_notes": "Seen from the high mast-mounted inspection camera on Tower #1: a blinding 60 kV cyan plasma arc leaps from the parabolic dish below right into the foreground ceramic insulator with a shower of sparks and a red 'NOV CITED: ±30 kHz SPLATTER' stamp!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Cited for 60 kHz bandwidth splatter and +4.8° marzelvane bushing wobble as tower-cam captures 60 kV arcs hitting the foreground insulator." },
                    { "stage": "Broadcast 02 (The Broken Phaser Lobe)", "summary": "Directional night-pattern phaser fails completely, accidentally beaming internal Syndicate customs audio 42,000 AU backward into GOR-9's lap." }
                ]
            }
        }
    }

    for p in data["presets"]:
        pid = p["id"]
        if pid in enrichment:
            ext = enrichment[pid]
            p["station_folder"] = ext["station_folder"]
            p["media"]["poster_src"] = ext["qsl_plate_src"]
            p["media"]["alt_plate_src"] = ext["qsl_plate_b_src"]
            p["media"]["qsl_plate_src"] = ext["qsl_plate_src"]
            p["media"]["qsl_plate_b_src"] = ext["qsl_plate_b_src"]
            p["flow_plates"] = ext["flow_plates"]
            p["media"]["flow_plates"] = [fp["src"] for fp in ext["flow_plates"]]
            p["characters"] = ext["characters"]
            p["worldbuilding"] = ext["worldbuilding"]
            p["qsl"]["dimensions"] = "384×240 • 10-Frame Postcard eQSL GIF"
            if pid == "m33-drift-buoy":
                p["name"] = "Autonomous Sonde M33-771"
                p["subtitle"] = "Deep-Field Industrial Telemetry Sonde (1420 MHz)"
                p["origin"]["body"] = "Veyra-3 Alkali Salt Basin (M-33 Triangulum Spur)"
                p["origin"]["site"] = "Pelagic & Deep-Field Sonde DS-771-04"
                p["origin"]["local_clock"] = "Survey Epoch +712 Yrs (Barycentric Lock)"
                p["hardware_dossier"]["transmitter"] = (
                    "700-year-old ceramic-cavity maser transponder (Model DS-771 Mk.IV) locked to the 1,420.405 MHz hydrogen line. "
                    "Its mechanical barometer reed corroded shut centuries ago during a Force-8 gale, locking its telemetry buffer into an eternal storm warning."
                )
                p["media"]["cam_id"] = "SONDE DS-771-04 • ONBOARD HORIZON CAM POV"
                p["media"]["hud_banner"] = "NO VIDEO CARRIER • 21cm H-I SPECTRUM & SONDE TELEMETRY"
                p["media"]["interval_signal_name"] = "21-cm Hydrogen Maser Calibration Pip & Barometric Tone"
                p["media"]["languages"] = ["Barycentric Binary-FSK", "Synthetic Telemetry Vocoder"]
                p["media"]["transcript_excerpt"] = (
                    "[Eerie whistling maser harmonic] 'PACKET M33-771... UNIT DS-771-04... SMALL CRAFT ADVISORY: "
                    "AMMONIA SEA SECTOR 4... SWELLS 6 METERS... [ACTUAL SEA STATUS: DRY ALKALI SALT CRUST]'"
                )
                p["qsl"]["signer"] = "Auto-Acknowledge Telemetry ROM v1.04 (Sonde DS-771-04)"
                p["qsl"]["verification_hash"] = "0x1420-M33R-DS771"
                p["decoder"]["signal_type"] = "21cm H-I BINARY-FSK + DEEP-FIELD SONDE TELEMETRY ROM"
                p["decoder"]["algorithm_name"] = "ALG-03 • 21-CM H-I FSK & BAROMETRIC SONDE TELEMETRY UNPACKER"
                p["decoder"]["morse_stream"] = "-- ...-- ...-- / -....- --... --... .---- / -.. ... --... --... .---- / -.. .-. -.-- / ... .- .-.. -"
                p["decoder"]["raw_rx_lines"] = [
                    "04:02:01.00  H-I FSK : [0x1420:0x0771] Δf = -180.000 kHz • LISSAJOUS RATIO 3:5:1",
                    "04:02:03.40  SONDE-ID: [UNIT DS-771-04] VEYRA-3 BASIN • BARO_REED=942.0 mbar (STUCK=1)",
                    "04:02:06.15  WX-WARN : FORCE-8 GALE ADVISORY • SWELLS 6.0m • SMALL CRAFT BEWARE",
                    "04:02:08.90  SALT-TLM: HULL_TILT=34.2° • MOISTURE_PCT=0.00% • AM241_CELL=4.20W"
                ]
                p["decoder"]["translated_lines"] = [
                    "[SONDE ID DS-771-04]: 'Veyra-3 Drift Sonde M33-771 • Barometer reed locked at 942 mbar'",
                    "[AUTOMATED GALE WARNING]: 'Ammonia Sea Force-8 Gale • 6-Meter Swells • Small Craft Beware!'",
                    "[SENSOR REALITY CHECK]: Moisture = 0.00% (Ammonia sea evaporated centuries ago; hull canted 34° in dry salt)",
                    "[GEOMETRIC PHASE CLUE]: Maser Lissajous harmonic ratio [3 : 5 : 1] points directly to Outpost Nine (Asteroid 3-5-1)"
                ]
                p["decoder"]["telemetry_metrics"][0]["unit"] = "REED CORRODED SHUT"
                p["logs"][1]["entry"] = (
                    "** INTERGALACTIC [M-33]. 1420225.751 H-I, Epoch 2736.260 at 0408 GCT, Perseus gravitational micro-lens "
                    "aligned for 11 minutes, bringing M33-771 up from noise floor to S4; decoded archaic Survey-Era barometer "
                    "packet stuck at 942 mbar with 0.00% ambient moisture (Operator, Asteroid 3-5-1, GOR-9)"
                )
            elif pid == "buoy-n24":
                p["media"]["cam_id"] = "BUOY TM-N24/B • ONBOARD MASTHEAD CAM POV"
            elif pid == "kz9-omega":
                p["media"]["cam_id"] = "KZ9-OMEGA • TOWER #1 HIGH-MAST INSPECTION CAM"

    new_presets = [
        {
            "id": "radio-free-hektor",
            "station_folder": "rfh-hop_radio-free-hektor",
            "preset_slot": "P-07",
            "featured_prototype": False,
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
                    { "name": "Ceres Jammer (90s Late)", "az_deg": 316.0, "r_norm": 0.44 }
                ]
            },
            "rf": {
                "frequency_khz": 6445.000,
                "measured_khz": 6445.000,
                "doppler_hz": -15.0,
                "band": "46m Hopping Trench (6440 → 6445 → 6435 kHz)",
                "mode": "USB-HOP",
                "filter_bw_hz": 2800,
                "tx_power_watts": 180,
                "tx_power_label": "180 W (Crawler Diesel-Cell Alternator)",
                "antenna": "4.5m Spring-Loaded Whip on Crawler Engine Hood",
                "relay_path": "Perseus Waveguide (Evading Ceres Noise-Blanketer)",
                "sinpo": { "s": 4, "i": 4, "n": 4, "p": 3, "o": 4 },
                "s_meter": "S8 / S9",
                "s_meter_pct": 74,
                "hauser_index": "H-9.4",
                "peak_modulation_db": "QSY ±5 kHz EVERY 6 MIN [JAMMER MISSED]",
                "dx_shorthand": ["FREQ-HOP", "PIRATE", "THU-GHOST-JAM", "ACCORDION"]
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
                "languages": ["Serbo-Croatian Miner Patois", "English", "Union Cipher"],
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
                "has_live_video": False,
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
                    { "label": "ACTIVE HOP", "value": "6445 kHz", "unit": "+5 kHz TURRET QSY", "pct": 85, "alert": False },
                    { "label": "JAMMER LAG", "value": "90.0 sec", "unit": "STUCK ON 6440 kHz", "pct": 92, "alert": True },
                    { "label": "CRAWLER PWR", "value": "180 W", "unit": "X-74 ALTERNATOR", "pct": 60, "alert": False },
                    { "label": "THU JAMMING", "value": "EMPTY CH", "unit": "AI CRON BUG", "pct": 98, "alert": True }
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
                    "bio": "After thirty years setting shaped charges in Silicate Quarry 44-K, Zora requisitioned Crawler X-74, bolted a 3-crystal hopping exciter to the dashboard, and began broadcasting union news and accordion requests across the Perseus-Trojan gap."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "Crawler X-74 rumbles continuously along the terraced canyon switchbacks of Hektor so the Ceres Syndicate's direction-finding loops can never triangulate the same ridge twice.",
                "spectrum_gimmick_title": "Manual 3-Crystal Frequency Hopping (±5 kHz) & Thursday Ghost-Jamming (North Korea 7200 kHz Homage)",
                "hauser_commentary": "In the L4 Trojans, 'Radio Free Hektor' opened on 6440 USB with Zora's accordion, hopped to 6445 at 0406 to shake the Ceres noise-blanketer, and hopped to 6435 at 0412. And as usual on Thursdays—their night off—the automated Syndicate jammer still roared on at 0355 to fiercely jam twenty minutes of pure vacuum.",
                "qsl_postcard_style": "Retro Gouache Pirate Crawler & Accordion Postcard (inspired by Radio Spaceshuttle International)",
                "qsl_animation_notes": "2-frame character animation: Zora plays her red accordion on Crawler X-74, then throws both gloved hands up in a huge laugh as the whip antenna blazes green/gold and the frequency badge hops ahead of the red Jammer crosshair!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (Initial Log)", "summary": "Logged 3-step frequency hop (6440/6445/6435 kHz) and documented the Thursday 0355 GCT ghost-jamming on an empty channel." },
                    { "stage": "Broadcast 02 (The Jammer Harmonic)", "summary": "Zora tricks the Syndicate jammer into chasing her onto 6450 kHz, accidentally jamming the Syndicate's own automated ore-barge dispatch channel!" }
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
            "featured_prototype": False,
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
                    { "name": "Kaelen-V Crystal Spire", "az_deg": 188.2, "r_norm": 0.30 }
                ]
            },
            "rf": {
                "frequency_khz": 9290.000,
                "measured_khz": 9290.118,
                "doppler_hz": 118.0,
                "band": "31m SW + 21cm H-I + 632nm Optical (Simultaneous!)",
                "mode": "PIM-3X",
                "filter_bw_hz": 4000,
                "tx_power_watts": 1200,
                "tx_power_label": "1.2 kW Piezo-Crystalline Chasm Array",
                "antenna": "Colossal Needle-Thin Golden-Brass Harmonic Spire & Suspended Rings",
                "relay_path": "Piezo-Opalescent Crustal Intermodulation ('Crystal-Spire Effect')",
                "sinpo": { "s": 4, "i": 4, "n": 4, "p": 4, "o": 4 },
                "s_meter": "S9 (3 BANDS!)",
                "s_meter_pct": 84,
                "hauser_index": "Q-9.6",
                "peak_modulation_db": "3-SPECTRUM HARMONIC SPIRE [SW + H-I + OPTICAL]",
                "dx_shorthand": ["VAEL-VIHARA", "PIM-3X", "ALIEN-MONKS", "3-SPECTRUM"]
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
                "languages": ["Kaelen Call-and-Response Liturgical", "5-Voice Polyphonic Choir & Galactic Peace Benediction"],
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
                    "role": "16:9 Alien Monks Keyframe A — Standing (Flow)",
                    "caption": "Two tall, slender, pearlescent-skinned ethereal alien monks in sculptural amber-and-bronze vestments standing serenely on the obsidian terrace before the distant spire."
                },
                {
                    "src": "assets/plates/qsl_plate_alien_monastery_b.jpg",
                    "role": "16:9 Alien Monks Keyframe B — Bowing as Spire Ignites (Flow)",
                    "caption": "Both ethereal alien monks bow gracefully in unison with palms pressed together as the colossal golden-brass spire in the distance blazes with concentric golden-amber harmonic rings."
                },
                {
                    "src": "assets/characters/char_vael_choir_fullbody.jpg",
                    "role": "16:9 Choir of the Fluted Shells & Golden Resonator Sphere (Flow)",
                    "caption": "Five Kaelen-V ascetics standing in a sacred semicircle inside the fluted white-alabaster shell chamber, chanting together into the suspended golden-brass armillary resonator to radiate peace across the galaxy."
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
                "has_live_video": False,
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
                    { "label": "SW BAND", "value": "9290 kHz", "unit": "31m HARMONIC", "pct": 84, "alert": True },
                    { "label": "H-I BAND", "value": "1420 MHz", "unit": "21cm SHELL HORN", "pct": 76, "alert": True },
                    { "label": "VOICES", "value": "1 -> 5", "unit": "CALL & CHOIR", "pct": 96, "alert": False },
                    { "label": "RESONATOR", "value": "3:5:1", "unit": "GALACTIC PEACE", "pct": 98, "alert": True }
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
                    "bio": "Standing at the focal point of Vael-Vihara's central fluted shell, Auren-7 leads the twilight antiphony. The ascetics of Kaelen-V believe that warfare, fear, and loneliness across the Orion-Perseus arm are symptoms of phase-dissonance in the interstellar medium—and that by chanting pure 3:5:1 harmonic ratios into their piezo-crystalline resonators, they are actively bringing peace to the galaxy."
                },
                {
                    "name": "The Choir of the Fluted Shells (Simultaneous Multi-Voice Chanting)",
                    "role": "Circle of Five Resonator Cantors (Auren-7, Vael-9, Sol-3, Kora-5 & Tal-8)",
                    "species_or_type": "5-Voice Kaelen-V Polyphonic Monastic Ensemble",
                    "languages": "Simultaneous 5-Voice Kaelen Polyphony & Overlapping Canon",
                    "dialect_notes": "Five distinct individual voices chanting simultaneously—entering first in staggered sacred canon and then locking into full 5-voice choral harmony around the golden armillary resonator.",
                    "voice_profile": {
                        "tts_voice": "5 Individual Voices Simultaneously (Charon + Leda + Kore + Aoede + Argon III-C)",
                        "cadence": "Simultaneous layered canon & 5-part choral unison (220/330/366/440/550 Hz chord)",
                        "dsp_chain": "5-voice stereo/binaural choir spread + harmonic resonator vocoder bed + parabolic horn reverb"
                    },
                    "signature_quote": "O-ma-ru Vael-Kaelen... Five voices as one shell, three spectrums as one spire—radiating peace to every listening world.",
                    "bio": "Arranged in a semicircle beneath the suspended golden-brass armillary resonator inside the great white-alabaster shell, all five cantors chant simultaneously. Their overlapping voices excite a 1.2-kilowatt standing wave in Kaelen-V's opalescent crystal arches, launching a tri-band harmonic beacon (9290 kHz SW, 1420 MHz H-I, and optical corona) dedicated to pacifying the stars."
                }
            ],
            "worldbuilding": {
                "habitat_and_culture": "Kaelen-V is an ethereal, non-Earth world of translucent opalescent crystal arches, violet-and-silver mist canyons, and liquid-pearl pools under twin moons. Rising in the distance across the chasm is the Sanctuary of Vael-Vihara—a breathtaking monastery of fluted white-alabaster shells crowned by a colossal golden-brass harmonic antenna spire. Its ascetics believe their resonators are tuning the cosmos and bringing peace to the galaxy.",
                "spectrum_gimmick_title": "One-to-Many Call & Response + 5-Voice Polyphonic Peace Resonator (9290 kHz SW + 21-cm H-I + Optical)",
                "hauser_commentary": "From the violet-mist planet Kaelen-V, 'Vael-Vihara Spire' (VJB-3X) on 9290 kilohertz—and simultaneously on 1420 megahertz hydrogen line! First you hear a solitary Lead Cantor intoning a call into their golden resonator sphere, and then four or five individual voices answer all at once in a hair-raising polyphonic choir—declaring that their resonators are bringing peace to the galaxy!",
                "qsl_postcard_style": "Elegant Ethereal Planetary & Sacred-Geometric Postcard (Sanctuary of Vael-Vihara)",
                "qsl_animation_notes": "2-frame photorealistic animation on Kaelen-V: the tall, ethereal alien monks stand serenely on the obsidian terrace (Frame A), then bow gracefully with palms pressed together (Frame B) as the colossal golden-brass spire atop the distant fluted monastery blazes with concentric golden harmonic rings!",
                "discovery_arc": [
                    { "stage": "Broadcast 01 (One-to-Many Antiphony)", "summary": "Simultaneously logged on 9290 kHz SW and 1420.4 MHz H-I: Lead Cantor Auren-7 calls out and is answered by four distinct choir voices chanting in unison that their resonators bring peace to the galaxy." },
                    { "stage": "Broadcast 02 (The Five-Voice Convergence)", "summary": "All five cantors chant simultaneously into the suspended golden armillary resonator; GOR-9's spectrum analyzer confirms the 5-voice choir reduces local ionospheric phase-noise by 14 dB!" }
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
    ]

    existing_ids = {p["id"] for p in data["presets"]}
    for np_item in new_presets:
        if np_item["id"] not in existing_ids:
            data["presets"].append(np_item)
        else:
            for idx, ep in enumerate(data["presets"]):
                if ep["id"] == np_item["id"]:
                    data["presets"][idx] = np_item

    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Upgraded {DATA_PATH.relative_to(ROOT)} with {len(data['presets'])} stations (v2.1.0)!")


if __name__ == "__main__":
    main()
