# Map size and terrain bias

The recovered gameplay grid initializes to 32 by 32. Different land coverage
inside that grid is a candidate; complete smaller or larger native dimensions
are not established. The [object-grid finding](../../manifests/map-dimension-object-grid-boundary.json)
owns the additional fixed 32 constraint and climate boundary. The
[authored-map loader](../../manifests/map-authoring-loader-boundary.json) and
[resource placement finding](../../manifests/resource-density-generation-boundary.json)
own the reused layout and start-placement contracts.

## Dimensions and backing

Gameplay dimensions at `0x82F77364` and `0x82F77448` initialize to 32; the
selected authored-map loader reads 1024 cells. Terrain/flag storage with
stride 40 and selected transfers of 1600 padded entries do not imply 1600
playable cells.

The selected object operation at `0x82D7E6B8` reaches spatial visitor
`0x821D6340` using Q=`U32[0x8314F2C0]`. The accepted visitor checks unsigned
coordinates against Q+160 and Q+164, then uses the descriptor address
`low32(U32[Q+124] + 16*low28(a + 32*b))`. If admitted, `(32,0)` and `(0,1)`
alias. A rectangle with first bound at least 33 and second bound at least 2
therefore contains this collision. Increasing only the second axis avoids
this particular collision, but its allocation and complete consumers remain
unbound.

The selected consumer calls each nonnull payload's current vptr+0xC with
argument 1, then clears its vector word after return. The callback's effect
is unclassified; it is not proved to delete the object. Exact native words
support this local contract despite truncated decompilation.

| Request | Static assessment | Remaining gate |
|---|---|---|
| Less land inside 32x32 | Candidate authored-map design | Surrounding water remains playable; no inaccessible crop/border contract |
| True smaller dimensions | Partial, with selected dimension-driven loops | Extent producers, fixed constants, generation/start termination and all consumers |
| Wider first axis above 32 | Selected object index aliases adjacent-row cells | Backing and index representation changes before a supported expansion |
| Taller second axis | Avoids this particular collision | Capacity, complete consumers, generation, rendering, saves and peers |
| Larger than existing terrain backing | Unsupported by the bounded storage contract | Representation expansion across every affected plane and consumer |

## Composition and starting locations

Map composition and civilization start preference are separate mechanisms.
The selected setup reads recognized CLIMATE16 at active scenario Q+0x20
(`0x830E8FF0`) and admits signed16 values 0..4. At `0x82D22A04/08` its local
dispatch stores two BE32 words at `0x82F71FD0/D4`. The selected reader below
binds a city-distance AI filter; map-composition meaning remains unbound. No native level names or generator
quantities are assigned from those stores.

The existing resource-placement finding's
`initialSettlerSpawnBoundary/conditionalReordering` binds an actual selected
civilization-specific terrain-score reorder at `0x82CFE908`. It chooses a
strictly-positive maximum and swaps a whole start-coordinate pair. Selected
setup mode 2 bypasses it. Named terrain/civilization meanings, current mode,
score generation, candidate legality and retained ordering remain conditions.
Encoded explicit starting coordinates provide a separate location mechanism;
they do not define terrain preference.

## Selected spatial backing producer

The finding's `spatialBackingProducerBoundary` binds a selected Q
publication/initialization route. Constructor `0x82C783C8` zeros backing
metadata Q+124/+128/+132. A later `0x82C78B60` call writes literal 32 to both
bounds and 1024 to Q+168, then requests 1024 descriptors through `0x822F4CB8`.
The selected allocation helper requests 16,384 bytes and records the returned
pointer and end in the vector metadata. This is requested/recorded extent,
not delivered writable allocation or proof that constructor zeros survived
all intervening helpers.

Descriptor construction still crosses `0x821B7A40` or growth helper
`0x822F5250`; its actual current+0x5C mapping and retained completion remain
unbound. The installed candidate and cold-cache contracts below are conditional.
Its literal bounds are independent of caller dimension arguments in this
selected body. descriptorInitializationBoundary below owns the fast-path initializer
`0x821B7A40`; its next gate is current tail-effect retention. Changed dimensions,
complete generation, rendering, persistence and peer behavior remain unproved.

## Empty descriptor construction

The finding's `descriptorInitializationBoundary` binds `0x821B7A40`:
source begin 0 selects a finite 28-instruction path with no child call. It
zeros destination+4/+8/+12 and returns the original destination. The first
four bytes are not written or read by that path. This is twelve zero metadata
bytes, not a completely zeroed 16-byte descriptor.

Selected caller source words at SP+84/+88/+92 are zero only under retained
r28=0 and frame conditions. With sufficient actual backing and completing
fast-path iterations, the 1024 descriptors for the fixed grid have equal empty
begin/end words and reach the accepted visitor's empty return. The current tail
virtual+0x5C can still mutate them; actual current mapping, completing cold
construction and retention before visitor ingress remain gates. Growth,
allocator delivery and complete generation remain separate.

## Selected construction-tail candidate

