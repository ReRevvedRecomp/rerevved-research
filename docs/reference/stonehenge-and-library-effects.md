# Stonehenge and Library effects

This page covers what the native code does for Stonehenge and for the Library,
where those results are stored and credited, and why replacing either effect
takes more than one edit. It is written for modders who want to change a
Building or Wonder bonus, such as a flat Gold or Culture amount.

Everything here is a static reading of the supported image. No city update,
credit or Wonder completion was observed while the game ran. The stored
descriptions say Stonehenge gives a Temple effectiveness adjustment of 50
percent and the Library gives a city science multiplier of 2. Those texts name
the intent. The code below is what actually runs.

## What the code does, with examples

### Stonehenge changes the Temple contribution

Stonehenge is item 203, normalized Wonder index 3. Inside `CityUpdate`
(`0x82D13978`) the Temple builds one running value. Call it the contribution:
it is kept in register `r18` and stack `+0x78`, then written to city `+0x48`.

For a city with population `P` (the signed byte at city `+0x03`):

- With a Cathedral, the Cathedral takes precedence. It adds `2 * P` and the
  Temple path is skipped.
- With no Cathedral and a Temple, the Temple adds `P`. If the Stonehenge check
  returns nonzero, it adds `trunc(P / 2)` more, rounding toward zero.
- With neither building, neither path adds anything.
- When the state word `r23` equals 3 at `0x82D14F24`, this whole
  building group is skipped.

Example: a city of population 6 with a Temple and no Cathedral adds 6. When
Stonehenge is active for that city's owner it adds 6 + 3 = 9. A city of
population 5 adds 5, or 5 + 2 = 7 when Stonehenge is active.

The Stonehenge check is the indexed Wonder query `0x82CEF4E8`, called at
`0x82D14F88` with index 3. It does not ask whether this city holds Stonehenge.
For index 3 it accepts the claim owner, or any player whose halfword at
`0x830E9070` matches the owner's. So one claimed Stonehenge can raise the Temple
value in every city that passes this check, not only in the city that built it.
The names of the neutral state word and of the halfword array are not known.

A second native consumer reads the same index. In the AI evaluation
(`0x82CB44E0`), the call at `0x82CB59D0` passes index 3, and a nonzero result
adds the signed half of `r31` at `0x82CB59DC..0x82CB59E4`. What `r31` means in
the final AI decision is not established.

### The Library doubles one value and leaves Gold alone

The Library is item 105, normalized Building index 5. In `CityUpdate` a Library
doubles a different running value, `r20`, in the same function:

- With a University (mask `0x1000`), `r20` is multiplied by 4, and a nonzero
  city `+0x24` mask `0x2000` adds 5. A University takes precedence.
- With a Library (mask `0x20`) and no University, `r20` is multiplied by 2, and
  the same city mask adds 2.
- A state word obtained through stack `+0xA4` that equals 6 skips this branch.
  The comparison is not a civilization test.

Example: with `r20` equal to 3 and only a Library, the branch gives 6, or 8 when
the `0x2000` mask is set.

The doubled value feeds Science. It goes to city `+0x44`, to owner row `+0x08`
and to the stored research progress. The Gold the city earns comes from a
separate value (stack `+0x7C`), stored to city `+0x46` and owner row `+0x0C`.
So a Library as written doubles Science, not Gold. A Library Gold bonus is new
behavior and must leave the `+0x44` Science path as it is. A bonus tied to one
civilization has to test the owner's civilization (Chinese is index 6 in
`0x830ECD28`) and the Library bit separately. The comparison with 6 at
`0x82D1468C` reads `0x830ED3D8`, not that array, so it is not a civilization
test.

## Where the results go

| Value | City field | Owner row at `0x830EE388 + owner*0x28` | Credited to |
|---|---|---|---|
| Library doubled value `r20` | `+0x44`, stored at `0x82D14EA0` | `+0x08`, mode 0 only | Science progress, see below |
| Gold value (stack `+0x7C`) | `+0x46`, stored at `0x82D14ED0` | `+0x0C`, mode 0 only | Reserve `0x830ED544 + owner*4` at `0x82D15610` |
| Contribution `r18` | `+0x48`, stored at `0x82D152F0` | `+0x10`, mode 0 only | Accumulator `0x830ED484 + owner*4` at `0x82D15614` |

