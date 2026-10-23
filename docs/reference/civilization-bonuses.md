# Civilization Unique Abilities

Each civilization has one UA and four cumulative UEAs: Ancient starts apply
UA/Ancient UEA; later eras add effects without removing earlier ones. Later-era
scenario grants retain the gates below. UAs can grant technology/building/unit/
gold/map state or ongoing rules; they are separate from UEA table `0x82F6F950`:
16 rows, four 32-bit IDs each, stride `0x10`, total `0x100`.

Names are recovered, not debug symbols. Effect evidence is static unless stated;
shared lookup alone proves neither complete effect ownership nor runtime,
presentation, AI, save, scenario or multiplayer parity.

## Recovered storage and lookup

| Item | Address | Accepted meaning |
| --- | ---: | --- |
| Civilization UEA table | `0x82F6F950` | 16 rows by four cumulative era unlock IDs |
| Civilization name pointers | `0x82F7A348` | 16 internal names aligned with the UEA rows |
| Player era array | `0x830ECD08` | Current era index consumed for each player |
| Player civilization array | `0x830ECD28` | Civilization index selecting one table row |
| Excluded player global | `0x82F700B0` | Player index for which the lookup returns false |
| `ActiveCivilizationBonusLookup` | `0x82CF0CB0` | Shared activation owner and only recovered table reader |
| UA text owner | `0x82CF97D0` | Presents the separate UA through `@CIVBONUSTEXT` |

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

Separate UA entries include one-time grants/initial state; German, Indian, Zulu
and Mongolian entries establish ongoing rules.

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

`African` is the internal image string for the player-facing Zulu civilization
at index 13. `Arab` is likewise the internal name for the Arabian civilization
at index 11.

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

Each requires unresolved selector-17 `0x82CEF4E8` zero, unowned technology and
cumulative `ActiveCivilizationBonusLookup`; success calls `TechnologyAcquire`
(`0x82D09208`) with player, technology, context, source/reason 6 and phase 1.
This generic acquisition also serves research, trade, setup, network and UA
routes. It sets player bit in 48-word `0x830EDC48` and invokes discovery
gameplay/presentation consumers.

Opportunity is configured start turn or era transition, not continuous. All
eight use cumulative mode; later-era starts may grant earlier UEAs. Exact mode
remains uncalled/unclamped. UA grants are separate: Arabian index 11 receives
Religion 19 when current-start turn equals one, without UEA query. Saved
ownership omits grant provenance; `0x82CC4040` transfers all 48 words both ways,
so removing a host rule does not revoke technology.

UEA40 has no technology branch. Replacing an existing literal changes another
retail placement; dormant 57 has no accepted placement/presentation/AI meaning.
Suppressing Mongolian Ancient 40 and granting Horseback Riding 4 needs a new
combined civilization/era producer with explicit irreversible-save, timing,
UI/AI/multiplayer semantics. No public ABI supports it.

## Shared consumers

No table writer, initializer, row cache or second reader is known. Combat,
effective stats, AI, rush, production/economy, calendar and other systems share
`ActiveCivilizationBonusLookup`; relations catalog owns exact direct callsites.
These edges establish no ID meanings, selecting branches, calendar effect or AI
parity. A generic variant has one shared activation mechanism, not proof that
every changed UEA behaves correctly.

## Effect ownership catalog

Activation ID alone does not identify effect ownership. Accepted owner classes
project distinct IDs onto all 64 retail cells:

| Owner class | Distinct retail IDs | Retail cells | Boundary |
| --- | --- | ---: | --- |
| Shared cumulative lookup | 1, 3, 5, 8, 9, 10, 12, 13, 16, 17, 18, 19, 20, 23, 24, 28, 30, 32, 34, 35, 41, 42, 43, 47, 48, 50, 55, 56, 58, 59, 60 | 44 | An accepted producer consumes the result of `ActiveCivilizationBonusLookup` for the named effect. |
| Direct civilization/effect path | 40 | 1 | The mapped native effect bypasses the shared lookup. |
| Mixed companion path | None | 0 | No native retail cell is accepted in this class. |
| Unknown | 2, 4, 6, 7, 14, 25, 26, 27, 36, 38, 46, 51, 61 | 19 | No accepted evidence packet linking the effect's producer and consumer establishes the native owner. |

The 95-site inventory requests 44 of 45 retail IDs, offering search guidance,
not named-effect/full-ownership proof or exclusion of direct companions. Merged
calls for 12/16/28 escaped earlier immediate-literal search. Only 40 lacks a
literal request and has a direct owner.

