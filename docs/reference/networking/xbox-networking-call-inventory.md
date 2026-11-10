# Xbox networking call inventory

The version 1.3 title reaches the network through four kinds of call: Xbox
message calls (`XMsgStartIORequestEx`, `XMsgStartIORequest`,
`XMsgInProcessCall`) that carry XGI session requests and Live base messages,
QoS (quality of service) calls, socket calls and XNet calls. This page lists
each direct call found in the image, what the call passes and what is still
unknown. A replacement SDK has to answer these calls, so the argument shapes
matter more here than the names.

Nothing on this page ties a call to a visible menu action. The
[QoS page](xbox-system-link-qos.md) covers the traced menu path, the lookup
chain and the host setup order.

## How to read an XMsg call

The request that fills the game list buffer shows the pattern. Function
`0x82A1F3F0` calls the imported `XMsgStartIORequest` thunk (`0x82E926F4`) with:

| Argument | Value |
| --- | --- |
| Caller value | 251 |
| Message | `0x000B001B` |
| Request pointer and length | A 20-byte record, length 20 |
| Completion pointer | Supplied by the caller, `+0x28` of the session object |

The 20-byte record holds the function's second argument at `+0x00`, a 64-bit
word at `+0x04`, the buffer size at `+0x0C` and the buffer pointer at `+0x10`.
When the size is below 1334 or the buffer pointer is null, the function writes
1334 to the size word and returns 122 without sending anything. With a
qualifying buffer it zeroes the first two buffer words and sends the message.
A nonnegative asynchronous submission returns 997 when the completion pointer
is not null.

Function `0x82A1E8D0` is the matching prerequisite. It builds temporary state,
takes temporary storage through `XamAlloc`, calls `XMsgInProcessCall` with
caller value 252 and message `0x00058023`, then frees the storage. It returns
zero on a nonnegative result and 1627 on its mapped failure path.

