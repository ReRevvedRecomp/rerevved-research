# Resource density and placement

Presence writers include terrain conversion, two record-coordinate operations
and a setup arm beside an initial Settler request. Conversion uses fixed `4.0`
with mutable RNG/normalization. Scenario `RESOURCEDENSITY` has no proved
connection; `3` does not establish increased resources.

Evidence terms: these are static, conditional contracts. Selected paths do not
prove actual inputs, completed setup or runtime effects; claim-specific return,
ownership and alias guards remain explicit.

- [Density boundary](../../manifests/resource-density-generation-boundary.json): setting/search limits.
- [Writer boundary](../../manifests/resource-density-generation-boundary.json#/placementWriterBoundary): locators and retention.
- [Scenario schema](../../manifests/scenario-schema-boundary.json): parsing.
- [Resource definitions](resource-definitions.md): 22 ordinals/technologies, including Oxen `0`, Iron `1`.
- [Presence/identity](#presence-identity-and-the-selected-writer), [tile changes](#post-setup-tile-changes),
  [Abundant/Legendary](#abundant-and-legendary-feasibility), [setup probe](#paired-new-game-setup-probe-contract).

## Stored setting

Signed16 slot 3 is scenario `+0x6`, default `2`. Apply owner `0x82DAEFD8` writes
`2` to active `0x830E8FD6`; matched custom records copy all 16 bits without
density-specific range checking, conditional on returns, valid records and
retention.

| Value | Established meaning |
|---|---|
| `2` | Record/local setup default |
| Other signed16 values | Storage/copy only; gameplay effects/support unknown |

No value maps to Sparse, Abundant, Legendary Start or Strategic Balance. Closed
bounded negative searches do not prove the field unused.

## Presence, identity and the selected writer

`0x82CF1558` requires presence `0x20`, clear `0x1001`, then matches
terrain/coordinate remainder against 22 definitions; player/context gates are
separate. No per-tile ID plane is read. Definitions map identity; Iron's case
follows below.

Five stores in `0x82D0F0D0` convert old terrain `2`/`5` to `1`/`3` and
conditionally OR `0x20`. Positive visitation count `2..8` and a second RNG
draw's low-word floating-conversion test using `4.0` are required. `0x82D0FC50`
loads saved RNG pointer +`16`. Valid disjoint frames, retained inputs, bounded
indices and normal helpers retain pointer `0x82F7AD00` and `+16`, thus reading
`0x82F7AD10`. Earlier RNG work reads that field, writing only record
state/counter.

The
[count boundary](../../manifests/resource-density-generation-boundary.json#/placementWriterBoundary/componentCountBoundary)
binds label traversal: each visited cell increments its class once; outer-seed
terrain zero negates the count afterward, otherwise retains positive.
Eligibility 2 through 8 is neither requested count nor map quota. Traversal can
clear `7` to `0` while retaining cached terrain sign; later reads see changes.
This visitation snapshot is not generally current/immutable component size;
eight displacement pairs lack decoded geometry.

Producer-to-reader retention requires valid dimensions, disjoint planes/frames,
bounded intermediate indices and finite helpers. Loaded bits stay in f31 through
six copy sites to presence on such a continuation. Earlier value/initializer
remain unknown: neither quarter-probability nor tuning knob is proved.

Copy preserves RNG/floating registers, writing destination and eight-byte
below-stack save slot; valid disjoint ranges and saved-pointer retention must
protect RNG/frame. Stores preserve old flags but do not guarantee valid ordinal.
Named-map success bypasses conversion. Later effects/return/retention and
completed-map runtime behavior remain unproved.

## Other presence writers

[Record-coordinate writers](../../manifests/resource-density-generation-boundary.json#/placementWriterBoundary/recordPresenceWriterBoundary)
lie outside terrain `2`/`5` conversion:

| Owner/store | Guard |
| --- | --- |
| `0x82D1AC70` / `0x82D1AE04` | Signed record coordinates, incoming mask and selector equality; OR `0x20`, no local terrain/RNG/count test |
| `0x82D1B400` / `0x82D1C40C` | Old `0x1` clear after required helper return/input retention |

Record domain/caller inputs remain unknown. The
[callback boundary](../../manifests/resource-density-generation-boundary.json#/placementWriterBoundary/recordPresenceWriterBoundary/callbackRetentionBoundary)
binds initialized `+0xF4` to `0x82D7D950`: context `-1` resource read,
initialized `+0x248` -> `0x82D7FCB0`, then `0x82D64B18`. Reader finitely returns
`-1` or `0` through `21`. Lookup `-1`, nested flags selecting no call, and final
terrain !=`3` give finite return retaining flag/coordinates/ inputs under
valid-memory/disjoint-frame guards; writes remain in callback frames. Positive
results, other flag work and terrain `3` need further contracts.

For nonnegative results, `0x821C6C28` finitely copies descriptor `+4` to `+8` if
different, preserving `+0`/`+4` under frame exclusions. `0x821D6340` has finite
bounds-fail, empty and all-zero-payload paths, retaining reset/caller state
under frame/alias guards. Nonzero payload reaches
[chain predicate](../../manifests/resource-density-generation-boundary.json#/placementWriterBoundary/recordPresenceWriterBoundary/callbackRetentionBoundary/nonnegativeHelperBoundary/nonzeroPayloadPredicateBoundary)
`0x821B2D90`, dispatching current payload vtable `+0` at `0x821B2DB0`. After
return it follows `+4` links: `1` for retained `0x8314F67C`, `0` for null.
Current target, finite chain and retained registers/frames/domain words remain
required; nonmatching cycles have no progress bound. True selects `0x822E55F0`,
whose capacity fast path is below; growth remains conditional. Query result is
neither placement count nor success Boolean, and precedes more work.

The
[payload case](../../manifests/resource-density-generation-boundary.json#/placementWriterBoundary/recordPresenceWriterBoundary/callbackRetentionBoundary/nonnegativeHelperBoundary/nonzeroPayloadPredicateBoundary/payloadSlot0Boundary)
binds constructor `0x82E54250` storing `0x82132AB8` in captured receiver;
initialized slot `+0` = `0x821CC860`. Same live queried receiver plus retained
vptr/cell selects this getter at `0x821B2DB0`. Three instructions return full64
`0xFFFFFFFF8314F67C`, changing only `r3`/`r11`, without memory/stack access and
retaining `r31`. Low-word comparison returns `1` without chain read (including
`K+4`) or initialized `K`; wrapper stack/load/return guards remain.

Constructor later passes preceding base-call result to `0x82C5FC40`, not a
proved constructor-receiver copy. It calls `0x82D3DBA0` with `60`, may
initialize 60 bytes and dispatch old child `+4`. Returns/writes/lifetime remain
unknown. Full write sets must miss original vptr; unequal pointers are
insufficient. Actual query payload/order/lifetime is unjoined: this is no
universal target or completed positive refresh.

`+0xF4` is sampled before the flag store; arbitrary signed coordinates can alias
receiver's first word without changing cached target. Bounds, vptr order and
nonaliasing remain required; no actual invocation/full completion is proved.

## Initial Settler coordinates

The
[start boundary](../../manifests/resource-density-generation-boundary.json#/initialSettlerSpawnBoundary)
binds `Y[p]` at `0x830E343C+4*p`, `X[p]` at `0x830E345C+4*p`. Reached player `p`
loads X/Y at `0x82D231B4`/`0x82D231B8`; `0x82D23258` conditionally requests
`0x82D11750(p,0,X[p],Y[p])` (`0` = Settlers). No display-axis orientation
follows. Sampled barbarian is excluded; session/flag/definition gates can choose
a city instead. Local guards do not distinguish human/AI.

Selector `0x82D02C58` writes arrays. Encoded nonzero `k` gives `X=trunc(k/100)`,
`Y=k-100*trunc(k/100)` without terrain/bounds validation. Procedural selection
samples/filters/spaces candidates, calling `0x82CFFD08` mode `0` before stores
and `1` after. The
[helper contract](../../manifests/resource-density-generation-boundary.json#/initialSettlerSpawnBoundary/candidateHelperBoundary)
still requires actual RNG inputs, bounded indices and finite production;
selector table is no proved permutation.

Eight sampled bytes: `z` counts `0`, `h` counts `1`, `d` counts `3`, `p` counts
`2`/`5`. Predicate `z>=2` and `p>=max(2-h,0)+max(2-d,0)` finitely returns
`0`/`1` in mode `0` under read/arithmetic/save guards. Mode `1` rejects with
`0`; accepted inputs can select pool bits/write `1`/`3`, returning `1` without
draws if both counts >=`2`. Repair rejection loops have no retry cap; selector/
progress remain unknown. Raw classes prove no resource/food/forest/water
guarantee. Reads normalize one coordinate but writes do not;
sampled/written-cell identity needs proof.

Both modes retain full64 `r4`; native suffixes restore saved registers if bytes
survive. Stack saves always occur; mode `1` also writes conversion scratch, RNG
state/counter and computed classes. Caller reloads updated RNG state/counter;
modulus, normalization, coordinates, selector and frame/save bytes need
protection beyond scalar return.

Before setup reads, `0x82D230E0` -> `0x82CFE908` can swap coordinate pairs
between slots, changing producer-to-player mapping. Sampled object `2` bypasses;
identity/order and reorder fill/frame/bounds/return remain guarded.

Loaded coordinates precede child `+0x100`. Matching registered getter preserves
player/coordinates, but current child/target/result, lifetime and unchecked
`result+0xC` validity remain required. Creator callbacks, loop tail, production/
ordering and unit-coordinate retention are unresolved; a request is not
placement, and the founding marker is not a substitute spawn anchor.

## After the player-request loop

The
[post-request boundary](../../manifests/resource-density-generation-boundary.json#/initialSettlerSpawnBoundary/postSpawnPlacementBoundary)
identifies a conditional insertion candidate:

| Site | Contract |
| --- | --- |
| `0x82D239E4`, `0x82D239EC` | Increment player, compare current signed count, loop while smaller |
| `0x82D239F0` | Normal fallthrough |
| `0x82D239F4` | Initial nonpositive-count bypass skips preceding reload |
| `0x82D2393C` | Unit-request merge after player-table miss or presence refresh; before child `+0x100`, unchecked `result+0xC`, coordinate/global stores and increment |
| `0x82D23810` | Excluded-player branch outside coverage |
| Beyond `0x82D234C0` | City arm changes count-pointer register; restoration/join unbound |

Getter preservation needs current binding/result/read guards; creation success
is unchecked. Fixed valid count and finite retained iterations visit its range,
but neither every arm's return nor successful Settlers follows. A future pass
could use retained spawn arrays across players independently of the native
player-table gate; final iteration registers do not represent all units.
New-game-only ingress, successful spawns, remaining joins and later
table/session effects remain unknown. Final retention and usable placement hook
are unproved.

## Creator return and retention

The
[creator contract](../../manifests/resource-density-generation-boundary.json#/initialSettlerSpawnBoundary/creatorReturnBoundary)
separates request, initialization and success. Retained type0 flags admit a scan
of at most 256 player slots, selecting first owner/`+7` both `0xFF`. Exhaustion
finitely returns `-1` without unit writes under memory/return guards; setup can
continue because it ignores result.

Selected record clear is exactly 84 bytes (five 16-byte blocks plus four),
requiring four-byte alignment even for odd slots. Leaf returns input pointer,
preserving outside bytes. Creator writes owner/type0/slot/initializers;
`+0x1C`/`+0x1E` receive only low16 coordinates.

Type0 flags `1` bypass movement UEA calls. Nonzero current human mask and
bounded valid player give finite classifier return without descendants; movement
times three truncates to unit `+2`. Zero-mask path remains unbound. Native proof
excludes generated host insertion and establishes no runtime parity.

Mandatory `+0x1A0` call `0x82D11980` selects initialized `0x82D7FE40` under
retained vptr; return/writes/lifetime/creator/setup retention remain open. Later
`+0x1B4` selects no-op `0x821D5678` only if freshly sampled vptr still matches.
Session lookup and retained flags gate the tail.

With all callback/register/frame/save/unit guards, tail returns `0..255`; `0` is
success, but an initialized index proves neither registration nor lifetime.
Save/restore conditionally retains setup registers; `f29`, count, frame/source
bytes need every callback's contract. Successful creation and Iron refresh
remain separate gates.

## India's adjacent grant and an Iron case

The
[spawn-relative case](../../manifests/resource-density-generation-boundary.json#/initialSettlerSpawnBoundary/ironPlacementCaseBoundary)
follows `0x82D23258` when civilization `0x830ECD28+4*p` equals `10`, identified
as `Indian` by
[row 10](../../manifests/civilization-bonus-storage.json#/storage/rows/10).
Creator result is unchecked; normal failure can still reach the writer under
frame/register/input retention. Presence proves no successful Settler.

RNG conversion scale `8.0` selects an offset. Retained table and index `0..7`
yield `(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)`. After
adding to spawn coordinates, `0x82D23324` ORs `0x20`, then `0x82D2332C` calls
cached `+0xF4`. No local terrain/bounds/forbidden/Iron test exists.
Normalization/index bounds, geometry/legal placement and full64 callback
interpretation remain required; negative offsets mean low-word minus one. Scale
proves no probability.

This selects a tile, not ID; terrain/remainder determine identity, and OR may
leave an existing resource unchanged. India's availability fallback follows
technology/UEA39 calls and does not place resources; see the
[reader boundary](../../manifests/resource-definitions.json#/readerBoundary).

Conditional Iron case: index `0`, `(a,b)=(X[p],Y[p]+1)`, `0<=X[p]<=39`,
`0<=Y[p]<=38`, clear `0x1001`, retained Hill `4`, `(X[p]+Y[p]+1) mod 3 == 0`.
Valid disjoint memory/frames, retained definitions and same physical tile give
read-back ordinal `1` in context `-1`. These are symbolic inputs, not observed
spawn/RNG; no conversion or Iron search occurs.

Installed target/retention admits nonnegative refresh, whose complete return and
flag/terrain survival remain unproved. The finite result-`-1` case cannot prove
Iron retention. End-to-end placement needs creator success, retained setup
inputs, actual admitted candidate and completed positive refresh.

## Iron and the founding-city boundary

The
[Iron/capital case](../../manifests/resource-density-generation-boundary.json#/ironCapitalCaseBoundary)
binds ordinal `1`, record `0x82F6FB14`, name/token `Iron`. In domain `0..39` per
coordinate, context `-1` returns it exactly for presence, clear `0x1001`, Hill
`4`, and signed sum remainder zero modulo `3`, under memory/retention guards.
Domain proves neither dimensions nor legality; ordinary players need
availability gates. Presence cannot force Iron anywhere; conversion produces
`1`/`3`, not `4`.

Founding `0x82D18D88` conditionally marks a palace city and stores coordinates.
`0x82D1A11C` reads that center; retained nonbarbarian player and result !=`-1`
permit `0x82D1A148` clearing presence before rewards. This consumes center
resource, not nearby placement. Counter/mask/input/entry/helper guards prevent
treating the marker as unique current-capital resolver or observed instance.

[UEA36 continuation](../../manifests/resource-density-generation-boundary.json#/ironCapitalCaseBoundary/uea36RetentionBoundary):
`0x82D199DC -> 0x82CF0CB0(36,p,0)`. The
[native return contract](../../manifests/civilization-bonus-storage.json#/nativeReturnContract)
returns full-width `0`/`1` within four comparisons, writes no memory, and
preserves saved city/coordinates/index/frame. Volatiles including `r4` may
change; saved register retains player. Generated host insertion is excluded.
Caller sets `+3` to `2 + result`, adds clamped era `0..99`, overriding to `1`
for sampled barbarian. Final population remains unproved.

[Registered-child case](../../manifests/resource-density-generation-boundary.json#/ironCapitalCaseBoundary/uea36RetentionBoundary/sessionChildReturnBoundary):
nonnull `+0x100` at `0x82D19A7C` selects `0x82A73340` under current
owner/child/target/lifetime guards. Two instructions return zero-extended
`+0x20`, without memory writes or other GPR/floating/control changes.
Initialized vtable bytes identify no current child. Zero is valid return, yet
unchecked `result+0xC` must be readable. Equality with player low word copies
`+3` to `+4` and conditionally sets a global; inequality skips. Initialized `-1`
proves no current compared value.

Both completing branches and null-child bypass reach `0x82CFE828(i)` at
`0x82D19AD0` under protected frame/source guards; return/writes/retention remain
unknown. Founding supplies no neighbor argument. Spawn-relative writing does,
but Iron `1` still needs positive refresh; neither trace proves retained nearby
placement.

## Post-setup tile changes

For same-terrain type overrides, see the separate
[resource identity override contract](resource-identity-overrides.md). It owns
the common-reader hook candidate, fresh-object type/name routing, native Oak
child effects, sidecar storage and earlier India-policy ordering.

The
[tile mutation
boundary](../../manifests/resource-density-generation-boundary.json#/postSetupTileMutationBoundary)
distinguishes logical tile state from completed refresh and persistence.

| Question | Static result |
|---|---|
| Terrain state after a byte store | Conditional. Direct resource, yield and movement-admission reads use the new byte. A separate terrain snapshot stays unchanged; complete visual, minimap, route, city and AI invalidation is not established. |
| Positive resource refresh | Conditional. Append can return with capacity available. A nonempty query skips object creation and type replacement; a new object still requires allocation, construction, registration and retention. |
| City workable geometry | Eight candidate neighbors at radius one normally; twenty with the Courthouse bit. Ownership, assignment and yield gates still decide actual use. |
| Map dimensions and topology | Retained supported bounds are 32 by 32, with first-coordinate wrap and second-coordinate clipping in the city and accepted AI calculations. The backing stride is 40. |
| Presence legality and Abundant count | Intrinsic existence requires clear `0x1001`, presence `0x20` and a matching terrain/remainder definition. Count unique physical resource tiles after native writers, independently of player technology. |
| India's starting resource | The direct starting attempt for civilization index 10 is separate from India's four cumulative UEA entries. It does not guarantee a newly added or Iron resource. |

### Terrain consumers and stale state

Store `0x8312B288+i`, `i=40*a+b`, changes one byte without refresh. Resource,
three yield accessors and movement admission `0x82CF0268` read it on their next
admitted call; stored credits/assignments/routes/AI summaries do not.
`0x82D00C78` can rescore normalized candidates, query food/production/trade and
store assignment, but return/scheduling supplies no general hot-refresh
contract. Route/search/strategic-AI invalidators remain unknown.

Terrain load `0x82C6E898` calls `0x82C6AEB8`, which saves live plane at `+0xEC`,
allocates `+0xF4` snapshot and copies rows. Later live writes leave it stale.
Rebuild needs live receiver, allocation and dependent render state;
geometry/minimap/blend/lightmap refresh remains unproved, including via resource
callback.

### Positive refresh and replacement

After reset/query/predicate, `0x822E55F0` with valid aligned vector, nonzero
begin and end<capacity copies payload to end, advances `+8` by four and returns
descriptor. Writes must spare query metadata, unvisited words, caller and
planes. Growth tails to `0x821B4450`; allocation `0x821B4554`, copy/ storage and
return remain conditional. Query needs stable finite end and completing
predicates/appends.

`0x82D7FCB0` skips creation for nonnull begin/nonzero count, without type/name
comparison or replacement. Terrain change plus `+0xF4` does not replace an
existing visual. Empty result requires nonnull allocation `0x82D7FD2C` (null
still dereferences), constructor `0x82E54250`, `+0x14` dispatch and `0x82C78D68`
manager insertion, including further appends/refcount loops/ helpers.
Completion/lifetime remain required; insertion alone proves no retained
registration.

`0x82D64B18` locally returns for terrain !=`3`; `3` uses `+0x118`/ `+0x120`
child work, with targets in the manifest but completion conditional. Finite
retained query, capacity appends, nonempty result and terrain !=`3` give a
returning positive case that skips creation; fresh creation/replacement remain
unproved.

### City geometry and map edges

City candidates are eight `{-1,0,1} x {-1,0,1}` offsets excluding `(0,0)`
(Chebyshev radius one). Courthouse `+0x10` bit `0x4000` adds twelve radius-two
boundary cells excluding four outer corners: twenty neighbors, or 21 with
separately treated center, not necessarily worked/usable. Tables
`0x82F7A0B8`/`0x82F7A168`:
[Courthouse scan](../../manifests/courthouse-city-coordinate-scan.json).

Dimensions `0x82F77364`/`0x82F77448` initialize to `32`: 1024 supported cells,
stride 40. City normalization `(a+offset+32)%32` wraps first component, clips
second to `0..31`. This consumer topology proves no compass orientation or
alternate sizes; validate current bounds. Resource reader does not normalize.

Prospective spawn-city ring uses eight neighbors; clipped second-axis edges need
a Legendary failure policy. Deduplicate wrapped physical cells before counting
or assigning identities.

### Legal presence and the native baseline

On normalized supported coordinates, context `-1` accepts presence with clear
`0x1001` and matching terrain/remainder. Codes `0..6` cover all selected
remainders in 22 rows; others lack matches. Water/mountain qualify, so movement,
land-only, technology and availability filters cannot define intrinsic count.

Measure `N` after all native generation/starting writers (including retained
India result), before policy changes. Count unique physical presence with
intrinsic `0..21`, excluding padding, aliases, definition rows, query results
and object counts. Preserve forbidden raw presence without counting it.

Target `min(3*N,L)`, where `L` is eligible physical capacity, adds at most
target minus `N`; zero baseline adds zero. Abundant can finitely traverse absent
eligible cells deterministically, preserving terrain/unrelated flags and
reporting saturation.

### Save serialization

Selected save passes 1600 terrain bytes and 1600 flag halfwords through
`0x82CC4040`. Default-stream `0x822DE688` forwards live terrain to `+8`;
`0x822DE7A0` walks current flags through `0x822E1338`. Returns, compression,
finalization and retention until each read remain required; nonzero alternate
stream changes source behavior.

Raw planes need no cached-terrain/presence refresh, but derived-object
consistency, save success, mode-one readers and changed-tile
reload/reconstruction remain separate gates.

### Title implementer contract

1. Validate bounds; wrap first coordinate, clip second, deduplicate and use stride
   40. Keep initial Settler anchors. Abundant preserves valid resources;
   Strategic preserves native floor; Legendary preserves terrain, allows
   duplicates and can replace ring resources.
2. Strategic chooses coordinates before conversion: Iron Hill `4`,
   `(a+b)%3==0`; Oxen terrain `1`, `(a+b)%4==0`; both need presence and
   clear `0x1001`. Terrain alone cannot force identity.
3. Use radius-one/eight-neighbor rings. Abundant preserves terrain, targeting at
   most three times post-native count. Resolve clipping/overlaps finitely;
   Legendary allows duplicate ordinals.
4. Authorized conversion writes terrain before presence/callback; Legendary
   publishes identity without terrain changes. Require query/growth/allocation/
   construction/dispatch/manager completion with retained state. Nonempty queries
   prove no replacement; callback returns are not success flags.
5. Conversion needs an exclusive pre-consumer point or complete visual/minimap/
   route/city/AI refresh. Save final retained planes; validate visible state and
   reload separately. These findings certify no safe live-edit API.

## Abundant and Legendary feasibility

The
[feasibility boundary](../../manifests/resource-density-generation-boundary.json#/abundantLegendaryFeasibilityBoundary)
owns consumers, locators, capacity and gates. Abundant conditionally adds native
presence; Legendary preserves terrain/allows duplicates, needing identity
overrides for nonmatches. Both require timing/consumer/new-object contracts;
changing visible identities also needs replacement.

### Presence consumers

Presence `0x20` lives in `0x8312A608+2*(40*a+b)`, separate from terrain
renderer. Procedural `0x82D0F0D0` stores `0x82D10508`, `0x82D10608`,
`0x82D10708`, `0x82D10808`, `0x82D10930` follow conversion/RNG/count gates;
record stores `0x82D1AE04`/`0x82D1C40C` and India `0x82D23324` retain the
qualifications above. Twenty direct reader calls are mapped; indirect,
independent and cached consumers remain incomplete.

| Consumer | Live or cached | Native locator and consequence |
|---|---|---|
| Intrinsic type and availability | Live planes | `0x82CF1558(a,b,context)` recomputes type; context `-1` avoids player technology filtering. |
| Food, production, trade | Live component input; stored city credits separate | Reader calls `0x82CF1F0C`, `0x82CF1CAC`, `0x82CF1A44` see current presence on recalculation. |
| City candidates and assignments | Live input, stored result | `0x82D016D8` and `0x82D019D4` do not run merely because a flag changed. |
| City work and neighbor type bitsets | Cached | `0x82D13EA0` and `0x82D14358` feed `1<<q` city words; old bits require a proved reset/rebuild order. |
| AI candidate score | Live selected calculation; broader state unknown | `0x82D027E8` reads type before definition valuation; strategic caches and queued decisions remain unbound. |
| Setup counts | Live when computed, prior decisions retained | `0x82D2456C` and `0x82D24778` precede the post-setup recount and are not Abundant's global baseline. |
| Resource models | Cached objects fed by live type | `0x82D7D974` forwards type; `0x82D7FD18` skips creation/type replacement for a nonempty query. |
| Resource availability/discovery | Live query, stored object byte | `0x82E53F34` and `0x82E544AC` do not prove all later object refresh. |
| Tile detail | Live on refresh; displayed UI separate | `0x82DECEB8`/`0x82DECEE8` query identity/availability before detail construction. |
| Notifications and founding | Live selected calls | `0x82CE8080`, `0x82CEA998` search types; `0x82D1A11C` can lead to clearing center presence at `0x82D1A148`. |
| Minimap and fog | Unknown | No exact reader/cache/refresh owner is joined; the resource callback is not a proof of coverage. |
| Save/load | Live raw planes; reconstruction separate | `0x82CC49B4..0x82CC4A18` transfers terrain/flags on the default stream; successful derived-state reconstruction remains conditional. |

The
[mixed-identity
observation](resource-identity-overrides.md#mixed-identity-observation)
blocks any universal identity-hook claim. A cached old city bit or an
independent bonus formula is a possible explanation, not an established cause.

### Legal capacity and native identity

`0x82CF1558` takes `r3=a`, `r4=b`, `r5=context`: presence, clear `0x1001`,
matching terrain/remainder. Potential absent-tile eligibility is clear `0x1001`
plus normalized terrain `0..6`; no spacing/river/land-only test appears.
Stronger native placement legality remains unproved.

Abundant preserves resources/terrain, counts final unique native resources and
randomly selects absent eligible cells in finite reproducible order to
`min(3*N,L)`, logging achieved count/saturation. `N=0` targets zero. No identity
override is needed; callbacks, cache parity and baseline timing remain
conditional. All twenty-two types are algebraically possible without terrain
writes where matching terrain exists:

| Existing terrain | Native valid definitions, in remainder order | Legendary choices |
|---|---|---|
| Sea `0` | Dye `10`, Whale `16`, Fish `18` | Fish `18` |
| Grassland `1` | Oxen `0`, Wheat `20`, Cattle `19`, Incense `11` | Random Oxen, Cattle or Wheat |
| Plains `2` | Wine `8`, Marble `13`, Silk `14` | Random Wine or Marble |
| Forest `3` | Rubber `5`, Oak `9`, Game `17` | Oak `9` |
| Hill `4` | Iron `1`, Coal `3`, Aluminum `6` | Iron `1` |
| Desert `5` | Sulfur `2`, Oil `4`, Spices `12` | Spices `12` |
| Mountain `6` | Uranium `7`, Gems `15`, Gold `21` | Random Gems or Gold |

[Definition matrix](resource-definitions.md): `0x82F6FAD0`, 22 rows of `0x44`,
terrain `+0x40`, remainder `+0x42`. Mountain means terrain `6`, not an inferred
class in unnamed `+0x41`. Unsupported terrain has no match. Two Grassland/two
water/two Forest is an owner premise, not a universal native ring census.

### Legendary identity choices

For normalized `s=a+b`, divisor is four on Grassland, three elsewhere. Draw a
permitted target first; matching `s % divisor` needs only presence `0x20`,
otherwise override with its same-terrain remainder. Eleven targets extend
Balanced's Oak/Oxen/Fish by eight:

| Terrain | Additional override targets and remainders |
|---|---|
| Grassland | Wheat `20`: `1`; Cattle `19`: `2` |
| Plains | Wine `8`: `0`; Marble `13`: `1` |
| Hill | Iron `1`: `0` |
| Desert | Spices `12`: `2` |
| Mountain | Gems `15`: `1`; Gold `21`: `2` |

Native Oak requires `s%3==1`, Fish `s%3==2`; Grassland `0/1/2` yields
Oxen/Wheat/Cattle, `3` Incense (every permitted draw needs override). Native
Plains `0/1`, Hill `0`, Desert `2`, Mountain `1/2` may match; other remainders
cannot. Always selecting native identity changes requested randomness.

Nonmatches retain the mixed-identity risk without proving every target defective
or its cause. Native matches without active/stale overrides avoid that source of
disagreement, but still need presence/cache/visual gates. Preserve native
technology/context filtering.

Duplicates remove distinct-type capacity limits. Freeze one choice per physical
cell across overlapping rings; preserve all centers, even inside other rings.
Resolve clipped/forbidden/unsupported/fallback conflicts before writes. Log and
retain Normal for impossible starts; another ring must not invalidate that
fallback.

### Terrain construction and hook contract

`0x82C6EB14` calls snapshot builder with `r3=terrain owner`, `r4=0x8312B288`,
`r5=40`. `0x82C6AEB8` uses fixed plane/stride, frees old `+0xF4` at
`0x82C6AEE8`, allocates/copies rows at `0x82C6AF28..0x82C6AF54`,
allocates/reuses `+0xF0` and writes cell classifications.
Allocation/helpers/dependent state make this construction, not safe live
refresh. Height/blend/lightmap, minimap/fog, path/search, strategic-AI, city
work/credits and geometry invalidation remain unbound; patching snapshot bytes
is insufficient. Legendary avoids terrain changes, but resource-state gates
remain.

Freeze policy before `0x82D25254`. At return `0x82D25258`, `r3` is about to
enter `r29`; `-1` fails. This is observation, not a certified seam: visual
attempts already occurred at `0x82D2332C`, `0x82D2455C`, `0x82D24768`. Recount
`0x82D2530C` uses `r3=1,r4=1`, no coordinates. Neither proves empty queries,
final writers or pre-snapshot/first-render order.

Publish presence/identity before current inline receiver `A=0x8314F76C` `+0xF4`
with `r3=A,r4=a,r5=b`; `U32[A]` is vptr, not receiver. Initialized `0x82D7D950`
reads intrinsic type, dispatches `+0x248` to `0x82D7FCB0`, then `0x82D64B18`.
Empty-query allocation/constructor/name/ model/registration/lifetime must
complete. Nonempty `0x82D7FD18` -> `0x82D7FE2C` skips type/name replacement:
publish before first creation or prove disposal/rebind/replacement. Forest child
work can change despite retained terrain (Balanced Oak); return/read-back proves
no retained visual.

Identity candidate: pre-`0x82CF15C4`, `r11=40*a+b`, `r8=coordinate sum`,
`r7=terrain base`. Substitute only same-terrain remainder; retain presence,
forbidden/player gates and valid zero. Close mixed-identity consistency before
Legendary use. Matrix/reader selection has high static confidence; end-to-end
feasibility needs order and retained creation/replacement. Supported `0..6` has
choices; impossible cells use Normal.

Abundant adds absent native types; Legendary may replace existing types. Neither
setup/recount proves final-writer-to-first-consumer order. Consumer-table limits
still cover city bits/credits, yields/bonuses, AI, detail, minimap/fog and
reload. Native flags save presence, not override ordinal: restore frozen policy
before load consumers via
[identity lifecycle](resource-identity-overrides.md#persistence).

## Mutation seam and native setup order

No shared mutation seam is certified. The selected native setup path constructs
the scene and attempts resource creation before later player assignment and
presence writers. Abundant needs the final native count; Legendary can change an
existing identity. Neither the setup return nor recount satisfies both
requirements.

The
[mutation seam
boundary](../../manifests/resource-density-generation-boundary.json#/abundantLegendaryFeasibilityBoundary/mutationSeamBoundary)
owns this partial order, exact registers, packet evidence and remaining gates.
It is not a total first-frame timeline.

| Selected order | Addresses | Presence/identity and retained state |
|---|---|---|
| Setup enters scene generation | `0x82D25254 -> 0x82D217C8`; `0x82D22A24` current `+0x150(A,1,1)` | Initialized target `0x82D86A78`; actual receiver/vptr/target and completing calls remain gates. |
| Map generation writes presence | `0x82D86AD0 -> 0x82D0F0D0`; stores `0x82D10508/10608/10708/10808/10930` | Live flag plane; named-map success through `0x82D0ADE0` bypasses procedural work. |
| Procedural starts are selected | `0x82D10FC0 -> 0x82D02C58`; stores `0x82D03078/03084` | Stored X/Y arrays, with repair/excluded-slot qualifications; later assignment can swap them. |
| Early observation edge | `0x82D86AD4` | After generation return, before the following terrain/scene chain; not final native N or final per-player assignment. |
| Terrain and resource scene construction | `0x82D86B34 -> 0x82C7E760`; `0x82C6EB14 -> 0x82C6AEB8`; `0x82D86CBC` current `+0xFC` | Terrain snapshot is cached. Initialized sweep `0x82D7E068` reads flags and conditionally calls resource `+0xF4` at `0x82D7E12C`. |
| Resource-object attempts | `0x82D7D950 -> 0x82D7FCB0`; `0x82D7FD18` | Live intrinsic q feeds cached object/type/model. Nonempty query skips type replacement. Absolute first successful object remains conditional. |
| Scene tail returns to setup | `0x82D8744C -> 0x82D7FC48`; `0x82D87458 -> 0x82C6CB18`; return to `0x82D22A28` | Further scene work; these entries are not identified as minimap/fog builds or first render. |
| Player assignment, unit/city requests | `0x82D230E0 -> 0x82CFE908`; X/Y loads `0x82D231B4/231B8`; Settler request `0x82D23258` | Mode `+4==2` skips coordinate reorder; other values call paired swaps. Scenario/city arms also exist; successful creation/lifetime remains conditional. |
| Later native presence and counts | `0x82D23324/2332C`; `0x82D24504/24514`; `0x82D24550/2455C/2456C`; `0x82D24760/24768/24778` | Writes interleave with visual attempts and selected intrinsic class counts. These counts are not map-wide N. |
| Successful setup return and recount | `0x82D25258`; `0x82D25300`; `0x82D2530C -> 0x82D11AD8` | Initialized `+0x54` target `0x82D80AD8` is one `blr`. Recount preserves `0x20`, clears `0xB04` and calls city calculation at `0x82D128FC`; complete rebuild is unproved. |
| City credits/bits and AI evaluation | `0x82D016D8/019D4`; `0x82D13EA0/14358`; `0x82D236E4 -> 0x82D02530` | Live q can produce stored credits, ORed bits or decisions. Their complete reset/build schedule is not joined. |
| Minimap, fog, first game frame | Exact owners/edge unbound | No proof covers every consumer or establishes ordering before the first render. |

The concrete obstruction is interleaving: `0x82D24504` can change presence
before a visual attempt at `0x82D24514`, while `0x82D24760` later adds more
presence. Under completing empty-query/object paths, an object can therefore
precede Abundant's final native baseline. Early counting can omit native
resources; late counting does not precede those attempts.

### Candidate hook and rebuild limits

Pre-`0x82D86AD4`, word `0x3BE00001` (`li r31,1`), follows generation
`0x82D86AD0`: `r30` receiver, `r29` generation flag, `r31` incoming `r5` about
to become `1`. Selected ingress is `A,1,1`; `r3` proves neither success nor
coordinate. It runs per completing branch invocation, not proved once per new
game. Require accepted-launch latch, mode `1/2`, actual dispatch and retained
starts. Named maps need producer linkage; normal load `r4=0` bypasses, but other
ingress is not exhaustively excluded.

This trace precedes scene work, yet later swaps/writes and transitive cache
reads remain; staged policy needs ownership of later writes/final counting. No
complete late repair exists: `+0xF4` conditionally creates, sweep
`+0xFC / 0x82D7E068` does not replace, `+0x54` is no-op. Recount has no direct
`0x82D13978` call, but indirect calls prevent absence proof. Selected city work
proves no complete bit reset/credits/AI/minimap/fog rebuild. City-bitset caller
search hit sixteen and remains closed. Constructors are no safe live API; these
modes preserve terrain.

Title source freezes/stages Resources before `sub_82D25170`; Balanced publishes
at LR-guarded recount `0x82D25310`, after optional AI removal, before its
presence/refresh/native recount, not at `0x82D25254` BL. Wrapper preamble and
`Apply` clear snapshots; moving publication requires lifecycle changes.
Revision/digests:
[identity lifecycle](resource-identity-overrides.md#persistence).

### Load ordering

Load restores presence, never reruns placement. Default stream transfers all
sixteen flag bits including `0x20`, subject to stream/order/return guards;
overrides need sidecar. Title stages it before `bctrl 0x82D844C8` (return
`0x82D844CC`); pre-BL `0x82D86674` clears/republishes before
`0x82CC4040(1,frame+0xC0,r29)`. Terrain `0x82CC49AC` precedes flags
`0x82CC49F4`.

Retained `r29==0` route: `0x82D86870 -> 0x82D7F550` dispatches `+0x150(A,0,arg)`
at `0x82D7F5C8`, reaching sweep `0x82D86CBC`; `0x82D7F614` calls `+0xFC` again
afterward. Restoration precedes those consumers under target/frame/global/call
retention. Earlier header `0x82D8645C -> 0x82CC29B8`, dispatches, alternate
routes/streams, aggregates and first frame remain unjoined. Emitted-hook
validation and Oxen/Cattle consistency remain separate gates.

### Placement legality beyond intrinsic lookup

No general spacing/river/coast/reservation validator is proved. Clear `W&0x1001`
plus terrain `0..6` is potential intrinsic eligibility; reader also requires
presence. Sweep `W&0x400` instead selects `+0x100` before `W&0x30` permits
`+0xF4`; meaning unknown. Conservative host exclusion of `0x400` reduces
admitted capacity below intrinsic `L`. With `K` admitted absent cells, `C=N+K`,
target `min(3*N,C)`, retaining existing resources. `0x1401` is no universal
legality mask.

Sampler `0x82D246F4..0x82D24710` ordinarily accepts terrain `6` without
presence. Rejections increment at `0x82D24714`; `9999` falls through without
rechecking. Counter increments before first draw and spans successful outer
passes, so it does not count `9999` draws and is no general oracle.

Freeze once per accepted launch; preserve terrain/centers/native resources,
define host admission, measure final N, select finitely and log capacity/count.
Publish before affected reads/first creation or prove replacement/cache rebuild.
No current address satisfies this complete contract.

## Paired new-game setup probe contract

The
[probe
contract](../../manifests/resource-density-generation-boundary.json#/abundantLegendaryFeasibilityBoundary/mutationSeamBoundary/pairedSetupProbeContract)
defines twelve required fixed sites, optional discriminators, exact original
instruction words and the coverage needed to interpret their order. These are
verified native boundaries, not a runtime result or an emitted-hook guarantee.

The capture is one accepted mode-1 launch and one accepted mode-2 GOTW launch,
with the same supported build/content/loadout/settings and native Normal
Resources, using a fresh title process for each mode. Record actual map, seed,
week, scenario, difficulty and players; the two modes need not produce the same
map.

Observe only: do not add resources, found a city or open extra UI to force an
unexercised cache in this capture.

Every row records an epoch, monotonic 64-bit sequence, thread, PC, LR,
frame/call ID and `G=U32[0x8314EFC8]`, `mode=U32[G+4]`. The setup global is a
pointer cell; mode is not `U32[0x8314EFCC]`. Tile rows include raw coordinates,
effective address, `idx=40*a+b`, current flag halfword and terrain byte. Record
unknown player/ordinal explicitly.

A predicted intrinsic ordinal is not the reader's actual player-filtered return.
Preserve ordinal zero. All hooks observe before the listed instruction, preserve
guest state and execute that instruction once. Logging must not call native
helpers or RNG.

Nested consumer attribution also needs matched invocation exits/tail returns
from transparent wrappers or trustworthy call/return observation. Those are
additional observer events, not more fixed guest sites. Entry-only tokens must
not survive a return; without matched scopes the outer consumer is unknown.

| Required site | Owner | Record beyond common fields | Frequency and question |
|---|---|---|---|
| `P01 0x82D217C8` | `0x82D217C8` | Entry `r3..r8`; plane/start snapshots and player count/exclusion | Per setup invocation. Where does setup begin, including retries? |
| `P02 0x82D86AD4` | `0x82D86A78` | `r30=receiver`, `r29=generation flag`, `r31=incoming r5`; current vptr/slots and snapshots | Per generation return. Is this candidate after final starts/writes and before consumers? Selected setup values are `A,1,1`; `r3` is not success. |
| `P03 0x82D25258` | `0x82D25170` | `r3=setup result` before copying to `r29`; snapshots | Per setup return. `-1` is failure. What preceded the accepted return? |
| `P04 0x82CF1558` | `0x82CF1558` | `r3=a,r4=b,r5=context`, entry LR, `r16..r31` | Per tile/query. First identity reads, including count LRs `0x82D24570/2477C`, before classification. Actual q is not yet returned. |
| `P05 0x82D7FD00` | `0x82D7FCB0` | `r28=receiver,r31=a,r29=b,r26=q_input`; descriptor at receiver `+0x208` | Per nonnegative-q query. Empty/create versus nonempty/skip. Null-start creation bypasses `0x82D7FD18`, so that branch alone is insufficient. |
| `P06 0x82E54250` | `0x82E54250` | `r3=object,r4=a,r5=b,r6=q`; object generation and checked 0x84-byte watch | Per constructor/tile. First construction activity, including other callers; this is not live registration. |
| `P07 0x82D00C78` | `0x82D00C78` | `r3=city`; checked record/owner/coordinates and record watch | Per city calculation. First candidate/yield/resource work. Entry alone does not prove a build. |
| `P08 0x82D13978` | `0x82D13978` | `r3=city,r4=raw mode`; same record/watch | Per city update. First bitset owner entry, then actual clear/OR/credit stores. |
| `P09 0x82D02530` | `0x82D02530` | `r3=a,r4=b,r5=raw evaluation context` | Per AI candidate. First evaluation, then its reads and stored decisions. Do not assume `r5` is a player. |
| `P10 0x82D92590` | `0x82D92590` | `r3=cache object`; `r4..r8` and old five words | Per overlay setter. Detect first comparison/reuse as well as updates. Values map to `+6C/+74/+70/+78/+7C`; they are not ordinals. |
| `P11 0x82D931B8` | `0x82D92FA0` | `r29=a,r30=b,r31=owner,r26=cache`; `r3,r27,r23,r24,r25` | Per tile overlay update after yield queries. Which tuple reaches the setter? This is an interior return point, not a function entry. |
| `P12 0x82D25310` | `0x82D25170` | Raw `r3,r29`; plane/start snapshots | Per recount return. What occurred between setup return, title publication and recount completion? `r3` is not a certified status. |

For P07/P08, the city record is `0x8314FE28+0xBC*slot`, with signed owner byte
`+0` and signed coordinate halfwords `+0x30/+0x32`. Check mapped ranges; do not
guess a slot limit. P11's owner `+0x70` supplies a city selector when valid. Its
numeric outputs are helper results, not resource types.

The overlay setter compares five old values before its equality early-return.
Changed values store at `0x82D92678/67C/684/688/68C`. P11 follows the food query
at `0x82D931B4` and precedes the setter call at `0x82D931D0`. Entry probes alone
cannot distinguish a build from reuse: correlate actual reads/writes and object
generation IDs.

### Required coverage outside the fixed-site count

Twelve fixed hooks are not an exhaustive last-writer or cache census. The
following are additional required observer capabilities. If unavailable, the
fixed-site capture is diagnostic and its completeness verdict is inconclusive.

Observe committed writes of every width, including bulk/host/atomic writes, to:

| Region | Range |
| --- | --- |
| Full flag plane | `[0x8312A608,0x8312B288)` |
| Terrain plane | `[0x8312B288,0x8312B8C8)` |
| Start arrays | `[0x830E343C,0x830E347C)` |
| Active-start selector words | `[0x82F700AC,0x82F700B4)` |

The latter are signed32 count `C` and excluded ordinal `E`.

Keep their raw bits and every transition with the active/excluded slot mapping;
snapshots alone do not prove retention. The supported array model requires count
`0..8`. Keep before/after bytes, PC, width, origin, sequence and affected
halfwords. Separate the last physical flag store from the last actual `0x20`
change.

An idempotent old-word store can overwrite a hypothetical addition; it is not
automatically harmless. Capture other flag changes, including `0x80`, `0x400`
and `0x1001`. No separate native per-tile ordinal plane is established.

Observe resource-input reads through those planes and definition rows
`[0x82F6FAD0,0x82F700A8)`, including aliases/bypasses of the common reader.
Classify each observed reader and correlate it with the accepted twenty-site
call map and active invocation IDs. Unknown readers/independent fields keep the
claim covering every consumer open.

Watching native planes does not prove that an independent stored identity or
cache source is absent. Dynamic object/city/ overlay watches record the located
derived fields; they do not close all strategic AI, minimap or fog state.

Tile/detail output may be filtered and repeated samples capped. Complete
summaries of stores and first consumers for each cell, distinct PC/target counts
and global first object/cache events must still be retained. Account for all
1600 backing cells, marking the 1024 playable cells separately.

Dropped required events, unsupported write forms or unordered cross-thread
visibility invalidate a positive result. A sequence allocated before an
unsynchronized store is not proof that the write was visible before the next
event.

Arm at the accepted-launch host transaction before native setup, and continue
past P12 through a qualified first gameplay frame plus final snapshots and
pending-work status. Loading/menu presents are not that boundary. No exact guest
first-frame PC is certified here.

Record title clear/publish/apply events and any host plane writes in the same
sequence; the native-baseline runs must make no resource-policy changes.
Preserve retries as separate invocations.

Optional diagnostics in the manifest cover:

| Diagnostic | Site |
| --- | --- |
| Adapter | `0x82D7D950` |
| Nonempty branch | `0x82D7FD18` |
| Constructor return | `0x82D7FD48` |
| Manager return | `0x82D7FD9C` |
| Type store | `0x82E54280` |
| Count-query returns | `0x82D24570/2477C` |
| Sweep dispatch | `0x82D86CBC` |
| Both reader exits | `0x82CF1684/1690` |

The events for constructors, type stores and managers distinguish attempts from
completing local work; none alone proves retained visible state. Logging of
actual returns must cover both reader exits. P05 records a captured input, not
inherently an intrinsic-reader return.

That label needs the actual link between the reader in context 1, current
dispatch and retention; an unknown caller does not inherit it.

### Pass, fail and inconclusive results

For a strict shared global seam at the same instruction `S` in both accepted
modes, require complete ordered coverage and classified source/cache ownership,
then require:

`max(final X/Y/C/E write, final native relevant-field store) < S < first resource construction/cache input`

Use physical stores for this sufficient criterion, including idempotent ones.
Require retained starts/planes through closure, an unambiguous gate that admits
the accepted launch only once, legal current terrain/flags and a final unique
intrinsic native count independent of player technology.

A later store needs a separate proof that its fresh read/modify/write preserves
an added bit before the criterion can be relaxed. A trace where the bit happened
to remain zero is insufficient. Earlier cache work similarly needs a complete
later reset/rebuild.

Earlier retained affected objects/caches/counts without replacement/reset, or
later native presence/terrain/start writers, rule out that strict candidate. For
Legendary, a nonempty object query on a changed identity needs replacement;
another `+0xF4` call does not supply it.

Kept objects outside Abundant's affected absent tiles can be harmless in a
narrower per-tile analysis, which must not be reported as the shared global
seam.

Unknown readers/fields, event loss, unordered threads, unexercised caches,
ambiguous epochs/endpoints and incomplete object-lifetime evidence are
inconclusive. A cache not entered during the pair is not exercised, rather than
proved absent or safe. These two observer-only launches can prove observed order
or reject a candidate.

They do not prove added resources propagate to every consumer or all supported
maps. That needs a separate controlled presence-only mutation/parity check after
the ordering and coverage gates close.

Mode-3 normal load is a separate follow-up around staging/reset
`0x82D844C8/86674`, plane transfer and later sweeps. It is excluded from this
pair; load restores saved presence and must not rerun placement.

## Practical limit

The result supplies four native writer owners and a count eligibility gate for
the selected conversion pass. The selected scenario alias path reads other
fields, and a separate placement leaf sets flag `0x80`; neither establishes a
density count control.

Increasing all resources or guaranteeing Iron/Oxen near the initial Settler
spawn still requires completed nearby placement and refresh, legal terrain,
completed start production and setup timing, retained creation, deterministic
ordering and bounded failure.

The local mapping from players to coordinate requests above supplies an anchor
contract, with those execution and retention conditions still open. The
after-loop candidate supplies a scheduling location.

One retained payload/getter case establishes the predicate return, while actual
query membership, constructor-child retention, growth and new-object refresh
remain qualified. The post-setup contract supplies geometry, topology, intrinsic
counting and raw save-plane arguments with their exact gates. A real
`RESOURCEDENSITY` consumer remains unbound.

Normalization-dependent tuning requires its earlier producer and actual value.
