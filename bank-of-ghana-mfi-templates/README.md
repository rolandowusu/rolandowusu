# Bank of Ghana — Microfinance Institution financial statements template

`BoG_MFI_Financial_Statements_Template.xlsx` is a working Excel template for a Ghanaian
microfinance institution's balance sheet, income statement and cash flow statement, built to
the structure a Bank of Ghana prudential return expects and to IFRS as applied by Ghanaian
deposit-taking institutions.

## Sheets

| Sheet | What it does |
|---|---|
| **Cover** | Purpose, colour and sign convention, list of built-in checks, sources and limitations. |
| **Setup** | Institution name, licence tier, both reporting period dates, share count. Every statement heading reads from here. |
| **Balance Sheet** | Statement of financial position, current and prior period, with a movement column and a balance check. |
| **Income Statement** | Statement of comprehensive income through to total comprehensive income, plus appropriations and EPS. |
| **Cash Flow Statement** | Indirect method. The current-period operating section is derived from the other two statements. |
| **Changes in Equity** | Stated capital, statutory reserve, credit risk reserve, revaluation reserve, income surplus — both periods, checked back to the balance sheet. |
| **Loan Classification** | Portfolio by days past due, minimum provision by class, credit risk (regulatory) reserve computation, PAR>30 and NPL ratio. |
| **Prudential Ratios** | Adjusted capital base, capital adequacy, liquidity and reserves, single obligor and deposit concentration, asset quality, profitability and efficiency. |
| **Worked Example** | A fictitious but fully articulating set of figures showing the expected format and sign convention. |

## Ghana-specific content

- Susu deposits as a deposit category.
- Statutory reserve fund and the **credit risk (regulatory) reserve** — the excess of the Bank of
  Ghana minimum provision over the IFRS 9 allowance, appropriated from income surplus rather
  than charged to profit or loss. The Loan Classification sheet computes the required balance.
- Loan classification by days past due: Current, OLEM, Substandard, Doubtful, Loss.
- Growth and Sustainability Levy line on the income statement.
- Amounts in Ghana Cedis (GH¢).

## Conventions

- **Cream fill, blue text** — a cell you type in. Everything else is a formula.
- **Yellow fill** — a regulatory threshold or key assumption to confirm before you rely on it.
- **Green text** — a link to another sheet.
- **Green fill** — a check cell; it reads `OK` or names the difference.
- Expenses, the impairment charge, the tax charge, dividends and the impairment allowance are
  entered as **negative numbers**.

## Order of completion

1. Setup 2. Balance Sheet 3. Income Statement 4. Loan Classification
5. Cash Flow Statement (investing, financing, prior-period column) 6. Changes in Equity
7. Prudential Ratios (yellow thresholds) 8. Clear every check cell to `OK`.

## What this is not

This is not a scan or reproduction of an official Bank of Ghana form, and it does not replace
the return templates the Bank issues to licensed institutions. **No minimum paid-up capital,
capital adequacy ratio, reserve requirement or single obligor limit is asserted as fact
anywhere in the workbook** — every one of those sits in a yellow cell for you to enter from the
notice in force. The provision rates pre-filled on the Loan Classification sheet (1% / 10% /
25% / 50% / 100%) are the rates commonly applied to microfinance institutions and are marked
yellow for the same reason.

The Bank of Ghana website was not reachable from the environment this workbook was built in, so
the current thresholds could not be read off the source documents. Check them against:

- Operating Rules and Guidelines for Microfinance Institutions (Notice BG/GOV/SEC/2011/04, as amended)
- Notice No. 3/BOG/SEC/GOV/2026 — revised microfinance sector framework
- Banks and Specialised Deposit-Taking Institutions Act, 2016 (Act 930), s.34 on the statutory reserve fund
- Non-Bank Financial Institutions Act, 2008 (Act 774)
