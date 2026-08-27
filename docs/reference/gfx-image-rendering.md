# GFx external-image rendering

The recovered GFx image architecture has two separately evidenced static
flows: external-image creation and upload, and image-backed shape display and
draw submission. Their shared object layers make them useful together, but the
evidence does not assert that one runtime asset traversed every step. Semantic
names are recovered labels, not original debug symbols.

## Object layers

The image path uses distinct objects that must not be collapsed into one
texture identity:

| Layer | Recovered role |
| --- | --- |
| Decoded-image record | Seven-word, vptr-less description of numeric format, dimensions, pitch, data, byte extent, and level bound |
| GFx image resource | Scaleform-side resource or request that owns or refers to decoded image content |
| Renderer texture | `0x30`-byte object holding renderer owner, dimensions, and backend texture pointer |
| Backend texture | `0x34`-byte graphics object whose six-word template feeds a guest fetch-shadow entry |

No layer implies a public graphics format, channel order, platform API object,
or particular asset identity.

## External-image creation and state snapshot

`GfxLoadDefineExternalImageTag` at `0x821E9390` parses the external-image tag
and calls `GfxBuildExternalImageDescriptor` at `0x821E9178`. The latter builds
and registers the deferred `0x28`-byte descriptor.

`GFxImageFileResCreate` at `0x822189A8` creates the Scaleform image-file
request and dispatches its external-image branch through the snapshotted
state-kind-12 creator. Snapshot builder `0x82216D18` records the recovered
state outputs at:

| Snapshot offset | State role |
| --- | --- |
| `+0x10` | State-kind-10 opener used by the bounded external-file decode branch |
| `+0x18` | State-kind-12 creator used by the external-image request branch |

`GfxCreateExternalImage` at `0x821E2F80` opens the descriptor filename,
selects a decoder, allocates a renderer texture through `0x82302DC8`, and
dispatches upload through `GfxUploadRendererTexture` at `0x82304CF0`.

The renderer texture stores its renderer owner at `+0x1C`, width and height at
`+0x20` and `+0x24`, and backend texture at `+0x28`. The decoded record,
renderer texture, and backend texture remain separate ownership layers.

## Decoded-image and conversion contract

The `0x1C`-byte decoded-image record has this bounded layout:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Numeric format selector |
| `+0x4` | Width |
| `+0x8` | Height |
| `+0xC` | Level-zero pitch or row stride |
| `+0x10` | Base data pointer |
| `+0x14` | Byte extent |
| `+0x18` | Level bound |

`GfxFormatLevelExtent` at `0x821E04A8` and `GfxSelectMipSource` at
`0x821E0568` enforce the supported extent, level, and derived-pointer bounds.
The generic upload path may call `GfxTemporaryDecodedImageCreate` at
`0x821E08D8`. It allocates a `0x38`-byte temporary conversion object, calls
initializer `0x821E0720`, validates embedded base storage and nonzero
dimensions, and returns null through its bounded cleanup path on failure. The
embedded decoded record begins at `+0x10`. Upload-local helper `0x82304B38`
handles the supported non-power-of-two conversion path.

Backend submission reaches `GfxBackendUploadRegion` at `0x82578E00`. Direct
and mip paths supply the selected source, numeric format, pitch, and rectangle;
the helper validates required inputs, prepares bounded region state, and
returns a status. This remains a static guest-code boundary and does not
establish host graphics API semantics. Numeric formats, byte lanes, channel
order, and alpha meaning remain unnamed.

## Image-backed shape and direct fill

`GfxImageFileMovieShapeInitialize` at `0x82235830` creates a `0x90`-byte
synthetic shape and calls `GfxImageShapeImageInitialize` at `0x821F82D8`.
The shape owns a fill-style array through fields `+0x64`, `+0x68`, and `+0x6C`.
The initializer resizes that array to one `0x28`-byte direct image-fill entry.

The bounded fill entry contains:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Fill type byte |
| `+0x1` | Fill flags byte |
| `+0x8` | Resource-handle kind, observed as zero on this path |
| `+0xC` | Decoded GFx image-resource pointer |

`GfxImageFillTextureResolve` at `0x8225BC48` resolves the resource through the
display context and writes the renderer-texture pointer at output `+0x0` on
its bounded successful path. `GfxMeshResourceSourceSubmit` at `0x82266358`
then supplies resolved resources to the renderer fill-state boundary.

This static handoff proves neither execution for a specific asset nor visible
output.

## Source tables and fill descriptors

The temporary source-table view pairs a primary base at `+0x4` with its
authoritative count at `+0x48`. Entries are `0x28` bytes. Candidate indices are
checked against the count before an entry is addressed.

Each `0x28`-byte fill descriptor begins with a coherent mapping tuple:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Number of valid source selectors |
| `+0x4` | Three selector words. Unused entries are `0xFFFFFFFF` |
| `+0x10` | Coupled fill subtype |

