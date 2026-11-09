# Native renderer shader refusals

A replayed acceptance check over the stored shader corpus refuses some
stages. This page says which, what they are, and what each refusal class
means. The result is a candidate: no refused stage has a shown draw site, and
none is shown unreachable. Detail is in the
[refusal manifest](../../manifests/native-renderer-shader-generation.json#/findings/RVA-F-0414).
For how scene shaders are made, see
[shader generation](native-renderer-shader-generation.md).

## Counts

| Measure | Count |
|---|---|
| Vertex shaders checked | 292 |
| Accepted | 228 |
| Refused | 64 |
| Translation failures | 65 (64 vertex, 1 pixel) |
| Stages in both lists | 62 |
| Union | 67 |

The 64 refused vertex shaders fall into four classes: 30 computed index
fetches, 10 index reads, 11 fetches that depend on control flow and 13 with no vertex
fetch. The 64 translation failures that are vertex shaders use memory export.
The one pixel shader failure is a world map shader that reads a 1D texture.

## What the refused stages are

64 of the 67 stages are image stages inside the executable. All 64 carry debug
provenance from the WMV video decoder, and their container starts run from
`0x820F0B18` to `0x8210EC80`. By operation they are:

| Operation | Stages |
|---|---|
| Motion compensation | 33 |
| Padding | 7 |
| Deblocking | 7 |
| Residual processing | 5 |
| Detiling | 4 |
| Intra processing, range reduction, intensity compensation, copying | 2 each |

These are not world map shaders, and no link to the separate Bink movie path at
`0x82E30308` is established, so none of these stages is excluded as unreachable. Debug
provenance shows where the code was compiled from, not that it runs. The 30 computed indices are addresses or gather
coordinates for media processing, not scene instancing or bone indices. For
example, container `0x820F49D0` computes `r3.x` at instruction slot 9 and
fetches with it at slot 10.

The other three stages come from effect files:

- A vertex shader from the normal map effect file (container `+0x5430`, code
  `+0x583C`) is a false refusal. The check treated a 2D texture coordinate
  register as a vertex index. The shader needs no vertex index.
- A vertex shader from the grass effect file (container `+0x1AE0`, code `+0x22C8`) reads
  `r0.x`, but only to write zero when the value is a finite index. It is a zero
  setup idiom, not a bone, wind or instancing index. If the literal stays zero,
  it can be treated as equivalent to code without the read.
- A pixel shader from the world map effect file (container `+0x62A8`, code `+0x6530`,
  480 bytes) uses a 1D texture. The file pairs it with a vertex shader at
  `+0x3880`; the loader and the draw call are not found.

## What each class means

| Class | Meaning | What a renderer needs |
|---|---|---|
| Computed, flow-dependent or missing fetch (54) | Decoder vertex shaders | Faithful shader side fetch and control flow, plus memory export, if executed |
| Index read (10) | 8 decoder shaders, the false case from the normal map shader, the grass idiom | Fix the check that failed on the normal map shader; keep a zero literal equivalence for the grass shader or supply the vertex index |
| Memory export (64) | The decoder bank | Export of address and data with matching memory readers, or a defensible exclusion |
| 1D texture (1) | World map pixel shader | 1D texture support if the pass is reachable, or an exact pass exclusion |

A strict miss in a shader list is a listing or acceptance defect. It is not a
reason to compile unseen shaders on first use.

## Open questions

- The 64 exports have no known destination buffer, draw site, completion point
  or reader. Searches for references to four representative container starts
  found none, which does not rule out shared bases, aliases or indirect calls.
- Which draw activates the world map pixel shader, and whether the decoder bank
  runs in play.
- Complete coverage of the corpus is not claimed.

The per stage ledger of all 67 stages, with digests, is not published.
