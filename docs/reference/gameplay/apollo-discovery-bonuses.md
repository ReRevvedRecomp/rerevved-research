# Apollo Program technology and discovery bonuses

The [canonical finding](../../../manifests/apollo-technology-discovery-bonuses.json)
records how Apollo makes technologies count as owned, how its guarded
completion works and what direct acquisition does. Four things are resolved: the
selected native provider, the returned `F` for technology 4, all 46 reward rows
and the native return that applies only under stated conditions. A separate
proposal would grant each eligible technology and present its reward after
native completion work. Scheduling, save and load, and agreement across peers
still need acceptance. This is not an implemented feature, and it does not show
that rewards are delivered during normal play.

## Virtual ownership and raw first-world eligibility

Apollo is item 217, which is normalized Wonder 17, identified independently by
its record. Selected completion publishes the owner and city at `0x830E51D0` and
`0x830E51D4`. The active-Wonder query `0x82CEF4E8` rejects an absent owner of -1
and applies the current setting, the owner and team, and the expiration checks.
Apollo's expiration halfword is -1. Under the supported current state, the
Wonder is active for player -1, for its owner and for the owner's current team.
The extra city comparison that applies to Wonders 4, 9 and 13 does not apply to
17.

The technology query `0x82CEF6A8` calls that query at `0x82CEF704`. Active
Apollo makes supported technologies 1 to 46 return owned before the raw
ownership read. Technology 47 still follows the bit path. Technology 0 returns
false, and the sentinel -1 returns true. Neither query requests acquisition
(`0x82D09208`). This does not establish a separate retail path that actually
acquires all those technologies.

Generic acquisition reads the entire raw word `W=U32[0x830EDC48+4*t]` at
`0x82D09318` and ORs player `p`'s bit at `0x82D0937C`. It has no early veto for
Apollo's virtual ownership. The required resolver and the effects of the
reached source 0 callback come before the read. When `W==0` and `t!=47`, it
writes the first discoverer `p` at `0x82D0932C` and the shared `F=1` at
`0x82D09330`. The source is written at `0x82D09384`. When the low bit of the
phase is 1, the acquisition tally increments at `0x82D093A0`, even when `p`'s raw
bit was already present. Normal science avoids this repeat through its
virtual-ownership check. Direct acquisition is therefore not an isolated reward
API that can be called twice safely.

The unclaimed candidate accepts `t` in ascending order from 1 to 46, and only
when the whole raw word is 0. It rechecks that immediately before each phase 1
call and relies on it through the native read. A word `W!=0` is excluded even
when only another civilization owns the technology, or when source 6
suppression, a recipient failure or another native rule prevented an earlier
reward. Raw ownership, discoverer, source and tally do not show that an award
was delivered. The `W==0` criterion does not track external state changes or
another timeline. It cannot justify repairing or reissuing a bonus whose raw
ownership word is already claimed.

### Claimed state records

These words show that a technology has been claimed. None of them shows that a
reward was delivered.

| Record | Address | Written at | Meaning and limit |
|---|---|---|---|
| Raw ownership | `W = U32[0x830EDC48 + 4*t]`, bit `p` | `0x82D0937C`; `0x82D09378` computes the bit | Test the whole word, not player `p`'s bit and not virtual ownership. |
| First discoverer | `U32[0x830EDB88 + 4*t]` | `0x82D0932C` for old `W == 0` and `t != 47` | Writes `p`. It is not a completed reward receipt. |
| Latest acquisition source | `U32[0x830ED588 + 4*(48*p + t)]` | `0x82D09384` | The accepted source, including exact phase 2. |
| Acquisition tally | `U32[0x830EDD08 + 4*p]` | `0x82D093A0` | Increments for an odd phase, including repeated calls on a raw owned technology. |
| Shared first world `F` | `U32[0x830E3438]` | `0x82D09330` | Set when `W == 0`. Suppressors and nested calls can replace it. |
| Native acquired technology | `U32[0x830EDD28 + 4*p]` | `0x82D09370` | The native write is kept. It differs from selected research. |

At `0x82D093A4` these records can already exist before the Irrigation store at
`0x82D0A3F8` in the same call. Source 6 or a failed native recipient can leave a
raw owned technology with no reward. Such a word stays excluded. A missing
reward does not reopen the bonus.

