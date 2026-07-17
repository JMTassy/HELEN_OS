// Local persistence — game saves only. Explicitly NOT a HELEN ledger,
// NOT a receipt, NOT canonical replay. localStorage, this app's key only.

const KEY = 'goblin-warren-second-bloom/v0';

export function save(state) {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* private mode: play without saves */ }
}

export function load() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

export function clear() {
  try { localStorage.removeItem(KEY); } catch { /* ignore */ }
}

// Interruption-recovery text (ADHD rule §8: resume context, no tutorial replay).
// UI_STATE_CONSISTENCY_INVARIANT: boot() restores nothing, so these lines may
// only speak in memory-tense — true of the save file, silent about the live
// world. Present-tense claims ("still glows") are lies on a fresh boot and
// are rejected by tests/test_resume_banner_truth.mjs. Real state restoration
// (deterministic action-log replay) is DEBUG_BACKLOG, not copy-editing.
export function resumeBanner(saved) {
  if (!saved) return null;
  if (saved.completed) return 'Welcome back. You lit the lantern here once — the Warren remembers.';
  if (saved.marked) return 'Welcome back. The Warren remembers the mark you left.';
  if (saved.fireState >= 1) return 'Welcome back. You have woken this fire before.';
  return 'Welcome back. The ember is waiting for you.';
}
