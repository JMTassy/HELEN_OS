// Event bus + local telemetry.
// Telemetry is game telemetry ONLY — not a HELEN receipt, not a ledger,
// never written outside this app's own storage.

export class EventBus {
  constructor() { this.handlers = new Map(); }
  on(type, fn) {
    if (!this.handlers.has(type)) this.handlers.set(type, []);
    this.handlers.get(type).push(fn);
  }
  emit(type, payload = {}) {
    for (const fn of this.handlers.get(type) || []) fn(payload);
    for (const fn of this.handlers.get('*') || []) fn({ type, ...payload });
  }
}

export class Telemetry {
  constructor() { this.events = []; }
  record(tick, name, data = {}) {
    this.events.push({ tick, name, ...data });
  }
  names() { return this.events.map(e => e.name); }
  has(name) { return this.events.some(e => e.name === name); }
  tickOf(name) {
    const e = this.events.find(ev => ev.name === name);
    return e ? e.tick : -1;
  }
}

// Abstract input events — the Embodied Delegation Ladder's rungs.
// V0 bindings: KINDLE=press-and-hold, DRAG=pointer drag, MARK=tap-hold.
// Future tactile pack rebinds these (blow/shake/tilt) with zero logic changes.
export const INPUT = Object.freeze({
  KINDLE: 'KINDLE', // sustained direct gesture — feeds the fire
  DRAG: 'DRAG',     // direct manipulation — move an object
  MARK: 'MARK',     // delegated attention — strengthen a trace
});
