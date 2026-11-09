# Game of the Week seed and week replay

The new-game setup call at `0x82D91A94 -> 0x82DADC88` recomputes the weekly seed
after the early manual-seed call. It also runs for ordinary new games, so a
manual GotW override must require current setup mode `+4 == 2` and the accepted
manual launch. `0x82D8685C` is the separate load/record-restore writer observed
with mode 3.

## Settings input contract

Boolean `gotw_custom_seed` defaults to `false`. With the box unchecked and
no week override, the game uses the shared weekly selection. Checking it
enables a manual seed. An explicit week is independent: choosing only a seed
retains the native week and does not infer a historical week.

After native session `==1`, pre-`0x82E76ED4 -> 0x82DADC88` has fresh setup r3,
week r4, zero r5; entry LR `0x82E76ED8` identifies origin.

| Setting | Contract |
| --- | --- |
| Default `false`, no week override | Retain native r4/r5=0 at both writers. |
| `true` | Validate [content membership](#content-backed-seeds-and-dlc-error); zero-extend seed into r5 at `0x82E76ED4`, reapply before `0x82D91A94` only for `+4 == 2`/matching launch. Week follows independent replay policy. |

Preserve session/mode/setup, registers, condition state, frame/memory; change
argument only, not global seed/clock. Low32 r5 zero means automatic selection
even if upper bits are set. An explicit seed stores all 32 bits at `+0x138` ,
admitting `1..4294967295` without checking for a positive signed value or a
narrower range. Content supports fewer seeds. Automatic zero is not locally
excluded. Acceptance alone proves neither generation nor loading.

## Week, seed and civilization

Writer stores low32 week w at `+0x134`. Automatic expanded-MapList ordinal is
`(w mod N_sel)+1`; explicit seed skips selection only for this invocation, not
later r5=0 calls or configuration/map-count lookup. Nonzero unsigned N/C give
`+0x13C`:

`civilization = ((floor(w/N) + seed) mod 2^32) mod C`

`0x82DADCF4..0x82DADD18` derives week/seed/civilization, no scenario/difficulty/
era; entry handler sets difficulty. Selection/civilization counts are separate
samples requiring stable configuration. Zero-divisor traps follow week/seed
stores and can leave partial state.

The same seed need not select the same civilization with a different week
or different counts. Supply it before
writer and player-slot publication `0x82E76F14`. Generation `0x82D0F13C` samples
`+0x138`; `0x82D0F154` clears `0x82F7AD04`, `0x82D0F164` copies seed to
`0x82F7AD00`, without local zero/mode test.

## Content-backed seeds and DLC error

Pinned archives support 277 distinct seeds in `1..300`, excluding 23. Use
extracted membership: `Pregame.FPK` member `ccglobaldefines.xml` at `0x2D34`,
`MapList` XML line 228/archive `0x60AC`, expands to 277 unique entries. Under
selector/retention guards, automatic seed is `expandedMapList[week % 277]`;
`(week % 277)+1` is ordinal, not seed. Stable configuration gives civilization
N=277.

`Misc0.FPK`/`Misc1.FPK` each-role membership matches exactly 277 complete
height/blend/lightmap triples; no Map500 role.
[Archive identities](../../manifests/game-of-the-week-local-generation.json#/manualMapSeedBoundary/contentSeedDomainBoundary/contentVersion)
bound this domain. Replacement configuration/textures/registered content can
change it; presence/DDS signatures prove neither decoding nor all-seed success.

Getter `0x82E101E0`, candidate cell `0x82120F04`, supplies terrain key. Numbered
`0x82C6E188` builds the numbered heights filename from `+0x9C`; failed load returns false
`0x82C6E204`. Caller clears `+0x54` at `0x82C6EB00`, calls `0x82C6AEB8`.
Retained zero `+0x54` and `0x8314F251` make `0x82C6E898` false; nonzero fallback
takes another path. `0x82C7E760` propagates false; `0x82D86B34..0x82D86BF4`
selects generic unavailable/corrupt content, body `0x82137AD0`, "Downloadable
Content" heading `0x8211F118`. Heading identifies no failed resource. Manifest
qualifies getter/retention/flags and seed 500/276/278 observations.

Numbered textures require membership validation: `1..300` admits 23 missing
keys; wider nonzero writer domain supplies no textures.

## Map source and later seed changes

MapList supplies a scalar seed that may also be a key for prebuilt textures.
It does not supply terrain or a scenario. Changing its ordinal neither supplies
an arbitrary seed nor prevents later overwrites.
`0x82D86AD0` passes zero/named-map pointer according to `0x8314F252`;
constructor r3 is name, not setup. Successful `0x82D0ADE0` `.map` load bypasses
`0x82D0F0FC`; otherwise enters `0x82D0F100`.
[Loader boundary](../../manifests/map-authoring-loader.json) owns
bytes; no week-to-name selection is proved.

Procedural `0x82D0F11C` loads G from `0x8314EFC8` into r9; `0x82D0F13C` captures
G+0x138 in r27. At first draw `0x82D0F3C4`, fill/ frame guards retain
seed/r24=0, with no intervening time/week/constant reseed. Live
modulus/normalization and full generation remain unresolved.

## Later writer

`sub_82D91A78` is `0x821368CC` slot `+0x10`. Setup `0x82D21C20..0x82D21C88`
constructs it, copies `+0x134` to command `+0x34`, conditionally submits through
manager child; `0x82D90BA0` is another producer. Current child/targets/object
retention qualify indirect delivery.

Before `0x82D91A94`: r3=current `0x8314EFC8`, r4=command `+0x34` loaded before
replacing r3, r5=0; entry LR `0x82D91A98`. No mode test: both 1/2 reach it, and
nonzero week still reselects seed/recomputes `+0x13C`.

| Site | Week and seed arguments | Condition |
| --- | --- | --- |
| `0x82D91A94` | Incoming command object+0x34; current setup r3; r5=0 | New-game modes 2 and 1; manual override requires mode 2 and matching launch. |
| `0x82D8685C` | Loaded record word at sp+0xB0; r5=0 | Load/record-restore context observed in mode 3; reached arm requires retained incoming r8=0. |
| `0x82D21D98` | Converted random-helper result; r5=0 | Setup week is zero, plus session/registry gates. |
| `0x82D21E50` | Week 1; r5=0 | Setup week is zero. |
| `0x82D06390` | Forwarded input; r5=0 | Tail wrapper; actual caller unbound. |
| `0x82E2C270` | Converted random-helper result; r5=0 | Separate reset continuation. |
| `0x82E2E294` | Input object+0x20 and +0x24 | Separate setup replacement continuation. |

Load `0x82D86854` restores record RNG to `0x82F7AD00`; `0x82D8685C` uses record
week/zero seed to write `+0x134`/automatic `+0x138`/`+0x13C`, without changing
mode. Guard is retained r8=0, not explicit mode 3; `sub_82D86400` has other
possible contexts. No custom-save or regeneration contract follows. Retained
nonzero week skips two zero-week arms. `0x82CC2B24..0x82CC2B80` initializes
serializer local from `+0x134`, calls helper by address, then copies to record;
load week depends on helper output.

Seed stores: automatic `0x82DADCB4`, explicit `0x82DADCBC`; resets/copies
`0x82DAD400`/`0x82DAD5B8`/`0x82DAD5E4` have unjoined receiver/order. Inventory
excludes no aliased/bulk/external/indirect writer. Week reseed
`0x82D21E60 -> 0x82E2A638` passes setup+0x134; `0x82E2A658` stores `0x82F7AD00`,
`0x82E2A680` clears counter. Other resets: `0x82E2C2A0/0x82E2C2C0`,
`0x82E2E2CC/0x82E2E2E0`; record copy `0x82D86854`. General order remains
unknown. `0x82D10FB8/0x82D10FBC` restores after terrain/before start
coordinates, so explains no pre-terrain reseed; new-game overwrite is
`0x82D91A94`.

Visual key is separate: `0x82C6EABC` dispatches registry+0x54; `0x82C6EAC4`
stores terrain+0x9C, used by `0x82C6E188` for `Map%d` when named selector is
clear. Candidate `0x82120EB0` +0x54 getter `0x82E101E0` reads setup+0x138 at
`0x82E101E8`. Actual slot/order need observation; generator-only overrides can
leave visuals using another seed.

| Question | Verdict and confidence |
| --- | --- |
| 1. Procedural or fixed map? | The reached mode-2 procedural arm copies the current setup seed. A successful named-map load still bypasses it. The use of MapList as a terrain loader is disproved. |
| 2. Setup retention/overwrite? | Native operands and the new-game overwrite at `0x82D91A94` are bound; full alias coverage remains open. |
| 3. Reseed before terrain? | Conditional, strong: none in the inspected interval from the copy to the first draw under its guards; other week reseeders have unbound ordering. |
| 4. Minimal seed-only intervention? | Reapply the latched manual r5 before `0x82D91A94`, gated on mode 2 and launch identity. Full implementation acceptance remains conditional. |
| 5. Probe for one launch? | Incoming LR and setup mode distinguish early, new-game and load origins. Runtime evidence qualifications are in the manifest. |

## Minimal runtime discriminator

Use an observer that is disabled by default with a request identity and
monotonically increasing event sequence. Preserve guest state and record
incoming LR before it changes. The writer origins distinguish the new-game
overwrite from load restoration. Record every writer/reseeder hit up to a
declared event cap; mark truncation as inconclusive for complete ordering.

1. At every `0x82DADC88` entry, log LR, r3/r4/r5, the global setup pointer and
   setup +4/+0x134/+0x138/+0x13C. At `0x82DADD1C`, log the same fields through
   retained r31. LR `0x82E76ED8` identifies early setup, `0x82D91A98` the
   later new-game writer, and `0x82D86860` the observed load writer. Record
   mode on each hit; the new-game wrapper also runs in mode 1.
2. At `0x82D0F0D0`, log LR, optional name r3, current setup and its fields,
   named-selector byte `0x8314F252` and selector pointer `0x83137F88`.
   Record the low-byte loader result at `0x82D0F0F4` and a hit at `0x82D0F100`.
3. Before `0x82D0F13C`, log r9=G and G's fields. At `0x82D0F168`, log r27,
   PRNG words +0/+4/+8, normalization bits +0x10 and saved old state sp+0x88.
   At the first `0x82D0F3C4` hit, log r27/r24/r5, f0 bits and r31/r16 dimensions.
4. Log reached reseeders listed above with sequence, caller and input value.
   At common exit `0x82D10FC4`, record the chosen branch and digests of logical
   terrain/flag cells, using valid dimensions and stride 40.
5. At `0x82C6EABC`, capture the actual registry receiver/vptr/+0x54 target;
   at `0x82C6EAC8`, capture r31's +0x9C key/+0x54 flag and current setup seed.
   Optional `0x82C6EAD8` captures the prebuilt-texture load result.

A later automatic writer followed by its value at the generator identifies
re-derivation. A changed setup pointer identifies replacement. A successful
named load without F100 identifies file terrain. A manual value at both F168 and
the first draw rejects a pre-terrain reseed in that observed interval.

Changed terrain digests with an unchanged visible map direct attention to the
recorded texture key and load result. No constructor hit leaves its caller gate
unresolved.

## Shared weekly inputs

Selected ReRevved SDK converts guest FILETIME directly to `sys_days`, Sunday
zero, without local-time conversion. Guest clock base/scaling can differ despite
matching host dates. With valid clock fields/helpers, `0x82D2EFE0` selects
preceding Sunday noon (previous week before Sunday noon); day scalar/unsigned
divide `0x82D8CC14` gives Sunday 12:00 UTC boundaries for checked 2006-2099.
This is source evidence, not retail timezone or observed rollover.

Shared games need equal effective week, expanded MapList contents/order/counts,
civilization definitions/order, generator version and map-affecting options.
Count alone is insufficient. Manifest retains membership/identity and the
count/length/digest/extraction below.

## Retention and result isolation

Privilege adapter/native epilogue returns are conditional. Base XEX clears both
tested privilege bits, but patched module/global predicate remains unknown.
First native edge is `0x82814324 -> 0x82E92C04` = `__imp__NtCreateEvent`.
Constructor/publisher retention precedes configuration receiver `+0x50` at
`0x82C79104`; explicit seed does not bypass it. Keep
setup/week/seed/civilization through callbacks, player-slot write and start
request. `0x82D8A2E0` can dispatch child `+0x14`/`+0x54` and `+0x10`/`+0x50`;
targets/effects/ordered generation delivery remain conditional despite the bound
later overwrite.

Latch manual origin independently of checkbox changes. Result namespace uses
week `+0x134` ; property `0x20000038` label "Seed" means week, not `+0x138` .
Guard local score/week caches and base/victory-child submissions from
classifying custom results as shared challenge. Filtering only the final host
submission does not prove that local caches are protected. Retain
session/failure cleanup. The selected
[save/load boundary](#saving-and-loading) separates native record requests
from unproved custom-origin/rules/profile persistence. No leaderboard support
is required.

Gates/revisions/locators:
[`game-of-the-week-local-generation.json`](../../manifests/game-of-the-week-local-generation.json),
`manualMapSeedBoundary`, `settingsSeedContract`,
`configurationPublisherBoundary.constructorImportBoundary.nativeReturnBoundary`.

## Saving and loading

A Game of the Week game cannot be saved or loaded from the pause menu. A normal
game shows Controller, Save, Load, Options and Exit. A Game of the Week game
shows only Controller, Options and Exit, so both Save and Load are missing, not
greyed out. The code shows how the game would behave if a mod put Save back.
A Game of the Week save or load at runtime has not been observed.

Worked example. A player starts the current week's game, plays to turn 10 and
opens the pause menu. The menu builder `0x82D06398` reads setup mode, finds 2,
clears its save permission and builds the short list. If a mod changed only that
comparison, Save would reach the common writer `0x82D82510`. The record would
hold the week, the current random number state, the player civilizations, the
calendar and the logical map. Whether the setup mode, the original map seed or
any host setting survive a save and load is not established, and the whole
format is not shown to leave them out. On the load path read here, the game
takes the week from the record, works out the seed and setup civilization
again, and does not restore the setup mode. Such a reloaded game may no longer
look like a Game of the Week game to anything that tests setup mode.

### Why the menu has no Save

Special Functions `0x82D06398` builds one permission value before it chooses a
list. All of these must pass, or the short list is built:

| Check | Requirement |
|---|---|
| `0x82D06468..0x82D06470` | Byte `0x8314F10B` (the network game byte) is zero. |
| `0x82D06474..0x82D0647C` | Halfword `0x8314F1CC` (a restriction field) is zero. |
| `0x82D06480..0x82D06494` | Setup at `0x8314EFC8`, word `+4`, is not 2. Mode 2 clears the permission at `0x82D0648C`. |
| `0x82D0649C..0x82D064D8` | The selected device `frontend+0xD0` is nonzero and the selected user's sign-in query returns nonzero. |

The combined value is tested at `0x82D064EC..0x82D064F4`. Zero selects the short
list built at `0x82D065D4`. The full list is shown at `0x82D06538` and the short
list at `0x82D06614`. Only setup mode 2 is shown to separate Game of the Week
from other games. Title source also names a special game word `0x8314F180` and a
halfword `0x8314F1D0`, but no save check reading either one was found. The
title's `gotw_standard_rules` setting is a per game latch and is not a field in
this check.

In the full list, row 1 sets action 83 at `0x82D06588` and row 2 sets action 76
at `0x82D06598`. The action table uses `action+1`. Action 83 reaches
`0x82D06898 -> 0x82D00550`, the save wrapper. Action 76 reaches
`0x82D068E8 -> 0x82D005D8`, the load wrapper. The save wrapper calls the picker
through root slot `+0xDC` and, after the picker succeeds, the writer through
slot `+0x74`. Under the default table `0x82138768` these are `0x82D83208` and
`0x82D82510`. The save wrapper has no setup mode test of its own. The load
wrapper tests the network byte at `0x82D00638..0x82D00640`.

A second mode 2 exclusion sits in the optional manual Save prompt `0x82D1D1C0`.
`0x82D1D320` compares setup mode with 2 and clears eligibility at `0x82D1D328`.
The network byte, the restriction halfword, a signed threshold, the device and
the selected user also apply. When the modal accepts row zero at `0x82D1D3A4`,
`0x82D1D3AC` calls the same save wrapper. This prompt is not an automatic save,
and a pause menu change does not need it. These are the mode checks examined,
not a full list of every alias or upstream check.

Do not enable saving by changing setup mode for the whole game, or by clearing
the network byte or the restriction halfword. Setup mode 2 also selects the
weekly result code.

### Automatic saving

Automatic saving uses a separate wrapper, `0x82D83E80`, in default table slot
`+0x70` (cell `0x821387D8`). The common writer is slot `+0x74` (cell
`0x821387DC`). The wrapper has no setup mode test in its full selected body, and
no Game of the Week exclusion was found. Four request sites call it:

| Request site | Condition | Open question |
|---|---|---|
| `0x82CC8B9C` | Incoming derived `r24` is zero, `r23` is nonzero and frontend `+0x14` is above 0 at `0x82CC8B78`. | The earlier selected user callback and the actual caller. |
| `0x82CDED18` | Frontend `+0x14` is above 0 at `0x82CDECC0` and current turn minus start turn is at least 10 at `0x82CDECDC`. | This does not show a repeating ten turn interval. |
| `0x82D1F434` | Index is nonzero, the current and previous participant tests pass and frontend `+0x14` is 1 at `0x82D1F410`. | `0x82D8AB00` makes an unresolved selected user call at virtual `+0x100`. |
| `0x82D00898` | Frontend `+0x14` is above 0 at `0x82D00874`. | The caller, and whether a quit reaches it. |

The setting code `0x82E2D6B0..0x82E2D6D0` stores a non default AutoSaveRate
value in frontend `+0x14`. The number selects a policy and is not shown to be an
interval. The wrapper needs a storage ready result at `0x82D83F24`, builds a
type 1 record, writes the device from frontend `+0xD0`, and needs a name shorter
than 42 bytes. It copies the name to record `+0x108` and calls the common writer
through slot `+0x74` at `0x82D83FA0`. A skipped save keeps the starting return
value 1 (`0x82D83EA8`), so a return of 1 does not show that a file was written.
Do not claim that Game of the Week never autosaves, and do not force the rate to
get past a check that has not been identified.

The numbered name helper `0x82CC1874..0x82CC1894` returns 100 plus the signed
remainder of its input modulo 50. The selected caller passes current turn plus
1, so a nonnegative input gives a number from 100 to 149. Full file names, paths,
slot rotation and overwrite behavior have not been observed. Native automatic
slots may share storage with an earlier game's save.

### What the save record holds

The output producer `0x82D81560` calls the header writer `0x82CC29B8` in output
mode 0 at `0x82D815E0`, calls the common body `0x82CC4040` at `0x82D81654`, then
compresses the body and writes lengths and bytes to the caller's stream. The
default input mode is 1. These are requests. Whether the bytes arrive depends on
the helper and the storage backend.

| State | Sites | Notes |
|---|---|---|
| Saved week | Header `0x82CC2B24` reads setup `+0x134`. The store at `0x82CC2B80` publishes it at header record `+0x10`. | A scalar copy. It is the week, not a map seed. |
| Current random state | Header request, plus `0x82CC54CC..0x82CC553C` for `0x82F7AD00`. | The state now, not the initial map seed. |
| Player civilizations | `0x82CC4554..0x82CC45A0`, eight words at `0x830ECD28`, only when the version is at least 13. | Not the setup civilization at `+0x13C`. |
| Current year and turn | `0x82CC421C..0x82CC42F4`, `0x8312B8E0` and `0x8312B8DC`. | Scalar copies. |
| Start turn and scenario | `0x82CC6090..0x82CC6194`, `0x8312B8D8` and `0x8312B8D4`. | The version check before these was not examined. |
| Terrain | `0x82CC498C..0x82CC49D4`, 1600 bytes at `0x8312B288`. | Logical terrain. |
| Terrain flags | `0x82CC49D4..0x82CC4A1C`, 1600 halfwords at `0x8312A608`. | Flags plane. |
| Terrain edges | `0x82CC5108..0x82CC5150`, 1600 bytes at `0x8311F690`. | Edge plane. |

Terrain identities come from [map tile semantics](../../manifests/xbox-map-tile-semantics.json)
and the calendar identity comes from [game calendar state](../../manifests/game-calendar-state.json).
A body loop over 1024 records of 14 bytes has no assigned terrain meaning.

No round trip was found for setup mode, the original map seed, the setup
civilization, the standard rules setting, custom settings, native challenge
restrictions or the weekly score caches. The game cannot save a title setting
without a title path that writes it. The body return after `0x82D81654` is a
size or logging value, so it does not show that the record is complete.

### What load restores

The load owner `0x82D86400` requests the header at `0x82D8645C` and the body at
`0x82D86674`. The next steps apply only on the reached arm where the retained `r8` is zero
(`saveLoadBoundary.load.weekAndSeed` in the
[manifest](../../manifests/game-of-the-week-local-generation.json)); another
load path is not covered. At `0x82D86854` the header's random state goes back to
`0x82F7AD00`. This is a copy, not a generator draw.

The load path reads the saved week from `sp+0xB0` at `0x82D86848`, passes seed
argument zero at `0x82D86844` and calls `0x82DADC88` at `0x82D8685C` (return
address `0x82D86860`). That writer stores the week at setup `+0x134` and works
out seed `+0x138` and civilization `+0x13C` again. It does not restore setup
mode `+4` or any host setting. The one load that was observed had mode 3, but
the loader body is not shown to run only in mode 3, and a saved Game of the Week
origin or its rules are not shown to be restored.

So a reloaded game can have the saved random state but a seed worked out from
the week, not the original custom seed. Saved player civilizations can differ
from the new setup civilization. The saved logical planes can rebuild terrain
only when those bytes actually arrive. They are not a copy of height textures or
renderer state.

At `0x82D86870` the loader calls `0x82D7F550` with whether the old setup week
differs from the saved week. It calls current root `+0x150` with `r4` zero and
that answer in `r5` (`0x82D7F5B8..0x82D7F5C8`). Under default table `0x82138768`,
cell `0x821388B8` selects `0x82D86A78`. With the low byte of `r4` zero, that
function skips its map constructor call at `0x82D86AD0`. Later helper calls,
the first reader of the terrain and any statistics or cache effects are not
resolved, so the load is not shown to avoid map generation altogether.

### Hook points for a resumed game

The weekly result code reads setup week `+0x134`, not the seed. A game that is
saved and loaded can replay result and cache steps, so a mod that allows saving
needs to keep that game out of the shared weekly result. These four places are
candidate hook sites, not validated control transfers. The meaning of each is
read from the stores around it, not from a run, and the continuation addresses
were not decoded in a separate query.

| Hook site | Continue at | What it skips |
|---|---|---|
| `0x82D7DC44` | `0x82D7DC90` | The result record stores at `0x82D7DC60..0x82D7DC88`: score, table value, outcome and year. |
| `0x82DBF138` | `0x82DBF13C` | The cached score store at result owner `+0x24`. |
| `0x82DBF14C` | `0x82DBF150` | The cached week store at `+0x28`. |
| `0x82DBE69C` | `0x82DBE7AC` | The submission, in the base and victory child paths. |

Filtering only the last submission leaves local caches unprotected. Mode 2 alone
is not enough to mark a resumed game as durable origin: the observed load had
mode 3, and nothing here shows that every loaded game does. A mod also has to restore its own origin and rules after load, before the first reader
of those values. To get the original custom seed back, it must supply that seed
to the load writer at `0x82D8685C`. A change made after load comes too late if
seed readers have already run. Cached online scores are not part of game state
and need no restoring. No leaderboard support is needed to use the native paths
that skip submission.

### Limits

Native fields, word span digests and limits are in
[`saveLoadBoundary`](../../manifests/game-of-the-week-local-generation.json#/saveLoadBoundary).
The [slot contract](save-storage.md) gives namespaced slot identity and
finalization evidence for manual saves. It does not cover custom Game of the
Week data, automatic slot behavior or result isolation for resumed games.
Profile service teardown and republication stay open under the selected user
owner lifetime, so do not invent profile keys for Game of the Week data. Values
a mod saves for a game, such as its origin, week and seed, need storage of the
mod's own.

## Exact replay and the week input

The
[week replay
boundary](../../manifests/game-of-the-week-local-generation.json#/weekReplayBoundary)
owns the native flow, source order, domains and remaining gates. Exact replay
needs the effective week as well as the seed and matching setup/content. These
static contracts do not establish completed replay equivalence.

| Address | Established fact |
|---|---|
| `0x82DADCA4` | The writer stores incoming week `r4` at setup `+0x134`. |
| `0x82D21C20` / `0x82D21C60` | The reached setup arm copies setup week into command `+0x34`. |
| `0x82D90BE0` / `0x82D90BFC` | The alternate command producer copies the same setup field into command `+0x34`. |
| `0x82D91A88..0x82D91A94` | The wrapper loads command week into `r4`, sets `r5=0`, loads current setup into `r3`, then calls the writer. |
| `0x82D21E5C..0x82D21E60` | Setup passes its week in `r4` to initializer `0x82E2A638`. |
| `0x82E2A650..0x82E2A688` | The initializer writes week to four RNG state words and clears their counters before tailing to the runtime seed wrapper. |
| `0x827F1870` | Wrapper `0x827F1858` stores the seed at returned runtime record `+0x14`, conditional on its helper and returned destination. |
| `0x82D0F124` / `0x82D0F144` | Procedural construction saves the pre-terrain main RNG state word at `sp+0x88`. |
| `0x82D0F13C` / `0x82D0F154` / `0x82D0F164` | Construction captures the map seed, clears the main counter and installs that seed for terrain generation. |
| `0x82D10FB0..0x82D10FC0` | The reached tail restores the saved state word, clears the counter and calls start selector `0x82D02C58`. |
| `0x82D02CF4..0x82D02D60` | The selector-table loop consumes main RNG state before later coordinate selection. |
| `0x82E76FEC` | Difficulty handler `0x82E76FC0` independently stores its incoming difficulty at setup `+0xF8`. |
| `0x82D22D0C..0x82D22EA4` | Player/session assignment and civilization eligibility affect setup, including AI RNG draws. |

The four initialized records are `0x8314F750`, `0x82F7AD00`, `0x82F7B458` and
`0x8314FB80`, with counters at each address plus four. The initializer's runtime
helper destination, return and state retention remain conditional. The
restoration before starts copies only the state word and resets the counter; it
does not restore a complete RNG record.

When the earlier week initialization and intervening execution retain their
relationship, this saved pre-terrain state is week-dependent. An identical
temporary map seed can therefore give matching terrain while starts differ. It
does not prove that the saved state equals the raw week or explain a specific
displacement without paired state/coordinate evidence.

Exact replay also requires matching difficulty, player/session assignment,
civilization eligibility, active scenario start selectors `0x830E8FD0+0x42` and
indexed halfwords beginning `+0x44`, counts, dimensions, RNG parameters,
content, generator version and gameplay overrides. Named-map success follows a
different terrain route. This is not an exhaustive census of indirect inputs.

Week zero is a sentinel in `0x82D21D28..0x82D21E50`, with random-week and
week-one fallback arms. It is excluded from ordinary explicit-week replay
without a separately gated bypass. Automatic selection retains its accepted
zero-extended `1..0x7FFFFFFF` sufficient week domain and helper/count guards.

The field is uint32; an explicit nonzero seed bypasses automatic selection
locally for larger words, but does not certify their other consumers.

## Week limits

The [limit boundary](../../manifests/game-of-the-week-local-generation.json#/weekLimitBoundary)
separates title policy, native storage, automatic selection and calendar input.
The selected ReRevved custom-week setting accepts `1..2147483647`. A larger
string is rejected; invalid launch input falls back to the native week. This
setting limit does not establish a retail final week.

The native writer stores all 32 week bits without a maximum-week branch.
For stable count 277, the expanded-range helper compares the low word of the
ordinal, and the caller stores the low word of its result. The selector's
sign-extended multiplication therefore does not alone break lookup above
`0x7FFFFFFF`. This bounded result does not certify all high-week consumers.

The stored maximum is `4294967295`. Supplying `4294967296` without validation
truncates to zero, which encounters the existing setup sentinel and its
conditional random/week-one fallbacks. This is not a designed restart at week
one. The clock recomputes the week for each request rather than incrementing a
persistent counter. Its unsigned day-count division can return at most
`613566756`; calendar and clock representation constrain chronological input
before that mathematical ceiling.

The first future calendar-model week error is Sunday `2704-03-06`: native week
`36430` skips Gregorian week `36429`. Native week `36472` then repeats across
the 2704/2705 boundary. Cumulative leap counting uses division by four while
month lengths use Gregorian century rules. The selected Windows SDK's positive
signed FILETIME range ends in September 30828, normalizing to week `1503927`;
beyond that representation, conversion can overflow rather than provide a
defined future date. These are static/source-model boundaries, with no observed
future launch, graceful termination or restart. The canonical boundary retains
the exact dates, source identities and helper/clock qualifications.

## Independent civilization selection

The [civilization boundary](../../manifests/game-of-the-week-local-generation.json#/civilizationOverrideBoundary)
identifies a conditional override that retains the week and map-seed inputs.
Immediately before `0x82DADD18`, replace the derived civilization in `r10`;
the native store publishes it to current setup `r31+0x13C`. Validate an ordinary
civilization against effective definitions and eligibility. Supported ordinary
IDs are `0..15`; the Barbarian ID is separate.

Apply the latched policy for the accepted early mode-2 writer, before
`0x82E76EF4` loads the civilization and `0x82E76F14` publishes it to the player
map. Reapply at the later new-game writer, which recomputes this field. Preserve
the existing launch identity, helper/return/retention guards and ordinary/load
paths; a late setup-field change alone does not establish player selection.

The native AI assignment skips a classified human. In mode 2 its duplicate
scan starts at player slot one, so it can admit an AI matching the human at
slot zero. Civilization ID zero is not specially excluded. Changing that
policy is separate from selecting the human civilization.

Custom civilization selection needs the same outcome/cache/submission isolation
as other custom GotW inputs, including when it matches the automatic choice.
This is an insertion contract, not a shipped setting or observed launch.
Starting units/bonuses, both writer outputs, player assignment and result
isolation still require paired runtime acceptance; retaining week/seed does not
prove identical complete games.

## Ordered MapList and replay lookup

The pinned MapList in source order has a count, length, digest and local
extraction method in the
[ordered
record](../../manifests/game-of-the-week-local-generation.json#/weekReplayBoundary/orderedMapList).
The archive and selected member identities are:

| Artifact | SHA-256 |
|---|---|
| `Pregame.FPK` | `14E50B0382542B345F29B129175CB1B1B9A4538547E8B5567CAA5A864531A2DE` |
| `ccglobaldefines.xml` | `C68C7BEE458CD4C5B6A3773AFD2EA07D8CC60E7A606DB5D1B82F3626D44445E3` |

The member begins at archive `0x2D34`; MapList is at XML line 228/archive
`0x60AC`. There are 277 unique entries. Effective replacement configuration
requires revalidation; membership alone does not establish order.

The expanded CSV is 1,012 ASCII bytes, without spaces or a trailing newline. Its
SHA-256 is `F29FBDA96BD88836EBDD9C639FD9DE9522610A1CAB2C8CD486163EE33453FA48`.
Extract and verify the list in source order locally before applying these
formulas.

Under the accepted selector gates, `seed = MapList[week % 277]` with zero-based
indexing. For current native week `Wc`, seed `s` and its index `j`:

```text
j = index_of(MapList, s)
if s is absent or Wc < j:
    no nonnegative matching past week exists
else:
    Wprime = j + 277 * floor((Wc - j) / 277)
```

Use wide host arithmetic. `Wprime` is the latest matching week because it is
congruent to `j`, does not exceed `Wc`, and adding 277 exceeds `Wc`. A seed
recurs every 277 weeks; it does not identify one unique historical game. A
result of zero still hits the native sentinel. Seed 276 has index 253; with
`Wc=1085`, the arithmetic gives `Wprime=1084`.

This example does not establish runtime equivalence or a value from the current
clock.

## Title implementer contract

Week and seed controls are independent:

| Explicit controls | Effective week | Seed argument at both writer calls |
|---|---|---|
| Neither | Native week | Zero: native automatic selection |
| Week only | Chosen week | Zero: automatic selection for that week |
| Seed only | Native week | Chosen seed |
| Both | Chosen week | Chosen seed |

Choosing only a seed must not silently select a past week. Validate any manual
seed against the set supported by content when retaining numbered textures.
Latch the original native week separately from effective week, seed policy,
both custom flags and the accepted launch/setup identity before `0x82E76ED4` .

Before both `0x82E76ED4` and `0x82D91A94`, substitute zero-extended effective
week in `r4` when selected, and the same latched seed policy in `r5`. Let the
native writer publish all three setup fields and calculate civilization before
player-slot publication. Both hook adapters must expose `r4` and `r5` as
writable; expose `r3` for setup validation.

Preserve `r3=current setup` and all other guest state. An entry hook may
identify the origins by LR `0x82E76ED8` and `0x82D91A98`.

The late hook requires readable setup `+4 == 2` and the matching accepted
launch. Its native week came from the incoming command `+0x34` before `r3` was
replaced; do not reload it from current setup `r3+0x34`. Early substitution
means the command normally carries effective week, so do not require equality
with the original native week.

Leave mode-1 games, mode-3 loads and `0x82D8685C` on their native paths. With
neither control enabled, preserve both native calls unchanged. Allow native
week-based RNG initialization to run; no extra host RNG write is required by
this ordinary contract for a nonzero week.

Either custom control requires a latched marker identifying the game's custom
origin to isolate its outcome, score cache, week cache and base/victory-child
submissions. Retain native completion and failure cleanup. At
`0x82DBE6CC..0x82DBE6D4`, an unequal older setup week can admit submission when
the score is not greater; it is not an isolation mechanism.

Final submission filtering alone does not prove local cache protection. Preserve
existing save/profile policy.

Accept exact replay only with paired native/replay captures under identical
setup/content:

- Both writer outputs
- Four initial RNG records
- Pre-terrain saved/restored state
- Starts
- AI civilizations
- Logical terrain/resource/hut state

Retain default, seed-only, week-only, both controls and mode 1/mode 3
noninterference checks before claiming replay equivalence.
