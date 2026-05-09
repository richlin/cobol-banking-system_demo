from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Account:
    account_id: str
    name: str
    balance: Decimal
    account_type: str
    status_suffix: Optional[str] = None
    row_id: Optional[int] = None


@dataclass
class Transaction:
    account_id: str
    transaction_type: str
    amount: Decimal
    date: str
    time: str
    row_id: Optional[int] = None


class BankingError(Exception):
    """Base exception for modernized banking behavior."""


class AccountNotFound(BankingError):
    """Raised when COBOL-style sequential account search finds no match."""


class InsufficientFunds(BankingError):
    """Raised when withdrawal amount exceeds the account balance."""
