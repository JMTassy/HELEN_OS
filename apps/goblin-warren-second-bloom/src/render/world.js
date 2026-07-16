// Canvas renderer — the world IS the interface.
// Placeholder art tier (procedural, seeded), flagged in assets/manifest.json.
// Palette from the operator's boards: night violet, lantern amber, forest green.

import { FIRE_STATE } from '../game/needs.js';

const PAL = {
  night: '#171226', ground: '#241b33', groundLit: '#3a2b2a',
  ember: '#ff7b2d', flame: '#ffb347', flameHot: '#ffe08a',
  goblin: '#5d8a4a', goblinDark: '#3f6134', cloth: '#8a6d3b',
  lulu: '#6d5a8f', trace: '#7dffb0', hint: '#ffd97a', wood: '#6b4a2f',
  text: '#f0e6d2',
};

export class WorldRenderer {
  constructor(canvas, world, opts = {}) {
    this.cv = canvas;
    this.cx = canvas.getContext('2d');
    this.world = world;
    this.reduceParticles = !!opts.reduceParticles;
    this.anim = 0; // render-time only; never feeds logic
  }

  px(p) { return [p[0] * this.cv.width, p[1] * this.cv.height]; }

  draw() {
    this.anim += 1;
    const { cx, cv, world } = this;
    const fire = world.fire;
    const [fx, fy] = this.px(world.firePosition);

    // sky + ground
    cx.fillStyle = PAL.night; cx.fillRect(0, 0, cv.width, cv.height);
    cx.fillStyle = PAL.ground; cx.fillRect(0, cv.height * 0.55, cv.width, cv.height * 0.45);

    // firelight radius grows with fire state
    const reach = [0.09, 0.24, 0.32, 0.55][fire.state] * cv.width;
    const glow = cx.createRadialGradient(fx, fy, 8, fx, fy, reach);
    const warmth = fire.state === FIRE_STATE.EMBER ? 0.35 : 0.75;
    glow.addColorStop(0, `rgba(255,160,60,${warmth})`);
    glow.addColorStop(1, 'rgba(255,120,40,0)');
    cx.fillStyle = glow; cx.fillRect(0, 0, cv.width, cv.height);

    this.#drawLantern();
    this.#drawWood();
    this.#drawTwig();
    this.#drawFire(fx, fy);
    this.#drawTraces();
    for (const g of world.goblins) this.#drawGoblin(g);

    // gentle vignette keeps focus center-warm
    const vin = cx.createRadialGradient(cv.width / 2, cv.height / 2, cv.width * 0.3, cv.width / 2, cv.height / 2, cv.width * 0.75);
    vin.addColorStop(0, 'rgba(0,0,0,0)'); vin.addColorStop(1, 'rgba(10,6,20,0.55)');
    cx.fillStyle = vin; cx.fillRect(0, 0, cv.width, cv.height);
  }

