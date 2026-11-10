# Native renderer user pointer draws

A user pointer draw (UP draw) hands the renderer vertex data, and for the
indexed form index data, straight from a caller pointer instead of from a
created buffer. The GFx interface drawing calls these entries. Before the draw
reaches the command ring, the guest copies that data into ring space and
updates a set of device fields. This page records what that path does, in the
order it does it, so a replacement can keep every effect that other code reads.

Two entry points start the path. Both are static findings with confidence
`strong` and describe what the code can do, not how often it runs.

| Entry | Lowerer it calls | Selected note |
|---|---|---|
| `0x826A3568` (indexed) | `0x826A3048` at `0x826A35AC` | Takes vertex space, then index space |
| `0x826A3000` (not indexed) | `0x826A2B58` at `0x826A3020` | Takes vertex space only |

The lowerer reserves `q = low32(count * stride) >> 2` dwords (4 byte words)
with 16 byte alignment, so a count of 5 and a stride of 16 reserves 20 dwords,
which is 80 bytes. The wrapper copies the caller data into the reserved
space only after the lowerer returns. The indexed wrapper copies and
publishes when the child result is zero. The not indexed wrapper copies when
the returned destination is nonzero. Both tests come from the recompiled copy
of the function, not from a manifest finding.

## Order of effects in the lowerer

[`RVA-F-0319`](../../../manifests/native-renderer-dirty-up-helper-contract.json#/currentEvidence/lowererMaskFlow)
gives the full order for `0x826A3048`. The main steps:

1. Save the stream 0 stride byte at `G+0x30F0` (`0x826A3094`), then store the
   temporary stride `low8(stride >> 2)` there (`0x826A309C`). A stride of 20
   bytes becomes 5. A stride of 1024 becomes 0.
2. If that byte differs from the cached byte at `G+0x2E38` and a vertex shader
   is set, add dirty bit `0x80000` (`0x826A30B8`).
3. Snapshot the five dirty words, then run the helpers in a fixed order: two
   constant uploads (`0x826ACFF8` for vertex constants at `G+0x0780` and
   pixel constants at `G+0x1780`), then `0x826ADD88`, `0x826AC8C8`, and the
   register run helpers `0x826ACC60`, `0x826ACEA0` and `0x826ACD20`. Each
   runs only when its snapshot is nonzero.
4. Restore the stride byte (`0x826A32E4`). If the cursor is now past the
   limit, flush through `0x8269C588` (`0x826A32F4`).
5. Take vertex space, then index space, through `0x8269B818`, stage the
   pending command end at `G+0x3484`, and OR mask `0x01` into `G+0x18` at
   `0x826A3520`.

The helper results are full 64 bit masks. `0x826ADD88` returns its mask and
does not store it to `G+0x10`.

## Reservation size is not the bytes written

The inline shader code copy in `0x826ADA38` shows why. For shader code of
length `L`, it reserves `(L >> 2) + 5` dwords from `0x8269C7A8`, writes five
header words, copies `L` bytes, then moves the cursor by `20 + 4 * (L >> 2)`
bytes. With `L = 1` and a returned address of `0x1000`, the request is 20
bytes, the cursor ends at `0x1014`, the copy runs through `0x1018` and the
code ends at `0x1019`. A request therefore does not enclose every write, and
no multiple of 4 length is guaranteed. The source cache flush at `0x826A72F8`
runs after the copy and says nothing about the destination bytes. See
[`inlineTransferBoundary`](../../../manifests/native-renderer-dirty-up-helper-contract.json#/currentEvidence/inlineTransferBoundary).

The cache words are stored in the order `G+0x2E40` then `G+0x2E38` here, the
reverse of the order the persistent patch path uses.

## Mode and color fold in `0x826ADD88`

[`RVA-F-0317`](../../../manifests/native-renderer-mode-fold-contract.json#/currentEvidence/orderedFold)
records what the mode refusal in a replacement protects:

- With a live vertex shader and no pixel shader, the control word `G+0x2954`
  low 3 bits become 5. With a pixel shader and dirty bit `0x100000`, they
  become 4. Upper bits stay.
- Color word `G+0x2884` bits 16 through 19 are cleared at `0x826ADE6C`, or the
  whole `RT0+0x1C` word is restored at `0x826ADFB4`, when `G+0x2ABF` has mask `0x08` set.
- Byte `G+0x2ABE` gets mask `0x08` set when `load32(PS base + 0x30) & 0x70000000` is
  above `0x10000000`.

Computing these values needs no allocation. The fold also runs the shared
metadata and fetch code, so the scalar part alone does not replace the call.

## Persistent shader patches

[`RVA-F-0318`](../../../manifests/native-renderer-up-fetch-history.json) shows
that the temporary stride byte can cause real shader changes. When the byte
differs and the cached declaration does not match, `0x826ADD88` can reach
`0x826AD150` and patch the persistent shader code. It may also allocate an
identifier at `0x82FA0544`. The effect refresh path at `0x82662D28` and the
copy at `0x82694480` later read that code
([`RVA-F-0308`](../../../manifests/native-renderer-shader-readback-activation.json)).
A UP draw can therefore change shader bytes that outlive the draw. A cache hit
writes no code but still copies the stream words to `G+0x2E38`.

## Pressure and allocation

When the command ring is full, `0x826AC610` copies as many whole groups of
words as fit before the limit, then calls `0x8269C588` and repeats
([`RVA-F-0320`](../../../manifests/native-renderer-command-pressure-contract.json)).
The vertex and index takes go through `0x8269B818`, which picks one of three
routes: `0x8269B618` when no manager is installed, `0x826A6848` for a fixed
pool, or `0x826A6AB8` for a dynamic manager
([`RVA-F-0315`](../../../manifests/native-renderer-lowerer-scratch-contract.json#/currentEvidence/allocatorAndLifetime)).
A failed second take does not undo the first.

## Open questions

- Which stride, dirty bits and shader variant the real draws use is unknown.
- Which readers outside the lowerer use each field above is not fully known;
  see [draw fields](native-renderer-draw-fields.md).
- Whether other code can reach the same helpers without these wrappers is
  not settled.
