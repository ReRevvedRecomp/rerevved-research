# Ordinary combat boundary

One guarded static route in `CombatResolve` retains the accepted core stat
pair through weighting into frame words 156 and 160, then reloads those words
at `0x82CDBDE8` and `0x82CDBDF4`. A guarded asymmetric continuation carries
them through tripling and mask construction into the actual selection reads
and first signed comparison, then through override and ordinal selection into
the first stack stores. Later control distinguishes a retry that overwrites
those contents from a no-reset subcase that retains the array but bypasses
presentation. A separate conditional presenter path retains an incoming
array to transfer-call input. Natural reachability, an ordinary combat
outcome and persistent participant changes are unproved.

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
One continuation requires `0 < WA`, `2*WA <= WD < 2^29`, four
`IsHumanPlayer` returns with low byte zero, the current tested word equal to 13, and the stated zero
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
joins the earlier stat pair to these first stores. The continuing route
retains `r25=1`; its later retry and control flow require the distinctions
below. The independent local exit example retains its separate `r25=0`
condition.

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

## Stored contents and presentation

The `WA=100` example cannot retain its first pair. Value 1 removes the
single defender mask bit, and the retained `r25=1` arm increments `r29`
to 101. The signed test against 1000 falls through to another array
initialization. Eighteen eight-byte writes fill stack offsets `[848,992)`
with `0xFF`, replacing both first words with `0xFFFFFFFF`. With this value-1 first store, the same first
retry occurs for `WA<=998`; larger permitted inputs require a separate
control check.

A new conditional upstream example keeps core words 10 and 25 but uses
composed scalars 100 and 100, deriving `WA=1000`, `WD=2500` and selection
frame words 3000 and 7500. The same generator inputs give decision word
7, less than 3000, and ordinal 0. After the first value 1/ordinal 0 stores,
`r29=1001` bypasses the retry. The selected 144-byte array survives, with
`0xFF` in its other initialized bytes. The native exit publishes third
state 2756632324 and counter `low32(C+3)`.

This no-reset subcase additionally requires a nonzero human-player mask
with both participant bits clear. The repeated `IsHumanPlayer` results
are consistently zero. The retained frame-148-zero guard at `0x82CDD618`
excludes the presentation-side arm at `0x82CDD734`. Both later participant
byte arms converge on the same continuation, even if native stores change
those bytes. The route reaches the resolver end block without the argument
at `0x82CDD8BC` or call at `0x82CDD930`, despite retaining resolver mode
zero. Normal ABI returns and native/external nonalias effects remain
conditions. A compatible first-store route into presentation remains unproved.

The field at frame offset 148 is produced upstream as a zero/one Boolean.
It is initialized to zero and can become one through participant/local-player
equality, guarded countdown bit tests, later human classification or a separate
table-bit arm. Later global-byte and classifier tests can clear it. A zero
preparation return preserves an existing one through the nonzero field arm;
it does not universally clear the field.

The equality producer compares the current defender word at frame +1596,
which can differ from original incoming `r6`. The resolver initially stores
that argument, then passes the same frame word as an output to
`0x82CFE450`. One finite matching-entry route writes player index zero
there before the defender core call. The core call reloads that normalized
player at `0x82CDA224`. Original `r6=-1` therefore does not by itself
establish a later equality with a null local-player return of -1.

For that valid normalized defender, the null-return equality is unequal at
`0x82CDB9BC`. A no-output helper route preserves -1, but establishes no
valid normalized player. A current defender unit of -1 separately selects
an early return. These cases cannot supply the missing continuing stat and
array route.

The countdown producer provides another precise boundary. A current countdown
of 1 decrements to zero and enters the participant bit tests. With the same
null local-player return -1, native `slw` produces zero because the shift's
low six bits are 63. The first intersection is zero even with participant
halfword `+24` equal to `0xFFFF`, so the branch bypasses the one store.
A different local-player result requires the unresolved nonnull indirect
call through vtable `+0x100` in this helper. Other nonzero producers remain
possible, but a compatible stat and selected-array continuation requires a
separately established producer. The prior zero-route arrays and independent
presenter input chain remain conditional results.

Independently, the accepted installed vtable conditionally identifies
presentation target `0x82D7F838`. A zero manager `+0x18` word bypasses its
consumer call. The nonzero arm retains incoming `r8=P` in nonvolatile
`r24` across both calls to `0x82D7DEE8`, then supplies `r7=P` to
`0x82D66B20`. The native compiler prologue save thunks preserve incoming argument registers.
Normal ABI returns and nonalias memory effects are required.
The consumer's finite text loops retain that pointer and, under explicit
frame, save-area and write-disjointness conditions, its original 144 bytes.
Its transfer call input has source `P`, destination `0x83024E58` and length
144. This independent input chain is not reached by the resolver subcase above.

The transfer prefix stops before `0x827F8688`. Complete publication and the
persistent participant `+0x52` writer remain unresolved.

The native presentation, pump and completion must be preserved. The accepted
[combat lifecycle](../../manifests/combat-resolution-lifecycle.json) observed
participant state changing during presentation. No damage, experience,
death, capture, randomness distribution, or human/AI, city, naval or air
parity is inferred from these local blocks.

See [the bounded evidence](../../manifests/ordinary-combat-outcome-boundary.json)
for exact read windows, guarded joins, local example assumptions, stores and
unclosed edges, and [unit definitions](unit-definitions.md#combat-stat-role-boundary)
for the accepted stat-role inputs.
