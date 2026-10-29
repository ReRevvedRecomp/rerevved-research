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

## AI production and launch policy

The [AI nuclear finding](../../manifests/ai-nuclear-weapon-gates.json)
separates ordinary unit production, acquisition through the Manhattan Project and
autonomous launch. These are static boundaries; a natural AI acquisition-to-launch
chain has not been observed.

Ordinary production of an ICBM (unit type 27) is rejected by the shared human/AI
candidate list. Its initialized prerequisite tuple is `[0,0,0]`: the required
first query returns zero and rejects it at `0x82CEC6A0`. A separate nuclear-flag
test rejects it at `0x82CEC7BC`. Changing only that flag test leaves the first
rejection intact. This does not establish an AI-only mask or zero valuation.

The Manhattan Project (item 218) provides a separate acquisition path. Its
accepted native requirement is Atomic Theory (technology 37). The AI evaluator
can append eligible Wonder IDs. A priority gate and the strategy 0/3 category
gate can give the Manhattan Project a score of 0, but that does not remove the
candidate: a valid random fallback can still select it. Actual competing scores,
the selected ordinal and assignment remain conditions.

After completion publishes the pending reward, Calendar reloads the correct
city ordinal at `0x82D1D84C` and requests mode 2 at `0x82D1DD54`. With its zero
fourth argument, equality of current turn `0x8312B8DC` and the start-turn word
`0x8312B8D8` clears mode 2 at `0x82D16C64`. The selected helper returns before
creation, while the caller still clears the pending flag at `0x82D1DD60`.
This shared, conditional suppression is not a demonstrated failure at a natural
AI completion. Otherwise, the terminal index 18 arm can request creation of
unit type 27 at `0x82D177A8`, subject to required service/helper returns,
creator success and retained city/unit state.

The mode 2 service path compares the city owner with a current-context player,
without establishing that either is human. Its two notification routes call
advisor show at `0x82D17470` or `0x82D1775C`. Normal returned values, including
an early-out result, are discarded before the grant paths merge. They do not
veto the reward locally. Every taken formatter, service, advisor and callback
must still return with the city, owner, index and saved state retained.

The ordinary creator needs a slot whose owner byte and byte+7 are both 0xFF.
Exhaustion returns -1; slot 0 is valid. A nonnegative result alone does not
establish a retained unit object: the accepted object-rejection route stores
zero to unit+0x3C before a possible normal return. Successful publication at
`0x82D8029C` instead links the object there, subject to allocation, model
acceptance, registration and lifetime conditions. This distinction does not
prove that every logical-unit path requires that object pointer.

The initialized ICBM movement value is 40. With matching returned/captured
owner, a valid slot and retained type 27/definition, the Manhattan Project
rewrites the movement value to 120 at `0x82D177F0`, then requests recount at
`0x82D177FC`. It does not validate those record/object premises before the
write. No zero-movement or selected human-only grant exclusion was found;
actual retained AI receipt remains unobserved.

An AI-owned nuclear unit has a dedicated decision arm at `0x82CBF570`.
It rejects Democracy (government 4), self, Barbarians and nonwar pairs.
It also requires reverse pair-history bit 0x20. A selected city-capture
producer can set that bit through the following accumulated chain. For AI
player p and opponent q, the relevant word is
`H(q,p)=U32[0x830ED0D8+4*(8*q+p)]`.

| Step | Selected condition and writer |
|---|---|
| 0x8 | Wording about backing by nuclear weapons requires a nonzero count of unit type 27 for p; the negotiation suffix stores `H(q,p)\|0x8` at `0x82CC9DFC`. |
| 0x10 | A later positive negotiation response must avoid retry, have q outside Democracy (government 4), no active kind 1 commitment, a zero Great Wall predicate for p and no taken special-choice alternative. `0x82CCEEC8` adds 0x10 only if sampled 0x8 was already set, then the path requests war relation 0. |
| 0x20 | q subsequently takes a p-owned city. `0x82D1B474` adds 0x20 only if that same word already had 0x10. |

The count is the type 27 cell of the per-type unit-record tally at
`0x830E4628+152*p+108`, distinct from the post-use count at `0x830ECBC4`.
A checked caller can supply the same ordered pair to both negotiation owners;
actual context identity, a positive UI choice, helper returns and history
retention remain conditions. Nonhuman p is locally compatible. A prior missile,
matching negotiation and later city loss therefore provide a concrete selected
route to launch eligibility. q's Democracy blocks this selected history step
independently of p's Democracy launch exclusion. This does not prove natural
reachability, unique writers or the original flag names. Being at war alone
is insufficient.

