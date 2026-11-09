# City population cap

A city in the shipped game stops at population 31, with Irrigation as the one
writer that adds 1 without a local check. This page explains
what enforces that number, what a city beyond the assignment vector would
produce natively, and what a mod must change if it raises the cap. Native
addresses and ranges live in the manifest
[city-population-cap.json](../../manifests/city-population-cap.json)
(`RVA-F-0384`); this page explains them. Nothing here is a runtime observation,
and no larger cap is shown to be safe.

## What limits city size

| Limit | Value | Where it comes from |
|---|---|---|
| Population storage | Signed byte at city `+0x03`, positive values up to 127 | Records start at `0x8314FE28`, stride 188, 128 slots |
| Entry clamp | Signed population of 32 or more becomes 31 | `CityUpdate` at `0x82D139D4` to `0x82D139E4` |
| Food growth ceiling | Stops at 8, 16 or 31 | A signed definition halfword selects ceiling 9, 17 or 32; growth stores ceiling minus one |
| Grants | Clamp or refuse at 31 | Hanging Gardens, Statue of Liberty, the economic reward, the Great Humanitarian command; Irrigation has no local test |
| Citizen assignments | 32 bytes at city `+0x58`, one per citizen ordinal | A separate lock word follows at city `+0x78` |
| Unassigned citizen histogram | 8 words | Helper `0x82CE1C10` |
| Population cost table | 33 entries, populations 0 to 32 | Helper `0x82CF7E30` |

The byte could hold 127, but that does not make 127 a usable cap. Each limit
above is a separate piece of code, and raising one alone leaves the others
unsafe. A population of 32 fits the assignment vector and the cost table. A
population of 48 fits the histogram. Neither number is a safe cap for the whole
city. Irrigation and a few other writers have no local test at 31, so 31 is not
a universal invariant either; it is the largest value the evidence supports.

## What a city beyond the assignment vector produces

Each citizen has an ordinal `i`, counted from zero, and an assignment byte. An
assignment of -1 means the citizen works no tile. `CityUpdate` still counts
that citizen: it selects terrain type 8 at the city's own coordinates and adds a
default contribution.

| Component | Per default citizen | Native cause |
|---|---|---|
| Food | 0 | The food reader returns the type 8 base of 0 and skips the city marker bit |
| Production | 1 | The production reader returns 1 for the city marker before any terrain, resource or player modifier |
| Trade | `floor(i / 6)` | `CityUpdate` skips the trade reader for type 8 and adds this value directly |

The reads are at `0x82D13C78` to `0x82D13C9C` (selection) and
`0x82D13E80` to `0x82D13E90` (trade). They hold when the city tile keeps its
marker bit set and its other flag clear, and when the calls return normally.

Worked example. Suppose a mod lets the 32 assignment bytes stay as they are and
treats every citizen at ordinal 32 or higher as assignment -1. At population 125
those are ordinals 32 to 124, which is 93 citizens:

- Food: 93 times 0, so 0.
- Production: 93 times 1, so 93.
- Trade: the sum of `floor(i / 6)` for `i` from 32 to 124, which is 1170.

If all 125 citizens were default, the totals would be 125 production and 1240
trade. All 31 citizens at today's cap give 31 production and 65 trade. The trade
term grows roughly with the square of the population. These are raw branch
contributions. Later code can double the trade, add half of it, or add a
constant, and the final value is stored as a signed halfword at city `+0x4A`. The
net Gold and science credit and every modifier remain unmeasured. The default
branch does not show an entertainer or specialist role, and it shows no
happiness or culture effect.

A mod must keep the full population loop and the real ordinal. Treating the
extra citizens as inert, clamping their trade level, or stopping the loop at 32
all change this native result.