Source 6 writes the early records before clearing `F`. Exact phase 2 also
writes raw ownership and source, without the odd-phase tally or the Irrigation
store.

## Completion, caller and growth ordering

`completionFinalizationBoundary` ties the pre-helper `0x82D16330` and the
post-helper `0x82D16344` to the code. The reached Wonder branch keeps city `c`
and normalized 17, debits production and copies item 217 to city `+0x3A`. It
clears the current item at `+0x38` only when the saved second entry argument is
0. The helper call is `0x82D16BA0(17,c,1,0)`. Its `r4` is a city, not an
acquisition player. The player `p` must come from the supported city owner, which
must stay valid, and must agree with the published claim. The absent-claim check
and the item clear that applies only under a condition prevent repeats on these
local paths. They do not show that every partially completed attempt can be
retried safely.

Normalized 17 stays selected and bypasses the second mode 2 helper at
`0x82D16374` for either value of the byte check. It then publishes the pending
Wonder bit `0x1000` at city `+0x24`. At `0x82D16388` the original second
argument is reloaded from `frame+0x17C`. A nonzero argument reaches the original
restore and return, provided the frame and return target are intact. A zero
argument reloads the city and calls `0x82CF1060` at `0x82D163BC`. Neither
selected prefix requests acquisition.

The selected Calendar caller sets the second argument to 0 at `0x82D1FC0C`,
copies city `r25` to `r3` at `0x82D1FC10` and calls `0x82D13978` at
`0x82D1FC14`. The city loop uses stride 188 and positive signed population. The
callee saves the city at `frame+0x174` and the second argument at `+0x17C`, and
it samples the city's signed owner. This is a native caller that applies only
under stated conditions. It is not an observed completion by a human player, an
AI player or a peer, and it is not a census of every caller.

`completionGrowthContinuationBoundary` links the zero branch to the accepted
[city growth threshold](../../../manifests/city-growth-threshold.json). One query is
compared with the signed progress at `+0x34`, and a separately requested result
supplies the subtraction. The accepted branch clears city `+5` and increments
population at `+3`. A separately sampled halfword chooses the limit 9, 17 or 32.
Reaching the limit replaces population with limit minus 1 and clears progress.
Both outcomes at the limit next request `0x82D00C78` at `0x82D16440`. These are
local limits that apply only under conditions. They are not a general population
cap and say nothing about the current selector.

The successor for insufficient progress, `0x82D168AC`, reads unsigned progress
and branches below `0x8000` to `0x82D1697C`. Otherwise it clears progress,
decrements population at `0x82D168C8` and requests `0x82D00C78` at `0x82D168CC`.
The selected growth prefixes request no acquisition. That does not show that
other helpers or later paths never request it. This city growth is distinct from
the Irrigation reward.

## Sharing, provider and returned technology 4 F

For `W==0` and `t!=4`, the accepted path with one ownership bit bypasses sharing
before the native suppressors. Technology 4 additionally samples `q` at
`0x82F700B0`. When `q==p`, one raw bit stays. When `q!=p`, a second bit is added
at `0x830EDC58`. The sentinel -1 skips the extra store. The initialized value
`q=7` is not evidence of the current value. With a positive supported player
limit, the selected 16-bit count can accept source 5 recursion at `0x82D094BC`
and `0x82D0951C`. Exact phase 1 excludes the second branch, but not necessarily
the first. The outer `F` is not saved and restored around recursion.

The first selected recursive tuple is `(j,4,-1,5,1)`. The exact argument moves,
the complete query and the original save25 and restore25 suffixes keep
`r5=-1`. The usual ABI rules alone would not preserve that volatile register. In
the accepted case of a query that does not recurse, `F1` still reaches
`0x82D09548` when both acceptance checks are false. Active Apollo can make the
visited ownership query true and exclude the first recursion. A clear phase mask
2 independently excludes the second. These are static cases that depend on
conditions. They are not observed player or team state.

At `0x82D0A778`, let `M` be the manager, `S` the child and `Q` the result:

`M=U32[0x8314EFE0]`, `S=U32[M+0x10]`, `Q=U32[S+0x20]`.

