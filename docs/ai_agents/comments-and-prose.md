# Comments and prose

Default to deleting explanatory comments. Retain non-obvious guest locators,
ABI/layout constraints, safety/tool/generated-output boundaries or provenance
that names/types cannot convey. Prefer one to three lines at use; clarity,
correctness, quotations, licensing and provenance may need more. Remove process
narration and restated instructions.

Preserve source/reference/permission/provenance citations verbatim, plus finding
addresses, offsets, hashes, symbols, confidence and uncertainty. Runtime
strings, help, catalog fields, metadata and test labels are behavior/data. Edit
generated output only through its generator/canonical input.

## Reference prose

- Use ASCII, short declarative sentences and ordinary noun phrases; retain
  established technical hyphens, avoiding invented modifier chains.
- Prefer periods, commas or lists; use semicolons only when clearer.
- Use ordinary Civilization Revolution and game terms for established behavior.
  Describe what setup and the first turn do in natural language. Keep technical
  terms where they identify code, storage or network behavior precisely; do not
  give unresolved fields or Xbox message cases invented gameplay meanings.
- Separate observation/interpretation; retain image, locator and tool where needed.
- State uncertainty; do not promote candidate names/behavior.
- Apply [contribution policy](README.md) to tracked Markdown/records.
- Reference pages describe settled behavior, without repeated image versions,
  probes, runs, captures, validation history or branch state. Keep evidence
  mechanics in manifests and private operations outside reference pages.
- Exclude editorial/status/progress dates; retain source-citation dates and
  explicit observation/capture metadata identifying or bounding evidence.

## Writing reference pages

Reference pages are written for modders first. Open with what the system does
in game terms, with a worked example where one helps. Follow with how the code
does it, then addresses, limits and open questions.

- Write numbers apart from words: `at most 15`, `turn 20`, `strict 2x`.
  Identifiers in backticks keep their spelling (`arg1`, `low32`).
- Use at most one hyphen in a compound unless it is an established term such
  as `read-only` or `byte-for-byte`. Rewrite longer chains as a phrase.
- Do not chain words with slashes in prose. Write `repair during setup and
  loading`, not `setup/load repair`. Slashes stay in paths, ratios and code.
- Do not write `ordinary` to mean the normal case. Name the special case
  instead, or drop the word: `combat`, not `ordinary combat`.
- Write game concepts by their name in title case, for example `First
  Discovery bonus` and `Unique Abilities`. Otherwise use plain words without a
  hyphen: `the first code that reads the field`, not `first-reader`.
- Use plain words for analysis shorthand:

  | Avoid | Write instead |
  |---|---|
  | gate, gates | requirement, check, or the condition itself |
  | bind, binds, bound (as a verb) | shows, confirms, ties X to Y |
  | bounded | limited to, and state the limit |
  | closure | the full set of callers or paths |
  | join, joins | link, or which code connects X to Y |
  | frontier | open question, unexplored callers |
  | admission, admits | accepts, allows |
  | retention | whether X stays valid or unchanged |
  | ingress | entry point |
  | seam | hook point |
  | owner, owns (of code or data) | the function that writes or uses it, or its name; keep owner for the player who owns a city or unit |
  | generated body, chunk | the recompiled copy of the function |
  | conditional | the condition itself, or `only when` |
  | packet (outside network messages) | omit |
  | theorem, witness, corridor | proof, example, code path |

Terms that stay are defined in the [glossary](../glossary.md).