Static evidence names neither message and does not give the record layout of
the returned buffer. See [the QoS page](xbox-system-link-qos.md#collection-request-and-completion)
for how the caller uses the buffer.

## XMsg and XGI call forms

| Function | Call site | Import | Caller value | Message | Request |
| --- | --- | --- | --- | --- | --- |
| `0x82A1F3F0` | Truncated in Ghidra | `XMsgStartIORequest` `0x82E926F4` | 251 | `0x000B001B` | 20 bytes |
| `0x82A1E8D0` | Truncated in Ghidra | `XMsgInProcessCall` `0x82E92714` | 252 | `0x00058023` | Local state |
| `0x823442D0` | `0x82344330` | `XMsgStartIORequestEx` `0x82E926E4` | 250 | `0x0007001A` | 12 bytes |
| `0x82A1F860` | `0x82A1F890` | `XMsgInProcessCall` `0x82E92714` | 252 | `0x0005800E` | 20-byte local record |

The first two rows need the recompiled copy of the function, because Ghidra
truncates both bodies on bad instruction data. The last row is described under
[the host setup message](#host-setup-message-0x0005800e).

### Searches for general search messages

A search for the messages `0x000B0016`, `0x000B001C` and `0x000B0065` through
all three imports found no call
([search method](../../../manifests/xbox-system-link-qos-root.json#/generalSessionSearchNegative/method)).

The result does not exclude wrappers, other constant forms, indirect dispatch,
other XGI messages or discovery that is not XGI. The same modeled-reference
search form also reports no call for `0x000B001B`, because Ghidra truncates
`0x82A1F3F0`; the recompiled copy shows the call. The search form therefore
cannot prove that the producers of a message are complete. The session search
contract records the browse wrapper that does send `0x000B0016` (see
[browse](../../../manifests/xbox-live-session-search-contract.json#/browse/wrapper)).

### Request with no known menu link

Function `0x823442D0` calls `XMsgStartIORequestEx` at `0x82344330` with caller
value 250, message `0x0007001A`, zero, a pointer to three incoming words, length
12 and a second pointer. The second pointer is null unless the first incoming
word is zero. In that case it addresses three local words: `0x00080002`, zero
and zero.

After a nonnegative import result it calls `0x82812CA0` with zero. The return
mapping is:

| Result | Return |
| --- | --- |
| Both calls nonnegative | 0 |
| Negative, with masked high bits equal to `0x00070000` | The low 16 bits |
| Any other result | 1627 |

Ghidra reports two callers, `0x82344438` and `0x82344510`. Neither was
expanded. The values and request shape give no message meaning, and nothing
links the function to a menu action or multiplayer state, so it is not a
supported System Link seed.

### Networking seeds that were checked

A seed counts only when it shows both an exact networking call and a link to a
menu action or multiplayer state. A review of the XGI, XSession and XMsg roots,
the socket and QoS roots, and the message types 46 through 55 found none:

- The XGI and XMsg roots repeat the `0x00058023` and `0x000B001B` path through
  `0x82C9CF70` and `0x82C9D338`. Those calls are made on the session object and
  show no link to a menu action. The request at `0x823442D0` has no such link
  either.
- The `socket`, `bind`, `sendto`, `recvfrom` and QoS listen roots are generic wrappers
  with no link to a menu action or multiplayer state.
- Types 46 through 55 reach the object serializer, local routing, the queue
  drain and the dispatcher. They reach no session, discovery, socket, QoS or
  transport call. See [Xbox network messages](xbox-network-messages.md).

The review found no seed. The System Link and network message manifests share
19 addresses, including socket wrappers and allocation helpers. Shared
addresses do not establish that the two topics are separate or that they share
roles.

This covers the listed evidence only. Indirect, asynchronous, unsupported
constant and unmodeled paths remain open.

## QoS listen wrappers

Wrapper `0x827F10D0` inserts caller value 1 before five title arguments and
calls the import `NetDll_XNetQosListen` (`0x82E927B4`). It has two producers in
the title:

| Producer | Call site | Arguments and effect |
| --- | --- | --- |
| `0x82C99018` | `0x82C99048` | Object `+0x0C`, object `+0x08`, object word `+0x04` times 12, zero, operation 5. Returns true exactly when the wrapper returns zero. |
| `0x82C99060` | `0x82C99094` | Object `+0x0C`, three zeros, operation 16. Then walks the 12-byte records at `+0x08`, routes element-derived pointers and the collection base through `0x82D3D9F0` only when a local test allows it, writes a sentinel to each record's first word and clears `+0x08`. |

Ghidra fully decompiles `0x82C99018`. It truncates `0x82C99060` at the save
thunk, so that body comes from the recompiled copy.

Ghidra models no caller for either producer, which does not show they are
unused. The session wrapper reaches them through vtable slots: methods
`0x82C9C360` and `0x82C9BF98` call `0x82C99018` after building the records, and
`0x82C99060` runs from the destructor of the QoS object. The manifest links
carry those details ([listen records](../../../manifests/xbox-live-session-search-contract.json#/hostAdvertisement/qosListen),
[release](../../../manifests/xbox-live-session-search-contract.json#/nativeSessionObjectRetirementBoundary/qosRetirement)).

Operation values 5 and 16, the object fields and the record walk give no
payload meaning, host or client direction, discovery, transport or menu link.

## Socket calls

Six wrappers sit in front of the socket imports:

| Call | Wrapper | Import |
| --- | --- | --- |
| `socket` | `0x827F1230` | `0x82E92814` |
| `bind` | `0x827F12C8` | `0x82E92874` |
| `getsockname` | `0x827F12B0` | `0x82E92864` |
| `sendto` | `0x827F1368` | `0x82E928D4` |
| `recvfrom` | `0x827F1330` | `0x82E928B4` |
| `select` | `0x827F12F8` | `0x82E92894` |

The title makes 29 direct calls through them, in 20 functions. Function
`0x82A1A978` makes both address setup and send calls, so it appears twice in the
function lists.

| Group | Calls | Functions |
| --- | --- | --- |
| Address setup | 13: 8 `socket`, 3 `bind`, 2 `getsockname` | `0x82A17E70`, `0x82A07350`, `0x82A1A978`, `0x82838018`, `0x82A1A340`, `0x82A09820`, `0x82A10B28` |
| Send | 10 `sendto` | `0x82A0C248`, `0x82A0C2B8`, `0x82A0B1F8`, `0x82A182A0`, `0x82A11350`, `0x82A07550`, `0x82A0A428`, `0x82A1A978` |
| Receive | 5 `recvfrom`, 1 `select` | `0x82A1D2A8`, `0x82A09C88`, `0x82A07D80`, `0x82A18838`, `0x82A119D0`, `0x82A075B8` |

The functions expose local handle storage, return tests and buffers. The send
calls use 16-byte address arguments. None has a supported link to a menu action, multiplayer state or the message types 46
through 55.

## XNet calls

| Call | Wrapper | Import |
| --- | --- | --- |
| `XNetGetTitleXnAddr` | `0x827F1160` | `0x82E927E4` |
| `XNetXnAddrToInAddr` | `0x827F1068` | `0x82E92764` |
| `XNetInAddrToXnAddr` | `0x827F1080` | `0x82E92774` |
| `XNetUnregisterInAddr` | `0x827F1098` | `0x82E92784` |
| `XNetStartup` | `0x827F1040` (import call at `0x827F1028`) | `0x82E92734` |
| `XNetCleanup` | `0x827F1050` | `0x82E92744` |
| `XNetRandom` | `0x827F1058` | `0x82E92754` |
| `XNetDnsLookup` | None recorded | `0x82E92794` |
| `XNetDnsRelease` | None recorded | `0x82E927A4` |

The 14 direct calls split as follows:

| Group | Calls | Functions and direct callers |
| --- | --- | --- |
| Local address | 2 | `0x82A08170` (caller `0x82A0A190`) and `0x82CB1610` (caller `0x82C99368`) |
| Conversion | 3 | `0x82A090B8`, `0x82C99490` and `0x82A09110`, none with a direct caller |
| Unregister | 1 | `0x82C99510`, no direct caller; it ignores the return |
| Startup | 1, reached through `0x827F0F88` and `0x827F1040`; the wrapper has 4 call sites | Callers `0x82837F00`, `0x82A0F460` and `0x82E476B0` |
| Cleanup | 1 | `0x82A0F4F8`, callers `0x82A0F1C0`, `0x82A10F10`, `0x82A09988` and `0x82A09F40` |
| DNS | 4: 2 lookups and 2 releases | `0x82A07968` (callers `0x82A0F1C0`, `0x82A0A278`, `0x82A074B0`, `0x82A1A340`) and `0x82838018` (no caller) |
| Random | 2 eight-byte fills | `0x82A0C598` (caller `0x82C9DA48`) and `0x82A09368` (callers `0x82A09768`, `0x82A09988`) |

Other manifests identify some of these functions:

- `0x82C99490` formats a host address as text with port 1000 through
  `XNetXnAddrToInAddr`, and `0x82E476B0` is the startup helper that the browse
  path requires ([transport](../../../manifests/xbox-live-mode-entry-invite-contract.json#/transport/address),
  [browse](../../../manifests/xbox-live-session-search-contract.json#/browse/gate)).
- `0x82CB1610` is the local member record producer that repeats
  `XNetGetTitleXnAddr` until the result is not zero
  ([local member identity](../../../manifests/xbox-hotjoin-transfer-restore.json#/nativeLocalMemberIdentityBoundary)).
- The GameSpy surface inventory names `0x82A09368`, `0x82A0C598`, `0x82A1A978`,
  `0x82A1A340`, `0x82A09820`, `0x82A0C2B8` and `0x82A07350` as parts of the
  Query and Reporting, server browsing and availability code
  ([components](../../../manifests/xbox-gamespy-surface-inventory.json#/components)).

The direct-call inventories alone show no link to a menu action. They also miss
indirect calls, table placement, asynchronous links and other networking
interfaces. The neighborhood `0x82C99xxx` is proximity only and shows nothing
about use.

## Host setup message 0x0005800E

Function `0x82A1F860` is a wrapper around `XMsgInProcessCall` at `0x82A1F890`
with caller value 252 and message `0x0005800E`. The message is
`XUserMuteListQuery`: the user index and a remote XUID go in, and a caller-supplied
four-byte BOOL comes back. The title calls it while it sets up a host game, and
the SDK sees it as an unimplemented XLIVEBASE message.

The wrapper builds a 20-byte local scratch area. The first 16 bytes are the
input record the import receives as argument 1:

| Offset | Content |
| --- | --- |
| `+0x00` | Low 32 bits of the wrapper's argument 1, the user index |
| `+0x04` to `+0x07` | Not written, padding |
| `+0x08` | The wrapper's 64-bit argument 2, the remote XUID |
| `+0x10` | A separate word, initialized to zero, outside the input record |

The import receives caller value 252, message `0x0005800E`, the pointer to this
record and the wrapper's argument 3. Argument 3 is the pointer to the
caller-supplied BOOL. In the direct caller `0x82CA1710`, instruction `0x82CA1850`
stores zero to stack word `+0x50`, instruction `0x82CA1864` calls `0x82A1F860`,
and instruction `0x82CA1884` loads the same word afterward.

After the call the wrapper returns its local `+0x10` word, not the import
result. That word is initialized to zero, and nothing in the wrapper writes it.
No receiver evidence shows a write to it through argument 1, so zero is the
current modeled outcome and not a guarantee of the return value. The 16-byte
input wording names a record span, not pointer alignment.

The direct constant search through the three XMsg imports misses this wrapper.
The call from guest callsite `0x82A1F890` with caller value 252 and message
`0x0005800E` has been observed at runtime
([request buffer](../../../manifests/xbox-system-link-qos-root.json#/requestBufferProducer)).

### Sources for the identity

| Source | Role |
| --- | --- |
| [Xenia Canary dispatch mapping](https://github.com/AdrianCassar/xenia-canary/blob/b5f6f6ed618210ecfbbcb228994418f734cdd850/src/xenia/kernel/xam/apps/xlivebase_app.cc#L230-L233) | Maps `0x0005800E` to `XUserMuteListQuery`. Clean-room implementation guidance, not retail authority. |
| [Xenia Canary declaration](https://github.com/AdrianCassar/xenia-canary/blob/b5f6f6ed618210ecfbbcb228994418f734cdd850/src/xenia/kernel/xnet.h#L790-L794) | Declares user index, remote XUID and a separate four-byte state field. It does not show that the title's `+0x10` word is that field. |
| [Source SDK header `ixboxsystem.h`](https://github.com/pmrowla/hl2sdk-csgo/blob/49e950f3eb820d88825f75e40f56b3e64790920a/public/ixboxsystem.h#L371-L375) | Independent Xbox 360 contract: user index, remote XUID and a caller-supplied BOOL output. |

The title code, the header and the pinned implementation together close the
message identity and the input and output layout, and nothing more. The pinned
implementation is clean-room guidance, not retail behavior.

## Addresses

| Item | Address |
| --- | --- |
| `XMsgStartIORequestEx`, `XMsgStartIORequest`, `XMsgInProcessCall` imports | `0x82E926E4`, `0x82E926F4`, `0x82E92714` |
| `NetDll_XNetQosListen`, `Lookup`, `Release` imports | `0x82E927B4`, `0x82E927C4`, `0x82E927D4` |
| Search request helper and prerequisite | `0x82A1F3F0`, `0x82A1E8D0` |
| Request with no known menu link | `0x823442D0` (call `0x82344330`) |
| QoS listen wrapper and producers | `0x827F10D0`; `0x82C99018`, `0x82C99060` |
| Host setup message wrapper and call | `0x82A1F860`, `0x82A1F890` |
| Direct caller of the host setup wrapper | `0x82CA1710` |

## Open questions

- Which menu action, if any, makes each call in the inventories.
- The meaning of messages `0x000B001B`, `0x00058023` and `0x0007001A`, and the
  record layout of the buffer returned for `0x000B001B`.
- Whether any other source gives the request or reply of `0x0005800E` beyond
  the identity and layout above: the mute list state, the validation rules, the
  BOOL write rules and any effect on voice, lobby, session or transport.
- Indirect, asynchronous and table-driven calls that the direct-call inventories
  cannot see.

## Evidence sources

- [Topic manifest](../../../manifests/xbox-system-link-qos-root.json): the
  [XMsg request](../../../manifests/xbox-system-link-qos-root.json#/requestBufferProducer),
  [general search negative](../../../manifests/xbox-system-link-qos-root.json#/generalSessionSearchNegative),
  [request with no menu link](../../../manifests/xbox-system-link-qos-root.json#/unscopedXMsgStartIORequestEx),
  [QoS listen producers](../../../manifests/xbox-system-link-qos-root.json#/qosListenProducers),
  [socket](../../../manifests/xbox-system-link-qos-root.json#/socketRootDiscovery),
  [XNet address](../../../manifests/xbox-system-link-qos-root.json#/xnetAddressDiscovery),
  [remaining XNet](../../../manifests/xbox-system-link-qos-root.json#/remainingXnetDiscovery)
  and [host message](../../../manifests/xbox-system-link-qos-root.json#/hostMessageProducer)
  records.
- [Xbox System Link QoS boundary](xbox-system-link-qos.md)
