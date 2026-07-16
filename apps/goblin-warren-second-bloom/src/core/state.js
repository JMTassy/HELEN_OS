// World state + explicit transition pipeline.
// dispatch(MARK) → strengthenTrace → (ticks) → trace peak → Bram perceives
//   → orients → moves → arrives → carries → delivers → fire fed → resolved.
// dispatch(MARK) NEVER resolves the need directly. That is the hard law.

import { makeRng, Scheduler } from './determinism.js';
import { EventBus, Telemetry, INPUT } from './events.js';
import { validateLevel } from '../content/schema.js';
import { makeTrace, markTrace, tickTrace, resetTraceSeq, TRACE_TYPE } from '../game/traces.js';
import {
  makeFire, kindleFire, feedTwig, feedLog, lightLantern, needResolved, FIRE_STATE,
} from '../game/needs.js';
import { makeGoblin, tickGoblin, GOBLIN_STATE } from '../game/goblins.js';

export class World {
  constructor(levelData, seed = 7) {
    validateLevel(levelData);
    resetTraceSeq();
    this.level = levelData;
    this.rng = makeRng(seed);
    this.seed = seed;
    this.scheduler = new Scheduler();
    this.bus = new EventBus();
    this.telemetry = new Telemetry();
    this.paused = false;
    this.completed = false;

    this.fire = makeFire();
    this.firePosition = levelData.objects.find(o => o.object_id === 'FIRE').position;
    this.objects = new Map(levelData.objects.map(o => [o.object_id, {
      ...o, visible: o.object_id !== 'BIGWOOD', dragFailed: false, glowHint: false, consumed: false,
    }]));
    this.traces = [];
    this.goblins = levelData.goblin_spawns.map(s => makeGoblin(s.goblin_id, s.position, s.state));

    this.bus.on('*', (e) => this.telemetry.record(this.scheduler.tick, e.type, e));
  }

  emit(name, data = {}) { this.bus.emit(name, data); }

  goblin(id) { return this.goblins.find(g => g.goblin_id === id); }

  // ── verbs (abstract input events; bindings live in the UI layer) ──────────

  dispatch(action, payload = {}) {
    if (this.paused || this.completed) return { ok: false, reason: 'inactive' };
    if (!this.level.available_verbs.includes(action)) return { ok: false, reason: 'verb_unavailable' };

    switch (action) {
      case INPUT.KINDLE: return this.#kindle();
      case INPUT.DRAG: return this.#drag(payload.objectId);
      case INPUT.MARK: return this.#mark(payload.objectId);
      default: return { ok: false, reason: 'unknown_action' };
    }
  }

  #kindle() {
    // Direct verb. Never touches Bram's task. Never touches traces.
    const evt = kindleFire(this.fire);
    this.emit('kindle_hold', { progress: this.fire.kindleProgress });
    if (evt) {
      this.emit('fire_woken', {});
      const bram = this.goblin('BRAM');
      if (bram && bram.state === GOBLIN_STATE.SLEEPING) {
        bram.state = GOBLIN_STATE.IDLE;
        this.emit('bram_woke', {});
      }
    }
    return { ok: true };
  }

  #drag(objectId) {
    const obj = this.objects.get(objectId);
    if (!obj || !obj.visible || !obj.draggable || obj.consumed) return { ok: false, reason: 'not_draggable' };

    if (obj.drag_weight > 10) {
      // The limitation beat: heavy wood does not move. Deterministic, always.
      obj.dragFailed = true;
      this.emit('drag_failed', { object: objectId });
      // The glow hint appears ONLY after a failed drag — taught by causality.
      if (!obj.glowHint) {
        obj.glowHint = true;
        this.emit('glow_hint', { object: objectId });
      }
      return { ok: true, moved: false };
    }

    if (objectId === 'TWIG') {
      const evt = feedTwig(this.fire);
      if (!evt) return { ok: false, reason: 'fire_not_ready' };
      obj.consumed = true;
      this.emit('twig_dragged', {});
      this.emit(evt, {});
      // firelight reveals the distant wood pile
      const wood = this.objects.get('BIGWOOD');
      if (wood && !wood.visible) { wood.visible = true; this.emit('wood_revealed', {}); }
      return { ok: true, moved: true };
    }
    return { ok: false, reason: 'nothing_to_do' };
  }

  #mark(objectId) {
    const obj = this.objects.get(objectId);
    if (!obj || !obj.visible || !obj.markable || obj.consumed) return { ok: false, reason: 'not_markable' };

    let trace = this.traces.find(t => t.targetId === objectId && !t.consumed);
    if (!trace) {
      trace = makeTrace({
        type: TRACE_TYPE.RESOURCE,
        targetId: objectId,
        position: obj.position,
        affinity: ['wood', 'fire'],
      });
      this.traces.push(trace);
    }
    markTrace(trace);
    this.emit('mark_tap', { object: objectId, trace: trace.trace_id, intensity: trace.intensity });
    // NOTE: no need-resolution state was touched here. MARK is attention only.
    return { ok: true, trace: trace.trace_id };
  }

  // ── logical tick ──────────────────────────────────────────────────────────

  tick() {
    if (this.paused || this.completed) return; // pause = zero time penalty
    this.scheduler.advance();

    for (const t of this.traces) {
      if (tickTrace(t)) this.emit('trace_peak', { trace: t.trace_id, object: t.targetId });
    }

    for (const g of this.goblins) {
      const before = g.carrying;
      tickGoblin(g, this, (name, data) => this.emit(name, data));
      // delivery side-effect: only Bram's delivered log strengthens the fire
      if (before && !g.carrying && this.telemetry.has('wood_delivered') && this.fire.state === FIRE_STATE.FED) {
        const evt = feedLog(this.fire);
        if (evt) this.emit(evt, {});
        const lit = lightLantern(this.fire);
        if (lit) this.emit(lit, {});
      }
    }

    if (!this.completed && needResolved(this.fire)) {
      this.completed = true;
      this.emit('need_resolved', { need: 'FIRE_DYING' });
      this.emit('level_complete', { level: this.level.level_id });
    }
  }

  pause() { this.paused = true; this.emit('paused', {}); }
  resume() { this.paused = false; this.emit('resumed', {}); }

  snapshot() {
    return {
      tick: this.scheduler.tick,
      fire: { ...this.fire },
      completed: this.completed,
      goblins: this.goblins.map(g => ({ id: g.goblin_id, state: g.state, pos: [...g.position] })),
      traces: this.traces.map(t => ({ id: t.trace_id, intensity: t.intensity, peaked: t.peaked })),
    };
  }
}
