# Resource definitions

The 22-row table maps **Oxen 0** to technology **4, Horseback Riding**.
Cattle 19 uses technology 9, Code of Laws. The shared `Cow` token does not
identify a single resource. The [manifest](../../manifests/resource-definitions.json)
records image, row and name hashes, readers and limits. The [placement
reference](resource-placement.md) covers creation, refresh and whether placed
resources stay valid.

## IDs, names and nominal technologies

Reader IDs are zero-based: `-1` means absent, and `0` is valid Oxen. The exact
initialized ASCII names and tokens do not establish UI localization, and they
do not identify any code that reads a token. The signed value at `+0x43` is the
technology ID, and the technology table supplies the names. A technology ID of
`-1` skips the check on whether the player has the technology. The tile and
context checks still apply.

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
corroborates the 22 names and the pairing of Oxen with Horseback Riding. It
writes `Dyes` for `Dye` and `Automobile` for `The Automobile`. Its Grassland
matches terrain `1` for Oxen, Wheat, Cattle and Incense, although no native
enum for it was recovered. The other labels rest on native discriminators. No
Horse or Horses entry occurs in these 22 rows. This does not exclude units or
other content.

Six names differ from their tokens. The tokens `Silver`, `Sugar`, `Fur` and
`Deer` sit in the Sulfur, Rubber, Oak and Game rows, and they are not shown to
be aliases. The token `Cow` serves both Oxen and Cattle. Name lookups and token
lookups therefore differ.

## Terrain and coordinate lookup

Take coordinates with `0<=a,b<=39` and `i=40*a+b`. The lookup rejects a tile
with any of the flags `0x1001`, requires the presence flag `0x20`, and matches
the signed terrain at `+0x40` and the signed remainder of `a+b` at `+0x42`. The
divisor is 4 for terrain `1` and 3 for every other terrain. The 22 rows cover
each case exactly once:

| Terrain byte | Label | Divisor | Remainder 0 | Remainder 1 | Remainder 2 | Remainder 3 |
|---:|---|---:|---|---|---|---|
| 0 | Sea | 3 | 10 Dye | 16 Whale | 18 Fish | - |
| 1 | 1 (wiki: Grassland) | 4 | 0 Oxen | 20 Wheat | 19 Cattle | 11 Incense |
| 2 | Plains | 3 | 8 Wine | 13 Marble | 14 Silk | - |
| 3 | Forest | 3 | 5 Rubber | 9 Oak | 17 Game | - |
| 4 | Hill | 3 | 1 Iron | 3 Coal | 6 Aluminum | - |
| 5 | Desert | 3 | 2 Sulfur | 4 Oil | 12 Spices | - |
| 6 | Mountain | 3 | 7 Uranium | 15 Gems | 21 Gold | - |

Setting the presence flag cannot choose an arbitrary resource. Oxen and Cattle
need different coordinate remainders. This reader shows nothing about map
dimensions, legality, yields, probabilities or completed placement. The reader
does not read `+0x41`. Other code reads it, as the
[contribution consumers](../../manifests/resource-identity-override.json)
describe.

## Identity and player availability

Context `-1` skips the technology and player checks. For a player, the query
checks the nominal technology first. The query can then still pass through
UEA39 or player word `10`. An earlier selector 17 check is separate from
technology 17, Feudalism. The callee's return, its effects, and whether the
player's state stays unchanged are all qualified. The nominal technology is
therefore not a complete access rule.

Keep valid `0` apart from absent `-1`. Keep the resource's identity apart from
a player's ability to use it. Setting arbitrary IDs, placing a chosen resource
safely, refreshing it, and keeping it valid at run time are not yet shown.

## Founding-center reward

