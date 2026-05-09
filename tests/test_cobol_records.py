from decimal import Decimal

import pytest

from banking.cobol_records import (
    format_customer_record,
    format_transaction_record,
    parse_customer_record,
    parse_transaction_record,
)
from banking.models import Transaction


def test_parse_customer_record_preserves_cobol_fields_and_status_suffix():
    record = parse_customer_record(
        "345akeem55Akeem Mohammed                     2441SA"
    )

    assert record.account_id == "345akeem55"
    assert record.name == "Akeem Mohammed"
    assert record.balance == Decimal("2441")
    assert record.account_type == "S"
    assert record.status_suffix == "A"


def test_format_customer_record_outputs_cobol_width_without_status_by_default():
    line = format_customer_record(
        account_id="acct-1",
        name="Example Customer",
        balance=Decimal("1250"),
        account_type="C",
    )

    assert len(line) == 50
    assert line[:10] == "acct-1    "
    assert line[10:40] == "Example Customer              "
    assert line[40:49] == "     1250"
    assert line[49:50] == "C"


def test_format_customer_record_can_preserve_status_suffix_and_cents():
    line = format_customer_record(
        account_id="long-account-id",
        name="Example Customer With A Very Long Name",
        balance=Decimal("12.34"),
        account_type="S",
        status_suffix="A",
    )

    assert len(line) == 51
    assert line[:10] == "long-accou"
    assert line[10:40] == "Example Customer With A Very L"
    assert line[40:49] == "    12.34"
    assert line[49:51] == "SA"


def test_parse_transaction_record_uses_cobol_fixed_width_fields():
    record = parse_transaction_record("345akeem55D     20002025/07/2721:12:16")

    assert record.account_id == "345akeem55"
    assert record.transaction_type == "D"
    assert record.amount == Decimal("2000")
    assert record.date == "2025/07/27"
    assert record.time == "21:12:16"


def test_format_transaction_record_outputs_cobol_width():
    line = format_transaction_record(
        Transaction("acct-1", "D", Decimal("25"), "2025/07/27", "01:02:03")
    )

    assert len(line) == 38
    assert line == "acct-1    D       252025/07/2701:02:03"


def test_parse_blank_amount_as_zero_for_legacy_compatibility():
    record = parse_transaction_record("acct-1    D         2025/07/2701:02:03")

    assert record.amount == Decimal("0")


@pytest.mark.parametrize("line", ["short", "acct      name"])
def test_parse_customer_record_rejects_short_rows(line):
    with pytest.raises(ValueError, match="customer record"):
        parse_customer_record(line)


def test_parse_transaction_record_rejects_short_rows():
    with pytest.raises(ValueError, match="transaction record"):
        parse_transaction_record("short")


def test_parse_records_reject_invalid_amounts():
    with pytest.raises(ValueError, match="invalid customer record amount"):
        parse_customer_record("acct-1    " + "Name".ljust(30) + "      bad" + "S")

    with pytest.raises(ValueError, match="invalid transaction record amount"):
        parse_transaction_record("acct-1    D      bad2025/07/2701:02:03")


def test_format_amount_rejects_values_that_do_not_fit_cobol_width():
    with pytest.raises(ValueError, match="does not fit"):
        format_customer_record("acct", "Name", Decimal("1234567890"), "S")
