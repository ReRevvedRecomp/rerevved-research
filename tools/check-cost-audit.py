#!/usr/bin/env python3
"""Check bounded gameplay-cost formula models against independent expectations.

Each model covers one rule documented in docs/reference/gameplay/gameplay-cost-arithmetic.md:
rush cost, the AI unit-choice rush valuation, fleet sale value, technology cost,
road cost and Gold reserve interest. A model compares the native integer
arithmetic with a rational or literal expectation over small supplied input
ranges, asserts the expected disagreements and agreements, and prints case and
difference counts. The JSON report also records the SHA-256 of the manifests
that own the formulas.

Limits: this does not execute guest instructions and does not check that the
native arithmetic was read correctly; the manifests and their address evidence
supply that premise. The input ranges are chosen for analysis, so they do not
show which combinations occur in play, and negative or overflowing inputs are
not covered.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE_MANIFESTS = (
    "rush-cost-producer.json",
    "production-cost-ownership.json",
    "unit-sale-refund-value.json",
    "building-wonder-cost-identities.json",
    "building-wonder-cost-modifier-branches.json",
    "road-build-cost.json",
    "technology-research-cost.json",
    "gold-reserve-interest.json",
)
REPORT_KEYS = ("rush", "ai", "fleet", "technology", "controls")


def trunc0(value: Fraction) -> int:
    return int(value)


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def check_models() -> dict:
    # These four factors represent accepted examples, not the complete unit table.
    factors = (2, 4, 5, 10)
    rush_cases = ai_cases = rush_differences = ai_differences = 0
    for factor in factors:
        full_cost = factor * 10 // 2
        for era in range(4):
            for bonus25 in (False, True):
                numerator = (2 if bonus25 else 1) * era + 2
                for bonus35 in (False, True):
                    divisor = 2 if bonus35 else 1
                    native_rate = numerator // divisor
                    for invested in range(full_cost + 1):
                        remaining = full_cost - invested
                        native = native_rate * remaining
                        proposed = ceil_fraction(
                            Fraction(numerator * remaining, divisor)
                        )
                        assert 0 <= native <= proposed
                        assert (remaining != 0) or (native == proposed == 0)
                        rush_cases += 1
                        rush_differences += native != proposed

                        # AIUnitChoiceEvaluate subtracts before the final half;
                        # the human producer subtracts from the completed unit cost.
                        ai_value = trunc0(
                            Fraction(native_rate * (factor * 10 - invested), 2)
                        )
                        assert ai_value >= native
                        ai_cases += 1
                        ai_differences += ai_value != native

    assert (3 // 2) * 10 == 10
    assert ceil_fraction(Fraction(3 * 10, 2)) == 15
    assert (3 // 2) * 2 == 2
    assert ceil_fraction(Fraction(3 * 2, 2)) == 3
    assert trunc0(Fraction(2 * (2 * 10 - 2), 2)) == 18
    assert 2 * (trunc0(Fraction(2 * 10, 2)) - 2) == 16

    fleet_cases = fleet_differences = 0
    for classifier in (1, 2):
        for carrier_multiplier in (1, 3):
            for passenger_multiplier in (1, 3):
                for passengers in (0, 1, 10):
                    native = 5 * classifier * carrier_multiplier * (6 + passengers * 5)
                    per_record = (
                        5
                        * classifier
                        * (
                            carrier_multiplier * 6
                            + passengers * passenger_multiplier * 5
                        )
                    )
                    assert (native == per_record) == (
                        passengers == 0 or carrier_multiplier == passenger_multiplier
                    )
                    fleet_cases += 1
                    fleet_differences += native != per_record
    assert 5 * 3 * (6 + 5) == 165
    assert 5 * (3 * 6 + 5) == 115

    # Each expected value specifies an alternative independently with Fraction.
    def subtract_half(value: int) -> int:
        return value - trunc0(Fraction(value, 2))

    assert subtract_half(5) == 3
    assert trunc0(Fraction(15, 2)) == 7  # Roads use direct division.
    assert 4 * subtract_half(9) == 20
    assert subtract_half(4 * 9) == 18
    assert subtract_half(subtract_half(subtract_half(270))) == 34
    assert trunc0(Fraction(270, 8)) == 33
    tech_cases = tech_differences = 0
    for base in range(2, 21):
        for global_value in range(2, 13):
            for multiplier in (15, 10, 8, 5):
                native = multiplier * trunc0(Fraction(6 * base, global_value + 6))
                late_division = trunc0(
                    Fraction(6 * base * multiplier, global_value + 6)
                )
                assert 0 <= late_division - native < multiplier
                tech_cases += 1
                tech_differences += native != late_division
    road_cases = 0
    for factor in range(1, 5):
        for scalar in range(4):
            for active in (False, True):
                base = factor * (scalar + 2) * 5
                road = trunc0(Fraction(base, 2)) if active else base
                assert road == (base // 2 if active else base)
                road_cases += 1
    interest_cases = 0
    for reserve in range(201):
        native = (reserve + 25) // 50
        nearest = Fraction(reserve, 50) + Fraction(1, 2)
        assert native == nearest.numerator // nearest.denominator
        interest_cases += 1

    return {
        "evidenceKind": "bounded authored formula models, not guest execution",
        "domains": {
            "unitFactors": list(factors),
            "productionScalar": 10,
            "era": [0, 3],
            "invested": "0 through the example unit's full production cost",
            "bonusGates": "all four supplied combinations; retail coactivation is not asserted",
            "fleet": "Galleon factor 6, Spy factor 5; both classifier and own-multiplier alternatives; 0/1/10 passengers",
        },
        "rush": {
            "cases": rush_cases,
            "differencesFromProposedCeilingPolicy": rush_differences,
            "interpretation": "reproduces the known early-division defect under supplied gates",
        },
        "ai": {
            "cases": ai_cases,
            "differencesFromNativeHumanRush": ai_differences,
            "interpretation": "candidate local valuation mismatch; live candidate/current-item identity, retention and decision effects remain unproved",
        },
        "fleet": {
            "cases": fleet_cases,
            "differencesFromPerRecordPolicy": fleet_differences,
            "interpretation": "reproduces known carrier-multiplier propagation; per-record valuation is an explicit correction policy",
        },
        "technology": {
            "cases": tech_cases,
            "differencesFromLateDivision": tech_differences,
            "domain": "supplied B=2..20, g=2..12, M=15/10/8/5; all scaling gates supplied active",
            "interpretation": "precision candidate; multiplier units, intended rounding and live joint inputs are unknown",
        },
        "controls": {
            "roadCases": road_cases,
            "interestCases": interest_cases,
            "mismatches": 0,
            "interpretation": "small supplied-input formula checks against independent rational expectations, not guest execution or all-consumer parity",
        },
    }


def build_report(repo: Path) -> dict:
    result = check_models()
    result["sources"] = {
        f"manifests/{name}": hashlib.sha256(
            (repo / "manifests" / name).read_bytes()
        ).hexdigest()
        for name in SOURCE_MANIFESTS
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--research-root",
        type=Path,
        default=REPO,
        help="checkout holding manifests/ (default: this repository)",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="new JSON report path; an existing file is never overwritten",
    )
    args = parser.parse_args(argv)
    if args.out.exists():
        print(f"error: refusing to overwrite {args.out}", file=sys.stderr)
        return 2
    try:
        result = build_report(args.research_root)
        with args.out.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({key: result[key] for key in REPORT_KEYS}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