The selected founding path consumes the accepted center resource and grants
one increment to a reserve or state value. It does not establish recurring city income.
The [center-resource boundary](../../manifests/resource-definitions.json#/centerResourceBonusBoundary)
records the exact classifier, stores, evidence and remaining limits.

The founding reader uses the founding player's normal availability context.
That context includes the nominal technology, UEA39 and the civilization
fallback described above. The reader also skips the excluded player. After it
accepts the resource, it clears resource presence before dispatching the
reward. A separate ordinal classifier chooses the native destinations.
Definition `+0x41` is not this classifier.

| ID | Resource | Class | Native founding increment |
|---:|---|---:|---|
| 0 | Oxen | 1 | +10 Production reserve |
| 1 | Iron | 1 | +10 Production reserve |
| 2 | Sulfur | 1 | +10 Production reserve |
| 3 | Coal | 1 | +10 Production reserve |
| 4 | Oil | 1 | +10 Production reserve |
| 5 | Rubber | 1 | +10 Production reserve |
| 6 | Aluminum | 1 | +10 Production reserve |
| 7 | Uranium | 1 | +10 Production reserve |
| 8 | Wine | 5 | +10 Gold reserve |
| 9 | Oak | 1 | +10 Production reserve |
| 10 | Dye | 5 | +10 Gold reserve |
| 11 | Incense | 4 | +10 Culture strength score |
| 12 | Spices | 5 | +10 Gold reserve |
| 13 | Marble | 1 | +10 Production reserve |
| 14 | Silk | 4 | +10 Culture strength score |
| 15 | Gems | 3 | +10 Gold reserve |
| 16 | Whale | 0 | +10 Food reserve |
| 17 | Game | 0 | +10 Food reserve |
| 18 | Fish | 0 | +10 Food reserve |
| 19 | Cattle | 0 | +10 Food reserve |
| 20 | Wheat | 0 | +10 Food reserve |
| 21 | Gold | 3 | +10 Gold reserve |

Food and Production target the city reserves at `+0x34` and `+0x36`. Classes 3
and 5 share the player Gold reserve as their destination. In this part of the
function, Spices therefore credits Gold. This native arm does not explain a
reported Science increment. No class 2 resource occurs in the 22-row
classifier.

Incense 11 and Silk 14 already have native class 4 entries and a +10 store
when the founding and availability checks pass. Ceremonial Burial 3 and
Literacy 12 are their nominal technologies. They have the same alternative ways
to pass the availability check as other resources. The destination is the
Culture strength score at `0x830ED4E4`, which has one entry per player. Its
concrete consumers are recorded in the
[class 4 consumer boundary](../../manifests/resource-definitions.json#/centerResourceBonusBoundary/class4ConsumerBoundary).
The name "Culture strength score" summarizes its recovered roles. It is not a
name recovered from the source. The grant does not directly add 10 to the
city's Culture income at `+0x48`. The existing entries, the +10 store and the
linked consumers do not support a diagnosis of a missing entry or a dropped
consumer. Actual state is still needed to explain a particular failed check or
display observation. The design intent is not yet established.

The Cultural Leader presentation reads this exact score and ranks players by
`1000 * Cultural Victory count + score`. The count uses Wonders, Great People
and clamped converted-city credits. While the score stays in its Calendar range of 0 to
209, it is a remainder below one count unit, so +10 can change the ranking among
players with equal counts. It does not itself add a Great Person, Wonder or
converted-city credit, or directly increase the Cultural Victory count.

Calendar uses the city's Culture contribution differently. It sums the
contributions into a player row and, on the selected update arm, moves the
strength score toward a value based on Culture per city. When the inputs stay
unchanged and the arithmetic does not overflow, the update is
`score - trunc0(score/3) + trunc0(35 * cityCultureSum/cityCount)`.
It runs only with more than three cities while `currentTurn-startTurn<=20`.
After that it runs with any positive city count. It then clamps the score to 0..209;
an accepted UEA 11 lookup can impose a floor of 60. A +10 difference can shrink
to 6 or 7 on one smoothing update, or disappear at a clamp or floor. This is
not an unchanged permanent balance or an added 10 per turn.

The same Calendar path derives a level from the score, applies separate native
adjustments, clamps it to 0..6 and clears its low bit, leaving 0, 2, 4 or 6.
For a player who is not excluded and has a neutral subtraction, its score
thresholds are 60, 120 and 180. The culture-border sweep reads that exact level
of the city's owner and uses it in two influence multipliers alongside city
`+0x48`. Thus the founding grant can affect gameplay inputs beyond ranking when
it changes the derived level. A grant below a threshold need not change those multipliers immediately.
Other native factors, arithmetic and overwrites still govern the result; no
fixed territorial gain or completed city conversion follows from +10 alone.

A separate foreign-city candidate helper also rejects a selected candidate
when its owner's level exceeds the actor's. Its caller's action and delivered
effect remain unresolved. The effects on Great People thresholds and chances,
the full set of AI and diplomacy uses, and the save and load cadence were not
established. The score, derived level, city rate, the player's contribution
accumulator and the Cultural Victory count therefore remain distinct values.

Adding another +10 at founding would duplicate an existing grant. The smallest
change that keeps the native lifetime is to keep its checks, the consumed
presence and the current rewards. Redirecting class 4 into a city rate or another Culture
counter would change the native reward's meaning.

A recurring +10 city Culture contribution would need its own lifetime rule.
The native path consumes the presence flag, so a later resource query on an
unchanged tile cannot recover the founding resource from that flag. A future
recurring option would need five things: a durable record of which resource the
city started with, availability checks for the current owner, explicit rules
for city capture and resource loss, a single composition from the native
baseline before the Culture cache and aggregate writes, and a way to rebuild
the derived contribution on load without adding it again to an already modified
saved value. The existing evidence shows no hook point that both recomputes
that contribution and keeps the native one-shot founding lifetime. No runtime
observation was made, and the full lifecycle of capture, loss, saving, loading
and display was not covered.
