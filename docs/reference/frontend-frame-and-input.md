# Frontend, frame, and input ownership

Frontend lifecycle, timing, application callbacks, availability and input have
separate owners. Names are recovered, not debug symbols. Static continuations
require their stated identities, normal ABI returns and stable nonalias state;
runtime observations are identified explicitly.

## Frontend state identity

The global at `0x82FFD624` publishes the frontend root. Its field at `+0x70`
holds the current frontend-state pointer. The bounded frontend states share a
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

A bounded registration search found no direct reference to the factory for key
2. Vtable `0x8211EBD0` is installed by the factory and by in-place initializer
`0x82E60D50`; neither complete body registers or dispatches the state. The
entry target is referenced only by table word `0x8211EBD4`, so the frontend
state-owner insertion edge and resolved dynamic callsite remain unknown.

These values identify two concrete states in the recovered paths. They do not
define a universal frontend enumeration or assign original class names to other
numeric keys.

## Gameplay availability signals

`FrontendInGameStateCheck` at `0x82E17238` reads the current state through the
frontend root and requires key 2. Other recovered signals are independently
owned:

| Signal | Address | Recovered role |
| --- | ---: | --- |
| Active player ID | `0x8312B8E8` | Published by the bounded turn-selection path |
| Human-player mask | `0x8312E608` | Classifies known human players when nonzero |
| Interface-gate pointer | `0x8314F28C` | Points to an object whose byte `+0x5` controls interface updates |

Bounded runtime observations show the fields combining into a conservative
availability test across gameplay, modal, load, and menu transitions. The test
is not a general lifecycle enum, and none of these signals substitutes for the
application callback boundary.

The static publisher in `AppResLoadBuild` conditionally installs a word-0 table
and writes the candidate pointer to `0x8314F28C`. Its immediate owner dispatch
prevents a retention claim beyond that call; live identity, lifetime and
clear/toggle ownership remain unresolved.

