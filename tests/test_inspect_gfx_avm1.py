import importlib.util
import struct
import unittest
from pathlib import Path

TOOL_PATH = Path(__file__).parents[1] / "tools" / "inspect_gfx_avm1.py"
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

    def test_malformed_action_extents_and_trailing_data(self):
        for data, diagnostic in (
            (b"\x96\x01", "truncated action length at 0x100"),
            (b"\x96\x02\x00\x00", "action at 0x100 exceeds its block"),
            (
                b"\x9b\x05\x00\x00\x00\x00\x02\x00\x00",
                "function body at 0x108 exceeds its block",
            ),
            (b"\x94\x02\x00\x02\x00\x00", "With body at 0x105 exceeds its block"),
            (
                b"\x8f\x08\x00\x04\x02\x00\x00\x00\x00\x00\x01\x00",
                "Try bodies at 0x10B exceed their block",
            ),
            (b"\x00\x04", "nonzero bytes follow End at 0x100"),
            (b"\x88\x03\x00\x00\x00\x01", "constant pool has trailing bytes"),
        ):
            with self.subTest(data=data):
                with self.assertRaisesRegex(ValueError, diagnostic):
                    MODULE.parse_actions(data, 0x100)

    def test_define_function2_register_parameters(self):
        header = b"handler\0\x01\x00\x02\x01\x00\x01arg\0\x01\x00"
        action = MODULE.parse_actions(long_action(0x8E, header) + b"\0\0", 0x200)[0]
        self.assertEqual(action["functionName"], "handler")
        self.assertEqual(action["registerCount"], 2)
        self.assertEqual(action["flags"], 1)
        self.assertEqual(action["parameters"], [{"register": 1, "name": "arg"}])
        self.assertEqual(action["body"][0]["name"], "End")
        self.assertEqual(action["body"][0]["offset"], "0x217")

    def test_numeric_push_values(self):
        payload = (
            b"\x01\x00\x00\xc0\x3f"
            b"\x06\x00\x00\x04\xc0\x00\x00\x00\x00"
            b"\x07\xfe\xff\xff\xff\x05\x01\x04\x03"
        )
        action = MODULE.parse_actions(long_action(0x96, payload) + b"\0", 0)[0]
        self.assertEqual(
            [(item["kind"], item["value"]) for item in action["values"]],
            [
                ("float", 1.5),
                ("double", -2.5),
                ("integer", -2),
                ("boolean", True),
                ("register", 3),
            ],
        )

    def test_try_catch_register(self):
        header = b"\x07\x01\x00\x01\x00\x01\x00\x03"
        action = MODULE.parse_actions(long_action(0x8F, header) + b"\0\0\0\0", 0)[0]
        self.assertEqual(action["catchRegister"], 3)
        self.assertNotIn("catchName", action)
        for name in ("tryBody", "catchBody", "finallyBody"):
            with self.subTest(body=name):
                self.assertEqual(action[name][0]["name"], "End")

    def test_tag_stream_dispatches_actions_and_nested_sprites(self):
        actions = long_action(0x96, b"\x00target\0") + b"\0"
        do_action = struct.pack("<H", (12 << 6) | len(actions)) + actions
        init_action = (
            struct.pack("<H", (59 << 6) | (len(actions) + 2)) + b"\x07\x00" + actions
        )
        sprite_body = b"\x09\x00\x01\x00" + do_action + b"\0\0"
        sprite = struct.pack("<H", (39 << 6) | len(sprite_body)) + sprite_body
        stream = do_action + init_action + sprite + b"\0\0"
        matches = []
        MODULE.parse_tag_stream(
            stream, 0, len(stream), ["fixture"], ["target"], matches
        )
        self.assertEqual(
            [item["tagType"] for item in matches],
            ["DoAction", "DoInitAction", "DoAction"],
        )
        self.assertEqual(matches[1]["spriteId"], 7)
        self.assertIn("spriteId=9", matches[2]["tagPath"])
        self.assertEqual(
            [item["actionOffset"] for item in matches], ["0x2", "0x12", "0x26"]
        )
        for item in matches:
            self.assertEqual(item["matchedTargets"], ["target"])
            self.assertEqual(item["actions"][0]["values"][0]["value"], "target")


if __name__ == "__main__":
    unittest.main()
