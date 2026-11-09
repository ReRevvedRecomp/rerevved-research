# Building and Wonder storage limits

This page answers one question for modders: can I add a Building or a Wonder?
The short answer is that adding a record to a table is not enough. The code
that lists, claims and completes each kind has its own fixed limits, and those
limits must be changed together. The limits below are static facts about
selected paths. They do not prove that every other path rejects a new item, and
no new Building or Wonder was tried in the running game.

| Question | Verdict |
|---|---|
| Can the production option list carry more Buildings? | Locally constrained. The list append has a capacity check, but its growth path and the 100 word source tail are not fully understood. |
| Can I add a Building record after item 122? | No spare space. The next record position overlaps data that is not a record. |
| Can the Wonder menu offer a 34th Wonder? | No. The menu loop, the claim helper and the claim table all stop at 33 slots. |
| Do initialized Wonder items 233 through 236 appear in the menu? | No. They lie outside the loop and the helper range. |
| Does the eligibility check stop a high item ID? | It has no upper ID check, so it cannot be relied on to reject or accept one safely. |

## Buildings

### Item IDs and records

Building definitions are items 100 through 122: 23 records at `0x82F71FD8`, each
`0xCC` bytes. Item 122 ends at `0x82F7322B`. The next 12 bytes
(`0x82F7322C..0x82F73237`) hold data that is not a record, and the Wonder table
starts at `0x82F73238`. A record for a hypothetical item 123 would start inside
that data, so the next stride position is not spare storage.

The cost helper accepts IDs 100 through 199. That is the range it computes
for, not a list of valid definitions, and it must not be read as room for 77
more Buildings. See [Unit definitions](unit-definitions.md) for the cost
helpers.

### Completion

When a city has enough production, the completion helper `0x82D02090` is called
with the city and the item ID minus 100. The call is at `0x82D16158`;
`0x82D16154` prepares its argument, so a hook belongs at the call address, not
the preparation. It writes the completion state:

- For indices 19 through 22 (the spaceship parts, items 119 through 122) it
  takes a separate path. It ORs bit `0x100` into city word `+0x24` only when the
  word at `0x830ECC0C + 8 * owner` equals -1, and it skips the building bit
  writes.
- For other indices it reads the player era word `0x830ECD08 + 4 * owner`,
  limits it to 0 through 3, and ORs `1 << index` into city word `+0x10` and into
  word `+0x14 + 4 * era`. It then calls `0x82D00C78`.
- Both paths store `100 + index` at city `+0x3A`.
- The helper checks the 28 signed bytes at city `+0x87` through `+0xA2`. If a
  byte equals the index it returns. If it first finds a zero it writes the index
  there and returns. It stops after 28 bytes.

The helper has no independent upper check on the item ID. Do not treat its shifts
or its list as a contract for new IDs. Room in the option list would not give a
valid new ID or a completion slot.

### The production option list

The option wrapper for Buildings (mode 2) copies a fixed tail of 100 words. It
passes a byte count based on `100 - k`, where `k` is the number of leading
negative words, and it returns the visible count `n - k` separately. It never
checks that `n` is at most 100.

The list then goes to the append helper `0x822D10C0`, called at `0x82DFF360` on
the descriptor at child `+0x430`. The descriptor holds a begin pointer (child
`+0x434`), an end pointer (`+0x438`) and a capacity end (`+0x43C`):

- With a nonzero begin pointer and a size below the capacity, it writes one 4
  byte entry at the end and moves the end forward by 4. This path makes no
  allocation call and has no 100 entry limit.
- With a zero begin pointer or a full descriptor, it calls `0x822D1150` at
  `0x822D113C`, and no local check follows that call.

What `0x822D1150` does when the list is full is not known: its growth policy,
its allocation, what it does on failure and how long the descriptor lives (the
reset at `0x821C6C28`) are not inspected. The absence of a 100 entry check does
not show that the native generator ever returns more than 100.

**Verdict:** locally constrained, with the complete transport capacity
unresolved.

