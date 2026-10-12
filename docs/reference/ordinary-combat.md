# Ordinary combat boundary

Separate local blocks in `CombatResolve` establish stat-weighting operations,
conditional selection arithmetic and exact generator-word stores. Their
continuations are unjoined. The result does not establish an ordinary path
from the accepted stat pair to an outcome or persistent participant changes.

## Independent local blocks

The accepted pair obtains attacker attack at `0x82CDA214` and defender defense
at `0x82CDA234`, retaining them separately. Later weighting instructions have
the corresponding operand orientation under explicit register-retention
assumptions. Resolver mode and a separate local flag remain distinct inputs.

UnitType 16, Catapult, has definition byte `+0x48` equal to 1 in the supported
image. Local mask construction and selection examples assume valid frame and
table bindings, zero participant `+0x52` values, zero byte guards, and supplied
weighted register/frame values. These are synthetic checkpoint inputs, not
observed or validated ordinary combat values.

The selection block advances a state word by a low-word multiply-add and
optional unsigned modulus reduction, then uses scaled arithmetic in a signed
comparison. On the synthetic single-bit case, a successful ordinal-zero
selection clears the defender-corresponding local bit. Two four-byte stores
write selection value 1 and ordinal 0 through current `r7`, at offsets 0
and `+0x48`. The pointer's origin and memory class are unknown. The same local
checkpoint and exit assumptions support exact generator state/counter stores;
they do not join the checkpoint to the earlier combat-stat pair.

## Unclosed continuations

The selected definition value makes two branches fall through unread ranges
`0x82CDBE60..0x82CDBEE0` and `0x82CDBF40..0x82CDBFC0`. Core-pair retention
into selection is unproved. The missing instruction at `0x82CDC640` also
leaves the selection-store pointer unbound.

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
