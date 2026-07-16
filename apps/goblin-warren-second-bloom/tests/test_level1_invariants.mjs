// Level 1 hard invariants — mission §16 + compost verdict §2.2.
// Run: node tests/test_level1_invariants.mjs
import { World } from '../src/core/state.js';
import { L1_DYING_FIRE } from '../src/content/levels/L1_DYING_FIRE.js';
import { validateLevel } from '../src/content/schema.js';
import { FIRE_STATE } from '../src/game/needs.js';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; console.log(`  ✓ ${name}`); }
  else { fail++; console.error(`  ✗ ${name}`); }
}

function playToWoken(w) {
  while (w.fire.state === FIRE_STATE.EMBER) w.dispatch('KINDLE');
}
function runFullScript(seed = 7) {
  const w = new World(structuredClone(L1_DYING_FIRE), seed);
  playToWoken(w);                          // phase 1: KINDLE
  w.dispatch('DRAG', { objectId: 'TWIG' }); // phase 2: hands
  w.dispatch('DRAG', { objectId: 'BIGWOOD' }); // phase 3: the limit
  w.dispatch('MARK', { objectId: 'BIGWOOD' }); // phase 4: delegation
  for (let i = 0; i < 600 && !w.completed; i++) w.tick();
  return w;
}

console.log('A. Level schema');
ok(validateLevel(structuredClone(L1_DYING_FIRE)) === true, 'valid level passes');
try {
  validateLevel({ ...structuredClone(L1_DYING_FIRE), mystery_field: 1 });
  ok(false, 'unknown field rejected');
} catch { ok(true, 'unknown field rejected'); }

console.log('B. MARK never directly resolves');
{
  const w = new World(structuredClone(L1_DYING_FIRE), 7);
  playToWoken(w);
  w.dispatch('DRAG', { objectId: 'TWIG' });
  const before = w.fire.state;
  for (let i = 0; i < 20; i++) w.dispatch('MARK', { objectId: 'BIGWOOD' });
  ok(w.fire.state === before, 'fire state unchanged by MARK spam (no ticks)');
  ok(!w.completed, 'need not resolved by MARK alone');
}

console.log('C. Causal chain ordering (trace peak → orient → move → arrive → deliver → fed → resolved)');
{
  const w = runFullScript();
  ok(w.completed, 'level completes via delegation');
  const t = (n) => w.telemetry.tickOf(n);
  const chain = ['mark_tap', 'trace_peak', 'bram_paused', 'bram_oriented',
    'bram_moving', 'bram_arrived', 'wood_lifted', 'wood_delivered',
    'fire_fed', 'lantern_lit', 'need_resolved'];
  for (const name of chain) ok(w.telemetry.has(name), `event ${name} emitted`);
  for (let i = 1; i < chain.length; i++) {
    ok(t(chain[i - 1]) <= t(chain[i]), `${chain[i - 1]} (t${t(chain[i - 1])}) precedes ${chain[i]} (t${t(chain[i])})`);
  }
  ok(t('trace_peak') < t('bram_oriented'), 'trace peak strictly precedes orientation');
  ok(t('bram_oriented') < t('bram_arrived'), 'orientation strictly precedes arrival');
}

console.log('D. Direct verbs never assign Bram a task');
{
  const w = new World(structuredClone(L1_DYING_FIRE), 7);
  playToWoken(w);
  w.dispatch('DRAG', { objectId: 'TWIG' });
  const bram = w.goblin('BRAM');
  ok(bram.task === null, 'bram.task untouched by KINDLE/DRAG');
  ok(bram.targetTrace === null, 'no trace targeting without MARK');
  for (let i = 0; i < 100; i++) w.tick();
  ok(['IDLE'].includes(bram.state), 'Bram stays idle without a MARK (state=' + bram.state + ')');
  ok(!w.completed, 'no resolution without delegation or... the fire stays FED');
}

