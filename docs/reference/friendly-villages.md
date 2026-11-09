# Friendly village rewards

Friendly villages normally select the lowest of six relative civilization
scores. Each score is the player's value divided by that metric's aggregate
total. These are comparison scores, not independent reward probabilities.
Ties keep the earlier category. In game-design terms, this is a catch-up
selector based on relative civilization development: the smallest share wins.

`share[player, category] = metric[player, category] / aggregate[category]`

| Category | Development metric | Raw player value | Usual reward |
| --- | --- | --- | --- |
| 1 | Population and settlement-unit presence | `25 * population + 50 * settlement tally` | Settlers on Chieftain or Warlord, subject to the checks below; otherwise 25 Gold |
| 2 | Military investment | Sum of `trunc(5 * unit production factor * weight * (rank+1) / 2)`, with weight 1 for a unit and weight 3 for an Army | Map reveal, unless an eligible visiting combat unit receives the earlier rank upgrade |
| 3 | Building investment | `5 * sum(building production factors)` | Caravan, subject to eligibility; otherwise 25 Gold |
| 4 | Technology development | `50 * technology-acquisition tally` | Current research technology when valid; otherwise 25 Gold |
| 5 | Economic resources | `treasury + sum(cached city trade)` | 25 Gold |
| 6 | Cultural Victory progress | `owned Wonders + Great People tally + clamp(converted-city credits, 0, 999)` | One Spy |

The sums use the cities and units that the collector accepts. Native arithmetic,
signed caches and floating-point division apply. A zero aggregate has no local
division guard. Invalid or unordered scores need not select any category.

Category four counts technology acquisitions that have the right phase,
including free technologies. It is not science per turn or stored research
progress. The function that writes the tally has no local already-owned check,
so arbitrary calls need not produce a count of distinct technologies known.

Category six competes normally with the other five. It is not a fallback or a
measure of culture generated per turn. The Wonder component is a recount of the
current accepted claims. Native text names the Great People component, but which
Great People states contribute remains unresolved. City transfers driven by
culture update signed converted-city credits, which need not equal a simple
count of the converted cities currently held.

The settlement tally accepts the Settlers definition and a second settler
definition. Its extra tile-bucket credit can alias the same statistic, so it is
not shown to be a plain unit headcount. The city trade cache is distinct from
the final Gold credit.

Caravan is native unit type 29, and Settlers is type 0. The creator's
initialization keeps that distinction before later callbacks. A requested unit
is not proof of successful placement or of a reward that was delivered and
stays in place.

## Settlers difficulty check

On the setup-copy path, Chieftain (0) and Warlord (1) pass the
signed difficulty-word comparison `< 2`. King (2), Emperor (3) and the
nonnegative Deity fallback values above three fail it and give 25 Gold for
this category. The local Caravan eligibility checks contain no difficulty
comparison.

The Settlers branch also requires byte `0x8314F10B` to be zero. Earlier reward
alternatives must be bypassed, and halfword `0x8314F1C8` must be zero for the
regular category dispatch. Those fields remain unnamed.

Setup can substitute two, or an initialized zero that stays in place, for the
selected difficulty. The named result therefore requires the setup-copy path and
a value that stays unchanged until the village read. The current zero mode
fields alone do not establish their earlier setup values. The raw signed check
also accepts negative words, which are not assigned supported difficulty names.
The Deity view is a fallback. It does not show an exact ordinal or the legal
input range.

## Priority and delivery limits

A qualifying random technology candidate can take priority. Otherwise the
upgrade of a visiting unit in category two comes before the regular dispatch. A
separate nonzero halfword override can request two Spies. The random
introductory message, which has six variants, does not select the category, and
a later research prompt does not show that the village awarded a technology.

Captured barbarian settlements and artifact tiles use separate paths. Metric
freshness, actual branch delivery and final visible rewards still need runtime
observation. The metric inputs, request sites, eligibility predicates, setup
overrides and evidence are in
[`friendly-village-rewards.json`](../../manifests/friendly-village-rewards.json).

## Consecutive games

A player reported an opening village reward influenced by the preceding game
on retail Xbox 360. The report has not been reproduced, and the original donor
save is unavailable.

The selected reset fills surround the score table. A selected successful load
publishes scores before recounting, but it can read saved statistics. Indirect
setup and reset callbacks remain unresolved, so those static observations do
not establish that scores from another game stay in place.

The [score lifecycle finding](../../manifests/friendly-village-score-lifecycle.json)
holds the selected native edges and the controlled comparison. A correction
needs the actual state that stays in place and the reward branch. Clearing scores alone introduces
ties; changing the RNG would alter seeded replay without establishing the
cause.
