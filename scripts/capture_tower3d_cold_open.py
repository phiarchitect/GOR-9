#!/usr/bin/env python3
"""Capture the 30fps GOR-9 Cold Open 3D Power-Up & Lift-to-Dashboard Sequence from `docs/tower-3d.html`
without modifying `docs/tower-3d.html` on disk, and encode to 2560x1440 QHD MP4
following the GEOMETOR VIDEO_PIPELINE.md and PHOTON Studio specifications.

Choreography synced to `episodes/ep01_2736.305_parallelogram/audio/cam00_cold_open_mix.wav` (21.62s):
  1. 0.00s - 0.35s : Dark Station in deep-space starfield (Tower, Sign, Marzelvane, and Booth OFF)
  2. 0.35s - 1.20s : Station Power-Up — Base Compound (Reactor #2, Habitat, Pad Beacons) & Tower Climb Spine [L]
  3. 0.85s - 2.35s : Vertical 3D 'G / O / R / ◎ / 9' Sign Animates (G -> O -> R -> ◎ -> 9 -> ALL LIT) [S]
  4. 2.35s - 3.35s : Marzelvane Power On — 4 concentric rings energize from dark steel to Cherenkov cyan
  5. 3.45s - 3.95s : Broadcast Booth 'ON AIR' Crimson Lights strike on [A]
  6. 4.18s - 9.18s : 30.00 fps Marzelvane Burst synced 1:1 to the 1B C-Lydian Opening Chime:
                     Ring 1 (4.18s C4) -> Ring 2 (4.38s G4) -> Ring 3 (4.58s D5) -> Ring 4 (4.78s F#5)
                     -> Spire Lock & Expanding Barycentric Shockwave Burst (5.02s G5 chord + sustain)
  7. 9.18s - 11.20s: Full Station On-Air Below-Cliff Hero Hold
  8. 11.20s - 21.62s: Hard-Cut into the North-facing Central Lift Tube at +26.0m (`lift_emerge`, d = 4.45m),
                     then a continuous 30.00 fps glide leaving the lift, passing the swiveled Broadcast Stool
                     (`operator_pov`, d = 2.08m), and tilting perpendicular (0.18 rad) into the 16:9
                     Master Show Director HUD Dashboard (`cold_open_final`, d = 1.36m, fov = 48°).
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
VIDEO_DIR = ROOT / "videos" / "cold_open"
SRC_COLD_OPEN_WAV = EP_DIR / "audio" / "cam00_cold_open_mix.wav"
COLD_OPEN_WAV = VIDEO_DIR / "cold_open.wav"
FRAMES_DIR = VIDEO_DIR / "frames"
OUT_COLD_OPEN_MP4 = VIDEO_DIR / "gor9_cold_open.mp4"
OUT_COLD_OPEN_1080P_MP4 = VIDEO_DIR / "cold_open_1080p.mp4"
OUT_COLD_OPEN_THUMB = VIDEO_DIR / "gor9_cold_open_thumb.jpg"


INJECTED_CAPTURE_JS = r"""
    // ═════════════════════════════════════════════════════════════════
    // IN-MEMORY DETERMINISTIC 30FPS BROADCAST COLD-OPEN CAPTURE ENGINE
    // (Served dynamically without modifying docs/tower-3d.html on disk)
    // ═════════════════════════════════════════════════════════════════
    let _lastShowHudIdx = -1;
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

      // ── 0. CAMERA CHOREOGRAPHY ──
      // Act I (0.00s .. 11.20s): Fixed dramatic view from below the basalt cliffs looking up
      // Act II (11.20s .. 21.62s): Hard-cut into the North-facing Central Lift Tube at +26.0m (`lift_emerge`),
      //   holding 0.90s (11.20s .. 12.10s) inside the crimson lift portal, then gliding smoothly at 30fps
      //   (12.10s .. 19.60s) past the swiveled Broadcast Stool (`operator_pov`, d = 2.08m) to `cold_open_final`
      //   (`d = 1.36m`, `tilt = HERO_SCREEN_TILT = 0.18 rad`, `fov = 48.0°`) 100% perpendicular to the
      //   16:9 Master Show Director HUD screen!
      if (t < 11.20) {
        camera.position.set(78.0, -14.0, 54.0);
        controls.target.set(-2.0, 32.5, 0.0);
        camera.fov = 56.0;
      } else {
        const u = smoothstep(12.10, 19.60, t);
        const curDist = COLD_OPEN_DIST_START * (1.0 - u) + COLD_OPEN_DIST_END * u;
        const curTilt = COLD_OPEN_TILT_START * (1.0 - u) + COLD_OPEN_TILT_END * u;
        const curFov = 58.0 * (1.0 - u) + 48.0 * u;
        camera.fov = curFov;
        camera.position.set(
          HERO_SCREEN_CENTER.x,
          HERO_SCREEN_CENTER.y + curDist * Math.sin(curTilt),
          HERO_SCREEN_CENTER.z + curDist * Math.cos(curTilt)
        );
        controls.target.copy(HERO_SCREEN_CENTER);
      }
      camera.updateProjectionMatrix();

      // Update the live 16:9 Master Show Director HUD canvas (`renderBroadcastShowDashboard`)
      // and perimeter console screens on interior beats without overwriting Bay 0's `showHudTex`!
      const cState = t < 13.80 ? 0 : (t < 16.50 ? 1 : (t < 19.20 ? 2 : (t < 20.60 ? 3 : 0)));
      if (_lastShowHudIdx !== cState && typeof renderBroadcastShowDashboard === 'function') {
        _lastShowHudIdx = cState;
        renderBroadcastShowDashboard(cState);
      }
      CONSOLE_BAYS.forEach((bay, bIdx) => {
        if (bay.machineType === 'broadcast_cockpit_3screen') return;
        const idx = (bIdx + cState) % bay.screens.length;
        if (bay.screenStateIdx !== idx && bay.screenTextures && bay.screenTextures[idx] && bay.screenMat) {
          bay.screenStateIdx = idx;
          bay.screenMat.map = bay.screenTextures[idx];
          bay.screenMat.needsUpdate = true;
        }
      });

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

      // ── 5. O.R.S. 351 ORBIT, VAN ALLEN STROBES & ASTEROID 3-5-1 SIDEREAL SKY SPIN ──
      const satPhase = t * 0.055;
      ors351Sat.position
        .copy(satOrbitCenter)
        .addScaledVector(satOrbitU1, satOrbitR * Math.cos(satPhase))
        .addScaledVector(satOrbitU2, satOrbitR * Math.sin(satPhase));
      ors351Sat.lookAt(satOrbitCenter);
      ors351Sat.updateMatrixWorld(true);

      const blinkSlot = Math.floor(t * 1.25) % 2;
      const cyanOn = blinkSlot === 0 ? 1.0 : 0.0;
      const amberOn = blinkSlot === 1 ? 1.0 : 0.0;
      if (cyanOn > 0.5) {
        satCyanBeaconMat.color.setHex(0x38e8ff);
        satAmberBeaconMat.color.setHex(0x221608);
      } else {
        satCyanBeaconMat.color.setHex(0x0a1e24);
        satAmberBeaconMat.color.setHex(0xffaa2b);
      }
      orbitalSatellites.forEach((sat) => {
        const distToCam = camera.position.distanceTo(sat.group.position);
        const isDistantBoothView = distToCam > 60.0;
        const bodyDistFactor = isDistantBoothView
          ? Math.min(3.4, 1.15 + (distToCam - 60.0) * 0.008)
          : 0.70;
        const towerFacingDistFactor = isDistantBoothView
          ? Math.min(7.8, 2.4 + (distToCam - 60.0) * 0.022)
          : 0.58;
        sat.cyanFlares.forEach((fl) => {
          const df = fl.isTowerFacing ? towerFacingDistFactor : bodyDistFactor;
          const s = fl.baseScale * df;
          fl.sprite.scale.set(s, s, 1.0);
          fl.mat.opacity = (fl.isTowerFacing ? (isDistantBoothView ? 0.90 : 0.34) : 0.48) * cyanOn;
        });
        sat.amberFlares.forEach((fl) => {
          const df = fl.isTowerFacing ? towerFacingDistFactor : bodyDistFactor;
          const s = fl.baseScale * df;
          fl.sprite.scale.set(s, s, 1.0);
          fl.mat.opacity = (fl.isTowerFacing ? (isDistantBoothView ? 0.90 : 0.34) : 0.48) * amberOn;
        });
        sat.amberLights[0].intensity = 2.6 * amberOn;
        sat.amberLights[1].intensity = 1.8 * amberOn;
        sat.cyanLights[0].intensity = 2.6 * cyanOn;
        sat.cyanLights[1].intensity = 1.8 * cyanOn;
      });

      const ASTEROID_SPIN_RATE = 0.015; // rad/s
      const spinAngle = t * ASTEROID_SPIN_RATE;
      skyGroup.rotation.y = -spinAngle;
      skyGroup.rotation.x = 0.038 * Math.sin(spinAngle * 0.5);

      const starMapUVShift = ((spinAngle / (Math.PI * 2.0)) % 1.0 + 1.0) % 1.0;
      starMapPanTextures.forEach((stTex) => {
        stTex.offset.x = starMapUVShift;
      });
      if (armillarySpinGroup) {
        armillarySpinGroup.rotation.y = -spinAngle * 2.4;
      }
      driftingAsteroids.forEach((a, idx) => {
        a.mesh.rotation.x = idx * 0.7 + t * a.rx * 30.0;
        a.mesh.rotation.y = idx * 1.3 + t * a.ry * 30.0;
      });

      controls.enableDamping = false;
      if (renderer.domElement.width !== 2560 || renderer.domElement.height !== 1440) {
        renderer.setPixelRatio(1);
        renderer.setSize(2560, 1440, false);
      }
      camera.aspect = 2560 / 1440;
      camera.updateProjectionMatrix();
      controls.update();
      renderer.render(scene, camera);
    }

    async function runColdOpenCapture() {
      const params = new URLSearchParams(window.location.search);
      const fps = parseFloat(params.get('fps') || '30');
      const duration = parseFloat(params.get('dur') || '21.62');
      const workerId = params.get('wid') || '0';
      const pairsStr = params.get('pairs');

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
      _lastShowHudIdx = -1;

      // Upgrade shockwave rings & discharge sphere to high-segment smooth geometry for 30fps radiation
      marzelShockwaves.forEach((sw) => {
        sw.mesh.geometry.dispose();
        sw.mesh.geometry = new THREE.TorusGeometry(1.0, 0.035, 32, 128);
      });
      burstSphereMesh.geometry.dispose();
      burstSphereMesh.geometry = new THREE.SphereGeometry(1.0, 64, 48);

      const capW = parseInt(params.get('w') || '2560', 10);
      const capH = parseInt(params.get('h') || '1440', 10);

      // Force exact 2560x1440 (16:9 QHD) WebGL canvas dimensions regardless of headless window chrome
      renderer.setPixelRatio(1);
      renderer.setSize(capW, capH, false);
      camera.aspect = capW / capH;
      camera.updateProjectionMatrix();

      const gl = renderer.getContext();
      const pixelBuf = new Uint8Array(capW * capH * 4);
      async function sendFrame(actualIdx) {
        gl.finish();
        gl.readPixels(0, 0, capW, capH, gl.RGBA, gl.UNSIGNED_BYTE, pixelBuf);
        for (let att = 0; att < 5; att++) {
          try {
            const resp = await fetch(`/__raw_rgba/${actualIdx}`, { method: 'POST', body: pixelBuf });
            if (resp.ok) break;
          } catch (err) {}
          await new Promise((r) => setTimeout(r, 60));
        }
      }

      const dt = 1.0 / fps;
      if (pairsStr) {
        const items = pairsStr.split(',');
        await fetch('/__js_log', { method: 'POST', body: `wid=${workerId} starting ${items.length} frames at ${capW}x${capH}` });
        for (let i = 0; i < items.length; i++) {
          const [idxStr, tStr] = items[i].split(':');
          const actualIdx = parseInt(idxStr, 10);
          const t = parseFloat(tStr);
          setStationStateAtTime(t, dt);
          await sendFrame(actualIdx);
        }
        await fetch(`/__done/${workerId}`, { method: 'POST' });
        return;
      }

      const totalFrames = Math.ceil(duration * fps);
      for (let f = 0; f < totalFrames; f++) {
        const t = f / fps;
        setStationStateAtTime(t, dt);
        await sendFrame(f);
      }
      await fetch(`/__done/${workerId}`, { method: 'POST' });
    }

    runColdOpenCapture().catch((err) => {
      fetch('/__js_log', { method: 'POST', body: 'JS_ERR: ' + String((err && err.stack) || err) });
    });
