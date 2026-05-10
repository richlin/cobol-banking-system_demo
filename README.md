# COBOL Banking Modernization Demo

Minimal guide for running the legacy COBOL path and the modernized Python path side by side.

## Prerequisites

- Python 3
- Bash shell
- pytest, for tests

## Run the Legacy COBOL Path

This repo uses the local `cobc` simulator path to compile and run `BANKACCT.cob`.

```bash
./setup.sh
./run.sh
```

Follow the interactive menu prompts. In the local simulator-backed legacy path, use option `8` to exit.

## Run the Modernized Python Path

Use a separate SQLite database so legacy `.DAT` files are not changed.

```bash
python3 -m banking.cli menu --db /tmp/cobol_banking_modern.sqlite3
```

Follow the same menu flow you used in the legacy path.
Use option `7` to exit the modernized Python menu.

## Compare Legacy vs Modernized Behavior

Manual comparison:

1. Run `./run.sh`.
2. In another terminal, run `python3 -m banking.cli menu --db /tmp/cobol_banking_modern.sqlite3`.
3. Enter the same business actions in both menus, such as create account, deposit, withdraw, mini statement, and apply interest.
4. Compare balances, transaction history, and validation behavior.

Note: the local legacy simulator exits with option `8`; the modernized Python menu exits with option `7`.

Automated simulator-derived comparison:

```bash
python3 scripts/generate_simulator_test_cases.py
python3 -m pytest tests/test_simulator_compatibility.py
```

## Migrate Existing Data

```bash
python3 -m banking.migration CUSTOMERS.DAT TRANSACTIONS.DAT /tmp/cobol_banking_migrated.sqlite3
```

## Run Verification

```bash
python3 -m pytest
python3 -m coverage run -m pytest
python3 -m coverage report --include='banking/domain.py,banking/cobol_records.py,banking/migration.py,banking/simulator_compat.py' --fail-under=90
```

## More Documentation

- Detailed project guide: `docs/project_details.md`
- Modernization plan: `MIGRATION_PLAN.md`
- Decisions: `DECISIONS.md`
- Legacy inventory: `docs/legacy_inventory.md`
- Retail banking scenarios: `docs/retail_banking_test_scenarios.md`