  #flick(n, speed = 0.2, amp = 1) {
    return Math.sin(this.anim * speed + n) * amp;
  }

  #drawFire(fx, fy) {
    const { cx, world } = this;
    const s = world.fire.state;
    // wood base
    cx.strokeStyle = PAL.wood; cx.lineWidth = 6; cx.lineCap = 'round';
    cx.beginPath(); cx.moveTo(fx - 22, fy + 10); cx.lineTo(fx + 22, fy + 4); cx.stroke();
    cx.beginPath(); cx.moveTo(fx - 18, fy + 4); cx.lineTo(fx + 18, fy + 12); cx.stroke();

    if (s === FIRE_STATE.EMBER) {
      const pulse = 3 + this.#flick(0, 0.12, 2) + world.fire.kindleProgress / 18;
      cx.fillStyle = PAL.ember;
      cx.beginPath(); cx.arc(fx, fy, Math.max(2.5, pulse), 0, 7); cx.fill();
      return;
    }
    const size = [0, 16, 24, 40][s];
    for (let i = 0; i < 3; i++) {
      const w = size * (1 - i * 0.28), h = size * (1.6 - i * 0.3);
      const sway = this.reduceParticles ? 0 : this.#flick(i * 2, 0.25, 3);
      cx.fillStyle = [PAL.ember, PAL.flame, PAL.flameHot][i];
      cx.beginPath();
      cx.moveTo(fx - w / 2, fy + 6);
      cx.quadraticCurveTo(fx + sway, fy - h, fx + w / 2, fy + 6);
      cx.closePath(); cx.fill();
    }
  }

  #drawTwig() {
    const t = this.world.objects.get('TWIG');
    if (!t || t.consumed) return;
    const [x, y] = this.px(t.dragPos || t.position);
    this.cx.strokeStyle = '#8a6a45'; this.cx.lineWidth = 4; this.cx.lineCap = 'round';
    this.cx.beginPath(); this.cx.moveTo(x - 12, y + 4); this.cx.lineTo(x + 12, y - 4); this.cx.stroke();
    this.cx.beginPath(); this.cx.moveTo(x + 2, y); this.cx.lineTo(x + 9, y - 9); this.cx.stroke();
  }

  #drawWood() {
    const w = this.world.objects.get('BIGWOOD');
    if (!w || !w.visible || w.consumed) return;
    const [x, y] = this.px(w.position);
    const cx = this.cx;
    const shake = w.wiggle ? this.#flick(1, 0.9, 2.5) : 0;
    cx.save(); cx.translate(shake, 0);
    cx.fillStyle = PAL.wood;
    for (let i = 0; i < 3; i++) {
      cx.beginPath();
      cx.roundRect(x - 26 + i * 6, y - 6 - i * 11, 52 - i * 10, 10, 5);
      cx.fill();
    }
    if (w.glowHint) {
      const a = 0.35 + (this.reduceParticles ? 0 : this.#flick(2, 0.15, 0.15));
      cx.strokeStyle = PAL.hint; cx.globalAlpha = Math.max(0.2, a); cx.lineWidth = 2.5;
      cx.beginPath(); cx.arc(x, y - 12, 38, 0, 7); cx.stroke();
      cx.globalAlpha = 1;
    }
    cx.restore();
    if (w.wiggle) w.wiggle -= 1;
  }

  #drawLantern() {
    const l = this.world.objects.get('LANTERN');
    const [x, y] = this.px(l.position);
    const cx = this.cx, lit = this.world.fire.lanternLit;
    cx.strokeStyle = '#4a3b2a'; cx.lineWidth = 3;
    cx.beginPath(); cx.moveTo(x, y - 34); cx.lineTo(x, y + 26); cx.stroke();
    cx.beginPath(); cx.moveTo(x, y - 34); cx.lineTo(x + 14, y - 28); cx.stroke();
    if (lit) {
      const g = cx.createRadialGradient(x + 16, y - 18, 2, x + 16, y - 18, 60);
      g.addColorStop(0, 'rgba(255,215,120,0.9)'); g.addColorStop(1, 'rgba(255,215,120,0)');
      cx.fillStyle = g; cx.beginPath(); cx.arc(x + 16, y - 18, 60, 0, 7); cx.fill();
    }
    cx.fillStyle = lit ? PAL.flameHot : '#2c2438';
    cx.fillRect(x + 11, y - 24, 10, 13);
  }

  #drawTraces() {
    const cx = this.cx;
    for (const t of this.world.traces) {
      if (t.consumed || t.intensity <= 0) continue;
      const [x, y] = this.px(t.position);
      const r = 14 + (t.intensity / 100) * 26;
      const a = 0.15 + (t.intensity / 100) * 0.55;
      cx.strokeStyle = PAL.trace; cx.globalAlpha = a; cx.lineWidth = t.peaked ? 4 : 2.5;
      cx.beginPath(); cx.arc(x, y - 12, r + (this.reduceParticles ? 0 : this.#flick(3, 0.3, 3)), 0, 7); cx.stroke();
      cx.globalAlpha = 1;
    }
  }

  #drawGoblin(g) {
    const cx = this.cx;
    const [x, y] = this.px(g.position);
    const body = g.goblin_id === 'LULU' ? PAL.lulu : PAL.goblin;
    const bob = (g.state === 'MOVING' || g.state === 'CARRYING') && !this.reduceParticles
      ? Math.abs(this.#flick(4, 0.6, 3)) : 0;
    cx.save(); cx.translate(x, y - bob); cx.scale(g.facing, 1);

    if (g.state === 'SLEEPING') {
      cx.fillStyle = PAL.goblinDark;
      cx.beginPath(); cx.ellipse(0, 4, 16, 9, 0, 0, 7); cx.fill();
      cx.fillStyle = PAL.text; cx.font = '11px monospace';
      cx.scale(g.facing, 1); cx.fillText('z z', 10, -14);
      cx.restore(); return;
    }
    // body + head + ears (silhouette-first, per boards)
    cx.fillStyle = body;
    cx.beginPath(); cx.ellipse(0, 0, 9, 13, 0, 0, 7); cx.fill();
    cx.beginPath(); cx.arc(0, -17, 8, 0, 7); cx.fill();
    cx.beginPath(); cx.moveTo(-7, -20); cx.lineTo(-16, -26); cx.lineTo(-6, -25); cx.closePath(); cx.fill();
    cx.beginPath(); cx.moveTo(7, -20); cx.lineTo(16, -26); cx.lineTo(6, -25); cx.closePath(); cx.fill();
    // eye
    cx.fillStyle = '#101010'; cx.beginPath(); cx.arc(4, -18, 1.6, 0, 7); cx.fill();
    // state tells
    if (g.state === 'PAUSED') {
      cx.fillStyle = PAL.text; cx.font = 'bold 14px monospace';
      cx.scale(g.facing, 1); cx.fillText('!', -2, -32); cx.scale(g.facing, 1);
    }
    if (g.state === 'CARRYING' || (g.state === 'ACTING' && g.stateTicks > 4)) {
      cx.fillStyle = PAL.wood; cx.fillRect(-14, -8, 28, 7);
    }
    if (g.state === 'CELEBRATING') {
      cx.strokeStyle = body; cx.lineWidth = 3;
      cx.beginPath(); cx.moveTo(-8, -6); cx.lineTo(-15, -16); cx.stroke();
      cx.beginPath(); cx.moveTo(8, -6); cx.lineTo(15, -16); cx.stroke();
    }
    cx.restore();
  }
}
