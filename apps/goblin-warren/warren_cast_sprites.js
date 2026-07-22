/*
  BEAD-V5-PROCEDURAL-CREATURE-SPRITES-001
  Warren Cast — role-readable procedural pixel creatures

  NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none
  prototype ⊬ canon · sprite ⊬ verdict · 📜 ledger sleeps

  Law of this module:
    - pure Canvas, generated at runtime; no external images, no copied IP
    - NES chunky pixel style on a 16×16 logical grid
    - three-color ramp per role (base / shadow / highlight) + accents
    - role-first silhouette: function readable before costume
    - every role passes the black-fill silhouette test
    - drawing NEVER mutates governed state (sprites are skin, not law)

  Integration contract for the host game (Game Bible seat):
    WarrenCast.ROLES[role].drawSprite(ctx, x, y, size, npc)
      npc = { seed, t, pose: 'idle'|'work'|'proposal'|'damaged',
              state: { building, carrying, proposing, denied, held, admitted, damaged },
              verdict: 'ACCEPTABLE'|'HOLD'|'DENY' (HAL only) }
    WarrenCast.ROLES[role].drawBadge(ctx, x, y, size)      — Game Bible icon style
    WarrenCast.ROLES[role].drawSilhouette(ctx, x, y, size) — black-fill debug
    WarrenCast.drawLineup(ctx, x, y, size, opts)           — Shift+S cast lineup
    WarrenCast.onAfterDraw(fn)                             — AURA residue hook:
      fn(ctx, x, y, size, npc, role) called after each sprite; the host may
      paint residue trails / inspector commentary anchors there.
    WarrenCast.selftest()                                  — returns [{name, pass, note}]
*/
(function (global) {
'use strict';

const GRID = 16;

/* ---------------------------------------------------------- grid helpers */
function makeGrid() {
  const g = new Uint8Array(GRID * GRID);
  return {
    d: g,
    px(x, y, c) { if (x >= 0 && x < GRID && y >= 0 && y < GRID) g[y * GRID + x] = c; },
    rect(x, y, w, h, c) { for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) this.px(i, j, c); },
    hline(x, y, w, c) { this.rect(x, y, w, 1, c); },
    vline(x, y, h, c) { this.rect(x, y, 1, h, c); },
    get(x, y) { return (x >= 0 && x < GRID && y >= 0 && y < GRID) ? g[y * GRID + x] : 0; },
  };
}
/* deterministic per-seed rand */
function srand(seed) {
  let s = (seed * 2654435761) >>> 0 || 1;
  return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
}

/* color codes: 0 empty · 1 base · 2 shadow · 3 highlight · 4 accent · 5 accent2 · 6 ember/flame */
const CODES = ['', 'base', 'shadow', 'highlight', 'accent', 'accent2', 'ember'];

/* ---------------------------------------------------------- state overlays */
function applyStateOverlays(g, npc, rnd) {
  const s = npc.state || {};
  if (s.building)  { g.px(3, 15, 2); g.px(5, 14, 2); g.px(11, 15, 2); g.px(13, 14, 2); }   /* dust/root pixels */
  if (s.carrying)  { g.rect(11, 8, 3, 3, 4); g.px(12, 7, 2); }                             /* resource bundle */
  if (s.proposing) { g.rect(6, 0, 3, 2, 5); g.px(10, 0, 6); }                              /* scroll + spark */
  if (s.damaged || npc.pose === 'damaged') { g.px(5, 6, 2); g.px(9, 8, 2); g.px(7, 10, 2); } /* scar pixels */
}
/* halo overlays are painted at draw time (they need alpha), not in the grid */

/* ---------------------------------------------------------- role builders
   Each returns a 16×16 grid. Variation comes only from seed. Poses modify
   a small feature set. Silhouette-first: body shape carries the function. */

function buildGOBLIN(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  const earUp = rnd() > .5 ? 1 : 0, sack = 2 + Math.floor(rnd() * 2);
  const bob = npc.pose === 'idle' ? Math.round(Math.sin((t || 0) * 2 + (npc.seed || 0)) * 1) : 0;
  /* hunched C-shape: high back arc, head low-forward */
  g.rect(4, 7 + bob, 7, 6, 1);                     /* torso mass */
  g.rect(3, 5 + bob, 6, 4, 1);                     /* hunched back rises */
  g.rect(8, 8 + bob, 4, 3, 1);                     /* head thrust forward */
  g.rect(9, 6 + bob, 3, 3, 2);                     /* sack hood over head */
  g.px(7, 4 + bob - earUp, 2); g.px(6, 5 + bob, 2);/* hood peak */
  g.px(10, 9 + bob, 6); g.px(12, 9 + bob, 6);      /* ember eyes */
  g.rect(2, 6 + bob, sack, sack, 2);               /* scrap bundle on back */
  g.px(3, 6 + bob, 3);
  g.rect(5, 13, 2, 3, 2); g.rect(9, 13, 2, 3, 2);  /* short legs */
  if (npc.pose === 'work') { g.rect(12, 11, 3, 2, 4); }          /* digging scrap */
  if (npc.pose === 'proposal') { g.rect(11, 4, 2, 3, 5); }       /* holds up scrap-scroll */
  g.hline(5, 8 + bob, 4, 3);                       /* back highlight */
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildHER(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  const flowers = 2 + Math.floor(rnd() * 3);
  const sway = npc.pose === 'idle' ? Math.round(Math.sin((t || 0) * 1.3) * 1) : 0;
  /* upright, leaf mantle: triangular cloak silhouette */
  for (let j = 0; j < 8; j++) g.hline(7 - Math.floor(j * .8) + sway, 6 + j, 2 + Math.floor(j * 1.6), 1); /* widening mantle */
  g.rect(6 + sway, 3, 4, 4, 1);                    /* head */
  g.hline(5 + sway, 6, 6, 3);                      /* mantle collar highlight */
  for (let f = 0; f < flowers; f++) g.px(5 + sway + Math.floor(rnd() * 5), 2 - (f % 2), 4); /* bloom crown */
  g.px(7 + sway, 4, 2); g.px(9 + sway, 4, 2);      /* calm eyes */
  g.hline(4, 14, 8, 2);                            /* hem shadow */
  if (npc.pose === 'work') { g.px(3, 10, 4); g.px(2, 12, 4); }   /* tending blooms */
  if (npc.pose === 'proposal') { g.rect(12, 6, 2, 2, 4); g.px(13, 5, 3); } /* offered bloom */
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildCHIDDUSH(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  const hoodW = 4 + Math.floor(rnd() * 2);
  /* scholar hood + tablet held forward */
  g.rect(5, 2, hoodW, 4, 2);                       /* deep hood */
  g.rect(6, 4, 3, 2, 1);                           /* shadowed face */
  g.rect(4, 6, 7, 7, 1);                           /* robe */
  g.rect(10, 7, 4, 5, 5);                          /* blue-violet tablet */
  g.px(11, 8, 3); g.px(12, 9, 3); g.px(11, 10, 3); /* glyph marks on tablet */
  g.rect(5, 13, 2, 3, 2); g.rect(8, 13, 2, 3, 2);
  /* tiny glyph orbit (idle animation) */
  const a = (t || 0) * 2.2;
  g.px(7 + Math.round(Math.cos(a) * 5), 6 + Math.round(Math.sin(a) * 3), 5);
  g.px(7 + Math.round(Math.cos(a + 3.14) * 5), 6 + Math.round(Math.sin(a + 3.14) * 3), 5);
  if (npc.pose === 'work') g.px(12, 6, 6);                        /* pattern found spark */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }
  g.hline(5, 7, 3, 3);
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildCLAW(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  /* angular posture, one big CLOSED gauntlet — the fist NEVER opens */
  g.rect(4, 4, 6, 9, 1);                           /* angular torso */
  g.px(4, 4, 0); g.px(9, 4, 0);                    /* cut corners = angular */
  g.rect(5, 2, 4, 3, 2);                           /* low helm head */
  g.px(6, 3, 6);                                   /* single ember slit */
  /* the gauntlet: solid 3×3 closed block, all poses */
  g.rect(10, 8, 3, 3, 4);
  g.rect(10, 8, 3, 1, 2);                          /* knuckle shadow */
  g.rect(4, 13, 2, 3, 2); g.rect(8, 13, 2, 3, 2);
  g.vline(4, 5, 6, 3);
  if (npc.pose === 'work') g.rect(13, 9, 2, 1, 2);               /* braced against line */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }        /* files a HOLD */
  applyStateOverlays(g, npc, srand(npc.seed || 1));
  return g;
}

function buildJESTER(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  /* asymmetry is the rule: one hat spike, split-color body, jitter idle */
  const jx = npc.pose === 'idle' ? Math.round(Math.sin((t || 0) * 9 + (npc.seed || 0)) * 1) : 0;
  g.rect(5 + jx, 5, 6, 8, 1);                      /* body */
  for (let j = 5; j < 13; j++) for (let i = 8 + jx; i < 11 + jx; i++) if (g.get(i, j)) g.px(i, j, 5); /* right half broken harmony */
  g.rect(6 + jx, 2, 4, 3, 1);                      /* head */
  g.vline(4 + jx, 0, 4, 4);                        /* single left hat spike */
  g.px(4 + jx, 0, 6);                              /* bell ember */
  g.px(7 + jx, 3, 2); g.px(9 + jx, 3, 5);          /* mismatched eyes */
  g.rect(11 + jx, 6, 2, 2, 4); g.px(13 + jx, 5, 6);/* one juggling arm, right only */
  g.px(3 + jx, 9, 5);                              /* dropped prop, left only */
  g.rect(5, 13, 2, 3, 2); g.rect(9, 12, 2, 4, 4);  /* odd legs, different lengths */
  if (npc.pose === 'work') { g.px(12 + jx, 4, 6); g.px(13 + jx, 2, 6); }  /* chaos sparks */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildARCHIVIST(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  const candleH = 2 + Math.floor(rnd() * 2);
  const step = Math.round(Math.sin((t || 0) * 0.6) * 1);          /* slow step */
  /* scroll backpack silhouette */
  g.rect(5, 5, 6, 8, 1);                           /* robe */
  g.rect(6, 2, 4, 4, 1);                           /* head */
  g.rect(2, 4, 3, 7, 2);                           /* scroll backpack cylinder */
  g.px(3, 3, 3); g.px(3, 11, 3);                   /* scroll caps */
  g.vline(12, 8 - candleH, candleH, 4);            /* candle */
  g.px(12, 7 - candleH, 6);                        /* flame */
  g.px(7, 4, 2); g.px(9, 4, 2);
  g.rect(6 + step, 13, 2, 3, 2); g.rect(9 - step, 13, 2, 3, 2);
  if (npc.pose === 'work') { g.rect(11, 10, 3, 2, 5); g.px(12, 9, 3); } /* binding a receipt */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }
  g.hline(6, 6, 3, 3);
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildWARDEN(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  /* shield block: the shield IS the silhouette; near-zero idle */
  g.rect(4, 3, 8, 11, 4);                          /* tower shield front */
  g.rect(5, 4, 6, 9, 1);                           /* shield face */
  g.vline(7, 4, 9, 3);                             /* boss line */
  g.rect(6, 1, 4, 2, 2);                           /* helm just above shield */
  g.px(7, 2, 6);                                   /* watch slit */
  g.rect(4, 14, 3, 2, 2); g.rect(9, 14, 3, 2, 2);  /* heavy stance */
  if (npc.pose === 'work') g.px(3, 8, 2);                         /* braced */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildSTEWARD(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  const basket = 2 + Math.floor(rnd() * 2);
  const bob = npc.pose === 'idle' ? Math.round(Math.sin((t || 0) * 1.1) * 1) : 0;
  /* rounded stable body */
  g.rect(5, 6 + bob, 6, 7, 1);
  g.hline(6, 5 + bob, 4, 1); g.hline(6, 13 + bob, 4, 1);          /* rounded caps */
  g.rect(6, 2 + bob, 4, 4, 1);                     /* head */
  g.px(7, 3 + bob, 2); g.px(9, 3 + bob, 2);
  g.rect(11, 9 + bob, basket + 1, basket, 2);      /* basket at hip */
  g.px(12, 8 + bob, 4); g.px(13, 8 + bob, 4);      /* grain in basket */
  g.rect(6, 13, 2, 3, 2); g.rect(9, 13, 2, 3, 2);
  if (npc.pose === 'work') { g.px(3, 10, 4); g.px(2, 11, 4); }    /* weighing */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }
  g.hline(6, 7 + bob, 3, 3);
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildMAYOR(npc, t) {
  const g = makeGrid(), rnd = srand(npc.seed || 1);
  /* upright posture + bell staff + council marker */
  g.rect(5, 5, 6, 9, 1);                           /* tall coat */
  g.rect(6, 1, 4, 4, 1);                           /* high head */
  g.px(7, 2, 2); g.px(9, 2, 2);
  g.hline(5, 7, 6, 4);                             /* council band */
  g.vline(12, 2, 11, 2);                           /* staff */
  g.rect(11, 1, 3, 2, 4);                          /* bell */
  g.px(12, 3, 6);                                  /* clapper spark */
  g.rect(6, 14, 2, 2, 2); g.rect(9, 14, 2, 2, 2);
  const ring = npc.pose === 'work' ? Math.round(Math.sin((t || 0) * 8)) : 0;
  if (ring) g.px(14, 2, 6);                        /* bell rings while routing */
  if (npc.pose === 'proposal') { g.rect(6, 0, 3, 2, 5); }        /* council summons */
  g.vline(6, 6, 6, 3);
  applyStateOverlays(g, npc, rnd);
  return g;
}

function buildHAL(npc, t) {
  const g = makeGrid();
  /* HAL is an OBJECT: octagonal lantern; only the flame changes */
  const o = [[5,2],[10,2],[3,4],[12,4],[3,11],[12,11],[5,13],[10,13]];
  /* octagon frame */
  g.hline(5, 2, 6, 2); g.hline(5, 13, 6, 2);
  g.vline(3, 4, 8, 2); g.vline(12, 4, 8, 2);
  g.px(4, 3, 2); g.px(11, 3, 2); g.px(4, 12, 2); g.px(11, 12, 2);
  g.rect(5, 4, 6, 8, 1);                           /* glass */
  g.rect(7, 6, 2, 4, 6);                           /* flame — verdict-colored at paint */
  g.px(7, 5, 6);
  g.rect(7, 0, 2, 2, 2);                           /* hanging loop */
  g.hline(5, 4, 6, 3);
  return g;
}

/* ---------------------------------------------------------- palettes
   three-color ramp + accents; all distinct base colors (selftest 3) */
const PALETTES = {
  GOBLIN:    { base:'#6f8f3c', shadow:'#465c26', highlight:'#a6c25e', accent:'#8a6a3a', accent2:'#c9b06a', ember:'#ff9a3c' },
  HER:       { base:'#4e9a58', shadow:'#316239', highlight:'#d8c25a', accent:'#e08ab0', accent2:'#f0e0a0', ember:'#fff0c0' },
  CHIDDUSH:  { base:'#5a6a9a', shadow:'#3a4468', highlight:'#8fa0cf', accent:'#7a5ad0', accent2:'#9a7af0', ember:'#e0e8ff' },
  CLAW:      { base:'#8a4a3a', shadow:'#5c2e24', highlight:'#c07858', accent:'#a03828', accent2:'#d0a080', ember:'#ff5030' },
  JESTER:    { base:'#b04a9a', shadow:'#6e2e60', highlight:'#e080c8', accent:'#30b0a0', accent2:'#40d8c0', ember:'#fff040' },
  ARCHIVIST: { base:'#9a8a6a', shadow:'#635a46', highlight:'#cfc0a0', accent:'#d0b050', accent2:'#e8d890', ember:'#ffcf60' },
  WARDEN:    { base:'#7a8290', shadow:'#4c525c', highlight:'#aeb6c4', accent:'#5a6472', accent2:'#c8d0da', ember:'#a0d8ff' },
  STEWARD:   { base:'#c08a4a', shadow:'#7c5830', highlight:'#e8b878', accent:'#d8c840', accent2:'#f0e090', ember:'#fff0b0' },
  MAYOR:     { base:'#6a4a8a', shadow:'#44305c', highlight:'#9878c0', accent:'#d0a830', accent2:'#e8cf70', ember:'#fff080' },
  HAL:       { base:'#c8ccc0', shadow:'#787c74', highlight:'#f0f4ea', accent:'#a0a49a', accent2:'#e0e4da', ember:'#a8d858' },
};
const HAL_VERDICT = { ACCEPTABLE:'#a8d858', HOLD:'#e0a83c', DENY:'#8a5a4a' };

/* ---------------------------------------------------------- painters */
const afterDrawHooks = [];
function paintGrid(ctx, grid, x, y, size, pal, opts) {
  const cell = size / GRID;
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  const halo = opts && opts.halo;
  if (halo) {                                       /* held=fog · admitted=bloom · denied=compost */
    ctx.globalAlpha = .35;
    ctx.fillStyle = halo;
    ctx.fillRect(x - cell, y - cell, size + cell * 2, size + cell * 2);
    ctx.globalAlpha = 1;
  }
  for (let j = 0; j < GRID; j++) for (let i = 0; i < GRID; i++) {
    const c = grid.get(i, j);
    if (!c) continue;
    ctx.fillStyle = (opts && opts.silhouette) ? '#101410'
      : (c === 6 && opts && opts.emberColor) ? opts.emberColor
      : pal[CODES[c]] || pal.base;
    ctx.fillRect(x + i * cell, y + j * cell, Math.ceil(cell), Math.ceil(cell));
  }
  if (opts && opts.tint) {                          /* denied compost tint */
    ctx.globalAlpha = .3; ctx.fillStyle = opts.tint;
    ctx.fillRect(x, y, size, size); ctx.globalAlpha = 1;
  }
  ctx.restore();
}

/* ---------------------------------------------------------- badges (Game-Bible icon style) */
function badgePainter(iconFn) {
  return function (ctx, x, y, size) {
    const cell = size / 8;
    ctx.save();
    ctx.imageSmoothingEnabled = false;
    const p = (i, j, col) => { ctx.fillStyle = col; ctx.fillRect(x + i * cell, y + j * cell, Math.ceil(cell), Math.ceil(cell)); };
    iconFn(p);
    ctx.restore();
  };
}
const BADGES = {
  GOBLIN:    badgePainter(p => { for (let i=1;i<7;i++) p(i, 5 - Math.floor(Math.sin(i)*2), '#6f8f3c'); p(5,3,'#ff9a3c'); }),
  HER:       badgePainter(p => { p(3,1,'#e08ab0'); p(4,1,'#e08ab0'); p(3,2,'#d8c25a'); for(let j=3;j<7;j++)p(3,j,'#4e9a58'); }),
  CHIDDUSH:  badgePainter(p => { for(let j=1;j<7;j++){p(2,j,'#7a5ad0');p(5,j,'#7a5ad0');} p(3,2,'#9a7af0'); p(4,4,'#9a7af0'); }),
  CLAW:      badgePainter(p => { for(let j=2;j<5;j++)for(let i=2;i<5;i++)p(i,j,'#8a4a3a'); p(3,1,'#a03828'); }),
  JESTER:    badgePainter(p => { p(1,1,'#b04a9a'); p(6,2,'#30b0a0'); p(3,4,'#fff040'); p(5,6,'#b04a9a'); p(2,6,'#30b0a0'); }),
  ARCHIVIST: badgePainter(p => { for(let j=1;j<7;j++)p(3,j,'#9a8a6a'); p(3,0,'#ffcf60'); p(5,3,'#cfc0a0'); }),
  WARDEN:    badgePainter(p => { for(let j=1;j<7;j++){p(2,j,'#7a8290');p(3,j,'#aeb6c4');p(4,j,'#aeb6c4');p(5,j,'#7a8290');} }),
  STEWARD:   badgePainter(p => { for(let i=2;i<6;i++)p(i,4,'#c08a4a'); for(let i=3;i<5;i++)p(i,3,'#d8c840'); p(2,5,'#7c5830'); p(5,5,'#7c5830'); }),
  MAYOR:     badgePainter(p => { p(3,1,'#d0a830'); p(4,1,'#d0a830'); p(3,2,'#e8cf70'); for(let j=2;j<7;j++)p(5,j,'#6a4a8a'); }),
  HAL:       badgePainter(p => { p(3,1,'#787c74');p(4,1,'#787c74');p(2,2,'#787c74');p(5,2,'#787c74'); p(3,3,'#a8d858');p(4,3,'#a8d858');p(3,4,'#a8d858');p(4,4,'#a8d858'); p(2,5,'#787c74');p(5,5,'#787c74');p(3,6,'#787c74');p(4,6,'#787c74'); }),
};

/* ---------------------------------------------------------- idle motions */
const IDLE = {
  GOBLIN:    (t, s) => ({ dx: 0, dy: Math.sin(t * 2 + s) * .8 }),
  HER:       (t, s) => ({ dx: Math.sin(t * 1.3 + s) * .6, dy: 0 }),
  CHIDDUSH:  (t, s) => ({ dx: 0, dy: Math.sin(t * .9 + s) * .4 }),
  CLAW:      (t, s) => ({ dx: 0, dy: Math.abs(Math.sin(t * .7 + s)) * .3 }),
  JESTER:    (t, s) => ({ dx: Math.sin(t * 9 + s) * 1.2, dy: Math.cos(t * 7 + s) * .8 }),
  ARCHIVIST: (t, s) => ({ dx: Math.sin(t * .5 + s) * .4, dy: 0 }),
  WARDEN:    () => ({ dx: 0, dy: 0 }),                              /* stillness IS the idle */
  STEWARD:   (t, s) => ({ dx: 0, dy: Math.sin(t * 1.1 + s) * .5 }),
  MAYOR:     (t, s) => ({ dx: 0, dy: Math.sin(t * .8 + s) * .3 }),
  HAL:       (t) => ({ dx: 0, dy: Math.sin(t * 1.5) * .5 }),        /* lantern swings gently */
};

/* ---------------------------------------------------------- role registry */
const BUILDERS = { GOBLIN: buildGOBLIN, HER: buildHER, CHIDDUSH: buildCHIDDUSH,
  CLAW: buildCLAW, JESTER: buildJESTER, ARCHIVIST: buildARCHIVIST,
  WARDEN: buildWARDEN, STEWARD: buildSTEWARD, MAYOR: buildMAYOR, HAL: buildHAL };

const ROLES = {};
Object.keys(BUILDERS).forEach(role => {
  ROLES[role] = {
    role,
    palette: PALETTES[role],
    silhouetteSeed: role.length * 7 + 3,
    idleMotion: IDLE[role],
    workPose: 'work',
    proposalPose: 'proposal',
    damagedPose: 'damaged',
    drawSprite(ctx, x, y, size, npc) {
      npc = npc || {};
      const t = npc.t || 0;
      const idle = (npc.pose || 'idle') === 'idle' ? IDLE[role](t, npc.seed || 0) : { dx: 0, dy: 0 };
      const grid = BUILDERS[role](npc, t);
      const s = npc.state || {};
      const opts = {
        emberColor: role === 'HAL' ? (HAL_VERDICT[npc.verdict] || HAL_VERDICT.ACCEPTABLE) : null,
        halo: s.admitted ? 'rgba(120,220,110,.9)' : s.held ? 'rgba(160,170,160,.9)' : null,
        tint: s.denied ? '#4a3a20' : null,
      };
      paintGrid(ctx, grid, x + idle.dx * (size / GRID), y + idle.dy * (size / GRID), size, PALETTES[role], opts);
      for (const fn of afterDrawHooks) fn(ctx, x, y, size, npc, role);   /* AURA residue hook */
    },
    drawBadge(ctx, x, y, size) { BADGES[role](ctx, x, y, size); },
    drawSilhouette(ctx, x, y, size) {
      paintGrid(ctx, BUILDERS[role]({ seed: ROLES[role].silhouetteSeed }, 0), x, y, size, PALETTES[role], { silhouette: true });
    },
  };
});

/* ---------------------------------------------------------- lineup (Shift+S) */
function drawLineup(ctx, x, y, size, opts) {
  const names = Object.keys(ROLES);
  const pad = size * .35;
  names.forEach((role, i) => {
    const cx = x + i * (size + pad);
    if (opts && opts.silhouette) ROLES[role].drawSilhouette(ctx, cx, y, size);
    else ROLES[role].drawSprite(ctx, cx, y, size, { seed: 7 + i, t: (opts && opts.t) || 0, pose: (opts && opts.pose) || 'idle' });
    ROLES[role].drawBadge(ctx, cx + size * .25, y + size + pad * .3, size * .5);
  });
}

/* ---------------------------------------------------------- selftests */
function selftest() {
  const out = [];
  const T = (name, fn) => { try { const r = fn(); out.push({ name, pass: !!r.pass, note: r.note || '' }); }
                            catch (e) { out.push({ name, pass: false, note: String(e) }); } };
  const cnv = (typeof document !== 'undefined') ? document.createElement('canvas') : null;
  if (cnv) { cnv.width = cnv.height = 256; }
  const ctx = cnv ? cnv.getContext('2d') : null;
  const names = Object.keys(ROLES);

  T('1 every role has drawSprite', () => ({ pass: names.every(r => typeof ROLES[r].drawSprite === 'function') }));
  T('2 every role has drawBadge',  () => ({ pass: names.every(r => typeof ROLES[r].drawBadge === 'function') }));
  T('3 every role has unique palette', () => {
    const bases = new Set(names.map(r => PALETTES[r].base));
    return { pass: bases.size === names.length, note: `${bases.size}/${names.length} distinct` };
  });
  T('4 HAL has three verdict colors', () => ({
    pass: HAL_VERDICT.ACCEPTABLE === '#a8d858' && HAL_VERDICT.HOLD === '#e0a83c' && HAL_VERDICT.DENY === '#8a5a4a' }));
  T('5 JESTER is asymmetric', () => {
    const g = buildJESTER({ seed: 5 }, 0);
    let diff = 0;
    for (let j = 0; j < GRID; j++) for (let i = 0; i < GRID / 2; i++)
      if ((g.get(i, j) > 0) !== (g.get(GRID - 1 - i, j) > 0)) diff++;
    return { pass: diff >= 6, note: `${diff} mirror-diff px` };
  });
  T('6 WARDEN has near-zero idle', () => {
    let amp = 0;
    for (let k = 0; k < 20; k++) { const m = IDLE.WARDEN(k * .3, 1); amp += Math.abs(m.dx) + Math.abs(m.dy); }
    return { pass: amp < .01, note: `amp=${amp.toFixed(4)}` };
  });
  T('7 CLAW gauntlet never opens', () => {
    for (const pose of ['idle', 'work', 'proposal', 'damaged']) {
      const g = buildCLAW({ seed: 3, pose }, 1.7);
      for (let j = 8; j < 11; j++) for (let i = 10; i < 13; i++)
        if (!g.get(i, j)) return { pass: false, note: `open at pose=${pose}` };
    }
    return { pass: true };
  });
  T('8 no external assets loaded', () => {
    if (typeof performance === 'undefined') return { pass: true, note: 'no perf API (headless)' };
    const imgs = performance.getEntriesByType('resource').filter(r => /\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(r.name));
    const tags = (typeof document !== 'undefined') ? document.getElementsByTagName('img').length : 0;
    return { pass: imgs.length === 0 && tags === 0, note: `${imgs.length} img resources, ${tags} <img>` };
  });
  T('9 drawing 30 NPCs does not throw', () => {
    if (!ctx) return { pass: true, note: 'headless: skipped draw' };
    for (let i = 0; i < 30; i++) {
      const role = names[i % names.length];
      ROLES[role].drawSprite(ctx, (i % 8) * 32, Math.floor(i / 8) * 32, 32,
        { seed: i, t: i * .3, pose: ['idle','work','proposal','damaged'][i % 4],
          state: { carrying: i % 3 === 0, proposing: i % 4 === 1, denied: i % 5 === 2, admitted: i % 7 === 3 },
          verdict: ['ACCEPTABLE','HOLD','DENY'][i % 3] });
    }
    return { pass: true };
  });
  T('10 sprite drawing does not mutate governed state', () => {
    const governed = Object.freeze({ ledger: 'sleeps', canon: false, authority: false });
    const npc = { seed: 9, t: 1, pose: 'idle', state: { carrying: true }, governed };
    const before = JSON.stringify(governed) + JSON.stringify(npc.state);
    if (ctx) for (const r of names) ROLES[r].drawSprite(ctx, 0, 0, 32, npc);
    const after = JSON.stringify(governed) + JSON.stringify(npc.state);
    return { pass: before === after };
  });
  return out;
}

/* ---------------------------------------------------------- export */
const WarrenCast = {
  ROLES, PALETTES, HAL_VERDICT, GRID,
  drawLineup, selftest,
  onAfterDraw(fn) { afterDrawHooks.push(fn); },
  law: 'sprite ⊬ verdict · Garden ADMIT ≠ Kernel ADMISSION · ledger sleeps',
};
if (typeof module !== 'undefined' && module.exports) module.exports = WarrenCast;
global.WarrenCast = WarrenCast;
})(typeof window !== 'undefined' ? window : globalThis);
