import argparse
from decimal import Decimal

from banking.domain import BankingService
from banking.storage import BankingDatabase


def run_smoke(db_path) -> None:
    db = BankingDatabase(db_path)
    service = BankingService(db, clock=lambda: ("2025/07/27", "21:12:16"))

    service.create_account("acct-1", "Ada Lovelace", Decimal("1000"), "S")
    service.deposit("acct-1", Decimal("250"))
    service.withdraw("acct-1", Decimal("125"))
    service.apply_interest()
    statement = service.mini_statement("acct-1")
    balance = service.view_accounts()[0].balance
    db.close()

    if balance != Decimal("1147.50"):
        raise RuntimeError(f"unexpected smoke balance: {balance}")
    if [item.transaction_type for item in statement] != ["D", "W", "I"]:
        raise RuntimeError("unexpected smoke statement")

    print("smoke scenario passed")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Modern COBOL banking app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke = subparsers.add_parser("smoke", help="run independent smoke scenario")
    smoke.add_argument("--db", required=True)

    args = parser.parse_args(argv)
    if args.command == "smoke":
        run_smoke(args.db)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
