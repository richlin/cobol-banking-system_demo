from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_legacy_inventory_maps_cobol_source_of_truth():
    inventory = (ROOT / "docs" / "legacy_inventory.md").read_text()

    required_terms = [
        "IDENTIFICATION DIVISION",
        "ENVIRONMENT DIVISION",
        "DATA DIVISION",
        "PROCEDURE DIVISION",
        "CUSTOMER-RECORD",
        "TRANSACTION-RECORD",
        "WORKING-STORAGE",
        "MAIN-PARA",
        "CREATE-ACCOUNT",
        "VIEW-ACCOUNTS",
        "DEPOSIT-MONEY",
        "WITHDRAW-MONEY",
        "UPDATE-BALANCE-ADD",
        "UPDATE-BALANCE-SUBTRACT",
        "WRITE-CUSTOMER-RECORD",
        "MINI-STATEMENT",
        "APPLY-INTEREST",
        "LOG-TRANSACTION-DEPOSIT",
        "LOG-TRANSACTION-WITHDRAW",
        "LOG-TRANSACTION-INTEREST",
        "GET-CURRENT-DATETIME",
    ]

    for term in required_terms:
        assert term in inventory


def test_legacy_inventory_documents_simulator_mismatches():
    inventory = (ROOT / "docs" / "legacy_inventory.md").read_text()

    assert "simulator" in inventory.lower()
    assert "51" in inventory
    assert "status suffix" in inventory.lower()
    assert "delete" in inventory.lower()
