# Xbox game selector commands

The System Link game list is a Scaleform movie, `GFX_GameSelector.gfx`. When the
player presses Y or X on it, the movie does not call game code directly. It
asks the host for a command named `OnPressY` or `OnPressX`, and native code
then routes that command text through a chain of virtual calls. This page
records that route for version 1.3. It stops where the code stops saying
anything specific: no function on the route is tied to a visible Refresh or
Create Game action, to a session, or to any network call.

## What a Y press does

A worked example, Y pressed on the System Link game list:

1. The movie reads `Key.getCode()` and sees 45.
2. It issues `GetURL2` with the URL `FSCommand:OnPressY` and numeric argument
   0.
3. Native code checks that the text starts with the 10 bytes `FSCommand:`,
   skips them, and calls a virtual method with the remaining text `OnPressY`.
4. That method (`0x82C7CBE0`) calls two more virtual methods, the second being
   the command handler `0x82E819E0`.
5. When a field on the handler's object is not null, the handler calls
   `0x82D76350` through a virtual slot, and that function compares the command
   with five command strings. For `OnPressY` it reads a stored value, and when more than
   500 has passed since that value it stores a new one, writes a 1 into a flag
   byte on a second object, and calls helper `0x82D6F5D8`.

X works the same way with key code 42 and `OnPressX`. Its native branch ends in
a short forwarder (`0x82D6C340`) and then a state update (`0x82D704F0`).

What is not known: the meaning of the 500 threshold, the flag byte, either
helper, and which on-screen action either press performs. The bodies read for
this page (the functions named above except the two helpers `0x82D6F5D8` and
the target of the branch at `0x82D7054C`, which are unexplored) import no XGI
function, submit no Xbox message, call no socket function, serialize no buffer
and compute no checksum. Those two unexplored places could still reach
networking, so the page does not rule it out for either route.

## Command table

| Command | Key code | Movie URL | Guest string | Parameter reference |
| --- | --- | --- | --- | --- |
| `OnPressY` | 45 | `FSCommand:OnPressY` | `0x821242A0` | `0x82DECBB4` |
| `OnPressX` | 42 | `FSCommand:OnPressX` | `0x8212648C` | `0x82DECB94` |

Each guest string has one modeled reference, and both references sit inside
`0x82DECB20` (see the section on that function below). The visible `Refresh`
(`0x821391A4`) and `Create Game` (`0x821391AC`) strings have no modeled
references, so the page cannot say which key belongs to which label.

## Movie side

The movie is `Resource/Common/GFX_GameSelector.gfx` (35,763 bytes; digest in
the manifest). Its action block at tag `0xECC` reads `Key.getCode()`:

| Command | Compare | Branch | URL push | `GetURL2` |
| --- | --- | --- | --- | --- |
| `OnPressY` | `0x134D` against 45 | `0x1556` | `0x155C`, with numeric argument 0 | `0x156A`, flags 0 |
| `OnPressX` | `0x135D` against 42 | `0x1573` | `0x1579`, with numeric argument 0 | `0x1587`, flags 0 |

The command names also sit at script offsets `0x10CB` and `0x10E5` for
`OnPressY`, and `0x10F8` and `0x1112` for `OnPressX`.

The guest image defines the resource name `GFX_GameSelector.gfx` at
`0x8211FFB0`. No modeled reference, no address built from a high and low half
in one block and no stored word equal to the address uses it
([search record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/resourceGuidance)).
The name matches the movie only by spelling, so it is a search lead and not
proof of how the movie loads. The game could still build or use the name some
other way.

## Native prefix check and callback sites

For frontend input and event ownership see
[frontend-frame-and-input.md](frontend-frame-and-input.md); for movie loading
see [gfx-state-and-loadclip.md](gfx-state-and-loadclip.md). Neither covers
`FSCommand:`. This section covers only the code that recognizes it.

The guest image defines `FSCommand:` at `0x8213E624` with two modeled
references: a data reference at `0x82206660` and a parameter reference at
`0x8220A5CC`. Neither address lies in a function Ghidra models. Both are
decoded instructions inside the recompiled function that starts at
`0x82206350` and runs to the next entry at `0x8220BD08`; Ghidra models only
`0x82206350` through `0x82206357`, ending after the entry save thunk.

