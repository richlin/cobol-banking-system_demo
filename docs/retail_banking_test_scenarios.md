# Retail Banking Test Scenario Catalog

This catalog thinks from a retail banking customer's point of view. It separates scenarios the current modernized application can test now from scenarios that should guide future product expansion.

## Coverage Legend

- `current`: supported by the current modernized COBOL banking scope.
- `compat`: supported as simulator-derived compatibility behavior.
- `future`: realistic retail banking behavior not implemented yet.

## Customer Onboarding and Account Opening

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-001 | P0 | current | Customer opens a savings account with valid ID, name, initial balance, and account type. | Account is created and persisted. |
| RB-002 | P0 | current | Customer opens a checking account with valid data. | Account is created with checking type. |
| RB-003 | P1 | compat | Customer name is longer than the legacy 30-character field. | Stored/displayed value is truncated to the fixed-width field behavior. |
| RB-004 | P1 | compat | Account ID is longer than 10 characters. | Stored/displayed account ID follows fixed-width truncation behavior. |
| RB-005 | P1 | future | Customer tries to open an account with duplicate account ID. | System rejects or defines deterministic duplicate handling. |
| RB-006 | P1 | future | Customer opens account with zero initial balance. | Product rule determines whether zero balance is allowed. |
| RB-007 | P1 | future | Customer opens account with negative initial balance. | Account creation is rejected. |
| RB-008 | P1 | future | Customer enters invalid account type. | Account creation is rejected with a clear error. |
| RB-009 | P2 | future | Customer enters blank name. | Account creation is rejected. |
| RB-010 | P2 | future | Customer enters name with punctuation or non-ASCII characters. | Name is accepted or normalized according to product rules. |

## Account Viewing and Inquiry

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-011 | P0 | current | Customer views all accounts after multiple accounts exist. | Accounts are returned in persisted order. |
| RB-012 | P1 | compat | Customer views accounts when no accounts exist. | Empty-state message or empty result is returned. |
| RB-013 | P1 | future | Customer searches for one account by ID. | Matching account details are returned. |
| RB-014 | P1 | future | Customer searches for a missing account. | Not-found response is returned. |
| RB-015 | P2 | future | Customer views account after migration from old 50-character records. | Account data is parsed correctly without a status suffix. |
| RB-016 | P2 | future | Customer views account after migration from 51-character simulator records. | Account data and status metadata are preserved. |

## Deposits

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-017 | P0 | current | Customer deposits money into an existing savings account. | Balance increases and deposit transaction is logged. |
| RB-018 | P0 | current | Customer deposits money into an existing checking account. | Balance increases and deposit transaction is logged. |
| RB-019 | P0 | current | Customer deposits into missing account. | Account-not-found behavior occurs and no transaction is logged. |
| RB-020 | P1 | compat | Customer deposits zero amount. | Simulator-compatible input validation rejects the amount. |
| RB-021 | P1 | compat | Customer deposits negative amount. | Simulator-compatible input validation rejects the amount. |
| RB-022 | P1 | compat | Customer enters non-numeric deposit amount. | Simulator-compatible input validation rejects the amount. |
| RB-023 | P1 | future | Customer deposits cents, such as 10.25. | Balance and transaction amount preserve cents according to product rules. |
| RB-024 | P1 | future | Customer deposits amount exceeding single-transaction limit. | Transaction is rejected and auditable. |
| RB-025 | P2 | future | Customer deposits into inactive account. | Deposit is rejected if inactive status is implemented. |

