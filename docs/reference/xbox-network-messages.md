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
then stores before later copy. The
[RNG transfer contract](../../manifests/combat-rng-save-reload-boundary.json#/headerStateTransferBoundary)
identifies this word as current main RNG state, with conditional save/load
transfer. It does not prove complete generator restoration or identify an
immutable map seed. Other object meanings and writer closure remain unknown.

`SynchCheck` first clears mismatch bit `0x10`. A nonzero sampled network byte
admits the scalar and RNG comparisons; unequal comparisons set that bit.
Skipped, equal and unequal branches share a normal-return continuation that
samples a fresh scalar and submits numeric 60 with local index, scalar, -1 and
current RNG state. This is not an echo or proof of repair. Numeric 60 ORs an
index-derived mask into `0x83157E40` and writes the scalar into the indexed
`0x8312E5C0` array later read by case 53. No acknowledgement name, valid-index
guarantee, complete peer receipt or arrival order is established. Exact gates:
[case 55](../../manifests/xbox-network-message-root.json#/turnAndSyncAnchors/case55/returnSubmissionBoundary)
and [case 60](../../manifests/xbox-network-message-root.json#/turnAndSyncAnchors/case60).

The [scalar/phase contract](../../manifests/spaceship-part-presentation-boundary.json#/worldActorSaveSyncProjectionBoundary)
owns the selected unit contribution and sample timing. Its conditional nested
command drain can run before actor retirement. A scalar projection is not a
bulk game-state recovery snapshot.

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

The index object's consumer `0x82D8FCC8` selects equal/unequal child callbacks
and conditionally publishes helper-returned values at receiver-associated
storage. Its local body supplies no direct snapshot application, mismatch-bit
test or numeric-60 submission. Opaque calls remain open; this is not a
disconnect or completed resync identification. A diagnostic binds the writer's
receiver-associated value one to hotjoin pending state; the separate `+0x2C`
store is not identified by that label. A selected state-one consumer calls a
network-manager helper, then writes transferring state two without testing the
helper return. A selected removal tail clears the indexed state; its conditional
turn helper submits `BeginTurn` only when its scan finds no state two/three.
Missing entries do not count as active transfer. The
[consumer boundary](../../manifests/xbox-network-message-root.json#/turnAndSyncAnchors/case55/indexObjectConsumerBoundary)
and [progress boundary](../../manifests/xbox-network-message-root.json#/turnAndSyncAnchors/hotjoinProgressBoundary)
own those effects, conditions and lifetime premises.

The [hotjoin transfer/restore boundary](../../manifests/xbox-hotjoin-transfer-restore-boundary.json)
owns the native compressed save-style snapshot, transfer-ID queue result,
received-stream writes, shared mode-1 loader, completion mask and conditional
receive-callback-to-command-append corridor. Exception metadata establishes
`0x82D8F878` as a native entry despite its configured containing-function model.
This is implemented world-state recovery machinery. Successful delivery,
fresh disconnected-player admission, command reconciliation and accepted
return-to-play remain unproved.

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

## Native transport sequence boundary

The [selected native receive helpers](../../manifests/xbox-network-message-root.json#/nativeTransportReceiveBoundary)
establish more than raw UDP: a header-bearing path compares 16-bit modular
sequence fields, skips older records, buffers later records with an equality
check, and drains buffered records matching the next expected field. Separate
control inputs retire a stored prefix or select stored records by an incoming
sequence field/range; they do not establish a retry time interval.
The expected field advances before the dispatch outcome is known. When numeric
type seven reaches `0x82A123F8`, that dispatcher returns one without a type
handler. This does not guarantee a true enclosing receive result. A true
transport result is not a world-write receipt. The type-101 retry parser also reads
two bytes before its length check; its exact declared-payload bound and proposed
pre-read guard belong to the manifest.

The [selected send path](../../manifests/xbox-network-message-root.json#/nativeTransportSendBoundary)
reaches `NetDll_sendto` through a proved native shim. Its outer nonzero result
also covers selected no-send and nonfatal-error branches, and can store a
sampled value at connection `+0x88` without a peer receipt. The SDK's stopped-client
length/drop branch additionally requires relay mode and a still-registered
datagram handle. The manifest separates the API result, observer callback,
sample store and unproved delivery and clock-provider contracts.

The [selected readiness gate](../../manifests/xbox-network-message-root.json#/nativeTransportReadinessBoundary)
supplies a zero-timeout, one-socket write-set poll. Its zero result alone does
not distinguish ordinary not-ready from selector failure; neither outcome is
a peer-delivery receipt. Native mode and relay-queue integration remain open.

These are local retained-connection contracts. Full fragmentation, timer/retry
limits, wrap/lifetime bounds, direct/relay crossover and successful command
delivery remain open. The SDK's directory retries and direct-path replay window
are separate layers. No new reorder or retransmit implementation follows from
this partial native audit.

The hotjoin manifest's
[connection callback boundary](../../manifests/xbox-hotjoin-transfer-restore-boundary.json#/returningConnectionCallbackBoundary)
identifies the installed vector and selected listener slots. The
[connection-index boundary](../../manifests/xbox-hotjoin-transfer-restore-boundary.json#/nativeConnectionIndexBoundary)
follows selected raw callback corridors into guarded native index allocation
and disconnect forwarding. A native connection index is not an established
XUID/game-player binding. Transport sequence handling and this allocation path
do not establish fresh returning-player admission or successful recovery.

The [member-name selector](../../manifests/xbox-hotjoin-transfer-restore-boundary.json#/nativeMemberNameSelectionBoundary)
extends that path through a parsed 64-byte string field, case-insensitive setup
string comparison and zero-result index lookup. Actual vacancy requires retained
service/descriptor identity; validation, member-to-XSession binding and retirement
remain active research. The bounded parser hardening seam is a proposal, not a
malformed-peer or runtime failure observation.

The [XSession membership boundary](../../manifests/xbox-hotjoin-transfer-restore-boundary.json#/nativeXSessionMembershipBoundary)
joins selected parsed member fields to the native member-join wrapper before
the later free-index scan, and traces the member-leave call before guarded
retirement. Name-based candidate selection can occur earlier. Retained owner,
record and descriptor identity, supported counts and helper effects remain
conditions; neither API call establishes returning-player or world acceptance.

The [selected local-member producer](../../manifests/xbox-hotjoin-transfer-restore-boundary.json#/nativeLocalMemberIdentityBoundary)
binds local address, sign-in and profile-XUID requests to the selected local
record's user-index and count fields. Its pending-address back edge has no local
deadline or cancellation check. Record-pointer storage and partial address
writes can precede the count-one write; they do not establish completed
membership. The proposed title readiness stage, logging hooks and unrun controls
remain research findings, with outer attempt/cleanup handling and player
admission open.

The [selected create/startup boundary](../../manifests/xbox-live-session-search-contract.json#/nativeCreateStartupBoundary)
shows the earlier synchronous SDK relay-startup wait and distinguishes initializer
success from a ready network. Host/join callers require exact local-producer
result one and collapse other producer results to three. SDK cleanup serializes
behind startup, while Client Stop waits behind the active Associate operation;
an earlier direct Stop does not prevent a later association by that startup.
They do not provide whole-attempt cancellation.
Native reference pairing and outer cancellation ownership remain active.

The [selected cleanup helpers](../../manifests/xbox-system-link-qos-root.json#/nativeNetworkCleanupBoundary)
separate the WSA-only session helper from the WSA-then-XNet helper. The SDK's
zero XNet cleanup result covers both nonfinal reference release and final
network cleanup. These local calls establish neither a complete lifetime
balance nor a leak; the destructor callbacks and outer owners remain active.

The [selected failed-startup diagnostic](../../manifests/xbox-system-link-qos-root.json#/nativeStartupDiagnosticBoundary)
has a normal return path in the checked recompiled type-20 handler, with valid
guest string access and normal helper/logger behavior required. The startup
helper then returns the later WSA result. Visible debug output, XNet readiness,
original retail trap handling and complete reference pairing are separate
contracts.

The [selected session-owned object retirement](../../manifests/xbox-live-session-search-contract.json#/nativeSessionObjectRetirementBoundary)
binds the QoS and settings objects to their selected destructors. QoS release
precedes serialized-buffer disposal, and a configured SDK release can also clear
the active service's QoS mirror. Failed or skipped release still requires correct
final cleanup. Local field clears establish neither complete network retirement
nor a clean second match; allocator behavior, the registry service callback and
outer reference pairing remain active.

The [selected allocation-return contract](../../manifests/xbox-live-session-search-contract.json#/nativeSessionAllocationReturnBoundary)
connects explicit conditional zero-return arms to the recorded session consumer
guard proposals. Concrete refill/heap/handler states and cleanup-safe caller
unwind remain active research; the source paths establish no executed failure.

The [selected failure policy](../../manifests/xbox-live-session-search-contract.json#/nativeSessionFailurePolicyBoundary)
keeps create and migration result encodings separate. For a session-create result
whose low word differs from one, its selected join-parent suffix requests
retirement of a present network object. Early guard exits skip that suffix. The
proposed local guards avoid publishing fresh partial objects; callback, queue,
socket and complete reference compensation remain active research.

The [selected outer join rollback](../../manifests/xbox-live-session-search-contract.json#/nativeOuterJoinRollbackBoundary)
reaches service destruction for a matching registry value on its processed
failure route. Session-wrapper destruction additionally requires a retained,
nonnull wrapper with the selected vptr; preparation can fail before one exists.
Stable registry/key/object identities and normal helper returns are required.
Its early exits differ, and the mode-2 marker setter is
separate from search cancellation or release. This conditional destructor reach
does not establish final socket retirement or a clean retry.

The [selected socket-unwind helpers](../../manifests/xbox-network-message-root.json#/nativeSocketUnwindHelperBoundary)
separate registry-node removal, callback traversal, deferred flagging and the
immediate close/container/WSA/XNet call sequence. The immediate path ignores
the close API result; its later return has a different source. The SDK's zero
close result also does not establish OS-close success or object destruction.
Connection callbacks, configured retirement targets and complete lifetimes
remain active research.

The [selected callback and configured-target contract](../../manifests/xbox-network-message-root.json#/nativeSocketCallbackTargetBoundary)
binds reverse iteration to a slot address, its stored connection value and a
fixed-flag helper sequence. Element callbacks receive the slot address instead.
The initial configured retirement target reaches header/list or virtual-memory
requests, with subordinate retirement effects still active. These different
results do not form a shared cleanup-success enum.

The [selected forced-connection continuation](../../manifests/xbox-network-message-root.json#/nativeForcedConnectionRetirementBoundary)
publishes state seven before its container requests and can continue after a
callback wrapper requests socket retirement. Safe continuation depends on the
actual callbacks and retained connection/container lifetimes. This establishes
a lifetime obligation; it does not establish a stale access or a complete fix.
Actual growth, copy and installed destructor effects remain active research.

The [selected container-mutation contract](../../manifests/xbox-network-message-root.json#/nativeConnectionContainerMutationBoundary)
records search comparison order, capacity/backing/count publication and the
callback-before-erase sequence. Actual target binding, existing-backing growth
and callback ownership remain active before a completed container transfer or
a failure-safe retry.

The [selected growth/copy target contract](../../manifests/xbox-network-message-root.json#/nativeConnectionGrowthCopyBoundary)
joins the configurable growth slot and its initial target to the allocator's
conditional zero-return path. The forward-copy routine has local return paths
and a bounded span/storage contract. These facts support a growth-guard proposal;
actual title binding and complete failure ownership still need proof.

The [selected constructor/callback contract](../../manifests/xbox-network-message-root.json#/nativeConnectionContainerConstructionBoundary)
binds the constructed buckets and separate list to four-byte strides, distinct
callback configurations and a fixed list-slot target. Parent pointer guards do
not establish valid child backing. Actual title-object identity, partial-state
compensation and the target's retirement effect remain active research.

The [configured-target return boundary](../../manifests/xbox-network-message-root.json#/nativeSocketConfiguredReturnBoundary)
binds the selected exit helper to preservation of the parent result word under
valid frame, lock and ABI premises. It also records a four-slot callback writer;
zero raw direct calls and zero modeled references do not prove an immutable
table. Local result preservation remains separate from completed retirement.

The [selected native duplicate-handle uses](../../manifests/xbox-network-message-root.json#/nativeDuplicateHandleUseBoundary)
account for three raw direct wrapper sites found by the aligned-word scan of
initialized executable memory. Two request
the current-thread pseudo-handle; the third reads a field populated by a thread
creator, with retention across its intervening wait required. These selected
inputs do not establish a socket alias. Indirect use, thread/owner teardown and
actual runtime occurrence remain separate research.

The [selected registry service reset](../../manifests/xbox-live-session-search-contract.json#/nativeSessionServiceResetBoundary)
binds the destructor's two lookups and a constructed cross-key path to a
conditional receiver class. Its selected callback resets a local list and
vector; the nine copied head markers are not established player or SDK event
identities. Key replacement, other construction orders and complete network
retirement remain active research.

The [dynamic export census](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeDynamicExportBoundary)
accounts for eight direct lookup sites using the pinned SDK's startup-extension
and instrumentation mappings. Indirect/tail paths and other platform versions
remain outside that negative; no service or startup runtime result follows.

Selected [statistics request consumers](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeStatsConsumerBoundary)
and the [voice-create status contract](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeVoiceStatusBoundary)
join native API return checks to the pinned SDK owners. They distinguish
unsupported results from output consumption; they do not establish a statistics
backend, voice transport, audible output or a successful online feature.

The [selected guest-refusal predicate](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeGuestRefusalBoundary)
adapts sign-in-info status before testing one output bit. Its true branch
requests a refusal message and sign-in UI, while the pinned SDK leaves the
tested bit clear. Actual guest-profile policy, caller/action identity and
display/completion behavior remain active research.

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
