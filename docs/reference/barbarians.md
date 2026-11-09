# Barbarian spawning and capital protection

These findings cover the stated static branches. They do not establish an
observed spawning rate or delivered actions. Each condition below still needs
the specified returns, live identity, player ownership, unchanged state,
completed rebuilds and the stated ordering.

## Raging behavior and implementer contract

The [capital protection contract](../../manifests/barbarian-capital-grace-feasibility.json)
specifies a static design, valid only under its stated conditions, for
Raging-only protection of current Palace capitals before signed year -3000.
Normal military actions check the current target when a new action starts.
Eligibility resumes at 3000 BC. A fresh capture backstop protects the transfer
of a city to a new owner. Nuclear checks use the actual addressed damage
footprint, including polar aliases, and fresh guards before population damage
and victim damage.

A refused order takes four steps. It uses the native result1 consumption. It
retires the movement and pending-X state immediately for a fresh actor, and it
clears the matched selections. It then continues through a scoped producer
continuation. The linked-unit case keeps the parent's native busy cleanup. A
normal action skips the later Blitz refill. A native one-shot forced selection
and the limited budget readers supply local ways to make progress. Pending-X
alone, a queue retry0 and a return from the executor alone are not sufficient.

The manifest's `safeGateContract` holds the exact schemas, the supported native
input and interface premises, the sites, the write footprint and the
continuations. This is implementation-ready static evidence. No grace rule is
implemented or observed. Field units, noncapital cities and other civilizations
keep their native behavior. So do departure from a source hut and the selected
nonmilitary Spy, Caravan and espionage operations.

Units may stay in a city early on because of a native garrison check, valid only
under conditions. The default threshold holds the current unit when the weighted
count `C` is at most 2. Raging's aggression input lowers that threshold to 1.
The table below gives the exact comparison and its guards. The selected
connection into this hold adds no separate clock test and no difficulty test.
Earlier candidate selection still has its own time inputs. No fixed-date
departure grace follows.

Holding units in their source city cannot protect only capitals while still
allowing departures into the field or toward other cities. The investigated pair
deadline instead has a named peace-agreement producer. The selected city
predicate uses a reachability plane. Neither establishes protection of a
capital on all routes. The limited evidence for both, and the link from hut
release into the hold, are in `nativeNormalGraceBoundary` in the feasibility
manifest.

More spawning can give units more opportunities to leave, but it does not
reproduce Beta Centauri's aggression, because `BAGRESSIVE` and `BFECUNDITY` are
separate. Three guards explain a hold and release of units in a city, valid only
under stated conditions. They are not a universal hut rule.

| Question | Verdict and native limit |
| --- | --- |
| Do three units trigger departure? | Only under conditions. `0x82CB3F08` takes a city ordinal, checks its owner against the barbarian ordinal and returns `R=3-a` for signed `a=BAGRESSIVE`, except that `a=0` returns 99. At `0x82CC1308..0x82CC1324`, weighted defenders `C<=R` clear the current unit's selected target. `C>R` keeps the selected-neighbor path only when unit byte `+4==0`, and the other holds are bypassed. Default `a=1` therefore allows departure at `C=3`; Beta `a=2` allows it at `C=2`. |
| Who moves and attacks? | Only under conditions. The current input unit can keep its selected neighbor. No instruction sends every city unit out. Eight-neighbor scoring, existing directions, destination and origin markers, definition flags and fallback selection still apply. The local codes and stores need later delivery and execution before they establish a move or an attack. |
| Is this fecundity, era or year? | The barbarian threshold branch reads `BAGRESSIVE` at `Q+0`. That local branch has no fecundity, clock or era input. General AI candidate selection separately depends on the turn, the year and unit stats, as described below. |
| Is rebuilt presence fresh at production? | Only under conditions. The actual live child and result are still unidentified. Whether the completed scan supplies the later read is not yet established. Matching the accepted child class settles its accessor's return and effects, but not the whole rebuild or the order of invocation. |

`C` is the defender byte `0x830E6E90+40*x+y`. Filtered units from the
configured pool add 1 when `+4==0` and 2 otherwise, modulo 256. Production `W`
instead adds 1 or 3. Types 3 to 5 have attack and defense of 1 and pass the
definition masks. Three matching records of the usual kind give `C=3` only with
a fresh rebuild, matching coordinates and no other contribution or wrap. A
nonzero `+4`, a stale plane, an invalid city or other records invalidate a
simple headcount. The live player ownership and the displayed hut remain
inputs.

