from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CIVILIZATION_HEADERS = (
    "civ_id",
    "internal_name",
    "display_name",
    "leader",
    "starting_bonus_id",
    "starting_bonus",
)
BONUS_HEADERS = ("bonus_id", "effect")
ERA_NAMES = ("Ancient", "Medieval", "Industrial", "Modern")
BONUS_TABLE_BEGIN = "<!-- civilization-bonus-map:begin -->"
BONUS_TABLE_END = "<!-- civilization-bonus-map:end -->"
ID_TABLE_BEGIN = "<!-- civilization-era-id-map:begin -->"
ID_TABLE_END = "<!-- civilization-era-id-map:end -->"
ACHIEVEMENT_TABLE_BEGIN = "<!-- achievement-catalog:begin -->"
ACHIEVEMENT_TABLE_END = "<!-- achievement-catalog:end -->"
ACHIEVEMENT_IDS = tuple(range(5, 55))
ACHIEVEMENT_ROOT_KEYS = frozenset({"schemaVersion", "image", "source", "achievements"})
ACHIEVEMENT_SOURCE_KEYS = frozenset(
    {
        "titleId",
        "languageId",
        "language",
        "format",
        "extractor",
        "extractorVersion",
        "extractorSha256",
        "achievementCount",
        "gamerscoreTotal",
    }
)
ACHIEVEMENT_ROW_KEYS = frozenset(
    {
        "id",
        "name",
        "description",
        "unachievedDescription",
        "gamerscore",
        "imageId",
        "unlockTrigger",
    }
)
ACHIEVEMENT_TRIGGER_KEYS = frozenset({"status", "evidence"})
ACHIEVEMENT_STATUSES = frozenset({"needs_mapping", "mapped"})


class ReferenceDataError(ValueError):
    pass


@dataclass(frozen=True)
class Civilization:
    civ_id: int
    internal_name: str
    display_name: str
    leader: str
    starting_bonus: str


@dataclass(frozen=True)
class CivilizationRow:
    index: int
    name: str
    bonuses: tuple[int, int, int, int]


@dataclass(frozen=True)
class Achievement:
    achievement_id: int
    name: str
    description: str
    unachieved_description: str
    gamerscore: int
    image_id: int
    trigger_status: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class ReferenceData:
    civilizations: tuple[Civilization, ...]
    bonus_effects: dict[int, str]
    manifest_rows: tuple[CivilizationRow, ...]
    achievements: tuple[Achievement, ...] = ()


def _read_csv(
    path: Path,
    headers: tuple[str, ...],
    allow_empty: frozenset[str] = frozenset(),
) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            if tuple(reader.fieldnames or ()) != headers:
                raise ReferenceDataError(
                    f"{path.name}: expected headers {','.join(headers)}"
                )
            rows = list(reader)
    except csv.Error as error:
        raise ReferenceDataError(f"{path.name}: malformed CSV: {error}") from error

    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ReferenceDataError(f"{path.name}:{row_number}: extra CSV field")
        for header in headers:
            value = row.get(header)
            if value is None or (not value and header not in allow_empty):
                raise ReferenceDataError(
                    f"{path.name}:{row_number}: {header} is required"
                )
            if value != value.strip():
                raise ReferenceDataError(
                    f"{path.name}:{row_number}: {header} has outer whitespace"
                )
            if "|" in value or "\n" in value or "\r" in value:
                raise ReferenceDataError(
                    f"{path.name}:{row_number}: {header} is not Markdown-safe"
                )
            markers = (
                BONUS_TABLE_BEGIN,
                BONUS_TABLE_END,
                ID_TABLE_BEGIN,
                ID_TABLE_END,
            )
            if any(marker in value for marker in markers):
                raise ReferenceDataError(
                    f"{path.name}:{row_number}: {header} contains a generated marker"
                )
    return rows


