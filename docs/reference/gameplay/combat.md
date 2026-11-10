# Combat

A battle takes the attacker's attack strength and the defender's defense
strength, turns each into a weight for every combat figure, and then draws
random numbers to decide which side loses a figure. It repeats until one side
has no figures left. Loss protection can throw a result away and draw again
when it would wipe out a protected side. The result is written to the two
units and shown by the battle presentation.

This page covers how the resolver `CombatResolve` (at `0x82CD9970`) carries
the strengths into a random selection, how the random state is saved and
reloaded, how the battle screen numbers are made and what the presentation
code does with the result. The rules for which side is protected, the proof
for Catapults and the survival of the winner are in
[Combat loss protection](combat-loss-protection.md). How a unit's strength is
built from rank, terrain, Fortify and other modifiers is in
[Combat strength](combat-strength.md).

Every path below needs the stated inputs, normal returns under the native
ABI, and no memory writes that overwrite the frame or live state. The numbers
are supplied inputs under those conditions. They are not observed battles and
do not show that such a battle can occur. Whether natural combat reaches these
paths, and whether displayed strengths match the internal ones, is not proved.
Evidence is in [combat-outcome.json](../../../manifests/combat-outcome.json),
[combat-rng-save-reload.json](../../../manifests/combat-rng-save-reload.json) and
[combat-resolution-lifecycle.json](../../../manifests/combat-resolution-lifecycle.json).

## How a battle is decided

| Step | What happens | Where |
|---|---|---|
| 1. Core stats | The attacker's attack and the defender's defense are read separately. | `0x82CDA214` and `0x82CDA234` |
| 2. Weighted strengths | Each core stat is multiplied by its composed scalar. The product keeps its low 32 bits: `WA = low32(A*X)` and `WD = low32(D*Y)`. | Frame words 156 and 160, reloaded at `0x82CDBDE8` and `0x82CDBDF4` |
| 3. Casualty reduction | Wounds lower the strength used for the ratio test. This does not change the weighted frame words. | `0x82CDBE58` and `0x82CDBF38` |
| 4. Protection | Two local flags mark a side that may not be wiped out. The ratio test uses the weighted, wound reduced words from step 3, before any late weight. | `0x82CDC138`, [Combat loss protection](combat-loss-protection.md) |
| 5. Late weights | A definition byte can triple or add half to the weighted word, and an Army divides by 3. These are the per figure weights for the draw, not the protection ratio. | Frame words, then masks |
| 6. Masks | Each side gets a mask with one bit per figure. | `0x82CDC640` |
| 7. Random selection | A comparison draw and an ordinal draw remove one figure from one side. This repeats. | `0x82CDC6C0` to `0x82CDC748` |
| 8. Result | The final masks go to the two units and the generator state and counter are published. | `0x82CDC880..0x82CDC8AC`, `0x82CDD690..0x82CDD72C` |
| 9. Presentation | The selection array goes to the presenter and its pump. | `0x82D7F838`, `0x82E2A570` |

The resolver has three modes. Mode 0 resolves the battle. Mode 1 returns the
evaluation scalar `trunc(100*rawAttack/(rawAttack + rawDefense + 1))` before
any selection, from the raw stats. Mode 2 builds the paired battle screen
records and returns the same formula on the wound reduced strengths. Neither
scalar is a whole battle win chance. A separate local flag is a different input
from the mode.

### A battle in numbers

Take a Catapult attacking a Catapult after turn 20 (UnitType 16, base attack 4
and defense 1), with both on Grassland at rank 1, no wounds and no other
modifier. The strengths pass through the steps like this:

| Quantity | Attacker | Defender |
|---|---:|---:|
| Base attack and defense | 4 | 1 |
| Completed scalar | 100 | 100 |
| Weighted strength (`WA`, `WD`), no wounds | 400 | 100 |
| Late weight, tripled for the Catapult definition | 1200 | 300 |
| Figure mask | 1 | 1 |

The ratio 4:1 is the same at every stage. With one figure each, a comparison
draw using the weights 1200 and 300 decides which side loses its figure. Loss
protection can reject a result that removes the protected attacker.

A second example shows the generator steps. Take supplied core words 10 and 25
with composed scalars 10 and 10, both units Catapults. Then `WA = 100` and
`WD = 250`, the late frame words are 300 and 750, and both masks are 1. With
generator state 3 and the file modulus and scale, the first stepped state is
3173050 and the truncated comparison word is 0, which is below 300. The next
state, 471647893, gives ordinal 0 and a matching bit. The first stores write
value 1 and ordinal 0 at frame offsets 848 and 920 after two generator steps,
with counter word `low32(C + 2)`.

