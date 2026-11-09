# Native renderer anchor draw sites

The
[anchor-site topic manifest](../../manifests/native-renderer-anchor-draw-sites.json)
attributes four runtime-reported addresses to their containing guest functions
and records the static resource paths within the stated limits. The addresses
came from title `df823a99` (observation 2026-10-17) and selected the search
sites; this result does not turn them into independent runtime frequency
evidence.

| Reported address | Actual branch or entry | Containing function | Static path and resources | Frequency |
| --- | --- | --- | --- | --- |
| `0x8230686C` | `0x82306868: bl 0x826A39F8` | `0x823067F8` | Indexed sink: `0x82C2A8E8 -> 0x82C29628`, with outer functions `0x82C4C740` and `0x82C4BC00`, plus `0x82C71A00` on direct `0x82C4C740`. The index buffer field is `+0x3094`. The source, format, texture, target and subsystem are unknown. | Unresolved |
| `0x82304258` | `0x82304254: bl 0x826A3000` | `0x82303F70` | GFx nonindexed UP: vertices `+0x208`, stride 28, primitive 4, count `3*trunc(r9/3)` from `r9`. Color transform `+0x114`; `[entry-r8+0x28]` is set through `0x8269AF10`. It selects no target. | Unresolved |
| `0x82303E90` | `0x82303E8C: bl 0x826A3568` | `0x82303C38` | GFx indexed draw: vertex buffer `+0x164` and index buffer `+0x168`, formats `+0x16C` and `+0x170`, texture from the active fill. The trace of who uses these fields stops at a dynamic vtable. | Unresolved |
| `0x826A22F8` | Entry; caller `0x826A2A80: bl 0x826A22F8` | `0x826A22F8`, called by `0x826A2970` | ClearF keeps a nonnull r5 rectangle. A null one builds the extents from RT0 `+0x3098` or depth `+0x30A8`. It forwards r6 as color, f1 as depth and r8 as stencil, clips the viewport and scissor, and iterates the selected MRT slots that have a target. The surface and tiled set are unknown. | Unresolved |

The recompiled copy of `0x82C2A8E8` encloses raw `0x82C2BDE4`, is registered in
the init map, and calls `0x82C29628`. The canonical query truncates on a bad
instruction and reports no callers or callees. A search of the recompiled code
finds three calls: one in `0x82C4C740` and two in `0x82C4BC00`. A raw direct
`bl` search (LK=1, cap 32) independently found `0x82C4C8E0 -> 0x82C4BC00` and
`0x82C71D44 -> 0x82C4C740`, without truncation or cancellation.

Eight functions stay in the result: `0x823067F8`, `0x82C29628`, `0x82C2A8E8`,
`0x82C4C740`, `0x82C4BC00`, `0x82C71A00`, `sub_82C7DF58` and `sub_82D83B38`.
The longest path has six edges through `0x82C4BC00`. The direct path through
`0x82C4C740` has five. A prior `bctrl` limits provenance, not caller traversal.
The subsystem remains unknown at the declared cap of about five levels.

Neither GFx producer has a raw direct caller. The trace of the indexed producer
stops at dynamic vtable dispatch. The scans do not exclude indirect or tail
branches or duplicate references. ClearF has seven matches: `0x823064E0` and
`0x8250E718` were selected, and five are unexpanded at the cap. For the latter,
the nonzero low-byte result of the prior `bctrl` decides whether ClearF runs,
without blocking caller attribution.

Per-frame execution, output, asset identity and complete passes remain unknown.
The [D3D surface](../../manifests/native-renderer-d3d-runtime-surface.json) and
[draw fields](native-renderer-draw-fields.md) keep the wider qualifications on
which resources are set on the device.
