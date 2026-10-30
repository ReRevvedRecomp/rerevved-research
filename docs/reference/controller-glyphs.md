# Controller prompt families

The [controller prompt finding](../../manifests/controller-glyph-family-default-boundary.json)
owns the static name and label boundaries for a proposed restart-required
**Button Prompts: Xbox / PlayStation** option. No setting or hook was implemented.
An owner-reported startup experiment forced the native family byte to zero
while observed city prompts stayed Xbox. That byte is excluded as the
implementation route. A second owner-reported experiment at `0x821E3018/r4`
fired all 15 selected equal-size redirects and showed clean city PlayStation
face prompts. Xbox LT/RT remained unchanged. It also requested native PS3
shoulder names; this establishes availability, not the visible frame selector.

## Preferred filename redirect

On external-image kind2, `0x821E300C` forms filename `r4`. Immediately before
the opener dispatch at **`0x821E3018`**, that pointer is the narrow redirect
candidate. The selected name equation is `D=[request+0xC]`, `B=[D+0x18]`,
`name=B+0xC`; the installed opener is `0x82E87B28`. Rewriting r4 before its
formation instruction would be overwritten.

Selected GFX declarations supply names such as `A.dds`, `B.dds`, `X.dds`,
`Y.dds`, `LT.dds` and `RT.dds`. Descriptor/clone pointer copies are bound.
The supplied experiment logged bare basenames. Exact provider and complete
screen coverage remain unbound; preserve any supplied prefix and compare the
selected basename. Keep replacement bytes
valid for the native request and preserve original descriptor/name storage.

The broader opener captures incoming r4 at `0x82E87B38`, then uses retained
r30 for both type11 lookup and ordinary fallback. Rewriting lookup r6 alone
would leave fallback unchanged. The external-image-specific seam is preferred.
The accepted [opener contract](../../manifests/gfx-file-opener-handoff.json)
and [creation/upload path](gfx-image-rendering.md) retain their conditions.

## Dimensions and package limits

The creator retains declaration dimensions at `0x821E30A4/30A8` and supplies
them to upload `0x821E31C8`. A filename change does not change those values.

| Proposed group | Xbox size | PlayStation size | Result |
| --- | --- | --- | --- |
| A/B/X/Y face positions | 64x64 | 64x64 | Owner-reported equal-size redirects |
| LB/RB to L1/R1 | 128x64 | 64x64 | Name-only substitution is not dimension-preserving |
| LT/RT to L2/R2 | 64x128 | 64x64 | Separate adaptation or label path needed |
| Selected stick/click/direction/Start/Select/axis pairs | 64x64 | 64x64 | Preserve distinct meanings and transforms |
| Controller diagrams | 512x512 | 512x512 | DXT3 versus ARGB/mip headers differ |

The 79 selected DDS headers agree with CSV PNG dimensions. Narrow button-pair
header formats match, but renderer/pixel equivalence is unproved. No successful
swap, stretching or out-of-bounds result is asserted for mismatched inputs.

Selected ordinary families occur in Pregame and hoa; some click/axis assets
occur only in Pregame. `ps3ddown.dds` occurs only in hoa among eight inspected
indices. Existing PS3 down-label bindings instead reuse the up image with
their own transforms. Level/pedia screen membership does not prove which
registered source supplies requested textures. Actual provider and precedence
remain open.

## Movie label alternatives and coverage

CityScreen sprite152 `SetText` sends its icon argument to a named child with
dual-family sprite151. UnitStack sprite234 `SetHelp` sends its icon argument
to four button children using dual-family sprite217. MainMenu, CityScreen
SubMenu and Civilopedia have additional concrete local label edges.

The constructor-installed `+0x2C` target is conditionally `0x8222E740`.
It does not establish that the three fixed-A native field writers target any
of those actual movies. Their current objects, copied value, native argument
producers and publication/consumption remain unjoined.

| Requested screen | Static selected content | Remaining coverage |
| --- | --- | --- |
| City A/B/X/Y/LT/RT | CityScreen dual frames and external bindings; local SetText edge | Actual native caller/provider; trigger dimensions |
| Unit panel | UnitStack dual frames/bindings; local SetHelp edge | Selected panel; UpdateInfoDisplay route bound below |
| Main menu | Dual frames/bindings; root-field-to-local-child edge | Actual button request; logo evidence is separate |
| Popups/combat HUD | StatusPopup, DialogueBox and CombatHUD contain dual families | Complete dynamic label sources and visible coverage |
| Help | ControllerMap and Civilopedia dual families | Diagram format/selection; full tutorial/rich-text census |
| Nonexternal legend | buttonLegend has dual labels and SetIcon children | Artwork/loader classification remains open |

