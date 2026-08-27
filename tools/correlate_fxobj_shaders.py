#!/usr/bin/env python3
"""Correlate ReXGlue shader dumps with opaque Xbox 360 FX objects."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SHADER_DUMP_RE = re.compile(
    r"^shader_([0-9a-fA-F]{16})\.ucode\.bin\.(vert|frag)$"
)
MIN_SHADER_BYTES = 12


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def swap_dword_bytes(data: bytes) -> bytes | None:
    if len(data) % 4:
        return None
    return b"".join(data[offset : offset + 4][::-1] for offset in range(0, len(data), 4))


def find_offsets(haystack: bytes, needle: bytes, maximum: int) -> list[int]:
    offsets: list[int] = []
    start = 0
    while len(offsets) < maximum:
        offset = haystack.find(needle, start)
        if offset < 0:
            break
        offsets.append(offset)
        start = offset + 1
    return offsets


def load_shader_dumps(shader_directory: Path) -> list[dict[str, object]]:
    shaders: list[dict[str, object]] = []
    identities: set[tuple[str, str]] = set()
    for path in sorted(shader_directory.iterdir(), key=lambda item: item.name.lower()):
        match = SHADER_DUMP_RE.fullmatch(path.name)
        if match is None or not path.is_file():
            continue
        data = path.read_bytes()
        if len(data) < MIN_SHADER_BYTES:
            raise ValueError(
                f"shader dump is smaller than {MIN_SHADER_BYTES} bytes: {path.name}"
            )
        identity = (match.group(1).upper(), match.group(2))
        if identity in identities:
            raise ValueError(
                f"duplicate shader identity {identity[0]} {identity[1]}"
            )
        identities.add(identity)
        shaders.append(
            {
                "path": path,
                "hash": identity[0],
                "stage": identity[1],
                "data": data,
                "sha256": sha256(data),
            }
        )
    if not shaders:
        raise ValueError(f"no ReXGlue shader dumps found in {shader_directory}")
    return shaders


def correlate(
    fxobj_paths: list[Path], shader_directory: Path, maximum_matches: int
) -> dict[str, object]:
    if maximum_matches < 1:
        raise ValueError("maximum_matches must be positive")
    shaders = load_shader_dumps(shader_directory)
    assets: list[dict[str, object]] = []
    for path in sorted(fxobj_paths, key=lambda item: item.name.lower()):
        data = path.read_bytes()
        assets.append(
            {
                "name": path.name,
                "bytes": len(data),
                "sha256": sha256(data),
                "data": data,
            }
        )

    results: list[dict[str, object]] = []
    matched_identities: set[tuple[str, str]] = set()
    for shader in shaders:
        raw = shader["data"]
        assert isinstance(raw, bytes)
        variants = [("raw", raw)]
        swapped = swap_dword_bytes(raw)
        if swapped is not None and swapped != raw:
            variants.append(("dword-byte-swapped", swapped))
        matches: list[dict[str, object]] = []
        for asset in assets:
            asset_data = asset["data"]
            assert isinstance(asset_data, bytes)
            for encoding, needle in variants:
                offsets = find_offsets(asset_data, needle, maximum_matches)
                if offsets:
                    matches.append(
                        {
                            "fxobj": asset["name"],
                            "encoding": encoding,
                            "offsets": offsets,
                        }
                    )
        if matches:
            matched_identities.add((str(shader["hash"]), str(shader["stage"])))
        results.append(
            {
                "shaderHash": shader["hash"],
                "stage": shader["stage"],
                "bytes": len(raw),
                "sha256": shader["sha256"],
                "matches": matches,
            }
        )

    return {
        "schemaVersion": 1,
        "fxobjs": [
            {
                "name": asset["name"],
                "bytes": asset["bytes"],
                "sha256": asset["sha256"],
            }
            for asset in assets
        ],
        "shaders": results,
        "summary": {
            "fxobjCount": len(assets),
            "shaderCount": len(shaders),
            "matchedShaderCount": len(matched_identities),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Locate ReXGlue hash-named shader microcode dumps inside opaque FX objects."
        )
    )
    parser.add_argument(
        "--fxobj", action="append", type=Path, required=True, help="Candidate FX object"
    )
    parser.add_argument(
        "--shader-directory",
        type=Path,
        required=True,
        help="Directory containing shader_<hash>.ucode.bin.<stage> files",
    )
    parser.add_argument("--maximum-matches", type=int, default=16)
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="Return failure when any shader does not match a candidate FX object",
    )
    args = parser.parse_args()

    try:
        for path in args.fxobj:
            if not path.is_file():
                raise ValueError(f"FX object is not a file: {path}")
        if not args.shader_directory.is_dir():
            raise ValueError(
                f"shader directory is not a directory: {args.shader_directory}"
            )
        result = correlate(args.fxobj, args.shader_directory, args.maximum_matches)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps(result, indent=2, sort_keys=True))
    summary = result["summary"]
    assert isinstance(summary, dict)
    if args.require_all and summary["matchedShaderCount"] != summary["shaderCount"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