"""


def _rgba_bottom_up_to_png_bytes(data: bytes, width: int, height: int) -> bytes:
    """Convert bottom-up WebGL RGBA bytes into a valid lossless PNG in ~20ms using stdlib zlib."""
    import struct
    import zlib

    row_bytes = width * 4
    scanlines = b"".join(
        b"\x00" + data[(height - 1 - y) * row_bytes : (height - y) * row_bytes]
        for y in range(height)
    )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(scanlines, level=1)

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def _build_cold_open_concat_steps(total_dur: float = 21.62, fps: int = 30) -> list[tuple[float, float, str]]:
    """Build full 30.00 fps Cold Open frame steps (649 frames at 1/30s = 21.62s)
    so that Asteroid 3-5-1's sidereal starfield spin, O.R.S. 351's orbit, the Marzelvane burst,
    and the Lift-to-Dashboard glide all animate continuously at 30.00 fps on both static and moving shots.
    """
    n_frames = int(round(total_dur * fps))
    dt = 1.0 / float(fps)
    steps: list[tuple[float, float, str]] = []
    for f in range(n_frames):
        t_sample = round(f * dt, 5)
        steps.append((t_sample, round(dt, 6), f"Cold Open 30fps frame {f:04d} (t={t_sample:.3f}s)"))
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
    width: int = 2560,
    height: int = 1440,
    test_times: list[float] | None = None,
    clean: bool = True,
    workers: int = 4,
    time_budget: float = 0.0,
) -> list[Path]:
    import time

    t_global_start = time.monotonic()
    subprocess.run(["pkill", "-9", "-f", "gor9_coldopen_w"], check=False)
    if clean and out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    times_list = test_times if test_times is not None else [f / float(fps) for f in range(int(round(duration * fps)))]

    # Read docs/tower-3d.html dynamically into memory without touching the file on disk
    # and disable window.addEventListener('resize' so headless Chromium window chrome never resizes the canvas.
    raw_html = (DOCS_DIR / "tower-3d.html").read_text(encoding="utf-8")
    raw_html = raw_html.replace(
        "window.addEventListener('resize'",
        "window.addEventListener('__disabled_resize'",
    )
    target_anchor = "    animate();\n  </script>"
    if target_anchor not in raw_html:
        target_anchor = "animate();"
    injected_html = raw_html.replace(target_anchor, INJECTED_CAPTURE_JS + "\n  </script>", 1)
    injected_bytes = injected_html.encode("utf-8")

    lock = threading.Lock()
    existing_initial = sum(1 for idx in range(len(times_list)) if (out_dir / f"frame_{idx:04d}.png").exists())
    received_count = existing_initial
    done_workers: set[str] = set()

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
            if self.path.startswith("/__js_log"):
                length = int(self.headers.get("Content-Length", "0"))
                msg = self.rfile.read(length).decode("utf-8", errors="replace")
                print(f"  [JS] {msg}", flush=True)
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"OK")
                return
            if self.path.startswith("/__raw_rgba/"):
                actual_idx = int(self.path.split("/__raw_rgba/")[1])
                length = int(self.headers.get("Content-Length", "0"))
                data = self.rfile.read(length)
                png_bytes = _rgba_bottom_up_to_png_bytes(data, width, height)
                frame_path = out_dir / f"frame_{actual_idx:04d}.png"
                frame_path.write_bytes(png_bytes)
                with lock:
                    received_count += 1
                    rc = received_count
                if rc % 5 == 0 or rc == len(times_list):
                    print(f"  [tower-3d capture] {rc}/{len(times_list)} frames (saved frame_{actual_idx:04d}.png)", flush=True)
                try:
                    self.send_response(200)
                    self.send_header("Content-Length", "2")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    self.wfile.write(b"OK")
                except BrokenPipeError:
                    pass
                return
            if self.path.startswith("/__done/"):
                wid = self.path.split("/__done/")[1]
                with lock:
                    done_workers.add(wid)
                try:
                    self.send_response(200)
                    self.send_header("Content-Length", "4")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    self.wfile.write(b"DONE")
                except BrokenPipeError:
                    pass
                return
            self.send_response(404)
            self.end_headers()

    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
        daemon_threads = True

    chrome_bin = find_chrome_binary()

    with ThreadedTCPServer(("127.0.0.1", 0), CaptureRequestHandler) as httpd:
        port = httpd.server_address[1]
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        # Loop until all frames are present on disk (resumes automatically if any worker stalls)
        for pass_num in range(10):
            if time_budget > 0.0 and (time.monotonic() - t_global_start) >= time_budget - 3.0:
                break
            missing_pairs = [
                (idx, t)
                for idx, t in enumerate(times_list)
                if not (out_dir / f"frame_{idx:04d}.png").exists()
            ]
            if not missing_pairs:
                break

            n_workers = min(workers, len(missing_pairs))
            chunks = [missing_pairs[w::n_workers] for w in range(n_workers)]
            print(
                f"Launching {n_workers} parallel WebGL workers (pass {pass_num + 1}) "
                f"for {len(missing_pairs)} missing frames at {width}x{height}...",
                flush=True,
            )
            with lock:
                done_workers.clear()

            procs: list[tuple[subprocess.Popen, Path]] = []
            win_h = max(height + 120, 1560)
            for w, chunk in enumerate(chunks):
                wid = str(w)
                pairs_q = ",".join(f"{idx}:{t:.5f}" for idx, t in chunk)
                url = (
                    f"http://127.0.0.1:{port}/__capture_cold_open.html"
                    f"?fps={fps}&dur={duration:.3f}&w={width}&h={height}&wid={wid}&pairs={pairs_q}"
                )
                tmp_profile = Path(f"/tmp/gor9_coldopen_w{w}_{os.getpid()}")
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
                    f"--window-size={width},{win_h}",
                    url,
                ]
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                procs.append((proc, tmp_profile))

            t0 = time.monotonic()
            max_wait = (time_budget - (t0 - t_global_start)) if time_budget > 0.0 else 600.0
            while time.monotonic() - t0 < max_wait:
                with lock:
                    if len(done_workers) >= n_workers:
                        break
                if all(p.poll() is not None for p, _ in procs):
                    break
                time.sleep(0.3)

            subprocess.run(["pkill", "-9", "-f", "gor9_coldopen_w"], check=False)
            for proc, tmp_profile in procs:
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    proc.kill()
                shutil.rmtree(tmp_profile, ignore_errors=True)

            if time_budget > 0.0 and (time.monotonic() - t_global_start) >= time_budget - 2.0:
                break

        httpd.shutdown()

    return [out_dir / f"frame_{i:04d}.png" for i in range(len(times_list))]


def encode_qhd_mp4_from_frames(
    frames_dir: Path,
    audio_wav: Path,
    out_mp4: Path,
    duration: float,
    fps: int = 30,
) -> None:
    """Encode native 2560x1440 30.00 fps PNG sequence + WAV audio to QHD High@L5.1 MP4."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "/usr/bin/ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-start_number",
        "0",
        "-i",
        str(frames_dir / "frame_%04d.png"),
        "-i",
        str(audio_wav),
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True)
    print(f"Encoded 2560x1440 MP4 (direct ffmpeg) -> {out_mp4}", flush=True)


