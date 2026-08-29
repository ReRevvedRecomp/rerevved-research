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
and unit-stack commands without dispatching either command. Exact guest string
`GFX_GameSelector.gfx` is defined at `0x8211FFB0`, but it has no modeled
reference, bounded split-address code use, or aligned initialized-memory pointer
placement. The resource agreement remains search guidance, not proof of action
ownership or loading. A default-off title probe at exact function entry
`0x82DECB20` produced no matching line during a controlled System Link game-list
Y press with the canonical Boolean presence flag enabled. The process exited
normally, but the run captured no command or receiver identity and does not
identify the visible action's producer or prove that another runtime path cannot
reach the function. The buffer record layout, visible Refresh relation,
advertisement, discovery source, host/client direction, delivery, matchmaking,
transport, relay, and Internet play remain unresolved.

Exact game-selector AVM1 supplies a narrower producer. It compares
`Key.getCode()` with integer 45 and, on equality, executes `GetURL2` with URL
`FSCommand:OnPressY` and numeric argument zero. The same action block compares
the key code with integer 42 and, on equality, executes `GetURL2` with URL
`FSCommand:OnPressX` and numeric argument zero. The guest image defines exact
scheme string `FSCommand:` at `0x8213E624`. Guest code associated with generated
entry `0x82206350` materializes that address, applies an exact 10-byte comparison
through `0x827F43F0`, and advances the matched input by 10. Its first path
reaches directly decoded receiver-vtable slot `+0x04` callback site
`0x8220A634`; exact raw words and narrow generated corroboration give the second
path a matching candidate at `0x8220B4C0`. Ghidra models only the entry fragment
of the larger generated function. This establishes two neutral movie-side
command producers and a native callback boundary. It does not map either key
code to a visible label, assign a Create Game semantic, or identify the concrete
receiver, dynamic target, resource-loading path, or networking behavior.

One default-off runtime trace at those two exact callback sites captured the
first exact NUL-terminated `OnPressY` once. The observed path was callsite
`0x8220B4C0`, receiver `0x509201FC`, readable receiver leading word
`0x82162F34` (`receiver_mapped=true`), and dynamic target `0x82C7CBE0`; the
process then exited normally with code zero.
This establishes one neutral runtime receiver and target tuple for the
controlled action. It does not identify the receiver class, visible action
owner, resource-loading path, platform message, or networking behavior, and it
does not exclude the other callback site in another context.

Read-only static analysis confirms that observed target `0x82C7CBE0` is an
exact modeled function entry and has one data reference, from `0x82162F38`.
That address is exactly slot `+0x04` of the observed receiver vtable base
`0x82162F34`. The configured Ghidra body truncates after its entry save thunk;
narrow generated-code corroboration for the exact target shows a neutral
two-stage virtual forwarder. It ignores the original callback receiver, calls
slot `+0x98` on the callback's second-argument object, then calls slot `+0x10`
on the returned object with the post-prefix command and neutral fourth
argument. This does not identify either object's class, either virtual method's
semantics, or the visible action owner.

The observed vtable base itself has zero modeled direct references. A separate
bounded read-only search found zero modeled functions that construct exact
value `0x82162F34` through a same-basic-block `lis` plus `addi` or `ori` pair
within an eight-instruction lookahead; the result was not truncated. This
closes only that constant-construction form and does not prove that the vtable
has no constructor, indirect producer, or runtime store.

A final bounded read-only search found zero aligned initialized-memory words
equal to exact vtable base `0x82162F34`. Together, zero modeled references,
zero tested split-constant constructions, and zero initialized pointer
placements exhaust the supported direct static reference forms for this seed.
They do not exclude a derived value, copied pointer, relocation not represented
by those forms, or runtime production.

A separate default-off trace observed the two exact virtual calls inside target
`0x82C7CBE0` for the first exact `OnPressY` in one process. The first virtual
target was `0x82226AA0`; its returned-object pointer was `0x514BFB90`; and the
second virtual target was `0x82E819E0`. The trace produced exactly one matching
line and the process exited normally with code zero. These values identify one
neutral paired runtime path only. They do not identify either object's class,
either virtual method's semantics, visible action ownership, resource loading,
a platform message, networking behavior, delivery, or ordering.