The original seventeen-movie census included twelve dual-family movies, eleven
with selected external-image bindings. Two additional list movies are bound below. A prompt can use both timeline selection and
an external texture. No consumer was conclusively proved to use neither path;
GameMessage lacks the selected structures but its other artwork is unclassified.
This is static movie coverage, not complete runtime screen attribution.

The selected native label candidates are recorded below. The filename seam
has supplied runtime acceptance for 15 equal-size mappings. Restart is required
by scope; complete cross-screen label coverage and live switching remain open.

## Native shoulder-label candidates

The finding's `shoulderLabelBoundary` records 24 exact label/image/placement
edges. City151, Unit217 and Main149 all use these frames:

| Xbox label/frame | PS3 label/frame |
|---|---|
| LB /38 | PS3L1 /178 |
| RB /28 | PS3R1 /162 |
| LT /33 | PS3L2 /186 |
| RT /23 | PS3R2 /170 |

The PS3 frames retain their own 64x64 declarations. City constructor/init/update
edges conditionally reach native LB/RB construction inputs for cityBar.SetPrev/
SetNext. Immediately before `0x82DFFFF8` or `0x82E00064`, r7 is the icon
pointer and r6 is separate text. Movie calls 0xB301/0xB34C forward that second
argument to sprite151 children. Temporary payload and current invocation
delivery still require their helper/retention contracts.

The shared wrapper has a selective candidate before `0x82C7C2F4` spills r7,
with method/format checks. Different root SetIcon calls pass RT/LT in r6 at
`0x82DFE63C/0x82DFE6E8`; their native constructor selects two list movies,
not the requested City151/Unit217/Main149 timelines. Their own consumer join
is recorded in listMovieConsumerBoundary below.

Main has a constructor/table-associated fixed-A field request: r5 before
`0x82E5171C` into `0x82C7C090`. Actual field consumption remains conditional.
Unit's UpdateInfoDisplay-to-SetHelp route is bound below. The generic string
constructor `0x82D3A6C8/r4` receives both delivery families and ordinary text;
no universal icon-only discriminator is established there. No safe single
label hook covering all three screens or conclusively neither-path consumer
is proved.

Retaining the demonstrated equal-size filename route and adding selective
shoulder labels is currently the simpler supported design. Replacing faces
with label hooks would require the same unresolved cross-screen joins.

## List-movie trigger consumers

The selected native RT/LT producer has two bound movie-local edges.
BuildingList root SetIcon at 0x3324 forwards argument reg2 through
this.theBubble.theIcon.gotoAndPlay at 0x333E; root theBubble placement 0x5E6C
and its child theIcon placement 0x5DDE reach glyph sprite157. GreatPeopleList
uses SetIcon 0x402E/call 0x4048 and placements 0x6BB4/0x6B24 to sprite179.
Both use RT at frame 23/LT at frame 33 and PS3R2 at frame 170/PS3L2 at
frame 186, with independent 64x64 PS3
declarations. The manifest retains payload hashes and exact label offsets.

Before `0x82DFE63C`, r6 supplies RT; before `0x82DFE6E8`, r6 supplies LT.
Replacing those selected pointers with PS3R2/PS3L2 is a concrete trigger-label
candidate under retained constructor/base-name/invoke and movie conditions.
It does not assign these list glyphs to City151, Unit217 or Main149.
Unit's selected writers are bound below; current source/storage and delivery
remain conditional.

The selected Unit callback spine preserves S through explicit native helpers
and generic/current-virtual handlers. Its 111-word packet contains 108 instructions
and three table cells, all image-equal. The eight-owner direct SetHelp-name
model does not follow differently named AVM delegation. UpdateInfoDisplay
below supplies that selected consumer join; current source/vector retention,
helper effects and actual invoke retention remain conditions.


## Unit UpdateInfoDisplay ingress

The selected native ingress is **0x82DEB950**, invoking
`this.unitPanel.UpdateInfoDisplay`. Immediately before that call, the four
icon pointers are **r9, r10, caller SP+84 and SP+92**. The stack offsets
are decimal84/92, or **SP+0x54/SP+0x5C**. Their sources are four
words at r28+0/+4/+8/+12; r28 is loaded from current SP+260 at 0x82DEB320.
The four help-text pointers come from a separate vector in r26. The eleven
submitted arguments are strings; the first three are name/attack/defense
display inputs.

