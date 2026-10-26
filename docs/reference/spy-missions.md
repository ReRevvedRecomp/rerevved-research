# Spy missions

The recovered menu offers these choices. Current unit, building and Wonder
production share one sabotage mission.

| Choice | Mission ID |
| --- | --- |
| Disrupt defensive units | 0 |
| Sabotage current production | 1 |
| Demolish a building | 3 |
| Kidnap a Great Person | 4 |
| Steal Gold | 5 |
| Bribe a Great General | 6 |
| Leave quietly | 7 |

The menu checks target state before offering conditional choices. Its packed
command contains the mission and target city. The effect dispatcher has
separate entries for the six harmful choices. ID 2 is not offered by this
menu, and leaving quietly skips the action prefix.

One selected unit-filter path creates a Spy and passes a target city directly
to the effect function. It supplies no mission byte, so every valid target on
that path selects defense disruption. This is a local selection policy. It
does not establish that every ordinary AI Spy follows the same route or that
other mission commands fail.

A broader AI policy needs the actual entry path for ordinary AI Spies and the
same target-eligibility guarantees as the interactive menu. Choosing arbitrary
mission IDs would skip those guarantees. The current static result does not
establish a correction or feature for broader AI use.

The [mission-selection finding](../../manifests/spy-mission-selection.json)
owns exact menu, dispatch, caller and target-range evidence, bounded negatives
and the remaining runtime discriminator.
