# Xbox network messages

In the Xbox 360 build of Civilization Revolution (version 1.3), a network
message is a small record that describes one game action: a unit moves, a fight
starts, a city rushes production, a player finishes a turn. The game fills in a
record of five 32-bit words, passes it to one submit function, keeps it in a
fixed queue of 32 slots and runs it through a dispatcher with 66 cases. The same
record can also be copied into a network object and written to a byte buffer.
Whether a given type is sent, to whom, and when it runs on another machine are
not recovered.

Every claim on this page is read from the Xbox image and its recompiled copy.
The PS3/iOS comparison guide is unverified, and its record size, type range and
serialization differ from the Xbox code. Numeric agreement alone does not carry
a cross-platform message name over to the Xbox.

The page has three layers:

1. The internal message type and record.
2. The Xbox queue, targeting and dispatch.
3. Object serialization, and the limits of what is known about the transport.

Game message type numbers are not PowerPC instruction opcodes and are not Xbox
360 GPU PM4 command opcodes. Those describe CPU instructions and graphics
commands, and neither identifies a game message.

Detail pages for the parts that grew large:

- [Xbox command serialization](xbox-command-serialization.md): the object, its
  byte layout and the function table that holds the factory pointer.
- [Xbox turn command flow](xbox-turn-command-flow.md): types 46 through 55 and
  60, the state words they use and the lobby and hotjoin limits next to them.
- [Xbox command callback tables](xbox-command-callback-tables.md): the two
  function pointer tables used by the type 53 scan and the helper code they
  reach.

## A worked example: a Move command

A Move command has type 17 and four argument words, `arg1` through `arg4`. These
steps are calls and branches in the guest code. No run has watched them happen.

1. **Submit.** The caller passes the type, four arguments and a separate target
   to `NetworkCommandSubmit` (`0x82CE1950`). It stages the five record words on
   the stack. The target is not part of the record.
2. **Object.** The submit path builds a network object through `0x82D90A18`,
   which copies the five words into the object at `+0x34` and stores the leading
   value 77 at `+0x10`. It then calls a virtual method of the network manager's
   child object. The method is slot `+0x44` when the target is -1 and slot
   `+0x3C` otherwise.
3. **Queue.** The local ring holds the five words of each record, and
   `NetworkCommandQueueDrain` (`0x82CE16C8`) copies one record out and calls the
   dispatcher `NetworkCommandDispatch` (`0x82CDDF08`).
4. **Dispatch.** The dispatcher accepts type 17, because it is in the range 0
   through 65, and jumps through table `0x82CDE014` to the Move handler at
   `0x82CDEDFC`. The handler is described in the
   [unit movement lifecycle](../../manifests/unit-movement-lifecycle.json). The
   dispatcher reads `type` and the first three arguments directly. The target is
   not in the ring, so the dispatcher never sees it.
5. **Bytes.** If the object is written to a buffer, the write path produces 52
   bytes: a 32 byte base envelope and the 20 byte record. Reading one back
   consumes 48 bytes. Neither number is a complete datagram size.

A mod that adds or changes a command has these limits to work within. The record
holds a type and exactly four arguments of 32 bits each. A command that needs
fewer arguments still writes all five words. The dispatcher accepts only types 0
through 65, through a table of 66 entries. It reads only the type and the first
three arguments directly, and the meaning of `arg4` is not established.

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
constructs a network object with a vtable and selects manager child virtual slot
`+0x44` when the target is -1 or slot `+0x3C` otherwise. The original slot
names, the meaning of -1, and whether a message is a broadcast, a local action
or aimed at one player are unresolved.