def ensure_youtube_json(video_dir: Path) -> Path:
    import json

    yt_path = video_dir / "youtube.json"
    if not yt_path.exists():
        meta = {
            "short_code": "COLD-OPEN",
            "g_id": "2736.305",
            "channel": "@GOR-9-station",
            "categoryId": "24",
            "privacyStatus": "unlisted",
            "title_1080p": "GOR-9 • Galactic Outpost Radio: High Basalt Shelf Tower Cold Open (14,285.7 kHz USB • 0400 GCT)",
            "description": (
                "This is GOR-9. Galactic Outpost Radio, broadcasting at 50 kilowatts from the High Basalt Shelf Tower "
                "on Asteroid 3-5-1, 42,100 AU out in Oort Cloud Sector 9.\n"
                "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
                "0:00 Station Power-Up & Vertical GOR-9 Sign Ignition\n"
                "0:04 4-Ring Marzelvane Cherenkov Burst & 1B C-Lydian Signal Lock\n"
                "0:11 Central Lift Tube Emerge & Octagonal Broadcast Deck Glide"
            ),
            "tags": [
                "GOR-9",
                "Galactic Outpost Radio",
                "Marzelvane",
                "Shortwave",
                "Sci-Fi",
            ],
            "files": {
                "wide_1080p_mp4": str(OUT_COLD_OPEN_MP4),
                "thumbnail_16x9_png": str(OUT_COLD_OPEN_THUMB),
            },
            "uploads": {},
            "history": {},
        }
        yt_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return yt_path


