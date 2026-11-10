# Unit movement presentation

When a unit moves, the game first commits the move to the unit's data: its
tile, its remaining movement points and its command state. Only then does it
draw the move. The drawing code is a separate coordinate updater, `0x82D5FFC8`,
that slides the unit's on screen position toward the new tile one frame at a
time. This page covers that updater: what controls its speed, where it snaps the
unit to its destination, and where a mod could change either. Nothing here
changes where a unit ends up or how many movement points it spends.

## What a faster move would change

The updater picks a whole number step `q` each frame. When the distance left to
the target is at most `q + q/2` (with `q/2` truncated toward zero), the unit
snaps straight to the exact target. Otherwise it keeps sliding and sets the
shared busy flag again, so the command thread keeps waiting. Two changes are
possible at this point:

- Scale `q` up. The unit snaps from farther away, so the end of the slide
  shortens. The selected code does not show that `q` is the distance the slide
  advances on a frame.
- Skip the comparison and take the snap arm. The unit's on screen position
  jumps to the target on the first update.

Worked example (distance and `q` in the updater's own units, values chosen for
the example):

| Case | `q` | Snap when distance is at most | Distance 3 |
|---|---|---|---|
| Native, `q` = 1 | 1 | 1 | Keeps sliding |
| `q` scaled by 2 | 2 | 3 | Snaps |

Small steps are fragile. For example, at a frame time of 17 milliseconds and a scalar
of 85, `q` is 1. Halving the scalar first gives 42 and `q` becomes 0. Any
change must check that a scaled value is positive and that `q + q/2` does not
overflow, and fall back to the native value when it is not.