## Withdrawals

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-026 | P0 | current | Customer withdraws available funds from savings. | Balance decreases and withdrawal transaction is logged. |
| RB-027 | P0 | current | Customer withdraws available funds from checking. | Balance decreases and withdrawal transaction is logged. |
| RB-028 | P0 | current | Customer withdraws more than available balance. | Withdrawal is rejected and no transaction is logged. |
| RB-029 | P0 | current | Customer withdraws from missing account. | Account-not-found behavior occurs and no transaction is logged. |
| RB-030 | P1 | compat | Customer withdraws zero amount. | Simulator-compatible input validation rejects the amount. |
| RB-031 | P1 | compat | Customer withdraws negative amount. | Simulator-compatible input validation rejects the amount. |
| RB-032 | P1 | compat | Customer enters non-numeric withdrawal amount. | Simulator-compatible input validation rejects the amount. |
| RB-033 | P1 | future | Customer withdraws exact full balance. | Balance becomes zero and transaction is logged. |
| RB-034 | P1 | future | Customer withdraws cents, such as 10.25. | Balance and transaction amount preserve cents according to product rules. |
| RB-035 | P1 | future | Customer exceeds daily withdrawal limit. | Transaction is rejected with limit reason. |
| RB-036 | P2 | future | Customer withdraws from inactive account. | Withdrawal is rejected if inactive status is implemented. |

## Interest

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-037 | P0 | current | Bank applies interest to one savings account. | Balance increases by 2% and interest transaction is logged. |
| RB-038 | P0 | current | Bank applies interest when checking accounts also exist. | Only savings accounts receive interest. |
| RB-039 | P1 | compat | Bank applies interest when no savings accounts exist. | No balances change and no interest transaction is logged. |
| RB-040 | P1 | current | Bank applies interest to multiple savings accounts. | Each savings account receives one interest transaction. |
| RB-041 | P1 | future | Bank applies interest twice. | Product rule decides whether repeated application is allowed or blocked by period. |
| RB-042 | P2 | future | Bank applies interest to inactive savings account. | Interest is skipped if inactive status is implemented. |
| RB-043 | P2 | future | Interest creates fractional cents. | Rounding mode is deterministic and documented. |

## Statements and Transaction History

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-044 | P0 | current | Customer views mini statement with fewer than five transactions. | All matching transactions are returned. |
| RB-045 | P0 | current | Customer views mini statement with more than five transactions. | Current COBOL-derived behavior returns the first five matching records. |
| RB-046 | P1 | compat | Simulator mini statement displays last five transactions. | Compatibility fixture records simulator-observed behavior separately. |
| RB-047 | P1 | compat | Customer views mini statement when no transactions exist. | Empty history response is returned. |
| RB-048 | P1 | compat | Customer views mini statement when transaction file is missing. | Missing-history response is returned. |
| RB-049 | P1 | future | Customer filters statement by date range. | Only transactions in range are returned. |
| RB-050 | P1 | future | Customer downloads full statement. | Complete account transaction history is exported. |
| RB-051 | P2 | future | Customer sees mixed transaction types: deposit, withdrawal, interest, delete. | Display labels are correct for each transaction type. |

## Data Migration and Data Quality

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-052 | P0 | current | Migrate current `legacy/CUSTOMERS.DAT`. | All valid customer rows are imported. |
| RB-053 | P0 | current | Migrate current `legacy/TRANSACTIONS.DAT`. | All valid transaction rows are imported. |
| RB-054 | P0 | current | Migrate malformed customer row. | Row is rejected with source, line number, raw text, and reason. |
| RB-055 | P0 | current | Migrate malformed transaction row. | Row is rejected with source, line number, raw text, and reason. |
| RB-056 | P1 | current | Migrate old 50-character customer row without status suffix. | Customer imports successfully with no status metadata. |
| RB-057 | P1 | current | Migrate 51-character customer row with status suffix. | Customer imports successfully and preserves status metadata. |
| RB-058 | P1 | future | Migrate duplicate account IDs. | Duplicates are rejected or deterministically resolved. |
| RB-059 | P1 | future | Migrate blank lines in data files. | Blank lines are ignored. |
| RB-060 | P2 | future | Migrate amount field with non-numeric value. | Row is rejected with a useful reason. |
| RB-061 | P2 | future | Migrate transaction for missing account. | Product rule decides whether orphan transactions are imported or rejected. |

## Account Lifecycle and Status

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-062 | P1 | compat | Simulator marks account inactive through delete flow. | Simulator fixture captures inactive metadata if compatibility testing includes delete. |
| RB-063 | P1 | future | Customer tries to transact on inactive account. | Transaction is rejected. |
| RB-064 | P1 | future | Customer reactivates inactive account. | Status changes to active with audit trail. |
| RB-065 | P2 | future | Customer closes account with non-zero balance. | Closure is rejected or requires balance transfer. |
| RB-066 | P2 | future | Customer closes account with zero balance. | Account is closed and audited. |

