// Need system — Level 1 has one need (the dying fire) expressed through
// the fire's visible state. The fire is the emotional barometer: its state
// IS the interface. Text explains only what motion cannot.

export const FIRE_STATE = Object.freeze({
  EMBER: 0,        // cold night; a single pulsing ember
  SMALL_FLAME: 1,  // KINDLE woke it; light spreads; Bram wakes
  FED: 2,          // twig delivered by hand; big wood becomes visible
  STRONG: 3,       // Bram's log delivered; warmth fills the clearing
});

export function makeFire() {
  return {
    state: FIRE_STATE.EMBER,
    kindleProgress: 0,   // 0..100 sustained-gesture progress
    lanternLit: false,
  };
}

export const KINDLE_PER_TICK = 9; // ~1.2s of held gesture to wake the fire

// Direct verb: sustained KINDLE gesture. Returns event name when state changes.
export function kindleFire(fire) {
  if (fire.state !== FIRE_STATE.EMBER) return null;
  fire.kindleProgress = Math.min(100, fire.kindleProgress + KINDLE_PER_TICK);
  if (fire.kindleProgress >= 100) {
    fire.state = FIRE_STATE.SMALL_FLAME;
    return 'fire_woken';
  }
  return null;
}

// Direct verb: player drags the twig into the fire.
export function feedTwig(fire) {
  if (fire.state !== FIRE_STATE.SMALL_FLAME) return null;
  fire.state = FIRE_STATE.FED;
  return 'fire_fed_twig';
}

// Delegated resolution: ONLY Bram's delivered log does this.
export function feedLog(fire) {
  if (fire.state !== FIRE_STATE.FED) return null;
  fire.state = FIRE_STATE.STRONG;
  return 'fire_fed';
}

export function lightLantern(fire) {
  if (fire.state === FIRE_STATE.STRONG && !fire.lanternLit) {
    fire.lanternLit = true;
    return 'lantern_lit';
  }
  return null;
}

export function needResolved(fire) {
  return fire.state === FIRE_STATE.STRONG && fire.lanternLit;
}
