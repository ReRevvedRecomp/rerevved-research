# Ordinary combat boundary

One guarded static route in `CombatResolve` retains the accepted core stat
pair through weighting into frame words 156 and 160, then reloads those words
at `0x82CDBDE8` and `0x82CDBDF4`. A guarded asymmetric continuation carries
them through tripling and mask construction into the actual selection reads
and first signed comparison. Separate local blocks establish conditional
stack writes and exact generator-word stores. Natural reachability, an ordinary
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
comparison. On the synthetic single-bit case, a successful ordinal-zero
selection clears the defender-corresponding local bit. Two four-byte stores
write selection value 1 and ordinal 0. Entry through `0x82CDC640` forms
`r7 = r1+848`, so the first writes use stack offsets 848 and 920. The pointer
survives the comparison and ordinal retry, then advances by four bytes for
another entry. The same local checkpoint and exit assumptions support exact
generator state/counter stores. The guarded continuation joins the earlier
combat-stat pair to the first comparison. Ordinal and override conditions
remain separate. Its continuing edge through the override and ordinal retry
into the selected stores is unjoined; the independent ordinal and exit example
does not establish that edge. Later publication of the stack contents is unproved.

For a conditional asymmetric example, core words 10 and 25 with composed
scalars 10 and 10 give `WA=100` and `WD=250`. The continuation derives frame
words 300 and 750 and masks 1 and 1. With current generator state 3 and the
stated modulus and double scale, the first stepped state is 3173050 and the
truncated comparison word is zero, less than 300. These are supplied guarded
inputs, not observed live stats or a naturally reachable combat.

The branches at `0x82CDBE58` and `0x82CDBF38` bypass reduction when the
respective definition byte has no set bits among bits 0, 1 and 2. Definition
byte 1 enters both fallthroughs. Each counts the same three bits of its
participant halfword `+0x52`, multiplies that count by the current weighted
word, and divides the low product word signed by the definition count. It
subtracts the quotient into a separate register, `r29` or `r30`. The current
weighted words in `r23`/`r15` and frame offsets 156/160 survive these blocks.
A zero participant halfword gives quotient zero. Core-pair retention into
these frame loads is established only under the guarded route above. The
asymmetric continuation establishes onward retention into the first selection
comparison under its additional conditions.

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
