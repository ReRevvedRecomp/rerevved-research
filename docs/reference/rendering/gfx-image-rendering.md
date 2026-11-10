# GFx external-image rendering

Two static flows share object layers: creating and uploading an external image,
and submitting an image-backed shape and draw. No runtime asset is shown to pass
through all steps. Names are recovered, not debug symbols. The findings do not
establish visible output, asset identity or host graphics API behavior.

## Object layers

The image path uses distinct objects that must not be collapsed into one texture
identity:

| Layer | Recovered role |
| --- | --- |
| Decoded-image record | Description of numeric format, dimensions, pitch, data, byte extent, and level bound in seven words, without a vptr |
| GFx image resource | Scaleform-side resource or request that holds or refers to decoded image content |
| Renderer texture | `0x30`-byte object holding the renderer pointer, dimensions, and backend texture pointer |
| Backend texture | `0x34`-byte graphics object whose six-word template feeds a guest fetch-shadow entry |

No layer implies a public graphics format, channel order, platform API object,
or particular asset identity.

## External-image creation and state snapshot

`GfxLoadDefineExternalImageTag` (`0x821E9390`) parses the tag and then calls
`GfxBuildExternalImageDescriptor` (`0x821E9178`), which builds and registers a
deferred `0x28`-byte descriptor. `GFxImageFileResCreate` (`0x822189A8`) creates a
request and dispatches the snapshotted kind-12 creator. `0x82216D18` keeps ten
outputs:

| Snapshot offset | State role |
| --- | --- |
| `+0x10` | Opener for state kind 10 used by the selected external-file decode branch |
| `+0x14` | Output for state kind 11; role unnamed |
| `+0x18` | Creator for state kind 12 used by the external-image request branch |
| `+0x1C` | Output for state kind 15; role unnamed |
| `+0x20` | Output for state kind 21; role unnamed |
| `+0x24` | Output for state kind 16; role unnamed |
| `+0x28` | Output for state kind 19; role unnamed |
| `+0x2C` | Output for state kind 18; role unnamed |
| `+0x30` | Output for state kind 20; role unnamed |
| `+0x34` | Output for state kind 25; role unnamed |

GFx kinds are not gameplay enums, and they are not interchangeable with timing,
callback, input or availability state. Live values are not yet established.
`GfxCreateExternalImage` (`0x821E2F80`) opens the file name, selects a decoder,
allocates through `0x82302DC8`, and then calls `GfxUploadRendererTexture`
(`0x82304CF0`). The texture fields are the renderer pointer at `+0x1C`, the width
at `+0x20`, the height at `+0x24` and the backend texture at `+0x28`. The object
layers stay distinct.

## Decoded-image and conversion contract

The `0x1C`-byte decoded-image record has this layout:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Numeric format selector |
| `+0x4` | Width |
| `+0x8` | Height |
| `+0xC` | Pitch at level zero or row stride |
| `+0x10` | Base data pointer |
| `+0x14` | Byte extent |
| `+0x18` | Level bound |

`GfxFormatLevelExtent` (`0x821E04A8`) and `GfxSelectMipSource` (`0x821E0568`)
enforce limits on extent, level and pointer. The optional
`GfxTemporaryDecodedImageCreate` (`0x821E08D8`) allocates `0x38` bytes,
initializes through `0x821E0720`, checks the base storage and that the
dimensions are nonzero, and cleans up to null on failure. The embedded record is
at `+0x10`. `0x82304B38` handles the supported non-power-of-two conversion.
`GfxBackendUploadRegion` (`0x82578E00`) validates the direct or mip source, the
numeric format, the pitch and the rectangle, prepares the region state, and
returns a status. Formats, byte layout, channel order and alpha remain unnamed.

## Image-backed shape and direct fill

`GfxImageFileMovieShapeInitialize` (`0x82235830`) creates a `0x90`-byte shape.
`GfxImageShapeImageInitialize` (`0x821F82D8`) then resizes the array that
belongs to the shape, at `+0x64`, `+0x68` and `+0x6C`, to one `0x28`-byte direct
fill:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Fill type byte |
| `+0x1` | Fill flags byte |
| `+0x8` | Resource-handle kind, observed as zero on this path |
| `+0xC` | Decoded GFx image-resource pointer |

`GfxImageFillTextureResolve` (`0x8225BC48`) resolves through the display context
and writes the texture to output `+0x0` on success. `GfxMeshResourceSourceSubmit`
(`0x82266358`) passes the resolved resources to fill state.

## Source tables and fill descriptors

