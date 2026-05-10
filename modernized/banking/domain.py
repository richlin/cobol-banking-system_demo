from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from typing import Iterable, List, Optional, Tuple

from banking.models import Account, AccountNotFound, InsufficientFunds, Transaction


def system_clock() -> Tuple[str, str]:
    now = datetime.now()
    return now.strftime("%Y/%m/%d"), now.strftime("%H:%M:%S")


class InMemoryRepository:
    def __init__(
        self,
        accounts: Optional[Iterable[Account]] = None,
        transactions: Optional[Iterable[Transaction]] = None,
    ):
        self._accounts = list(accounts or [])
        self._transactions = list(transactions or [])

    def list_accounts(self) -> List[Account]:
        return list(self._accounts)

    def append_account(self, account: Account) -> Account:
        self._accounts.append(account)
        return account

    def update_account(self, account: Account) -> Account:
        for index, existing in enumerate(self._accounts):
            if existing is account:
                self._accounts[index] = account
                return account
            if (
                existing.row_id is not None
                and account.row_id is not None
                and existing.row_id == account.row_id
            ):
                self._accounts[index] = account
                return account
        for index, existing in enumerate(self._accounts):
            if existing.account_id == account.account_id:
                self._accounts[index] = account
                return account
        raise AccountNotFound(account.account_id)

    def list_transactions(self) -> List[Transaction]:
        return list(self._transactions)

    def append_transaction(self, transaction: Transaction) -> Transaction:
        self._transactions.append(transaction)
        return transaction


class BankingService:
    def __init__(self, repository, clock=system_clock):
        self.repository = repository
        self.clock = clock

    def create_account(
        self, account_id: str, name: str, balance: Decimal, account_type: str
    ) -> Account:
        account = Account(
            account_id=account_id,
            name=name,
            balance=Decimal(balance),
            account_type=account_type,
        )
        return self.repository.append_account(account)

    def view_accounts(self) -> List[Account]:
        return self.repository.list_accounts()

    def transactions(self) -> List[Transaction]:
        return self.repository.list_transactions()

    def deposit(self, account_id: str, amount: Decimal) -> Decimal:
        account = self._find_account(account_id)
        updated = replace(account, balance=account.balance + Decimal(amount))
        self.repository.update_account(updated)
        self._log_transaction(account_id, "D", Decimal(amount))
        return updated.balance

    def withdraw(self, account_id: str, amount: Decimal) -> Decimal:
        account = self._find_account(account_id)
        amount = Decimal(amount)
        if account.balance < amount:
            raise InsufficientFunds(account_id)

        updated = replace(account, balance=account.balance - amount)
        self.repository.update_account(updated)
        self._log_transaction(account_id, "W", amount)
        return updated.balance

    def mini_statement(self, account_id: str, limit: int = 5) -> List[Transaction]:
        matches = []
        for transaction in self.repository.list_transactions():
            if transaction.account_id == account_id:
                matches.append(transaction)
                if len(matches) >= limit:
                    break
        return matches

    def apply_interest(self, rate: Decimal = Decimal("0.02")) -> List[Tuple[str, Decimal]]:
        applied = []
        for account in self.repository.list_accounts():
            if account.account_type == "S":
                amount = (account.balance * Decimal(rate)).quantize(Decimal("0.01"))
                updated = replace(account, balance=account.balance + amount)
                self.repository.update_account(updated)
                self._log_transaction(account.account_id, "I", amount)
                applied.append((account.account_id, amount))
        return applied

    def _find_account(self, account_id: str) -> Account:
        for account in self.repository.list_accounts():
            if account.account_id == account_id:
                return account
        raise AccountNotFound(account_id)

    def _log_transaction(
        self, account_id: str, transaction_type: str, amount: Decimal
    ) -> Transaction:
        date, time = self.clock()
        transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=Decimal(amount),
            date=date,
            time=time,
        )
        return self.repository.append_transaction(transaction)
