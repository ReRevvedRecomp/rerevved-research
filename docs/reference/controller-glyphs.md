# Controller prompt families

The [controller prompt finding](../../manifests/controller-glyph-family-default-boundary.json)
owns the static name and label boundaries for a proposed restart-required
**Button Prompts: Xbox / PlayStation** option. No setting or hook was implemented.
An owner-reported startup experiment forced the native family byte to zero
while observed city prompts stayed Xbox. That byte is excluded as the
implementation route.

## Preferred filename redirect

On external-image kind2, `0x821E300C` forms filename `r4`. Immediately before
the opener dispatch at **`0x821E3018`**, that pointer is the narrow redirect
candidate. The selected name equation is `D=[request+0xC]`, `B=[D+0x18]`,
`name=B+0xC`; the installed opener is `0x82E87B28`. Rewriting r4 before its
formation instruction would be overwritten.

Selected GFX declarations supply names such as `A.dds`, `B.dds`, `X.dds`,
`Y.dds`, `LT.dds` and `RT.dds`. Descriptor/clone pointer copies are bound.
Actual runtime bytes, prefix and provider remain unobserved: preserve any
supplied prefix and compare the selected basename. Keep replacement bytes
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
| A/B/X/Y face positions | 64x64 | 64x64 | Initial equal-size candidates |
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

Seventeen selected movies include twelve dual-family movies, eleven with
selected external-image bindings. A prompt can use both timeline selection and
an external texture. No consumer was conclusively proved to use neither path;
GameMessage lacks the selected structures but its other artwork is unclassified.
This is static movie coverage, not complete runtime screen attribution.

The next label-alternative question is CityScreen's native SetText icon-argument
producer and same-movie identity. The preferred name seam is a concrete static
candidate for compatible mappings. Restart is required by scope; live swapping
and a whole-family implementation remain unproved.
