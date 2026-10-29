# AI configuration boundaries

Ordinary setup has five civilized slots and Barbarian slot 5. With one human,
the existing opponent control can retain up to four AI civilizations. The
serializer traverses eight player pools and civilization/era entries, plus a
64-entry relation array. Those backing extents do not establish playable
additional slots: initialization, turn order, placement, UI and networking for
players 6 and 7 remain unverified.

## Eight civilization target

Eight civilizations means one human and seven AI. Keeping Barbarians as a
separate participant suggests count 9 with Barbarian slot 8. The selected
placement loop has eight permutation entries and skips the Barbarian before
writing coordinates, so eight civilization starts fit its coordinate rows.
That is a useful positive capacity result; actual starts remain unobserved.

Several consumers need structural changes. The placement preference histogram
scores every participant with eight player columns before excluding Barbarians.
At player 8, its counts alias the next terrain category for player 0. The
unchanged ninth unit pool would overlap live map label/count planes and fall
outside the fixed save transfer. Diplomacy indexing also has stride eight;
Barbarian consumers must be classified before expanding that representation.
Earlier setup work uses the count before the ordinary count stores, so changing
the two late setup constants alone does not establish added civilization
initialization.

The [placement expansion finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0331)
owns these exact joins and limits. Four AI is the current supported ordinary
setting, not a proved absolute engine ceiling.

## Six AI setup

One human and six AI, retaining Barbarians, needs seven civilizations and
eight participants. The selected native eight-entry unit, civilization,
coordinate and relation backing fits this layout. Five AI uses seven
participants. These layouts keep every participant below index eight and
avoid the ninth-column and ninth-pool collisions above.

The [setup assignment finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0332)
binds an early seam after actual human-mask construction, the later ordinary
count stores and the native AI civilization writer with duplicate retries.
It preserves the earlier human selection and the separate Barbarian ID.
The bounded contract keeps the human at slot zero, before every AI in the
native comparison against earlier civilization IDs.
This is a concrete offline prototype contract, with valid starts, turns,
contacts and save/load still unobserved.

Restricted selection flags admit only five civilization IDs. Expansion must
exclude those modes rather than relying on retries to create enough distinct
IDs. Game of the Week also changes the duplicate comparison to omit
player slot zero; the bounded expansion contract excludes that mode as well
as multiplayer and the native special two-player override.

## Economic and strategic consumers

Native research and production helpers expose three post-composition seams.
Research exposes the completed technology cost. Unit production exposes a
scalar that the native factor subsequently multiplies and divides by two;
building and Wonder production expose a final cost after existing reductions.
An option at these points needs distinct rounding, positive minima, AI
classification and effective-policy persistence. Percentages are title policy,
not recovered retail difficulty fields.

Civilization bonuses already influence one native production-candidate
valuation. A cumulative UEA lookup can add half a local coefficient before
later scoring. This does not establish a separate leader personality or
aggression, diplomacy, army formation, target or research preference.

The selected production score arm advances a local state recurrence and adds a
scaled contribution to its nonnegative coefficient, then applies four ordered
flag-dependent adjustments. The state, multiplier and floating scale remain
symbolic; the recovered arithmetic does not establish a random distribution or
a universal score range. Its common comparison replaces the retained candidate
on an equal score as well as a greater one. The unit-filter comparison has a
separate strict-greater rule. The production update writes local stack state
and continues candidate iteration; final winner retention, city production
assignment and execution remain separate gates. Exact arithmetic and provenance
are in the [score continuation boundary](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0330/scoreContinuationBoundary).

The [AI boundary findings](../../manifests/ai-options-boundaries.json) own exact
seams, capacities, the valuation join and runtime qualifications. Starting
technology ownership and native activation timing remain in
[starting technology grants](../../manifests/starting-technology-grants.json).
Arbitrary technology IDs need their actual setup-time acquisition effects
validated before exposing a starting list.

## Gold, Food and Culture output

Completed native city contributions expose conditional percentage seams before
cache and owner-state consumers diverge. Each seam needs a register change and
a matching saved-temporary change; changing a cache or return value alone does
not reach all known representations. The [city-yield hook finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0343)
owns exact registers, widths, native overrides and consumer limits.

| Yield | Proposed boundary | Required coherence |
| --- | --- | --- |
| Gold | Before `0x82D14ECC`, completed value in `r8` | Replace saved `stack+0x7C` too, before city `+0x46`, mode-zero aggregate and later reserve credit. |
| Food | Before `0x82D14280`, completed contribution in `r10` | Replace saved `stack+0x90` too, before city `+0x4C`/`+0x40`, mode-zero aggregate and growth input. |
| Culture | Before `0x82D152E8`, completed value in `r18` | Replace saved `stack+0x78` too, before city `+0x48`, mode-zero aggregate and later owner accumulator. |

Gold and Culture retain signed entry owner in `r17` and mode in `r15`;
`r31` is the city ordinal times `0xBC`. Food retains the city base in `r21`
and the same city offset in `r31`, but has no established common owner
register at its earliest scalar seam. Its hook must read the saved entry owner
at `stack+0x84`; `r4` can instead hold population on a native branch.

These points preserve native composition, including technology, building,
Wonder and civilization effects. Subsequent native clearing must still run.
In particular, the excluded-owner path can clear a credit without rewriting
an earlier cache, and the UEA 42 path clears Food/Gold but retains Culture.
A percentage must preserve these distinctions and the native signed-halfword
cache versus full-word contribution widths.

