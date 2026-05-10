# Agent Instructions

## Project Purpose

This repository modernizes a COBOL banking demo into a maintainable Python and SQLite implementation. Agents should preserve legacy behavior intentionally, document source-of-truth decisions, and keep verification evidence in the repo.

## Source of Truth

- `legacy/BANKACCT.cob` is the authoritative legacy source for migration behavior.
- `legacy/setup.sh`, `legacy/cobc`, and the generated `legacy/BANKACCT` simulator are reference material only.
- Do not let simulator-only behavior override `legacy/BANKACCT.cob` unless `DECISIONS.md` records that choice explicitly.
- Current `.DAT` files may contain simulator-era metadata, such as customer status suffixes. Preserve such data where migration supports it, but do not treat it as COBOL behavior by default.

## Modern Stack

- Runtime: Python 3
- Persistence: SQLite
- Core tests: pytest and coverage.py
- Core modules live in `modernized/banking/`
- Optional HTTP adapter: `modernized/banking/api.py`
- Optional API dependencies: `modernized/requirements-api.txt`

## Operating Rules

- Keep changes small and behavior-focused.
- Prefer tests before implementation for new behavior.
- Do not modify vendored `gnucobol-3.2/` files unless the task explicitly targets that tree.
- Do not edit generated/cache artifacts such as `.coverage`, `.pytest_cache/`, `.DS_Store`, `__pycache__/`, or temporary SQLite files.
- When behavior is ambiguous, update `DECISIONS.md` before implementing.
- When progress or verification state changes, update `PROGRESS.md`.
- When a correction or reusable lesson appears, update `tasks/lessons.md`.
- Track active implementation work in `tasks/todo.md`.

## Migration Harness

Read these files before non-trivial work:

1. `PROGRESS.md`
2. `DECISIONS.md`
3. `MIGRATION_PLAN.md`
4. `docs/legacy_inventory.md`
5. `tasks/todo.md`

Use `docs/retail_banking_test_scenarios.md` for broader retail banking scenario design. Treat `current` and `compat` scenarios as candidates for immediate automation; treat `future` scenarios as product expansion unless the user asks to implement them.

## Verification Commands

Run the narrowest relevant checks first, then broaden before completion.

```bash
python3 -m pytest
python3 -m coverage run -m pytest
python3 -m coverage report --include='modernized/banking/domain.py,modernized/banking/cobol_records.py,modernized/banking/migration.py,modernized/banking/simulator_compat.py' --fail-under=90
PYTHONPATH=modernized python3 -m banking.cli smoke --db /private/tmp/cobol_banking_smoke.sqlite3
PYTHONPATH=modernized python3 -m banking.migration legacy/CUSTOMERS.DAT legacy/TRANSACTIONS.DAT /private/tmp/cobol_banking_migrated.sqlite3
PYTHONPYCACHEPREFIX=/private/tmp/cobol_banking_pycache python3 -m compileall modernized/banking
```

Simulator-derived compatibility fixture:

```bash
PYTHONPATH=modernized python3 modernized/scripts/generate_simulator_test_cases.py
python3 -m pytest modernized/tests/test_simulator_compatibility.py
```

## Done Criteria

A change is done only when:

- The affected behavior has tests.
- Legacy/source-of-truth implications are documented.
- Relevant verification commands pass.
- `PROGRESS.md` and `tasks/todo.md` reflect the final state.
- Any non-obvious architectural or behavior choice is recorded in `DECISIONS.md`.