The city stores run before the mode checks. The owner row additions run only in
mode 0. A later change to a city field after the function returns does not
change the stored value or the earlier owner total.

The state credits at the end of `CityUpdate`:

- Gold. At `0x82D15610` the reserve word receives the old reserve plus stack
  `+0x7C`. The block `0x82D155E4..0x82D15610` has no loop and no skip, so each
  pass through it stores once. The owner used is the entry snapshot saved at
  stack `+0x84`.
- The accumulator. At `0x82D15614` the word at `0x830ED484 + owner*4` receives
  `r18`. When the UEA 23 lookup at `0x82D15618` is active, `0x82D15634` adds
  the signed half of `r18`. The accepted classification calls this Great
  Person generation. It is not a per city Culture bank, and it is indexed by
  owner, not by city.
- Science. When the selected word at `0x830EDD48 + owner*4` is above 0,
  `0x82D155B8` stores old selected progress plus the zero column plus `r20` and
  `0x82D155BC` clears the zero column. Otherwise `0x82D155E0` adds `r20` to the
  zero column. Progress sits at `0x830EDD68` with a row stride of `48 * 4`.
  The cached Calendar path writes city `+0x44` to the same table at
  `0x82D1FAB4`.

Other changes sit nearby and are separate: reserve interest at `0x82D1F4A4`
and Gold from technology completion excess at `0x82D20C14`. A Library does not
add to either.

Native overrides run between the cache stores and the credits:

- When city word `+0x24` has mask `0x8`, or the UEA 42 lookup is not active and
  the state word `0x830ED3D8 + owner*4` is zero, `0x82D15350..0x82D1536C` clears
  city `+0x40`, `+0x42`, `+0x44` and `+0x46` together with the matching stored
  values. City `+0x48` and `r18` are left alone.
- For the excluded owner (`0x82F700B0`), `0x82D153C0..0x82D153EC` zeroes the
  Gold, `r18` and `r20` values. The credit adds zero while city `+0x46` keeps
  its old value.
- A separate clear of `r20` at `0x82D15524` affects Science only.

The reserve credit adds all 32 bits of stack `+0x7C`, but city `+0x46` holds
only its low 16 bits.

Border growth reads city `+0x48` too, at `0x82CBE854` and `0x82CBE8D0`, and adds
derived terms into indexed halfwords. Matching only a player total is therefore
not enough for a rule that applies to one city.

## Modes and the 24 call sites

`CityUpdate` takes a mode in `r4`. The accepted scan found 24 direct calls and
every one sets the mode locally:

| Mode | Sites | Effect |
|---|---|---|
| 1 | 8 | Branches at `0x82D13A50` to `0x82D159A4`. Skips the yield block and the credits. Production can still complete. |
| -1 | 13 | Refreshes city values and exits at `0x82D15380`. Skips the credits. |
| 0 | 3, all in Calendar, each only when its conditions hold | Can reach the credits. |

The three mode 0 sites are `0x82D1FC14`, `0x82D1FD20` and `0x82D1FDC8` in
`CalendarTurnAdvance`. The first can be skipped by the cached branch. The
second needs difficulty 3 (Emperor) and the third difficulty 4 (Deity), plus
several more conditions. The difficulty word is `0x82FFE7C8`, the shared word
described in [AI settings and behavior](ai-options.md). With either difficulty held steady a city can reach two
of the three calls in one pass, so these are not three guaranteed credits and
not exactly one. A bonus that fires on every `CityUpdate` entry would fire at 21
sites that do not credit anything. The Gold reserve aggregate at `0x82CF9F38`
calls in mode -1 and reads city `+0x46` as a total, which is a displayed value
and not a treasury write.

## Wonder claims and completion

### The claim table

Wonder claims live in a table at `0x830E5148` with 33 slots of 8 bytes: owner
at `+0x00`, city at `+0x04`. Slot `index * 8` holds normalized Wonder `index`
(item `200 + index`). Stonehenge is slot 3, words `0x830E5160` and
`0x830E5164`. An unclaimed slot holds -1 in both words. The reset at
`0x82D060C4..0x82D060D4` fills all 0x108 bytes with 0xFF. One serializer
path at `0x82CC4F14..0x82CC4FF0` resets all 33 slots and then copies paired
words for indices 0 through 20, which include Stonehenge.