The accepted registered child `S` has the installed vptr `0x8215FA78`. Its
`+0x100` cell `0x8215FB78` points to the complete two-word accessor `0x82A73340`.
The accessor returns `Q`, writes no memory and changes only `r3`. `Q` is the
constructed 108 byte result, not the manager. The path through `0x82CA7720`, for
the accepted class, calls this getter at `0x82CA78CC` and then calls
`0x82CAA6A8(Q,-1)` at `0x82CA78D4`. The wrapper forces producer mode 0 and always
stores the returned low 32 bits to `Q+0x0C`, including the failure value -1. A
successful scan for a vacancy with a negative input, below 8, yields a
compatible ordinal from 0 to 7.

The default child offsets `+0x148` and `+0x190` point to `0x82CA3D38` and
`0x82CA39E0`. A null child `+0x2C` that stays null supplies check value 1 and
scalar 0. Nonnull backend targets keep their supported current dispatch and
normal-return contracts. A nonnegative supplied input has no upper-bound check
in the producer. The path needs three things: the same live `M`, `S`, `Q` and
table, a successful compatible ordinal, and a result word of the same
generation. It also needs no later failed or supplied overwrite. The constructor value -1
alone is not sufficient, because `0x82D0A788..794` uses `teams[L]` before the
phase 2 check.

Exact phase 1 bypasses all 38 phase 2 unit-caption bodies before this provider.

Every accepted first recursive branch requires a previously absent raw bit and
publishes it before its descendants. This holds under configured `N<=8`,
supported `p` and `q`, and no incompatible mutation in between. Under those
premises the strict growth of bits limits the reached phase 1 recursion, and
finite replays have at most 6 descendants. The native prerequisites of
technology 4 at `0x82F77628`, `0x82F7762A` and `0x82F7762C` are all `0xFFFF`.
The suppressor `0x82D09584` clears `F` after sharing, regardless of the `F`
that descendants return. All 38 native old-technology `+0x4C` fields differ from
4, so civilization 4 accepts no unit-conversion callback for this path. The
actual loops, the getter, the terminal stores and the original save14 and
restore14 therefore return every reached phase 1 descendant for technology 4,
and the outer invocation, with `F0`. This holds under the stated current state,
storage, helper and frame conditions. No forced `F`, no sharing bypass and no
opaque conversion callback purity is needed.

The same suppressor with all `0xFFFF` prerequisites applies to technologies 1,
2 and 5. Matching unit or building definitions for 1, 2, 4 and 5 do not
establish a first-discovery entitlement. Source 6 suppression and all other
native player, team, recipient and phase checks remain intact.

## Complete native grant and return coverage

The canonical matrix covers every `t` from 1 to 46. For each it lists the
prerequisites, the `unit+0x4A` first-reward matches, the separate `unit+0x4E`
availability captions, the `old-type+0x4C` matches, the `building+0x42` matches,
the actual special target, the government offer and the obsolete Wonder. It
covers every native dispatch under the stated conditions. It does not claim that
every technology grants a reward or that every allocation succeeds.

- Units: the scan covers 38 definitions and excludes type 27. Recipient
  selection scans 128 cities with a matching nonnegative owner and positive
  population. Definition flag 2 additionally requires flag 2 in `city+0x24`.
  The selection strictly maximizes population plus `((buildingWord<<2)&8)` and
  keeps the earlier city on ties. A positive best and a set phase mask 1 request
  `0x82D11750`. Exhaustion with -1 writes native success 0. Movement, veteran
  and type 29 continuation remain. Matched types 19, 21, 22 and 23 use the
  accepted alternate `0x82CF4C40`. Positive requests bypass its recursion for a
  negative input, and only type 21 can request secondary Militia 7. All 19
  matched definitions that stay valid clear creator flag `0x80`, which excludes
  its optional achievement branch.
