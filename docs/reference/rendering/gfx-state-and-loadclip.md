# GFx state and MovieClipLoader requests

This static flow connects GFx state lookup, MovieClipLoader requests and
fulfillment. Names are recovered, not debug symbols. Runtime evidence is stated
explicitly.

## State bag and forwarding interface

Two related vtables play different roles:

| Vtable | Role | Recovered slots |
| --- | --- | --- |
| `0x8213CF60` | One concrete synchronized state bag | `+0x8` set or erase, `+0xC` keyed lookup |
| `0x8213CF34` | MovieClipLoader forwarding interface at object `+0x10` | `+0x8` set forwarder, `+0xC` get forwarder |

`GfxStateBagSetOrErase` (`0x821EE910`) installs a non-null object under key
`+0x10`, or erases the supplied key for null. `GfxStateBagGet` (`0x821EEA38`)
searches the synchronized local container, then the parent on a miss. The
forwarders `0x821E2B30` and `0x821E2B98` resolve a provider before dispatch. The
forwarding interface and the concrete bag differ. Other provider implementations
remain possible.

## Native loadClip registration

Registration pairs the `MovieClipLoader`.`loadClip` name entry `0x8211DB70` with
the handler entry `0x8211DB74`, which leads to `MovieClipLoaderLoadClipHandler`
(`0x82295018`). The handler consumes these argument record fields:

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
`MovieClipLoaderBuildRequestAlternate` (`0x82229608`) allocate and initialize
`0x38`-byte requests. They forward non-null results to
`MovieClipLoaderAttachRequest` (`0x82229C00`), which reads the string at `+0xC`.

The path runs from the `loadClip` handler to either the direct or the alternate
request builder, and from there to `MovieClipLoaderAttachRequest`. The two
builders are alternate destinations, not distinct public types.

## Task-manager lookup and fulfillment

Attachment queries `State_TaskManager` key `0x16` through object `+0x10`:

- Null: append through `+0x220`, selecting the synchronous fallback queue.
- Non-null: can reach `MovieClipLoaderFulfilledRequestHandler` (`0x82229518`),
  which selects `0x82227EF0` or `0x822270F8` and appends the non-null
  construction through `+0x224`. Both constructors repeat that keyed lookup.

Null selects the expected fallback. It is not evidence of a missing setter
or a fault. The provider and the wider request and result container types remain
unknown.

## Where the flows do not meet

No tracked edge in the selected flow links to DefineExternalImage. The DDS and
PNG suffixes, the two arguments and the eventual rendering establish no shared
descriptor, opener, creator, mapping or renderer path. Request success, visible
content, filesystem and package mapping, guest-memory mutation, and hook and SDK
behavior are not yet shown.

## Evidence sources

- [GFx loadClip state provider](../../../manifests/gfx-ui-loadclip-state-provider.json)
- [GFx MovieClipLoader request
  boundary](../../../manifests/gfx-ui-moviecliploader-request.json)
- [Catalog contract](../../catalogs.md)
