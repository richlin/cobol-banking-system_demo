#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path


MODERNIZED_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODERNIZED_ROOT.parent
SIMULATOR = REPO_ROOT / "legacy" / "BANKACCT"
OUTPUT = MODERNIZED_ROOT / "tests" / "fixtures" / "simulator_test_cases.json"


def customer_row(account_id, name, balance, account_type, status="A"):
    row = f"{account_id[:10]:<10}{name[:30]:<30}{int(balance):>9}{account_type[:1]}"
    if status is not None:
        row += status[:1]
    return row


def run_case(case):
    with tempfile.TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        if not case.get("omit_customers_file"):
            (temp_dir / "CUSTOMERS.DAT").write_text(
                "\n".join(case["initial_customers"]) + "\n"
                if case["initial_customers"]
                else ""
            )
        if not case.get("omit_transactions_file"):
            (temp_dir / "TRANSACTIONS.DAT").write_text(
                "\n".join(case["initial_transactions"]) + "\n"
                if case["initial_transactions"]
                else ""
            )

        inputs = "\n".join(case["simulator_inputs"]) + "\n"
        result = subprocess.run(
            [sys.executable, str(SIMULATOR)],
            cwd=temp_dir,
            input=inputs,
            text=True,
            capture_output=True,
            check=False,
        )

        customers_path = temp_dir / "CUSTOMERS.DAT"
        transactions_path = temp_dir / "TRANSACTIONS.DAT"
        case["simulator_returncode"] = result.returncode
        case["stdout_contains"] = case["stdout_contains"]
        case["expected_customers"] = (
            customers_path.read_text().splitlines() if customers_path.exists() else []
        )
        case["expected_transactions"] = (
            transactions_path.read_text().splitlines()
            if transactions_path.exists()
            else []
        )
        for expected in case["stdout_contains"]:
            if expected not in result.stdout:
                raise RuntimeError(f"{case['id']} missing stdout fragment: {expected}")
        if result.returncode != 0:
            raise RuntimeError(f"{case['id']} simulator failed: {result.stderr}")
        return case


