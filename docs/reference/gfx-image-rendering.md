# GFx external-image rendering

Two static flows share object layers: external-image creation/upload and
image-backed shape/draw submission. No runtime asset is proved to traverse all
steps. Names are recovered, not debug symbols; findings do not establish visible
output, asset identity or host graphics API semantics.

## Object layers

The image path uses distinct objects that must not be collapsed into one texture
identity:

| Layer | Recovered role |
| --- | --- |
| Decoded-image record | Description of numeric format, dimensions, pitch, data, byte extent, and level bound in seven words, without a vptr |
| GFx image resource | Scaleform-side resource or request that owns or refers to decoded image content |
| Renderer texture | `0x30`-byte object holding renderer owner, dimensions, and backend texture pointer |
| Backend texture | `0x34`-byte graphics object whose six-word template feeds a guest fetch-shadow entry |

No layer implies a public graphics format, channel order, platform API object,
or particular asset identity.

## External-image creation and state snapshot

`GfxLoadDefineExternalImageTag` (`0x821E9390`) parses then calls
`GfxBuildExternalImageDescriptor` (`0x821E9178`) to build/register deferred
`0x28`-byte descriptor. `GFxImageFileResCreate` (`0x822189A8`) creates request
and dispatches snapshotted kind-12 creator. `0x82216D18` retains ten outputs:

| Snapshot offset | State role |
| --- | --- |
| `+0x10` | Opener for state kind 10 used by the bounded external-file decode branch |
| `+0x14` | Output for state kind 11; role unnamed |
| `+0x18` | Creator for state kind 12 used by the external-image request branch |
| `+0x1C` | Output for state kind 15; role unnamed |
| `+0x20` | Output for state kind 21; role unnamed |
| `+0x24` | Output for state kind 16; role unnamed |
| `+0x28` | Output for state kind 19; role unnamed |
| `+0x2C` | Output for state kind 18; role unnamed |
| `+0x30` | Output for state kind 20; role unnamed |
| `+0x34` | Output for state kind 25; role unnamed |

GFx kinds are not gameplay enums or interchangeable timing/callback/input/
availability state; live values are unproved. `GfxCreateExternalImage`
(`0x821E2F80`) opens filename, selects decoder, allocates via `0x82302DC8`, then
calls `GfxUploadRendererTexture` (`0x82304CF0`). Texture fields: owner `+0x1C`,
width/height `+0x20`/`+0x24`, backend `+0x28`; ownership layers remain distinct.

## Decoded-image and conversion contract

The `0x1C`-byte decoded-image record has this bounded layout:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Numeric format selector |
| `+0x4` | Width |
| `+0x8` | Height |
| `+0xC` | Pitch at level zero or row stride |
| `+0x10` | Base data pointer |
| `+0x14` | Byte extent |
| `+0x18` | Level bound |

`GfxFormatLevelExtent` (`0x821E04A8`)/`GfxSelectMipSource` (`0x821E0568`)
enforce extent/level/pointer bounds. Optional `GfxTemporaryDecodedImageCreate`
(`0x821E08D8`) allocates `0x38`, initializes via `0x821E0720`, checks base
storage/nonzero dimensions, and cleans up to null on failure. Embedded record is
`+0x10`; `0x82304B38` handles supported non-power-of-two conversion.
`GfxBackendUploadRegion` (`0x82578E00`) validates direct/mip source, numeric
format, pitch and rectangle, prepares region state and returns status. Formats,
byte lanes, channel order and alpha remain unnamed.

## Image-backed shape and direct fill

`GfxImageFileMovieShapeInitialize` (`0x82235830`) creates `0x90`-byte shape,
then `GfxImageShapeImageInitialize` (`0x821F82D8`) resizes owned array
`+0x64`/`+0x68`/`+0x6C` to one `0x28`-byte direct fill:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Fill type byte |
| `+0x1` | Fill flags byte |
| `+0x8` | Resource-handle kind, observed as zero on this path |
| `+0xC` | Decoded GFx image-resource pointer |

`GfxImageFillTextureResolve` (`0x8225BC48`) resolves through display context,
writing output `+0x0` texture on success; `GfxMeshResourceSourceSubmit`
(`0x82266358`) passes resolved resources to fill state.

## Source tables and fill descriptors

Source table: base `+0x4`, authoritative count `+0x48`, stride `0x28`; bounds
check precedes addressing. Fill descriptors begin with coupled tuple:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Number of valid source selectors |
| `+0x4` | Three selector words. Unused entries are `0xFFFFFFFF` |
| `+0x10` | Coupled fill subtype |

