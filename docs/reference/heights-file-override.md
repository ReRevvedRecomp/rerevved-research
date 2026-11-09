# Heights file and the override hook

Every numbered or named map has a heights file. It is a DDS image that sets how
high the 3D terrain rises across the map. The tile map file says what each tile
is (see [map tile semantics](../../manifests/xbox-map-tile-semantics.json)), and
the heights file says how the land is shaped. A mod that wants flatter hills, a
steeper mountain range or a custom named map shape needs to replace these bytes.

The hook below is a static candidate, not a tested mod. Its runtime operation
has not been observed.

Worked example. A mod wants a flatter version of one numbered map. The game
asks the file loader for the heights name of map 12. The name is built from
three retail format strings: the numbered map format at `0x821642E0`, the named
map format at `0x821642E8` (used when a named map is active) and the heights
format at `0x821642F0`, which adds the heights suffix. Their text is in the
[map authoring loader](../../manifests/map-authoring-loader.json) manifest. The
loader returns a buffer holding the whole DDS file. The mod hooks the return, checks that the request is the height request, checks the
file name, and copies its own 524416 byte DDS over the buffer. The game then
builds the terrain from the mod's file and never sees the original.

## What the heights file is

The retail files all share one layout. A census of the 277 numbered maps found
the same header and length in every heights file:

| Property | Value |
|---|---|
| Size | 512 by 512 samples |
| Pixel format | 16 bits, red mask `0xFFFF`, no other masks, descriptor word `0x28000058` after clearing layout bit `0x100` |
| Header | Classic DDS, little endian words, flags `0x1007`, mip count 0, pitch and depth 0 |
| Payload | One level of tight rows, 1024 bytes per row, 524288 bytes, starting at file offset 128 |
| Total | 524416 bytes |
| Samples | Unsigned 16 bit, little endian in the file |

The sample order was read from the data. Adjacent samples differ about 42 times
less when read as little endian than as big endian, in two checks of 20 maps
each. The terrain reader takes unsigned big endian 16 bit values, and the code
between the file and that reader that turns one into the other has not been
found. Mirroring the retail layout is therefore the only recommended recipe, and
no complete authoring recipe is accepted. See
[`xbox-heights-authoring-contract.json`](../../manifests/xbox-heights-authoring-contract.json)
(`RVA-F-0376`), section `retailObservedProfile`.

Height numbers turn into terrain height through a scale. The key `TerrainZScale`
is a 13 byte string at `0x8216433C`, requested at `0x82C6E950`. A retail global
configuration declares one value of 2.3 for it. That is a candidate source only:
the value the game actually reads, and the physical unit, are not shown. The
terrain code computes `f32(f32(f32(n) * Z) * (255 / 65536))` for a sample `n`
from 0 to 65535 and scale `Z`.

## Size rules a custom file must meet

- The terrain code keeps the ratio of heights width to terrain width in
  `terrain+0x7C` and of height to terrain height in `terrain+0x80`. On the arm
  reached, `0x82C6EC1C..0x82C6EC84` takes one eighth of the first ratio and
  stops when it is zero. If the terrain width `T` is 32, the file width must be
  at least 256.
- After loading, the code derives a sample step from the locked pitch `P` and
  width `W` at `0x822F99A0`. It then allocates `step * V * W` bytes and copies
  `V` rows of `P` bytes. Samples packed two bytes apart with matching storage
  need `P == 2 * W`. Under the nominal pitch of `256 * ceil(W / 128)`, that
  holds only for widths that are multiples of 128. Square images of 86 by 86 and
  171 by 171 give a step of 2 but overrun the allocation, by 7224 and 29070
  bytes.
- Default output sizing rounds dimensions up to powers of two, so a width of 33
  would ask for 64, not be rejected. Unequal regions miss the direct copy path,
  and the result of resampling is not known.
- Neither 32 nor 33 is established as the required width. A 32 by 32 tile map
  does not mean a 32 by 32 heights image. The retail 512 by 512 file meets all
  the rules above.

## How the override works

All numbered and named base formats reach the height request at `0x822F9888`.
That function has no cache check or early exit before calling the file wrapper
`0x822D64C0` at `0x822F98B8`, except for a null or empty name. The wrapper calls
the common file loader `0x82E806E0` at `0x822D6504`. The loader returns either a
direct open result or a stream result, and in both cases it requests `L + 4`
bytes where `L` is the file length. The first four bytes hold `L` as a big
endian 32 bit value, and the DDS file follows. The wrapper adds four to the
returned base before it hands the pointer on.

