# Science and technology cost

One `CalendarTurnAdvance` path pools progress toward the selected technology
from rows whose signed comparison halfword matches the incoming player. It
compares that progress with the cost returned by `0x82CF0EE8`. The grouping
suggests teams, but full comparison-array identity remains qualified.

| State | Address and indexing |
| --- | --- |
| Selected technology | `0x830EDD48[player]` |
| Stored progress | `0x830EDD68[player*48 + technology]` |
| Group comparison | Signed halfword `0x830E9070[player]` |
| Acquisition context | `0x830E3328[player]` |
| Completion marker | `0x830E3348[player]` |

Cached city path adds signed `+0x44` under native selection/cache gates, not
unconditionally per city/turn. Completion needs pooled progress>=cost, player
!=`0x82F700B0`, technology unowned. Valid nonzero technology reaches
`0x82D20C34` -> `TechnologyAcquire` with player, technology, retained context,
source `0`, phase `1`. Context starts at `-1`; the first city whose individual
progress meets the cost fills it, so pooled completion can still use `-1`.

The block calls cost again, adds pooled-minus-second-cost to Gold at
`0x830ED544[player]`, then marks completion before nonzero-tech test; zero skips
acquisition. It neither subtracts progress nor proves next-tech carryover.
Stores keep low32, comparisons signed: nonnegative excess needs valid indices,
no signed overflow, stable cost; no local technology clamp exists. Source `6`
civilization grants remain separate; shared acquisition proves no common
policy/reason semantics or cadence.

## First-discovery rewards

Literacy matches the Courthouse definition in the generic first-discovery
building loop. It is a native reward candidate subject to first-discovery,
source/phase, recipient-score and delivery gates; Greek participation is not
required for that local match. This does not establish the cause of a reported
caption or replace the separate science effect. The
[reward boundary](../../manifests/technology-first-discovery-rewards.json)
records the retained-recipient and presentation limits.

Ceremonial Burial selects Temple through the ordinary building reward loop.
Its recipient score equals city population, while a later gate requires a
score greater than population. The selected native path therefore chooses no
Temple recipient. Bypassing that hurdle for Temple retains the existing
largest-city rule, earlier city-slot ties and missing-Temple check. It does
not select a capital or create a reward absent from the native machinery.

Egypt's Medieval Irrigation uses the free-technology source. The acquisition
owner explicitly suppresses first-discovery effects for that source, before
Irrigation's population scan. A targeted Egypt exception is a change to this
shipped rule. It can retain the ordinary first-ownership gate and phase-one
population reward; phase two only presents the result.

The [first-discovery finding](../../manifests/technology-first-discovery-rewards.json)
records exact branches, recipient filters, duplicate limits and the remaining
helper and runtime requirements. A reported discovery notice alone does not
establish delivery.

## Technology research cost

`TechnologyResearchCost` (`0x82CF0EE8`) starts at two for valid nonzero
technology. Each of the three nonsentinel prerequisites adds the occurrence
count rooted at that prerequisite, and adds it again if its ownership query is
zero.
Descendant ownership is untested; repeated paths count repeatedly. There is no
visited set: initial depth zero expands through 500 and counts children at 501.
The helper does not initialize depth; the guard bounds depth, not total work.

Four gates enable signed low32 `6*base` / signed low32 `global_82FFE7C8+6`,
truncated toward zero: byte `0x8314F10B`, classifier, local-player mask in
requested ownership, `global_82FFE7C8 > 1`. Then multiply by
`[15,10,8,5][index]`, signed halfword index `0x830E8FD8`; without scaling,
multiply base directly. Index is unchecked; arithmetic wraps. Division traps do
not prevent negative denominator after adding six wraps. Technology zero returns
9999 early; -1 skips prerequisites but retains gates/multiplier.