Inside that function:

- `0x82206650` materializes `0x8213E624` and `0x82206660` stores it in stack
  slot `+0x17C`.
- At `0x8220A5CC` the code reloads that slot as argument 2, passes an input
  pointer as argument 1 and the literal 10 as argument 3 to `0x827F43F0` (call
  at `0x8220A5D4`), and tests the result against zero.
- At `0x8220B458` a second use of the same stack string calls `0x827F43F0` with
  a second input and the literal 10, and tests the result against zero.

`0x827F43F0` takes two byte pointers and a signed count. A count below 1
returns 0. Otherwise it returns the first unsigned byte difference and stops on
that difference, on the first input's NUL byte, or when the count runs out.
With count 10, a zero result means the input starts with `FSCommand:`.

On each path where the prefixes match, the code advances the input by 10 and
reaches an indirect call through receiver vtable slot `+0x04`:

| Callback site | Target load | Arguments | Evidence |
| --- | --- | --- | --- |
| `0x8220A634` | `0x8220A620` | receiver, result of a prior virtual call, input + 10, a fourth argument with no recovered meaning | Decoded Ghidra instruction window |
| `0x8220B4C0` | receiver vtable slot `+0x04` | the same four arguments | Raw words through the call site, with no decoded Ghidra window; recompiled code gives the matching decoded form |

The first site is direct evidence. The second is a candidate that matches in
shape. This shows two native places where text after the prefix reaches a
virtual call. It does not name the receiver class, the target or the action.

## Observed route for OnPressY

A Y press on the System Link game list reaches callback site `0x8220B4C0`. The
other site was not seen on that press, and another context could use it. The
[callback record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandCallbackProbe),
[target record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandTargetProbe)
and
[dispatch record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandRefreshDispatchProbe)
hold these values.

| Step | Address | Observed or recovered |
| --- | --- | --- |
| Receiver | `0x509201FC` | Mapped, with leading word `0x82162F34` |
| Callback target | `0x82C7CBE0` | Modeled function entry; slot `+0x04` of the vtable at `0x82162F34` |
| First virtual call from the target | `0x82226AA0` | One-word accessor |
| Returned object | `0x514BFB90` | The accessor's observed value |
| Second virtual call from the target | `0x82E819E0` | Common command handler plus an optional dispatch |
| Optional dispatch object | `0x511CECE0` | Held at incoming object field `+0x430` |
| Optional dispatch target | `0x82D76350` | Slot `+0x0C` of that object; command comparison function |

The values above are from one process. They are neutral addresses, not class
names.

### The vtable at 0x82162F34

The word at `0x82162F34` is `0x821B07F8`, and the word at slot `+0x04`
(`0x82162F38`) is `0x82C7CBE0`. The target has exactly one modeled reference,
a data reference from `0x82162F38`. Ghidra models the target only from
`0x82C7CBE0` to `0x82C7CBE7`, after its entry save thunk.

Nothing else references the vtable base `0x82162F34`: no modeled reference, no
address built from a high and low half in one block and no stored word equal to
it ([search record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/nativeFsCommandBoundary/observedTargetStatic)).
That does not exclude a derived value, a copied pointer, a relocation, a
constructor, an indirect producer or a store while the game runs. It also does
not exclude direct loads, other ways of building the value, or halves split
across blocks.

### 0x82C7CBE0

The recompiled copy shows a two-stage virtual forwarder. It ignores the original
callback receiver, treats callback argument 2 as an object, calls that object's
vtable slot `+0x98`, then calls slot `+0x10` on the returned object with the
text after the prefix and the fourth argument.

### 0x82226AA0 and 0x82E819E0

`0x82226AA0` is fully decompiled: it returns the word at argument object offset
`+0xFC`. The observed returned-object pointer is the value of that word.

