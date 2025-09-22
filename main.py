import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass, field
from typing import List

from balance_sheet import BalanceSheet, Asset, Liability, GrowthType
from cash_flow import CashFlow, Income, Expense

@dataclass
class BuyHouseEvent:
    year: int
    house_value: float
    mortgage_value: float
    mortgage_rate: float
    mortgage_term: int

    def apply(self, balance_sheet: BalanceSheet, cash_flow: CashFlow) -> None:
        house = Asset(
            name="House",
            initial_value=self.house_value,
            growth_type=GrowthType.APPRECIATING,
            annual_rate=0.03,
            start_year=self.year,
        )
        mortgage = Liability(
            name="Mortgage",
            initial_balance=self.mortgage_value,
            growth_type=GrowthType.AMORTISING,
            annual_rate=self.mortgage_rate,
            term_years=self.mortgage_term,
            start_year=self.year
        )
        expense = Expense(
            name="Mortgage repayment",
            amount=mortgage.annual_payment(),
            start_year=mortgage.start_year,
            end_year=mortgage.start_year + mortgage.term_years
        )

        balance_sheet.assets.append(house)
        balance_sheet.liabilities.append(mortgage)
        cash_flow.expenses.append(expense)

@dataclass
class FinancialModel:
    balance_sheet: BalanceSheet
    cash_flow: CashFlow
    events: List[int] = field(default_factory=list)

    def add_event(self, event: BuyHouseEvent):
        event.apply(self.balance_sheet, self.cash_flow)
        self.events.append(event.year)

    def plot(self, balancesheet, cashflow):
        balance_df = pd.DataFrame(balancesheet)
        cashflow_df = pd.DataFrame(cashflow)
        df = balance_df.merge(cashflow_df, on="year", how="left")

        plt.figure(figsize=(10, 6))

        plt.bar(df["year"], df["total_assets"], label="Total Assets", alpha=0.6, color="skyblue")
        plt.bar(df["year"], -df["total_liabilities"], label="Total Liabilities", alpha=0.6, color="salmon")

        plt.plot(df["year"], df["inflow"], label="Inflow")
        plt.plot(df["year"], -df["outflow"], label="Outflow")

        plt.plot(df["year"], df["net_worth"], label="Net Worth", color="green", marker="o", linewidth=2)
        plt.plot(df["year"], df["net_flow"], label="Net Cash Flow", color="purple", marker="D", linewidth=2)

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
        Asset(name="Savings", initial_value=50_000, growth_type=GrowthType.FLAT, annual_rate=0, start_year=2024),
        Asset(name="Investments", initial_value=30_000, growth_type=GrowthType.APPRECIATING, annual_rate=0.15, start_year=2024),
        Asset(name="Lifestyle Assets", initial_value=80_000, growth_type=GrowthType.DEPRECIATING, annual_rate=0.05, start_year=2026),
        Asset(name="Property", initial_value=200_000, growth_type=GrowthType.APPRECIATING, annual_rate=0.04, start_year=2028),
        Asset(name="Superannuation", initial_value=100_000, growth_type=GrowthType.FLAT, annual_rate=0, start_year=2024),
    ]
    liabilities = [
        # Liability(name="Home Loan", initial_balance=150_000, growth_type=GrowthType.AMORTISING, annual_rate=0.04, term_years=15, start_year=2028),
        # Liability(name="Other Loan", initial_balance=100_000, growth_type=GrowthType.AMORTISING, annual_rate=0.06, term_years=5,  start_year=2025),
    ]
    balance_sheet = BalanceSheet(assets, liabilities)

    incomes = [
        Income(name="Salary", amount=100_000, annual_rate=0.03, start_year=2024, end_year=2040),
        Income(name="Rental Income", amount=20_000, annual_rate=0.02, start_year=2026)
    ]
    expenses = [
        Expense(name="Living Expenses", amount=40_000, start_year=2024),
        # Expense(name="Vacation Expenses", amount=100_000, start_year=2027, end_year=2027),
    ]
    cash_flow = CashFlow(incomes, expenses)

    life_events = [
        BuyHouseEvent(year=2030, house_value=500_000, mortgage_value=300_000, mortgage_rate=0.05, mortgage_term=10)
    ]

    start, end = 2024, 2050
    financial_model = FinancialModel(balance_sheet, cash_flow)

    for event in life_events:
        financial_model.add_event(event)
    financial_model.model(start, end)
