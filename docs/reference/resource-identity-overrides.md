# Resource identity overrides without terrain stores

A mod can make a tile show Oak, Oxen or Fish without changing its terrain.
This works through hooks that hold only under stated conditions, and through
the paths that create new models. Oak also changes the child flags of Forest,
so keeping the terrain does not guarantee the same appearance. The title
freezes the Resources setting before setup, so a pending Balanced choice can
control India's starting resource. It publishes the tile changes at the
recount, which comes after the native attempts to create objects.

The
[override boundary](../../manifests/resource-identity-override.json)
records the static read sets, calls, confidence and limits.
[Resource definitions](resource-definitions.md) cover the IDs and access.
[Tile changes](resource-placement.md#post-setup-tile-changes) cover the terrain
snapshot, the topology and the refresh. A reported terrain-swap drawing problem
is separate run-time context. The mixed-identity report has no captured trace
from a trace build and no ordered list of consumers that would show its cause.

| Question | Verdict | Confidence |
|---|---|---|
| Every identity consumer shares one helper | Holds only under conditions: 20 direct calls are listed, and the selected inventory of definition-base uses shows no inline duplicate of the helper. Whether every subsystem is covered is open. | Strong |
| A fresh object follows the overridden type | The request for the new type and name is shown. Allocation, model fulfillment and whether the object stays valid hold only under conditions. Existing objects are not replaced automatically. | Strong |
| An unused, persisted native tile field can hold the override | Holds only under conditions: the save transfers the full flag word, but no field is certified unused and kept through load. | Strong |
| Forest terrain plus Oak preserves identical trees | Disproved for unchanged child state. Native Oak can change Forest child flags. Whether the visible appearance is equivalent is unresolved. | Strong |
| A policy applied only at the recount can control India, and removing the whole branch preserves the RNG state | Disproved. The current source freezes Resources earlier. A narrow skip of the store and callback keeps the explicit random draw. | Confirmed static order; source implementation qualified |

## Identity consumers

A census of every aligned direct branch found 20 calls to `0x82CF1558` and no
other branch that is not a link. The manifest lists the callers, contexts and
uses:

| Surface | Static route and limit |
|---|---|
| Food, production, trade | `0x82CF1CE8`, `0x82CF1AF0` and `0x82CF17C8` call the helper at `0x82CF1F0C`, `0x82CF1CAC` and `0x82CF1A44`. The contribution helpers `0x82CF1698` and `0x82CF1730` also call it. |
| City candidates and work tiles | `0x82D016D8`, `0x82D13EA0` and `0x82D14358` use the helper. The latter two OR `1<<q` into a city resource word. Credits computed earlier and the screen refresh are separate. |
| Tile tooltip and resource detail | `0x82DECEB8` obtains the intrinsic type. `0x82DECEE8` checks player availability. `0x82DECF30` then forwards the type and coordinates to `0x82DEAB38`. `0x82DE01DC` also checks availability for the selected tile. |
| Resource visual | `0x82D7D974` reads the intrinsic type and forwards it through receiver `+0x248`. `0x82E53F34` and `0x82E544AC` use the same helper to check eligibility and availability. |
| Candidate valuation | `0x82D027E8` reads the intrinsic type. `0x82D027F4..0x82D0283C` uses its definition contribution and technology. This list and the city scoring do not cover every strategic AI consumer. |
| Trade and monopoly aggregation | Trade yield and the city bitsets of type presence share the helper. No function that counts monopolies across the whole game is established. A bitset is not an occurrence count. |
| India UEA39 | The same helper performs the technology query at `0x82CF1638`, UEA39 at `0x82CF1650`, and then the civilization 10 fallback. These checks accept the selected type. They do not derive a different one. |
| Minimap | No minimap function is linked to this inventory. An empty search of the defined strings does not show absence, and it does not show coverage by the common helper. |
| Save and load | The selected plane serializer transfers terrain and flags. It does not store a separate override ID in those planes, and it does not classify their resource type. Saved aggregates and reconstruction are separate questions. |

The manifest also lists the other calls for notifications, locations, founding
and counts. Twelve exact-base sites in ten functions use the definition base.
Among them, only `0x82CF1558` maps terrain and remainder to a row. The ranges
`0x82CEA16C..0x82CEA1A8` and `0x82CF0630` compute contributions from an
existing ordinal. They are not duplicate hooks. Longer aliases, other bases,
dispatch and independent formulas are outside this negative result.

## Mixed identity observation

The
[runtime qualification](../../manifests/resource-identity-override.json#/runtimeEvidence/mixedIdentityObservation)
records Balanced Oxen on native Grassland whose remainder selects Cattle. The
tile behaved as Oxen, and the Romans with Code of Laws also received Cattle
food. Whether every consumer agrees on the identity stays open despite the
direct census. A trace must tell four causes apart: stale bits or credits, an
independent formula, a bypass, and an error in the hook, the context or the
ordering. The cause is unknown. Legendary keeps this open question. Abundant
that only adds presence can keep the native identity.

## Override and fresh visual creation

Returning unconditionally from `0x82CF1558` would skip the checks on presence,
forbidden flags and the player. A hook must keep those checks and must keep
valid Oxen `0`. Only `-1` means absence. Just before the instruction at the
mid-function address `0x82CF15C4`, `r11` holds the physical index `i`, `r8`
holds the sum and `r7` holds the terrain. When the terrain matches, replace
only the full `r8` with the chosen remainder:

| Current terrain | Chosen ordinal | Synthetic sum |
|---|---:|---:|
| Forest `3` | Oak `9` | `1` |
| Grassland `1` | Oxen `0` | `0` |
| Sea `0` | Fish `18` | `2` |

The divide at `0x82CF15E4..0x82CF15FC` feeds the normal row matching. The
technology, UEA39 and civilization 10 checks follow. Each terrain and remainder
pair is unique, so a rejected choice cannot select another matching row. An
earlier overflow trap keeps the original sum. The canonical range `0..31`
excludes that exceptional case. Three things are still required: the hook must
be emitted and work at run time, its inputs must stay stable, and other state
must stay unchanged.

| Fresh visual edge | Contract |
| --- | --- |
| `0x82D7D974`, `0x82D7D97C` | Return `q`, copy it to `r6` and dispatch through `+0x248` to the initialized `0x82D7FCB0`. |
| Empty query `0x82D7FD44` | Calls `0x82E54250(a,b,q)`. Stores the coordinates at `+0x70` and `+0x74` and the type at `+0x78`. |
| `0x82D7FD58..0x82D7FD68` | The name comes from `0x82F6FAD0+68*q`. `0x82D7FD84` dispatches through `+0x14` and the installed cell `0x82132ACC` to `0x82E544E8`. |
| Setter | Prepares the name, stores `+0x10`, calls `0x82C63320` at `0x82E545D4`, then the lookup `0x82C92950` at `0x82C63364` and `0x82C633D4`. Later special placement reads the stored `q`. |

The chosen type and name request the model's identity. Allocation,
fulfillment, registration, lifetime and appearance hold only under conditions.
When the query result is nonempty, `0x82D7FD18` leads to `0x82D7FE2C`, which
neither compares nor changes the old type and name. Repeating `+0xF4` does not
replace the object. Changing only `+0x78` leaves the object inconsistent. A mod
must show that the object can be rebound or replaced. The setup calls of `+0xF4`
at `0x82D2332C`, `0x82D2455C` and `0x82D24768` come before the recount
`0x82D2530C` to `0x82D11AD8` (link register `0x82D25310`). The recount is too
late for fresh objects. Earlier timing alone does not show an empty query, and
it does not show the final writers.

## Persistence

No native tile storage is certified as unused. That does not show that none
exists. The default save at `0x822DE7A0` visits 1600 halfwords through
`0x822E1338` and writes two bytes through `+8` at `0x822E1400`. The load at
`0x822DE720` visits 1600 halfwords through `0x822DEC88` and reads two bytes at
`0x822DECB8`, with a byte swap that applies only under a condition. No mask is
applied, so all 16 bits transfer when the stream, the order and completion
match. Later writes can erase them. The recount at `0x82D11BD4..0x82D11BF0`
applies `0xF4FB`, which clears `0x0B04`. The known masks `0x1001`, `0x20`,
`0x411` and `0x1000`, together with an incomplete census of aliases, readers and
writers, certify no spare bit, plane or padding. Alternate streams and
reconstruction are separate questions.

A sufficient sidecar contains four things: a schema, the frozen policy, the
identity of the rule and configuration, and sorted unique records of
`(tileIndex U16, ordinal U8)`. Three records use nine payload bytes, not
counting the header and the save identity. If the roles of Oak, Oxen and Fish
are fixed, the sidecar could use three U16 indices plus a way to encode
absence. This is not a native format and not a proven minimum. Multiple starts
need rules for conflicts.

The [save hook points](save-storage.md) are tied to the selected user and
device namespace and to the normalized filename at `+0x108`. The load hook
point sits before `bctrl 0x82D844C8` (return address `0x82D844CC`). The save
hook point sits after the final `0x82D829E8` with `r25!=0`. The sidecar should
record the native digest or an equivalent generation identity. Replacing the
file atomically after a successful save lets the digest detect a crash between
the two files. The sidecar must be restored before the code that reads identity
and models. Failure, mismatch, a missing sidecar, autosaves and rollback each
need a defined behavior. The reset at `0x82D86674` must not later erase the
restored state.

The inspected revision `789e0b7fcc8f29c76fac2af1b93e959953a79cf4` implements
sidecars. The manifest entry `persistence/existingTitleState` records its
hashes and locators. It does not cover every checkout or every running binary.
On load, the title captures the filename and stages a validated payload that is
tied to the digest, before `0x82D844C8`. At the hook point before the call at
`0x82D86674`, it clears the old state and then publishes the staged snapshot.
This happens before the other settings and the native continuation. A missing
or rejected sidecar logs a fallback and restores no overrides. Pending state
lasts only for the transaction. Native loads have no rollback.

When `r25!=0` at `0x82D829E8`, the title writes, flushes and atomically
replaces the sidecar. A failure is logged, and the native save is not rolled
back. Distinct autosaves are not certified. The
[selected load order](resource-placement.md#load-ordering) links publication to
the default planes and to two later sweeps. It does not cover the earlier
header, the earlier dispatch, alternate routes or all caches. Restoring the
state before every reader, and a visible reload, are not yet shown.

## Forest and Oak

Terrain `3` stays Forest, and the terrain snapshot stays unchanged. Setting
presence `0x20` leaves the final branch on `W&0x411` unchanged. The Oak setter
is a separate path. `0x82E544E8` routes IDs `5` and `9` to `0x82E54C14`.
`0x82E54C30` then dispatches through `+0x11C` with the coordinates, mask `7` and
Boolean `0`. When the first child matches, the call chain is `0x82D7ED00`,
`0x82E3DC80`, `0x82E3D7D0`. If the type 3 model stays valid, that chain
resolves slots 0, 1 and 2 and calls `0x8234BDB8(child,1,1)`. That call ORs `1`
into scene `+0xA8` and takes a recursive path.

Finally, `0x82D64B18` separately queries Forest through `+0x120` and updates
matches through `+0x118` and object `+0x48`. This requires live links to the
scene objects and callbacks that complete. Oak can change existing scene state
even though the terrain is unchanged. Whether the trees look identical needs a
visual comparison. Bypassing the child work is a different policy.

## India order and suppression

Setup at `0x82D25254` includes civilization 10 before the recount at
`0x82D2530C` (link register `0x82D25310`). The title freezes and stages
Resources before native setup. It consults the pending Balanced choice at the
store hook and publishes the tiles later. Publication alone cannot repair an
object identity that was set earlier.

Removing the whole branch changes the RNG state: the counter at `0x82D2328C`,
the state at `0x82D2329C` and the possible reduced state at `0x82D232B4`. A
jump from just before `0x82D23324` to `0x82D23330` reaches the count reload at
`0x82D23938`. It skips the store and refresh at `0x82D2332C` and keeps the draw
and the offset. Skipping only the call leaves the presence flag set. Skipping
only the store still refreshes. `r3` is unused before the paths merge, so no
synthetic success value is needed.

This shows the local flow. It does not show anything about writes made by the
omitted callback, RNG use further down the call chain, or equivalence with full
setup. Keep the player, coordinates, count, frame and save state unchanged, and
validate the hook together with the earlier frozen host and peer policy.

## Title implementer contract

1. Freeze the policy before `0x82D25254`. Normalize and deduplicate the ring
   candidates using the accepted 32x32 topology and a stride of 40. Define
   finite behavior for when a resource kind is missing or when starts overlap.
2. Keep terrain bytes unchanged. Publish same-terrain overrides before the
   first visual object is created. The candidate hook `0x82CF15C4` keeps the
   native identity checks. Validate all affected consumers and keep valid
   ordinal `0`.
3. Show that fresh objects complete, or that existing objects are replaced.
   Decide whether the native Oak child changes give the Forest appearance you
   want.
4. Persist the frozen choices in a versioned sidecar tied to the save slot and
   the digest, until a native field is shown to be available. Cover load
   failure, autosaves and peers.
5. Keep India's native draw. Then skip `0x82D23324..2332C` to `0x82D23330` only
   when the policy requires it. Keep the earlier policy freeze. A choice made
   only at the recount cannot control that arm.
6. Treat seven items as open acceptance checks: the minimap, strategic AI,
   monopoly counts, whether the model stays valid, unchanged terrain bytes
   together with visible output, save and reload, and agreement between peers.
