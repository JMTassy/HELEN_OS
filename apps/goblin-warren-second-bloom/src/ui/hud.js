// HUD — minimal, consistent placement (mission §12).
// Top-left: objective. Top-right: pause + settings. Center: the world.
// Every screen answers in <3s: Where am I? What changed? What can I do now?

export class Hud {
  constructor(root, world, opts) {
    this.world = world;
    this.opts = opts;
    root.insertAdjacentHTML('beforeend', `
      <div id="hud-objective" class="hud-card" aria-live="polite"></div>
      <div id="hud-controls">
        <button id="btn-pause" class="hud-btn" aria-label="Pause">⏸</button>
        <button id="btn-calm" class="hud-btn" aria-label="Reduced sensory mode" title="Reduced sensory mode">✨</button>
      </div>
      <div id="hud-banner" class="hud-card hidden" role="status"></div>
      <div id="hud-complete" class="hud-card hidden" role="dialog"></div>
      <div id="hud-hint" class="hud-hint hidden"></div>
    `);
    this.objective = root.querySelector('#hud-objective');
    this.banner = root.querySelector('#hud-banner');
    this.complete = root.querySelector('#hud-complete');
    this.hint = root.querySelector('#hud-hint');
    this.btnPause = root.querySelector('#btn-pause');
    this.btnCalm = root.querySelector('#btn-calm');

    this.btnPause.addEventListener('click', () => {
      if (world.paused) { world.resume(); this.btnPause.textContent = '⏸'; }
      else { world.pause(); this.btnPause.textContent = '▶'; }
    });
    this.btnCalm.addEventListener('click', () => opts.toggleCalm());

    this.setObjective(world.level.objective_text);

    // Objective evolves with the world — icon-first, few words (§8/§9).
    world.bus.on('fire_woken', () => this.setObjective('🔥 The fire is awake. Feed it.'));
    world.bus.on('fire_fed_twig', () => this.setObjective('🪵 More wood… that pile looks heavy.'));
    world.bus.on('drag_failed', () => this.setObjective('✋ Too heavy for you alone.'));
    world.bus.on('glow_hint', () => this.flash('Hold the wood to leave a mark.'));
    world.bus.on('mark_tap', () => this.setObjective('✨ Your mark glows…'));
    world.bus.on('trace_peak', () => this.setObjective('👀 Someone will notice.'));
    world.bus.on('bram_oriented', () => this.setObjective('👀 Bram noticed your mark.'));
    world.bus.on('wood_delivered', () => this.setObjective('🤝 Bram brought the wood!'));
    world.bus.on('level_complete', () => this.showComplete());
  }

  setObjective(text) { this.objective.textContent = text; }

  flash(text) {
    this.hint.textContent = text;
    this.hint.classList.remove('hidden');
    clearTimeout(this._hintT);
    this._hintT = setTimeout(() => this.hint.classList.add('hidden'), 3500);
  }

  showBanner(text) {
    if (!text) return;
    this.banner.textContent = text;
    this.banner.classList.remove('hidden');
    setTimeout(() => this.banner.classList.add('hidden'), 6000);
  }

  showComplete() {
    this.complete.innerHTML = `
      <h2>🌸 ${this.world.level.title}</h2>
      <p>${this.world.level.complete_text}</p>
      <p class="quiet">You woke the fire yourself.<br>
      You couldn't lift the big wood.<br>
      When you marked it, Bram brought it.</p>
      <button id="btn-again" class="hud-btn wide">Sit by the fire again</button>`;
    this.complete.classList.remove('hidden');
    this.complete.querySelector('#btn-again').addEventListener('click', () => this.opts.restart());
  }
}
