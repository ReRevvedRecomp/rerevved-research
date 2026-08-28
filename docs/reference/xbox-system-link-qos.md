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
does not prove that no XGI path exists: wrappers, other constant formation,
indirect dispatch, and other messages remain possible.

The next static gate is the first bounded consumer of completed per-entry
records. Until that gate closes, their layout and payload meaning, the visible
Refresh relation, advertisement, discovery, host/client direction, delivery,
matchmaking, transport, relay, and Internet play remain unresolved.

See `manifests/xbox-system-link-qos-root.json` for evidence locators and guards.
