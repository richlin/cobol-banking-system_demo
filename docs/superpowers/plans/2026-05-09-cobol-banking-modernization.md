# COBOL Banking Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modern Python and SQLite banking application that reproduces `legacy/BANKACCT.cob` behavior and migrates legacy `.DAT` files without using the simulator as source of truth.

**Architecture:** The implementation separates COBOL record parsing, domain behavior, SQLite persistence, and interfaces. The COBOL program remains the behavioral source of truth; simulator-only behavior is documented as a mismatch and excluded unless needed for data preservation.

**Tech Stack:** Python 3, SQLite, pytest, coverage.py, optional FastAPI adapter for HTTP deployment.

---

## File Structure

- `docs/legacy_inventory.md`: COBOL source inventory, field maps, procedure maps, and known source/documentation mismatches.
- `DECISIONS.md`: target stack and behavior-source decisions.
- `PROGRESS.md`: session progress, blockers, and next steps.
- `tasks/todo.md`: executable task checklist linked to the migration plan.
- `modernized/banking/models.py`: dataclasses and domain exceptions.
- `modernized/banking/cobol_records.py`: fixed-width customer and transaction record parsing/formatting.
- `modernized/banking/domain.py`: behavior-equivalent account, deposit, withdrawal, statement, and interest operations.
- `modernized/banking/storage.py`: SQLite schema and repository.
- `modernized/banking/migration.py`: `.DAT` to SQLite migration with row-level validation.
- `modernized/banking/cli.py`: independent runnable CLI for end-to-end scenarios.
- `modernized/banking/api.py`: optional FastAPI adapter around the service layer.
- `modernized/tests/`: characterization, unit, integration, migration, and documentation coverage tests.

## Tasks

- [x] Create planning, decision, progress, and legacy inventory documents.
- [x] Write failing tests for COBOL inventory completeness, fixed-width record parsing, and sample data migration.
- [x] Implement record parsers and inventory docs until those tests pass.
- [x] Write failing domain behavior tests for the 8 required scenarios.
- [x] Implement domain behavior until those tests pass.
- [x] Write failing SQLite integration and migration tests.
- [x] Implement storage and migration until those tests pass.
- [x] Write failing CLI/API smoke tests.
- [x] Implement independent CLI and optional FastAPI adapter.
- [x] Update README and run full verification: pytest, coverage threshold, CLI scenario, and migration smoke test.

## Verification Gates

- `python3 -m pytest`
- `python3 -m coverage run -m pytest`
- `python3 -m coverage report --include='modernized/banking/domain.py,modernized/banking/cobol_records.py,modernized/banking/migration.py,modernized/banking/simulator_compat.py' --fail-under=90`
- `PYTHONPATH=modernized python3 -m banking.cli smoke --db /tmp/cobol_banking_smoke.sqlite3`
- `PYTHONPATH=modernized python3 -m banking.migration legacy/CUSTOMERS.DAT legacy/TRANSACTIONS.DAT /tmp/cobol_banking_migrated.sqlite3`
