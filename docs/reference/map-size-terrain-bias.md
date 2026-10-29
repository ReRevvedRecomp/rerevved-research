# Map size and terrain bias

The recovered gameplay grid initializes to 32 by 32. Different land coverage
inside that grid is a candidate; complete smaller or larger native dimensions
are not established. The [object-grid finding](../../manifests/map-dimension-object-grid-boundary.json)
owns the additional fixed32 constraint and climate boundary. The
[authored-map loader](../../manifests/map-authoring-loader-boundary.json) and
[resource placement finding](../../manifests/resource-density-generation-boundary.json)
own the reused layout and start-placement contracts.

## Dimensions and backing

Gameplay dimensions at `0x82F77364` and `0x82F77448` initialize to 32; the
selected authored-map loader reads 1024 cells. Terrain/flag storage with
stride40 and selected transfers of 1600 padded entries do not imply 1600
playable cells.

The selected object operation at `0x82D7E6B8` reaches spatial visitor
`0x821D6340` using Q=`U32[0x8314F2C0]`. The accepted visitor checks unsigned
coordinates against Q+160 and Q+164, then uses the descriptor address
`low32(U32[Q+124] + 16*low28(a + 32*b))`. If admitted, `(32,0)` and `(0,1)`
alias. A rectangle with first bound at least33 and second bound at least2
therefore contains this collision. Increasing only the second axis avoids
this particular collision, but its allocation and complete consumers remain
unbound.

The selected consumer calls each nonnull payload's current vptr+0xC with
argument1, then clears its vector word after return. The callback's effect
is unclassified; it is not proved to delete the object. Exact native words
support this local contract despite truncated decompilation.

| Request | Static assessment | Remaining gate |
|---|---|---|
| Less land inside32x32 | Candidate authored-map design | Surrounding water remains playable; no inaccessible crop/border contract |
| True smaller dimensions | Partial, with selected dimension-driven loops | Extent producers, fixed constants, generation/start termination and all consumers |
| Wider first axis above32 | Selected object index aliases adjacent-row cells | Backing and index representation changes before a supported expansion |
| Taller second axis | Avoids this particular collision | Capacity, complete consumers, generation, rendering, saves and peers |
| Larger than existing terrain backing | Unsupported by the bounded storage contract | Representation expansion across every affected plane and consumer |

## Composition and starting locations

Map composition and civilization start preference are separate mechanisms.
The selected setup reads recognized CLIMATE16 at active scenario Q+0x20
(`0x830E8FF0`) and admits signed16 values0..4. At `0x82D22A04/08` its local
dispatch stores two BE32 words at `0x82F71FD0/D4`. Their downstream readers
and map-composition meaning remain unbound. No native level names or generator
quantities are assigned from those stores.

The existing resource-placement finding's
`initialSettlerSpawnBoundary/conditionalReordering` binds an actual selected
civilization-specific terrain-score reorder at `0x82CFE908`. It chooses a
strictly-positive maximum and swaps a whole start-coordinate pair. Selected
setup mode2 bypasses it. Named terrain/civilization meanings, current mode,
score generation, candidate legality and retained ordering remain conditions.
Encoded explicit starting coordinates provide a separate location mechanism;
they do not define terrain preference.

## Selected spatial backing producer

The finding's `spatialBackingProducerBoundary` now binds a selected Q
publication/initialization route. Constructor `0x82C783C8` zeros backing
metadata Q+124/+128/+132. A later `0x82C78B60` call writes literal32 to both
bounds and1024 to Q+168, then requests1024 descriptors through `0x822F4CB8`.
The selected allocation helper requests16384 bytes and records the returned
pointer and end in the vector metadata. This is requested/recorded extent,
not delivered writable allocation or proof that constructor zeros survived
all intervening helpers.

Descriptor construction still crosses `0x821B7A40` or growth helper
`0x822F5250`; the initializer's final current virtual+0x5C is also unbound.
Its literal bounds are independent of caller dimension arguments in this
selected body. The next question is the fast-path descriptor initializer
`0x821B7A40` and its retained empty-descriptor contract. Changed dimensions,
complete generation, rendering, persistence and peer behavior remain unproved.

No game or implementation was run.
