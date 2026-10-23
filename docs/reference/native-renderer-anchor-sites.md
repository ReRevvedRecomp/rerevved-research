# Native renderer anchor draw sites

The
[anchor-site topic manifest](../../manifests/native-renderer-anchor-draw-sites.json)
attributes four runtime-reported addresses to their containing guest functions
and records the bounded static resource paths. The addresses came from title
`df823a99` (observation 2026-10-17) and selected the search sites; this result
does not turn them into independent runtime frequency evidence.

| Reported address | Actual branch or entry | Containing function | Static owner and resources | Frequency |
| --- | --- | --- | --- | --- |
| `0x8230686C` | `0x82306868: bl 0x826A39F8` | `0x823067F8` | Indexed sink: `0x82C2A8E8 -> 0x82C29628`, outer `0x82C4C740`/`0x82C4BC00`, plus `0x82C71A00` on direct `0x82C4C740`. Index binding `+0x3094`; source/format/texture/target/subsystem unknown. | Unresolved |
| `0x82304258` | `0x82304254: bl 0x826A3000` | `0x82303F70` | GFx nonindexed UP: vertices `+0x208`, stride 28, primitive 4, count `3*trunc(r9/3)` from `r9`. Color transform `+0x114`; `[entry-r8+0x28]` binds via `0x8269AF10`. No target selection. | Unresolved |
| `0x82303E90` | `0x82303E8C: bl 0x826A3568` | `0x82303C38` | GFx indexed gate: vertex/index `+0x164`/`+0x168`, formats `+0x16C`/`+0x170`, texture from active fill. Ownership stops at dynamic vtable. | Unresolved |
| `0x826A22F8` | Entry; caller `0x826A2A80: bl 0x826A22F8` | `0x826A22F8`, called by `0x826A2970` | ClearF retains nonnull r5 rectangle; null builds extents from RT0 `+0x3098` or depth `+0x30A8`. Forwards r6 color/f1 depth/r8 stencil; clips viewport/scissor, iterates selected bound MRT slots. Surface/tiled set unknown. | Unresolved |

Generated `0x82C2A8E8` encloses raw `0x82C2BDE4`, is init-map registered, and
calls `0x82C29628`. Canonical query truncates on bad instruction with no
callers/callees. Generated search finds three calls: one in `0x82C4C740`, two in
`0x82C4BC00`. Raw direct-bl (LK=1, cap 32) independently found
`0x82C4C8E0 -> 0x82C4BC00` and `0x82C71D44 -> 0x82C4C740` without
truncation/cancellation.

Eight retained functions: `0x823067F8`, `0x82C29628`, `0x82C2A8E8`,
`0x82C4C740`, `0x82C4BC00`, `0x82C71A00`, `sub_82C7DF58`, `sub_82D83B38`.
Longest path: six edges via `0x82C4BC00`; direct `0x82C4C740`: five. Prior
`bctrl` limits provenance, not caller traversal; subsystem remains unknown at
the declared approximately five-level cap.

Neither GFx producer has a raw direct caller; indexed ownership stops at dynamic
vtable dispatch. Scans exclude neither indirect/tail branches nor duplicate
references. ClearF has seven matches: `0x823064E0`/`0x8250E718` selected, five
unexpanded at cap. On the latter, prior `bctrl`'s nonzero low-byte result gates
ClearF without blocking caller attribution.

Per-frame execution, output, asset identity and complete passes remain unknown.
[D3D surface](../../manifests/native-renderer-d3d-runtime-surface.json) and
[draw fields](native-renderer-draw-fields.md) retain wider binding
qualifications.