The hold also needs four things: source halfword bit 0, a valid `0x83128D08`
city, `flags&0x87==0` and a nonzero defense. A marked destination bypasses the
hold. A unit with attack above defense has a support bypass, unlike the
equal-stat barbarian types. Origin 2 or 4 is separate. A cleared target can
enter the fallback, so clearing it does not guarantee that the unit stays
still.

A spawning-only override belongs at the CityUpdate fecundity consumer when the
city is eligible. It must keep the guards on `W`, mode, production, cost,
allocation and scheduling. It adds no fixed multiplier, no forced attacks and no
Beta parity. A separate aggression control is the city-ordinal branch
`0x82CB3F38..0x82CB3F74`. There `a=2` gives `R=1`, and the default `a=1` gives
`R=2`. Keep its owner check, state and return. Changing the whole preset or the
global `Q` changes unrelated settings. No aggression feature is implemented
here.

Runtime acceptance must follow the same unit and city through `a` and `R`, `C`
and `W`, the weight, the neighbor, the holds and fallback, and the executed
command. The evidence of eight functions and 748 words is in
`ragingBehaviorBoundary`.

## City production and rate inputs

City creation selects type 3, 4 or 5 by latitude for a barbarian-owned city.
CityUpdate repeats this selection when both `+0` and `+1` match the barbarian
word. The meaning of the second field is unknown. CityUpdate adds 0, 1 or 3 to
the invested production at `+0x36`. `Q+2`, the presence of coordinates and a
separate mode control the amount.

Completion compares the normal cost and then requests `0x82D15AB0 -> 0x82D11750`
at the city coordinates. Types 3 to 5 have factor 1, which bypasses the Settler
population check. A result of `-1` fails. A result that is not a failure and
stays valid subtracts the cost. The full return, the placement, the queue and
the action are still open.

The Calendar selects populated saved-player cities and may call mode-zero
CityUpdate at `0x82D1FC14`. Cached values and scheduling checks can skip the
call. The actual barbarian is excluded from the extra mode-zero calls at
`0x82D1FD20` and `0x82D1FDC8`, so these calls show no spawn interval. The local
mechanism does not show recurring successful spawns, a fresh guard count, a
population cap or the frequency of departures. The formula, publication, order
and whether values stay valid are in `recurringProductionBoundary`.

## Fecundity and rebuilt presence

`BFECUNDITY` is `Q+2`. Its default is 1, Beta sets 2, and custom scenarios use
the matched bits. Applying the failure value `(-1,0)` resets it. An earlier
preset does not identify the value that is still in place later. For two aligned
inputs, the fill clears exactly 128 `Q` bytes or 1,600 presence bytes and
returns the destination. The rebuild adds the weights 1 or 3 of eligible
configured-pool units, modulo 256, at coordinates sampled earlier. This is not
a fresh guard count.

A callback runs between sampling the coordinates and adding the contribution.
If the root and frame keep their required values, the instructions at
`0x82D12AD4..0x82D12ADC` load `M=[0x8314EFE0]` and `S=[M+0x10]`. A null value
takes a bypass that supplies -1 at `0x82D12B00`. A matching registered `S` with
vptr `0x8215FA78` selects `+0x100`, which leads to the two-instruction function
`0x82A73340`. That function returns `[S+0x20]` without writes or other register
changes. Next, `+0xC` must be readable, and allocation can leave it zero. The
actual child, class and result, the later dispatch, whether the scan stays
valid, and the ordered `0x82D15408` read from the matching presence-table entry
all remain open and depend on conditions.

Fecundity 1 accepts presence 0 or 1 and credits 1. Fecundity 2 accepts presence
0, 1 or 2 and credits 3. Zero mode suppresses a nonzero presence. The speed test
checks for exactly 2 and is not a linear multiplier. These formula cases show
neither a cadence nor a safe mod policy. Details are in
`recurringProductionBoundary.inputBindingBoundary`.

## Setup garrison requests

`0x82D217C8` walks 128 cities. When the bases and frame stay valid,
`0x82D247A8..0x82D24858` selects populated cities whose signed owner matches the
barbarian owner. A value of `-1` disables the walk. It requests the unit of
type 3, 4 or 5 for the latitude at the city coordinates. Whether the request
succeeds, the repeat timing and probability, whether the entry runs only in a
new game, and the full return are not yet shown. A later suffix writes unit `+5`
using an unchecked return, including a possible `-1`. The allocation and the
guards that keep values valid are still required.

## Recount Militia request

Recount `0x82D11AD8`, through the edge `0x82D12880 -> 0x82D11750`, requests
Militia 7 for the signed owner and coordinates of the current city. It does not
use a neighboring barbarian owner. The city owner must match the session result
at `+0xC` and the second local-player result. The first helper compares a
separate global. Whether the city and frame stay valid, and the actual session
target and return, are not yet tied to the code.

