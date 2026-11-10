# Map size and terrain bias

The recovered gameplay grid starts at 32 by 32 cells. Changing how much land
sits inside that grid is a possible approach. Full support for smaller or
larger native dimensions is not established. The
[object-grid finding](../../../manifests/map-dimension-object-grid.json)
covers the extra fixed 32 constraint and the climate boundary. The
[authored-map loader](../../../manifests/map-authoring-loader.json) and the
[resource placement finding](../../../manifests/resource-density-generation.json)
cover the reused layout and the start-placement contracts.

## Dimensions and backing

The gameplay dimensions at `0x82F77364` and `0x82F77448` start at 32. The
selected authored-map loader reads 1024 cells. Terrain and flag storage uses a
stride of 40, and selected transfers copy 1600 padded entries. Neither fact
shows that 1600 cells are playable.

The selected object operation at `0x82D7E6B8` reaches the spatial visitor
`0x821D6340` using Q=`U32[0x8314F2C0]`. The accepted visitor checks unsigned
coordinates against Q+160 and Q+164. It then uses the descriptor address
`low32(U32[Q+124] + 16*low28(a + 32*b))`. If the visitor accepts the call,
the cells `(32,0)` and `(0,1)` alias. A rectangle whose first bound is at
least 33 and whose second bound is at least 2 therefore contains this
collision. Increasing only the second axis avoids this particular collision.
Its allocation and its complete set of consumers are not yet tied to the
dimensions.

The selected consumer calls each nonnull payload's current vptr+0xC with
argument 1, then clears its vector word after the call returns. The callback's
effect is unclassified, and it is not shown to delete the object. The exact
native words support this local contract even though the decompilation is
truncated.

| Request | Static assessment | Remaining work |
|---|---|---|
| Less land inside 32x32 | Candidate authored-map design | Surrounding water stays playable; no contract hides a cropped border |
| True smaller dimensions | Partial; selected loops are driven by the dimensions | Extent producers, fixed constants, where generation and start placement end, and all consumers |
| Wider first axis above 32 | The selected object index aliases cells in adjacent rows | Backing and index representation must change before expansion is supported |
| Taller second axis | Avoids this particular collision | Capacity, all consumers, generation, rendering, saves and peers |
| Larger than the existing terrain backing | Unsupported by the limited storage contract | Representation expansion across every affected plane and consumer |
| Terrain or landmass composition bias | Authored content and the local `CLIMATE` dispatch are leads | A reader that connects the two setup words to a composition quantity |
| Civilization starting-terrain bias | A selected native score reorder exists | Score meaning, valid candidates, mode and order, fairness and spacing, deterministic application |

## Composition and starting locations

Map composition and civilization start preference are separate mechanisms.
The selected setup reads the recognized `CLIMATE` value (16 bits) at active
scenario Q+0x20 (`0x830E8FF0`) and accepts signed 16-bit values 0 to 4. At
`0x82D22A04` and `0x82D22A08` its local dispatch stores two big-endian 32-bit
words at `0x82F71FD0` and `0x82F71FD4`. The selected reader below ties these
words to a city-distance AI filter. Their meaning for map composition is not
established. No native level names or generator quantities are assigned to
those stores.

The resource-placement finding
`initialSettlerSpawnBoundary/conditionalReordering` shows an actual selected
terrain-score reorder that depends on the civilization, at `0x82CFE908`. It
picks the maximum score, which must be strictly positive, and swaps a whole
start-coordinate pair. Selected setup mode 2 skips it. The reorder itself is
established in the recovered code. What is still needed is the knowledge to
assign terrain meanings to the scores and to change the reorder safely. That
means the named terrain and civilization meanings, the current mode, how scores
are generated, and which candidates are legal. Whether the ordering stays
unchanged afterward is also open.
Encoded explicit starting coordinates are a separate way to choose locations.
They do not set terrain preference.

## Selected spatial backing producer

The finding's `spatialBackingProducerBoundary` shows a selected route that
publishes and initializes Q. Constructor `0x82C783C8` zeros the backing
metadata at Q+124, Q+128 and Q+132. A later call to `0x82C78B60` writes the
literal 32 to both bounds and 1024 to Q+168. It then requests 1024
descriptors through `0x822F4CB8`. The selected allocation helper requests
16,384 bytes and records the returned pointer and end in the vector metadata.
This records the requested extent. It does not show that writable memory was
delivered, or that the constructor's zeros survive every helper in between.

Descriptor construction still passes through `0x821B7A40` or the growth helper
`0x822F5250`. The actual current+0x5C mapping and whether construction
completes are not yet established. The installed candidate and cold-cache
contracts below hold only under their stated conditions. In the selected body,
the literal bounds do not depend on the caller's dimension arguments. The
`descriptorInitializationBoundary` section below covers the fast-path
initializer `0x821B7A40`. The next question there is whether the current tail
effect leaves the descriptors unchanged. Changed dimensions, complete
generation, rendering, persistence and peer behavior are not yet shown.

## Empty descriptor construction

The finding's `descriptorInitializationBoundary` covers `0x821B7A40`. When the
source begin is 0, it takes a finite path of 28 instructions with no child
call. That path zeros destination+4, +8 and +12 and returns the original
destination. It neither writes nor reads the first four bytes. So it zeros
twelve metadata bytes and does not zero the whole 16-byte descriptor.

The caller's source words at SP+84, SP+88 and SP+92 are zero only when r28
stays 0 and the frame is unchanged. Suppose the backing is large enough and
the fast-path iterations finish. Then the 1024 descriptors for the fixed grid
have equal empty begin and end words, and they reach the accepted visitor's
empty return. The current tail virtual+0x5C can still change them. Three
things are not yet established: the actual current mapping, whether cold
construction completes, and whether the descriptors stay unchanged until the
visitor is entered. Growth, allocator delivery and complete generation are
separate questions.

