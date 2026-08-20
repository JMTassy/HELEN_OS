// Regression — DEFECT-002: orphaned drag preview after a REFUSED drop.
//
// UI_STATE_CONSISTENCY_INVARIANT: the input layer must never leave view-state
// asserting an outcome the world did not grant. A drag preview may survive a
// pointerup only if the world actually consumed the object; on refusal the
// object returns to its resting place.
//
// The defect: index.html cleared the preview only when the player released
// OFF target. When the player released ON the fire and the world refused the
// twig (cold ember → feedTwig() returns null), the preview survived and the
// twig rendered floating inside the fire that had just rejected it.
//
// Run: node tests/test_drag_settlement.mjs
import { settleDrag } from '../src/ui/drag.js';
import { World } from '../src/core/state.js';
import { L1_DYING_FIRE } from '../src/content/levels/L1_DYING_FIRE.js';
import { INPUT } from '../src/core/events.js';
import { FIRE_STATE } from '../src/game/needs.js';

let pass = 0, fail = 0;
const ok = (c, n) => { if (c) { pass++; console.log(`  ✓ ${n}`); } else { fail++; console.error(`  ✗ ${n}`); } };
const fresh = () => new World(structuredClone(L1_DYING_FIRE), 7);
const kindled = () => { const w = fresh(); while (w.fire.state === FIRE_STATE.EMBER) w.dispatch(INPUT.KINDLE); return w; };

console.log('A. the world genuinely refuses a twig on a cold fire');
{
  const w = fresh();
  const r = w.dispatch(INPUT.DRAG, { objectId: 'TWIG' });
  ok(r.ok === false && r.reason === 'fire_not_ready', 'cold fire rejects the twig');
  ok(w.objects.get('TWIG').consumed === false, 'refused twig is not consumed');
}

console.log('B. the legacy handler left a ghost (documents the original defect)');
{
  const w = fresh();
  const twig = w.objects.get('TWIG');
  twig.dragPos = [...w.firePosition];
  // legacy inline handler exactly as it stood at 0c2b64f:
  //   if (onFire) world.dispatch(DRAG, {objectId}); else obj.dragPos = null;
  w.dispatch(INPUT.DRAG, { objectId: 'TWIG' });   // refused; no clearing followed
  ok(twig.dragPos !== null && twig.consumed === false,
    'legacy path orphans the preview — a twig rendered inside a fire that refused it');
}

console.log('C. settleDrag clears the preview on refusal (the repair)');
{
  const w = fresh();
  const twig = w.objects.get('TWIG');
  twig.dragPos = [...w.firePosition];
  const r = settleDrag(w, 'TWIG', true);
  ok(twig.dragPos === null, 'preview cleared — the twig returns to its resting place');
  ok(twig.consumed === false, 'refused twig still not consumed');
  ok(r.ok === false && r.reason === 'fire_not_ready', 'refusal reason passed through to the caller');
  ok(w.fire.state === FIRE_STATE.EMBER, 'the world state is untouched by the refusal');
}

console.log('D. positive case — an accepted drop still works');
{
  const w = kindled();
  const twig = w.objects.get('TWIG');
  twig.dragPos = [...w.firePosition];
  const r = settleDrag(w, 'TWIG', true);
  ok(r.ok === true, 'warm fire accepts the twig');
  ok(twig.consumed === true, 'accepted twig is consumed (renderer skips consumed objects)');
  ok(w.fire.state === FIRE_STATE.FED, 'fire advanced to FED');
  ok(w.objects.get('BIGWOOD').visible === true, 'firelight revealed the wood pile');
}

console.log('E. neighbor — released off target');
{
  const w = kindled();
  const twig = w.objects.get('TWIG');
  twig.dragPos = [0.9, 0.9];
  const r = settleDrag(w, 'TWIG', false);
  ok(twig.dragPos === null, 'preview cleared on off-target release');
  ok(twig.consumed === false && w.fire.state === FIRE_STATE.SMALL_FLAME, 'no world change on off-target release');
  ok(r.ok === false && r.reason === 'released_off_target', 'off-target reason reported');
}

console.log('F. firewall — settling a drag grants no delegated agency');
{
  const w = fresh();
  w.objects.get('TWIG').dragPos = [...w.firePosition];
  settleDrag(w, 'TWIG', true);
  const bram = w.goblin('BRAM');
  ok(bram.task === null && bram.targetTrace === null, 'no task or trace assigned to Bram');
  ok(w.traces.length === 0, 'no trace created by a direct verb');
  ok(w.completed === false, 'no need resolved');
}

console.log('G. malformed input fails closed');
{
  const w = fresh();
  const r = settleDrag(w, 'NO_SUCH_OBJECT', true);
  ok(r.ok === false && r.reason === 'unknown_object', 'unknown object rejected without throwing');
}

console.log('H. replay — identical sequences produce identical state');
{
  const run = () => {
    const w = fresh();
    w.objects.get('TWIG').dragPos = [...w.firePosition];
    settleDrag(w, 'TWIG', true);
    while (w.fire.state === FIRE_STATE.EMBER) w.dispatch(INPUT.KINDLE);
    settleDrag(w, 'TWIG', true);
    for (let i = 0; i < 30; i++) w.tick();
    return JSON.stringify(w.snapshot());
  };
  ok(run() === run(), 'same inputs, same world');
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
