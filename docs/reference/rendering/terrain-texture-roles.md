# Terrain texture roles

Every map has three terrain images: a heights image, a blends image and a
lightmap image. A modder who builds a custom map needs to know how each image
lines up with the 32 by 32 tile map. This page records what the game code
proves about that, and what it does not. It does not give a complete recipe for
placing a texture on the map. The facts are in
[`terrain-height-grid-consumer.json`](../../../manifests/terrain-height-grid-consumer.json)
(`RVA-F-0378`) and
[`terrain-shader-role-binding.json`](../../../manifests/terrain-shader-role-binding.json)
(`RVA-F-0379`).

Worked example. A mod author paints the tile file so that file row 3, column 5
is a hill. The game stores that tile at native position `(x,y)=(3,26)`: the row
becomes `x` and the column becomes `31-c`. That tile rule is proved. The same
author then wants the pixel at row 100, column 200 of the lightmap to light that
hill. No path establishing how a lightmap pixel maps to a native position has been
identified in the inspected code, so the page cannot say which pixel that is. The author has to test it in the game. The one
UV formula the code does show is in the section on blends and lightmap.

## The three images

| Role | Retail size | Where the game keeps it |
|---|---|---|
| Heights | 512 by 512 samples | `terrain+0x24`, a CPU image read by the height converter |
| Blends | 2048 by 2048, DXT1 | `terrain+0xD4` |
| Lightmap | 4096 by 4096, DXT1 | `terrain+0xD8` |

The sizes come from a census of 277 retail maps, recorded in
[`xbox-heights-authoring-contract.json`](../../../manifests/xbox-heights-authoring-contract.json)
(`RVA-F-0376`). The file format and loader rules for the three images are in
[`xbox-dds-map-role-texture-contract.json`](../../../manifests/xbox-dds-map-role-texture-contract.json)
(`RVA-F-0373`). The heights file is described for authors in
[Heights file and the override hook](../setup/heights-file-override.md). How the map
size relates to terrain is in [Map size and terrain bias](../gameplay/map-size-terrain-bias.md).

## Tiles and the 32 by 32 grid

The tile map file is read row by row. A file tile at row `r` and column `c`
becomes native `(x,y)=(r,31-c)`, stored at index `40*x+y` in a plane with a
stride of 40 (`RVA-F-0370`,
[`xbox-map-tile-semantics.json`](../../../manifests/xbox-map-tile-semantics.json)).
This holds only for the 32 by 32 map.

The terrain keeps a copy of those tile bytes. The copy at `0x82C6AF28..0x82C6AF54`
moves `W` bytes per row from the plane at `plane+40*n` to `base+W*n`, with no row
reversal. The lookup leaf at `0x82C675A0..0x82C67630` then reads
`base+D*x+y`. When both dimensions are 32, a lookup at `(x,y)` returns the byte
copied from `plane+40*x+y`, so the copy and the lookup keep the native axes. The
lookup limits `x` and `y` to the map and returns 1 when no copy exists.

## The 33 by 33 corner records

The terrain builds one record for each tile corner. `0x82C6E9A0..0x82C6E9FC`
stores `W+1` at `terrain+0x64` and `D+1` at `terrain+0x68`, which gives 33 by 33
records for a 32 by 32 map. For each corner `(i,j)`, `0x82C6C394` through
`0x82C6C3F8` look up the four tiles at `(i-1,j-1)`, `(i,j-1)`, `(i-1,j)` and
`(i,j)` and build a mask from which of them equal terrain type 6. The record is
stored at index `j*(W+1)+i`. A later step multiplies `i` and `j` by two scale
fields, applies a shared scalar offset, and stores the results at
`record+0x120` and `record+0x124`. The global object that supplies those fields
is not proved to be the original terrain object.

These records come from tile types, not from height pixels. The 33 by 33 grid
does not show that the heights image has 513 samples, that its pixels sit at
tile corners or centers, that tiles share edge samples, or that the game
resamples or filters the image.

## The heights image

The heights image is read in `0x82C69850`. The file loader reverses the rows
once when it extracts the image (`0x822F99F8..0x822F9A28`), and the converter
reverses them a second time when it reads samples. The two reversals cancel, so
a sample keeps its file row. Each sample is an unsigned 16 bit value `n`, and
the converter computes `n * terrainScale * 255 / 65536`, where `255 / 65536` is
the float word `0x3B7F0000`. The scale comes from `TerrainZScale`; its value is
not known.

