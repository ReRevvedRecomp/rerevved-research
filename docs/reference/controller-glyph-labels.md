# Controller glyph label inventory

The [label inventory](../../manifests/controller-glyph-label-inventory.json)
records every FrameLabel in buttonLegend sprite 97 (37) and MainMenu 149,
Keyboard 137, HoA_KeyLegend 129, CityScreen 151 and UnitStack 217 (45 each).
The five 45-label sprites have identical label and frame sequences. The manifest
keeps exact tag and label offsets and payload identities for each movie.
Frames are 1-based, and exact label case is retained.

## Xbox to PS3 pairs

The basis is control position and identifier meaning, not a recovered native pairing table. Each pair is present in all six sprites except the last four pairs, which are absent on both sides in buttonLegend.

| Xbox | PS3 | buttonLegend frames | Other five sprites frames |
|---|---|---|---|
| A | PS3X | 7 -> 129 | 7 -> 154 |
| B | PS3CIRCLE | 11 -> 105 | 11 -> 130 |
| X | PS3SQUARE | 15 -> 113 | 15 -> 138 |
| Y | PS3TRIANGLE | 19 -> 121 | 19 -> 146 |
| RT | PS3R2 | 23 -> 145 | 23 -> 170 |
| RB | PS3R1 | 28 -> 137 | 28 -> 162 |
| LT | PS3L2 | 33 -> 161 | 33 -> 186 |
| LB | PS3L1 | 38 -> 153 | 38 -> 178 |
| RS | PS3RS | 43 -> 233 | 43 -> 258 |
| LS | PS3LS | 48 -> 225 | 48 -> 250 |
| DUP | PS3DUP | 53 -> 185 | 53 -> 210 |
| DLEFT | PS3DLEFT | 59 -> 209 | 59 -> 234 |
| DRIGHT | PS3DRIGHT | 66 -> 193 | 66 -> 218 |
| DDOWN | PS3DDOWN | 73 -> 201 | 73 -> 226 |
| STARTBUTTON | PS3START | 81 -> 177 | 81 -> 202 |
| BACKBUTTON | PS3SELECT | 88 -> 169 | 88 -> 194 |
| DPAD | PS3DPAD | 96 -> 217 | 96 -> 242 |
| DHORIZONTAL | PS3DHORIZONTAL | absent on both sides | 102 -> 266 |
| DVERTICAL | PS3DVERTICAL | absent on both sides | 109 -> 273 |
| L3 | PS3L3 | absent on both sides | 117 -> 288 |
| R3 | PS3R3 | absent on both sides | 122 -> 281 |

`blank` is the shared neutral default label at frame 1. `XBOX` and `PS3` mark family starts: XBOX shares the A frame, while PS3 shares the PS3CIRCLE frame. They are aliases or markers, not an additional control pair. Mapping XBOX to PS3 would therefore select different control positions.

## Whole-string collision classification

A, B, X and Y have the highest chance of matching regular text. RT, RB, LT, LB, RS, LS, L3, R3 and DUP remain short abbreviations or codes and need context. DLEFT, DRIGHT, DDOWN, DPAD, STARTBUTTON, BACKBUTTON, DHORIZONTAL and DVERTICAL are more distinctive controller identifiers and have lower risk of a spelling match; DLEFT is not proved universally safe. blank is a common word and is not a platform mapping candidate. XBOX and PS3 are family markers. No census of regular text across the executable or universal rewrite safety was established.

## SetIcon and loading D-pad boundary

hoa.FPK:buttonlegend.gfx root action tag 0x38 defines SetIcon: name Push 0x93, anonymous DefineFunction2 declaration 0x98, body [0xC2,0x10B), DefineLocal 0x10B. Flags 0x29 preload this into reg1 and arguments are theNumber (reg2), theIcon (reg3) and theString (reg4). At 0xC2 the stack receives reg3 as the sole gotoAndPlay argument; 0xD2 builds buttonIcon + reg2, 0xD3 resolves that child, 0xD4 pushes gotoAndPlay and 0xD9 calls it. The later text-field assignment uses separate reg4.

