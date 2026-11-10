# Recovered game reference

These pages summarize findings from the canonical manifests and catalogs.
They are references for contributors and modders, not independent evidence or
player setup instructions. Proposed hooks and features keep their stated
conditions.

Pages are grouped in folders by system.

## Gameplay

- [Unit definitions](gameplay/unit-definitions.md) - unit records, production costs, AI evaluation, Move commands and limits on adding definitions.
- [Gameplay cost arithmetic](gameplay/gameplay-cost-arithmetic.md) - rounding in rush, technology, Wonder, road, interest and fleet sale costs, and the AI rush valuation candidate.
- [Building and Wonder storage limits](gameplay/building-wonder-storage-limits.md) - option list capacity, 33 Wonder claim slots, definition limits and what adding a Building or Wonder would need.
- [Stonehenge and Library effects](gameplay/stonehenge-and-library-effects.md) - Temple and Library yields, state credits, the ranking table, Wonder completion and why a replacement is not one hook.
- [Unit movement presentation](gameplay/unit-movement.md) - how unit movement is drawn: step size, native snap, busy and completion addresses, and hook points for faster movement.
- [City Militia and trainable Scout](gameplay/city-militia-scout.md) - grants when founding cities, Loyalty, saved state and Scout requirements.
- [Barbarian spawning and capital protection](gameplay/barbarians.md) - garrisons, AI, production and the static capital check, which applies only under a condition.
- [Friendly village rewards](gameplay/friendly-villages.md) - six development measures, reward choices, priority rules and limits across games.
- [Spy missions](gameplay/spy-missions.md) - native choices, local selection policy and limits on how AI Spies reach missions.
- [Combat](gameplay/combat.md) - battle flow, random state, saving and reloading, loss protection and presentation.
- [Combat strength](gameplay/combat-strength.md) - attack and defense strength, Veteran, Fortify, terrain, armies and unit abilities.
- [Combat loss protection](gameplay/combat-loss-protection.md) - which battles are protected, ratio rules by turn, the Catapult guarantee and survival.
- [Nuclear actions](gameplay/nuclear-actions.md) - AI unit production and launch checks, interception that depends on a condition, damage, missile consumption and effect limits.
- [Civilization Unique Abilities](gameplay/civilization-bonuses.md) - leaders, UAs and cumulative 16 by 4 UEAs.
- [AI settings and behavior](gameplay/ai-options.md) - how the AI decides, how many AI civilizations play and at what difficulty, eliminating AI civilizations and Always at War.
- [City growth and population bonuses](gameplay/city-growth.md) - thresholds, carryover and Gold and Irrigation rewards.
- [City population cap](gameplay/city-population-cap.md) - the native size limit of 31, what extra citizens produce, the unassigned citizen histogram and hook points for a larger cap.
- [Economy bonus correction contracts](gameplay/economy-bonus-corrections.md) - keep Gold income and growth benefits while removing their cost penalties.
- [Science and technology cost](gameplay/science.md) - cost, progress, First Discovery bonuses, acquisition,
  excess Gold, AI research choice and when a spaceship launch date is accepted.
- [Apollo Program discovery bonuses](gameplay/apollo-discovery-bonuses.md) - virtual ownership,
  direct acquisition, eligibility for first-discovery rewards and limits on repeats.
- [Map size and terrain bias](gameplay/map-size-terrain-bias.md) - object indexing with a fixed width of 32,
  dimensions, climate inputs and civilization start preference.
- [Resource definitions](gameplay/resource-definitions.md) - 22 resource entries, names and tokens, required technologies, terrain and coordinate remainders.
- [Resource identity overrides](gameplay/resource-identity-overrides.md) - type and models, Forest effects, persistence and India ordering.
- [Resource density and placement](gameplay/resource-placement.md) - resource-presence flags, Settler coordinates, Iron and limits on placement and refresh.

## Setup and saves

- [Heights file and the override hook](setup/heights-file-override.md) - what the per-map heights DDS is, the size rules a custom file must meet, and the candidate hook that replaces its bytes after load.
- [Starting eras and game pace](setup/scenario-era-and-pace.md) - scenario technology
  grants, movement input and independent progression surfaces.
- [Save storage and slot identity](setup/save-storage.md) - file names, namespaces and sidecar hook points.
- [Game calendar state](setup/game-calendar.md) - converting turns to years, era
  changes, the earliest Domination date, deadlines and presentation limits.
- [Game of the Week seed selection](setup/game-of-the-week.md) - weekly and manual inputs, replay and result isolation.

## Interface

- [Spaceship part presentation](interface/spaceship-part-presentation.md) - what happens when a part is built, what a mod that skips the cutscene must keep, and every hook point.
- [Retail achievements](interface/achievements.md) - all 50 IDs, English metadata, gamerscore,
  icon image IDs and native unlock-trigger mapping status.
