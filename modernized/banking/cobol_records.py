from decimal import Decimal, InvalidOperation

from banking.models import Account, Transaction


CUSTOMER_RECORD_WIDTH = 50
TRANSACTION_RECORD_WIDTH = 38


def _parse_amount(raw: str, record_name: str) -> Decimal:
    value = raw.strip()
    if value == "":
        return Decimal("0")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid {record_name} amount: {raw!r}") from exc


def _format_amount(value: Decimal) -> str:
    amount = Decimal(value)
    if amount == amount.to_integral_value():
        text = str(amount.to_integral_value())
    else:
        text = format(amount.quantize(Decimal("0.01")), "f")
    if len(text) > 9:
        raise ValueError(f"amount does not fit COBOL 9-character field: {text}")
    return text.rjust(9)


def parse_customer_record(line: str) -> Account:
    row = line.rstrip("\n")
    if len(row) < CUSTOMER_RECORD_WIDTH:
        raise ValueError(
            f"customer record must be at least {CUSTOMER_RECORD_WIDTH} characters"
        )

    return Account(
        account_id=row[0:10].strip(),
        name=row[10:40].strip(),
        balance=_parse_amount(row[40:49], "customer record"),
        account_type=row[49:50].strip(),
        status_suffix=row[50:].strip() or None,
    )


def format_customer_record(
    account_id: str,
    name: str,
    balance: Decimal,
    account_type: str,
    status_suffix: str = None,
) -> str:
    line = (
        f"{account_id[:10]:<10}"
        f"{name[:30]:<30}"
        f"{_format_amount(balance)}"
        f"{account_type[:1]}"
    )
    if status_suffix:
        line += status_suffix[:1]
    return line


def parse_transaction_record(line: str) -> Transaction:
    row = line.rstrip("\n")
    if len(row) < TRANSACTION_RECORD_WIDTH:
        raise ValueError(
            f"transaction record must be at least {TRANSACTION_RECORD_WIDTH} characters"
        )

    return Transaction(
        account_id=row[0:10].strip(),
        transaction_type=row[10:11].strip(),
        amount=_parse_amount(row[11:20], "transaction record"),
        date=row[20:30].strip(),
        time=row[30:38].strip(),
    )


def format_transaction_record(transaction: Transaction) -> str:
    return (
        f"{transaction.account_id[:10]:<10}"
        f"{transaction.transaction_type[:1]}"
        f"{_format_amount(transaction.amount)}"
        f"{transaction.date[:10]:<10}"
        f"{transaction.time[:8]:<8}"
    )