Snapping the on screen coordinates is not the same as finishing the move. The
unit's later animation, action clocks, camera and the command's wait are not
skipped by it (see [Limits](#limits)).

## Where the numbers come from

**Records.** A unit slot index is `I = 256*owner + slot`, where `owner` is the
player who owns the unit. The logical unit record is `U = 0x830F2BF0 + 84*I`. The presentation
record is `A = 0x83024F18 + 292*I`; its base addresses are formed at
`0x82D601B0` and `0x82D601BC`. A unit has several children, looped at
`0x82D60CDC` to `0x82D60DC4` according to its definition. Child `c` keeps its
current X at `A+0x4C+4*c` and its current Y at `A+0x70+4*c`. Its auxiliary
action state is at `A+0x28+2*c`. This is a logical unit presentation updater.
It is not shown to be a newly allocated movement actor.

**Target.** `0x82D5BBF4` to `0x82D5BC24` derive the first target from `U+0x1C`
and `U+0x1E` times 1024, and a local helper adds definition and formation
offsets. The caller at `0x82D60DC4` receives the outputs and reloads them at
`0x82D60E28` and `0x82D60E30`.

**Distance.** `0x82D61170` to `0x82D61260` compute a signed approximate X and Y
distance and handle horizontal wrap before progress is judged.

**Frame time.** `0x82D60044` to `0x82D60084` convert the frame scalar to
milliseconds and clamp `0x8314F04C` to 1 through 250. Other presentation code
shares that value.

**Scalar.** `0x82D61884` to `0x82D618B8` derive a scalar from `0x82FFE7C8` and
`0x8312B8DC`. `0x82D618C0` to `0x82D61978` may adjust it from the queued route
distance and from the definition value at `+0x42`, clamped. No gameplay option
names are assigned to these inputs.

**Shared flag.** `0x82D6197C` to `0x82D61994` halve the scalar when bit `0x400`
of the shared word `0x830E4550` is set. This does not make a Fast option. The
word has other gameplay and command readers and is part of the native saved
game state, so it cannot serve as a local preference. In the supplied
positive input example the halving can take `q` from 1 to 0.

**Step.** `0x82D619A0`, `0x82D619A4` and `0x82D619A8` compute
`q = trunc(signed_low32(scalar * frameMs) / 1000)`, with the product kept to
its low 32 bits as signed. `0x82D619AC` through `0x82D619BC` compare the
distance with `q + trunc(q/2)`. The `q` value is in register `r27`.

**Type timing.** `0x82D5CC98` returns eight distinct timing values from 40 to
100. They are used at `0x82D6127C` to `0x82D612F0` for auxiliary field `+0x3A`.
They are not a universal step duration.

## Hook points

| Candidate | Address | What it does |
|---|---|---|
| Scale the step | `0x82D619AC`, after the native quotient at `0x82D619A8` | Scale only a validated positive `r27`. The later comparison, slide and action work stay native. Check the scaled `q` and `q + q/2` for overflow; invalid inputs use the native value |
| Force the snap | `0x82D619BC`, native fallthrough `0x82D619C0` | For one validated move child, take the native snap with the registers, condition state and frame as they are. This snaps the on screen position on the first update. It does not remove the wait or the skeletal animation |

A hook must identify one regular unit move request (command 17) by owning player, slot,
`I`, child and the current request and thread. Stale or unrelated identities
fall back to native behavior. No blanket unit type or global clock override is
selected. A mod must not change the shared cooldown `0x830E4548`, the shared
frame time `0x8314F04C`, `0x830E4550` as a local preference, the unit's
movement budget, tile, queued destination, step or lifecycle flags, or clear
the shared busy flag by hand.

## Snap, busy and completion

- **Snap arm.** `0x82D619C0` and `0x82D619C8` store both target coordinates and
  continue at `0x82D62030` through `0x82D619CC` and `0x82D619D8`. Native code also
  picks a snap arm at `0x82D61860` to `0x82D61880` when the distance is above
  3072, in the selected observer or visibility state, or when shared bit `0x40`
  is set.
- **Busy.** `0x82D60050` and `0x82D60054` clear busy bit `0x02000000` on entry.
  Above the near target threshold, `0x82D619EC` sets selected active work and
  `0x82D61A10` ORs the busy bit, stored at `0x82D61A18`. An exact snap skips this
  one busy set. Other writers are not excluded.
- **Arrival.** `0x82D62030` to `0x82D6204C` test both exact target coordinates.
  `0x82D62050` to `0x82D6212C` keep the native action and arrival work.
  `0x82D6222C` onward keeps later animation work, including calls at
  `0x82D62480`, `0x82D624BC` and `0x82D62B7C` to `0x82D5E568`.
- **Tail.** `0x82D62CF4` to `0x82D62D04` clean up the native unit flags when no
  selected active work remains. The caller completion stays at `0x82CD75C4`
  (presenter `0x82D11AD8`, pump `0x82E2A838`) and the command tail at
  `0x82CE16AC`.
- **Camera.** The helper `0x82D5CD78` to `0x82D5CE4C` picks the combined
  auxiliary values at `+0x4C` and `+0x70` and writes the focus values
  `0x82F771C4` and `0x82F772D0`. When the combined X is zero or less it uses the
  logical unit coordinates instead. It shows that coordinates are published
  there. It does not show that a regular move calls it, or what the engine
  camera does with the result.

## Actor clock and child state

Two other clocks sit beside the step above. Neither is a skeletal animation
clock, and the step `q` is not one either.

**Update frequency.** The step uses integer arithmetic on the low 32 bits. With
a scalar of 85, one 17 millisecond update gives `q` of 1, but splitting the same
time into updates of 8 and 9 milliseconds gives 0 and 0. The same total elapsed
time can therefore move a unit differently when updates run more often. The
frame time clamp and the snap, busy and arrival work stay part of any
comparison.

**Actor clock.** The type 24 actor updater `0x82D5E660` samples the shared frame
time at `0x82D5E694`. When a fresh resolver result differs from the actor's
owner, the sample is doubled by a low 32 bit shift at `0x82D5E7E0`, so the
step `d` is 1 to 250, or 2 to 500. That test is not an AI only test.
`0x82D5E7F8` advances the current time, and `0x82D5E808` copies the previous
sample into `A+4`. At `0x82D5E858` to `0x82D5E868` it compares the signed
previous time with the signed low 32 bits of `L - d - 2000`, where `L` is the
return value of `0x82D5E568`. For a definition with byte `+0x48` equal to 1,
child 0 is selected, and request 3 maps to 1010 through `0x82D5CFD0` and the word
`0x82F793AC`. `0x82E59F98` then asks child `+0x28` through the registries
`0x831560D0`, `0x831560D8` and `0x831560E0`. The returned `L` and these
registry values were not observed, and the clock is not a general movement,
skeleton or combat duration.

**Child state.** The child constructor `0x82D9B710` installs table `0x82135C90`.
Its initialized slot `+0x08` is `0x821B3B60`, which stores its second argument
at child `+0x6C`. Selector 37 and then 14 are written there in that order. A
store is not processing: the first code that reads child `+0x6C` is unknown. The
parent's `+0x6C` and the child's `+0x6C` are different fields. Zero elapsed time
is not a no op for the constructed view, so skipping an update on a zero delta
would drop real work.

Evidence:
[the actor clock](../../../manifests/spaceship-part-presentation.json#/worldActorFrameBoundary/ownerTiming)
and [the child selector](../../../manifests/spaceship-part-presentation.json#/worldActorChildDispatchBoundary/initializedSelector).
For the combat side, see
[the combat endpoint](../../../manifests/combat-outcome.json#/conditionalPresentationEndpoints).
The shared word `0x8314F04C` is read by several paths, which does not make it an
animation setting.

## Limits

- A coordinate snap is not a `unit+0x22 = 0xFFFF` finish. It does not prove that
  child action clocks, the camera, every busy source or the command wait finish
  at once.
- No menu, debug or scenario Instant option and no AI only speed input exists in
  the selected code. Computed values keep native signed and low 32 bit behavior.
- Tests on the owning player and on visibility do not tell an AI player from
  another human. Neighboring commands do not prove multi step route behavior. Fog,
  zone of control, cities, linked units and AI order must stay native.
- Types 24 and 27, combat and the commands before a regular move, transports,
  formations, modal interruption and routes that continue across turns, and
  rail, teleport, ship and aircraft moves need separate checks.
- The shared word `0x830E4550` is saved native state, so a per player speed
  preference has no supported place to live. Nothing here shows a peer local
  setting is safe.
- The selected path was not seen running. Whether a move command reaches this
  updater, how its children and models finish, how the camera applies the
  focus values, and what happens in the cases above are open. The accepted
  [lifecycle finding](../../../manifests/unit-movement-lifecycle.json) places
  simulation before presentation and gives the completion edges above, and the
  [speed producer finding](../../../manifests/presentation-speed-producers.json)
  rejects the shared cooldown as a speed input.

Evidence: [unit-movement-presentation.json](../../../manifests/unit-movement-presentation.json)
(`RVA-F-0383`). It supports limited experiments, not an enabled option or
observed acceleration.
