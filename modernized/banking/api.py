from decimal import Decimal

from banking.domain import BankingService
from banking.storage import BankingDatabase


def create_app(db_path="banking.sqlite3"):
    try:
        from fastapi import FastAPI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FastAPI is optional for this repo. Install fastapi and uvicorn to run "
            "the HTTP adapter; core verification uses the CLI and SQLite service."
        ) from exc

    db = BankingDatabase(db_path)
    service = BankingService(db)
    app = FastAPI(title="Modernized COBOL Banking System")

    @app.get("/accounts")
    def list_accounts():
        return [account.__dict__ for account in service.view_accounts()]

    @app.post("/accounts")
    def create_account(account_id: str, name: str, balance: str, account_type: str):
        account = service.create_account(
            account_id, name, Decimal(balance), account_type
        )
        return account.__dict__

    @app.post("/accounts/{account_id}/deposit")
    def deposit(account_id: str, amount: str):
        return {"balance": str(service.deposit(account_id, Decimal(amount)))}

    @app.post("/accounts/{account_id}/withdraw")
    def withdraw(account_id: str, amount: str):
        return {"balance": str(service.withdraw(account_id, Decimal(amount)))}

    @app.post("/interest")
    def apply_interest():
        return [
            {"account_id": account_id, "amount": str(amount)}
            for account_id, amount in service.apply_interest()
        ]

    @app.get("/accounts/{account_id}/statement")
    def statement(account_id: str):
        return [transaction.__dict__ for transaction in service.mini_statement(account_id)]

    return app
