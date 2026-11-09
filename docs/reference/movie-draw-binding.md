# Movie draw binding

The game draws a movie frame as a four vertex strip that samples texture planes
filled by a video decoder. This page covers how the guest code hands those
planes to the draw, and the edges around it that are accepted. It does not
identify the decoder, the clock that picks a frame, or how a frame lines up
with audio.

## How the draw gets its first plane

The movie code at `0x82E305F8` builds an 880 byte stack frame. It saves its
first two arguments in home cells above the local frame: the first at `S+0x384`
and the second at `S+0x38C`, where `S` is the new stack pointer. These cells
are not fields of a new movie object.

At the binding call `0x82E335A8` the code does this:

1. Load `Pa` from `S+0x38C`, then the index `j` from `Pa+0x14`.
2. Reload the pointer, form `P+0x78+32*j` as the record base, and read a
   backend value `B` from field `+0x10` of that 32 byte record. When both loads
   see the same `P`, the cell is `P+0x88+32*j`.
3. Call `0x8269AF10` with the graphics device, a zero, `B`, and the 64 bit mask
   `0x0000000080000000`. This mask is a low word bit, not bit 63. No test for a
   nonnull `B` comes first.

`0x8269AF10` is the fetch descriptor setter. It is accepted in
[the fetch descriptor manifest](../../manifests/gfx-backend-fetch-descriptor.json#/descriptorMerge).
Slot 0 keeps its six word fetch state at graphics offset `+0x480` and its
backend pointer at `+0x3100`. A nonnull `B` merges the backend's words from
`+0x1C` to `+0x30` with the existing slot state, ORs the mask into the 64 bit
dirty word at `+0x18`, and stores `B`. A null `B` skips the merge, writes zero
to the pointer cell, and leaves the earlier fetch state in place.

Worked example. Take `P = 0x10000000` and `j = 3`. The record base is
`0x100000D8` and the backend cell is `0x100000E8`. That cell is neither the
record base nor `P+0x10`, so a test with a readable backend there tells the
indexed record layout apart from a flat field.

## The draw and cleanup

The draw call is `0x82E39878 -> 0x826A3000`, with return `0x82E3987C`. It
submits four strip vertices of stride 20. On success the wrapper copies 80 bytes
and publishes its cursor. Later cleanup clears the backend cells and keeps the
fetch state. A null backend also keeps the earlier state. Copying the vertices
and publishing the cursor does not mean the decoder finished, the texture was
read, or the frame was shown.

## Frame driver edges

The movie state is the numeric key 5 object, built by factory `0x821B3BB8`.
Its construction installs vtable `0x82121340`. Slot `+0x04` points at
`0x82C5F680` and slot `+0x08` at `0x82C5E778`. The first loads the shared
timing record `0x8314F280`, calls that record's slot `+0x08`, which targets `0x82C7EB68`, and
then uses the accumulated time or frame delta in later update calls. The
behavior of `0x82C5E778` is unresolved, so do not call it a decoder, stop or
skip handler. Neither slot shows that playback runs.

## Where to read more

| Question | Manifest |
|---|---|
| Caller, binding call, draw tuple, cleanup, slot 0 origin | [F0162](../../manifests/movie-nonindexed-up-draw.json#/currentEvidence/slotZeroOrigin) |
| Setter behavior, null backend | [F0031](../../manifests/gfx-backend-fetch-descriptor.json#/fetchSelection) |
| Key 5 object and frame slots | [F0059](../../manifests/attract-movie-frame-driver.json#/frameOwnership) |
| Timing record and per frame update | [F0015](../../manifests/gameplay-frame-timing-owner.json#/perFrameUpdate) |

Frame pacing and the timing record are in
[native renderer frame pacing](native-renderer-frame-pacing.md). The GFx draw
side, which is a separate path, is in [GFx image rendering](gfx-image-rendering.md).

## Limits

- The state cells `Pa`, `Pb`, the graphics device pointer and `j` must hold
  across their reads. The saved values do not rule out a helper, a stack write
  or another thread changing them.
- No record count or allocation size is known, so `j` is not shown to be in
  range. A safe check needs readable cells and `P+0x88+32*j+4` not to pass
  `0x100000000`.
- `j` is not shown to be a frame number or a clock.
- Plane sizes, channel roles and a color matrix are not established. Repeated
  bind calls, draws or cleanups do not give a frame rate.

## Open questions

- Which code writes the planes, and which function is the decoder or provider?
- Which clock or input selects the frame to show?
- How does the played audio position relate to the shown frame?
- Which function handles skip, fade or end of a movie?
