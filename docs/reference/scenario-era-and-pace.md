# Starting eras and game pace

Native scenarios provide startup technology grants and separate rule inputs.
They do not establish either all-earlier-era ownership or a single setting
that slows the whole game. The [starting-era finding](../../manifests/scenario-start-era-grant-boundary.json)
and [SPEEDMODE finding](../../manifests/scenario-speedmode-movement-boundary.json)
own the new conditional native boundaries.

## Starting technology grants

Active scenario Q=`0x830E8FD0` contains signed16 STARTERA14 at Q+0x1C,
SPEEDMODE12 at Q+0x18, and TECHNOLOGYRATE4 at Q+8. Their recognized names
alone do not define their gameplay policy.

Selected setup instructions in `0x82D217C8` choose grant counts5/14/24 for
STARTERA1/2/3. A loop samples nonzero technologies, checks eligibility through
`0x82CE2C50`, rejects already-owned candidates, writes the player's ownership
bit at `0x830EDC48`, and increments the acquisition tally at `0x830EDD08`.
That tally is not proved to be a unique-known-technology count. Eligibility
checks ownership, prerequisites and other fields/helpers; no local
technology-era comparison is established. Opaque helpers can carry additional
policy.

A separate STARTERA4 arm writes a common mask to ownership words1..46,
excluding words0 and47. It sets selected player-era words to3 and uses prior
tally[0]+46 for its tally value. The mask comes from a retained frame-object
field and is not independently proved to identify active players.

These selected setup instructions use direct writes; they do not locally
call ordinary acquisition `0x82D09208`. That distinction does not characterize
the whole setup. Native count selection and candidate eligibility do not
prove every technology assigned to an earlier era is granted.

An all-earlier-era feature still needs an authoritative technology-era
assignment and a setup point before dependent readers. Ownership alone does
not prove derived unlocks, initial/cumulative civilization abilities,
government, city bonuses, discovery rewards and notifications are coherent.
The [starting-grant](../../manifests/starting-technology-grants.json) and
[first-discovery](../../manifests/technology-first-discovery-rewards.json)
contracts retain those distinctions, along with save and peer requirements.
The generated setup body ending at EOF is excluded as semantic closure;
selected native words support these local claims.

## Coordinated slower progression

SPEEDMODE12 is read as a signed movement-stat addend by `0x82CF1F70` on both
return paths. It is not a proved universal time multiplier, movement budget
or command-cost policy. The handwritten title movement override is excluded
from native evidence.

| Surface | Recovered input or consumer | Scope |
|---|---|---|
| Science | TECHNOLOGYRATE4 selects a research-cost factor in `0x82CF0EE8` | Distinct authored cost input; actual selection and cadence remain conditional |
| Unit production | Definition cost and effective scalar in `0x82CF1148` | Separate thresholds, modifiers, display/rush/AI/completion ordering |
| Buildings/Wonders | Category costs in `0x82CF1278` | Separate non-unit comparisons and stores |
| Growth | Shared word `0x830E45C8` in `0x82CF1060` | Initialization, progress production and policy remain unbound |
| Culture/borders | City influence arithmetic and separate victory credits | No universal culture-cost scalar established |
| Movement | SPEEDMODE12 in `0x82CF1F70` | Signed stat addition; custom negative values are not proved safe |
| Calendar/events | Piecewise turn-to-year conversion and separate year/turn readers | Calendar changes can affect events without slowing economic progress |
| Presentation | Native Normal/Fast animation timing | Separate from game-rule progression |

The existing [science](science.md), [unit](unit-definitions.md),
[growth](city-growth.md), and [calendar](game-calendar.md) records own the
reused surfaces. The continuation below binds a nonzero preset and closes the
converter's direct-input question; an economic/event reader remains open. A coordinated speed design needs separate choices
for costs, yields, movement, calendar and event cadence. No setting or runtime
behavior was implemented.

## Era tally and preset continuations

The starting-era finding's `tallyEraAndSetupBoundary` binds an ordinary chooser
using signed acquisition-tally thresholds5/14/24 to request player eras1/2/3,
with0 below5. This classifies player progress; it does not assign individual
technologies to eras. Setter `0x82D05A48` writes a changed era before a current
virtual+0x16C and conditional local-player effects. A selected later setup
call at `0x82D23050` explicitly requests era0. Complete grant-to-call and
first-reader ordering remain unbound, so the earlier ownership-grant window
does not establish safe finalization. Authoritative technology-era membership
remains the next discriminator.

The pace finding's `presetAndCalendarBoundary` binds built-in ordinal5 to a
SPEEDMODE1 store at `0x82DAF2DC`, after selected formatting calls. Actual
selection/retention remains conditional. All32 instructions of turn-to-year
converter `0x82CEFA20` use local arithmetic with no memory access or calls;
it has no direct SPEEDMODE input. Transformed caller input and other economic
or event readers remain outside that negative. Next select one such bounded
consumer before claiming a coordinated slower-game rule.
