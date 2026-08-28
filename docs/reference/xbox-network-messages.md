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
- The stored word rooted at `0x82F7AD00` has four bounded candidate direct
  writers. Three copy the `+0x134` word from the object referenced by neutral
  pointer global `0x8314EFC8`; one of those copies through its second
  parameter. The fourth copies local-record field `+0x0C`. For the local-record
  path, a flag-guarded builder
  seeds a temporary from the prior stored word, applies helper `0x822DE438`,
  and writes the result to that field before the caller's later copy. This is
  not an executable-wide writer closure, and none of the pointer, object,
  helper, record, or word has a supported semantic name.
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
- Case 53 contains two static type-55 submit sites. Both pass the current-data
  helper result as arg1 and the stored word as arg2; halfword
  `0x82F77454` selects the alternate site when zero. A neutral compound
  per-player predicate gates the optional type-55 path. Its first scan starts
  an index at zero only when neutral signed word `0x82F700AC` is positive. It
  increments the index by one, advances neutral data positions by `0x80` and
  `4`, and repeats while the incremented index is signed-less-than the reloaded
  bound. Within one entered iteration, its sequential set path requires the
  loop index to differ
  from a neutral helper result; a second helper's low-byte result and a third
  helper result to be nonzero; bit `0x100` in a neutral indexed word to be
  zero; a fourth helper result not to equal one; indexed word
  `0x8312E5C0 + 4*i` to differ from the current-data result; and the selected
  low-byte flag to be zero. The selected flag is zero exactly when at least
  one of two preceding player-indexed words is nonzero and neutral global byte
  `0x8314EF9F` is zero; both indexed words zero or a nonzero global byte select
  one. The neutral constant bases used by these indexed gates are
  `0x830ED0D8`, `0x830E5650`, and `0x830E5AD0`.
- Case 53's second scan takes a fresh current-data helper snapshot, starts its
  index at zero only when the same signed bound is positive, advances the index
  and one neutral pointer by one and `4`, and repeats while the incremented
  index is signed-less-than the reloaded bound. Within one entered iteration,
  its guarded body requires the index to differ from a neutral helper result,
  a second helper's low byte to be nonzero, and the current iteration word to
  differ from the fresh snapshot.
- Passing those three guards initializes a neutral stack object at `r1+0xA0`.
  Its leading word is `0x82136930` before a call window
  and `0x8211EC1C` afterward or when the call is skipped. When the network
  manager's `+0x10` child is nonnull, the body passes that child, the stack
  object, and literal one as arguments 1 through 3 to the child's unresolved
  virtual slot `+0x44`. The bounded window has a complete
  initialization-store map over object-relative `[+0,+0x38)`, not a declared
  allocation extent, recovered type,
  serialization layout, or lifetime model. The child, indirect call, and
  literal-one roles remain unnamed. This static structure does not
  establish a fixed runtime cardinality, runtime reachability, or helper and
  element semantics.
- `0x82136930` is a neutral five-slot function table with exact extent
  `[0x82136930,0x82136944)`. Its slots point to `0x821D3D30`, `0x821D5678`,
  `0x82D90EC8`, `0x82D90E80`, and `0x82D91BD0`. The third and fourth targets
  call the accepted base-envelope write/read helpers and then pass object
  `+0x34` to the accepted 32-bit write/read primitives. The fifth passes
  manager pointer `0x8314EFDC` and object `+0x34` to neutral helper
  `0x82D8FCC8`; it is not the accepted command-object consume target.
  Allocator path `0x821D3A98` requests `0x38` bytes, installs the table, and
  initializes the same observed offsets as the guarded stack path, but stores
  zero at `+0x34` where the stack path stores its loop index. The request does
  not prove exact usable heap extent or a general stack extent.
