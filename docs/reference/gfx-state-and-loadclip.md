# GFx state and MovieClipLoader requests

This static flow joins GFx state lookup, MovieClipLoader requests and
fulfillment. Names are recovered, not debug symbols; runtime evidence is stated
explicitly.

## State bag and owner forwarding interface

Two related vtables have different ownership roles:

| Vtable | Role | Recovered slots |
| --- | --- | --- |
| `0x8213CF60` | One concrete synchronized state bag | `+0x8` set or erase, `+0xC` keyed lookup |
| `0x8213CF34` | MovieClipLoader owner forwarding interface at owner `+0x10` | `+0x8` set forwarder, `+0xC` get forwarder |

`GfxStateBagSetOrErase` (`0x821EE910`) installs non-null object key `+0x10`, or
erases the supplied key for null. `GfxStateBagGet` (`0x821EEA38`) searches the
synchronized local container, then parent on a miss. Forwarders `0x821E2B30` and
`0x821E2B98` resolve a provider before dispatch. Owner interface and concrete
bag differ; other provider implementations remain possible.

## Native loadClip registration

Registration pairs `MovieClipLoader`.`loadClip`: name entry `0x8211DB70`,
handler entry `0x8211DB74` -> `MovieClipLoaderLoadClipHandler` (`0x82295018`).
Consumed packet fields:

| Offset | Recovered role |
| --- | --- |
| `+0x4` | Handler state initialized on entry and finalized on exit |
| `+0x8` | Receiver used for the first request-dependent virtual dispatch |
| `+0x18` | Context for extracting arguments |
| `+0x1C` | Argument count, required to be at least two |

The handler extracts arguments zero and one and selects one of two request
builders.

## Request construction and attachment

`MovieClipLoaderBuildRequestDirect` (`0x82229AA0`) and
`MovieClipLoaderBuildRequestAlternate` (`0x82229608`) allocate/initialize
`0x38`-byte requests, forwarding non-null results to
`MovieClipLoaderAttachRequest` (`0x82229C00`), which reads string `+0xC`.

`loadClip handler` -> `direct or alternate request builder` ->
`MovieClipLoaderAttachRequest`: alternate destinations, not distinct public
types.

## Task-manager lookup and fulfillment

Attachment queries `State_TaskManager` key `0x16` through owner `+0x10`:

- Null: append through `+0x220`, selecting synchronous fallback queue.
- Non-null: can reach `MovieClipLoaderFulfilledRequestHandler` (`0x82229518`),
  selecting `0x82227EF0` or `0x822270F8` and appending non-null construction
  through `+0x224`. Both constructors repeat that keyed lookup.

Null is expected fallback, not evidence of missing setter/fault. Provider and
wider request/result container types remain unknown.

## Non-convergence boundary

No tracked edge in this bounded flow joins DefineExternalImage. DDS/PNG
suffixes, two arguments and eventual rendering establish no shared descriptor,
opener, creator, mapping or renderer path. Request success, visible content,
filesystem/package mapping, guest-memory mutation, hook and SDK behavior remain
unproved.

## Evidence sources

- [GFx loadClip state provider](../../manifests/gfx-ui-loadclip-state-provider.json)
- [GFx MovieClipLoader request
  boundary](../../manifests/gfx-ui-moviecliploader-request-boundary.json)
- [Catalog contract](../catalogs.md)
