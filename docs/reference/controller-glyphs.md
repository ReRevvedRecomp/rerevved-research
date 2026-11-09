# Controller prompt families

The game draws button prompts (A, B, X, Y, the triggers, the D-pad and so on)
from two sources. Some prompts are external images named after the button, such
as the A or LT image. Others are frames inside a screen movie, picked by a
frame label such as `A` for Xbox or `PS3X` for PlayStation. A prompt can use
both. The [controller prompt finding](../../manifests/controller-glyph-family-default.json)
records the code paths for both, for a proposed restart required option named
**Button Prompts: Xbox / PlayStation**. No setting or hook is implemented.

## What a modder can do

Example: on the city screen, asking the game for the PlayStation cross image in
place of the A button image makes the A prompt draw as a cross. Doing the same
for each equal-size face prompt gives clean PlayStation cross, circle and
triangle prompts on the city screen. The trigger prompts LT
and RT need a different route, because their images have a different shape (see
[Dimensions](#dimensions-and-package-limits)).

Tester reports show what each route does on the city screen and loading
tips:

- The native family byte does not pick the prompt icons on this path. Setting
  it to the PlayStation value leaves the city prompts Xbox.
- Replacing equal-size button images gives clean PlayStation face prompts.
- Changing the label strings for the bumpers and triggers to their PlayStation
  names gives correctly sized shoulder and trigger prompts beside the face
  prompts, with no blank icons and no change to the controls, because the movies
  declare their own PlayStation images.
- Label changes reach only some prompts. The loading screen D-pad stays Xbox.
  Changing all eight loading tip image names and making the shoulder and
  trigger boxes square was enough to turn loading tip icons PlayStation at the
  right size.
- PlayStation and Xbox versions of the stick and direction images exist, but
  which frame a screen shows is not known.

The manifest keeps each hook point and request by meaning. The tests cover the city screen and loading tips. They give no complete count of
visible prompts, no provider for each screen, and no support for switching
families while the game runs.

## Filename redirect

For an external image of kind 2, `0x821E300C` forms the file name in `r4`. The
best hook point is `0x821E3018`, just before the call to the file opener. The
name comes from `D=[request+0xC]`, `B=[D+0x18]`, `name=B+0xC`, and the installed
opener is `0x82E87B28`. A rewrite of `r4` before `0x821E300C` would be
overwritten.

The movie declarations supply names such as `A.dds`, `B.dds`, `X.dds`, `Y.dds`,
`LT.dds` and `RT.dds`. The descriptor and clone copies of the name pointer are
confirmed. The reported run logged bare names with no folder prefix, including
the A button, left bumper and a video-player request. Which provider serves them, and which screens
use them, is not fully confirmed. Keep any prefix the game supplies, compare
the base name, keep the replacement bytes valid for the request, and do not
change the original descriptor or name storage.

The general opener also reads the incoming `r4` into `r30` at `0x82E87B38`. It
uses `r30` for both the type 11 lookup at `0x82E87B88` and the fallback open.
Changing only the lookup argument `r6` would leave the fallback on the old name,
so the image specific hook point is preferred. The
[opener contract](../../manifests/gfx-file-opener-handoff.json) and the
[image creation and upload path](gfx-image-rendering.md) keep their own
conditions.

## Dimensions and package limits

The image creator keeps the declared width and height at `0x821E30A4` and
`0x821E30A8` and passes them to the upload at `0x821E31C8`. A name change does
not change them.

| Proposed group | Xbox size | PlayStation size | Result |
| --- | --- | --- | --- |
| A, B, X, Y | 64x64 | 64x64 | Reported equal-size redirects |
| LB, RB to L1, R1 | 128x64 | 64x64 | A name swap does not keep the size |
| LT, RT to L2, R2 | 64x128 | 64x64 | Needs a separate fix or the label route |
| Stick, click, direction, Start, Select and axis pairs | 64x64 | 64x64 | Keep distinct meanings and transforms |
| Controller diagrams | 512x512 | 512x512 | Xbox is DXT3 with no declared mips; PS3 is ARGB with mip count 10 |

The 79 selected DDS headers agree with the PNG sizes in the title image
inventory. The narrow button pair headers declare matching 32-bit ARGB masks,
caps and mip fields. That does not prove that decoded pixels or rendering are
the same. No result is claimed for a swap, stretch or out of bounds read with
mismatched sizes.

The 44 selected button, axis and analog names have 77 copies: 41 in Pregame, 2
in Common0 and 34 in hoa. The two controller diagrams make 79 headers. Eight
package indices were inspected: Pregame, hoa, Common0, Level, Misc0, Misc1,
units and pedia. Level, Misc0, Misc1, units and pedia hold no exact selected
button images, so a movie in those packages can request a prompt that another
registered source supplies. Which source wins is not observed. Common0 holds
the analog helpers (`analogL3` and `analogR3`, which have no matching PS3 name)
and not the regular button pairs. Pregame holds both names of every regular
pair except the PS3 down prompt.

`ps3ddown.dds` is only in hoa, entry 203. The movie labels for PS3 down reuse
the PS3 up image with their own transforms, so swapping a raw down image for an up
image by name alone can conflict with those transforms. The manifest records
the entry's offsets and digest.

## Movie labels

Each label edge below starts at a call that passes an icon argument to a named
child of a movie. All of them end in a frame sprite that has both families.

| Movie | Local label input and destination | Positions (hex) |
|---|---|---|
| `Level:GFX_CityScreen.gfx` | sprite 152 `SetText(theString reg2, theIcon reg3)` calls `this.theIcon.gotoAndPlay(reg3)`; the child `theIcon` is sprite 151 | body 0x5723 to 0x578A, call 0x5788, placement 0x57B5 |
| `Level:GFX_UnitStack.gfx` | sprite 234 `SetHelp(theNum reg2, theIcon reg3, theString reg4)` calls `this['buttonIcon'+theNum].gotoAndPlay(reg3)`; four children are sprite 217 | body 0x5E53 to 0x5E7F, call 0x5E6A, placements 0x6126, 0x6142, 0x615E, 0x617A |
| `Pregame:GFX_MainMenu.gfx` | sprite 153 reads `_root.theIcon` and calls `this.theIcon.gotoAndPlay`; the child is sprite 149 | action tag 0x2FFD, call 0x3050, placement 0x2FD8 |
| `Common0:GFX_CityScreen_SubMenu.gfx` | sprite 172 reads `_root.theIcon` and calls the local `theIcon.gotoAndPlay`; the child is sprite 168 | action tag 0x2B33, call 0x2B7B, placement 0x2AFA |
| `pedia:GFX_Civilopedia.gfx` | sprite 181 `SetText(theString reg2, theIcon reg3)` calls `this.theIcon.gotoAndPlay(reg3)`; the child is sprite 179 | body 0xA713 to 0xA77A, call 0xA778, placement 0xA77C |

The 12 movies with both families are `Pregame.FPK:gfx_mainmenu.gfx`,
`Common0.FPK:hoa_keylegend.gfx`, `Common0.FPK:gfx_dialoguebox.gfx`,
`Common0.FPK:gfx_cityscreen_submenu.gfx`, `Common0.FPK:gfx_controllermap.gfx`,
`Common0.FPK:gfx_keyboard.gfx`, `hoa.FPK:buttonlegend.gfx`,
`Level.FPK:gfx_cityscreen.gfx`, `Level.FPK:gfx_unitstack.gfx`,
`Level.FPK:gfx_combathud.gfx`, `Level.FPK:gfx_hud_statuspopup.gfx` and
`pedia.FPK:gfx_civilopedia.gfx`.

The constructor installed `+0x2C` target is `0x8222E740` only when the
constructor runs as selected. This does not show that the three fixed A native
field writers reach any of these movies. Their current objects, copied value,
argument producers and delivery are not connected to a movie.

| Screen | Selected content | Still open |
|---|---|---|
| City A, B, X, Y, LT, RT | Sprite 151 holds all six label and image pairs; `SetText` reaches it | The native caller and provider; trigger sizes |
| Unit panel | Sprite 217 holds all six; `SetHelp` reaches `buttonIcon0` to `buttonIcon3` | Current delivery (see [Unit panel](#unit-panel-update-call)) |
| Main menu | Sprite 149 holds all six; `_root.theIcon` reaches it | The real button request; logo evidence is separate |
| Popups | `Level:GFX_HUD_StatusPopup.gfx` sprite 182 and `Common0:GFX_DialogueBox.gfx` sprite 142 have both families | The label sources; the dialogue A image placement is incomplete in the parser used |
| City submenu | Sprite 168 holds both families; `_root.theIcon` reaches it | The native writer |
| Combat HUD | `Level:GFX_CombatHUD.gfx` sprite 181 holds all six | The native label source |
| Help | `Common0:GFX_ControllerMap.gfx` sprite 138 holds all six and two 512x512 diagrams; Civilopedia sprite 179 holds all six | Diagram choice; the full tutorial and rich text census |
| Keyboard and legend | `Common0:GFX_Keyboard.gfx` sprite 137 and `HoA_KeyLegend.gfx` sprite 129 hold all six | The request alone does not show the file is resolved or loaded |
| Legend without images | `hoa:buttonLegend.gfx` sprite 97 has both label families and no image tags | The loader and provider |
| Unclassified | `GFX_CityScreen_OverlayMessage`, `GFX_HUD_TurnInfoPopup`, `GFX_Key` and `GFX_AdvisorBox` declare button images | No label timeline was found; a declaration does not show use |
| Neither structure | `Common0:GFX_GameMessage.gfx` has no image tags and no label or action evidence | This does not rule out font, vector or imported artwork |

The first census covered 17 movies. Twelve have both families, 11 of them with
external image declarations, plus the one legend without images. Two list
movies are covered in [List movies](#list-movies). No consumer was proved to use
neither route. Help, tutorial and rich text coverage is incomplete. This is
coverage of the movie files, not of which screen the game shows at runtime.

## Shoulder and trigger labels

The finding's `shoulderLabelBoundary` records 24 label, image and placement
edges. City 151, Unit 217 and Main 149 use the same frames:

| Xbox label and frame | PS3 label and frame |
|---|---|
| LB 38 | PS3L1 178 |
| RB 28 | PS3R1 162 |
| LT 33 | PS3L2 186 |
| RT 23 | PS3R2 170 |

Each PS3 frame keeps its own 64x64 declaration. The manifest lists the label
offsets for all three movies in decimal.

The city constructor `0x82DFC728` requests `GFX_CityScreen.gfx` and installs a
table that selects init `0x82E02300`. When the objects and helpers are as
selected, init and the update chain reach `0x82DFFE38`. Signed nonnegative
previous and next indices choose the LB and RB inputs. Just before the calls at
`0x82DFFFF8` and `0x82E00064`, `r7` holds the icon pointer and `r6` holds
separate text. These are two hook points that could turn LB into `PS3L1` and RB
into `PS3R1`. The temporary string they point to still depends on the string
helper and on how long it stays valid.

The `cityBar` sprite 247 passes the `SetPrev` and `SetNext` icon argument to
`prevIcon` and `nextIcon`, both sprite 151 (calls 0xB301 and 0xB34C, placements
0xBC93 and 0xBC75). City face calls supply A, B and X in mode 0 and A, B and
LS in mode 1. A method member named `barX` therefore does not always carry the
X label.

The shared call wrapper offers a hook point before `0x82C7C2F4` spills `r7`,
limited by the method and the two string format. The root `SetIcon` calls for
the building and great people lists pass `r6` at `0x82DFE63C` (RT) and
`0x82DFE6E8` (LT). Their constructor selects two list movies, not City 151,
Unit 217 or Main 149.

Main menu: the constructor `0x82E51828` requests `GFX_MainMenu.gfx` and installs
a table whose `+0x24` selects the fixed A writer. Before `0x82E5171C`, `r5` is A
and `r4` is `this.theIcon`, passed to `0x82C7C090`. Slot choice, `S+8`
identity, field publication and use of `_root.theIcon` are not confirmed. The
Unit constructor's A, Y and X root fields have no matching `theUnitIcon` token
in the movie.

Both delivery families reach the narrow string constructor `0x82D3A6C8` through
`r4`, but so does regular text. A hook there needs a way to tell an icon
argument from text, and neither spelling nor caller supplies one. No single
label hook that covers all three screens is proved.

Keeping the equal-size filename route and adding selective shoulder label hooks
is the simpler design. Replacing the face prompts with label hooks would need
the same unresolved links between screens.

## List movies

The building list and the great people list each have a native RT and LT
producer with two movie-local edges. In the building list, root `SetIcon` at
0x3324 forwards its argument `reg2` through `this.theBubble.theIcon.gotoAndPlay`
at 0x333E. The root placement `theBubble` (0x5E6C) and its child `theIcon`
(0x5DDE) reach glyph sprite 157. The great people list uses `SetIcon` 0x402E,
call 0x4048, and placements 0x6BB4 and 0x6B24 to sprite 179. Both use RT at
frame 23, LT at frame 33, PS3R2 at frame 170 and PS3L2 at frame 186, each with
its own 64x64 declaration. The manifest keeps the payload hashes and label
offsets.

Before `0x82DFE63C`, `r6` supplies RT. Before `0x82DFE6E8`, `r6` supplies LT.
Replacing those pointers with `PS3R2` and `PS3L2` is a concrete trigger label
candidate, under the constructor, base name, invoke and movie conditions. It
does not apply to City 151, Unit 217 or Main 149.

## Unit panel update call

The native call is at `0x82DEB950`, invoking `this.unitPanel.UpdateInfoDisplay`.
Just before it, the four icon pointers are `r9`, `r10`, caller `SP+84` and
`SP+92` (hex `SP+0x54` and `SP+0x5C`). They come from four words at `r28+0`,
`+4`, `+8` and `+12`; `r28` is loaded from the current `SP+260` at `0x82DEB320`.
The four help text pointers come from a separate vector in `r26`. All eleven
arguments are strings, and the first three are the name, attack and defense
text.

In UnitStack sprite 246, `UpdateInfoDisplay` (0x8727) forwards the index,
`bN` and `sN` at 0x8774, 0x8791, 0x87AE and 0x87CB to `infoPanel.SetHelp`.
Placement 0x97DE selects sprite 234, whose four `buttonIcon` children select
glyph sprite 217. This connects the native Unit callback to the movie that uses
it, without selecting a root `SetHelp` by name. The callback keeps the string
through native helpers and handlers, and the selected search of direct `SetHelp`
names does not follow differently named delegation in the movie.

Still unconfirmed: the current vector contents, the parser and invoke target,
the helper return, and the movie and provider.

**Icon vector writer.** `unitIconVectorWriterBoundary` links `0x82DEB818` to a
B assignment in the four string vector at `SP+260`. At that call `r3` points to
cell `r28+4*k` and `r4` supplies B at `0x8212D9B8`. Its wrapper uses length 1
and offset 0, so the cell holds B and a NUL when resize, copy, source and
backing behave as selected. One path with `k=0` skips the earlier optional
inserts and supplies B in `r9` at `0x82DEB950`. Setup requests four copies of
`blank` through `0x821B93F0` and `0x821B6E28`; the real allocation and fill are
not confirmed. Unit 217 pairs B at frame 11 with PS3CIRCLE at frame 130, so a
substitution chosen by method and receiver at the four icon arguments can ask
for that frame while keeping `blank`.

**Optional icon writers.** `unitOptionalIconWritersBoundary` records five icon
assignments. `0x82DEB604` and `0x82DEB864` request Y, `0x82DEB7A8` requests X,
and `0x82DEB64C` and `0x82DEB8D0` use `r17`. Assignments in the same function
set `r17` to LS or A. When none runs, `r17` keeps the unresolved global string
at `0x8314F0A8`. Text assignments use a separate vector.

For the early and later help lengths and `low8(r16)` as selected, the two Y
conditions are complementary. B plus the optional inserts fit cells 0 to 3.
Different values can request cell 4, and no selected size check prevents it.
Reuse the existing Unit 217 label pairs. These are the selected native inputs.
They show no runtime display, and they do not show that rewriting single letters
everywhere is safe.

## Labels and loading tips

The [label inventory](controller-glyph-labels.md) lists all 262 labels in the
six sprites: 37 in buttonLegend 97 and 45 in each other sprite. Every Xbox
control label has a PS3 counterpart. `blank` and the XBOX and PS3 family
aliases are separate. Single letters, common words and short codes need context
before a constructor rewrite. DLEFT style names have a lower spelling risk, and
none is proved safe everywhere.

The loading tip prompts that show the D-pad axes are HTML image sources, not
buttonLegend frames. Native init `0x82E84908` builds 61 cached tips. Slots 57
and 58 call `0x82E81F58` at `0x82E85000` and `0x82E8503C` with the image names
`XBOXVERTICAL` and `XBOXHORIZONTAL`, width 36, height 36 and vspace -15. These
names are not `DVERTICAL`, `DHORIZONTAL` or `DPAD`, so the 17 string label
experiment never saw them.

One selective hook point is `0x82E81F58`, register `r3`, before its first
`mflr r12`. Require the incoming link register `0x82E85004` with exactly
`XBOXVERTICAL`, or `0x82E85040` with exactly `XBOXHORIZONTAL`, and supply
`PS3VERTICAL` or `PS3HORIZONTAL`. This changes only the image name. Keep `r4`,
`r5` and `r6` at 36, 36 and -15, and keep the replacement storage readable
while it is used. The tip table flag `0x8314EF9D` makes this a restart required
hook point.

The builder puts the name in the HTML `src`. The full localized tip goes to
`SetBoxText` at `0x82E851AC` (`r6`) as one narrow string, and the movie forwards
it to `Text_txt.htmlText`. No wide string and no numeric `gotoAndPlay` frame is
supplied on this path.

Both loading movies export all four axis names with 64x64 declarations, and the
markup shows them at 36x36. The tip index and the HTML image resolver, cache and
provider were not captured, so the static result does not say which axis a
player saw. The label inventory records the 240 frame legend and 295 frame
glyph sprite difference.

The 15 filename mappings left out `xboxvertical` and `xboxhorizontal`. A later
reported experiment showed those swaps firing, and an Xbox LB stayed visible
until all eight builder image names were rewritten. The eight names the builder
requested in that run were:

| Name | Size (width x height) | vspace | Rewrite |
|---|---|---|---|
| LT | 28 x 56 | -40 | PS3L2, 28 x 28 |
| RT | 32 x 48 | -40 | PS3R2, 32 x 32 |
| LB | 56 x 28 | -10 | PS3L1, 28 x 28 |
| RB | 56 x 28 | -10 | PS3R1, 28 x 28 |
| XBOXVERTICAL | 36 x 36 | -15 | PS3VERTICAL |
| XBOXHORIZONTAL | 36 x 36 | -15 | PS3HORIZONTAL |
| L3 | 36 x 36 | -15 | PS3L3 |
| R3 | 36 x 36 | -15 | PS3R3 |

No face letter reached this builder. The two caller filter above was not tested
on its own. `runtimeLoadingTipImageCheck` in the manifest records these values.
Tip by tip coverage, the descriptor and provider, the bytes the movie receives
and general escaping remain unconfirmed.

## HTMLIMG descriptor and final text callback

`loadingTipLocalizationDescriptorBoundary` links the service factory through
constructor `0x821B17C0` to table `0x82120DA8`. The first mode is 7 and the
delimiter is 64 (`@`). The initializer requests `text.ini`, then may run a
separate `current+0x14` callback.

The selected `Pregame.FPK` `text.ini` entry 2 (payload 47892/22837 bytes, SHA-256
`92EEA6BEA32528FD71C5B9B7B28F9C6BEB4BA2A4FF79B8605F399FD5960CC6C7`) has the
section `HTMLIMG` at line 837 and `Type = __STR` at line 839. The comparison at
`0x82E6A710` and its equal branch `0x82E6A718` select kind 1 and store it at
`descriptor+4` at `0x82E6A888`. The token text is at `descriptor+8`. The only
section key that starts with HTMLIMG is HTMLIMG itself. Later sorting leaves
the descriptor number symbolic, not equal to its input order.

When the input matches, registration succeeds and the mode stays 7, the kind 1
parser arm reads the first aligned eight byte argument and requests a narrow
append at `0x82E69210`. This ties the image markup to that parser arm.

The final text callback at `0x82E6A358` selects cell `0x82120DB4`, which points to
`0x821D5678`. That target is a single `blr`, so it changes no text and adds no
escaping while that table stays current. Earlier transforms and the bytes the
movie finally receives are not confirmed.

**Initializer and append.** The installed initializer `0x821B1980` passes a zero
second argument to `0x82E6AD10`. Numeric selector and region results choose a
mode, and a zero low byte from validation falls back to 7. The setter at
`0x82E6AAD4` writes the chosen mode to `S+124` before an unresolved current
virtual at `+8`, so the constructor's mode 7 does not fix the later parser mode.

Append `0x821B2A60` takes the full narrow markup in `r4`, scans to the first
NUL, and passes that byte count and the destination's old length to
`0x82D3ACA0`. When lengths do not overflow, the source is valid and resize
`0x82D3A748` behaves as selected, the insert and copy functions keep those bytes
without escaping or encoding change. The append `r4` is a different argument
from image builder `0x82E81F58` `r3`, so it gives no image name hook.

**Resize and source aliases.** `resizeBackingAndSourceBoundary` covers
`0x82D3A748` and its reserve, backing and provider wrappers. A positive resize
records the requested length at `0x82D3A7BC` after the reserve returns, without
checking the storage actually delivered. Growth copies the old prefix and
terminator, then can release the old header. A requested capacity or recorded
length alone proves no usable destination size.

Append keeps its original source address. A source inside released old backing
can become invalid. Even without growth, a source that crosses the new
terminator address can change before the suffix is copied. With writable
storage delivered, the prefix and source bytes unchanged through the
allocation, copy, release and terminator writes, the selected operations append
the original markup and NUL without escaping. The provider, mode and
descriptor, earlier and later transforms and the movie delivery remain open.

## Open questions

- Native Xbox to PS3 action mapping, including stick movement against click and
  the confirm and cancel convention.
- The Unit icon vector writers and their current values, full Main field use,
  which City trigger a player sees, and the loading tip index and HTML image
  provider.
- Full coverage of HUD, unit, help, menu and popup consumers beyond the 17 movie
  census and the two list movies.
- The artwork of buttonLegend beyond the D-pad vectors in the label inventory.
- Package provider, precedence and preload completion for each prompt; image
  and texture lifetime and renderer release.
- Input device detection, automatic switching and live switching.

Evidence: [controller-glyph-family-default.json](../../manifests/controller-glyph-family-default.json)
(`RVA-F-0364`), [controller-input-glyph-selection.json](../../manifests/controller-input-glyph-selection.json)
and [controller-glyph-label-inventory.json](../../manifests/controller-glyph-label-inventory.json)
(`RVA-F-0368`).
