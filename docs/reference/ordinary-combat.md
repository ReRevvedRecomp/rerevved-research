# Ordinary combat boundary

A guarded `CombatResolve` route carries core stats through frame words 156/160
(reloads `0x82CDBDE8`/`0x82CDBDF4`), tripling, masks, comparison and ordinal
selection into first stack stores. Later control either overwrites the array or
retains it while bypassing presentation. A separate presenter chain reaches
transfer input; natural reachability, ordinary outcome and persistent
participant changes remain unproved.

Evidence terms: every continuation below requires its stated inputs, normal
native ABI returns and nonalias effects protecting frame/live state. Numerical
examples are supplied guarded inputs, not observed stats or reachable-combat
proof.

## Random state and save/reload

The selected resolver uses the main generator record at `0x82F7AD00`: state
at `+0`, draw counter at `+4`, modulus at `+8` and double scale at `+0x10`.
These are sampled inputs to a deterministic calculation. The counter records
draw consumption; it does not enter the selected result comparison.

Two selected frame `+268` pointer builders form `0x830E4554`. If their result
survives to the accepted samples, this separate word supplies the late override:
zero retains the comparison, while nonzero forces selection value1. That
override follows a consumed comparison draw. Its actual live value and the
producer-to-sample retention remain conditions; its name or gameplay policy
is not recovered from this pointer identity.

The [save-header boundary](../../manifests/combat-rng-save-reload-boundary.json)
binds a conditional persistence mechanism. The default mode0 output path in
`0x82CC29B8` includes the current main-state word. Mode1 input places its
helper-dependent value in local record `+0xC`. On a later guarded load path,
`0x82D86854` writes that field back to `0x82F7AD00`.

This header directly transfers the state word rather than a complete generator
snapshot. Its separate `0x8314F750` field is not the main draw counter. No
direct header field carries the counter, modulus or scale; other serializers,
aliases and later initialization remain outside that negative.

The stream must actually deliver the saved bytes, and intervening calls must
retain the record and restored state. Normal return and a nonzero header size
do not certify delivery. An omitted state flag can leave the load record's
initialized zero for restoration; a no-byte read can retain a temporary's live
value. The manifest retains the exact mode, flag, endian and lifetime premises.

Restoring the same consumed state, compatible parameters and the same ordered
combat inputs/draws can reproduce the same local calculation. This concerns
current pseudorandom state, rather than only the initial map seed. Earlier
helper effects, overrides, retries and other intervening state changes matter.
Repeated retained-input replays are dependent trials. Equal displayed strengths
alone establish neither a 50 percent whole-battle win chance nor bias.

The later [combat event boundaries](../../manifests/achievement-event-boundaries.json)
separately bind final operative weights, a selected mode0 decision/publication
and a conditional local decisive-defensive result. They preserve their actual
participant, lifetime and causal-lineage requirements. No complete live
save-to-battle replay or universal winner formula follows from this section.

## Guarded stat and selection flow

The accepted pair obtains attacker attack at `0x82CDA214` and defender defense
at `0x82CDA234`, retaining them separately. The guarded route excludes the
literal-25 replacement, tripling and local-flag replacement, and preserves those
register roles until weighting. Current composed scalars multiply the two stat
words, keeping each product's low 32 bits.

Resolver mode and a separate local flag remain distinct inputs.

This route requires both participants to have UnitType 16, zero additive inputs,
zero ownership-query returns, positive weighted words and the stated byte, flag
and player guards. It also requires normal native ABI returns and external
memory effects that do not alias the protected frame or live inputs.

The preparation call takes a narrow helper bypass and returns zero under a
comparison against an existing local float word. That word's initialization is
unproved. These explicit conditions establish conditional dataflow, not observed
ordinary values or a naturally reachable path. Other resolver arms can replace,
triple, halve, add to or zero the stat words.

UnitType 16, Catapult, has definition byte `+0x48` equal to 1 in the supported
image. Let `WA=low32(A*X)` and `WD=low32(D*Y)` be the retained weighted words.
One continuation requires `0 < WA`, `2*WA <= WD < 2^29`, four `IsHumanPlayer`
returns with low byte zero, the current tested word equal to 13, and the stated
zero participant byte guards.

These conditions leave local flags `r20=0` and `r25=1`, bypassing the optional
float adjustment. The definition byte selects tripling into frame words
`low32(3*WA)` and `low32(3*WD)`. The same zero participant bytes bypass division
and select single-bit masks.

The mask block changes `r23` from the weighted attack word to the defender mask.
The attack value survives in frame word 156. Definition bit 0 and zero
participant `+0x52` bits produce masks `r24=r23=1`; clear definition bits 1 and
2 skip further additions. The generator operands survive this block, and both
nonzero masks reach the pointer setup at `0x82CDC640`.

Actual frame reads at `0x82CDC674` and `0x82CDC678` recover the tripled weighted
words. This continuation retains the earlier values rather than supplying new
stat values at selection. ABI, nonalias and preparation-float conditions remain
required.

