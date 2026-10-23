from __future__ import annotations

import os
import re
import textwrap
import unittest
from pathlib import Path

from java_test_support import JavaFixture, ghidra_classpath, matching_brace

REPO = Path(__file__).resolve().parents[1]
GHIDRA = REPO / "ghidra"
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
    "SummarizeRecordBytes",
    "FindFieldAccesses",
    "FindRawFieldStores",
    "FindRawGlobalStoreCandidates",
    "FindAbsoluteHalfwordCandidates",
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


OWNER_CALL_FIXTURE = textwrap.dedent(
    """
    import ghidra.program.flatapi.FlatProgramAPI;
    import ghidra.app.script.GhidraScript;
    import ghidra.program.model.address.Address;
    import ghidra.program.model.address.AddressFactory;
    import ghidra.program.model.address.AddressSpace;
    import ghidra.program.model.lang.Register;
    import ghidra.program.model.listing.Function;
    import ghidra.program.model.listing.FunctionManager;
    import ghidra.program.model.listing.Instruction;
    import ghidra.program.model.listing.Program;
    import ghidra.util.task.TaskMonitor;
    import java.io.PrintWriter;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    import java.lang.reflect.Proxy;
    import java.util.HashSet;
    import java.util.LinkedHashSet;
    import java.util.List;
    import java.util.Map;
    import java.util.Set;

    public class OwnerCallGhidraFixture {
        private static Object defaultValue(Class<?> type) {
            if (!type.isPrimitive()) return null;
            if (type == boolean.class) return false;
            if (type == byte.class) return (byte) 0;
            if (type == short.class) return (short) 0;
            if (type == int.class) return 0;
            if (type == long.class) return 0L;
            if (type == float.class) return 0.0f;
            if (type == double.class) return 0.0d;
            if (type == char.class) return '\\0';
            return null;
        }

        private static Address address(long offset) {
            InvocationHandler handler = (proxy, method, args) -> {
                switch (method.getName()) {
                    case "getOffset":
                    case "getUnsignedOffset":
                    case "getAddressableWordOffset":
                        return offset;
                    case "toString":
                        return String.format("0x%08X", offset);
                    case "hashCode":
                        return Long.hashCode(offset);
                    case "equals":
                        return args != null && args.length == 1
                            && args[0] instanceof Address
                            && ((Address) args[0]).getOffset() == offset;
                    case "compareTo":
                        return Long.compare(offset, ((Address) args[0]).getOffset());
                    case "getSize":
                        return 4;
                    default:
                        return defaultValue(method.getReturnType());
                }
            };
            return (Address) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {Address.class}, handler);
        }

        private static AddressSpace addressSpace() {
            InvocationHandler handler = (proxy, method, args) -> {
                if (method.getName().equals("getAddress") && args != null && args.length == 1) {
                    if (args[0] instanceof Long) return address((Long) args[0]);
                    if (args[0] instanceof String) return address(Long.decode((String) args[0]));
                }
                if (method.getName().equals("getName")) return "ram";
                return defaultValue(method.getReturnType());
            };
            return (AddressSpace) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {AddressSpace.class}, handler);
        }

        private static final class Node {
            final long entry;
            final Set<Node> callers = new LinkedHashSet<>();
            final Set<Node> callees = new LinkedHashSet<>();
            Function function;

            Node(long entry) {
                this.entry = entry;
            }
        }

        private static Function function(Node node) {
            InvocationHandler handler = (proxy, method, args) -> {
                switch (method.getName()) {
                    case "getEntryPoint":
                        return address(node.entry);
                    case "getCallingFunctions":
                        return functions(node.callers);
                    case "getCalledFunctions":
                        return functions(node.callees);
                    case "getName":
                        return "f" + Long.toHexString(node.entry);
                    case "hashCode":
                        return System.identityHashCode(proxy);
                    case "equals":
                        return args != null && args.length == 1 && proxy == args[0];
                    case "toString":
                        return "f" + Long.toHexString(node.entry);
                    default:
                        return defaultValue(method.getReturnType());
                }
            };
            node.function = (Function) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {Function.class}, handler);
            return node.function;
        }

        private static Set<Function> functions(Set<Node> nodes) {
            Set<Function> result = new LinkedHashSet<>();
            for (Node node : nodes) result.add(node.function);
            return result;
        }

        private static FunctionManager functionManager(List<Node> nodes) {
            InvocationHandler handler = (proxy, method, args) -> {
                if ((method.getName().equals("getFunctionAt")
                        || method.getName().equals("getFunctionContaining"))
                    && args != null && args.length == 1 && args[0] instanceof Address) {
                    long value = ((Address) args[0]).getOffset();
                    for (Node node : nodes) {
                        if (value == node.entry
                            || (method.getName().equals("getFunctionContaining")
                                && value > node.entry && value < node.entry + 0x10)) {
                            return node.function;
                        }
                    }
                    return null;
                }
                return defaultValue(method.getReturnType());
            };
            return (FunctionManager) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {FunctionManager.class}, handler);
        }

        private static Program program(FunctionManager functions, AddressSpace space) {
            AddressFactory factory = (AddressFactory) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {AddressFactory.class},
                (proxy, method, args) -> method.getName().equals("getDefaultAddressSpace")
                    ? space : defaultValue(method.getReturnType()));
            return (Program) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {Program.class},
                (proxy, method, args) -> method.getName().equals("getAddressFactory")
                    ? factory
                    : method.getName().equals("getFunctionManager")
                        ? functions : defaultValue(method.getReturnType()));
        }

        private static void setField(Object target, Class<?> owner, String name, Object value)
                throws Exception {
            var field = owner.getDeclaredField(name);
            field.setAccessible(true);
            field.set(target, value);
        }

        @SuppressWarnings("unchecked")
        private static Map<Long, Integer> closure(
                FindFieldAccesses script, FunctionManager functions, Set<Long> seeds,
                int callerDepth, int calleeDepth, boolean explicit) throws Exception {
            Method method = FindFieldAccesses.class.getDeclaredMethod(
                "buildClosure", FunctionManager.class, Set.class, int.class, int.class, boolean.class);
            method.setAccessible(true);
            try {
                return (Map<Long, Integer>) method.invoke(
                    script, functions, seeds, callerDepth, calleeDepth, explicit);
            } catch (InvocationTargetException exception) {
                Throwable cause = exception.getCause();
                if (cause instanceof Exception) throw (Exception) cause;
                throw exception;
            }
        }

        private static Instruction copyInstruction(Register destination, Register source,
                String mnemonic) {
            return (Instruction) Proxy.newProxyInstance(
                OwnerCallGhidraFixture.class.getClassLoader(),
                new Class<?>[] {Instruction.class},
                (proxy, method, args) -> {
                    switch (method.getName()) {
                        case "getMnemonicString":
                            return mnemonic;
                        case "getNumOperands":
                            return 1;
                        case "getOpObjects":
                            return new Object[] {destination, source};
                        case "getResultObjects":
                            return new Object[] {destination};
                        default:
                            return defaultValue(method.getReturnType());
                    }
                });
        }

        private static int updateAliases(
                FindVtableSlotCallsCfg script, Instruction instruction,
                Set<String> aliases, int count) throws Exception {
            Method method = FindVtableSlotCallsCfg.class.getDeclaredMethod(
                "updateAliases", Instruction.class, Set.class, int.class);
            method.setAccessible(true);
            return (Integer) method.invoke(script, instruction, aliases, count);
        }

        private static Register register(String name) {
            return new Register(name, "", Address.NO_ADDRESS, 4, true, 0);
        }

        private static void check(boolean condition, String message) {
            if (!condition) throw new AssertionError(message);
        }

        private static void checkClosure() throws Exception {
            Node s = new Node(0x100), x = new Node(0x110), y = new Node(0x120);
            s.callees.add(x);
            x.callers.add(s);
            x.callees.add(s);
            s.callers.add(x);
            x.callees.add(y);
            y.callers.add(x);
            List<Node> nodes = List.of(s, x, y);
            for (Node node : nodes) function(node);
            FunctionManager functions = functionManager(nodes);
            FindFieldAccesses script = new FindFieldAccesses();
            AddressSpace space = addressSpace();
            setField(script, FlatProgramAPI.class, "currentProgram", program(functions, space));
            setField(script, FlatProgramAPI.class, "monitor", TaskMonitor.DUMMY);
            setField(script, GhidraScript.class, "errorWriter", new PrintWriter(System.err, true));

            Map<Long, Integer> result = closure(
                script, functions, Set.of(0x100L), 1, 2, true);
            check(result.get(0x120L) == 2, "callee traversal omitted Y");
            Map<Long, Integer> limited = closure(
                script, functions, Set.of(0x100L), 0, 1, true);
            check(!limited.containsKey(0x120L), "callee depth limit admitted Y");
            check(closure(script, functions, Set.of(), 0, 0, false).isEmpty(),
                "omitted seeds did not preserve broad-mode sentinel");
            boolean rejected = false;
            try {
                closure(script, functions, Set.of(0x999L), 0, 0, true);
            } catch (IllegalArgumentException expected) {
                rejected = true;
            }
            check(rejected, "unresolved explicit seed was accepted");
            rejected = false;
            try {
                closure(script, functions, Set.of(0x100L, 0x999L), 0, 0, true);
            } catch (IllegalArgumentException expected) {
                rejected = true;
            }
            check(rejected, "partially unresolved explicit seeds were accepted");
        }

        private static void checkAliases() throws Exception {
            FindVtableSlotCallsCfg script = new FindVtableSlotCallsCfg();
            Register r3 = register("r3");
            Register r4 = register("r4");
            Set<String> aliases = new HashSet<>(Set.of("r3"));
            int count = updateAliases(script, copyInstruction(r3, r3, "mr"), aliases, 0);
            check(aliases.contains("r3") && count == 0, "live self-copy lost its alias");
            aliases = new HashSet<>(Set.of("r3"));
            count = updateAliases(script, copyInstruction(r4, r3, "mr"), aliases, 0);
            check(aliases.contains("r4") && count == 1, "live distinct copy was not counted");
            aliases = new HashSet<>(Set.of("r5"));
            count = updateAliases(script, copyInstruction(r4, r3, "mr"), aliases, 0);
            check(!aliases.contains("r4") && count == 0, "dead source created an alias");
            aliases = new HashSet<>(Set.of("r3"));
            count = updateAliases(script, copyInstruction(r3, r4, "add"), aliases, 0);
            check(!aliases.contains("r3") && count == 0, "non-copy clobber preserved an alias");
        }

        public static void main(String[] args) throws Exception {
            checkClosure();
            checkAliases();
            System.out.println("OK");
        }
    }
    """
)


