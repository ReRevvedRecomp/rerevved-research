# Xbox System Link QoS boundary

Static calls and controlled menu traces are separate evidence, neither a
complete System Link implementation nor an online-play guide. Unless explicitly
bound, objects, fields, slots, literals and helpers remain neutral: no class,
visible action, resource-loading, session, advertisement/discovery, transport,
delivery, ordering or synchronization semantics follow from a call tuple.
Bounded negatives do not exclude indirect, asynchronous, unlogged or unmodeled
paths.

All traces below used default-off observers; exact scopes and remaining limits
are stated with each result.

## Lookup, result gating, and cleanup

Version 1.3 imports consecutive `NetDll_XNetQosListen`, `NetDll_XNetQosLookup`,
`NetDll_XNetQosRelease`. Lookup `0x82E927C4` has one modeled call, `0x827F1144`
in `0x827F10F0`: inserts caller 1, forwards eight register/four stack arguments
and returns unchanged. Sole producer `0x82C99628` builds three arrays from
`0x5C` records at `+0x08`/`+0x00`/`+0x2C`; passes count, arrays, three zeros, 8,
three zeros and result-slot address. Success means return zero.

`0x82C9D338` tests nonnull result `+0x04`: zero advances state 2->3, nonzero
retains 2; null bypasses. Later records instead come from enclosing `+0x24`
buffer/count. Nonnull downstream object and zero local byte permit one callback
per index plus final callback, without other QoS-body reads. Before lookup,
state copies that collection to lookup `+0x04`, zeros `+0x98C`. Zero count
returns without import, retaining null; downstream bypass can still continue.
Lookup alone cannot create a missing collection entry.

### Collection request and completion

`0x82C9CF70` first calls `0x82A1F3F0` without buffer: size 1334, return 122, no
message. It allocates exactly that count through `0x82D3DBA0`; nonnull return
goes to `+0x24`, then second call supplies buffer/completion `+0x28`. Zero or
997 return sets `+0x1C` to one.

Exact helper `0x82A1F3F0` zeroes the first two buffer words and calls imported
`XMsgStartIORequest` with literal caller value 251, message `0x000B001B`, the
completion pointer, and a 20-byte request record:

| Offset | Record field |
| --- | --- |
| `+0x00` | 32-bit second argument |
| `+0x04` | 64-bit word |
| `+0x0C` | Buffer size |
| `+0x10` | Buffer pointer |

Exact prerequisite helper `0x82A1E8D0` issues imported `XMsgInProcessCall` with
caller value 252 and message `0x00058023` as a prerequisite. Xbox static
evidence does not supply semantic names for either message, the 64-bit word, or
the buffer record type.

`0x82C99728` releases nonnull result through `0x827F1150`/
`NetDll_XNetQosRelease`. Initial slot points inside the object; lookup
replacement, release treatment, allocator and completed-entry layout remain
unknown.

## Menu labels and bounded negative searches

UI `0x82E52068` resolves `System Link`/Player Match/Ranked Match without local
session/message/socket/search calls; `Refresh`/`Create Game` have no modeled
references. Direct imported `XMsgStartIORequestEx`, `XMsgStartIORequest`,
`XMsgInProcessCall` searches found no producers for
`0x000B0016`/`0x000B001C`/`0x000B0065`. They also miss the independently
corroborated truncated `0x000B001B` body, so exclude no general XGI path.

Controlled Refresh probe for caller 251/`0x000B001B`/length 20 captured no
matching request, completion or buffer-write extent. Movie
`GFX_GameSelector.gfx` and guest share `OnPressY`/`OnPressX`; each has one
parameter reference in `0x82DECB20`, whose three bounded callees handle generic
UI/unit commands, not these dispatches. Resource string `0x8211FFB0` has no
modeled reference, tested split-address use or aligned initialized pointer:
naming is only a lead.

Canonical-Boolean-enabled entry probe `0x82DECB20` logged nothing on controlled
Y press; normal exit captured no command/receiver. Other contexts remain
possible. Buffer layout, Refresh ownership, host/client direction, relay and
Internet play remain unresolved alongside the page-wide networking limits.

## Movie command producers and callback targets