Named root placements put sprite 97 at buttonIcon1 to buttonIcon5: buttonIcon1 at 0x70CD, buttonIcon2 at 0x70ED, buttonIcon3 at 0x710D, buttonIcon5 at 0x712D, buttonIcon4 at 0x714E. The function is data-driven: the caller provides the label. It does not choose a hardcoded D-pad string.

All 41 buttonLegend action tags (43 decoded function and tag records) were checked; none pushes an exact Xbox or PS3 D-pad label. The exact hoa.FPK:gfx_loadingscreen.gfx entry 1 at index offset 0x36, payload offset 50636, size 15418, SHA-256 E32331E7A6455BA3B7ECBF431E60E650DAD740847D5E7AFE424BA940B6E7A5A8 was also checked: 13 action tags, 73 decoded records, no SetIcon token and no exact D-pad label push. Its only import tag in this parse is gfxfontlib.swf at 0x1C69.

The selected native loading tip route uses HTML image sources rather than
buttonLegend sprite 97. `controller-glyph-family-default.json` records the
native `XBOXVERTICAL` and `XBOXHORIZONTAL` producers and the selective hook
point at `0x82E81F58`, register `r3`. The names differ from timeline labels
`DVERTICAL` and `DHORIZONTAL`.

Generic loading root SetBoxText at 0x161D forwards to textBox.SetText at 0x1631;
placement 0x22E3 selects sprite 68, whose SetText writes `Text_txt.html=true`
at 0x227A and `htmlText=theString` at 0x2288. StartGame uses 0x1720 and 0x1734,
placement 0x23C6 to sprite 75, and `html` and `htmlText` writes at 0x2372 and 0x2380.

| Source -> PS3 export | Generic tag 1001 offsets | StartGame offsets | Declared size |
|---|---|---|---|
| XBOXVERTICAL -> PS3VERTICAL | 0x82 ->0x358 | 0x8C ->0x362 | Both 64x64 |
| XBOXHORIZONTAL -> PS3HORIZONTAL | 0xC1 ->0x5BF | 0xCB ->0x5C9 | Both 64x64 |

Each first resource string and matching ExportAssets name uses the exact
identifier above; the second image string appends `.dds`. The native axis
markup keeps 36x36 and vspace -15. Both loading roots have two frames; neither
uses the legend's glyph timeline. The generic payload is hash-identical in
hoa, Pregame and Level; the manifest pins the selected StartGame payload separately.

The separate legend sprite 97 has 240 frames: DPAD starts at 96 and is populated at
frames 96 to 101, then removes the artwork and stops on frame 102. PS3DPAD starts at
frame 217, remains populated through frames 217 to 224 and stops at frame 224.
The other five glyph sprites have 295 frames and PS3DPAD at frame 242. Frame
242 exceeds the timeline of legend sprite 97. Its vector glyphs
also use different bounds and transforms, so a numeric-frame offset is not portable.

The action-string negative above remains valid; it did not cover native-built
HTML. The family manifest records supplied acceptance of the broader eight-name
builder rewrite. Per-tip attribution, selective caller-LR filtering and current
HTML resolver, cache and provider remain unobserved.


The pair table, together with `blank`, `XBOX` and `PS3`, accounts for every
requested label. No Xbox control label lacks a PS3 counterpart. The four pairs
that are absent in buttonLegend are absent on both sides. The inventory shows
no global safety for constructor rewrites and no runtime behavior.

`DoInitAction` tag 59 action streams start after a two byte sprite ID. The
loading movie has four such tags: 0x233E (sprite 69), 0x25C8 (sprite 70),
0x2A09 (sprite 71) and 0x38FC (sprite 72), with 3, 5, 29 and 4 functions. The
full loading count is 13 top-level action records plus 60 functions, 73 in all.
buttonLegend has no tag 59, so its 41 action tags and 43 records are not
affected by that rule.

How the native code uses these labels is covered on
[the controller prompt page](controller-glyphs.md): the
[HTMLIMG descriptor and append path](controller-glyphs.md#htmlimg-descriptor-and-final-text-callback)
and the [Unit panel writers](controller-glyphs.md#unit-panel-update-call).