- Both neutral tables share leading targets `0x821D3D30` and `0x821D5678`.
  The first preserves its opaque first argument, installs companion table
  `0x8211EC1C` at offset zero, conditionally calls `0x82D3D9F0` when
  arg2 bit zero is set, and returns the first argument. The second is a no-op
  return. Shared helper `0x82D3D9F0` performs one bounded conditional pointer-
  routing sequence through four neutral callees. Its fallback `0x827F5780`
  returns for a null pointer; otherwise it passes the return from `0x82812B20`,
  zero, and the original pointer to return gate `0x82811F48`. A nonzero gate
  return ends the fallback. A zero return runs a three-call secondary sequence
  and stores its final return at offset zero of a pointer returned by the first
  call. In that secondary sequence, `0x827F6910` calls `0x827FE4E8` and returns
  static address `0x82F2E9A8` when the source returns zero or source `+8`
  otherwise. Source `0x827FE4E8` uses bounded indirect gates and may return an
  initial nonzero value other than one, zero, or a pointer returned after passing one and
  `0xC4` to `0x827F9628`, with four observed offset writes on the guarded
  nonzero-result path. Intermediate selector `0x8280DD30` returns a
  nested `r13`-relative word under a zero-word gate. Final lookup `0x827F68A8`
  searches 45 stride-eight key/value entries and has exact miss mappings
  `0x13..0x24 -> 0xD`, `0xBC..0xCA -> 8`, and all others `-> 0x16`. The gate
  defaults to one and, for a nonnull third argument, reads and
  writes values at arg1- and arg3-relative addresses through locally selected
  paths, including bit tests, paired-pointer stores, and counter updates. One
  selected path changes its result to zero only
  when `NtFreeVirtualMemory` returns a negative value. Value source
  `0x82812B20` is a leaf that returns the word at `0x831580F8`; the canonical
  flat image stores zero at that address. Ghidra records one read and no writer,
  and an exact 32-bit displacement-scalar scan finds only that same load. The
  canonical image contains no aligned initialized-memory word with exact value
  `0x831580F8`. The model and searches exclude unaligned, indirect, indexed,
  runtime, and other address-materialization forms and are incomplete, so this
  does not establish read uniqueness, a writer closure, initialization code, or
  a runtime value. This
  local dataflow does not establish allocator,
  deallocator, constructor/destructor, release, ownership, lifetime, object,
  class, structure, return-value, or runtime semantics.
- Companion leading table `0x8211EC1C` is installed by a caller-provided-object
  initializer and by two post-command-call transitions. It contains six
  consecutive function pointers and has structural extent
  `[0x8211EC1C,0x8211EC34)`. Its first two targets match the common leading
  targets above, its next two are the accepted base-envelope writer and reader,
  its fifth is shared return-zero stub `0x822DF8A0`, and its sixth is neutral
  wrapper `0x821B14B0`. That wrapper preserves its opaque first argument across
  one unconditional helper call and a second call gated by arg2 bit zero, then
  returns the first argument; no destructor or release meaning is assigned.
  Zero word `0x8211EC34` separates the table from a distinct five-pointer
  sequence at `0x8211EC38`, which exact initializer `0x82E2EBD8` installs at
  caller-provided object offset zero. This closes a structural boundary, not an
  executable-wide installation or lifetime inventory. Original class and slot
  names, object extent, field meanings, ownership, lifetime, helper semantics,
  runtime delivery, and transport remain unresolved.
- Ghidra records four other reads of `0x82F700AC`: three use it as a signed-
  positive guard, while `0x821BD7F8` bounds incoming arg1 before a following
  mask path. It records no writer and omits the four independently identified
  case-53 reads. This is not a complete access inventory and does not establish
  the word's owner or fixed runtime value.
- Function `0x82D05D50` writes constant zero to `0x8314EF9F` on its straight-
  line entry path, and `0x82D217C8` contains a direct call to that writer at
  `0x82D217E0`. A corrected scan finds that writer as the only matching
  displacement access in the defined instruction listing, and initialized
  memory contains no aligned pointer value to the byte. The current reference
  model omits the independently proven read and call references, so this is
  not a complete access inventory and other writers remain unresolved.
- The no-type-55 path and both type-55 paths converge before one direct numeric
  type-54 submission. This static convergence does not prove runtime ordering,
  reachability, delivery, readiness, completion, or synchronization.

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
