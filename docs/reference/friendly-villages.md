# Friendly village rewards

Friendly villages normally select the lowest of six relative civilization
scores. Each score is the player's value divided by that metric's aggregate
total. These are comparison scores, not independent reward probabilities.
Ties retain the earlier category.

| Metric | Ordinary reward |
| --- | --- |
| Population plus another per-player count | Settlers on Chieftain or Warlord, subject to the gates below; otherwise 25 Gold |
| Unit production values adjusted by unit fields | Map reveal, unless an eligible visiting combat unit receives the earlier rank upgrade |
| Owned-building production factors | Caravan, subject to eligibility; otherwise 25 Gold |
| An unnamed per-player statistic | Current research technology when valid; otherwise 25 Gold |
| Treasury plus a city statistic | 25 Gold |
| Three other per-player counters | One Spy |

Caravan is native unit type 29; Settlers is type 0. The creator's ordinary
initialization preserves that distinction before later callbacks. A requested
unit is not proof of successful placement or a retained delivered reward.

## Settlers difficulty gate

On the ordinary setup-copy path, Chieftain (0) and Warlord (1) pass the
signed difficulty-word comparison `< 2`. King (2), Emperor (3) and the
nonnegative Deity fallback values above three fail it and give 25 Gold for
this category. The local Caravan eligibility checks contain no difficulty
comparison.

The Settlers branch also requires byte `0x8314F10B` to be zero. Earlier reward
alternatives must be bypassed and halfword `0x8314F1C8` must be zero for ordinary
category dispatch. Those fields remain unnamed.

Setup can substitute two or a retained initialized zero for the selected
difficulty. The named result therefore requires the ordinary setup-copy path
and retention into the village read; current zero mode fields alone do not
establish their earlier setup values. The raw signed gate also admits negative
words, which are not assigned supported difficulty names. The Deity view is a
fallback, not proof of an exact ordinal or legal input range.

## Priority and delivery limits

A qualifying random technology candidate can take priority. Otherwise the
category-two visiting-unit upgrade precedes ordinary dispatch. A separate
nonzero halfword override can request two Spies. The six-way random introductory
message does not select the category, and a later research prompt does not
prove that the village awarded a technology.

Captured barbarian settlements and artifact tiles use separate paths. Metric
freshness, actual branch delivery and final visible rewards still need runtime
observation. Metric inputs, request sites, eligibility predicates,
setup overrides and evidence are in
[`friendly-village-rewards.json`](../../manifests/friendly-village-rewards.json).
