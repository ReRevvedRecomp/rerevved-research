# Native renderer frame passes

The
[frame-pass manifest](../../manifests/native-renderer-frame-pass.json)
groups static fragments, not execution counts or total frame order. Alternate
setup/end share guarded `0x82C71880`. Callback `0x82E87D18` reaches
`0x82C7DF58`: service `bctrl` at `0x82C7E0F8` returns `0x82C7E0FC` before
`0x82C7E104 -> 0x82C71A00`, requiring nonzero incoming r4 low byte.

`RVA-F-0262` joins `0x8250F988`/`0x8250AC90` only if the global retains the
`0x8250F0E8` object, vptr `0x82047050`, and dispatch predicates pass. Reset
stores/historical captures prove neither current retention nor unique type.

[Group binding](../../manifests/native-renderer-frame-group-binding.json)
(`RVA-F-0265`), nonzero `+0x98` arm:

1. Byte `+0xA0` selects `+0xAC`/`+0xB0`; zero-initialized assignment
   passes it as r4 to `0x821D6DD0`.
2. `0x8250F988` can store it at `+0x550` after incoming `+0x74`/`+0x78`
   provider work and `0x82520478` low-byte guard.
3. F988 reloads `+0x550` at `0x8250FA0C`, passes r4 to F60 at
   `0x8250FA14`; F60 reads `+0x60`/`+0x58`. Later callbacks reload
   current group and read `+0x48`/`+0x4C`. Equality with original group
   requires retention, valid storage, nonaliasing and vptr conditions.

