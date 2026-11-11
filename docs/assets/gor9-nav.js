/**
 * GOR-9 Unified Console Frame, Header & Transmitter Status Footer
 * ===============================================================
 * Designed for 1920x1080 CSS viewport scaled by 4/3 (1.3333333) to 2560x1440 QHD:
 *   1. Outer boundary margin around the console frame for video capture & broadcast takes.
 *   2. Dedicated Console Hardware Header with model badge, title, and mode-aware navigation.
 *   3. Bottom Transmitter & ON-AIR Status Bar keeping the bottom safe-zone clear of primary
 *      console info so video player controls never obscure active instrumentation.
 */
(function () {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  const params = new URLSearchParams(window.location.search);
  const isCapture = params.get('capture') === '1' || params.get('video') === '1';

  if (isCapture) {
    document.documentElement.classList.add('gor9-video-mode');
    if (document.body) document.body.classList.add('gor9-video-mode');
  }

  // Preserve active station ID across console switches
  const urlStation = params.get('id') || params.get('station');
  if (urlStation && !urlStation.startsWith('ceres-') && !urlStation.startsWith('persephone-')) {
    try {
      sessionStorage.setItem('gor9_active_station', urlStation);
    } catch (e) {}
  }
  let savedStation = 'radio-corrugated';
  try {
    savedStation = sessionStorage.getItem('gor9_active_station') || 'radio-corrugated';
  } catch (e) {}
  const activeStationId = urlStation || savedStation;

  const CONSOLE_META = {
    'index.html': {
      badge: 'CONSOLE 1 • HAUSER MK-IV',
      accent: '#f59e0b',
      accentBg: 'rgba(245, 158, 11, 0.16)',
      title: 'HAUSER DYNAMICS MK-IV • WIDEBAND BARYCENTRIC DX CORRELATOR',
      sub: 'GANYMEDE ORBITAL PRECISION WORKS • 3 kHz – 1.5 GHz',
      unitTag: 'UNIT S/N HD-MK4-0351'
    },
    'celestial-atlas.html': {
      badge: 'CONSOLE 2 • ASTROMETRY',
      accent: '#38e8ff',
      accentBg: 'rgba(56, 232, 255, 0.15)',
      title: 'CELESTIAL SPHERE, 5\' SOLAR CORONAGRAPH & OORT RELAY RING',
      sub: 'ASTEROID 3-5-1 (42,100 AU • INFALL -42.6 m/s) • SWEEP 254.300 → .310',
      unitTag: '4.90"/AU CORONAGRAPH'
    },
    'propagation.html': {
      badge: 'CONSOLE 3 • VAN ALLEN VA-4',
      accent: '#4ade80',
      accentBg: 'rgba(74, 222, 128, 0.15)',
      title: 'VAN ALLEN VA-4 • OORT SPACE WEATHER, PROPAGATION & DILITHIUM BUS',
      sub: 'VAN ALLEN & SONS SWITCHGEAR (CERES FOUNDRY #7 • 2.77 AU)',
      unitTag: 'UNIT S/N VA4-0089'
    },
    'euclidean-detector.html': {
      badge: 'CONSOLE 4 • VAN ALLEN ED-9',
      accent: '#f59e0b',
      accentBg: 'rgba(245, 158, 11, 0.16)',
      title: 'VAN ALLEN ED-9 • COSMIC GEOMETRIC INTELLIGENCE CORRELATOR',
      sub: '1.33-LY OORT VLBI BASELINE (GOR-9 ↔ GOR-3) • HOUGH PROOF ENGINE',
      unitTag: 'TOLERANCE 0.0001 ARCSEC'
    },
    'bogey-detector.html': {
      badge: 'CONSOLE 5 • BOGEY-9',
      accent: '#f43f5e',
      accentBg: 'rgba(244, 63, 94, 0.18)',
      title: 'HAUSER BOGEY-9 • PERIMETER ASTEROID TRAIL-CAM & UAP DISCRIMINATOR',
      sub: 'STARLIGHT CMOS / WHITE-HOT FLIR • 9 LIDAR MOTION GATES',
      unitTag: 'UNIT S/N BG9-0351'
    },
    'station.html': {
      badge: 'CONSOLE 7 • QSL DOSSIER',
      accent: '#38bdf8',
      accentBg: 'rgba(56, 189, 248, 0.16)',
      title: 'INTERCEPTED DX STATION DOSSIER & SSTV eQSL COLLECTOR VERIFICATION',
      sub: 'OORT SECTOR 9 SWEEP 254.310 VERIFIED RECEPTION LEDGER',
      unitTag: 'EPOCH 254.310 • W0'
    },
    'broadcast.html': {
      badge: 'MASTER OPS • ALL SYSTEMS',
      accent: '#f59e0b',
      accentBg: 'rgba(245, 158, 11, 0.16)',
      title: 'GOR-9 • BROADCAST OPERATIONS SITUATIONAL AWARENESS CONSOLE',
      sub: 'OCTAGONAL ATC CONTROL TOWER DECK • ASTEROID 3-5-1 (42,100 AU)',
      unitTag: '8 DX CARRIERS ACTIVE'
    }
  };

  const meta = CONSOLE_META[path] || CONSOLE_META['index.html'];

  const style = document.createElement('style');
  style.textContent = `
    /* Unified 1080p -> 1440p (4/3 Scale) Outer Margin & Hardware Console Frame */
    html, body {
      width: 100vw !important;
      height: 100vh !important;
      max-height: 100vh !important;
      overflow: hidden !important;
      background: radial-gradient(circle at 50% 40%, #060a12 0%, #020306 100%) !important;
      box-sizing: border-box !important;
    }

    body.gor9-framed-body {
      padding: 18px 24px 22px 24px !important;
      display: flex !important;
      flex-direction: column !important;
      margin: 0 !important;
    }

    .gor9-console-frame {
      width: 100%;
      height: 100%;
      min-height: 0;
      display: flex;
      flex-direction: column;
      background: linear-gradient(180deg, #0b111c 0%, #060a11 100%);
      border: 2px solid #2a3d5c;
      border-radius: 10px;
      box-shadow:
        0 0 0 1px #0a101a,
        0 18px 50px rgba(0, 0, 0, 0.92),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
      overflow: hidden;
      position: relative;
    }

    /* Top Console Hardware Header */
    .gor9-uni-header {
      background: linear-gradient(90deg, #0b111d 0%, #131e31 50%, #0b111d 100%);
      border-bottom: 2px solid ${meta.accent};
      padding: 0 16px;
      height: 48px;
      min-height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      z-index: 90;
      box-sizing: border-box;
      flex-shrink: 0;
    }

    .gor9-uni-left {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .gor9-hw-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: ${meta.accentBg};
      border: 1px solid ${meta.accent};
      color: ${meta.accent};
      font-size: 11.5px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 4px;
      letter-spacing: 0.08em;
      white-space: nowrap;
      box-shadow: 0 0 10px ${meta.accentBg};
    }

    .gor9-hw-titles {
      display: flex;
      align-items: baseline;
      gap: 12px;
      min-width: 0;
      overflow: hidden;
    }

    .gor9-hw-title {
      font-size: 14px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }

    .gor9-hw-sub {
      font-size: 11px;
      color: #94a3b8;
      letter-spacing: 0.04em;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .gor9-console-tabs {
      display: flex;
      align-items: center;
      gap: 5px;
      flex-shrink: 0;
    }

    .gor9-tab {
      text-decoration: none;
      background: #0b121e;
      border: 1px solid #24344d;
      color: #94a3b8;
      font-family: inherit;
      font-size: 10.5px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.12s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .gor9-tab:hover {
      color: #f8fafc;
      border-color: #38bdf8;
      background: rgba(56, 189, 248, 0.12);
    }

    .gor9-tab.active {
      background: ${meta.accentBg};
      border-color: ${meta.accent};
      color: ${meta.accent};
      font-weight: 800;
    }

    .gor9-video-lock-pills {
      display: none;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    body.gor9-video-mode .gor9-console-tabs {
      display: none !important;
    }

    body.gor9-video-mode .gor9-video-lock-pills {
      display: flex !important;
    }

    .gor9-hdr-pill {
      background: #070b12;
      border: 1px solid #253652;
      border-radius: 4px;
      padding: 4px 10px;
      font-size: 11px;
      color: #94a3b8;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }

    .gor9-hdr-pill b {
      color: #e2e8f0;
    }

    /* Middle Workspace Container */
    .gor9-frame-workspace {
      flex: 1;
      min-height: 0;
      width: 100%;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }

    /* Bottom Transmitter Power & ON-AIR Telemetry Footer Bar */
    .gor9-uni-footer {
      height: 44px;
      min-height: 44px;
      background: linear-gradient(90deg, #070b12 0%, #0d1524 50%, #070b12 100%);
      border-top: 1px solid #263854;
      padding: 0 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 11.5px;
      color: #94a3b8;
      flex-shrink: 0;
      z-index: 85;
    }

    .gor9-ftr-group {
      display: flex;
      align-items: center;
      gap: 14px;
      white-space: nowrap;
    }

    .gor9-onair-badge {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: rgba(244, 63, 94, 0.18);
      border: 1px solid #f43f5e;
      color: #fecdd3;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 4px;
      letter-spacing: 0.08em;
      text-decoration: none;
    }

    .gor9-onair-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #f43f5e;
      box-shadow: 0 0 8px #f43f5e;
      animation: gor9Pulse 1.4s infinite;
    }

    @keyframes gor9Pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.35; }
    }

    .gor9-ftr-metric {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(4, 7, 13, 0.78);
      border: 1px solid #1e2d45;
      border-radius: 4px;
      padding: 3px 9px;
    }

    .gor9-ftr-metric .k {
      color: #64748b;
      font-size: 10.5px;
      font-weight: 700;
    }

    .gor9-ftr-metric .v-amber { color: #f59e0b; font-weight: 800; }
    .gor9-ftr-metric .v-green { color: #4ade80; font-weight: 800; }
    .gor9-ftr-metric .v-cyan { color: #38bdf8; font-weight: 800; }

    .gor9-pa-meter {
      display: inline-flex;
      gap: 2px;
      align-items: center;
      margin-left: 3px;
    }

    .gor9-pa-seg {
      width: 4px;
      height: 11px;
      border-radius: 1px;
      background: #1e293b;
    }
    .gor9-pa-seg.on-g { background: #4ade80; box-shadow: 0 0 4px rgba(74, 222, 128, 0.5); }
    .gor9-pa-seg.on-a { background: #f59e0b; box-shadow: 0 0 4px rgba(245, 158, 11, 0.5); }

    .gor9-ftr-divider {
      width: 1px;
      height: 18px;
      background: #1f2e46;
    }
  `;
  document.head.appendChild(style);

  function buildConsoleFrame() {
    if (isCapture) {
      document.body.classList.add('gor9-video-mode');
    }

    const existingHeader = document.querySelector('header.atc-topbar, header.station-topbar, header.top-bar');
    if (!existingHeader) return;

    // Preserve any legacy [id] elements inside the original header so page scripts never fail on getElementById(...)
    const preservedNodes = [];
    existingHeader.querySelectorAll('[id]').forEach((el) => {
      if (!el.id.startsWith('gor9-')) {
        preservedNodes.push(el.cloneNode(true));
      }
    });

    const stParam = `?id=${encodeURIComponent(activeStationId)}`;
    const navHtml = `
      <div class="gor9-uni-left">
        <span class="gor9-hw-badge">${meta.badge}</span>
        <div class="gor9-hw-titles">
          <span class="gor9-hw-title">${meta.title}</span>
          <span class="gor9-hw-sub">${meta.sub}</span>
        </div>
      </div>

      <div class="gor9-video-lock-pills">
        <span class="gor9-hdr-pill">STATION: <b style="color:#f59e0b;">ASTEROID 3-5-1 • SECTOR 9</b></span>
        <span class="gor9-hdr-pill">CALIBRATION: <b style="color:#38e8ff;">${meta.unitTag}</b></span>
      </div>

      <nav class="gor9-console-tabs" aria-label="Station Console Navigation">
        <a href="broadcast.html${stParam}" class="gor9-tab ${path === 'broadcast.html' ? 'active' : ''}" id="gor9-tab-broadcast">📡 OPS</a>
        <a href="index.html${stParam}" class="gor9-tab ${path === 'index.html' ? 'active' : ''}" id="gor9-tab-mk4">🎛️ 1·MK-IV</a>
        <a href="celestial-atlas.html${stParam}" class="gor9-tab ${path === 'celestial-atlas.html' ? 'active' : ''}" id="gor9-tab-celestial">🪐 2·SKY/3D</a>
        <a href="propagation.html" class="gor9-tab ${path === 'propagation.html' ? 'active' : ''}" id="gor9-tab-va4">🌩️ 3·VA-4</a>
        <a href="euclidean-detector.html" class="gor9-tab ${path === 'euclidean-detector.html' ? 'active' : ''}" id="gor9-tab-ed9">📐 4·ED-9</a>
        <a href="bogey-detector.html" class="gor9-tab ${path === 'bogey-detector.html' ? 'active' : ''}" id="gor9-tab-bogey">🛸 5·BOGEY-9</a>
        <a href="tower-3d.html" class="gor9-tab ${path === 'tower-3d.html' ? 'active' : ''}" id="gor9-tab-tower">🗼 6·TOWER</a>
        <a href="station.html${stParam}" class="gor9-tab ${path === 'station.html' ? 'active' : ''}" id="gor9-tab-station">🃏 7·QSL</a>
      </nav>
    `;

    existingHeader.className = 'gor9-uni-header';
    existingHeader.innerHTML = navHtml;

    if (preservedNodes.length > 0) {
      const compatVault = document.createElement('div');
      compatVault.style.display = 'none';
      compatVault.setAttribute('aria-hidden', 'true');
      preservedNodes.forEach((n) => compatVault.appendChild(n));
      existingHeader.appendChild(compatVault);
    }

    // Wrap console contents inside .gor9-console-frame with bottom ON-AIR & Transmitter Power Footer
    if (!document.querySelector('.gor9-console-frame')) {
      document.body.classList.add('gor9-framed-body');
      const frame = document.createElement('div');
      frame.className = 'gor9-console-frame';

      const workspace = document.createElement('div');
      workspace.className = 'gor9-frame-workspace';

      // Move non-modal, non-script children into workspace
      const children = Array.from(document.body.children);
      document.body.insertBefore(frame, document.body.firstChild);
      frame.appendChild(existingHeader);
      frame.appendChild(workspace);

      children.forEach((ch) => {
        if (ch === frame || ch === existingHeader) return;
        if (ch.tagName === 'SCRIPT' || ch.classList.contains('modal-backdrop')) return;
        workspace.appendChild(ch);
      });

      const footer = document.createElement('footer');
      footer.className = 'gor9-uni-footer';
      footer.innerHTML = `
        <div class="gor9-ftr-group">
          <a href="broadcast.html${stParam}" class="gor9-onair-badge" id="gor9-switch-ops">
            <span class="gor9-onair-dot"></span>ON AIR • GOR-9 • 14,285.7 kHz USB
          </a>
          <div class="gor9-ftr-metric">
            <span class="k">TX PA OUTPUT:</span>
            <span class="v-green" id="gor9-ftr-pa-val">42.0 / 50.0 kW PEP</span>
            <span class="gor9-pa-meter" aria-hidden="true">
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-g"></span>
              <span class="gor9-pa-seg on-a"></span>
              <span class="gor9-pa-seg on-a"></span>
              <span class="gor9-pa-seg"></span>
            </span>
          </div>
          <div class="gor9-ftr-metric">
            <span class="k">APEX RINGS:</span>
            <span class="v-cyan">4/4 LOCKED • VSWR 1.08:1</span>
          </div>
        </div>

        <div class="gor9-ftr-group">
          <div class="gor9-ftr-metric">
            <span class="k">REACTOR #2 (W0):</span>
            <span class="v-amber" id="gor9-ftr-bus-val">12.0 / 50.0 kW • DUCT BIAS LOCKED</span>
          </div>
          <div class="gor9-ftr-metric">
            <span class="k">PULSAR CLOCK:</span>
            <span class="v-green" id="gor9-ftr-pulsar-clock">PSR B1937+21 • EPOCH 254.310 • W0 • B0000 PST</span>
          </div>
        </div>
      `;
      frame.appendChild(footer);

      // Live Pulsar Barycentric Time Beat Ticker (1 Beat = 1,000 pulses of PSR B1937+21 = 1.557806s)
      const pulsarStartMs = Date.now();
      setInterval(() => {
        const el = document.getElementById('gor9-ftr-pulsar-clock');
        if (!el) return;
        const elapsedBeats = Math.floor((Date.now() - pulsarStartMs) / 1557.80645);
        const beat = elapsedBeats % 10000;
        const watch = Math.floor(elapsedBeats / 10000) % 6;
        el.textContent = `PSR B1937+21 • EPOCH 254.310 • W${watch} • B${String(beat).padStart(4, '0')} PST`;
      }, 390);
    }
  }

  // Expose helper so any console can update the active station ID dynamically when presets are clicked
  window.updateGor9NavStation = function (stationId) {
    if (!stationId) return;
    try {
      sessionStorage.setItem('gor9_active_station', stationId);
    } catch (e) {}
    const stParam = `?id=${encodeURIComponent(stationId)}`;
    const map = {
      'gor9-switch-ops': `broadcast.html${stParam}`,
      'gor9-tab-broadcast': `broadcast.html${stParam}`,
      'gor9-tab-mk4': `index.html${stParam}`,
      'gor9-tab-celestial': `celestial-atlas.html${stParam}`,
      'gor9-tab-station': `station.html${stParam}`,
    };
    Object.keys(map).forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.href = map[id];
    });
  };

  if (document.querySelector('header.atc-topbar, header.station-topbar, header.top-bar')) {
    buildConsoleFrame();
  } else {
    document.addEventListener('DOMContentLoaded', buildConsoleFrame);
  }
})();
