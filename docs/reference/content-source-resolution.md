# Frontend content staging and source resolution

Preload, downloadable-content staging, registered sources and bare-name
resolution are separate static boundaries. Names are recovered, not debug
symbols; this lookup contract proves neither runtime delivery nor acceptance.

## Separate frontend stages

`GfxMainMenuPreloadStage` (`0x82E2C770` through `0x82E2C88F`) calls
`GfxCompleteMainMenuPreload` at `0x82E2C85C` before optional display-list clear.

`FrontendContentStage` starts at `0x82E2C890`, with two direct calls:

| Callsite | Target | Recovered role |
| --- | --- | --- |
| `0x82E2C944` | `DlcAggregateBuildAndRegister` at `0x82E29570` | Enumerate downloadable content and build one registered aggregate |
| `0x82E2CA1C` | `ScenarioDefinitionDiscover` at `0x82DAF700` | Start bounded numbered scenario-definition discovery |

Adjacency does not merge stages. The downloadable-content selector remains
unnamed; sign-in, license, authorization, listing, selection and gameplay
semantics remain unproved.

## Registered-source ownership

Global `0x8314F0C0` holds registered sources. `RegisteredSourceAppend`
(`0x82E7FDF8`) attempts lazy initialization on null, publishing a successful
collection before appending. Separate `0x8314F0C4` holds `Resource\Common`
fallback; its initializer never appends it to the registered vector.

`DlcAggregateBuildAndRegister` enumerates type-2 records, opens accepted mounted
roots, builds from root-level `dlc.fpk`, and appends the aggregate once.
`name.txt` is optional identification. Bare scenario/map/DDS entries must be
inside `dlc.fpk`; adjacent files do not register their directory.

Three named-map DDS suffixes identify height, mountain/hill blend and
lightmap. Their three string addresses had zero exact references; the
inspected map consumer was a thunk and the terrain-loader body was truncated.
Dimensions, format, mips, byte order, row layout and payload remain unknown;
generic texture scale does not establish a byte-level contract for authoring.

## Bare-name lookup order

For the bounded named-map resource path, lookup order is:

1. Attempt the direct loose-file opener.
2. Search the vector of registered sources through
   `RegisteredSourceReverseResolver` at `0x82E80028`.
3. Consult the separate `Resource\Common` fallback.

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

`MapListSelectionStateUpdate` (`0x82DADC88`) stores retained input at `+0x134`.
Zero override calls `NumberedMapListSelect` (`0x82E2B8D0`), storing return at
`+0x138`; nonzero override is stored directly. Selector requests unsigned input
modulo current count, plus one.

Parser `MAPNUMBER` is signed variator slot 32, copied to `0x830E9010`. The
bounded parser/application/scanner/updater/selector set has no direct edge to
either argument. Fields remain neutral; menu numbering, map identity, setup and
runtime selection are unresolved. See the
[selector packet](../../manifests/map-list-selection-owner.json).

| Direct caller | Arguments and limit |
| --- | --- |
| Five-instruction `0x82D06380` | Forwards incoming word as `r4`, forces `r5` zero, loads `r3` from `0x8314EFC8`, tail-jumps at `0x82D06390`. |
| Complete `0x82D91A78` | Loads `r4` from incoming object `+0x34`, forces `r5` zero, uses same receiver, calls at `0x82D91A94`, returns one. Field writer/meaning unresolved. |

Neither establishes MAPNUMBER linkage; see the
[producer packet](../../manifests/map-list-update-argument-producers.json).

## Evidence boundaries

- Registration proves no runtime enumeration, archive open, acceptance, listing
  or gameplay start.
- Container layout, synchronization and contents remain unknown.
- Resolver order defines no signature, license, authentication, STFS, installation,
  archive-writing or host-path policy, nor Xbox DDS byte contract.
- No title patch, hook, API, mod, SDK or archive mutation follows.

## Evidence sources

- [Main-menu File Data handoff](../../manifests/gfx-main-menu-filedata-handoff.json)
- [Map content precedence](../../manifests/map-content-precedence.json)
- [Map delivery boundary](../../manifests/map-delivery-boundary.json)
- [MapList selection owner](../../manifests/map-list-selection-owner.json)
- [Registered-source delivery
  boundary](../../manifests/registered-source-delivery-boundary.json)
- [Catalog contract](../catalogs.md)
