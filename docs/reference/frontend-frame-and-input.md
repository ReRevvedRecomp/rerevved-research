# Frontend, frame, and input ownership

The frontend lifecycle, shared timing state, application callbacks, gameplay
availability signals, and controller input are separate ownership paths. The
semantic names below are recovered labels, not original debug symbols.

## Frontend state identity

The global at `0x82FFD624` publishes the frontend root. Its field at `+0x70`
holds the current frontend-state pointer. The bounded frontend states share a
two-word identity prefix:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Concrete state vtable |
| `+0x4` | Numeric state key |

Key 2 identifies the recovered game-start receiving state. Its factory at
`0x821B0AF0` creates an eight-byte object whose slot `+0x4` enters
`AudioGameStartInit` at `0x82E60F70`. Key 5 identifies the recovered
attract-movie state. Its factory at `0x821B3BB8` creates a `0x10`-byte state
whose slot `+0x1C` builds the attract-movie playback object.

A bounded registration search found no direct reference to the key-2 factory.
Vtable `0x8211EBD0` is installed by the factory and by in-place initializer
`0x82E60D50`; neither complete body registers or dispatches the state. The
entry target is referenced only by table word `0x8211EBD4`, so the frontend
state-owner insertion edge and resolved dynamic callsite remain unknown.

These values identify two concrete states in the recovered paths. They do not
define a universal frontend enumeration or assign original class names to
other numeric keys.

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

A bounded static ownership packet tested the accepted interface reader and six
writer candidates. Six exact bodies reduce to non-returning thunk calls in the
configured project and `0x82DD8FB8` truncates on bad instruction data. A direct
reference inventory contains 29 reads across 27 other modeled functions but
was not expanded. No static publisher, clearer, toggler, or lifecycle relation
is therefore accepted. This does not change the separately captured runtime
gate role. Exact limits are in
[`playable-interface-gate-ownership-boundary.json`](../../manifests/playable-interface-gate-ownership-boundary.json).

`LocalPlayerIdResolve` at `0x82D8A3A0` bounds one local-player selection path.
It returns `-1` when input offset `+0x10` is null. Otherwise it dispatches the
object's vtable slot `+0x100` and returns word `+0xC` from the dispatched
result. The input and result types, concrete fields, indirect target, fallback
meaning, and multiplayer or network semantics remain unresolved.

## Shared frame-timing owner

`FrameTimingOwnerPublish` at `0x82E293E8` allocates and initializes one
`0x48`-byte owner. It publishes the same pointer through globals `0x8314F280`
and `0x8314F2D4`. The owner vtable at `0x82164E14` exposes two recovered slots:

| Slot | Target | Role |
| --- | --- | --- |
| `+0x4` | `FrameTimingReset` at `0x82C7EBF8` | Resets the accumulated, working, and counter fields |
| `+0x8` | `FrameTimingAdvance` at `0x82C7EB68` | Advances the sample, delta, accumulated time, and update counter |

Initialization and reset both write the 64-bit fields at `+0x8`, `+0x10`, and
`+0x20`, plus the word at `+0x30`. Initialization also writes the 64-bit field
at `+0x28`.

A bounded first-reader search reconfirmed the `+0x10` stores at `0x82E2943C`
and `0x82C7EC08`. Exact references to primary owner global `0x8314F280`
produce 28 distinct reader functions, exceeding the six-candidate cap before
field classification. No first `+0x10` reader or value meaning is therefore
assigned.

`AttractMovieFrameStep` at `0x82C5F680` advances this shared owner, but its
vtable and construction path place it on the key-5 attract-movie object. It is
not the playable-game frame boundary. Static timing dispatch also proves no
runtime cadence.

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

The input-poller vtable at `0x8216A26C` selects the poller through slot `+0x4`.
The `CcGameInputProcessor` vtable at `0x82138B4C` uses slot `+0x4` for dispatch
and slot `+0x8` for the recovered class-name function at `0x821D8498`.

This chain establishes polling, delta-record creation, and the processor
dispatch boundary. It does not establish queue fan-out or an executable
controller-glyph-family selector.

## Evidence boundaries

- Frontend state, interface availability, callback dispatch, timing, and input
  remain distinct signals and owners.
- Guest pointers published through frontend or interface globals have bounded
  lifetimes. The static layouts do not promise persistence across teardown.
- No movement producer, duration field, or movement-specific callback follows
  from these application-wide paths.
- The recovered boundaries define no runtime hook or guest-state mutation.

## Evidence sources

- [Frontend gameplay transition](../../manifests/frontend-gameplay-transition.json)
- [Playable game state gates](../../manifests/playable-game-state-gates.json)
- [Playable interface-gate ownership boundary](../../manifests/playable-interface-gate-ownership-boundary.json)
- [Attract-movie frame driver](../../manifests/attract-movie-frame-driver.json)
- [Gameplay frame-timing owner](../../manifests/gameplay-frame-timing-owner.json)
- [Gameplay main-frame boundary](../../manifests/gameplay-main-frame-boundary.json)
- [Controller input and glyph selection](../../manifests/controller-input-glyph-selection.json)
- [Catalog contract](../catalogs.md)
