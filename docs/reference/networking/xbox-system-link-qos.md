# Xbox System Link QoS boundary

Version 1.3 sends a request for a 1334-byte buffer, passes the buffer's records
to a QoS (quality of service) lookup and releases the result. This page follows
that chain and the host setup order seen when a game is hosted. Nothing here
shows which menu action starts the chain, and the page is neither a complete
System Link implementation nor an online play guide.

A call tuple shows addresses, values and shapes. It does not show what an
object, field, slot, literal or helper means, so none of them has a class,
visible action, session, discovery, transport, delivery, ordering or
synchronization meaning here. A search that finds nothing excludes only the
forms it tried. It leaves indirect, asynchronous, unlogged and unmodeled paths
open.

## The chain in one pass

The functions below belong to the session object that the title installs for
every mode other than 1 (table `0x82160450`; see the
[session search contract](../../../manifests/xbox-live-session-search-contract.json#/modeTwoTable)).
For a search by identifier, the title:

1. Runs the prerequisite request, message `0x00058023`.
2. Asks how large the request buffer must be (1334 bytes), allocates it and
   sends message `0x000B001B` with that buffer.
3. In state 1 of the state function `0x82C9D338`, copies the buffer pointer to
   the lookup object and calls the lookup producer `0x82C99628`, which passes
   the buffer's records to `NetDll_XNetQosLookup`.
4. Checks the result's word at `+0x04`. Zero moves the state from 2 to 3.
5. Releases the result through `NetDll_XNetQosRelease` when it is not null.

Static evidence names neither message and gives no layout for the records the
buffer holds.

## Lookup, result check and release

The title imports `NetDll_XNetQosListen`, `NetDll_XNetQosLookup` and
`NetDll_XNetQosRelease` as consecutive imports (`0x82E927B4`, `0x82E927C4`,
`0x82E927D4`). The listen wrapper and its producers are in the
[call inventory](xbox-networking-call-inventory.md#qos-listen-wrappers).

| Step | Function | What it does |
| --- | --- | --- |
| Lookup wrapper | `0x827F10F0`, call at `0x827F1144` | The one modeled call of import `0x82E927C4`. Inserts caller value 1, forwards 8 register arguments and 4 stack arguments, returns the result unchanged. |
| Producer | `0x82C99628`, call at `0x82C996F4` | The only caller of the wrapper. Builds three arrays from the `0x5C`-byte records, taking record offsets `+0x08`, `+0x00` and `+0x2C`. Passes the count, the three arrays, three zeros, 8, three zeros and the address of result slot `+0x98C`. Returns true exactly when the wrapper returns zero. |
| First consumer | `0x82C9D338`, lookup call at `0x82C9D3FC` | Reads the result slot at `0x82C9D414` and the result word `+0x04` at `0x82C9D424`. |
| Release | `0x82C99728`, tail call at `0x82C99744` | Passes a nonnull result slot to `0x827F1150`, which calls `NetDll_XNetQosRelease`. |

The producer's three arrays sit at object offsets `+0x0C`, `+0x32C` and
`+0x64C`. Before a lookup with a positive count, slot `+0x98C` is set to object
address `+0x96C`.

The result check in `0x82C9D338` works as follows:

- A null result slot skips the check.
- For a nonnull result, a zero word at `+0x04` moves the state from 2 to 3. A
  nonzero word keeps state 2.
- When the downstream object is not null and its byte flag is zero, the
  function calls one callback per index of the request buffer and then one
  final callback. It reads no other word of the QoS result before those calls.
- Before the lookup, it copies the request buffer pointer from enclosing
  object field `+0x24` to lookup object field `+0x04`, and zeroes `+0x98C`.
- When the buffer's count is zero, the producer returns without calling the
  import and the slot stays null. The state function then takes the null
  bypass and can still continue into the downstream path. A QoS lookup alone
  therefore cannot create a missing entry in the collection.

The check is a local test and does not show repeated polling. The meanings of
states 2 and 3 are not known. Where the lookup replaces the slot's
initial pointer, how release treats it, the allocator and the layout of a
completed entry remain unknown.

### Collection request and completion

The request buffer comes from `0x82C9CF70`. It first calls `0x82A1F3F0`
without a buffer: the call writes size 1334, returns 122 and sends no message.
It then allocates that many bytes through `0x82D3DBA0` and, when the allocation
is not null, stores the pointer at `+0x24` and calls `0x82A1F3F0` a second time
with the buffer and the completion pointer at `+0x28`. A return of zero or 997
sets field `+0x1C` to 1.

`0x82A1F3F0` zeroes the first two buffer words and calls the imported
`XMsgStartIORequest` with caller value 251, message `0x000B001B`, the
completion pointer and a 20-byte request record:

| Offset | Record field |
| --- | --- |
| `+0x00` | 32-bit second argument |
| `+0x04` | 64-bit word |
| `+0x0C` | Buffer size |
| `+0x10` | Buffer pointer |

The prerequisite helper `0x82A1E8D0` calls `XMsgInProcessCall` with caller
value 252 and message `0x00058023` first. Static evidence gives neither
message a name, nor the 64-bit word, nor the buffer record type. The
[call inventory](xbox-networking-call-inventory.md#how-to-read-an-xmsg-call)
shows both calls in full.

## System Link menu labels and searches that found nothing

Function `0x82E52068` resolves the four labels for match type, player match,
ranked match and System Link and passes them to UI `SetTitle` and `SetText`
calls. It makes no session, message, socket or search call. The refresh and
create-game strings have no modeled references, so the page cannot say which control
sends which request.

Searches through the three imported XMsg forms found no producer for messages
`0x000B0016`, `0x000B001C` or `0x000B0065`. The same search form also misses
the truncated `0x000B001B` body that other evidence confirms, so it excludes no
general XGI path. The [call inventory](xbox-networking-call-inventory.md#searches-for-general-search-messages)
lists the search forms.

One controlled System Link game list refresh did not send caller 251, message
`0x000B001B`, length 20. The probe captured no matching request, no completion
and no buffer write extent. This shows neither which function handles the refresh nor
that the request is absent on other paths.

## Game selector commands

The game list is a Scaleform movie that sends the script command for the Y
press for key code 45 and the script command for the X press for key code 42.
Neither route reaches a network call in the logged schemas, and neither press
is tied to the refresh or create-game action. [Xbox game selector commands](xbox-game-selector-commands.md) holds the
movie anchors, callback sites, observed targets and zero-edge results.

## Host setup flow

X on the game list opens game type and timer selection. Only completing those
choices attempts to host. In a controlled host setup that reached a lobby, the
logged calls came in this order:

| Order | Call |
| --- | --- |
| 1 | `bind` to port 1000 on the selected address, then a `getsockname` readback |
| 2 | Title XNADDR acquisition |
| 3 | `XGISessionCreateImpl` with flags `0x21`, 2 public slots and 0 private slots |
| 4 | QoS listen with flags `0x05` and 84 opaque bytes |
| 5 | One `XGISessionJoinLocal` call |
| 6 | Unimplemented XLIVEBASE message `0x0005800E` |
| 7 | A `bind` attempt on port 26900, then another XNADDR acquisition |

The title reached the lobby with message `0x0005800E` unimplemented. The
message is `XUserMuteListQuery`; the
[call inventory](xbox-networking-call-inventory.md#host-setup-message-0x0005800e)
gives its layout and its call site `0x82A1F890`. The order of the calls does
not show cause.

Leaving the lobby normally was followed by a session delete, QoS listen with
flags `0x10` and cleanup. Cleanup reported zero counted direct LAN packets,
QoS disabled and no QoS bytes kept. These records do not show that the
title's own session was torn down. No successful `sendto` or `recvfrom`
diagnostic appeared, which leaves unlogged or other I/O forms open.

The title can show a host error dialog after a host attempt. Each of its seven
exact strings, at `0x8213A554`, `0x8213A777`, `0x8213A80C`,
`0x8213A824`, `0x8213A84C`, `0x8213AAE0` and `0x8213AB77`, has zero modeled
references in the version 1.3 image. That rules out only the direct string
route. It does not identify what produces the error or tie the dialog to the
session create outputs, QoS, sockets, discovery, transport or the SDK's
success-only session handlers.

## Open questions

- The record layout of the 1334-byte buffer and the meaning of messages
  `0x000B001B` and `0x00058023`.
- Which function handles the refresh, and whether the refresh reaches `0x000B001B` on
  another path.
- Host or client direction, relay and Internet play.
- The meanings of the QoS result word `+0x04` and of states 2 and 3.

## Evidence source

- [Topic manifest](../../../manifests/xbox-system-link-qos-root.json), mainly the
  [lookup](../../../manifests/xbox-system-link-qos-root.json#/qosLookup),
  [result](../../../manifests/xbox-system-link-qos-root.json#/qosResultLifecycle),
  [collection](../../../manifests/xbox-system-link-qos-root.json#/downstreamCollection),
  [request buffer](../../../manifests/xbox-system-link-qos-root.json#/requestBufferProducer),
  [host setup](../../../manifests/xbox-system-link-qos-root.json#/loggedHostSetupObservation)
  and [host error](../../../manifests/xbox-system-link-qos-root.json#/hostErrorStringEvidence)
  records.
- [Xbox networking call inventory](xbox-networking-call-inventory.md)
- [Xbox game selector commands](xbox-game-selector-commands.md)
