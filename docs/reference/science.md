# Science and technology cost

One `CalendarTurnAdvance` path pools progress toward the selected technology
from rows whose signed comparison halfword matches the incoming player. It
compares that progress with the cost returned by `0x82CF0EE8`. The grouping
suggests teams, but the full identity of the comparison array is not
established.

| State | Address and indexing |
| --- | --- |
| Selected technology | `0x830EDD48[player]` |
| Stored progress | `0x830EDD68[player*48 + technology]` |
| Group comparison | Signed halfword `0x830E9070[player]` |
| Acquisition context | `0x830E3328[player]` |
| Completion marker | `0x830E3348[player]` |

The cached-city path adds signed `+0x44` only when the native selection and
cache conditions hold, rather than once per city per turn unconditionally.
Completion needs three things: pooled progress at least equal to the cost, an
incoming player that differs from the word at `0x82F700B0`, and a technology the
player does not own. A valid nonzero technology reaches `0x82D20C34` and then
`TechnologyAcquire` with the player, the technology, the saved context, source
`0` and phase `1`. The context starts at `-1`. The first city whose individual
progress meets the cost fills it, so pooled completion can still use `-1`.

The block calls the cost function again, adds pooled progress minus that
second cost to Gold at `0x830ED544[player]`, then marks completion before
testing for a nonzero technology. Technology zero skips acquisition. The block
does not subtract progress. It does not establish that excess progress carries
over to the next technology. Stores keep the low 32 bits and comparisons are
signed. A nonnegative excess needs valid indices, no signed overflow and a
stable cost. There is no local technology clamp. Source `6` civilization grants
remain separate. Sharing the acquisition function does not establish a common
policy, the meanings of the reason codes or the timing.

## First-discovery rewards

Literacy matches the Courthouse definition in the generic first-discovery
building loop. It is a native reward candidate. It is subject to four checks:
first discovery, source and phase, recipient score, and delivery. Greek
participation is not required for that local match. This does not establish the
cause of a reported caption or replace the separate science effect. The
[reward boundary](../../manifests/technology-first-discovery-rewards.json)
records the limits on the recipient, which must stay unchanged, and on
presentation.

Ceremonial Burial selects Temple through the building reward loop. Its
recipient score equals city population, while a later check requires a score
greater than population. The selected native path therefore chooses no Temple
recipient. Bypassing that hurdle for Temple keeps the existing largest-city
rule, the tie rule for earlier city slots and the missing-Temple check. It does
not select a capital or create a reward absent from the native machinery.

Egypt's Medieval Irrigation uses the free-technology source. The acquisition
function explicitly suppresses first-discovery effects for that source, before
Irrigation's population scan. A targeted Egypt exception is a change to this
shipped rule. It can keep the first-ownership check and the phase-one
population reward. Phase two only presents the result.

The [first-discovery finding](../../manifests/technology-first-discovery-rewards.json)
records exact branches, recipient filters, duplicate limits and the remaining
helper and runtime requirements. A reported discovery notice alone does not
establish delivery.

## Technology research cost

`TechnologyResearchCost` (`0x82CF0EE8`) starts at two for valid nonzero
technology. Each of the three nonsentinel prerequisites adds the occurrence
count rooted at that prerequisite, and adds it again if its ownership query is
zero. The helper does not test descendant ownership, and it counts repeated paths
each time. There is no visited set: starting at depth zero, it expands through
500 and counts children at 501. The helper does not initialize depth. Its guard
limits recursion depth, not total work.

Four checks enable the scaling: byte `0x8314F10B`, the classifier, the
local-player mask in the requested ownership, and `global_82FFE7C8 > 1`. With
scaling, the result is signed low32 `6*base` divided by signed low32
`global_82FFE7C8+6`, truncated toward zero. It is then multiplied by
`[15,10,8,5][index]`, where the index is the signed halfword `0x830E8FD8`.
Without scaling, the base is multiplied directly. The index is unchecked, and
the arithmetic wraps. Division traps do not prevent a negative denominator after
adding six wraps. Technology zero returns 9999 early. Technology -1 skips the
prerequisites but keeps the checks and the multiplier.

