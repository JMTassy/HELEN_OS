// Strict level schema. Unknown fields fail loudly in development.
// Levels are content data, never hard-coded across UI handlers.

const LEVEL_FIELDS = new Set([
  'level_id', 'title', 'zone', 'active_goblins', 'background_goblins',
  'available_verbs', 'objects', 'needs', 'goblin_spawns', 'phases',
  'tutorial_mode', 'next_level', 'objective_text', 'complete_text',
]);

const OBJECT_FIELDS = new Set([
  'object_id', 'kind', 'position', 'draggable', 'drag_weight', 'markable',
]);

const NEED_FIELDS = new Set([
  'need_id', 'type', 'position', 'delegated_actor', 'resolution',
]);

const SPAWN_FIELDS = new Set(['goblin_id', 'position', 'state']);

function checkFields(obj, allowed, where, errors) {
  for (const k of Object.keys(obj)) {
    if (!allowed.has(k)) errors.push(`unknown field "${k}" in ${where}`);
  }
}

export function validateLevel(level) {
  const errors = [];
  checkFields(level, LEVEL_FIELDS, `level ${level.level_id || '?'}`, errors);
  if (!level.level_id) errors.push('level_id required');
  if (!Array.isArray(level.available_verbs)) errors.push('available_verbs must be array');
  for (const o of level.objects || []) checkFields(o, OBJECT_FIELDS, `object ${o.object_id}`, errors);
  for (const n of level.needs || []) checkFields(n, NEED_FIELDS, `need ${n.need_id}`, errors);
  for (const s of level.goblin_spawns || []) checkFields(s, SPAWN_FIELDS, `spawn ${s.goblin_id}`, errors);
  for (const o of level.objects || []) {
    if (o.position && (o.position.length !== 2)) errors.push(`object ${o.object_id} position must be [x,y]`);
  }
  if (errors.length) {
    throw new Error('LEVEL SCHEMA INVALID:\n  ' + errors.join('\n  '));
  }
  return true;
}
