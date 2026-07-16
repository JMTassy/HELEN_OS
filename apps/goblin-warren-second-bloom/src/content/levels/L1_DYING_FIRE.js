// LEVEL 1 — THE DYING FIRE
// Core proof: the Embodied Delegation Ladder.
//   body (KINDLE) → hand (DRAG) → limit (heavy wood) → signal (MARK) → Bram acts.
// One continuous 90-second scene. No action counter. No daily verdict.

export const L1_DYING_FIRE = {
  level_id: 'L1_DYING_FIRE',
  title: 'The Dying Fire',
  zone: 'campfire_clearing',
  active_goblins: ['BRAM'],
  background_goblins: ['LULU'],
  available_verbs: ['KINDLE', 'DRAG', 'MARK'],
  objective_text: 'The night is cold. Wake the fire.',
  complete_text: 'The lantern is lit. You and Bram did this together.',
  tutorial_mode: 'PERCEPTUAL_ONLY',
  next_level: 'L2_QUIET_SIGNAL',
  objects: [
    { object_id: 'FIRE', kind: 'campfire', position: [0.50, 0.62], draggable: false, markable: false },
    { object_id: 'TWIG', kind: 'twig', position: [0.62, 0.72], draggable: true, drag_weight: 1, markable: false },
    { object_id: 'BIGWOOD', kind: 'wood_pile', position: [0.16, 0.38], draggable: true, drag_weight: 99, markable: true },
    { object_id: 'LANTERN', kind: 'lantern', position: [0.78, 0.42], draggable: false, markable: false },
  ],
  needs: [
    {
      need_id: 'FIRE_DYING',
      type: 'DYING_FIRE',
      position: [0.50, 0.62],
      delegated_actor: 'BRAM',
      resolution: 'FIRE_STRONG_AND_LANTERN_LIT',
    },
  ],
  goblin_spawns: [
    { goblin_id: 'BRAM', position: [0.36, 0.78], state: 'SLEEPING' },
    { goblin_id: 'LULU', position: [0.88, 0.80], state: 'BACKGROUND' },
  ],
  phases: ['COLD_NIGHT', 'FIRST_FLAME', 'HANDS', 'LIMIT', 'DELEGATION', 'TOGETHER'],
};
