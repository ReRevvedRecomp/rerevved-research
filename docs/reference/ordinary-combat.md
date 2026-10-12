# Ordinary combat boundary

One guarded static route in `CombatResolve` retains the accepted core stat
pair through weighting into frame words 156 and 160, then reloads those words
at `0x82CDBDE8` and `0x82CDBDF4`. Separate local blocks establish conditional
selection arithmetic, local stack writes and exact generator-word stores.
Continuity onward into selection remains unjoined. Natural reachability, an
ordinary combat outcome and persistent participant changes are unproved.

## Independent local blocks

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
image. Local mask construction and selection examples assume valid frame and
table bindings, zero participant `+0x52` values, zero byte guards, and supplied
weighted register/frame values. These are synthetic checkpoint inputs, not
observed or validated ordinary combat values.

The selection block advances a state word by a low-word multiply-add and
optional unsigned modulus reduction, then uses scaled arithmetic in a signed
comparison. On the synthetic single-bit case, a successful ordinal-zero
selection clears the defender-corresponding local bit. Two four-byte stores
write selection value 1 and ordinal 0. Entry through `0x82CDC640` forms
`r7 = r1+848`, so the first writes use stack offsets 848 and 920. The pointer
survives the comparison and ordinal retry, then advances by four bytes for
another entry. The same local checkpoint and exit assumptions support exact
generator state/counter stores. They do not join the checkpoint to the earlier
combat-stat pair or establish later publication of the stack contents.

The branches at `0x82CDBE58` and `0x82CDBF38` bypass reduction when the
respective definition byte has no set bits among bits 0, 1 and 2. Definition
byte 1 enters both fallthroughs. Each counts the same three bits of its
participant halfword `+0x52`, multiplies that count by the current weighted
word, and divides the low product word signed by the definition count. It
subtracts the quotient into a separate register, `r29` or `r30`. The current
weighted words in `r23`/`r15` and frame offsets 156/160 survive these blocks.
A zero participant halfword gives quotient zero. Core-pair retention into
these frame loads is established only under the guarded route above. Control
and value retention onward into selection remain unproved.

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
for exact read windows, checkpoint assumptions, stores and unclosed edges, and
[unit definitions](unit-definitions.md#combat-stat-role-boundary) for the
accepted stat-role inputs.