Ghidra truncates `0x82E819E0` at the save thunk and wrongly shows that path as
not returning. Its recompiled copy keeps the incoming object, command and third
argument, calls `0x82E40680` (the base command handler described below), then
reads incoming object field `+0x430`. When that field is not null, it passes the
command and third argument to helper calls that fill two stack temporaries,
calls slot `+0x0C` of the field's object with pointers to them, destroys the
temporaries and returns.

### 0x82D76350

Ghidra reads bad instruction data at `0x82D76358` and truncates the
decompilation, and its caller and callee lists for this function are empty and
not a complete negative. The recompiled copy of this function loads the command
text pointer from the word at argument 2, loads a second object from incoming
object field `+0x04`, and compares the command with five strings:

| String address | Command |
| --- | --- |
| `0x82139224` | Not identified |
| `0x82126498` | Not identified |
| `0x821242A0` | `OnPressY` |
| `0x82128F58` | Not identified |
| `0x8212648C` | `OnPressX` |

Branches that matter:

- `OnPressY`: derives a scalar from a global double and takes an unsigned delta
  involving incoming object field `+0x11C`. When the delta is 500 or less it
  returns. Otherwise it updates field `+0x11C`, writes 1 to the second object's
  byte `+0x11`, and calls `0x82D6F5D8` with that second object. That helper is
  not expanded. The delta does not show time units or debounce behavior.
- `OnPressX`: after a byte 0 test on incoming object field `+0x11`, loads the
  second object's vtable slot `+0x3C` and calls it indirectly at `0x82D765B8`.
- Other branches call `0x82D6F858`, `0x82D39138` and `0x82D6F300`. These
  addresses are not expanded.

## Observed route for OnPressX

An X press on the System Link game list reaches the indirect call at
`0x82D765B8` with the target `0x82D6C340`
([X correlation record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandOnPressXCorrelationProbe)).
The tail dispatch at `0x82D6C350` then reached the target `0x82D704F0`
([tail target record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandOnPressXTailTargetProbe)).
Each target is from one process. No object, argument or platform data is
recorded for either.

`0x82D6C340` has a complete body of 5 instructions: load the incoming object's
leading word, put the literal 11 in argument 2, load vtable slot `+0x1C`, move
it to the count register, and branch through it at `0x82D6C350`.

`0x82D704F0` has the body `0x82D704F0` through `0x82D7054C`:

- It writes the byte 1 to incoming object field `+0x0C`.
- It loads the state pointer from the word at `0x8314F2E4`.
- Unless the pointer at state `+0x04` is not null, its `+0x08` word equals
  argument 2 and state `+0x10` also equals argument 2, it stores argument 2 to
  state `+0x10` and clears the bytes at state `+0x40` and `+0x41`.
- It loads the pointer at state `+0x08`. If that is null it returns. Otherwise
  it branches through the pointed object's vtable slot `+0x0C` at `0x82D7054C`.

The tail target of that last branch, the classes of both objects, the meaning
of each field and the slot meanings are all open.

## The command reference function 0x82DECB20

The movie's two command names also appear in the guest, which made
`0x82DECB20` look like a handler. It is not one for these commands.

`0x82DECB20` has one modeled reference, a data pointer at `0x82128750`, and no
modeled direct caller. The seven words around that pointer are all modeled
function entries:

| Address | Target |
| --- | --- |
| `0x82128744` | `0x82DEE4F0` |
| `0x82128748` | `0x82C7BCC0` |
| `0x8212874C` | `0x82C7BD50` |
| `0x82128750` | `0x82DECB20` |
| `0x82128754` | `0x82DE9F30` |
| `0x82128758` | `0x821BC970` |
| `0x8212875C` | `0x82C7C850` |

Seven consecutive function pointers show a neighborhood only: no table base,
class boundary, slot meaning or action is recovered.

Its recompiled copy (Ghidra truncates after later option handling at the known
save and restore thunk) runs in this order:

1. At `0x82DECB38` it calls `0x82E40680` with the object, command and third
   argument.
2. At `0x82DECB48` it calls `0x82DEA4C8` with the same arguments.
3. It compares the command with `OnAccept`, `OnCancel`, `OnPressX` and
   `OnPressY`. A match skips the remaining local option and unit-stack handling
   by branching to `0x82DECC20`. No separate X or Y target is called.