In UnitStack sprite246, UpdateInfoDisplay at 0x8727 forwards (index,bN,sN)
at 0x8774/0x8791/0x87AE/0x87CB to infoPanel.SetHelp. Placement 0x97DE selects
sprite234; its four named buttonIcon children select glyph sprite217. This
joins the retained native Unit callback/update spine to the actual movie
consumer rather than selecting a generic root SetHelp by name.

The 72-word packet has 52 instructions and 20 data words, all image-equal.
Current vector contents, parser/current invoke target, normal helper return
and movie/provider identity remain conditions. The selected B writer below
narrows this vector question; the selected optional writers below narrow the local
source question. Current source/storage and delivery remain open.

### Unit icon-vector writer

`unitIconVectorWriterBoundary` connects 0x82DEB818 to a B assignment in the
four-string vector at current SP+260. At that call, r3 addresses cell r28+4*k
and r4 supplies exact B at 0x8212D9B8. Its wrapper derives length 1/offset 0;
under retained resize/copy/source/backing effects the cell contains B,NUL.
One admitted k=0 branch skips the earlier optional insertions and supplies B
in r9 at 0x82DEB950. This is a guarded input path, without an observed action.

Initialization requests four copies of blank through 0x821B93F0/0x821B6E28;
actual allocation/fill and later string/vector lifetime remain conditions.
The accepted Unit217 inventory pairs B at frame 11 with
PS3CIRCLE at frame 130. A substitution selected by method and receiver
at the four icon arguments can request that counterpart
while retaining blank, subject to replacement storage and actual invoke/movie
delivery. The optional writers below bind further selected sources; full screen
coverage remains open.

### Unit optional icon writers

`unitOptionalIconWritersBoundary` binds five selected icon assignments:
0x82DEB604/0x82DEB864 request Y, 0x82DEB7A8 requests X, and
0x82DEB64C/0x82DEB8D0 use r17. Same-owner assignments conditionally make
r17 LS or A; an untouched path retains the unresolved current global string
at 0x8314F0A8. Text assignments use a separate vector.

Under retained early/later help lengths and low8(r16), the two Y predicates
are complementary. The accepted B plus optional insertions fit cells 0..3;
changed gate values can request cell 4, and no selected capacity check prevents
it. Reuse the existing Unit217 label pairs and constructor/copy/storage guards.
Current source/backing and invoke/movie/provider delivery remain conditional.
This is selected native input coverage, without a runtime display or global
single-letter-rewrite safety claim.

## Complete labels and loading tips

The label inventory records all 262 labels across the six requested sprites:
37 in buttonLegend97 and 45 in each other sprite. All Xbox control labels have
semantic PS3 counterparts; blank and XBOX/PS3 family aliases are separate.
Single letters/common words and short codes require context for constructor
rewriting. DLEFT-style identifiers have lower spelling risk, not proven
global safety.

The selected loading-tip axis route uses HTML image sources, separate from
the buttonLegend timeline. Native initialization 0x82E84908 builds 61 cached
tips. Slots 57/58 call 0x82E81F58 at 0x82E85000/0x82E8503C with image names
`XBOXVERTICAL`/`XBOXHORIZONTAL`, width 36, height 36 and vspace-15. The names
are not `DVERTICAL`, `DHORIZONTAL` or `DPAD`, so the supplied 17-name
whole-string experiment did not test these inputs.

One selective hook candidate is **0x82E81F58/r3**, before its first `mflr r12`.
Require incoming LR **0x82E85004** with exact `XBOXVERTICAL`, or
**0x82E85040** with exact `XBOXHORIZONTAL`, and supply `PS3VERTICAL` or
`PS3HORIZONTAL`. This changes only the selected image-name argument. Keep
r4/r5/r6 at 36/36/-15 and retain readable replacement storage through use.
The table initialization flag 0x8314EF9D makes this a restart-required seam.

The builder places the name in HTML `src`; the complete localized tip goes
to `SetBoxText` at **0x82E851AC/r6** through a single narrow-string argument.
The movie forwards it to `Text_txt.htmlText`. No wide string or numeric
`gotoAndPlay` frame is supplied on this selected path. Current formatter,
localization, copying, movie and invoke retention remain conditions.

The supplied 15 filename mappings omitted `xboxvertical` and `xboxhorizontal`.
A later owner experiment reported those additional filename swaps firing;
Xbox LB remained until all eight builder image names were rewritten. The
image-name seam above separates the selected names from surrounding tip prose.

The conditional HTMLIMG kind 1 and constructed final no-op are bound below.
The conditional append result below narrows byte effects. Current provider,
registration/mode, earlier transforms, resize/source retention, final formatting
and actual GFx bytes remain unproved.

