// Trace system — visible environmental signals goblins can notice.
// Taxonomy: WARNING | RESOURCE | RELATIONAL (RELATIONAL dormant until L4).
// MARK strengthens a trace. MARK NEVER touches need-resolution state —
// that separation is the game's constitutional law, enforced by tests.

export const TRACE_TYPE = Object.freeze({
  WARNING: 'WARNING',
  RESOURCE: 'RESOURCE',
  RELATIONAL: 'RELATIONAL',
});

export const TRACE_PEAK = 100;
const MARK_BOOST = 40;
const GROWTH_PER_TICK = 6;   // marked traces intensify toward peak
const DECAY_PER_TICK = 0.5;  // unmaintained traces fade gently (no punishment)

let nextTraceSeq = 0;

export function makeTrace({ type, targetId, position, affinity = [] }) {
  nextTraceSeq += 1;
  return {
    trace_id: `T${nextTraceSeq}`,
    type,
    targetId,
    position: [...position],
    affinity,
    intensity: 0,
    peaked: false,
    growing: false,
    observers: [],
  };
}

export function resetTraceSeq() { nextTraceSeq = 0; }

export function markTrace(trace) {
  trace.intensity = Math.min(TRACE_PEAK, trace.intensity + MARK_BOOST);
  trace.growing = true;
}

// Returns true the tick the trace reaches peak (edge-triggered, once).
export function tickTrace(trace) {
  if (trace.growing && !trace.peaked) {
    trace.intensity = Math.min(TRACE_PEAK, trace.intensity + GROWTH_PER_TICK);
    if (trace.intensity >= TRACE_PEAK) {
      trace.peaked = true;
      trace.growing = false;
      return true;
    }
  } else if (!trace.peaked && trace.intensity > 0) {
    trace.intensity = Math.max(0, trace.intensity - DECAY_PER_TICK);
  }
  return false;
}