The selection block advances a state word by a low-word multiply-add and
optional unsigned modulus reduction, then uses scaled arithmetic in a signed
comparison. A valid current pointer in frame word 268 has a zero pointee at
`0x82CDBFC8`. Under the stated nonalias conditions, both survive into the
override reload at `0x82CDC6C0` and dereference at `0x82CDC6C4`.

The zero test takes `0x82CDC6CC` to the ordinal block and preserves the
comparison result. Pointer initialization and a global identity are unproved.

Each ordinal attempt advances the same generator state and counter. It computes
`double(state)*Q`, then multiplies that rounded double by 9.0 and truncates to a
signed 64-bit value. The low word supplies the shift ordinal. The shifted bit
selects the defender mask when the comparison result is 1, or the attacker mask
when it is zero.

Native `slw` uses the ordinal's low six bits and produces zero when bit 5 is
set. With masks 1 and 1, a matching ordinal has low six bits zero; the full
ordinal need not always be zero.

A rejected bit retries at `0x82CDC6D4`, retaining the comparison result, masks,
flags and store pointer. A matching bit reaches `0x82CDC744` and `0x82CDC748`.
Entry through `0x82CDC640` forms `r7 = r1+848`, so these first four-byte writes
use stack offsets 848 and 920, then the pointer advances by four. Every
conversion requires finite intermediates and a defined signed 64-bit result.

A finite successful attempt is an explicit condition; termination for arbitrary
generator inputs is unproved. The guarded route joins the earlier stat pair to
these first stores. The continuing route retains `r25=1`; its later retry and
control flow require the distinctions below. The independent local exit example
retains its separate `r25=0` condition.

For a conditional asymmetric example, core words 10 and 25 with composed scalars
10 and 10 give `WA=100` and `WD=250`. The continuation derives frame words 300
and 750 and masks 1 and 1. With current generator state 3 and the stated modulus
and double scale, the first stepped state is 3173050 and the truncated
comparison word is zero, less than 300.

The next state is 471647893, which gives ordinal zero and a matching bit. The
first stores write value 1 and ordinal 0 at frame offsets 848 and 920 after two
generator steps, with counter word `low32(C+2)`. These are supplied guarded
inputs, not observed live stats or a naturally reachable combat.

A separate conditional example changes only the current initial state to zero.
Its first state is 2531011 and comparison word is again zero. Ordinals 1 and 7
from states 505908858 and 3539360597 fail the single-bit mask test. The retry
preserves the earlier selection value and pointer.

State 159719620 then gives ordinal zero and the same first stores after four
generator steps, with counter word `low32(C+4)`.

The branches at `0x82CDBE58` and `0x82CDBF38` bypass reduction when the
respective definition byte has no set bits among bits 0, 1 and 2. Definition
byte 1 enters both fallthroughs. Each counts the same three bits of its
participant halfword `+0x52`, multiplies that count by the current weighted
word, and divides the low product word signed by the definition count.

It subtracts the quotient into a separate register, `r29` or `r30`. The current
weighted words in `r23`/`r15` and frame offsets 156/160 survive these blocks. A
zero participant halfword gives quotient zero. Core-pair retention into these
frame loads is established only under the guarded route above.

The asymmetric continuation establishes onward retention into the first selected
stack stores under its additional conditions.

## Stored contents and presentation

`WA=100` loses its first pair: value 1 removes defender bit; `r25=1` increments
`r29` to 101, whose signed <1000 test reinitializes the array. Eighteen
eight-byte writes fill `[848,992)` with `0xFF`, replacing both words by
`0xFFFFFFFF`. The same retry applies for `WA<=998`; larger inputs need a separate
control-flow proof.

Core 10/25 with scalars 100/100 gives `WA=1000`/`WD=2500`, frame 3000/7500.
Same RNG gives decision 7<3000, ordinal 0; after value 1/ordinal 0, `r29=1001`
bypasses reset. The array's 144 bytes survive, with the other bytes still
`0xFF`; the exit publishes the third state 2756632324 and `low32(C+3)`.

This requires nonzero human mask with both participant bits clear, consistently
zero `IsHumanPlayer`, and frame 148 zero at `0x82CDD618`, excluding `0x82CDD734`
presentation. Both participant-byte arms converge despite possible stores;
resolver ends without argument `0x82CDD8BC` or call `0x82CDD930`, even in mode
zero. A compatible first-store/presentation route remains unproved.

### Presentation gate and participant normalization

Frame 148 starts zero; participant/local-player equality, countdown bits, later
human classification or table bits can set one; later byte/classifier tests can
clear it. Zero preparation preserves an existing one on the nonzero-field arm,
not universally clearing it.

Equality uses current defender frame +1596, not necessarily entry `r6`.
`0x82CFE450` receives that stored argument as output; one finite matched route
writes player zero before core reload `0x82CDA224`. Entry `r6=-1` therefore
proves no later null-player equality. Valid normalized defender is unequal at
`0x82CDB9BC`; no-output -1 proves no valid player, and defender unit -1 exits
early. Neither supplies continuing stats/array.

