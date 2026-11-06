#!/usr/bin/env python3
"""Capture the 30fps GOR-9 Cold Open 3D Power-Up Sequence from `docs/tower-3d.html`
without modifying `docs/tower-3d.html` on disk, and encode to 2560x1440 QHD MP4
following the GEOMETOR VIDEO_PIPELINE.md specification.

Choreography synced to `episodes/ep01_2736.305_parallelogram/audio/cam00_cold_open_mix.wav` (21.62s):
  1. 0.00s - 0.35s : Dark Station in deep-space starfield (Tower, Sign, Marzelvane, and Booth OFF)
  2. 0.35s - 1.20s : Station Power-Up — Base Compound (Reactor #2, Habitat, Pad Beacons) & Tower Climb Spine [L]
  3. 0.85s - 2.45s : Vertical 3D 'G / O / R / ◎ / 9' Sign Animates (G -> O -> R -> ◎ -> 9 -> ALL LIT) [S]
  4. 2.35s - 3.45s : Marzelvane Power On — 4 concentric rings energize from dark steel to Cherenkov cyan
  5. 3.45s - 4.10s : Broadcast Booth 'ON AIR' Crimson Lights strike on [A]
  6. 4.18s - 10.98s: Marzelvane Burst synced 1:1 to the 1B C-Lydian Opening Chime:
                     Ring 1 (4.18s C4) -> Ring 2 (4.38s G4) -> Ring 3 (4.58s D5) -> Ring 4 (4.78s F#5)
                     -> Spire Lock & Expanding Barycentric Shockwave Burst (5.02s G5 chord + 5.25s sustain)
  7. 13.60s - 21.62s: Interior Cut to the Crimson ON-AIR Broadcast Booth (`booth_wide` -> `operator_pov`)
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import shutil
import socketserver
import subprocess
import threading
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
COLD_OPEN_WAV = EP_DIR / "audio" / "cam00_cold_open_mix.wav"
FRAMES_DIR = EP_DIR / "frames_cold_open_3d"
OUT_COLD_OPEN_MP4 = EP_DIR / "gor9_cold_open_tower3d.mp4"


INJECTED_CAPTURE_JS = r"""
    // ═════════════════════════════════════════════════════════════════
    // IN-MEMORY DETERMINISTIC 30FPS BROADCAST COLD-OPEN CAPTURE ENGINE
    // (Served dynamically without modifying docs/tower-3d.html on disk)
    // ═════════════════════════════════════════════════════════════════
    function setStationStateAtTime(t, dt) {
      // Hide HTML HUD overlays for clean full-bleed 16:9 cinema capture
      const topNav = document.querySelector('.top-nav');
      if (topNav) topNav.style.display = 'none';
      const hudL = document.getElementById('hud-left');
      if (hudL) hudL.style.display = 'none';
      const hudR = document.getElementById('hud-right');
      if (hudR) hudR.style.display = 'none';
      const hudB = document.getElementById('hud-bottom');
      if (hudB) hudB.style.display = 'none';

      // ── 0. CAMERA CHOREOGRAPHY (FIXED DRAMATIC VIEW FROM BELOW THE CLIFFS LOOKING UP) ──
      // Elevated slightly (y = +12.5m at r = 104m) so the sightline to the '9' slot (+31.8m)
      // clears the octagonal Broadcast Booth roof (+29.0m) with clean separation while keeping
      // the newly textured stepped basalt asteroid cliffs prominent across the bottom foreground
      camera.position.set(86.0, 12.5, 59.0);
      controls.target.set(-2.0, 33.5, 0.0);
      camera.fov = 56.0;
      camera.updateProjectionMatrix();

      // ── 1. DARK STATION -> BASE COMPOUND & TOWER SPINE POWER-UP (t = 0.35s .. 1.20s) ──
      const pTower = smoothstep(0.35, 1.20, t);
      matTowerAmber.color.setRGB(
        0.05 + (1.0 - 0.05) * pTower,
        0.04 + (0.67 - 0.04) * pTower,
        0.02 + (0.17 - 0.02) * pTower
      );
      matAmberGlow.color.setRGB(
        0.05 + (1.0 - 0.05) * pTower,
        0.04 + (0.67 - 0.04) * pTower,
        0.02 + (0.17 - 0.02) * pTower
      );
      matTowerCyan.color.setRGB(
        0.03 + (0.22 - 0.03) * pTower,
        0.07 + (0.91 - 0.07) * pTower,
        0.09 + (1.00 - 0.09) * pTower
      );
      matCyanGlow.color.setRGB(
        0.03 + (0.22 - 0.03) * pTower,
        0.07 + (0.91 - 0.07) * pTower,
        0.09 + (1.00 - 0.09) * pTower
      );
      matTowerSpireCore.color.setRGB(
        0.04 + (0.72 - 0.04) * pTower,
        0.09 + (0.97 - 0.09) * pTower,
        0.11 + (1.00 - 0.11) * pTower
      );
      matCyanCore.color.setRGB(
        0.04 + (0.72 - 0.04) * pTower,
        0.09 + (0.97 - 0.09) * pTower,
        0.11 + (1.00 - 0.11) * pTower
      );
      matTowerCrimson.color.setRGB(
        0.08 + (1.00 - 0.08) * pTower,
        0.02 + (0.08 - 0.02) * pTower,
        0.02 + (0.03 - 0.02) * pTower
      );
      towerStructureLight.intensity = 5.5 * pTower;
      habLight.intensity = 4.5 * pTower;
      reactorLight.intensity = 6.0 * pTower;

      // ── 2. VERTICAL 'G / O / R / ◎ / 9' SIGN ANIMATES (t = 0.85s .. 2.35s) ──
      // Steps: 0:G (0.85..1.15s) -> 1:O (1.15..1.45s) -> 2:R (1.45..1.75s) -> 3:◎ (1.75..2.05s) -> 4:9 (2.05..2.35s)
      // Then at t >= 2.35s: ALL 5 SLOTS LOCK ON STEADY!
      if (t < 0.85) {
        signSlotMats.forEach((sm) => {
          sm.face.color.setHex(0x140505);
          sm.core.color.setHex(0x1a0606);
          sm.retGlow.color.setHex(0x081418);
          sm.retCore.color.setHex(0x0c1c22);
        });
        signLightESE.intensity = 0.0;
        signLightWNW.intensity = 0.0;
      } else if (t < 2.35) {
        const seqPhase = (t - 0.85) / 0.30; // 0..5 across 1.50s
        const activeStep = Math.min(4, Math.floor(seqPhase));
        const subP = seqPhase - activeStep;
        const pulse = 0.88 + 0.12 * Math.sin(subP * Math.PI);
        signSlotMats.forEach((sm, idx) => {
          const b = idx === activeStep ? pulse : (idx < activeStep ? 0.85 : 0.05);
          sm.face.color.setRGB(0.88 * b, 0.025 * b, 0.0);
          sm.core.color.setRGB(1.0 * b, 0.10 * b, 0.03 * b);
          sm.retGlow.color.setRGB(0.22 * b, 0.91 * b, 1.0 * b);
          sm.retCore.color.setRGB(0.72 * b, 0.97 * b, 1.0 * b);
        });
        const activeY = SIGN_SLOT_Y[activeStep];
        const isRingStep = activeStep === 3;
        signLightESE.color.setHex(isRingStep ? 0x38e8ff : 0xff0804);
        signLightWNW.color.setHex(isRingStep ? 0x38e8ff : 0xff0804);
        signLightESE.position.y = activeY;
        signLightWNW.position.y = activeY;
        signLightESE.intensity = 8.5 * pulse;
        signLightWNW.intensity = 8.5 * pulse;
      } else {
        // Locked steady sign after t = 2.35s (zero idle shimmer)
        signSlotMats.forEach((sm) => {
          sm.face.color.setRGB(0.88, 0.025, 0.0);
          sm.core.color.setRGB(1.0, 0.09, 0.03);
          sm.retGlow.color.setRGB(0.22, 0.91, 1.0);
          sm.retCore.color.setRGB(0.72, 0.97, 1.0);
        });
        signLightESE.color.setHex(0xff0804);
        signLightWNW.color.setHex(0xff0804);
        signLightESE.position.y = 39.6;
        signLightWNW.position.y = 39.6;
        signLightESE.intensity = 9.5;
        signLightWNW.intensity = 9.5;
      }

      // ── 3. MARZELVANE POWER ON (t = 2.35s .. 3.35s) & 5. MARZELVANE BURST AS CHIME PLAYS (t = 4.18s .. 9.20s) ──
      // Chime 1B starts at t = 4.18s:
      //   Ring 1 (C4): 4.18s
      //   Ring 2 (G4): 4.38s
      //   Ring 3 (D5): 4.58s
      //   Ring 4 (F#5): 4.78s
      //   Spire Lock & Barycentric Burst Climax (G5 chord): 5.02s
      const chimeStart = 4.18;
      const spireLockTime = 5.02;
      const burstEnd = 9.20;
      let climaxFlash = 0.0;
      let coreSurge = 0.0;

      if (t >= chimeStart && t <= burstEnd) {
        if (t >= spireLockTime - 0.04) {
          const rise = smoothstep(spireLockTime - 0.04, spireLockTime + 0.16, t);
          const dtAfterLock = Math.max(0.0, t - (spireLockTime + 0.16));
          const fall = Math.exp(-dtAfterLock / 1.85) * (1.0 - smoothstep(8.20, burstEnd, t));
          climaxFlash = rise * fall;
        }
        coreSurge = smoothstep(chimeStart, chimeStart + 0.25, t) * (1.0 - smoothstep(8.00, burstEnd, t));
      }

      let totalRingEnergy = 0.0;
      marzelRings.forEach((ring, rIdx) => {
        // Standby power-on ramp (t = 2.35s .. 3.30s, staggered inner to outer, then steady)
        const pStandby = smoothstep(2.35 + rIdx * 0.16, 2.75 + rIdx * 0.16, t);
        const idleWave = 0.65 * pStandby;

        let ringCharge = 0.0;
        let ignFlash = 0.0;
        let spokeSurge = 0.0;

        if (t >= chimeStart && t <= burstEnd) {
          const tRingNote = chimeStart + rIdx * 0.20; // 4.18, 4.38, 4.58, 4.78s
          const tRingFull = tRingNote + 0.18;
          const rampUp = smoothstep(tRingNote, tRingFull, t);
          const dtHold = Math.max(0.0, t - spireLockTime);
          const coolDown = Math.exp(-dtHold / (2.0 + rIdx * 0.20)) * (1.0 - smoothstep(8.20, burstEnd, t));
          ringCharge = rampUp * coolDown;

          if (t >= tRingNote && t <= tRingFull + 0.28) {
            ignFlash = Math.sin(smoothstep(tRingNote, tRingFull + 0.28, t) * Math.PI);
          }
          if (t >= tRingNote - 0.10 && t <= tRingFull + 0.12) {
            spokeSurge = Math.sin(smoothstep(tRingNote - 0.10, tRingFull + 0.12, t) * Math.PI);
          }
        }

        const e = Math.min(1.5, ringCharge + 0.70 * ignFlash + 0.85 * climaxFlash);
        totalRingEnergy += e;

        const w = Math.min(1.0, idleWave + e * 0.85);
        const whiteMix = Math.min(1.0, 0.55 * ringCharge + 0.75 * ignFlash + 0.85 * climaxFlash);

        const baseGlow = Math.max(pStandby, Math.min(1.0, e * 2.0));
        ring.glowMatTop.color.setRGB(
          0.03 + baseGlow * Math.min(0.97, 0.14 + 0.45 * w + 0.55 * whiteMix),
          0.06 + baseGlow * Math.min(0.94, 0.74 + 0.18 * w + 0.18 * whiteMix),
          0.09 + baseGlow * 0.91
        );
        ring.glowMatBot.color.setRGB(
          0.03 + baseGlow * Math.min(0.97, 0.31 + 0.55 * w + 0.40 * whiteMix),
          0.06 + baseGlow * Math.min(0.94, 0.84 + 0.08 * w + 0.08 * whiteMix),
          0.09 + baseGlow * 0.91
        );
        const tubeScale = 0.55 + 0.45 * baseGlow + 0.75 * ringCharge + 0.65 * ignFlash + 0.80 * climaxFlash;
        ring.glowTop.scale.set(1.0, 1.0, tubeScale);
        ring.glowBot.scale.set(1.0, 1.0, tubeScale);

        ring.innerHaloMat.opacity = Math.min(
          0.38,
          baseGlow * (0.08 + 0.05 * idleWave) + 0.18 * ringCharge + 0.14 * ignFlash + 0.16 * climaxFlash
        );
        ring.innerHaloMat.color.setRGB(
          Math.min(1.0, 0.24 + 0.65 * whiteMix),
          Math.min(1.0, 0.90 + 0.10 * whiteMix),
          1.0
        );
        const innerScale = 1.0 + 0.35 * ringCharge + 0.45 * ignFlash + 0.55 * climaxFlash;
        ring.innerHalo.scale.set(1.0, 1.0, innerScale);

        ring.outerHaloMat.opacity = Math.min(
          0.20,
          baseGlow * (0.03 + 0.02 * idleWave) + 0.10 * ringCharge + 0.08 * ignFlash + 0.10 * climaxFlash
        );
        const outerScale = 1.0 + 0.45 * ringCharge + 0.55 * ignFlash + 0.75 * climaxFlash;
        ring.outerHalo.scale.set(1.0, 1.0, outerScale);

        ring.superHaloMat.opacity = Math.min(
          0.11,
          0.04 * ringCharge + 0.05 * ignFlash + 0.08 * climaxFlash
        );
        const superScale = 1.0 + 0.45 * ringCharge + 0.85 * climaxFlash;
        ring.superHalo.scale.set(1.0, 1.0, superScale);

        ring.spokeGlowMat.opacity = Math.min(
          0.88,
          0.05 * baseGlow + 0.42 * ringCharge + 0.60 * spokeSurge + 0.38 * climaxFlash
        );
        ring.spokeGlowMat.color.setRGB(
          Math.min(1.0, 0.25 + 0.75 * (spokeSurge + climaxFlash)),
          0.95,
          1.0
        );

        ring.tipMat.color.setRGB(
          0.06 + baseGlow * Math.min(0.94, 0.45 + 0.45 * (ringCharge + ignFlash + climaxFlash)),
          0.10 + baseGlow * 0.90,
          0.14 + baseGlow * 0.86
        );
        ring.tipSpriteMat.opacity = Math.min(
          0.95,
          baseGlow * (0.34 + 0.10 * idleWave) + 0.45 * ringCharge + 0.30 * ignFlash + 0.32 * climaxFlash
        );
        const spScale =
          baseGlow * (0.82 + 0.14 * idleWave) +
          1.35 * ringCharge +
          1.15 * ignFlash +
          1.45 * climaxFlash;
        ring.tipSprites.forEach((sp, sIdx) => {
          const mult = sIdx % 2 === 0 ? 1.0 : 0.82;
          sp.scale.set(spScale * mult, spScale * mult, 1.0);
        });
      });

      const pMarzelMaster = smoothstep(2.35, 3.30, t);
      const meanRingEnergy = totalRingEnergy * 0.25;
      const idleHubPulse = 0.65 * pMarzelMaster;
      hubCoreGlowMat.opacity = Math.min(0.68, 0.12 * pMarzelMaster + 0.06 * idleHubPulse + 0.32 * coreSurge + 0.36 * climaxFlash);
      spireAuraMat.opacity = Math.min(0.42, 0.04 * pMarzelMaster + 0.03 * idleHubPulse + 0.16 * meanRingEnergy + 0.26 * climaxFlash);

      const hubScale = hubFlare.baseScale * (pMarzelMaster * (0.9 + 0.10 * idleHubPulse) + 0.95 * coreSurge + 1.45 * climaxFlash);
      hubFlare.sprite.scale.set(hubScale, hubScale, 1.0);
      hubFlare.mat.opacity = Math.min(0.78, hubFlare.baseOpacity * pMarzelMaster + 0.28 * coreSurge + 0.34 * climaxFlash);

      const midScale = midSpireFlare.baseScale * (pMarzelMaster * (0.9 + 0.10 * idleHubPulse) + 0.85 * meanRingEnergy + 1.55 * climaxFlash);
      midSpireFlare.sprite.scale.set(midScale, midScale, 1.0);
      midSpireFlare.mat.opacity = Math.min(0.75, midSpireFlare.baseOpacity * pMarzelMaster + 0.24 * meanRingEnergy + 0.36 * climaxFlash);

      const apexScale = apexSpireFlare.baseScale * (pMarzelMaster * (0.9 + 0.12 * idleHubPulse) + 0.95 * meanRingEnergy + 2.15 * climaxFlash);
      apexSpireFlare.sprite.scale.set(apexScale, apexScale, 1.0);
      apexSpireFlare.mat.opacity = Math.min(0.85, apexSpireFlare.baseOpacity * pMarzelMaster + 0.24 * meanRingEnergy + 0.36 * climaxFlash);

      // Expanding Barycentric Shockwave Rings & Spherical Discharge Wave right on the Spire Lock chord (t = 5.02s)
      marzelShockwaves.forEach((sw, swIdx) => {
        const swStart = spireLockTime + swIdx * 0.42;
        const swDur = 3.05;
        if (t >= swStart && t <= swStart + swDur) {
          const p = (t - swStart) / swDur;
          const easeOut = 1.0 - Math.pow(1.0 - p, 1.65);
          const rad = 4.5 + 64.0 * easeOut;
          sw.mesh.visible = true;
          sw.mesh.scale.set(rad, rad, 1.2 + 4.5 * p);
          sw.mesh.position.y = (swIdx - 0.5) * 2.6 * p;
          sw.mat.opacity = Math.sin(p * Math.PI) * Math.pow(1.0 - p, 0.85) * 0.40;
        } else {
          sw.mesh.visible = false;
          sw.mat.opacity = 0.0;
        }
      });

      if (t >= spireLockTime && t <= spireLockTime + 3.20) {
        const spP = (t - spireLockTime) / 3.20;
        const spRad = 5.0 + 60.0 * (1.0 - Math.pow(1.0 - spP, 1.65));
        burstSphereMesh.visible = true;
        burstSphereMesh.scale.set(spRad, spRad * 0.58, spRad);
        burstSphereMat.opacity = Math.sin(spP * Math.PI) * Math.pow(1.0 - spP, 1.10) * 0.14;
      } else {
        burstSphereMesh.visible = false;
        burstSphereMat.opacity = 0.0;
      }

      marzelLight.intensity = pMarzelMaster * 12.0 + 24.0 * meanRingEnergy + 48.0 * climaxFlash;
      marzelBurstLight.intensity = 20.0 * meanRingEnergy + 95.0 * climaxFlash;

      // ── 4. BROADCAST BOOTH 'ON AIR' RED LIGHTS STRIKE ON (t = 3.45s .. 3.95s) ──
      let pOnAir = smoothstep(3.45, 3.95, t);
      if (t >= 3.48 && t <= 3.68) {
        pOnAir = Math.min(1.25, pOnAir + 0.35 * Math.sin(((t - 3.48) / 0.20) * Math.PI));
      }
      const pOnAirClamped = Math.min(1.0, pOnAir);
      matBoothRedGlow.color.setRGB(
        0.08 + (0.90 - 0.08) * pOnAirClamped,
        0.02 * (1.0 - 0.5 * pOnAirClamped),
        0.02 * (1.0 - 0.5 * pOnAirClamped)
      );
      matCrimsonGlow.color.setRGB(
        0.08 + (1.00 - 0.08) * pOnAirClamped,
        0.02 + (0.08 - 0.02) * pOnAirClamped,
        0.02 + (0.03 - 0.02) * pOnAirClamped
      );
      matMicTally.color.setRGB(
        0.08 + (1.00 - 0.08) * pOnAirClamped,
        0.03 + (0.08 - 0.03) * pOnAirClamped,
        0.03 + (0.03 - 0.03) * pOnAirClamped
      );
      boothInKneeMats.forEach((m) => {
        m.emissiveIntensity = 0.08 * pOnAir;
      });
      ceilingSoffit.material.emissiveIntensity = 0.12 * pOnAir;
      boothWarmLight.intensity = 7.5 * pOnAir;
      deskFillLight.intensity = 3.8 * pOnAir;
      boothBeaconLight.intensity = 12.0 * pOnAir;

      controls.update();
      renderer.render(scene, camera);
    }

    async function runColdOpenCapture() {
      const params = new URLSearchParams(window.location.search);
      const fps = parseFloat(params.get('fps') || '30');
      const duration = parseFloat(params.get('dur') || '21.62');
      const testTimesStr = params.get('test_times');

      // Wait for all Three.js textures (basalt PBR maps, sky dome, console screens) to finish loading
      await new Promise((resolve) => {
        let settled = false;
        const done = () => {
          if (!settled) {
            settled = true;
            setTimeout(resolve, 600);
          }
        };
        THREE.DefaultLoadingManager.onLoad = done;
        setTimeout(done, 2400);
      });

      // Upgrade shockwave rings & discharge sphere to high-segment smooth geometry for 30fps radiation
      marzelShockwaves.forEach((sw) => {
        sw.mesh.geometry.dispose();
        sw.mesh.geometry = new THREE.TorusGeometry(1.0, 0.035, 32, 128);
      });
      burstSphereMesh.geometry.dispose();
      burstSphereMesh.geometry = new THREE.SphereGeometry(1.0, 64, 48);

      // Force exact 1920x1080 (16:9) WebGL canvas dimensions regardless of headless window chrome
      renderer.setPixelRatio(1);
      renderer.setSize(1920, 1080, false);
      camera.aspect = 1920 / 1080;
      camera.updateProjectionMatrix();

      const dt = 1.0 / fps;
      if (testTimesStr) {
        const times = testTimesStr.split(',').map((s) => parseFloat(s));
        for (let i = 0; i < times.length; i++) {
          const t = times[i];
          setStationStateAtTime(t, dt);
          const blob = await new Promise((res) => renderer.domElement.toBlob(res, 'image/png'));
          await fetch(`/__frame/${i}`, { method: 'POST', body: blob });
        }
        await fetch('/__done', { method: 'POST' });
        return;
      }

      const totalFrames = Math.ceil(duration * fps);
      for (let f = 0; f < totalFrames; f++) {
        const t = f / fps;
        setStationStateAtTime(t, dt);
        const blob = await new Promise((res) => renderer.domElement.toBlob(res, 'image/png'));
        await fetch(`/__frame/${f}`, { method: 'POST', body: blob });
      }
      await fetch('/__done', { method: 'POST' });
    }

    runColdOpenCapture();
