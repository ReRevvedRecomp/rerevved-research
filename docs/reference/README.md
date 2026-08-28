# Recovered game reference

These pages present settled guest-code findings by game system. They are the
readable layer over the topic manifests and reusable catalogs, not a separate
source of evidence.

- [Unit definitions](unit-definitions.md) - unit type IDs, base combat stats,
  normal production-cost ownership, civilization-specific identities, and
  bounded combat and AI consumers.
- [Civilization Unique Abilities](civilization-bonuses.md) - leaders, Unique
  Abilities, the 16 by 4 cumulative Unique Era Ability table, and its
  shared activation lookup.
- [Save storage and slot identity](save-storage.md) - selected record layout,
  internal filenames, and pre-load/post-save sidecar edges.
- [Frontend, frame, and input ownership](frontend-frame-and-input.md) -
  frontend states, timing, application callbacks, availability, and controller
  dispatch boundaries.
- [GFx state and MovieClipLoader requests](gfx-state-and-loadclip.md) - state
  providers, native loadClip requests, attachment, and fulfillment.
- [GFx external-image rendering](gfx-image-rendering.md) - decoded images,
  image fills, renderer state, indexed draws, and guest fetch emission.
- [Audio manager and 2D script table](audio-script-table.md) - manager and
  stream ownership, table lifecycle, bounded lookup, and unresolved fields.
- [Frontend content staging and source resolution](content-source-resolution.md) -
  distinct staging owners, registered-source publication, reverse lookup, and
  fallback order.
- [Game calendar state](game-calendar.md) - turn/year scalars, native
  conversion, transition ownership, and presentation limits.
- [Scene render-tree lifecycle](scene-render-lifecycle.md) - tree publication,
  render and update edges, teardown, and receiver qualifications.
- [Xbox network messages](xbox-network-messages.md) - internal records, queue
  and dispatch ownership, supported semantic anchors, serialization, and wire
  qualifications.
- [Xbox System Link QoS boundary](xbox-system-link-qos.md) - exact lookup
  producer, result-word gate, release path, and remaining discovery
  qualifications.

Keep related strings, semantic function names, enum values, fields, and guards
together on the applicable system page. Do not create separate string,
function, or enum inventories here. The machine-readable catalogs provide the
canonical cross-system indexes.
