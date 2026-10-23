# Evidence model

Retail guest data is authoritative; Ghidra, generated C++, runtime logs and
external sources interpret it, without independently proving correctness.

Promoted findings need:

- Image SHA-256 or its manifest reference.
- Exact addresses/offsets and the narrow supported claim.
- Confidence: `confirmed`, `strong`, `candidate`, or `rejected`.
- Static/dynamic locators for behavioral claims.
- Unresolved alternatives or falsification conditions.

Evidence terms: "accepted" means supported within recorded scope; "selected"
identifies inspected paths, not exhaustive coverage. Bounded negatives exclude
only tested forms. Preserve claim-specific guards, unknowns and runtime limits.

Keep raw decompilation local; publish names, addresses, signatures, layouts,
call edges and short summaries. Consumers explicitly adopt/copy findings;
sibling builds must not depend on this repository.

Keep retail descriptions/help/format strings, full selection tables/lossless
membership, native-code slices and complete operands local. Publish locators,
counts, lengths, digests and independent summaries. Text digests identify only
recorded bytes, not an unrecorded terminator or original encoding.