Food's completed sum is the contribution added to the growth box at city
`+0x34`. The selected growth path subtracts its native threshold and carries
the remainder when population increases. Its negative-progress path resets
the box and decrements population. Scaling that accumulated box would compound;
scaling the newly composed contribution can affect both growth and population
loss. This evidence does not recover a separate gross-harvest/maintenance pair,
so it supports a native growth-contribution option with explicit sign policy,
not a proved gross-harvest percentage.

Known downstream effects are bounded. Gold reaches an owner aggregate, the
reserve credit and a selected refresh-then-cache reader. Food reaches its two
snapshots, an owner aggregate and growth state. Culture reaches an owner
aggregate, a separate owner accumulator and two signed `+0x48` inputs of the
border sweep. Complete displays, final-yield AI valuation, trade, rush, Great
People and Cultural Victory joins remain unbound. The established UEA 25
rush-rate and valuation formulas are separate from completed city Gold.
Border-input scaling does not establish a fixed territorial increment.

The city Culture aggregate also supplies the separate
[Culture strength score](../../manifests/resource-definitions.json#/centerResourceBonusBoundary/class4ConsumerBoundary),
which participates in Cultural Leader ranking and a derived border-influence
level. The ranking reads the score; border influence also depends on the
quantized level. Both remain distinct from the Cultural Victory count.

Reaching a seam proves a composition event, not one event per city per turn.
Mode one bypasses this yield block; mode minus one refreshes caches then exits
before selected state credits. Calendar can call mode zero more than once
for a city and can also consume cached Culture without recomposition.
Scale each original temporary once per reached composition, never an existing
reserve, growth box, accumulator or already scaled cache. Policy changes need
demonstrated cache invalidation and recomputation order. Complete saved-cache
transfer, load order, policy persistence, capture/resource/technology refresh
and runtime parity remain acceptance gates. City-founding resource rewards
are separate from these per-composition contributions.

## Eternal Kombat and Always at War

The [Always at War finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362/nativeScenarioBoundary)
binds Eternal Kombat to built-in scenario ordinal 9. Its native preset sets
`WARANDPEACE` slot 9 to 2 at `0x82DAF43C`. It also changes upgrade rate,
starting size, attack bonus and display-card inputs. Copying the preset would
therefore change more than diplomacy.

Selected contact code recognizes that value and stages a native command 38
request for war, relation 0, for the reached pair. It bypasses the ordinary
negotiation suffix. Conditional admission supports both AI/AI and human/AI
pairs; human contact has an additional current-participant restriction.
Selected availability and negotiation branches also recognize the rule.

This supplies a reusable per-pair mechanism. It does not establish that the
scenario visits every active pair at initialization or keeps every pair at war
after every peace request, load or membership change. Selected branches bypass
one Great Wall/current-Democracy negotiation corridor; that does not cover all
forced-peace effects. Shared-group writes, relation-derived rankings and local
versus session delivery retain the finding's separate conditions.

The finding's `pairVisitationBoundary` binds one native scheduler at
`0x82D034A0`. Each invocation requires at least one participant to equal its
supplied context K. With three supplied ordinals and K=0, it excludes both
orientations of pair 1/2 before later helpers. WARANDPEACE2 preserves that
restriction, statistics/classification checks and turn-delay gates. The
wrapper applies further admission before forwarding the pair to contact.

One invocation therefore cannot reconcile all pairs. Later covering K
invocations and other schedulers remain possible. The finding's
`kProducerLifecycleBoundary` binds the selected `0x82D1D1C0` edge: entry
stores its original player P at SP+0x234, `0x82D1E84C` reloads that home into
r31, and `0x82D1E90C..10` forwards it as K to `0x82D034A0`. Thus K=P under
the explicit protected-home, normal-return and nonvolatile retention premises.
The optional suffix includes a current virtual callback, whose effects remain
conditions.

Accepted local update/presentation calls can supply that player; they do not
establish every configured player or successful setup/load/membership repair.
The finding's `commandIngressBoundary` binds command48, BeginTurnAI, to that
sweep and a guarded command50, ImDone, suffix that requests48. Service, mask and
one-shot gates precede publication; three nonzero-word tests can bypass the
sweep after dispatch. None establishes actual delivery or mandatory repair
before setup/load/membership relation readers. commandDeliveryBoundary below owns the selected sender/ring bridge and
remaining received-invocation gate.
No scenario flag transplant, setting or runtime behavior was implemented.

The finding's `commandDeliveryBoundary` binds the retained factory table's
child+0x44 to sender `0x82CA6500`. Null info or a missing S+0x14 can return
before complete serialization. The command object's selected+0x10 target
`0x82D91C58` separately passes its embedded record at A+0x34 to `0x82CE16C8`.
No mandatory sender-to-that-processing invocation is proved. Next bind the
received selector/invocation and same-record lifetime, before lifecycle or
first-reader coverage. The130-word packet has127 instructions and three
table cells;125 assertions, five supplied cases and three mutation controls
passed. This remains conditional delivery evidence, not peer authority.

## Default transport construction

`RVA-F-0362/constructorTransportInitializationBoundary` binds the selected
CB12F0 call at0x82CB1348 to constructor0x82CA5E80. Its local store at
0x82CA5EC4 writes zero to S+0x14 before the first allocator call; the complete
82-word local owner has no later explicit overlapping S-relative store.
Helper aliases, normal return and the same retained receiver remain conditions.

For a retained zero S+0x14, the accepted sender takes its missing-transport
bypass. A later nonzero publication/helper effect or a separately established
current receiver is therefore required before selecting P and its current
virtual+0x0C at0x82CA45A8. No received invocation, absence of later writers,
delivery or continuous all-pair war follows. The91-word packet passed native,
independent encoding, explicit-store and mutation checks.
