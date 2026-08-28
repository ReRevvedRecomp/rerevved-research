# Xbox System Link QoS boundary

Version 1.3 imports `NetDll_XNetQosListen`, `NetDll_XNetQosLookup`, and
`NetDll_XNetQosRelease` as one consecutive Xbox networking group. The exact
lookup import at `0x82E927C4` has one modeled call reference, from
`0x827F1144` inside wrapper `0x827F10F0`.

The wrapper supplies literal caller value 1, forwards eight incoming register
arguments, forwards four additional stack arguments, and returns the import
result unchanged. This closes a caller-plus-twelve-argument import shape. The
meaning and layout of those arguments remain unresolved in Xbox guest evidence.

The visible English `System Link` label belongs to UI setup function
`0x82E52068`, which also resolves the Player Match and Ranked Match labels. It
does not call a session, message, socket, or search function locally. The
defined `Refresh` and `Create Game` strings have no modeled references.

Bounded direct-call searches found no producer for general XGI search messages
`0x000B0016`, `0x000B001C`, or `0x000B0065` through the title's imported
`XMsgStartIORequestEx`, `XMsgStartIORequest`, or `XMsgInProcessCall` forms. This
does not prove that no XGI path exists: wrappers, other constant formation,
indirect dispatch, and other messages remain possible.

The next static gate is the first exact caller or result consumer around
`0x827F10F0`. Until that gate closes, the QoS payload, lookup output records,
completion state, visible Refresh relation, advertisement, discovery,
host/client direction, delivery, matchmaking, transport, relay, and Internet
play remain unresolved.

See `manifests/xbox-system-link-qos-root.json` for evidence locators and guards.
