# Native renderer frame passes

The
[frame-pass manifest](../../../manifests/native-renderer-frame-pass.json)
groups static fragments, not execution counts or total frame order. The
alternate setup and end share the guarded `0x82C71880`. Callback `0x82E87D18`
reaches `0x82C7DF58`. The service `bctrl` at `0x82C7E0F8` returns to `0x82C7E0FC`
before `0x82C7E104 -> 0x82C71A00`, which requires a nonzero low byte in the
incoming r4.

`RVA-F-0262` links `0x8250F988` and `0x8250AC90` only if the global still holds
the `0x8250F0E8` object with vptr `0x82047050` and the dispatch predicates pass.
Reset stores and historical captures show neither that the object is currently
held nor that its type is unique.

[Group setup](../../../manifests/native-renderer-frame-group-binding.json)
(`RVA-F-0265`), nonzero `+0x98` arm:

1. Byte `+0xA0` selects `+0xAC` or `+0xB0`. The zero-initialized assignment
   passes it as r4 to `0x821D6DD0`.
2. `0x8250F988` can store it at `+0x550` after the incoming `+0x74` and `+0x78`
   provider work and the `0x82520478` low-byte guard.
3. F988 reloads `+0x550` at `0x8250FA0C` and passes r4 to F60 at `0x8250FA14`.
   F60 reads `+0x60` and `+0x58`. Later callbacks reload the current group and
   read `+0x48` and `+0x4C`. Equality with the original group needs the value to
   stay valid, valid storage, no aliasing and the vptr conditions.

