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
export function resumeBanner(saved) {
  if (!saved) return null;
  if (saved.completed) return 'Welcome back. The lantern still burns. Bram remembers.';
  if (saved.marked) return 'Welcome back. Bram noticed your mark on the wood.';
  if (saved.fireState >= 1) return 'Welcome back. The fire still glows where you woke it.';
  return 'Welcome back. The ember is waiting for you.';
}
