# Project Details

## Overview

This repository contains a COBOL banking demo and a modernized Python and SQLite implementation. The modernization treats `BANKACCT.cob` as the source of truth for legacy behavior. The generated simulator path is useful for compatibility testing, but it is not the migration authority unless `DECISIONS.md` says otherwise.

## Features

### Legacy COBOL Scope

- Create customer accounts.
- View customer accounts.
- Deposit funds.
- Withdraw funds with insufficient-funds validation.
- View mini statements.
- Apply 2% savings-account interest.
- Persist customer and transaction records in flat `.DAT` files.

### Modernized Python Scope

- Python domain layer in `banking/domain.py`.
- Fixed-width COBOL record parsing in `banking/cobol_records.py`.
- SQLite persistence in `banking/storage.py`.
- Data migration in `banking/migration.py`.
- Interactive menu and smoke scenario in `banking/cli.py`.
- Optional FastAPI adapter in `banking/api.py`.
- Simulator-derived compatibility fixture in `tests/fixtures/simulator_test_cases.json`.

## Source of Truth

- Authoritative legacy behavior: `BANKACCT.cob`
- Legacy data files: `CUSTOMERS.DAT`, `TRANSACTIONS.DAT`
- Simulator reference: `setup.sh`, `cobc`, generated `BANKACCT`
- Modern target stack: Python 3 and SQLite

Known mismatch: current `CUSTOMERS.DAT` rows may include a simulator-era status suffix at position 51. The modern migration preserves this suffix as metadata, but the COBOL source does not define inactive-account behavior.

Local run-path mismatch: `./run.sh` uses the simulator-backed `cobc` path and displays simulator menu option `8` for exit. The modernized Python menu follows the COBOL-source menu shape and exits with option `7`. Compare business actions, not the exit option.

## Data Format

### Customer Records

| Field | Position | Length | Description |
| --- | --- | --- | --- |
| Account ID | 1-10 | 10 | Unique account identifier |
| Customer Name | 11-40 | 30 | Customer name |
| Balance | 41-49 | 9 | Account balance |
| Account Type | 50 | 1 | `S` for savings, `C` for checking |
| Status Suffix | 51 | 1 | Simulator-era metadata, when present |

### Transaction Records

| Field | Position | Length | Description |
| --- | --- | --- | --- |
| Account ID | 1-10 | 10 | Account identifier |
| Transaction Type | 11 | 1 | `D`, `W`, `I`, or simulator-era `X` |
| Amount | 12-20 | 9 | Transaction amount |
| Date | 21-30 | 10 | `YYYY/MM/DD` |
| Time | 31-38 | 8 | `HH:MM:SS` |

## Project Structure

```text
BANKACCT.cob                         Legacy COBOL source
CUSTOMERS.DAT                        Legacy customer data
TRANSACTIONS.DAT                     Legacy transaction data
banking/                             Modern Python implementation
tests/                               Automated tests
scripts/generate_simulator_test_cases.py
docs/legacy_inventory.md             COBOL inventory
docs/retail_banking_test_scenarios.md
MIGRATION_PLAN.md
DECISIONS.md
PROGRESS.md
tasks/todo.md
tasks/lessons.md
AGENTS.md
```

## Verification Strategy

The verification harness has four layers:

1. Unit tests for fixed-width parsing and domain rules.
2. Migration tests for `.DAT` to SQLite conversion.
3. CLI smoke tests for independent modern runtime.
4. Simulator-derived compatibility tests for observed legacy-adjacent behavior.

Run all tests:

```bash
python3 -m pytest
```

Regenerate and run simulator-derived tests:

```bash
python3 scripts/generate_simulator_test_cases.py
python3 -m pytest tests/test_simulator_compatibility.py
```

## Scenario Catalog

`docs/retail_banking_test_scenarios.md` contains broader customer-oriented scenarios. Scenarios marked `current` and `compat` are candidates for immediate automated coverage. Scenarios marked `future` describe product expansion ideas and should not be implemented unless explicitly requested.

## Maintenance Notes

- Update `DECISIONS.md` before changing source-of-truth behavior.
- Update `PROGRESS.md` after significant work or verification.
- Update `tasks/todo.md` with active and completed work.
- Update `tasks/lessons.md` after corrections or reusable lessons.
- Keep README minimal; put detailed explanations in `docs/`.
