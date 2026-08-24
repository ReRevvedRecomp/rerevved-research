# Catalog mining method

Catalog mining turns a bounded guest-code question into a supported finding
and, when reusable, catalog records. Topic manifests retain investigation
evidence. The catalogs retain reusable symbols, layouts, vtables, slots, and
explicit relations.

See the [topic manifest contract](topic-manifests.md), the
[catalog contract](catalogs.md), and the [headless workflow](workflow.md) for
their file formats and tools.

## Investigation scope

Before inspection, define one falsifiable question, exact guest-code seeds, and
the smallest read set that can answer it. Limit direct caller or callee expansion
to eight exact functions unless a smaller bound is appropriate.

Use one foreground read-only Ghidra query when possible. Batch related seeds in
that query, and consult generated code only after identifying an exact function.
Raw instructions, decompiler output, query reports, and logs remain ignored
scratch.

Stop when the image does not match, the project is locked, dispatch cannot be
resolved, fan-out exceeds the declared bound, a required writer is unknown, or
the claim needs runtime evidence. A bounded negative is useful when it records
the tested premise, exact read set, result, and remaining alternatives.

## Recording results

1. Confirm the image identity in `manifests/image.json`.
2. Record a new bounded finding in one topic manifest.
3. Add catalog records only for reusable supported entities and explicit
   relations. Address proximity, matching shapes, and endpoint evidence do not
   establish an edge.
4. Allocate catalog IDs under [Catalog contract](catalogs.md). Preserve existing
   IDs and reserved ranges.
5. Record evidence locators, confidence, qualifications, guards, and a remaining
   alternative or falsification condition.
6. Delete scratch after the supported facts have a canonical home.

Static evidence supports static claims. Behavioral claims require an
independently reviewable runtime observation.
