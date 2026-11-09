# Native renderer shader generation

The game does not ship a compiled cache of its scene shaders. It builds many of
them at run time from text, using the Xbox 360 D3DX compiler that is linked
into the executable. Most measured NIF geometries draw through the default
material, so the shader such a model gets depends on a small descriptor that the
game builds from the model, the scene and a few constants. GR2 models are
counted separately below. This page summarizes how that works.
The addresses and limits are in the
[generator manifest](../../manifests/native-renderer-shader-generation.json#/findings/RVA-F-0412).

## Worked example

A static building mesh with a base texture and a glow texture, no fog and one
directional light reaches the default material. `0x8236FAF8` writes a
descriptor: skin mode 0, one UV set, a base map and a glow map, one directional
light. The material emitter `0x8238CB60` turns that descriptor into HLSL text,
and `0x8257EE38` compiles it with entry `Main` and the profiles `vs_3_0` and
`ps_3_0`. A different light count or a skinned mesh gives a different descriptor
and so a different shader.

## Compiler and generators

`0x8257EE38` is `D3DXCompileShader`. It has eight callers: the text linker
`0x82545EE8`, the program creator `0x8254B588`, the two GFx initializers
`0x82302208` and `0x82302348` (profiles `vs_1_1` and `ps_1_1`), the copy and
depth shaders at `0x824FF578`, `0x824FF690` and `0x824FF7A8`, and the movie
YUV shaders at `0x82E30308`. An error shader is built at `0x82532A80`.

| Generator | What it makes | Notes |
|---|---|---|
| Text linker (`0x82545EE8`) | Fixed function emulation from text fragments | 11 vertex and 21 pixel fragment bits; a four word key built at `0x82527918` |
| Material emitter (`0x8238CB60`) | HLSL from a node graph | The game subclass is `CcNiStandardMaterialCurvedWorld` (constructor `0x82E779F8`) |

The text linker serves only null geometry draws and renderer mode toggles. The
only null geometry draw caller found, `0x82513850`, is reached only from
uncalled screen texture paths, so the linker is not on the scene geometry
path. The material emitter is the path for default material scene draws.

Fixed text shaders form closed sets: 29 GFx texts (5 vertex, 24 pixel), 3
movie, 3 copy and depth, and 2 error shaders. Profiles for the emitter are fixed
at `vs_3_0` and `ps_3_0`, and the compile flags are 0.

## The descriptor

`0x8237B7F8` reads 63 distinct descriptor bits from four words. The fields are
small counters and enums: skin mode, normals, specular, vertex color mode, fog,
UV set count, map presence, environment map type, decal count, light counts,
shadow masks, per slot UV index and transform, shadow technique and alpha test.
The manifest lists each field by word and bit. The reachable set is far smaller
than 2 to the power 63.

Limits in shipped data:

- At most 8 lights per object; the worst case found is about 5.
- Shadows and projected textures are off unless an indirect caller exists. The
  only stores of the shadow manager (`0x82F8E74C`) are in `0x823AE6D0`, which
  has no direct caller found, and `0x823AEBC8`; indirect callers of
  `0x823AE6D0` are unresolved.
- Environment maps and fog are off, because no shipped NIF holds a fog property
  or texture effect.
- The shipped light rig has one directional and one ambient light.

## Model data

The shipped game has 260 NIF files with 998 geometries. 951 of them, including
all 519 particle systems, use the default material. About 3,700 models are
`.gr2` files. Of 3,570 that decode, 34 materials use the default material. GR2
models map textures only by usage name, on UV set 0 with no transform, and never
supply dark, normal or parallax maps. Only a material that names a registered
technique gets its own shader.

## Skin modes

The skin mode field takes 0, 1 or 2 from a test of the skin partition at
`0x8236FB40`. A skin without a partition gives 0. A partition whose count,
array or first partition pointer is zero gives 2. Otherwise the mode is 1.

Renderer preparation can change mode 1 into mode 2. After upload, `0x8250B668`
calls `0x823A5A68`, which frees the CPU index arrays and clears the first
partition pointer at `0x823A5AA8`. It leaves the GPU representation in place.
A skin that kept its partition object then reads as mode 2 the next time
`0x8236FAF8` runs. The release is skipped when bit `0x20` of data byte `+54` is
set. Mode 2 builds a four bone vertex shader through `0x82374398` with the
fragment `TransformSkinnedPositionNoIndices`.

This matters for any plan that lists shaders from freshly loaded assets: the
list must also cover the state after preparation. The manifest
[RVA-F-0413](../../manifests/native-renderer-shader-generation.json#/findings/RVA-F-0413)
gives the full call chain with addresses.

## Water shader identity

Candidate result, from
[RVA-F-0415](../../manifests/native-renderer-shader-generation.json#/findings/RVA-F-0415).
Two pixel programs in the corpus match shipped effect files byte for byte:

| Program | Size | Effect file and offset |
|---|---|---|
| River pixel shader | 564 bytes | Water effect file, `0x3B7C` |
| Shoreline pixel shader | 144 bytes | Wave effect file, `0x2244` |

Neither vertex program matched any of the five candidate effect files (rivers,
water, wave, terrain and terrain contour).
That does not show a vertex shader is missing. The match ties a program to a
file, not to a technique, a draw or any visible result. No guest address that
loads these shaders is known.

## Open questions

- Which descriptors a play session reaches. The reached set depends on scene
  state and is not listed statically.
- Whether the linker cache file is ever written, and where scene lights come
  from.
- Which shipped object takes the skin mode 2 path after preparation.
- Indirect callers of `0x823AE6D0`, which would turn shadows on.
- Particle streams, run time map transforms and defaults for absent vertex
  color or specular properties in GR2 models.

Refused stages are on the
[refusals page](native-renderer-shader-refusals.md). Constant upload is on the
[shader constants page](native-renderer-shader-constants.md).
