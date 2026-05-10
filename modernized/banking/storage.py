import sqlite3
from decimal import Decimal
from pathlib import Path
from typing import List

from banking.models import Account, Transaction


class BankingDatabase:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                name TEXT NOT NULL,
                balance TEXT NOT NULL,
                account_type TEXT NOT NULL,
                status_suffix TEXT
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def list_accounts(self) -> List[Account]:
        rows = self.connection.execute(
            """
            SELECT id, account_id, name, balance, account_type, status_suffix
            FROM accounts
            ORDER BY id
            """
        ).fetchall()
        return [
            Account(
                row["account_id"],
                row["name"],
                Decimal(row["balance"]),
                row["account_type"],
                row["status_suffix"],
                row["id"],
            )
            for row in rows
        ]

    def append_account(self, account: Account) -> Account:
        cursor = self.connection.execute(
            """
            INSERT INTO accounts
                (account_id, name, balance, account_type, status_suffix)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                account.account_id,
                account.name,
                str(account.balance),
                account.account_type,
                account.status_suffix,
            ),
        )
        self.connection.commit()
        account.row_id = cursor.lastrowid
        return account

    def update_account(self, account: Account) -> Account:
        if account.row_id is None:
            raise ValueError("cannot update account without row_id")
        self.connection.execute(
            """
            UPDATE accounts
            SET account_id = ?, name = ?, balance = ?, account_type = ?,
                status_suffix = ?
            WHERE id = ?
            """,
            (
                account.account_id,
                account.name,
                str(account.balance),
                account.account_type,
                account.status_suffix,
                account.row_id,
            ),
        )
        self.connection.commit()
        return account

    def list_transactions(self) -> List[Transaction]:
        rows = self.connection.execute(
            """
            SELECT id, account_id, transaction_type, amount, date, time
            FROM transactions
            ORDER BY id
            """
        ).fetchall()
        return [
            Transaction(
                row["account_id"],
                row["transaction_type"],
                Decimal(row["amount"]),
                row["date"],
                row["time"],
                row["id"],
            )
            for row in rows
        ]

    def append_transaction(self, transaction: Transaction) -> Transaction:
        cursor = self.connection.execute(
            """
            INSERT INTO transactions
                (account_id, transaction_type, amount, date, time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction.account_id,
                transaction.transaction_type,
                str(transaction.amount),
                transaction.date,
                transaction.time,
            ),
        )
        self.connection.commit()
        transaction.row_id = cursor.lastrowid
        return transaction

    def close(self) -> None:
        self.connection.close()
