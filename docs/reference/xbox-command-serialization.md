# Xbox command serialization

When the game sends a command to another player, it turns the five-word
command record into a network object and writes that object into a byte
buffer. This page records exactly how many bytes that is, in what order, and
which values the object layer adds around the record. It does not describe the
rest of the network path.

The Xbox 360 image of Civilization Revolution version 1.3 is the authority for
every claim here. Message names, record shapes, packing rules and framing from
the PS3/iOS comparison guide are search leads only; the Xbox code does not use
that guide's compact packing.

## A worked example

A Move command has `type` 17 and four arguments, `arg1` through `arg4`. The
[internal record](xbox-network-messages.md#internal-record-and-local-queue) is
those five 32-bit words. Written by the object layer, it produces:

| Part | Bytes | Content |
| --- | ---: | --- |
| Base envelope | 32 | Eight 32-bit values: the leading value 77, the literal 4, then six metadata words |
| Embedded record | 20 | `type`, `arg1`, `arg2`, `arg3`, `arg4`, each 4 bytes |
| Total from the write path | 52 | |

Reading the same object back consumes 48 bytes: 28 bytes of base envelope, then
the same 20 bytes of record. The reader does not read the leading 77, which
accounts for the 4 byte difference between 52 and 48. Whether any outer code
consumes that word before the read method runs is not recovered, so a decoder
should not assume an offset for it. Neither 52 nor 48 is a complete packet size; framing and headers outside these helpers are not
recovered.

Two consequences matter to a mod that adds or changes a command:

- The payload has room for `type` and four arguments, each exactly 32 bits. A
  command that uses fewer arguments still writes all five words, because the
  write helper always visits offsets 0, 4, 8, 12 and 16.
- Nothing here packs fields by type. The comparison guide's compact,
  type-dependent layout does not apply to the Xbox object layer.

## How the object layer works

The command object has vtable `0x821368E0`. It holds five function pointers,
through `0x821368F0`; the next vtable starts at `0x821368F4` and begins with the
same two leading targets. Those two leading slots stay unnamed.

| Slot | Target | What it does |
| --- | --- | --- |
| `+0x08` | `0x82D910C0` | Write: calls base helper `0x82CB1F78`, then passes object `+0x34` to `0x821D2F98` |
| `+0x0C` | `0x82D91078` | Read: calls base helper `0x82CB1EC8`, then passes object `+0x34` to `0x821D2F28` |
| `+0x10` | `0x82D91C58` | Calls the local queue drain `0x82CE16C8` on object `+0x34` |

The five-word record sits at object `+0x34`. The outbound constructor
`0x82D90A18` copies the five staged words into `+0x34` through `+0x44`. The
send path that calls this constructor, and the 32-slot queue that feeds the
dispatcher, are described in
[Xbox network messages](xbox-network-messages.md).

### The base envelope

Both base helpers call the same 4-byte buffer primitives, `BufferWriteU32` and
`BufferReadU32`. They do not mirror each other.

| Step | Write helper `0x82CB1F78` | Read helper `0x82CB1EC8` |
| ---: | --- | --- |
| 1 | Object `+0x10` | Read a value and check that it equals the literal 4 |
| 2 | Literal 4 | Object `+0x2C` |
| 3 | Object `+0x2C` | Object `+0x1C` |
| 4 | Object `+0x1C` | Object `+0x18` |
| 5 | Object `+0x18` | Object `+0x14` |
| 6 | Object `+0x14` | Object `+0x24` |
| 7 | Object `+0x24` | Object `+0x28` |
| 8 | Object `+0x28` | |
| Bytes | 8 values, 32 bytes | 7 values, 28 bytes |

The writer emits object `+0x10` first. The reader never reads into `+0x10`; the
whole reader ends at `0x82CB1F70` and contains no such read. This
absence applies only to this reader. The meaning of the six metadata words, the
role of `+0x10`, and whether an outer dispatcher consumes it before the read
method runs are not recovered.

### The leading value 77 and the factory default 1000

The outbound constructor `0x82D90A18` stores the literal 77 at object `+0x10`:
`0x82D90A24` loads it and `0x82D90A64` stores it. Confidence is confirmed for
the value and its writer, so the first value of the base envelope on the
outbound path is exactly 77. Its meaning is not recovered. It is not named a
class, opcode, channel, packet or transport type, and nothing shows it is the
only value the field takes.

`NetworkCommandObjectFactory` at `0x821D3778` builds the same kind of object
and sets that same field to 1000 instead:

| Step in `0x821D3778` | Result |
| --- | --- |
| Allocate through `0x82D3DBA0` | Exactly `0x48` (72) bytes |
| Install the vtable | `0x821368E0`, stored at `0x821D37C4` |
| Set object `+0x10` | 1000 |
| Initialize the base metadata | Six words |
| Zero the embedded record | Offsets `+0x34` through `+0x44`, five words |

The 77 and the 1000 are two defaults for one field. That does not show the
field's meaning, and static evidence does not show that 77 selects this factory
or overwrites the 1000. Ghidra reports no direct caller of the factory and one
direct callee, the allocator, so how the game reaches it is open. Its role
looks like a default factory for the same object type; this is a strong lead,
not a proved registration.

Only two places refer to the vtable: the constructor store at `0x82D90A68` and
the data reference at `0x821D37C4` inside the factory. The read method
`0x82D91078` has one reference, its vtable word at `0x821368EC`, and no direct
caller.

### The embedded record and byte order

The write wrapper `0x821D2F98` and read wrapper `0x821D2F28` each handle the
record as five ordered 32-bit primitives for `type`, `arg1`, `arg2`, `arg3` and
`arg4`, giving exactly 20 bytes. The wrappers pass record offsets 0, 4, 8, 12
and 16 in that order.

| Direction | Wrapper words | Primitive |
| --- | --- | --- |
| Write | `0x821D2FB4..0x821D2FEC` | `0x821D3EA0`: compares buffer byte-order state `+0x08` with the state at `0x82F78854`, reverses the four bytes of the source word only when they differ, then calls buffer slot `+0x08` with length 4 |
| Read | `0x821D2F44..0x821D2F7C` | `0x822D93E8`: calls buffer slot `+0x04` with length 4 and the destination pointer (`0x822D9404..0x822D9418`), then compares the two states and reverses the four destination bytes in place only when they differ (`0x822D9420..0x822D9484`) |

Because each primitive reverses its bytes only when the buffer state differs
from the guest's active state, this page makes no claim of one fixed wire
byte order. The controlling state decides it.

## The factory row and the function table

The factory pointer occurs exactly once in the initialized image, at
`0x8216CC08`, followed by descriptor `0x40002C03` at `0x8216CC0C`. The rows
around it are not a registry of network objects. They belong to one ordered
run of 8-byte rows, each a function start followed by a descriptor word.

| Fact | Value |
| --- | --- |
| Lower boundary | `0x8216B800`; the pair before it, at `0x8216B7F8`, is zero |
| Walked extent | Half-open `[0x8216B800, 0x8218A050)`, 15,626 rows |
| Last row | `0x8218A048`, targeting `0x827F7860` |
| Target span | `0x821B0000` through `0x827F7860`, strictly increasing |
| Descriptor top bits `01` | 15,590 rows; the first 4,976 of them end at `0x82175378`, with targets through `0x82344650`, and 4,900 of those targets are exact Ghidra function starts |
| Descriptor top bits `11` | 36 rows; the first changeover is at `0x82175380` |
| What ends the walk | The next pair targets `0x827F7C50` with descriptor `0x00001414`, which lacks descriptor bit 30 |

The factory is one row among 15,626 whose targets spread across the
executable. The rows stay unbroken for at least 64 words on each side of the
factory row, and include several function starts that Ghidra does not name.

The walked run is the first part of a larger directory. The PE header places
the Exception directory at `0x8216B800` with 28,353 rows through `0x821A2E08`,
inside the `.pdata` section. The SDK loader reads 8-byte rows of this shape as
runtime function entries, each with a function start and an encoded length.
The header and loader evidence is in
[`RVA-F-0362`](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362/selectedAlwaysAtWarClosureBoundary/currentEvidence/sharedChecks/exceptionMetadata).
The 15,626 rows are the part inspected for ordered rows, not the full
directory.

The table gives no support for factory registration of wire messages:

- No literal 77 occurs in the factory row or in the twelve words around it.
- Ghidra reports zero references to the table root `0x8216B800`, the factory
  row `0x8216CC08` and the walk end `0x8218A050`.
- No supported consumer maps a serialized leading 77 to
  `NetworkCommandObjectFactory`.

Zero guest references do not rule out use by the loader, an unwinder, a
debugger or other platform code. Which platform component reads the directory
at run time, and the meaning of each descriptor bit, are not established here.

## Addresses

| Address | Role |
| --- | --- |
| `0x821368E0` | Command object vtable; five entries through `0x821368F0` |
| `0x82D90A18` | Outbound constructor; copies the record to `+0x34..+0x44`; stores 77 at `+0x10` |
| `0x82D910C0`, `0x82D91078`, `0x82D91C58` | Write, read and local drain slots |
| `0x82CB1F78`, `0x82CB1EC8` | Base envelope write and read helpers |
| `0x82CB1F9C..0x82CB1FF8` | Base write calls in order |
| `0x82CB1EE4..0x82CB1F58` | Base read calls in order; the reader ends at `0x82CB1F70` |
| `0x821D2F98`, `0x821D2F28` | Embedded record write and read wrappers |
| `0x821D3EA0`, `0x822D93E8` | Four-byte write and read primitives |
| `0x82F78854` | Byte-order state that the primitives compare with the buffer state |
| `0x821D3778` | `NetworkCommandObjectFactory` |
| `0x82D3DBA0` | Allocator the factory calls |
| `0x8216CC08`, `0x8216CC0C` | Factory pointer and its descriptor `0x40002C03` |
| `0x8216B800`, `0x8218A050` | Start and half-open end of the walked function table run |

Ghidra's decompilation of the two base helpers, both record wrappers and the
read primitive stops early at the known Xenon thunk limit. Their order and
byte counts come from exact image words, with narrow recompiled-code
corroboration. The write primitive `0x821D3EA0` and the constructor
`0x82D90A18` decompile in full.

## Limits and open questions

The object layer is closed. These points are not, and the recovered code does
not establish them:

- Complete outer packet framing, and any headers outside the helpers above.
- What the leading 77 means, whether any outer code consumes it before the read
  method runs (the write path emits 52 bytes and the read path consumes 48), and
  whether it is unique.
- What the six metadata words mean.
- Target encoding, batching, and Xbox session or platform transport.
- Delivery, runtime ordering, and any single wire byte order.
- Whether 77 reaches `NetworkCommandObjectFactory`, and how the factory is
  registered.
- Which platform component reads the function table, and its descriptor bits.

## Evidence

- [Wire serialization record](../../manifests/xbox-network-message-root.json#/wireSerialization)
- [Internal record and queue](../../manifests/xbox-network-message-root.json#/internalRepresentation)
- [Xbox network messages](xbox-network-messages.md)