The three callees only recognize general commands:

| Callee | What it recognizes | Action |
| --- | --- | --- |
| `0x82E40680` | `OnAccept`, `OnCancel`, `OnOption` | Calls `0x82C7B710` first at `0x82E40698`, then dispatches object vtable slots `+0x30`, `+0x34` and `+0x38`, passing the object and third argument |
| `0x82C7B710` | `OnInit` (`0x8212E7B8`), `OnExit` (`0x8212E7C0`), `PlaySound` (`0x82162D40`), `StopSound` (`0x82162D4C`) | Dispatches object vtable slots `+0x14`, `+0x18`, `+0x1C` and `+0x20` in that order, passing the object and third argument |
| `0x82DEA4C8` | `OnLoadUnitStack` (`0x82128344`), `OnClearUnitStack` (`0x82127F5C`) | Unit-stack command state, described below |

`0x82DEA4C8` ignores its third argument and scans a word array rooted at object
field `+0x4C8`. For the first array value that is not 2, value 0 selects
`OnLoadUnitStack` and value 1 selects `OnClearUnitStack`. When the incoming
command matches the selected string, it changes that entry to 2, stores the
result of `0x8280DE30` plus 2000 at object field `+0x4D4`, and runs a follow-up
scan. It does not compare `OnPressX` or `OnPressY`.

None of the three callees, and no comparison in them, handles `OnPressX` or
`OnPressY`. The commands pass only through general filtering.

The observed Y route calls `0x82E40680` from `0x82E819E0`, and `0x82DECB20` calls
the same function. A candidate reading is that `0x82E819E0` and `0x82DECB20` are
sibling command handlers that share it. That reading is not tested. A Y press was not seen to enter
`0x82DECB20` in one process
([boundary record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeCommandBoundaryProbe)).
That does not prove the function is never reached from another context.

## Network calls

Neither press was seen to cause an XGI or XSession message, a direct-LAN bind
or getname, a successful `sendto` or `recvfrom`, or a QoS listener event while
its command was dispatched. The Y dispatch is the optional call inside
`0x82E819E0` and the X dispatch is the indirect call at `0x82D765B8`
([Y record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandRefreshCorrelationProbe),
[X record](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/runtimeFsCommandOnPressXCorrelationProbe)).

This covers only those logged message kinds. It does not exclude an unlogged
API attempt, a failed socket operation, a helper, a later asynchronous path,
platform behavior, delivery or ordering. It does not map either press to a
Create Game action, session creation, advertisement or discovery. What a host
flow does after X is on the [QoS page](xbox-system-link-qos.md).

## Addresses

| Item | Address |
| --- | --- |
| `FSCommand:` string | `0x8213E624` |
| Prefix comparator | `0x827F43F0` |
| Recompiled function that matches the prefix | `0x82206350` through `0x8220BD08` |
| Callback sites | `0x8220A634`, `0x8220B4C0` |
| Y route | `0x82C7CBE0`, `0x82226AA0`, `0x82E819E0`, `0x82D76350` |
| X route | `0x82D765B8`, `0x82D6C340`, `0x82D704F0` |
| Command reference function | `0x82DECB20` |
| Resource name string | `0x8211FFB0` |

## Open questions

- Receiver class and concrete type of every object on both routes.
- Which visible action each press performs, and whether Refresh and Create
  Game are involved.
- Whether the second callback site (`0x8220B4C0`) or the first
  (`0x8220A634`) is reached from other contexts.
- The second target of the tail dispatch at `0x82D7054C`, and the helper
  `0x82D6F5D8`.
- Whether any command here causes a network call outside the logged message
  kinds, including through `0x82D6F5D8` and the target of the branch at
  `0x82D7054C`.

## Evidence sources

- [Game selector locators](../../manifests/xbox-system-link-qos-root.json#/uiAnchors)
- [Native FSCommand boundary](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/nativeFsCommandBoundary)
- [Command chain locators](../../manifests/xbox-system-link-qos-root.json#/uiAnchors/commandChainLocators)
- [Xbox System Link QoS boundary](xbox-system-link-qos.md)
