# Scene render-tree lifecycle

The published scene render tree, application-wide scene update helper, and
audio manager receiver are distinct guest objects. The semantic names below
are recovered labels, not original debug symbols. The evidence is static unless
stated otherwise.

## Tree publication and layout

Global `0x8314F08C` stores a heap-published `0x2C`-byte scene render tree. A
bounded block inside wider initializer `0x82D52AE8` allocates the tree, calls
constructor `0x82D4BF58`, and publishes either the constructed pointer or null.
The constructor installs no vptr.

The bounded tree layout includes:

| Offset | Recovered role |
| --- | --- |
| `+0x8` | Incoming render float stored by the tree renderer |
| `+0xC` | Incoming render word stored by the tree renderer |
| `+0x10` | Critical section used by the bounded render path |

The remaining pointer and byte fields are unnamed. The absence of a constructor
vptr store means no scene-tree vtable is supported by this evidence.

## Render and update edges

Scene render gate `0x82E43830` checks the published tree and its surrounding
anonymous gates, reloads the tree, and calls renderer `0x82D4C348`. The renderer
enters the critical section and stores its incoming values at `+0x8` and
`+0xC` before bounded downstream work.

`SceneUpdateHelper` at `0x82E43B50` is reached from the broader application
update chain. One exact gated caller loads global `0x8314F084` as the receiver
and calls `RenderMgrUpdate` at `0x82D526A0`. That callee separately loads the
scene-tree global at `0x8314F08C` and reaches the bounded tree update edge.

Global `0x8314F084` is the published `0x4C8`-byte audio manager. The exact
receiver qualification does not prove that `RenderMgrUpdate` is an original
audio-manager method or assign full audio semantics to the function. The two
globals remain distinct.

## Teardown

`SceneRenderTreeTeardown` at `0x82D51EC0` processes an existing tree and clears
`0x8314F08C` at `0x82D51F20`. The wider shutdown path and helper semantics are
unresolved.

Address `0x82D55834` is a fall-through continuation inside
`SceneNodeRenderWrap`, not a separate function and not a proved teardown
target. No teardown-to-wrapper relation follows from address proximity or the
bounded generated shape.

## Retained scene-root content reference

The `0xA8`-byte scene-root content object retains a refcounted pointer at
`+0x44`. `SceneRootContentSlot0Body` assigns it from prepared-record `+0x28`
through helper `0x821B2440`, which releases the replaced pointer when needed
and acquires the incoming pointer.

The first accepted wrapper, `SceneNodeRenderWrap` at `0x82D55808`, and the
accepted visit consumer, `SceneNodeRenderVisit` at `0x82D55C68`, contain no
direct receiver-relative `+0x44` access. Their indirect vtable targets remain
outside that negative, so the field is still an assignment-owned reference
without an accepted first direct consumer. Its concrete type, indirect use,
other consumers, and lifetime remain unresolved. Exact limits are in
[`scene-root-ref-consumer-boundary.json`](../../manifests/scene-root-ref-consumer-boundary.json).

A fresh vtable-bounded scan tested slots `+0x04`, `+0x08`, `+0x0C`, `+0x10`,
`+0x18`, `+0x1C`, `+0x20`, and `+0x24`. Ghidra found no decoded `+0x44`
operand across 318 instructions, but all eight exact target bodies truncated on
bad instruction data. This is a decode-coverage negative only: none of those
slots is classified as a consumer or non-consumer. The exact targets and stops
are recorded in
[`scene-root-ref-vtable-consumer-boundary.json`](../../manifests/scene-root-ref-vtable-consumer-boundary.json).

## Evidence boundaries

- Publication, render calls, update calls, and teardown do not establish
  successful runtime rendering or visible output.
- The scene render tree is distinct from the scene-active gate and the audio
  manager receiver.
- The wider application callback does not make this a movement-specific update
  owner or establish runtime cadence.
- The lifecycle mapping defines no renderer hook, audio hook, guest-memory
  mutation, API, mod, or SDK behavior.

## Evidence sources

- [Scene render-tree publication](../../manifests/scene-render-tree-publication.json)
- [Scene render-tree update](../../manifests/scene-render-tree-update.json)
- [Scene-root reference consumer boundary](../../manifests/scene-root-ref-consumer-boundary.json)
- [Scene-root vtable reference-consumer boundary](../../manifests/scene-root-ref-vtable-consumer-boundary.json)
- [Gameplay main-frame boundary](../../manifests/gameplay-main-frame-boundary.json)
- [Audio initialization and stream ownership](../../manifests/audio-initialization-stream-ownership.json)
- [Catalog contract](../catalogs.md)
