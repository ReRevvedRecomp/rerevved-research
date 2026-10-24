# Xbox network messages

Civilization Revolution version 1.3 uses a native Xbox record of five words for
a game command, a fixed local queue, and a 66-case dispatcher. Its record size,
type range, and serialization differ from the unverified PS3/iOS comparison
guide. Numeric agreement alone does not transfer a cross-platform message name.

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
incoming argument is a separate target, not a sixth record word. The submit path
constructs a vtable-bearing object and selects manager-child virtual slot
`+0x44` when the target is -1 or slot `+0x3C` otherwise. The original slot
names, the meaning of -1, and broadcast/local/targeted policy are unresolved.

The local ring begins at `0x83155C28`. Producer counter `0x8314F1F4` and
consumer counter `0x8314F1F8` address 32 modulo slots with stride `0x14`.
`NetworkCommandQueueDrain` at `0x82CE16C8` copies all five words from one slot
and directly calls `NetworkCommandDispatch` at `0x82CDDF08`.

## Dispatcher and accepted types

Unsigned 0 through 65 pass bound `0x82CDDFF4`, dispatch `0x82CDE010` through
66-entry `0x82CDE014`.
[Manifest](../../manifests/xbox-network-message-root.json) owns the full numeric
map. Accepted Xbox names:

| Type | Name | Evidence |
| --- | --- | --- |
| 0 | Combat | Combat lifecycle |
| 6 | Rush | Cost producer/consumer |
| 17 | Move | Movement lifecycle |

