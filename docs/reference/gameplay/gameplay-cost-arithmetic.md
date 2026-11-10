# Gameplay cost arithmetic

Several Gold and production costs in the game come from integer arithmetic
that rounds at each step. The order of the steps changes the result. This page
shows what each cost does in play terms, with a worked example, then how the
code computes it. A mod that replaces one of these costs must reproduce the
rounding, or choose a different rule on purpose.

All numbers below come from static reading of the supported image. No cost was
observed in a running game. `trunc0(x)` means divide and round toward zero.

| Cost | Native result | What differs from the obvious formula |
|---|---|---|
| Unit rush cost | Rate is truncated before it is multiplied | America pays 10 Gold where half of 30 is 15 |
| Technology cost | Division comes before the final multiplier | 15 instead of 22 in the example below |
| Wonder cost | Each halving rounds the kept half up | 270 becomes 34, not 33 |
| Road cost | One direct halving | Base 15 becomes 7 |
| Gold reserve interest | Rounded to the nearest whole Gold | A reserve of 25 earns 1 Gold |
| Fleet sale value | The carrier's multiplier covers its passengers | 165 Gold where valuing each unit alone gives 115 |
| AI unit rush value | Invested production is subtracted before the final half | 18 where the human rush gives 16 (candidate) |

## Unit rush cost

Rushing a unit costs a Gold rate for each point of production still missing.
The rate depends on the era, and two civilization bonuses change it:

```text
numerator = (bonus 25 active ? 2 : 1) * era_index + 2
rate      = trunc0(numerator / (bonus 35 active ? 2 : 1))
cost      = rate * remaining_production
```

`remaining_production` is the unit's full cost minus the invested production
stored at city `+0x36`. Worked example: America in the Medieval era has
`era_index` 1 and bonus 25 inactive, so the numerator is 3, and bonus 35
gives a divisor of 2. The native code
divides first, so the rate is `trunc0(3/2) = 1` and 10 missing production costs
10 Gold. Multiplying first would give `3 * 10 / 2 = 15` Gold. The proposed
correction rounds the product up: `ceil(numerator * remaining / divisor)`.

