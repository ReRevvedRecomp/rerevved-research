from __future__ import annotations

import unittest
from pathlib import Path

from java_test_support import JavaFixture, java_method

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "ghidra" / "DumpStringBoundary.java"


class DumpStringBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        method = java_method(
            SCRIPT.read_text(encoding="utf-8"), "private void addFunctions("
        )
        source = """
import java.util.*;
public class StringBoundaryFixture {
    record Address(String value) {}
    record Function(Address getEntryPoint) {}
    METHOD
    public static void main(String[] args) {
        Map<Address, Function> destination = new LinkedHashMap<>();
        for (String name : args[0].split(",")) {
            if (!name.isEmpty()) destination.put(new Address(name), new Function(new Address(name)));
        }
        List<Function> additions = new ArrayList<>();
        for (String name : args[1].split(",")) {
            if (!name.isEmpty()) additions.add(new Function(new Address(name)));
        }
        new StringBoundaryFixture().addFunctions(destination, additions, Integer.parseInt(args[2]));
        System.out.println(String.join(",", destination.keySet().stream().map(Address::value).toList()));
        System.out.println(destination.size());
    }
}
""".replace("METHOD", method)
        cls.fixture = JavaFixture(cls, {"StringBoundaryFixture.java": source})

    def test_order_duplicates_and_cap(self):
        for initial, additions, cap, expected in (
            (("root",), ("caller", "callee"), 4, ("root", "caller", "callee")),
            (("root",), ("root", "callee"), 3, ("root", "callee")),
            (("root", "caller"), (), 2, ("root", "caller")),
            (
                ("root",),
                ("caller-a", "callee-a", "callee-b"),
                3,
                ("root", "caller-a", "callee-a"),
            ),
            (("root", "caller"), ("callee",), 2, ("root", "caller")),
        ):
            with self.subTest(initial=initial, additions=additions, cap=cap):
                result = self.fixture.run(
                    "StringBoundaryFixture",
                    ",".join(initial),
                    ",".join(additions),
                    str(cap),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                lines = result.stdout.splitlines()
                self.assertEqual(tuple(lines[0].split(",")), expected)
                self.assertEqual(int(lines[1]), len(expected))


if __name__ == "__main__":
    unittest.main()
