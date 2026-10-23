# Native renderer shader constants

The
[shader-constant manifest](../../manifests/native-renderer-world-constants.json#/findings/RVA-F-0260)
bounds static frame/mesh ownership, not a complete world pass or runtime
cadence. Callback `0x82E87D18 -> 0x82C7DF58 -> 0x82C71A00` continues via
`0x82C4C740` or `0x82C4BC00`, then `0x82C2A8E8 -> 0x82C29628 -> 0x823067F8`.

In `0x82C2A8E8`, stack-backed VS setter `0x82C2CE4C` uses start `0`, count `96`;
PS `0x82C2CFE4` uses `0`/`8`. At `0x82C2A960`, incoming r3 saved at `r1+0x16F4`
supplies byte `+0x1F3DC`: nonzero enters `0x82C2A978`; zero cleans up and
branches `0x82C2A974` -> `0x82C3DD0C`. This object differs from shared
`0x8314F300` used for copies/slots. Each kind has one selected static site;
return reachability, counts and frame/object/draw/pass cadence remain unknown.

## Stack staging and shader objects

The
[dataflow follow-up](../../manifests/native-renderer-world-constants.json#/findings/RVA-F-0264)
supports these requests after the nonzero-object guard. Two 128-call loops use
stride `16`, callback `0x821D5678` = `blr`. The 40-instruction `0x821B0000`
report covers dispatch, counter/stride and frame restoration, supporting no
selected block write; callback BLR alone would not suffice.

| Copy | Arguments | Requested extent |
| --- | --- | --- |
| VS `0x82C2AAF0` -> `0x823066D0` | `r3=[0x8314F300]`, `r4=0`, `r5=r1+0x80`, `r6=96` | `[0x8314F300]+0x780` -> `r1+0x80..r1+0x67F`, `0x600` bytes |
| PS `0x82C2AB08` | Same pointer/`r4=0`, `r5=r1+0x900`, `r6=8` | `[0x8314F300]+0x1780` -> `r1+0x900..r1+0x97F`, `0x80` bytes |

Copy has byte/word/vector arms; unknown alignment and unexpanded
`0x827F89D8`/`0x82825410` qualify full transfer/return. Original semantic
producers remain unknown.

| Object slot | Load and producer | Forwarded load; bind BL |
| --- | --- | --- |
| `r1+0x74` | `0x82C2CCD8`, `[0x8314F300]+0x3194` via `0x823067C0 -> 0x82692B08` | `0x82C2CCEC`; `0x82C2CCF4` |
| `r1+0x70` | `0x82C2CCF8`, `[0x8314F300]+0x3198` via `0x82306788 -> 0x82692E18` | `0x82C2CD0C`; `0x82C2CD14` |

Nonnull objects pass retain `0x82698160` before storage; slots release under
null guards after setters. `+0x3194/+0x3198` differ from `+0x780/+0x1780`;
stage/shader meanings remain unassigned.

Raw VS `0x82C2CEAC`/PS `0x82C2D044` lie in the helper span, but selected
branches `0x82C2CE50 -> 0x82C2CEB0`/`0x82C2CFE8 -> 0x82C2D048` skip them.
Arguments, decoding and reachability remain unknown: candidates, not additional
writes.

## Constant ranges and setter contracts

| range | writer | frequency | meaning |
| --- | --- | --- | --- |
| VS c0..c95; source `r1+0x80..r1+0x67F` (0x600 bytes); device `+0x780..+0xD7F` (0x600 bytes); r7 `0xFFFFFF0000000000` | `0x82C2A8E8 -> 0x82692588` at `0x82C2CE4C` | Selected static site on the guarded generated path; execution count and runtime cadence unknown | 96 vertex vec4 float records; register slot semantics unresolved |
| PS c0..c7; source `r1+0x900..r1+0x97F` (0x80 bytes); device `+0x1780..+0x17FF` (0x80 bytes); r7 `0xC000000000000000` | `0x82C2A8E8 -> 0x82692668` at `0x82C2CFE4` | Selected static site on the guarded generated path; execution count and runtime cadence unknown | 8 pixel vec4 float records; register slot semantics unresolved |

| Stage | Setter | Shadow range | Dirty state | Meaning |
| --- | --- | --- | --- | --- |
| Vertex | `0x82692588` | `device +0x780 + 16*start` | Dirty offset `+0x00` | Vertex float payload; slot meaning unresolved |
| Pixel | `0x82692668` | `device +0x1780 + 16*start` | Dirty offset `+0x08` | Pixel float payload; slot meaning unresolved |
| Vertex | `0x82692788` | `device +0x2780 + 4*(start>>5)` | Dirty offset `+0x20`, bit 56 | Vertex boolean payload; slot meaning unresolved |
| Pixel | `0x826927E8` | `device +0x2790 + 4*(start>>5)` | Dirty offset `+0x20`, bit 56 | Pixel boolean payload; slot meaning unresolved |
| Vertex | `0x82692848` | `device +0x27A0 + 4*start` | Dirty offset `+0x20`, bit 56 | Vertex packed integer payload; slot meaning unresolved |
| Pixel | `0x826928A0` | `device +0x27E0 + 4*start` | Dirty offset `+0x20`, bit 56 | Pixel packed integer payload; slot meaning unresolved |

Uploader `0x82538718` has six dynamic-range arms, calling only when
`start < end`; this proves upload shape, not world ownership. No direct
boolean/integer setter occurs in the selected world path; ranges remain open
beyond generic/record-driven families.

Generic ABI: device record `+0x80`, `r4`=`start`, `r6`=`end-start`; counts are
elements/records, not bytes.

| Payload | VS/PS start-end | Source bases + displacement |
| --- | --- | --- |
| Float | `+0x18/+0x1C`, `+0x20/+0x24` | `+0x08/+0x10` + `16*start` |
| Boolean | `+0x68/+0x6C`, `+0x70/+0x74` | `+0x58/+0x60` + `4*start` |
| Integer | `+0x40/+0x44`, `+0x48/+0x4C` | `+0x30/+0x38` + `16*start` |

The bounded evidence leaves these caller families unnamed:

- `0x82C25F78` and `0x82C26400` are record-driven float writers with dynamic
  source records and ranges.
- `0x8266B370` reaches all six setter families through guarded record-driven
  branches, but no accepted frame/world edge identifies its pass.
- `0x826C79D0` is classified by the D3D surface as middleware or an effect and
  shader-patch client, not the D3D runtime.
- Other raw direct callers, including `0x823029B8`, have no supported
  frame/world attribution in this bounded packet. Raw sites `0x82E36668` and
  `0x82E366C8` have no established identity for the containing function.

## Later consumers and unresolved draw order

Earlier indexed draw `0x82C2BDE4 -> 0x82C29628` shares the helper/frame and has
a loop backedge, but ordered consumption remains unproved.

First later traversal `0x82C2D120..0x82C2D1EC` iterates zero..<`16`, reading
`r1+0x1220`, calling SetTexture `0x8269AF10`, then possibly null-guarded
release. D3D binding uses `device+0x480+0x18*slot`, `+0x3100+4*slot`, dirty
`+0x18`. `rerevved/generated/default/rerevved_recomp.106.cpp:33361-33473` has
U64 accesses at `:33432`/`:33434` and indexed reads. Index reload after the
unexpanded call prevents a derived-range absence claim. This is binding, not a
proved draw/float-shadow consumer; F0267's seven-arm audit excludes this loop.

[Consumer follow-up](../../manifests/native-renderer-world-constants.json#/findings/RVA-F-0267)
tracks dispatch `0x82C2D270`: selector `0` loads `0x82C2D2A0` and reaches
`0x82C2D3D4`, then:

| Selector | Target |
| --- | --- |
| `4` | `0x82C2DE18` |
| `8` | `0x82C2E85C` |
| `16` | `0x82C2F360` |
| `20` | `0x82C2FD08` |
| `24` | `0x82C306B0` |
| `36` | `0x82C31124` |

`8` uses `0x82C2E5E8=0x82C2E85C`; `0x82C2E5C8=0x82C2E6FC` is unselected case-0.
F360/FD08 call sampler setters `0x8268F140`/`0x8268EF98`. The
[sampler boundary](../../manifests/native-renderer-sampler-shadow-write-boundary.json)
records each window's explicit stores: 4 bytes `R+0x48C+0x18*i`, 4 bytes
`R+0x490+0x18*i` (twice), OR 8-byte dirty `R+0x18`. Bounds `i` = `0..3`/`0..7`
exclude same-base float shadows `D+0x780..D+0xD7F`/`D+0x1780..D+0x17FF`.
Computed indices, receiver/frame aliases, save/restore and shared-callee effects
remain outside that proof; later continuation requires return/retention.

Final arm calls `0x8268F3E0` (record/state updates and byte store), then
`0x82C31538` -> increment `0x82C2D1FC`. Across seven selected windows, explicit
`r1` accesses are four-byte, outside complete staged ranges with no observed
crossing. Indexed/shared-pointer/callee effects remain unknown. Generated
locators: title `rerevved`, revision `75df5c52ca90a5ea77690a90cf965ff8d79bac92`.

Unresolved: later consumers/ordered draws, aliases, byte retention,
save/restore, full transfer/alignment, frequency, world-pass order and safe
reuse. No static evidence assigns
camera/light/fog/time/material/bone/terrain/water/shadow/unit/effect/label/menu/movie/UI
semantics to any range. Next discriminator is later sampler/state consumption or
loop iteration under existing guards; earlier `0x82C2BDE4` draw join stays open.

[Frame passes](native-renderer-frame-passes.md),
[anchor sites](native-renderer-anchor-sites.md) and
[D3D surface](../../manifests/native-renderer-d3d-runtime-surface.json) retain
surrounding call/storage evidence.
