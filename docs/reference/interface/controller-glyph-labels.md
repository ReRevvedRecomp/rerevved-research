# Controller glyph label inventory

The [label inventory](../../../manifests/controller-glyph-label-inventory.json)
records every frame label in the button legend sprite 97 (37 labels) and in the
sprites of five other movies: the main menu 149, the keyboard 137, the key
legend 129, the city screen 151 and the unit stack 217 (45 labels each). The
five 45-label sprites have identical label and frame sequences. The manifest
keeps exact tag and label offsets and payload identities for each movie, and it
holds the exact label text for every row below. Frames are 1-based, and exact
label case is kept.

## Xbox to PS3 pairs

The basis is control position and identifier meaning, not a recovered native pairing table. Each pair is present in all six sprites except the last four pairs, which are absent on both sides in the button legend.

| Xbox control | PS3 control | Button legend frames | Other five sprites frames |
|---|---|---|---|
| A button | Cross | 7 -> 129 | 7 -> 154 |
| B button | Circle | 11 -> 105 | 11 -> 130 |
| X button | Square | 15 -> 113 | 15 -> 138 |
| Y button | Triangle | 19 -> 121 | 19 -> 146 |
| Right trigger | R2 | 23 -> 145 | 23 -> 170 |
| Right bumper | R1 | 28 -> 137 | 28 -> 162 |
| Left trigger | L2 | 33 -> 161 | 33 -> 186 |
| Left bumper | L1 | 38 -> 153 | 38 -> 178 |
| Right stick | Right stick | 43 -> 233 | 43 -> 258 |
| Left stick | Left stick | 48 -> 225 | 48 -> 250 |
| D-pad up | D-pad up | 53 -> 185 | 53 -> 210 |
| D-pad left | D-pad left | 59 -> 209 | 59 -> 234 |
| D-pad right | D-pad right | 66 -> 193 | 66 -> 218 |
| D-pad down | D-pad down | 73 -> 201 | 73 -> 226 |
| Start button | Start | 81 -> 177 | 81 -> 202 |
| Back button | Select | 88 -> 169 | 88 -> 194 |
| Whole D-pad | Whole D-pad | 96 -> 217 | 96 -> 242 |
| D-pad horizontal pair | D-pad horizontal pair | absent on both sides | 102 -> 266 |
| D-pad vertical pair | D-pad vertical pair | absent on both sides | 109 -> 273 |
| Left stick click (L3) | Left stick click (L3) | absent on both sides | 117 -> 288 |
| Right stick click (R3) | Right stick click (R3) | absent on both sides | 122 -> 281 |

A neutral blank label is the shared default at frame 1. Two more labels mark the start of the Xbox family and of the PS3 family. The Xbox marker shares the A button frame, while the PS3 marker shares the PS3 circle frame. They are aliases or markers, not an additional control pair. Mapping the Xbox marker to the PS3 marker would therefore select different control positions.

## Whole-string collision classification

The single-letter labels for the A, B, X and Y buttons have the highest chance of matching regular text. The labels for the triggers, bumpers, sticks, stick clicks and D-pad up remain short abbreviations or codes and need context. The labels for D-pad left, right and down, the whole D-pad, Start, Back, and the horizontal and vertical D-pad pairs are more distinctive controller identifiers and have lower risk of a spelling match. The D-pad left label is not shown to be universally safe. The blank label is a common word and is not a platform mapping candidate. The two family markers are not control labels. No census of regular text across the executable and no universal rewrite safety were established.

## Icon-setting function and loading D-pad boundary

Root action tag `0x38` of the button legend movie defines the icon-setting function. The button legend movie is an entry in the HoA archive. The name push is at `0x93`, the anonymous `DefineFunction2` declaration at `0x98`, the body at `[0xC2,0x10B)`, and the `DefineLocal` at `0x10B`. Flags `0x29` preload this into reg1. The function takes three arguments: the icon number (reg2), the icon label (reg3) and the text string (reg4). At `0xC2` the stack receives reg3 as the sole `gotoAndPlay` argument. `0xD2` builds the child name from the icon prefix plus reg2, `0xD3` resolves that child, `0xD4` pushes `gotoAndPlay` and `0xD9` calls it. The later text-field assignment uses the separate reg4.

