from decimal import Decimal

from banking.migration import main, migrate_files
from banking.storage import BankingDatabase


CUSTOMER_ROWS = [
    "345akeem55Akeem Mohammed                     2441SA",
    "678jemi345Jemi Mohammed                      1592SA",
    "4569364kimJohn Doe                          10000CI",
    "fkgreie345Jack Loom                         57720SA",
]

TRANSACTION_ROWS = [
    "345akeem55D     20002025/07/2721:12:16",
    "345akeem55I       462025/07/2721:12:55",
    "678jemi345I       302025/07/2721:12:55",
    "4569364kimX        02025/07/2721:21:02",
    "345akeem55I       472025/07/2722:25:28",
    "678jemi345I       312025/07/2722:25:28",
    "345akeem55I       482025/07/2722:26:19",
    "678jemi345I       312025/07/2722:26:19",
    "fkgreie345I     11202025/07/2722:26:19",
    "fkgreie345D      5002025/07/2717:46:54",
    "fkgreie345D      1002025/07/2717:47:58",
]


def write_lines(path, rows):
    path.write_text("\n".join(rows) + "\n")


def test_migrate_sample_data_imports_all_valid_rows_and_preserves_status(tmp_path):
    customers = tmp_path / "CUSTOMERS.DAT"
    transactions = tmp_path / "TRANSACTIONS.DAT"
    db_path = tmp_path / "banking.sqlite3"
    write_lines(customers, CUSTOMER_ROWS)
    write_lines(transactions, TRANSACTION_ROWS)

    report = migrate_files(customers, transactions, db_path)

    assert report.customer_rows == 4
    assert report.transaction_rows == 11
    assert report.rejected_rows == []

    db = BankingDatabase(db_path)
    accounts = db.list_accounts()
    migrated_transactions = db.list_transactions()

    assert len(accounts) == 4
    assert len(migrated_transactions) == 11
    assert accounts[0].account_id == "345akeem55"
    assert accounts[0].balance == Decimal("2441")
    assert accounts[0].status_suffix == "A"
    assert migrated_transactions[3].transaction_type == "X"


def test_migration_rejects_invalid_rows_with_reason(tmp_path):
    customers = tmp_path / "CUSTOMERS.DAT"
    transactions = tmp_path / "TRANSACTIONS.DAT"
    db_path = tmp_path / "banking.sqlite3"
    write_lines(customers, CUSTOMER_ROWS + ["bad"])
    write_lines(transactions, TRANSACTION_ROWS + ["also bad"])

    report = migrate_files(customers, transactions, db_path)

    assert report.customer_rows == 4
    assert report.transaction_rows == 11
    assert len(report.rejected_rows) == 2
    assert report.rejected_rows[0].source == "CUSTOMERS.DAT"
    assert "customer record" in report.rejected_rows[0].reason


def test_migration_ignores_blank_rows(tmp_path):
    customers = tmp_path / "CUSTOMERS.DAT"
    transactions = tmp_path / "TRANSACTIONS.DAT"
    db_path = tmp_path / "banking.sqlite3"
    write_lines(customers, CUSTOMER_ROWS + [""])
    write_lines(transactions, TRANSACTION_ROWS + [""])

    report = migrate_files(customers, transactions, db_path)

    assert report.customer_rows == 4
    assert report.transaction_rows == 11
    assert report.rejected_rows == []


def test_migration_main_reports_rejections(tmp_path, capsys):
    customers = tmp_path / "CUSTOMERS.DAT"
    transactions = tmp_path / "TRANSACTIONS.DAT"
    db_path = tmp_path / "banking.sqlite3"
    write_lines(customers, ["bad"])
    write_lines(transactions, ["also bad"])

    result = main([str(customers), str(transactions), str(db_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "customer rows imported: 0" in output
    assert "transaction rows imported: 0" in output
    assert "rejected rows: 2" in output
    assert "CUSTOMERS.DAT:1" in output


def test_migration_main_returns_success_when_all_rows_import(tmp_path, capsys):
    customers = tmp_path / "CUSTOMERS.DAT"
    transactions = tmp_path / "TRANSACTIONS.DAT"
    db_path = tmp_path / "banking.sqlite3"
    write_lines(customers, CUSTOMER_ROWS[:1])
    write_lines(transactions, TRANSACTION_ROWS[:1])

    result = main([str(customers), str(transactions), str(db_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "customer rows imported: 1" in output
    assert "transaction rows imported: 1" in output
    assert "rejected rows: 0" in output
