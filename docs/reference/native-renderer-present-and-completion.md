# Native renderer present and completion

When the game shows a frame, the guest does more than call `VdSwap`. It
writes progress words the CPU reads later, runs a handshake with the command
stream, and answers hardware interrupts. Other guest code reads those words
to decide when a resource is free and when to wait. This page lists the
words and the order in which they change. `G` is the device structure, `B`
the 96 byte block at `G+0x2A90`, `S2` the 32 byte block at `G+0x2A94`, and `P`
the issue ticket at `G+0x2A9C`. Results are static findings with confidence
`strong`, and say nothing about how often a path runs.

## Present order

The main present worker `0x826ABEA8` calls the pre swap wrapper
`0x826A4150`, then the swap function `0x826A4638`; the alternate caller `0x82517E38`
uses the same order
([`RVA-F-0128`](../../manifests/native-renderer-ring-span.json)). That function
then runs, in order, `0x826AADA8`, the `VdRetrainEDRAM` loop `0x826B0508`,
`0x8269C270`, `0x826A9DA8` and `0x82690040`. The last marks all five dirty
words as set. Its call sites are in
[`RVA-F-0310`](../../manifests/native-renderer-present-tail-reader.json#/currentEvidence/exactContextEffects).

The pre swap handshake uses `S2+4`: request 1, wait for 1, emit the callback
commands `0x8269BF40` (callback `0x826A3FB8`), then wait for 0. It reads the
system command buffer state, not resolve state, so it is not a resolve
completion fence ([`RVA-F-0118`](../../manifests/native-renderer-vdswap.json#/currentEvidence/waitPayloadDiscriminator)).

## Tickets and fences

[`RVA-F-0306`](../../manifests/native-renderer-d3d-completion-contract.json#/fenceArithmetic)
gives the arithmetic. All comparisons are unsigned 32 bit.

- `0x8269C6C0` reports a resource busy exactly when `P - f < P - C`, where `f`
  is the fence stored at resource offset 8 and `C` the completed ticket at `B+0`.
- `0x8269BE70` waits until that stops being true, polling through
  `0x8268CBB8`. The poll can stop on its own without progress.
- `0x8269BCA8` emits two `EVENT_WRITE_SHD` commands. The first writes the
  cursor value to the encoded address of `B+4`. The second writes the old
  `P` to `B`. It then stores `P + 2` at `0x8269BD84`.
- Only when `G+0x541C` is 0 and mask `0x02` of `G+0x2ABD` is set does it also write
  `B+0` and `B+4` directly from the CPU.

So a worked example: with `P = 5`, a resource stamped 5 is busy until the
fence write puts 5 into `B+0`, and the next ticket is 7.

## Interrupt callback

`0x826A62F8` registers handler `0x8269B450` with the interrupt import at
`0x826A6364` (`0x826A67CC` clears it). For event 1, the handler reads the
callback at `S2+0x10` and its argument at `S2+0x14`, calls it, then clears the
current CPU bit in `S2+0` under the lock at `G+0x2A98` (mask `0x3F`). A debug
call followed by a trap for the value `0x0BADF00D` marks a retired entry, not a
callback. For event 0, mask `0x01` of MMIO `0x7FC86544` decides whether
`0x826A3EB8` runs. The handler tables are in
[`RVA-F-0310`](../../manifests/native-renderer-present-tail-reader.json).

## Counters and throttle

| Field | Written by | Meaning |
|---|---|---|
| `G+0x40B0` | `0x826A4664` | Count of swap requests |
| `G+0x40B4` | `0x826A3FF8` | Callback count |
| `G+0x40B8` | `0x826A3F30`, `0x826A410C` | Count of flips taken from the queue or done at once |
| `G+0x40BC`, `G+0x40C0` | `0x826A3FB8` (queue arm) | Queued pointer and target |

When mask `0x04` of `G+0x5D7C` is set, `0x826A4BC8` repeats its poll while
`G+0x40B0 - G+0x40B8` is at least 15, unless `0x8268CBB8` returns 0. Mask `0x01`
of the same word controls the fence wait in `0x8269C270`. Showing a frame on the PC does not
move `G+0x40B8`; only the flip code above does.

## Timestamps

The eight words at `B+0x40` through `B+0x5F` are written by an
`EVENT_WRITE_SHD` with initiator `0x80000003` (`0x826A9BDC`). The timestamp
query for selector 6 (`0x826A9340`) reads three of them through the index in
`G+0x5478`. It stores `index + 2` after its first nonzero test and before its
later zero tests, so a query changes later queries. The result is a ratio of
two differences times 100, clamped; a zero test returns a NaN, not 0. The
reads are at `0x826A9374`, `0x826A937C` and `0x826A9380`. The clock unit is
unknown.

## Open questions

- Whether the optional sink objects at `G+0x541C` and `G+0x5B0C` are ever set
  is unknown; see [tiling workers](native-renderer-tiling-workers.md).
- The actual targets of the optional callbacks at `G+0x409C` and `G+0x40A0`
  are unproved.
- Other writers of `G+0x2A98` and of the resource class mask `G+0x2AA0` are
  not ruled out. The word at `0x8319AEA8` may be one.
