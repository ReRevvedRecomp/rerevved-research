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
the bonus. Selected scalar initialization/calendar stores are recorded in the
[capacity finding](../../manifests/city-population-cap.json#/growthBoundary).
Flag meanings, complete writer coverage and runtime ranges remain unknown.

When cumulative UEA 8, Faster city growth, is active, the ordinary integer
result is `max(20, B - 10)`. Otherwise the threshold is `B`. For wrapped signed
inputs, the exact active result is `s32(B - min_signed(10, s32(B - 20)))`.

City update compares the signed value at `+0x34` with the first threshold-helper
result. On growth, it subtracts a separately queried result and increments
population at `+0x03`. The two results can differ if their inputs change. The progress
producers and the field's full meaning remain unknown. Evidence:
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

The classifier's nonzero-mask and zero-mask/null-child branches retain helper
state while clearing or bypassing the unnamed field at `+0x78`. A nonnull child
requires the actual receiver and call target to be identified. Mask rebuild
copies a nonzero source or combines session predicates. Searches for source
stores, address construction and displaced or overlapping accesses found no
producer, but did not exclude aliases, bulk copies or all writers. Zeros in the
image and known call sites do not establish the live mask or retention across
calls.

The helper's save14/restore14 at `0x82D019E8/0x82D019EC` can restore the outer
owner, ordinal and loop pointer despite reuse of `r31`, provided every child
preserves the saved bytes and the city and marker bytes. It updates workers,
tiles and flags without directly storing owner or population. Valid divisors,
extents, finite counters and returning calls remain required. Five later
classifiers read the mask again, so an initial nonzero mask is insufficient.

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

## Population capacity

Population is a signed byte at city `+0x03`, and the shipped game stops cities
at 31 in nearly every path. `CityUpdate` clamps a signed population of 32 or
more to 31, food growth stops at ceilings 8, 16 or 31, and the grants and
rewards clamp or refuse at 31. Irrigation is the exception: it adds 1 to a
positive owned population with no local cap check.
A larger cap also needs changes to the 32 citizen assignment bytes, the
eight-word histogram of unassigned citizens, the 33-entry population cost
table, the city screen, and the signed byte and signed halfword arithmetic
around growth. The byte itself holds up to 127, which does not make 127 safe.

[City population cap](city-population-cap.md) gives the default yield of
citizens beyond the assignment vector, the histogram and its consumers, the
overflow arithmetic at a larger cap, every hook point with its address, and the
open questions. Evidence: [city-population-cap.json](../../manifests/city-population-cap.json),
`RVA-F-0384`, and its accepted mutation and growth dependencies.
