# Native renderer shader constants

The
[shader-constant manifest](../../manifests/native-renderer-world-constants.json#/findings/RVA-F-0260)
records, as a static result, which frame and mesh code writes shader constants.
It does not cover a complete world pass or runtime cadence. Callback
`0x82E87D18 -> 0x82C7DF58 -> 0x82C71A00` continues through `0x82C4C740` or
`0x82C4BC00`, then `0x82C2A8E8 -> 0x82C29628 -> 0x823067F8`.

In `0x82C2A8E8`, the stack-backed VS setter `0x82C2CE4C` uses start `0` and
count `96`. The PS setter `0x82C2CFE4` uses start `0` and count `8`. At
`0x82C2A960`, the incoming r3 saved at `r1+0x16F4` supplies byte `+0x1F3DC`. A
nonzero byte enters `0x82C2A978`. A zero byte cleans up and branches
`0x82C2A974` -> `0x82C3DD0C`. This object differs from the shared `0x8314F300`
used for copies and slots. Each kind has one selected static site. Return
reachability, counts, and the cadence per frame, object, draw and pass remain
unknown.

## Stack staging and shader objects

The
[dataflow follow-up](../../manifests/native-renderer-world-constants.json#/findings/RVA-F-0264)
supports these requests after the nonzero-object guard. Two 128-call loops use
stride `16`, with callback `0x821D5678` = `blr`. The 40-instruction `0x821B0000`
report covers dispatch, counter and stride, and frame restoration. It supports no
selected block write, and the callback `blr` alone would not suffice.

| Copy | Arguments | Requested extent |
| --- | --- | --- |
| VS `0x82C2AAF0` -> `0x823066D0` | `r3=[0x8314F300]`, `r4=0`, `r5=r1+0x80`, `r6=96` | `[0x8314F300]+0x780` -> `r1+0x80..r1+0x67F`, `0x600` bytes |
| PS `0x82C2AB08` | Same pointer and `r4=0`, `r5=r1+0x900`, `r6=8` | `[0x8314F300]+0x1780` -> `r1+0x900..r1+0x97F`, `0x80` bytes |

The shared
[copy contract](../../manifests/native-renderer-shader-fetch-patch.json#/currentEvidence/shaderConstructionBoundary/metadataTransferBoundary)
limits the transfer and return for lengths of at least 16. It rests on five
premises: a readable aligned source envelope, a writable destination and stack,
disjoint physical aliases, supported execution, and stored values that stay
unchanged. These requested lengths meet its size floor. Their actual mappings,
aliases and stored bytes are not yet linked to the contract. The same contract
ties the shader metadata request at `0x8269467C` to its offset-table copy only
within the stated allocation and metadata limits. Original semantic producers and
the current shader and pass identity remain unknown.

| Object slot | Load and producer | Forwarded load; setter BL |
| --- | --- | --- |
| `r1+0x74` | `0x82C2CCD8`, `[0x8314F300]+0x3194` via `0x823067C0 -> 0x82692B08` | `0x82C2CCEC`; `0x82C2CCF4` |
| `r1+0x70` | `0x82C2CCF8`, `[0x8314F300]+0x3198` via `0x82306788 -> 0x82692E18` | `0x82C2CD0C`; `0x82C2CD14` |

Nonnull objects pass through the reference-taking call `0x82698160` before
storage, and slots release under null guards after the setters. `+0x3194` and
`+0x3198` differ from `+0x780` and `+0x1780`. Stage and shader meanings remain
unassigned.

The raw VS `0x82C2CEAC` and PS `0x82C2D044` lie in the helper span, but the
selected branches `0x82C2CE50 -> 0x82C2CEB0` and `0x82C2CFE8 -> 0x82C2D048` skip
them. Arguments, decoding and reachability remain unknown. They are candidates,
not additional writes.

## Constant ranges and setter contracts

| range | writer | frequency | meaning |
| --- | --- | --- | --- |
| VS c0..c95; source `r1+0x80..r1+0x67F` (0x600 bytes); device `+0x780..+0xD7F` (0x600 bytes); r7 `0xFFFFFF0000000000` | `0x82C2A8E8 -> 0x82692588` at `0x82C2CE4C` | Selected static site on the guarded recompiled path; execution count and runtime cadence unknown | 96 vertex vec4 float records; register slot semantics unresolved |
| PS c0..c7; source `r1+0x900..r1+0x97F` (0x80 bytes); device `+0x1780..+0x17FF` (0x80 bytes); r7 `0xC000000000000000` | `0x82C2A8E8 -> 0x82692668` at `0x82C2CFE4` | Selected static site on the guarded recompiled path; execution count and runtime cadence unknown | 8 pixel vec4 float records; register slot semantics unresolved |

| Stage | Setter | Shadow range | Dirty state | Meaning |
| --- | --- | --- | --- | --- |
| Vertex | `0x82692588` | `device +0x780 + 16*start` | Dirty offset `+0x00` | Vertex float payload; slot meaning unresolved |
| Pixel | `0x82692668` | `device +0x1780 + 16*start` | Dirty offset `+0x08` | Pixel float payload; slot meaning unresolved |
| Vertex | `0x82692788` | `device +0x2780 + 4*(start>>5)` | Dirty offset `+0x20`, mask `0x0100000000000000` | Vertex boolean payload; slot meaning unresolved |
| Pixel | `0x826927E8` | `device +0x2790 + 4*(start>>5)` | Dirty offset `+0x20`, mask `0x0100000000000000` | Pixel boolean payload; slot meaning unresolved |
| Vertex | `0x82692848` | `device +0x27A0 + 4*start` | Dirty offset `+0x20`, mask `0x0100000000000000` | Vertex packed integer payload; slot meaning unresolved |
| Pixel | `0x826928A0` | `device +0x27E0 + 4*start` | Dirty offset `+0x20`, mask `0x0100000000000000` | Pixel packed integer payload; slot meaning unresolved |

Uploader `0x82538718` has six dynamic-range arms and calls only when
`start < end`. This shows the upload shape, not which world code uses it. No
direct boolean or integer setter occurs in the selected world path. The ranges
remain open beyond the generic and record-driven families.

Generic ABI: device record `+0x80`, `r4`=`start`, `r6`=`end-start`. Counts are
elements or records, not bytes.

| Payload | VS and PS start and end | Source bases + displacement |
| --- | --- | --- |
| Float | `+0x18/+0x1C`, `+0x20/+0x24` | `+0x08/+0x10` + `16*start` |
| Boolean | `+0x68/+0x6C`, `+0x70/+0x74` | `+0x58/+0x60` + `4*start` |
| Integer | `+0x40/+0x44`, `+0x48/+0x4C` | `+0x30/+0x38` + `16*start` |

The evidence leaves these caller families unnamed:

- `0x82C25F78` and `0x82C26400` are record-driven float writers with dynamic
  source records and ranges.
- `0x8266B370` reaches all six setter families through guarded record-driven
  branches, but no accepted frame or world edge identifies its pass.
- `0x826C79D0` is classified by the D3D surface as middleware or an effect and
  shader-patch client, not the D3D runtime.
- Other raw direct callers, including `0x823029B8`, have no supported frame or
  world attribution in this result. Raw sites `0x82E36668` and `0x82E366C8` have
  no established identity for the containing function.

## Later consumers and unresolved draw order

The earlier indexed draw `0x82C2BDE4 -> 0x82C29628` shares the helper and frame
and has a loop backedge, but ordered consumption is not yet shown.

The first later traversal `0x82C2D120..0x82C2D1EC` iterates from zero up to but
excluding `16`. It reads `r1+0x1220`, calls SetTexture `0x8269AF10`, and then may
release under a null guard. D3D sets the texture through
`device+0x480+0x18*slot`, `+0x3100+4*slot` and dirty `+0x18`.
`rerevved/generated/default/rerevved_recomp.106.cpp:33361-33473` has U64
accesses at `:33432` and `:33434` and indexed reads. The index reload after the
unexpanded call prevents a claim that a derived range is absent. This is texture
setting. It is not shown to be a draw or float-shadow consumer, and the seven-arm
audit in F0267 excludes this loop.

The
[consumer follow-up](../../manifests/native-renderer-world-constants.json#/findings/RVA-F-0267)
tracks dispatch `0x82C2D270`. Selector `0` loads `0x82C2D2A0` and reaches
`0x82C2D3D4`, then:

| Selector | Target |
| --- | --- |
| `4` | `0x82C2DE18` |
| `8` | `0x82C2E85C` |
| `16` | `0x82C2F360` |
| `20` | `0x82C2FD08` |
| `24` | `0x82C306B0` |
| `36` | `0x82C31124` |

Selector `8` uses `0x82C2E5E8=0x82C2E85C`. `0x82C2E5C8=0x82C2E6FC` is the
unselected case 0. F360 and FD08 call the sampler setters `0x8268F140` and
`0x8268EF98`. The
[sampler boundary](../../manifests/native-renderer-sampler-shadow-write.json)
records each window's explicit stores: 4 bytes at `R+0x48C+0x18*i`, 4 bytes at
`R+0x490+0x18*i` (twice), and an OR into the 8-byte dirty word `R+0x18`. The
limits `i` = `0..3` and `0..7` exclude the same-base float shadows
`D+0x780..D+0xD7F` and `D+0x1780..D+0x17FF`. Computed indices, receiver and
frame aliases, save and restore, and shared-callee effects remain outside that
proof. Later continuation needs a normal return and values that stay unchanged.

The final arm calls `0x8268F3E0` (record and state updates and a byte store),
then `0x82C31538` -> increment `0x82C2D1FC`. Across seven selected windows, the
explicit `r1` accesses are four bytes wide and fall outside the complete staged
ranges, with no observed crossing. Indexed, shared-pointer and callee effects
remain unknown. Locators into the recompiled code: title `rerevved`, revision
`75df5c52ca90a5ea77690a90cf965ff8d79bac92`.

Unresolved: later consumers and ordered draws, aliases, whether bytes stay
unchanged, save and restore, full transfer and alignment, frequency, world-pass
order and safe reuse. No static evidence assigns camera, light, fog, time,
material, bone, terrain, water, shadow, unit, effect, label, menu, movie or UI
semantics to any range. The next discriminator is later sampler or state
consumption, or loop iteration under the existing guards. The link to the earlier
`0x82C2BDE4` draw stays open.

[Frame passes](native-renderer-frame-passes.md),
[anchor sites](native-renderer-anchor-sites.md) and
[D3D surface](../../manifests/native-renderer-d3d-runtime-surface.json) keep the
surrounding call and storage evidence.

## Inline shader metadata transfer

The inline shader path has a separate scalar copy contract that applies only
under conditions, including zero and small lengths. It does not inherit the
vector copy contract above. Its conditions are in the
[inline transfer boundary](../../manifests/native-renderer-dirty-up-helper-contract.json#/currentEvidence/inlineTransferBoundary),
and the shader construction path is in the
[shader fetch patch manifest](../../manifests/native-renderer-shader-fetch-patch.json#/currentEvidence/shaderConstructionBoundary).
Neither shows a complete inline replacement. For how shaders are built, see
[shader generation](native-renderer-shader-generation.md).
