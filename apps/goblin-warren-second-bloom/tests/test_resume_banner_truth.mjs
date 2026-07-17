// Regression — DEFECT-001: the resume banner must never assert live world
// state, because boot() creates a fresh world and restores nothing.
// UI_STATE_CONSISTENCY_INVARIANT: a surface may only assert state the state
// layer actually holds. Banner claims must be memory-tense (true of the save
// file), never present-tense (claims about the running world).
// Run: node tests/test_resume_banner_truth.mjs
import { resumeBanner } from '../src/game/persistence.js';
import { World } from '../src/core/state.js';
import { L1_DYING_FIRE } from '../src/content/levels/L1_DYING_FIRE.js';
import { FIRE_STATE } from '../src/game/needs.js';

let pass = 0, fail = 0;
const ok = (c, n) => { if (c) { pass++; console.log(`  ✓ ${n}`); } else { fail++; console.error(`  ✗ ${n}`); } };

// what boot() actually produces on every reload — ground truth
const fresh = new World(structuredClone(L1_DYING_FIRE), 7);
ok(fresh.fire.state === FIRE_STATE.EMBER && !fresh.fire.lanternLit,
  'ground truth: reload boots a cold ember, no restoration exists');

// every save shape the game can write
const SHAPES = [
  { name: 'first-kindle', saved: { fireState: 1, marked: false, completed: false } },
  { name: 'twig-fed', saved: { fireState: 2, marked: false, completed: false } },
  { name: 'marked', saved: { fireState: 2, marked: true, completed: false } },
  { name: 'completed', saved: { fireState: 3, marked: true, completed: true } },
  { name: 'untouched', saved: { fireState: 0, marked: false, completed: false } },
];

// present-tense live-state claims that a fresh boot cannot honor
const LIVE_CLAIMS = [/still glows/i, /still burns/i, /still have/i, /is lit/i, /is burning/i];

console.log('A. banner exists for every returning player (ADHD §8 contract)');
for (const s of SHAPES) ok(typeof resumeBanner(s.saved) === 'string' && resumeBanner(s.saved).length > 0,
  `banner present for ${s.name}`);

console.log('B. banner never asserts unrestored live state (DEFECT-001)');
for (const s of SHAPES) {
  const text = resumeBanner(s.saved);
  const lie = LIVE_CLAIMS.find(rx => rx.test(text));
  ok(!lie, `${s.name}: no live-state claim ${lie ? `(violates: "${text}")` : ''}`);
}

console.log('C. neighbors and malformed input');
ok(resumeBanner(null) === null, 'no banner on first visit (null save)');
ok(typeof resumeBanner({}) === 'string', 'malformed empty save fails closed to a truthful default');
ok(/welcome back/i.test(resumeBanner({ fireState: 1 })), 'banner still welcomes (feature preserved, not deleted)');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
