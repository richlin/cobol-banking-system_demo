import argparse
import os
from decimal import Decimal, InvalidOperation

from banking.domain import BankingService
from banking.models import AccountNotFound, InsufficientFunds
from banking.storage import BankingDatabase


def run_smoke(db_path) -> None:
    if os.path.exists(db_path):
        os.remove(db_path)
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


_TYPE_LABEL = {"D": "DEP", "W": "WTH", "I": "INT"}


def run_menu(db_path) -> None:
    db = BankingDatabase(db_path)
    service = BankingService(db)

    print("==============================================")
    print("🏦 PYTHON BANKING SYSTEM (modernized)")
    print("==============================================")

    while True:
        print(" ")
        print("📋 MAIN MENU:")
        print("  1. Create New Account")
        print("  2. View All Accounts")
        print("  3. Deposit Money")
        print("  4. Withdraw Money")
        print("  5. Mini Statement")
        print("  6. Apply Interest (Savings)")
        print("  7. Exit System")
        print(" ")
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            print(" ")
            print("💳 CREATE NEW ACCOUNT")
            print("=====================")
            acct_id = input("Enter Account ID (max 10 chars): ").strip()[:10]
            name = input("Enter Customer Name (max 30 chars): ").strip()[:30]
            try:
                balance = Decimal(input("Enter Initial Balance: $").strip())
            except InvalidOperation:
                print("❌ Invalid amount.")
                continue
            acct_type = input("Enter Account Type (S=Savings, C=Checking): ").strip().upper()
            service.create_account(acct_id, name, balance, acct_type)
            print(" ")
            print("✅ Account created successfully!")
            print(f"   Account ID: {acct_id}")
            print(f"   Name: {name}")
            print(f"   Balance: ${balance}")
            print(f"   Type: {acct_type}")

        elif choice == "2":
            print(" ")
            print("👥 ALL CUSTOMER ACCOUNTS")
            print("========================")
            accounts = service.view_accounts()
            if not accounts:
                print("❌ No accounts found.")
            else:
                print("Account ID | Customer Name              | Balance    | Type")
                print("-----------|----------------------------|------------|-----")
                for a in accounts:
                    print(f"{a.account_id:<10} | {a.name:<30} | ${a.balance:<10} | {a.account_type}")

        elif choice == "3":
            print(" ")
            print("💰 DEPOSIT MONEY")
            print("================")
            acct_id = input("Enter Account ID: ").strip()
            try:
                amount = Decimal(input("Enter deposit amount: $").strip())
            except InvalidOperation:
                print("❌ Invalid amount.")
                continue
            try:
                new_balance = service.deposit(acct_id, amount)
                print(" ")
                print("✅ Deposit successful!")
                print(f"   Account ID: {acct_id}")
                print(f"   Amount deposited: ${amount}")
                print(f"   New balance: ${new_balance}")
            except AccountNotFound:
                print(" ")
                print(f"❌ Account not found: {acct_id}")

        elif choice == "4":
            print(" ")
            print("💸 WITHDRAW MONEY")
            print("=================")
            acct_id = input("Enter Account ID: ").strip()
            try:
                amount = Decimal(input("Enter withdrawal amount: $").strip())
            except InvalidOperation:
                print("❌ Invalid amount.")
                continue
            try:
                new_balance = service.withdraw(acct_id, amount)
                print(" ")
                print("✅ Withdrawal successful!")
                print(f"   Account ID: {acct_id}")
                print(f"   Amount withdrawn: ${amount}")
                print(f"   New balance: ${new_balance}")
            except InsufficientFunds:
                account = next((a for a in service.view_accounts() if a.account_id == acct_id), None)
                print(" ")
                print("❌ Insufficient funds!")
                if account:
                    print(f"   Current balance: ${account.balance}")
                print(f"   Requested amount: ${amount}")
            except AccountNotFound:
                print(" ")
                print(f"❌ Account not found: {acct_id}")

        elif choice == "5":
            print(" ")
            print("📊 MINI STATEMENT")
            print("================")
            acct_id = input("Enter Account ID: ").strip()
            print(" ")
            print(f"Last 5 transactions for Account: {acct_id}")
            print("Date       | Time     | Type | Amount     ")
            print("-----------|----------|------|------------")
            txns = service.mini_statement(acct_id)
            if not txns:
                print("No transactions found for this account.")
            for t in txns:
                label = _TYPE_LABEL.get(t.transaction_type, t.transaction_type)
                print(f"{t.date} | {t.time} | {label:<4} | ${t.amount}")

        elif choice == "6":
            print(" ")
            print("💰 APPLY INTEREST TO SAVINGS ACCOUNTS")
            print("====================================")
            print("Applying 2% annual interest to all savings accounts...")
            applied = service.apply_interest()
            for acct_id, amount in applied:
                print(f"Interest applied to {acct_id}: ${amount}")
            print(" ")
            print(f"✅ Interest applied to {len(applied)} savings accounts.")

        elif choice == "7":
            print("👋 Thank you for using Python Banking System!")
            break

        else:
            print("❌ Invalid option. Please enter 1-7.")

    db.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Modern COBOL banking app")
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke = subparsers.add_parser("smoke", help="run independent smoke scenario")
    smoke.add_argument("--db", required=True)

    menu = subparsers.add_parser("menu", help="interactive banking menu")
    menu.add_argument("--db", required=True)

    args = parser.parse_args(argv)
    if args.command == "smoke":
        run_smoke(args.db)
        return 0
    if args.command == "menu":
        run_menu(args.db)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
