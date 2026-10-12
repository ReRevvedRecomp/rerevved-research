# Ordinary combat boundary

One guarded static route in `CombatResolve` retains the accepted core stat
pair through weighting into frame words 156 and 160, then reloads those words
at `0x82CDBDE8` and `0x82CDBDF4`. A guarded asymmetric continuation carries
them through tripling and mask construction into the actual selection reads
and first signed comparison, then through override and ordinal selection into
the first stack stores. Separate local blocks establish exact generator-word
stores under independent exit conditions. Natural reachability, an ordinary
combat outcome and persistent participant changes are unproved.

## Guarded stat and selection flow

The accepted pair obtains attacker attack at `0x82CDA214` and defender defense
at `0x82CDA234`, retaining them separately. The guarded route excludes the
literal-25 replacement, tripling and local-flag replacement, and preserves
those register roles until weighting. Current composed scalars multiply the
two stat words, keeping each product's low 32 bits. Resolver mode and a
separate local flag remain distinct inputs.

This route requires both participants to have UnitType 16, zero additive
inputs, zero ownership-query returns, positive weighted words and the stated
byte, flag and player guards. It also requires normal native ABI returns and
external memory effects that do not alias the protected frame or live inputs.
The preparation call takes a narrow helper bypass and returns zero under a
comparison against an existing local float word. That word's initialization
is unproved. These explicit conditions establish conditional dataflow, not
observed ordinary values or a naturally reachable path. Other resolver arms
can replace, triple, halve, add to or zero the stat words.

UnitType 16, Catapult, has definition byte `+0x48` equal to 1 in the supported
image. Let `WA=low32(A*X)` and `WD=low32(D*Y)` be the retained weighted words.
One continuation requires `0 < WA`, `2*WA <= WD < 2^29`, four predicate returns
with low byte zero, the current tested word equal to 13, and the stated zero
participant byte guards. These conditions leave local flags `r20=0` and
`r25=1`, bypassing the optional float adjustment. The definition byte selects
tripling into frame words `low32(3*WA)` and `low32(3*WD)`. The same zero
participant bytes bypass division and select single-bit masks.

The mask block changes `r23` from the weighted attack word to the defender
mask. The attack value survives in frame word 156. Definition bit 0 and zero
participant `+0x52` bits produce masks `r24=r23=1`; clear definition bits 1
and 2 skip further additions. The generator operands survive this block, and
both nonzero masks reach the pointer setup at `0x82CDC640`. Actual frame reads
at `0x82CDC674` and `0x82CDC678` recover the tripled weighted words. This
continuation retains the earlier values rather than supplying new stat values
at selection. ABI, nonalias and preparation-float conditions remain required.

The selection block advances a state word by a low-word multiply-add and
optional unsigned modulus reduction, then uses scaled arithmetic in a signed
comparison. A valid current pointer in frame word 268 has a zero pointee at
`0x82CDBFC8`. Under the stated nonalias conditions, both survive into the
override reload at `0x82CDC6C0` and dereference at `0x82CDC6C4`. The zero test
takes `0x82CDC6CC` to the ordinal block and preserves the comparison result.
Pointer initialization and a global identity
are unproved.

Each ordinal attempt advances the same generator state and counter. It
computes `double(state)*Q`, then multiplies that rounded double by 9.0 and
truncates to a signed 64-bit value. The low word supplies the shift ordinal.
The shifted bit selects the defender mask when the comparison result is 1,
or the attacker mask when it is zero. Native `slw` uses the ordinal's low six
bits and produces zero when bit 5 is set. With masks 1 and 1, a matching
ordinal has low six bits zero; the full ordinal need not always be zero.

A rejected bit retries at `0x82CDC6D4`, retaining the comparison result,
masks, flags and store pointer. A matching bit reaches `0x82CDC744` and
`0x82CDC748`. Entry through `0x82CDC640` forms `r7 = r1+848`, so these first
four-byte writes use stack offsets 848 and 920, then the pointer advances
by four. Every conversion requires finite intermediates and a defined
signed 64-bit result. A finite successful attempt is an explicit condition;
termination for arbitrary generator inputs is unproved. The guarded route
joins the earlier stat pair to these first stores. Later publication of the
stack contents is unproved. The independent local exit and generator-store
example has `r25=0`; the continuing stat route retains `r25=1` and does not
establish that later exit.

For a conditional asymmetric example, core words 10 and 25 with composed
scalars 10 and 10 give `WA=100` and `WD=250`. The continuation derives frame
words 300 and 750 and masks 1 and 1. With current generator state 3 and the
stated modulus and double scale, the first stepped state is 3173050 and the
truncated comparison word is zero, less than 300. The next state is 471647893,
which gives ordinal zero and a matching bit. The first stores write value 1
and ordinal 0 at frame offsets 848 and 920 after two generator steps, with
counter word `low32(C+2)`. These are supplied guarded inputs, not observed
live stats or a naturally reachable combat.

A separate conditional example changes only the current initial state to
zero. Its first state is 2531011 and comparison word is again zero. Ordinals
1 and 7 from states 505908858 and 3539360597 fail the single-bit mask test.
The retry preserves the earlier selection value and pointer. State 159719620
then gives ordinal zero and the same first stores after four generator steps,
with counter word `low32(C+4)`.

The branches at `0x82CDBE58` and `0x82CDBF38` bypass reduction when the
respective definition byte has no set bits among bits 0, 1 and 2. Definition
byte 1 enters both fallthroughs. Each counts the same three bits of its
participant halfword `+0x52`, multiplies that count by the current weighted
word, and divides the low product word signed by the definition count. It
subtracts the quotient into a separate register, `r29` or `r30`. The current
weighted words in `r23`/`r15` and frame offsets 156/160 survive these blocks.
A zero participant halfword gives quotient zero. Core-pair retention into
these frame loads is established only under the guarded route above. The
asymmetric continuation establishes onward retention into the first selected
stack stores under its additional conditions.

## Unclosed continuations

The accepted installed vtable conditionally identifies presentation target
`0x82D7F838`. Its incoming argument copy and later call arguments are separate
endpoint facts. A zero manager `+0x18` word bypasses the call; the nonzero arm
crosses an unread retention interval. No incoming selection array is proved
to reach the consumer.

A separate consumer checkpoint calls `0x827F8550` with destination
`0x83024E58`, its current source pointer and length 144. The transfer prefix
stops before `0x827F8688`. Complete publication and the persistent participant
`+0x52` writer remain unresolved.

The native presentation, pump and completion must be preserved. The accepted
[combat lifecycle](../../manifests/combat-resolution-lifecycle.json) observed
participant state changing during presentation. No damage, experience,
death, capture, randomness distribution, or human/AI, city, naval or air
parity is inferred from these local blocks.

See [the bounded evidence](../../manifests/ordinary-combat-outcome-boundary.json)
for exact read windows, guarded joins, local example assumptions, stores and
unclosed edges, and [unit definitions](unit-definitions.md#combat-stat-role-boundary)
for the accepted stat-role inputs.