def production_lifecycle(source: str) -> tuple[str, str]:
    declaration_start = source.index("PrintWriter out = new PrintWriter(")
    declaration_end = source.index(";", declaration_start) + 1
    declaration = source[declaration_start:declaration_end]
    declaration = re.sub(
        r'new FileWriter\((?:outPath|required\("REREVVED_DUMP_PATH"\))\)',
        "writer",
        declaration,
    )
    declaration = re.sub(
        r"new OutputStreamWriter\(.*?StandardCharsets\.UTF_8\)",
        "writer",
        declaration,
        flags=re.DOTALL,
    )
    if "FileWriter(" in declaration or "OutputStreamWriter(" in declaration:
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
        cls.fixture = JavaFixture(
            cls, {"GhidraQueryWriteHarness.java": harness_source()}
        )

    def test_compiled_production_lifecycle_detects_write_flush_and_close_failures(self):
        result = self.fixture.run("GhidraQueryWriteHarness")
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


class GhidraQueryInstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources = {
            "QueryInstructionFixture.java": (
                REPO / "tests" / "QueryInstructionFixture.java"
            ).read_text(encoding="ascii")
        }
        for script in (
            "FindVtableSlotCalls",
            "FindVtableSlotCallsCfg",
            "FindRawVtableSlotCalls",
            "FindGlobalAddressAccesses",
        ):
            source = (GHIDRA / f"{script}.java").read_text(encoding="utf-8")
            # Bind production queries to the fixture's input-only API objects.
            sources[f"{script}.java"] = re.sub(
                r"^import ghidra\.[^;]+;\n", "", source, flags=re.MULTILINE
            )
        cls.fixture = JavaFixture(cls, sources)

    def query(self, scenario, *args):
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("REREVVED_")
        }
        environment.update(
            {
                "REREVVED_DUMP_PATH": str(self.fixture.root / "query.txt"),
                "REREVVED_VTABLE_SLOT_DISPLACEMENTS": "0x34",
                "REREVVED_TARGET_VAS": "0x12340002",
            }
        )
        result = self.fixture.run(
            "QueryInstructionFixture", scenario, *args, environment=environment
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_ctr_transfer_preserves_value_and_rejects_unproven_retransfer(self):
        for scenario, total in (
            ("ctr-overwrite", 1),
            ("ctr-live", 1),
            ("ctr-stale", 0),
            ("ctr-wrong", 0),
            ("ctr-missing", 0),
        ):
            with self.subTest(scenario=scenario):
                output = self.query(scenario)
                self.assertIn(f"Total: {total}\n", output)
                if total:
                    self.assertIn("Slot load: 0x00000000", output)
                    self.assertIn(
                        "bctrl: 0x0000000C"
                        if scenario == "ctr-overwrite"
                        else "bctrl: 0x00000010",
                        output,
                    )

    def test_cfg_bounds_and_straight_line_controls(self):
        for distance, controls in ((16, 1), (17, 0)):
            with self.subTest(distance=distance):
                output = self.query("cfg-distance-", str(distance))
                self.assertIn(
                    f"Recognized straight-line callsites: {controls}\n", output
                )
                self.assertIn("Total: 0\n", output)
                if controls:
                    self.assertIn("Straight-line controls: 0x00000040", output)
        for branches, total in ((2, 1), (3, 0)):
            with self.subTest(branches=branches):
                output = self.query("cfg-branches-", str(branches))
                self.assertIn(f"Total: {total}\n", output)
                self.assertIn("Recognized straight-line callsites: 0\n", output)
        output = self.query("cfg-state-cap")
        self.assertIn("Explored path states: 256\n", output)
        self.assertIn("Loads reaching state cap: 1\n", output)
        for scenario in ("cfg-clobber", "cfg-call"):
            with self.subTest(scenario=scenario):
                output = self.query(scenario)
                self.assertIn("Total: 0\n", output)
                self.assertIn("Recognized straight-line callsites: 0\n", output)
        for scenario, total in (("cfg-r0", 0), ("cfg-alias", 1)):
            with self.subTest(scenario=scenario):
                output = self.query(scenario)
                self.assertIn(f"Total: {total}\n", output)
                self.assertIn("Recognized straight-line callsites: 0\n", output)
                if total:
                    self.assertIn("Alias copies: 2\n", output)

    def test_raw_query_subtracts_decoded_candidates_and_bounds_window(self):
        output = self.query("raw-decoded")
        self.assertIn("Executable raw words scanned: 6\n", output)
        self.assertIn("Raw candidates covered by decoded query: 1\n", output)
        self.assertIn("Raw-only slot-load candidates: 1\n", output)
        self.assertIn("Raw slot load: 0x00000100", output)
        self.assertIn("Total raw-only callsite candidates: 1\n", output)
        self.assertIn("Truncated: false\n", output)
        self.assertIn("Cancelled: false\n", output)
        for distance, total in ((8, 1), (9, 0)):
            with self.subTest(distance=distance):
                output = self.query("raw-window", str(distance))
                self.assertIn(f"Total raw-only callsite candidates: {total}\n", output)
        output = self.query("raw-control")
        self.assertIn("Total raw-only callsite candidates: 0\n", output)

    def test_global_query_continues_after_nonmatching_split_part(self):
        output = self.query("global-continue")
        self.assertIn("Materializers emitted: 1\n", output)
        self.assertIn("Target: 0x12340002", output)
        self.assertIn("Materializer high: 0x00000000", output)
        self.assertIn("Materializer low: 0x00000008", output)


class GhidraOwnerCallTests(unittest.TestCase):
    def test_owner_call_graph_and_alias_helpers_execute_against_ghidra_apis(self):
        closure_source = (GHIDRA / "FindFieldAccesses.java").read_text(encoding="utf-8")
        self.assertIn("boolean explicitSeeds", closure_source)
        self.assertIn("Map<Long, Integer> callerDepths", closure_source)
        self.assertIn("Map<Long, Integer> calleeDepths", closure_source)
        alias_source = (GHIDRA / "FindVtableSlotCallsCfg.java").read_text(
            encoding="utf-8"
        )
        self.assertIn("boolean sourceLive", alias_source)
        self.assertIn("if (!identity) aliasCopies++;", alias_source)
        classpath = ghidra_classpath()
        if classpath is None:
            self.skipTest("REREVVED_GHIDRA_HOME is not configured")
        fixture = JavaFixture(
            self,
            {"OwnerCallGhidraFixture.java": OWNER_CALL_FIXTURE},
            production=(
                GHIDRA / "FindFieldAccesses.java",
                GHIDRA / "FindVtableSlotCallsCfg.java",
            ),
            classpath=classpath,
        )
        result = fixture.run("OwnerCallGhidraFixture")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "OK")


if __name__ == "__main__":
    unittest.main()