A value below 8 selects eight neighbors. It is not a cap on live units. Two
source bytes must be zero. When the city, frame and table stay valid and the
return is normal, the code increments one of them even after `-1`. A byte that
stays set blocks another city request. A population above 2 may decrease even
on failure. A global latch is set before the helpers and the request. After a
suppression or failure it blocks later candidates and cities, and its reset
schedule is unknown. The tables are rebuilt afterward, so the guards consume
earlier weighted bytes, which are not established to be fresh counts.

No local random draw or threshold was identified. The helper is not shown to be
a probability check. This request for Militia near a barbarian establishes
neither recurring barbarian spawning nor a population limit.

## Turn-selection creation request

Dispatch `0x75` reaches `0x82D2AE4C -> 0x82D11750`. The request uses the signed
type from an earlier unit, the fresh active-player owner and the coordinates of
the selected row, taken after two opaque helpers. That the player and unit are
the same ones is not shown. When the definition base stays valid, the request
needs `0x10` clear, `0x8314F1C8` nonzero and a type other than `-1`. The
neighboring 256-record loop is a sibling that bypasses creation when a flag is
set. It is not a population cap. The helper argument `16` has no local
probability comparison and no known odds. A barbarian check, a fixed type and a
recurring schedule are not shown. The selector, the globals and the helper
effects remain open.

## Galley and Galleon Militia tail

`0x82CF5510 -> 0x82D11750` requests Militia 7 for the incoming owner. This
happens after a positive score and an original Galley or Galleon (type 20 or
21). A network byte and whether it stays valid select the original or the local
coordinates. This extra request shows no barbarian rule. The 256-slot scan tests
the owner and `+7` against `0xFF`. It does not count live units. The Militia
tail can follow an allocation failure, and its result differs from the result
the outer function returns. The later flags, recount and fields need normal
returns and a valid owner, frame and record. No local odds or recurring schedule
is established.

## Paired Spy requests

`0x82D0E340` requests Spy 28 at `0x82D0EAB0` and `0x82D0EAC4`, using the saved
owner and coordinates. The second request needs the return and the input of the
first to stay valid. A nonzero global halfword makes the selection after the
earlier alternatives. Neither result is checked. No barbarian owner or schedule
is identified. A six-attempt search and a six-value selector show no live
maximum and no odds. The candidate and selector inputs, the helper effects and
the full return remain unknown. The sibling for a zero halfword has separate
dispatch and type checks.

## Unit decisions and origin counts

Barbarians can bypass a low combat score, a coordinate rejection and one halving
penalty in AI decisions. The other guards remain. The chance to attack and the
movement are not yet shown. A separate origin check discards neighbors below 2
or 4, counted from filtered weighted bytes and unit and effective-stat markers.
Neither producer requires a hut or a barbarian, so no rule of two or four guards
for a hut follows. The rebuild order, the live inputs and the movement consumer
remain unknown.

## Beta Centauri preset

The named built-in preset is selector 4. Its description advertises increased
barbarian numbers. After default initialization, its branch writes these slots
at `0x82DAF26C..0x82DAF29C`:

| Scenario slot | Default | Beta |
| --- | ---: | ---: |
| `BAGRESSIVE`, Q+0 | 1 | 2 |
| `BFECUNDITY`, Q+2 | 1 | 2 |
| `BARBVSGOODY`, Q+4 | 1 | 2 |
| `STARTERA`, Q+0x1C | 0 | 4 |
| `CANNOTWINBY`, Q+0x22 | 0 | 2 |
| `NOSPACERACE`, Q+0x24 | 0 | 1 |
| `STARTYEAR`, Q+0x3E | 0 | 2025 |
| `DISPLAYCARD`, Q+0x3C | -1 | 556 |

The names and defaults come from
[`scenario-schema.json`](../../manifests/scenario-schema.json).
Only the aggression threshold and the fecundity credit are tied to code here.
The names alone do not show other slot effects or a path specific to a scenario
ID.

If fecundity 2 is still in place at the production reader, it selects credit 3
when `W<3` and the separate suppression does not apply. Aggression 2 separately
lowers the weighted city threshold described above.

The selected-record publisher `0x82D6D568` runs only when object byte `+0x18==0`.
It loads an ID from `[object+0x20] + 4*[object+0x14]` and calls the application
function at `0x82D6D59C` with `r4=1`. A valid selected ID 4 takes the Beta
branch. The later helper and callback effects and the actual object and
selection are not tied to the code. The sibling call at `0x82D6D504` instead
supplies `(-1,0)` and can restore the defaults.