def build_cases():
    cases = []

    for index in range(1, 9):
        account_id = f"new{index:07d}"[:10]
        cases.append(
            {
                "id": f"SIM-CREATE-{index:02d}",
                "category": "create_account",
                "description": "Create an account through the simulator.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [],
                "initial_transactions": [],
                "actions": [
                    {
                        "type": "create",
                        "account_id": account_id,
                        "name": f"Create Customer {index}",
                        "balance": 1000 + index * 50,
                        "account_type": "S" if index % 2 else "C",
                    }
                ],
                "simulator_inputs": [
                    "1",
                    account_id,
                    f"Create Customer {index}",
                    str(1000 + index * 50),
                    "S" if index % 2 else "C",
                    "8",
                ],
                "stdout_contains": ["Account created successfully"],
            }
        )

    for index in range(1, 9):
        account_id = f"dep{index:07d}"[:10]
        balance = 1000 + index * 100
        amount = 25 + index * 5
        cases.append(
            {
                "id": f"SIM-DEPOSIT-{index:02d}",
                "category": "deposit",
                "description": "Deposit into an active account through the simulator.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(account_id, f"Deposit Customer {index}", balance, "S")
                ],
                "initial_transactions": [],
                "actions": [
                    {"type": "deposit", "account_id": account_id, "amount": amount}
                ],
                "simulator_inputs": ["3", account_id, str(amount), "8"],
                "stdout_contains": ["Deposit successful"],
            }
        )

    for index in range(1, 9):
        account_id = f"wth{index:07d}"[:10]
        balance = 2000 + index * 100
        amount = 20 + index * 10
        cases.append(
            {
                "id": f"SIM-WITHDRAW-{index:02d}",
                "category": "withdraw_success",
                "description": "Withdraw available funds through the simulator.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(account_id, f"Withdraw Customer {index}", balance, "C")
                ],
                "initial_transactions": [],
                "actions": [
                    {"type": "withdraw", "account_id": account_id, "amount": amount}
                ],
                "simulator_inputs": ["4", account_id, str(amount), "8"],
                "stdout_contains": ["Withdrawal successful"],
            }
        )

    for index in range(1, 7):
        account_id = f"low{index:07d}"[:10]
        balance = 100 + index * 10
        amount = balance + 500
        cases.append(
            {
                "id": f"SIM-INSUFFICIENT-{index:02d}",
                "category": "withdraw_insufficient",
                "description": "Reject withdrawal when simulator reports insufficient funds.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(account_id, f"Low Balance {index}", balance, "C")
                ],
                "initial_transactions": [],
                "actions": [
                    {"type": "withdraw", "account_id": account_id, "amount": amount}
                ],
                "simulator_inputs": ["4", account_id, str(amount), "8"],
                "stdout_contains": ["Insufficient funds"],
            }
        )

    for index in range(1, 7):
        savings_id = f"int{index:07d}"[:10]
        checking_id = f"chk{index:07d}"[:10]
        savings_balance = 1000 + index * 50
        checking_balance = 2000 + index * 100
        cases.append(
            {
                "id": f"SIM-INTEREST-{index:02d}",
                "category": "apply_interest",
                "description": "Apply simulator savings interest to active savings accounts.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(savings_id, f"Interest Saver {index}", savings_balance, "S"),
                    customer_row(checking_id, f"Interest Check {index}", checking_balance, "C"),
                ],
                "initial_transactions": [],
                "actions": [{"type": "apply_interest"}],
                "simulator_inputs": ["6", "8"],
                "stdout_contains": ["Interest applied"],
            }
        )

    for index in range(1, 5):
        account_id = f"mix{index:07d}"[:10]
        opening = 1000 + index * 100
        deposit = 100 + index * 50
        withdraw = 50
        cases.append(
            {
                "id": f"SIM-MULTI-{index:02d}",
                "category": "multi_step",
                "description": "Run create, deposit, withdraw, and interest as one simulator flow.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [],
                "initial_transactions": [],
                "actions": [
                    {
                        "type": "create",
                        "account_id": account_id,
                        "name": f"Multi Customer {index}",
                        "balance": opening,
                        "account_type": "S",
                    },
                    {"type": "deposit", "account_id": account_id, "amount": deposit},
                    {"type": "withdraw", "account_id": account_id, "amount": withdraw},
                    {"type": "apply_interest"},
                ],
                "simulator_inputs": [
                    "1",
                    account_id,
                    f"Multi Customer {index}",
                    str(opening),
                    "S",
                    "3",
                    account_id,
                    str(deposit),
                    "4",
                    account_id,
                    str(withdraw),
                    "6",
                    "8",
                ],
                "stdout_contains": [
                    "Account created successfully",
                    "Deposit successful",
                    "Withdrawal successful",
                    "Interest applied",
                ],
            }
        )

    for index in range(1, 7):
        account_id = f"miss{index:06d}"[:10]
        cases.append(
            {
                "id": f"SIM-MISSING-{index:02d}",
                "category": "missing_account",
                "description": "Attempt account mutation when the account is absent.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [],
                "initial_transactions": [],
                "actions": [
                    {
                        "type": "deposit" if index % 2 else "withdraw",
                        "account_id": account_id,
                        "amount": 100 + index,
                    }
                ],
                "simulator_inputs": [
                    "3" if index % 2 else "4",
                    account_id,
                    str(100 + index),
                    "8",
                ],
                "stdout_contains": ["Account not found"],
            }
        )

    invalid_amounts = [
        ("deposit", "0", "Invalid amount"),
        ("deposit", "-1", "Invalid amount"),
        ("deposit", "abc", "Invalid amount"),
        ("deposit", "12x", "Invalid amount"),
        ("withdraw", "0", "Invalid amount"),
        ("withdraw", "-5", "Invalid amount"),
        ("withdraw", "abc", "Invalid amount"),
        ("withdraw", "1.5x", "Invalid amount"),
    ]
    for index, (action_type, raw_amount, expected_text) in enumerate(
        invalid_amounts, start=1
    ):
        account_id = f"bad{index:07d}"[:10]
        cases.append(
            {
                "id": f"SIM-INVALID-AMOUNT-{index:02d}",
                "category": "invalid_amount",
                "description": "Reject zero, negative, or non-numeric simulator input amounts.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(account_id, f"Invalid Amount {index}", 1000, "S")
                ],
                "initial_transactions": [],
                "actions": [
                    {
                        "type": action_type,
                        "account_id": account_id,
                        "amount": raw_amount,
                    }
                ],
                "simulator_inputs": [
                    "3" if action_type == "deposit" else "4",
                    account_id,
                    raw_amount,
                    "8",
                ],
                "stdout_contains": [expected_text],
            }
        )

    no_data_cases = [
        ("view_empty", ["2", "8"], [{"type": "view_accounts"}], "No accounts found"),
        (
            "mini_no_history",
            ["5", "emptyacct", "8"],
            [{"type": "mini_statement", "account_id": "emptyacct"}],
            "No transactions found",
        ),
        (
            "mini_missing_file",
            ["5", "emptyacct", "8"],
            [{"type": "mini_statement", "account_id": "emptyacct"}],
            "No transaction history found",
        ),
        ("invalid_menu", ["9", "8"], [{"type": "invalid_menu"}], "Invalid option"),
    ]
    for index, (name, inputs, actions, expected_text) in enumerate(
        no_data_cases, start=1
    ):
        cases.append(
            {
                "id": f"SIM-NO-DATA-{index:02d}",
                "category": name,
                "description": "Exercise simulator read-only or menu edge behavior.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [],
                "initial_transactions": [],
                "omit_transactions_file": name == "mini_missing_file",
                "actions": actions,
                "simulator_inputs": inputs,
                "stdout_contains": [expected_text],
            }
        )

    for index in range(1, 4):
        checking_id = f"nosave{index:04d}"[:10]
        cases.append(
            {
                "id": f"SIM-NO-SAVINGS-{index:02d}",
                "category": "interest_no_savings",
                "description": "Apply interest when there are no savings accounts.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(checking_id, f"No Savings {index}", 2000 + index, "C")
                ],
                "initial_transactions": [],
                "actions": [{"type": "apply_interest"}],
                "simulator_inputs": ["6", "8"],
                "stdout_contains": ["No savings accounts found"],
            }
        )

    for index in range(1, 4):
        account_id = f"old{index:07d}"[:10]
        cases.append(
            {
                "id": f"SIM-OLD-FORMAT-{index:02d}",
                "category": "old_format_record",
                "description": "Mutate a 50-character pre-status account record.",
                "comparison_scope": "logical_cobol_fields",
                "initial_customers": [
                    customer_row(account_id, f"Old Format {index}", 500 + index, "S", status=None)
                ],
                "initial_transactions": [],
                "actions": [
                    {"type": "deposit", "account_id": account_id, "amount": 10 + index}
                ],
                "simulator_inputs": ["3", account_id, str(10 + index), "8"],
                "stdout_contains": ["Deposit successful"],
            }
        )

    return cases


def main():
    cases = [run_case(case) for case in build_cases()]
    if not 50 <= len(cases) <= 70:
        raise RuntimeError(f"expected 50-70 cases, generated {len(cases)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "source": "BANKACCT simulator",
                "case_count": len(cases),
                "comparison_note": (
                    "Cases are generated by running the simulator. Tests compare "
                    "logical COBOL fields so simulator-only status suffixes and "
                    "dynamic timestamps do not become new migration source of truth."
                ),
                "cases": cases,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {len(cases)} simulator-derived cases to {OUTPUT}")


if __name__ == "__main__":
    main()
