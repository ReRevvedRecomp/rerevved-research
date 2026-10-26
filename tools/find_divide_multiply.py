#!/usr/bin/env python3
"""Report bounded PPC divide-before-multiply candidates from word dumps."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MAX_RANGES = 8
MAX_INSTRUCTIONS = 256
MAX_WINDOW = 16
WORD_RE = re.compile(
    r"^\s*(?:>\s*)?0x([0-9A-Fa-f]{8}):\s*0x([0-9A-Fa-f]{8})(?:\s+.*)?$"
)
SECTION_RE = re.compile(r"^===\s+0x[0-9A-Fa-f]{8}\s+===$")
PROGRAM_RE = re.compile(r"^Program:\s*(\S.*)$")
BRANCH_XO = {16, 528}
NEUTRAL_XO = {0, 32, 33, 129, 257, 449}
WRITE_XO = {40, 202}
LOGICAL_WRITE_XO = {60, 824, 922}


class ScanError(ValueError):
    """Raised for malformed or incomplete scan evidence."""


@dataclass(frozen=True)
class Range:
    start: int
    end: int

    @property
    def instructions(self) -> int:
        return (self.end - self.start) // 4


def _instruction(
    kind: str,
    operation: str = "",
    dest: int | None = None,
    sources: tuple[int, ...] = (),
    copy_source: int | None = None,
) -> tuple[str, str, int | None, tuple[int, ...], int | None]:
    return kind, operation, dest, sources, copy_source


def _integer(value: str, label: str) -> int:
    try:
        return int(value, 0)
    except ValueError:
        try:
            return int(value, 16)
        except ValueError as exc:
            raise ScanError(f"invalid {label}: {value}") from exc


def _parse_range(value: str) -> Range:
    parts = value.split(":")
    if len(parts) != 2:
        raise ScanError(f"invalid range: {value}")
    start, end = (_integer(part, "range endpoint") for part in parts)
    result = Range(start, end)
    if start % 4 or end % 4 or start >= end:
        raise ScanError(f"range must be aligned and half-open: {value}")
    if result.instructions > MAX_INSTRUCTIONS:
        raise ScanError(f"range exceeds {MAX_INSTRUCTIONS} instructions: {value}")
    return result


def _parse_dump(path: Path) -> tuple[str, dict[int, int]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ScanError(f"cannot read dump {path}: {exc}") from exc
    program: str | None = None
    words: dict[int, int] = {}
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        match = PROGRAM_RE.match(line)
        if match:
            value = match.group(1).strip()
            if program is not None and program != value:
                raise ScanError(f"conflicting program headers in {path}:{number}")
            program = value
            continue
        if line.startswith(("Targets:", "Word radius:")) or SECTION_RE.match(line):
            continue
        match = WORD_RE.match(line)
        if match:
            address, value = int(match.group(1), 16), int(match.group(2), 16)
            previous = words.get(address)
            if previous is not None and previous != value:
                raise ScanError(f"conflicting word rows in {path}:{number}")
            words[address] = value
            continue
        if "0x" in line or ":" in line:
            raise ScanError(f"malformed dump row in {path}:{number}")
        raise ScanError(f"unexpected dump line in {path}:{number}")
    if program is None:
        raise ScanError(f"missing Program header in {path}")
    if not words:
        raise ScanError(f"missing word rows in {path}")
    return program, words


def _load_image(manifest_path: Path, image_path: Path) -> tuple[str, int, bytes]:
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
        analysis = document["analysisProgram"]
        name = analysis["name"]
        base = _integer(str(analysis["imageBase"]), "imageBase")
        size = int(analysis["imageSize"])
        expected = str(analysis["flatImageSha256"]).upper()
        image = image_path.read_bytes()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ScanError(f"invalid image evidence: {exc}") from exc
    actual = hashlib.sha256(image).hexdigest().upper()
    if not isinstance(name, str) or not name:
        raise ScanError("image manifest analysisProgram.name is required")
    if len(image) != size:
        raise ScanError("image size does not match image manifest")
    if actual != expected:
        raise ScanError("image SHA256 does not match image manifest")
    return name, base, image


def _merge_dumps(paths: Iterable[Path], expected: str) -> dict[int, int]:
    merged: dict[int, int] = {}
    for path in paths:
        program, words = _parse_dump(path)
        if program != expected:
            raise ScanError(f"unexpected program header in {path}: {program!r}")
        for address, value in words.items():
            previous = merged.get(address)
            if previous is not None and previous != value:
                raise ScanError(f"conflicting word rows at 0x{address:08X}")
            merged[address] = value
    return merged


def _validate_words(words: dict[int, int], image: bytes, base: int) -> None:
    for address, value in words.items():
        offset = address - base
        if offset < 0 or offset + 4 > len(image):
            raise ScanError(f"address outside image: 0x{address:08X}")
        expected = int.from_bytes(image[offset : offset + 4], "big")
        if value != expected:
            raise ScanError(f"dump word does not match image at 0x{address:08X}")


def _decode(word: int) -> tuple[str, str, int | None, tuple[int, ...], int | None]:
    primary = word >> 26
    rt, ra, rb = (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
    xo = (word >> 1) & 0x3FF
    if primary == 18:
        return _instruction("call" if word & 1 else "branch")
    if primary == 16:
        return _instruction("branch")
    if primary == 19:
        if xo in BRANCH_XO:
            return _instruction("call" if word & 1 else "branch")
        if xo in NEUTRAL_XO:
            return _instruction("neutral")
        if xo in (4, 150):
            return _instruction("trap")
        return _instruction("unknown")
    if primary == 3:
        return _instruction("trap")
    if primary == 7:
        return _instruction("multiply", "mulli", rt, (ra,))
    if primary in (10, 11):
        return _instruction("neutral")
    if primary in (14, 15):
        if primary == 14 and word & 0xFFFF == 0 and ra:
            return _instruction("copy", "mr", rt, (ra,), ra)
        return _instruction("write", "gpr", rt)
    if primary == 21:
        return _instruction("write", "gpr", ra)
    if primary == 24:
        if word & 0xFFFF == 0:
            return _instruction("copy", "mr", ra, (rt,), rt)
        return _instruction("write", "gpr", ra)
    if primary != 31:
        return _instruction("unknown")
    if xo == 459:
        return _instruction("div", "divwu", rt, (ra, rb))
    if xo == 491:
        return _instruction("div", "divw", rt, (ra, rb))
    if xo == 235:
        return _instruction("multiply", "mullw", rt, (ra, rb))
    if xo == 444 and rb == rt:
        return _instruction("copy", "mr", ra, (rt,), rt)
    if xo == 4:
        return _instruction("trap")
    if xo in NEUTRAL_XO:
        return _instruction("neutral")
    if xo in WRITE_XO:
        return _instruction("write", "gpr", rt)
    if xo in LOGICAL_WRITE_XO:
        return _instruction("write", "gpr", ra)
    return _instruction("unknown")


def _scan_range(
    words: dict[int, int], selected: Range
) -> tuple[list[dict], dict[str, int]]:
    provenance: dict[int, tuple[int, str, int, int]] = {}
    candidates: list[dict] = []
    barriers = {
        key: 0
        for key in ("total", "branches", "calls", "unknown", "quotient_overwrites")
    }
    for index, address in enumerate(range(selected.start, selected.end, 4)):
        kind, operation, dest, sources, copy_source = _decode(words[address])
        for register, value in list(provenance.items()):
            if index - value[3] > MAX_WINDOW:
                del provenance[register]
        if kind in ("branch", "call", "unknown"):
            barriers["total"] += 1
            key = (
                "calls"
                if kind == "call"
                else "branches"
                if kind == "branch"
                else "unknown"
            )
            barriers[key] += 1
            provenance.clear()
            continue
        if kind == "multiply":
            seen: set[int] = set()
            for register in sources:
                origin = provenance.get(register)
                if origin is None or origin[0] in seen:
                    continue
                seen.add(origin[0])
                candidates.append(
                    {
                        "divide_address": f"0x{origin[0]:08X}",
                        "multiply_address": f"0x{address:08X}",
                        "operation_pair": f"{origin[1]}->{operation}",
                        "quotient_register": f"r{origin[2]}",
                    }
                )
        if kind == "div":
            if dest in provenance:
                barriers["quotient_overwrites"] += 1
            if dest is not None:
                provenance[dest] = (address, operation, dest, index)
        elif dest is not None:
            if kind == "copy" and copy_source is not None:
                origin = provenance.get(copy_source)
                if origin is None:
                    provenance.pop(dest, None)
                else:
                    provenance[dest] = origin
            else:
                if kind != "multiply" and dest in provenance:
                    barriers["quotient_overwrites"] += 1
                provenance.pop(dest, None)
    candidates.sort(key=lambda item: (item["divide_address"], item["multiply_address"]))
    return candidates, barriers


def scan(
    dump_paths: Iterable[Path],
    image_path: Path,
    manifest_path: Path,
    ranges: Iterable[Range],
) -> dict:
    selected = sorted(ranges, key=lambda item: (item.start, item.end))
    if not selected or len(selected) > MAX_RANGES:
        raise ScanError(f"one through {MAX_RANGES} ranges are required")
    for selected_range in selected:
        if (
            selected_range.start % 4
            or selected_range.end % 4
            or selected_range.start >= selected_range.end
            or selected_range.instructions > MAX_INSTRUCTIONS
        ):
            raise ScanError("range must be aligned, half-open, and bounded")
    if any(
        current.start < previous.end
        for previous, current in zip(selected, selected[1:])
    ):
        raise ScanError("ranges overlap")
    program, base, image = _load_image(manifest_path, image_path)
    words = _merge_dumps(dump_paths, program)
    _validate_words(words, image, base)
    records, candidates = [], []
    barriers = {
        key: 0
        for key in ("total", "branches", "calls", "unknown", "quotient_overwrites")
    }
    for selected_range in selected:
        missing = next(
            (
                address
                for address in range(selected_range.start, selected_range.end, 4)
                if address not in words
            ),
            None,
        )
        if missing is not None:
            raise ScanError(f"missing dump word at 0x{missing:08X}")
        found, counts = _scan_range(words, selected_range)
        candidates.extend(found)
        for key, value in counts.items():
            barriers[key] += value
        records.append(
            {
                "start": f"0x{selected_range.start:08X}",
                "end": f"0x{selected_range.end:08X}",
                "instructions": selected_range.instructions,
                "examined_instructions": selected_range.instructions,
                "recognized_instructions": selected_range.instructions
                - counts["total"],
                "barrier_instructions": counts["total"],
            }
        )
    candidates.sort(key=lambda item: (item["divide_address"], item["multiply_address"]))
    total = sum(item.instructions for item in selected)
    return {
        "image": {
            "program": program,
            "base": f"0x{base:08X}",
            "sha256": hashlib.sha256(image).hexdigest().upper(),
        },
        "ranges": records,
        "coverage": {
            "dump_words": len(words),
            "range_instructions": total,
            "examined_instructions": total,
            "recognized_instructions": total - barriers["total"],
            "missing_instructions": 0,
        },
        "barriers": barriers,
        "candidates": candidates,
        "limits": {
            "candidate_only": True,
            "false_negative_limits": [
                "Only divw/divwu feeding mullw/mulli is recognized.",
                "Branches, calls, unknown instructions, and dataflow beyond the bounded window stop provenance.",
                "The report does not classify a candidate as a gameplay bug.",
            ],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump", action="append", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--image-manifest", required=True, type=Path)
    parser.add_argument("--range", action="append", required=True, dest="ranges")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        ranges = [_parse_range(value) for value in args.ranges]
        result = scan(args.dump, args.image, args.image_manifest, ranges)
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, ScanError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
