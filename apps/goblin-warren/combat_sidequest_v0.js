/**
 * combat_sidequest_v0.js — Pop-in combat vertical slice for Goblin Warren
 *
 * authority=false · claim=NO_CLAIM · sovereign=false · ledger_effect=none
 *
 * LAW:
 *   model/engine of combat  ⊬  global Warren state
 *   result object only; host decides whether to keep a cosmetic trace
 *   Garden ADMIT ⊬ Kernel ADMISSION
 *
 * Public contract:
 *   openCombatSideQuest(context) → void
 *   updateCombatSideQuest(dt)    → void   (optional; module has own rAF while open)
 *   renderCombatSideQuest()      → void
 *   closeCombatSideQuest(result) → void   (also called internally)
 *   isCombatSideQuestOpen()      → boolean
 *   setCombatReducedEffects(on)  → void
 *
 * Input context (bounded):
 *   { sourceZoneId?, sourceTraceId?, encounterSeed?, difficultyPreset? }
 * Output result:
 *   { status: "completed"|"failed"|"abandoned", crittersSaved: number,
 *     rewardTraceId: string|null, elapsedMs: number }
 */
(function (root) {
  "use strict";

  var SCHEMA = "COMBAT_SIDEQUEST_V0";
  var DEFAULT_DURATION_MS = 90 * 1000;
  var ARENA_W = 720;
  var ARENA_H = 420;

  var state = null; // null when closed
  var hostResultHandler = null;
  var reducedEffects = false;
  var lastResult = null;
  var keys = Object.create(null);
  var listenersBound = false;

  /* ---------- seeded rng (replay-friendly within an encounter) ---------- */
  function makeRng(seed) {
    var s = (seed >>> 0) || 20260716;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 0x100000000;
    };
  }

  function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function dist(a, b) {
    var dx = a.x - b.x, dy = a.y - b.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /* ---------- pure simulation helpers (testable) ---------- */
  function buildEncounter(ctx) {
    ctx = ctx || {};
    var seed = (ctx.encounterSeed != null ? ctx.encounterSeed : 0xC0A7) >>> 0;
    var rnd = makeRng(seed);
    var difficulty = ctx.difficultyPreset || "normal";
    var enemyHp = difficulty === "easy" ? 3 : difficulty === "hard" ? 6 : 4;
    var playerHp = difficulty === "hard" ? 4 : 5;
    var critterCount = difficulty === "easy" ? 4 : 3;

    var critters = [];
    for (var i = 0; i < critterCount; i++) {
      critters.push({
        id: "critter_" + i,
        x: 180 + i * 90 + rnd() * 20,
        y: 260 + rnd() * 40,
        r: 10,
        fear: 0,
        alive: true,
        saved: false,
        wobble: rnd() * Math.PI * 2,
      });
    }

    return {
      schema: SCHEMA,
      open: true,
      phase: "portal", // portal | fight | resolve | closed
      context: {
        sourceZoneId: ctx.sourceZoneId || "warren_town",
        sourceTraceId: ctx.sourceTraceId || null,
        encounterSeed: seed,
        difficultyPreset: difficulty,
      },
      t0: 0,
      elapsedMs: 0,
      durationMs: DEFAULT_DURATION_MS,
      reducedEffects: reducedEffects,
      player: {
        x: ARENA_W * 0.22,
        y: ARENA_H * 0.55,
        r: 14,
        hp: playerHp,
        maxHp: playerHp,
        vx: 0,
        vy: 0,
        facing: 1,
        attackCd: 0,
        invuln: 0,
        dodgeCd: 0,
        dodgeLeft: 0,
        hitFlash: 0,
      },
      enemy: {
        x: ARENA_W * 0.72,
        y: ARENA_H * 0.48,
        r: 22,
        hp: enemyHp,
        maxHp: enemyHp,
        vx: 0,
        vy: 0,
        attackCd: 1.2,
        hitStop: 0,
        recoil: 0,
        alive: true,
        phase: "idle",
      },
      critters: critters,
      particles: [],
      shake: 0,
      hitStop: 0,
      msg: "A corrupted trace tears open. Protect the little ones.",
      status: null, // filled on close
      rewardTraceId: null,
      rng: rnd,
      // DOM
      overlay: null,
      canvas: null,
      ctx2d: null,
      raf: 0,
      lastTs: 0,
      accepted: false,
    };
  }

  function countAliveCritters(st) {
    var n = 0;
    for (var i = 0; i < st.critters.length; i++) {
      if (st.critters[i].alive) n++;
    }
    return n;
  }

  function spawnParticles(st, x, y, color, n, speed) {
    if (st.reducedEffects) n = Math.max(1, Math.floor(n / 3));
    for (var i = 0; i < n; i++) {
      var a = st.rng() * Math.PI * 2;
      var sp = (speed || 80) * (0.4 + st.rng());
      st.particles.push({
        x: x,
        y: y,
        vx: Math.cos(a) * sp,
        vy: Math.sin(a) * sp,
        life: 0.25 + st.rng() * 0.35,
        color: color,
        r: 2 + st.rng() * 2,
      });
    }
  }

  function tryPlayerAttack(st) {
    var p = st.player;
    if (p.attackCd > 0 || st.phase !== "fight") return false;
    p.attackCd = 0.32;
    var range = 38;
    var hitX = p.x + p.facing * 22;
    var hitY = p.y;
    var e = st.enemy;
    if (e.alive && dist({ x: hitX, y: hitY }, e) < range + e.r) {
      e.hp -= 1;
      e.recoil = 0.12;
      e.vx = p.facing * 160;
      e.vy = (st.rng() - 0.5) * 40;
      st.hitStop = st.reducedEffects ? 0.02 : 0.06;
      if (!st.reducedEffects) st.shake = 3.5;
      spawnParticles(st, e.x, e.y, "#e6b84a", 10, 140);
      st.msg = "Hit! The disturbance recoils.";
      if (e.hp <= 0) {
        e.alive = false;
        e.hp = 0;
        spawnParticles(st, e.x, e.y, "#b08ae0", 24, 180);
        st.msg = "Disturbance composted into light.";
        finishFight(st, "completed");
      }
      return true;
    }
    st.msg = "Swing — miss. Watch the critters.";
    return false;
  }

  function tryPlayerDodge(st) {
    var p = st.player;
    if (p.dodgeCd > 0 || st.phase !== "fight") return false;
    p.dodgeCd = 0.85;
    p.dodgeLeft = 0.18;
    p.invuln = Math.max(p.invuln, 0.22);
    p.vx = p.facing * 280;
    st.msg = "Dodge — brief invulnerability.";
    return true;
  }

  function damagePlayer(st, fromX) {
    var p = st.player;
    if (p.invuln > 0 || st.phase !== "fight") return;
    p.hp -= 1;
    p.hitFlash = 0.2;
    p.invuln = st.reducedEffects ? 0.35 : 0.55;
    p.vx = (p.x < fromX ? -1 : 1) * 140;
    if (!st.reducedEffects) st.shake = 5;
    spawnParticles(st, p.x, p.y, "#e07a6a", 8, 100);
    st.msg = "Ouch — invulnerability window.";
    if (p.hp <= 0) {
      p.hp = 0;
      finishFight(st, "failed");
    }
  }

  function finishFight(st, status) {
    if (st.phase === "resolve" || st.phase === "closed") return;
    st.phase = "resolve";
    st.status = status;
    var saved = countAliveCritters(st);
    for (var i = 0; i < st.critters.length; i++) {
      var c = st.critters[i];
      if (c.alive) {
        c.saved = status === "completed";
        c.fear = status === "completed" ? 0 : c.fear;
      }
    }
    if (status === "completed") {
      st.rewardTraceId = "combat_trace_critter_rescue_v0";
      st.msg =
        "Saved " +
        saved +
        " critter" +
        (saved === 1 ? "" : "s") +
        ". Bounded reward ready for host.";
    } else if (status === "failed") {
      st.rewardTraceId = null;
      st.msg = "You fell. The critters scatter. Restart or exit.";
    } else {
      st.rewardTraceId = null;
      st.msg = "Abandoned. No reward.";
    }
  }

  function simStep(st, dt) {
    if (!st || !st.open) return;
    if (st.phase === "portal" || st.phase === "resolve" || st.phase === "closed") {
      // still tick particles lightly
      tickParticles(st, dt);
      return;
    }

    st.elapsedMs += dt * 1000;
    if (st.elapsedMs >= st.durationMs && st.enemy.alive) {
      // timeout: fail if enemy still up
      finishFight(st, "failed");
      st.msg = "Time up — disturbance not stabilized.";
      return;
    }

    if (st.hitStop > 0) {
      st.hitStop -= dt;
      return; // freeze during hit-stop
    }

    var p = st.player;
    var e = st.enemy;
    var spd = p.dodgeLeft > 0 ? 0 : 165;

    // movement input
    var mx = 0, my = 0;
    if (keys.KeyA || keys.ArrowLeft) mx -= 1;
    if (keys.KeyD || keys.ArrowRight) mx += 1;
    if (keys.KeyW || keys.ArrowUp) my -= 1;
    if (keys.KeyS || keys.ArrowDown) my += 1;
    if (mx || my) {
      var len = Math.sqrt(mx * mx + my * my);
      mx /= len;
      my /= len;
      if (mx) p.facing = mx > 0 ? 1 : -1;
    }
    p.vx = p.vx * 0.75 + mx * spd * 0.25;
    p.vy = p.vy * 0.75 + my * spd * 0.25;
    if (p.dodgeLeft > 0) p.dodgeLeft -= dt;
    p.x = clamp(p.x + p.vx * dt, 24, ARENA_W - 24);
    p.y = clamp(p.y + p.vy * dt, 48, ARENA_H - 24);
    p.attackCd = Math.max(0, p.attackCd - dt);
    p.dodgeCd = Math.max(0, p.dodgeCd - dt);
    p.invuln = Math.max(0, p.invuln - dt);
    p.hitFlash = Math.max(0, p.hitFlash - dt);

    // enemy AI: chase nearest critter, or player if close
    if (e.alive) {
      e.attackCd = Math.max(0, e.attackCd - dt);
      e.recoil = Math.max(0, e.recoil - dt);
      var target = p;
      var best = dist(e, p);
      for (var i = 0; i < st.critters.length; i++) {
        var c = st.critters[i];
        if (!c.alive) continue;
        var d = dist(e, c);
        if (d < best * 0.85) {
          best = d;
          target = c;
        }
      }
      if (e.recoil <= 0) {
        var ang = Math.atan2(target.y - e.y, target.x - e.x);
        var esp = 70;
        e.vx = Math.cos(ang) * esp;
        e.vy = Math.sin(ang) * esp;
      } else {
        e.vx *= 0.9;
        e.vy *= 0.9;
      }
      e.x = clamp(e.x + e.vx * dt, 30, ARENA_W - 30);
      e.y = clamp(e.y + e.vy * dt, 50, ARENA_H - 30);

      // contact damage to player
      if (dist(e, p) < e.r + p.r - 2) {
        damagePlayer(st, e.x);
      }
      // harm critters slowly on contact
      for (var j = 0; j < st.critters.length; j++) {
        var cr = st.critters[j];
        if (!cr.alive) continue;
        if (dist(e, cr) < e.r + cr.r) {
          cr.fear = Math.min(1, cr.fear + dt * 0.8);
          if (cr.fear >= 1) {
            cr.alive = false;
            spawnParticles(st, cr.x, cr.y, "#8fc060", 12, 60);
            st.msg = "A critter fled into the compost fog…";
            if (countAliveCritters(st) === 0) {
              finishFight(st, "failed");
              st.msg = "All critters lost. Restart or exit.";
            }
          }
        } else {
          cr.fear = Math.max(0, cr.fear - dt * 0.15);
        }
        // critters scuttle away from enemy
        var away = Math.atan2(cr.y - e.y, cr.x - e.x);
        cr.x = clamp(cr.x + Math.cos(away) * 35 * dt, 20, ARENA_W - 20);
        cr.y = clamp(cr.y + Math.sin(away) * 35 * dt, 50, ARENA_H - 20);
        cr.wobble += dt * 6;
      }
    }

    if (st.shake > 0) st.shake = Math.max(0, st.shake - dt * 18);
    tickParticles(st, dt);
  }

  function tickParticles(st, dt) {
    var next = [];
    for (var i = 0; i < st.particles.length; i++) {
      var pt = st.particles[i];
      pt.life -= dt;
      if (pt.life <= 0) continue;
      pt.x += pt.vx * dt;
      pt.y += pt.vy * dt;
      pt.vx *= 0.96;
      pt.vy *= 0.96;
      next.push(pt);
    }
    st.particles = next;
  }

  /* ---------- rendering ---------- */
  function draw(st) {
    if (!st || !st.ctx2d) return;
    var ctx = st.ctx2d;
    var shx = 0, shy = 0;
    if (st.shake > 0 && !st.reducedEffects) {
      shx = (st.rng() - 0.5) * st.shake * 2;
      shy = (st.rng() - 0.5) * st.shake * 2;
    }
    ctx.save();
    ctx.clearRect(0, 0, ARENA_W, ARENA_H);
    ctx.translate(shx, shy);

    // arena floor
    ctx.fillStyle = "#12101a";
    ctx.fillRect(0, 0, ARENA_W, ARENA_H);
    ctx.fillStyle = "#1a1526";
    for (var gx = 0; gx < ARENA_W; gx += 24) {
      for (var gy = 0; gy < ARENA_H; gy += 24) {
        if (((gx / 24 + gy / 24) | 0) % 2 === 0) ctx.fillRect(gx, gy, 24, 24);
      }
    }
    // rift
    ctx.fillStyle = "rgba(120,60,180,0.25)";
    ctx.beginPath();
    ctx.ellipse(ARENA_W * 0.72, ARENA_H * 0.48, 70, 40, 0, 0, Math.PI * 2);
    ctx.fill();
    if (!st.reducedEffects) {
      ctx.strokeStyle = "rgba(176,138,224,0.5)";
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // critters
    for (var i = 0; i < st.critters.length; i++) {
      drawCritter(ctx, st.critters[i], st);
    }

    // enemy
    if (st.enemy.alive || st.phase === "resolve") {
      drawEnemy(ctx, st.enemy, st);
    }

    // player
    drawPlayer(ctx, st.player, st);

    // particles
    for (var j = 0; j < st.particles.length; j++) {
      var pt = st.particles[j];
      ctx.globalAlpha = clamp(pt.life * 2, 0, 1);
      ctx.fillStyle = pt.color;
      ctx.fillRect(pt.x - pt.r / 2, pt.y - pt.r / 2, pt.r, pt.r);
      ctx.globalAlpha = 1;
    }

    // HUD
    drawHud(ctx, st);
    ctx.restore();
  }

  function drawPlayer(ctx, p, st) {
    ctx.save();
    ctx.translate(p.x, p.y);
    if (p.hitFlash > 0) ctx.globalAlpha = 0.45 + 0.55 * Math.sin(p.hitFlash * 40);
    if (p.invuln > 0 && Math.floor(p.invuln * 20) % 2 === 0) ctx.globalAlpha *= 0.55;
    // body
    ctx.fillStyle = "#6ecf7a";
    ctx.beginPath();
    ctx.ellipse(0, 0, p.r, p.r * 1.1, 0, 0, Math.PI * 2);
    ctx.fill();
    // goggles (shape cue, not color-only)
    ctx.fillStyle = "#2a2030";
    ctx.fillRect(-6, -6, 5, 4);
    ctx.fillRect(2, -6, 5, 4);
    ctx.strokeStyle = "#e6b84a";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(-6.5, -6.5, 6, 5);
    ctx.strokeRect(1.5, -6.5, 6, 5);
    // attack arc
    if (p.attackCd > 0.22) {
      ctx.strokeStyle = "#e6b84a";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(p.facing * 10, 0, 28, -0.8, 0.8);
      ctx.stroke();
    }
    // label
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#e8dcc0";
    ctx.font = "10px monospace";
    ctx.textAlign = "center";
    ctx.fillText("YOU", 0, -p.r - 8);
    ctx.restore();
  }

  function drawEnemy(ctx, e, st) {
    if (!e.alive && st.phase === "resolve") {
      // dissolve residue
      ctx.fillStyle = "rgba(176,138,224,0.35)";
      ctx.beginPath();
      ctx.arc(e.x, e.y, e.r * 0.6, 0, Math.PI * 2);
      ctx.fill();
      return;
    }
    ctx.save();
    ctx.translate(e.x, e.y);
    var pulse = 1 + Math.sin(st.elapsedMs / 120) * 0.06;
    ctx.scale(pulse, pulse);
    // spiky blob — distinct silhouette from critters
    ctx.fillStyle = "#5a2a8a";
    ctx.beginPath();
    for (var i = 0; i < 8; i++) {
      var a = (i / 8) * Math.PI * 2;
      var rr = e.r * (i % 2 === 0 ? 1.15 : 0.75);
      var px = Math.cos(a) * rr;
      var py = Math.sin(a) * rr;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = "#e07a6a";
    ctx.lineWidth = 2;
    ctx.stroke();
    // eye slits
    ctx.fillStyle = "#e07a6a";
    ctx.fillRect(-8, -4, 5, 2);
    ctx.fillRect(3, -4, 5, 2);
    ctx.restore();
    // hp bar
    drawBar(ctx, e.x - 24, e.y - e.r - 14, 48, 5, e.hp / e.maxHp, "#e07a6a", "#3a2030");
    ctx.fillStyle = "#e8dcc0";
    ctx.font = "9px monospace";
    ctx.textAlign = "center";
    ctx.fillText("DISTURBANCE", e.x, e.y - e.r - 18);
  }

  function drawCritter(ctx, c, st) {
    if (!c.alive) return;
    ctx.save();
    ctx.translate(c.x, c.y + Math.sin(c.wobble) * 2);
    // mushroom body — round, friendly, not spiky
    ctx.fillStyle = c.fear > 0.4 ? "#c8e090" : "#8fc060";
    ctx.beginPath();
    ctx.arc(0, 2, c.r * 0.7, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#d86a9a";
    ctx.beginPath();
    ctx.ellipse(0, -2, c.r, c.r * 0.7, 0, Math.PI, 0);
    ctx.fill();
    // spots (shape+pattern)
    ctx.fillStyle = "#fff6";
    ctx.fillRect(-4, -5, 3, 3);
    ctx.fillRect(2, -3, 2, 2);
    // fear ring
    if (c.fear > 0.05) {
      ctx.strokeStyle = "rgba(224,122,106," + c.fear + ")";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, c.r + 4, 0, Math.PI * 2 * c.fear);
      ctx.stroke();
    }
    if (c.saved) {
      ctx.fillStyle = "#e6b84a";
      ctx.font = "12px monospace";
      ctx.textAlign = "center";
      ctx.fillText("♥", 0, -c.r - 6);
    }
    ctx.restore();
  }

  function drawBar(ctx, x, y, w, h, ratio, fg, bg) {
    ctx.fillStyle = bg;
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = fg;
    ctx.fillRect(x, y, w * clamp(ratio, 0, 1), h);
    ctx.strokeStyle = "#e8dcc0";
    ctx.lineWidth = 1;
    ctx.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1);
  }

  function drawHud(ctx, st) {
    // top bar
    ctx.fillStyle = "rgba(10,8,16,0.82)";
    ctx.fillRect(0, 0, ARENA_W, 36);
    ctx.fillStyle = "#e6b84a";
    ctx.font = "bold 12px monospace";
    ctx.textAlign = "left";
    ctx.fillText("CORRUPTED TRACE — PROTECT THE CRITTERS", 12, 22);

    var remain = Math.max(0, (st.durationMs - st.elapsedMs) / 1000);
    ctx.textAlign = "right";
    ctx.fillStyle = "#e8dcc0";
    ctx.fillText(remain.toFixed(0) + "s", ARENA_W - 12, 22);

    // player hp as pips (not color-only: shape)
    var p = st.player;
    for (var i = 0; i < p.maxHp; i++) {
      var x = 12 + i * 16;
      var y = ARENA_H - 22;
      ctx.fillStyle = i < p.hp ? "#e07a6a" : "#3a2030";
      ctx.beginPath();
      ctx.moveTo(x + 6, y);
      ctx.lineTo(x + 12, y + 6);
      ctx.lineTo(x + 6, y + 12);
      ctx.lineTo(x, y + 6);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = "#e8dcc0";
      ctx.stroke();
    }
    ctx.fillStyle = "#9a8f78";
    ctx.font = "10px monospace";
    ctx.textAlign = "left";
    ctx.fillText("HP (diamonds)", 12 + p.maxHp * 16 + 8, ARENA_H - 12);

    // message
    ctx.fillStyle = "rgba(10,8,16,0.75)";
    ctx.fillRect(ARENA_W / 2 - 200, ARENA_H - 36, 400, 24);
    ctx.fillStyle = "#e8dcc0";
    ctx.textAlign = "center";
    ctx.font = "11px monospace";
    ctx.fillText(st.msg, ARENA_W / 2, ARENA_H - 20);

    // phase overlays
    if (st.phase === "portal") {
      ctx.fillStyle = "rgba(8,6,14,0.72)";
      ctx.fillRect(0, 0, ARENA_W, ARENA_H);
      ctx.fillStyle = "#e6b84a";
      ctx.font = "bold 20px monospace";
      ctx.textAlign = "center";
      ctx.fillText("SIDE QUEST: CORRUPTED TRACE", ARENA_W / 2, ARENA_H / 2 - 40);
      ctx.fillStyle = "#e8dcc0";
      ctx.font = "13px monospace";
      ctx.fillText("Protect tiny critters from the disturbance.", ARENA_W / 2, ARENA_H / 2 - 12);
      ctx.fillText("WASD move · SPACE attack · SHIFT dodge · Esc abandon", ARENA_W / 2, ARENA_H / 2 + 12);
      ctx.fillStyle = "#8fc060";
      ctx.fillText("[Enter / click] ACCEPT     [Esc] IGNORE", ARENA_W / 2, ARENA_H / 2 + 48);
    }
    if (st.phase === "resolve") {
      ctx.fillStyle = "rgba(8,6,14,0.55)";
      ctx.fillRect(0, 0, ARENA_W, ARENA_H);
      ctx.fillStyle = st.status === "completed" ? "#8fc060" : "#e07a6a";
      ctx.font = "bold 22px monospace";
      ctx.textAlign = "center";
      var title =
        st.status === "completed"
          ? "STABILIZED"
          : st.status === "failed"
          ? "FAILED"
          : "ABANDONED";
      ctx.fillText(title, ARENA_W / 2, ARENA_H / 2 - 30);
      ctx.fillStyle = "#e8dcc0";
      ctx.font = "13px monospace";
      ctx.fillText(
        "Critters saved: " + countAliveCritters(st) + " · reward: " + (st.rewardTraceId || "none"),
        ARENA_W / 2,
        ARENA_H / 2
      );
      ctx.fillText("[R] restart   [Enter/Esc] return to Warren", ARENA_W / 2, ARENA_H / 2 + 28);
    }
  }

  /* ---------- DOM lifecycle ---------- */
  function ensureOverlay(st) {
    if (st.overlay) return;
    var ov = document.createElement("div");
    ov.id = "combat-sidequest-overlay";
    ov.setAttribute("role", "dialog");
    ov.setAttribute("aria-label", "Combat side quest");
    ov.style.cssText =
      "position:fixed;inset:0;z-index:9999;display:flex;flex-direction:column;" +
      "align-items:center;justify-content:center;background:rgba(6,4,12,0.88);" +
      "font-family:ui-monospace,monospace;color:#e8dcc0;";
    ov.innerHTML =
      '<div style="width:min(760px,96vw);display:flex;flex-direction:column;gap:8px">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">' +
      '<div style="color:#e6b84a;font-weight:bold;letter-spacing:.04em">⚔ COMBAT SIDE QUEST V0 · NON_SOVEREIGN</div>' +
      '<div style="display:flex;gap:6px;flex-wrap:wrap">' +
      '<button type="button" data-act="accept" style="background:#2c4d24;color:#e6f0c8;border:1px solid #1c3317;border-radius:6px;padding:6px 10px;cursor:pointer">Accept</button>' +
      '<button type="button" data-act="restart" style="background:#2a2030;color:#e8dcc0;border:1px solid #4a3a52;border-radius:6px;padding:6px 10px;cursor:pointer">Restart</button>' +
      '<button type="button" data-act="fx" style="background:#2a2030;color:#e8dcc0;border:1px solid #4a3a52;border-radius:6px;padding:6px 10px;cursor:pointer">FX: full</button>' +
      '<button type="button" data-act="exit" style="background:#3a2030;color:#e8dcc0;border:1px solid #6a3a42;border-radius:6px;padding:6px 10px;cursor:pointer">Exit</button>' +
      "</div></div>" +
      '<canvas width="' +
      ARENA_W +
      '" height="' +
      ARENA_H +
      '" style="width:100%;max-width:720px;border:2px solid #4a3a52;border-radius:10px;background:#0c0a12;image-rendering:pixelated;touch-action:none"></canvas>' +
      '<div style="font-size:11px;color:#9a8f78">authority=false · result is a bounded object · host decides cosmetic trace · no global mutation</div>' +
      "</div>";
    document.body.appendChild(ov);
    st.overlay = ov;
    st.canvas = ov.querySelector("canvas");
    st.ctx2d = st.canvas.getContext("2d");

    ov.addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-act]");
      if (!btn || !state) return;
      var act = btn.getAttribute("data-act");
      if (act === "accept") acceptPortal();
      else if (act === "restart") restartEncounter();
      else if (act === "exit") abandonOrClose();
      else if (act === "fx") {
        setCombatReducedEffects(!reducedEffects);
        btn.textContent = reducedEffects ? "FX: reduced" : "FX: full";
      }
    });

    // click canvas = accept when portal
    st.canvas.addEventListener("click", function () {
      if (state && state.phase === "portal") acceptPortal();
      else if (state && state.phase === "resolve") closeWithCurrent();
    });
  }

  function bindListeners() {
    if (listenersBound) return;
    listenersBound = true;
    window.addEventListener("keydown", onKeyDown, true);
    window.addEventListener("keyup", onKeyUp, true);
  }

  function unbindListeners() {
    if (!listenersBound) return;
    listenersBound = false;
    window.removeEventListener("keydown", onKeyDown, true);
    window.removeEventListener("keyup", onKeyUp, true);
    keys = Object.create(null);
  }

  function onKeyDown(e) {
    if (!state || !state.open) return;
    keys[e.code] = true;
    if (e.code === "Enter") {
      e.preventDefault();
      if (state.phase === "portal") acceptPortal();
      else if (state.phase === "resolve") closeWithCurrent();
    } else if (e.code === "Escape") {
      e.preventDefault();
      abandonOrClose();
    } else if (e.code === "Space") {
      e.preventDefault();
      if (state.phase === "fight") tryPlayerAttack(state);
    } else if (e.code === "ShiftLeft" || e.code === "ShiftRight") {
      e.preventDefault();
      if (state.phase === "fight") tryPlayerDodge(state);
    } else if (e.code === "KeyR" && state.phase === "resolve") {
      e.preventDefault();
      restartEncounter();
    }
  }

  function onKeyUp(e) {
    keys[e.code] = false;
  }

  function acceptPortal() {
    if (!state || state.phase !== "portal") return;
    state.phase = "fight";
    state.accepted = true;
    state.t0 = performance.now();
    state.elapsedMs = 0;
    state.msg = "Fight! Protect critters · Space attack · Shift dodge";
  }

  function restartEncounter() {
    if (!state) return;
    var ctx = state.context;
    var handler = hostResultHandler;
    hardTeardown(false);
    openCombatSideQuest(ctx, handler);
    if (state) {
      state.phase = "fight";
      state.accepted = true;
      state.msg = "Restarted. Protect the critters.";
    }
  }

  function abandonOrClose() {
    if (!state) return;
    if (state.phase === "portal") {
      state.status = "abandoned";
      state.rewardTraceId = null;
      closeWithCurrent();
    } else if (state.phase === "fight") {
      finishFight(state, "abandoned");
      closeWithCurrent();
    } else {
      closeWithCurrent();
    }
  }

  function closeWithCurrent() {
    if (!state) return;
    var result = {
      status: state.status || "abandoned",
      crittersSaved: countAliveCritters(state),
      rewardTraceId: state.rewardTraceId,
      elapsedMs: Math.round(state.elapsedMs),
      schema: SCHEMA,
      context: state.context,
    };
    lastResult = result;
    hardTeardown(true);
    if (typeof hostResultHandler === "function") {
      try {
        hostResultHandler(result);
      } catch (err) {
        console.warn("[combat_sidequest_v0] host handler error", err);
      }
    }
  }

  function hardTeardown(notifyClosed) {
    if (!state) return;
    if (state.raf) {
      cancelAnimationFrame(state.raf);
      state.raf = 0;
    }
    if (state.overlay && state.overlay.parentNode) {
      state.overlay.parentNode.removeChild(state.overlay);
    }
    unbindListeners();
    state.open = false;
    state.phase = "closed";
    state.overlay = null;
    state.canvas = null;
    state.ctx2d = null;
    state.particles = [];
    state = null;
    if (notifyClosed) {
      /* host already notified via closeWithCurrent */
    }
  }

  function loop(ts) {
    if (!state || !state.open) return;
    if (!state.lastTs) state.lastTs = ts;
    var dt = Math.min(0.033, (ts - state.lastTs) / 1000);
    state.lastTs = ts;
    simStep(state, dt);
    draw(state);
    state.raf = requestAnimationFrame(loop);
  }

  /* ---------- public API ---------- */
  function openCombatSideQuest(context, onResult) {
    if (state && state.open) {
      console.warn("[combat_sidequest_v0] already open");
      return;
    }
    hostResultHandler = typeof onResult === "function" ? onResult : hostResultHandler;
    state = buildEncounter(context || {});
    state.reducedEffects = reducedEffects;
    ensureOverlay(state);
    bindListeners();
    state.lastTs = 0;
    state.raf = requestAnimationFrame(loop);
    draw(state);
  }

  function updateCombatSideQuest(dt) {
    if (!state || !state.open) return;
    simStep(state, dt || 1 / 60);
  }

  function renderCombatSideQuest() {
    if (!state || !state.open) return;
    draw(state);
  }

  function closeCombatSideQuest(result) {
    if (!state) return;
    if (result && result.status) {
      state.status = result.status;
      state.rewardTraceId = result.rewardTraceId || null;
    } else if (!state.status) {
      state.status = "abandoned";
    }
    closeWithCurrent();
  }

  function isCombatSideQuestOpen() {
    return !!(state && state.open);
  }

  function setCombatReducedEffects(on) {
    reducedEffects = !!on;
    if (state) state.reducedEffects = reducedEffects;
  }

  function getLastCombatResult() {
    return lastResult;
  }

  // expose pure helpers for node selftest
  var __test = {
    buildEncounter: buildEncounter,
    simStep: simStep,
    tryPlayerAttack: tryPlayerAttack,
    tryPlayerDodge: tryPlayerDodge,
    damagePlayer: damagePlayer,
    finishFight: finishFight,
    countAliveCritters: countAliveCritters,
    DEFAULT_DURATION_MS: DEFAULT_DURATION_MS,
    SCHEMA: SCHEMA,
  };

  var api = {
    SCHEMA: SCHEMA,
    openCombatSideQuest: openCombatSideQuest,
    updateCombatSideQuest: updateCombatSideQuest,
    renderCombatSideQuest: renderCombatSideQuest,
    closeCombatSideQuest: closeCombatSideQuest,
    isCombatSideQuestOpen: isCombatSideQuestOpen,
    setCombatReducedEffects: setCombatReducedEffects,
    getLastCombatResult: getLastCombatResult,
    __test: __test,
  };

  root.CombatSideQuestV0 = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
