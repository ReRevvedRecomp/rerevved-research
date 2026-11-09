# NIF scene data and draw inputs

The game stores 3D objects as NIF scene files. This page summarizes what the
guest code does with the geometry, transform, material and texture records of
a loaded NIF, and what is still not shown: no accepted evidence ties one loaded
NIF shape to the buffers, constants and textures of a draw call. The page
describes file and object layouts only. It does not describe skinning, bone
palettes or animation.

## What a shape holds

A shape (`NiTriShape`) points to geometry data (`NiTriShapeData`) and to a list
of properties. A material property and a texturing property sit side by side in
that list. A texturing property refers to source textures, which name the image
files. There is no direct link from a material to a texture.

| Record | What the guest keeps | Manifest |
|---|---|---|
| Triangle geometry | Vertex count as a u16 at `+0x0C`. Positions at `+0x20`, exactly count times 12 bytes. Normals at `+0x24`. Triangle count at `+0x40`, packed list length at `+0x44`, packed three u16 triangle storage at `+0x48`. | [F0123](../../manifests/nif-trishapedata.json#/findings/RVA-F-0123/geometryContract) |
| Normal sharing | Groups at `+0x4C` and `+0x50`. Sharing adds contributions from each group. It does not average by group size or promise equal final normals. | [F0122](../../manifests/nif-trishapedata.json#/findings/RVA-F-0122/semanticPromotion) |
| Transforms | Local rotation, translation and scale at `+0x20`, `+0x50` and `+0x5C`. World fields at `+0x60`, `+0x90` and `+0x9C`. Parent at `+0x18`. | [F0125](../../manifests/nif-scene-transform-contract.json#/runtimeLayout) |
| Material | A 56 byte payload: four Color3 values, then glossiness and alpha. Runtime fields at `+0x1C`, `+0x28`, `+0x34`, `+0x40`, `+0x4C` and `+0x50`. Values stay as decoded f32. | [F0129](../../manifests/nif-material-property-field-contract.json#/derivedLayout) |
| Texturing property | Nine standard slots (Base, Dark, Detail, Gloss, Glow, Bump, Normal, Parallax, Decal 0) plus a separate shader suffix. A texture descriptor holds a source reference, flags, a presence bit and an optional 32 byte transform. | [F0130](../../manifests/nif-texturing-property-field-contract.json#/slotContract) |
| Source texture | A 24 byte derived profile that stores both a filename index and a Pixel Data reference. | [F0131](../../manifests/nif-source-texture-field-contract.json#/derivedLayout) |
| External lookup | With Use External set to 1, a nonnull filename index and null Pixel Data, the filename string at `+0x30` leads to the runtime filename at `+0x34`, then to a lazily converted resource at `+0x3C`. | [F0132](../../manifests/nif-external-texture-lookup-policy.json#/lookupChain) |

The relationships between these records come from
[F0124](../../manifests/nif-scene-material-texture-relationships.json#/sceneEdges).
F0120 and F0121 in [the geometry family](../../manifests/nif-trishapedata.json)
cover the method table and the match group domain. The seven files linked on
this page are the NIF manifests.

## Placing a vertex in the world

World placement uses column vectors. With P for the parent and L for the
shape's own local record:

```text
sW = sP * sL
RW = RP * RL
tW = tP + sP * (RP * tL)
```

A root copies its 64 byte local region to its world region. Apply the shape's
local transform first, then each ancestor from the nearest parent to the root.
The file stores a rotation in 36 bytes (nine f32). The runtime object pads it
to 48 bytes.

Worked example. A parent has scale 2, no rotation and translation (10, 0, 0).
A shape has scale 3, no rotation and local translation (1, 0, 0). The world
scale is 6 and the world translation is (10, 0, 0) + 2 * (1, 0, 0) = (12, 0, 0).

## What is not shown

A draw call works from device state: vertex and index buffers, shader objects
and constant registers. These steps have no accepted link from that state to a
NIF shape:

- Geometry. No loaded shape or data instance is tied to a vertex fetch or index
  object. The first reader at `0x8250B668` is not shown to submit geometry.
- World transform. The guest code that reads the world fields `+0x60`, `+0x90`
  and `+0x9C` and writes a shader constant is not identified.
- Material and texture. No material field is tied to a shader constant, texture
  operation, lighting equation or blend setting. Slot names do not give hardware
  sampler numbers or UV sets. The external lookup has no accepted root folder or
  archive namespace.
- Skinning. Whether a vertex shader uses weight or index attributes, and where
  a palette would come from, is open. A byte attribute in a draw does not show
  a skin source.

The anchor draw site at `0x8230686C` (`0x82306868 -> 0x826A39F8`) is accepted
as a call chain in
[the anchor manifest](../../manifests/native-renderer-anchor-draw-sites.json),
without subsystem, asset or shader identity. Its fog comment does not extend
that.

## Limits

- A material value kept as decoded f32 does not allow clamping, color space
  conversion or renderer defaults.
- Raw file fields are not all kept in the runtime object: texture flags are
  masked with `0xF00F`, and the Shader Map ID is read and then written as zero.
- Observations of the shared texture provider show registration and stream
  matches only. They do not show insertion order, a successful lookup or a
  texture binding.
- Terrain, particles, water and shader generation have their own records and
  are not covered by the NIF contracts. See
  [shader constants](native-renderer-shader-constants.md) and
  [draw fields](native-renderer-draw-fields.md).

## Open questions

- Which loaded shape, material, world transform or skin source supplies one
  reached draw call?
- Which guest code reads the world transform and writes its shader constants?
- Does a shipped vertex shader use a bone palette at all?
- Which root and namespace resolve an external texture filename?