On the null incoming `+0x74` arm, the
[fallback contract](../../../manifests/native-renderer-frame-group-binding.json#/currentEvidence/fallbackProviderBoundary)
ties `0x82520958` to a 276-byte storage request initialized by `0x825200D0`.
Its successful local suffix returns that saved object. The first unresolved
provider is incoming group `+0x60` at `0x825209A0`, stored to object `+0xF8`.
Renderer `+0x550` still receives the incoming group. The allocation extent, the
current storage and vptr, the helper returns and the target and depth identity
are not yet established.

Wrapper D10 `+0x74` supplies a separate group. Its target and depth remain
unknown. The
[Resolve discriminator](../../../manifests/native-renderer-resolve-destination-lifecycle.json#/decisiveObservation/observationCoverage)
requires four things before `0x8250AFEC`: a link from the item or provider to r6,
the same-call color and depth descriptor with its EDRAM row, the current run and
image identity, and successful reads. Native EDRAM diagnostics and Xenos
descriptor events supply neither link, and capped omissions are inconclusive.
Even if all four were shown, the identity of the incoming group `+0x74` and
`+0x78` in F0265 would stay open.

| Fragment | Local static edge | Target | Depth | EDRAM base | Clear | Resolve destination | Consumers | Predicated tiling | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| callback-tiling | `0x82E87D18 -> 0x82C7DF58 -> 0x82C71A00`; three static helper callsites to `0x82C71880` at `0x82C71CB8`, `0x82C71E1C`, and `0x82C71E58` | Unknown | Unknown | Unknown | Delegated to the alternate-tiling arm | None shown | Relations, predicates and order of `0x8250F988` and `0x8250AC90` in `RVA-F-0262`, which hold only under conditions; others unknown | Unknown | strong |
| alternate-tiling-arm | `0x82C71880 -> 0x8269D7D8 -> 0x826A2970 -> 0x826A22F8`; after setup returns, the same helper sibling-calls `0x8269DB20` at `0x82C71944`; setup and end arm requires global bit `0x8`, nonnull global pointer, receiver byte `+0xA3` nonzero, and middleware `+8` zero | Bound target identity unknown | Bound depth identity unknown | Unknown | ClearF masks `0x30` and `0x0F` or `0x3F`; emitter clips and iterates selected MRTs | None shown | Clear emitter; a sibling end call follows the setup return only under a condition | Unknown | candidate |
| alternate-tiling-arm | `0x82C71880` sibling-calls `0x8269DB20` at `0x82C71944` after setup returns; replay and state cleanup through `0x8269CD20` and `0x8269C888` | Unknown | Unknown | Unknown | No direct ClearF callsite in the selected helper | None shown | Replay and device state helpers | Unknown | candidate |
| renderer-table-pass | BeginTiling callsite `0x8250FA44` under `[r20+4] > 1`, then command-span sites and dynamic callbacks | Pointer from renderer `+0xBC`; target identity unknown | Unknown | Unknown | No direct ClearF callsite | None in this method | Receiver `+0x14C`; current `+0x550` group for `+0x48` and `+0x4C`; F0265 handoff that holds only under a condition, F60 `+0x60` and `+0x58` attachments. Incoming equality across helpers and draw, state and resource consumers unknown | BeginTiling has `r4=1`, `r6=r20+8`, `r7=0`, `r9=0`; meaning unresolved | strong |
| group-bracket | When `[r26+4] > 1`, tile predicate at `0x8250AD54`; under provider guards, depth Resolve `0x8250AE20` precedes indexed-color Resolve `0x8250AFEC`, then predication clears | Current group from renderer `+0x550`; indexed color uses `+0x3098 + 4*index`; concrete target unknown | Depth index `4` selects `+0x30A8`; concrete depth identity unknown | Unknown | Predication is resolve state, not a proved color clear | r6 at `0x8250AFB8` is selected provider output; `+0x90` and `+0x94` of `0x82517860` remain dependent on vptr `0x8204767C` | Exact provider and same-frame consumer unresolved | Per-tile predicate under the group-count and provider guards | strong |
| group-bracket | Local Resolve callsites -> `0x8250B070 -> 0x8269D320`; EndTiling then reaches replay `0x826AC218` | Restores bound fields `+0x3098` through `+0x30A8`; surfaces unknown | The depth setting is in the restored range; identity unknown | Unknown | Integer r4,r5,r6,r7,r9,r10 are zero; r8 is not yet shown; f1 is separate | Null r5/r6 skip EndTiling's internal Resolve loop in the static body | Replay and restored target state | Predication cleared before call | strong |
| alternate-tiling-arm | Clear implementation edge `0x8269D7D8 -> 0x826A2970` at `0x8269D9D8` and `0x8269DA24`; `0x826A2970 -> 0x826A22F8` at `0x826A2A80` | Bound RT0 or selected MRT slots; surface unknown | Bound depth `+0x30A8` for default extents; surface unknown | Unknown | ABI is device, mask, optional rectangle, float4 color, depth, stencil; emitter clips the viewport and scissor and iterates selected MRTs | None | Lower clear commands that belong to the device | Outer-pass tiling membership unknown | strong |
| presentation | The worker calls flush wrapper `0x826A4630` at `0x826ABF80`, then sibling-calls the VdSwap function `0x826A4638` at `0x826ABF90`; alternate caller uses `0x82517E58` then `0x82517E88`; wrapper tails to `0x826A4150` | Presentation descriptor, whose identity depends on its correlation with the earlier Resolve | Not applicable | Not applicable | None | Earlier Resolve may match the first VdSwap epoch; same-frame pairing unresolved | VdSwap import `0x82E92454` at `0x826A4884` | Not applicable | strong |

`RVA-F-0262` orders sibling `+0x15C` before first `+0x160`, with a second
`+0x160` later. No shadow, terrain, water, fog, unit, effect, label or UI pass,
fixed EDRAM base, complete tiled MRT set, cadence, Resolve completion or output
is established. Worker `0x826ABEA8` and alternate `0x82517E38` are presentation
boundaries, not shown to be frame roots.

The remaining open links separate the incoming provider `+0x74` and `+0x78`,
the current `+0x550` consumers and the fields `+0x3098` through `+0x30A8`.
Execution, whether pointers stay valid, surfaces and total order are not yet
shown.

## Names and flow in plain terms

Names used on this page: `F` is the frame object pointer saved in `r31` by frame function `0x82C71A00`, `Rr` the
global renderer, `G` the incoming group, `B` the separate fallback storage
object, and `C` the context loaded from `Rr+0x564`. They name roles, not
established types or instances. Byte `F+0xA0` and byte `Rr+0xA0` use different
tests.

The flow below applies step by step, and each step happens only if the one before it did:

1. `F` picks `+0xAC` or `+0xB0`, then calls the `+0x15C` function of `Rr`
   directly (when `F+0x98` is nonzero) or through `0x821D6D10`.
2. `0x8250F988` asks `G` for its provider at virtual `+0x74`. A nonnull answer
   is used. A null answer goes to the fallback `0x82520958`, which asks `G`
   again at virtual `+0x60` (`0x825209A0`) and stores the returned word in `B+0xF8`.
3. Only a nonnull provider and a nonzero low byte from `0x82520478` let
   `0x8250F9D0` store `G` at `Rr+0x550`. The store publishes `G`, not `B`.
4. `0x82516F60` and the callbacks at group `+0x48` and `+0x4C` reload `Rr+0x550`.
   Each reload needs the pointer to stay valid.
5. A separate `+0x160` path (`0x8250AC90`) runs a depth Resolve before the
   indexed color Resolve, with resource details in
   [resolve resources](native-renderer-resolve-resources.md).

The fallback result is the last known edge: the target of group virtual `+0x60`
is not known, so neither the fallback result nor the group's target and depth
can be named. Which of these edges run in a real frame is not covered by
this page. No shadow, terrain, water, fog, unit, effect, label or interface
pass is named here.
