from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "tools" / "find_divide_multiply.py"
SPEC = importlib.util.spec_from_file_location("find_divide_multiply", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
scanner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scanner
SPEC.loader.exec_module(scanner)


def divw(dest: int, left: int, right: int, *, unsigned: bool = False) -> int:
    xo = 459 if unsigned else 491
    return (31 << 26) | (dest << 21) | (left << 16) | (right << 11) | (xo << 1)


def mullw(dest: int, left: int, right: int) -> int:
    return (31 << 26) | (dest << 21) | (left << 16) | (right << 11) | (235 << 1)


def mulli(dest: int, source: int, immediate: int) -> int:
    return (7 << 26) | (dest << 21) | (source << 16) | (immediate & 0xFFFF)


def mr(dest: int, source: int) -> int:
    return (31 << 26) | (source << 21) | (dest << 16) | (source << 11) | (444 << 1)


def addi(dest: int, source: int, immediate: int = 1) -> int:
    return (14 << 26) | (dest << 21) | (source << 16) | (immediate & 0xFFFF)


class FindDivideMultiplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = 0x1000
        self.image_size = 0x100

    def make_case(
        self, words: dict[int, int], dump_rows: list[tuple[int, int]] | None = None
    ):
        image = bytearray(self.image_size)
        for address, value in words.items():
            offset = address - self.base
            image[offset : offset + 4] = value.to_bytes(4, "big")
        image_path = self.root / "image.bin"
        image_path.write_bytes(image)
        manifest_path = self.root / "image.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "analysisProgram": {
                        "name": "synthetic.bin",
                        "imageBase": hex(self.base),
                        "imageSize": len(image),
                        "flatImageSha256": hashlib.sha256(image).hexdigest().upper(),
                    }
                }
            ),
            encoding="utf-8",
        )
        rows = dump_rows if dump_rows is not None else sorted(words.items())
        dump_path = self.root / "dump.txt"
        dump_path.write_text(
            "Program: synthetic.bin\n"
            "Targets: 0x00001000\n"
            "Word radius: 8\n\n"
            "=== 0x00001000 ===\n"
            + "".join(f"  0x{address:08X}: 0x{value:08X}\n" for address, value in rows),
            encoding="utf-8",
        )
        return image_path, manifest_path, dump_path

    def scan_case(self, words: dict[int, int], start: int = 0x1000, end: int = 0x1010):
        image, manifest, dump = self.make_case(words)
        return scanner.scan([dump], image, manifest, [scanner.Range(start, end)])

    def test_exact_dataflow_and_register_copy(self) -> None:
        words = {
            0x1000: divw(3, 4, 5),
            0x1004: addi(6, 7),
            0x1008: 0x7C681B78,  # mr r8,r3; logical form has RA as destination.
            0x100C: mullw(9, 8, 10),
        }
        result = self.scan_case(words)
        self.assertEqual(
            result["candidates"],
            [
                {
                    "divide_address": "0x00001000",
                    "multiply_address": "0x0000100C",
                    "operation_pair": "divw->mullw",
                    "quotient_register": "r3",
                }
            ],
        )

    def test_unsigned_divide_mulli_and_trap_retain_provenance(self) -> None:
        words = {
            0x1000: divw(3, 4, 5, unsigned=True),
            0x1004: 0x0C640000,  # twi 3,r4,0; normal completion continues.
            0x1008: mulli(9, 3, 7),
        }
        result = self.scan_case(words, end=0x100C)
        self.assertEqual(result["candidates"][0]["operation_pair"], "divwu->mulli")

    def test_overwritten_quotient_is_not_reported(self) -> None:
        words = {0x1000: divw(3, 4, 5), 0x1004: addi(3, 6), 0x1008: mullw(9, 3, 10)}
        result = self.scan_case(words, end=0x100C)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["barriers"]["quotient_overwrites"], 1)

    def test_literal_rotate_overwrite_is_not_reported(self) -> None:
        words = {
            0x1000: divw(3, 4, 5),
            0x1004: 0x5503003E,  # rlwinm r3,r8,0,0,31; destination is RA.
            0x1008: mullw(9, 3, 10),
        }
        result = self.scan_case(words, end=0x100C)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["barriers"]["quotient_overwrites"], 1)

    def test_r0_divide_destination_can_feed_multiply(self) -> None:
        words = {0x1000: divw(0, 4, 5), 0x1004: mullw(9, 0, 10)}
        result = self.scan_case(words, end=0x1008)
        self.assertEqual(result["candidates"][0]["quotient_register"], "r0")

    def test_logical_andc_uses_ra_as_destination(self) -> None:
        words = {
            0x1000: divw(10, 4, 5),
            0x1004: 0x7CC84078,  # andc r8,r6,r8; it must not clobber r10.
            0x1008: mullw(9, 10, 7),
        }
        result = self.scan_case(words, end=0x100C)
        self.assertEqual(len(result["candidates"]), 1)

    def test_branch_and_unknown_clear_provenance(self) -> None:
        for middle in (0x48000000, 0x48000001, 0xFFFFFFFF):
            with self.subTest(middle=hex(middle)):
                words = {0x1000: divw(3, 4, 5), 0x1004: middle, 0x1008: mullw(9, 3, 10)}
                result = self.scan_case(words, end=0x100C)
                self.assertEqual(result["candidates"], [])
                if middle == 0x48000001:
                    self.assertEqual(result["barriers"]["calls"], 1)

    def test_range_boundary_does_not_import_provenance(self) -> None:
        words = {0x1000: divw(3, 4, 5), 0x1004: mullw(9, 3, 10)}
        result = self.scan_case(words, start=0x1004, end=0x1008)
        self.assertEqual(result["candidates"], [])

    def test_missing_and_conflicting_rows_are_rejected(self) -> None:
        words = {0x1000: divw(3, 4, 5), 0x1004: mullw(9, 3, 10)}
        image, manifest, dump = self.make_case(words, [(0x1000, words[0x1000])])
        with self.assertRaisesRegex(scanner.ScanError, "missing dump word"):
            scanner.scan([dump], image, manifest, [scanner.Range(0x1000, 0x1008)])
        conflict = self.root / "conflict.txt"
        conflict.write_text(
            "Program: synthetic.bin\n0x00001000: 0x00000000\n0x00001000: 0x00000001\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(scanner.ScanError, "conflicting word rows"):
            scanner.scan([conflict], image, manifest, [scanner.Range(0x1000, 0x1004)])
        with self.assertRaisesRegex(scanner.ScanError, "aligned"):
            scanner.scan([dump], image, manifest, [scanner.Range(0x1001, 0x1008)])

    def test_malformed_dump_and_image_mismatch_are_rejected(self) -> None:
        words = {0x1000: divw(3, 4, 5), 0x1004: mullw(9, 3, 10)}
        image, manifest, dump = self.make_case(words)
        malformed = self.root / "malformed.txt"
        malformed.write_text(
            "Program: synthetic.bin\n0x1000: not-a-word\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(scanner.ScanError, "malformed dump row"):
            scanner.scan([malformed], image, manifest, [scanner.Range(0x1000, 0x1004)])
        image.write_bytes(image.read_bytes()[:-1] + b"x")
        with self.assertRaisesRegex(scanner.ScanError, "SHA256"):
            scanner.scan([dump], image, manifest, [scanner.Range(0x1000, 0x1008)])


if __name__ == "__main__":
    unittest.main()
