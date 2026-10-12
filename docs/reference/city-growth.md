# City growth threshold

`CityGrowthThresholdLookup` at `0x82CF1060` computes a baseline from city
population, a shared scalar, and three city flags. The scalar and flags retain
neutral names because their gameplay meanings are unresolved.

| Input | Storage | Use |
| --- | --- | --- |
| `P` | City `+0x03`, signed byte | Population multiplier |
| `G` | Word at `0x830E45C8`, interpreted as signed | Shared factor |
| `word_10` | City `+0x10`, unsigned word | Bit `0x100` subtracts two from the factor |
| `half_3C` | City `+0x3C`, unsigned halfword | Bit `0x2` selects the first reduction |
| `word_24` | City `+0x24`, unsigned word | Bit `0x40` selects the second reduction |

Let `s32(v)` retain the low 32 bits and interpret them as signed, and let
`u32(v)` retain those bits as unsigned. `trunc0` means division toward zero.
The exact baseline arithmetic is:

```text
D  = 2 if word_10 bit 0x100 is set, otherwise 0
B0 = s32(s32(G - D) * P)
T(v) = trunc0(s32(2 * u32(v) + 1) / 3)
B1 = T(B0) if half_3C bit 0x2 is set, otherwise B0
B  = T(B1) if word_24 bit 0x40 is set, otherwise B1
```

For nonnegative values without overflow, each reduction is
`floor((2*v + 1)/3)`. Both flags apply the reduction twice, including rounding
after the first division. No baseline clamp precedes the civilization bonus.
The scalar's initialization and runtime value, the flag meanings, and the
runtime input ranges remain unresolved.

When cumulative UEA 8, Faster city growth, is active, the ordinary integer
result is `max(20, B - 10)`. Otherwise the threshold is `B`. For wrapped signed
inputs, the exact active result is
`s32(B - min_signed(10, s32(B - 20)))`.

The accepted city-update consumer compares signed city halfword `+0x34` with
the threshold. On growth it subtracts the threshold from that stored progress
and increments population byte `+0x03`. The producers and complete meaning of
stored progress remain unresolved.

The static formula, input locators, arithmetic boundaries, and consumer evidence
are in [city-growth-threshold.json](../../manifests/city-growth-threshold.json).
