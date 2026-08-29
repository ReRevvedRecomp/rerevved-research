# Xbox System Link QoS boundary

Version 1.3 imports `NetDll_XNetQosListen`, `NetDll_XNetQosLookup`, and
`NetDll_XNetQosRelease` as one consecutive Xbox networking group. The exact
lookup import at `0x82E927C4` has one modeled call reference, from
`0x827F1144` inside wrapper `0x827F10F0`.

The wrapper supplies literal caller value 1, forwards eight incoming register
arguments, forwards four additional stack arguments, and returns the import
result unchanged. Its sole producer is `0x82C99628`. For each `0x5C`-byte input
record, that producer builds three parallel arrays selecting record offsets
`+0x08`, `+0x00`, and `+0x2C`. It passes the record count, those three arrays,
three zero values, literal 8, three more zero values, and the address of an
object-owned result-pointer slot.

The producer reports success only when lookup returns zero. Exact consumer
`0x82C9D338` reads the result pointer and branches on its word at offset
`+0x04`. A null result bypasses the branch. For a non-null result, a zero word
permits the enclosing state to advance from literal 2 to literal 3; a nonzero
word retains state 2. These remain neutral field and state roles.

The indexed records used immediately after that gate do not come from completed
QoS result entries in the exact local body. Function `0x82C9D338` reads a result
buffer pointer from enclosing-object field `+0x24`, reads its leading count, and
enters downstream virtual callbacks only when its downstream object field is
non-null. On the local byte-flag-zero branch, it invokes one callback per buffer
index and then a final callback. It reads no other QoS result-body field before
any of those calls.

Before calling producer `0x82C99628`, the state function copies that same
collection pointer into lookup-object field `+0x04` and zeroes lookup-object
result slot `+0x98C`. The producer reads the collection's leading count through
field `+0x04`. When that count is zero, it returns before issuing
`NetDll_XNetQosLookup`, leaving the result slot zero. The state function then
takes its null-result bypass and can continue into the separately guarded
downstream path. Implementing lookup alone therefore cannot create a missing
collection entry in this exact path.

Exact producer `0x82C9CF70` prepares that buffer through a fixed two-call
request pattern. Its first call to `0x82A1F3F0` supplies no buffer. The helper
writes required size 1334 and returns 122 without issuing a message. The
producer requests exactly that byte count from size-based allocator
`0x82D3DBA0`; on a non-null return it stores the pointer at field `+0x24` and
calls the helper again with the allocated buffer and field `+0x28` as a
completion pointer. The producer accepts return zero or 997 and then sets field
`+0x1C` to one.

Exact helper `0x82A1F3F0` zeroes the first two buffer words and calls imported
`XMsgStartIORequest` with literal caller value 251, message `0x000B001B`, the
completion pointer, and a 20-byte request record. That record contains the
32-bit second argument at `+0x00`, a 64-bit word at `+0x04`, the buffer size at
`+0x0C`, and the buffer pointer at `+0x10`. Exact prerequisite helper
`0x82A1E8D0` issues imported `XMsgInProcessCall` with caller value 252 and
message `0x00058023` as a prerequisite. Xbox static evidence does not supply
semantic names for either message, the 64-bit word, or the buffer record type.

The title also imports `NetDll_XNetQosRelease` through wrapper `0x827F1150`.
Exact cleanup function `0x82C99728` reads the same object-owned result slot and
passes its pointer to release when non-null. The slot is initialized to an
embedded object address before lookup, but static evidence does not establish
whether lookup replaces that pointer or how release treats it. It also does not
identify an allocator or the completed per-entry layout.

The visible English `System Link` label belongs to UI setup function
`0x82E52068`, which also resolves the Player Match and Ranked Match labels. It
does not call a session, message, socket, or search function locally. The
defined `Refresh` and `Create Game` strings have no modeled references.

Bounded direct-call searches found no producer for general XGI search messages
`0x000B0016`, `0x000B001C`, or `0x000B0065` through the title's imported
`XMsgStartIORequestEx`, `XMsgStartIORequest`, or `XMsgInProcessCall` forms. This
does not prove that no XGI path exists: exact generated corroboration now closes
the separate `0x000B001B` request above even though its Ghidra body is truncated
and the same modeled-reference search form misses that call.

A default-off probe for exact caller 251, request `0x000B001B`, and length 20
produced no matching trace during a controlled System Link game-list Refresh.
No request or completion state and no request-buffer write extent was captured.

The exact `GFX_GameSelector.gfx` resource and guest image contain matching
`OnPressY` and `OnPressX` strings. Each guest string has one parameter reference
in `0x82DECB20`; that function and its three bounded callees handle generic UI
and unit-stack commands without dispatching either command. The resource match
is search guidance, not proof of action ownership. The next evidence gate is the
exact guest-image `GFX_GameSelector` resource-name anchor and its bounded
reference set. The buffer record layout, visible Refresh relation,
advertisement, discovery source, host/client direction, delivery, matchmaking,
transport, relay, and Internet play remain unresolved.

See `manifests/xbox-system-link-qos-root.json` for evidence locators and guards.