The converter then wraps the result and stores the wrapper at `terrain+0xB4`.
It passes that wrapper twice to the global service at `0x8314F28C`, at
`0x82C69C6C` and `0x82C69C94`. When that service is the table installed at
`0x82120EB0`, the target at `0x82120F68` is `0x82E0ECD0`, a single return
instruction, so those two calls read no height samples. The attached wrapper
holds a GPU resource, not a CPU array of floats. Nothing found reads it back to
place vertices. A small getter at `0x82C67890` returns the field, but no caller
was found.

The ratio of image size to tile size is 512 over 32, which is 16 samples per
tile. That is a size ratio. It is not a rule about where samples fall.

## Blends and lightmap

A cold load of the two color images stores each one through the type 7 exporter
at `0x82C8D540`. The exporter copies the resource's object pointer
into `terrain+0xD4` for blends and `terrain+0xD8` for lightmap, with reference
counting (`0x82C8D560` calling `0x821B2440`). The generic exporter is described
in [`gfx-texture-resource-export.json`](../../../manifests/gfx-texture-resource-export.json).

The terrain shader that appears to use them is the 13 fetch form, a vertex
program `571D6127CBF96DD1` with a pixel program `2DEEA7E9B28316E1`, drawn at
`0x8250C764` calling `0x826A39F8`. In a recorded draw, the 2048 by 2048 image
is sampler slot 11 and the 4096 by 4096 image is slot 12. Both slots read the
same texture coordinate:

```text
u = clamp(q.x + c16.x, 0, 32768) / 32768
v = 1 - clamp(q.y + c16.y, 0, 32768) / 32768
```

Here `q` is the decoded vertex input and `c16` is a vertex constant. In the one
recorded draw, `c16` is `(-512, 28160, 0, 1)`. With that constant, `q.x=16896`
and `q.y=-11776` give `u=0.5` and `v=0.5`. There is no extra offset for either
slot, no texel offset, and the shader sampler settings are linear filtering with
repeat addressing. So the two slots have no relative vertical flip between them,
as long as the slot guesses hold.

Slot 11 steers a three step mix between three 512 by 512 materials in slots 8,
9 and 10, using its red, green and blue values in that order. Each step blends
toward the next material, so this is not a normalized sum of three weights.
Slot 12 feeds a lighting step with constants `a=0.12156856060028076`,
`b=1.1383928060531616` and `t=0.8784314393997192`. If its red value `L.x` is at
least `t`, the step adds `a` before multiplying; otherwise it scales by `b`. A
solid white lightmap therefore gives a factor of 1.1215685606002808 at that step,
not 1. A second 1024 by 1024 texture in slot 7 multiplies the result, and later
steps mix in more color, so the page does not say what a white lightmap looks
like on screen.

An 8 fetch form of the terrain shader, with programs `DBCF02DFB9E3F8FB` and
`F375BB83352BFB1B`, samples only slots 0 through 7 and has no slot 11 or 12. The
effect name alone does not pick one terrain material path.

## What is not proved

- Heights: where a file row and column land in native `(x,y)`, whether samples
  sit at tile centers or corners, edge sharing, filtering, the live scale value
  and the sea level sample.
- Blends and lightmap: that slot 11 and slot 12 really hold `terrain+0xD4` and
  `terrain+0xD8`. No code found passes the stored pointer to a texture stage.
  Matching sizes do not prove the roles.
- The source of `q`, and whether `c16` changes per map. The one recorded value
  is not a rule.
- Which pixel of a blends or lightmap file lands on which native tile, and the
  row order of the file when it is uploaded.
- Which raw DDS channel feeds slot 11's red, green or blue, which materials sit
  in slots 8 to 10, and whether they change with climate or era.
- The receiver object of the draw routine at `0x8250C498`, read at `0x8250C598`.
  The evidence each open item needs is listed under
  [`requiredInstanceEvidence`](../../../manifests/terrain-shader-role-binding.json#/requiredInstanceEvidence).

The manifests list the exact addresses and the check each open item needs.
