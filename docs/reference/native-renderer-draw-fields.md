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

Declaration scan advances 12 bytes until 16-bit 0xFF. Copying n records from
+0x34 omits that terminator; 0x38+12*n allocation leaves four extra bytes.
Subfields/API semantics remain unknown.

Parent-backed surfaces store the parent at +0x18; AddRef/Release recurse under
count/type/flag guards. Standalone packed +0x18 has no proved parent role;
variants differ.

## Device state and lifetime

Flush reads/clears dirty +0x00/+0x08/+0x10/+0x18/+0x20; sampler store 0x8268F058
targets device +0x18. Flush also reads +0x28; writer/meaning remain unknown.

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

Static bounded fields establish no complete C++ layout, frequency, draw order or
safe snapshot mask; manifest records unresolved ranges/readers.

- [D3D runtime surface](../../manifests/native-renderer-d3d-runtime-surface.json): wider device state.
- [Resource contract](../../manifests/native-renderer-resolve-resource-contract.json): qualified six-word texture descriptors.