`GfxFillDescriptorResize` (`0x82269590`) zeros count/subtype, marks selectors
unused. `GfxCoupledFillMeshBuild` (`0x822688C0`) chooses simple/complex from
source/configuration. `GfxSimpleFillVertexWrite` (`0x822CA118`) feeds
`GfxMeshIndexProduce` (`0x822C9F78`); complex `0x822CA718` publishes coupled
cardinality/subtype. Count/selectors/subtype/vertex format must remain coherent.

## Renderer capability invariant

`GfxRendererGetCaps` at `0x82302E90` reports inactive status without a valid
capability record. When active, the bounded result includes:

| Capability | Value |
| --- | --- |
| Capability bits | `0x330C` |
| Vertex formats | `0x1B` |
| Blend modes | `0x36B` |
| Maximum texture size | 8192 |

Vertex-format bit `0x10` is the declared `Vertex_XY16iCF32` capability, not a
transform flag.

Snapshot controls simple/complex choice. Runtime observation saw inactive
snapshot select simple, then successful same-renderer query restore complex
texturing. This defines no forced bit/subtype/selector, hook or SDK change.

## Renderer state and indexed draw

| Function | Address | Recovered role |
| --- | ---: | --- |
| `GfxSetRendererMatrix` | `0x82303650` | Copies the six-word GFx matrix into renderer state |
| `GfxSetRendererFillState` | `0x82303BE0` | Dispatches fill state into renderer subobjects |
| `GfxSetRendererVertexState` | `0x82303BF0` | Stores vertex-buffer pointer and format |
| `GfxSetRendererIndexState` | `0x82303C00` | Stores index-buffer pointer and normalized format |

`GfxIndexedDraw` (`0x82303C38`) checks state/buffers/index format/positive
count, applies fill, composes affine transform via `0x823038D8`, then reaches
`GraphicsFlushAndIssue` (`0x826A3568`). Direct inventory: one data reference
`0x82169E6C` = vtable `0x82169E30 + 0x3C`, no code caller. Slot is bound;
dynamic sites/renderer families remain unknown. Color `0x823029B8`, viewport
`0x82302F60` and blend `0x823036D0` have only local roles/unknown wider
ownership.

CPU shader selection patches vertex fetches before cursor publication;
`0x826AD150` receives immediate patched code. Common exit `0x826AE5B8` retains
persistent variant metadata identifying physical program/word count, including
reused patched programs. Pixel code uses graphics `+0x3194` object.
Viewport/derived scale-offset and separately clipped scissor are stored in
state; [CPU contract](../../manifests/gfx-draw-producer.json) owns
arithmetic/arguments/ offsets/listing limits. CPU shadows prove no later tile
overrides.

## Guest fetch and command emission

`GraphicsFlushAndIssue` -> `GraphicsDirtyStateAndDrawPrepare` (`0x826A3048`) ->
`FetchDirtyRunPacketEmit` (`0x826ACEA0`) converts contiguous dirty texture
ordinals to register runs; `CommandRangeRolloverWriter` (`0x826AC610`) handles
rollover.

Indexed wrapper consumes geometry/stride `SP+84`. After lowerer success it
copies vertex span and index span rounded to a multiple of four bytes into
upload buffers, publishing cursor. Return is index-copy result, not lowerer
status; [draw contract](../../manifests/gfx-draw-producer.json) owns
arguments/sites.

Nonoverlapping fetches: texture 0 = `0x4800` through `0x4805`; logical vertex 0
= `0x48BE`/`0x48BF` in immediate indexed state. Renderer slot 0, shadow index
`0x30`, normalized texture ordinal 0 are related, not interchangeable.

## Evidence boundaries

- No movie/logo/image, dimensions, descriptor/buffer values, shader behavior or
  presentation result is inferred beyond stated observations.
- No public format, channel order, graphics API, forced capability, hook,
  memory write or SDK behavior follows.
- No bounded tracked edge joins MovieClipLoader to this path.

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
- [GFx nonindexed UP draw boundary](../../manifests/gfx-nonindexed-up-draw.json)
- [Bound indexed draw and CPU fetch
  array](../../manifests/menu-indexed-buffer-draw.json)
- [GFx dirty-fetch packet](../../manifests/gfx-dirty-fetch-packet.json)
- [Catalog contract](../catalogs.md)
