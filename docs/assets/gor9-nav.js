/**
 * GOR-9 Broadcast Operations & Station Console Switch Bar
 * =======================================================
 * Provides a consistent top navigation bar across all GOR-9 Broadcast & Station Consoles:
 *   - [📡 BROADCAST OPS DASHBOARD] (`broadcast.html`: All-Systems Situational Awareness)
 *   - Station Consoles (`index.html`, `celestial-atlas.html`, `propagation.html`,
 *     `euclidean-detector.html`, `bogey-detector.html`, `tower-3d.html`, `station.html`)
 *   - Preserves active received station selection (?id=...) across consoles
 */
(function () {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  const params = new URLSearchParams(window.location.search);

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

  const style = document.createElement('style');
  style.textContent = `
    .gor9-uni-header {
      background: linear-gradient(180deg, #111827 0%, #070b12 100%);
      border-bottom: 1px solid #26354d;
      padding: 0 14px;
      min-height: 44px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-family: 'JetBrains Mono', 'Share Tech Mono', monospace;
      z-index: 90;
      position: relative;
      box-sizing: border-box;
      flex-shrink: 0;
    }
    .gor9-uni-left {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }
    .gor9-onair-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(244, 63, 94, 0.16);
      border: 1px solid #f43f5e;
      color: #fda4af;
      font-size: 10px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 3px;
      letter-spacing: 0.06em;
      white-space: nowrap;
      text-decoration: none;
    }
    .gor9-onair-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #f43f5e;
      box-shadow: 0 0 8px #f43f5e;
      animation: gor9Pulse 1.4s infinite;
    }
    @keyframes gor9Pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
    .gor9-mode-switch {
      display: inline-flex;
      background: #04070d;
      border: 1px solid #2b3d59;
      border-radius: 4px;
      padding: 2px;
      gap: 3px;
      flex-shrink: 0;
    }
    .gor9-mode-pill {
      text-decoration: none;
      font-size: 10.5px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 3px;
      color: #8b9bb4;
      letter-spacing: 0.04em;
      transition: all 0.14s ease;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .gor9-mode-pill:hover {
      color: #e2e8f0;
      background: rgba(56, 189, 248, 0.1);
    }
    .gor9-mode-pill.active-ops {
      background: linear-gradient(180deg, rgba(240, 184, 73, 0.24) 0%, rgba(240, 184, 73, 0.1) 100%);
      color: #f0b849;
      border: 1px solid rgba(240, 184, 73, 0.65);
      box-shadow: 0 0 12px rgba(240, 184, 73, 0.18);
    }
    .gor9-mode-pill.active-review {
      background: linear-gradient(180deg, rgba(56, 232, 255, 0.22) 0%, rgba(56, 232, 255, 0.08) 100%);
      color: #38e8ff;
      border: 1px solid rgba(56, 232, 255, 0.65);
      box-shadow: 0 0 12px rgba(56, 232, 255, 0.18);
    }
    .gor9-console-tabs {
      display: flex;
      align-items: center;
      gap: 4px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .gor9-tab {
      text-decoration: none;
      background: #0c121d;
      border: 1px solid #23324a;
      color: #94a3b8;
      font-family: inherit;
      font-size: 10px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 3px;
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
      background: rgba(56, 189, 248, 0.1);
    }
    .gor9-tab.active {
      background: rgba(240, 184, 73, 0.16);
      border-color: #f0b849;
      color: #f0b849;
      font-weight: 800;
      box-shadow: inset 0 0 8px rgba(240, 184, 73, 0.15);
    }
    .gor9-tab.active.cyan-act {
      background: rgba(56, 232, 255, 0.16);
      border-color: #38e8ff;
      color: #38e8ff;
      box-shadow: inset 0 0 8px rgba(56, 232, 255, 0.15);
    }
    .gor9-tab.overview-tab {
      border-color: rgba(240, 184, 73, 0.5);
      color: #fcd34d;
    }
    .gor9-tab.review-tab {
      border-color: rgba(56, 232, 255, 0.4);
      color: #7dd3fc;
    }
    .gor9-tab-sep {
      width: 1px;
      height: 18px;
      background: #26354d;
      margin: 0 2px;
    }
  `;
  document.head.appendChild(style);

  function buildNavBar() {
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
        <a href="broadcast.html${stParam}" class="gor9-onair-pill" title="Return to Master Broadcast Situational Awareness">
          <span class="gor9-onair-dot"></span>ON AIR • GOR-9
        </a>
        <div class="gor9-mode-switch" role="navigation" aria-label="Broadcast Situational Awareness">
          <a href="broadcast.html${stParam}" class="gor9-mode-pill active-ops" id="gor9-switch-ops">
            📡 BROADCAST OPS DASHBOARD
          </a>
        </div>
        <span style="font-size:10px;color:#94a3b8;letter-spacing:0.05em;white-space:nowrap;">
          ASTEROID 3-5-1 • <b style="color:#f0b849;">8 RECEIVED DX STATIONS</b> • <b style="color:#38e8ff;">CERES CFS-7 LOCK</b>
        </span>
      </div>

      <nav class="gor9-console-tabs" aria-label="Station Console Navigation">
        <a href="broadcast.html${stParam}" class="gor9-tab overview-tab ${path === 'broadcast.html' ? 'active' : ''}" id="gor9-tab-broadcast" title="All-Systems Broadcast Situational Awareness">
          📡 ALL-SYSTEMS OPS
        </a>
        <a href="index.html${stParam}" class="gor9-tab ${path === 'index.html' ? 'active' : ''}" id="gor9-tab-mk4" title="Hauser MK-IV Wideband DX Receiver">
          🎛️ 1·HAUSER MK-IV
        </a>
        <a href="celestial-atlas.html${stParam}" class="gor9-tab ${path === 'celestial-atlas.html' ? 'active cyan-act' : ''}" id="gor9-tab-celestial" title="Celestial Sphere, Oort Neighbors & 3D Relay Sphere">
          🪐 2·3D SKY &amp; RELAY
        </a>
        <a href="propagation.html" class="gor9-tab ${path === 'propagation.html' ? 'active' : ''}" id="gor9-tab-va4" title="Van Allen VA-4 Space Weather & 52.4 kW Dilithium Bus">
          🌩️ 3·VAN ALLEN VA-4
        </a>
        <a href="euclidean-detector.html" class="gor9-tab ${path === 'euclidean-detector.html' ? 'active' : ''}" id="gor9-tab-ed9" title="Van Allen ED-9 Euclidean Geometric Correlator">
          📐 4·EUCLID ED-9
        </a>
        <a href="bogey-detector.html" class="gor9-tab ${path === 'bogey-detector.html' ? 'active' : ''}" id="gor9-tab-bogey" title="Hauser Bogey-9 Perimeter Trail-Cam & UAPs">
          🛸 5·BOGEY-9 UAP
        </a>
        <a href="tower-3d.html" class="gor9-tab ${path === 'tower-3d.html' ? 'active' : ''}" id="gor9-tab-tower" title="3D Octagonal ATC Booth & 86.5m Lighthouse">
          🗼 6·3D TOWER
        </a>
        <a href="station.html${stParam}" class="gor9-tab ${path === 'station.html' ? 'active cyan-act' : ''}" id="gor9-tab-station" title="Received Station eQSL Cards & Signal Dossier">
          🃏 7·STATION QSL LOG
        </a>
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildNavBar);
  } else {
    buildNavBar();
  }
})();