### The completion edge

A new Stonehenge claim happens in `CityUpdate` when the city has enough invested
production, the slot is unclaimed (owner is -1) and the eligibility check
`0x82CF3608` returns nonzero. After the production writes, `0x82D16340` calls
the claim helper `0x82D16BA0` with `r3` the normalized Wonder, `r4` the city,
`r5` 1 and `r6` 0. The helper stores the live city owner at `0x82D16C08` and the
city at `0x82D16C10`.

The edge after that call is `0x82D16344`. There `r27` equals 3 for Stonehenge
and `r23` holds the city. The entry owner is in `r21`, but validate the newly
stored claim instead of assuming the owner cannot change. This is the one place
that marks a new claim:

- Loading a save, a reset, a transfer and the Calendar owner synchronization
  also write claim words, at `0x82D060D4`, `0x82CC4F14..0x82CC4FF0`,
  `0x82D1B01C`, `0x82D1C8F4`, `0x82D1F57C`, `0x82D1F5D4` and `0x82D1F62C`. None
  of them runs `0x82D16344`.
- Mode 1 can complete production, so mode is not a filter. Once an inner call
  claims the slot, a later call cannot claim it again while the owner word stays
  claimed.
- A consistent saved Stonehenge is claimed and is skipped. A restored slot of -1
  with item 203 and enough production can complete again.
- Hooking every entry to `0x82D16BA0`, or watching for an owner change, would
  catch the wrong events.

### The Religion grant

The selected completion path requests no technology acquisition. A mod that
wants Stonehenge to give Religion has a static contract to follow. It uses the
acquisition function `0x82D09208` with the arguments owner, 19 (Religion),
city, 5 (the Wonder reward source) and 1 (the normal state phase). The native
Oxford branch calls the same function at `0x82D17194` with the same shape. Before
the call, check that `0x82CEF6A8(19, owner)` returns zero, which is the full
native availability test. The raw Religion ownership word `0x830EDC94` is not
enough on its own.

The call records the technology at `0x830EDD28 + 4 * owner`, sets the owner bit
in `0x830EDC48 + 4 * technology` at `0x82D0937C` and records reason 5 at
`0x830ED588 + 4 * (48 * owner + technology)`. It has no duplicate guard of its
own and repeats its effects if called twice. Native presentation stays as it
is: with flag 1 the selected popup branches are not entered, so no separate
Religion message is promised. The real display was not observed.
The ownership is saved through `0x82CC4718` and `0x82CC4760`, and disabling a
rule never removes a Religion already granted.

The call must run in the interrupted guest context, with all registers, stack
and continuation preserved. The static facts do not prove it is safe from a new
hook. Whether the excluded player can reach the grant, malformed or rewritten claims, the human and
AI interface, network replication and save, load and transfer controls remain
open.

### Reading Wonder index 3

The raw scan found 64 direct calls to the indexed query. Six are in `CityUpdate`
with literal indices 4, 13, 16, 3, 12 and 9. Another 45 have literal arguments
in their callers, and the last 13 are mapped by their callers: 11 pass zero after another check
returns zero, and two pass indices 1 and 19. Two sites select index 3: the Temple call and the AI call above.
A search for the two Stonehenge slot words as a split constant found nothing,
which excludes only that form. Other readers through computed indices or
aliases are not excluded.

## The yield ranking table

The ranking table sits at `0x830E9200`. It holds ranks by player and column, filled
by the producer `0x82CB2E48`. Eight rows fit its saved span.

| Part | Value |
|---|---|
| Cell address | `0x830E9200 + row * 32 + column * 2`, one signed halfword per cell |
| Columns written by ranking | 0 through 11 |
| Column 12 (`+24`) | A count written separately: it counts zero words, other than the excluded player's, in a row of `0x830ED2D8` |
| Rank | Zero based. The player chosen first for a column gets 0. Ties keep the earlier player. Values of -1 or less are never chosen and can stay unwritten. |
| Excluded player row | When the word at `0x82F700B0` is not -1, the producer stores the player count word `0x82F700AC` into a cell of that row at `0x82CB3704..0x82CB3710` |
| Save span | 128 halfwords, 256 bytes, `0x830E9200..0x830E9300`, equal to 8 rows of 16 halfwords |

