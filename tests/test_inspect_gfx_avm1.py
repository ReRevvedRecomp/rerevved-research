import importlib.util
import struct
import unittest
from pathlib import Path

TOOL_PATH = Path(__file__).parents[1] / "tools" / "inspect-gfx-avm1.py"
SPEC = importlib.util.spec_from_file_location("inspect_gfx_avm1", TOOL_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def long_action(opcode, payload):
    return bytes([opcode]) + struct.pack("<H", len(payload)) + payload


class InspectGfxAvm1Tests(unittest.TestCase):
    def test_constant_pool_push_resolves_string(self):
        pool = long_action(0x88, struct.pack("<H", 2) + b"loadClip\0MovieClipLoader\0")
        push = long_action(0x96, b"\x08\x00\x08\x01")
        actions = MODULE.parse_actions(pool + push + b"\0", 0x100)
        self.assertEqual(actions[1]["values"][0]["value"], "loadClip")
        self.assertEqual(actions[1]["values"][1]["value"], "MovieClipLoader")

    def test_define_function_body_is_decoded(self):
        body = long_action(0x96, b"\x00SetPortrait\0") + b"\0"
        header = b"handler\0" + struct.pack("<H", 0) + struct.pack("<H", len(body))
        actions = MODULE.parse_actions(long_action(0x9B, header) + body + b"\0", 0x200)
        nested = actions[0]["body"][0]
        self.assertEqual(nested["values"][0]["value"], "SetPortrait")
        self.assertEqual(nested["offset"], "0x20F")

    def test_nested_scopes_isolate_constant_pools(self):
        outer_pool = long_action(0x88, struct.pack("<H", 1) + b"outer\0")

        function_body = (
            long_action(0x88, struct.pack("<H", 1) + b"function\0")
            + long_action(0x96, b"\x08\x00")
            + b"\0"
        )
        function_header = (
            b"handler\0" + struct.pack("<H", 0) + struct.pack("<H", len(function_body))
        )
        function = long_action(0x9B, function_header) + function_body

        with_body = (
            long_action(0x88, struct.pack("<H", 1) + b"with\0")
            + long_action(0x96, b"\x08\x00")
            + b"\0"
        )
        with_action = long_action(0x94, struct.pack("<H", len(with_body))) + with_body

        try_body = (
            long_action(0x88, struct.pack("<H", 1) + b"try\0")
            + long_action(0x96, b"\x08\x00")
            + b"\0"
        )
        catch_body = long_action(0x96, b"\x08\x00") + b"\0"
        finally_body = long_action(0x96, b"\x08\x00") + b"\0"
        try_header = (
            b"\0"
            + struct.pack("<HHH", len(try_body), len(catch_body), len(finally_body))
            + b"error\0"
        )
        try_action = (
            long_action(0x8F, try_header) + try_body + catch_body + finally_body
        )

        actions = MODULE.parse_actions(
            outer_pool
            + function
            + with_action
            + try_action
            + long_action(0x96, b"\x08\x00")
            + b"\0",
            0x300,
        )

        self.assertEqual(actions[1]["body"][1]["values"][0]["value"], "function")
        self.assertEqual(actions[2]["body"][1]["values"][0]["value"], "with")
        self.assertEqual(actions[3]["tryBody"][1]["values"][0]["value"], "try")
        self.assertEqual(actions[3]["catchBody"][0]["values"][0]["value"], "outer")
        self.assertEqual(actions[3]["finallyBody"][0]["values"][0]["value"], "outer")
        self.assertEqual(actions[4]["values"][0]["value"], "outer")

    def test_rect_end_uses_declared_bit_width(self):
        self.assertEqual(MODULE.rect_end(bytes([0x08, 0x00]), 0), 2)


if __name__ == "__main__":
    unittest.main()