## Selected construction-tail candidate

`tailTargetRetentionBoundary` ties installed table 0x82120EB0+0x5C, cell
0x82120F0C, to 0x82E10450. The current receiver 0x8314F28C starts at zero. The
reused publisher's later current+0x0C call at 0x82E2E504 still decides
whether the target stays valid. No current target and no publication-before-tail
order follows from this.

With a nonzero cache X at 0x8314EF84, the candidate returns U32[X+12] in a
16-instruction arm with no children or loops. It writes only 24 stack bytes.
Suppose the stack, control flow and map memory do not alias, as the finding
requires. Then it restores the full 64-bit r30 and r31 values. It also keeps
the protected bounds, the vector and the 2048 descriptor words unchanged up to
the caller's Q+178=1 store at 0x82C78D54. Two questions stay open: whether the
caller completes, and whether the state stays unchanged until the visitor
0x821D6340. The initial X is zero. The uncached path's allocator call
0x82E10484 and its later child are therefore separate completion questions.

## Cold-cache construction

`coldCacheConstructionBoundary` covers the zero-cache arm of 0x82E10450.
Suppose the 16-byte allocation is nonzero and the child completes with its
state kept. Then the arm samples V=U32[P+12] at 0x82E104B0 and publishes
wrapper P at 0x82E104B4 to cache 0x8314EF84. It returns V, and the cache
contains P. The null arm reads guest address 0 before storing cache 0. It
therefore does not show that returning zero is safe.

Child 0x82E70D28 constructs separate 864-byte and 336-byte objects only when
its conditions hold. Its selected +12 replacement at 0x82E70E64 re-reads P+8
after any old object is released. Nested allocation and constructors, current
virtual effects, completion of the atomic loop, and the survival of aliases
and fields are all open. Requested extents alone show no storage delivery.
The current service, table and cache, the caller's restore, and the order
between caller and visitor are also open. No map-size feasibility follows.

`firstObjectConstructionPrefixBoundary` narrows the constructor request for
the first 864-byte object. It follows two direct prefixes and the original
save thunk, and it reaches the unopened function `0x82358A88` with the full
incoming object argument. Its 24 selected words make 13 stack stores covering
80 distinct bytes before that request. The stack storage must be disjoint so
that the wrapper, object, map and backing fields survive. A normal helper
return alone does not establish that the protected fields stay unchanged. Whether the constructor returns, the
object is delivered, and the later cache and mapping behave as needed is open.

## Exact `CLIMATE` reader and AI candidate check

`climateReaderBoundary` covers the reads at 0x82CB53A0 and 0x82CB53BC of the
two setup words inside the selected AI evaluator. The local code forms the
absolute distance between the signed city-record field at +50 and half the
signed dimension at 0x82F77448. It then classifies that distance with the
current setup thresholds into bands 3, 4 and 5. When the evaluator's checks on
the player and the candidate pass, a candidate in the wrong band skips to
0x82CB548C. This is an AI filter that applies only under those checks. The
finding does not show the final choice or the delivered production.

The selected reader writes no terrain cells or dimensions. Its relevance to
the generator and to terrain composition is not established.

## `CLIMATE` terrain receiver fields

`climateTerrainInputRetentionBoundary` reuses the accepted terrain handoff to
0x82C6E898. Under its conditions, it stores T0 at receiver+936 at 0x82C6E9B8,
T1 at +932 at 0x82C6E9BC, and trunc(s32(T0)/2) at +940 at 0x82C6E9F0. These
stores assume that the required helpers return and that the same receiver
stays in use.

Its immediate helper 0x82C6C860 walks fifteen 24-byte records starting at
+544. Its direct relative accesses reach +892, so they do not touch these
climate fields. That negative result does not cover opaque calls and aliases.
Before assigning any effect on composition, biome, land area or dimensions, a
code path that reads +932, +936 or +940 must be found. The fixed 32-by-32
dimensions, the stride of 40 and the prebuilt terrain are separate questions.

## Terrain reader search

`climateFieldReaderNavigationBoundary` records a literal text search of the
exact generated functions C6D4D0 and C6A178, which accepted terrain-wrapper
requests reach. The search read 2077 source lines in 22 windows. Neither
function contained the selected 932, 936 or 940 tokens, or their hexadecimal
forms. A generation run that uses the same receiver would still have to show
that the receiver stays valid across interleaved calls.

This source search does not show that no native reader exists, and it does not
show how terrain is composed. It does not cover adjusted bases, indexed or
computed access, aliases, globals or callees. Reopening the question needs an
exact reader tied to the receiver, or an address or call that tells the
candidates apart. No further native query or broader terrain census was made.

## Named-map pre-plane initialization search

The [edge and length finding](../../../manifests/xbox-map-tile-edge-and-length.json)
records a zero byte in the initialized image at `0x8311F68F`, just before the
edge plane `E=0x8311F690`. The selected clear leaves that byte out. A limited
search of the configured program found no modeled earlier store and no call
through the exact pointer. It found no initializer. It does not show that the
zero survives at run time.

The search covered only its stated raw `lis` chains, a 32-word lookahead and
the modeled store forms. Unknown bases, covering clears that start elsewhere,
indirect calls and other unmodeled forms remain possible. The search does not
show that no global writer exists, and it does not give a safe recipe for an
authored map.

The selected operation `E[-1] |= 1` leaves bit `0x2` alone, and endpoint
incidence reads that bit. The operation can still change other bits of the
byte. "No write occurs" and "the consumed bit stays unchanged" are therefore
different claims. Neither claim is established for the path from
initialization to the read. Another exact writer or a call that tells the
candidates apart is needed.