- [Frontend, frame, and input paths](interface/frontend-frame-and-input.md) - states, timing and callbacks, availability, menus and controllers.
- [Advisor popup sites](interface/advisor-popup-sites.md) - the 169 advisor popup callers grouped by purpose, with result use and which popups a mod can suppress.
- [Controller prompt families](interface/controller-glyphs.md) - restart-required name
  redirect, movie-label alternatives, dimensions and package coverage.
- [Controller glyph labels](interface/controller-glyph-labels.md) - exact six-sprite
  inventories, platform pairs, collision classes and loading-tip HTML inputs.

## Networking

- [Xbox network messages](networking/xbox-network-messages.md) - the five word command record, its queue and 66 case dispatcher, the type table with name status, framing and transport order, and Xbox limits.
- [Xbox turn command flow](networking/xbox-turn-command-flow.md) - commands 46 to 55 for turn start, finished players, AI step, sync check and end turn, the type 49 mask, the stored random state word and the case 53 scans.
- [Xbox command serialization](networking/xbox-command-serialization.md) - the 20 byte command payload inside a 32 byte write and 28 byte read envelope, the leading value 77 against the factory default 1000, and the function table near factory `0x821D3778`.
- [Xbox command callback tables](networking/xbox-command-callback-tables.md) - the function pointer tables at `0x82136930` and `0x8211EC1C`, the `0x827F5780` fallback chain and the `0x831580F8` value; a reference appendix with no known modding use yet.
- [Xbox System Link QoS](networking/xbox-system-link-qos.md) - lookup, result check and release chain, request buffer, host setup order and what the searches did not find.
- [Xbox game selector commands](networking/xbox-game-selector-commands.md) - the Y and X button handlers from the System Link movie through the script command prefix check to the observed native targets.
- [Xbox networking call inventory](networking/xbox-networking-call-inventory.md) - XMsg and XGI call forms, QoS listen, socket and XNet inventories, and the `0x0005800E` host message.

## Rendering

- [Terrain texture roles](rendering/terrain-texture-roles.md) - heights, blends and lightmap image sizes, the 32 by 32 tile and 33 by 33 corner record layout, the slot 11 and 12 texture coordinate formula, and what is not yet shown.
- [GFx state and MovieClipLoader requests](rendering/gfx-state-and-loadclip.md) - providers, loadClip, attachment and fulfillment.
- [GFx external-image rendering](rendering/gfx-image-rendering.md) - images, fills, state, indexed draws and fetches.
- [Scene render tree lifecycle](rendering/scene-render-lifecycle.md) - publication, render and update, teardown and receiver limits.
- [Native renderer draw fields](rendering/native-renderer-draw-fields.md) - layouts, state and commands, and lifetime.
- [Native renderer anchor sites](rendering/native-renderer-anchor-sites.md) - draw and clear functions, callers and resource limits.
- [Native renderer frame passes](rendering/native-renderer-frame-passes.md) - partial order of tiling, clear, resolve and presentation.
- [Native renderer frame pacing](rendering/native-renderer-frame-pacing.md) - timing, waits and limiters, and presentation intervals.
- [Native renderer shader constants](rendering/native-renderer-shader-constants.md) -
  writers, stage shadows and unknown consumers.
- [Native renderer shader generation](rendering/native-renderer-shader-generation.md) - how scene shaders are compiled at run time, descriptor fields, skin modes and water shader identity.
- [Native renderer shader refusals](rendering/native-renderer-shader-refusals.md) - the 67 refused shader stages, the video decoder bank and what each refusal class means.
- [Native renderer user pointer draws](rendering/native-renderer-up-draw-reservation.md) - ring space reservation, copies and device field updates for GFx UP draws, and the effects a replacement must keep.
- [Native renderer tiling workers](rendering/native-renderer-tiling-workers.md) - how Begin, End and the worker threads hand recorded commands to each tile, and the open `0x8A` and `0x8C` questions.
- [Native renderer ring setup and teardown](rendering/native-renderer-ring-and-teardown.md) - command buffer and primary ring, setup and reconfiguration order, setup callers and video imports.
- [Native renderer present and completion](rendering/native-renderer-present-and-completion.md) - present order, tickets and fences, the interrupt callback, flip counters and timestamp queries.
- [Native renderer resolve resources](rendering/native-renderer-resolve-resources.md) - the 0x34 byte resource header read by Resolve and its two buffer objects.
- [NIF scene data and draw inputs](rendering/nif-scene-draw-inputs.md) - triangle geometry, transforms, material and texture records of a NIF shape, and why no loaded shape is yet tied to a draw call.
- [Movie draw plane setup](rendering/movie-draw-binding.md) - how movie code hands its first texture plane to the draw, the strip draw and cleanup, and the unknown decoder and clock.

## Content

- [Content staging and source resolution](content/content-source-resolution.md) -
  staging, registration and lookup and fallback order.
- [Audio manager and 2D script table](content/audio-script-table.md) - layout, lifecycle, lookup and unknowns.

Keep related strings, names, enums, fields and guards together. Catalogs hold
cross-system indexes; do not duplicate them.
