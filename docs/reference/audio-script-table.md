# Audio manager and 2D script table

The audio manager owns a low-level stream system and 2D script pointer table.
Names are recovered, not debug symbols. Evidence is static except where runtime
correlation is stated; ownership does not prove successful I/O or playback.

## Audio manager ownership

`AudioManagerCreateAndInit` (`0x82E43C80`) allocates and constructs a
`0x4C8`-byte manager, publishes it at `0x8314F084`, then initializes it:

| Offset | Recovered role |
| --- | --- |
| `+0x1C` | Owned `0x6C`-byte low-level audio object |
| `+0x350` | 2D script pointer table |
| `+0x358` | 2D script table bound |

Constructor: `0x82D52338`; initializer: `0x82D52AE8`, within the manifests'
recorded scope. Original class name remains unknown.

## Low-level stream owner

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

Types 2/3 are numeric dispatch values, not established 2D/3D identities. The
lifecycle search found only the dispatcher as a modeled caller of the writer, no
code caller for the dispatcher, and no slot `+0x4` read in their 36
instructions. First handle use, validity, close and release remain unknown.

## 2D script table lifecycle

`Audio2DScriptPointerTablePopulate` (`0x82D47128`) resets the collection, stores
input count at `+0x358`, allocates count times four bytes, publishes `+0x350`,
and inserts existing pointers without constructing entries.

`Audio2DScriptPointerTableReset` (`0x82D4FA30`) walks nonzero table/bound. Each
non-null entry dispatches first-word slot `+0x8` with entry in `r3`, `1` in
`r4`. After return, or for null entries, it reloads the table and clears the
slot. Reloaded bound requires stable collection state and returning calls to
visit every original slot.

It passes nonzero backing storage to `0x82D3D9F0`; return clears `+0x350` then
`+0x358`. Zero-pointer flow clears only the bound. Populate passes the same
manager before publishing count/allocation. Entry destructor semantics and
backing-helper freeing effects remain unknown.

## Bounded lookup and handoff

`Audio2DScriptEntryLookup` (`0x82D4E5C8`) returns table `+0x350`[ID] for
unsigned ID below `+0x358`, using four-byte entries; otherwise it diagnoses an
illegal 2D script and returns null. The caller retains non-null results into
`0x82D4F678`, which sign-extends entry halfword `+0x6` into prepared word
`+0x0`. Both fields' higher-level semantics remain unknown.

Inserted pointers correlate with constructor `0x82D46D28` and a shared
first-word candidate, without establishing concrete type, semantic vtable name
or successful prepared record.

## Evidence boundaries

- Halfword `+0x6`, entry type/lifetime and type-2/type-3 semantics remain unknown.
- Ownership/lookup establishes no runtime mutation, replacement, hook or SDK behavior.

## Evidence sources

- [Audio initialization and stream
  ownership](../../manifests/audio-initialization-stream-ownership.json)
- [Audio 2D script table
  ownership](../../manifests/audio-2d-script-table-ownership.json)
- [Audio pointer-table reset](../../manifests/audio-pointer-table-reset.json)
- [Audio 2D script entry lookup](../../manifests/audio-2d-script-entry-lookup.json)
- [Catalog contract](../catalogs.md)