The selected setup path can copy difficulty into `0x82FFE7C8`. The separate
setup overrides, and the limits on keeping the value unchanged, are recorded in
the
[village reward finding](../../manifests/friendly-village-rewards.json#/settlersDifficultyBoundary).
The meanings of the multiplier and the game speed, and the runtime cost, are not
yet established. The exact domains are in the
[cost manifest](../../manifests/technology-research-cost.json).
See also [gameplay cost arithmetic](gameplay-cost-arithmetic.md#technology-cost)
for a worked rounding example.

## AI research choice and Alphabet

Status: candidate defect, from static evidence only. No AI research choice
was observed.

When a player with no research selected reaches the shared technology prompt
(`0x82CECCD8`) as a nonlocal player, the game builds a list of the technologies
that player can research and scores them to pick one. The scoring loop starts at
the second entry of that list. The first technology on the list is never scored,
so the AI cannot choose it. When Alphabet is first on the list, the AI skips
Alphabet.

Worked example. An AI player owns nothing and the eligible technologies are
Alphabet (technology 1), Bronze Working (2) and Ceremonial Burial (3). The game
builds the list `1, 2, 3, -1`, where `-1` is an end marker. The loop runs three
times and scores Bronze Working, Ceremonial Burial and the end marker. Alphabet
is never scored. The list has the same shape on every later choice, so Alphabet
stays skipped until the player gets it another way. The real list depends on the
definitions and on what the player owns.

How the code does it:

- The nonlocal branch lists the eligible technology IDs in ascending order and
  appends `-1`. With `N` real technologies the list size is `N + 1`.
- At `0x82CED340` the scan pointer is set to the list base plus 4, which is the
  second entry. The loop at `0x82CED610` runs `N` times and advances the pointer
  by 4 each time. It visits positions 1 through `N`: it skips position 0 and
  visits the `-1` marker at position `N`.
- The result goes out as a numeric type 4 value at `0x82CED61C..0x82CED62C`. The
  command writer `0x82CDFFB0` stores it in `0x830EDD48[player]`, the selected
  technology.
- The shared eligibility check `0x82CE2C50` accepts Alphabet when the player does
  not own it. Its three prerequisite values and its blocker value are all `-1`.
  The optional prerequisite check `0x82CE2280` returns zero for Alphabet, so it
  does not exclude it.
- When `N` is 0 the loop is skipped, and that path is unchanged by the defect.
  When `N` is 1, the loop scores only the `-1` marker.

The turn-start check at `0x82D1D604` calls the prompt for a nonlocal player
without a command, as listed in the
[prompt callers](../../manifests/technology-prompt-callers.json). The branch
tests the human mask, not whether the player is an AI, so being nonlocal does not
prove an AI player.

A correction would start the loop at the first real entry, keep the count and the
empty list path, visit every eligible ID once and never the `-1` marker. Forcing
Alphabet ownership or lowering its cost does not fix the list. See
[AI settings](ai-options.md) for the other AI configuration findings.

Open conditions:

- Whether AI players reach this branch in a natural game, and whether the
  scoring result is used unchanged, has not been observed.
- Modified technology definitions, other ways the AI picks research and what
  happens when the `-1` marker is chosen are not covered.
- `0x82D20C9C` calling `0x82CED640` is a grant scan over technologies 0 through
  47. It does not select research and is not part of this finding.

The [manifest](../../manifests/ai-research-candidate-ordinals.json) holds the
exact locators, the cases by real candidate count `N` and the falsification conditions.

## Spaceship launch result

The selected launch dialog returns a signed arrival year or -1. Its caller
accepts only positive results, which excludes valid BC dates and year zero,
before that producer submits the launch. The selected arrival evaluator accepts
the signed date domain, with separate state and victory checks.

The [arrival-year boundary](../../manifests/spaceship-launch-arrival-year.json)
records the field chain, the native cancellation sentinel and a proposed
`result != -1` acceptance contract. This is a static correction contract.
Whether the dialog result stays valid, the launch delivery and the repaired
victory remain unobserved.

## Spaceship part presentation

Each built part increments a component count, can show an advisor notice, and
starts a rocket actor whose busy wait holds the turn. The shared spaceship
screen also returns launch results, so refusing it can change gameplay. The
[spaceship part presentation](spaceship-part-presentation.md) page covers the
code path, every hook point and what a mod that skips the cutscene must keep.

## Evidence sources

- [Technology research cost](../../manifests/technology-research-cost.json)
- [First-discovery rewards](../../manifests/technology-first-discovery-rewards.json)
- [Science completion](../../manifests/science-completion.json)
- [AI research candidate ordinals](../../manifests/ai-research-candidate-ordinals.json)
- [Spaceship launch arrival year](../../manifests/spaceship-launch-arrival-year.json)
- [Starting technology grants](../../manifests/starting-technology-grants.json)
- [City yield state credits](../../manifests/city-yield-state-credit.json)
