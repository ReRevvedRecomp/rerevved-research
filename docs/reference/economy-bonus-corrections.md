# Economy bonus correction contracts

These proposed corrections remove two civilization-bonus penalties while
preserving their benefits. They target the supported image in
[image.json](../../manifests/image.json); implementation and runtime behavior
remain unvalidated. Native evidence and exact instruction alternatives are in
[the correction manifest](../../manifests/economy-bonus-corrections.json).

## Recommended shared mechanism

Use one selective result filter at `ActiveCivilizationBonusLookup`
(`0x82CF0CB0`), composed with the existing lookup owner. Capture the incoming
bonus ID, cumulative-mode argument, native LR and growth baseline before
delegating. Run the existing lookup exactly once, then change only the full
64-bit return register r3 for the cases below. Leave its other returned state
intact.

The native LR is the guest call's return PC, not the call instruction address
or the wrapper's host return address. All sixteen Gold callers explicitly set
that LR in the inspected generated source. The growth caller also puts its
composed baseline in `ctx.r31` before calling the same lookup.

Use per-call local snapshots. The implementation must establish its registered
hook, original/delegation route and wrapper preservation against the manifest's
source identities. Calling the replaced entry recursively or restoring all
entry registers would violate this contract.

## Gold income without the rush penalty

UEA25 is Spain's and Zulu's Industrial bonus and the Aztecs' Modern bonus.
The native rush numerator is `(1 + bonus25) * era + 2`. Make it `era + 2`
at the listed rate consumers by returning false only for their bonus25 lookup.
Keep the lookup table and Gold-income path active.

The exact filter is:

```text
captured bonus ID == 25
captured cumulative-mode argument == 0
captured native LR is in the table below
=> after normal lookup return, set full64 r3 = 0
```

All entries use the native owner's player argument. There is no local-player
or hardcoded civilization-index gate: the native table still determines bonus
activation, and other civilizations' inactive results remain inactive.

| Rate consumer | Call PC | Native LR to match |
| --- | --- | --- |
| treasury-to-production-equivalent aggregate | `0x82CB3464` | `0x82CB3468` |
| unit paid amount | `0x82CB67BC` | `0x82CB67C0` |
| primary paid unit conversion | `0x82CB68E0` | `0x82CB68E4` |
| policy-bit paid unit conversion | `0x82CB69E4` | `0x82CB69E8` |
| building/Wonder paid amount | `0x82CB6BCC` | `0x82CB6BD0` |
| primary paid building/Wonder conversion | `0x82CB6CDC` | `0x82CB6CE0` |
| item107 alternate paid conversion | `0x82CB6DC0` | `0x82CB6DC4` |
| unit quote | `0x82CE28AC` | `0x82CE28B0` |
| building quote | `0x82CE2990` | `0x82CE2994` |
| Wonder quote | `0x82CE2A48` | `0x82CE2A4C` |
| unit amount text | `0x82CEC320` | `0x82CEC324` |
| building amount text | `0x82CEC450` | `0x82CEC454` |
| Wonder amount text | `0x82CEC560` | `0x82CEC564` |
| unit conversion | `0x82D17970` | `0x82D17974` |
| building conversion | `0x82D17A04` | `0x82D17A08` |
| Wonder conversion | `0x82D17A4C` | `0x82D17A50` |

Fifteen rows are price or paid-conversion uses. The treasury aggregate row is
a purchasing-power arithmetic mirror; include it to align that calculation
with the corrected rate. Its downstream utility remains unbound, so it must
not be described as another treasury debit.

### Preserve these calls

| Call PC | Native LR | Role |
| --- | --- | --- |
| `0x82D148BC` | `0x82D148C0` | City Gold income: adds half its reaching intermediate |
| `0x82CB5B7C` | `0x82CB5B80` | Separate candidate valuation |
| `0x82CB5E18` | `0x82CB5E1C` | Separate candidate valuation |
| `0x82CED54C` | `0x82CED550` | Separate candidate score |

The income path retains `G + trunc0(G/2)` before later modifiers. Great
Explorer income, Science-excess deposits and all other bonus calls remain
native. Globally disabling bonus25 or replacing its retail cells would remove
the requested income benefit.

### Keep pricing and conversion consistent

