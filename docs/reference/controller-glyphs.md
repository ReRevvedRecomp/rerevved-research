# Controller glyph families

The [controller-family finding](../../manifests/controller-glyph-family-default-boundary.json)
binds a native default-byte producer and selected movie label consumers. It
does not yet connect that byte to displayed PlayStation glyphs.

## Native configuration and loading

`Use360ControllerAsDefaultKeymap` is registered at `0x82E2D5D0` with byte
destination `0x82F6E866` and default 1. Its description associates zero with
PS3 controller keys. The selected helper writes a normalized queried value or
the supplied default, subject to normal helper returns and retained storage.
The effective reader, configuration source and initialization phase remain
unbound. A key and a producer do not prove a working platform switch.

The accepted [external-image path](gfx-image-rendering.md) registers deferred
descriptors, then opens a requested filename through the installed
[resource-backed opener](../../manifests/gfx-file-opener-handoff.json).
Two PS3 literal calls into the named-file preloader are bound. Their completion,
selected FPK copy and residency remain unobserved; boot, front-end and screen
entry timing are not established for actual glyph instances.

## Movie consumers and mapping

Two selected legend movies implement `SetIcon(number, icon, text)`: icon is
passed to `gotoAndPlay` on a named button instance, while text is assigned
separately. Selected main-menu, keyboard and legend sprites contain both
families and explicit external-image bindings. Another legend has neither
external-image nor standard bitmap tags; its artwork mechanism remains open.

This five-movie census does not cover all HUD actions, unit panels, tutorial
text, menus or popups. It establishes neither general inline-text tokens nor
native delivery of every icon argument.

No native action-pair table was recovered. A proposed semantic mapping uses
face position: A/B/X/Y to cross/circle/square/triangle; bumpers to L1/R1 and
triggers to L2/R2. Stick artwork stays separate from stick clicks, Start/Back
maps to Start/Select, and directional variants retain their transforms.
Confirm/cancel policy and unmatched analog helpers remain open.

Archive indices confirmed both families and an additional PS3 down asset.
The inspected down-label bindings instead reuse the up image. Replacing names
by spelling alone could therefore conflict with existing artwork transforms.
Asset membership and label order do not establish native control mapping.

The finding's `nativeLabelInputBoundary` follows separate native field
requests. Three selected writers supply a fixed `A` input for `_root.theIcon`
or `this.theIcon`. They reach a temporary-string constructor and an indirect
movie-object call at virtual slot `+0x2C`. The copy/publication helper, current
target and same-movie identity remain unproved. Supplied input is not a
displayed glyph receipt, and these selected arguments do not read the family
byte. Another native `SetIcon` producer selects economic labels, showing why
method-name equality alone cannot identify controller consumers.

A new aligned static pointer-word search found no exact pointer to the family
byte. Runtime-written pointers, containing-base aliases, unaligned pointers
and computed forms remain outside that negative result.

## Feasibility

First bind the selected field request's actual `+0x2C` target and same-movie
publication, then join a read or proven containing-storage alias of
`0x82F6E866` to the current label. If it controls those labels, a startup preference is the
first candidate. Selected load-name redirection is a fallback requiring known
package availability, dimensions and preserved transforms. A first
implementation should require restart while the minimum reload boundary is
unproved.

Live switching requires a coherent contract for label copies, movie instances
and definitions, deferred descriptors, GFx registration, name/resource caches,
image/texture references, release and invalidation/rebinding. The generic
loader does not establish those lifetimes. No setting, patch, game launch,
display result or safe live swap was implemented or observed.