Selected turn-command debug labels are independently bound by the native
mapper and its dispatcher input in
[`native-human-turn-completion-boundary.json`](../../manifests/native-human-turn-completion-boundary.json#/nativeCommandNames).
They identify native names, without proving delivery or completed processing.

| Case | Static contract |
| --- | --- |
| 25/44 | Shared branch creates special type 30, stores arg2 as Great General carrier link; neither case is named `AddGeneral`. |
| 46/47 | `BeginTurn` / `BeginTurnReload`. Each calls `CalendarTurnAdvance`, submits 49 and invokes same player follow-up. 46 has two sites, 47 one: `LocalPlayerIdResolve` -> `arg1`, -1 -> `arg2`/`arg3`, `0x82F7AD00` word -> `arg4`, separate target -1. Static sites prove neither runtime multiplicity nor delivery. |
| 49 | `BuildDone`. `slw` mask from `arg1` ORs `0x83157E44`. Case 46 clears before submissions, loops while unequal to human mask; 47 clears or, when `0x8314F1B0` zero, seeds human mask. Shift bit `0x20` yields zero. These relations establish no runtime barrier or successful receipt. |
| 57 | Stores low `arg2` halfword at `0x830E9050 + arg1*2`. Setup supplies player `arg1`/unresolved virtual `arg2`; eight elements reset `-1`, persist both ways and feed cost. Command/policy name unknown. |
| 48/50-53 | `BeginTurnAI` / `ImDone` / `ImNotDone` / `AIDone` / `ImDoneAI`. 48 sets `0x4000`, may submit 53. 50 updates mask and gates 48 on human-mask equality; 51 conditionally clears bit, 52 sets bit, 53 stores player argument/receipt mask. No PS3 setup names assigned. |
| 54/55 | `EndTurn` / `SynchCheck`. 54 clears mismatch `0x10` and advances turn/calendar. 55 compares data/stored seed, can emit `Synch Err: Data`/`Synch Err: Seed`; checksum coverage remains unknown. |

## Local human completion boundary

Owner `0x82D259E8` has a guarded local-human `ImDone` producer at
`0x82D269B4..0x82D26A70`. Observation at `0x82D26A38` follows the shared
state/staged checks and second local-player equality; `0x82D26A5C` exposes
the request arguments. Preserve the complete guest context at these interior
points. Calling either point as a function would bypass native setup.

A full-owner wrapper could provisionally request completion with a temporary
status bit `0x40`. Active adoption still needs bit ownership and restoration,
nested-consumer checks and observed round ordering. The early `0x14000` path
contains AI/GameOver state; the startup pending word can be discarded without
submission. Neither supplies a human request, and directly submitting
`EndTurn` skips the earlier human/AI completion chain.

The [completion manifest](../../manifests/native-human-turn-completion-boundary.json)
owns the candidate guards and default-off observation contract. A calendar
increment or a queued request alone does not count a completed world round.

## Turn and synchronization state

Four candidate `0x82F7AD00` writers: three copy object `+0x134` from
`0x8314EFC8` (one via second parameter); fourth copies record `+0x0C`.
Flag-guarded record builder seeds temporary from old word, applies `0x822DE438`,
then stores before later copy. Pointer/object/helper/record/word meanings and
image-wide writer closure remain unknown.

Case 53 has two type-55 sites (current-data arg1/stored-word arg2), with zero
`0x82F77454` selecting alternate. Optional path's first scan starts at zero only
for positive signed `0x82F700AC`, increments index one and pointers `0x80`/`4`,
retesting reloaded signed bound. Sequential set guards:

- Index differs from helper result; second low byte/third result nonzero.
- Indexed `0x100` clear; fourth result !=one.
- `0x8312E5C0 + 4*i` differs from current data; selected low-byte flag zero.

That flag is zero iff either of two player words is nonzero and `0x8314EF9F`
zero; otherwise one. Bases: `0x830ED0D8`, `0x830E5650`, `0x830E5AD0`. Second
scan takes fresh current-data snapshot, same positive-bound/index/reload loop,
pointer step `4`; requires differing helper index, nonzero second-helper low
byte and differing iteration word.

Passing those three guards initializes a neutral stack object at `r1+0xA0`. Its
leading word is `0x82136930` before the call window and `0x8211EC1C` afterward
or when skipped. When the network manager's `+0x10` child is nonnull, it
receives that child, the stack object and literal one as arguments 1 through 3
through unresolved virtual slot `+0x44`. Initialization stores cover
object-relative `[+0,+0x38)`; this is not a declared allocation extent,
recovered type, serialization layout or lifetime model. Child, indirect-call and
literal-one roles remain unnamed. Runtime cardinality, reachability and
helper/element semantics remain unknown.

| Table/helper | Bounded structure/dataflow and limit |
| --- | --- |
| `0x82136930` | Five slots, `[0x82136930,0x82136944)`: `0x821D3D30`, `0x821D5678`, `0x82D90EC8`, `0x82D90E80`, `0x82D91BD0`. Slots three/four call envelope then U32 write/read for `+0x34`; fifth passes `0x8314EFDC`/`+0x34` to `0x82D8FCC8`, not command consume. `0x821D3A98` requests `0x38`, installs table/same fields, but `+0x34` zero instead of loop index. Request proves no usable heap/general stack extent. |
| Common leading targets | `0x821D3D30` retains arg1, installs `0x8211EC1C`, conditionally calls `0x82D3D9F0` for arg2 bit zero, returns arg1. `0x821D5678` is no-op. |
| `0x82D3D9F0` | Conditional pointer routing through four callees. Fallback `0x827F5780` returns on null; otherwise sends `0x82812B20` result, zero, original pointer to `0x82811F48`. Nonzero return ends; zero runs three secondary calls and stores final result at first-return pointer offset zero. |
| Secondary source | `0x827F6910` calls `0x827FE4E8`, returning `0x82F2E9A8` for zero or source `+8`. Source's indirect gates may return initial nonzero !=one, zero, or pointer from `0x827F9628` with one/`0xC4`; guarded nonzero path has four offset writes. `0x8280DD30` returns nested `r13` word under zero-word guard. |
| `0x827F68A8` | Searches 45 stride-eight key/value rows; misses `0x13..0x24 -> 0xD`, `0xBC..0xCA -> 8`, otherwise `-> 0x16`. |
| Return gate | Defaults one; nonnull arg3 admits arg1/arg3 reads/writes, bits, paired pointers/counters. Selected path returns zero only for negative `NtFreeVirtualMemory`. |
| `0x82812B20` | Leaf returns `0x831580F8`, zero in image. Ghidra one read/no writer; exact 32-bit displacement scan finds same load, no aligned initialized pointer word. Unaligned/indirect/indexed/runtime/other materializers remain open: no unique reader, writer closure, initializer or live-value proof. |
| `0x8211EC1C` | Caller-object initializer/two post-command transitions install six pointers, `[0x8211EC1C,0x8211EC34)`. Common first two, envelope writer/reader, return-zero `0x822DF8A0`, wrapper `0x821B14B0` (retains arg1 through unconditional helper and arg2-bit-zero helper, returns arg1). No destructor/release meaning. |
| Adjacent table | Zero `0x8211EC34` separates five pointers at `0x8211EC38`, installed at caller offset zero by `0x82E2EBD8`; structural boundary only, not complete installation/lifetime inventory. |

These helper dataflows establish no allocator/deallocator,
construction/destruction, release/ownership, class/object/field, return-value or
runtime/transport semantics. Original class/slot names and extents remain
unknown.

Ghidra lists four other `0x82F700AC` reads: three positive guards and
`0x821BD7F8` arg1 bound before mask. It omits four case-53 reads/no writer;
owner/value/access inventory remain incomplete. `0x82D05D50` zeros `0x8314EF9F`
at straight-line entry; `0x82D217C8` calls at `0x82D217E0`. Corrected
defined-instruction scan finds only that displacement, no aligned initialized
pointer. Reference model omits proven read/call; other writers remain open. All
type-55 submit/no-submit paths merge before one type-54 site. Other cases remain
neutral; shared targets prove no shared meaning.

## Object serialization and envelope

The constructed command object uses vtable `0x821368E0` and embeds the five-word
record at `+0x34`. Its paired methods serialize and deserialize `type`, `arg1`,
`arg2`, `arg3`, and `arg4` as five ordered 32-bit primitives, for an exact
20-byte object-layer payload.

Each primitive conditionally reverses its four bytes when buffer byte-order
state differs from the guest's active state. This does not establish one
unconditional wire endianness.

The bounded base-envelope writer contributes 32 bytes before the 20-byte
payload, for 52 bytes from the object write path. The paired reader consumes 28
bytes before the payload, for 48 bytes from the object read path. The asymmetry
is real: the reader validates literal 4 but does not read object `+0x10`. These
contributions are not complete packet sizes.

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
`[0x8216B800, 0x8218A050)` and 15,626 rows.

It spans executable targets from `0x821B0000` through `0x827F7860`; the factory
is merely one row in that much larger metadata set.

No literal 77 occurs in the factory row or its bounded neighbors. The precise
platform owner and descriptor bit meanings remain unproved, and no supported
consumer maps serialized leading value 77 to `NetworkCommandObjectFactory`. The
table therefore supplies no claim about factory registration for wire messages.

## Xbox-specific boundaries

The Xbox implementation differs from the PS3/iOS guide in these areas:

- The accepted Xbox internal type range is 0 through 65, not a transferred
  cross-platform range.
- The Xbox internal record is five 32-bit words; its target is separate. A
  six-integer `AMsg` description is not the Xbox record contract.
- The Xbox command object's embedded payload is five ordered 32-bit primitives.
  The comparison guide's opcode-dependent compact packing is not its
  serialization rule.
- Numeric agreement with a PS3/iOS row is not evidence for an Xbox semantic
  name, dispatch behavior, setup role, or lockstep property.

The unverified comparison names outside Combat, Rush, and Move remain search
guidance only. So do PS3/iOS broadcast labels, GameSpy or Game Center framing,
compact field layouts, setup sequencing, checksum coverage, and statements about
deterministic lockstep.

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
- [Great General attachment
  lifecycle](../../manifests/great-general-attachment-lifecycle.json)
- [Game calendar state](../../manifests/game-calendar-state.json)
- [Catalog contract](../catalogs.md)