## Transfers and Payments

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-067 | P1 | future | Customer transfers from savings to checking. | Source decreases, destination increases, both ledger entries are recorded. |
| RB-068 | P1 | future | Customer transfers more than available balance. | Transfer is rejected atomically. |
| RB-069 | P1 | future | Customer transfers to missing account. | Transfer is rejected and source balance is unchanged. |
| RB-070 | P1 | future | Customer transfers from missing account. | Transfer is rejected. |
| RB-071 | P2 | future | Customer schedules future-dated payment. | Payment is stored pending execution. |
| RB-072 | P2 | future | Customer cancels scheduled payment. | Payment is cancelled and cannot execute. |

## Fees, Holds, and Limits

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-073 | P2 | future | Monthly maintenance fee is applied. | Fee transaction is logged and balance decreases. |
| RB-074 | P2 | future | Fee would overdraw account. | Product rule decides whether fee posts or is waived/rejected. |
| RB-075 | P2 | future | Deposit is held before becoming available. | Ledger balance and available balance differ until hold expires. |
| RB-076 | P2 | future | Customer attempts withdrawal against held funds. | Withdrawal is rejected if available balance is insufficient. |
| RB-077 | P2 | future | Customer exceeds deposit velocity limits. | Transaction is rejected or flagged. |

## Audit, Reliability, and Operational Risk

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-078 | P0 | current | Successful deposit writes exactly one transaction. | No duplicate ledger entry is created. |
| RB-079 | P0 | current | Failed withdrawal writes no transaction. | Audit trail does not show a posted withdrawal. |
| RB-080 | P1 | future | Storage write fails during transaction. | Operation rolls back atomically. |
| RB-081 | P1 | future | Two withdrawals happen concurrently. | Final balance is consistent and cannot overdraw accidentally. |
| RB-082 | P1 | future | Migration is run twice. | Import is idempotent or documented as non-idempotent with safeguards. |
| RB-083 | P2 | future | System clock changes during transaction. | Date/time handling remains deterministic enough for audit. |
| RB-084 | P2 | future | Application restarts after write. | Persisted account and transaction state remains readable. |

## Security, Privacy, and Access Control

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-085 | P1 | future | Unauthenticated user attempts to view accounts. | Request is rejected. |
| RB-086 | P1 | future | Customer attempts to view another customer's account. | Request is rejected. |
| RB-087 | P1 | future | Teller/admin views account with proper permission. | Request succeeds and is audited. |
| RB-088 | P1 | future | Sensitive data appears in logs. | Logs exclude or mask sensitive data. |
| RB-089 | P2 | future | Malicious account ID contains SQL-like text. | Input is treated as data and cannot alter storage. |
| RB-090 | P2 | future | Malicious name contains control characters. | Input is normalized or rejected according to policy. |

## Accessibility and User Experience

| ID | Priority | Scope | Scenario | Expected Outcome |
| --- | --- | --- | --- | --- |
| RB-091 | P2 | future | Customer receives validation error. | Error explains what to correct. |
| RB-092 | P2 | future | Customer repeats same submit action. | System prevents accidental duplicate posting. |
| RB-093 | P2 | future | Customer uses mobile UI with narrow viewport. | Critical account actions remain usable. |
| RB-094 | P2 | future | Customer uses screen reader. | Account balances, actions, and errors are announced correctly. |

## Current Automation Recommendations

1. Keep all `current` and `compat` scenarios automated in pytest.
2. Promote `future` scenarios into tests before implementing each new capability.
3. Do not use simulator-only behavior to override `legacy/BANKACCT.cob` behavior unless a decision record explicitly changes the source-of-truth rule.
4. For money movement scenarios, assert both balance changes and transaction-log side effects.
5. For failed transactions, assert both customer-visible error behavior and absence of ledger mutation.
