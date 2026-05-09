# Avatar Placement Rules

Full doc: `airi_helen_avatar/SKILL.md`

## Canonical (current)

```
Center of constellation — gravitational anchor
  size: 120px circle
  exclusion zone: 80px radius (nodes orbit outside)
  orbital ring: 18s rotating ellipse
  pulse: 4s signal amber breathe

Detail panel — witness thumbnail (on node click)
  size: 36px circle
  phrase: "I witness this {TYPE}."
```

## Allowed Expansions

If user requests — and only then:

- Boot/splash: full-width portrait, dissolves in ≤2s before live field appears
- Ledger seal: 24px icon adjacent to MAYOR verdict block, only if connected to a real receipt event
- Bottom bar: persistent 28px circular mini-avatar as "active witness" indicator

## Forbidden

- Full-color without palette unlock
- Animated face (waving, speaking, reacting)
- Multiple HELEN instances on same surface
- AURA image in place of HELEN
- Avatar placed purely for aesthetic reasons with no functional role