- Buildings: the scan matches 23 normalized definitions and excludes `t44`. The
  native score must exceed both the current best and the population. Only
  normalized 4, 6, 7, 17 and 18 have nontrivial score terms, which permit
  positive branches for `t` of 14, 10, 7, 9 and 46. Other native matches fail
  that hurdle. The Temple and Egypt correction, the Literacy Courthouse
  suppression and the stale-caption policy remain distinct. A positive phase 1
  delivery sets the bit, calls `0x82D02090` and publishes the shared recipient
  `R=0x830E3434` only after the return. Phase 2 skips new delivery and uses the
  native `R` and the fallback for an existing building. Each technology has at
  most one first-reward unit and one building match. `t14` may deliver both
  independently.
- Special targets: `t11` and `t39` increment each owned city of positive
  population and recount. `t18` and `t22` keep the exact credit that the native
  culture threshold derives. `t20` and `t45` add 100 and 500 Gold. These
  mutations require phase mask 1 to be set. The `t44` reveal-plane ORs run in
  both phases, and they are idempotent only while the planes and geometry stay
  unchanged. Other special targets keep their formatting behavior.
- Civilization 4: the current civilization `0x830ECD28[p]==4` independently
  enables native conversion after the `F` group. The new `+0x4A` and old `+0x4C`
  matches are paired, with the finite count and 256 scans, the alive, type and
  flag checks and the phase predicates all kept. Phase 1 calls the current
  `+0x1A4` removal `0x82D7D9B0`, changes the type, calls the `+0x1A0`
  registration `0x82D7FE40` and the `+0x1B4` no-op `0x821D5678`, and then calls
  the optional `+0x1BC` snapshot `0x82D81BA0`. Removal copies 84 bytes, destroys
  an object that is neither null nor 1 through `+0x0C(1)` and clears matching
  references. Phase 2 formats only accepted captions. Converted types can fail
  its old-type filter. The normal supported object and ABI contracts apply.
- Terminal code: `0x82D0AD70` and `0x82D0AD74` clear `0x830E33F0[p]` and
  `0x830E3410[p]`. The optional `frame+0xA4` refresh city starts at -1 and
  differs from the input `context+0x1F4`. The reached phase 1 recount and the
  original return at `0x82D0ADD4` and `0x82D0ADD8` stay in place. No normalized
  success Boolean is inferred.

The Irrigation example remains valid. An accepted owned city with population 7
reaches `0x82D0A3F8`, becomes 8 and requests `0x82D00C78`. At the earlier PC
`0x82D093A4`, the raw ownership, discoverer, source and tally may already be
recorded before that award. Those records still do not show that this invocation
completed the delivery, and they do not exclude effects by another invocation.

## Completing-city context and SDI scoring

The accepted SDI result remains substantive. Technology 46 matches normalized
building 18, which is item 118. At `0x82D0A138` its weighted score reads the
signed population of the seed city through `188*c` and multiplies it by the
count of low 16 building bits of the candidate. An initial best of 0 does not
cancel the term. Replacing the winner changes the seed offset, but its stored
best can still depend on the earlier context.

Two full 128 city replays on the same mapped snapshot differ only in a valid
owned seed city. They select different recipients when no eligible bit 0
candidate exists. Suppose the seed population is 0 to 31 and the candidate
population is 1 to 31. Then non-bit 0 scores are at most 527, and eligible bit 0
scores are at least 1001. A unique eligible bit 0 candidate therefore wins in
both traces. The population bounds, the existence and the uniqueness are
premises. No native population cap or capital invariant follows. `K=0` cancels
numerically, while its population load still executes.

`acquisitionContextEntryRetentionBoundary` ties the incoming `r5` low 32 bits,
through the original save at `0x827F7C50`, to `frame+0x1F4`. That location is
incoming `SP+0x24`, a parameter home that the caller backs. `0x82D09754`
zero-extends it into `r15`. The required resolver and any current `+0x1C0`
callback must keep those home and frame bytes unchanged. The ABI register rules
alone do not show that the memory is not aliased. `W==0` for technology 46
follows the count 1 bypass.

When the fields stay valid, the 38 unit scan has no qualifying match for
technology 46, and the first 18 building fields do not match. A building
mismatch at `0x82D09BD0` branches to `0x82D0A2E4` without the `frame+0xA4` store.
The captured signed pointer endpoint at `base+4758`, not a live global count,
accepts SDI. The selected 575 local operations reach `0x82D09BEC` with the saved
`c`, `188*c` and a best of 0, without a call or a store. The current fields and
bounds, and the supported home and helper state, remain conditions. The valid
completing city `c` is therefore an explicit candidate input. A player index or
-1 is not substituted merely because another caller uses it.