Both selected loading movies export all four exact axis names with 64x64
declarations; markup displays them at 36x36. The observed tip index and current
HTML image resolver/cache/provider were not captured. This static result does
not identify which axis the owner saw. The supplied eight-name loading-tip
check records broader runtime acceptance, with exact source/provider and
per-tip attribution still qualified.
The [label inventory](controller-glyph-labels.md) owns movie offsets and the
separate 240-versus-295-frame legend distinction.

See [all labels, pairs and collision classes](controller-glyph-labels.md) and the [canonical inventory](../../manifests/controller-glyph-label-inventory.json).

## HTMLIMG descriptor and final localization callback

`loadingTipLocalizationDescriptorBoundary` in the canonical glyph manifest
binds the selected service factory through constructor 0x821B17C0 to
table 0x82120DA8. Its initial mode is 7 and delimiter 64 (`@`). The initializer
requests `text.ini`, then can run a separate current+0x14 callback; normal
initialization and retention remain conditions.

The selected Pregame.FPK `text.ini` entry 2, payload 47892/22837 bytes,
SHA-256 `92EEA6BEA32528FD71C5B9B7B28F9C6BEB4BA2A4FF79B8605F399FD5960CC6C7`,
has section `HTMLIMG` at line 837 and `Type = __STR` at 839. The native
comparison at 0x82E6A710/equality branch 0x82E6A718 selects kind 1 and stores
it at descriptor+4 at 0x82E6A888; token text is at descriptor+8. The only
candidate section key that prefixes HTMLIMG is HTMLIMG itself. Later sorting
leaves the numeric descriptor index symbolic, rather than its input ordinal.

Under this matching input, successful registration and retained mode 7, the
kind-1 parser arm consumes the first aligned eight-byte vararg and requests a
narrow append at 0x82E69210. This joins the supplied image markup to the
selected parser arm. The conditional append result below narrows byte effects;
resize, current provider/mode and final formatting/delivery remain conditions.

The final localization virtual at 0x82E6A358 conditionally selects cell
**0x82120DB4 ->0x821D5678**. That target is exactly one `blr` and makes no
local text change. It adds no escaping of its own while that table remains
current. Earlier transformations and the actual delivered GFx bytes remain
unproved.

### Conditional initializer and narrow append

The installed initializer 0x821B1980 supplies a zero second argument to
0x82E6AD10. Numeric selector/region results choose a mode, and a zero low-byte
validation result falls back to 7. The setter writes the selected mode at
0x82E6AAD4 to S+124 before unresolved current virtual+8. Constructor mode 7
therefore does not establish the later parser's mode. Current selector,
validation and callback effects remain conditions.

Append 0x821B2A60 receives the complete narrow markup in r4, scans to its first
NUL and supplies that byte count and the destination's old stored length to
0x82D3ACA0. Under admitted nonoverflowing lengths, valid retained source and
compatible resize 0x82D3A748, the selected insertion/copy owners preserve those
bytes without escaping or encoding conversion. Resize backing/length/prefix,
source aliasing and later formatting/delivery remain gates. Append r4 is a
different argument from image-builder 0x82E81F58/r3; this supplies no
selective image-name hook.

### Conditional resize and source aliases

`resizeBackingAndSourceBoundary` binds 0x82D3A748 and its selected reserve,
backing-construction and provider wrappers. Positive resize records requested
length at 0x82D3A7BC after normal reserve return without checking delivered
storage. Growth conditionally copies the old prefix plus terminator, then can
request release of the old header. Requested capacity and recorded length
alone prove no usable destination extent.

Append retains its original source address. A source inside released old
backing can become invalid; even with no growth, a source span crossing the
new terminator address can change before suffix copying. With delivered
writable extent, retained prefix and original source bytes unchanged through
allocation/copy/release/terminator effects, the selected byte operations append
the original markup and NUL without escaping. Actual provider/mode/descriptor,
earlier/later transforms and GFx delivery remain open. No runtime display
experiment is claimed here.

## Supplied loading-tip image acceptance

The owner-reported experiment at 0x82E81F58 rewrote LT/RT/LB/RB,
XBOXVERTICAL/XBOXHORIZONTAL and L3/R3 to their PS3 image names. Shoulder and
trigger markup boxes were squared to their smaller side, preserving vspace;
the owner confirmed PlayStation loading-tip icons at the right size.
This accepts the broader eight-name builder filter, with the two-caller LR
filter proposed above remaining unproved.

`runtimeLoadingTipImageCheck` in the canonical manifest owns the observed
argument sizes and mappings.
Current descriptor/provider identity, full per-tip coverage, actual GFx bytes
and general escaping remain unproved.
