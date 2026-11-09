# Native renderer tiling workers

The Xbox 360 draws a frame in tiles because its fast video memory (EDRAM) is
too small for the whole picture. The guest records commands between a begin
and an end call, then replays them once per tile. Replay runs on guest worker
threads, one per hardware thread. This page summarizes how the guest hands
work to those threads and what stays unknown. All results are static findings
with confidence `strong` unless stated.

## Names used here

| Name | Meaning |
|---|---|
| `G` | The device structure |
| `W = G+0x2AC0` | Shared worker state |
| `Q_i = G+0x2C3C+0x50*i` | Queue record for hardware thread `i`, six selected records |
| `N = G+0x2B00` | Count of submitted work not yet retired |

## From begin to retirement

[`RVA-F-0311`](../../manifests/native-renderer-tiling-wrapper-exit.json) and
[`RVA-F-0303`](../../manifests/native-renderer-tiling-worker-store.json) hold
the local detail. The path, in order:

1. Begin (`0x8269CE90`, or the alternate `0x8269D7D8`) reaches `0x826AC0A8`. It
   saves six publication words and emits a 252 byte record with header
   `0x80`. The parser `0x826AB740` copies 248 bytes of it to `W+0x6C`.
2. End (`0x826AC218`) makes three allocations through `0x8269B818`: 148, 40
   and 48 dwords, which is 592, 160 and 192 bytes, with alignments 32, 32 and
   4. If one fails, End restores the saved words, returns 1 and does nothing
   else. Earlier takes are not undone.
3. On success End finishes seven lists, emits the callback `0x826AC020` with
   the root of the recorded commands, and calls `0x8269BD98` to count the
   work. Only the middle submit adds 1 to `N`; the optional and final submits
   add 0.
4. `0x826AC020` stores the root in the queue record, adds 1 to its producer
   count and signals its event. Worker threads (`0x826ABEA8`, `0x826ABB90`)
   wake, take the root, and run the recorded tokens.
5. The last thread to finish, seen as `W+0x3C` reaching 0 with `W+0x48` null,
   calls `0x826ABA68`, which subtracts from `N` once at `0x826ABB34`.

`0x8269C810` waits for a fence and then spins until `N` is 0, so a count that
is never retired hangs it.

## Record types the parser reads

- `0x80`: rectangle context, copied to `W+0x6C`.
- `0x89`: two lists, `G+0x33C0` and `G+0x3424`, built at `0x8269D5C8` and
  `0x8269DC38`. The parser sends them to `0x826AB160`, which calls `0x826AB058`
  on each entry.
- `0x8A`: three pointers at record offsets `+4`, `+8` and `+0xC`, used by
  `0x826AB448`, `0x826AB510` and `0x826AB648`. Each stores a status word
  through a destination pointer, then flushes cache lines.
- `0x8C`: installs a function and context at `W+0x10` and `W+0x14`
  (`0x826ABDA4`, `0x826ABDB0`). The call happens at `0x826ABD6C` with the queue,
  context, payload and iteration count.

## What is still unknown

- Nothing found builds a `0x8A` record. A search for the immediate `0x8A00`
  ([`RVA-F-0313`](../../manifests/native-renderer-replay-destination-owner.json#/currentEvidence/constructor8ASyntaxBoundary))
  found the parser comparison at `0x826AB918`, a text match at `0x8316B23C`,
  and one unclassified word at `0x831949A4` with no containing function.
  A search that finds no constructor does not show that none exists.
- No emitted `0x8C` record, and so no real callback target, has been found
  ([`RVA-F-0312`](../../manifests/native-renderer-worker-state-reader.json#/currentEvidence/callback8C)).
  The word at `0x820D726C` may be code or data.
- The installer of the allocation manager at `G+0x34CC` is unknown. When
  `0x826A6AB8` runs, it raises a small request to `manager+0xA8`, a minimum
  and not a maximum, and calls `manager+0xAC`.
- A dispatcher at `0x826A9810` stores its second argument at `G+0x5B0C` when the
  selector is `0x22`. It has no direct caller and no known source of that value.
- The device fill at creation zeroes `G+[0, 0x5E00)`, which covers `G+0x541C`
  and `G+0x5B0C`.

## Why removing the workers is unproven

Reset code reads worker state too. `0x8269C8E0` waits until `W+0x28` equals
`W+0x2C`; `0x826AC578` signals, waits for and closes each queue thread; and
`0x8268CF60` copies `Q_i+0x34` to `G+0x2A88`
([`RVA-F-0312`](../../manifests/native-renderer-worker-state-reader.json)).
A finite example shows the count rule needs a participation rule too. With
one counted add, `N = 1`, and the same terminated root in two queues, each
thread sets a different participation bit and each reaches the final step,
so `N` ends at `0xFFFFFFFF`. This is a state machine example, not an observed
run. The recovery code at `0x826A5BC8` also writes `N = 0` without normal
retirement.
