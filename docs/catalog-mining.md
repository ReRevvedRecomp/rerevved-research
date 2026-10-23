# Catalog mining method

Mining answers a bounded guest-code question. Topic manifests retain evidence;
catalogs retain reusable symbols, layouts, vtables, slots and explicit
relations. Formats/tools: [topic manifests](topic-manifests.md),
[catalogs](catalogs.md), [headless workflow](workflow.md).

## Investigation scope

Define one falsifiable question, exact seeds and minimum reads. Expand at most
eight direct callers/callees, fewer where appropriate. Prefer one foreground
read-only query with related seeds; identify exact functions before generated
corroboration. Instructions, decompilation, reports and logs stay ignored
scratch.

Stop on image mismatch, lock, unresolved dispatch/writer, exceeded fan-out or
required runtime evidence. Negative results record premise, read set, result and
remaining alternatives.

## Recording results

1. Confirm `manifests/image.json` identity.
2. Record one bounded finding in a topic manifest.
3. Promote reusable entities/explicit relations only; proximity, shape and
   endpoint evidence do not prove an edge.
4. Allocate under [Catalog contract](catalogs.md), preserving IDs/reservations.
5. Record locators, confidence, qualifications, guards and alternative/falsifier.
6. Delete scratch after facts have a canonical home.

Static evidence supports static claims; behavior requires independently
reviewable runtime observation.
