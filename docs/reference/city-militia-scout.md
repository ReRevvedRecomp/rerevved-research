# City Militia and trainable Scout feasibility

Proposed behavior: one extra ordinary type-7 Militia with Loyalty per successful
new human/AI founding, retaining native/scenario defenders. Capture,
reconstruction, loads and civilization-specific definitions are excluded.
Separate five-Production Scout needs title support/evidence.

The [packet](../../manifests/city-militia-scout-feasibility.json) owns image,
locators, hashes and static qualifications; it adds no runtime observation. The
following contracts remain conditional on their stated return/lifetime gates.

## Feasibility verdict

| Requirement | Verdict |
| --- | --- |
| One extra Militia for every newly founded city, human and AI | Conditional hook at the end of successful founding at `0x82D1A314`, restricted to two admitted founding origins. The creator's complete lifetime and delivery exactly once for every founding still need proof. Keep native/scenario defenders. |
| Additional civilization-specific Militia definitions | Rejected for this requirement. Reuse ordinary native type 7 for every civilization. |
| Automatic Loyalty | Rank-neutral OR of `0x8` into unit `+0x10` after retained creator return. Selected defense consumer and default-stream save/load transfer are bound conditionally. |
| A separate trainable Scout costing exactly five Production | Conditional on a distinct title-owned identity, trainability, naming, production and absolute-cost support. Appearance reuses Militia as a placeholder; the current percentage API cannot express the complete contract. |
| Scout is never automatically granted to new cities | Requires proof that grant selection excludes Scout. An added type inside the native defender selector's range could otherwise be selected if it passes the predicates. |
| Scout starts with March and without Loyalty | March needs its bit plus the initial movement adjustment. The current hook is too narrow, and a later native Loyalty writer must be accounted for under its civilization/stat predicates. |

## Established facts

CityCreate selects a defender, stores type at `+0x38`, then conditionally
requests it for signed owner at `+0x30/+0x32`. Nonzero configured start turn and
nonbarbarian owner are required; no human test exists. All-civilization
ingress/allocation remain unproved. Extra Militia accompanies any native unit,
including another Militia.

Selector scans 6 through 37, filtering flags/stats/technology, maximizing
defense with later ties winning. Modern Infantry 11 is possible, not a fixed
scenario grant. Beta selector 4 stores STARTERA 4/STARTYEAR 2025, but
year-to-start-turn publication and exact selecting technology/definitions remain
unjoined; the reported example is conditional, not end-to-end verified.

