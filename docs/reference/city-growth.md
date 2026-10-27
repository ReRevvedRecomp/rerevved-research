# City growth threshold

`CityGrowthThresholdLookup` (`0x82CF1060`) uses population, a shared scalar and
three flags. The gameplay meanings of the scalar and flags remain unknown.

| Input | Storage | Use |
| --- | --- | --- |
| `P` | City `+0x03`, signed byte | Population multiplier |
| `G` | Word at `0x830E45C8`, interpreted as signed | Shared factor |
| `word_10` | City `+0x10`, unsigned word | Bit `0x100` subtracts two from the factor |
| `half_3C` | City `+0x3C`, unsigned halfword | Bit `0x2` selects the first reduction |
| `word_24` | City `+0x24`, unsigned word | Bit `0x40` selects the second reduction |

`s32(v)`/`u32(v)` interpret low 32 bits signed/unsigned; `trunc0` divides toward
zero:

```text
D  = 2 if word_10 bit 0x100 is set, otherwise 0
B0 = s32(s32(G - D) * P)
T(v) = trunc0(s32(2 * u32(v) + 1) / 3)
B1 = T(B0) if half_3C bit 0x2 is set, otherwise B0
B  = T(B1) if word_24 bit 0x40 is set, otherwise B1
```

Without overflow on nonnegative inputs, reduction is `floor((2*v + 1)/3)`;
both flags apply it twice with intermediate rounding. There is no clamp before
the bonus. Scalar initialization and value, flag meanings and runtime ranges
remain unknown.

When cumulative UEA 8, Faster city growth, is active, the ordinary integer
result is `max(20, B - 10)`. Otherwise the threshold is `B`. For wrapped signed
inputs, the exact active result is `s32(B - min_signed(10, s32(B - 20)))`.

City update compares signed `+0x34`, subtracting threshold and incrementing
`+0x03` on growth; progress producers/full meaning remain unknown. Evidence:
[city-growth-threshold.json](../../manifests/city-growth-threshold.json).

The active floor can raise a baseline below 20. The proposed
[economy bonus correction](economy-bonus-corrections.md#zulu-growth-without-increased-food-requirements)
retains that baseline while preserving the native benefit at larger values.

## Population bonus branches

Applying the 100-Gold reward requests type-0 Settlers at the first populated
city owned by the reward player, without testing whether it is the capital.
The returning continuation advances the threshold marker without testing grant
success. The 2,000-Gold reward adds +1 below population 31; Irrigation first
discovery also adds +1 to owned cities with separate phase/source/eligibility
guards and no below-31 test. Both call `0x82D00C78` after the writes.

Classifier's nonzero-mask or zero-mask/null-child arms retain helper state,
clearing/bypassing unnamed `+0x78`. Nonnull child requires actual receiver/
target binding. Mask rebuild copies nonzero source or folds session predicates;
source-store/materializer and displacement/overlap searches found no producer,
excluding neither aliases, bulk copies nor all writers. Image zeros/call sites
prove no live mask or ordered retention.

Helper's save14/restore14 at `0x82D019E8/0x82D019EC` can restore outer owner,
ordinal and loop pointer despite reused `r31`, conditional on saved and city/
marker bytes surviving every child. It updates workers/tiles/flags, without
direct owner/population store; divisors, extents, finite counters/returns remain
guards. Five later classifiers resample mask, so first-nonzero proof is
insufficient.

## OCC reward contract

To replace the application of the 100-Gold reward:

1. Retain reward player; scan 128 slots, match signed owner/population 1 through
   30, increment once and call `0x82D00C78(cityIndex)`. Skip 31; granting 32
   breaks R=32/cap31.
2. Require helper completion and retained frame/nonvolatiles/city/owner/population/
   marker. Actual mask/order remain unknown. Zero mask needs current child,
   `+0x100`, repeated dispatch/lifetime binding; manifest lists every reached gate.
3. Skip `0x82CF57E4` creator, resume `0x82CF57E8` once. Retain applying
   flag, tier index/table and marker address for `0x82CF5BE0`. Preserve preview/
   later tiers; never separately mark or retry partial loop.

This conditional native-call contract proves no actual mask, full return or
all-city execution. Exact guards/alternatives:
[occ-gold-population-reward.json](../../manifests/occ-gold-population-reward.json).
