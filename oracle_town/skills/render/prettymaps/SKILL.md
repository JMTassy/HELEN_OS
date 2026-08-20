# SKILL — prettymaps_render (HELEN OS map rendering)
authority=false · canon=false · ledger_effect=none · status=CANDIDATE · a bounded work-surface, not a ruling

Render OpenStreetMap-based stylized maps via the external **PrettyMaps** library (marceloprates).
NON-SOVEREIGN. This skill governs the *use* of an external tool under a copyleft license — its most
important job is not drawing maps, it is **not shipping an unattributed figure**.

## ⚖️ LICENSE GATE (load-bearing — read first)
Witnessed from `github.com/marceloprates/prettymaps` README (raw, 2026-08-17):
- **License: GNU AGPL-3.0** (strong copyleft, incl. the network-use clause).
- **Mandatory attribution:** *"Please keep the printed message on the figures crediting my repository and
  OpenStreetMap (mandatory by their license)."* Plus OpenStreetMap's own copyright
  (`openstreetmap.org/copyright`).

Operator directive (2026-08-17): **HELEN OS cannot yet credit — so keep in memory and DO NOT PUBLISH.**
Therefore this skill is **fail-closed**:

    publish_allowed = attribution_stamped_on_figure  AND  helen_credit_pipeline_wired  AND  agpl_review_done
    default = FALSE  ⇒  every output is LOCAL_ONLY / NO_PUBLISH / NO_SHIP

- The skill **always** stamps the credit on the figure; it must **never** strip or omit it.
- Until HELEN's published surfaces are guaranteed to carry the PrettyMaps + OSM credit, no PrettyMaps-derived
  figure may be shipped, posted, sent to a client, or embedded in a public artifact.
- PrettyMaps is **not vendored** into the sovereign codebase. It is an *external, operator-installed* tool
  (`pip install prettymaps` — heavy deps: osmnx/matplotlib/shapely/vsketch — **operator-gated, not auto-installed**).
- AGPL implications for any HELEN service that *conveys* PrettyMaps output over a network are a **legal
  question flagged to the operator**, not resolved here. This skill is not legal advice; it enforces the
  attribution mechanism and the NO_PUBLISH default.

## Contract (HELEN Skills Doctrine)
- **Reads:** location (place name or lat/lon), preset (`default|minimal|macao|tijuca`), boundary
  (circle/radius/dilate), per-layer style; OSM data via osmnx (external network read).
- **Writes:** `artifacts/maps/<slug>.{svg,png}` (LOCAL, stamped, NO_PUBLISH) + a receipt sidecar
  `artifacts/maps/<slug>.receipt.json`.
- **Artifact:** the stamped map figure — quarantined LOCAL_ONLY.
- **Receipt (mandatory fields):** `{source_lib:"prettymaps", source_license:"AGPL-3.0",
  attribution_text, attribution_present:bool, osm_credit:true, publish_status:"NO_PUBLISH",
  location, preset, generated_local_only:true, authority:false}`.
- **HAL flag:** authority=false. The figure is a REVIEWED_CANDIDATE at best; publication belongs to a
  license-cleared pipeline, not to this skill.

## Attribution stamp (enforced on every figure)
    Map data © OpenStreetMap contributors · openstreetmap.org/copyright
    Rendered with PrettyMaps (© marceloprates, AGPL-3.0)

## Features exposed (from witnessed README)
presets (default/minimal/macao/tijuca) · tag-filtered OSM layers · per-layer matplotlib styling + palettes ·
SVG vector output (vsketch) · hillshade terrain · keypoints annotation · circle/radius/dilate boundaries.

## Firewall / discipline
Never writes to `oracle_town/kernel/**`, `helen_os/governance|schemas/**`, ledger, or MAYOR paths. Does not
install packages, fetch, or run without an operator verb. The wrapper `helen_prettymaps.py` (candidate)
refuses to emit an un-stamped figure and defaults `publish_status=NO_PUBLISH`.

*HELEN OS — created by JM Tassy.*