"""


def _build_cold_open_concat_steps() -> list[tuple[float, float, str]]:
    """Build 30.00 fps steps across the active power-up, sign sequence, and radiating
    Marzelvane burst (0.35s .. 9.05s) so the burst radiates smoothly at 30fps without stutter,
    followed by a single lossless hold frame for the steady state (9.05s .. 21.62s).
    """
    steps: list[tuple[float, float, str]] = [
        (0.15, 0.35, "000: Dark station in deep-space starlight"),
    ]
    fps = 30.0
    dt = 1.0 / fps
    num_active_frames = 261  # 261 * (1/30s) = 8.70s -> covers t = 0.35s .. 9.05s at true 30fps
    for i in range(num_active_frames):
        t_sample = round(0.35 + i * dt, 5)
        steps.append((t_sample, round(dt, 6), f"30fps active frame {i + 1:03d} (t={t_sample:.3f}s)"))
    # Remaining steady state hold from 9.05s to 21.62s (12.57s)
    steps.append((9.25, 12.57, "262: Full Station On-Air Below-Cliff Hero Hold"))
    return steps


COLD_OPEN_CONCAT_STEPS: list[tuple[float, float, str]] = _build_cold_open_concat_steps()


def find_chrome_binary() -> str:
    pw_root = Path.home() / ".cache" / "ms-playwright"
    if pw_root.is_dir():
        for candidate in sorted(pw_root.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
            return str(candidate)
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("No Chromium/Chrome binary found")


def get_wav_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def capture_sequence(
    out_dir: Path,
    fps: int = 30,
    duration: float = 21.62,
    width: int = 1920,
    height: int = 1080,
    test_times: list[float] | None = None,
    clean: bool = False,
) -> list[Path]:
    if clean and out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    if test_times is not None:
        missing_pairs = [
            (idx, t)
            for idx, t in enumerate(test_times)
            if not (out_dir / f"frame_{idx:04d}.png").exists()
        ]
        if not missing_pairs:
            print(f"  [tower-3d capture] All {len(test_times)} frames already present in {out_dir}")
            return [out_dir / f"frame_{i:04d}.png" for i in range(len(test_times))]
    else:
        missing_pairs = None

    done_event = threading.Event()
    received_count = 0
    expected_count = len(missing_pairs) if missing_pairs is not None else int(round(duration * fps))

    # Read docs/tower-3d.html dynamically into memory without touching the file on disk
    raw_html = (DOCS_DIR / "tower-3d.html").read_text(encoding="utf-8")
    target_anchor = "    animate();\n  </script>"
    if target_anchor not in raw_html:
        target_anchor = "animate();"
    injected_html = raw_html.replace(target_anchor, INJECTED_CAPTURE_JS + "\n  </script>", 1)
    injected_bytes = injected_html.encode("utf-8")

    class CaptureRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DOCS_DIR), **kwargs)

        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path.startswith("/__capture_cold_open.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(injected_bytes)))
                self.end_headers()
                self.wfile.write(injected_bytes)
                return
            return super().do_GET()

        def do_POST(self):
            nonlocal received_count
            if self.path.startswith("/__frame/"):
                raw_idx = int(self.path.split("/__frame/")[1])
                actual_idx = missing_pairs[raw_idx][0] if missing_pairs is not None else raw_idx
                length = int(self.headers.get("Content-Length", "0"))
                data = self.rfile.read(length)
                frame_path = out_dir / f"frame_{actual_idx:04d}.png"
                frame_path.write_bytes(data)
                received_count += 1
                if received_count % 10 == 0 or received_count == expected_count:
                    print(f"  [tower-3d capture] {received_count}/{expected_count} frames (saved frame_{actual_idx:04d}.png)")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return
            if self.path.startswith("/__done"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"DONE")
                done_event.set()
                return
            self.send_response(404)
            self.end_headers()

    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with ThreadedTCPServer(("127.0.0.1", 0), CaptureRequestHandler) as httpd:
        port = httpd.server_address[1]
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        q = f"fps={fps}&dur={duration:.3f}"
        if missing_pairs is not None:
            q += "&test_times=" + ",".join(f"{t:.5f}" for _, t in missing_pairs)
        url = f"http://127.0.0.1:{port}/__capture_cold_open.html?{q}"

        chrome_bin = find_chrome_binary()
        tmp_profile = Path(f"/tmp/gor9_tower3d_chrome_{os.getpid()}")
        tmp_profile.mkdir(parents=True, exist_ok=True)

        cmd = [
            chrome_bin,
            "--headless=new",
            f"--user-data-dir={tmp_profile}",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--use-gl=angle",
            "--use-angle=swiftshader",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={width},{height + 160}",
            url,
        ]
        print(f"Launching headless WebGL capture ({width}x{height}) for {expected_count} frames")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            done_event.wait(timeout=1200)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            shutil.rmtree(tmp_profile, ignore_errors=True)
            httpd.shutdown()
    if test_times is not None:
        return [out_dir / f"frame_{i:04d}.png" for i in range(len(test_times))]
    return sorted(out_dir.glob("frame_*.png"))


def assemble_concat_qhd_mp4(
    slide_pngs: list[Path],
    durations: list[float],
    audio_wav: Path,
    out_mp4: Path,
) -> None:
    """Assemble QHD MP4 using the exact -f concat pipeline from shorts.py (elements & etc)."""
    concat_file = out_mp4.parent / f"_{out_mp4.stem}_concat.txt"
    lines = []
    total_dur = 0.0
    for png, dur in zip(slide_pngs, durations):
        d = max(0.01, dur)
        total_dur += d
        lines.append(f"file '{png.resolve()}'")
        lines.append(f"duration {d:.6f}")
    lines.append(f"file '{slide_pngs[-1].resolve()}'")
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    cmd = [
        "/usr/bin/ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(audio_wav),
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-b:a",
        "192k",
        "-shortest",
        "-t",
        f"{total_dur:.3f}",
        "-vf",
        "fps=30,scale=2560:1440:flags=lanczos,setsar=1:1,format=yuv420p",
        "-vsync",
        "cfr",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-profile:v",
        "high",
        "-level:v",
        "5.1",
        "-crf",
        "18",
        "-maxrate",
        "16M",
        "-bufsize",
        "32M",
        "-g",
        "90",
        "-keyint_min",
        "90",
        "-sc_threshold",
        "0",
        "-bf",
        "2",
        "-flags",
        "+cgop",
        "-colorspace",
        "bt709",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-color_range",
        "tv",
        "-movflags",
        "+faststart",
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True)
    print(f"Encoded 2560x1440 QHD High@L5.1 MP4 -> {out_mp4}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture GOR-9 Cold Open from docs/tower-3d.html")
    parser.add_argument("--test-frames", action="store_true", help="Capture 6 diagnostic keyframes only")
    parser.add_argument("--width", type=int, default=1920, help="WebGL render width (upscaled with lanczos to 2560)")
    parser.add_argument("--height", type=int, default=1080, help="WebGL render height (upscaled with lanczos to 1440)")
    args = parser.parse_args()

    dur = get_wav_duration(COLD_OPEN_WAV)
    if args.test_frames:
        test_dir = EP_DIR / "previews" / "cold_open_3d_test"
        capture_sequence(
            test_dir,
            fps=30,
            duration=dur,
            width=args.width,
            height=args.height,
            test_times=[0.15, 1.60, 2.50, 3.85, 5.25, 16.50],
        )
        return

    sample_times = [step[0] for step in COLD_OPEN_CONCAT_STEPS]
    step_durations = [step[1] for step in COLD_OPEN_CONCAT_STEPS]
    slides_dir = EP_DIR / "slides_cold_open_3d"
    slide_pngs = capture_sequence(
        slides_dir,
        fps=30,
        duration=dur,
        width=args.width,
        height=args.height,
        test_times=sample_times,
    )
    assemble_concat_qhd_mp4(slide_pngs, step_durations, COLD_OPEN_WAV, OUT_COLD_OPEN_MP4)


if __name__ == "__main__":
    main()