Countdown 1 decrements to zero, then tests bits. Local-player -1 gives `slw`
low-six shift 63 -> zero, even with `+24` = `0xFFFF`, bypassing the one store.

The [resolver boundary](../../manifests/playable-game-state-gates.json) binds
initial null input and conditional registry child. Its `+0x100` returns `+0x20`;
successful 108-byte allocation initializes `+0xC` low word `0xFFFFFFFF`. Neither
adds compatible nonzero `+148` inputs. Child `+0x88` conditionally exchanges
`+0xC` between searched ordinals; initial probe precedes retry bound 8. Stable
count, nonnegative nonoverflowing ordinals and ownership/ABI/nonalias guards
retain initialized -1.

Separate ordinal producer/three callers bind loads/stores; insertion guards join
two getter returns to constructed results. Current key/child equality, internal
`+0x4` lookup/`+0x148`, actual scalars and retention remain open. Wrapper needs
result identity/`+0x190`; four setup bodies contain no `+0x88` invocation.
[Prior-word boundary](../../manifests/playable-game-state-gates.json) requires
exact key/value joins or a new scoped caller, plus ordered compatible
consumption before selecting nonzero stat/array arms.

[Caller-key/scalar boundary](../../manifests/playable-game-state-gates.json)
bounds direct ingress/sparse installer hypothesis without actual key/receiver.
Two readers pass own `+0x34` to four-byte input helper; shared receiver, source
and `+0x8` zero remain unknown. Zero-route arrays and independent presenter
remain conditional.

### Independent presenter input

Retained installed vtable identifies `0x82D7F838`. Manager `+0x18` zero bypasses
consumption; nonzero retains `r8=P` in `r24` across two `0x82D7DEE8` calls, then
passes `r7=P` to `0x82D66B20`. Native save thunks preserve incoming arguments.
Finite text loops and explicit frame/save/ write-exclusion guards retain pointer
and original 144 bytes, supplying source `P`, destination `0x83024E58`, length
144 to transfer. The resolver subcase above does not reach this chain.

The separate `selectionTransferContinuationBoundary` closes the aligned
144-byte copy and local return. With valid retained input, backing and save
storage, the selected path copies five then thirteen 8-byte chunks to
`[0x83024E58,0x83024EE8)`. Source and destination may be disjoint or identical;
destructive partial overlap is excluded. This leaves the incoming buffer
independent of the first resolver array above.

Immediate consumer tracing stops at the current child/table `+0x100` dispatch
at `0x82D66C18`. No explicit destination read or forwarding precedes that stop,
but the caller's record-relative stores still require alias exclusion. Actual
target/effects and destination-to-participant `+0x52` writer remain unbound.

An independently selected reader in `0x82D66178` has a conditional local
contract at `0x82D664C8`. With retained buffer base `0x83024E58`, record base
`0x82F79FC0` and index q=`low30(r29)<18`, it reads one four-byte word from
each 72-byte plane. The second word goes to `0x82F79FE0`; a zero first word
selects `r24`, otherwise `r23`, for `0x82F79FE4`. Both fields remain unlabelled.
The high two index bits alias. The ten consecutive reader instructions end at
unqueried `0x82D664F0`; entry-to-reader retention, actual invocation and earlier
copy-to-reader order/byte identity are not established. This reader does not
resolve the current `0x82D66C18` dispatch or identify a persistent winner. See
`conditionalPairedBufferReaderBoundary` in the bounded evidence for the exact
samples, stores, guards and 16-word native receipt.

The separate `conditionalParticipantFieldRequestBoundary` starts at
`0x82D66778`. Matching current intermediate cells and a set bit in the high
halfword admit cell resets and an OR into one working mask. A further status gate
controls the two halfword stores at `0x82D6683C`/`0x82D66844`. With retained
unit-table base and valid player/unit bindings, their destinations are the
two records' `+0x52` fields. High mask bits are discarded; aliases can change
the result. The earlier reader's order/byte generation, actual participant
identities and later persistence remain unjoined, so these stores identify no
complete battle winner.

`conditionalParticipantProvenanceBoundary` supplies separate local producers:
the unit-table base, two current candidate reloads, candidate/index selection,
a signed definition-byte mask and native `slw` bit. The selected zero-initializer
and skip-loop paths bound the bit index to 0..8 before their first helper;
an independently reached shift or loop tail has no such bound. The mask can
expand into three shifted copies, with sign-extension bits retained for a
negative source byte. Current definition-table identity, inter-band retention
and the unqueried `0x82D66690` helper-to-consumer continuation remain open;
these producers do not join the earlier reader.

Preserve presentation/pump/completion:
[combat lifecycle](../../manifests/combat-resolution-lifecycle.json) observed
participant changes during presentation. No damage/experience/death/
capture/distribution or human/AI/city/naval/air parity follows. See
[bounded evidence](../../manifests/ordinary-combat-outcome-boundary.json) for
windows/guards/examples and
[stat roles](unit-definitions.md#combat-stat-role-boundary).
