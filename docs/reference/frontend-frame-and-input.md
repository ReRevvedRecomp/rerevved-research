# Frontend, frame, and input paths

Frontend lifecycle, timing, application callbacks, availability and input are
handled by separate code. Names are recovered, not debug symbols. The static
paths need the stated identities, normal ABI returns and stable state without
harmful aliasing. Runtime observations are identified explicitly.

## Frontend state identity

The global at `0x82FFD624` publishes the frontend root. Its field at `+0x70`
holds the current frontend-state pointer. The selected frontend states share a
two-word identity prefix:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Concrete state vtable |
| `+0x4` | Numeric state key |

- Key 2 identifies the recovered game-start receiving state. Its factory at
  `0x821B0AF0` creates an eight-byte object whose slot `+0x4` enters
  `AudioGameStartInit` at `0x82E60F70`.
- Key 5 identifies the recovered attract-movie state. Its factory at
  `0x821B3BB8` creates a `0x10`-byte state whose slot `+0x1C` builds the
  attract-movie playback object.

The [registration query](../../manifests/key2-game-start-registration.json),
limited to the selected paths, found two initializers and the entry-table word.
Neither initializer registers or dispatches the state. The separate
[state-transition contract](../../manifests/game-start-formatting.json#/stateTransitionBoundary)
ties the entry call to the current-state and table premises, and the call runs
only when those premises hold. Actual registration, the request producer and
natural entry are not yet established.

The [entry lifetime contract](../../manifests/xbox-lobby-ready-check.json#/nativeEntryControllerLifetimeBoundary)
distinguishes the screen manager from the game header's loading object. The
selected old frontend exit clears the manager global after a destructor
request. A requested screen key and a separate loading object do not prove
which controller is current during game entry or provide safe cancellation.

These values identify two concrete states in the recovered paths. They do not
define a universal frontend enumeration or assign original class names to other
numeric keys.

## Screen events during transitions

Screen events use a separate queue from game commands. When the sampled
controller's byte at `+0x0C` is nonzero, the dispatcher requests storage of
the event and its argument. The [UI queue contract](../../manifests/native-ui-event-queue.json)
covers this path. Its embedded queue count is at manager `+0x28`, separate
from the requested screen key at `+0x10`.

The reader calls the saved event before it advances queue metadata, then
requests that the record be freed. Controller and queue changes during
that callback need separate lifetime evidence. A count change does not
prove delivery, removal of the same front record or safe cancellation.

The [screen-controller lifecycle](../../manifests/native-screen-controller-lifecycle.json)
covers the selected update, replacement and cleanup requests. Replacement is
published before its entry call. A zero status byte uses a fresh current
controller for another method request, without a following local clear.
Cleanup requests and freed vector backing do not prove that every controller
still held was destroyed. Which code actually holds and invokes the controller
during game entry remains qualified.

## Gameplay availability signals

`FrontendInGameStateCheck` at `0x82E17238` reads the current state through the
frontend root and requires key 2. Other recovered signals are written and read independently:

| Signal | Address | Recovered role |
| --- | ---: | --- |
| Active player ID | `0x8312B8E8` | Published by the selected turn-selection path |
| Human-player mask | `0x8312E608` | Classifies known human players when nonzero |
| Interface check pointer | `0x8314F28C` | Points to an object whose byte `+0x5` controls interface updates |

Selected runtime observations show the fields combining into a conservative
availability test across gameplay, modal, load, and menu transitions. The test
is not a general lifecycle enum, and none of these signals substitutes for the
application callback boundary.

The static publisher in `AppResLoadBuild` installs a word-0 table only under
a condition and writes the candidate pointer to `0x8314F28C`. Its immediate
dispatch on the object shows nothing about whether the pointer stays valid
beyond that call. Live identity, lifetime, and which code clears or toggles the
byte remain unresolved.

The exact stores, alias guards and the table slot that is used only under a
condition are in
[`game-of-the-week-local-generation.json`](../../manifests/game-of-the-week-local-generation.json#/configurationPublisherBoundary).
The separately captured runtime check role is unchanged. The six incomplete
writer candidates and the unexpanded inventory of 29 reads are limited to what
[`playable-interface-flag-ownership.json`](../../manifests/playable-interface-flag-ownership.json)
records.

### Local-player result and lifetime

`LocalPlayerIdResolve` (`0x82D8A3A0`) returns the full-register value `-1` when
the `+0x10` field of its input is null. Otherwise it dispatches through
`+0x100` and zero-extends the `+0xC` field of the returned pointer, without a
null check. Combat loads the input from `0x8314EFE0`.

The initializer zeros the input object's `+0x10` field. Setup at `0x82D8C600`
stores the matching registry lookup result there. A successful producer
installs `0x8215FA78`, whose `+0x100` target `0x82A73340` returns the child at
`+0x20`. The factory runs only under a condition. It allocates 108 bytes, sets
result field `+0xC` to `0xFFFFFFFF`, and publishes the constructor's return
value at `+0x20`. When allocation, production and lookup all succeed and the
stored pointer stays unchanged, the resolver reads the low 32 bits of -1. An
allocation failure can leave null at the unchecked read.

A store scan, including the three exact writers it found, shows no later
assignment to the consumed word. The child method passes the result to a
node-payload reader without a direct write or link. A second scan finds only the
child's own `+0xC` initialization, not the separate result. The selected stores
use node, payload or adjusted subobject bases. A float store could overwrite a
word, but the receiver and the dispatched scalar remain unknown.

### Ordinal writers that run only under a condition

The child method at `+0x88` passes the same `+0x20` through an ordinal search
only when its condition holds. It then exchanges result field `+0xC`:

| Current word | Store |
| --- | --- |
| Outer ordinal | Searched ordinal |
| Otherwise searched ordinal | Outer ordinal |
| Neither | Unchanged |

The initial probe comes before a retry limit of 8, so that range is not
universal. The initial `0xFFFFFFFF` survives when four things hold: the count is
stable, the ordinals are nonnegative and do not overflow, the guards on the
object, the ABI and aliasing pass, and neither argument matches.

Another producer keeps its receiver and stores `+0xC` when `low32(r4)==0`. It
stores `low32(r6)` when `signed32(r6)>=0`. When `signed32(r6)<0`, it runs a
finite vacancy search over 0 to 7. A wrapper separately stores the return value,
including -1. Two callers pass registry getter results that are connected to
constructed objects only under a condition. Five things remain open: whether the
lookup key equals the current key, the internal `+0x4` relookup, `+0x148`, the
actual scalars, and whether the stored value stays unchanged. The wrapper needs
the incoming result identity and `+0x190`. Four setup functions never invoke
`+0x88`, so a compatible nonzero value needs these links or a new scoped caller.
Execution order, legal range and meaning, lifetime and network semantics remain
unknown.

No raw direct caller was found for `0x82CAF2C0` or `0x82CAF258`. Two methods
pass their own `+0x34` to `BufferReadU32`, which dispatches input `+0x4` for four
bytes before a reversal that happens only under a condition. The shared
receiver, the actual bytes and source, and a `+0x8` zero are not yet shown. A
sparse search of candidate bases found no installer. The actual key and
compatible ordinal remain open in the
[resolver boundary](../../manifests/playable-game-state-requirements.json).

## Shared frame-timing object

`FrameTimingOwnerPublish` at `0x82E293E8` allocates and initializes one
`0x48`-byte timing object. It publishes the same pointer through globals
`0x8314F280` and `0x8314F2D4`. The object's vtable at `0x82164E14` exposes two
recovered slots:

| Slot | Target | Role |
| --- | --- | --- |
| `+0x4` | `FrameTimingReset` at `0x82C7EBF8` | Resets the accumulated, working, and counter fields |
| `+0x8` | `FrameTimingAdvance` at `0x82C7EB68` | Advances the sample, delta, accumulated time, and update counter |

| Writes | Fields |
| --- | --- |
| Initialization and reset | 64-bit fields at `+0x8`, `+0x10`, and `+0x20`; word at `+0x30` |
| Initialization also | 64-bit field at `+0x28` |

A search for the first reader, limited to the selected references, reconfirmed
the `+0x10` stores at `0x82E2943C` and `0x82C7EC08`. Exact references to the
primary global `0x8314F280` produce 28 distinct reader functions, which exceeds
the six-candidate cap before field classification. No first `+0x10` reader or
value meaning is therefore assigned.

`AttractMovieFrameStep` at `0x82C5F680` advances this shared object, but its
vtable and construction path place it on the object for the attract movie with
key 5. It is not the frame boundary for playable games. Static timing dispatch
also shows no runtime cadence.

## Application callback registration

The application object keeps its callback vector at `+0x80` and its callback
synchronization object at `+0x90`. `ApplicationCallbackContainerCtor` at
`0x82E2AFD0` allocates a four-byte callback object, installs vtable
`0x82120D2C`, and passes it to `ApplicationCallbackRegister` at `0x82E2AF20`.
Registration locks the application object and appends the callback pointer to the vector.

The callback vtable's slot `+0x0` enters `PlayableFrameCallback` at
`0x82E87D18`, which reaches broad driver `0x82C7DF58`. A selected runtime
observation places the broad driver on the game-start thread during playable
gameplay. It is a frame boundary. It is not the availability predicate and not a
movement-specific update function.

## Controller poll-to-dispatch path

The recovered controller path is:

`InputPoller` (`0x82C14EE8`) -> `ControllerDeltaEmit` (`0x82C14AD8`) ->
`ControllerEventBuild` (`0x82C14A30`) -> `CcGameInputProcessorDispatch`
(`0x82E555A0`).

The input poller's vtable at `0x8216A26C` selects the poller through slot
`+0x4`. The `CcGameInputProcessor` vtable at `0x82138B4C` uses slot `+0x4` for
dispatch and slot `+0x8` for the recovered function for the class name at
`0x821D8498`.

This chain establishes polling, delta-record creation, and the processor
dispatch boundary. It does not establish queue fan-out or an executable selector
for the controller glyph family.

## Evidence boundaries

- Frontend state, interface availability, callback dispatch, timing, and input
  remain distinct signals, each written by different code.
- Guest pointers published through frontend or interface globals have limited
  lifetimes. The static layouts do not promise persistence across teardown.
- No movement producer, duration field, or movement-specific callback follows
  from these application-wide paths.
- The recovered boundaries define no runtime hook or guest-state mutation.

## Special Functions options action

When the full chooser returns 3, or the alternate chooser returns 1, the code
selects action 29. That action dispatches receiver `0x8314F76C` slot `+0xCC` and
then returns to the construction loop. Vtable `0x82138768`, when the object
still holds it, selects `0x82D84580`, which constructs the dialog and invokes
`+0x2C`. The constructed object's vptr, when still held, selects `0x82E40738`.
The runner uses the dialog and interface callbacks. On exit it dispatches
`+0xC`, restores saved bytes through the current interface and child pointers,
and returns `+0x42C`. Whether those pointers stay valid, and whether the
runner returns at all, is not yet shown.

The update helper returns zero for a nonzero dialog `+0x8`, which selects exit
after earlier returns. The state and status branch sets that byte, and so does
the initialized `+0x30`, the latter before the application dispatch and the
outcome checks. Neither identifies a button.

Base construction passes the dialog to movie `+0x9C` before the Options vtable
is installed. The constructed route stores `+0xFC`, and the getter at `+0x98`
returns it. The shared handler gets the dialog and then dispatches `+0x10`.
Under identity and command guards, the accept command selects `+0x30` and the cancel
command selects `+0x34`. Cancel can clear `+0x8` after setting it. An exit that always
happens is not yet shown.

### Callback receiver and handler limits

The driver saves context `+0x74` on the stack. The first `+0x3C` call uses that
receiver and loads the handler from return value `+0xC0`. The second call
reloads the context field and supplies the movie argument. Whether the saved
value equals the receiver, and whether the receiver equals the return object,
remain unknown. The constructed instance's initial `+0xC0` is zero. That shows
neither the return object nor that a handler was installed.

The helper constructor stores movie `+0x38`, a reference to movie `+0xC` at
helper `+0x34`, and two vtables. A secondary dispatch that runs only under a
condition reaches the descriptor storage. The first publication wrapper
prepares a local key and may select that target. These stores identify neither
the driver context nor a return object that holds a handler. Later callers pass
the descriptor address that holds the saved helper through construction, copy
and cleanup. One copy reaches the unresolved secondary `+0x28`.

A copy can dispatch the current `+0x8`. The base chain installs tables only
under a condition, and the first targets of those tables return or increment
`+0x4`. Applying them needs the helper and table to stay valid. The later base
constructor uses a separate global receiver. The image table and an explicit
replacement select different targets. A replacement can invoke the callback and
further unresolved calls. Another route passes the address of the replacement
writer to a helper that can append it through a global cursor. The consumer and
the order remain unknown even though the cursor is initialized and reset. The
current table is not yet shown to be separate from the returned pointer.
Therefore the base call establishes neither that the helper stays valid nor
that it is published to the driver.

### Named commands and return paths

The named route needs live instance and dialog vptrs and a temporary that
differs from the sub-option command. The preparation does not show that the bytes match
the original command. The actual Options producer, the handler registration and
the instance that receives callbacks remain unknown.

The queued instance at `+0x48` prepares a record for two unresolved virtual
calls. One of them dispatches `+0x18` on the descriptor's `+0x4` pointer when
the first byte is 7. That identity must survive the extraction table calls and
cleanup. The upstream lookup copies an indexed tag and pointer, but the record
writer and the primary vptr remain unknown. A separate parsed handoff at
`0x8228B1F0` produces tag 6 and a cached payload, and selects a zero output when
the payload stays in place. Payload `+0` initializes to 1, which is not shown to
be a tag-7 vptr. The other dispatch uses a separate object `+0x4`. Neither path
is linked to the driver or to completion.

Entry and exit set and clear child `+0x2A` and reach the manager's pointer-range
work. That shows neither capture nor a stable identity. After the runner
returns, Options dispatches dialog `+0` with one, optionally passes the original
receiver `+0x1F0`, and then rebuilds the menu. The child calls and the clear and
set of `+0x1E8` run only under a condition. Focus and pause handling, Back and
Escape handling, and exclusive capture remain unknown. All edges need valid
objects, the stated vptrs and the earlier returns.

Both choosers map -1 to receiver `+0xB0` with zero, an optional call to
`0x82D05C90`, and then a -1 return. Input handling, focus restoration and the
live vtable are not yet established. The exact conditions are in the
[options manifest](../../manifests/special-functions-options-dispatch.json).

## Player-count setup

`0x82D217C8` stores six at `0x82F700AC` and five at the excluded-player slot
`0x82F700B0`. When `0x8314F180` is nonzero, the count is overridden to two and
the excluded index is taken from the saved r16. The meaning of the override and
its full provenance remain unknown. Initialization skips the excluded ordinal.
Count, civilization, human status and storage capacity are distinct. Game start
reaches setup through a direct call chain. The human-mask helper clears the
mask, then copies a nonzero source or combines player predicates. Clear bits do
not show that a player is a plain AI player, and key 2 does not distinguish
creating a game from loading one. Whether setup runs only for a new game, and
how a civilization could safely be omitted, are not yet shown. See the
[setup boundary](../../manifests/player-count-setup.json).

The inner -1 setup bypass does not establish cancellation of its enclosing
game-start state. `0x82E60F70` does not compare the outer setup return before
its guarded presentation continuation. That path can reach the indexed string
argument of `0x82E225D0` and the narrow-string byte scan of `0x82D3B830`. Valid
native inputs may satisfy this contract. Invalid input and crash causation are
not established by missing local checks. The
[formatting boundary](../../manifests/game-start-formatting.json) records the
exact branches, the application `+0x60` identity, two argument slots, the
current, pending and requested-state transitions, and the selected native
refusal and reset routes. Those routes include the selected waiting-overlay
event-16 cleanup and the guarded setup continuation. That continuation needs a
normal cleanup return and roots that stay valid, and it is not an accepted
retry. Its deferred frontend request is distinct from controller cleanup. Safe
late cancellation and the actual invalid slot are not yet shown.

## Advisor presentation entry

The advisor constructor passes the name address to the base before
initialization. Two wrappers named for accept and cancel forward to the
scene-tree walker only under a condition. Their names show no gameplay
callbacks. The lookup chain, which code shows or enqueues the advisor, and
whether the choice is optional or mandatory remain unknown. The
[entry boundary](../../manifests/advisor-show.json#/findings/RVA-F-0242)
supplies construction and forwarding, not safe popup suppression.
The [advisor popup sites](advisor-popup-sites.md) page groups the 169 callers by purpose and result use.

## Evidence sources

- [Native pause and resume dispatch](../../manifests/native-pause-resume-dispatch.json):
  with matching live root and child tables, a selected zero-argument request
  can reach a global application object's `+0x70` child and its virtual `+0x10`.
  On the selected key-2 table this constructs a code-17 state message with a
  zero byte at `+0x34`; the alternative method uses one. The registered sender
  identity and the selected early-return checks are confirmed. The selected
  processing method forwards the byte to a root-state consumer whose accepted
  zero arm clears bit `0x800` and reaches the frontend child's resume callback.
  An already-clear bit bypasses those effects. A selected accept command can
  reach the zero-request callback through the pause class's current table. The
  separate tail for the Start press command has different guards. Actual input, receipt and
  invocation, current identity, child presentation and host and peer authority
  are not yet tied to this path. The local-menu getter tests the nested
  dialog-child marker. A separate receiver-relative event-byte reader still
  needs proof that it uses the same singleton and that the store comes before
  the read.
- [Frontend gameplay transition](../../manifests/frontend-gameplay-transition.json)
- [Playable game state requirements](../../manifests/playable-game-state-requirements.json)
- [`playable-interface-flag-ownership.json`](../../manifests/playable-interface-flag-ownership.json)
- [Attract-movie frame driver](../../manifests/attract-movie-frame-driver.json)
- [Gameplay frame-timing object](../../manifests/gameplay-frame-timing-owner.json)
- [Gameplay main-frame boundary](../../manifests/gameplay-main-frame.json)
- [Controller input and glyph
  selection](../../manifests/controller-input-glyph-selection.json)
- [Catalog contract](../catalogs.md)
