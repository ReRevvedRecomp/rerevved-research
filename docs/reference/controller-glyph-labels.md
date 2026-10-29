# Controller glyph label inventory

The [label inventory](../../manifests/controller-glyph-label-inventory.json)
records every FrameLabel in buttonLegend sprite97 (37) and MainMenu149,
Keyboard137, HoA_KeyLegend129, CityScreen151 and UnitStack217 (45 each).
The five45-label sprites have identical label/frame sequences; exact per-movie
tag and label offsets and payload identities remain in the manifest. Frames
are1-based; exact label case is retained.

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

`blank` is the shared neutral/default label at frame 1. `XBOX` and `PS3` mark family starts: XBOX shares the A frame, while PS3 shares the PS3CIRCLE frame. They are aliases/markers, not an additional control pair. Mapping XBOX to PS3 would therefore select different control positions.

## Whole-string collision classification

A, B, X and Y have the highest obvious ordinary-text collision potential. RT, RB, LT, LB, RS, LS, L3, R3 and DUP remain short abbreviations/codes and need context. DLEFT, DRIGHT, DDOWN, DPAD, STARTBUTTON, BACKBUTTON, DHORIZONTAL and DVERTICAL are more distinctive controller identifiers and have lower spelling-based collision risk; DLEFT is not proved universally safe. blank is a common word and is not a platform mapping candidate. XBOX and PS3 are family markers. No executable-wide ordinary-text census or universal rewrite safety was established.

## SetIcon and loading D-pad boundary

hoa.FPK:buttonlegend.gfx root action tag 0x38 binds SetIcon: name Push 0x93, anonymous DefineFunction2 declaration 0x98, body [0xC2,0x10B), DefineLocal 0x10B. Flags 0x29 preload this into reg1 and arguments are theNumber/reg2, theIcon/reg3, theString/reg4. At 0xC2 the stack receives reg3 as the sole gotoAndPlay argument; 0xD2 builds buttonIcon + reg2, 0xD3 resolves that child, 0xD4 pushes gotoAndPlay and 0xD9 calls it. The later text-field assignment uses separate reg4.

Named root placements bind buttonIcon1..5 to sprite97: buttonIcon1 at 0x70CD, buttonIcon2 at 0x70ED, buttonIcon3 at 0x710D, buttonIcon5 at 0x712D, buttonIcon4 at 0x714E. The function is data-driven: the caller provides the label. It does not choose a hardcoded D-pad string.

All 41 buttonLegend action tags (43 decoded function/tag records) were checked; none pushes an exact Xbox/PS3 D-pad label. The exact hoa.FPK:gfx_loadingscreen.gfx entry 1 at index offset 0x36, payload offset 50636, size 15418, SHA-256 E32331E7A6455BA3B7ECBF431E60E650DAD740847D5E7AFE424BA940B6E7A5A8 was also checked: 13 action tags, 73 decoded records, no SetIcon token and no exact D-pad label push. Its only import tag in this parse is gfxfontlib.swf at 0x1C69.

The selected native loading-tip route uses HTML image sources rather than
buttonLegend97. `controller-glyph-family-default-boundary.json` owns the
native `XBOXVERTICAL`/`XBOXHORIZONTAL` producers and selective
0x82E81F58/r3 seam. The names differ from timeline labels
`DVERTICAL`/`DHORIZONTAL`.

Generic loading root SetBoxText at0x161D forwards to textBox.SetText at0x1631;
placement0x22E3 selects sprite68, whose SetText writes Text_txt.html=true
at0x227A and htmlText=theString at0x2288. StartGame uses0x1720/0x1734,
placement0x23C6->sprite75, and html/htmlText writes0x2372/0x2380.

| Source -> PS3 export | Generic tag1001 offsets | StartGame offsets | Declared size |
|---|---|---|---|
| XBOXVERTICAL -> PS3VERTICAL | 0x82 ->0x358 | 0x8C ->0x362 | Both64x64 |
| XBOXHORIZONTAL -> PS3HORIZONTAL | 0xC1 ->0x5BF | 0xCB ->0x5C9 | Both64x64 |

Each first resource string and matching ExportAssets name uses the exact
identifier above; the second image string appends `.dds`. The native axis
markup keeps36x36 and vspace-15. Both loading roots have two frames; neither
uses the legend's glyph timeline. The generic payload is hash-identical in
hoa/Pregame/Level; the manifest pins the selected StartGame payload separately.

The separate legend97 has240 frames: DPAD starts96, is populated96..101,
then removes the artwork and stops on102; PS3DPAD starts217, remains
populated217..224 and stops224. The other five glyph sprites have295 frames
and PS3DPAD242. Frame242 exceeds legend97's timeline. Its vector glyphs
also use different bounds/transforms, so a numeric-frame offset is not portable.

The action-string negative above remains valid; it did not cover native-built
HTML. The family manifest records supplied acceptance of the broader eight-name
builder rewrite. Per-tip attribution, selective caller-LR filtering and current
HTML resolver/cache/provider remain unobserved.


The pair table plus `blank`, `XBOX` and `PS3` accounts for every requested
label. There are no unpaired Xbox control labels. The four pairs absent in
buttonLegend are absent on both sides, rather than missing PS3 counterparts.
The inventory supplies no global constructor-rewrite safety or runtime contract.