Exact game-selector AVM1 supplies a narrower producer. It compares
`Key.getCode()` with integer 45 and, on equality, executes `GetURL2` with URL
`FSCommand:OnPressY` and numeric argument zero. The same action block compares
the key code with integer 42 and, on equality, executes `GetURL2` with URL
`FSCommand:OnPressX` and numeric argument zero.

The guest image defines exact scheme string `FSCommand:` at `0x8213E624`. Guest
code associated with generated entry `0x82206350` materializes that address,
applies an exact 10-byte comparison through `0x827F43F0`, and advances the
matched input by 10.

Its first path reaches directly decoded receiver-vtable slot `+0x04` callback
site `0x8220A634`; exact raw words and narrow generated corroboration give the
second path a matching candidate at `0x8220B4C0`. Ghidra models only the entry
fragment of the larger generated function. This establishes two neutral
movie-side command producers and a native callback boundary.

It does not map either key code to a visible label, assign a Create Game
semantic, or identify the concrete receiver, dynamic target, resource-loading
path, or networking behavior.

One runtime trace, disabled by default, at those two exact callback sites
captured the first exact NUL-terminated `OnPressY` once. The observed path was
callsite `0x8220B4C0`, receiver `0x509201FC`, readable receiver leading word
`0x82162F34` (`receiver_mapped=true`), and dynamic target `0x82C7CBE0`; the
process then exited normally with code zero.

This establishes one neutral runtime receiver and target tuple for the
controlled action. It does not identify the receiver class, visible action
owner, resource-loading path, platform message, or networking behavior, and it
does not exclude the other callback site in another context.

Read-only static analysis confirms that observed target `0x82C7CBE0` is an exact
modeled function entry and has one data reference, from `0x82162F38`. That
address is exactly slot `+0x04` of the observed receiver vtable base
`0x82162F34`.

The configured Ghidra body truncates after its entry save thunk; narrow
generated-code corroboration for the exact target shows a neutral two-stage
virtual forwarder. It ignores the original callback receiver, calls slot `+0x98`
on the callback's second-argument object, then calls slot `+0x10` on the
returned object with the post-prefix command and neutral fourth argument.

This does not identify either object's class, either virtual method's semantics,
or the visible action owner.

The observed vtable base itself has zero modeled direct references. A separate
bounded read-only search found zero modeled functions that construct exact value
`0x82162F34` through a `lis` plus `addi` or `ori` pair in the same basic block
within an eight-instruction lookahead; the result was not truncated.

This closes only that constant-construction form and does not prove that the
vtable has no constructor, indirect producer, or runtime store.

A final bounded read-only search found zero aligned initialized-memory words
equal to exact vtable base `0x82162F34`. Together, zero modeled references, zero
tested split-constant constructions, and zero initialized pointer placements
exhaust the supported direct static reference forms for this seed.

They do not exclude a derived value, copied pointer, relocation not represented
by those forms, or runtime production.

### Forwarded command path

A separate trace, disabled by default, observed the two exact virtual calls
inside target `0x82C7CBE0` for the first exact `OnPressY` in one process. The
first virtual target was `0x82226AA0`; its returned-object pointer was
`0x514BFB90`; and the second virtual target was `0x82E819E0`.

The trace produced exactly one matching line and the process exited normally
with code zero. These values identify one neutral paired runtime path only. They
do not identify either object's class, either virtual method's semantics,
visible action ownership, resource loading, a platform message, networking
behavior, delivery, or ordering.

Bounded static identification resolves both runtime targets as exact modeled
function entries. Target `0x82226AA0` is a one-word accessor that returns the
word at argument-object offset `+0xFC`; the runtime returned-object pointer is
the observed value of that accessor. Ghidra truncates target `0x82E819E0` at the
known save thunk.

Its exact generated body preserves the incoming object, command, and neutral
third argument, calls the already bounded generic FSCommand chain, then
conditionally dispatches through slot `+0x0C` of the object held at
incoming-object field `+0x430`, using pointers to two stack temporaries
populated by helper calls supplied with the command and neutral argument.

This does not name either object, field, or method and exposes no
platform-message or networking edge.

One trace, disabled by default, observed optional dispatch for the first exact
`OnPressY` in one process. The dispatch object was `0x511CECE0` and the slot
`+0x0C` dynamic target was `0x82D76350`. The trace produced exactly one matching
line and the process exited normally with code zero. This is one neutral object
and target tuple only.

