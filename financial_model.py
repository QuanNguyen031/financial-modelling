import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass, field
from typing import List

from balance_sheet import BalanceSheet
from cash_flow import CashFlow, Income, Expense
from asset import Savings, ManagedFund, Shares, Property, Superannuation, LifestyleAsset
from liability import HomeLoan, OtherLiability

@dataclass
class FinancialModel:
    balance_sheet: BalanceSheet
    cash_flow: CashFlow
    events: List[int] = field(default_factory=list)

    def plot(self, balancesheet, cashflow):
        balance_df = pd.DataFrame(balancesheet)
        cashflow_df = pd.DataFrame(cashflow)
        df = balance_df.merge(cashflow_df, on="year", how="left")

        plt.figure(figsize=(10, 6))

        plt.bar(df["year"], df["total_assets"], label="Total Assets", alpha=0.6, color="skyblue")
        plt.bar(df["year"], -df["total_liabilities"], label="Total Liabilities", alpha=0.6, color="salmon")

        plt.plot(df["year"], df["inflow"], label="Inflow", linewidth=2.5)
        plt.plot(df["year"], -df["outflow"], label="Outflow", linewidth=2.5)

        plt.plot(df["year"], df["net_worth"], label="Net Worth", marker="o", linewidth=2.5)
        plt.plot(df["year"], df["net_flow"], label="Net Cash Flow", color="purple", marker="D", linewidth=2.5)

        for year in self.events:
            plt.axvline(x=year, linestyle="--", linewidth=1.5)

        plt.xlabel("Year")
        plt.ylabel("Amount")
        plt.title("Financial Projection (Balance Sheet + Cash Flow)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.xticks(df["year"], rotation=45)
        plt.legend()

        plt.tight_layout()
        plt.show()
    
    def model(self, start_year, end_year):
        bs_projection = self.balance_sheet.project(start_year, end_year)
        cf_projection = self.cash_flow.project(start_year, end_year)
        self.plot(bs_projection, cf_projection)

if __name__ == "__main__":
    assets = [
        Savings(initial_value=25_000, start_year=2025),
        Savings(initial_value=15_000, annual_contribution=2_000, start_year=2065),
        ManagedFund(initial_value=12_000, start_year=2029),
        Property(initial_value=100_000, start_year=2032),
        Shares(initial_value=30_000, start_year=2025),
        Superannuation(initial_value=12_000, salary=80_000, start_year=2025),
        LifestyleAsset(initial_value=30_000, start_year=2025, depreciation_rate=0.15)
    ]
    liabilities = [
        HomeLoan(initial_value=500_000, interest_rate=0.05, term_years=30, start_year=2025),
        OtherLiability(initial_value=450_000, interest_rate=0.07, annual_repayment=32_000, start_year=2028)
    ]
    balance_sheet = BalanceSheet(assets, liabilities)

    incomes = [
        # Income(name="Salary", amount=100_000, annual_rate=0.03, start_year=2024, end_year=2040),
        # Income(name="Rental Income", amount=20_000, annual_rate=0.02, start_year=2026)
    ]
    expenses = [
        # Expense(name="Living Expenses", amount=40_000, start_year=2024),
        # Expense(name="Vacation Expenses", amount=100_000, start_year=2027, end_year=2027),
    ]
    cash_flow = CashFlow(incomes, expenses)

    start, end = 2025, 2070
    financial_model = FinancialModel(balance_sheet, cash_flow)
    financial_model.model(start, end)