The divide is at `0x82CE2910` and the multiply at `0x82CE2934` in `RushCostCompute`
(`0x82CE27F0`). The full unit cost that feeds the remaining production is
`signed definition byte +0x44 * scalar / 2`; its instruction addresses, from
`0x82CE28FC` to `0x82CE2928`, are in the
[production cost manifest](../../../manifests/production-cost-ownership.json#/instructionAddresses).
The formula and the command path are in the
[rush cost manifest](../../../manifests/rush-cost-producer.json#/costFormula).
The same cost feeds the rush display at `0x82DFFE38`, the completion check at
`0x82D159F8` and two AI evaluators; see [unit definitions](unit-definitions.md).

## Technology cost

Technology cost counts prerequisites, optionally scales that count, then
multiplies it. `B` is the prerequisite count (at least 2), `g` the shared
difficulty word at `0x82FFE7C8`, and `M` one of `15`, `10`, `8` or `5`:

```text
native         = M * trunc0(6*B / (g + 6))
multiply first = trunc0(6*B*M / (g + 6))
```

Worked example. With `B = 2`, `g = 2` and `M = 15`, native is
`15 * trunc0(12/8) = 15 * 1 = 15`. Multiplying first gives `trunc0(180/8) = 22`.
The native result moves in steps of `M`, which may be deliberate. Over
`B = 2..20`, `g = 2..12` and all four values of `M`, the two forms differ in
639 of 836 cases, always by less than `M`. Whether the rounding is intended is
unknown, so the multiply-first form is a comparison, not an accepted fix.

The scaling applies only when four checks pass: byte `0x8314F10B` is zero, the
player classifier `0x82CD5A70` returns a low byte of zero, the local player
owns the technology, and `g > 1`. The full list of inputs, division traps and
the technology 0 and -1 cases is in the
[technology cost manifest](../../../manifests/technology-research-cost.json#/formula)
and the [science page](science.md#technology-research-cost).

Where the inputs come from:

- `g`: on the normal setup path the game copies the setup difficulty into
  `0x82FFE7C8`. Chieftain is 0, Warlord 1, King 2 and Emperor 3, so King and
  Emperor satisfy `g > 1`. Setup overrides mean `g` is not always the current
  menu value. See the
  [village reward finding](../../../manifests/friendly-village-rewards.json#/settlersDifficultyBoundary).
- `M`: the scenario key `TECHNOLOGYRATE` is slot 4 (not `SPEEDMODE`, slot 12) in
  the [scenario schema](../../../manifests/scenario-schema.json). Applying a custom
  record copies 64 halfwords to `0x830E8FD0`, which places slot 4 at `0x830E8FD8`,
  the index the cost helper reads. The record default is 1 and the last duplicate
  key wins. The helper supports index 0 through 3. Named levels, save
  persistence and the values used in play are unknown.

Science completion uses the returned cost twice: it compares individual and
pooled stored progress with it, then calls the helper again and adds the progress
beyond the second cost to Gold. See the
[science completion manifest](../../../manifests/science-completion.json).

## Wonder cost halving

Wonder costs apply several halvings in sequence. Each one subtracts
`trunc0(cost/2)`, so an odd cost keeps the larger half:

| Stage | Addresses | When it applies |
|---|---|---|
| Common Wonder half | `0x82CF14CC`, `0x82CF14D8`, `0x82CF14E4` | Every Wonder in the helper's range |
| Wonders cost half as much (UEA 24) | `0x82CF14E8` to `0x82CF14FC` | Cumulative UEA 24 is active |
| Final shared half | `0x82CF1540` to `0x82CF1548` | Classifier low byte is zero and `0x82FFE7C8 > 2` |

Worked example. Starting from 270, three halvings give `270 -> 135 -> 68 -> 34`.
One truncation of `270/8` gives 33. A mod that stacks reductions must keep
the rounding after every step. This shows why; it does not show that all three
stages are active together in one game. The common half belongs to the base
Wonder formula and is separate from UEA 24. Canonical records:
[common scale](../../../manifests/building-wonder-cost-identities.json#/wonderRange/commonScale)
and the [modifier branches](../../../manifests/building-wonder-cost-modifier-branches.json).

### Mask aliases

Earlier building reductions test an item mask built from a literal 1 and the
shift `slw` (word `0x7D7CD830`, at `0x82CF1330` and `0x82CF1334`), shifted by the
item number minus 100. The shift uses only the low 6 bits of the count, so two
initialized Wonder records alias building masks:

| Item | Shift count | Mask | Reaches the test for |
|---|---|---|---|
| Wonder 229 | 129 | `0x2` | Barracks, UEA 19 |
| Wonder 233 | 133 | `0x20` | Library, UEA 20, and the three-quarter reduction |

Wonder 233 also matches the three-quarter reduction that reads the halfword at
`0x830E8FFE`; the scenario key `QUARTERPRICELIB` (slot 23) can supply it. An
authored key alone does not show the value is active or that Library is the
only target. Both items are initialized records, not proof of a purchase:
Wonder 229 still needs dynamic bit 2 and its outer check, and Wonder 233 is
excluded from the normal menu and the known city update path. See
[`wonder-records.json`](../../../manifests/wonder-records.json),
[`wonder-eligibility.json`](../../../manifests/wonder-eligibility.json) and
[`wonder-outer-check-record-fields.json`](../../../manifests/wonder-outer-check-record-fields.json).

## Road cost

A road costs `factor * (scalar + 2) * 5`. Under UEA 1, Roads cost half as much
(Roman Ancient, French Medieval, Aztec Industrial), the code divides by two
directly. For a factor of 1 and a scalar of 1 the base is 15, and the halved cost
is `trunc0(15/2) = 7`.

`RoadBuildCostLookup` (`0x82CF83C0`) divides at `0x82CF846C` and `0x82CF8470`.
The city update path in `0x82D13978` repeats the arithmetic at `0x82D16854` and
`0x82D16858`, and submits command 7. The factor helper `0x82D019F0` and the
scalar's origin are not identified. See the
[road cost manifest](../../../manifests/road-build-cost.json).

## Gold reserve interest

Under UEA 47, Gold reserves earn 2 percent interest. Each turn the reserve
gains `(reserve + 25) / 50`, a signed division toward zero. For a nonnegative
reserve this is rounding to the nearest Gold with ties up. A reserve of 24 earns
0 Gold, 25 earns 1, 74 earns 1 and 75 earns 2. Negative reserves follow the
signed division and are not symmetric.

`CalendarTurnAdvance` (`0x82D1EAB0`) adds the term at `0x82D1F490..0x82D1F4A4`;
a read side consumer at `0x82CF9F38` uses the same arithmetic. Details are in the
[reserve interest manifest](../../../manifests/gold-reserve-interest.json).

## Fleet sale value

Selling a carrier credits `5 * H * M * S`. `S` is the carrier's definition factor
plus the factors of its linked cargo units. `H` is 1 or 2 from the classifier
`0x82CD5A70`. `M` is 1 or 3 from the carrier's own `+0x4` byte, applied to the
whole sum. Cargo is therefore multiplied by the carrier's `M`, not its own.

Worked example. A Galleon (factor 6) with a Spy (factor 5), `H = 1`, and a
carrier `M` of 3: native `5 * 3 * (6 + 5) = 165` Gold. Valuing each record by
its own multiplier gives `5 * (3*6 + 5) = 115`. An empty Galleon is 90 and ten
Spies make 840. The per-record value is a proposed correction policy, not
evidence of the intended rule. See the
[unit sale manifest](../../../manifests/unit-sale-refund-value.json).

## AI unit rush valuation (candidate)

`AIUnitChoiceEvaluate` (`0x82CB44E0`) values rushing a unit with a different
order of operations from the human rush. With `F` the signed unit factor,
`S` the effective scalar, `I` invested production and `R` the already truncated
Gold rate:

```text
human rush = R * (trunc0(F*S/2) - I)
AI value   = trunc0(R * (F*S - I) / 2)
```

Worked example. A Warrior has `F = 2`; with `S = 10`, `I = 2` and `R = 2` the human
cost is `2 * (10 - 2) = 16` and the AI value is `trunc0(2 * 18 / 2) = 18`. The
American half-price bonus plays no part. The operations are the multiply at
`0x82CB6818`, the subtract at `0x82CB6824`, the rate divide at `0x82CB6828`, the
multiply at `0x82CB6830` and the half at `0x82CB6838` and `0x82CB6844`.

Two paid arms use the value as an amount. The primary arm at `0x82CB68A4` to
`0x82CB68B0` needs the amount below the owner's Gold. The policy bit `0x4` arm at
`0x82CB6990` to `0x82CB69B4` needs it below `trunc0(Gold/2)`, and an earlier
check can enter that arm directly. Each arm stores the item, debits the amount from the
reloaded Gold word, adds `trunc0(amount / recomputed rate)` to the 16-bit
production (stores at `0x82CB6928` to `0x82CB6954` and `0x82CB6A2C` to
`0x82CB6A88`) and calls `CityUpdate(city, 1)`. An amount of zero or less takes a
separate path without these stores. The block never submits command 6.

This is a candidate, not a confirmed defect. The factor and scalar need not
describe the same item, because the scalar reads the city's old current item
before replacement. The first and recomputed rates match only when the era and
bonus state stay the same. Confirmation needs one natural AI occurrence that
records both Gold reads, which check is taken, the stores, the `CityUpdate`
return and the outcome. Records:
[`ai-unit-rush-valuation.json`](../../../manifests/ai-unit-rush-valuation.json)
(`RVA-F-0398` to `RVA-F-0401`).

### Related AI turn checks

A separate AI path, `AITurnUnitEvaluation` (`0x82CB6E48`), compares the normal
unit cost with Gold before it submits command 6. The cost is
`trunc0(S32(U32(F*S)) / 2)`, with no invested production and no rush rate, at
`0x82CBA210..0x82CBA218`. The reserve word is compared at `0x82CBA2AC..0x82CBA2BC`:
only Gold below the cost skips, and equality passes. Command 6 is submitted at
`0x82CBA2F4..0x82CBA308` with no debit. For a Warrior with `S = 9` the cost is 9,
where dividing the scalar first gives 8. Records:
[`normalCostGate`](../../../manifests/production-cost-ownership.json#/consumers/ai/1/normalCostGate)
and the zero amount case in
[`zeroAmountUnitBoundary`](../../../manifests/rush-cost-producer.json#/commandPath/zeroAmountUnitBoundary).
A zero amount does not make the consumer do nothing: it still stores values,
calls helpers and writes a flag. The scalar's own return and continuation
records are under
[`effectiveScalar/returnBoundary`](../../../manifests/production-cost-ownership.json#/effectiveScalar/returnBoundary).

## Finding this kind of rounding

[`tools/find_divide_multiply.py`](../../../tools/find_divide_multiply.py) screens
word ranges for a division whose result feeds a multiplication within 16
instructions (see the [workflow](../../workflow.md#screen-bounded-integer-arithmetic)).
Its results for these cost paths, with the screened ranges and the screen's
limits, are in
[ai-unit-rush-valuation.json](../../../manifests/ai-unit-rush-valuation.json).

## Model checks

[`tools/check-cost-audit.py`](../../../tools/check-cost-audit.py) runs small
formula models against rational and literal expectations. It does not run guest
code and does not confirm that the native arithmetic was read correctly.

```powershell
python tools\check-cost-audit.py --out <new report path>
```

| Check | Input range | Result |
|---|---|---|
| Rush against a round up policy | Factors 2, 4, 5, 10; scalar 10; four eras; both bonus choices; invested production from 0 to the full cost | 1,744 cases, 210 differ |
| AI value against the human rush | Same range | 1,744 cases, 1,668 differ (cases, not distinct bugs) |
| Fleet against per record value | Carrier factor 6, passenger factor 5; both multiplier choices; 0, 1 and 10 passengers | 24 cases, 8 differ |
| Technology against multiply first | `B` 2 to 20, `g` 2 to 12, all four `M` | 836 cases, 639 differ |
| Road half | Factor 1 to 4, scalar 0 to 3, bonus on and off | 32 cases, no mismatch |
| Interest rounding | Reserves 0 to 200 | 201 cases, no mismatch |

## Limits

- The input ranges are chosen for analysis. Whether a combination of these
  conditions happens in the retail game is not shown.
- Negative and overflowing inputs, unsupported item IDs, rendering math, yields,
  growth, combat and other callers of these costs are not covered.
- The technology rounding, the AI rush valuation and the fleet value policy have
  no accepted correction. Each needs live inputs and an intended rule first.
