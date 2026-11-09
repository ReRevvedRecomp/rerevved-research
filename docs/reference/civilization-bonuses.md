# Civilization Unique Abilities

Each civilization has one Unique Ability (UA) and four cumulative Unique Era
Abilities (UEAs). Ancient starts apply the UA and the Ancient UEA. Later eras
add effects without removing earlier ones. Scenario grants that start in a later
era keep the checks below. UAs can grant technologies, buildings, units, Gold or
map state, or apply ongoing rules. They are separate from the UEA table at
`0x82F6F950`, which has 16 rows of four 32-bit IDs each, with stride `0x10` and
total size `0x100`.

Names are recovered, not debug symbols. Effect evidence is static unless stated.
The shared lookup alone does not show which code writes each complete effect. It
also does not show parity in runtime, presentation, AI, save, scenario or
multiplayer behavior.

## Recovered storage and lookup

| Item | Address | Accepted meaning |
| --- | ---: | --- |
| Civilization UEA table | `0x82F6F950` | 16 rows by four cumulative era unlock IDs |
| Civilization name pointers | `0x82F7A348` | 16 internal names aligned with the UEA rows |
| Player era array | `0x830ECD08` | Current era index consumed for each player |
| Player civilization array | `0x830ECD28` | Civilization index selecting one table row |
| Excluded player global | `0x82F700B0` | Player index for which the lookup returns false |
| `ActiveCivilizationBonusLookup` | `0x82CF0CB0` | Shared activation check and the only recovered reader of the table |
| UA text function | `0x82CF97D0` | Presents the separate UA through the civilization bonus text token |

`ActiveCivilizationBonusLookup` receives the requested UEA ID in `r3`, the
player index in `r4`, and an exact era flag in `r5`.

- In cumulative mode (`r5 == 0`), it clamps the player's era to 0 through 3
  and searches every row entry from Ancient through the current era.
- In exact mode (`r5 != 0`), it compares only the current era entry and does
  not clamp the era before indexing.
- It returns false when the requested player equals the excluded player value.

All 95 known call sites across 30 functions use cumulative mode. No exact-mode
caller is known. Do not call exact mode without an independent era range guard.

## Leader and Unique Ability map

Player-facing names, leaders and gameplay descriptions are normalized in
[`civilizations.csv`](../../data/civilizations.csv) and
[`era-bonus-definitions.csv`](../../data/era-bonus-definitions.csv). Internal
names, row order and numeric UEA IDs come from the image.

The [reference data contract](../../data/README.md) records the external
interpretation sources and generation rule.

<!-- civilization-bonus-map:begin -->
| Civilization | Leader | UA | Ancient UEA | Medieval UEA | Industrial UEA | Modern UEA |
| --- | --- | --- | --- | --- | --- | --- |
| Roman | Julius Caesar | Code of Laws and Republic | Roads cost half as much | Wonders cost half as much | Increased Great Person generation | New cities begin with +1 population |
| Egyptian | Cleopatra | An Ancient Wonder | Desert tiles provide +1 Food and +1 Trade | Irrigation | Riflemen gain +1 movement | Caravans provide +50% Gold |
| Greek | Alexander the Great | Courthouse in the capital | Democracy | Increased Great Person generation | Libraries cost half as much | Sea tiles provide +1 Food |
| Spanish | Isabella | Navigation | Exploration provides twice the Gold | Naval units gain +1 combat | Cities produce +50% Gold | Hill tiles provide +1 Production |
| German | Otto von Bismarck | Elite units upgrade automatically | New Warriors are Veterans | Forest tiles provide +1 Production | Barracks cost half as much | Gold reserves earn 2% interest |
| Russian | Catherine the Great | Wider view of the surrounding map | Plains tiles provide +1 Food | New defensive units receive Loyalty | Riflemen cost half as much | Spies cost half as much |
| Chinese | Mao Zedong | Writing | New cities begin with +1 population | Literacy | Libraries cost half as much | Cities are unaffected by Anarchy |
| American | Abraham Lincoln | A Great Person | Gold reserves earn 2% interest | Unit rush costs are halved | Plains tiles provide +1 Food | Factories provide triple Production |
| Japanese | Tokugawa Ieyasu | Ceremonial Burial | Sea tiles provide +1 Food | Samurai Knights gain +1 attack | Cities are unaffected by Anarchy | New defensive units receive Loyalty |
| French | Napoleon | Cathedral in the capital | Pottery | Roads cost half as much | Cannons gain +2 attack | Riflemen gain +1 movement |
| Indian | Mohandas Gandhi | Access to all resources | Cities are unaffected by Anarchy | Religion | Settlers cost half as much | Courthouses cost half as much |
| Arabian (`Arab` internally) | Saladin | Religion | Caravans provide +50% Gold | Mathematics | Cavalry and Knights gain +1 attack | Gold reserves earn 2% interest |
| Aztec | Montezuma II | Additional starting Gold | Units heal after winning combat | Temples provide +3 Science | Roads cost half as much | Cities produce +50% Gold |
| Zulu (`African` internally) | Shaka | Lower strength threshold for overrunning enemies | Warriors gain +1 movement | Faster city growth | Cities produce +50% Gold | Riflemen cost half as much |
| Mongolian | Genghis Khan | Captured cities provide +50% Trade | Captured Barbarian villages become cities | Cavalry gains +1 movement | Mountain tiles provide +2 Production | Communism |
| English | Elizabeth I | Monarchy | Longbow Archers gain +1 defense | Naval units gain +1 combat | Hill tiles provide +1 Production | Naval support is doubled |
<!-- civilization-bonus-map:end -->

