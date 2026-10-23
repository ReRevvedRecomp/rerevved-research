# Resource identity overrides without terrain stores

Oak/Oxen/Fish same-terrain overrides have conditional hooks/fresh-model routes.
Oak also changes Forest child flags; retained terrain does not ensure identical
drawing. Title freezes Resources before setup, allowing pending Balanced to
control India, but publishes tiles at recount after native object attempts.

The
[override boundary](../../manifests/resource-identity-override-boundary.json)
owns static read sets/calls/confidence/limits;
[definitions](resource-definitions.md) owns IDs/access,
[tile changes](resource-placement.md#post-setup-tile-changes)
snapshot/topology/refresh. Reported terrain-swap drawing is separate runtime
context; mixed-identity report has no captured trace-build/ordered-consumer
proof.

| Question | Verdict | Confidence |
|---|---|---|
| Every identity consumer shares one helper | Conditional: 20 direct calls enumerated; no inline duplicate proved in the selected definition-base inventory; subsystem completeness remains open. | Strong |
| A fresh object follows the overridden type | Proved type/name request; conditional allocation, model fulfillment and retention. Existing objects are not automatically replaced. | Strong |
| An unused, persisted native tile field can hold the override | Conditional: full flag transfer is supported, but no field is certified unused and retained through load. | Strong |
| Forest terrain plus Oak preserves identical trees | Disproved for unchanged child state; visible appearance remains conditional. | Strong |
| Recount-only policy can control India and wholesale removal preserves RNG | Disproved. Current source freezes Resources earlier; a narrow store/callback skip retains the explicit draw. | Confirmed static order; source implementation qualified |

## Identity consumers

Complete aligned direct-branch census found 20 `0x82CF1558` calls and no
additional non-link branch. Manifest lists owners/contexts/uses:

| Surface | Static route and limit |
|---|---|
| Food, production, trade | `0x82CF1CE8`, `0x82CF1AF0`, `0x82CF17C8` call the helper at `0x82CF1F0C`, `0x82CF1CAC`, `0x82CF1A44`. Contribution helpers `0x82CF1698` and `0x82CF1730` also call it. |
| City candidates and work tiles | `0x82D016D8`, `0x82D13EA0`, `0x82D14358` use the helper. The latter two OR `1<<q` into a city resource word. Previously computed credits and screen refresh remain separate. |
| Tile tooltip/resource detail | `0x82DECEB8` obtains intrinsic type, `0x82DECEE8` checks player availability, then `0x82DECF30` forwards type and coordinates to `0x82DEAB38`. `0x82DE01DC` also checks selected-tile availability. |
| Resource visual | `0x82D7D974` reads intrinsic type and forwards it through receiver `+0x248`. `0x82E53F34` and `0x82E544AC` use the same helper for eligibility/availability. |
| Candidate valuation | `0x82D027E8` reads intrinsic type; `0x82D027F4..0x82D0283C` uses its definition contribution/technology. This and city scoring do not enumerate every strategic AI consumer. |
| Trade and monopoly aggregation | Trade yield and city type-presence bitsets share the helper. A whole-game monopoly/count owner is not established; a bitset is not an occurrence count. |
| India UEA39 | The same helper performs technology query at `0x82CF1638`, UEA39 at `0x82CF1650`, then civ-10 fallback. These accept the selected type; they do not derive a different one. |
| Minimap | No minimap owner is joined to this inventory. An empty defined-string search does not prove absence or common-helper coverage. |
| Save/load | The selected plane serializer transfers terrain and flags. It does not store a separate override ID in those planes or classify their resource type. Saved aggregates and reconstruction remain separate. |

Manifest retains other notification/location/founding/count calls. Among 12
exact-base sites in ten owners, only `0x82CF1558` maps terrain/remainder to row.
`0x82CEA16C..0x82CEA1A8`/`0x82CF0630` compute existing-ordinal contributions,
not duplicate hooks. Longer aliases, other bases, dispatch and independent
formulas remain outside that negative.

## Mixed identity observation

The
[runtime qualification](../../manifests/resource-identity-override-boundary.json#/runtimeEvidence/mixedIdentityObservation)
records Balanced Oxen on native Cattle-remainder Grassland: it behaved as Oxen
while Romans/Code of Laws also received Cattle food. Universal identity
agreement remains open despite the direct census. Trace must distinguish stale
bits/credits, independent formula, bypass or hook/context/order error; cause is
unknown. Legendary retains this gate; presence-only Abundant can keep native
identity.

## Override and fresh visual creation

Unconditional `0x82CF1558` return would bypass presence/forbidden/player gates.
Retain them and valid Oxen `0`; only `-1` means absence. Pre-instruction midasm
`0x82CF15C4` has `r11`=physical `i`, `r8`=sum, `r7`=terrain. For matching
terrain, replace only full `r8` with chosen remainder:

| Current terrain | Chosen ordinal | Synthetic sum |
|---|---:|---:|
| Forest `3` | Oak `9` | `1` |
| Grassland `1` | Oxen `0` | `0` |
| Sea `0` | Fish `18` | `2` |

Divide `0x82CF15E4..0x82CF15FC` feeds ordinary row matching, then technology/
UEA39/civ-10 gates. Unique pairs prevent a rejected choice selecting another
matching row. Earlier overflow trap retains original sum; canonical `0..31`
excludes its exceptional case. Hook emission/runtime, input stability and other
state preservation remain required.

| Fresh visual edge | Contract |
| --- | --- |
| `0x82D7D974`, `0x82D7D97C` | Return `q`, copy to `r6`, dispatch `+0x248` -> initialized `0x82D7FCB0` |
| Empty query `0x82D7FD44` | Calls `0x82E54250(a,b,q)`; stores `+0x70/+0x74` coordinates and `+0x78` type |
| `0x82D7FD58..0x82D7FD68` | Name from `0x82F6FAD0+68*q`; `0x82D7FD84` dispatches `+0x14`, installed cell `0x82132ACC` -> `0x82E544E8` |
| Setter | Prepares name, stores `+0x10`, calls `0x82C63320` at `0x82E545D4`, then lookup `0x82C92950` at `0x82C63364`/`0x82C633D4`; later special placement reads stored `q` |

Chosen type/name requests model identity; allocation, fulfillment, registration,
lifetime and appearance remain conditional. Nonempty `0x82D7FD18` ->
`0x82D7FE2C` neither compares nor changes old type/name. Repeating `+0xF4` does
not replace; changing only `+0x78` leaves inconsistency. Prove rebind/
replacement. Setup `+0xF4` at `0x82D2332C`/`0x82D2455C`/`0x82D24768` precedes
recount `0x82D2530C -> 0x82D11AD8`, LR `0x82D25310`; recount is too late, while
merely earlier timing proves neither empty query nor final writers.

## Persistence

No native tile storage is certified unused; this does not prove impossibility.
Default save `0x822DE7A0` visits 1600 halfwords via `0x822E1338`, writing two
bytes through `+8` at `0x822E1400`. Load `0x822DE720` visits 1600 via
`0x822DEC88`, reading two at `0x822DECB8` with conditional swap. No mask: all 16
bits transfer under matched stream/order/completion guards. Later writes can
erase them: recount `0x82D11BD4..0x82D11BF0` applies `0xF4FB`, clearing
`0x0B04`. Known masks `0x1001`, `0x20`, `0x411`, `0x1000` and incomplete
alias/reader/writer census certify no spare bit/plane/ padding. Alternate
streams/reconstruction remain separate.

Sufficient sidecar: schema, frozen policy, rule/config identity, sorted unique
`(tileIndex U16, ordinal U8)`; three records use nine payload bytes before
header/save identity. Fixed Oak/Oxen/Fish roles could use three U16 indices plus
absence encoding, not a proved native format/minimum. Multiple starts need
conflict handling.

[Save seams](save-storage.md): selected user/device namespace and normalized
`+0x108` filename; before `bctrl 0x82D844C8` (return `0x82D844CC`), after final
`0x82D829E8` with `r25!=0`. Bind native digest/equivalent generation identity;
atomic post-success replacement detects inter-file crash via digest. Restore
before identity/model consumers; failure/mismatch/missing, autosave and rollback
need contracts. Reset `0x82D86674` must not later erase it.

Inspected revision `789e0b7fcc8f29c76fac2af1b93e959953a79cf4` implements
sidecars; `persistence/existingTitleState` pins hashes/locators, not every
checkout/running binary. Load captures filename/stages validated digest-bound
payload before `0x82D844C8`; pre-BL `0x82D86674` clears old then publishes
staged snapshot before other settings/native continuation. Missing/rejected
sidecars log fallback with no restored overrides. Pending state is
transaction-local; native loads have no rollback.

Save `r25!=0` at `0x82D829E8` permits write/flush/atomic replace; failure logs
without native-save rollback. Distinct autosaves remain uncertified.
[Selected load order](resource-placement.md#load-ordering) joins publication to
default planes/two later sweeps, not earlier header/dispatch, alternate routes
or all caches. Universal pre-reader restoration/visible reload remain unproved.

## Forest and Oak

Terrain `3` retains Forest/snapshot; presence `0x20` leaves final `W&0x411`
branch unchanged, but Oak setter is separate. `0x82E544E8` routes IDs `5`/`9` to
`0x82E54C14`; `0x82E54C30` dispatches `+0x11C` with coordinates, mask `7`,
Boolean `0`. Matching first child gives
`0x82D7ED00 -> 0x82E3DC80 -> 0x82E3D7D0`; retained type-3 model resolves slots
0/1/2 and calls `0x8234BDB8(child,1,1)`, ORing `1` into scene `+0xA8` with a
recursive path.

Final `0x82D64B18` separately queries Forest via `+0x120`, updates matches via
`+0x118`/object `+0x48`. Live bindings and completing callbacks remain required.
Oak can change existing scene state despite unchanged terrain; identical trees
need visual comparison, and bypassing child work is another policy.

## India order and suppression

Setup `0x82D25254` includes civ-10 before recount `0x82D2530C / LR 0x82D25310`.
Title freezes/stages Resources before native setup, consults pending Balanced at
store hook, publishes tiles later. Publication alone cannot repair earlier
object identity.

Whole-arm removal changes RNG: counter `0x82D2328C`, state `0x82D2329C`,
possible reduced state `0x82D232B4`. Pre-`0x82D23324` jump to `0x82D23330` ->
count reload `0x82D23938` skips store/refresh `0x82D2332C`, retaining
draw/offset. Call-only skip leaves presence; store-only skip still refreshes.
`r3` is unused before merge, needing no invented success.

This proves local flow, not omitted callback writes/transitive RNG/full-setup
equivalence. Preserve player/coordinates/count/frame/save state and validate
hook plus earlier frozen host/peer policy.

## Title implementer contract

1. Freeze policy before `0x82D25254`; normalize/deduplicate ring candidates
   using the accepted 32x32 topology and stride 40. Define finite behavior
   when a resource kind is missing or starts overlap.
2. Keep terrain bytes unchanged. Publish same-terrain overrides before first
   visual creation; candidate hook `0x82CF15C4` preserves native identity gates.
   Validate all affected consumers and retain valid ordinal `0`.
3. Close fresh-object completion or replacement of existing objects, and
   decide
   whether native Oak child changes meet the desired Forest appearance.
4. Persist frozen choices in a versioned sidecar tied to the save slot and
   digest until a native field is proved available. Cover load failure,
   autosaves and peers.
5. Retain India's native draw, then conditionally skip `0x82D23324..2332C` to
   `0x82D23330`. Preserve the earlier policy freeze; recount-only resolution
   cannot control that arm.
6. Keep minimap, strategic AI, monopoly counts, actual model retention,
   unchanged terrain bytes and visible output, save/reload and peer agreement
   as open acceptance gates.