| Upgrade | Contract and limit |
| --- | --- |
| Loyalty index 3 | `0x8` in live `+0x10`, separate from rank `+0x05`/city loyalty. CityUpdate UEA26 tests live-type flags `0x6` and nonzero attack, then cached production-item defense>attack. Cross-call identity/retention is unproved; [base-consumer packet](../../manifests/unit-definition-base.json#/findings/RVA-F-0277) owns provenance. Russian Medieval/Japanese Modern rows contain 26. Writer changes neither rank nor movement; retained Militia attack zero rejects it, and CityCreate bypasses this production continuation. |
| Loyalty defense | `0x82CFBED0` maps 3 via `0x82CFBF80` to `0x82CFBFD0`. Owner equality with `U8[0x830E8790 + 40*X + Y]` adds 50 at `0x82CFC00C`. Defender call `0x82CDAC10`, join `0x82CDAC18`, retained multiplication `0x82CDB39C`: additive 50 percentage points with other bonuses. Description's "home territory" still needs plane publication/ownership; Engineer is separate. |
| Loyalty persistence | Default stream transfers whole `+0x10` via `0x82CC4040 -> 0x82CC1DA0`, `0x82CC2048/0x82CC2064`, four-byte endian conversion. Requires completed stream, matching format/metadata, retained records/no overwrite; no executed round trip. [Upgrade manifest](../../manifests/unit-special-upgrades.json) owns paths and closed reader searches. |
| March index 6 | `0x40`; earned command adds three movement units and spends rank. Title creation effect adds absent bit/three units once without rank cost, but only in CityUpdate production and excludes base identities. Later native Loyalty can follow; omitting a custom grant proves no universal absence. |
| Scout upgrade index 8 | `0x100`, neither a Scout unit nor required starting effect. |

Creator callback locally writes object pointer/conditional rank, not Loyalty;
opaque child/manager helpers and later gameplay prevent an image-wide negative.
The 29-type public catalog has Militia 7, no Scout.
[Native extent](unit-definitions.md#native-count-and-end-boundary) has occupied
additional rows/end, no safe free slot. The 256 player unit records are
instances, not definition capacity.

Cost is signed factor*composed scalar/2, truncated. Factor five is not cost
five; factor one yields five only for some scalars. Percentage rules neither
register Scout nor express absolute cost.

## Title implementer contract

1. Insert at `0x82D1A314` before displaced word `0x7E038378` (`mr r3,r16`). At
   this final CityCreate tail, admit only saved incoming return PC `0x82CE03AC`
   (command-13 founding) or `0x82CBC040` (AI founding). With current canonical
   SP `F`, that saved PC is `U32[F+0x178]`: CityCreate allocated `0x180` bytes
   and native save14 stored entry LR at incoming SP minus 8.

   Capture's call at `0x82D1B784` and the four inventoried setup calls fail
   this whitelist. Deserialization does not enter either admitted origin.
   CityCreate mode is insufficient: network byte `0x8314F10B` can force it to
   zero at `0x82D18E54`.
2. Retain city slot `j=r16`, owner `p=r20`, X from `U32[F+0x19C]` and Y from
   `U32[F+0x1A4]`. The entry stores and later ordinal reload are `0x82D18DC4`,
   `0x82D18D9C`, `0x82D18DA4` and `0x82D19AC0`. Require `0<=j<128`, a live city
   at `0x8314FE28+0xBC*j`, matching signed owner `+1` and coordinates
   `+0x30/+0x32`, and `0<=p<8`.

   The exhausted-city return `-1` at `0x82D18E88` takes a different unwind and
   never reaches this hook. Preserve the frame and guest continuation state
   across the added call and execute the displaced instruction once.
3. Make one call to `0x82D11750(p,7,x,y)`. Signed `-1` means failure; slot zero
   is valid. For returned `0<=u<256`, validate `U=0x830F2BF0+0x54*(256*p+u)`,
   owner, type 7, slot `+0x30` and coordinates. A valid slot alone does not
   prove a live registered unit.

The mandatory `+0x1A0 -> 0x82D7FE40` callback can destroy its rejected object
and clear `U+0x3C` at `0x82D80238`, yet return normally. Its accepted arm
publishes the object at `0x82D8029C`. Require completing allocation,
constructor, model/manager registration, retained object back-pointer
`+0x84==U`, and lifetime through the final creator return.

   A nonzero object pointer alone does not prove those conditions. The
   following current `+0x1B4` dispatch at `0x82D1199C` is an exact `blr` only
   while its initialized target `0x821D5678` is retained. Do not automatically
   retry a partial object failure: its logical slot may already be occupied.
4. After both callbacks and creator return, on that same validated live unit,
   read/OR/write the big-endian 32-bit word `U+0x10 |= 0x8`. Keep rank and
   movement unchanged; earned command 22 spends rank. The creator's earlier
   84-byte clear erases pre-creation grants. Repeating this OR is idempotent
   for the bit, while repeating the creator allocates another unit.

The contract is conditional on required native calls returning and retaining the
stated frame, registers, records and object/manager lifetime. Seven raw direct
CityCreate calls were inventoried without truncation; this is not a universal
indirect/tail caller or event-delivery proof.

Exactly one extra unit per admitted successful invocation follows from one hook
execution and one call. Validation in the running title is still needed for
human/AI route coverage, network authority/replay, reentrancy and durable
delivery exactly once per city. Immediate upgrade UI refresh after the
post-creator OR is also unbound.

The [canonical contract](../../manifests/city-militia-scout-feasibility.json)
records each gate, selected callback failure/return and native/source locator
under `foundingMilitiaContract`.

## Separate Scout and definition boundaries

Native creator, owner/coordinates, upgrade bits, rank-neutral logic and shared
cost/production readers are starting points; definitions, naming/models, menu/AI
admission and fixed cost need title support/research.

Scout inherits unspecified Militia properties and placeholder appearance;
overrides are name, trainability, five-hammer cost, March, no Loyalty and no
automatic grant. Custom art is unnecessary, but identity routing is required. An
ID within defender range 6 through 37 could win the native predicates and be
granted. No ID/stats/flags are selected here; a separate definition alone does
not prove production-only availability.

## Minimum title support for Scout

The
[focused contract](../../manifests/city-militia-scout-feasibility.json#/minimumScoutSupportBoundary)
requires distinct identity, shared human/AI production/final cost 5,
rank-neutral common creation effects and identity persistence. After native
movement setup, March sets `0x40` and adds three; starting Loyalty `0x8` is
excluded. Automatic ordinary Militia remains separate.

Current civilization/base-type identity and percentage APIs cannot register a
live variant. A Militia-7-backed title identity is a conditional smaller option:
candidate/current-production/live identity must agree across save/load/network.
Renaming every Militia is insufficient; visuals can stay Militia while label is
Scout. Native census remains incomplete; ID 38 storage/registration is
unadmitted.
[Latest consumer result](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/productionNameAndUpgradeContinuation)
retains production/name/upgrade gates.

## Unresolved boundaries

Full creator/lifetime, universal event coverage, territory publication, upgrade
UI, movement persistence and later March replenishment remain open, as do live
definition count, safe extension, names/models, eligibility and AI fallback. The
packet records a cost-hook/city-table address discrepancy without inferring a
runtime defect. Use actual human/AI owner and consistent simulation order;
network evidence proves neither authority, replay/peer synchronization nor
exactly-once delivery. Turn-sync is outside scope.

| Evidence | Finding and remaining limit |
| --- | --- |
| [Count/extent](../../manifests/unit-definition-count-extent.json) | Initialized count, occupied append boundary |
| [Base consumers](../../manifests/unit-definition-base.json#/findings/RVA-F-0277) | Embedded/cached readers, fixed/live bounds, relocation gates |
| [Census validation](../../manifests/unit-definition-base.json#/findings/RVA-F-0278) | Longer-lifetime positive control failed on canonical listing |
| [Disposable coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0279) | Decode recovered; missing ownership blocked replay |
| [Call flow](../../manifests/unit-definition-base.json#/findings/RVA-F-0280) | Normal metadata and pure computed body |
| [Creation reconciliation](../../manifests/unit-definition-base.json#/findings/RVA-F-0281) | Transient retained body/owner/block coverage |
| [Census replay](../../manifests/unit-definition-base.json#/findings/RVA-F-0282) | Control accepted, 16 representatives |
| [Omitted coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0283) | Five decoded/unowned pairs, one undefined, outside eight-byte bodies |
| [Cost decode](../../manifests/unit-definition-base.json#/findings/RVA-F-0284) | 32-bit language excludes inline `std`; preceding store decodes, continuation does not |
| [Detached strategy](../../manifests/unit-definition-base.json#/findings/RVA-F-0285) | Both stores decode with intended widths/flow |
| [Consumer trace](../../manifests/unit-definition-base.json#/findings/RVA-F-0286) | Guarded late low-address narrowing into ram32 |
| [Native observation](../../manifests/unit-definition-base.json#/findings/RVA-F-0287) | Isolated STORE/synthetic return gives low32 address, full eight-byte value |
| [Cost-owner coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0288) | Structural coverage |
| [Shared coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/ordinarySwitchRecoveredObservation) | Seven-owner structural/local census pass; navigation continues classification of verified-file native/count candidates |
| [Count/model](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/countAndModelContinuation) | Eight bases, full 148-byte Militia 7 baseline. Copied zero +0x4A/+0x4C excludes Leonardo's nonzero route, not TechnologyAcquire's technology 0/owner-state 4/live-unit/action gate. Model mask 7 preserves child inputs, not assets/registration. Cost 5/March-without-Loyalty remain separate. |
| [Description/stat](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/descriptionAndStatContinuation) | Five bases, five rejected pairings; copied +0x4A=0 fails normal admission under zero-query return. Eligibility override must reconcile secondary/Leonardo/replacement gates. |
| [Name/model/cost](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/nameIdentityModelCostContinuation) | Loaded name pointer, 38/102 presentation conflict, model-name lifetime, two B readers. Factor 1/final scalar 10 gives 5; delivery after modifiers, training/name/creation policy remain conditional. |
| [AI/city](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/aiAndCityConsumerContinuation) | Eight bases including `0x82CBF570` frame +0x5C reloads. Copied attack 0 skips local searches, proving neither production nor global AI. Instance/city/selector/public bounds differ from count 39. |
| [Movement/selection/rush](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/movementSelectionAndRushContinuation) | Eight bases, two rejected pairs. Retarget `0x82CD7A60` before +0x80 save; movement/rush need coherent row/order, not yet universal March/five-hammer delivery. |

No complete site list, safe storage or extension API is established. Scout needs
these contracts before ID selection; ordinary Militia needs no new definition.