The arm chooses the last qualifying opponent, then its largest visible city
with population greater than 6. It does not retry earlier opponents if that
one lacks a qualifying city. A conditional local route stages Move 17 and calls
the existing command ring at `0x82CBF880`; the alternate session route has
separate delivery gates. A return value or staged record is not a launch
receipt.

The manifest's conditional title contract separates an AI-only production
admission seam at `0x82CEC67C` from a launch-history relaxation at
`0x82CBF668`. Under their explicit identity, policy, retention and return
premises, they preserve the existing human path and later SDI and presentation
behavior. No single shared flag patch or runtime-safe implementation is
established. Multiplayer authority, saved policy/actions, peace/UN interactions
and nuclear-use counter consumers retain their own acceptance requirements.

The finding's `counterConsumerBoundary` resolves one contact-policy effect of
the post-use word at `0x830ECBC4`. A fresh nonzero sample for the contact
handler's normalized participant p forces its local policy flag to one at
`0x82CD00E8..EC`. This can affect a conditional later selection and war request;
the counter is not merely used for wording. A subsequent equal-halfword test
can clear the flag, and later relation, selection, helper and delivery gates
still apply.

The finding's `actorNormalizationBoundary` binds one named ordinary-AI
ingress through the wrapper and handler. Three ordered swaps determine p.
Under retained equal resolver samples, p is the second original participant
only when that resolver value equals that participant; otherwise p is the
original actor. In particular, a stable value outside both participants makes
the wrapper and handler reversals cancel. Applying the handler-only rule to
the original request would give the wrong attribution in that case.

Changing resolver samples can change which participant's counter is read.
Preserve the wrapper and handler normalization, counter and later policy
gates. Actual launcher equality, current resolver values, admitted contact and
same-generation retention remain observation requirements. Natural nuclear
use, that matching contact, save retention and peer authority remain unobserved.

The finding's `counterResetBoundary` binds a conditional zero baseline.
`0x82D05D60` assigns r29=0; the selected interval has no other explicit r29
writer. All taken calls and current context must preserve full r29 and the
required frame. On reaching `0x82D061D8..E0`, eight completing stores clear
`[0x830ECBC4,0x830ECBE4)` with no local human/AI test. This does not prove
natural reset timing, complete owner return, later zero retention or save/load
delivery. `counterTransferBoundary` binds mode1 input at `0x82CC587C`
through `0x822DE4F0`; mode0 at `0x82CC58A0` is output. The eight-word loops
ignore individual reports and do not retry or aggregate success. The scalar
reader can reverse a mixture of delivered and retained bytes after a short
request. An admitted missing-child case returns normally after eight
zero-delivery requests, preserving all old words under its explicit conditions.
childReadDeliveryBoundary below owns that selected child read and the current
service+0x10 destination-byte frontier.
Actual nuclear actor/resolver observation remains parked.

The finding's `childReadDeliveryBoundary` binds selected default child
`0x82D38448` through `0x82D38360` and synchronous wrapper `0x8280F3F0`.
Missing handle or a nonzero current predicate returns0; an alternate stream
uses its own current target. On the default route, EOF status0xC0000011 is
normal Boolean success with count0. Short input can report2; a selected
failure can advance the child's count while returning0. None guarantees
four-byte delivery. Eight EOF requests can retain all old history words under
the explicit endian, nonaliasing and ABI conditions.

Destination-byte effects stop at current service root+0x10. The queried
initial root is0x82F2FA9C, whose corresponding cell0x82F2FAAC selects the
NtReadFile import identified below; actual current mapping and imported
completion remain premises.
The192-word packet has189 instructions and three cells. Thirteen supplied
cases, three eight-request sequences and four mutation controls passed;
no natural input or save round trip was observed.

## Initial synchronous import

`RVA-F-0363/initialServiceImportBoundary` binds initial cell0x82F2FAAC to
0x82E92ED4, registered as `__imp__NtReadFile`. Its leading import tags are
opaque data, with encoded mtctr/bctr tail words; there is no selected generated
guest read implementation. The19-word packet has13 instruction words,
four data/opaque words and two neighbors, all pinned-image equal.

The accepted wrapper forwards H/D/N and the protected per-request result
home. Its pending/wait, EOF/count0 and short-read reporting do not establish
destination-byte delivery. The actual retained import provider's widths,
write extent, result production and completed pending request remain the next
contract. Current root/table/provider identity, handle/frame lifetime and
alias retention remain conditions. Actor/resolver observation remains parked.