The source table has its base at `+0x4`, its authoritative count at `+0x48` and
stride `0x28`. A bounds check comes before addressing. Fill descriptors begin
with a coupled tuple:

| Offset | Recovered role |
| --- | --- |
| `+0x0` | Number of valid source selectors |
| `+0x4` | Three selector words. Unused entries are `0xFFFFFFFF` |
| `+0x10` | Coupled fill subtype |

`GfxFillDescriptorResize` (`0x82269590`) zeros the count and subtype and marks
the selectors unused. `GfxCoupledFillMeshBuild` (`0x822688C0`) chooses the
simple or complex path from the source and configuration.
`GfxSimpleFillVertexWrite` (`0x822CA118`) feeds `GfxMeshIndexProduce`
(`0x822C9F78`). The complex path at `0x822CA718` publishes the coupled
cardinality and subtype. The count, selectors, subtype and vertex format must
stay coherent.

## Renderer capability invariant

`GfxRendererGetCaps` at `0x82302E90` reports inactive status without a valid
capability record. When active, the result includes:

| Capability | Value |
| --- | --- |
| Capability bits | `0x330C` |
| Vertex formats | `0x1B` |
| Blend modes | `0x36B` |
| Maximum texture size | 8192 |

Vertex-format bit `0x10` is the declared `Vertex_XY16iCF32` capability, not a
transform flag.

The snapshot controls the choice between the simple and the complex path. A
runtime observation saw an inactive snapshot select the simple path, and then a
successful query on the same renderer restore complex texturing. This defines no
forced bit, subtype or selector, no hook and no SDK change.

## Renderer state and indexed draw

| Function | Address | Recovered role |
| --- | ---: | --- |
| `GfxSetRendererMatrix` | `0x82303650` | Copies the six-word GFx matrix into renderer state |
| `GfxSetRendererFillState` | `0x82303BE0` | Dispatches fill state into renderer subobjects |
| `GfxSetRendererVertexState` | `0x82303BF0` | Stores vertex-buffer pointer and format |
| `GfxSetRendererIndexState` | `0x82303C00` | Stores index-buffer pointer and normalized format |

`GfxIndexedDraw` (`0x82303C38`) checks the state, the buffers, the index format
and a positive count, applies the fill, composes the affine transform through
`0x823038D8`, and then reaches `GraphicsFlushAndIssue` (`0x826A3568`). The
direct inventory finds one data reference, `0x82169E6C`, which is vtable
`0x82169E30 + 0x3C`, and no code caller. The slot is confirmed. Dynamic sites
and renderer families remain unknown. Color `0x823029B8`, viewport `0x82302F60`
and blend `0x823036D0` have only local roles; their wider use is unknown.

CPU shader selection patches vertex fetches before cursor publication, and
`0x826AD150` patches the copied code before the cursor is published. The common exit `0x826AE5B8`
keeps persistent variant metadata that identifies the physical program and word
count, including for reused patched programs. Pixel code uses the graphics
`+0x3194` object. The viewport, the derived scale and offset, and the separately
clipped scissor are stored in state. The
[CPU contract](../../../manifests/gfx-draw-producer.json) records the arithmetic,
the arguments, the offsets and the listing limits. CPU shadows do not show any
later tile overrides.

## Affine and vertex constant records

`GfxIndexedDraw` writes its transform into four vertex shader constant
records, c0 to c3. The producer `0x823038D8` copies the six floats at renderer
`+0xE4`..`+0xF8` (the projection record) to its own stack frame, then calls the
composer `0x82259C80` with that copy as `P` and the six floats at renderer
`+0xFC`..`+0x110` as `M`. The draw setup call at `0x82303DB4` supplies that
matrix. The composer's result is `P` times `M`, with `P` on the left. In the
selected instructions `mad` is a fused multiply and add, and `mul` and `add`
round each result to single precision:

```text
c0 = mad(m3,p1, mul(m0,p0))    c3 = mad(m3,p4, mul(m0,p3))
c1 = mad(p1,m4, mul(p0,m1))    c4 = mad(p4,m4, mul(p3,m1))
c2 = add(mad(p1,m5, mul(p0,m2)), p2)
c5 = add(mad(p4,m5, mul(p3,m2)), p5)
```

The producer then writes four records straight into the graphics device's
vertex float shadow, with `Z` as the zero stored at `0x8211B944` and `H` as the
one stored at `0x8211CE4C`:

| Record | Graphics bytes | x, y, z, w | Register words |
|---|---|---|---|
| c0 | `+0x780` to `+0x78F` | c0, c1, Z, c2 | `0x4000` to `0x4003` |
| c1 | `+0x790` to `+0x79F` | c3, c4, Z, c5 | `0x4004` to `0x4007` |
| c2 | `+0x7A0` to `+0x7AF` | Z, Z, H, Z | `0x4008` to `0x400B` |
| c3 | `+0x7B0` to `+0x7BF` | Z, Z, Z, H | `0x400C` to `0x400F` |

That is 16 words, 64 bytes, the same extent as a setter call with start 0 and
count 4. The producer does not call the vertex float setter `0x82692588`. After
each record it ORs the high bit into the 64 bit dirty word at the device's `+0`.

Worked example (small values that are exact in single precision). Take
`P = (2, 3, 5, 7, 11, 13)` and `M = (17, 19, 23, 29, 31, 37)`. The six results
are `(121, 131, 162, 438, 474, 581)`, so the records are
`(121, 131, 0, 162)`, `(438, 474, 0, 581)`, `(0, 0, 1, 0)` and `(0, 0, 0, 1)`.
Composing in the other order would give `(167, 260, 355, 275, 428, 585)`.

These equations assume that the composer's output does not overlap its `M`
input, that all four reads of the device pointer at renderer `+0xB8` see the
same device, and that nothing changes the stack record between composition and
the shadow stores. They do not show which shader reads these constants. Nothing here
shows them as texture coordinate generation. Any code that edits the record
between composition and the stores changes the constants. The guest code has no
such edit. Evidence:
[the composer and shadow writes](../../../manifests/gfx-draw-producer.json#/currentEvidence/nativeInputRefinement/composer),
[the record table](../../../manifests/gfx-draw-producer.json#/currentEvidence/nativeInputRefinement/shadowWrites)
and [the matrix setter](../../../manifests/gfx-renderer-state-setters.json#/matrixSetter).

Movie frames use a separate draw path, covered in
[movie draw binding](movie-draw-binding.md).

## Guest fetch and command emission

`GraphicsFlushAndIssue` calls `GraphicsDirtyStateAndDrawPrepare` (`0x826A3048`),
which calls `FetchDirtyRunPacketEmit` (`0x826ACEA0`). That function converts
contiguous dirty texture ordinals to register runs. `CommandRangeRolloverWriter`
(`0x826AC610`) handles rollover.

The indexed wrapper consumes the geometry and stride at `SP+84`. After the
lowerer succeeds, it copies the vertex span and the index span, with the index span rounded to a
multiple of four bytes, into upload buffers and publishes the cursor. The return
value is the index-copy result, not the lowerer status. The
[draw contract](../../../manifests/gfx-draw-producer.json) records the arguments
and sites.

The fetches do not overlap. Texture 0 uses `0x4800` through `0x4805`. Logical
vertex 0 uses `0x48BE` and `0x48BF` in immediate indexed state. Renderer slot 0,
shadow index `0x30` and normalized texture ordinal 0 are related but not
interchangeable.

## Evidence boundaries

- No movie, logo or image, dimensions, descriptor or buffer values, shader
  behavior or presentation result is inferred beyond the stated observations.
- No public format, channel order, graphics API, forced capability, hook,
  memory write or SDK behavior follows.
- No tracked edge in the selected paths links MovieClipLoader to this path.

## Evidence sources

- [GFx Scaleform image creation](../../../manifests/gfx-scaleform-image-creation.json)
- [GFx decoded-image upload](../../../manifests/gfx-decoded-image-upload.json)
- [GFx mip-source selection](../../../manifests/gfx-mip-source-selection.json)
- [GFx format-10 image decoder](../../../manifests/gfx-format10-image-decoder.json)
- [GFx image-movie shape display](../../../manifests/gfx-image-movie-shape-display.json)
- [GFx source-count contract](../../../manifests/gfx-source-count-contract.json)
- [GFx coupled-fill producer](../../../manifests/gfx-coupled-fill-producer.json)
- [GFx complex fill](../../../manifests/gfx-complex-fill.json)
- [GFx renderer state setters](../../../manifests/gfx-renderer-state-setters.json)
- [GFx draw producer](../../../manifests/gfx-draw-producer.json)
- [GFx backend fetch descriptor](../../../manifests/gfx-backend-fetch-descriptor.json)
- [GFx fetch allocation](../../../manifests/gfx-fetch-allocation.json)
- [GFx nonindexed UP draw boundary](../../../manifests/gfx-nonindexed-up-draw.json)
- [Bound indexed draw and CPU fetch
  array](../../../manifests/menu-indexed-buffer-draw.json)
- [GFx dirty-fetch run emission](../../../manifests/gfx-dirty-fetch-packet.json)
- [Catalog contract](../../catalogs.md)
