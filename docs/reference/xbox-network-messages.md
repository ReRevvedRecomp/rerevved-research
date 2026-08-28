# Xbox network messages

Civilization Revolution version 1.3 uses an Xbox-native five-word game-command
record, a fixed local queue, and a 66-case dispatcher. Its record size, type
range, and serialization differ from the vendored PS3/iOS guide. Numeric
agreement alone does not transfer a cross-platform message name.

This page separates three layers:

1. The internal game message type and record.
2. Xbox queue, targeting, and dispatch behavior.
3. Object serialization and the documented limits of the platform wire model.

Game-layer message type numbers are not PowerPC instruction opcodes and are not
Xbox 360 GPU PM4 packet opcodes. The latter two describe CPU instructions and
graphics command packets, respectively; neither identifies a CivRev game
message.

## Internal record and local queue

The internal record is exactly `0x14` bytes:

| Offset | Width | Recovered field |
| ---: | ---: | --- |
| `+0x0` | 4 | `type` |
| `+0x4` | 4 | `arg1` |
| `+0x8` | 4 | `arg2` |
| `+0xC` | 4 | `arg3` |
| `+0x10` | 4 | `arg4` |

`NetworkCommandSubmit` at `0x82CE1950` stages those five words. Its sixth
incoming argument is a separate target, not a sixth record word. The submit
path constructs a vtable-bearing object and selects manager-child virtual slot
`+0x44` when the target is -1 or slot `+0x3C` otherwise. The original slot
names, the meaning of -1, and broadcast/local/targeted policy are unresolved.

The local ring begins at `0x83155C28`. Producer counter `0x8314F1F4` and
consumer counter `0x8314F1F8` address 32 modulo slots with stride `0x14`.
`NetworkCommandQueueDrain` at `0x82CE16C8` copies all five words from one slot
and directly calls `NetworkCommandDispatch` at `0x82CDDF08`.

## Dispatcher and accepted types

The dispatcher accepts unsigned types 0 through 65. Its bound check is at
`0x82CDDFF4`, indirect branch is at `0x82CDE010`, and exact 66-entry target
table begins at `0x82CDE014`. The complete numeric target map is kept in the
[Xbox network-message manifest](../../manifests/xbox-network-message-root.json),
not duplicated here.

Only three numeric types have independently accepted Xbox semantic names:

| Type | Accepted name | Independent Xbox evidence |
| ---: | --- | --- |
| 0 | Combat | Combat resolution lifecycle |
| 6 | Rush | Rush-cost producer and consumer path |
| 17 | Move | Unit-movement lifecycle |

Other useful cases retain neutral static roles:

- Types 25 and 44 share a branch that creates special unit type 30 and stores
  the second argument in its Great General carrier link. The branch has Xbox
  Great General semantics, but neither numeric case is named `AddGeneral`.
- Types 46 and 47 each enter `CalendarTurnAdvance`, submit numeric type 49, and
  invoke the same per-player follow-up. Type 46 has two static type-49 submit
  sites and type 47 has one. All three pass the `LocalPlayerIdResolve` result
  as `arg1`, -1 as `arg2` and `arg3`, the stored word rooted at `0x82F7AD00`
  as `arg4`, and -1 as the separate target. Static site count does not prove
  runtime call multiplicity or delivery.
- Type 49 forms a PowerPC `slw` mask from `arg1` and ORs it into
  `0x83157E44`. Case 46 clears that mask before its submit sites and later
  compares it with the human-player mask, branching back while they differ.
  Case 47 either clears the mask before its submit site or, when gate word
  `0x8314F1B0` is zero, seeds it from the human-player mask. These relations do
  not establish a runtime barrier, readiness, completion, or successful
  receipt. PowerPC `slw` yields zero when the shift operand has bit `0x20` set.
- The evidence does not distinguish `BeginTurn`, `EndTurn`, `ImDoneAI`,
  readiness, or completion names among types 46 through 49.