## Deferred per-entry presentation candidate

The completion marker `0x830E3348[p]` and the context `0x830E3328[p]` differ from
the selected research `0x830EDD48[p]` and the recursive marker `0x830E3430`.
Phase 1 publishes one technology, and later `0x82D1D460..47C` consumes one
request with source 0 and phase 2. Two phase 1 entries cannot both survive that
scalar slot. The shared `R` can also be overwritten at `0x82D0A208` before its
reader at `0x82D0A214`. The native delayed processing therefore cannot preserve a
batch of grants.

Immediate grants at `0x82D16344` have another concrete defect. Apollo's pending
Wonder bit `0x1000` marks work that later reads city `+0x3A`. The reader at
`0x82D1DD3C..54` expects the item 217 that completion stored first. It subtracts
200 and calls Wonder mode 2. The pending bit does not guarantee the contents of
that field. The code at `0x82D1DD58..60` can clear the bit only after that call
fully returns. Granting a free building in that city first overwrites 217 with
`100+b`. Completing phase 2 for the new gift does not process the original
pending Wonder.

The candidate records only the actual completion tuple at `0x82D16344`, and then
lets native finalization, growth and presentation finish. It processes the queue
after a matching Calendar presentation sweep completes and the outer command
returns at depth 0. Two further conditions apply. No native marker or context
generation may remain unresolved. No eligible city may keep pending item bits
`0x1100`, including the original pending Wonder of the completing Apollo city.
Reaching the common return `0x82CE16AC` alone is not sufficient, because
`0x82D10FD8` can bypass the reader. The command-depth word `0x83156344` is
bookkeeping. It is not shown to be a lock against reentry, and nested native
command dispatch remains possible.

Marker values alone cannot establish readiness. The reset `0x82D1F4EC` writes
-1, which the reader that tests only for nonzero still accepts. A consumed
positive marker can keep identical bits. The candidate must track the actual
`0x82D20C18` publications, select the generation at `0x82D1D460` and consume only
that one when its request at `0x82D1D47C` fully returns at `0x82D1D480`. A newer
nested publication stays pending. Running phase 2 directly for a batch does not
show that the native marker was consumed. If the consumer is bypassed or filters
out the request, draining the queue waits for the actual completion. Draining
eventually in every mode is not shown.

For each fresh `W==0` entry, in ascending order, run `(p,t,c,0,1)` to its full
native return, and then run `(p,t,c,0,2)` to its full native return before `t+1`.
Before the next entry, recheck the current game, the Apollo claim owner and
city, the valid owned city `c`, the pending generations and item flags, and
`W==0`. Leave the native marker and context untouched. Keep the RAM effects and
the original guest execution context. Do not restore the old `F`, the
recipients, the city items or the terminal clears. No phase 3 equivalent is
selected.

The gift building IDs of normal grants are at most 18, so `0x82D02090` sets no
pending Wonder or spaceship item flag. It writes the building and era bits,
recounts, stores the latest item `100+b` and checks for duplicates before
appending `b` in `city+0x87..0xA2`. A full list still prevents insertion under
the native rule. The recount ORs the low dirty flags 1 and 2 and keeps the high
pending flags. The separate spaceship bit `0x100` also uses `+0x3A`, with its
native owner, part and range checks and the gameplay work that follows. Multiple
gifts in the same city keep their combined bits and list results. The caption
for each gift's `R` and explicit building completes before the next entry. If a
nested modal command creates a new pending item, finish the pair that has
started and defer the rest.

The native `R` and the first-unit success are read before the main modal. The
formatter uses the initialized buffer `0x82FFD7C0` with capacity 4096.
`0x82E2F1A0` copies its bytes into a private copy at `frame+0x50` through `0x821B1500` at
`0x82E2F218`. `0x82E2F350` passes that carrier to `0x82E07290`, and `0x82E057F8`
makes another private copy at `0x82E05810` before pumping. The accepted contracts
for a copy from a distinct source, resize, NUL and backing store apply, as do
the lifetimes of those copies. A later `F` is freshly read at `0x82D0A948`
and is not restored after modal work.