Separate UA entries include one-time grants and initial state. The German,
Indian, Zulu and Mongolian entries establish ongoing rules.

## Unique Era Ability IDs

The four values are ordered Ancient, Medieval, Industrial, and Modern. They are
cumulative unlocks, not four mutually exclusive replacements.

<!-- civilization-era-id-map:begin -->
| Civ ID | Internal name | Ancient UEA | Medieval UEA | Industrial UEA | Modern UEA |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | Roman | 1 | 24 | 23 | 36 |
| 1 | Egyptian | 32 | 58 | 12 | 38 |
| 2 | Greek | 60 | 23 | 20 | 28 |
| 3 | Spanish | 7 | 6 | 25 | 41 |
| 4 | German | 50 | 30 | 19 | 47 |
| 5 | Russian | 16 | 26 | 17 | 34 |
| 6 | Chinese | 36 | 10 | 20 | 42 |
| 7 | American | 47 | 35 | 16 | 2 |
| 8 | Japanese | 28 | 27 | 42 | 26 |
| 9 | French | 59 | 1 | 13 | 12 |
| 10 | Indian | 42 | 43 | 5 | 18 |
| 11 | Arab | 38 | 9 | 14 | 47 |
| 12 | Aztec | 46 | 4 | 1 | 25 |
| 13 | African | 55 | 8 | 25 | 17 |
| 14 | Mongolian | 40 | 3 | 56 | 48 |
| 15 | English | 61 | 6 | 41 | 51 |
<!-- civilization-era-id-map:end -->

The internal name of the Zulu civilization at index 13 differs from its
player-facing name. So does the internal name of the Arabian civilization at
index 11.

The Japanese row illustrates the two-layer model. Japan's UA grants knowledge of
Ceremonial Burial, while its Ancient UEA is ID 28, which adds one food to sea
tiles. Both apply from the Ancient era onward. Medieval, Industrial, and Modern
each add another cumulative UEA.

## Technology-grant UEAs

`CalendarTurnAdvance` (`0x82D1EAB0`) has eight hard-coded branches, not a
parameter table:

| UEA ID | Technology ID | Technology | Retail placement |
| ---: | ---: | --- | --- |
| 9 | 13 | Mathematics | Arabian Medieval |
| 10 | 12 | Literacy | Chinese Medieval |
| 43 | 19 | Religion | Indian Medieval |
| 48 | 32 | Communism | Mongolian Modern |
| 57 | 18 | Monarchy | No retail UEA-table placement |
| 58 | 11 | Irrigation | Egyptian Medieval |
| 59 | 5 | Pottery | French Ancient |
| 60 | 15 | Democracy | Greek Ancient |

Each of the eight branches needs three things: the unresolved selector-17 query
`0x82CEF4E8` returning zero, an unowned technology and an active cumulative
`ActiveCivilizationBonusLookup`. Success calls `TechnologyAcquire` (`0x82D09208`)
with the player, the technology, the context, source (reason) 6 and phase 1.
This generic acquisition also serves research, trade, setup, network and UA
routes. It sets the player's bit in the 48-word table at `0x830EDC48` and
invokes the discovery gameplay and presentation consumers.

The grant opportunity occurs on the configured start turn or at an era
transition, not continuously. All eight use cumulative mode, so a start in a
later era may grant earlier UEAs. Exact mode remains uncalled and unclamped. UA
grants are separate. Arabian index 11 receives Religion 19 when the current
turn minus the start turn equals one, without a UEA query. Saved ownership omits
the provenance of a grant. `0x82CC4040` transfers all 48 words in both
directions, so removing a host rule does not revoke a technology.

