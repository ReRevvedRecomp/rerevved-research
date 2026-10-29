# Recovered game reference

System pages summarize canonical manifests/catalogs, not independent evidence or
player setup instructions. Proposed hooks/features retain stated conditions.

## Units, cities, and civilization

- [Unit definitions](unit-definitions.md) - records, production/cost/AI, Move staging and extension limits.
- [City Militia and trainable Scout](city-militia-scout.md) - founding/Loyalty/persistence and Scout requirements.
- [Barbarian spawning and capital protection](barbarians.md) - garrisons, AI, production and the conditional static capital gate.
- [Friendly village rewards](friendly-villages.md) - six development metrics, reward identities, priority alternatives and session-lifecycle limits.
- [Spy missions](spy-missions.md) - native choices, local selection policy and ordinary AI ingress limits.
- [Ordinary combat boundary](ordinary-combat.md) - stats, stores, presentation and outcome/persistence limits.
- [Nuclear actions](nuclear-actions.md) - AI unit production and launch gates, conditional interception, damage, missile consumption and effect limits.
- [Civilization Unique Abilities](civilization-bonuses.md) - leaders, UAs and cumulative 16 by 4 UEAs.
- [AI configuration boundaries](ai-options.md) - eight-civilization placement, participant storage, economic seams and bonus-aware valuation.
- [City growth and population bonuses](city-growth.md) - thresholds, carryover and Gold/Irrigation rewards.
- [Economy bonus correction contracts](economy-bonus-corrections.md) - retain Gold income and growth benefits while removing their cost penalties.
- [Science and technology cost](science.md) - cost, progress, first-discovery rewards, acquisition,
  excess Gold and the spaceship launch-date admission boundary.

## Resources, setup, and saves

- [Map size and terrain bias](map-size-terrain-bias.md) - fixed32 object indexing,
  dimensions, climate inputs and civilization start preference.
- [Starting eras and game pace](scenario-era-and-pace.md) - scenario technology
  grants, movement input and independent progression surfaces.
- [Resource definitions](resource-definitions.md) - 22 ordinals, names/tokens, technologies and terrain/remainders.
- [Resource identity overrides](resource-identity-overrides.md) - type/models, Forest effects, persistence and India ordering.
- [Resource density and placement](resource-placement.md) - presence, Settler coordinates, Iron and refresh/placement limits.
- [Save storage and slot identity](save-storage.md) - filenames, namespaces and sidecar seams.
- [Game calendar state](game-calendar.md) - turn/year conversion, transitions,
  and presentation limits.
- [Game of the Week seed selection](game-of-the-week.md) - weekly/manual inputs, replay and result isolation.

## Frontend, content, and rendering

- [Retail achievements](achievements.md) - all 50 IDs, English metadata, gamerscore,
  icon image IDs and native unlock-trigger mapping status.
- [Frontend, frame, and input ownership](frontend-frame-and-input.md) - states, timing/callbacks, availability, menus and controllers.
- [Controller prompt families](controller-glyphs.md) - restart-required name
  redirect, movie-label alternatives, dimensions and package coverage.
- [Controller glyph labels](controller-glyph-labels.md) - exact six-sprite
  inventories, platform pairs, collision classes and loading-tip limits.
- [Content staging and source resolution](content-source-resolution.md) -
  staging, registration and lookup/fallback order.
- [Audio manager and 2D script table](audio-script-table.md) - ownership, lifecycle, lookup and unknowns.
- [GFx state and MovieClipLoader requests](gfx-state-and-loadclip.md) - providers, loadClip, attachment and fulfillment.
- [GFx external-image rendering](gfx-image-rendering.md) - images, fills, state, indexed draws and fetches.
- [Scene render tree lifecycle](scene-render-lifecycle.md) - publication, render/update, teardown and receiver limits.
- [Native renderer draw fields](native-renderer-draw-fields.md) - layouts, state/commands and lifetime.
- [Native renderer anchor sites](native-renderer-anchor-sites.md) - draw/clear owners, callers and resource limits.
- [Native renderer frame passes](native-renderer-frame-passes.md) - partial tiling/clear/resolve/presentation order.
- [Native renderer frame pacing](native-renderer-frame-pacing.md) - timing, waits/limiters and presentation intervals.
- [Native renderer shader constants](native-renderer-shader-constants.md) -
  writers, stage shadows and unknown consumers.

## Networking

- [Xbox network messages](xbox-network-messages.md) - records/queues, native turn labels, human completion, serialization and wire limits.
- [Xbox System Link QoS boundary](xbox-system-link-qos.md) - lookup/results, action traces and discovery unknowns.

Keep related strings, names, enums, fields and guards together. Catalogs own
cross-system indexes; do not duplicate them.