Full detail: [surplusOutputBoundary](../../manifests/city-population-cap.json#/surplusOutputBoundary).

## The unassigned citizen histogram

Helper `0x82CE1C10` takes a city and does two jobs. It counts the assignment
bytes that are not -1 (call that count `A`), and it fills a table of eight
words that groups the remaining citizens by trade level. With population `P`,
it returns `U = P - A` and adds one to word `floor(i / 6)` for every `i` from
`A` to `P - 1`. Only words 0 to 7 are cleared first. Word 8 is written when a
citizen at ordinal 48 exists, so population 49 with all 32 assignments used is
the first case that writes past the table.

### Five consumers

| Caller | Call at | Use |
|---|---|---|
| Trade reader `0x82CF17C8` | `0x82CF186C` | Ignores the words. Uses `U` to recover `A` and returns `trunc0((A - 1) / 6)`, which is 0 to 5 for `A` up to 32. WorkerRefresh adds it to its candidate score |
| Detail screen `0x82DFC8A0` | `0x82DFD864` | Counts positive words and builds text for each one from `H[j]` and `H[j] * j` |
| Comparator `0x82E1EE48` | `0x82E1EEA0` | Compares the eight words with cached words, together with population and the halfword at city `+0x3C` |
| Reconciler `0x82E22B38` | `0x82E22B50` | Adds or removes interface children by the difference between new and cached words; it does not update the cache |
| Refresh function `0x82E25EA8` | `0x82E26058` | After a refresh, copies the eight words into the interface cache |

The return value `U` has a gameplay consumer through the trade reader, so any
replacement must still return the full `P - A`. The word consumers write no
yield directly. This list covers the five direct callers; indirect and inline
uses were not searched.

### The histogram loses assignment positions

The helper assumes the unassigned citizens are the tail of the vector, from
ordinal `A` up to `P - 1`. `CityUpdate` instead uses the real position of each
-1 byte. The two agree only when the -1 bytes really sit at the tail.

Worked example. Take `P = 7` and `A = 6`. The histogram puts one citizen in word
1, because it assumes ordinal 6. If the one -1 byte is actually at ordinal 0,
`CityUpdate` adds `floor(0 / 6) = 0` trade for it, while the histogram weights
it as 1. This is a layout example, not a state seen in play. A display that must
show exact trade needs the real assignment bytes, not just `P` and `A`.

### Keeping eight words for a larger cap

For `1 <= P <= C` and `A <= min(P, 32)`, define virtual words `j` from 0 up with

```text
H[j] = max(0, min(P, 6 * (j + 1)) - max(A, 6 * j))
```

Because `A` is at most 32, the first eight words sum to `min(P, 48) - A`, so
population plus the eight native words recover `A` and the whole table. Words 8
and above depend only on `P`: `H[j] = clamp(P - 6 * j, 0, 6)`. At `P = 125`
that is 77 citizens in words 8 to 20, with a weighted sum of 1072. The 93
citizens at ordinals 32 to 124 are a different count, and both are correct: the
first follows the histogram's tail grouping, the second the assignment vector.
All 3629 combinations of `P` up to 125 and `A` up to `min(P, 32)` passed this
reconstruction check. The formula defines a proposed extension; it does not
describe what the native code reads past word 7.

## Overflow arithmetic

The figures below use a cap `C`, with 125 and 127 as worked values.

| Check | Result |
|---|---|
| Signed byte | 125 plus 1 is 126 and plus 2 is 127. 127 plus 1 stores `0x80`, read as -128. Headroom is not enforcement |
| Food threshold | `C * F` stays within 32767 when `F <= floor(32767 / C)`. At 125, `F <= 262` (262 gives 32750, 263 gives 32875). At 127, `F <= 258` (258 gives 32766, 259 gives 32893). Stored progress needs its own signed halfword limit |
| Hanging Gardens | `trunc0((3 * P + 1) / 2)` is 188 at 125 and 191 at 127 before the clamp, so clamp in a word before the byte store |
| Histogram | Highest ordinal `C - 1` uses word 20 at 125 (21 words) and word 21 at 127 (22 words) |
| Cost table | `SP - 0x90 + 4 * P` reaches `SP + 0x164` at 125 and `SP + 0x16C` at 127; entries 33 and up have no native value |
| OCC required population `R` | Candidates need `P >= max(native, R)` and completion needs `P > max(native, R - 1)`. For `C = 125`, `R = 126` blocks both below 126; `R = 127` also blocks both |
| SDI First Discovery reward (technology 46, Building index 18) | Scoring is `Pcandidate + K * Pseed + 1000 * bit0`, where `K` counts the set low 16 bits of the Building word. At 125 a non-bit0 candidate with `K = 15` scores 2000 and beats a unique bit0 candidate that scores 1126. At 127 the scores are 2032 and 1128 |

Growth itself uses arithmetic, not a population table: `F = G - D` with `D` 0
or 2, `B0 = s32(F * P)`, then the reductions on the
[city growth](city-growth.md) page. For a population of 500 the byte is not
enough: 500 stored in one byte becomes 244, which a signed read gives as -12. It
would need 16-bit population reads, relocated assignment storage (468 more
bytes per city at 500 assignments), and new rules in every consumer below.

## Hook points

These are all the places found that a larger cap must change. The list is not
complete, because the census of readers and writers is open (see the questions
below).

| Area | Addresses | What must change |
|---|---|---|
| Entry clamp | `0x82D139D4` to `0x82D139E4` | Replace the 31 clamp with the new cap, and make sure population is at most 127 before narrowing |
| Food ceilings and increment | `0x82D163D8` to `0x82D16438` | The increment narrows to a byte before the ceiling test. Saturate in a word first. Changing 32 to 128 alone fails because 128 reads as -128 |
| Irrigation | `0x82D0A3B0` to `0x82D0A414` | Adds 1 with no local test. Saturate before the byte store |
| Hanging Gardens, Statue of Liberty | `0x82D16BA0` | Clamp at 31. Compute and clamp in a word before the byte store |
| Economic reward and Great Humanitarian | `0x82CF5588`; `0x82CE0B88` to `0x82CE0BC4` | Each allows the grant only when `P < 31`. Raise both with the cap |
| WorkerRefresh | `0x82D01788` to `0x82D019E4` | Limit the whole citizen body to `N = min(P, 32)`: the read at `0x82D017CC`, the write at `0x82D019D4` and the lock shifts. Ordinal 32 overlaps the lock word, and ordinal 100 reaches the next city |
| CityUpdate yields | `0x82D13C78`, loop end `0x82D13F1C` | Supply -1 for ordinal 32 and up without reading memory. Keep the full `P` loop |
| Assignment counter | `0x82CE1C40` to `0x82CE1C58`; histogram writes `0x82CE1C88` to `0x82CE1CA4` | Scan `N` bytes and keep `U = P - A`. Replace the unsafe histogram writes |
| Assignment matcher | `0x82CE27A0` to `0x82CE27C4` | Scan `N` entries, but keep a free citizen available when `P > N` even if the first 32 are assigned |
| Assignment classifier | `0x82CEDE04` to `0x82CEDE28` | Scan `N` entries and compare with real `P` at `0x82CEDE3C`. Its shift indexes the assignment value, not the ordinal |
| Command 8 | `0x82CE0094`; writes `0x82CE0100`, `0x82CE0140`; loop `0x82CE0160` | Keep the selected position scan, which writes at most 20 entries. Limit only the population fill and its lock shifts to `N`. A tile mask can hold more bits than `P` |
| Fixed writers | `0x82E023D8`, `0x82E02518` | Keep the fixed 32 byte copy and the separate lock word |
| Population cost | `0x82CF7F34` to `0x82CF7F68`; interface caller `0x82E57DDC` | Keep entries 0 to 32 and define saturation or extension for higher values; none exist natively |
| Yield and progress caches | every low halfword store | Check each store and each 32-bit total over the new range, including AI modes 0 and 1 |
| Population text | `0x82E03650` to `0x82E03C88` | Text is a signed decimal; three digits need checked field widths |
| Saves and peers | `0x82CC2DC8` | Keep the byte, 32 assignment bytes and lock word layout, and check file and network paths |

The manifest sections
[assignmentConsumers](../../manifests/city-population-cap.json#/assignmentConsumers),
[fixedCapacityConsumers](../../manifests/city-population-cap.json#/fixedCapacityConsumers)
and [mutationCensus](../../manifests/city-population-cap.json#/mutationCensus)
list each site with its exact access and the other writers (nuclear branches,
removal, Barbarian decrement, new-city presets, setup stores, and the AI
branch at `0x82CBC02C`).

## City screen limits

A larger cap also reaches the city screen. The manifest records these limits:
[uiReplacementEntryBoundary](../../manifests/city-population-cap.json#/uiReplacementEntryBoundary),
[bitSelectorCallbackBoundary](../../manifests/city-population-cap.json#/bitSelectorCallbackBoundary),
[nonzeroVisualHelperBoundary](../../manifests/city-population-cap.json#/nonzeroVisualHelperBoundary),
[childBudgetBoundary](../../manifests/city-population-cap.json#/childBudgetBoundary),
[lookupTargetBindingBoundary](../../manifests/city-population-cap.json#/lookupTargetBindingBoundary)
and [lookupOutputBoundary](../../manifests/city-population-cap.json#/lookupOutputBoundary).

- The constructor `0x82E261A8` sets up 42 layout cells and a child list that
  grows. Neither fixes a limit on citizen icons.
- Four layout target words at `0x82E250A0` still use the real population. The
  reconciler `0x82E22B38` only searches existing children, so it cannot create
  the extra icons. Capping the targets at 31 while keeping every histogram word
  loses icons.
- Keeping all eight histogram words and all six city bits can need 54 children:
  48 histogram records plus 6 bit records at population 125 with no assigned
  citizens. Enough final slots is not enough, because the add helpers can
  reuse a child and leave the cached count unchanged.
- Direct cache writers at `0x82E21AC8` and `0x82E244EC` to `0x82E24534` use
  `+0x6D4 + 4 * index` with no upper check. Index 9 hits the cached
  population and index 11 hits the selector at `+0x700`.
- Candidate hook points are the four target words at `0x82E250A0` and the
  summary entry `0x82E2609C`. Neither is shown to be safe, and the entry also
  runs during construction.
- The visual chooser `0x82E5CDF8` knows seven resource pairs for indexes 1 to 7;
  index 0 and every index above 7 use the same default pair.

## Saves and peers

The city record writer `0x82CC2DC8` sends population as one byte, the
assignments as 32 byte values and the lock word as four bytes, with no packed
population. Load reaches 128 city rows through `0x82D86400` and `0x82CC4040`.
The command format uses five 32-bit words. These widths show no field that
forces a smaller population, but a completed save, a reload and a network round
trip were not examined.

## Open questions

- The census of every reader and writer is not complete. A whole-image scan
  evaluated 4530 states associated with containing functions and left 22612 forms unsupported. It missed the
  command 8 writes at `0x82CE0100` and `0x82CE0140`, so it cannot prove that no
  access is missing.
- Writers still open: migration, the rest of the Great Humanitarian entry
  paths, conquest and setup presets, transient AI simulation, and indirect or
  bulk copies.
- Readers still open: every table indexed by population, happiness, culture,
  production, trade and AI formulas over the new range, the unnamed value
  stored for default citizens, the five-slot auxiliary vector at `0x82E03650`,
  and final screen widths.
- The meaning of the population cost table entries is unknown.
- The target of the descriptor call at `0x82C9648C` is not identified, so the
  resource lookup under the icon setters is not resolved.
- No icon layout for more than 31 citizens was tested.

Related pages: [city growth](city-growth.md) for the threshold formula and [Apollo discovery bonuses](apollo-discovery-bonuses.md) for the first
discovery score.