- Type 48 sets state bit `0x4000` and can submit type 53 on a guarded path.
- Type 50 updates a player mask and gates one type-48 submission when it equals
  the human-player mask. Type 51 conditionally clears a bit, type 52 sets one,
  and type 53 stores an argument in a player-indexed array and records receipt
  in a separate mask. These cases are not assigned the PS3 setup names.
- Type 54 clears sync-mismatch bit `0x10` and enters turn/calendar advancement.
  Type 55 compares record arguments with current data and a stored seed and can
  emit the exact Xbox diagnostics `Synch Err: Data` and `Synch Err: Seed`.
  Neither case is assigned the PS3 `Checksum` name, and checksum coverage is
  not established.

The remaining numeric cases are neutral dispatcher entries. Shared targets do
not by themselves prove shared meaning.

## Object serialization and envelope

The constructed command object uses vtable `0x821368E0` and embeds the five-word
record at `+0x34`. Its paired methods serialize and deserialize `type`, `arg1`,
`arg2`, `arg3`, and `arg4` as five ordered 32-bit primitives, for an exact
20-byte object-layer payload. Each primitive conditionally reverses its four
bytes when buffer byte-order state differs from the guest's active state. This
does not establish one unconditional wire endianness.

The bounded base-envelope writer contributes 32 bytes before the 20-byte
payload, for 52 bytes from the object write path. The paired reader consumes
28 bytes before the payload, for 48 bytes from the object read path. The
asymmetry is real: the reader validates literal 4 but does not read object
`+0x10`. These contributions are not complete packet sizes.

The outbound constructor at `0x82D90A18` stores leading value 77 at object
`+0x10`. `NetworkCommandObjectFactory` at `0x821D3778` allocates `0x48` bytes,
installs the same vtable, initializes that field to 1000, and zeros the embedded
record. Static evidence does not show 77 selecting that factory or overwriting
the factory default.

## Factory-table result

The factory pointer occurs once in initialized data, at `0x8216CC08`, followed
by descriptor `0x40002C03`. The surrounding eight-byte rows are not a
network-object registry. They form one executable-wide ordered
function-pointer/descriptor table with exact half-open extent
`[0x8216B800, 0x8218A050)` and 15,626 rows. It spans executable targets from
`0x821B0000` through `0x827F7860`; the factory is merely one row in that much
larger metadata set.

No literal 77 occurs in the factory row or its bounded neighbors. The precise
platform owner and descriptor bit meanings remain unproved, and no supported
consumer maps serialized leading value 77 to `NetworkCommandObjectFactory`.
The table therefore supplies no wire-factory registration claim.

## Xbox-specific boundaries

The Xbox implementation differs from the PS3/iOS guide in these areas:

- The accepted Xbox internal type range is 0 through 65, not a transferred
  cross-platform range.
- The Xbox internal record is five 32-bit words; its target is separate. A
  six-integer `AMsg` description is not the Xbox record contract.
- The Xbox command object's embedded payload is five ordered 32-bit primitives.
  The vendored opcode-dependent compact packing is not its serialization rule.
- Numeric agreement with a PS3/iOS row is not evidence for an Xbox semantic
  name, dispatch behavior, setup role, or lockstep property.

The vendored names outside Combat, Rush, and Move remain search guidance only.
So do PS3/iOS broadcast labels, GameSpy or Game Center framing, compact field
layouts, setup sequencing, checksum coverage, and deterministic-lockstep
statements.

## Remaining wire and runtime qualifications

The recovered model does not establish complete outer packet framing, headers
outside the proved helpers, metadata field meanings, target encoding, batching,
Xbox session or platform transport, host/client authority, delivery, queue
thread safety, overflow behavior, runtime ordering, resynchronization, or
deterministic lockstep.

## Evidence sources

- [Xbox network-message root](../../manifests/xbox-network-message-root.json)
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Rush-cost producer](../../manifests/rush-cost-producer.json)
- [Unit-movement lifecycle](../../manifests/unit-movement-lifecycle.json)
- [Great General attachment lifecycle](../../manifests/great-general-attachment-lifecycle.json)
- [Game calendar state](../../manifests/game-calendar-state.json)
- [Catalog contract](../catalogs.md)
