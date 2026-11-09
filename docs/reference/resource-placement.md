# Resource density and placement

Four code paths write the resource-presence flag. Terrain conversion writes it.
Two operations that use record coordinates write it. A setup branch next to an
initial Settler request writes it. Conversion compares against the fixed value
`4.0`, and it depends on RNG and normalization state that can change. No link
to the scenario setting `RESOURCEDENSITY` is shown. Setting it to `3` does not
show that more resources appear.

These findings describe static code paths under stated conditions. They do not
show the actual inputs, a completed setup or any run-time effect. Each claim
keeps its conditions on returns, on frames and memory, and on aliasing.

- [Density boundary](../../manifests/resource-density-generation.json): the setting and the limits of the search.
- [Writer boundary](../../manifests/resource-density-generation.json#/placementWriterBoundary): locators and the conditions under which values stay unchanged.
- [Scenario schema](../../manifests/scenario-schema.json): parsing.
- [Resource definitions](resource-definitions.md): the 22 ordinals and their technologies, including Oxen `0` and Iron `1`.
- [Presence, identity and the selected writer](#presence-identity-and-the-selected-writer), [tile changes](#post-setup-tile-changes),
  [Abundant and Legendary](#abundant-and-legendary-feasibility), [setup probe](#paired-new-game-setup-probe-contract).

## Stored setting

Slot 3 of the signed 16-bit scenario values sits at scenario `+0x6`, and its
default is `2`. The function `0x82DAEFD8` applies the scenario and writes `2`
to the active value at `0x830E8FD6`. Matched custom records copy all 16 bits
without any range check specific to density. This holds only when the calls
return, the records are valid and the values stay unchanged.

| Value | Established meaning |
|---|---|
| `2` | Record and local setup default |
| Other signed 16-bit values | Stored and copied only; gameplay effects and support are unknown |

No value is identified as Sparse, Abundant, Legendary Start or Strategic
Balance. Searches within the recorded limits do not show that the field is
unused.

## Presence, identity and the selected writer

`0x82CF1558` requires presence `0x20` and clear `0x1001`. It then matches the
terrain and the coordinate remainder against the 22 definitions. The checks on
the player and the context are separate. The function reads no per-tile ID
plane. The definitions decide which resource is present. Iron's case follows
below.

Five stores in `0x82D0F0D0` convert old terrain `2` to `1` and old terrain `5`
to `3`. They OR `0x20` into the flags only under conditions. The stores need
two things: a positive visitation count from 2 to 8, and a pass of the
low-word floating-point conversion test on a second RNG draw, using `4.0`.
`0x82D0FC50` loads the saved RNG pointer plus `16`. Suppose the frames are valid
and disjoint, the inputs stay unchanged, the indices stay in range and the
helpers behave normally. Then the pointer `0x82F7AD00` and the offset `+16` stay
valid, so the load reads `0x82F7AD10`. Earlier RNG work reads that field and
writes only the record state and the counter.

The
[count boundary](../../manifests/resource-density-generation.json#/placementWriterBoundary/componentCountBoundary)
covers the label traversal. Each visited cell increments its class once. When
the terrain of the outer seed cell is zero, the count is negated afterward.
Otherwise it stays positive. The eligible range of 2 through 8 is not a
requested resource count or a map quota. The traversal can clear `7` to `0`
while the cached terrain sign stays in place, and later reads see those
changes. The count records the traversal. It need not equal the component's
current size. The geometry of the eight displacement pairs is unresolved.

For the value to pass from the producer to the reader, four things must hold:
the dimensions are valid, the planes and frames are disjoint, the intermediate
indices stay in range, and the helpers finish. On such a path, the loaded bits
stay in `f31` through six copy sites and reach presence. The earlier value and
its initializer remain unknown. This shows neither a one-in-four probability
nor a usable setting for adjusting it.

The copy leaves the RNG and floating-point registers alone. It writes the
destination and an eight-byte save slot below the stack. Valid disjoint ranges
and a saved pointer that stays unchanged must protect the RNG and the frame.
The stores keep the old flags, but they do not guarantee a valid ordinal. A
successful named-map load skips the conversion. Later effects, returns, whether
values stay unchanged, and the run-time behavior of a completed map are not yet
shown.

## Other presence writers

The
[record-coordinate writers](../../manifests/resource-density-generation.json#/placementWriterBoundary/recordPresenceWriterBoundary)
sit outside the conversion of terrain `2` and `5`:

| Function and store | Condition |
| --- | --- |
| `0x82D1AC70` / `0x82D1AE04` | Needs signed record coordinates, the incoming mask and equal selectors. ORs `0x20`. Tests no terrain, RNG or count locally. |
| `0x82D1B400` / `0x82D1C40C` | Requires the old flags `& 0x1` to equal zero, after the required helper returns and its inputs stay unchanged. |

The domain of the records and the inputs from the callers are unknown. The
[callback boundary](../../manifests/resource-density-generation.json#/placementWriterBoundary/recordPresenceWriterBoundary/callbackRetentionBoundary)
ties the initialized `+0xF4` to `0x82D7D950`. That function reads the resource
with context `-1`, calls the initialized `+0x248` target `0x82D7FCB0`, and then
calls `0x82D64B18`. The reader returns in finite time either `-1` or a value
from `0` through `21`. All three conditions must hold for a finite return that
keeps the flag, the coordinates and the inputs, provided the memory is valid and
the frames are disjoint. The conditions are a lookup result of `-1`, nested flags that select no
call, and a final terrain other than `3`. In these cases the writes stay inside
the callback's frames. Positive results, other flag work and terrain `3` need
further contracts.

For nonnegative results, `0x821C6C28` copies descriptor `+4` to `+8` in finite
time when they differ. It leaves `+0` and `+4` unchanged, provided the frames
are excluded from the writes. `0x821D6340` has three finite paths: a bounds
failure, an empty descriptor and an all-zero payload. These keep the reset and
caller state unchanged under the frame and alias conditions. A nonzero payload
reaches the
[chain predicate](../../manifests/resource-density-generation.json#/placementWriterBoundary/recordPresenceWriterBoundary/callbackRetentionBoundary/nonnegativeHelperBoundary/nonzeroPayloadPredicateBoundary)
`0x821B2D90`. It dispatches the current payload's vtable entry `+0` at
`0x821B2DB0`. After that returns, it follows the `+4` links and returns `1` for
the pointer `0x8314F67C` and `0` for null. Three things are still required: the
current target, a finite chain, and registers, frames and domain words that
stay unchanged. A cycle that never matches has no limit on progress. A true
result selects `0x822E55F0`. Its capacity fast path is described below, and
growth holds only under conditions. The query result is neither a placement
count nor a success Boolean, and more work follows it.

The
[payload case](../../manifests/resource-density-generation.json#/placementWriterBoundary/recordPresenceWriterBoundary/callbackRetentionBoundary/nonnegativeHelperBoundary/nonzeroPayloadPredicateBoundary/payloadSlot0Boundary)
shows that constructor `0x82E54250` stores `0x82132AB8` in the captured
receiver. The initialized slot `+0` holds `0x821CC860`. When the same live
queried receiver keeps its vptr and cell, it selects this getter at
`0x821B2DB0`. Three instructions return the full 64-bit value
`0xFFFFFFFF8314F67C`. They change only `r3` and `r11`, make no memory or stack
access, and leave `r31` unchanged. The comparison of the low words returns `1`.
It reads no chain, including `K+4`, and it does not use the initialized `K`. The
conditions on the wrapper's stack, load and return still apply.

Later, the constructor passes the result of the preceding base call to
`0x82C5FC40`. This is not shown to be a copy of the constructor's receiver. The
constructor calls `0x82D3DBA0` with `60`. That call may initialize 60 bytes and
dispatch the old child `+4`. Its returns, writes and lifetime are unknown. The
full set of writes must miss the original vptr, and unequal pointers are not
enough to show that. The actual query payload, its order and its lifetime are
not yet linked to this case. It is therefore no universal target and no
completed positive refresh.

The call reads `+0xF4` before the flag store. Arbitrary signed coordinates can
alias the receiver's first word without changing the cached target. Bounds, the
order of the vptr access and the absence of aliasing are still required. No
actual call and no full completion is shown.

## Initial Settler coordinates

The
[start boundary](../../manifests/resource-density-generation.json#/initialSettlerSpawnBoundary)
records `Y[p]` at `0x830E343C+4*p` and `X[p]` at `0x830E345C+4*p`. When the loop
reaches player `p`, it loads X at `0x82D231B4` and Y at `0x82D231B8`. At
`0x82D23258` it requests `0x82D11750(p,0,X[p],Y[p])` only under conditions,
where `0` means Settlers. No display-axis orientation follows. The sampled
barbarian player is excluded. Checks on the session, flags and definitions can
choose a city instead. The local checks do not tell human players from AI
players.

The selector `0x82D02C58` writes the arrays. An encoded nonzero `k` gives
`X=trunc(k/100)` and `Y=k-100*trunc(k/100)`, with no check of terrain or bounds.
Procedural selection samples, filters and spaces candidates. It calls
`0x82CFFD08` in mode `0` before the stores and in mode `1` after them. The
[helper contract](../../manifests/resource-density-generation.json#/initialSettlerSpawnBoundary/candidateHelperBoundary)
still requires actual RNG inputs, indices in range and a finite production of
results. The selector table is not shown to be a permutation.

The helper samples eight bytes. Let `z` count the bytes equal to `0`, `h` those
equal to `1`, `d` those equal to `3`, and `p` those equal to `2` or `5`. In mode
`0`, the predicate is `z>=2` and `p>=max(2-h,0)+max(2-d,0)`. It returns `0` or
`1` in finite time, provided the reads, the arithmetic and the saves behave as
required. In mode `1` it rejects with `0`. When the inputs are accepted, it can
select pool bits and write `1` or `3`. It returns `1` without any draws if both
counts are at least `2`. The repair rejection loops have no retry cap, and the
selector and its progress are unknown. The raw classes do not establish any
guarantee about resources, food, Forest or water. The reads normalize one coordinate, but the
writes do not. It must still be shown that the sampled cell and the written
cell are the same.

Both modes keep the full 64-bit `r4`. The native function endings restore the
saved registers if the saved bytes survive. The stack saves always happen. Mode
`1` also writes conversion scratch space, the RNG state and counter, and the
computed classes. The caller reloads the updated RNG state and counter. The
modulus, the normalization, the coordinates, the selector, and the frame and
save bytes need protection beyond the scalar return value.

Before setup reads the coordinates, `0x82D230E0` calls `0x82CFE908`, which can
swap coordinate pairs between slots. That changes which player each producer
slot maps to. The sampled object `2` skips the swap. The reorder's identity and
order, and the conditions on how it fills, on its frame, its bounds and its
return, still apply.

The code loads the coordinates before the child call through `+0x100`. When the
matching registered getter is used, it keeps the player and the coordinates
unchanged. The current child, target and result, their lifetime, and the
validity of the unchecked `result+0xC` are still required. The creator
callbacks, the loop tail, the production and ordering of results, and whether
the unit's coordinates stay unchanged are unresolved. A request is not a
placement, and the founding marker is not a substitute spawn anchor.

## After the player-request loop

The
[post-request boundary](../../manifests/resource-density-generation.json#/initialSettlerSpawnBoundary/postSpawnPlacementBoundary)
identifies a candidate insertion point that applies only under conditions:

| Site | Contract |
| --- | --- |
| `0x82D239E4`, `0x82D239EC` | Increment the player, compare the current signed count, and loop while the player is smaller. |
| `0x82D239F0` | Normal fall through to the next code. |
| `0x82D239F4` | When the count starts at zero or below, this entry skips the preceding reload. |
| `0x82D2393C` | Where the unit-request paths merge after a miss in the player table or after a presence refresh. It sits before the child call through `+0x100`, the unchecked `result+0xC`, the coordinate and global stores and the increment. |
| `0x82D23810` | The excluded-player branch, which the finding does not cover. |
| Beyond `0x82D234C0` | The city arm changes the register that points to the count. Whether it is restored, and where the paths merge, is not established. |

The getter keeps its values unchanged only when the current link to the child,
the result and the reads satisfy the finding's conditions. Creation success is
unchecked. If the count is fixed and valid and the iterations are finite and
unchanged, the loop visits the whole range. That shows neither that every arm
returns nor that Settlers are created. A future pass could use the spawn arrays,
which stay valid, across all players, independently of the native player-table
check. The registers after the final iteration do not represent all units.
Whether this entry runs only for a new game, whether spawns succeed, where the
remaining paths merge, and the later table and session effects are all unknown.
Whether the final state stays valid, and whether a usable placement hook
exists, are not yet established.

## Creator return and unchanged state

The
[creator contract](../../manifests/resource-density-generation.json#/initialSettlerSpawnBoundary/creatorReturnBoundary)
separates the request, the initialization and the success. When the type 0
flags stay unchanged, the creator scans at most 256 player slots. It selects
the first slot whose owner byte and `+7` are both `0xFF`. If no slot is free, it
returns `-1` in finite time and writes no unit, provided the memory and the
return behave as required. Setup can continue because it ignores the result.

The selected record clear is exactly 84 bytes: five 16-byte blocks plus four.
It requires four-byte alignment even for odd slots. The leaf function returns
its input pointer and leaves the bytes outside the record unchanged. The
creator writes the owner, the type 0 flag, the slot and the initializers. The
fields `+0x1C` and `+0x1E` receive only the low 16 bits of the coordinates.

Type 0 flags equal to `1` skip the movement UEA calls. A nonzero current human
mask and a valid player in range give a finite return from the classifier with
no further calls. The movement value times three is truncated into unit `+2`.
The path for a zero mask is not established. The native evidence excludes the
generated host insertion and shows no run-time parity.

The mandatory call through `+0x1A0` at `0x82D11980` selects the initialized
`0x82D7FE40` when the vptr stays unchanged. Its return, its writes, its
lifetime, and whether the creator and setup state stay unchanged are open. The
later call through `+0x1B4` selects the no-op `0x821D5678` only if the freshly
sampled vptr still matches. The session lookup and the flags that stay
unchanged decide whether the tail runs.

When all the conditions on callbacks, registers, frames, saves and units hold,
the tail returns a value from `0` to `255`. Zero means success, but an
initialized index shows neither registration nor lifetime. The save and restore
keep the setup registers unchanged only under conditions. `f29`, the count, and
the frame and source bytes need the contract of every callback. Successful
creation and the Iron refresh are separate open questions.

## India's adjacent grant and an Iron case

The
[spawn-relative case](../../manifests/resource-density-generation.json#/initialSettlerSpawnBoundary/ironPlacementCaseBoundary)
follows `0x82D23258` when the civilization at `0x830ECD28+4*p` equals `10`.
[Row 10](../../manifests/civilization-bonus-storage.json#/storage/rows/10)
identifies it as `Indian`. The creator's result is unchecked. A normal failure
can still reach the writer when the frame, registers and inputs stay unchanged.
A resource-presence flag does not show that a Settler was created successfully.

An RNG conversion with scale `8.0` selects an offset. With the table unchanged
and an index from `0` to `7`, the offsets are
`(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)`. After the offset
is added to the spawn coordinates, `0x82D23324` ORs `0x20`, and `0x82D2332C`
calls the cached `+0xF4`. No local check of terrain, bounds, forbidden flags or
Iron exists. Normalization, index bounds, the geometry and legality of the
placement, and the interpretation of the full 64-bit callback value are still
required. A negative offset means the low word minus one. The scale shows no
probability.

This selects a tile, not a resource ID. The terrain and the coordinate
remainder determine the resource, and the OR may leave an existing resource
unchanged. India's availability fallback follows the technology and UEA39 calls
and does not place resources. See the
[reader boundary](../../manifests/resource-definitions.json#/readerBoundary).

The Iron case applies only when seven conditions hold: index `0`;
`(a,b)=(X[p],Y[p]+1)`; `0<=X[p]<=39`; `0<=Y[p]<=38`; clear `0x1001`; Hill `4`
stays in place; and `(X[p]+Y[p]+1) mod 3 == 0`. With valid disjoint memory and
frames, definitions that stay unchanged and the same physical tile, the
read-back gives ordinal `1` in context `-1`. These are symbolic inputs and not
an observed spawn or RNG draw. No conversion or Iron search occurs.

Installing the target and keeping it unchanged allows a refresh that returns a
nonnegative result. Whether that refresh finishes, and whether the tile's flags
and terrain survive it, is not yet shown. The finite case with result `-1`
cannot show that Iron stays in place. End-to-end placement needs four things:
the creator succeeds, the setup inputs stay unchanged, an actual candidate is
accepted, and a positive refresh completes.

## Iron and the founding-city boundary

The
[Iron and capital case](../../manifests/resource-density-generation.json#/ironCapitalCaseBoundary)
ties ordinal `1` to the record `0x82F6FB14`, whose name and token are `Iron`. In
a domain of `0..39` per coordinate, context `-1` returns Iron exactly when the
tile has presence, clear `0x1001`, Hill `4`, and a signed coordinate sum whose
remainder modulo `3` is zero. This holds when the memory conditions are met and
the values stay unchanged. The domain shows neither the dimensions nor
legality. A real player query also needs the availability checks. Setting
presence cannot force Iron onto any tile. Conversion produces `1` and `3`, not
`4`.

Founding at `0x82D18D88` marks a palace city and stores its coordinates, under
conditions. `0x82D1A11C` reads that center. When the player stays a
nonbarbarian and the result is not `-1`, `0x82D1A148` clears presence before the
rewards. This consumes the resource on the city center. It does not place a
resource nearby. The conditions on the counter, the mask, the inputs, the entry
and the helper mean the marker cannot be treated as a unique resolver of the
current capital, or as an observed instance.

The
[UEA36 continuation](../../manifests/resource-density-generation.json#/ironCapitalCaseBoundary/uea36RetentionBoundary)
runs from `0x82D199DC` to `0x82CF0CB0(36,p,0)`. The
[native return contract](../../manifests/civilization-bonus-storage.json#/nativeReturnContract)
returns a full-width `0` or `1` within four comparisons, writes no memory, and
leaves the saved city, coordinates, index and frame unchanged. The volatile
registers, including `r4`, may change. The saved register keeps the player. The
generated host insertion is excluded. The caller sets `+3` to `2 + result` and
adds the era, clamped to `0..99`. It overrides the value to `1` for the sampled
barbarian player. The final population is not yet shown.

In the
[registered-child case](../../manifests/resource-density-generation.json#/ironCapitalCaseBoundary/uea36RetentionBoundary/sessionChildReturnBoundary),
a nonnull `+0x100` at `0x82D19A7C` selects `0x82A73340`, under conditions on the
current parent object's identity, the child, its target and its lifetime. Two instructions return the
zero-extended `+0x20`, with no memory writes and no changes to other
general-purpose, floating-point or control registers. The initialized vtable
bytes identify no current child. Zero is a valid return, but the unchecked
`result+0xC` must be readable. When the value equals the player's low word, the
code copies `+3` to `+4` and sets a global only under a condition. When it
differs, the code skips this. The initialized `-1` shows no current compared
value.

Both completing branches and the bypass for a null child reach `0x82CFE828(i)`
at `0x82D19AD0`, provided the frame and source bytes are protected. Its return,
its writes and whether its state stays unchanged are unknown. Founding supplies
no neighbor argument. The spawn-relative write does supply one, but Iron `1`
still needs a positive refresh. Neither trace shows that a nearby placement
stays in place.

## Post-setup tile changes

For same-terrain type overrides, see the separate
[resource identity override contract](resource-identity-overrides.md). It covers
the common-reader hook candidate, the routing of the type and name for fresh
objects, the native Oak child effects, the sidecar storage and the earlier
ordering of India's policy.

The
[tile mutation
boundary](../../manifests/resource-density-generation.json#/postSetupTileMutationBoundary)
separates the logical tile state from a completed refresh and from persistence.

| Question | Static result |
|---|---|
| Terrain state after a byte store | Holds only under conditions. The direct reads for resources, yields and movement acceptance use the new byte. A separate terrain snapshot stays unchanged. Complete invalidation of visuals, the minimap, routes, cities and AI is not established. |
| Positive resource refresh | Holds only under conditions. The append can return when capacity is available. A nonempty query skips object creation and type replacement. A new object still needs allocation, construction and registration, and it must stay valid. |
| City workable geometry | Eight candidate neighbors at radius one normally; twenty with the Courthouse bit. Which player owns a tile, how citizens are assigned and the yield checks still decide actual use. |
| Map dimensions and topology | The supported dimensions that stay unchanged are 32 by 32. The city and accepted AI calculations wrap the first coordinate and clip the second. The backing stride is 40. |
| Presence legality and Abundant count | Intrinsic existence requires clear `0x1001`, presence `0x20` and a matching terrain and remainder definition. Count unique physical resource tiles after the native writers, independently of any player's technology. |
| India's starting resource | The direct starting attempt for civilization index 10 is separate from India's four cumulative UEA entries. It does not guarantee a newly added or Iron resource. |

### Terrain consumers and stale state

A store to `0x8312B288+i`, where `i=40*a+b`, changes one byte and does not
refresh any derived state. The resource reader, the three yield accessors and
the movement check `0x82CF0268` read the new byte on their next call. Stored
credits, assignments, routes and AI summaries do not see it. `0x82D00C78` can
rescore normalized candidates, query food, production and trade, and store an
assignment. Its return and scheduling give no general contract for refreshing a
live game. The code that invalidates routes, searches and strategic AI is
unknown.

The terrain load `0x82C6E898` calls `0x82C6AEB8`. That function saves the live
plane at `+0xEC`, allocates the snapshot at `+0xF4` and copies the rows. Later
writes to the live plane leave the snapshot stale. A rebuild needs the live
receiver, an allocation and the dependent render state. Refreshing the
geometry, the minimap, the blending and the lightmap is not yet shown, and that
includes a refresh through the resource callback.

### Positive refresh and replacement

After the reset, the query and the predicate, `0x822E55F0` copies the payload to
the end of the vector and advances `+8` by four. It returns the descriptor.
This needs a valid aligned vector, a nonzero begin and an end below the
capacity. The writes must spare the query metadata, the unvisited words, the
caller and the planes. Growth tail-calls `0x821B4450`. The allocation at
`0x821B4554`, the copy and storage, and the return hold only under conditions.
The query needs a stable, finite end and predicates and appends that complete.

`0x82D7FCB0` skips creation when the begin is nonnull and the count is nonzero.
It compares no type or name and does no replacement. Changing the terrain and
calling `+0xF4` does not replace an existing visual object. An empty result
needs four steps: a nonnull allocation at `0x82D7FD2C` (a null result is still
dereferenced), the constructor `0x82E54250`, the dispatch through `+0x14`, and
the insertion into the manager at `0x82C78D68`. The last step includes further
appends, reference-count loops and helpers. These steps must complete and the
object must have a lifetime. Insertion alone does not show that the
registration stays valid.

`0x82D64B18` returns locally for any terrain other than `3`. Terrain `3` does
child work through `+0x118` and `+0x120`. The manifest lists the targets, but
completion holds only under conditions. Four things together give a positive
case that returns and skips creation: a finite query that stays valid, appends
that fit in capacity, a nonempty result, and terrain other than `3`. Fresh
creation and replacement are not yet shown.

### City geometry and map edges

City candidates are the eight offsets `{-1,0,1} x {-1,0,1}` other than `(0,0)`,
which is Chebyshev radius one. The Courthouse bit `0x4000` at `+0x10` adds
twelve cells on the radius two boundary and leaves out the four outer corners.
That gives twenty neighbors, or 21 tiles with the center, which is treated
separately. These tiles are not necessarily worked or usable. The offset tables
are at `0x82F7A0B8` and `0x82F7A168`. See the
[Courthouse scan](../../manifests/courthouse-city-coordinate-scan.json).

The dimensions at `0x82F77364` and `0x82F77448` start at `32`. That gives 1024
supported cells with a stride of 40. City normalization `(a+offset+32)%32` wraps
the first component and clips the second to `0..31`. This topology shows no
compass orientation and no other sizes. Validate the current bounds. The
resource reader does not normalize.

A ring around a prospective spawn city uses eight neighbors. Where the second
axis clips the ring at an edge, Legendary needs a policy for the failure.
Deduplicate wrapped physical cells before counting them or assigning
identities.

### Legal presence and the native baseline

On normalized supported coordinates, context `-1` accepts a tile that has
presence, clear `0x1001` and a matching terrain and remainder. The terrain codes
`0..6` cover all the selected remainders in the 22 rows. Other codes have no
match. Water and mountain tiles qualify. Filters for movement, land only,
technology and availability therefore cannot define the intrinsic count.

Measure `N` after all native generation and starting writers, including India's
result as it stays in place, and before any policy change. Count unique
physical presence flags whose intrinsic value is `0..21`. Exclude padding,
aliases, definition rows, query results and object counts. Keep forbidden raw
presence in place without counting it.

The target is `min(3*N,L)`, where `L` is the eligible physical capacity. It adds
at most the target minus `N`. A baseline of zero adds zero. Abundant can walk
through the absent eligible cells in finite time and in a deterministic order.
It keeps terrain and unrelated flags unchanged and reports when the capacity is
saturated.

### Save serialization

The selected save passes 1600 terrain bytes and 1600 flag halfwords through
`0x82CC4040`. On the default stream, `0x822DE688` forwards the live terrain to
`+8`, and `0x822DE7A0` walks the current flags through `0x822E1338`. The
returns, the compression, the finalization and the state staying unchanged
until each read are still required. A nonzero alternate stream changes the
source behavior.

The raw planes need no refresh of cached terrain or presence. Four things
remain separate open questions: the consistency of derived objects, the success
of the save, the mode `1` readers, and the reload and reconstruction of changed
tiles.

### Title implementer contract

1. Validate the bounds. Wrap the first coordinate, clip the second,
   deduplicate, and use a stride of 40. Keep the initial Settler anchors.
   Abundant keeps valid resources. Strategic keeps the native floor. Legendary
   keeps terrain, allows duplicates and can replace resources in a ring.
2. Strategic chooses its coordinates before conversion. Iron needs Hill `4` and
   `(a+b)%3==0`. Oxen needs terrain `1` and `(a+b)%4==0`. Both need presence
   and clear `0x1001`. Terrain alone cannot force an identity.
3. Use rings of radius one with eight neighbors. Abundant keeps terrain and
   targets at most three times the count after the native writers. Resolve
   clipping and overlaps in finite time. Legendary allows duplicate ordinals.
4. Authorized conversion writes terrain before presence and the callback.
   Legendary publishes identity without terrain changes. Require that the
   query, growth, allocation, construction, dispatch and manager insertion all
   complete, with state that stays valid. A nonempty query shows no
   replacement, and callback returns are not success flags.
5. Conversion needs either an exclusive point before any consumer runs, or a
   complete refresh of visuals, the minimap, routes, cities and AI. Save the
   final planes as they stand. Validate the visible state and the reload
   separately. These findings certify no safe live-edit API.

## Abundant and Legendary feasibility

The
[feasibility boundary](../../manifests/resource-density-generation.json#/abundantLegendaryFeasibilityBoundary)
records the consumers, locators, capacity and conditions. Abundant can add
native resource-presence flags under those conditions. Legendary preserves
terrain and allows duplicates, but needs identity overrides when the chosen
resource does not match the native lookup. Both need correct timing, consumer
coverage and new-object handling. Changing a visible resource also requires
replacing its existing object.

### Presence consumers

Presence `0x20` lives at `0x8312A608+2*(40*a+b)`, separate from the terrain
renderer. The stores in the procedural function `0x82D0F0D0` at `0x82D10508`,
`0x82D10608`, `0x82D10708`, `0x82D10808` and `0x82D10930` follow the conversion,
RNG and count checks. The record stores `0x82D1AE04` and `0x82D1C40C` and
India's store at `0x82D23324` carry the qualifications given above. Twenty
direct reader calls are mapped. The indirect, independent and cached consumers
are not fully mapped.

| Consumer | Live or cached | Native locator and consequence |
|---|---|---|
| Intrinsic type and availability | Live planes | `0x82CF1558(a,b,context)` recomputes the type. Context `-1` skips the player's technology filter. |
| Food, production, trade | Live input to the components; stored city credits are separate | The reader calls at `0x82CF1F0C`, `0x82CF1CAC` and `0x82CF1A44` see the current presence when the city is recalculated. |
| City candidates and assignments | Live input, stored result | `0x82D016D8` and `0x82D019D4` do not run merely because a flag changed. |
| City work and neighbor type bitsets | Cached | `0x82D13EA0` and `0x82D14358` feed `1<<q` city words. Old bits need a reset or rebuild order that is shown to work. |
| AI candidate score | Live selected calculation; broader state unknown | `0x82D027E8` reads the type before the definition valuation. Strategic caches and queued decisions are not tied to this finding. |
| Setup counts | Live when computed; earlier decisions stay in place | `0x82D2456C` and `0x82D24778` come before the post-setup recount and are not Abundant's global baseline. |
| Resource models | Cached objects fed by the live type | `0x82D7D974` forwards the type. `0x82D7FD18` skips creation and type replacement for a nonempty query. |
| Resource availability and discovery | Live query, stored object byte | `0x82E53F34` and `0x82E544AC` do not show that every later object refresh follows. |
| Tile detail | Live on refresh; the displayed UI is separate | `0x82DECEB8` and `0x82DECEE8` query the identity and availability before the detail is built. |
| Notifications and founding | Live selected calls | `0x82CE8080` and `0x82CEA998` search for types. `0x82D1A11C` can lead to clearing the center's presence at `0x82D1A148`. |
| Minimap and fog | Unknown | No exact reader, cache or refresh function is linked, and the resource callback does not show coverage. |
| Save and load | Live raw planes; reconstruction is separate | `0x82CC49B4..0x82CC4A18` transfers terrain and flags on the default stream. Successful reconstruction of derived state holds only under conditions. |

The
[mixed-identity
observation](resource-identity-overrides.md#mixed-identity-observation)
rules out any claim that an identity hook works for every consumer. A cached
old city bit or an independent bonus formula is a possible explanation, not an
established cause.

### Legal capacity and native identity

`0x82CF1558` takes `r3=a`, `r4=b` and `r5=context`. It requires presence, clear
`0x1001` and a matching terrain and remainder. A tile without presence could be
eligible if `0x1001` is clear and the normalized terrain is `0..6`. No spacing,
river or land-only test appears. Any stronger native placement legality is not
yet established.

Abundant keeps resources and terrain. It counts the final unique native
resources. It then selects absent eligible cells at random, in a finite and
reproducible order, up to `min(3*N,L)`. It logs the achieved count and any
saturation. `N=0` targets zero. No identity override is needed. The callbacks,
the parity of caches and the timing of the baseline hold only under conditions.
All 22 types are algebraically possible without terrain writes wherever a
matching terrain exists:

| Existing terrain | Native valid definitions, in remainder order | Legendary choices |
|---|---|---|
| Sea `0` | Dye `10`, Whale `16`, Fish `18` | Fish `18` |
| Grassland `1` | Oxen `0`, Wheat `20`, Cattle `19`, Incense `11` | Random Oxen, Cattle or Wheat |
| Plains `2` | Wine `8`, Marble `13`, Silk `14` | Random Wine or Marble |
| Forest `3` | Rubber `5`, Oak `9`, Game `17` | Oak `9` |
| Hill `4` | Iron `1`, Coal `3`, Aluminum `6` | Iron `1` |
| Desert `5` | Sulfur `2`, Oil `4`, Spices `12` | Spices `12` |
| Mountain `6` | Uranium `7`, Gems `15`, Gold `21` | Random Gems or Gold |

The [definition matrix](resource-definitions.md) starts at `0x82F6FAD0` and has
22 rows of `0x44` bytes. Terrain is at `+0x40` and the remainder at `+0x42`.
Mountain means terrain `6`. It is not a class inferred from the unnamed
`+0x41`. Unsupported terrain has no match. The layout of two Grassland, two
water and two Forest tiles is an assumption supplied from outside the native
evidence. It is not an established native count for every ring.

### Legendary identity choices

For normalized `s=a+b`, the divisor is four on Grassland and three on other
terrain. Draw a permitted target first. If `s % divisor` already matches the
target's remainder, the tile needs only presence `0x20`. Otherwise, override
with the target's remainder on the same terrain. Eleven targets are available:
Balanced's Oak, Oxen and Fish, plus eight more:

| Terrain | Additional override targets and remainders |
|---|---|
| Grassland | Wheat `20`: `1`; Cattle `19`: `2` |
| Plains | Wine `8`: `0`; Marble `13`: `1` |
| Hill | Iron `1`: `0` |
| Desert | Spices `12`: `2` |
| Mountain | Gems `15`: `1`; Gold `21`: `2` |

Native Oak requires `s%3==1` and Fish requires `s%3==2`. On Grassland,
remainders `0`, `1` and `2` give Oxen, Wheat and Cattle, and `3` gives Incense,
so every permitted draw on a tile with remainder `3` needs an override. On
Plains, remainders `0` and `1` may match. On Hill, `0` may match. On Desert, `2`
may match. On Mountain, `1` and `2` may match. Other remainders cannot. Always
selecting the native identity changes the randomness that was requested.

Targets that do not match the native remainder keep the mixed-identity risk.
This does not show that every such target is defective, and it does not show
the cause. Native matches with no active or stale override avoid that source of
disagreement. They still need the checks on presence, caches and visuals. Keep
the native technology and context filtering.

Allowing duplicates removes the need for enough distinct resource types. Freeze
one choice per physical cell across overlapping rings. Keep all centers, even
inside other rings. Resolve conflicts from clipped, forbidden and unsupported
cells and from fallbacks before any write. For an impossible start, log it and
keep Normal. Another ring must not invalidate that fallback.

### Terrain construction and hook contract

`0x82C6EB14` calls the snapshot builder with `r3` set to the terrain object,
`r4=0x8312B288` and `r5=40`. `0x82C6AEB8` uses the fixed plane and stride. It
frees the old `+0xF4` at `0x82C6AEE8`, allocates and copies the rows at
`0x82C6AF28..0x82C6AF54`, allocates or reuses `+0xF0`, and writes the cell
classifications. Because of the allocation, the helpers and the dependent
state, this is a construction and not a safe live refresh. Invalidating height,
blending, lightmaps, the minimap, fog, path search, strategic AI, city work and
credits, and geometry is not tied to any code. Patching snapshot bytes is not
enough. Legendary avoids terrain changes, but the open questions about resource
state remain.

Freeze the policy before `0x82D25254`. At the return `0x82D25258`, `r3` is about
to be copied into `r29`, and `-1` means failure. This is an observation and not
a certified hook point. Visual attempts already happened at `0x82D2332C`,
`0x82D2455C` and `0x82D24768`. The recount at `0x82D2530C` uses `r3=1` and `r4=1`
and passes no coordinates. Neither point shows empty queries or final writers,
and neither shows the order relative to the snapshot or the first render.

Publish the presence and the identity before the call of `+0xF4` on the current
inline receiver `A=0x8314F76C`, with `r3=A`, `r4=a` and `r5=b`. `U32[A]` is the
vptr and not the receiver. The initialized `0x82D7D950` reads the intrinsic
type, dispatches `+0x248` to `0x82D7FCB0`, and then calls `0x82D64B18`. For an
empty query, the allocation, the constructor, the name, the model, the
registration and the lifetime must all complete. A nonempty result at
`0x82D7FD18` leads to `0x82D7FE2C`, which skips the replacement of type and
name. A mod must therefore publish before the first creation, or show that the
object can be disposed of, rebound or replaced. Forest child work can change
even when the terrain stays the same (Balanced Oak). A return or a read-back
does not show that the visual stays in place.

The identity candidate sits just before `0x82CF15C4`, with `r11=40*a+b`, `r8` as
the coordinate sum and `r7` as the terrain base. Substitute only the remainder
on the same terrain. Keep presence, the forbidden-flag and player checks, and
valid zero. The mixed-identity consistency must be settled before Legendary is
used. The selection of the matrix and the reader has high static confidence.
End-to-end feasibility needs the right order and a creation or replacement that
stays valid. Supported terrain `0..6` has choices. Impossible cells use Normal.

Abundant adds native types to tiles that have none. Legendary may replace
existing types. Neither setup nor the recount shows the order from the final
writer to the first consumer. The limits in the consumer table still cover city
bits and credits, yields and bonuses, AI, the detail view, the minimap and fog,
and reloads. Native flags save presence and not the override ordinal. Restore
the frozen policy before the load consumers run, as described in the
[identity lifecycle](resource-identity-overrides.md#persistence).

## Mutation point and native setup order

No common hook point for changing resource state is certified. The selected
native setup path constructs the scene and attempts resource creation before
later player assignment and presence writers. Abundant needs the final native
count. Legendary can change an existing identity. Neither the setup return nor
the recount satisfies both requirements.

The
[mutation point
boundary](../../manifests/resource-density-generation.json#/abundantLegendaryFeasibilityBoundary/mutationSeamBoundary)
records this partial order, the exact registers, the evidence for each step and
the open questions. It does not establish the complete order through the first
frame.

| Selected order | Addresses | Presence, identity and state that stays valid |
|---|---|---|
| Setup enters scene generation | `0x82D25254 -> 0x82D217C8`; `0x82D22A24` current `+0x150(A,1,1)` | The initialized target is `0x82D86A78`. The actual receiver, vptr and target, and the calls that complete, are open. |
| Map generation writes presence | `0x82D86AD0 -> 0x82D0F0D0`; stores `0x82D10508/10608/10708/10808/10930` | Live flag plane. A successful named-map load through `0x82D0ADE0` skips the procedural work. |
| Procedural starts are selected | `0x82D10FC0 -> 0x82D02C58`; stores `0x82D03078/03084` | Stored X and Y arrays, with qualifications for repair and for the excluded slot. A later assignment can swap them. |
| Early observation edge | `0x82D86AD4` | After the generation returns and before the terrain and scene chain that follows. This is not the final native N and not the final per-player assignment. |
| Terrain and resource scene construction | `0x82D86B34 -> 0x82C7E760`; `0x82C6EB14 -> 0x82C6AEB8`; `0x82D86CBC` current `+0xFC` | The terrain snapshot is cached. The initialized sweep `0x82D7E068` reads flags and calls resource `+0xF4` at `0x82D7E12C` only under conditions. |
| Resource-object attempts | `0x82D7D950 -> 0x82D7FCB0`; `0x82D7FD18` | The live intrinsic q feeds the cached object, type and model. A nonempty query skips type replacement. The absolute first successful object is not established. |
| Scene tail returns to setup | `0x82D8744C -> 0x82D7FC48`; `0x82D87458 -> 0x82C6CB18`; return to `0x82D22A28` | Further scene work. These entries are not identified as minimap or fog builds, or as the first render. |
| Player assignment, unit and city requests | `0x82D230E0 -> 0x82CFE908`; X and Y loads `0x82D231B4/231B8`; Settler request `0x82D23258` | Mode `+4==2` skips the coordinate reorder, and other values call the paired swaps. Scenario and city arms also exist. Successful creation and lifetime hold only under conditions. |
| Later native presence and counts | `0x82D23324/2332C`; `0x82D24504/24514`; `0x82D24550/2455C/2456C`; `0x82D24760/24768/24778` | Writes alternate with visual attempts and with the selected intrinsic class counts. These counts are not the map-wide N. |
| Successful setup return and recount | `0x82D25258`; `0x82D25300`; `0x82D2530C -> 0x82D11AD8` | The initialized `+0x54` target `0x82D80AD8` is one `blr`. The recount keeps `0x20`, clears `0xB04` and calls the city calculation at `0x82D128FC`. A complete rebuild is not yet shown. |
| City credits and bits, and AI evaluation | `0x82D016D8/019D4`; `0x82D13EA0/14358`; `0x82D236E4 -> 0x82D02530` | The live q can produce stored credits, ORed bits or decisions. Their complete schedule of resets and builds is not linked to this order. |
| Minimap, fog, first game frame | The exact functions and the order edge are not identified | No evidence covers every consumer or establishes the order before the first render. |

The concrete obstacle is the interleaving. `0x82D24504` can change presence
before a visual attempt at `0x82D24514`, and `0x82D24760` later adds more
presence. If the empty-query and object paths complete, an object can therefore
be created before Abundant's final native baseline exists. Counting early can
omit native resources. Counting late does not come before those attempts.

### Candidate hook and rebuild limits

The point just before `0x82D86AD4`, holding the word `0x3BE00001` (`li r31,1`),
follows the generation call at `0x82D86AD0`. At that point `r30` is the
receiver, `r29` is the generation flag, and `r31` holds the incoming `r5`, which
is about to become `1`. The selected entry point is `A,1,1`. `r3` shows neither
success nor a coordinate. The point runs on every call that reaches it, and it
is not shown to run once per new game. A hook there needs four things: a latch
that accepts the launch, mode `1` or `2`, an actual dispatch, and starts that
stay unchanged. Named maps need a link to the producer. A normal load with
`r4=0` skips it, but other entry points are not fully excluded.

This trace comes before the scene work. Later swaps, later writes and reads of
caches further down the call chain still follow it. A staged policy therefore
has to account for the later writes and for the final count. No complete late
repair exists. `+0xF4` creates only under conditions, the sweep `+0xFC`
(`0x82D7E068`) does not replace objects, and `+0x54` does nothing. The recount
makes no direct call to `0x82D13978`, but indirect calls prevent showing that
it is never reached. The selected city work shows no complete reset of bits,
credits, AI, the minimap or fog. The search for callers of the city bitset reached
its cap of sixteen and was truncated, so the list may be incomplete. Constructors are not a safe live API. These
modes keep terrain unchanged.

The title source freezes and stages Resources before `sub_82D25170`. Balanced
publishes at the recount `0x82D25310`, where the link register is checked. That
is after the optional AI removal and before the recount's own presence work,
refresh and native recount. It does not publish at the call at `0x82D25254`. The
wrapper preamble and `Apply` clear the snapshots, so moving the publication
requires changes to the lifecycle. The revision and digests are in the
[identity lifecycle](resource-identity-overrides.md#persistence).

### Load ordering

Load restores presence and never reruns placement. The default stream transfers
all sixteen flag bits, including `0x20`, when the stream, the order and the
returns behave as required. Overrides need the sidecar. The title stages it
before `bctrl 0x82D844C8` (return address `0x82D844CC`). At the point before the
call at `0x82D86674`, it clears and republishes the state before
`0x82CC4040(1,frame+0xC0,r29)`. Terrain at `0x82CC49AC` is transferred before
flags at `0x82CC49F4`.

On the route where `r29==0` stays true, `0x82D86870` calls `0x82D7F550`, which
dispatches `+0x150(A,0,arg)` at `0x82D7F5C8` and reaches the sweep at
`0x82D86CBC`. Afterward, `0x82D7F614` calls `+0xFC` again. Restoration comes
before those consumers, provided the target, the frame, the globals and the
calls stay unchanged. The earlier header path `0x82D8645C` to `0x82CC29B8`, the
dispatches, the alternate routes and streams, the aggregates and the first
frame are not linked to this order. Validation of the emitted hook and the
consistency of Oxen and Cattle are separate open questions.

### Placement legality beyond intrinsic lookup

No general validator for spacing, rivers, coasts or reservations is shown. A
clear `W&0x1001` and terrain `0..6` make a tile potentially eligible by its
intrinsic value. The reader also requires presence. When `W&0x400` is set, the
sweep selects `+0x100` instead, before `W&0x30` permits `+0xF4`. The meaning of
that bit is unknown. A cautious host can exclude `0x400`, which reduces the
usable capacity below the intrinsic `L`. Let `K` be the number of usable absent
cells, so `C=N+K`. The target is then `min(3*N,C)`, and existing resources stay
in place. `0x1401` is not a universal legality mask.

The sampler `0x82D246F4..0x82D24710` accepts terrain `6` without presence.
Rejections increment the counter at `0x82D24714`. When the counter reaches
`9999`, the code falls through without rechecking. The counter increments before
the first draw and spans successful outer passes. It therefore does not count
`9999` draws, and it is not a reliable general check.

Freeze the policy once per accepted launch. Keep terrain, centers and native
resources unchanged. Define which cells the host accepts, measure the final N,
select in finite time, and log the capacity and the count. Publish before the
affected reads and the first creation, or show that the objects are replaced
and the caches rebuilt. No address identified so far satisfies all these
requirements.

## Paired new-game setup probe contract

The
[probe
contract](../../manifests/resource-density-generation.json#/abundantLegendaryFeasibilityBoundary/mutationSeamBoundary/pairedSetupProbeContract)
defines twelve required fixed sites, optional diagnostics, the exact original
instruction words, and the coverage needed to interpret their order. They are
verified native boundaries. They are not a run-time result and not a guarantee
that an emitted hook works.

The capture consists of one accepted mode `1` launch and one accepted mode `2`
GOTW launch. Both use the same supported build, content, loadout and settings,
with native Normal Resources, and each uses a fresh title process. Record the
actual map, seed, week, scenario, difficulty and players. The two modes need
not produce the same map.

Observe only: do not add resources, found a city or open extra UI to force an
unexercised cache in this capture.

Every row records an epoch, a monotonic 64-bit sequence number, the thread, the
PC, the LR, the frame or call ID, and `G=U32[0x8314EFC8]` with
`mode=U32[G+4]`. The setup global is a pointer cell. The mode is not
`U32[0x8314EFCC]`. Tile rows also include the raw coordinates, the effective
address, `idx=40*a+b`, the current flag halfword and the terrain byte. Record an
unknown player or ordinal explicitly as unknown.

A predicted intrinsic ordinal is not the reader's actual player-filtered
return. Keep ordinal zero. All hooks observe before the listed instruction,
preserve guest state and execute that instruction once. Logging must not call
native helpers or RNG.

Attributing a read to a nested consumer also needs matched invocation exits and
tail returns, taken from transparent wrappers or from a trustworthy observation
of calls and returns. These are additional observer events and not more fixed
guest sites. A token recorded only at entry must not survive a return. Without
matched scopes, the outer consumer is unknown.

| Required site | Function | Record beyond common fields | Frequency and question |
|---|---|---|---|
| `P01 0x82D217C8` | `0x82D217C8` | Entry `r3..r8`; snapshots of the planes and starts, and the player count and exclusion | Per setup invocation. Where does setup begin, including retries? |
| `P02 0x82D86AD4` | `0x82D86A78` | `r30=receiver`, `r29=generation flag`, `r31=incoming r5`; current vptr and slots, and snapshots | Per generation return. Does this candidate come after the final starts and writes and before the consumers? The selected setup values are `A,1,1`; `r3` is not success. |
| `P03 0x82D25258` | `0x82D25170` | `r3=setup result` before copying to `r29`; snapshots | Per setup return. `-1` is failure. What preceded the accepted return? |
| `P04 0x82CF1558` | `0x82CF1558` | `r3=a,r4=b,r5=context`, entry LR, `r16..r31` | Per tile and query. The first identity reads, including the count link registers `0x82D24570/2477C`, taken before classification. The actual q is not yet returned. |
| `P05 0x82D7FD00` | `0x82D7FCB0` | `r28=receiver,r31=a,r29=b,r26=q_input`; descriptor at receiver `+0x208` | Per query with nonnegative q. Does it find an empty result and create an object, or a nonempty result and skip? Creation from a null start skips `0x82D7FD18`, so that branch alone is not enough. |
| `P06 0x82E54250` | `0x82E54250` | `r3=object,r4=a,r5=b,r6=q`; object generation and checked 0x84-byte watch | Per constructor and tile. The first construction activity, including from other callers. This is not a live registration. |
| `P07 0x82D00C78` | `0x82D00C78` | `r3=city`; checked record, owner and coordinates, and a record watch | Per city calculation. The first candidate, yield or resource work. Entry alone does not show that a build happened. |
| `P08 0x82D13978` | `0x82D13978` | `r3=city,r4=raw mode`; same record and watch | Per city update. The first entry to the function that writes the bitset, then the actual clear, OR and credit stores. |
| `P09 0x82D02530` | `0x82D02530` | `r3=a,r4=b,r5=raw evaluation context` | Per AI candidate. The first evaluation, then its reads and stored decisions. Do not assume `r5` is a player. |
| `P10 0x82D92590` | `0x82D92590` | `r3=cache object`; `r4..r8` and the old five words | Per overlay setter. Detect the first comparison and any reuse as well as updates. The values map to `+6C/+74/+70/+78/+7C`; they are not ordinals. |
| `P11 0x82D931B8` | `0x82D92FA0` | `r29=a,r30=b,r31=owner,r26=cache`; `r3,r27,r23,r24,r25` | Per tile overlay update after the yield queries. Which tuple reaches the setter? This is an interior return point and not a function entry. |
| `P12 0x82D25310` | `0x82D25170` | Raw `r3,r29`; snapshots of the planes and starts | Per recount return. What happened between the setup return, the title publication and the end of the recount? `r3` is not a certified status. |

For P07 and P08, the city record is at `0x8314FE28+0xBC*slot`. It has a signed
owner byte at `+0` and signed coordinate halfwords at `+0x30` and `+0x32`. Check
the mapped ranges, and do not guess a slot limit. P11's owner at `+0x70`
supplies a city selector when it is valid. Its numeric outputs are helper
results and not resource types.

The overlay setter compares five old values before its early return on
equality. Changed values are stored at `0x82D92678/67C/684/688/68C`. P11 follows
the food query at `0x82D931B4` and comes before the setter call at `0x82D931D0`.
Entry probes alone cannot tell a build from a reuse. Correlate the actual reads
and writes, and the object generation IDs.

### Required coverage outside the fixed-site count

Twelve fixed hooks are not an exhaustive census of last writers or caches. The
following are additional required observer capabilities. If they are
unavailable, the fixed-site capture is diagnostic and its completeness verdict
is inconclusive.

Observe committed writes of every width, including bulk, host and atomic
writes, to:

| Region | Range |
| --- | --- |
| Full flag plane | `[0x8312A608,0x8312B288)` |
| Terrain plane | `[0x8312B288,0x8312B8C8)` |
| Start arrays | `[0x830E343C,0x830E347C)` |
| Active-start selector words | `[0x82F700AC,0x82F700B4)` |

The last range holds the signed 32-bit count `C` and the excluded ordinal `E`.

Keep their raw bits and every transition, together with the mapping of active
and excluded slots. Snapshots alone do not show that values stayed unchanged.
The supported array model requires a count of `0..8`. Keep the bytes before and
after, the PC, the width, the origin, the sequence number and the affected
halfwords. Record the last physical flag store separately from the last actual
change to `0x20`.

An idempotent old-word store can overwrite a hypothetical addition. It is not
automatically harmless. Capture other flag changes, including `0x80`, `0x400`
and `0x1001`. No separate native per-tile ordinal plane is established.

Observe resource-input reads through those planes and the definition rows
`[0x82F6FAD0,0x82F700A8)`, including aliases of the common reader and paths
that bypass it. Classify each observed reader and correlate it with the
accepted map of twenty call sites and the active invocation IDs. Unknown
readers and independent fields keep open the claim that every consumer is
covered.

Watching native planes does not show that an independent stored identity or
cache source is absent. Dynamic watches on objects, cities and overlays record
the derived fields that have been located. They do not cover all strategic AI,
minimap or fog state.

The tile and detail output may be filtered, and repeated samples may be capped.
Complete summaries must still be kept: the stores and first consumers for each
cell, the counts of distinct PCs and targets, and the global first object and
cache events. Account for all 1600 backing cells, and mark the 1024 playable
cells separately.

Dropped required events, unsupported write forms or unordered visibility across
threads invalidate a positive result. A sequence number allocated before an
unsynchronized store is not proof that the write was visible before the next
event.

Arm the capture at the host transaction that accepts the launch, before native
setup. Continue past P12 through a qualified first gameplay frame, plus the
final snapshots and the status of pending work. Loading and menu presents are
not that boundary. No exact guest first-frame PC is certified here.

Record the title's clear, publish and apply events and any host plane writes in
the same sequence. The native-baseline runs must make no resource-policy
changes. Keep retries as separate invocations.

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

The events for constructors, type stores and managers tell attempts apart from
local work that completes. None alone shows that visible state stays in place.
Logging of actual returns must cover both reader exits. P05 records a captured
input. It is not by nature a return from the intrinsic reader.

That label needs the actual link among the reader in context 1, the current
dispatch and whether state stays valid. An unknown caller does not inherit the
label.

### Pass, fail and inconclusive results

A strict shared global hook point is one instruction `S` that serves both
accepted modes. It requires complete ordered coverage, and every source and
cache must be classified by the code that writes it. It then requires:

`max(final X/Y/C/E write, final native relevant-field store) < S < first resource construction/cache input`

Use physical stores for this sufficient criterion, including idempotent ones.
Four more things are required: starts and planes that stay unchanged until the
full set of consumers has run, an unambiguous check that lets the accepted
launch through only once, legal current terrain and flags, and a final unique
intrinsic native count that does not depend on any player's technology.

A later store needs separate evidence that its fresh read-modify-write keeps an
added bit before the criterion can be relaxed. A trace where the bit happened to
remain zero is not enough. Earlier cache work likewise needs a complete later
reset or rebuild.

Affected objects, caches or counts that are created earlier and are kept
without replacement or reset, or later native writers of presence, terrain or
starts, rule out that strict candidate. For Legendary, a nonempty object query
on a changed identity needs replacement. Another `+0xF4` call does not supply
it.

Kept objects outside Abundant's affected absent tiles can be harmless in a
narrower per-tile analysis. That analysis must not be reported as the shared
global hook point.

Six conditions make a result inconclusive: unknown readers or fields, lost
events, unordered threads, unexercised caches, ambiguous epochs or endpoints,
and incomplete evidence about object lifetimes. A cache that is not entered
during the pair remains untested. Its absence or safety is not shown. These two
observer-only launches can show an observed order or reject a candidate.

They do not show that added resources reach every consumer or work on all
supported maps. That needs a separate controlled check, with a mutation that
only adds presence, once the questions of ordering and coverage are settled.

Mode `3` normal load is a separate follow-up. It covers the staging and reset at
`0x82D844C8/86674`, the plane transfer and later sweeps. It is excluded from
this pair. Load restores saved presence and must not rerun placement.

## Practical limit

The result identifies four native writers and a count check that decides
eligibility in the selected conversion pass. The selected scenario alias path
reads other fields, and a separate placement leaf sets flag `0x80`. Neither
establishes a control over the density count.

Increasing all resources, or guaranteeing Iron or Oxen near the initial Settler
spawn, still needs seven things: completed nearby placement and refresh, legal
terrain, completed start production, the right setup timing, a creation that
stays valid, a deterministic order, and a limit on failures.

The mapping from players to coordinate requests above gives an anchor contract,
with those execution conditions and conditions on unchanged state still open.
The candidate after the loop gives a place to schedule work.

One payload and getter case that stays valid establishes the predicate's return
value. The actual query membership, whether the constructor's child stays
valid, growth and the refresh of new objects remain qualified. The post-setup
contract gives arguments about geometry, topology, intrinsic counting and the
raw save planes, each with its exact conditions. No real consumer of
`RESOURCEDENSITY` is identified.

Tuning that depends on normalization needs its earlier producer and its actual
value.
