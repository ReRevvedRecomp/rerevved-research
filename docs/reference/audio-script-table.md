# Audio manager and 2D script table

The published audio manager owns both a low-level stream system and a bounded
2D script pointer table. The semantic names below are recovered labels, not
original debug symbols. Static ownership and bounded runtime correlation are
identified separately.

## Audio manager ownership

`AudioManagerCreateAndInit` at `0x82E43C80` allocates, constructs, publishes,
and initializes a `0x4C8`-byte audio manager. Global `0x8314F084` stores the
published pointer. The manager layout includes:

| Offset | Recovered role |
| --- | --- |
| `+0x1C` | Owned `0x6C`-byte low-level audio object |
| `+0x350` | 2D script pointer table |
| `+0x358` | 2D script table bound |

The manager constructor is `0x82D52338`. Initializer `0x82D52AE8` has the
bounded audio-manager initialization role recorded by the source manifests.
No original manager class name is assigned.

## Low-level stream owner

The `0x6C`-byte low-level object uses vtable `0x82147C38`. Its recovered
fields and slots are:

| Item | Offset | Recovered role |
| --- | --- | --- |
| Vtable slot | `+0x0` | Initialization at `0x82D457E0` |
| Vtable slot | `+0x14` | Stream setup dispatch at `0x82D46380` |
| Object field | `+0x30` | Low-level driver handle |
| Object field | `+0x54` | Type-2 stream-slot array |
| Object field | `+0x58` | Type-3 stream-slot array |

Stream slots are `0x38` bytes. `FAudioSystemMilesStreamOpen` at `0x82D461E8`
calls the Miles wrapper at `0x82A34630` and stores its result at slot `+0x4`.

Type 2 and type 3 are recovered numeric dispatch values only. The arrays are
not named 2D and 3D, and static ownership does not prove a successful stream
open or playback.

A bounded lifecycle search found the dispatcher as the sole modeled caller of
the stream-open writer and found no code caller for the dispatcher. Direct
classification across those two functions scanned 36 instructions and found
no stream-slot `+0x4` read. The handle's first use, validity check, close, and
release path therefore remain unresolved.

## 2D script table lifecycle

`Audio2DScriptPointerTablePopulate` at `0x82D47128` rebuilds the manager-owned
collection. It resets the prior collection, stores the input-range count at
manager `+0x358`, allocates count times four bytes, stores the table pointer at
`+0x350`, and inserts pre-existing pointers. It does not allocate or construct
the entries.

`Audio2DScriptPointerTableReset` at `0x82D4FA30` is the recovered reset owner
for the same table and bound. Table and bound must be treated as one collection
contract.

## Bounded lookup and handoff

`Audio2DScriptEntryLookup` at `0x82D4E5C8` accepts an unsigned script ID. An ID
below the word at manager `+0x358` returns the pointer at table `+0x350` plus
ID times four. An out-of-range ID reports the self-identifying illegal-2D-script
diagnostic and returns null.

The recovered caller preserves a non-null lookup result and passes it to the
prepared-record population function at `0x82D4F678`. That consumer
sign-extends the entry halfword at `+0x6` into prepared-record word `+0x0`.
The halfword's original meaning and the prepared record's higher-level audio
semantics remain unresolved.

Inserted pointers correlate with constructor site `0x82D46D28` and a shared
first-word candidate. The available layout does not establish a concrete entry
type, semantic vtable name, successful prepared record, stream I/O, or playback.

## Evidence boundaries

- Entry halfword `+0x6` remains an unnamed numeric field.
- The inserted entry type and lifetime are not established by lookup shape or
  the shared first word.
- Type-2 and type-3 stream arrays retain numeric names until a direct semantic
  edge is recovered.
- The ownership and lookup flow does not define runtime mutation, audio
  replacement, hook, or SDK behavior.

## Evidence sources

- [Audio initialization and stream ownership](../../manifests/audio-initialization-stream-ownership.json)
- [Audio 2D script table ownership](../../manifests/audio-2d-script-table-ownership.json)
- [Audio 2D script entry lookup](../../manifests/audio-2d-script-entry-lookup.json)
- [Catalog contract](../catalogs.md)
