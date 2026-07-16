// Seeded determinism kit. Built-in randomness and wall clocks are banned
// from game logic (enforced by the static-law test).
// Same seed + same action script = same world state + same telemetry, always.

export function makeRng(seed) {
  let s = (seed >>> 0) || 1;
  return function rng() {
    // LCG (numerical recipes); deterministic across platforms
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

// Fixed-step logical clock. Render loops accumulate real ms elsewhere;
// game logic only ever sees whole ticks (TICKS_PER_SECOND below).
export const TICKS_PER_SECOND = 10;

export class Scheduler {
  constructor() {
    this.tick = 0;
    this.queue = []; // { at, fn, tag }
  }
  at(tickDelay, fn, tag = '') {
    this.queue.push({ at: this.tick + Math.max(1, tickDelay | 0), fn, tag });
  }
  advance() {
    this.tick += 1;
    const due = this.queue.filter(q => q.at <= this.tick);
    this.queue = this.queue.filter(q => q.at > this.tick);
    // stable order: schedule order is insertion order (deterministic)
    for (const q of due) q.fn(this.tick);
  }
}