def _parse_id(value: str, location: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ReferenceDataError(f"{location}: expected decimal integer") from error
    if str(parsed) != value or parsed < 0:
        raise ReferenceDataError(f"{location}: expected canonical nonnegative integer")
    return parsed


def _load_civilizations(path: Path) -> tuple[Civilization, ...]:
    raw_rows = _read_csv(
        path, CIVILIZATION_HEADERS, allow_empty=frozenset({"starting_bonus_id"})
    )
    if any(row["starting_bonus_id"] for row in raw_rows):
        raise ReferenceDataError(
            "civilizations.csv: starting_bonus_id must remain blank until recovered"
        )
    rows = tuple(
        Civilization(
            civ_id=_parse_id(row["civ_id"], f"{path.name}:{index}:civ_id"),
            internal_name=row["internal_name"],
            display_name=row["display_name"],
            leader=row["leader"],
            starting_bonus=row["starting_bonus"],
        )
        for index, row in enumerate(raw_rows, start=2)
    )
    expected_ids = tuple(range(16))
    actual_ids = tuple(row.civ_id for row in rows)
    if actual_ids != expected_ids:
        raise ReferenceDataError(
            "civilizations.csv: civ_id values must be unique and ordered 0 through 15"
        )
    for field_name in ("internal_name", "display_name"):
        values = tuple(getattr(row, field_name) for row in rows)
        if len(values) != len(set(values)):
            raise ReferenceDataError(f"civilizations.csv: duplicate {field_name} value")
    return rows


def _load_bonus_effects(path: Path) -> dict[int, str]:
    raw_rows = _read_csv(path, BONUS_HEADERS)
    effects: dict[int, str] = {}
    for row_number, row in enumerate(raw_rows, start=2):
        bonus_id = _parse_id(row["bonus_id"], f"{path.name}:{row_number}:bonus_id")
        if bonus_id == 0:
            raise ReferenceDataError(
                f"{path.name}:{row_number}: bonus_id must be positive"
            )
        if bonus_id in effects:
            raise ReferenceDataError(
                f"{path.name}:{row_number}: duplicate bonus_id {bonus_id}"
            )
        effects[bonus_id] = row["effect"]
    if list(effects) != sorted(effects):
        raise ReferenceDataError(
            "era-bonus-definitions.csv: bonus_id values must be numerically ordered"
        )
    return effects


def _load_manifest_rows(path: Path) -> tuple[CivilizationRow, ...]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        shape = document["storage"]["shape"]
        raw_rows = document["storage"]["rows"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise ReferenceDataError(f"{path.name}: invalid storage.rows") from error

    expected_shape = {
        "civilizations": 16,
        "erasPerCivilization": 4,
        "entrySize": 4,
        "rowSize": 16,
        "totalSize": 256,
    }
    if shape != expected_shape:
        raise ReferenceDataError(f"{path.name}: unexpected storage.shape")
    if not isinstance(raw_rows, list):
        raise ReferenceDataError(f"{path.name}: storage.rows must be a list")

    rows: list[CivilizationRow] = []
    for raw in raw_rows:
        try:
            index = raw["index"]
            name = raw["name"]
            bonuses = tuple(raw["bonuses"])
        except (KeyError, TypeError) as error:
            raise ReferenceDataError(
                f"{path.name}: malformed civilization row"
            ) from error
        if type(index) is not int or not isinstance(name, str):
            raise ReferenceDataError(f"{path.name}: invalid row index or name")
        if len(bonuses) != len(ERA_NAMES) or not all(
            type(value) is int and value > 0 for value in bonuses
        ):
            raise ReferenceDataError(
                f"{path.name}: row {index} must have four positive bonus IDs"
            )
        rows.append(CivilizationRow(index, name, bonuses))

    if tuple(row.index for row in rows) != tuple(range(16)):
        raise ReferenceDataError(
            f"{path.name}: row indexes must be unique and ordered 0 through 15"
        )
    return tuple(rows)


def _resolve_json_pointer(document: Any, pointer: str, location: str) -> Any:
    if not pointer.startswith("/"):
        raise ReferenceDataError(f"{location}: evidence JSON pointer must start with /")
    current = document
    for token in pointer[1:].split("/"):
        if "~" in token and not re.fullmatch(r"(?:[^~]|~[01])*", token):
            raise ReferenceDataError(
                f"{location}: evidence JSON pointer has invalid escape"
            )
        token = token.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, list):
                if not re.fullmatch(r"0|[1-9][0-9]*", token):
                    raise KeyError(token)
                current = current[int(token)]
            elif isinstance(current, dict):
                current = current[token]
            else:
                raise KeyError(token)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise ReferenceDataError(
                f"{location}: evidence JSON pointer does not resolve"
            ) from error
    return current


def _resolve_evidence_locator(locator: str, repo: Path, location: str) -> None:
    if not locator or "#" not in locator or "\\" in locator:
        raise ReferenceDataError(
            f"{location}: evidence locator must be a relative JSON file plus pointer"
        )
    relative_file, pointer = locator.split("#", 1)
    if not relative_file or not pointer.startswith("/"):
        raise ReferenceDataError(
            f"{location}: evidence locator must be a relative JSON file plus pointer"
        )
    relative_path = Path(relative_file)
    if relative_path.is_absolute() or relative_path.suffix.lower() != ".json":
        raise ReferenceDataError(
            f"{location}: evidence locator must name a relative JSON file"
        )

    repo_root = repo.resolve()
    manifests_root = repo_root / "manifests"
    evidence_path = (repo / "data" / relative_path).resolve()
    if not evidence_path.is_relative_to(manifests_root):
        raise ReferenceDataError(f"{location}: evidence file must be in manifests")
    if not evidence_path.is_file():
        raise ReferenceDataError(f"{location}: evidence file does not resolve")

    try:
        document = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReferenceDataError(
            f"{location}: evidence file is not valid JSON"
        ) from error
    _resolve_json_pointer(document, pointer, location)


def _load_achievement_evidence(
    raw_evidence: Any, repo: Path, location: str
) -> tuple[str, ...]:
    if not isinstance(raw_evidence, list):
        raise ReferenceDataError(f"{location}: evidence must be a list")

    locators: list[str] = []
    for index, raw in enumerate(raw_evidence):
        evidence_location = f"{location}[{index}]"
        if not isinstance(raw, str):
            raise ReferenceDataError(f"{evidence_location}: locator must be a string")
        _resolve_evidence_locator(raw, repo, evidence_location)
        locators.append(raw)
    return tuple(locators)


def _load_achievements(repo: Path) -> tuple[Achievement, ...]:
    path = repo / "data" / "achievements.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReferenceDataError(f"{path.name}: invalid JSON") from error
    if not isinstance(document, dict):
        raise ReferenceDataError(f"{path.name}: root must be an object")
    if set(document) != ACHIEVEMENT_ROOT_KEYS:
        raise ReferenceDataError(f"{path.name}: invalid root fields")
    if type(document.get("schemaVersion")) is not int or document["schemaVersion"] != 1:
        raise ReferenceDataError(f"{path.name}: schemaVersion must be 1")
    if document.get("image") != "../manifests/image.json":
        raise ReferenceDataError(f"{path.name}: image must be ../manifests/image.json")

    source = document.get("source")
    if not isinstance(source, dict) or set(source) != ACHIEVEMENT_SOURCE_KEYS:
        raise ReferenceDataError(f"{path.name}: invalid source metadata")
    expected_source = {
        "titleId": "0x545407E5",
        "languageId": 1,
        "language": "English",
        "format": "XDBF/XACH",
        "achievementCount": 50,
        "gamerscoreTotal": 1000,
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected or (
            isinstance(expected, int) and type(source.get(key)) is not int
        ):
            raise ReferenceDataError(f"{path.name}: unexpected source.{key}")
    for key in ("extractor", "extractorVersion"):
        value = source.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ReferenceDataError(f"{path.name}: source.{key} must be nonempty")
    version = source["extractorVersion"]
    if any(character.isspace() for character in version):
        raise ReferenceDataError(
            f"{path.name}: source.extractorVersion must be a version"
        )
    digest = source.get("extractorSha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
        raise ReferenceDataError(f"{path.name}: source.extractorSha256 must be SHA-256")

    raw_rows = document.get("achievements")
    if not isinstance(raw_rows, list) or len(raw_rows) != len(ACHIEVEMENT_IDS):
        raise ReferenceDataError(f"{path.name}: achievements must contain 50 rows")
    ids: list[int] = []
    for index, raw in enumerate(raw_rows):
        location = f"{path.name}:achievements[{index}]"
        if not isinstance(raw, dict) or set(raw) != ACHIEVEMENT_ROW_KEYS:
            raise ReferenceDataError(f"{location}: invalid achievement fields")
        achievement_id = raw.get("id")
        if type(achievement_id) is not int:
            raise ReferenceDataError(f"{location}: id must be an integer")
        ids.append(achievement_id)
    if tuple(ids) != ACHIEVEMENT_IDS:
        raise ReferenceDataError(
            f"{path.name}: achievement IDs must be unique and ordered 5 through 54"
        )

    rows: list[Achievement] = []
    image_ids: set[int] = set()
    for index, raw in enumerate(raw_rows):
        location = f"{path.name}:achievements[{index}]"
        for field in ("name", "description", "unachievedDescription"):
            value = raw[field]
            if not isinstance(value, str) or not value:
                raise ReferenceDataError(f"{location}: {field} must be nonempty text")
        gamerscore = raw["gamerscore"]
        if type(gamerscore) is not int or gamerscore <= 0:
            raise ReferenceDataError(
                f"{location}: gamerscore must be a positive integer"
            )
        image_id = raw["imageId"]
        if type(image_id) is not int or image_id < 0:
            raise ReferenceDataError(
                f"{location}: imageId must be a nonnegative integer"
            )
        if image_id in image_ids:
            raise ReferenceDataError(f"{location}: duplicate imageId {image_id}")
        if image_id == raw["id"]:
            raise ReferenceDataError(f"{location}: imageId must differ from id")
        image_ids.add(image_id)

        trigger = raw["unlockTrigger"]
        if not isinstance(trigger, dict) or set(trigger) != ACHIEVEMENT_TRIGGER_KEYS:
            raise ReferenceDataError(f"{location}: invalid unlockTrigger")
        status = trigger.get("status")
        if not isinstance(status, str) or status not in ACHIEVEMENT_STATUSES:
            raise ReferenceDataError(f"{location}: invalid unlockTrigger.status")
        evidence = _load_achievement_evidence(
            trigger.get("evidence"), repo, f"{location}:unlockTrigger.evidence"
        )
        if status == "mapped" and not evidence:
            raise ReferenceDataError(
                f"{location}: mapped unlockTrigger requires resolving evidence"
            )
        rows.append(
            Achievement(
                achievement_id=raw["id"],
                name=raw["name"],
                description=raw["description"],
                unachieved_description=raw["unachievedDescription"],
                gamerscore=gamerscore,
                image_id=image_id,
                trigger_status=status,
                evidence=evidence,
            )
        )
    if len(image_ids) != len(ACHIEVEMENT_IDS):
        raise ReferenceDataError(f"{path.name}: image IDs must be unique")
    if sum(row.gamerscore for row in rows) != source["gamerscoreTotal"]:
        raise ReferenceDataError(f"{path.name}: gamerscore total does not match source")
    return tuple(rows)


def load_reference_data(repo: Path) -> ReferenceData:
    civilizations = _load_civilizations(repo / "data" / "civilizations.csv")
    bonus_effects = _load_bonus_effects(repo / "data" / "era-bonus-definitions.csv")
    manifest_rows = _load_manifest_rows(
        repo / "manifests" / "civilization-bonus-storage.json"
    )

    for civilization, manifest_row in zip(civilizations, manifest_rows, strict=True):
        if civilization.internal_name != manifest_row.name:
            raise ReferenceDataError(
                f"civilization {civilization.civ_id}: internal name "
                f"{civilization.internal_name!r} disagrees with manifest "
                f"{manifest_row.name!r}"
            )

    assigned_ids = {bonus_id for row in manifest_rows for bonus_id in row.bonuses}
    defined_ids = set(bonus_effects)
    missing_ids = sorted(assigned_ids - defined_ids)
    unused_ids = sorted(defined_ids - assigned_ids)
    if missing_ids:
        raise ReferenceDataError(
            "era-bonus-definitions.csv: missing assigned IDs "
            + ", ".join(map(str, missing_ids))
        )
    if unused_ids:
        raise ReferenceDataError(
            "era-bonus-definitions.csv: unused IDs " + ", ".join(map(str, unused_ids))
        )

    achievements = _load_achievements(repo)
    return ReferenceData(civilizations, bonus_effects, manifest_rows, achievements)


def _display_label(civilization: Civilization) -> str:
    if civilization.display_name == civilization.internal_name:
        return civilization.display_name
    return f"{civilization.display_name} (`{civilization.internal_name}` internally)"


def _render_bonus_table(data: ReferenceData) -> str:
    lines = [
        "| Civilization | Leader | UA | Ancient UEA | Medieval UEA | Industrial UEA | Modern UEA |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for civilization, manifest_row in zip(
        data.civilizations, data.manifest_rows, strict=True
    ):
        effects = [data.bonus_effects[bonus_id] for bonus_id in manifest_row.bonuses]
        cells = [
            _display_label(civilization),
            civilization.leader,
            civilization.starting_bonus,
            *effects,
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _render_id_table(data: ReferenceData) -> str:
    lines = [
        "| Civ ID | Internal name | Ancient UEA | Medieval UEA | Industrial UEA | Modern UEA |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in data.manifest_rows:
        cells = [str(row.index), row.name, *(str(value) for value in row.bonuses)]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _markdown_cell(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r\n", "<br>")
        .replace("\r", "<br>")
        .replace("\n", "<br>")
    )


def _render_achievement_table(data: ReferenceData) -> str:
    lines = [
        "| ID | Name | Unlocked description | Locked description | G | Icon ID | Trigger mapping |",
        "| ---: | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in data.achievements:
        mapping = row.trigger_status
        if row.evidence:
            mapping += "<br>" + "<br>".join(row.evidence)
        cells = [
            str(row.achievement_id),
            row.name,
            row.description,
            row.unachieved_description,
            str(row.gamerscore),
            str(row.image_id),
            mapping,
        ]
        lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")
    return "\n".join(lines)


def _replace_region(
    text: str,
    begin: str,
    end: str,
    body: str,
    document_name: str = "reference document",
) -> str:
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ReferenceDataError(
            f"{document_name}: expected one {begin} and one {end} marker"
        )
    if text.index(begin) >= text.index(end):
        raise ReferenceDataError(
            f"{document_name}: crossed generated markers {begin} and {end}"
        )
    prefix, remainder = text.split(begin, 1)
    current, suffix = remainder.split(end, 1)
    if not current.startswith("\n") or not current.endswith("\n"):
        raise ReferenceDataError(f"{document_name}: malformed generated region {begin}")
    return prefix + begin + "\n" + body + "\n" + end + suffix


def _render_civilization_document(text: str, data: ReferenceData) -> str:
    text = _replace_region(
        text,
        BONUS_TABLE_BEGIN,
        BONUS_TABLE_END,
        _render_bonus_table(data),
        "civilization-bonuses.md",
    )
    return _replace_region(
        text,
        ID_TABLE_BEGIN,
        ID_TABLE_END,
        _render_id_table(data),
        "civilization-bonuses.md",
    )


def _render_achievement_document(text: str, data: ReferenceData) -> str:
    return _replace_region(
        text,
        ACHIEVEMENT_TABLE_BEGIN,
        ACHIEVEMENT_TABLE_END,
        _render_achievement_table(data),
        "achievements.md",
    )


def render_document(text: str, data: ReferenceData) -> str:
    if BONUS_TABLE_BEGIN in text or BONUS_TABLE_END in text:
        text = _render_civilization_document(text, data)
    if ACHIEVEMENT_TABLE_BEGIN in text or ACHIEVEMENT_TABLE_END in text:
        text = _render_achievement_document(text, data)
    return text


def check_repository(repo: Path) -> ReferenceData:
    data = load_reference_data(repo)
    documents = (
        (
            repo / "docs" / "reference" / "civilization-bonuses.md",
            _render_civilization_document,
        ),
        (
            repo / "docs" / "reference" / "achievements.md",
            _render_achievement_document,
        ),
    )
    for path, renderer in documents:
        current = path.read_text(encoding="utf-8")
        expected = renderer(current, data)
        if current != expected:
            raise ReferenceDataError(
                f"{path.name}: rendered tables are stale; run "
                "python tools/reference_data.py --write"
            )
    return data


def write_repository(repo: Path) -> tuple[ReferenceData, bool]:
    data = load_reference_data(repo)
    documents = (
        (
            repo / "docs" / "reference" / "civilization-bonuses.md",
            _render_civilization_document,
        ),
        (
            repo / "docs" / "reference" / "achievements.md",
            _render_achievement_document,
        ),
    )
    rendered: list[tuple[Path, str, str]] = []
    for path, renderer in documents:
        current = path.read_text(encoding="utf-8")
        rendered.append((path, current, renderer(current, data)))
    changed = False
    for path, current, expected in rendered:
        if current != expected:
            with path.open("w", encoding="utf-8", newline="\n") as stream:
                stream.write(expected)
            changed = True
    return data, changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate or render normalized reference data"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite the generated Markdown regions; without this option, check them only",
    )
    args = parser.parse_args()

    try:
        if args.write:
            data, changed = write_repository(args.repo.resolve())
            action = "updated" if changed else "unchanged"
        else:
            data = check_repository(args.repo.resolve())
            action = "passed"
    except (OSError, ReferenceDataError) as error:
        parser.exit(1, f"reference-data: {error}\n")

    print(
        "reference-data: "
        f"{action} civilizations={len(data.civilizations)} "
        f"eraBonuses={len(data.bonus_effects)} "
        f"achievements={len(data.achievements)} "
        f"achievementGamerscore={sum(row.gamerscore for row in data.achievements)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
