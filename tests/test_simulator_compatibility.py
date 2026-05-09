import json
from decimal import Decimal
from pathlib import Path

import pytest

from banking.cobol_records import parse_customer_record, parse_transaction_record
from banking.domain import BankingService, InMemoryRepository
from banking.simulator_compat import apply_simulator_action


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "simulator_test_cases.json"


def load_cases():
    data = json.loads(FIXTURE.read_text())
    assert 50 <= data["case_count"] <= 70
    return data["cases"]


def load_fixture():
    return json.loads(FIXTURE.read_text())


def logical_account(account):
    return (
        account.account_id,
        account.name,
        Decimal(account.balance),
        account.account_type,
    )


def logical_transaction(transaction):
    return (
        transaction.account_id,
        transaction.transaction_type,
        Decimal(transaction.amount),
    )


def replay_case(case):
    accounts = [
        parse_customer_record(row) for row in case["initial_customers"] if row.strip()
    ]
    for index, account in enumerate(accounts, start=1):
        account.row_id = index
    transactions = [
        parse_transaction_record(row)
        for row in case["initial_transactions"]
        if row.strip()
    ]
    new_expected_transactions = case["expected_transactions"][
        len(case["initial_transactions"]) :
    ]
    clock_values = [
        (parse_transaction_record(row).date, parse_transaction_record(row).time)
        for row in new_expected_transactions
    ]
    clock_index = 0

    def fixture_clock():
        nonlocal clock_index
        if clock_index >= len(clock_values):
            return "2025/01/01", "00:00:00"
        value = clock_values[clock_index]
        clock_index += 1
        return value

    service = BankingService(InMemoryRepository(accounts, transactions), clock=fixture_clock)

    for action in case["actions"]:
        apply_simulator_action(service, action)

    return service


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case["id"])
def test_modernized_code_matches_simulator_derived_case(case):
    service = replay_case(case)

    expected_accounts = [
        parse_customer_record(row) for row in case["expected_customers"] if row.strip()
    ]
    expected_transactions = [
        parse_transaction_record(row)
        for row in case["expected_transactions"]
        if row.strip()
    ]

    assert [logical_account(account) for account in service.view_accounts()] == [
        logical_account(account) for account in expected_accounts
    ]
    assert [logical_transaction(transaction) for transaction in service.transactions()] == [
        logical_transaction(transaction) for transaction in expected_transactions
    ]


def test_simulator_fixture_has_required_variety_and_edge_cases():
    data = load_fixture()
    categories = {case["category"] for case in data["cases"]}

    assert data["case_count"] == 64
    assert {
        "create_account",
        "deposit",
        "withdraw_success",
        "withdraw_insufficient",
        "apply_interest",
        "multi_step",
        "missing_account",
        "invalid_amount",
        "view_empty",
        "mini_no_history",
        "mini_missing_file",
        "invalid_menu",
        "interest_no_savings",
        "old_format_record",
    }.issubset(categories)