The exact stores, alias guards and conditional table slot are in
[`game-of-the-week-local-generation.json`](../../manifests/game-of-the-week-local-generation.json#/configurationPublisherBoundary).
The separately captured runtime gate role is unchanged. The six incomplete
writer candidates and unexpanded inventory of 29 reads remain bounded by
[`playable-interface-gate-ownership-boundary.json`](../../manifests/playable-interface-gate-ownership-boundary.json).

### Local-player result and lifetime

`LocalPlayerIdResolve` (`0x82D8A3A0`) returns full-register `-1` for null input
`+0x10`; otherwise it dispatches `+0x100` and zero-extends returned-pointer
`+0xC`, without null checking. Combat loads input from `0x8314EFE0`.

Initializer zeros owner `+0x10`; setup `0x82D8C600` stores matching registry
lookup. Successful producer installs `0x8215FA78`, whose `+0x100` target
`0x82A73340` returns child `+0x20`. Conditional factory allocates 108 bytes,
sets result `+0xC` to `0xFFFFFFFF`, publishes constructor return at `+0x20`.
Successful allocation/production/lookup and retention join resolver to that
low32 -1; allocation failure can leave null at the unchecked read.

Store scan/three exact owners found no later consumed-word assignment. Child
method passes result to a node-payload reader without a direct write/link;
second scan identifies only child's own `+0xC` initialization, not the separate
result. Selected stores use node/payload or adjusted subobject bases; float
store could overwrite a word, but receiver/scalar dispatch remain unknown.

### Conditional ordinal writers

Child `+0x88` conditionally passes the same `+0x20` through ordinal search to
exchange result `+0xC`:

| Current word | Store |
| --- | --- |
| Outer ordinal | Searched ordinal |
| Otherwise searched ordinal | Outer ordinal |
| Neither | Unchanged |

Initial probe precedes retry bound 8; range is not universal. Stable count,
nonnegative nonoverflowing ordinals and ownership/ABI/nonalias guards preserve
initial `0xFFFFFFFF` because neither argument matches.

Another producer retains receiver, storing `+0xC` when `low32(r4)==0`:
`low32(r6)` for `signed32(r6)>=0`, otherwise finite 0..7 vacancy search for
`signed32(r6)<0`. Wrapper separately stores return, including -1. Two callers
pass registry getter results, conditionally joined to constructed objects, but
lookup/current-owner key equality, internal `+0x4` relookup/ `+0x148`, actual
scalars and retention remain open. Wrapper needs incoming result
identity/`+0x190`. Four setup bodies have no `+0x88` invocation; compatible
nonzero consumption needs these joins or a new scoped caller. Execution/order,
legal range/meaning, lifetime and network semantics remain unknown.

No raw direct caller was found for `0x82CAF2C0`/`0x82CAF258`. Two methods pass
own `+0x34` to `BufferReadU32`, dispatching input `+0x4` for four bytes before
conditional reversal. Shared receiver, actual bytes/source and `+0x8` zero
remain unproved; sparse candidate-base search found no installer. Actual
key/compatible ordinal remain open in the
[resolver boundary](../../manifests/playable-game-state-gates.json).

## Shared frame-timing owner

`FrameTimingOwnerPublish` at `0x82E293E8` allocates and initializes one
`0x48`-byte owner. It publishes the same pointer through globals `0x8314F280`
and `0x8314F2D4`. The owner vtable at `0x82164E14` exposes two recovered slots:

| Slot | Target | Role |
| --- | --- | --- |
| `+0x4` | `FrameTimingReset` at `0x82C7EBF8` | Resets the accumulated, working, and counter fields |
| `+0x8` | `FrameTimingAdvance` at `0x82C7EB68` | Advances the sample, delta, accumulated time, and update counter |

| Writes | Fields |
| --- | --- |
| Initialization and reset | 64-bit fields at `+0x8`, `+0x10`, and `+0x20`; word at `+0x30` |
| Initialization also | 64-bit field at `+0x28` |

A bounded first-reader search reconfirmed the `+0x10` stores at `0x82E2943C` and
`0x82C7EC08`. Exact references to primary owner global `0x8314F280` produce 28
distinct reader functions, exceeding the six-candidate cap before field
classification. No first `+0x10` reader or value meaning is therefore assigned.

`AttractMovieFrameStep` at `0x82C5F680` advances this shared owner, but its
vtable and construction path place it on the object for the attract movie with
key 5. It is not the frame boundary for playable games. Static timing dispatch
also proves no runtime cadence.

## Application callback registration

The application owner keeps its callback vector at `+0x80` and its callback
synchronization object at `+0x90`. `ApplicationCallbackContainerCtor` at
`0x82E2AFD0` allocates a four-byte callback object, installs vtable
`0x82120D2C`, and passes it to `ApplicationCallbackRegister` at `0x82E2AF20`.
Registration locks the owner and appends the callback pointer to the vector.

The callback vtable's slot `+0x0` enters `PlayableFrameCallback` at
`0x82E87D18`, which reaches broad driver `0x82C7DF58`. Bounded runtime
observation places the broad driver on the game-start thread during playable
gameplay. It is a frame boundary, not the availability predicate and not a
movement-specific update owner.

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
  remain distinct signals and owners.
- Guest pointers published through frontend or interface globals have bounded
  lifetimes. The static layouts do not promise persistence across teardown.
- No movement producer, duration field, or movement-specific callback follows
  from these application-wide paths.
- The recovered boundaries define no runtime hook or guest-state mutation.

## Special Functions options action

Full chooser return 3 and alternate return 1 select action 29, dispatching
receiver `0x8314F76C` slot `+0xCC`, then returning to the construction loop.
Retained vtable `0x82138768` selects `0x82D84580`, which constructs dialog and
invokes `+0x2C`; retained constructed vptr selects `0x82E40738`. Runner uses
dialog/interface callbacks; exit dispatches `+0xC`, restores saved bytes through
current gate/child pointers and returns `+0x42C`. Pointer retention/finite
return remain unproved.

Update helper returns zero for nonzero dialog `+0x8`, selecting exit after
earlier returns. State/status branch and initialized `+0x30` set that byte, the
latter before application dispatch/outcome gates; these identify no button.

Base construction passes dialog to movie `+0x9C` before Options vtable install;
constructed route stores `+0xFC`, getter `+0x98` returns it. Shared handler gets
dialog then dispatches `+0x10`. Under identity/command guards, `OnAccept`
selects `+0x30`, `OnCancel` selects `+0x34`. Cancel can clear `+0x8` after
setting it; unconditional exit is unproved.

### Callback receiver and handler limits

Driver saves context `+0x74` on stack. First `+0x3C` uses that receiver, loading
handler from return `+0xC0`; second reloads context field and supplies movie
argument. Saved-value and receiver/return equality remain unknown. Constructed
instance's initial `+0xC0` zero identifies neither return object nor handler
installation.

Helper constructor stores movie `+0x38`, movie `+0xC` reference at helper
`+0x34`, and two vtables. Conditional secondary dispatch reaches descriptor
storage; first publication wrapper prepares a local key and may select that
target. These stores identify neither driver context nor handler-bearing return.
Later callers pass descriptor-address holding saved helper through construction,
copy/cleanup; one copy reaches unresolved secondary `+0x28`.

Copy can dispatch current `+0x8`; base chain conditionally installs tables whose
first targets return or increment `+0x4`. Applying them requires retained
helper/table. Later base constructor uses a separate global receiver; image
table and explicit replacement select different targets. Replacement can invoke
callback/further unresolved calls. Another route passes replacement-writer
address to a helper that can append it via global cursor. Consumer/order remain
unknown despite cursor initialization/reset. Current table/returned-pointer
separation is unproved, so base call establishes neither helper retention nor
publication to driver.

### Named commands and return paths

Named route requires live instance/dialog vptrs and temporary differing from
`OnSubOption`; preparation proves no byte identity with original command. Actual
Options producer, handler registration and callback-ingress instance remain
unknown.

Queued instance `+0x48` prepares a record for two unresolved virtual calls. One
dispatches `+0x18` on descriptor `+0x4` pointer when first byte is 7; identity
must survive extraction table calls/cleanup. Upstream lookup copies indexed
tag/pointer, but record writer/primary vptr remain unknown. Separate
`0x8228B1F0` parsed handoff produces tag 6/cached payload, selecting zero output
if retained. Payload `+0` initializes to 1, not a tag-7 vptr proof. Other
dispatch uses separate object `+0x4`; neither joins driver/completion.

Entry/exit set/clear child `+0x2A` and reach manager pointer-range work, proving
neither capture nor stable identity. After runner return, Options dispatches
dialog `+0` with one, optionally original receiver `+0x1F0`, then rebuilds menu.
Child calls/`+0x1E8` clear-set remain conditional; focus/pause, Back/Escape and
exclusive capture remain unknown. All edges need valid objects, stated vptrs and
prior returns.

Both choosers map -1 to receiver `+0xB0` with zero, optional `0x82D05C90`, then
-1 return. Input binding, focus restoration/live vtable remain unproved. Exact
gates:
[options manifest](../../manifests/special-functions-options-dispatch.json).

## Player-count setup

`0x82D217C8` stores six at `0x82F700AC`, five at excluded-player `0x82F700B0`;
nonzero `0x8314F180` overrides count to two/excluded index to retained r16.
Override meaning/full provenance remain unknown. Initialization skips excluded
ordinal; count, civilization, human status and capacity differ. Game-start
reaches setup through a direct call chain. Human-mask helper clears, then copies
nonzero source or folds player predicates. Clear bits do not prove ordinary AI,
and key 2 does not distinguish create/load. New-game-only ingress and safe
civilization omission remain unproved. See
[setup boundary](../../manifests/player-count-setup-boundary.json).

## Advisor presentation entry

Advisor constructor passes name address to base before initialization. Two
accept/cancel-named wrappers conditionally forward to the scene-tree walker;
names prove no gameplay callbacks. Lookup chain, show/enqueue ownership and
optional-versus-mandatory choice remain unknown. The
[entry boundary](../../manifests/advisor-show.json#/findings/RVA-F-0242)
supplies construction/forwarding, not safe popup suppression.

## Evidence sources

- [Frontend gameplay transition](../../manifests/frontend-gameplay-transition.json)
- [Playable game state gates](../../manifests/playable-game-state-gates.json)
- [`playable-interface-gate-ownership-boundary.json`](../../manifests/playable-interface-gate-ownership-boundary.json)
- [Attract-movie frame driver](../../manifests/attract-movie-frame-driver.json)
- [Gameplay frame-timing owner](../../manifests/gameplay-frame-timing-owner.json)
- [Gameplay main-frame boundary](../../manifests/gameplay-main-frame-boundary.json)
- [Controller input and glyph
  selection](../../manifests/controller-input-glyph-selection.json)
- [Catalog contract](../catalogs.md)