UEA 40 has no technology branch. Replacing an existing literal changes another
retail placement. The dormant UEA 57 has no accepted placement, presentation or
AI meaning. Suppressing Mongolian Ancient 40 and granting Horseback Riding 4
would need a new combined producer for civilization and era. It would also need
explicit semantics for irreversible saves, timing, UI, AI and multiplayer. No
public ABI supports it.

## Shared consumers

No table writer, initializer, row cache or second reader is known. Combat,
effective stats, AI, rush, production and economy, the Calendar and other
systems share `ActiveCivilizationBonusLookup`. The relations catalog holds the
exact direct call sites. These edges establish no ID meanings, no selecting
branches, no Calendar effect and no AI parity. A generic variant has one shared
activation mechanism. That does not show that every changed UEA behaves
correctly.

## Effect ownership catalog

An activation ID alone does not identify the code that applies the effect. The
accepted classes of that code map distinct IDs onto all 64 retail cells:

| Class of effect code | Distinct retail IDs | Retail cells | Boundary |
| --- | --- | ---: | --- |
| Shared cumulative lookup | 1, 3, 5, 8, 9, 10, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 28, 30, 32, 34, 35, 41, 42, 43, 47, 48, 50, 55, 56, 58, 59, 60 | 47 | An accepted producer consumes the result of `ActiveCivilizationBonusLookup` for the named effect. |
| Direct civilization and effect path | 40 | 1 | The mapped native effect bypasses the shared lookup. |
| Mixed companion path | None | 0 | No native retail cell is accepted in this class. |
| Unknown | 2, 4, 6, 7, 14, 26, 27, 36, 38, 46, 51, 61 | 16 | No accepted evidence that links the effect's producer and consumer establishes the native function. |

The 95-site inventory requests 44 of 45 retail IDs. It offers search guidance.
It is not proof of a named effect or of the full set of writers, and it does not
exclude direct companions. Merged calls for 12, 16 and 28 escaped the earlier
search for immediate literals. Only 40 lacks a literal request and has a direct
path.

