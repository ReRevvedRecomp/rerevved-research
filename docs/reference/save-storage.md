# Save storage and slot identity

The player-facing slot label is separate from the internal storage filename.
Ruleset persistence must use the internal filename inside the selected
user/device content namespace.

## Selected content record

Picker has 11 records, stride `0x164`; accepted `SelectedContentRecordCopy`
(`0x82DDBFF8`) copies `0x13C` bytes to caller:

| Offset | Recovered meaning |
| --- | --- |
| `0x108` | NUL-terminated internal slot filename read by both manual save and load owners |

Sidecar keys need selected user/device namespace: filenames can repeat. Raw
roots `save1` through `save9`, `save0`, `saveb` through `savei` live at
`0x82F77368`, but use normalized record `0x108`, not localized manual/automatic
labels.

The recorded manual-save template is 9 bytes (SHA-256
`06DE6F4750B01FE77895587ABF06D78090DBB24410874FB60941A558D9B8AE51`); the
automatic-save template is 11 bytes (SHA-256
`D99FE9A92507C5B94D7770DE2753A005F1D82C7F24E8BFE90A82DAF1AC314F21`).

Digests identify recorded UTF-8 text without terminators, not guest addresses or
original encoding.

## Selected-user owner lifetime boundary

The `0x78`-byte owner initially publishes via `0x8314EFE0`. Exact inventory has
107 READ rows/65 functions plus three data sources, no modeled WRITE. Builder/
constructor reduce to non-returning thunks; `0x82E633C0` truncates on bad data.
Teardown, republication and profile-service `+0x18` lifetime remain unproved,
not excluded elsewhere.

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

Load entry `0x82D84238` precedes open/deserializer `0x82D844CC`, allowing
ruleset rejection before state change. Serializer returns `0x82D82984`; combined
finalization result at `0x82D829E8` is `r25`, with filename in `r29`. Atomic
sidecar replacement requires nonzero final result.

## Implementation guard

Host sidecar contains locked ruleset ID/version/configuration hash in native
slot's user/device namespace. Check before load; atomically replace via
temporary file after save success. Native save stays unchanged.