`GfxFillDescriptorResize` at `0x82269590` initializes that tuple to zero
sources, unused selectors, and subtype zero. `GfxCoupledFillMeshBuild` at
`0x822688C0` selects the simple or complex writer from bounded source and
renderer-configuration inputs. `GfxSimpleFillVertexWrite` at `0x822CA118`
hands its vertex stream to `GfxMeshIndexProduce` at `0x822C9F78`. The complex
writer at `0x822CA718` publishes resource cardinality and fill subtype as one
coupled result.

The mapping count, selectors, subtype, and selected vertex format are one
contract. None should be interpreted or changed independently.

## Renderer capability invariant

`GfxRendererGetCaps` at `0x82302E90` reports inactive status without a valid
capability record. When active, the bounded result includes capability bits
`0x330C`, vertex formats `0x1B`, blend modes `0x36B`, and maximum texture size
8192. Vertex-format bit `0x10` is the declared `Vertex_XY16iCF32` capability,
not a transform flag.

Static producer evidence ties the capability snapshot to simple-versus-complex
fill selection. Bounded runtime observation shows an inactive snapshot selecting
the simple path and a successful query from the same renderer restoring the
existing complex textured path. This ownership and ordering invariant does not
define a forced capability bit, fill subtype, selector, hook, or SDK change.

## Renderer state and indexed draw

Four narrow setters publish active geometry state:

| Function | Address | Recovered role |
| --- | ---: | --- |
| `GfxSetRendererMatrix` | `0x82303650` | Copies the six-word GFx matrix into renderer state |
| `GfxSetRendererFillState` | `0x82303BE0` | Dispatches fill state into renderer subobjects |
| `GfxSetRendererVertexState` | `0x82303BF0` | Stores vertex-buffer pointer and format |
| `GfxSetRendererIndexState` | `0x82303C00` | Stores index-buffer pointer and normalized format |

`GfxIndexedDraw` at `0x82303C38` checks active state, vertex and index buffers,
index format, and positive count. It applies fill state, composes the supplied
affine transform with renderer matrix state through `0x823038D8`, and reaches
`GraphicsFlushAndIssue` at `0x826A3568` after the draw gates pass.

Other bounded setup functions include color transform `0x823029B8`, viewport
setup `0x82302F60`, and blend setup `0x823036D0`. The last two names describe
only their recovered roles. Their wider state ownership remains unresolved.

## Guest fetch and command emission

`GraphicsFlushAndIssue` forwards to `GraphicsDirtyStateAndDrawPrepare` at
`0x826A3048`. That path reaches `FetchDirtyRunPacketEmit` at `0x826ACEA0`,
which converts contiguous dirty texture ordinals into guest register-write
runs. `CommandRangeRolloverWriter` at `0x826AC610` handles the bounded rollover
case.

The recovered fetch allocation is non-overlapping:

- Texture fetch 0 occupies guest registers `0x4800` through `0x4805`.
- Logical vertex fetch 0 occupies guest registers `0x48BE` and `0x48BF` in the
  immediate indexed-draw state.

Renderer slot 0, selected shadow index `0x30`, and normalized texture ordinal 0
are related stages, not interchangeable identities.

## Evidence boundaries

- The draw, fetch, conversion, viewport, and blend mappings do not by themselves
  establish visible runtime output.
- No specific movie, logo, image, dimensions, descriptor values, buffer
  contents, shader behavior, visible output, or presentation result is
  inferred.
- The mappings define no public texture-format name, channel order, platform
  graphics API meaning, forced capability, runtime hook, guest-memory write, or
  SDK behavior.
- MovieClipLoader request flow is not connected to this external-image path by
  a bounded tracked edge.

## Evidence sources

- [GFx Scaleform image creation](../../manifests/gfx-scaleform-image-creation.json)
- [GFx decoded-image upload](../../manifests/gfx-decoded-image-upload.json)
- [GFx mip-source selection](../../manifests/gfx-mip-source-selection.json)
- [GFx format-10 image decoder](../../manifests/gfx-format10-image-decoder.json)
- [GFx image-movie shape display](../../manifests/gfx-image-movie-shape-display.json)
- [GFx source-count contract](../../manifests/gfx-source-count-contract.json)
- [GFx coupled-fill producer](../../manifests/gfx-coupled-fill-producer.json)
- [GFx complex fill](../../manifests/gfx-complex-fill.json)
- [GFx renderer state setters](../../manifests/gfx-renderer-state-setters.json)
- [GFx draw producer](../../manifests/gfx-draw-producer.json)
- [GFx backend fetch descriptor](../../manifests/gfx-backend-fetch-descriptor.json)
- [GFx fetch allocation](../../manifests/gfx-fetch-allocation.json)
- [GFx dirty-fetch packet](../../manifests/gfx-dirty-fetch-packet.json)
- [Catalog contract](../catalogs.md)
