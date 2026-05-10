import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List

from banking.cobol_records import parse_customer_record, parse_transaction_record
from banking.storage import BankingDatabase


@dataclass
class RejectedRow:
    source: str
    line_number: int
    raw: str
    reason: str


@dataclass
class MigrationReport:
    customer_rows: int
    transaction_rows: int
    rejected_rows: List[RejectedRow]


def migrate_files(customer_file, transaction_file, db_path) -> MigrationReport:
    db = BankingDatabase(db_path)
    rejected = []
    customer_rows = _migrate_customers(Path(customer_file), db, rejected)
    transaction_rows = _migrate_transactions(Path(transaction_file), db, rejected)
    db.close()
    return MigrationReport(customer_rows, transaction_rows, rejected)


def _migrate_customers(path: Path, db: BankingDatabase, rejected: List[RejectedRow]) -> int:
    imported = 0
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            account = parse_customer_record(line)
        except ValueError as exc:
            rejected.append(RejectedRow(path.name, line_number, line, str(exc)))
            continue
        db.append_account(account)
        imported += 1
    return imported


def _migrate_transactions(
    path: Path, db: BankingDatabase, rejected: List[RejectedRow]
) -> int:
    imported = 0
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            transaction = parse_transaction_record(line)
        except ValueError as exc:
            rejected.append(RejectedRow(path.name, line_number, line, str(exc)))
            continue
        db.append_transaction(transaction)
        imported += 1
    return imported


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Migrate COBOL banking DAT files.")
    parser.add_argument("customers")
    parser.add_argument("transactions")
    parser.add_argument("db")
    args = parser.parse_args(argv)

    report = migrate_files(args.customers, args.transactions, args.db)
    print(f"customer rows imported: {report.customer_rows}")
    print(f"transaction rows imported: {report.transaction_rows}")
    print(f"rejected rows: {len(report.rejected_rows)}")
    for row in report.rejected_rows:
        print(f"{row.source}:{row.line_number}: {row.reason}")
    return 1 if report.rejected_rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