def main() -> None:
    import sys

    parser = argparse.ArgumentParser(description="Capture GOR-9 Cold Open in native 2560x1440 QHD to videos/cold_open/")
    parser.add_argument("--test-frames", action="store_true", help="Capture 6 diagnostic keyframes only")
    parser.add_argument("--width", type=int, default=2560, help="Native WebGL render width (default: 2560)")
    parser.add_argument("--height", type=int, default=1440, help="Native WebGL render height (default: 1440)")
    parser.add_argument("--workers", type=int, default=3, help="Parallel headless Chromium workers")
    parser.add_argument("--time-budget", type=float, default=0.0, help="Optional max seconds to run before saving progress and exiting cleanly")
    parser.add_argument("--no-clean", action="store_true", help="Resume without wiping existing frames")
    parser.add_argument("--encode-only", action="store_true", help="Re-encode MP4 from existing frames in videos/cold_open/frames/")
    parser.add_argument("--daemon", action="store_true", help="Spawn continuous background render job writing to videos/cold_open/render.log")
    parser.add_argument("--status", action="store_true", help="Check progress of videos/cold_open/ frames and render.log")
    parser.add_argument(
        "--replace-range",
        type=str,
        default=None,
        help="Optional inclusive frame index range start:end (e.g. 336:648) to delete and re-render without wiping other frames",
    )
    args = parser.parse_args()

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    if not COLD_OPEN_WAV.exists() and SRC_COLD_OPEN_WAV.exists():
        shutil.copy2(SRC_COLD_OPEN_WAV, COLD_OPEN_WAV)
    ensure_youtube_json(VIDEO_DIR)

    log_path = VIDEO_DIR / "render.log"
    if args.status:
        n_frames = len(list(FRAMES_DIR.glob("frame_*.png"))) if FRAMES_DIR.exists() else 0
        mp4_info = f"{OUT_COLD_OPEN_MP4.stat().st_size / (1024*1024):.2f} MB" if OUT_COLD_OPEN_MP4.exists() else "not yet encoded"
        print(f"[Cold Open Status] Frames: {n_frames}/{len(COLD_OPEN_CONCAT_STEPS)} | MP4: {mp4_info}")
        if log_path.exists():
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            print("--- Last 15 log lines ---")
            for ln in lines[-15:]:
                print(ln)
        return

    if args.daemon:
        pid_file = VIDEO_DIR / "daemon.pid"
        if pid_file.exists():
            try:
                old_pid = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(old_pid, 9)
            except Exception:
                pass
        subprocess.run(["pkill", "-9", "-f", "capture_tower3d_cold_open.py --workers"], check=False)
        subprocess.run(["pkill", "-9", "-f", "gor9_coldopen_w"], check=False)
        if not args.no_clean and FRAMES_DIR.exists():
            shutil.rmtree(FRAMES_DIR, ignore_errors=True)
        FRAMES_DIR.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--workers",
            str(args.workers),
            "--width",
            str(args.width),
            "--height",
            str(args.height),
            "--no-clean",
        ]
        log_f = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=log_f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        pid_file.write_text(str(proc.pid), encoding="utf-8")
        print(f"Spawned Cold Open 2560x1440 background render daemon (PID={proc.pid}) -> {log_path}")
        return

    dur = get_wav_duration(COLD_OPEN_WAV)
    if args.test_frames:
        test_dir = VIDEO_DIR / "test_frames"
        capture_sequence(
            test_dir,
            fps=30,
            duration=dur,
            width=args.width,
            height=args.height,
            test_times=[0.15, 1.60, 3.85, 5.35, 11.50, 15.85, 20.50],
            clean=not args.no_clean,
            workers=args.workers,
            time_budget=args.time_budget,
        )
        return

    sample_times = [step[0] for step in COLD_OPEN_CONCAT_STEPS]
    clean_dir = not args.no_clean
    if args.replace_range:
        clean_dir = False
        start_s, end_s = args.replace_range.split(":", 1)
        start_idx, end_idx = int(start_s), int(end_s)
        removed = 0
        for idx in range(start_idx, end_idx + 1):
            p = FRAMES_DIR / f"frame_{idx:04d}.png"
            if p.exists():
                p.unlink()
                removed += 1
        print(f"Removed {removed} frames in range {start_idx}..{end_idx} from {FRAMES_DIR}", flush=True)

    if not args.encode_only:
        slide_pngs = capture_sequence(
            FRAMES_DIR,
            fps=30,
            duration=dur,
            width=args.width,
            height=args.height,
            test_times=sample_times,
            clean=clean_dir,
            workers=args.workers,
            time_budget=args.time_budget,
        )
    else:
        slide_pngs = [FRAMES_DIR / f"frame_{i:04d}.png" for i in range(len(sample_times))]

    present_count = sum(1 for p in slide_pngs if p.exists())
    if present_count < len(slide_pngs):
        print(
            f"[Partial Progress] {present_count}/{len(slide_pngs)} frames present in {FRAMES_DIR}. "
            "Re-run with --no-clean to finish remaining frames and encode MP4.",
            flush=True,
        )
        return

    encode_qhd_mp4_from_frames(FRAMES_DIR, COLD_OPEN_WAV, OUT_COLD_OPEN_MP4, duration=dur, fps=30)
    print(f"Saved master QHD MP4 -> {OUT_COLD_OPEN_MP4}", flush=True)

    thumb_src = slide_pngs[min(len(slide_pngs) - 1, 160)]
    if thumb_src.exists():
        subprocess.run(
            ["/usr/bin/ffmpeg", "-y", "-i", str(thumb_src), "-q:v", "4", str(OUT_COLD_OPEN_THUMB)],
            check=True,
        )
        print(f"Exported Cold Open thumbnail -> {OUT_COLD_OPEN_THUMB}", flush=True)


if __name__ == "__main__":
    main()


