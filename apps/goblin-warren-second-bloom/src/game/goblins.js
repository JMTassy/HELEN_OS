// Goblin agent system — deterministic FSM, no LLM in the campaign loop.
// Personality = weights over trace types (4-axis framework, compost verdict §1).
// Bram: high diligence, Warning-affine, acts on STRONG resource traces only —
// which is exactly what a MARK-to-peak trace is. The causal bridge:
//   trace peak → pause → orient (head turn) → move → arrive → carry → deliver.
// Every stage is a separate ticked state so the player SEES the bridge.

export const GOBLIN_STATE = Object.freeze({
  SLEEPING: 'SLEEPING',
  BACKGROUND: 'BACKGROUND',
  IDLE: 'IDLE',
  PAUSED: 'PAUSED',
  ORIENTING: 'ORIENTING',
  MOVING: 'MOVING',
  ACTING: 'ACTING',
  CARRYING: 'CARRYING',
  CELEBRATING: 'CELEBRATING',
});

export const PROFILES = Object.freeze({
  BRAM: {
    name: 'Bram', role: 'repairer',
    curiosity: 0.2, diligence: 0.95, temperament: 'calm', sociality: 0.3,
    affinity: { WARNING: 1.0, RESOURCE: 0.5, RELATIONAL: 0.1 },
    actThreshold: 100, // acts only on peaked (strong) traces
    // Staged for legibility (animation = information): pause 0.8s, head-turn
    // then body-turn across 1.0s, deliberate walk. Each causal beat separated
    // in time so the player can read the chain.
    moveTicksPerUnit: 26, orientTicks: 10, pauseTicks: 8, actTicks: 10,
  },
  LULU: {
    name: 'Lulu', role: 'explorer',
    curiosity: 0.95, diligence: 0.5, temperament: 'playful', sociality: 0.6,
    affinity: { WARNING: 0.4, RESOURCE: 0.5, RELATIONAL: 1.0 },
    actThreshold: 30, // follows weak/novel traces (active from L2)
    moveTicksPerUnit: 18, orientTicks: 3, pauseTicks: 2, actTicks: 8,
  },
});

export function makeGoblin(goblin_id, position, state) {
  return {
    goblin_id,
    profile: PROFILES[goblin_id],
    position: [...position],
    state,
    stateTicks: 0,
    targetTrace: null,
    carrying: null,
    facing: 1,
    task: null, // KINDLE/DRAG must NEVER write this — invariant-tested
  };
}

function dist(a, b) {
  const dx = a[0] - b[0], dy = a[1] - b[1];
  return Math.sqrt(dx * dx + dy * dy);
}

function stepToward(g, target, ticksPerUnit) {
  const d = dist(g.position, target);
  const step = 1 / ticksPerUnit;
  if (d <= step) { g.position = [...target]; return true; }
  g.position = [
    g.position[0] + ((target[0] - g.position[0]) / d) * step,
    g.position[1] + ((target[1] - g.position[1]) / d) * step,
  ];
  g.facing = target[0] >= g.position[0] ? 1 : -1;
  return false;
}

// One logical tick of Bram's Level-1 behavior.
// `world` provides: traces, fire, objects, telemetry hooks via emit(name).
export function tickGoblin(g, world, emit) {
  const p = g.profile;
  g.stateTicks += 1;

  switch (g.state) {
    case 'SLEEPING':
      // wakes when the fire wakes (world flips this externally)
      break;

    case 'BACKGROUND':
      break; // Lulu in L1: present, warm, non-interactive

    case 'IDLE': {
      // perception: notice a peaked trace this goblin cares about
      const seen = world.traces.find(t =>
        t.peaked && !t.consumed &&
        (p.affinity[t.type] || 0) * t.intensity >= p.actThreshold * 0.5
      );
      if (seen) {
        g.targetTrace = seen;
        seen.observers.push(g.goblin_id);
        g.state = 'PAUSED'; g.stateTicks = 0;
        emit('bram_paused', { trace: seen.trace_id });
      }
      break;
    }

    case 'PAUSED':
      if (g.stateTicks >= p.pauseTicks) {
        g.state = 'ORIENTING'; g.stateTicks = 0;
        // head turns first (renderer stages it), body follows mid-orient
        g.prevFacing = g.facing;
        g.facing = g.targetTrace.position[0] >= g.position[0] ? 1 : -1;
        emit('bram_oriented', { trace: g.targetTrace.trace_id });
      }
      break;

    case 'ORIENTING':
      if (g.stateTicks >= p.orientTicks) {
        g.state = 'MOVING'; g.stateTicks = 0;
        emit('bram_moving', {});
      }
      break;

    case 'MOVING':
      if (stepToward(g, g.targetTrace.position, p.moveTicksPerUnit)) {
        g.state = 'ACTING'; g.stateTicks = 0;
        emit('bram_arrived', { at: g.targetTrace.targetId });
      }
      break;

    case 'ACTING':
      if (g.stateTicks >= p.actTicks) {
        g.carrying = g.targetTrace.targetId;
        g.targetTrace.consumed = true;
        g.state = 'CARRYING'; g.stateTicks = 0;
        emit('wood_lifted', { object: g.carrying });
      }
      break;

    case 'CARRYING': {
      const firePos = world.firePosition;
      if (stepToward(g, firePos, p.moveTicksPerUnit)) {
        emit('wood_delivered', { object: g.carrying });
        g.carrying = null;
        g.targetTrace = null;
        g.state = 'CELEBRATING'; g.stateTicks = 0;
      }
      break;
    }

    case 'CELEBRATING':
      if (g.stateTicks >= 12) { g.state = 'IDLE'; g.stateTicks = 0; }
      break;
  }
}
