from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from correlate_fxobj_shaders import correlate, swap_dword_bytes  # noqa: E402


class CorrelateFxobjShadersTests(unittest.TestCase):
    def write_shader(self, directory: Path, shader_hash: str, stage: str, data: bytes) -> None:
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
        swapped = swap_dword_bytes(shader)
        self.assertIsNotNone(swapped)
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


if __name__ == "__main__":
    unittest.main()
