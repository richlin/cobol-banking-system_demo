from decimal import Decimal

import pytest

from banking.domain import BankingService, InMemoryRepository, system_clock
from banking.models import Account, AccountNotFound, InsufficientFunds, Transaction


def fixed_clock():
    return "2025/07/27", "21:12:16"


def make_service(accounts=None, transactions=None):
    return BankingService(
        InMemoryRepository(accounts or [], transactions or []),
        clock=fixed_clock,
    )


def test_create_account_adds_account_without_transaction():
    service = make_service()

    account = service.create_account("acct-1", "Ada Lovelace", Decimal("100"), "S")

    assert account.account_id == "acct-1"
    assert account.name == "Ada Lovelace"
    assert account.balance == Decimal("100")
    assert account.account_type == "S"
    assert service.view_accounts() == [account]
    assert service.transactions() == []


def test_view_accounts_returns_all_accounts_in_file_order():
    accounts = [
        Account("a-1", "First", Decimal("10"), "S"),
        Account("a-2", "Second", Decimal("20"), "C"),
    ]

    assert make_service(accounts).view_accounts() == accounts


def test_deposit_updates_first_matching_account_and_logs_transaction():
    service = make_service([Account("acct-1", "Ada", Decimal("100"), "S")])

    new_balance = service.deposit("acct-1", Decimal("25"))

    assert new_balance == Decimal("125")
    assert service.view_accounts()[0].balance == Decimal("125")
    assert service.transactions() == [
        Transaction("acct-1", "D", Decimal("25"), "2025/07/27", "21:12:16")
    ]


def test_withdraw_updates_balance_and_logs_transaction():
    service = make_service([Account("acct-1", "Ada", Decimal("100"), "S")])

    new_balance = service.withdraw("acct-1", Decimal("40"))

    assert new_balance == Decimal("60")
    assert service.transactions() == [
        Transaction("acct-1", "W", Decimal("40"), "2025/07/27", "21:12:16")
    ]


def test_withdraw_rejects_insufficient_funds_without_transaction():
    service = make_service([Account("acct-1", "Ada", Decimal("30"), "S")])

    with pytest.raises(InsufficientFunds):
        service.withdraw("acct-1", Decimal("40"))

    assert service.view_accounts()[0].balance == Decimal("30")
    assert service.transactions() == []


def test_missing_account_raises_account_not_found():
    service = make_service()

    with pytest.raises(AccountNotFound):
        service.deposit("missing", Decimal("10"))


def test_mini_statement_returns_first_five_matching_transactions_like_cobol_loop():
    transactions = [
        Transaction("acct-1", "D", Decimal("1"), "2025/07/27", f"00:00:0{i}")
        for i in range(6)
    ]
    service = make_service([Account("acct-1", "Ada", Decimal("100"), "S")], transactions)

    statement = service.mini_statement("acct-1")

    assert len(statement) == 5
    assert [item.amount for item in statement] == [
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
    ]
    assert statement[-1].time == "00:00:04"


def test_mini_statement_returns_empty_list_when_no_transactions_match():
    service = make_service(
        [Account("acct-1", "Ada", Decimal("100"), "S")],
        [Transaction("other", "D", Decimal("1"), "2025/07/27", "00:00:00")],
    )

    assert service.mini_statement("acct-1") == []


def test_apply_interest_updates_only_savings_accounts_and_logs_interest():
    accounts = [
        Account("save-1", "Saver", Decimal("1000"), "S"),
        Account("check-1", "Checker", Decimal("1000"), "C"),
    ]
    service = make_service(accounts)

    applied = service.apply_interest()

    assert applied == [("save-1", Decimal("20.00"))]
    assert service.view_accounts()[0].balance == Decimal("1020.00")
    assert service.view_accounts()[1].balance == Decimal("1000")
    assert service.transactions() == [
        Transaction("save-1", "I", Decimal("20.00"), "2025/07/27", "21:12:16")
    ]


def test_in_memory_repository_rejects_update_for_unknown_account():
    repository = InMemoryRepository()

    with pytest.raises(AccountNotFound):
        repository.update_account(Account("missing", "Missing", Decimal("0"), "S"))


def test_in_memory_repository_updates_matching_account_when_row_ids_are_missing():
    first = Account("first", "First", Decimal("1"), "S")
    second = Account("second", "Second", Decimal("2"), "S")
    repository = InMemoryRepository([first, second])

    repository.update_account(Account("second", "Second", Decimal("20"), "S"))

    assert repository.list_accounts() == [
        first,
        Account("second", "Second", Decimal("20"), "S"),
    ]


def test_system_clock_uses_cobol_date_and_time_formats():
    date, time = system_clock()

    assert len(date) == 10
    assert date[4] == "/"
    assert date[7] == "/"
    assert len(time) == 8
    assert time[2] == ":"
    assert time[5] == ":"
