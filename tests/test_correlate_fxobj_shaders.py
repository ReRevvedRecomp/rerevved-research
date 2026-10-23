from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from correlate_fxobj_shaders import (  # noqa: E402
    correlate,
    find_offsets,
    swap_dword_bytes,
)


class CorrelateFxobjShadersTests(unittest.TestCase):
    def write_shader(
        self, directory: Path, shader_hash: str, stage: str, data: bytes
    ) -> None:
        (directory / f"shader_{shader_hash}.ucode.bin.{stage}").write_bytes(data)

    def test_correlates_raw_shader_bytes(self) -> None:
        shader = bytes(range(12))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader_directory = root / "shaders"
            shader_directory.mkdir()
            self.write_shader(shader_directory, "0123456789ABCDEF", "vert", shader)
            fxobj = root / "water.fxobj"
            fxobj.write_bytes(b"prefix" + shader + b"suffix")

            result = correlate([fxobj], shader_directory, 16)

        self.assertEqual(result["summary"]["matchedShaderCount"], 1)
        self.assertEqual(
            result["shaders"][0]["matches"],
            [{"fxobj": "water.fxobj", "encoding": "raw", "offsets": [6]}],
        )

    def test_correlates_dword_byte_swapped_shader(self) -> None:
        shader = bytes(range(12))
        swapped = b"\x03\x02\x01\x00\x07\x06\x05\x04\x0b\x0a\x09\x08"
        self.assertEqual(swap_dword_bytes(shader), swapped)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader_directory = root / "shaders"
            shader_directory.mkdir()
            self.write_shader(shader_directory, "FEDCBA9876543210", "frag", shader)
            fxobj = root / "rivers.fxobj"
            fxobj.write_bytes(b"header" + swapped + b"tail")

            result = correlate([fxobj], shader_directory, 16)

        self.assertEqual(result["summary"]["matchedShaderCount"], 1)
        self.assertEqual(
            result["shaders"][0]["matches"],
            [
                {
                    "fxobj": "rivers.fxobj",
                    "encoding": "dword-byte-swapped",
                    "offsets": [6],
                }
            ],
        )

    def test_same_hash_across_stages_counts_each_shader(self) -> None:
        shader = bytes(range(12))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader_directory = root / "shaders"
            shader_directory.mkdir()
            self.write_shader(shader_directory, "0123456789ABCDEF", "vert", shader)
            self.write_shader(shader_directory, "0123456789ABCDEF", "frag", shader)
            fxobj = root / "water.fxobj"
            fxobj.write_bytes(b"prefix" + shader + b"suffix")

            result = correlate([fxobj], shader_directory, 16)

        self.assertEqual(result["summary"]["matchedShaderCount"], 2)
        self.assertEqual(
            [shader_result["stage"] for shader_result in result["shaders"]],
            ["frag", "vert"],
        )
        self.assertTrue(
            all(shader_result["matches"] for shader_result in result["shaders"])
        )

    def test_reports_unmatched_shader(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader_directory = root / "shaders"
            shader_directory.mkdir()
            self.write_shader(
                shader_directory, "0000000000000001", "frag", bytes(range(12))
            )
            fxobj = root / "terrain.fxobj"
            fxobj.write_bytes(b"not the shader")

            result = correlate([fxobj], shader_directory, 16)

        self.assertEqual(result["summary"]["matchedShaderCount"], 0)
        self.assertEqual(result["shaders"][0]["matches"], [])

    def test_rejects_short_shader_dump(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader_directory = root / "shaders"
            shader_directory.mkdir()
            self.write_shader(
                shader_directory, "0123456789ABCDEF", "vert", bytes(range(8))
            )
            fxobj = root / "water.fxobj"
            fxobj.write_bytes(bytes(range(12)))

            with self.assertRaisesRegex(ValueError, "smaller than 12 bytes"):
                correlate([fxobj], shader_directory, 16)

    def test_rejects_duplicate_fxobj_basenames(self) -> None:
        shader = bytes(range(12))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader_directory = root / "shaders"
            shader_directory.mkdir()
            self.write_shader(shader_directory, "0123456789ABCDEF", "vert", shader)
            first = root / "one" / "shared.fxobj"
            case_variant = root / "one" / "Shared.fxobj"
            second = root / "two" / "shared.fxobj"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_bytes(b"first" + shader)
            second.write_bytes(b"second" + shader)
            fxobj = root / "shared.fxobj"
            fxobj.write_bytes(b"prefix" + shader)
            case_variant.write_bytes(b"first" + shader)
            for label, paths in (
                ("basename", [first, second]),
                ("same-path", [fxobj, fxobj]),
                ("case-variant", [case_variant, second]),
            ):
                with self.subTest(case=label):
                    with self.assertRaisesRegex(
                        ValueError, "duplicate FX object basename"
                    ):
                        correlate(paths, shader_directory, 16)

    def test_overlapping_offsets_and_cap(self) -> None:
        for maximum, expected in ((3, [0, 1, 2]), (2, [0, 1])):
            with self.subTest(maximum=maximum):
                self.assertEqual(find_offsets(b"aaaa", b"aa", maximum), expected)

    def test_nonpositive_match_limit(self) -> None:
        for maximum in (0, -1):
            with self.subTest(maximum=maximum):
                with self.assertRaisesRegex(
                    ValueError, "maximum_matches must be positive"
                ):
                    correlate([], REPO, maximum)

    def test_shader_without_distinct_swapped_variant(self) -> None:
        for label, shader, swapped in (
            ("unaligned", b"abcdefghijklm", None),
            ("unchanged", b"abbaabbaabba", b"abbaabbaabba"),
        ):
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temporary:
                self.assertEqual(swap_dword_bytes(shader), swapped)
                root = Path(temporary)
                self.write_shader(root, "0123456789ABCDEF", "vert", shader)
                fxobj = root / "water.fxobj"
                fxobj.write_bytes(shader)
                result = correlate([fxobj], root, 16)
                self.assertEqual(
                    result["shaders"][0]["matches"],
                    [{"fxobj": "water.fxobj", "encoding": "raw", "offsets": [0]}],
                )

    def test_cli_require_all(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shader = bytes(range(12))
            self.write_shader(root, "0000000000000001", "frag", shader)
            fxobj = root / "terrain.fxobj"
            for label, contents, status, matched in (
                ("matched", shader, 0, 1),
                ("unmatched", b"not the shader", 1, 0),
            ):
                with self.subTest(case=label):
                    fxobj.write_bytes(contents)
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-B",
                            str(REPO / "tools" / "correlate_fxobj_shaders.py"),
                            "--fxobj",
                            str(fxobj),
                            "--shader-directory",
                            str(root),
                            "--require-all",
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, status, result.stderr)
                    self.assertEqual(
                        json.loads(result.stdout)["summary"]["matchedShaderCount"],
                        matched,
                    )


if __name__ == "__main__":
    unittest.main()