| UEA | Static function and boundary |
| --- | --- |
| 1 | `RoadBuildCostLookup` (`0x82CF83C0`) and `0x82D13978` each independently compose the base road cost, query cumulative 1 and halve the signed result toward zero. The city value feeds affordability before command 7. The factor helper and the full command semantics remain open: [`road-build-cost.json`](../../manifests/road-build-cost.json). |
| 50 | `0x82D13978`, Warrior 6: when the lookup `0x82D15B78` is active, it increments `+0x05`, which is later clamped to two. Another flag also accepts the increment, so this is not the sole veteran grant: [`new-warrior-veteran.json`](../../manifests/new-warrior-veteran.json). |
| 3, 12, 55 | `EffectiveUnitMovementLookup` (`0x82CF1F70`) reads signed `+0x42`. `+0x50 & 0x200` selects 3, Riflemen 10 selects 12, and Warrior 6 selects 55. Each adds one on a normal composed return. The special return remains unresolved: [`unit-movement-stat.json`](../../manifests/unit-movement-stat.json). |
| 8 | `CityGrowthThresholdLookup` (`0x82CF1060`) queries at `0x82CF10F8` using the city player at `+0x00`. The [growth threshold](city-growth.md) page gives the formula, the adjustment and the progress limits. |
| 13 | `EffectiveUnitAttackLookup` (`0x82CF2230`) tests `UnitType` Cannon 17 at `0x82CF236C`, queries `0x82CF2380` and adds two at `0x82CF2390` only on success. |
| 23 | `0x82D13978` adds signed `r18` to the indexed `0x830ED484` and queries `0x82D15618`. If the query is active, it then adds signed `r18 / 2` toward zero. The nonnegative total is `r18 + floor(r18 / 2)`. This maps the arithmetic of Increased Great Person generation. It does not map the enclosing name or layout, or all producers and consumers. |
| 25 | CityUpdate queries `0x82D148BC` and adds half of the Gold intermediate that reaches it before storing at `frame+0x7C`. The income contribution is separate from the rush-rate and other AI valuation calls. The [correction contract](economy-bonus-corrections.md#gold-income-without-the-rush-penalty) preserves this income path. |
| 42 | `0x82D13978` requires local `0x8` clear and the second indexed word zero. The query `0x82D15344` can bypass `0x82D15350..0x82D1536C`, which preserves four indexed halfwords and locals that are otherwise zeroed from `r22`. It is one Anarchy check. The dynamic field and predicate names and other paths remain open. |
| 47 | `CalendarTurnAdvance` query `0x82D1F484` updates `0x830ED544 + player * 4` by `reserve + (reserve + 25) / 50`, with signed truncation. For a nonnegative reserve this is interest of 2 percent, rounded to the nearest, with halves rounding up. The query `0x82CF9FE8` in `0x82CF9F38` adds the same term to the aggregate without storing the reserve. [`gold-reserve-interest.json`](../../manifests/gold-reserve-interest.json) holds the negative boundary. |
| 40 | Capture `0x82D1B400` loads the new civilization at `0x82D1B74C` and tests Mongolian 14 at `0x82D1B758`. On equality it calls the creator at `0x82D1B784`. Otherwise it calls the regular reward at `0x82D1B8BC`. Replacing the table did not suppress it. The Horseback Riding extension became a mixed companion that is not in retail: a synthetic shared grant plus the separate check at `0x82D1B758`. |

A follow-up on the reserve lifecycle found no additional source or caller. It
found no exact references to the base or to an entry point of the function, and
both bodies were non-returning thunks. This shows neither a sole source nor a
consumer, and it leaves the arithmetic unchanged:
[`gold-reserve-aggregate-lifecycle.json`](../../manifests/gold-reserve-aggregate-lifecycle.json).

[`unique-era-ability-effect-ownership.json`](../../manifests/unique-era-ability-effect-ownership.json)
holds the qualifications and the projection onto cells. The repaired complete
yield accessors use the cumulative lookup: Plains +1 Food (16), Sea +1 Food
(28), Forest +1 Production (30), Desert +1 Food and +1 Trade (32), Hills +1
Production (41) and Mountains +2 Production (56). No generic tile API or broader
parity follows.

| Accessor | Yield | Terrain value (UEA ID, increment, call site) |
|---|---|---|
| `0x82CF1CE8` | Food, base table `0x82F771E0` | Plains 2 (16, +1), Sea 0 (28, +1), Desert 5 (32, +1), all at `0x82CF1E28` |
| `0x82CF1AF0` | Production, base table `0x82F771E1` | Forest 3 (30, +1, `0x82CF1C18`), Hills 4 (41, +1, `0x82CF1C40`), Mountains 6 (56, +2, `0x82CF1C68`) |
| `0x82CF17C8` | Trade, base table `0x82F771E2` | Desert 5 (32, +1, `0x82CF1A28`) |

Each accessor reads the terrain value from the table at `0x8312B288`, requests
the cumulative lookup for the matching ID, and adds the amount to its base yield
only when the lookup is active. These are static facts about the three
accessors. Other readers of a tile yield, such as display and AI, are not
enumerated.

## Modification guards

- Do not treat later era entries as replacements for earlier UEAs.
- Do not assume UAs pass through the UEA lookup. The shared lookup reads the
  four cumulative era entries, not the separate UA.
- Do not patch individual UEA consumer branches for a generic variant.
  Recovered UEA consumers already converge on the shared lookup.
- Do not assign gameplay meanings to numeric UEA IDs unless their effects
  are mapped.
- Do not infer AI behavioral parity solely because AI functions call the same
  lookup.
- Do not assume host replacement identity is saved with ordinary technology
  ownership or negotiated between multiplayer peers. The current modding policy
  adds no framework-wide mismatch check.
- Do not reuse UEA ID 57 as an extension point. Its hard-coded Monarchy branch
  has no retail UEA-table placement or accepted effect contract.

## Evidence sources

- [Civilization Unique Ability storage](../../manifests/civilization-bonus-storage.json)
- [City-growth threshold](../../manifests/city-growth-threshold.json)
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Rush-cost producer](../../manifests/rush-cost-producer.json)
- [Game calendar state](../../manifests/game-calendar-state.json)
- [`gold-reserve-interest.json`](../../manifests/gold-reserve-interest.json)
- [`gold-reserve-aggregate-lifecycle.json`](../../manifests/gold-reserve-aggregate-lifecycle.json)
- [Starting technology grants](../../manifests/starting-technology-grants.json)
- [`unique-era-ability-effect-ownership.json`](../../manifests/unique-era-ability-effect-ownership.json)
- [Civilization information panel text
  producers](../../manifests/civilization-info-panel-text-producers.json)
- [Catalog contract](../catalogs.md)
