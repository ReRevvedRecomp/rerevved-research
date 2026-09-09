from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GHIDRA = REPO / "ghidra"
SCRATCH = REPO / "docs" / "ai_agents" / "local" / ".tmp" / "rerevved-ghidra"
SCRIPTS = (
    "DumpDataValues",
    "DumpFunctionNeighborhood",
    "DumpFunctionNeighborhoodBatch",
    "DumpInstructions",
    "DumpMemoryWords",
    "DumpReferences",
    "FindDirectCallers",
    "DumpStringsInRange",
    "ExportFunctionFingerprints",
    "FindCallConstantArgs",
    "FindCallSplitConstantArgs",
    "FindFieldAccesses",
    "FindFieldRefs",
    "FindGlobalAddressAccesses",
    "FindRawVtableSlotCalls",
    "FindVtableSlotCalls",
    "FindVtableSlotCallsCfg",
    "FindPointerValues",
    "FindScalarUses",
    "FindSplitConstantCandidates",
    "FindSplitConstantUses",
    "FindStrings",
)


def matching_brace(source: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise AssertionError("unmatched brace")


def production_lifecycle(source: str) -> tuple[str, str]:
    declaration_start = source.index("PrintWriter out = new PrintWriter(")
    declaration_end = source.index(";", declaration_start) + 1
    declaration = source[declaration_start:declaration_end]
    declaration = re.sub(r"new FileWriter\(outPath\)", "writer", declaration)
    declaration = re.sub(
        r"new OutputStreamWriter\(.*?StandardCharsets\.UTF_8\)",
        "writer",
        declaration,
        flags=re.DOTALL,
    )
    if "FileWriter(outPath)" in declaration or "OutputStreamWriter(" in declaration:
        raise AssertionError("failed to inject the test Writer into production source")

    check_start = source.index("if (out.checkError())", declaration_end)
    check_end = matching_brace(source, source.index("{", check_start))
    return declaration, source[check_start:check_end]


def harness_source() -> str:
    """Build a JDK-only fragment from each production writer lifecycle.

    The complete scripts require Ghidra classes, so this compiles only their
    actual resource declaration and post-close error check with a test Writer.
    """
    methods: list[str] = []
    for script in SCRIPTS:
        declaration, check_block = production_lifecycle(
            (GHIDRA / f"{script}.java").read_text(encoding="utf-8")
        )
        methods.append(
            textwrap.dedent(
                f"""
                    private static void run{script}(
                            Writer writer, String failure, boolean checkErrors) throws Exception {{
                        String outPath = "{script}";
                        {declaration}
                        try (out) {{
                            out.print("partial-output");
                            if ("flush".equals(failure)) {{
                                out.flush();
                            }}
                        }}
                        if (checkErrors) {{
                    {textwrap.indent(check_block.strip(), "            ")}
                        }}
                    }}
                """
            ).strip()
        )

    return textwrap.dedent(
        f"""
            import java.io.IOException;
            import java.io.PrintWriter;
            import java.io.Writer;
            import java.lang.reflect.InvocationTargetException;
            import java.lang.reflect.Method;

            public class GhidraQueryWriteHarness {{
                private static final String[] SCRIPTS = {{
                    {", ".join('"' + script + '"' for script in SCRIPTS)}
                }};

                private static final class FailingWriter extends Writer {{
                    private final String failure;
                    private final StringBuilder content = new StringBuilder();
                    private boolean writeFailed;

                    private FailingWriter(String failure) {{
                        this.failure = failure;
                    }}

                    @Override
                    public void write(char[] characters, int offset, int length)
                            throws IOException {{
                        if ("write".equals(failure) && !writeFailed) {{
                            writeFailed = true;
                            int partialLength = Math.max(1, length / 2);
                            content.append(characters, offset, partialLength);
                            throw new IOException("injected write failure");
                        }}
                        content.append(characters, offset, length);
                    }}

                    @Override
                    public void flush() throws IOException {{
                        if ("flush".equals(failure)) {{
                            throw new IOException("injected flush failure");
                        }}
                    }}

                    @Override
                    public void close() throws IOException {{
                        if ("close".equals(failure)) {{
                            throw new IOException("injected close failure");
                        }}
                    }}

                    private String content() {{
                        return content.toString();
                    }}
                }}

            {textwrap.indent(chr(10).join(methods), "    ")}

                private static void run(String script, String failure, boolean checkErrors) {{
                    FailingWriter writer = new FailingWriter(failure);
                    try {{
                        Method method = GhidraQueryWriteHarness.class.getDeclaredMethod(
                            "run" + script, Writer.class, String.class, boolean.class);
                        method.invoke(null, writer, failure, checkErrors);
                        System.out.println((checkErrors ? "checked" : "legacy") + "|" +
                            script + "|" + failure + "|RETURNED|WROTE|" + writer.content());
                    }}
                    catch (InvocationTargetException exception) {{
                        Throwable cause = exception.getCause();
                        System.out.println((checkErrors ? "checked" : "legacy") + "|" +
                            script + "|" + failure + "|THREW|" +
                            cause.getClass().getName() + "|" + writer.content());
                    }}
                    catch (Exception exception) {{
                        throw new RuntimeException(exception);
                    }}
                }}

                public static void main(String[] arguments) {{
                    String[] failures = {{"none", "write", "flush", "close"}};
                    for (String script : SCRIPTS) {{
                        for (String failure : failures) {{
                            run(script, failure, true);
                        }}
                    }}
                    for (String failure : failures) {{
                        run(SCRIPTS[0], failure, false);
                    }}
                }}
            }}
        """
    )


class GhidraQueryWriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.javac = shutil.which("javac")
        cls.java = shutil.which("java")
        if cls.javac is None or cls.java is None:
            raise AssertionError("JDK java and javac are required for lifecycle proof")
        SCRATCH.mkdir(parents=True, exist_ok=True)
        cls.fixture = Path(tempfile.mkdtemp(prefix="query-writes-", dir=SCRATCH))
        cls.addClassCleanup(cls.cleanup_fixture)
        cls.source_path = cls.fixture / "GhidraQueryWriteHarness.java"
        cls.source_path.write_text(harness_source(), encoding="utf-8")
        cls.classes = cls.fixture / "classes"
        cls.classes.mkdir()
        compile_result = subprocess.run(
            [
                cls.javac,
                "-encoding",
                "UTF-8",
                "-d",
                str(cls.classes),
                str(cls.source_path),
            ],
            cwd=cls.fixture,
            text=True,
            capture_output=True,
            check=False,
        )
        if compile_result.returncode != 0:
            raise AssertionError(compile_result.stderr)

    @classmethod
    def cleanup_fixture(cls) -> None:
        fixture = getattr(cls, "fixture", None)
        if fixture is None or not fixture.exists():
            return
        fixture_path = fixture.resolve()
        if fixture_path.parent != SCRATCH.resolve():
            raise AssertionError("refusing to remove fixture outside Ghidra scratch")
        shutil.rmtree(fixture_path)

    def test_all_query_scripts_check_closed_writer_before_success_marker(self):
        for script in SCRIPTS:
            source = (GHIDRA / f"{script}.java").read_text(encoding="utf-8")
            self.assertIn("import java.io.IOException;", source, script)
            self.assertNotIn("try (PrintWriter out", source, script)
            self.assertEqual(source.count("try (out)"), 1, script)
            check_start = source.index("if (out.checkError())")
            resource_start = source.index("try (out)")
            resource_end = matching_brace(source, source.index("{", resource_start))
            wrote_start = source.index('println("WROTE', check_start)
            self.assertGreater(check_start, resource_end, script)
            self.assertGreater(wrote_start, check_start, script)

    def test_compiled_production_lifecycle_detects_write_flush_and_close_failures(self):
        result = subprocess.run(
            [self.java, "-cp", str(self.classes), "GhidraQueryWriteHarness"],
            cwd=self.fixture,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [line.split("|") for line in result.stdout.splitlines()]
        checked = {(row[1], row[2]): row[3:] for row in rows if row[0] == "checked"}
        for script in SCRIPTS:
            self.assertEqual(
                checked[(script, "none")], ["RETURNED", "WROTE", "partial-output"]
            )
            for failure in ("write", "flush", "close"):
                content = "partial" if failure == "write" else "partial-output"
                self.assertEqual(
                    checked[(script, failure)],
                    ["THREW", "java.io.IOException", content],
                )

        legacy = {row[2]: row[3:] for row in rows if row[0] == "legacy"}
        for failure in ("write", "flush", "close"):
            content = "partial" if failure == "write" else "partial-output"
            self.assertEqual(legacy[failure], ["RETURNED", "WROTE", content])

    def test_vtable_query_allows_source_writes_after_ctr_transfer(self):
        source = (GHIDRA / "FindVtableSlotCalls.java").read_text(encoding="utf-8")
        find_start = source.index("private Match findCallsite")
        post_ctr_start = source.index(
            "if (writesRegister(next, trackedSource))", find_start
        )
        post_ctr_end = source.index("if (hasControlFlow(next))", post_ctr_start)
        post_ctr = source[post_ctr_start:post_ctr_end]
        self.assertRegex(post_ctr, r"sourceValueLive\s*=\s*false;")
        self.assertNotIn("writesRegister(next, destination)", post_ctr)

    def test_vtable_query_rejects_unproven_later_ctr_transfer(self):
        source = (GHIDRA / "FindVtableSlotCalls.java").read_text(encoding="utf-8")
        find_start = source.index("private Match findCallsite")
        post_ctr_branch = source.index("} else {", find_start)
        transfer_start = source.index("if (isMtctr(next))", post_ctr_branch)
        self.assertGreater(transfer_start, post_ctr_branch)
        transfer_end = source.index(
            "if (writesRegister(next, trackedSource))", transfer_start
        )
        transfer = source[transfer_start:transfer_end]
        self.assertIn("source == null", transfer)
        self.assertIn("!sameRegister(source, trackedSource)", transfer)
        self.assertIn("!sourceValueLive", transfer)

    def test_cfg_vtable_query_is_bounded_and_keeps_control_count(self):
        source = (GHIDRA / "FindVtableSlotCallsCfg.java").read_text(encoding="utf-8")
        self.assertIn("MAX_PATH_INSTRUCTIONS = 16", source)
        self.assertIn("MAX_BRANCH_EDGES = 2", source)
        self.assertIn("MAX_STATES_PER_LOAD = 256", source)
        self.assertIn("state.branchEdges == 0 && state.aliasCopies == 0", source)
        self.assertIn('"Recognized straight-line callsites: "', source)
        self.assertIn('"Straight-line controls: "', source)
        self.assertIn("instruction.getFlowType().isCall()", source)
        self.assertIn("else if (writesCtr(instruction))", source)
        self.assertIn('!registerName(operandRegisters.get(1)).equals("r0")', source)

    def test_raw_vtable_query_subtracts_decoded_candidates_and_is_bounded(self):
        source = (GHIDRA / "FindRawVtableSlotCalls.java").read_text(encoding="utf-8")
        self.assertIn("MAX_WINDOW_WORDS = 8", source)
        self.assertIn("!block.isExecute()", source)
        self.assertIn("decodedCandidates.contains(current.getOffset())", source)
        self.assertIn("LWZ_OPCODE = 0x80000000L", source)
        self.assertIn("MTCTR_MASK = 0xFC1FFFFFL", source)
        self.assertIn("BCTRL_WORD = 0x4E800421L", source)
        self.assertIn("BRANCH_FORM_MASK = 0xFC0007FEL", source)
        self.assertIn('"Raw-only slot-load candidates: "', source)
        self.assertIn('"Truncated: "', source)
        self.assertIn('"Cancelled: "', source)

    def test_global_query_continues_after_a_nonmatching_split_part(self):
        source = (GHIDRA / "FindGlobalAddressAccesses.java").read_text(encoding="utf-8")
        scan_start = source.index("SplitPart low = splitPart")
        low_start = source.rindex("if (low != null)", scan_start)
        low_open = source.index("{", low_start)
        low_end = matching_brace(source, low_open)
        low_block = source[low_open:low_end]
        self.assertNotIn(
            "\n                        break;\n                    }", low_block
        )
        overwrite_start = source.index(
            "if (writesRegister(current, highRegister) || hasControlFlow(current))",
            low_end,
        )
        self.assertGreater(overwrite_start, low_end)


if __name__ == "__main__":
    unittest.main()
