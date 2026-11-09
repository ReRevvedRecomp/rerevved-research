# City Militia and trainable Scout feasibility

The proposal would grant one extra type 7 Militia with Loyalty whenever a human
or AI player successfully founds a new city. Native and scenario defenders stay
in place. The grant excludes capture, reconstruction, loads and
civilization-specific definitions. A separate Scout costing five Production
needs title support and evidence.

The [finding](../../manifests/city-militia-scout-feasibility.json) records the
image, locators, hashes and static limits. It adds no runtime observation.
The requirements below hold only if the stated returns and lifetimes hold.

## Feasibility verdict

| Requirement | Verdict |
| --- | --- |
| One extra Militia for every newly founded city, human and AI | Possible with a hook at the end of successful founding at `0x82D1A314`, limited to two accepted founding origins. Two points still need proof: the creator's complete lifetime, and delivery exactly once for every founding. Keep the native and scenario defenders. |
| Additional civilization-specific Militia definitions | Rejected for this requirement. Reuse native type 7 for every civilization. |
| Automatic Loyalty | A rank-neutral OR of `0x8` into unit `+0x10`, made after the creator returns and its result stays valid. The selected defense consumer and the save and load transfer in the default stream are tied to code under conditions. |
| A separate trainable Scout costing exactly five Production | Possible only with five kinds of title support: a distinct identity defined by the title, trainability, naming, production and an absolute cost. Its appearance reuses Militia as a placeholder. The current percentage API cannot express the complete contract. |
| Scout is never automatically granted to new cities | Needs proof that grant selection excludes Scout. An added type inside the range of the native defender selector could otherwise be selected if it passes the predicates. |
| Scout starts with March and without Loyalty | March needs its bit plus the initial movement adjustment. The current hook is too narrow. A later native Loyalty writer must also be accounted for under its civilization and stat predicates. |

## Established facts

CityCreate selects a defender and stores its type at `+0x38`. It then requests
that unit for the signed owner at `+0x30` and `+0x32`, under conditions. A
nonzero configured start turn and a nonbarbarian owner are required, and no
test for a human player exists. Entry and allocation for all civilizations are
not yet shown. An extra Militia accompanies any native unit, including another
Militia.

The selector scans types 6 through 37. It filters on flags, stats and
technology, and it maximizes defense, with later types winning ties. Modern
Infantry 11 is possible. It is not a fixed scenario grant. The Beta selector 4
stores `STARTERA` 4 and `STARTYEAR` 2025. The publication of a start turn from a
year, and the exact selecting technology and definitions, are not yet linked.
The reported example holds only under conditions and is not verified end to
end.