Two direct callers refresh the table outside Calendar: `0x82D0C900` and
`0x82D2582C`. Calendar reads cells at `0x82D1FBE0`, `0x82D1FCD8`, `0x82D1FCDC`
and `0x82D1FD6C`, indexed by the saved incoming player. The ranking feeds the
conditions that choose whether the later Calendar calls run.

To tell whether a rank is fresh, track the actual per cell stores. A producer
entry only starts an attempt, and a normal return does not mean every cell was
written. The table's column names, its full set of writers, and the meaning of
the underlying values are not established.

## Why a replacement is not one hook

A flat bonus that replaces a native effect has to keep several values in step:

1. Suppress only the native Stonehenge terms. Skipping the Temple term in the
   one city that gets the new bonus leaves the native effect in every other city
   that passes the index 3 check. Forcing the check false, or clearing the claim
   slot, changes other Wonder queries and claim counts. See
   [stonehenge-native-effect-suppression.json](../../manifests/stonehenge-native-effect-suppression.json).
2. Pick the bonus city from the claim city state, not from the index 3 check.
3. Compose the bonus at two places for Gold. One edit before `0x82D1537C` keeps
   the city cache and owner total right. A second edit at the store operand of
   `0x82D15610` makes the credit, and the cache amount must not also flow into
   stack `+0x7C` or it counts twice. See
   [city-yield-credit-hook-candidates.json](../../manifests/city-yield-credit-hook-candidates.json).
4. Choose the Culture destination first. The accumulator takes `r18` and half of
   it, so changing `r18` by `N` changes the result by `N` plus the change in
   `trunc(r18 / 2)`. Changing only the store operand gives exactly `N`. See
   [city-culture-credit-destination.json](../../manifests/city-culture-credit-destination.json).
5. Place the Religion grant at `0x82D16344` only, with the availability check
   first.

A fixed amount also depends on conditions that are not settled:

- The number of credits per city turn is not fixed, because of the Calendar
  calls above ([city-credit-calendar-cadence.json](../../manifests/city-credit-calendar-cadence.json)).
- The cached Calendar path adds the cached city `+0x48` value to the incoming
  player's row at `0x82D1FAD8` and skips the first call, so adding the amount
  again there counts it twice.
- Mode -1 calls refresh city values without crediting. Mode 1 calls do not
  refresh yields at all: they bypass the yield block at `0x82D13A50` and only
  let production complete, so a replacement cannot rely on them to update
  cached yields.

## Open questions

- Whether the AI term at `0x82CB59DC` belongs in a replacement.
- The complete set of Culture consumers and the intended Culture destination.
- Reads of Wonder claims through computed or aliased indices.
- Indirect callers of `CityUpdate` and the real credit count per turn.
- The meaning of `0x830ED3D8`, the second city byte at `+0x01`, the halfword at
  `0x8314F1D4` and the excluded player word `0x82F700B0`.
- Display and border consumers of city `+0x44`, `+0x46` and `+0x48`.

## Evidence

Manifests: [stonehenge.json](../../manifests/stonehenge.json),
[library-city-yield-writers.json](../../manifests/library-city-yield-writers.json),
[library-gold-credit-transaction.json](../../manifests/library-gold-credit-transaction.json),
[city-yield-state-credit.json](../../manifests/city-yield-state-credit.json),
[city-culture-border-yield-input.json](../../manifests/city-culture-border-yield-input.json),
[city-yield-credit-call.json](../../manifests/city-yield-credit-call.json),
[city-yield-turn-scheduling-inputs.json](../../manifests/city-yield-turn-scheduling-inputs.json),
[city-yield-scheduling-producer.json](../../manifests/city-yield-scheduling-producer.json),
[city-yield-ranking-table.json](../../manifests/city-yield-ranking-table.json),
[wonder-claim-slot-state.json](../../manifests/wonder-claim-slot-state.json),
[wonder-claim-table-consumer.json](../../manifests/wonder-claim-table-consumer.json),
[science-completion.json](../../manifests/science-completion.json), and the
four new records for the suppression, credit hook, Culture destination and
Calendar cadence findings linked above. Capacity limits for adding a Building
or Wonder are in [building-wonder-storage-limits.md](building-wonder-storage-limits.md).