The selected ordinary setup path can copy difficulty into `0x82FFE7C8`, with
separate setup overrides and retention limits recorded in the
[village reward finding](../../manifests/friendly-village-rewards.json#/settlersDifficultyBoundary).
Multiplier/game-speed meanings and runtime cost remain unproved. Exact domains:
[cost manifest](../../manifests/technology-research-cost.json).

## Spaceship launch result

The selected launch dialog returns a signed arrival year or -1. Its caller
admits only positive results, excluding valid BC dates and year zero before
that producer submits the launch. The selected arrival evaluator accepts the
signed date domain, with separate state and victory gates.

The [arrival-year boundary](../../manifests/spaceship-launch-arrival-year-boundary.json)
records the field chain, native cancellation sentinel and a proposed
`result != -1` admission contract. This is a static correction contract;
actual dialog retention, launch delivery and repaired victory remain unobserved.

## Spaceship part presentation

Part completion and its later pending-part processing are gameplay work.
The selected consumer increments a component count at `0x82D1DE04`, then
can request a foreign-owner advisor notice at `0x82D1DEBC`. Its unused result
and native cleanup at `0x82CE87A8` supply a conditional notice-filter boundary.
That cleanup clears the caller's presentation bit and returns through the
matching frame; a bare return is not equivalent.

Both owner-equality and foreign-notice paths then request a type24 logical
unit at `0x82D1DED8`. A successful slot gets marker0 at unit+0x22 and sets
`0x82FFE7C4` bit0x02000000. The caller pumps application work until that bit
clears or the pump returns zero, requests retirement, then resumes the later
spaceship handling. Exact allocation failure instead rejoins at
`0x82D1DF60` before starting this actor/wait.

The selected type24 updater calls `0x82D5E660`, which publishes focus inputs
at `0x82D5E778/780`, sets a separate focus flag and requests selector37.
Native completion stores marker0xFFFF at `0x82D5E898`, publishes a float
constant, requests selector14 and invokes object/child completion callbacks.
The inactive0xFFFF arm returns earlier and omits that completion work;
forcing an active marker or globally clearing busy is not equivalent.

This supplies a separate world-actor boundary. It does not prove a safe
per-player refusal: creation uses a real unit bank, retirement can affect
linked records, and actual child/media/input/audio/camera and peer/save
consumers remain qualified. The pre-advisor helper also changes selected
visibility/discovery state and must not be removed as a camera-only shortcut.

Creation omission does not reproduce every logical record byte at immediate
`0x82D1DF60`: mode0 retirement marks the row and retains its owner, while
omission leaves the free row unchanged. Selected native save field requests
include its owner and lifecycle word; actual saved bytes and timing remain
separate. Camera-only suppression leaves the busy wait. A late branch from
the initialized comparison at `0x82D5E868` to `0x82D5E888` reaches native
marker/selector14/object completion requests, but follows the focus work and
can change queued-input consumption. This is a conditional control-flow
boundary, not proof of no camera pull, zero wait or per-peer safety.

The initialized child selector writes state+0x6C; normal finish then requests
manager cleanup. A separate native current-data scalar ignores marker+0x22
but excludes dead-bit rows, so earlier retirement can change its result if a
snapshot falls between retirements. Native save transfer also requests that
marker. Queue event ingress and a later consumer are bound, but skipped pops
and actual reader order remain distinct. These facts narrow the remaining
camera/input, save and MP proof; they do not establish a local-only setting.

The constructed view table selects `0x82E0E4B8`; its zero-delta update still
publishes transforms. Under retained frame/interface/recipient mappings, input
dispatch precedes the same actor updater and possible queue pop. One AI-turn
snapshot at `0x82CDE8B8` follows returned actor retirement. A separate admitted
pre-update drain can reach command55's snapshot at `0x82CDEC64` inside the pump.
The two phases must stay distinct when assessing differing player preferences.

The selected output corridor writes a 16-float matrix and can sequentially
publish three words through view+0xA0; actual destination/engine use and current
child/list effects remain open. The drain info byte has an initial zero writer
and selected setter `0x82CA4A18` (child virtual+0x10), writing incoming r4's low
byte through the same info getter. Its actual incoming value and order before
the drain read remain unproved.

The shared spaceship screen also returns launch results. Positive results
from its automatic callers can request command32 at `0x82D1DFA4` or
`0x82D1E000`. Refusing the whole screen or pending-part branch can therefore
alter gameplay. Arrival presentation uses another wrapper of the same class.
The [part-presentation boundary](../../manifests/spaceship-part-presentation-boundary.json)
owns exact sites, field/result separation and the remaining completion,
media, local-peer and lifecycle qualifications.

## Evidence sources

- [Technology research cost](../../manifests/technology-research-cost.json)
- [First-discovery rewards](../../manifests/technology-first-discovery-rewards.json)
- [Science completion](../../manifests/science-completion.json)
- [Spaceship launch arrival year](../../manifests/spaceship-launch-arrival-year-boundary.json)
- [Starting technology grants](../../manifests/starting-technology-grants.json)
- [City yield state credits](../../manifests/city-yield-state-credit.json)