Starting from state 0 instead, the first state is 2531011 and the comparison
word is again 0. Ordinals 1 and 7, from states 505908858 and 3539360597, fail
the single bit mask test. The retry keeps the earlier selection value and the
store pointer. State 159719620 then gives ordinal 0 and the same first stores
after four generator steps, with counter word `low32(C + 4)`. These are
supplied inputs, not stats from a battle a player can reach.

## Loss protection

A side that is protected cannot be wiped out by one unlucky draw. The resolver
rejects the result and selects again, up to a retry limit of 1000. Through turn
20 any side with at least 2 times the opponent's strength is protected. After
that an attacker needs more than 3 times the defender (more than 2 times
against Barbarians), and a human defender needs more than 3 times the attacker
(more than 2 times in a city or against Barbarians). The rules, the proof that
a protected Catapult always reaches a win and the effect on the units are in
[Combat loss protection](combat-loss-protection.md).

## Stat and selection flow

### Core stats and the guarded route

The pair reads the attacker's attack at `0x82CDA214` and the defender's defense
at `0x82CDA234` and keeps them apart. The guarded route excludes the literal
25 replacement, the tripling arm and the local flag replacement, and keeps
those register roles until weighting. The composed scalars multiply the two
words and keep each product's low 32 bits.

The route needs both participants to be UnitType 16, zero additive inputs,
zero ownership query returns, positive weighted words and the stated byte,
flag and player checks. It also needs normal native ABI returns and external
memory writes that do not overlap the protected frame or the live inputs.

The preparation call takes a short helper bypass and returns zero because of a
comparison against an existing local float word. That word's initialization is
not proved. These conditions give a dataflow, not observed values and not a
path natural combat is known to reach. Other resolver arms can replace, triple,
halve, add to or zero the stat words.

### Catapult weights and masks

UnitType 16, Catapult, has definition byte `+0x48` equal to 1 in the supported
image. Let `WA = low32(A*X)` and `WD = low32(D*Y)` be the kept weighted words.
One path needs `0 < WA`, `2*WA <= WD < 2^29`, four `IsHumanPlayer` returns with
low byte zero, the tested current word equal to 13 and the stated zero
participant byte checks.

These conditions leave the local flags `r20 = 0` and `r25 = 1`, which bypasses
the optional float adjustment. The definition byte then triples both words into
frame words `low32(3*WA)` and `low32(3*WD)`. The same zero participant bytes
bypass division and give single bit masks.

The mask block replaces `r23`, the weighted attack word, with the defender
mask. The attack value stays in frame word 156. Definition bit 0 and zero
participant `+0x52` bits give masks `r24 = r23 = 1`. Clear definition bits 1
and 2 skip further additions. The generator operands survive this block, and
both nonzero masks reach the pointer setup at `0x82CDC640`.

Frame reads at `0x82CDC674` and `0x82CDC678` recover the tripled weighted words.
This path keeps the earlier values rather than supplying new stats at
selection. The ABI, nonoverlap and preparation float conditions still apply.

### Definition reductions

The branches at `0x82CDBE58` and `0x82CDBF38` skip the reduction when the
respective definition byte has none of bits 0, 1 and 2 set. Definition byte 1
takes both fallthroughs. Each counts the same three bits of its participant
halfword `+0x52`, multiplies the count by the current weighted word, and
divides the low word of the product, signed, by the definition's bit count.

