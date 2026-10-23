# Scene render-tree lifecycle

Scene tree, application scene-update helper and audio receiver are distinct.
Names are recovered, not debug symbols; evidence is static unless stated.

## Tree publication and layout

Initializer `0x82D52AE8` allocates a `0x2C`-byte heap tree, calls `0x82D4BF58`,
and publishes pointer/null at `0x8314F08C`. Constructor installs no vptr.
Layout:

| Offset | Recovered role |
| --- | --- |
| `+0x8` | Incoming render float stored by the tree renderer |
| `+0xC` | Incoming render word stored by the tree renderer |
| `+0x10` | Critical section used by the bounded render path |

Other fields and any scene-tree vtable remain unidentified.

## Render and update edges

Scene render gate `0x82E43830` checks the published tree and its surrounding
anonymous gates, reloads the tree, and calls renderer `0x82D4C348`. The renderer
enters the critical section and stores its incoming values at `+0x8` and `+0xC`
before bounded downstream work.

`SceneUpdateHelper` at `0x82E43B50` is reached from the broader application
update chain. One exact gated caller loads global `0x8314F084` as the receiver
and calls `RenderMgrUpdate` at `0x82D526A0`. That callee separately loads the
scene-tree global at `0x8314F08C` and reaches the bounded tree update edge.

Global `0x8314F084` is the published `0x4C8`-byte audio manager. The exact
receiver qualification does not prove that `RenderMgrUpdate` is an original
audio-manager method or assign full audio semantics to the function. The two
globals remain distinct.

## Teardown

`SceneRenderTreeTeardown` (`0x82D51EC0`) processes the tree, clearing
`0x8314F08C` at `0x82D51F20`; wider shutdown/helper semantics remain open.
`0x82D55834` is a `SceneNodeRenderWrap` fallthrough, not a function or proved
teardown target. Proximity/generated shape establishes no relation.

## Retained scene-root content reference

The `0xA8`-byte scene-root object retains refcounted `+0x44`.
`SceneRootContentSlot0Body` assigns prepared-record `+0x28` via `0x821B2440`,
releasing old/acquiring incoming pointers as needed.

`SceneNodeRenderWrap` (`0x82D55808`) and `SceneNodeRenderVisit` (`0x82D55C68`)
have no direct receiver-relative `+0x44` access; indirect targets remain outside
this negative. First direct consumer, concrete type, indirect/other use and
lifetime remain unknown. See
[`scene-root-references.json#/findings/RVA-F-0094`](../../manifests/scene-root-references.json#/findings/RVA-F-0094).

Slots `+0x04`, `+0x08`, `+0x0C`, `+0x10`, `+0x18`, `+0x1C`, `+0x20`, `+0x24`
yielded no decoded `+0x44` operand in 318 instructions. All eight bodies
truncated on bad data, so none is classified consumer or non-consumer.
Targets/stops:
[`scene-root-references.json#/findings/RVA-F-0104`](../../manifests/scene-root-references.json#/findings/RVA-F-0104).

## Evidence boundaries

- Lifecycle edges prove no successful rendering or visible output.
- Tree, scene-active gate and audio receiver remain distinct.
- Application callbacks establish neither movement-specific ownership nor cadence.
- No renderer/audio hook, memory mutation, API, mod or SDK behavior follows.

## Evidence sources

- [Scene render-tree publication](../../manifests/scene-render-tree-publication.json)
- [Scene render-tree update](../../manifests/scene-render-tree-update.json)
- [`scene-root-references.json#/findings/RVA-F-0094`](../../manifests/scene-root-references.json#/findings/RVA-F-0094)
- [`scene-root-references.json#/findings/RVA-F-0104`](../../manifests/scene-root-references.json#/findings/RVA-F-0104)
- [Gameplay main-frame boundary](../../manifests/gameplay-main-frame-boundary.json)
- [Audio initialization and stream
  ownership](../../manifests/audio-initialization-stream-ownership.json)
- [Catalog contract](../catalogs.md)
