// Drag settlement — the single transaction that ends a pointer drag.
//
// UI_STATE_CONSISTENCY_INVARIANT: the input layer must never leave view-state
// asserting an outcome the world did not grant. `dragPos` is a preview owned by
// the input layer, not world state; it may survive a pointerup only if the world
// actually consumed the object. On refusal the object returns to its resting
// place, so the player sees the truth: the fire would not take it.
//
// This rule lived inline in index.html where no test could reach it, and it was
// applied on only one of two refusal paths (DEFECT-002). It lives here so it is
// enforceable. See tests/test_drag_settlement.mjs.
import { INPUT } from '../core/events.js';

export function settleDrag(world, objectId, droppedOnTarget) {
  const obj = world.objects.get(objectId);
  if (!obj) return { ok: false, reason: 'unknown_object' };

  const result = droppedOnTarget
    ? world.dispatch(INPUT.DRAG, { objectId })
    : { ok: false, reason: 'released_off_target' };

  // The world consumed it, or it comes home. No third outcome.
  if (!obj.consumed) obj.dragPos = null;

  return result;
}
