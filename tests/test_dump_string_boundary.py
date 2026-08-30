from __future__ import annotations

import unittest
from collections import OrderedDict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "ghidra" / "DumpStringBoundary.java"


def add_functions(
    initial: tuple[str, ...], additions: tuple[str, ...], cap: int
) -> tuple[str, ...]:
    destination = OrderedDict.fromkeys(initial)
    for function in additions:
        if len(destination) >= cap:
            return tuple(destination)
        destination[function] = None
    return tuple(destination)


class DumpStringBoundaryTests(unittest.TestCase):
    def method_body(self) -> str:
        source = SCRIPT.read_text(encoding="utf-8")
        start = source.index("    private void addFunctions(")
        end = source.index(
            "    private void followRegistrationWindow(", start
        )
        return source[start:end]

    def test_cap_guard_precedes_insertion(self):
        method = self.method_body()
        guard = "if (destination.size() >= maxFunctions) {"
        insertion = "destination.put(function.getEntryPoint(), function);"
        self.assertIn(guard, method)
        self.assertLess(method.index(guard), method.index(insertion))
        self.assertNotIn("destination.size() > maxFunctions", method)

    def test_non_overflow_output_parity(self):
        cases = (
            (("root",), ("caller", "callee"), 4),
            (("root",), ("root", "callee"), 3),
            (("root", "caller"), (), 2),
        )
        for initial, additions, cap in cases:
            with self.subTest(initial=initial, additions=additions, cap=cap):
                expected = tuple(OrderedDict.fromkeys(initial + additions))
                self.assertEqual(add_functions(initial, additions, cap), expected)

    def test_overflow_stops_at_cap_without_reordering(self):
        result = add_functions(
            ("root",), ("caller-a", "callee-a", "callee-b"), 3
        )
        self.assertEqual(result, ("root", "caller-a", "callee-a"))
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
