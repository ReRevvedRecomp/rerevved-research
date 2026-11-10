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

The menu checks target state before offering choices that depend on it. Its packed
command contains the mission and target city. The effect dispatcher has
separate entries for the six harmful choices. ID 2 is not offered by this
menu, and leaving quietly skips the action prefix.

One selected unit-filter path creates a Spy and passes a target city directly
to the effect function. It supplies no mission byte, so every valid target on
that path selects defense disruption. This is a local selection policy. It
does not establish that every AI Spy follows the same route or that
other mission commands fail.

A broader AI policy needs the actual entry path for AI Spies in general and the
same target-eligibility guarantees as the interactive menu. Choosing arbitrary
mission IDs would skip those guarantees. The current static result does not
establish a correction or feature for broader AI use.

## Kidnapping and city growth

The kidnap choice appears only when the target city's halfword at `+0x3C` is
nonzero. When a kidnap succeeds in choosing a victim, the store at `0x82CF7134`
clears bit `1<<(type-31)` of that halfword. For a victim of type 32, the stored
name Great Humanitarian, it clears `0x2`. That is the bit that selects the first
reduction in the [growth threshold](city-growth.md#flag-producers). This link
is a candidate (`RVA-F-0417`). What sets the bit is unknown, and a completed
kidnap with a changed threshold has not been observed.

The [mission-selection finding](../../manifests/spy-mission-selection.json)
holds the exact menu, dispatch, caller and target-range evidence. It also
holds the limited negative results and the remaining runtime discriminator.
