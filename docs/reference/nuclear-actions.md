# Nuclear action boundaries

A nuclear action has separate command, gameplay-state and presentation stages.
The selected Move branch can consume the missile after interception or after a
damage-helper call. Neither a disappearing unit nor an invisible explosion
alone identifies a defect.

The [command finding](../../manifests/nuclear-action-boundaries.json#/findings/RVA-F-0333)
binds these static edges in the supported image. No nuclear action was observed
at runtime for this finding.

```text
Move17 -> definition flag0x20000 (initialized ICBM27)
       -> target split and helper -> mode word
          zero -> queued state -> SDI scan -> presentation request/wait
               -> no selected SDI: conditional damage helper
               -> both local outcomes: mode0 missile kill
          nonzero -> separate helper and effect request/poll prefix
                     ... completion and consumption unjoined
```

The zero-mode SDI scan checks tile and city state at the target and eight
table-derived offsets. The tested city bit joins the ordinary SDI Defense
building writer. A selected interception skips the local damage call and
formats an advisor message. Its delivery and display remain separate facts.
The damage helper has its own SDI recheck before the later population and
unit-damage paths; the scan can itself update tile state. Reaching that helper
does not prove damage occurred.

The wait can end when presentation flags clear or when the pump returns false.
It does not prove a completed missile animation. The later mode0 kill marks
the addressed unit dead and clears its link field under the accepted unit-kill
contract. Required returns and retained inputs still matter. The alternate
mode's prefix uses different virtual request/poll slots; the zero-mode result
must not be applied to it.

## Presentation anchors and missing join

The [presentation finding](../../manifests/nuclear-action-boundaries.json#/findings/RVA-F-0334)
identifies a `Nuke_Crater.xml` request, suppression-label sites and preparation
of the `g_fNukeExposure` name handle. It does not identify the active parameter
value, successful asset loading, the missile model, every explosion pass or a
rendered effect instance. A crater name is not a complete visual lifecycle.

A useful observation retains actor, unit, command target and mode, then compares
missile, SDI, city population and victim records before/after the same event.
If gameplay completes correctly but pixels fail, join the actual presentation
target to creation, update, render and destruction, and retain its draw/resource
identity through D3D submission, resolve and presentation. If state differs,
establish the first missing or incorrect command/state edge before a graphics
repair. Save persistence is another acceptance step.

The ordinary [Move lifecycle](../../manifests/unit-movement-lifecycle.json) and
[scene lifecycle](scene-render-lifecycle.md) supply adjacent contracts. Their
observed or static coverage does not establish this nuclear join.
