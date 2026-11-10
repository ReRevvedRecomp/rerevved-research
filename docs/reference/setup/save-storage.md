# Save storage and slot identity

The player-facing slot label is separate from the internal storage file name.
Ruleset persistence must use the internal file name inside the selected user
and device content namespace.

## Selected content record

The picker has 11 records with stride `0x164`. The accepted
`SelectedContentRecordCopy` (`0x82DDBFF8`) copies `0x13C` bytes to its caller:

| Offset | Recovered meaning |
| --- | --- |
| `0x108` | NUL-terminated internal slot file name read by both the manual save function and the load function |

Sidecar keys need the selected user and device namespace because file names
can repeat. The raw slot file name roots live at `0x82F77368`, but the code uses
the normalized record field `0x108`, not the localized manual or automatic
labels.

The recorded manual-save template is 9 bytes (SHA-256
`06DE6F4750B01FE77895587ABF06D78090DBB24410874FB60941A558D9B8AE51`); the
automatic-save template is 11 bytes (SHA-256
`D99FE9A92507C5B94D7770DE2753A005F1D82C7F24E8BFE90A82DAF1AC314F21`).

Digests identify recorded UTF-8 text without terminators, not guest addresses or
original encoding.

## Selected-user object lifetime boundary

The `0x78`-byte selected-user object is initially published through
`0x8314EFE0`. The exact inventory has 107 READ rows in 65 functions plus three
data sources, with no modeled WRITE. The builder and constructor reduce to
non-returning thunks, and `0x82E633C0` truncates on bad data. Teardown,
republication and the lifetime of profile-service `+0x18` are not yet
established. They are not excluded elsewhere.

## Recovered functions

Names below describe recovered semantics, not original debug symbols.

| Address | Semantic name | Role |
| --- | --- | --- |
| `0x82DDDFC0` | `SaveContentEnumerate` | Resolves the selected user and enumerates eleven type-1 content records. |
| `0x82D83208` | `SaveSlotPick` | Opens the slot picker in save mode and returns an accepted record. |
| `0x82D834F0` | `LoadSlotPick` | Opens the slot picker in load mode and returns an accepted record. |
| `0x82DDBFF8` | `SelectedContentRecordCopy` | Copies the accepted record payload to its caller. |
| `0x82D82510` | `SaveGameToSelectedContent` | Uses record `+0x108`, serializes the game, and finalizes the content file. |
| `0x82D84238` | `LoadGameFromSelectedContent` | Uses record `+0x108`, opens the content, and invokes the native deserializer. |

## Sidecar intervention edges

Load entry `0x82D84238` comes before the open and deserializer call at
`0x82D844CC`, which allows ruleset rejection before state changes. The
serializer returns at `0x82D82984`. The combined finalization result at
`0x82D829E8` is in `r25`, with the file name in `r29`. Atomic sidecar
replacement requires a nonzero final result.

## Implementation guard

The host sidecar contains the locked ruleset ID, version and configuration
hash in the native slot's user and device namespace. Check it before loading;
replace it atomically through a temporary file after a successful save. The
native save stays unchanged.
