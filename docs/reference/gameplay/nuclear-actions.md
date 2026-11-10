# Nuclear action boundaries

A nuclear action has separate command, gameplay-state and presentation stages.
The selected Move branch can consume the missile after interception or after a
damage-helper call. Neither a disappearing unit nor an invisible explosion
alone identifies a defect.

The [command finding](../../../manifests/nuclear-action-boundaries.json#/findings/RVA-F-0333)
ties these static edges to code in the supported image. No nuclear action was
observed at runtime for this finding.

```text
Move17 -> definition flag0x20000 (initialized ICBM27)
       -> target split and helper -> mode word
          zero -> queued state -> SDI scan -> presentation request and wait
               -> no selected SDI: damage helper
               -> both local outcomes: mode0 missile kill
          nonzero -> separate helper and effect request and poll prefix
                     ... completion and consumption not linked
```

The zero-mode SDI scan checks tile and city state at the target and at eight
offsets taken from a table. The tested city bit comes from the writer for the
SDI Defense building. A selected interception skips the local damage call and
formats an advisor message. Its delivery and display are separate facts. The
damage helper has its own SDI recheck before the later population and unit
damage paths, and the scan can itself update tile state. Reaching that helper
does not show that damage occurred.

The wait can end when the presentation flags clear or when the pump returns
false. It does not show a completed missile animation. The later mode0 kill
marks the addressed unit dead and clears its link field under the accepted
unit-kill contract. The required returns and the inputs that stay valid still
matter. The prefix of the alternate mode uses different virtual request and poll
slots. The zero-mode result must not be applied to it.

## Presentation anchors and missing link

The [presentation finding](../../../manifests/nuclear-action-boundaries.json#/findings/RVA-F-0334)
identifies a request for the nuclear crater effect file, the sites of the
suppression labels and the preparation of the name handle for the nuclear
exposure parameter. It does not identify the active parameter value, a
successful asset load, the missile model, every explosion pass or a rendered
effect instance. A crater name is not a complete visual lifecycle.

A useful observation records the actor, the unit, the command target and the
mode. It then compares the missile, SDI, city population and victim records
before and after the same event. If gameplay completes correctly but the pixels
fail, link the actual presentation target to its creation, update, render and
destruction. Follow its draw and resource identity through D3D submission,
resolve and presentation. If the state differs, establish the first missing or
incorrect command or state edge before a graphics repair. Save persistence is
another acceptance step.

The [Move lifecycle](../../../manifests/unit-movement-lifecycle.json) and the
[scene lifecycle](../rendering/scene-render-lifecycle.md) supply adjacent contracts. Their
observed or static coverage does not establish this nuclear link.

## AI production and launch policy

The [AI nuclear finding](../../../manifests/ai-nuclear-weapon-requirements.json)
separates three things: unit production, acquisition through the Manhattan
Project and autonomous launch. These are static boundaries. A natural AI chain
from acquisition to launch has not been observed.

The candidate list shared by human and AI players rejects production of an ICBM
(unit type 27). Its initialized prerequisite tuple is `[0,0,0]`. The first
required query returns zero and rejects it at `0x82CEC6A0`. A separate nuclear
flag test rejects it at `0x82CEC7BC`. Changing only that flag test leaves the
first rejection intact. This does not establish an AI-only mask or a zero
valuation.

The Manhattan Project (item 218) provides a separate acquisition path. Its
accepted native requirement is Atomic Theory (technology 37). The AI evaluator
can append eligible Wonder IDs. A priority check and the category check for
strategies 0 and 3 can give the Manhattan Project a score of 0, but that does
not remove the candidate. A valid random fallback can still select it. The
actual competing scores, the selected ordinal and the assignment remain
conditions.

After completion publishes the pending reward, the Calendar reloads the correct
city ordinal at `0x82D1D84C` and requests mode 2 at `0x82D1DD54`. The fourth
argument is zero. When the current turn `0x8312B8DC` equals the start-turn word
`0x8312B8D8`, the request clears mode 2 at `0x82D16C64`. The selected helper
returns before creation, while the caller still clears the pending flag at
`0x82D1DD60`. This suppression is shared and applies only under that condition.
It is not a demonstrated failure at a natural AI completion. When the turns
differ, the terminal index 18 branch can request creation of unit type 27 at
`0x82D177A8`. That needs the required service and helper returns, a successful
creator and city and unit state that stays valid.

The mode 2 service path compares the city owner with a player from the current
context. It does not establish that either is human. Its two notification
routes call advisor show at `0x82D17470` or `0x82D1775C`. Normal returned
values, including the result of an early exit, are discarded before the grant
paths merge. They do not veto the reward locally. Every formatter, service,
advisor and callback that is taken must still return with the city, owner, index
and saved state unchanged.

The creator for a regular unit needs a slot whose owner byte and byte `+7` are
both `0xFF`. Exhaustion returns -1, and slot 0 is valid. A nonnegative result
alone does not establish a unit object that stays valid. The accepted route that
rejects the object stores zero to `unit+0x3C` before a possible normal return.
Successful publication at `0x82D8029C` instead links the object there, subject
to conditions on allocation, model acceptance, registration and lifetime. This
distinction does not show that every logical-unit path requires that object
pointer.

The initialized ICBM movement value is 40. Suppose the returned and captured
owners match, the slot is valid, and type 27 and its definition stay valid.
Then the Manhattan Project rewrites the movement value to 120 at `0x82D177F0`
and requests a recount at `0x82D177FC`. It does not validate those record and
object premises before the write. No zero-movement exclusion was found, and no
condition restricting the grant to human players was found. Whether an AI player actually
keeps the receipt is unobserved.

An AI-owned nuclear unit has a dedicated decision branch at `0x82CBF570`. It
rejects Democracy (government 4), itself, Barbarians and pairs that are not at
war. It also requires reverse pair-history bit `0x20`. A selected producer for
city capture can set that bit through the chain below, in which each step builds
on the one before. For AI player `p` and opponent `q`, the relevant word is
`H(q,p)=U32[0x830ED0D8+4*(8*q+p)]`.

| Step | Selected condition and writer |
|---|---|
| 0x8 | Wording about backing by nuclear weapons requires a nonzero count of unit type 27 for `p`. The negotiation suffix stores `H(q,p)\|0x8` at `0x82CC9DFC`. |
| 0x10 | A later positive negotiation response must avoid a retry, have `q` outside Democracy (government 4), have no active kind 1 commitment, have a zero Great Wall predicate for `p` and take no special-choice alternative. `0x82CCEEC8` adds 0x10 only if the sampled 0x8 was already set. The path then requests war relation 0. |
| 0x20 | `q` subsequently takes a city owned by `p`. `0x82D1B474` adds 0x20 only if that same word already had 0x10. |

The count is the type 27 cell of the per-type tally of unit records at
`0x830E4628+152*p+108`. It is distinct from the post-use count at `0x830ECBC4`.
A checked caller can supply the same ordered pair to both negotiation functions.
The actual context identity, a positive UI choice, the helper returns and
whether the history stays valid remain conditions. A player `p` who is not human
is locally compatible. A prior missile, a matching negotiation and a later city
loss therefore provide a concrete selected route to launch eligibility. The
Democracy of `q` blocks this selected history step independently of the
Democracy launch exclusion for `p`. This does not show that the route is
naturally reachable, that the writers are unique or what the original flag names
are. Being at war alone is not sufficient.

The branch chooses the last qualifying opponent, then that opponent's largest
visible city with a population above 6. It does not retry earlier opponents if
that one lacks a qualifying city. One local route stages Move 17 and calls the
existing command ring at `0x82CBF880`, under conditions. The alternate session
route has separate delivery checks. A return value or a staged record does not
show that a launch occurred.

The manifest's title contract, which holds only under conditions, separates two
changes. One is an AI-only production hook at `0x82CEC67C`. The other is a
relaxation of the launch history at `0x82CBF668`. Under their explicit identity,
policy, state and return premises, they preserve the existing human path and the
later SDI and presentation behavior. No single shared flag patch and no
runtime-safe implementation is established. Multiplayer authority, saved policy
and actions, peace and UN interactions, and the consumers of the nuclear-use
counter each keep their own acceptance requirements.

The finding's `counterConsumerBoundary` resolves one contact-policy effect of
the post-use word at `0x830ECBC4`. A fresh nonzero sample for the normalized
participant `p` of the contact handler forces its local policy flag to one at
`0x82CD00E8..EC`. This can affect a later selection and war request that depend
on conditions. The counter is not merely used for wording. A subsequent test of
equal halfwords can clear the flag, and the later checks of relation, selection,
helpers and delivery still apply.

The finding's `actorNormalizationBoundary` ties one named AI entry point, passing
through the wrapper and the handler, to code. Three ordered swaps determine `p`.
When the resolver samples stay equal, `p` is the second original participant
only when the resolver value equals that participant. Otherwise `p` is the
original actor. In particular, a stable value outside both participants makes
the reversals of the wrapper and the handler cancel. Applying the handler-only
rule to the original request would give the wrong attribution in that case.

Changing the resolver samples can change which participant's counter is read.
Preserve the normalization of the wrapper and the handler, the counter and the
later policy checks. Four things remain to be observed: the actual launcher
equality, the current resolver values, an accepted contact and the same
generation staying valid. Natural nuclear use, that matching contact, save
persistence and peer authority also remain unobserved.

The finding's `counterResetBoundary` ties a zero baseline, valid under
conditions, to code. `0x82D05D60` assigns `r29=0`, and the selected interval has
no other explicit `r29` writer. All calls that are taken and the current context
must preserve the full `r29` and the required frame. On reaching
`0x82D061D8..E0`, eight completing stores clear `[0x830ECBC4,0x830ECBE4)` with
no local test for a human or AI player. This does not show the timing of a
natural reset, a complete return by the writer, that zero stays in place later,
or delivery through save and load. `counterTransferBoundary` ties the mode1
input at `0x82CC587C` through `0x822DE4F0` to code. Mode0 at `0x82CC58A0` is
output. The loops over eight words ignore individual reports, and they do not
retry or aggregate success. The scalar reader can reverse a mixture of delivered
and unchanged bytes after a short request. A missing child case that is accepted
returns normally after eight requests that deliver nothing. It keeps all old
words under its explicit conditions. `childReadDeliveryBoundary` below records
that selected child read, and the remaining question of whether the destination
bytes are written through current `service+0x10`. Actual observation of the
nuclear actor and the resolver remains parked.

The finding's `childReadDeliveryBoundary` ties the selected default child
`0x82D38448`, through `0x82D38360`, and the synchronous wrapper `0x8280F3F0` to
code. A missing handle or a nonzero current predicate returns 0. An alternate
stream uses its own current target. On the default route, the EOF status
`0xC0000011` is a normal Boolean success with count 0. Short input can report 2.
A selected failure can advance the count of the child while returning 0. None of
these guarantees delivery of four bytes. Eight EOF requests can leave all old
history words unchanged, under a separate premise that nothing is written to the
destination and under the explicit endian, nonaliasing and ABI conditions. EOF
with count 0 alone does not show an untouched destination.

Effects on the destination bytes stop at the current `service root+0x10`. The
queried initial root is `0x82F2FA9C`, whose corresponding cell `0x82F2FAAC`
selects the NtReadFile import identified below. The actual current mapping and
the imported completion remain premises. The evidence set of 192 words has 189
instructions and three cells. Thirteen supplied cases, three sequences of eight
requests and four mutation controls passed. No natural input and no save round
trip was observed.

## Initial synchronous import

`RVA-F-0363/initialServiceImportBoundary` ties the initial cell `0x82F2FAAC` to
`0x82E92ED4`, registered as `__imp__NtReadFile`. Its leading import tags are
opaque data, with encoded `mtctr` and `bctr` tail words. No selected recompiled
guest read implementation exists. The evidence set of 19 words has 13
instruction words, four data or opaque words and two neighbors, all equal to the
pinned image.

The accepted wrapper forwards `H`, `D` and `N` and the protected per-request
result home. Its pending and wait handling, EOF with count 0, and reporting of a
short read do not establish delivery of the destination bytes. The pinned
hosted-source contract below narrows the argument widths and the production of
the result. The actual writes of the current provider and backend, the
completion, the lifetime of the handle and frame, and whether aliases stay valid
remain conditions. Observation of the actor and the resolver remains parked.

## Pinned hosted read-provider contract

`pinnedSdkReadProviderBoundary` records SDK
`d1fa31f7430706513dd6370f0967fd8ad4dd952f`, also declared by the selected title
lock. Its typed import consumes the low 32 bit destination `D` and the length
`N`. It invokes `XFile::Read` immediately and publishes the status and count
home. It can then return PENDING for a nonsynchronous file. That report path is
distinct from the actual destination write of the selected backend.

`XFile` passes an accepted mutable span of `n` bytes to the current
`File::ReadSync`. The selected generic source neither copies file bytes itself
nor establishes the concrete backend, the terminal completion or the accuracy of
the count. Its file event can be set after zero-length or locally rejected
reads. EOF forces a final information value of 0, which alone does not show that
earlier effects on the destination were absent.

Each of the eight counters still needs five things: the actual installed and
loaded provider; the `H`, object, backend, backing and position; the full
mapping and lifetime; accurate four-byte writes for the same request; and the
later state staying valid. This is a pinned hosted-source contract, with retail
semantics and the actual restoration kept separate.
