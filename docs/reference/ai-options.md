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