| Upgrade | Contract and limit |
| --- | --- |
| Loyalty index 3 | `0x8` in live `+0x10`, separate from rank `+0x05` and from city loyalty. CityUpdate `UEA26` tests the live-type flags `0x6` and a nonzero attack, then tests whether the cached production-item defense exceeds attack. Identity across calls, and whether it stays valid, are not yet shown. The [base-consumer finding](../../manifests/unit-definition-base.json#/findings/RVA-F-0277) holds the provenance. The Russian Medieval and Japanese Modern rows contain 26. The writer changes neither rank nor movement. A Militia attack of zero that stays zero rejects it, and CityCreate bypasses this production continuation. |
| Loyalty defense | `0x82CFBED0` maps 3 through `0x82CFBF80` to `0x82CFBFD0`. When the owner equals `U8[0x830E8790 + 40*X + Y]`, it adds 50 at `0x82CFC00C`. The defender call is `0x82CDAC10`, the link is `0x82CDAC18` and the multiplication is `0x82CDB39C`. The result is an additive 50 percentage points with other bonuses. The description's wording about the unit's home territory still needs the plane publication and the territory owner. The Engineer is separate. |
| Loyalty persistence | The default stream transfers the whole `+0x10` through `0x82CC4040 -> 0x82CC1DA0`, `0x82CC2048` and `0x82CC2064`, with a four-byte endian conversion. This needs a completed stream, matching format and metadata, and records that stay valid with no overwrite. No round trip was executed. The [upgrade finding](../../manifests/unit-special-upgrades.json) holds the paths and the closed reader searches. |
| March index 6 | `0x40`. The earned command adds three movement units and spends rank. The title's creation effect adds the absent bit and three units once, without a rank cost, but only in the CityUpdate production path, and it excludes the base identities. A later native Loyalty can follow. Omitting a custom grant does not show a universal absence. |
| Scout upgrade index 8 | `0x100`. It is neither a Scout unit nor a required starting effect. |

The creator callback locally writes the object pointer and, under a condition,
the rank. It does not write Loyalty. Opaque child and manager helpers and later
gameplay prevent a negative result for the whole image. The public catalog of 29
types has Militia 7 and no Scout. The [native extent](unit-definitions.md#native-count-and-end-boundary)
has further occupied rows and an end. It has no safe free slot. The 256 player
unit records are instances, not definition capacity.

Cost is the signed factor times the composed scalar divided by 2, truncated. A
factor of five does not mean a cost of five. A factor of one yields five only
for some scalars. Percentage rules neither register Scout nor express an
absolute cost.

## Title implementer contract

1. Insert the hook at `0x82D1A314`, before the displaced word `0x7E038378`
   (`mr r3,r16`). This is the final tail of CityCreate. Accept only the saved
   incoming return PC `0x82CE03AC` (founding by command 13) or `0x82CBC040` (AI
   founding). With current canonical SP `F`, that saved PC is `U32[F+0x178]`.
   CityCreate allocated `0x180` bytes, and native save14 stored the entry LR at
   incoming SP minus 8.

   The capture call at `0x82D1B784` and the four inventoried setup calls fail
   this whitelist. Deserialization does not enter either accepted origin.
   CityCreate mode is not sufficient, because the network byte `0x8314F10B` can
   force it to zero at `0x82D18E54`.
2. Keep the city slot `j=r16`, the owner `p=r20`, X from `U32[F+0x19C]` and Y
   from `U32[F+0x1A4]`. The entry stores and the later ordinal reload are at
   `0x82D18DC4`, `0x82D18D9C`, `0x82D18DA4` and `0x82D19AC0`. Require four
   things: `0<=j<128`; a live city at `0x8314FE28+0xBC*j`; a matching signed
   owner at `+1` and matching coordinates at `+0x30` and `+0x32`; and `0<=p<8`.

   The return of `-1` for an exhausted city at `0x82D18E88` takes a different
   unwind and never reaches this hook. Preserve the frame and the guest
   continuation state across the added call, and execute the displaced
   instruction once.
3. Make one call to `0x82D11750(p,7,x,y)`. A signed `-1` means failure, and slot
   zero is valid. For a returned `0<=u<256`, validate
   `U=0x830F2BF0+0x54*(256*p+u)`, the owner, type 7, slot `+0x30` and the
   coordinates. A valid slot alone does not show a live registered unit.

The mandatory `+0x1A0 -> 0x82D7FE40` callback can destroy its rejected object
and clear `U+0x3C` at `0x82D80238`, yet return normally. Its accepted branch
publishes the object at `0x82D8029C`. Require five things: completed
allocation, the constructor, model and manager registration, the object
back-pointer `+0x84==U` staying valid, and a lifetime that lasts through the
final creator return.

   A nonzero object pointer alone does not show those conditions. The following
   current `+0x1B4` dispatch at `0x82D1199C` is an exact `blr` only while its
   initialized target `0x821D5678` is unchanged. Do not automatically retry a
   partial object failure, because its logical slot may already be occupied.
4. After both callbacks and the creator return, on that same validated live
   unit, read the big-endian 32-bit word, OR in the bit and write it back:
   `U+0x10 |= 0x8`. Keep rank and movement unchanged. The earned command 22
   spends rank. The earlier 84 byte clear by the creator erases pre-creation
   grants. Repeating this OR is idempotent for the bit, while repeating the
   creator allocates another unit.

The contract holds only if the required native calls return and the stated
frame, registers, records and object and manager lifetime stay valid. Seven raw
direct CityCreate calls were inventoried without truncation. This does not show
that no other caller exists through an indirect call or a tail call, and it does
not show delivery of an event.

Exactly one extra unit per accepted successful invocation follows from one hook
execution and one call. Validation in the running title is still needed for four
things: coverage of the human and AI routes, network authority and replay,
reentry, and durable delivery exactly once per city. The immediate refresh of the
upgrade UI after the OR that follows the creator is also not tied to code.

The [canonical contract](../../manifests/city-militia-scout-feasibility.json)
records each check, each selected callback failure and return, and each native
and source locator under `foundingMilitiaContract`.

## Separate Scout and definition boundaries

The native creator, the owner and coordinates, the upgrade bits, the
rank-neutral logic and the shared cost and production readers are starting
points. Definitions, naming, models, menu and AI acceptance, and a fixed cost
need title support and research.

Scout inherits unspecified Militia properties and the placeholder appearance.
Six things are overridden: the name, trainability, a five-hammer cost, March, no
Loyalty and no automatic grant. Custom art is unnecessary, but routing of the
identity is required. An ID inside the defender range 6 through 37 could win the
native predicates and be granted. No ID, stats or flags are selected here. A
separate definition alone does not show that the unit is available only through
production.

## Minimum title support for Scout

The [focused contract](../../manifests/city-militia-scout-feasibility.json#/minimumScoutSupportBoundary)
requires four things: a distinct identity, a shared human and AI production path
with a final cost of 5, rank-neutral common creation effects, and persistence of
the identity. After the native movement setup, March sets `0x40` and adds three.
The starting Loyalty `0x8` is excluded. The automatic Militia stays separate.

The current civilization and base-type identity and the percentage APIs cannot
register a live variant. A smaller option, which holds only under conditions, is
a title identity backed by Militia 7. The candidate, the current production and
the live identity must agree across save and load and the network. Renaming
every Militia is not sufficient. The visuals can stay Militia while the label is
Scout. The native census remains incomplete, and the storage and registration of
ID 38 is not accepted. The [latest consumer result](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/productionNameAndUpgradeContinuation)
keeps the production, name and upgrade checks.

## Production identity carrier

In game terms, a city's production choice is stored as one native item number.
Militia is item 7, and a Scout built on Militia would share that number. A mod
that adds a trainable Scout has to decide what the number 7 means whenever a
production command carries it.

The smaller design reserves item 7. Every explicit production command 5 whose
full item word is exactly 7 means Scout. Militia stays untrainable, and the
Militia that founding, scenarios and defenders give out stays Militia. That
needs no second row key, request ID or extra command word, but it does need
every human, AI and peer producer to agree on the rule. It is a proposed
meaning, not a backend that exists.

Worked example. A new city starts with current production 7, written by
CityCreate at `0x82D19AEC` as the founding default when the selected defender
type is 7 (the selection can be Modern Infantry 11). That is Militia, not Scout.
The player opens the production menu and picks the Scout row, which also holds
item 7. The two values are equal, so the game sees no change. On the AI and
general submit path, the equality at `0x82CB44B0` exits without sending a
command. On the human path, the equality at `0x82E02D20` skips the change
helper `0x82E02C50`, though the confirmation can still reach the producer at
`0x82E02D94`. A mod must therefore compare what the city is building (Militia
or Scout) against what was picked, not the two native numbers.

### How the choice reaches the city

| Step | Address | What it does |
|---|---|---|
| Menu row copy | `0x82E01680`, `0x82E01688`, `0x82E01690` | Reads the row item and stores it at the production child `+0x448`. An invalid row stores -1. |
| Handler | `0x82E02CE0` | Reads category `+0x440` and item `+0x448`. The unit branch `0x82E02D94 -> 0x82CEE650` forwards owner, city and item, not the row number. |
| Candidate list | `0x82CEBC38` | Fills scratch `0x8312D7B0` with 32 bit item words and visits each unit type once. |
| Human wrapper | `0x82CED7E8` | Skips `S` leading negative words and copies `(100 - S) * 4` bytes. Original row `a` becomes row `a - S`. |
| Human producer | `0x82CEE650` | Builds the command `(5, owner, city, item, U32[0x82F7AD00])`. The fifth word is the live random state, so it is not spare storage. |
| General producer | `0x82CE1950` | Builds the same five words. The submit helper's `mr r6,r7` at `0x82CB44BC` forwards the picked item unchanged. |
| Command 5 writer | `0x82CE0020` | After matching the city's owner, calls `0x82CB3F08(city)` and stores the low halfword of the item at city `+0x38`. |
| Later completion | CityUpdate | Reads the current item without making the candidate list again. |

The command ring has 32 slots of 20 bytes and queues commands. It is not a
build queue for a city. A constructed command is not delivered production.

Two rows holding 7 would lose their difference at `+0x448`, so a design with
several aliases would need an extra carrier. The one alias design avoids that:
every trusted candidate 7 means Scout.

### Preview is not a choice

City `+0x38` is also used for temporary previews. In `0x82CE9490`,
`0x82CE9DF8` saves the current item, `0x82CE9DFC` puts in a candidate building,
the cost calls run, and `0x82CE9E20` puts the old item back. None of that picks
production. A mod that tracks a Scout flag cannot treat every write to
`+0x38` as a selection. It needs to separate a committed choice from a preview,
keep the old context until the command-5 helper has read it, and publish the new
context only after the store at `0x82CE0020`. The list of writers in
[`production-item-writers.json`](../../manifests/production-item-writers.json)
is not complete.

The runtime observation on record saw building and wonder items at the command 5
store. It did not see a Scout choice, a Scout flag, delivery of the command or a
change between two items with the same native number.

### Automatic production and the AI

CityCreate also stores the current item at `0x82D19AEC` and grants a native unit
at `0x82D19C4C`. When the selected defender type is 7, these are Militia and
must not be read as Scout. A watcher on every current item 7 cannot tell them
apart. The automatic origins at `0x82D163BC -> 0x82CF1060` and the reselection
at `0x82D160F8` matter too: an equal native 7 can keep a stale Scout flag.

One AI case follows from the accepted rules. Militia has attack 0, so the branch
at `0x82CB6754..0x82CB6764` (attack 0 and item not 28) takes the same bypass as
the type 0 case, and item 7 is below 100. If the checks hold, item 7 skips the
five direct current item stores. This is inferred from the definition baseline,
not shown by a run. Do not apply it to a changed definition or a tagged item.

### Limits and open questions

- The census of producers found no explicit command 5 that carries item 7 as
  Militia, but it cannot show that none exists. Indirect and earlier built
  commands are not covered.
- The row copy at `0x82E01680` and `0x82E01688`, and the recreation store at
  `0x82CD7954`, come from the recompiled code, not from word reads of the image.
  The recreation store is not shown to restore movement for the next turn.
- The recompiled code confirms the copy and the compare at `0x82E02D20` but does
  not show the human confirmation being suppressed.
- No Scout menu, flag or command was observed. Detailed native fields and the
  limits above are in
  [`scoutProductionCarrierBoundary`](../../manifests/city-militia-scout-feasibility.json#/scoutProductionCarrierBoundary).
  The assignment and queue facts are in
  [`occ-settler-production-requirements.json`](../../manifests/occ-settler-production-requirements.json)
  and [`city-production.json`](../../manifests/city-production.json)
  (`RVA-F-0183`, `RVA-F-0184`, `RVA-F-0185`). Their Settlers observations are not
  results for Scout.

## Unresolved boundaries

Several points remain open: the full creator and its lifetime, coverage of every
event, the publication of territory, the upgrade UI, the persistence of movement
and the later replenishment of March. So do the live definition count, a safe
extension, names and models, eligibility and the AI fallback. The finding
records a discrepancy between the addresses of the cost hook and the city table,
without inferring a runtime defect. Use the actual human or AI owner and a
consistent simulation order. Network evidence shows neither authority, nor
replay and peer synchronization, nor delivery exactly once. Turn synchronization
is outside the scope.

| Evidence | Finding and remaining limit |
| --- | --- |
| [Count and extent](../../manifests/unit-definition-count-extent.json) | The initialized count and the occupied append boundary. |
| [Base consumers](../../manifests/unit-definition-base.json#/findings/RVA-F-0277) | Embedded and cached readers, fixed and live limits, and the checks on relocation. |
| [Census validation](../../manifests/unit-definition-base.json#/findings/RVA-F-0278) | A positive control with a longer lifetime failed on the canonical listing. |
| [Disposable coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0279) | Decoding recovered. Missing coverage of the containing function blocked the replay. |
| [Call flow](../../manifests/unit-definition-base.json#/findings/RVA-F-0280) | Normal metadata and a pure computed function body. |
| [Creation reconciliation](../../manifests/unit-definition-base.json#/findings/RVA-F-0281) | Transient coverage of the function body, its containing function and its basic block. |
| [Census replay](../../manifests/unit-definition-base.json#/findings/RVA-F-0282) | The control was accepted, with 16 representatives. |
| [Omitted coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0283) | Five pairs were decoded but unowned, and one was undefined. All lie outside the eight-byte bodies. |
| [Cost decode](../../manifests/unit-definition-base.json#/findings/RVA-F-0284) | The 32-bit language excludes an inline `std`. The preceding store decodes, and the continuation does not. |
| [Detached strategy](../../manifests/unit-definition-base.json#/findings/RVA-F-0285) | Both stores decode with the intended widths and flow. |
| [Consumer trace](../../manifests/unit-definition-base.json#/findings/RVA-F-0286) | A guarded late narrowing of a low address into ram32. |
| [Native observation](../../manifests/unit-definition-base.json#/findings/RVA-F-0287) | An isolated STORE with a synthetic return gives the low 32 bit address and the full eight-byte value. |
| [Cost function coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0288) | Structural coverage. |
| [Shared coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/ordinarySwitchRecoveredObservation) | Structural and local coverage of seven containing functions. The native and count candidates in the verified file are not yet classified. |
| [Count and model](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/countAndModelContinuation) | Eight bases and the full 148 byte Militia 7 baseline. A copied zero at `+0x4A` and `+0x4C` excludes Leonardo's nonzero route. It does not exclude the checks of TechnologyAcquire on technology 0, owner-state 4, a live unit and the action. Model mask 7 keeps the child inputs, but not the assets or the registration. A cost of 5 and March without Loyalty remain separate. |
| [Description and stats](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/descriptionAndStatContinuation) | Five bases and five rejected pairings. A copied `+0x4A=0` fails normal acceptance when the query returns zero. An eligibility override must reconcile the secondary, Leonardo and replacement checks. |
| [Name, model and cost](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/nameIdentityModelCostContinuation) | The loaded name pointer, the presentation conflict between 38 and 102, the lifetime of the model name, and two B readers. Factor 1 and a final scalar of 10 give 5. Delivery after the modifiers, and the training, name and creation policy, remain open and depend on conditions. |
| [AI and city](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/aiAndCityConsumerContinuation) | Eight bases, including the `frame+0x5C` reloads of `0x82CBF570`. A copied attack of 0 skips the local searches. It shows neither production nor global AI behavior. The instance, city, selector and public limits differ from count 39. |
| [Movement, selection and rush](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/movementSelectionAndRushContinuation) | Eight bases and two rejected pairs. The retarget `0x82CD7A60` comes before the save at `+0x80`. Movement and rush need a coherent row and order. Universal delivery of March and the five-hammer cost is not yet shown. |

No complete site list, safe storage or extension API is established. Scout needs
these contracts before an ID is selected. Militia needs no new definition.