Bare names are looked up in this order: direct loose file, then registered
sources, then the common fallback. See
[content source resolution](content-source-resolution.md). That order does not
apply to a named selector that contains path separators.

The wrapper is shared. It has seven known direct callers, and only the height
request returns to `0x822F98BC`. A hook must tell the height request apart from
the others.

## Recommended hook

The candidate is at `0x822D6508`, the instruction `stw r3,0(r31)`. It runs just
after the call at `0x822D6504` returns, and every source arm reaches it before
the height parser.

| Register | Holds |
|---|---|
| `r1` | `T`, the wrapper's stack pointer |
| `r30` | The original NUL terminated filename pointer |
| `r3` | `A`, the allocation base. Zero means the load failed |
| `r31` | `C`, the cell that receives the result pointer |

For a nonzero `A`, `L` is the big endian 32 bit word at `A`. `P = A + 4` points
at the complete DDS file, and sample data starts at `P + 128`.

The hook has two filters:

1. The saved return address at `T + 0x68` equals `0x822F98BC`. The wrapper
   saves its return address at the old stack pointer minus 8 and allocates a
   `0x70` byte frame. For the height request, `C` is `T + 0x104`. This address
   is unique among the seven direct callers. Indirect callers are not known.
2. The filename at `r30` matches the intended map. The exact prefix, path and
   case of the name the height caller builds with `sub_827F2830` are not fixed
   here. Capture the string at run time first. Do not match on the role name
   alone, assume case folding, match only a suffix or treat the caller as a
   unique map.

If `A` is zero, leave the failure path alone.

To replace the file, copy the complete DDS to `A + 4` and resume the original
store. Keep `r3` as `A`, keep the length prefix, and keep the frame and saved
link intact. The replacement must be exactly `L` bytes, and the range from
`A + 4` for `L` bytes must be valid and writable. The retail size is 524416
bytes, so use it only after checking the donor file and the live prefix. An
equal size copy keeps the allocation and satisfies the only size user seen in
the creation handoff, which is the size argument `r5` at `0x822F991C` read from
the big endian word at `P - 4`.

Do not pass `P` where the hook expects `A`. The nonnull arm stores `P` to `C`
afterwards, at `0x822D6514` and `0x822D6518`.

## Replacing the pointer instead

A mod can swap `r3` for its own allocation `A_new`, with valid backing for
`4 + L_new` bytes, the big endian length `L_new` at `A_new`, and a complete DDS
at `A_new + 4`. This is not recommended. The height caller asks for release of
the buffer through `sub_82D3D9F0` on failure (call `0x822F9954`, return
`0x822F9958`) and on success (call `0x822F9A58`, return `0x822F9A5C`), so the
swapped buffer must be compatible with that release. The displaced `A` also
needs its own release. A never freed pointer such as the one the logo hook uses
at `0x82E87B90` is not a safe pattern here. A pointer without the length prefix
breaks the layout.

## Limits and open questions

- Allocator rounding, whether the read helpers finish reading, and whether the
  range is writable are assumed, not shown.
- What the release paths `sub_827F5780` and `sub_82D2E960` free, and whether
  they can free a substituted buffer, is unknown.
- The three direct height callers are `sub_82C6E188`, `sub_82C6E368` and
  `sub_82C6E4D8`. Any cache bypass at that call must happen inside one of them,
  and their behavior is not known. The cache of the blend and lightmap route
  does not apply to the heights route.
- Parser steps past the creation handoff may check sizes that were not read.
- The conversion of little endian file samples into the big endian CPU values,
  the dimension and world links, the live `TerrainZScale` value and unit, and
  runtime acceptance of a custom file are all open.
- The hook has not run. Register layout, filename identity and writable backing
  are static results only.

Addresses, caller lists and qualifications are in
[`xbox-heights-file-override.json`](../../manifests/xbox-heights-file-override.json)
(`RVA-F-0377`) and the authoring facts are in
[`xbox-heights-authoring-contract.json`](../../manifests/xbox-heights-authoring-contract.json)
(`RVA-F-0376`).
