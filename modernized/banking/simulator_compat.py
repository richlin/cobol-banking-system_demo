from decimal import Decimal, InvalidOperation

from banking.models import AccountNotFound, InsufficientFunds


def apply_simulator_action(service, action):
    action_type = action["type"]

    if action_type == "create":
        service.create_account(
            action["account_id"],
            action["name"],
            Decimal(str(action["balance"])),
            action["account_type"],
        )
        return "applied"

    if action_type == "deposit":
        amount = _parse_positive_amount(action["amount"])
        if amount is None:
            return "rejected"
        try:
            service.deposit(action["account_id"], amount)
        except AccountNotFound:
            return "not_found"
        return "applied"

    if action_type == "withdraw":
        amount = _parse_positive_amount(action["amount"])
        if amount is None:
            return "rejected"
        try:
            service.withdraw(action["account_id"], amount)
        except AccountNotFound:
            return "not_found"
        except InsufficientFunds:
            return "insufficient_funds"
        return "applied"

    if action_type == "apply_interest":
        service.apply_interest()
        return "applied"

    if action_type in {"view_accounts", "mini_statement", "invalid_menu"}:
        return "read_only"

    raise ValueError(f"unknown simulator action type: {action_type}")


def _parse_positive_amount(raw_amount):
    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, ValueError):
        return None
    if amount <= 0:
        return None
    return amount
