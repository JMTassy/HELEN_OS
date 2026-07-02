#!/usr/bin/env python3
"""Governance Yield report -- reads governance_yield_tracker.csv and
computes the two scoring formulas discussed this session, rather than
requiring a manual spreadsheet read every time.

Formula (basic):
    yield = count(rule_change=true OR fixture_added=true) / count(events)

Formula (adjusted, weighted by cost):
    yield_adjusted = (rule_change_count + fixture_count)
                      / (operator_minutes + governance_objects_added)

A refinement reported from a parallel seat this session (unverified
here, recorded as reported -- not independently confirmed against that
seat's own metal): Governance Yield should zero out on BOTH passive
stability (nothing happened, nothing was tested) AND unguided activity
(lots of motion, nothing durable came of it) -- and the Goodhart vector
to watch for is faking external friction to inflate the numerator.
This report does not attempt to detect faked friction; that requires
human judgment on each row, which is why 'source' and 'notes' are
free-text fields, not scored ones.

Usage: python3 temple/autoresearch/governance_yield_report.py
"""
import csv
import os

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "governance_yield_tracker.csv")


def to_bool(s):
    return str(s).strip().lower() == "true"


def to_float(s, default=0.0):
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def main():
    if not os.path.exists(CSV_PATH):
        print(f"no tracker found at {CSV_PATH}")
        return

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("tracker exists but has zero rows -- nothing to report")
        return

    n = len(rows)
    rule_or_fixture = sum(
        1 for r in rows
        if to_bool(r.get("permanent_rule_change")) or to_bool(r.get("test_or_fixture_added"))
    )
    external_events = sum(1 for r in rows if to_bool(r.get("external_user_present")))
    leaks = sum(1 for r in rows if to_bool(r.get("authority_leakage")))
    revocations = sum(1 for r in rows if to_bool(r.get("revocation_used")))
    successful = sum(1 for r in rows if to_bool(r.get("transaction_successful")))
    operator_minutes = sum(to_float(r.get("operator_time_minutes")) for r in rows)

    yield_basic = rule_or_fixture / n if n else 0.0
    yield_adjusted = (
        rule_or_fixture / (operator_minutes + n) if (operator_minutes + n) else 0.0
    )

    print("GOVERNANCE YIELD REPORT")
    print(f"events: {n}")
    print(f"external-user events: {external_events} (0 means the external feedback loop is still not closed -- see LOOPS.md)")
    print(f"rule-strengthening or fixture-adding events: {rule_or_fixture}")
    print(f"yield (basic): {round(yield_basic, 4)}")
    print(f"yield (adjusted, cost-weighted): {round(yield_adjusted, 6)}")
    print(f"authority leakage incidents: {leaks}")
    print(f"revocations used: {revocations}")
    print(f"successful transactions: {successful}/{n}")
    print(f"total operator minutes logged: {operator_minutes}")

    top_note_events = [r for r in rows if r.get("notes", "").strip()]
    if top_note_events:
        print("\nmost recent event:")
        last = rows[-1]
        print(f"  {last.get('date')} | {last.get('event_id')} | {last.get('notes')[:150]}")


if __name__ == "__main__":
    main()