Phase 2 keeps seven native items. They are the government offers and choices
and command 2, the first-reward captions, the `t44` notice, the 33 Wonder
obsolescence, the advisors, the packed history `(p<<8)|5000|t` through
`0x82D00480`, and the accepted civilization 4 text. The availability captions
use the separate `unit+0x4E` matches and the native `0x830E3410[p]!=0`. The
terminal clear of phase 1 stays in place. No synthetic flag and no extra
source 6 acquisition manufactures them. The source 0 achievement request at
`0x82D09314`, for a local player with a non-sentinel value and a nonzero turn,
uses ordinal 2 and retail 7 and has no phase check. Keep both native requests
and the existing platform delivery and deduplication conditions.

Deferral changes timing. Eligibility, recipients, the population and culture
samples, and the order of helpers and the random number generator all happen
after the remaining Calendar work and presentation. Native claims made in the
meantime make `W!=0`, and those entries are skipped. This timing needs
acceptance. Equivalence with the immediate call at `0x82D16344` or with the
whole Calendar is not asserted.

## Saving, loading and peer acceptance obligations

A pending completion that is only transient can be lost if a save occurs before
the drain. The current title schema 5 save metadata stores no Apollo tuple. Its
selected path `0x82D82510`, `0x82D829E8` can disable the metadata or only warn
after native success. It does not show a save contract for a quiescent pair.

The minimal durable gameplay payload is a versioned ordered array of accepted
`(p,c)` tuples, with Apollo 17 implicit, tied to the native slot, device and file
digest. The order of the array preserves the first in, first out order. No
per-reward ledger and no cursor for the next `t` is needed. Saves between
complete pairs keep `W`, so fresh `W==0` tests skip entries that are complete or
were claimed in the meantime. Save serialization also requires the native
acquisition and presentation staging to be quiescent, with no unresolved marker
generation and no unfinished city item consumption. A nested modal Save must defer rather than wait on its
own pair. Capture the queue snapshot at the matching native save point, and
prevent the drain from advancing during that snapshot transaction.

Before the native file is changed, a durable authoritative REQUIRED or PREPARED
marker must identify the user, the device, the slot and the save transaction. A
failure prevents the native write. After native finalization, write the frozen
tuple payload tied to the native digest `D`, then COMMITTED(`D`, payload
digest). Accept only after all receipts, because the native and metadata files
are not assumed to be atomic. Before deserialization, known-managed saves need
the committed marker, a supported version, the payload and a matching native and
transaction identity. Missing, unreadable, prepared-only or mismatched required
state rejects the load. It must not become an empty legacy queue. Only
positively identified legacy saves may load empty without the new metadata. No
old Apollo claim is scanned to invent a completion. Required-marker storage,
legacy discrimination and failure handling are implementation obligations.

Validated tuples restore after the load reset and before gameplay resumes. Old
process, UI and command identities are discarded. A resumed drain needs a fresh
quiescent native receipt and current checks of the claim, the city and `W`. The
existing optional sidecar behavior alone does not implement that guarantee.

For multiplayer, a UI completion or marker readiness on one peer is not
authority to grant. The design requires an already accepted common authoritative
native command, barrier and order, and matching first in, first out, per-entry
receipts of `W`, claim, city and stage on all peers. The peers must accept or
defer the same entry in the same gameplay order. They must produce matching
deterministic ownership, discoverer, source and tally, matching unit, city,
culture, Gold and history effects, and matching gameplay command effects. Native
local UI and achievement differences remain native. Current new-game policy
synchronization, member UI readiness and local append and dispatch do not show
that common barrier, and they do not show a restore of a shared multiplayer
save. No custom command protocol is specified.

Game of the Week remains native through the title's authoritative current and
origin classification before enqueue. No new settings UI and no Game of the Week
policy is selected. Runtime acceptance work remains for several cases: natural
completion by human and AI players, all reward, UI and achievement effects,
same-city and nested-pending cases, save failure and reload points, and
execution on common peers. The canonical finding pins the native image, 14
selected receipts covering 1,666 distinct words, finite discriminators and six
audited title sources. These static results do not establish an implemented
all-mode grant loop or a delivered reward.
