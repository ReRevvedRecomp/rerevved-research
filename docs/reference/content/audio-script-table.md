# Audio manager and 2D script table

The audio manager holds a low-level stream system and a 2D script pointer table.
Names are recovered, not debug symbols. Evidence is static except where runtime
correlation is stated. Holding these objects does not show successful I/O or
playback.

## Audio manager layout

`AudioManagerCreateAndInit` (`0x82E43C80`) allocates and constructs a
`0x4C8`-byte manager, publishes it at `0x8314F084`, then initializes it:

| Offset | Recovered role |
| --- | --- |
| `+0x1C` | The manager's `0x6C`-byte low-level audio object |
| `+0x350` | 2D script pointer table |
| `+0x358` | 2D script table size limit |

The constructor is `0x82D52338` and the initializer is `0x82D52AE8`, within the
scope recorded in the manifests. The original class name remains unknown.

## Low-level stream object

The `0x6C`-byte object uses vtable `0x82147C38`:

| Item | Offset | Recovered role |
| --- | --- | --- |
| Vtable slot | `+0x0` | Initialization at `0x82D457E0` |
| Vtable slot | `+0x14` | Stream setup dispatch at `0x82D46380` |
| Object field | `+0x30` | Low-level driver handle |
| Object field | `+0x54` | Array of stream slots for type 2 |
| Object field | `+0x58` | Array of stream slots for type 3 |

Stream slots are `0x38` bytes. `FAudioSystemMilesStreamOpen` at `0x82D461E8`
calls the Miles wrapper at `0x82A34630` and stores its result at slot `+0x4`.

Types 2 and 3 are numeric dispatch values, not established 2D and 3D
identities. The lifecycle search found only the dispatcher as a modeled caller of
the writer, no code caller for the dispatcher, and no slot `+0x4` read in their
36 instructions. First handle use, validity, close and release remain unknown.

## 2D script table lifecycle

`Audio2DScriptPointerTablePopulate` (`0x82D47128`) resets the collection, stores
the input count at `+0x358`, allocates the count times four bytes, publishes
`+0x350`, and inserts existing pointers without constructing entries.

`Audio2DScriptPointerTableReset` (`0x82D4FA30`) walks the table when its pointer
and size limit are nonzero. Each non-null entry dispatches first-word slot `+0x8`
with the entry in `r3` and `1` in `r4`. After the call returns, or for null
entries, it reloads the table and clears the slot. Because it reloads the size
limit, visiting every original slot requires stable collection state and calls
that return.

It passes nonzero backing storage to `0x82D3D9F0`. After that call returns,
it clears `+0x350` and then `+0x358`. A zero pointer skips the call and clears
only the size limit. Populate passes the same manager before publishing the count
and allocation. The entry destructor behavior and whether the backing helper
frees storage remain unknown.

## Lookup and handoff

`Audio2DScriptEntryLookup` (`0x82D4E5C8`) returns table `+0x350`[ID] for an
unsigned ID below `+0x358`, using four-byte entries. For any other ID it reports
an invalid 2D script and returns null. The caller passes non-null results on to
`0x82D4F678`, which sign-extends entry halfword `+0x6` into prepared word `+0x0`.
The higher-level meaning of both fields remains unknown.

The inserted pointers correlate with constructor `0x82D46D28` and a shared
first-word candidate. That does not establish a concrete type, a semantic vtable
name or a successful prepared record.

## Evidence boundaries

- Halfword `+0x6`, the entry type and lifetime, and the meaning of types 2 and 3
  remain unknown.
- The table layout and lookup establish no runtime mutation, replacement, hook or
  SDK behavior.

## Evidence sources

- [Audio initialization and stream
  setup](../../../manifests/audio-initialization-stream-ownership.json)
- [Audio 2D script table
  layout](../../../manifests/audio-2d-script-table-ownership.json)
- [Audio pointer-table reset](../../../manifests/audio-pointer-table-reset.json)
- [Audio 2D script entry lookup](../../../manifests/audio-2d-script-entry-lookup.json)
- [Catalog contract](../../catalogs.md)