| UEA | Static owner and boundary |
| --- | --- |
| 1 | `RoadBuildCostLookup` (`0x82CF83C0`) and `0x82D13978` independently compose base road cost, query cumulative 1 and halve signed result toward zero. City value feeds affordability before command 7. Factor helper/full command semantics remain open: [`road-build-cost.json`](../../manifests/road-build-cost.json). |
| 50 | `0x82D13978`, Warrior 6: active lookup `0x82D15B78` increments `+0x05`, later clamped to two. Another flag also admits increment; not sole veteran grant: [`new-warrior-veteran.json`](../../manifests/new-warrior-veteran.json). |
| 3, 12, 55 | `EffectiveUnitMovementLookup` (`0x82CF1F70`) reads signed `+0x42`; `+0x50 & 0x200` selects 3, Riflemen 10 selects 12, Warrior 6 selects 55. Each adds one on ordinary composed return; special return remains unresolved: [`unit-movement-stat.json`](../../manifests/unit-movement-stat.json). |
| 8 | `CityGrowthThresholdLookup` (`0x82CF1060`) queries at `0x82CF10F8` using city player `+0x00`; [growth threshold](city-growth.md) owns formula/adjustment/progress limits. |
| 13 | `EffectiveUnitAttackLookup` (`0x82CF2230`) tests `UnitType` Cannon 17 at `0x82CF236C`, queries `0x82CF2380`, adds two at `0x82CF2390` only on success. |
| 23 | `0x82D13978` adds signed `r18` to indexed `0x830ED484`, queries `0x82D15618`, then adds signed `r18 / 2` toward zero if active: nonnegative total `r18 + floor(r18 / 2)`. Maps Increased Great Person generation arithmetic, not enclosing name/layout or all producers/consumers. |
| 42 | `0x82D13978` requires local `0x8` clear/second indexed word zero; query `0x82D15344` can bypass `0x82D15350..0x82D1536C`, preserving four indexed halfwords/locals otherwise zeroed from `r22`. One Anarchy gate; dynamic field/predicate names and other paths remain open. |
| 47 | `CalendarTurnAdvance` query `0x82D1F484` updates `0x830ED544 + player * 4` by `reserve + (reserve + 25) / 50`, signed truncation: ordinary nonnegative interest 2 percent, nearest/half-up. `0x82CF9F38` query `0x82CF9FE8` adds same term to aggregate without reserve store. [`gold-reserve-interest.json`](../../manifests/gold-reserve-interest.json) owns negative boundary. |
| 40 | Capture `0x82D1B400` loads new civilization `0x82D1B74C`, tests Mongolian 14 at `0x82D1B758`, calls creator `0x82D1B784` on equality, ordinary reward `0x82D1B8BC` otherwise. Table replacement did not suppress it; Horseback Riding extension became non-retail mixed companion: synthetic shared grant plus separate `0x82D1B758` gate. |

Reserve lifecycle follow-up found no additional source/caller: no exact base/
owner-entry references and both bodies were non-returning thunks. This proves
neither sole source nor consumer and leaves arithmetic unchanged:
[`gold-reserve-aggregate-lifecycle-boundary.json`](../../manifests/gold-reserve-aggregate-lifecycle-boundary.json).

[`unique-era-ability-effect-ownership.json`](../../manifests/unique-era-ability-effect-ownership.json)
owns qualifications/cell projection. Repaired complete yield accessors use
cumulative lookup: Plains +1 Food (16), Sea +1 Food (28), Forest +1 Production
(30), Desert +1 Food/+1 Trade (32), Hills +1 Production (41), Mountains +2
Production (56). No generic tile API or broader parity follows.

## Modification guards

- Do not treat later era entries as replacements for earlier UEAs.
- Do not assume UAs pass through the UEA lookup. The shared lookup owns the
  four cumulative era entries, not the separate UA.
- Do not patch individual UEA consumer branches for a generic variant.
  Recovered UEA consumers already converge on the shared lookup.
- Do not assign gameplay meanings to numeric UEA IDs unless their effects
  are mapped.
- Do not infer AI behavioral parity solely because AI functions call the same
  lookup.
- Do not assume host replacement identity is saved with ordinary technology
  ownership or negotiated between multiplayer peers. The current modding policy
  adds no framework-wide mismatch gate.
- Do not reuse UEA ID 57 as an extension point. Its hard-coded Monarchy branch
  has no retail UEA-table placement or accepted effect contract.

## Evidence sources

- [Civilization Unique Ability storage](../../manifests/civilization-bonus-storage.json)
- [City-growth threshold](../../manifests/city-growth-threshold.json)
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Rush-cost producer](../../manifests/rush-cost-producer.json)
- [Game calendar state](../../manifests/game-calendar-state.json)
- [`gold-reserve-interest.json`](../../manifests/gold-reserve-interest.json)
- [`gold-reserve-aggregate-lifecycle-boundary.json`](../../manifests/gold-reserve-aggregate-lifecycle-boundary.json)
- [Starting technology grants](../../manifests/starting-technology-grants.json)
- [`unique-era-ability-effect-ownership.json`](../../manifests/unique-era-ability-effect-ownership.json)
- [Civilization information panel text
  producers](../../manifests/civilization-info-panel-text-producers.json)
- [Catalog contract](../catalogs.md)
