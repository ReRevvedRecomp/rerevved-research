# Frontend content staging and source resolution

The frontend preload path, downloadable-content stage, registered-source
collection, and bare-name resolver are separate static boundaries. The
semantic names below are recovered labels, not original debug symbols. This
page describes guest ownership and lookup order; it does not establish runtime
delivery or package acceptance.

## Separate frontend stages

`GfxMainMenuPreloadStage` at `0x82E2C770` owns the bounded preload-completion
stage. It calls `GfxCompleteMainMenuPreload` at `0x82E2C85C` before an optional
display-list clear and ends at `0x82E2C88F`.

`FrontendContentStage` begins separately at `0x82E2C890`. Two direct calls
define its reusable fan-out:

| Callsite | Target | Recovered role |
| --- | --- | --- |
| `0x82E2C944` | `DlcAggregateBuildAndRegister` at `0x82E29570` | Enumerate downloadable content and build one registered aggregate |
| `0x82E2CA1C` | `ScenarioDefinitionDiscover` at `0x82DAF700` | Start bounded numbered scenario-definition discovery |

The adjacent function addresses do not merge the stages. The numeric selector
admitted by the downloadable-content call remains unnamed. These calls prove
no sign-in, license, authorization, menu-listing, selection, or gameplay
meaning.

## Registered-source ownership

Global `0x8314F0C0` stores the registered-source collection pointer.
`RegisteredSourceAppend` at `0x82E7FDF8` checks that pointer and attempts lazy
initialization when it is null. The successful null path publishes the
initialized collection before the supplied source pointer reaches the bounded
append helper.

The separate global at `0x8314F0C4` stores the `Resource\Common` fallback
collection pointer. Its initializer does not append that collection to the
registered-source vector. The two globals therefore represent different
ownership layers and must not be collapsed into one source list.

`DlcAggregateBuildAndRegister` enumerates type-2 content records, opens accepted
mounted roots, supplies the root-level `dlc.fpk` path to the aggregate builder,
and appends the completed aggregate once. Root-level `name.txt` is separate
optional identification data. Bare scenario, map, and DDS names must be entries
inside `dlc.fpk`; placing them beside the archive does not register that
directory as a common resource source.

The three accepted named-map DDS suffixes identify height,
mountain-hill-blend, and lightmap roles. A bounded consumer packet found zero
exact references to their three string addresses, a thunk-only named-map
consumer body, and a truncated terrain-loader body. The static source route
therefore supplies no role-specific dimensions, pixel format, mip behavior,
byte order, row layout, or payload rule. Generic dimension-derived texture
scale is not an authoring byte contract.

## Bare-name lookup order

For the bounded named-map resource path, lookup order is:

1. Attempt the direct loose-file opener.
2. Search the registered-source vector through
   `RegisteredSourceReverseResolver` at `0x82E80028`.
3. Consult the separate `Resource\Common` fallback.

The reverse resolver starts at the final zero-based vector index and decrements
toward zero after failed candidates. Later successful appends therefore outrank
earlier registered peers. Every registered vector entry is attempted before
the separate fallback collection.

The resolver preloads and null-checks the fallback pointer before vector
traversal, but it performs the fallback lookup only after the vector path
produces no result. This distinction matters when instrumenting the resolver:
a fallback-pointer read is not itself a fallback lookup.

Names containing a slash or backslash follow a separate explicit-path branch.
The bare-name ordering does not generalize to that branch. Reverse traversal
also does not establish a complete base-FPK versus DLC-FPK chronology or the
collision order of entries inside one aggregate.

## Numbered MapList selection state

`MapListSelectionStateUpdate` at `0x82DADC88` stores its retained input at
receiver `+0x134`. A zero override calls `NumberedMapListSelect` at
`0x82E2B8D0` and stores the returned entry at `+0x138`; a nonzero override
bypasses the selector and is stored directly at `+0x138`. The selector reduces
its unsigned input modulo the current MapList count, adds one, and requests
that entry.

The scenario parser maps `MAPNUMBER` to signed variator slot 32, and scenario
application copies that slot into the active variator block at `0x830E9010`.
The bounded parser, application, scanner, state-update, and selector functions
contain no direct edge from that slot to either update argument. The two state
fields therefore remain neutral: they are not named `MAPNUMBER`, and menu
numbering, exact map identity, setup, and runtime selection remain unresolved.
See [the exact selector packet](../../manifests/map-list-selection-owner.json).

Two configured direct callers now close neutral update-argument production.
Five-instruction wrapper `0x82D06380` forwards its incoming word as `r4`,
forces `r5` to zero, loads updater receiver `r3` from pointer global
`0x8314EFC8`, and tail-jumps at `0x82D06390`. Complete caller `0x82D91A78`
loads `r4` from its incoming object's `+0x34`, forces `r5` to zero, loads the
same receiver global, calls at `0x82D91A94`, and returns one. The `+0x34`
writer and meaning remain unresolved, and no MAPNUMBER relationship follows.
See [the producer packet](../../manifests/map-list-update-argument-producers.json).

## Evidence boundaries

- Static source registration does not prove runtime enumeration, successful
  archive open, resource acceptance, menu listing, or gameplay start.
- The recovered collection pointers do not establish concrete container
  layouts, synchronization guarantees, or runtime contents.
- No package signature, license, authentication, STFS, installation, archive
  writer, or host-path policy follows from the guest resolver order.
- No Xbox DDS writer contract follows from resource naming, lookup order, or
  the common loader's generic texture scale.
- The flow defines no title patch, runtime hook, API, mod, SDK, or archive
  mutation.

## Evidence sources

- [Main-menu File Data handoff](../../manifests/gfx-main-menu-filedata-handoff.json)
- [Map content precedence](../../manifests/map-content-precedence.json)
- [Map delivery boundary](../../manifests/map-delivery-boundary.json)
- [MapList selection owner](../../manifests/map-list-selection-owner.json)
- [Registered-source delivery boundary](../../manifests/registered-source-delivery-boundary.json)
- [Catalog contract](../catalogs.md)