Bounded static identification resolves both runtime targets as exact modeled
function entries. Target `0x82226AA0` is a one-word accessor that returns the
word at argument-object offset `+0xFC`; the runtime returned-object pointer is
the observed value of that accessor. Ghidra truncates target `0x82E819E0` at
the known save thunk. Its exact generated body preserves the incoming object,
command, and neutral third argument, calls the already bounded generic
FSCommand chain, then conditionally dispatches through slot `+0x0C` of the
object held at incoming-object field `+0x430`, using pointers to two stack
temporaries populated by helper calls supplied with the command and neutral
argument. This does not name either object, field, or method and exposes no
platform-message or networking edge.

One default-off trace observed optional dispatch for the first exact `OnPressY`
in one process. The dispatch object was `0x511CECE0` and the slot `+0x0C`
dynamic target was `0x82D76350`. The trace produced exactly one matching line
and the process exited normally with code zero. This is one neutral object and
target tuple only. It does not identify the object's class, the `+0x430` field,
the virtual method, visible action ownership, a platform message, networking,
delivery, or ordering.

Bounded static identification resolves dynamic target `0x82D76350` as an exact
modeled function entry. Ghidra truncates its body at bad instruction data;
narrow exact-target generated corroboration shows five local command-string
comparisons, including the already established `OnPressY` and `OnPressX`
anchors. The `OnPressY` branch compares an unsigned scalar delta involving
incoming-object field `+0x11C` with literal 500. When the delta is greater, it
updates that field, writes one to a second object's byte field `+0x11`, and
calls exact helper `0x82D6F5D8`. The helper remains unexpanded. The exact local
body contains no direct XGI import, Xbox message submission, socket import,
buffer serialization, checksum, or network-ordering edge. These relations do
not establish time units, debounce semantics, either object's class, field
meaning, a semantic method name, visible action ownership, platform behavior,
networking, delivery, or synchronization.

One default-off single-instance trace bracketed that
exact optional dispatch immediately before and after its original indirect
call while the existing SDK XGI and Stage 0 LAN debug schemas were enabled.
One System Link game-list Y press produced exactly one ordered marker pair on
the same thread, with no intervening log line, and the process exited normally
with code zero. Strictly between the markers there were zero matching existing
schema lines for XGI or XSession messages, direct-LAN bind or getname,
successful `sendto` or `recvfrom` counters, or QoS listener lifecycle events.
This is a bounded zero-edge result for those existing schemas only. It does not
exclude an unlogged API attempt, failed socket operation, helper, asynchronous
path outside the marker interval, platform behavior, networking, delivery, or
ordering.

Exact game-selector AVM1 separately maps key-code value 42 to
`FSCommand:OnPressX`. In the same exact native command body, that branch reaches
an indirect call at `0x82D765B8` after a local byte-zero gate. One
default-off single-instance trace bracketed only that call
and its return site. One System Link game-list X press produced exactly one
ordered same-thread marker pair; no log line intervened. The neutral
dynamic target was `0x82D6C340`, and the process exited normally with code
zero. Strictly between the markers there were zero matching existing-schema
lines for XGI or XSession messages, direct-LAN bind or getname, successful
`sendto` or `recvfrom` counters, or QoS listener lifecycle events. This
establishes one neutral observed OnPressX call target and another bounded
zero-edge result for the enumerated schemas only. It does not map the event to
the visible Create Game label or establish session creation, advertisement,
discovery, platform behavior, networking, delivery, or ordering. It also does
not exclude an unlogged or asynchronous path.

Bounded static identification resolves observed target `0x82D6C340` as an
exact modeled function entry. Its complete five-instruction body loads the
incoming object's leading vtable pointer, places literal 11 in the second
argument register, loads vtable slot `+0x1C`, and tail-dispatches through that
target at `0x82D6C350`. The local body contains no direct XGI import, Xbox
message submission, socket import, buffer serialization, checksum, or
network-ordering edge. This establishes only a neutral tail-dispatch shape. It
does not identify the object class, slot or literal semantics, dynamic target,
visible action owner, session behavior, advertisement, discovery, delivery, or
ordering.

One default-off single-instance trace then armed only from
the exact outer OnPressX call and observed the tail-dispatch site once. The
accepted line recorded neutral dynamic target
`0x82D704F0`; the process exited normally with code zero. No object, vtable,
argument, literal, field, buffer, payload, or platform event was recorded. This
establishes one neutral runtime target tuple only. It does not identify the
target's method semantics, object ownership, visible action, session creation,
advertisement, discovery, networking, delivery, or ordering.

See `manifests/xbox-system-link-qos-root.json` for evidence locators and guards.
