# Scene render-tree lifecycle

The scene tree, the application scene-update helper and the audio receiver are
distinct. Names are recovered, not debug symbols. Evidence is static unless
stated.

## Tree publication and layout

The initializer `0x82D52AE8` allocates a `0x2C`-byte heap tree, calls
`0x82D4BF58`, and publishes the pointer, or null, at `0x8314F08C`. The
constructor installs no vptr. The layout is:

| Offset | Recovered role |
| --- | --- |
| `+0x8` | Incoming render float stored by the tree renderer |
| `+0xC` | Incoming render word stored by the tree renderer |
| `+0x10` | Critical section used by the selected render path |

Other fields and any scene-tree vtable remain unidentified.

## Render and update edges

The scene render check at `0x82E43830` tests the published tree and its
surrounding anonymous checks, reloads the tree, and calls the renderer
`0x82D4C348`. The renderer enters the critical section and stores its incoming
values at `+0x8` and `+0xC` before the downstream work that was selected for
inspection.

`SceneUpdateHelper` at `0x82E43B50` is reached from the broader application
update chain. One exact caller, which runs only when its check passes, loads
global `0x8314F084` as the receiver and calls `RenderMgrUpdate` at `0x82D526A0`.
That callee separately loads the scene-tree global at `0x8314F08C` and reaches
the selected tree update edge.

Global `0x8314F084` is the published `0x4C8`-byte audio manager. The exact
receiver qualification does not show that `RenderMgrUpdate` is an original
audio-manager method, and it does not assign full audio semantics to the
function. The two globals remain distinct.

## Teardown

`SceneRenderTreeTeardown` (`0x82D51EC0`) processes the tree and clears
`0x8314F08C` at `0x82D51F20`. The wider shutdown and helper behavior remain
unresolved. `0x82D55834` is a fallthrough within `SceneNodeRenderWrap`, not a
function or an established teardown target. Address proximity and the shape of
the recompiled code do not establish a relationship.

## Scene-root content reference

The `0xA8`-byte scene-root object keeps a reference-counted pointer at `+0x44`.
`SceneRootContentSlot0Body` assigns prepared-record `+0x28` through `0x821B2440`,
releasing the old pointer and acquiring the incoming pointer as needed.

`SceneNodeRenderWrap` (`0x82D55808`) and `SceneNodeRenderVisit` (`0x82D55C68`)
have no direct receiver-relative `+0x44` access. Indirect targets are outside
this negative result. The first direct consumer, the concrete type, any indirect
or other use, and the lifetime remain unknown. See
[`scene-root-references.json#/findings/RVA-F-0094`](../../manifests/scene-root-references.json#/findings/RVA-F-0094).

Slots `+0x04`, `+0x08`, `+0x0C`, `+0x10`, `+0x18`, `+0x1C`, `+0x20` and `+0x24`
yielded no decoded `+0x44` operand in 318 instructions. All eight bodies were
truncated on bad data, so none is classified as a consumer or a non-consumer.
The targets and stops are in
[`scene-root-references.json#/findings/RVA-F-0104`](../../manifests/scene-root-references.json#/findings/RVA-F-0104).

## Evidence boundaries

- Lifecycle edges show no successful rendering or visible output.
- The tree, the scene-active check and the audio receiver remain distinct.
- Application callbacks establish neither movement-specific behavior nor cadence.
- No renderer or audio hook, memory mutation, API, mod or SDK behavior follows.

## Evidence sources

- [Scene render-tree publication](../../manifests/scene-render-tree-publication.json)
- [Scene render-tree update](../../manifests/scene-render-tree-update.json)
- [`scene-root-references.json#/findings/RVA-F-0094`](../../manifests/scene-root-references.json#/findings/RVA-F-0094)
- [`scene-root-references.json#/findings/RVA-F-0104`](../../manifests/scene-root-references.json#/findings/RVA-F-0104)
- [Gameplay main-frame boundary](../../manifests/gameplay-main-frame.json)
- [Audio initialization and stream
  setup](../../manifests/audio-initialization-stream-ownership.json)
- [Catalog contract](../catalogs.md)
