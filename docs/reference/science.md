# Science and technology cost

One `CalendarTurnAdvance` path pools selected-technology progress from rows
whose signed comparison halfword matches the incoming player, comparing
`0x82CF0EE8` cost. The grouping suggests teams, but full comparison-array
identity remains qualified.

| State | Address and indexing |
| --- | --- |
| Selected technology | `0x830EDD48[player]` |
| Stored progress | `0x830EDD68[player*48 + technology]` |
| Group comparison | Signed halfword `0x830E9070[player]` |
| Acquisition context | `0x830E3328[player]` |
| Completion marker | `0x830E3348[player]` |

Cached city path adds signed `+0x44` under native selection/cache gates, not
unconditionally per city/turn. Completion needs pooled progress>=cost, player
!=`0x82F700B0`, technology unowned. Valid nonzero technology reaches
`0x82D20C34` -> `TechnologyAcquire` with player, technology, retained context,
source `0`, phase `1`. Context starts `-1`; first individually cost-meeting city
fills it, so pooled completion can still use `-1`.

The block calls cost again, adds pooled-minus-second-cost to Gold at
`0x830ED544[player]`, then marks completion before nonzero-tech test; zero skips
acquisition. It neither subtracts progress nor proves next-tech carryover.
Stores keep low32, comparisons signed: nonnegative excess needs valid indices,
no signed overflow, stable cost; no local technology clamp exists. Source `6`
civilization grants remain separate; shared acquisition proves no common
policy/reason semantics or cadence.

## Technology research cost

`TechnologyResearchCost` (`0x82CF0EE8`) starts at two for valid nonzero
technology. Three nonsentinel prerequisites each add rooted occurrence count,
again if that prerequisite's ownership query is zero. Descendant ownership is
untested; repeated paths count repeatedly. No visited set: initial depth zero
expands through 500, counts children at 501. Helper does not initialize depth;
guard bounds depth, not work.

Four gates enable signed low32 `6*base` / signed low32 `global_82FFE7C8+6`,
truncated toward zero: byte `0x8314F10B`, classifier, local-player mask in
requested ownership, `global_82FFE7C8 > 1`. Then multiply by
`[15,10,8,5][index]`, signed halfword index `0x830E8FD8`; without scaling,
multiply base directly. Index is unchecked; arithmetic wraps. Division traps do
not prevent negative denominator after adding six wraps. Technology zero returns
9999 early; -1 skips prerequisites but retains gates/multiplier.

Difficulty/game-speed meanings and runtime cost remain unproved. Exact domains:
[cost manifest](../../manifests/technology-research-cost.json).

## Spaceship launch result

The selected launch dialog returns a signed arrival year or -1. Its caller
admits only positive results, excluding valid BC dates and year zero before
that producer submits the launch. The selected arrival evaluator accepts the
signed date domain, with separate state and victory gates.

The [arrival-year boundary](../../manifests/spaceship-launch-arrival-year-boundary.json)
records the field chain, native cancellation sentinel and a proposed
`result != -1` admission contract. This is a static correction contract;
actual dialog retention, launch delivery and repaired victory remain unobserved.

## Evidence sources

- [Technology research cost](../../manifests/technology-research-cost.json)
- [Science completion](../../manifests/science-completion.json)
- [Spaceship launch arrival year](../../manifests/spaceship-launch-arrival-year-boundary.json)
- [Starting technology grants](../../manifests/starting-technology-grants.json)
- [City yield state credits](../../manifests/city-yield-state-credit.json)