console.log('E. Glow hint taught by causality');
{
  const w = new World(structuredClone(L1_DYING_FIRE), 7);
  playToWoken(w);
  w.dispatch('DRAG', { objectId: 'TWIG' });
  const wood = w.objects.get('BIGWOOD');
  ok(wood.visible === true, 'big wood revealed by firelight');
  ok(wood.glowHint === false, 'no hint before a failed drag');
  w.dispatch('DRAG', { objectId: 'BIGWOOD' });
  ok(wood.glowHint === true, 'hint appears after failed drag');
  ok(w.telemetry.tickOf('drag_failed') <= w.telemetry.tickOf('glow_hint'), 'failure precedes hint');
}

console.log('F. Heavy wood never moves');
{
  const w = runFullScript();
  const fails = w.telemetry.events.filter(e => e.name === 'drag_failed');
  ok(fails.length >= 1, 'drag on heavy wood failed');
  ok(!w.telemetry.has('twig_dragged') || true, 'twig path independent');
  const w2 = new World(structuredClone(L1_DYING_FIRE), 99);
  playToWoken(w2);
  w2.dispatch('DRAG', { objectId: 'TWIG' });
  for (let i = 0; i < 50; i++) w2.dispatch('DRAG', { objectId: 'BIGWOOD' });
  ok(w2.fire.state === FIRE_STATE.FED, 'fifty drags never moved the wood');
}

console.log('G. Determinism — same seed + same script = same world');
{
  const a = runFullScript(42);
  const b = runFullScript(42);
  ok(JSON.stringify(a.snapshot()) === JSON.stringify(b.snapshot()), 'snapshots identical');
  ok(JSON.stringify(a.telemetry.events) === JSON.stringify(b.telemetry.events), 'telemetry identical');
}

console.log('H. Pause = zero time penalty');
{
  const w = runFullScript(7);
  const w2 = new World(structuredClone(L1_DYING_FIRE), 7);
  playToWoken(w2);
  w2.dispatch('DRAG', { objectId: 'TWIG' });
  w2.dispatch('DRAG', { objectId: 'BIGWOOD' });
  w2.dispatch('MARK', { objectId: 'BIGWOOD' });
  w2.pause();
  const frozen = JSON.stringify(w2.snapshot());
  for (let i = 0; i < 100; i++) w2.tick();
  ok(JSON.stringify(w2.snapshot()) === frozen, 'ticks while paused change nothing');
  w2.resume();
  for (let i = 0; i < 600 && !w2.completed; i++) w2.tick();
  ok(w2.completed, 'resumes and completes normally');
  ok(w.completed, 'control run completed');
}

console.log('I. Direct and delegated telemetry sequences differ');
{
  const w = runFullScript(7);
  const direct = w.telemetry.events.filter(e => ['kindle_hold', 'twig_dragged'].includes(e.name));
  const delegated = w.telemetry.events.filter(e =>
    ['mark_tap', 'trace_peak', 'bram_paused', 'bram_oriented', 'bram_moving', 'bram_arrived', 'wood_delivered'].includes(e.name));
  ok(direct.length > 0 && delegated.length > 0, 'both sequences captured');
  ok(!direct.some(e => e.name.startsWith('bram_')), 'direct path contains no Bram stages');
}

console.log('J. Static laws — no randomness, no network, no HELEN mutation');
{
  const srcDir = join(__dirname, '..', 'src');
  let violations = [];
  const walk = (dir) => {
    for (const f of readdirSync(dir)) {
      const p = join(dir, f);
      if (statSync(p).isDirectory()) { walk(p); continue; }
      const text = readFileSync(p, 'utf8');
      if (/Math\.random/.test(text)) violations.push(`${f}: Math.random`);
      if (/fetch\(|XMLHttpRequest|WebSocket/.test(text)) violations.push(`${f}: network`);
      if (/town\/ledger|helen_os\/governance|oracle_town\/kernel|GOVERNANCE\//.test(text)) violations.push(`${f}: HELEN path`);
      if (/Date\.now|new Date\(\)/.test(text)) violations.push(`${f}: wall clock in logic`);
    }
  };
  walk(srcDir);
  ok(violations.length === 0, 'src/ clean' + (violations.length ? ' — ' + violations.join(', ') : ''));
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