Display and submission use `0x82CE27F0`, whose r4 points to the amount output;
r3 returns eligibility/affordability. Command6 passes that amount to
`0x82D178A8`, which independently rebuilds the conversion rate. The AI has
additional paid paths, and candidate lists have their own amount text.
Correcting only the human quote/apply pair misses those consumers.

Preserve these native rules:

- Unit rate: `trunc0((era + 2) / (1 + bonus35))`.
- Building rate: `era + 2`; Wonder rate: `2 * (era + 2)`.
- Spaceship parts 119 through 122 use the building arm.
- Normal costs, invested Production, eligibility, affordability, owner checks,
  native rounding, command amount and treasury debit remain in place.
- AI unit arithmetic retains its distinct placement of invested Production
  before division by two. This correction does not combine the separate
  America's bonus35 rounding proposal.

The normal era increase remains. On entering the Industrial era, Spain and
Zulu's ordinary rate becomes 4 Gold per Production after the previous era's 3,
instead of jumping to 6. The Aztecs' Modern transition becomes 4 to 5 instead
of 4 to 8. Removing the bonus penalty does not freeze era pricing.

| Supplied inputs | Native | Corrected |
| --- | --- | --- |
| Industrial, 10 remaining Production, ordinary unit/building | 60 Gold at rate 6 | 40 Gold at rate 4 |
| Industrial, 10 remaining Wonder Production | 120 Gold at rate 12 | 80 Gold at rate 8 |
| Modern, SS Propulsion, 189 remaining Production | 1512 Gold at rate 8 | 945 Gold at rate 5 |
| Medieval America, bonus35 active, 10 remaining Production, bonus25 inactive | 10 Gold | 10 Gold |
| City Gold intermediate5 with bonus25 active | 7 before later modifiers | 7 before later modifiers |

These are arithmetic cases, not reconstructed screenshot state. A quote-only
change to 40 with the old Apply rate 6 buys only 6 Production. With both rates
4, 40 buys 10. Current city/item/owner/era/progress continuity remains necessary.

### Native-word alternative

The manifest records sixteen exact original and replacement normalizer words.
Keeping each lookup call and forcing its local normalization to the false case
is an alternative when a reliable caller-aware result hook is unavailable.
It needs durable generation/override integration. Editing generated output
alone is insufficient; replacing the lookup calls themselves would also skip
native register/LR effects.

## Zulu growth without increased Food requirements

Zulu's Medieval UEA8 lowers the growth threshold; it is not a +50% Food-yield
bonus. Its ordinary active rule is `max(20, B - 10)`, where B is the
already-composed baseline. The floor raises a baseline below 20.

At the inner lookup entry, use this separate result-filter predicate:

```text
captured native LR == 0x82CF10FC
captured bonus ID == 8
captured cumulative-mode argument == 0
uint32(captured entry r31) < 20
=> after normal lookup return, set full64 r3 = 0
```

The call instruction is `0x82CF10F8` (`0x4BFFFBB9`). Capture B at this
lookup entry, where it is already in `ctx.r31`; incoming r31 at the outer
threshold-function entry is still caller state. Do not reconstruct B from the
returned threshold or re-read city inputs afterward.

False takes the native branch at `0x82CF1100` to `0x82CF1130`, returning
the retained B. Both CityUpdate threshold calls then use the same correction.

| B | Native active threshold | Proposed active threshold |
| --- | --- | --- |
| 10 | 20 | 10 |
| 19 | 20 | 19 |
| 20 | 20 | 20 |
| 25 | 20 | 20 |
| 30 | 20 | 20 |
| 40 | 30 | 30 |

Inactive bonus behavior stays B. The existing factor subtraction, both ordered
reductions, their rounding, and the existing 10 and 20 constants stay
native. The unsigned predicate covers 0 through 19 and preserves all native
signed-negative outcomes; a bare signed `B < 20` check would be broader.

An alternative is to clamp the selected discount to nonnegative immediately
before `0x82CF1118` on the supported ordinary domain. That requires an
instruction insertion/diversion or equivalent owner change; no single-word
replacement is established. Disabling UEA8 globally would remove its benefit
at larger baselines.

## Evidence and implementation boundary

The two manifest findings contain native words, exact ranges/digests,
generated caller locators, preserved consumers and falsifiers. They establish
the correction contracts and supplied-input arithmetic. The effective build,
current hook composition, actual reported state, command delivery and runtime
outcomes remain unvalidated. This guide contains no in-game test procedure.
