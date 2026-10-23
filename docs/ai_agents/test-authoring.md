# Test authoring

Use the cheapest check that catches the defect, accounting for fixture cost
and repeated setup.

## When to add a test

- A demonstrated defect needs the smallest input that fails without the fix.
- A parser, validator, exporter, or driver adds an uncovered branch, byte
  layout, output contract, or failure path.
- Evidence identity, JSON Pointers, ordering, or query bounds affect a result.
- A writer or child process can fail. Check failure reporting, partial output,
  and caller-owned cleanup or environment restoration.

## When not to add a test

- Another test covers the same branch and assertions.
- Only a catalog row changes. Check rows together in a data test.
- Expected results come from the tested function, or a copied algorithm
  substitutes for production code.
- An earlier guard rejects the fixture. Start from valid input and assert
  the intended diagnostic.
- The assertion only pins source spelling or editorial prose.
- The check only enforces repository shape. Extend
  [the verification gate](../../tools/verify.ps1) for links, ASCII,
  script indexing, syntax, and forbidden tracked paths.

## Choose a fixture

Use the first level that detects the defect:

1. Literal bytes or values passed to production helpers, as in
   [AVM1 tests](../../tests/test_inspect_gfx_avm1.py).
2. Small dictionaries from `sample_documents()` in
   [catalog tests](../../tests/test_catalog_validator.py), or `function()`,
   `program()`, and `report()` in
   [matcher tests](../../tests/test_match_version_functions.py).
3. A data test that loads authored records once and checks independent
   expected identities, offsets, or relations. See
   [topic manifest tests](../../tests/test_topic_manifests.py).
4. Temporary files for actual CSV, JSONL, or binary file behavior. Copy only
   the inputs needed, as appropriate to
   [reference data tests](../../tests/test_reference_data.py).
5. A PowerShell process using the fake headless executable in
   [driver tests](../../tests/test_run_headless.py), or `-Plan` in
   [bootstrap tests](../../tests/test_ghidra_bootstrap.py).
6. The JDK writer harness in
   [query tests](../../tests/test_ghidra_query_writes.py).
7. The same file's `OWNER_CALL_FIXTURE` with Ghidra API classes when the
   behavior needs functions, instructions, or register objects.

## Products and matrices

Load every authored row once. Keep literal expected addresses, IDs, widths,
and field order that specify evidence contracts. Schemas prove shape, not
guest facts.

Choose cases by branch: raw/swapped shader bytes, nested action scopes,
bounded/overflowing candidate pools, or distinct path guards. Label cases with
`self.subTest`; do not repeat every fault per row. Keep write, flush, and close
failures separate because they occur at different points. Explain lost
coverage when reducing a matrix.

## Scaffolding

Reuse family helpers: `long_action()`,
`sample_documents()`, matcher record builders, and `observations()` in
[attestation tests](../../tests/test_canonical_image_evidence.py).
[java_test_support.py](../../tests/java_test_support.py) shares Java fixture
compilation, execution, and source extraction across families. Share repeated
mechanics as needed; keep expected values in the owning test.

Load immutable baselines in `setUpClass` and copy before mutation. Create only
needed temporary directories; register cleanup at creation to cover setup
failures. Source searches check wiring, not query behavior.

## Ghidra queries and verification

Use synthetic test inputs. Follow the [headless workflow](../workflow.md) for
queries and disposable repairs. Test or Ghidra success is not runtime evidence;
preserve the [evidence model](../evidence-model.md) limits. Test output failure
before accepting a success marker.

Keep partial output for diagnosis per the [Ghidra script
contract](../../ghidra/README.md).

Run from the repository root:

```powershell
python -B -m unittest discover -s tests -p test_inspect_gfx_avm1.py
python -B -m unittest discover -s tests -p 'test_*.py'
powershell -NoProfile -File tools\verify.ps1
```

Full discovery needs a JDK and `pwsh`. Ghidra API fixtures can skip when
`REREVVED_GHIDRA_HOME` is unset. Report skips; do not count them as proof.
[Verification](../style-guide.md#verification) owns dependencies and gate checks.
