# Native renderer ring setup and teardown

The guest talks to the video hardware through two separate buffers. The
command buffer is where draw code writes commands: its cursor is `G+0x30`, its
soft limit `G+0x34` and its hard limit `G+0x38`, where `G` is the device
structure. The primary ring is a small circular buffer the hardware reads. A
finished command buffer segment reaches the hardware as a short descriptor
written into the primary ring. This page covers how the guest builds that
setup, replaces it and takes it down, and which imports it calls. Results are
static findings with confidence `strong` unless stated.

## Setup in `0x8269C8E0`

[`RVA-F-0306`](../../../manifests/native-renderer-d3d-completion-contract.json#/deviceInitialization)
and [`RVA-F-0128`](../../../manifests/native-renderer-ring-span.json) record what
the ring setup function does:

- It allocates and zeroes a 96 byte block `B` and a separate 32 byte block
  `S2`, both reached from `G+0x2A90` and `G+0x2A94`.
- The issue ticket at `G+0x2A9C` becomes 3 only when it was 0. Otherwise it
  keeps its value. Ticket values stay odd on every known successful path.
- `B+0` holds the completed ticket, `U32(P - 2)` for ticket `P`, and `B+4`
  holds the cursor.
- Zero sizes in the configuration choose a primary ring of `0x8000` bytes and
  a secondary pool of `0x200000` bytes. A zero divisor chooses 32.
- `B+0x3C` is registered with `VdEnableRingBufferRPtrWriteBack` and `B+8` with
  `VdSetSystemCommandBufferGpuIdentifierAddress`.
- Primary ring base and mask live at `G+0x3A30` and `G+0x3A34`. The command
  buffer segment start lives at `G+0x3A50`, with the cursor set four bytes
  before it.

Exactly five direct calls reach `0x8269C8E0`, found by a raw search of direct
calls: `0x8250E438`, `0x8268CEB0`, `0x826A6474`, `0x826A67D8` and
`0x82C72270`
([`RVA-F-0314`](../../../manifests/native-renderer-video-detach-contract.json#/currentEvidence/ringInitCallerBoundary)).
Calls through a register would not appear in that search.

## How a segment reaches the hardware

When the segment is full, `0x8269C400` calls `0x8269BD98` with the segment's
encoded address and length. On the immediate path that builds two words: the
length in the low 24 bits ORed with `0x81000000`, then the encoded address.
`0x8269B900` writes `0xC0013F00`, the address and the length into the primary
ring at masked indices (`0x8269BA40` to `0x8269BA90`), stores the new index at
`G+0x2AC8`, and writes it to MMIO `0x7FC80714`. The present call reserves 64
dwords through `0x8269C7A8`, passes the reservation plus 4 to `VdSwap`, then
stores reservation plus `0x100` at `G+0x30`. That address is in the command
buffer, not the primary ring.

Not known: the start, end and wrap rule of the exact ring span that holds one
resolve and its swap, what acknowledges it, and so what is safe to retire. The
first read of the eight functions involved stopped early; six truncated at a
save thunk and two at an undecoded instruction.

## Replacing and tearing down

`0x8269C8E0` also performs reconfiguration
([`RVA-F-0314`](../../../manifests/native-renderer-video-detach-contract.json#/currentEvidence/selectedTeardownBoundary/reconfiguration)).
In order, it:

1. drains its selected guest condition and closes writes to the old ledger,
2. releases the blocks it holds at `G+0x39F4` and `G+0x39F8`,
3. unregisters the identifier address (value 0),
4. releases the old `S2`, then the old `B`, and clears those fields,
5. builds the replacement.

A configuration of 0 stops after step 4 and returns 0. If the replacement
fails, some allocations can remain. Release goes through
`0x82E29160`, `0x8280DB58` and `0x8280DEC8` to `MmFreePhysicalMemory` with type
0. `0x826A66D0` first unregisters the graphics callback (0 and 0), then calls
the ring function with configuration 0, then shuts down the SDK. `0x826A63E8`
calls it with the pointer `config+72`, the address at offset 72 of the
configuration, not the scalar stored there. Exactly which memory the
final device release frees, and how long each block stays valid, are
unresolved.

## Video imports

The renderer calls 21 video imports from 31 direct call sites in 20 functions.
The list includes `VdSwap` at `0x826A4884`, `VdSetGraphicsInterruptCallback`
at `0x826A6364` and `0x826A67CC`, `VdInitializeEngines` at `0x826A632C`,
`VdShutdownEngines` at `0x826A5C3C` and `0x826A6808`, and `VdPersistDisplay`
at `0x826A4B40`. Computed calls are outside this count.

## Draw entry inventory

[`RVA-F-0081`](../../../manifests/native-renderer-d3d-inventory.json) is an open
candidate inventory of the Direct3D surface above the commands. It
holds one entry, the wrapper `0x826A3568`, called at `0x82303E3C` and
`0x82303E8C` from `0x82303C38` with primitive type 4. A plain reference query
for `0x826A3568` returns no rows. After the repair scripts in
[`RVA-F-0086`](../../../manifests/native-renderer-d3d-draw-lowering.json) run, it
returns exactly those two. Device publication, the dispatch table extent and
other draw entry points are not covered.