Five named root placements put sprite 97 in the numbered icon children 1 to 5. Child 1 is at `0x70CD`, child 2 at `0x70ED`, child 3 at `0x710D`, child 5 at `0x712D` and child 4 at `0x714E`. The function is data-driven: the caller provides the label. It does not choose a hardcoded D-pad label.

All 41 action tags of the button legend movie (43 decoded function and tag records) were checked. None pushes an exact Xbox or PS3 D-pad label. The loading screen movie, entry 1 in the HoA archive at index offset `0x36`, payload offset 50636, size 15418, SHA-256 E32331E7A6455BA3B7ECBF431E60E650DAD740847D5E7AFE424BA940B6E7A5A8, was also checked. It has 13 action tags and 73 decoded records, no token for the icon-setting function and no exact D-pad label push. Its only import tag in this parse is for the font library movie, at `0x1C69`.

The selected native loading tip route uses HTML image sources rather than
legend sprite 97. The manifest `controller-glyph-family-default.json` records the
native producers for the Xbox vertical and horizontal D-pad image names and the
selective hook point at `0x82E81F58`, register `r3`. Those names differ from the
timeline labels for the vertical and horizontal D-pad pairs.

In the generic loading movie, the root text-box setter at `0x161D` forwards to
the text field's `SetText` at `0x1631`. Placement `0x22E3` selects sprite 68,
whose `SetText` sets the field's HTML flag to true at `0x227A` and assigns
`htmlText` from its string argument at `0x2288`. The start-game variant uses
`0x1720` and `0x1734`, placement `0x23C6` to sprite 75, and writes the HTML flag
and `htmlText` at `0x2372` and `0x2380`.

| Source -> PS3 image | Generic tag 1001 offsets | Start-game offsets | Declared size |
|---|---|---|---|
| Xbox vertical D-pad -> PS3 vertical D-pad | 0x82 ->0x358 | 0x8C ->0x362 | Both 64x64 |
| Xbox horizontal D-pad -> PS3 horizontal D-pad | 0xC1 ->0x5BF | 0xCB ->0x5C9 | Both 64x64 |

Each first resource string and its matching `ExportAssets` name use the exact
image identifier recorded in the manifest. The second image string appends the
DDS suffix. The native axis markup keeps 36x36 and vspace -15. Both loading
roots have two frames, and neither uses the legend's glyph timeline. The generic
payload is hash-identical in the HoA, Pregame and Level archives. The manifest
identifies the selected start-game payload separately.

The separate legend sprite 97 has 240 frames. The Xbox whole-D-pad label starts at
frame 96 and is populated at frames 96 to 101, then removes the artwork and stops
on frame 102. The PS3 whole-D-pad label starts at frame 217, remains populated
through frames 217 to 224 and stops at frame 224. The other five glyph sprites
have 295 frames and the PS3 whole-D-pad label at frame 242. Frame 242 exceeds the
timeline of legend sprite 97. Its vector glyphs also use different bounds and
transforms, so a numeric-frame offset is not portable.

The action-string negative above remains valid; it did not cover native-built
HTML. The family manifest records supplied acceptance of the broader eight-name
builder rewrite. Per-tip attribution, selective caller-LR filtering and the
current HTML resolver, cache and provider remain unobserved.

The pair table, together with the blank label and the two family markers,
accounts for every requested label. No Xbox control label lacks a PS3
counterpart. The four pairs that are absent in the button legend are absent on
both sides. The inventory shows no global safety for constructor rewrites and no
runtime behavior.

`DoInitAction` tag 59 action streams start after a two byte sprite ID. The
loading movie has four such tags: `0x233E` (sprite 69), `0x25C8` (sprite 70),
`0x2A09` (sprite 71) and `0x38FC` (sprite 72), with 3, 5, 29 and 4 functions. The
full loading count is 13 top-level action records plus 60 functions, 73 in all.
The button legend movie has no tag 59, so its 41 action tags and 43 records are
not affected by that rule.

How the native code uses these labels is covered on
[the controller prompt page](controller-glyphs.md): the
[HTMLIMG descriptor and append path](controller-glyphs.md#htmlimg-descriptor-and-final-text-callback)
and the [Unit panel writers](controller-glyphs.md#unit-panel-update-call).
