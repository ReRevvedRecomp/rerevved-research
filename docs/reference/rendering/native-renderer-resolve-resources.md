# Native renderer resolve resources

A resolve copies a finished render target out of EDRAM, the Xbox 360's fast
video memory, into main memory so later draws can read it. The guest
function `0x8269E520` does this copy and reads a small resource header that
says where the copy goes. This page records what that header holds, how the
guest creates and reuses the memory behind it, and what the guest does not
say. Results are static findings with confidence `strong`.

## The resource header

[`RVA-F-0126`](../../../manifests/native-renderer-resolve-resource-contract.json)
covers a 0x34 byte header. The creator `0x82533DB8` builds it through
`0x826B6FE8`, `0x826B6D68` and `0x8269A378`, allocates the backing memory
through `0x82E29168`, and patches page bases in with `0x826B7140`. Six words
sit at offsets `+0x1C` through `+0x30`.

| Word | Offset | What the guest does with it |
|---|---|---|
| 0 | `+0x1C` | Packed control bits. Resolve reads a different bit range than the creator sets; the creator flag `0x00200000` for a second backing region is not read by Resolve |
| 1 | `+0x20` | Primary page base in bits 12 through 31, numeric format in bits 0 through 5 |
| 2 | `+0x24` | Packed width and height, each stored as size minus 1 |
| 3 | `+0x28` | Packed layout and sample control bits |
| 4 | `+0x2C` | Packed by the creator, never read by Resolve |
| 5 | `+0x30` | Second page base, set only by the creator; Resolve reads only bits 9 and 10 |

Resolve reads five of the six words (`0x8269E5CC` to `0x8269E628`). The second
page base has no matching reader, so its purpose is unknown. The pitch,
slice, level, region, tiling and sample count fields inside words 2, 3 and 5
are not named, and the exact type, size and format at the main call site
`0x8250AFEC` are not statically known.

Worked example: a header whose word 1 is `0x1F400046` would have page base
`0x1F400` and numeric format `6` (the low six bits). The value is invented to
show the layout, not read from the game.

## Creation and reuse

[`RVA-F-0127`](../../../manifests/native-renderer-resource-lifetime.json) covers
the container built by `0x825184D0`. It creates two buffer objects through the
creator and keeps them at `+0x90` and `+0x94`. A selector at `+0x98` picks one
and flips between 0 and 1 after the present path. Cleanup `0x82518678` releases
both objects by reference count and clears both slots; `0x82518E88` calls that
cleanup and frees the container. The selector is frame state, not a version
number for the memory.

The backing allocator `0x82E29168` has 96 direct references: 42 inside
recognized functions and 54 in unassigned or data regions. That is over the
search cap of 6, so no caller was read. Nothing found shows when the backing
memory is replaced, invalidated or recycled.

## Which object a resolve writes

[`RVA-F-0140`](../../../manifests/native-renderer-resolve-destination-lifecycle.json)
asks whether the object passed to Resolve at `0x8250AFEC` is one of these
two buffer objects. The code keeps the current group item in `r30`, checks
only that it derives from the `NiXenon2DBufferData` base, calls the item's
virtual function at `+0x0C`, and passes the first output unchanged as `r6`.
It never checks the exact vtable. The static code therefore cannot tie that
call to the factory above. One read just before `0x8250AFEC` could settle it:
the vtable of `r30`, its `+0x0C` result, the selector value and whether the
selected slot equals `r6`.

## What this adds up to

The header gives a page, a format and a coarse size. The guest code read so
far gives no allocation identity, no content generation and no signal that
the copy has finished on the GPU. A guest pointer or the six words should not
be used alone as the name of a resource. The frame fallback provider
reached from the same group code is in
[frame passes](native-renderer-frame-passes.md).