## Wonders

### Thirty three claim slots

Wonder claims are stored at `0x830E5148`, 33 slots of 8 bytes (owner, then
city), ending at `0x830E5250`. Normalized index `i` is item `200 + i`, so the
table covers items 200 through 232. Three pieces use that same range:

- The menu generator `0x82CE2FD0` walks the 33 slots at `0x82CE3034..0x82CE3068`.
  It tests a slot only when its first word is -1, calls the eligibility helper
  `0x82CF3608` with index 0 through 32 and the owner byte, and appends
  `index + 200` when the helper returns nonzero. It returns the appended count,
  so it can offer items 200 through 232 only.
- The claim helper `0x82D16BA0` rejects an index below 0 at `0x82D16BC8` and an
  index of 33 or more at `0x82D16BD8`. Its mode 1 write stores the owner at
  `0x82D16C08` and the city at `0x82D16C10` in the same 8 byte slots.
- The reset at `0x82D060C4..0x82D060D4` fills 0x108 bytes with 0xFF, which is
  exactly the 33 slots.

Example: to add a Wonder as item 233 you would need all three to change
together. The menu loop would have to run to index 33, the helper would have to
accept index 33 and the table would need room for a 34th slot, which the
adjacent memory at `0x830E5250` does not provide. A new item that skips one of
these three pieces cannot be both offered and claimed.

**Verdict:** locally constrained. An extra distinct slot needs the menu limit,
the helper limit and the table extended together.

### Definitions go further than the menu

Wonder records are `0x14C` bytes each at `0x82F73238`, and they are initialized
through item 236, which is 37 records. Items 233 through 236 exist in the table
but lie outside the menu loop and outside the helper's range at the production
call site. The 12 stride positions for items 237 through 248
(`0x82F76234..0x82F771C3`) are all zero bytes, and the next position at
`0x82F771C4` holds different data that does not match a Wonder record.

Zero bytes after item 236 are not a promise of spare storage. They also do not
show that the table ends there or that other paths reject those IDs.

### Eligibility

The eligibility helper `0x82CF3608` has no upper ID check. Its generic branch
computes `0x82F73238 + index * 0x14C` with no bounds test and reads signed
halfwords at `+0x44`, `+0x46` and `+0x48` as technology IDs or -1. Indices 19
and 20 take separate branches. These technology checks are separate from the
menu loop and from the claim bounds, so passing the check proves nothing about
the other two.

### The serializer

`RVA-SYM-0333`, `BroadGameStateSerializer` at `0x82CC4040`, transfers many state
blocks. Its identity alone does not show that it transfers Wonder claims. The
claim paths it contains, a reset of 33 slots and a copy of 21 paired words, are
in [Stonehenge and Library effects](stonehenge-and-library-effects.md#wonder-claims-and-completion).

## What this does not show

- Items outside the menu are not shown to be globally invalid. Other paths may
  accept them.
- No save format, effect, presentation or multiplayer behavior for new content
  was examined.
- The growth path behind `0x822D1150` was not read.

## Evidence

[building-option-copy-capacity.json](../../manifests/building-option-copy-capacity.json),
[building-option-append-capacity.json](../../manifests/building-option-append-capacity.json),
[building-record-identities-100-122.json](../../manifests/building-record-identities-100-122.json),
[building-completion-state-writer.json](../../manifests/building-completion-state-writer.json),
[city-production.json](../../manifests/city-production.json) (`#/findings/RVA-F-0185/wonderChoice`),
[wonder-claim-slot-state.json](../../manifests/wonder-claim-slot-state.json),
[wonder-post-threshold-helper.json](../../manifests/wonder-post-threshold-helper.json),
[wonder-outer-check-record-fields.json](../../manifests/wonder-outer-check-record-fields.json),
[wonder-records.json](../../manifests/wonder-records.json) (`#/findings/RVA-F-0165`)
and the summary in
[building-wonder-storage-limits.json](../../manifests/building-wonder-storage-limits.json).