It does not identify the object's class, the `+0x430` field, the virtual method,
visible action ownership, a platform message, networking, delivery, or ordering.

Bounded static identification resolves dynamic target `0x82D76350` as an exact
modeled function entry. Ghidra truncates its body at bad instruction data;
narrow exact-target generated corroboration shows five local command-string
comparisons, including the already established `OnPressY` and `OnPressX`
anchors.

The `OnPressY` branch compares an unsigned scalar delta involving
incoming-object field `+0x11C` with literal 500. When the delta is greater, it
updates that field, writes one to a second object's byte field `+0x11`, and
calls exact helper `0x82D6F5D8`. The helper remains unexpanded.

The exact local body contains no direct XGI import, Xbox message submission,
socket import, buffer serialization, checksum, or network-ordering edge. These
relations do not establish time units, debounce semantics, either object's
class, field meaning, a semantic method name, visible action ownership, platform
behavior, networking, delivery, or synchronization.

## Bounded action traces

One trace of a single instance, disabled by default, bracketed that exact
optional dispatch immediately before and after its original indirect call while
the existing SDK XGI and Stage 0 LAN debug schemas were enabled.

One System Link game-list Y press produced exactly one ordered marker pair on
the same thread, with no intervening log line, and the process exited normally
with code zero. Strictly between the markers there were zero matching existing
schema lines for XGI or XSession messages, direct-LAN bind or getname,
successful `sendto` or `recvfrom` counters, or QoS listener lifecycle events.

This is a bounded zero-edge result for those existing schemas only. It does not
exclude an unlogged API attempt, failed socket operation, helper, asynchronous
path outside the marker interval, platform behavior, networking, delivery, or
ordering.

### OnPressX dispatch

AVM1 key 42 -> `FSCommand:OnPressX`; native branch's byte-zero gate reaches
`0x82D765B8`. One-instance call/return bracket on System Link X press logged one
same-thread pair/no intervening line, target `0x82D6C340`, normal exit zero.
Same schemas yielded zero XGI/XSession, bind/getname, successful
`sendto`/`recvfrom` or QoS events. Create Game/session meaning and unlogged/
asynchronous paths remain unproved.

Exact five-instruction `0x82D6C340` loads vptr, places 11 in argument two, loads
`+0x1C`, tail-dispatches `0x82D6C350`. No direct XGI/message/socket/
serialization/checksum/ordering edge. Another one-instance probe armed solely
from outer X call logged target `0x82D704F0` once, normal exit zero, without
object/vtable/argument/literal/field/buffer/payload/platform data.

Complete `0x82D704F0` sets incoming `+0x0C` byte one, loads state `0x8314F2E4`,
conditionally stores arg2 to `+0x10`, clears `+0x40`/ `+0x41`. Null `+0x08`
returns; otherwise `+0x0C` tail at `0x82D7054C`. It also contains none of those
direct network edges. Tail target and all
object/field/action/session/advertisement/discovery/delivery semantics remain
open.

## Networking call inventories

Three evidence surfaces reproduced known XMsg/QoS state paths. Socket/bind/send/
receive/listen roots were generic wrappers with no supported backward link to
menu actions or multiplayer state. Types 46 through 55 reach object serializer,
routing/queue/dispatcher, not an exact session/discovery/socket/QoS/transport
site. Sole shared manifest address `0x822DF8A0` is return-zero stub. No seed
joins networking callsite to action/state; indirect/asynchronous bridges remain
open.

Unscoped `XMsgStartIORequestEx` lead `0x823442D0` calls at `0x82344330`: caller
250, `0x0007001A`, three incoming words/length 12. First word zero adds local
three-word record beginning `0x00080002`; otherwise null. Nonnegative return
calls `0x82812CA0` with zero. Both nonnegative ->zero; negative with masked high
`0x00070000` ->low16; otherwise 1627. Modeled callers `0x82344438`/`0x82344510`
were unexpanded. This neutral request/ mapping lacks action/state linkage, so is
not a supported System Link seed.

### QoS listener producers

Wrapper `0x827F10D0` inserts caller one before five title arguments to
`NetDll_XNetQosListen`:

| Producer/site | Arguments and effect |
| --- | --- |
| `0x82C99018` / `0x82C99048` | `+0x0C`, `+0x08`, `+0x04`*12, zero, operation 5; true iff wrapper zero |
| `0x82C99060` / `0x82C99094` | `+0x0C`, three zeros, operation 16; walks `+0x08`, conditionally routes element/base through `0x82D3D9F0`, writes first-word sentinel, clears `+0x08` |

