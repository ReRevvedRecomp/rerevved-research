# Controller prompt families

The [controller prompt finding](../../manifests/controller-glyph-family-default-boundary.json)
owns the static name and label boundaries for a proposed restart-required
**Button Prompts: Xbox / PlayStation** option. No setting or hook was implemented.
An owner-reported startup experiment forced the native family byte to zero
while observed city prompts stayed Xbox. That byte is excluded as the
implementation route. A second owner-reported experiment at `0x821E3018/r4`
fired all15 selected equal-size redirects and showed clean city PlayStation
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
| Unit panel | UnitStack dual frames/bindings; local SetHelp edge | Selected panel only; actual native producer |
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
has supplied runtime acceptance for15 equal-size mappings. Restart is required
by scope; complete cross-screen label coverage and live switching remain open.

## Native shoulder-label candidates

The finding's `shoulderLabelBoundary` records24 exact label/image/placement
edges. City151, Unit217 and Main149 all use these frames:

| Xbox label/frame | PS3 label/frame |
|---|---|
| LB /38 | PS3L1 /178 |
| RB /28 | PS3R1 /162 |
| LT /33 | PS3L2 /186 |
| RT /23 | PS3R2 /170 |

The PS3 frames retain their own64x64 declarations. City constructor/init/update
edges conditionally reach native LB/RB construction inputs for cityBar.SetPrev/
SetNext. Immediately before `0x82DFFFF8` or `0x82E00064`, r7 is the icon
pointer and r6 is separate text. Movie calls0xB301/0xB34C forward that second
argument to sprite151 children. Temporary payload and current invocation
delivery still require their helper/retention contracts.

The shared wrapper has a selective candidate before `0x82C7C2F4` spills r7,
with method/format checks. Different root SetIcon calls pass RT/LT in r6 at
`0x82DFE63C/0x82DFE6E8`; their native constructor selects two list movies,
not the requested City151/Unit217/Main149 timelines. Their own consumer join
is recorded in listMovieConsumerBoundary below.

Main has a constructor/table-associated fixed-A field request: r5 before
`0x82E5171C` into `0x82C7C090`. Actual field consumption remains conditional.
Unit's actual native SetHelp producer is unjoined. The generic string
constructor `0x82D3A6C8/r4` receives both delivery families and ordinary text;
no universal icon-only discriminator is established there. No safe single
label hook covering all three screens or conclusively neither-path consumer
is proved.

Retaining the demonstrated equal-size filename route and adding selective
shoulder labels is currently the simpler supported design. Replacing faces
with label hooks would require the same unresolved cross-screen joins.

## List-movie trigger consumers

The selected native RT/LT producer's two movie-local edges are now bound.
BuildingList root SetIcon at0x3324 forwards argumentreg2 through
this.theBubble.theIcon.gotoAndPlay at0x333E; root theBubble placement0x5E6C
and its child theIcon placement0x5DDE reach glyph sprite157. GreatPeopleList
uses SetIcon0x402E/call0x4048 and placements0x6BB4/0x6B24 to sprite179.
Both use RT23/LT33 and PS3R2-170/PS3L2-186, with independent64x64 PS3
declarations. The manifest retains payload hashes and exact label offsets.

Before `0x82DFE63C`, r6 supplies RT; before `0x82DFE6E8`, r6 supplies LT.
Replacing those selected pointers with PS3R2/PS3L2 is a concrete trigger-label
candidate under retained constructor/base-name/invoke and movie conditions.
It does not assign these list glyphs to City151, Unit217 or Main149.
Unit's actual native SetHelp ingress remains the next question.

The selected Unit callback continuation preserves S through explicit native
helpers and reaches generic/current-virtual handlers. Its111-word packet
contains108 instructions and three table cells, all image-equal. The separate
eight-owner generated search did not join actual Unit SetHelp; it is not a
complete native absence result. Current callback/update ingress, method format
and icon-argument position remain the next discriminator. No Unit label hook
is selected from proximity to a generic SetHelp materializer.
