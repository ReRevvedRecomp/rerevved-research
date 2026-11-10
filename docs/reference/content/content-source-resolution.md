# Frontend content staging and source resolution

Preload, downloadable-content staging, registered sources and bare-name
resolution are separate static boundaries. Names are recovered, not debug
symbols. This lookup contract shows neither runtime delivery nor acceptance.

## Separate frontend stages

`GfxMainMenuPreloadStage` (`0x82E2C770` through `0x82E2C88F`) calls
`GfxCompleteMainMenuPreload` at `0x82E2C85C` before the optional display-list
clear.

`FrontendContentStage` starts at `0x82E2C890`, with two direct calls:

| Callsite | Target | Recovered role |
| --- | --- | --- |
| `0x82E2C944` | `DlcAggregateBuildAndRegister` at `0x82E29570` | Enumerate downloadable content and build one registered aggregate |
| `0x82E2CA1C` | `ScenarioDefinitionDiscover` at `0x82DAF700` | Start limited discovery of numbered scenario definitions |

Adjacency does not merge the stages. The downloadable-content selector remains
unnamed. Sign-in, license, authorization, listing, selection and gameplay
semantics are not yet established.

## Registered sources

Global `0x8314F0C0` holds the registered sources. `RegisteredSourceAppend`
(`0x82E7FDF8`) attempts lazy initialization on null and publishes a successful
collection before appending. The separate global `0x8314F0C4` holds the common
resource fallback. Its initializer never appends it to the registered vector.

`DlcAggregateBuildAndRegister` enumerates type-2 records, opens accepted mounted
roots, builds the aggregate from the content archive at the root level, and
appends the aggregate once. An optional text file at the root identifies the
package. Bare scenario, map and DDS entries must be inside that archive.
Adjacent files do not register their directory.

Three named-map DDS suffixes identify height, mountain and hill blend, and
lightmap. Their three string addresses had zero exact references. The inspected
map consumer was a thunk and the terrain-loader body was truncated. Dimensions,
format, mips, byte order, row layout and payload remain unknown. A generic
texture scale does not establish a byte-level contract for authoring.

## Bare-name lookup order

For the selected named-map resource path, lookup order is:

1. Attempt the direct loose-file opener.
2. Search the vector of registered sources through
   `RegisteredSourceReverseResolver` at `0x82E80028`.
3. Consult the separate common resource fallback.

The reverse resolver starts at the final zero-based vector index and decrements
toward zero after failed candidates. Later successful appends therefore outrank
earlier registered peers. Every registered vector entry is attempted before the
separate fallback collection.

The resolver preloads and null-checks the fallback pointer before vector
traversal, but it performs the fallback lookup only after the vector path
produces no result. This distinction matters when instrumenting the resolver: a
fallback-pointer read is not itself a fallback lookup.

Names containing a slash or backslash follow a separate explicit-path branch.
The ordering for bare names does not generalize to that branch. Reverse
traversal also does not establish a complete chronology for base and DLC FPKs or
the collision order of entries inside one aggregate.

## Numbered MapList selection state

`MapListSelectionStateUpdate` (`0x82DADC88`) stores its input at
`+0x134`. A zero override calls `NumberedMapListSelect`
(`0x82E2B8D0`) and stores the return value at `+0x138`. A nonzero override is
stored directly. The selector requests the unsigned input modulo the current
count, plus one.

The parser's map number token is signed variator slot 32, copied to
`0x830E9010`. The selected set of parser, application, scanner, updater and
selector code has no direct edge to either argument. The fields remain neutral.
Menu numbering, map identity, setup and runtime selection are unresolved. See
the [selector manifest](../../../manifests/map-list-selection-owner.json).

| Direct caller | Arguments and limit |
| --- | --- |
| Five-instruction `0x82D06380` | Forwards the incoming word as `r4`, forces `r5` to zero, loads `r3` from `0x8314EFC8`, and tail-jumps at `0x82D06390`. |
| Complete `0x82D91A78` | Loads `r4` from the incoming object `+0x34`, forces `r5` to zero, uses the same receiver, calls at `0x82D91A94`, and returns one. The field writer and meaning are unresolved. |

Neither caller establishes a link to the parser's map number token. See the
[producer manifest](../../../manifests/map-list-update-argument-producers.json).

## Evidence boundaries

- Registration shows no runtime enumeration, archive open, acceptance, listing
  or gameplay start.
- Container layout, synchronization and contents remain unknown.
- Resolver order defines no signature, license, authentication, STFS,
  installation, archive-writing or host-path policy, and no Xbox DDS byte
  contract.
- No title patch, hook, API, mod, SDK or archive mutation follows.

## Evidence sources

- [Main-menu File Data handoff](../../../manifests/gfx-main-menu-filedata-handoff.json)
- [Map content precedence](../../../manifests/map-content-precedence.json)
- [Map delivery boundary](../../../manifests/map-delivery.json)
- [MapList selection](../../../manifests/map-list-selection-owner.json)
- [Registered-source delivery
  boundary](../../../manifests/registered-source-delivery.json)
- [Catalog contract](../../catalogs.md)