Active game publication, resets, whether values stay valid after load, fresh
planes and natural scheduling therefore remain open and depend on conditions.
No game was run and no probe was made for this finding.

## Date, turns and era

The current turn affects general AI candidate selection. One guarded test of the
turn and the pair can install the current neighbor directly. A separate score
adjustment applies when the signed current turn has remainder zero modulo four.
It has no barbarian exemption. Barbarians bypass a different score rejection
that combines the turn with the coordinates.

These are deterministic local decisions, with the other guards and the
origin-count restriction still in force. They do not show a departure every four
turns, and they do not identify an actual hut invocation.

The displayed year has a separate use. Under the other-player guard and an
unnamed halfword guard, a year of 0 or more skips calls and state writes before
the common score handling. That predicate does not directly select a direction.
The skipped callees can affect later inputs, so indirect effects on scoring
remain unresolved.

The current turn, the configured start turn, the displayed year, the era and the
technologies a player owns are distinct. The accepted Calendar evidence ties the
elapsed turn and the era-dependent technology grants to code. Those grants do
not establish a spawn timer. The effective attack and defense functions have no
direct clock or era read.

Their cumulative era-bonus lookup excludes the actual barbarian owner, and types
3 to 5 bypass the direct technology branch in attack. Three things still prevent
a complete conclusion that scaling does not occur: the opaque selector10, a
signed configuration addend and inserted host stat helpers.

No confirmed link between the scenario fields and the game fields shows that
Beta Centauri's date accelerates spawning or hut departure. The manifest's
`timePolicyBoundary` gives the exact branches, the four-function read set, the
2,820 verified native words and the return, state and action links that are
required.

At `0x82CC055C..0x82CC05AC`, the selected adjustment adds `10*(A[I]-w)` to an
intermediate score. Here `w` is 1 or 3 according to the unit's current `+4`
byte. The inspected producer accumulates eligible records from the configured
unit pools into `A`. It uses attack at least equal to defense and other
definition filters, adds the same weights, and can wrap modulo 256.

This contribution path has no filter for barbarians only and none for huts.

The reader saves its origin index before earlier helper calls, then reloads the
unit fields and `A` later. The producer also keeps an early coordinate index
while reloading fields after calls. Reading the subtraction as support from
other units needs five things: a matching live unit, an unchanged weight,
unchanged coordinates, a completed rebuild whose data stays valid, and no wrap.
None of these is shown yet.

Two located callers, which are entry points into this code, load a saved player
scalar and a selected-unit sample taken earlier. A helper runs between those
loads. The actual values, the saved-word definition that reaches the load and
the register and frame state that stays valid therefore remain qualified.
Neither edge nor the unnamed bit of the source tile identifies a barbarian hut.

The next helper, `0x82CBC8E8`, has concrete native save and restore slots for
the caller's `r27` and `r31`. Its returning continuations restore those values
if the frame and saved bytes stay intact. It also explicitly writes unit
coordinates and flags.

Keeping the same player and unit registers therefore does not keep the unit
contents from before the call. It also does not show that the later AI origin
matches an earlier `A` contribution. The helper's output word and its returned
scalar are separate results.

Changing this score term could affect general AI candidates. It is not an
established control over hut release or spawn rate. The manifest entry
`timePolicyBoundary.originInputRetentionBoundary.callerRetentionBoundary` holds
the caller, the return conditions and the memory limits.

## Rate and limit boundary

The routine responsible for city production and its local credit inputs are
identified above. The actual scheduling and the policy that limits the active
barbarian population remain open. The 128 city records are a storage walk, and
the 256 per-player unit slots of the common creator are storage capacity.
Neither establishes a population policy for Raging Barbarians.

The other inspected creation branches included copy-like operations, paired-unit
operations, a Spy grant, a city-fill branch for nonbarbarians and a Calendar
grant that skipped the barbarian player. In particular, the comparison of the
returned index with 128 in the city-fill branch is not a barbarian population
maximum. Movement, attack policy and scenario-specific behavior remain
separate.

The exact scopes, the native words, the qualifications on the producer and the
reload, the searches that were closed, and the remaining publication and input
discriminator are in
[barbarian-spawn-population.json](../../manifests/barbarian-spawn-population.json).

## Barbarian leader message screens

In the inspected paths, a Barbarian leader message screen appears in two
situations. Other callers are not yet classified. The first eligible contact
with a Barbarian city in each latitude band shows a taunt, but only when the
city carries the human player's visibility bit. Otherwise the screen is skipped
and the band stays unshown. Capturing a Barbarian village shows a comment from
the leader of that band. A friendly village never raises one. The paths, the
band rule and the native skips are in
[barbarian-contact-messages.json](../../manifests/barbarian-contact-messages.json).