The quotient is subtracted into a separate register, `r29` or `r30`. The
weighted words in `r23` and `r15` and frame offsets 156 and 160 survive these
blocks. A zero participant halfword gives quotient zero. The core pair reaches
these frame loads only under the guarded route above. The first example in
[A battle in numbers](#a-battle-in-numbers) shows the onward path to the first
selected stack stores, under its added conditions.

### Comparison and ordinal selection

The selection block steps a state word with a low word multiply and add, and
an optional unsigned reduction by the modulus. It then uses scaled arithmetic
in a signed comparison. A valid current pointer in frame word 268 has a zero
pointee at `0x82CDBFC8`. Under the stated nonoverlap conditions both reach the
override reload at `0x82CDC6C0` and the dereference at `0x82CDC6C4`. A zero
test takes `0x82CDC6CC` to the ordinal block and keeps the comparison result.
Initialization of the pointer and the global's identity are not proved.

Each ordinal attempt steps the same generator state and counter. It computes
`double(state)*Q`, multiplies that rounded double by 9.0 and truncates the
result to a signed 64 bit value. The low word gives the shift ordinal. The
shifted bit picks the defender mask when the comparison result is 1, or the
attacker mask when it is 0. Native `slw` uses the low six bits of the ordinal
and gives zero when bit 5 is set. With masks 1 and 1 a matching ordinal has its
low six bits zero, but the full ordinal need not be zero.

A bit that does not match retries at `0x82CDC6D4`, keeping the comparison
result, the masks, the flags and the store pointer. A matching bit reaches
`0x82CDC744` and `0x82CDC748`. Entry through `0x82CDC640` forms
`r7 = r1 + 848`, so the first four byte writes go to stack offsets 848 and 920,
and then the pointer advances by four. Every conversion needs finite
intermediate values and a defined signed 64 bit result. A finite successful
attempt is a condition. Termination for any generator input is not proved.

The guarded route links the earlier stat pair to these first stores. It keeps
`r25 = 1`, so its later retry and control flow depend on the cases in the next
sections. A separate local exit example keeps its own `r25 = 0` condition.

## Random state and saving and reloading

The resolver uses the main generator record at `0x82F7AD00`: state at `+0`,
draw counter at `+4`, modulus at `+8` and double scale at `+0x10`. These are
inputs to a deterministic calculation. The counter records how many draws were
consumed. It does not enter the comparison of the result.

Two frame `+268` pointer builders form `0x830E4554`. If their result survives
to the samples, this word supplies the late override: zero keeps the comparison,
and nonzero forces selection value 1. The override follows a comparison draw
that was already consumed, so forcing 1 does not refund it. Its live value, the
path from producer to sample, its name and its gameplay meaning are not
recovered. The override is also part of
[Combat loss protection](combat-loss-protection.md#the-override-word).

### The save header

The default mode 0 output path of `0x82CC29B8` includes the current main state
word. Mode 1 input puts its helper dependent value in local record `+0xC`. On
a later guarded load path, `0x82D86854` writes that field back to `0x82F7AD00`
(see [the save header record](../../../manifests/combat-rng-save-reload.json)).

The header carries the state word, not a snapshot of the whole generator. Its
separate `0x8314F750` field is not the main draw counter. No direct header
field carries the counter, the modulus or the scale. Other serializers,
aliases and later initialization are outside that negative result.

The stream must actually deliver the saved bytes, and later calls must keep the
record and the restored state. A normal return and a nonzero header size do not
show delivery. If the state flag is omitted, the load record keeps its
initialized zero for the restore. If a read delivers no bytes, a temporary can
keep its live value. The manifest records the exact mode, flag, endian and
lifetime premises.

### What reloading repeats

Restoring the same consumed state, compatible parameters and the same ordered
combat inputs and draws can reproduce the same local calculation. This concerns
the current pseudorandom state, not only the initial map seed. Helper effects
that run earlier, overrides, retries and other state changes in between all
matter. Repeated replays with the same inputs are dependent trials. Equal
displayed strengths alone show neither a 50 percent chance to win the whole
battle nor a bias.

The [combat event records](../../../manifests/achievement-event-boundaries.json)
separately tie the final weights, a mode 0 decision and publication and a local
decisive defense result to their participants and lifetimes. No complete live
path from a save to a battle replay, and no universal winner formula, follows
from this section.

## Displayed strengths

The battle panel number path is separate from the unit type preview formatter.
Resolver mode 2 passes raw and wound reduced strengths into paired records
through `0x82D6A6A0`. The two unit number requests at `0x82DFAC74` and
`0x82DFB1E8` read record `+12`, the reduced value, and pass it to `0x82DF9EF0`.
`0x82DFAEA0` recovers the second record, and fresh local player samples pick
the orientation. Matching that value to the later mode 0 ratio needs the same
participants, wounds, modifiers and weighted words. The both zero replacement at
`0x82CDB7C0..0x82CDB7DC` and later zeroing arms stop the two from always being
equal. Both displayed totals also differ from the later per figure weights
that were normalized by definition and Army.

For a nonnegative strength stored in hundredths, `0x82DF9EF0` requests at most
two decimal places below 10, one below 100 and none from 100 upward, and it
drops zero suffixes. It omits low digits and does not round to nearest. Format
pointers are `0x82125768`, `0x82125770` and `0x821230EC`. Supplied internal
strengths 2000 and 1001 request the text 20 and 10 while 2000 is below
2*1001. The rule tests the exact internal integers. This shows a mismatch in
the precision of the request. Whether such a pair can occur in a legal early
battle, what the formatter writes and whether it reaches visible text are not
proved. The first unresolved output edge is `0x82D38DD0` and whether its output
object survives to the text request at `0x82C7C2E8`. Neither evaluation scalar
is a proved whole battle win chance.

Mode 2 numbers equal the fresh mode 0 early ratio words only for the same
participants, types, wounds and weighted words, with no helper or overlap
change, no both zero replacement and no later zeroing of the frame. If the
early reduced words are both zero, the replacement can later set them to 100
and 100.

## Stored contents and presentation

### The first rejection resets the array

The first protected rejection starts with the retry counter at 0, whatever the
attack weight. It increments to 1 and resets the array through 18 stores of 8
bytes over `[848, 992)`, replacing the first pair with `0xFFFFFFFF` words.
Raising `WA` from 100 to 1000 does not avoid this: `0x82CDC444` has replaced the
earlier strength in `r29` with the new counter.

Reasoning about the later suffix alone can supply a real array and counter
that are past the threshold, a consistent nonhuman mask and frame word 148
equal to zero, which bypass presentation. That does not show a path from an
initialized resolver to that checkpoint, that the first pair survives, or what
the final published generator state is. A compatible final selection,
presentation and persistent result link is not proved.

### The presentation flag and participant normalization

Frame word 148 starts at zero. Equality of participant and local player,
countdown bits, a later human classification or table bits can set it to one.
Later byte and classifier tests can clear it. A zero preparation keeps an
existing one on the nonzero field arm. It does not always clear it.

The equality uses the current defender frame word `+1596`, which is not always
the entry value in `r6`. `0x82CFE450` receives that stored argument as output.
One finite matched route writes player zero before the core reload at
`0x82CDA224`, so an entry `r6 = -1` does not prove a later null player match.
A valid normalized defender is unequal at `0x82CDB9BC`. A no output result of
-1 shows no valid player, and a defender unit of -1 exits early. Neither gives
continuing stats or an array.

A countdown of 1 decrements to zero and then tests bits. A local player of -1
gives an `slw` shift of 63 from its low six bits, so the result is zero even
with `+24` equal to `0xFFFF`, and the one store is skipped.

### The registry child

The [resolver record](../../../manifests/playable-game-state-requirements.json)
covers the initial null input and a registry child that exists only when
created. Its `+0x100` returns `+0x20`. A successful 108 byte allocation sets the
`+0xC` low word to `0xFFFFFFFF`. Neither step adds a compatible nonzero `+148`
input. Child `+0x88` can exchange `+0xC` between searched ordinals. Its first
probe comes before a retry limit of 8. A stable count, nonnegative ordinals that
do not overflow, and the no-aliasing, ABI and nonoverlap checks keep the
initialized -1.

A separate ordinal producer and three callers tie the loads and stores
together. The insertion checks link two getter returns to the constructed
results. Current key and child equality, the internal `+0x4` lookup and
`+0x148`, the actual scalars and whether they stay valid are open. The wrapper
needs a result identity and `+0x190`. Four setup bodies contain no `+0x88`
call. The prior word record needs exact key and value links, or a new scoped
caller, plus compatible consumption in order before it can select the nonzero
stat or array arms.

The caller key and scalar record limits the direct entry and sparse installer
idea without an actual key and receiver. Two readers pass their own `+0x34` to a
four byte input helper. The shared receiver, its source and a zero `+0x8`
remain unknown. The arrays on the zero route and the independent presenter
depend on those answers.

### The independent presenter input

The installed vtable identifies `0x82D7F838`. A manager `+0x18` of zero skips
consumption. A nonzero value keeps `r8 = P` in `r24` across two `0x82D7DEE8`
calls and then passes `r7 = P` to `0x82D66B20`. Native save thunks keep the
incoming arguments. Finite text loops and the stated frame, save and write
exclusion checks keep the pointer and the original 144 bytes, which supplies
source `P`, destination `0x83024E58` and length 144 to the transfer. The
resolver case above does not reach this chain.

The transfer record shows an aligned 144 byte copy and a local return. With
valid kept input, backing and save storage, the path copies 5 and then 13
blocks of 8 bytes to `[0x83024E58, 0x83024EE8)`. Source and destination can be
separate or identical. A destructive partial overlap is excluded. The incoming
buffer is therefore separate from the first resolver array above.

Tracing the buffer's consumer stops at the current child and table `+0x100`
call at `0x82D66C18`. No explicit read or forward of the destination comes
before it, but the caller's stores relative to the record still need overlap
to be excluded. The actual target and its effects, and the writer from the
destination to the participant `+0x52` fields, are not identified.

### The buffer reader and the participant field writes

A reader in `0x82D66178` has a local contract at `0x82D664C8`. With buffer base
`0x83024E58`, record base `0x82F79FC0` and index `q = low30(r29) < 18`, it
reads one four byte word from each 72 byte plane. The second word goes to
`0x82F79FE0`. A zero first word selects `r24`, any other value selects `r23`,
for `0x82F79FE4`. Neither field has a name. The high two index bits alias. The
ten consecutive reader instructions end at `0x82D664F0`, which was not queried.
Entry to the reader, whether it is actually called, and the order and byte
identity of the earlier copy are not shown. The reader does not resolve the
current `0x82D66C18` call and does not name a persistent winner. See
`conditionalPairedBufferReaderBoundary` in the manifest for the samples, stores
and a 16 word receipt.

A separate path starts at `0x82D66778`. Matching current intermediate cells and
a set bit in the high halfword allow cell resets and an OR into one working
mask. A further status check controls the two halfword stores at `0x82D6683C`
and `0x82D66844`. With a kept unit table base and valid player and unit
bindings, their destinations are the two records' `+0x52` fields. High mask bits
are dropped, and aliases can change the result. The order and byte generation of
the earlier reader, the actual participants and later persistence are not
linked to these stores, so they do not identify a battle winner.

Separate local producers supply the unit table base, two current candidate
reloads, the candidate and index choice, a signed definition byte mask and the
native `slw` bit. The zero initializer and skip loop paths limit the bit index
to 0 through 8 before their first helper. A shift or loop tail reached another
way has no such limit. The mask can grow into three shifted copies, with
sign extension bits kept for a negative source byte. The current definition
table identity and the state kept between bands are open. These producers do
not link to the earlier reader.

### Helper paths

Native `0x82D66690` calls `0x82D5CC98`, a leaf with no stores and no nested
calls. Its current 29 cell branch table selects eight local returns, each from
40 to 100. The path writes a local halfword at `r29 + 18` using
`trunc(250*return/denominator)`, with denominator 95 for index zero and 100
otherwise. That write is separate from the later `+0x52` stores. When the
sampled global `0x82FFE7C4` has bit `0x4` set, the optional floating update is
skipped and control reaches `0x82D66744`, which calls `0x82D5E568`.

One path of `0x82D5E568` makes no child call. It samples the indexed unit's
signed type byte, its definition byte through base `0x82F700D8`, and the unit
`+60` pointer Q. An odd definition byte selects zero and an even one selects
one. A null Q returns 1. Otherwise a signed count from Q's `+120` and `+124`
words returns 1 when it is at most that selector. A null `+120` gives count
zero. The signed type byte lookup comes before the null Q branch and still
needs valid backing. These reads do not identify the earlier frame `+88`
definition pointer.

The path writes only the helper's saved LR, saved `r31` and the stack backchain.
When the current inputs are kept and those writes do not overlap later source
storage, the signed matrix comparison allows `0x82D66778` exactly when the
sample is at least 1. Zero and negative samples take the less than path. Stack
aliases can change the sample even though registers are restored normally. The
cell, mask and status checks of the consumer still apply.

If the count check selects a descriptor, a halfword that is not the sentinel
first needs `0x82D5E608` to call `0x82D5CFD0`. Halfword -1 skips that child and
reaches `0x82D5E614`, which calls `0x82E59F98` with the descriptor and -1. The
returns and effects of those children are open. No supplied child result, no
same generation link from reader to consumer, no participant persistence and no
save delivery follows.

### Presentation, pump and completion

The [combat lifecycle record](../../../manifests/combat-resolution-lifecycle.json)
observed participant changes during presentation. It does not establish damage,
experience, death, capture or distribution, or the same behavior for humans, AI,
cities, naval or air units. The window and example details are in the
[outcome manifest](../../../manifests/combat-outcome.json). Unit stat roles are in
[unit definitions](unit-definitions.md#combat-stat-role-boundary).

## Limits and open questions

- Natural combat reachability of these paths is not proved, and neither is the
  match between displayed and internal strengths.
- The override word at `0x830E4554` has no recovered name or live value.
- The save header carries the state word only. Delivery of the saved bytes,
  and what consumes them after a load, are open.
- The registry child, the paired buffer reader and the participant field
  writes are not linked to the resolver array or to a battle winner.
- Presentation, its pump and the reader are not shown to finish. A winner
  result for the unit is in [Combat loss protection](combat-loss-protection.md).