Model has no callers, not proof of disuse. Operations/payload, host/client,
advertisement/discovery/transport and menu/state linkage remain unknown.

### Direct socket and XNet calls

These generated direct-call inventories have no supported backward link to menu
actions, multiplayer state or types 46 through 55. Arguments, handles, fields,
gates and helpers remain neutral. Indirect/table/asynchronous/unmodeled or other
API paths remain outside coverage; proximity `0x82C99xxx` proves no ownership.

| Surface | Counts and scope |
| --- | --- |
| `socket`, `bind`, `getsockname`, `sendto`, `recvfrom`, `select` | 29 calls in 20 functions: 13 address setup, 10 send, 6 receive/select. Buffer/address pointers and return tests mapped locally. |
| `XNetGetTitleXnAddr`, `XNetXnAddrToInAddr`, `XNetInAddrToXnAddr`, `XNetUnregisterInAddr` | Six calls. Two local-XNADDR functions each have one direct caller; three conversions/unregister have none. |
| Remaining XNet | Eight calls: one `XNetStartup`, one `XNetCleanup`, two `XNetDnsLookup`, two `XNetDnsRelease`, two `XNetRandom`. Startup wrapper four sites/three callers; cleanup four callers; DNS pairs four/zero callers; random functions one/two callers. Local version/record gates, setup/cleanup, result inspection/release and two eight-byte fills only. |

Enumerated direct XNet seeds are exhausted; broader linkage remains unresolved.

## Host flow and message identity

Each of the seven exact strings in the Host Error dialog has zero modeled
references in the version 1.3 image. This excludes the direct string-reference
route without identifying the error producer or tying the dialog to session
create outputs, QoS, sockets, discovery, transport, or the SDK's current
success-only session handlers.

A host-flow trace covering X, game type, and timer selection reached a lobby.

About 3.7 seconds after the exact OnPressX call returned, one thread recorded
binding to port 1000 on the selected address and reading the binding back, title
XNADDR acquisition, `XGISessionCreateImpl` with neutral flags `0x21`, two public
slots and zero private slots, QoS-listen flags `0x05` with 84 opaque bytes, and
one local-join dispatch.

It then recorded unimplemented XLIVEBASE message `0x0005800E`, followed about 50
ms later by an attempt to bind to port 26900 on the selected address and another
XNADDR acquisition. The unimplemented message was observed in a run that later
reached the lobby.

Normal leave was followed by records for session deletion, QoS with flags
`0x10`, and cleanup; cleanup reported zero counted direct-LAN packets and no
retained QoS bytes. No successful `sendto` or `recvfrom` diagnostic was
observed, without excluding unlogged or other I/O forms. A bounded direct-call
search found no nearby construction of message `0x0005800E`.

An independent exact seed then identified function `0x82A1F860`, which
constructs that message and calls imported `XMsgInProcessCall` at `0x82A1F890`.
It supplies a sparse 20-byte local record and returns the record word at `+0x10`
rather than the imported return directly.

A controlled one-process trace used a debug-only exact filter for caller 252 and
message `0x0005800E`. During the corrected host-setup flow, it recorded exactly
one matching call from guest callsite `0x82A1F890`; the title then reached the
lobby and completed normal leave, cleanup, and process exit. This links one
runtime event to the exact static callsite only.

The topic manifest records the exact pinned source locations and bounded title
dataflow. It closes `0x0005800E` as `XUserMuteListQuery` with a 16-byte input
record for the user index and remote XUID and a caller-owned four-byte BOOL
output. The guest wrapper ignores the imported dispatch result and returns its
initialized local `+0x10` word.

No accepted receiver evidence establishes a callee write through imported arg1
to that word, so zero is only the current modeled outcome and not a universal
return guarantee. This closes the message identity and input/output ABI only.
The pinned implementation is clean-room guidance, not retail behavior.

Mute-list state, validation policy, empty-list and BOOL write rules, completion
behavior, state ownership, and any voice, lobby, discovery, session, transport,
payload, or causation effect remain unproved.

## Evidence source

[Topic manifest](../../manifests/xbox-system-link-qos-root.json).