`tailTargetRetentionBoundary` binds installed table 0x82120EB0+0x5C,
cell 0x82120F0C, to 0x82E10450. Current receiver 0x8314F28C is initially zero;
the reused publisher's later current+0x0C call at 0x82E2E504 still gates
retention. No current target or publication-before-tail ordering follows.

With nonzero cache X at 0x8314EF84, the candidate returns U32[X+12] in a
16-instruction arm without children or loops. It writes only 24 stack bytes.
Under explicit stack/control/map alias exclusions, it restores the full 64-bit
r30/r31 values and preserves the protected bounds, vector and 2048 descriptor
words through the caller's Q+178=1 store at 0x82C78D54. Caller completion and later retention
to visitor 0x821D6340 remain open. Initial X is zero, so the uncached path's
allocator call 0x82E10484 and later child remain separate completion gates.

## Conditional cold-cache construction

`coldCacheConstructionBoundary` binds the zero-cache arm of 0x82E10450.
After a nonzero 16-byte allocation and retained child completion, it samples
V=U32[P+12] at 0x82E104B0, then publishes wrapper P at 0x82E104B4 to cache
0x8314EF84. Its return is V; the cache contains P. The null arm reads guest
address 0 before storing cache 0, so it supplies no safe-return-zero theorem.

Child 0x82E70D28 conditionally constructs separate 864- and 336-byte objects.
Its selected +12 replacement at 0x82E70E64 re-reads P+8 after any old-object
release. Nested allocation/constructors, current virtual effects, atomic-loop
completion and alias/field retention remain gates. Requested extents alone
prove no storage delivery. Current service/table/cache, caller restore and
caller-to-visitor ordering remain open; no map-size feasibility follows.

`firstObjectConstructionPrefixBoundary` narrows the first 864-byte object's
constructor request through two direct prefixes and the original save thunk.
It reaches unopened `0x82358A88` with the full incoming object argument.
Its 24 selected words make 13 stack stores covering 80 distinct bytes before
that request; disjoint stack storage is required to preserve wrapper, object,
map and backing fields. Normal helper return alone would prove no retention.
Constructor return/object delivery and the later cache/mapping remain open.

## Exact CLIMATE reader and AI candidate guard

`climateReaderBoundary` binds reads 0x82CB53A0/0x82CB53BC of the two setup
words inside the selected AI evaluator. The local code forms the absolute
distance between signed city-record field+50 and half the signed dimension
at 0x82F77448, then classifies it with the current setup thresholds into bands
3/4/5. Under its owner/candidate admission gates, a mismatching candidate skips
to 0x82CB548C. This is a conditional AI filter, without final-choice or
production delivery proof.

The selected reader writes no terrain cells or dimensions. Generator and
terrain-composition relevance remain unbound.

## CLIMATE terrain receiver fields

`climateTerrainInputRetentionBoundary` reuses the accepted terrain handoff to
0x82C6E898. It conditionally stores T0 at receiver+936 at 0x82C6E9B8,
T1 at +932 at 0x82C6E9BC and trunc(s32(T0)/2) at +940 at 0x82C6E9F0.
Required helper returns and the same retained receiver remain premises.

Its immediate 0x82C6C860 helper traverses fifteen 24-byte records beginning
at +544; its direct relative accesses reach +892 and do not select those climate
fields. Opaque calls/aliases remain outside that negative. An exact reader
of +932/+936/+940 is required before assigning composition, biome, land-area
or dimension effects. Fixed 32-by-32 dimensions, stride 40 and prebuilt terrain
remain separate.

## Bounded terrain reader navigation

`climateFieldReaderNavigationBoundary` records a literal search in the exact
generated C6D4D0 and C6A178 owners, reached by accepted terrain-wrapper requests.
Across 2077 source lines in 22 bounded windows, neither owner contained the
selected 932/936/940 or hexadecimal field tokens. Same-receiver generation
still requires retention across interleaved calls.

This is source navigation, not a native absence or composition theorem.
Adjusted bases, indexed/computed access, aliases, globals and callees remain
outside the negative. Re-entry requires an exact tied reader or address/call
discriminator. No additional native query or broader terrain census followed.

## Named-map pre-plane initialization search

The [edge/length boundary](../../manifests/xbox-map-tile-edge-and-length-boundary.json)
records an initialized-image zero byte at `0x8311F68F`, just before edge plane
`E=0x8311F690`. Its selected clear excludes that byte. A bounded search of the
configured program returned no modeled prior store or exact-pointer-call candidate;
it did not find an initializer or establish runtime zero retention.

The search covered only its stated raw `lis` chains, 32-word lookahead and
modeled store forms. Unknown bases, covering clears with another start, indirect
calls and other unmodeled forms remain possible. It establishes no global writer
absence or safe authored-map recipe.

The selected `E[-1] |= 1` operation preserves bit `0x2` consumed by endpoint
incidence, while it can change the whole byte. A claim that no write occurs and
a claim that the consumed bit is retained are therefore different. Neither
initialization-to-read join is established; another exact writer/caller discriminator is needed.
