# Resource definitions

The 22-row table maps **Oxen 0** to technology **4, Horseback Riding**; Cattle
19 uses 9, Code of Laws. Shared `Cow` token is not unique identity.
[Manifest](../../manifests/resource-definitions.json) owns image/row/name
hashes, readers and limits; [placement](resource-placement.md) owns
creation/refresh/retention.

## IDs, names and nominal technologies

Reader IDs are zero-based: `-1` absent, `0` valid Oxen. Exact initialized ASCII
names/tokens prove no UI localization or token consumer. Signed `+0x43` gives
technology ID; its table supplies names. `-1` bypasses technology ownership,
retaining tile/context gates.

| ID | Record name | Secondary token | Technology ID | Technology name | Terrain byte | Remainder |
|---:|---|---|---:|---|---:|---:|
| 0 | Oxen | Cow | 4 | Horseback Riding | 1 | 0 |
| 1 | Iron | Iron | 6 | Iron Working | 4 | 0 |
| 2 | Sulfur | Silver | 24 | Gunpowder | 5 | 0 |
| 3 | Coal | Coal | 27 | Steam Power | 4 | 1 |
| 4 | Oil | Oil | 28 | Combustion | 5 | 1 |
| 5 | Rubber | Sugar | 40 | The Automobile | 3 | 0 |
| 6 | Aluminum | Aluminum | 34 | Mass Production | 4 | 2 |
| 7 | Uranium | Uranium | 42 | Nuclear Power | 6 | 0 |
| 8 | Wine | Wine | 5 | Pottery | 2 | 0 |
| 9 | Oak | Fur | 10 | Construction | 3 | 1 |
| 10 | Dye | Dye | 18 | Monarchy | 0 | 0 |
| 11 | Incense | Incense | 3 | Ceremonial Burial | 1 | 3 |
| 12 | Spices | Spices | -1 | None | 5 | 2 |
| 13 | Marble | Marble | 7 | Masonry | 2 | 1 |
| 14 | Silk | Silk | 12 | Literacy | 2 | 2 |
| 15 | Gems | Gems | -1 | None | 6 | 1 |
| 16 | Whale | Whale | 23 | Navigation | 0 | 1 |
| 17 | Game | Deer | 17 | Feudalism | 3 | 2 |
| 18 | Fish | Fish | 2 | Bronze Working | 0 | 2 |
| 19 | Cattle | Cow | 9 | Code of Laws | 1 | 2 |
| 20 | Wheat | Wheat | 11 | Irrigation | 1 | 1 |
| 21 | Gold | Gold | 14 | Currency | 6 | 2 |

[Civilization Wiki list](https://civilization.fandom.com/wiki/List_of_resources_in_CivRev)
corroborates 22 names/Oxen-Horseback Riding, using `Dyes` for `Dye`,
`Automobile` for `The Automobile`. Its Grassland matches terrain `1` in
Oxen/Wheat/Cattle/Incense, without recovered native enum; other labels use
native discriminators. No Horse/Horses occurs in these 22 rows, without
excluding units/other content.

Six names differ from tokens: `Silver`/`Sugar`/`Fur`/`Deer` are
Sulfur/Rubber/Oak/Game cells, not proved aliases; `Cow` serves Oxen/Cattle.
Name/token lookups differ.

## Terrain and coordinate lookup

For `0<=a,b<=39`, `i=40*a+b`: reject `0x1001`, require `0x20`, match signed
terrain `+0x40` and signed `a+b` remainder `+0x42`. Divisor `4` for terrain `1`,
otherwise `3`; 22 rows uniquely cover:

| Terrain byte | Label | Divisor | Remainder 0 | Remainder 1 | Remainder 2 | Remainder 3 |
|---:|---|---:|---|---|---|---|
| 0 | Sea | 3 | 10 Dye | 16 Whale | 18 Fish | - |
| 1 | 1 (wiki: Grassland) | 4 | 0 Oxen | 20 Wheat | 19 Cattle | 11 Incense |
| 2 | Plains | 3 | 8 Wine | 13 Marble | 14 Silk | - |
| 3 | Forest | 3 | 5 Rubber | 9 Oak | 17 Game | - |
| 4 | Hill | 3 | 1 Iron | 3 Coal | 6 Aluminum | - |
| 5 | Desert | 3 | 2 Sulfur | 4 Oil | 12 Spices | - |
| 6 | Mountain | 3 | 7 Uranium | 15 Gems | 21 Gold | - |

Presence cannot choose arbitrary identity; Oxen/Cattle need different
remainders. This proves no map dimensions, legality, yields, probabilities or
completed placement. Unread `+0x41` remains unclassified.

## Identity and player availability

Context `-1` bypasses technology/player gates. Ordinary player queries nominal
technology, then may pass UEA39 or player word `10`; prior selector-17 gate is
separate from technology 17, Feudalism. Callee return/effects/player retention
remain qualified, so nominal technology is no complete access rule.

Distinguish valid `0`/absent `-1` and intrinsic identity/player availability.
Arbitrary-ID setting, safe inverse placement, refresh/runtime retention remain
unproved.
