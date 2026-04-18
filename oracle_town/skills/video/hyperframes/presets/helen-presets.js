'use strict';
/**
 * HELEN Cinematic Presets — authoritative JS asset
 *
 * All functions accept (tl, el, ...) and add tweens to a GSAP master timeline.
 * Python presets.py emits calls to these functions; composition.py inlines this file.
 *
 * Contract:
 *   - tl  = GSAP master timeline (seekable)
 *   - el  = DOM element or selector string
 *   - dur = shot duration in seconds
 *   - t0  = absolute start time on the master timeline
 */

// ── Camera moves ──────────────────────────────────────────────────────────────

const helenCamera = {
  slowPushIn: (tl, el, dur, t0) =>
    tl.fromTo(el, { scale: 1.0, x: 0 },
      { scale: 1.10, x: 0, duration: dur, ease: 'sine.inOut' }, t0),

  slowPullOut: (tl, el, dur, t0) =>
    tl.fromTo(el, { scale: 1.10, x: 0 },
      { scale: 1.0, x: 0, duration: dur, ease: 'sine.inOut' }, t0),

  driftRight: (tl, el, dur, t0) =>
    tl.fromTo(el, { scale: 1.05, x: 0 },
      { scale: 1.08, x: '-3%', duration: dur, ease: 'none' }, t0),

  driftLeft: (tl, el, dur, t0) =>
    tl.fromTo(el, { scale: 1.05, x: 0 },
      { scale: 1.08, x: '3%', duration: dur, ease: 'none' }, t0),

  handheldMicro: (tl, el, dur, t0) =>
    tl.to(el, {
      keyframes: [
        { x: 2, y: -2, duration: 0.3 },
        { x: -3, y: 1,  duration: 0.4 },
        { x: 1,  y: 2,  duration: 0.3 },
        { x: -1, y: -1, duration: 0.4 },
      ],
      repeat: -1, ease: 'none',
    }, t0),

  staticBreathe: (tl, el, dur, t0) =>
    tl.to(el, { scale: 1.02, duration: 6, yoyo: true, repeat: -1, ease: 'sine.inOut' }, t0),

  zoomThrough: (tl, el, dur, t0) =>
    tl.fromTo(el, { scale: 1.0, opacity: 1 },
      { scale: 1.4, opacity: 0, duration: dur, ease: 'power2.in' }, t0),

  orbit: (tl, el, dur, t0) =>
    tl.to(el, { rotationY: 8, duration: dur, yoyo: true, repeat: 1, ease: 'sine.inOut' }, t0),
};


// ── Text motion ───────────────────────────────────────────────────────────────

const helenText = {
  fade: (tl, el, t0) =>
    tl.from(el, { opacity: 0, duration: 1.2, ease: 'power2.out' }, t0),

  slideUp: (tl, el, t0) =>
    tl.from(el, { y: 28, opacity: 0, duration: 0.8, ease: 'power3.out' }, t0),

  slideLeft: (tl, el, t0) =>
    tl.from(el, { x: 40, opacity: 0, duration: 0.8, ease: 'power3.out' }, t0),

  scaleIn: (tl, el, t0) =>
    tl.from(el, { scale: 0.72, opacity: 0, duration: 0.9, ease: 'back.out(1.4)' }, t0),

  blurReveal: (tl, el, t0) =>
    tl.from(el, { filter: 'blur(10px)', opacity: 0, duration: 1.2, ease: 'power2.out' }, t0),

  wordByWord: (tl, el, t0) => {
    const words = el.querySelectorAll('.word');
    tl.from(words, { opacity: 0, y: 12, duration: 0.4, stagger: 0.18, ease: 'power2.out' }, t0);
  },

  typewriter: (tl, el, t0) => {
    const chars = el.querySelectorAll('.char');
    tl.from(chars, { opacity: 0, duration: 0.01, stagger: 0.055, ease: 'none' }, t0);
  },
};


// ── Transitions ───────────────────────────────────────────────────────────────

const helenTransition = {
  crossfade: (tl, elOut, elIn, dur, t0) => {
    tl.to(elOut,   { opacity: 0, duration: dur, ease: 'power1.inOut' }, t0);
    tl.from(elIn,  { opacity: 0, duration: dur, ease: 'power1.inOut' }, t0);
  },

  blurCross: (tl, elOut, elIn, dur, t0) => {
    tl.to(elOut,  { filter: 'blur(12px)', opacity: 0, duration: dur, ease: 'power2.in'  }, t0);
    tl.from(elIn, { filter: 'blur(12px)', opacity: 0, duration: dur, ease: 'power2.out' }, t0);
  },

  fadeBlack: (tl, elOut, elIn, dur, t0) => {
    const half = dur / 2;
    tl.to(elOut,   { opacity: 0, duration: half, ease: 'power2.in'  }, t0);
    tl.from(elIn,  { opacity: 0, duration: half, ease: 'power2.out' }, t0 + half);
  },

  zoomThrough: (tl, elOut, elIn, dur, t0) => {
    tl.to(elOut,   { scale: 1.4,  opacity: 0, duration: dur, ease: 'power2.in'  }, t0);
    tl.from(elIn,  { scale: 0.85, opacity: 0, duration: dur, ease: 'power2.out' }, t0);
  },

  hardCut: (_tl, _elOut, _elIn, _dur, _t0) => { /* instantaneous — no tween */ },
};


// ── CommonJS export (Node.js testing) ─────────────────────────────────────────
if (typeof module !== 'undefined') {
  module.exports = { helenCamera, helenText, helenTransition };
}
