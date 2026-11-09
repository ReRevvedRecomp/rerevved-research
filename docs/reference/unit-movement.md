# Unit movement presentation

The selected native unit-child translation updater is `0x82D5FFC8`.
It advances presentation coordinates separately from logical tile coordinates.
Its integer movement step per frame depends on frame milliseconds, route and
definition inputs. The updater uses this step to choose between translation
and snapping; it is not always the distance advanced. There is no single fixed step duration in that
branch. The shared frame delta and post-action cooldown are unsuitable inputs
for an isolated movement preference.

At `0x82D619A8` the updater computes that movement step in r27.
The comparison at `0x82D619BC` can take the native coordinate-snap arm at
`0x82D619C0`; exact arrival is checked at `0x82D62030`. The longer translation
arm reasserts shared busy, while subsequent auxiliary action and animation
work can remain after a snap. Preserve that work and native unit cleanup.

Two possible diagnostic hooks follow: scale a validated positive movement step
before `0x82D619AC`, with overflow checks, or condition the branch at
`0x82D619BC` to its native snap fallthrough. Both require a validated ordinary
Move17 request, owner/slot and current child lifetime. Neither establishes
zero wait or disabled skeletal animation. Keep logical movement, destination,
unit lifecycle, shared clocks and busy flags native.

The accepted ordinary lifecycle places simulation before presentation and
retains presenter/pump completion at `0x82CD75C4`, then command completion at
`0x82CE16AC`. The actual selected updater invocation within that wait,
accelerated completion, camera application and specialized-case parity remain
unobserved. The identified focus helper `0x82D5CD78` publishes auxiliary
coordinates; this does not prove its ordinary-move invocation or camera effect.

Types 24/27, combat, transport and formation variants, modal and cross-turn
work, and rail, teleport, ship and aircraft cases require separate validation.
Observer and visibility tests do not establish human/AI equivalence. No peer-local safety
or native Instant option follows from these selected paths.

Evidence: [unit-movement-presentation.json](../../manifests/unit-movement-presentation.json)
(RVA-F-0383), with its ordinary lifecycle and presentation-producer dependencies.
The static assessment supports conditional experiments, not an enabled option
or observed acceleration.