The local ring begins at `0x83155C28`. Producer counter `0x8314F1F4` and
consumer counter `0x8314F1F8` address 32 slots with modulo wrap and stride
`0x14`. `NetworkCommandQueueDrain` at `0x82CE16C8` copies all five words from one
slot and directly calls `NetworkCommandDispatch` at `0x82CDDF08`. Modulo storage
does not show thread safety, behavior on overflow, delivery or runtime order.
The [root record](../../manifests/xbox-network-message-root.json#/internalRepresentation)
holds the exact instruction words.

## Dispatcher and accepted types

Unsigned values 0 through 65 pass the range check at `0x82CDDFF4`. The jump at
`0x82CDE010` uses the 66 entry table at `0x82CDE014`. The
[root record](../../manifests/xbox-network-message-root.json#/queueAndDispatch/dispatch)
holds the same table with the instruction words that load it.

The Name status column uses four values:

- **Name supported**: Combat, Rush and Move, each tied to a lifecycle record by
  the handler's behavior.
- **Native label**: the game's own debug text names the type. The native mapper
  `0x82CD5400` limits its input to 0 through 65, and the dispatcher passes the
  record type to it. The labels are recorded in
  [`native-human-turn-completion.json`](../../manifests/native-human-turn-completion.json#/nativeCommandNames).
  A label names the type. It does not show that the command is sent, received or
  finished, or give it any readiness, barrier or checksum meaning.
- **Role only**: the handler's local effect is recovered, but no name is
  accepted.
- **Unnamed**: only the handler address is known.

| Type | Handler | Name | Name status | Note |
| ---: | --- | --- | --- | --- |
| 0 | `0x82CDF74C` | `Combat` | Name supported | [Combat lifecycle](../../manifests/combat-resolution-lifecycle.json) |
| 1 | `0x82CDFA74` | none | Unnamed | Same handler as type 42 |
| 2 | `0x82CDFDF8` | none | Unnamed | |
| 3 | `0x82CE16AC` | none | Unnamed | The common exit, with no handler of its own |
| 4 | `0x82CDFFA0` | none | Unnamed | The lobby unready request uses this type, see the turn command flow page |
| 5 | `0x82CDFFF8` | none | Unnamed | |
| 6 | `0x82CE0028` | `Rush` | Name supported | [Rush cost producer](../../manifests/rush-cost-producer.json) |
| 7 | `0x82CE003C` | none | Unnamed | |
| 8 | `0x82CE0094` | none | Unnamed | |
| 9 | `0x82CE16AC` | none | Unnamed | The common exit, with no handler of its own |
| 10 | `0x82CE026C` | none | Unnamed | |
| 11 | `0x82CE02A0` | none | Unnamed | |
| 12 | `0x82CE02D4` | `Settle` | Native label | |
| 13 | `0x82CE04E8` | `Fortify` | Native label | |
| 14 | `0x82CE06B0` | `Sentry` | Native label | |
| 15 | `0x82CE090C` | none | Unnamed | |
| 16 | `0x82CE1354` | none | Unnamed | |
| 17 | `0x82CDEDFC` | `Move` | Name supported | [Unit movement lifecycle](../../manifests/unit-movement-lifecycle.json) |
| 18 | `0x82CE06E0` | none | Unnamed | |
| 19 | `0x82CDFD94` | none | Unnamed | |
| 20 | `0x82CE0190` | none | Unnamed | The failed startup diagnostic is in the type 20 handler, see the transport section |
| 21 | `0x82CE0224` | none | Unnamed | |
| 22 | `0x82CE0710` | none | Unnamed | |
| 23 | `0x82CE0848` | none | Unnamed | |
| 24 | `0x82CE1368` | none | Unnamed | |
| 25 | `0x82CE14D8` | none | Role only | Special unit type 30, shared with type 44 |
| 26 | `0x82CDF484` | none | Unnamed | |
| 27 | `0x82CDF4C0` | none | Unnamed | |
| 28 | `0x82CDF4D0` | none | Unnamed | |
| 29 | `0x82CDFF78` | none | Unnamed | |
| 30 | `0x82CDFF8C` | none | Unnamed | |
| 31 | `0x82CDF478` | none | Unnamed | |
| 32 | `0x82CE1568` | none | Unnamed | |
| 33 | `0x82CDF4E4` | none | Unnamed | |
| 34 | `0x82CDF684` | none | Unnamed | |
| 35 | `0x82CDF6DC` | none | Unnamed | |
| 36 | `0x82CDF724` | none | Unnamed | |
| 37 | `0x82CDF578` | none | Unnamed | |
| 38 | `0x82CE0054` | none | Unnamed | |
| 39 | `0x82CE0068` | none | Unnamed | |
| 40 | `0x82CE12C4` | none | Unnamed | |
| 41 | `0x82CE1338` | none | Unnamed | |
| 42 | `0x82CDFA74` | none | Unnamed | Same handler as type 1 |
| 43 | `0x82CE1648` | none | Unnamed | |
| 44 | `0x82CE14D8` | none | Role only | Special unit type 30, shared with type 25 |
| 45 | `0x82CE166C` | none | Unnamed | |
| 46 | `0x82CDE1AC` | `BeginTurn` | Native label | |
| 47 | `0x82CDE424` | `BeginTurnReload` | Native label | |
| 48 | `0x82CDE79C` | `BeginTurnAI` | Native label | |
| 49 | `0x82CDE60C` | `BuildDone` | Native label | |
| 50 | `0x82CDE628` | `ImDone` | Native label | |
| 51 | `0x82CDE768` | `ImNotDone` | Native label | |
| 52 | `0x82CDE8F4` | `AIDone` | Native label | |
| 53 | `0x82CDE910` | `ImDoneAI` | Native label | |
| 54 | `0x82CDED8C` | `EndTurn` | Native label | |
| 55 | `0x82CDEC48` | `SynchCheck` | Native label | |
| 56 | `0x82CDE11C` | none | Unnamed | |
| 57 | `0x82CDE174` | none | Role only | One halfword per player |
| 58 | `0x82CDE12C` | none | Unnamed | |
| 59 | `0x82CDE14C` | none | Unnamed | |
| 60 | `0x82CDED60` | none | Role only | Stores the sample that type 55 submits |
| 61 | `0x82CDEDA4` | none | Unnamed | |
| 62 | `0x82CDEDC0` | none | Unnamed | |
| 63 | `0x82CDEDDC` | `GameOver` | Native label | |
| 64 | `0x82CDFD88` | none | Unnamed | |
| 65 | `0x82CDE188` | none | Unnamed | |

The unverified comparison names for other types remain search leads only.

### Types with a recovered role

| Types | Recovered role |
| --- | --- |
| 25 and 44 | They share one handler. It creates special unit type 30 for `arg1` and stores `arg2` as the Great General carrier link. Neither case is named `AddGeneral`. The text `AddGeneral` exists in the native label block at `0x82156CBC`, but no recorded route ties it to either type. The [label block record](../../manifests/xbox-turn-label-block.json) (`RVA-F-0411`) shows the block, and the [attachment record](../../manifests/xbox-network-message-root.json#/greatGeneralAttachmentAnchor) holds the handler. The reason for two cases and the timing of the award are unresolved. |
| 46 and 47 | `BeginTurn` and `BeginTurnReload`. Each calls `CalendarTurnAdvance`, submits type 49 and calls the same player follow-up. |
| 48, 50, 51, 52 and 53 | `BeginTurnAI`, `ImDone`, `ImNotDone`, `AIDone` and `ImDoneAI`. They keep a mask of finished players and start or continue the AI step. No PS3 setup names are assigned. |
| 49 | `BuildDone`. It ORs a mask made from `arg1` into `0x83157E44`. |
| 54 and 55 | `EndTurn` and `SynchCheck`. Case 54 clears mismatch bit `0x10` and advances turn and calendar. Case 55 compares data and a stored seed, and can print `Synch Err: Data` or `Synch Err: Seed`. What the checksum covers is unknown. |
| 57 | It stores the low halfword of `arg2` at `0x830E9050 + arg1 * 2`. Setup supplies the player in `arg1`, and `arg2` is an unresolved virtual call result. The eight elements start at -1, are saved and loaded, and feed production cost. The command and its policy have no recovered name. See [Unit definitions](unit-definitions.md#settler-production-gates). |
| 60 | It ORs an index mask into `0x83157E40` and stores `arg2` in the per player array that case 53 reads. Case 55 is the submitter. |

The [turn command flow](xbox-turn-command-flow.md) page holds every address,
state word and limit for types 46 through 55 and 60. It also holds the human
completion path (`TurnSelectionUpdate`, `0x82D259E8`), the stored word
`0x82F7AD00` and the random number states, the two scans of case 53, the lobby
ready check, and the limits on hotjoin, member removal and leave. A calendar
increment or a queued request alone does not count as a completed world round.
Submitting `EndTurn` directly skips the human and AI completion chain.

## Object serialization and the function table

The constructed command object has vtable `0x821368E0` and holds the five word
record at `+0x34`. Its paired methods write and read `type`, `arg1`, `arg2`,
`arg3` and `arg4` as five ordered 32-bit primitives, for an exact 20 byte
payload. Each primitive reverses its four bytes only when the buffer's byte order
state differs from the guest's active state, so there is no single fixed wire
byte order.

The base envelope writer adds 32 bytes before the payload (52 bytes from the
object write path). The paired reader consumes 28 bytes before the payload (48
bytes), because it checks the literal 4 and does not read object `+0x10`. The
outbound constructor at `0x82D90A18` stores 77 at `+0x10`.
`NetworkCommandObjectFactory` at `0x821D3778` allocates `0x48` bytes and sets the
same field to 1000. Static evidence does not show 77 selecting that factory. The
meaning of 77 and of the six metadata words is not recovered.

The factory pointer occurs once in initialized data, at `0x8216CC08`, followed
by descriptor `0x40002C03`. It is one row of an ordered table of 8 byte rows,
each a function start followed by a descriptor word. The inspected run is
`[0x8216B800, 0x8218A050)`, with 15,626 rows. That run is a prefix of the PE
Exception directory, which the header places at `0x8216B800` with 28,353 rows
through `0x821A2E08` in `.pdata`. The loader reads rows of this shape as runtime
function entries. The 15,626 rows are the part inspected for ordered rows, not
the whole directory. See
[`RVA-F-0362`](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362/selectedAlwaysAtWarClosureBoundary/currentEvidence/sharedChecks/exceptionMetadata)
and the
[table record](../../manifests/xbox-network-message-root.json#/wireSerialization/outerFactory/functionMetadataTable).
The table is not a registry of network objects. No literal 77 occurs in the
factory row or its neighbors, and no supported consumer maps a serialized 77 to
the factory, so the table supplies no claim about factory registration for wire
messages. Which platform component reads the directory and the meaning of each
descriptor bit are not established.

The [serialization page](xbox-command-serialization.md) holds the base
envelope step order, the addresses and the full table walk.

## Framing and transport order

This is the order of the layers recovered so far, from the game action to the
socket call. Each step is limited to what the code shows.

1. **Record.** Five words, queued through `NetworkCommandSubmit`.
2. **Object.** The record is copied into a command object with a leading value
   and base metadata. This layer is closed: see the serialization page.
3. **Buffer.** The object writes 52 bytes through primitives that may reverse byte
   order. Outer framing, headers outside the proved helpers, target encoding and
   batching are not recovered.
4. **Native transport.** Selected helpers keep 16-bit sequence fields, a stored
   prefix of records and buffered later records. A transport type
   below 8 is tested by the receive classifier `0x82A11B00`, a different
   function from the command dispatcher. Those transport types are not the game
   command types 0 through 65.
5. **Socket call.** The selected send path reaches `NetDll_sendto` through a
   proved native shim.

Delivery, Xbox session or platform transport details, host and client authority,
queue thread safety, behavior on overflow, runtime ordering, resynchronization
and deterministic lockstep are not established.

## Xbox-specific qualifications

The Xbox implementation differs from the PS3/iOS guide in these ways:

- The accepted Xbox type range is 0 through 65, not a transferred cross-platform
  range.
- The Xbox record is five 32-bit words, and its target is separate. A six integer
  `AMsg` description is not the Xbox record.
- The Xbox command object's payload is five ordered 32-bit primitives. The guide's
  compact packing, which depends on the opcode, is not the Xbox rule.
- Numeric agreement with a PS3/iOS row is not evidence for an Xbox name,
  dispatch behavior, setup role or lockstep property.

The unverified comparison guide names outside Combat, Rush and Move, PS3/iOS
broadcast labels, GameSpy or Game Center framing, compact field layouts, setup
order, checksum coverage and statements about deterministic lockstep stay search
leads. The roles in the
type table are static: they come from code relations, not from observed matches.

## Native transport sequence boundary

The paragraphs below summarize selected native contracts. Each one links to the
manifest that holds the exact addresses, premises and conditions. Every contract
is local: it describes what the code does when the stated storage, frames and
locks are valid and helper calls return normally. None shows a delivery, a
completed cleanup or a runtime observation. The socket and container cleanup
helpers are on the
[callback tables page](xbox-command-callback-tables.md#the-same-fallback-in-connection-code).

### Receive, send and readiness

- The [receive helpers](../../manifests/xbox-network-message-root.json#/nativeTransportReceiveBoundary)
  do more than raw UDP. A path with a header compares 16-bit sequence fields with
  modular arithmetic, skips older records, buffers later records after an
  equality check and drains buffered records that match the next expected field.
  Separate control inputs retire a stored prefix or select stored records by an
  incoming field or range, and they set no retry interval. The expected field
  advances before the dispatch result is known. When transport type 7 reaches
  `0x82A123F8`, that dispatcher returns 1 with no type handler, which does not
  guarantee a true receive result. A true transport result does not show that
  world state was written. The type 101 retry parser reads two bytes before its
  length check. The exact payload limit and the proposed guard before that read
  are in the manifest.
- The [send path](../../manifests/xbox-network-message-root.json#/nativeTransportSendBoundary)
  reaches `NetDll_sendto` through a proved native shim. A nonzero result from the
  outer call also covers selected no-send branches and nonfatal errors, and the
  call can store a sampled value at connection `+0x88` without any receipt from
  the peer. The SDK's stopped-client length and drop branch also needs relay mode
  and a datagram handle that is still registered. The manifest keeps four things
  apart: the API result, the observer callback, the sample store, and the
  delivery and clock contracts that are not yet shown.
- The [readiness check](../../manifests/xbox-network-message-root.json#/nativeTransportReadinessBoundary)
  polls one socket's write set with a zero timeout. A zero result alone does not
  tell not ready from a selector failure, and neither is a receipt from the peer.
  Native mode and relay queue handling remain open.
- Full fragmentation, timer and retry limits, wrap and lifetime limits, the
  crossover between direct and relay paths and successful command delivery remain
  open. The SDK's directory retries and direct path replay window are separate
  layers. This partial audit adds no new reorder or retransmit implementation.

### Connections, members and hotjoin

- The [connection callback record](../../manifests/xbox-hotjoin-transfer-restore.json#/returningConnectionCallbackBoundary)
  shows the installed vector and the selected listener slots. The
  [connection index record](../../manifests/xbox-hotjoin-transfer-restore.json#/nativeConnectionIndexBoundary)
  follows selected raw callback paths into native index allocation, under
  conditions, and into disconnect forwarding. A native connection index is not a
  link between an XUID and a game player. Neither the transport sequence code
  nor this allocation path shows that a returning player is accepted or that
  recovery succeeded.
- The [member name selector](../../manifests/xbox-hotjoin-transfer-restore.json#/nativeMemberNameSelectionBoundary)
  extends that path through a parsed 64 byte string field, a case-insensitive
  comparison with the setup string and an index lookup that returns zero. A real
  vacancy needs the service and descriptor to stay valid. Validation, the link
  between a member and an XSession, and retirement remain active research. The
  parser hardening hook point is a proposal, not an observed malformed peer or
  runtime failure.
- The [XSession membership record](../../manifests/xbox-hotjoin-transfer-restore.json#/nativeXSessionMembershipBoundary)
  ties selected parsed member fields to the native member join wrapper before the
  later free index scan, and traces the member leave call before its guarded
  retirement. A name based candidate can be chosen earlier. The record and
  descriptor identity, the supported counts and the helper effects are
  conditions. Neither API call shows that a returning player or the world is
  accepted.
- The [member transfer retirement record](../../manifests/xbox-hotjoin-transfer-restore.json#/nativeMemberTransferRetirementBoundary)
  shows selected state 6 marking and reinsertion, and separate requests on the
  member collection. The paired normal operations restore the queue count under
  the recorded helper premises. The final notification and disposal belong to a
  later pump. The real callback and storage effects, and what stays valid after
  the tail, are open before a full cancel or retry can be accepted.
- The [member storage and failure record](../../manifests/xbox-hotjoin-transfer-restore.json#/nativeMemberStorageFailureBoundary)
  expands node acquisition, local disposal requests and the failure path. A usable
  node and a graceful failure need contracts for the caller and for what holds the node. The selected
  native exception request reaches a pinned SDK handler that asks for a debugger
  break and does not unwind guest code. Source tie, real exception behavior and a
  complete cancel remain qualified.
- The [selected local member producer](../../manifests/xbox-hotjoin-transfer-restore.json#/nativeLocalMemberIdentityBoundary)
  ties local address, sign-in and profile XUID requests to the user index and
  count fields of the selected local record. Its pending address loop has no local
  deadline or cancel check. Storing the record pointer and writing part of the
  address can come before the count of one is written, and neither shows a
  completed membership. The proposed title readiness stage, the logging hooks and
  the controls that were not run are research findings. The outer attempt and
  cleanup handling, and whether the player is accepted, are open.

### Startup, join and cleanup

- The [create and startup record](../../manifests/xbox-live-session-search-contract.json#/nativeCreateStartupBoundary)
  shows the earlier synchronous SDK relay startup wait and separates an
  initializer's success from a ready network. Host and join callers need exactly
  1 from the local producer, and they collapse every other producer result to 3.
  SDK cleanup waits behind startup, and Client Stop waits behind the active
  Associate operation. An earlier direct Stop does not prevent a later
  association by that startup. None of these cancels a whole attempt. Native
  reference pairing and who cancels the outer attempt remain active.
- The [selected cleanup helpers](../../manifests/xbox-system-link-qos-root.json#/nativeNetworkCleanupBoundary)
  separate the helper that cleans only WSA from the helper that cleans WSA and
  then XNet. The SDK's zero XNet cleanup result covers both a nonfinal reference
  release and the final network cleanup. These local calls show neither a
  balanced lifetime nor a leak. The destructor callbacks and the outer code that holds the objects remain
  open.
- The [failed startup diagnostic](../../manifests/xbox-system-link-qos-root.json#/nativeStartupDiagnosticBoundary)
  has a normal return path in the checked recompiled type 20 handler, if guest
  string access is valid and the helper and logger behave normally. The startup
  helper then returns the later WSA result. Visible debug output, XNet readiness,
  the original retail trap handling and complete reference pairing are separate
  contracts.
- The [session object retirement record](../../manifests/xbox-live-session-search-contract.json#/nativeSessionObjectRetirementBoundary)
  ties the QoS and settings objects to their selected destructors. QoS release
  comes before the serialized buffer is disposed, and a configured SDK release
  can also clear the active service's QoS mirror. A failed or skipped release
  still needs the correct final cleanup. Local field clears show neither a
  complete network retirement nor a clean second match. Allocator behavior, the
  registry service callback and outer reference pairing remain active.
- The [allocation return record](../../manifests/xbox-live-session-search-contract.json#/nativeSessionAllocationReturnBoundary)
  links explicit zero return branches to the recorded guard proposals for the
  session consumer. The concrete refill, heap and handler states, and a caller
  unwind that cleans up safely, remain active research. The source paths show no
  executed failure.
- The [failure policy record](../../manifests/xbox-live-session-search-contract.json#/nativeSessionFailurePolicyBoundary)
  keeps the create and migration result encodings apart. When a session create
  result has a low word other than 1, the selected join parent suffix requests
  retirement of a network object that is present. Early exits skip that suffix.
  The proposed local guards avoid publishing fresh partial objects. Callback,
  queue and socket handling and full reference compensation remain active.
- The [outer join rollback record](../../manifests/xbox-live-session-search-contract.json#/nativeOuterJoinRollbackBoundary)
  reaches service destruction for a matching registry value on its processed
  failure route. Destroying the session wrapper also needs a nonnull
  wrapper, still in place, with the selected vptr, and preparation can fail before one exists.
  Stable registry, key and object identities and normal helper returns are
  required. The early exits differ, and the mode 2 marker setter is separate from
  search cancellation or release. Reaching the destructor under these conditions
  does not show a final socket retirement or a clean retry.
- The [list and title registry record](../../manifests/xbox-network-message-root.json#/nativeConnectionListTitleRegistryBoundary)
  traces the child and final retirement requests, the builder modes, and the
  receiver output, socket field and registry writes that run only under
  conditions. Its proposed guard for node allocation needs failure to propagate
  and the acquired socket to be compensated. The real entry, the receiver and
  callback identity, and map growth and count effects remain open. No executed
  failure and no complete cancel fix were established.
- The [registry and callback continuation](../../manifests/xbox-network-message-root.json#/nativeSocketRegistryCallbackContinuationBoundary)
  records the normal vector and count writes and the lookup based teardown or
  child dispatch. One direct construction wrapper adds a forwarded target and
  another registry slot write. Same key receiver and child lifetimes, the real
  target effects and the entry and class are needed before complete callback or
  retry behavior can be claimed.
- The [connection acceptance record](../../manifests/xbox-network-message-root.json#/nativeSocketAdmissionConnectionBindingBoundary)
  separates a refusal by the predicate, a failure of local accept and an accepted
  continuation. It records that state is written before the callback copy, and
  the later registry and child requests. The real callback table targets, the
  receiver class and what finally holds the connection are open. Local acceptance is not a completed
  member or player acceptance and not a clean retry. The
  [constructed closed callback record](../../manifests/xbox-network-message-root.json#/nativeSocketAdmissionConnectionBindingBoundary/constructedClosedCallbackJoin)
  combines the accepted constructor and table identities with the callback copy
  rule to find a selected target and its guarded disconnect continuation. Current
  registry and record identities, and the retirement effects that follow from
  them, are needed before the connection and socket drain can be called safe.
- The [acceptance policy record](../../manifests/xbox-network-message-root.json#/nativeConnectionAdmissionPolicyBoundary)
  lists the descriptor, an optional session check, application and scalar equality
  checks. Its descriptor count comparison does not show a limit on the record's
  member count, and which code finally holds the application and record, and the
  writers of the scalar, stay open. These predicate stages are separate from a completed
  member or player acceptance.
- The [selected duplicate handle uses](../../manifests/xbox-network-message-root.json#/nativeDuplicateHandleUseBoundary)
  account for three raw direct wrapper sites found by the aligned word scan of
  initialized executable memory. Two request the current thread pseudo handle. The
  third reads a field filled by a thread creator, and that field has to stay valid
  across the wait in between. These inputs do not show a socket alias. Indirect
  use, thread teardown and teardown by the code that holds it and real occurrence are separate research.
- The [registry service reset](../../manifests/xbox-live-session-search-contract.json#/nativeSessionServiceResetBoundary)
  ties the destructor's two lookups and a constructed cross key path to a receiver
  class that applies only under a condition. Its selected callback resets a local
  list and vector. The nine copied head markers are not shown to be player or SDK
  event identities. Key replacement, other construction orders and a complete
  network retirement remain open.

### Accepting connections and sending

- The [application acceptance record](../../manifests/xbox-network-message-root.json#/nativeConnectionApplicationAdmissionBoundary)
  lists selected capacity, phase, name index and statistic checks, and one source
  of the scalar write. The current association, XUID and player identity, the
  origin of the input and recovery and teardown are separate links still open. No
  new repair is selected.
- The [scalar envelope record](../../manifests/xbox-network-message-root.json#/nativeAdmissionScalarEnvelopeBoundary)
  records selected construction, a codec for a five word payload and the routed
  and header writes. The original scalar seed, the receive dispatcher and who
  holds the whole capture remain active. A request or a counter advance is not
  delivery.
- The [send buffer record](../../manifests/xbox-network-message-root.json#/nativeAdmissionSendBufferBoundary)
  records local serialization, byte forwarding and cleanup, with a candidate guard
  for a null backing. Full direct and queued capture, and rolling back an attempt,
  remain active. A descriptor return and a free request do not show success.
- The [buffer position and growth record](../../manifests/xbox-network-message-root.json#/nativeAdmissionBufferPositionGrowthBoundary)
  records a relative advance, restoring the header range under a condition, and
  the growth and error requests. The failure policy, the exceptional continuation
  and complete transport capture remain active. No standalone repair and no
  runtime acceptance is inferred.
- The [direct connection send record](../../manifests/xbox-network-message-root.json#/nativeDirectConnectionSendCaptureBoundary)
  records the routes with a callback and with an empty callback, byte capture under
  a condition and the local status categories. The real callbacks, storage and
  failure policy remain active. A local 0 and acceptance by the lower send layer
  do not show that a peer captured or received the data.
- The [send capacity and fallback record](../../manifests/xbox-network-message-root.json#/nativeConnectionSendCapacityFallbackBoundary)
  records capacity and scalar effects, checks on the pending record count and
  selected control, state and closed callback requests. The actual typed storage
  and the complete policy for pressure and retirement remain active. No
  standalone repair is inferred.
- The [control, callback and expiry record](../../manifests/xbox-network-message-root.json#/nativeConnectionControlCallbackExpiryBoundary)
  records selected control framing and classification, an alternate callback and
  raw counter and phase requests. The clock units, the callback target and
  complete retirement remain active. A local return is not delivery or a player
  accepted.
- The [send phase and sample record](../../manifests/xbox-network-message-root.json#/nativeConnectionSendPhaseSampleBoundary)
  records selected periodic, retry and pending reply requests, the first sample
  and the slot traversal. Counter units, the outer cadence, the exact header
  update effects and the real typed lifetimes remain active. Local results do not
  show delivery.

### Mode entry, identity and voice

- The [dynamic export census](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeDynamicExportBoundary)
  accounts for eight direct lookup sites that use the pinned SDK's startup
  extension and instrumentation mappings. Indirect and tail paths and other
  platform versions are outside that negative. No service or startup result at
  run time follows.
- The [statistics request consumers](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeStatsConsumerBoundary)
  and the [voice create status record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeVoiceStatusBoundary)
  tie native API return checks to the pinned SDK functions. They separate
  unsupported results from consumed output. They do not show a statistics backend,
  a voice transport, audible output or a working online feature.
- The [identity, notification and voice record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentityNotificationVoiceConsumerBoundary)
  connects selected local profile outputs, completion polls and notification
  callbacks to the native field and return consumers. A raw submission stub leaves
  a pointer shaped register for a signed native check, which is not a receipt.
  The real entry, the listener and object generations, the helpers downstream and
  the voice backend remain open.
- The [notification worker and privilege entry record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentityWorkerPrivilegeEntryBoundary)
  maps the selected poll and wrapper callers with their timer, status, output and
  terminal requests. SDK clock conversion and the separate limits on callback and
  cancellation analysis do not show an observed cadence or a finished shutdown.
  The real signal and wait, the listener and object writes and the policy helpers
  downstream remain open.
- The [signal, wait and listener retirement record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentitySignalWaitRetirementBoundary)
  connects selected constructor writes, local stop writes and cleanup requests to
  SDK event and listener behavior. An SDK listener Restore path that applies only
  under a condition can replay a nonempty queue without signaling its event.
  Whether native code reaches SDK restore, whether the worker is waited for until it finishes, and which code finally
  holds it, remain open.
- The [timeout, startup and heap routing record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentityTimeoutStartupHeapBoundary)
  resolves selected timeout, clear event and startup register paths, and the
  heap delegate branch. The later entry and heap record classifies the
  stored pointer as runtime function metadata. The real feature callers, which code currently holds it and a successful shutdown remain open.
- The [entry, method slot and heap lifetime record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentityEntryHeapLifetimeBoundary)
  resolves selected adapter arguments, retain and release slots, and the heap and
  free checks. The SDK's VM free entry that is reached has no guard for a null
  heap lookup. A proposed guard with limited scope keeps its existing error and
  output policy. Native occurrence, allocation initialization, which code finally holds the heap and
  a successful shutdown remain open.
- The [constructed component setup record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentityConstructedSetupBoundary)
  ties a selected parent, factory and table path to the setup request that uses a
  worker. It keeps the conventions for zero status, Boolean and pointer returns,
  the guarded slot 0 request and the field clear after a normal return. The
  current registry and receiver identity, cleanup of acquired resources, the real
  use upstream and a safe retry remain open.
- The [component lifecycle and service mode record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeIdentityComponentLifecycleBoundary)
  maps selected registered service routes to child initialization and component
  release requests. The routes have different local rollback checks. Allocation
  guards, the policy for required children and complete worker retirement remain
  open. The selected descriptor fills are established under their stack and span
  premises.
- The [manager host and service dispatch record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeHostMenuServiceDispatchBoundary)
  separates mode 2 host preparation and search cancel requests from registered
  service setup. Selected callers keep raw results across narrower branch tests
  and cleanup requests. Receiver generations, whether cancellation completes and
  the order within one attempt are separate questions about which code holds what, and they stay open.
- The [component member query record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeComponentMemberQueryBoundary)
  follows the separate manager callback through the roster lookup and selected
  local or remote state queries. The remote path refreshes stored state and calls
  child callbacks. Its result does not show that a player is accepted or that data
  was delivered. The clock, which code holds the child and the writer, and complete
  retirement remain open.
- The [component query presentation record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeComponentQueryPresentationBoundary)
  maps five query callers and the selected presentation requests, whose metadata
  supports audio and talk indicator intent. One caller returns a three state code
  whose consumer downstream is open. In the selected matching class, a row refresh
  uses its comparison word where the builder uses the row key. That gives a
  candidate correction in the title. Complete cache writes, sink behavior and the
  which code holds the current instance remain open.
- The [presentation adapter and storage record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeQueryPresentationEffectsBoundary)
  separates the readiness of the nested object, method result words, queue erase
  requests and row storage writes. A formatter's raw return does not in general
  show that a call completed. Insertion copies the row fields. Rotation, callbacks
  and the comparison cache writer are separate contracts.
- The [pre-build and row movement record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativePresentationPrebuildRotationBoundary)
  ties selected field update requests to a three word rotation that runs only
  under conditions. The pre-build body has no direct row reset, and its helpers
  and callbacks keep their own effects. Moving a cached word with its row does not
  publish fresh query state and does not show a complete rebuild.
- The [presentation collection lookup record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativePresentationCollectionLookupBoundary)
  identifies normal writes of candidate and sentinel outputs, in place key folding
  and temporary reset requests. Bucket table initialization, which code really holds the
  map, key and node, and completed release remain distinct from a returned output
  cell or collection pointer.
- The [hash initialization record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativePresentationHashInitializationBoundary)
  ties the global table writer to a native startup dispatch that runs only under
  conditions. Its expected table and seed writes and the caller status are distinct
  from a completed initialization in a loaded instance. Earlier callbacks, the
  real startup path and later table generations are separate requirements.
- The [startup status continuation record](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeStartupStatusContinuationBoundary)
  covers the selected failure that applies under a condition and a scalar
  overwrite, and records the SDK's patch before entry cache source order. The
  real loaded instance and the response to the failure are still open. No SDK
  blocker and no runtime fix is claimed.
- The [selected guest refusal predicate](../../manifests/xbox-live-mode-entry-invite-contract.json#/nativeGuestRefusalBoundary)
  adapts the sign-in info status before it tests one output bit. Its true branch
  requests a refusal message and the sign-in UI, while the pinned SDK leaves the
  tested bit clear. The guest profile policy, the identity of the caller and the
  action, and the display and completion behavior remain active research.

## Evidence sources

- [Xbox network-message root](../../manifests/xbox-network-message-root.json)
- [Xbox turn label block](../../manifests/xbox-turn-label-block.json)
- [Native human turn completion](../../manifests/native-human-turn-completion.json)
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Rush-cost producer](../../manifests/rush-cost-producer.json)
- [Unit-movement lifecycle](../../manifests/unit-movement-lifecycle.json)
- [Great General attachment
  lifecycle](../../manifests/great-general-attachment-lifecycle.json)
- [Game calendar state](../../manifests/game-calendar-state.json)
- [Catalog contract](../catalogs.md)
