# Civilization Unique Abilities

Each civilization has one Unique Ability (UA) and four cumulative Unique Era
Abilities (UEAs). Because every game begins in the Ancient era, both the UA and
Ancient UEA apply immediately. Later eras add another UEA without removing an
earlier effect.

The UA is separate from the image-backed UEA table at `0x82F6F950`. UAs are
heterogeneous: some grant initial state such as a technology, building, unit,
gold, or map knowledge, while others establish an ongoing rule. The UEA table
contains 16 civilization rows with four 32-bit UEA IDs per row, one unlock
for each era. Each row is `0x10` bytes and the complete table is `0x100` bytes.

The names below are recovered semantic labels, not original debug symbols.

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
caller is known. Do not call exact mode without an
independent era range guard.

## Leader and Unique Ability map

The player facing civilization names, leaders, and gameplay descriptions below
are normalized in [`civilizations.csv`](../../data/civilizations.csv) and
[`era-bonus-definitions.csv`](../../data/era-bonus-definitions.csv). The
internal names, row order, and numeric UEA IDs are recovered from the game
image. The [reference data contract](../../data/README.md) records the external
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

The UA column is separate from the four-value UEA table. Its entries are
not all passive effects: some are one-time grants or initial game state, while
the German, Indian, Zulu, and Mongolian entries establish ongoing rules.

## Unique Era Ability IDs

The four values are ordered Ancient, Medieval, Industrial, and Modern. They
are cumulative unlocks, not four mutually exclusive replacements.

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

The Japanese row illustrates the two-layer model. Japan's UA grants knowledge
of Ceremonial Burial, while its Ancient UEA is ID 28, which adds one food to sea
tiles. Both apply from the Ancient era onward. Medieval, Industrial, and Modern
each add another cumulative UEA.

## Technology-grant UEAs

The named technology UEAs do not come from one parameter table.
`CalendarTurnAdvance` at `0x82D1EAB0` contains eight repeated hard-coded
UEA-ID and technology-ID branches:

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

Every branch applies the same shape of checks: the unresolved selector-17
eligibility predicate at `0x82CEF4E8` must return zero, the player must not
already own the technology, and `ActiveCivilizationBonusLookup` must find the
UEA in cumulative mode. A passing branch calls `TechnologyAcquire` at
`0x82D09208` with the player, technology ID, player context, source/reason 6,
and phase flag 1.

`TechnologyAcquire` is the generic ordinary acquisition owner, not a
starting-technology-only function. Research, trade, setup, network, UA, and UEA
routes can converge there with different arguments. It sets the player bit in
the 48-word technology ownership array at `0x830EDC48` and fans the ordinary
discovery through gameplay and presentation consumers.

The UEA grant opportunity occurs at the configured start turn or an era
transition. It is not an always-on rule. All eight branches use cumulative mode;
none uses the uncalled and unclamped exact mode. A later-era scenario start can
therefore qualify earlier technology UEAs as well as the current-era entry.

Initial UAs remain separate. For example, the Arabian Religion UA directly
grants technology 19 when current turn minus start turn equals one and the
player's civilization is Arabian index 11. That branch does not query a UEA
ID. After either route grants a technology, the saved state records ordinary
ownership rather than UA or UEA provenance. The broad serializer at
`0x82CC4040` transfers all 48 ownership words in both directions, so removing a
host rule does not revoke an already-granted technology.

This layout rejects a simple Mongolian substitution. UEA 40, Captured
Barbarian villages become cities, has no technology-grant branch. Replacing an
existing technology literal would change another retail placement, while the
dormant ID 57 branch has no accepted retail placement, presentation, or AI
meaning. A rule that suppresses Mongolian Ancient UEA 40 and grants Horseback
Riding technology 4 would require a new civilization-and-era-scoped composite
producer with explicit irreversible save, timing, UI, AI, and multiplayer
semantics. No public ABI is supported for that producer.

## Shared consumers

The table has no known writer, initializer, copied row cache, or second reader.
Gameplay consumers call
`ActiveCivilizationBonusLookup` rather than reading rows directly. These
consumers include combat, rush-cost calculation, effective unit-stat readers,
AI evaluation, production and economy paths, and other gameplay systems.

Cataloged direct caller relations establish shared lookup consumption across
combat resolution, effective attack and defense readers, AI unit evaluation,
rush application, and calendar turn advancement. Exact callsites remain
canonical in the relations catalog. These edges do not assign meanings to UEA
IDs, prove which branch selects each call, establish AI behavioral parity, or
make the lookup a calendar effect.

This convergence gives a future generic UEA variant one shared table and lookup
mechanism. It does not by itself prove that every possible changed UEA produces
correct AI behavior.

## Effect ownership catalog

The table ID is an activation label, not proof of the native effect owner. The
effect-specific ownership catalog classifies all 64 retail cells by applying
each distinct UEA ID's accepted owner class to the row table above:

| Owner class | Distinct retail IDs | Retail cells | Boundary |
| --- | --- | ---: | --- |
| Shared cumulative lookup | 5, 9, 10, 13, 17, 23, 34, 35, 42, 43, 47, 48, 58, 59, 60 | 21 | An accepted producer consumes the result of `ActiveCivilizationBonusLookup` for the named effect. |
| Direct civilization/effect path | 40 | 1 | The mapped native effect bypasses the shared lookup. |
| Mixed companion path | None | 0 | No native retail cell is accepted in this class. |
| Unknown | 1, 2, 3, 4, 6, 7, 8, 12, 14, 16, 18, 19, 20, 24, 25, 26, 27, 28, 30, 32, 36, 38, 41, 46, 50, 51, 55, 56, 61 | 42 | No accepted effect-specific producer-consumer packet establishes the native owner. |

The 95-site generated inventory contains literal shared-lookup requests for 41
of the 45 retail IDs. That is useful search guidance only. A literal request
does not prove the named effect, complete ownership, or absence of a direct
companion. Retail IDs 12, 16, 28, and 40 do not appear as literal requests;
only UEA 40 has a separately mapped direct owner.

UEA 13 has a bounded shared owner in `EffectiveUnitAttackLookup` at
`0x82CF2230`. The accessor compares the base `UnitType` with Cannon type 17 at
`0x82CF236C`, requests cumulative UEA 13 at `0x82CF2380`, and adds two to the
effective attack value at `0x82CF2390` only after the lookup succeeds. This is
static composition evidence; it does not establish runtime execution,
presentation, or complete AI strategy.

UEA 23 has a bounded shared owner in the accumulation path inside
`0x82D13978`. The path adds retained signed contribution `r18` to an indexed
word based at `0x830ED484`, requests cumulative UEA 23 at `0x82D15618`, and,
when active, adds signed `r18 / 2` with truncation toward zero to the same word.
For a nonnegative contribution the total is `r18 + floor(r18 / 2)`. This maps
the Increased Great Person generation effect and its exact local arithmetic;
it does not name the enclosing function or table layout, recover every Great
Person producer or consumer, or establish runtime, presentation, AI, save,
scenario, or multiplayer behavior.

UEA 42 has a separate bounded shared owner in `0x82D13978`. When a local `0x8`
flag is clear and a second indexed state word is zero, the path requests
cumulative UEA 42 at `0x82D15344`. An active result branches around
`0x82D15350..0x82D1536C`, which would otherwise write retained zero `r22` to
four indexed halfword fields and their associated locals. This maps one exact
Cities are unaffected by Anarchy preservation gate. It does not name the
dynamic fields or predicates, prove every Anarchy path, or establish runtime,
presentation, AI, save, scenario, or multiplayer behavior.

UEA 47 has a closed economy owner. `CalendarTurnAdvance` requests cumulative
UEA 47 at `0x82D1F484`, reads the player-indexed reserve word at
`0x830ED544 + player * 4`, and stores `reserve + (reserve + 25) / 50` using
signed division toward zero. For an ordinary nonnegative reserve, the added
term is 2 percent rounded to the nearest integer with a half-unit rounded up.
`0x82CF9F38` requests the same UEA at `0x82CF9FE8` and adds the identical term
to its retained aggregate without storing the reserve. The complete evidence
and negative-value boundary are in
[`gold-reserve-interest.json`](../../manifests/gold-reserve-interest.json).

UEA 40 is the regression case. The Barbarian-capture path in `0x82D1B400`
loads the new owner's civilization at `0x82D1B74C`, compares it with Mongolian
civilization 14 at `0x82D1B758`, calls the city-record creator at
`0x82D1B784` on equality, and reaches the ordinary reward path at
`0x82D1B8BC` otherwise. Replacing the Mongolian Ancient table cell changed the
shared lookup but did not suppress this direct path. The accepted Horseback
Riding extension therefore became a non-retail mixed companion: a shared
synthetic technology grant plus a separate gate at `0x82D1B758`.

The complete evidence, qualifications, and cell projection are in
[`unique-era-ability-effect-ownership.json`](../../manifests/unique-era-ability-effect-ownership.json).
IDs 30, 32, 41, and 56 have exact shared-lookup seeds, while IDs 16 and 28 are
absent from the accepted lookup inventory. The bounded query did not provide
all three complete exact bodies, so IDs 16, 28, 30, 32, 41, and 56 remain
unknown.

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
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Rush-cost producer](../../manifests/rush-cost-producer.json)
- [Game calendar state](../../manifests/game-calendar-state.json)
- [Gold-reserve interest](../../manifests/gold-reserve-interest.json)
- [Starting technology grants](../../manifests/starting-technology-grants.json)
- [Unique Era Ability effect ownership](../../manifests/unique-era-ability-effect-ownership.json)
- [Catalog contract](../catalogs.md)
