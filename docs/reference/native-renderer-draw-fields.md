# Native renderer draw fields

The
[draw-object-fields manifest](../../manifests/native-renderer-draw-object-fields.json)
records static writers/readers, widths, classifications, confidence and coverage
for draw objects, bindings, dirty masks, commands and lifetime fields.

## Known objects

| Object | Proven extent | Proved fields | Catalog |
| --- | --- | --- | --- |
| Vertex buffer | 0x20 bytes | +0x00 control candidate, +0x04 initialization word, +0x14 sentinel candidate, +0x18 tagged data address, +0x1C encoded fetch/size | RVA-STR-0058 |
| Index buffer | 0x20 bytes | +0x00 draw control, +0x04 initialization word, +0x14 sentinel candidate, +0x18 draw address, +0x1C size/control candidate | RVA-STR-0059 |
| Vertex declaration | 0x38+12*n bytes | +0x00, +0x04, +0x14, +0x18, +0x1C, +0x20..+0x2F, and n copied 12-byte records from +0x34 | RVA-STR-0060 |
| Backend texture | 0x34 bytes | Six descriptor dwords at +0x1C..+0x30 | RVA-STR-0028 |
| Parent-backed surface | 0x30 bytes | +0x00, +0x04, +0x14, parent +0x18, and +0x1C | RVA-STR-0061 |
| Standalone surface | 0x30 bytes | +0x00, +0x04, +0x14, packed +0x18 candidate, and layout words +0x1C..+0x2C | RVA-STR-0062 |
| Device draw state | Partial, at least +0x319C | Dirty words, stream fetch shadows, declaration and index bindings, render targets, streams, strides, textures, shaders, fetch shadow, sampler slot | RVA-STR-0063 |
| Sampler shadow | Partial stage record | +0x0C and +0x10; its setter updates device +0x18 | RVA-STR-0064 |
| Draw command state view | Partial, at least +0x3498 | Cursor at device base +0x30, limit +0x38, commit words +0x3484..+0x3494 | RVA-STR-0065 |

The declaration scan advances 12 bytes at a time until it finds the 16-bit
value 0xFF. Copying n records from +0x34 omits that terminator; the 0x38+12*n
allocation leaves four extra bytes. Subfield meanings and API semantics remain
unknown.

Parent-backed surfaces store the parent at +0x18; AddRef/Release recurse under
count/type/flag guards. Standalone packed +0x18 has no proved parent role;
variants differ.

## Device state and lifetime

Flush reads and clears dirty +0x00/+0x08/+0x10/+0x18/+0x20. The sampler store
at 0x8268F058 targets device +0x18. Flush also reads +0x28, whose writer and
meaning remain unknown.

Distinct bindings: streams +0x30AC by index; fetch shadows +0x6F0/+0x6F4 with
8-byte indexing; stride bytes +0x30F0; textures +0x3100 by stage; fetch shadow
+0x480 by stage stride; sampler +0x1D4 by type. Direct consumers remain unknown
for streams, fetch shadows, strides, most textures and sampler entries.

AddRef/Release change +0x04, conditionally recursing through +0x18 under
count/type/flag tests. Stream/index setters write prior-resource +0x08 when
prior binding and device +0x2A9C are nonzero. Capture exclusion for these
lifetime bookkeeping candidates remains unproved. Cursor/commit words join
flush, wrapper and ring state; discard/masking remains unproved.

## Limits

These statically identified fields do not establish a complete C++ layout,
access frequency, draw order or safe snapshot mask. The manifest records
unresolved ranges and readers.

- [D3D runtime surface](../../manifests/native-renderer-d3d-runtime-surface.json): wider device state.
- [Resource contract](../../manifests/native-renderer-resolve-resource-contract.json): qualified six-word texture descriptors.

## State that survives removing the guest draw path

[`RVA-F-0307`](../../manifests/native-renderer-draw-state-reader.json) lists
which draw fields other guest code still reads when the draw entries
themselves are skipped. Setters, getters, creators, Release, reset, Clear,
Resolve, tiling and present code all keep running. A field with no reader
found is `unknown`, not unused, because loads through other bases, indexed
loads, copies and bulk writes were not all searched.

| Fields | Still read by |
|---|---|
| Dirty words at `G+0x10`, `+0x18`, `+0x20` | Clear and Resolve emitters, plus the flush functions `0x826A8140` and `0x826AA088` |
| Color word `G+0x2884` | Resolve (`0x8269E448` selects the color nibble only for argument 0) and shader mode code |
| Control word `G+0x2954` | Surviving readers unknown: no retained direct reader was found, and aliases and raw-only candidates stay unresolved |
| Shader constants shadows `G+0x2920`, `+0x2924`, `+0x2928` | Clear and Resolve register copies |
| Bytes `G+0x2ABD`, `+0x2ABE` | Resolve (mask `0x08` of `+0x2ABE` is tested and cleared) and the register run code |
| Stream stride cache `G+0x2E38` through `G+0x2E47` | `SetStreamSource` at `0x8268FC08`, which sets dirty bit `0x80000` on a difference |
| Shader code bytes at `VS+0x20` | The effect refresh and copy paths (`0x82662D28`, `0x82694480`) |
| Identifier counter at `0x82FA0544` | Surviving readers unknown. The identified readers sit in selector and patcher paths that draw skipping consumes (one decoded materializer and one raw split candidate at `0x826ADD1C`). A helper there stays live only through a surviving caller, so retained helper entry points are possible, not proved reads; copied or indexed aliases are not searched |
| Cursor and pool words `G+0x30`, `+0x34`, `+0x38`, `+0x3A44` to `+0x3A54` | The allocation routines `0x8269B618`, `0x8269B818` and `0x826A6848` |
| Tiling list `G+0x33C8` and worker state | See [tiling workers](native-renderer-tiling-workers.md) |

## Draw residue that blocks removing dirty fetch and mode work

Three results from the draw path describe state that stays after a draw:

- A shader code patch made while drawing is persistent. The effect code reads
  it later through `0x82694480`
  ([`RVA-F-0308`](../../manifests/native-renderer-shader-readback-activation.json)).
  The byte rules are in
  [`RVA-F-0304`](../../manifests/native-renderer-shader-fetch-byte-contract.json).
- The mode refusal protects an ordered fold in `0x826ADD88`: low 3 bits of
  `G+0x2954` become 5 or 4, with dirty bit `0x80000` added first
  ([`RVA-F-0317`](../../manifests/native-renderer-mode-fold-contract.json#/currentEvidence/orderedFold)).
- A temporary user pointer stride causes the same fetch patch path
  ([`RVA-F-0318`](../../manifests/native-renderer-up-fetch-history.json)).

See [user pointer draws](native-renderer-up-draw-reservation.md) for the order
of these effects.