On the null incoming `+0x74` arm, the
[fallback contract](../../manifests/native-renderer-frame-group-binding.json#/currentEvidence/fallbackProviderBoundary)
binds `0x82520958` to a 276-byte storage request initialized by `0x825200D0`.
Its successful local suffix returns that saved object. The first unresolved
provider is incoming group `+0x60` at `0x825209A0`, stored to object `+0xF8`.
Renderer `+0x550` still receives the incoming group. Allocation extent,
current storage/vptr, helper returns and target/depth identity remain unproved.

Wrapper D10 `+0x74` supplies a separate group; target/depth remain unknown. The
[Resolve discriminator](../../manifests/native-renderer-resolve-destination-lifecycle.json#/decisiveObservation/observationCoverage)
requires pre-`0x8250AFEC` item/provider-to-r6 linkage paired with same-call
color/depth descriptor and EDRAM row, current run/image identity and successful
reads. Native EDRAM diagnostics and Xenos descriptor events supply neither join;
capped omissions are inconclusive. Even closure leaves F0265 incoming-group
`+0x74/+0x78` identity open.

| Fragment | Local static edge | Target | Depth | EDRAM base | Clear | Resolve destination | Consumers | Predicated tiling | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| callback-tiling | `0x82E87D18 -> 0x82C7DF58 -> 0x82C71A00`; three static helper callsites to `0x82C71880` at `0x82C71CB8`, `0x82C71E1C`, and `0x82C71E58` | Unknown | Unknown | Unknown | Delegated to the alternate-tiling arm | None proved | Conditional `0x8250F988`/`0x8250AC90` relations/predicates/order in `RVA-F-0262`; others unknown | Unknown | strong |
| alternate-tiling-arm | `0x82C71880 -> 0x8269D7D8 -> 0x826A2970 -> 0x826A22F8`; after setup returns, the same helper sibling-calls `0x8269DB20` at `0x82C71944`; setup/end arm requires global bit `0x8`, nonnull global pointer, receiver byte `+0xA3` nonzero, and middleware `+8` zero | Bound target identity unknown | Bound depth identity unknown | Unknown | ClearF masks `0x30` and `0x0F` or `0x3F`; emitter clips and iterates selected MRTs | None proved | Clear emitter; conditional sibling end call follows setup return | Unknown | candidate |
| alternate-tiling-arm | `0x82C71880` sibling-calls `0x8269DB20` at `0x82C71944` after setup returns; replay and state cleanup through `0x8269CD20` and `0x8269C888` | Unknown | Unknown | Unknown | No direct ClearF callsite in the bounded helper | None proved | Replay and device state helpers | Unknown | candidate |
| renderer-table-pass | BeginTiling callsite `0x8250FA44` under `[r20+4] > 1`, then command-span sites and dynamic callbacks | Pointer from renderer `+0xBC`; target identity unknown | Unknown | Unknown | No direct ClearF callsite | None in this method | Receiver `+0x14C`; current `+0x550` group for `+0x48`/`+0x4C`; conditional F0265 handoff, F60 `+0x60`/`+0x58` attachments. Incoming equality across helpers and draw/state/resource consumers unknown | BeginTiling has `r4=1`, `r6=r20+8`, `r7=0`, `r9=0`; meaning unresolved | strong |
| group-bracket | When `[r26+4] > 1`, tile predicate at `0x8250AD54`; under provider guards, depth Resolve `0x8250AE20` precedes indexed-color Resolve `0x8250AFEC`, then predication clears | Current group from renderer `+0x550`; indexed color uses `+0x3098 + 4*index`; concrete target unknown | Depth index `4` selects `+0x30A8`; concrete depth identity unknown | Unknown | Predication is resolve state, not a proved color clear | r6 at `0x8250AFB8` is selected provider output; `0x82517860` `+0x90/+0x94` remains conditional on vptr `0x8204767C` | Exact provider and same-frame consumer unresolved | Per-tile predicate under the group-count and provider guards | strong |
| group-bracket | Local Resolve callsites -> `0x8250B070 -> 0x8269D320`; EndTiling then reaches replay `0x826AC218` | Restores bound fields `+0x3098` through `+0x30A8`; surfaces unknown | Depth binding is in restored range; identity unknown | Unknown | Integer r4,r5,r6,r7,r9,r10 are zero; r8 is unproved; f1 is separate | Null r5/r6 skip EndTiling's internal Resolve loop in the static body | Replay and restored target state | Predication cleared before call | strong |
| alternate-tiling-arm | Clear implementation edge `0x8269D7D8 -> 0x826A2970` at `0x8269D9D8` and `0x8269DA24`; `0x826A2970 -> 0x826A22F8` at `0x826A2A80` | Bound RT0 or selected MRT slots; surface unknown | Bound depth `+0x30A8` for default extents; surface unknown | Unknown | ABI is device, mask, optional rectangle, float4 color, depth, stencil; emitter clips viewport/scissor and iterates selected MRTs | None | Device-owned lower clear commands | Outer-pass tiling membership unknown | strong |
| presentation | Ordinary worker calls flush wrapper `0x826A4630` at `0x826ABF80`, then sibling-calls owner `0x826A4638` at `0x826ABF90`; alternate caller uses `0x82517E58` then `0x82517E88`; wrapper tails to `0x826A4150` | Presentation descriptor conditional on earlier Resolve correlation | Not applicable | Not applicable | None | Earlier Resolve may match the first VdSwap epoch; same-frame pairing unresolved | VdSwap import `0x82E92454` at `0x826A4884` | Not applicable | strong |

`RVA-F-0262` orders sibling `+0x15C` before first `+0x160`, with a second
`+0x160` later. No shadow/terrain/water/fog/unit/effect/label/UI pass, fixed
EDRAM base, complete tiled MRT set, cadence, Resolve completion or output is
established. Worker `0x826ABEA8`/alternate `0x82517E38` are presentation
boundaries, not proved frame roots.

Remaining joins distinguish incoming provider `+0x74`/`+0x78`, current `+0x550`
consumers and bindings `+0x3098` through `+0x30A8`: execution, pointer
retention, surfaces and total order remain unproved.

## Names and flow in plain terms

Names used on this page: `F` is the frame object pointer saved in `r31` by frame function `0x82C71A00`, `Rr` the
global renderer, `G` the incoming group, `B` the separate fallback storage
object, and `C` the context loaded from `Rr+0x564`. They name roles, not
proved types or instances. Byte `F+0xA0` and byte `Rr+0xA0` use different
tests.

The flow, with each step conditional on the one before:

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
