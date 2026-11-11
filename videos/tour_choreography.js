
    // ═════════════════════════════════════════════════════════════════
    // DETERMINISTIC 30FPS DRONE TOUR & SATELLITE ORBIT CAPTURE ENGINE
    // (Served in-memory without modifying docs/tower-3d.html on disk)
    // ═════════════════════════════════════════════════════════════════
    let _lastHudState = -1;

    function setTourStateAtTime(mode, t, duration, width = 2560, height = 1440) {
      // Hide HTML HUD overlays for clean 16:9 QHD cinema capture
      const topNav = document.querySelector('.top-nav');
      if (topNav) topNav.style.display = 'none';
      const hudL = document.getElementById('hud-left');
      if (hudL) hudL.style.display = 'none';
      const hudR = document.getElementById('hud-right');
      if (hudR) hudR.style.display = 'none';
      const hudB = document.getElementById('hud-bottom');
      if (hudB) hudB.style.display = 'none';

      // Ensure Station, Tower, and Booth ON AIR lights are 100% energized
      matTowerAmber.color.setHex(0xffaa2b);
      matTowerCyan.color.setHex(0x38e8ff);
      matTowerSpireCore.color.setHex(0xb8f8ff);
      matTowerCrimson.color.setHex(0xff1408);
      towerStructureLight.intensity = 5.5;
      habLight.intensity = 4.5;
      reactorLight.intensity = 6.0;

      matBoothRedGlow.color.setHex(0xe60804);
      matCrimsonGlow.color.setHex(0xff1408);
      matMicTally.color.setHex(0xff1408);
      boothInKneeMats.forEach((m) => {
        m.emissiveIntensity = 0.08;
      });
      ceilingSoffit.material.emissiveIntensity = 0.12;
      boothWarmLight.intensity = 7.5;
      deskFillLight.intensity = 3.8;
      boothBeaconLight.intensity = 12.0;

      // 1. O.R.S. 351 Satellite Position along its 22°-tilted circular orbit
      //    - In 'satellite_orbit' mode: completes exactly 1 full 360° (2*PI) orbital pass over `duration` (30.00s)
      //    - In 'drone_tour' mode: glides across the background sky (`t * 0.12`)
      const satPhase = mode === 'satellite_orbit'
        ? (t / duration) * Math.PI * 2.0
        : t * 0.12;

      ors351Sat.position
        .copy(satOrbitCenter)
        .addScaledVector(satOrbitU1, satOrbitR * Math.cos(satPhase))
        .addScaledVector(satOrbitU2, satOrbitR * Math.sin(satPhase));
      ors351Sat.lookAt(satOrbitCenter);
      ors351Sat.updateMatrixWorld(true);

      // 2. Camera Trajectory: Drone Tour vs Satellite Orbit
      if (mode === 'drone_tour') {
        // Complete 360° orbital flight around the 86.5m Tower & Asteroid 3-5-1,
        // starting wide over Acheron Chasm (92m), swooping close-up (21m) past the
        // crimson Broadcast Booth (+26m), vertical G/O/R/◎/9 Sign (+39..52m), and
        // Marzelvane Crown (+72m), then pulling out wide (92m) for the finale burst!
        const u = t / duration;
        const az = 0.42 + u * Math.PI * 2.0;
        const zoomWave = 0.5 - 0.5 * Math.cos(u * Math.PI * 2.0); // 0 = Wide (92m), 1 = Close-up (21m)
        const distR = 92.0 * (1.0 - zoomWave) + 21.0 * zoomWave;
        const heightWave = 0.5 + 0.5 * Math.sin(u * Math.PI * 2.0 - 0.45);
        const chasmDip = Math.max(0.0, Math.cos(az - 0.45)) * (1.0 - zoomWave) * 16.0;
        const camY = 26.5 + 47.5 * heightWave - chasmDip;
        const targetY = 27.0 + 36.5 * (0.5 + 0.5 * Math.sin(u * Math.PI * 2.0 - 0.65));

        camera.fov = 48.0;
        camera.updateProjectionMatrix();
        camera.position.set(Math.cos(az) * distR, camY, Math.sin(az) * distR);
        controls.target.set(0.0, targetY, 0.0);
      } else {
        // Satellite Orbit [1]: Locked to O.R.S. 351's local frame as it completes one full 360° pass!
        camera.fov = 42.0;
        camera.updateProjectionMatrix();
        camera.position.copy(satCamLocalPos).applyMatrix4(ors351Sat.matrixWorld);
        controls.target.copy(satCamLocalTarget).applyMatrix4(ors351Sat.matrixWorld);
      }

      // 3. Asynchronous Console Screen Cycling inside the Broadcast Booth
      const cState = Math.floor(t / 2.5) % 4;
      if (_lastHudState !== cState && typeof renderBroadcastShowDashboard === 'function') {
        _lastHudState = cState;
        renderBroadcastShowDashboard(cState);
      }
      CONSOLE_BAYS.forEach((bay, bIdx) => {
        if (bay.machineType === 'broadcast_cockpit_3screen') return;
        const idx = Math.floor(t / bay.cyclePeriod + bIdx) % bay.screens.length;
        if (bay.screenStateIdx !== idx && bay.screenTextures && bay.screenTextures[idx] && bay.screenMat) {
          bay.screenStateIdx = idx;
          bay.screenMat.map = bay.screenTextures[idx];
          bay.screenMat.needsUpdate = true;
        }
      });

      // 4. 3 Synchronized Marzelvane 4-Ring Power-Up & Barycentric Cherenkov Bursts!
      //    Burst windows start at t = 2.00s, 12.00s, and 22.00s:
      //      +0.00s: Ring 1 (C4)
      //      +0.20s: Ring 2 (G4)
      //      +0.40s: Ring 3 (D5)
      //      +0.60s: Ring 4 (F#5)
      //      +0.84s: Spire Lock & Expanding Barycentric Shockwave Burst!
      const burstStarts = [2.00, 12.00, 22.00];
      const burstDur = 5.60;
      let activeBt = -1.0;
      let activeBurstIdx = -1;
      for (let bi = 0; bi < burstStarts.length; bi++) {
        const dtB = t - burstStarts[bi];
        if (dtB >= 0.0 && dtB <= burstDur) {
          activeBt = dtB;
          activeBurstIdx = bi;
          break;
        }
      }

      const spireLockOffset = 0.84;
      let climaxFlash = 0.0;
      let coreSurge = 0.0;
      if (activeBt >= 0.0) {
        if (activeBt >= spireLockOffset - 0.04) {
          const rise = smoothstep(spireLockOffset - 0.04, spireLockOffset + 0.16, activeBt);
          const dtAfter = Math.max(0.0, activeBt - (spireLockOffset + 0.16));
          const fall = Math.exp(-dtAfter / 1.95) * (1.0 - smoothstep(4.50, burstDur, activeBt));
          climaxFlash = rise * fall * (activeBurstIdx === 2 ? 1.20 : 1.0);
        }
        coreSurge = smoothstep(0.0, 0.24, activeBt) * (1.0 - smoothstep(4.20, burstDur, activeBt));
      }

      const satBoost = mode === 'satellite_orbit' ? 1.35 : 1.0;
      let totalRingEnergy = 0.0;

      marzelRings.forEach((ring, rIdx) => {
        const idleWave = 0.5 + 0.5 * Math.sin(t * 3.4 - ring.phaseOffset);
        let ringCharge = 0.0;
        let ignFlash = 0.0;
        let spokeSurge = 0.0;

        if (activeBt >= 0.0) {
          const tRingNote = rIdx * 0.20; // 0.00, 0.20, 0.40, 0.60s
          const tRingFull = tRingNote + 0.18;
          const rampUp = smoothstep(tRingNote, tRingFull, activeBt);
          const dtHold = Math.max(0.0, activeBt - spireLockOffset);
          const coolDown = Math.exp(-dtHold / (2.05 + rIdx * 0.20)) * (1.0 - smoothstep(4.50, burstDur, activeBt));
          ringCharge = rampUp * coolDown;

          if (activeBt >= tRingNote && activeBt <= tRingFull + 0.28) {
            ignFlash = Math.sin(smoothstep(tRingNote, tRingFull + 0.28, activeBt) * Math.PI);
          }
          if (activeBt >= tRingNote - 0.10 && activeBt <= tRingFull + 0.14) {
            spokeSurge = Math.sin(smoothstep(tRingNote - 0.10, tRingFull + 0.14, activeBt) * Math.PI);
          }
        }

        const e = Math.min(1.6, ringCharge + 0.72 * ignFlash + 0.90 * climaxFlash);
        totalRingEnergy += e;

        const w = Math.min(1.0, idleWave * 0.65 + e * 0.85);
        const whiteMix = Math.min(1.0, 0.58 * ringCharge + 0.78 * ignFlash + 0.88 * climaxFlash);

        ring.glowMatTop.color.setRGB(
          Math.min(1.0, 0.18 + 0.45 * w + 0.55 * whiteMix),
          Math.min(1.0, 0.82 + 0.18 * w + 0.18 * whiteMix),
          1.0
        );
        ring.glowMatBot.color.setRGB(
          Math.min(1.0, 0.35 + 0.55 * w + 0.40 * whiteMix),
          Math.min(1.0, 0.92 + 0.08 * w + 0.08 * whiteMix),
          1.0
        );
        const tubeScale = (1.0 + 0.80 * ringCharge + 0.70 * ignFlash + 0.90 * climaxFlash) * satBoost;
        ring.glowTop.scale.set(1.0, 1.0, tubeScale);
        ring.glowBot.scale.set(1.0, 1.0, tubeScale);

        ring.innerHaloMat.opacity = Math.min(
          0.62,
          (0.10 + 0.06 * idleWave + 0.28 * ringCharge + 0.20 * ignFlash + 0.24 * climaxFlash) * satBoost
        );
        ring.innerHaloMat.color.setRGB(
          Math.min(1.0, 0.26 + 0.66 * whiteMix),
          Math.min(1.0, 0.90 + 0.10 * whiteMix),
          1.0
        );
        const innerScale = 1.0 + 0.42 * ringCharge + 0.52 * ignFlash + 0.68 * climaxFlash;
        ring.innerHalo.scale.set(1.0, 1.0, innerScale);

        ring.outerHaloMat.opacity = Math.min(
          0.38,
          (0.04 + 0.02 * idleWave + 0.16 * ringCharge + 0.12 * ignFlash + 0.16 * climaxFlash) * satBoost
        );
        const outerScale = 1.0 + 0.55 * ringCharge + 0.65 * ignFlash + 0.90 * climaxFlash;
        ring.outerHalo.scale.set(1.0, 1.0, outerScale);

        ring.superHaloMat.opacity = Math.min(
          0.22,
          (0.08 * ringCharge + 0.10 * ignFlash + 0.14 * climaxFlash) * satBoost
        );
        const superScale = 1.0 + 0.55 * ringCharge + 1.05 * climaxFlash;
        ring.superHalo.scale.set(1.0, 1.0, superScale);

        ring.spokeGlowMat.opacity = Math.min(
          0.90,
          0.08 + 0.45 * ringCharge + 0.62 * spokeSurge + 0.42 * climaxFlash
        );
        ring.spokeGlowMat.color.setRGB(
          Math.min(1.0, 0.25 + 0.75 * (spokeSurge + climaxFlash)),
          0.95,
          1.0
        );

        ring.tipMat.color.setRGB(
          Math.min(1.0, 0.55 + 0.45 * (ringCharge + ignFlash + climaxFlash)),
          Math.min(1.0, 0.94 + 0.06 * ringCharge),
          1.0
        );
        ring.tipSpriteMat.opacity = Math.min(
          0.96,
          0.38 + 0.10 * idleWave + 0.48 * ringCharge + 0.32 * ignFlash + 0.34 * climaxFlash
        );
        const spScale =
          (0.86 + 0.14 * idleWave + 1.45 * ringCharge + 1.20 * ignFlash + 1.60 * climaxFlash) * satBoost;
        ring.tipSprites.forEach((sp, sIdx) => {
          const mult = sIdx % 2 === 0 ? 1.0 : 0.82;
          sp.scale.set(spScale * mult, spScale * mult, 1.0);
        });
      });

      const meanRingEnergy = totalRingEnergy * 0.25;
      const idleHubPulse = 0.5 + 0.5 * Math.sin(t * 3.4);
      hubCoreGlowMat.opacity = Math.min(0.82, 0.15 + 0.06 * idleHubPulse + 0.38 * coreSurge + 0.44 * climaxFlash);
      spireAuraMat.opacity = Math.min(0.55, 0.05 + 0.03 * idleHubPulse + 0.20 * meanRingEnergy + 0.36 * climaxFlash);

      const hubScale = hubFlare.baseScale * satBoost * (0.95 + 0.10 * idleHubPulse + 1.15 * coreSurge + 1.75 * climaxFlash);
      hubFlare.sprite.scale.set(hubScale, hubScale, 1.0);
      hubFlare.mat.opacity = Math.min(0.90, hubFlare.baseOpacity + 0.32 * coreSurge + 0.40 * climaxFlash);

      const midScale = midSpireFlare.baseScale * satBoost * (0.95 + 0.10 * idleHubPulse + 0.95 * meanRingEnergy + 1.85 * climaxFlash);
      midSpireFlare.sprite.scale.set(midScale, midScale, 1.0);
      midSpireFlare.mat.opacity = Math.min(0.88, midSpireFlare.baseOpacity + 0.28 * meanRingEnergy + 0.42 * climaxFlash);

      const apexScale = apexSpireFlare.baseScale * satBoost * (0.95 + 0.12 * idleHubPulse + 1.05 * meanRingEnergy + 2.45 * climaxFlash);
      apexSpireFlare.sprite.scale.set(apexScale, apexScale, 1.0);
      apexSpireFlare.mat.opacity = Math.min(0.92, apexSpireFlare.baseOpacity + 0.28 * meanRingEnergy + 0.42 * climaxFlash);

      // Expanding Barycentric Shockwave Rings & Spherical Discharge Wave on each of the 3 bursts!
      const maxSwRad = mode === 'satellite_orbit' ? 115.0 : 72.0;
      marzelShockwaves.forEach((sw, swIdx) => {
        const swStart = spireLockOffset + swIdx * 0.38;
        const swDur = 3.10;
        if (activeBt >= swStart && activeBt <= swStart + swDur) {
          const p = (activeBt - swStart) / swDur;
          const easeOut = 1.0 - Math.pow(1.0 - p, 1.65);
          const rad = 4.5 + maxSwRad * easeOut;
          sw.mesh.visible = true;
          sw.mesh.scale.set(rad, rad, 1.3 + 5.2 * p);
          sw.mesh.position.y = (swIdx - 0.5) * 2.8 * p;
          sw.mat.opacity = Math.sin(p * Math.PI) * Math.pow(1.0 - p, 0.85) * (mode === 'satellite_orbit' ? 0.65 : 0.48);
        } else {
          sw.mesh.visible = false;
          sw.mat.opacity = 0.0;
        }
      });

      if (activeBt >= spireLockOffset && activeBt <= spireLockOffset + 3.25) {
        const spP = (activeBt - spireLockOffset) / 3.25;
        const spRad = 5.0 + (maxSwRad * 0.92) * (1.0 - Math.pow(1.0 - spP, 1.65));
        burstSphereMesh.visible = true;
        burstSphereMesh.scale.set(spRad, spRad * 0.62, spRad);
        burstSphereMat.opacity = Math.sin(spP * Math.PI) * Math.pow(1.0 - spP, 1.10) * (mode === 'satellite_orbit' ? 0.26 : 0.18);
      } else {
        burstSphereMesh.visible = false;
        burstSphereMat.opacity = 0.0;
      }

      marzelLight.intensity = 13.0 + 3.5 * Math.sin(t * 3.4) + 28.0 * meanRingEnergy + 58.0 * climaxFlash;
      marzelBurstLight.intensity = 24.0 * meanRingEnergy + 115.0 * climaxFlash;

      // 5. Vertical "G / O / R / ◎ / 9" Sign Animated Sequence!
      //    Locks all 5 slots bright during the peak of each Marzelvane Burst, and runs the
      //    animated G -> O -> R -> ◎ -> 9 -> ALL LIT sequence between bursts!
      if (climaxFlash > 0.18) {
        const boost = Math.min(1.25, 0.95 + 0.30 * climaxFlash);
        signSlotMats.forEach((sm) => {
          sm.face.color.setRGB(0.88 * boost, 0.03 * boost, 0.0);
          sm.core.color.setRGB(1.0, 0.12 * boost, 0.04 * boost);
          sm.retGlow.color.setRGB(0.25 * boost, 0.94 * boost, 1.0);
          sm.retCore.color.setRGB(0.76 * boost, 0.98 * boost, 1.0);
        });
        signLightESE.color.setHex(0xff0804);
        signLightWNW.color.setHex(0xff0804);
        signLightESE.position.y = 42.0;
        signLightWNW.position.y = 42.0;
        signLightESE.intensity = 11.0 * boost;
        signLightWNW.intensity = 11.0 * boost;
      } else {
        const seqRate = 2.4; // steps per second
        const seqTimer = t * seqRate;
        const step = Math.floor(seqTimer) % 8;
        const subPhase = seqTimer - Math.floor(seqTimer);
        const slotPulse = 0.88 + 0.12 * Math.sin(subPhase * Math.PI);

        if (step <= 4) {
          // Progressive build-up: G -> G+O -> G+O+R -> G+O+R+◎ -> G+O+R+◎+9
          signSlotMats.forEach((sm, idx) => {
            const b = idx === step ? slotPulse : (idx < step ? 0.84 : 0.12);
            sm.face.color.setRGB(0.88 * b, 0.025 * b, 0.0);
            sm.core.color.setRGB(1.0 * b, 0.10 * b, 0.03 * b);
            sm.retGlow.color.setRGB(0.22 * b, 0.91 * b, 1.0 * b);
            sm.retCore.color.setRGB(0.72 * b, 0.97 * b, 1.0 * b);
          });
          const activeY = SIGN_SLOT_Y[step];
          const isRingStep = step === 3;
          signLightESE.color.setHex(isRingStep ? 0x38e8ff : 0xff0804);
          signLightWNW.color.setHex(isRingStep ? 0x38e8ff : 0xff0804);
          signLightESE.position.y = activeY;
          signLightWNW.position.y = activeY;
          signLightESE.intensity = 8.5 * slotPulse;
          signLightWNW.intensity = 8.5 * slotPulse;
        } else if (step === 5 || step === 6) {
          // All 5 slots lit together
          const allB = 0.94 + 0.06 * Math.sin(t * 6.0);
          signSlotMats.forEach((sm) => {
            sm.face.color.setRGB(0.88 * allB, 0.025 * allB, 0.0);
            sm.core.color.setRGB(1.0 * allB, 0.10 * allB, 0.03 * allB);
            sm.retGlow.color.setRGB(0.22 * allB, 0.91 * allB, 1.0 * allB);
            sm.retCore.color.setRGB(0.72 * allB, 0.97 * allB, 1.0 * allB);
          });
          signLightESE.color.setHex(0xff0804);
          signLightWNW.color.setHex(0xff0804);
          signLightESE.position.y = 42.0;
          signLightWNW.position.y = 42.0;
          signLightESE.intensity = 9.5 * allB;
          signLightWNW.intensity = 9.5 * allB;
        } else {
          // Step 7: Marzelvane reticle rings (◎) solo pulse before next cycle
          const ringB = 0.94;
          signSlotMats.forEach((sm) => {
            sm.face.color.setRGB(0.18, 0.01, 0.0);
            sm.core.color.setRGB(0.24, 0.02, 0.01);
            sm.retGlow.color.setRGB(0.22 * ringB, 0.91 * ringB, 1.0 * ringB);
            sm.retCore.color.setRGB(0.72 * ringB, 0.97 * ringB, 1.0 * ringB);
          });
          signLightESE.color.setHex(0x38e8ff);
          signLightWNW.color.setHex(0x38e8ff);
          signLightESE.position.y = SIGN_SLOT_Y[3];
          signLightWNW.position.y = SIGN_SLOT_Y[3];
          signLightESE.intensity = 7.5;
          signLightWNW.intensity = 7.5;
        }
      }

      // 6. Van Allen Cyan (#38e8ff) & Amber (#ffaa2b) Satellite Strobe Beacons (1.25 Hz alternating blink)
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
        const isDistantView = distToCam > 60.0;
        const bodyDistFactor = isDistantView
          ? Math.min(3.4, 1.15 + (distToCam - 60.0) * 0.008)
          : 0.72;
        const towerFacingDistFactor = isDistantView
          ? Math.min(7.8, 2.4 + (distToCam - 60.0) * 0.022)
          : 0.60;

        sat.cyanFlares.forEach((fl) => {
          const df = fl.isTowerFacing ? towerFacingDistFactor : bodyDistFactor;
          const s = fl.baseScale * df;
          fl.sprite.scale.set(s, s, 1.0);
          fl.mat.opacity = (fl.isTowerFacing ? (isDistantView ? 0.90 : 0.36) : 0.52) * cyanOn;
        });
        sat.amberFlares.forEach((fl) => {
          const df = fl.isTowerFacing ? towerFacingDistFactor : bodyDistFactor;
          const s = fl.baseScale * df;
          fl.sprite.scale.set(s, s, 1.0);
          fl.mat.opacity = (fl.isTowerFacing ? (isDistantView ? 0.90 : 0.36) : 0.52) * amberOn;
        });
        sat.amberLights[0].intensity = 2.8 * amberOn;
        sat.amberLights[1].intensity = 2.0 * amberOn;
        sat.cyanLights[0].intensity = 2.8 * cyanOn;
        sat.cyanLights[1].intensity = 2.0 * cyanOn;
      });

      // 7. Asteroid Sidereal Spin, Pulsar Armillary Spin & Tumbling Main-Belt Asteroids
      const spinAngle = t * 0.018;
      skyGroup.rotation.y = -spinAngle;
      skyGroup.rotation.x = 0.038 * Math.sin(spinAngle * 0.5);
      const starMapUVShift = ((spinAngle / (Math.PI * 2.0)) % 1.0 + 1.0) % 1.0;
      starMapPanTextures.forEach((stTex) => {
        stTex.offset.x = starMapUVShift;
      });
      if (armillarySpinGroup) {
        armillarySpinGroup.rotation.y = -t * 0.45;
      }
      driftingAsteroids.forEach((a, idx) => {
        a.mesh.rotation.x = idx * 0.7 + t * a.rx * 30.0;
        a.mesh.rotation.y = idx * 1.3 + t * a.ry * 30.0;
      });

      controls.enableDamping = false;
      if (renderer.domElement.width !== width || renderer.domElement.height !== height) {
        renderer.setPixelRatio(1);
        renderer.setSize(width, height, false);
      }
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      controls.update();
      renderer.render(scene, camera);
    }

    
window.__studioSetup = async (width, height, duration, fps) => {
  _lastHudState = -1;
  marzelShockwaves.forEach((sw) => {
    sw.mesh.geometry.dispose();
    sw.mesh.geometry = new THREE.TorusGeometry(1.0, 0.040, 32, 128);
  });
  burstSphereMesh.geometry.dispose();
  burstSphereMesh.geometry = new THREE.SphereGeometry(1.0, 64, 48);
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
};

window.__studioStep = async (frameIdx, tSec, duration, width, height) => {
  const params = new URLSearchParams(window.location.search);
  const mode = params.get("mode") || "drone_tour";
  setTourStateAtTime(mode, tSec, duration, width, height);
};
