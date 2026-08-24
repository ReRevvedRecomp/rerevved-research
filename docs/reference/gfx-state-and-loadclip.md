# GFx state and MovieClipLoader requests

The recovered GFx state bag, MovieClipLoader owner interface, native
`loadClip` handler, request objects, and fulfillment routes form one bounded
request flow. The semantic names below are recovered labels, not original
debug symbols. The evidence is static unless stated otherwise.

## State bag and owner forwarding interface

Two related vtables have different ownership roles:

| Vtable | Role | Recovered slots |
| --- | --- | --- |
| `0x8213CF60` | One concrete synchronized state bag | `+0x8` set or erase, `+0xC` keyed lookup |
| `0x8213CF34` | MovieClipLoader owner forwarding interface at owner `+0x10` | `+0x8` set forwarder, `+0xC` get forwarder |

`GfxStateBagSetOrErase` at `0x821EE910` derives the installed key from a
non-null state object's field `+0x10`. When the state object is null, it erases
the separately supplied key. `GfxStateBagGet` at `0x821EEA38` searches the
local synchronized container and falls back to its parent bag on a local miss.

The owner forwarders at `0x821E2B30` and `0x821E2B98` resolve a backing
provider before calling its corresponding slot. The owner interface is not the
concrete bag, and the recovered concrete bag is not proved to be the only
provider implementation.

## Native loadClip registration

The native registration data pairs the `MovieClipLoader` class name with the
`loadClip` method name. The method-name entry at `0x8211DB70` is paired with
handler entry `0x8211DB74`, which resolves to `MovieClipLoaderLoadClipHandler`
at `0x82295018`.

The bounded incoming packet exposes these consumed fields:

| Offset | Recovered role |
| --- | --- |
| `+0x4` | Handler state initialized on entry and finalized on exit |
| `+0x8` | Receiver used for the first request-dependent virtual dispatch |
| `+0x18` | Argument-extraction context |
| `+0x1C` | Argument count, required to be at least two |

The handler extracts arguments zero and one and selects one of two request
builders.

## Request construction and attachment

`MovieClipLoaderBuildRequestDirect` at `0x82229AA0` and
`MovieClipLoaderBuildRequestAlternate` at `0x82229608` each allocate and
initialize a `0x38`-byte request. Both forward a non-null result to
`MovieClipLoaderAttachRequest` at `0x82229C00`. The attachment function reads
the request string at request offset `+0xC`.

The common flow is:

`loadClip handler` -> `direct or alternate request builder` ->
`MovieClipLoaderAttachRequest`.

The two builders establish alternate destination paths, not distinct public
request types.

## Task-manager lookup and fulfillment

The attachment boundary looks up GFx state key `0x16` through the owner
interface at `+0x10`. That key is the recovered `State_TaskManager` key.

- A null lookup is an expected fallback. The request is appended through the
  owner field at `+0x220`, and the downstream selection uses the synchronous
  queue.
- A non-null result can reach `MovieClipLoaderFulfilledRequestHandler` at
  `0x82229518`. That handler selects one of the bounded constructors at
  `0x82227EF0` or `0x822270F8` and appends a non-null constructed result through
  owner field `+0x224`.
- Both fulfilled constructors repeat a keyed lookup through the same owner
  interface.

A null task-manager lookup is therefore not evidence of a missing setter or a
fault. The exact provider implementation and wider request/result container
types remain unresolved.

## Non-convergence boundary

No bounded tracked edge connects this MovieClipLoader request flow to the
DefineExternalImage tag path. DDS or PNG suffixes, two request arguments, and
eventual renderer use do not establish that convergence. This page assigns no
external-image descriptor, file opener, creator, mapping, or renderer path to
MovieClipLoader.

The static flow also proves no request success, visible content result,
filesystem fallback, package mapping, guest-memory mutation, hook, or SDK
behavior.

## Evidence sources

- [GFx loadClip state provider](../../manifests/gfx-ui-loadclip-state-provider.json)
- [GFx MovieClipLoader request boundary](../../manifests/gfx-ui-moviecliploader-request-boundary.json)
- [Catalog contract](../catalogs.md)
