import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence, Tuple

from balance_sheet import BalanceSheet
from cash_flow import CashFlow, Income, Expense
from asset import Savings, ManagedFund, Shares, Property, Superannuation, LifestyleAsset
from liability import HomeLoan, OtherLiability
from life_event import LifeEvent, HomePurchase, ChildBirth, Inheritance

@dataclass
class FinancialModel:
    balance_sheet: BalanceSheet
    cash_flow: CashFlow
    events: List[LifeEvent] = field(default_factory=list)

    def plot(
        self,
        balance_projection: Iterable[dict],
        cash_flow_projection: Iterable[dict],
        events: Sequence[LifeEvent],
    ) -> None:
        balance_df = pd.DataFrame(balance_projection)
        cashflow_df = pd.DataFrame(cash_flow_projection)
        df = balance_df.merge(cashflow_df, on="year", how="left")

        if df.empty:
            return

        asset_key = "total_assets"
        liability_key = "total_liabilities"
        net_worth_key = "net_worth"
        inflow_key = "inflow"
        outflow_key = "outflow"
        net_flow_key = "net_flow"

        label_suffix = ""
        amount_label = "Amount"

        plt.figure(figsize=(10, 6))

        plt.bar(df["year"], df[asset_key], label=f"Total Assets{label_suffix}", alpha=0.6, color="skyblue")
        plt.bar(df["year"], -df[liability_key], label=f"Total Liabilities{label_suffix}", alpha=0.6, color="salmon")

        plt.plot(df["year"], df[inflow_key], label=f"Inflow{label_suffix}", linewidth=2.5)
        plt.plot(df["year"], -df[outflow_key], label=f"Outflow{label_suffix}", linewidth=2.5)

        plt.plot(df["year"], df[net_worth_key], label=f"Net Worth{label_suffix}", marker="o", linewidth=2.5)
        plt.plot(df["year"], df[net_flow_key], label=f"Net Cash Flow{label_suffix}", color="purple", marker="D", linewidth=2.5)

        for event in events:
            plt.axvline(x=event.start_year, linestyle="--", linewidth=1.5, color="grey", alpha=0.7)

        if events:
            _, ymax = plt.ylim()
            for idx, event in enumerate(events):
                plt.text(
                    event.start_year,
                    ymax,
                    event.name,
                    rotation=90,
                    va="bottom",
                    ha="right",
                    fontsize=8,
                    alpha=0.7,
                    rotation_mode="anchor",
                )

        ax = plt.gca()
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))

        plt.xlabel("Year")
        plt.ylabel(amount_label)
        plt.title("Financial Projection (Balance Sheet + Cash Flow)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.xticks(df["year"], rotation=45)
        plt.legend()

        plt.tight_layout()
        plt.show()

    """TODO: review"""
    def _components_with_events(
        self, start_year: int, end_year: int
    ) -> Tuple[BalanceSheet, CashFlow, List[LifeEvent]]:
        balance_sheet = deepcopy(self.balance_sheet)
        cash_flow = deepcopy(self.cash_flow)
        active_events: List[LifeEvent] = []

        for event in sorted(self.events, key=lambda e: e.start_year):
            if event.start_year > end_year:
                continue
            event.apply(balance_sheet, cash_flow)
            active_events.append(event)

        return balance_sheet, cash_flow, active_events

    def _add_real_terms(
        self,
        projection: Iterable[dict],
        base_year: int,
        keys: Sequence[str],
    ) -> List[dict]:
        entries = [dict(entry) for entry in projection]
        if not entries:
            return []

        if self.inflation_rate == 0:
            return entries

        rate_base = 1 + self.inflation_rate
        if rate_base <= 0:
            raise ValueError("Inflation rate must be greater than -100%.")

        for entry in entries:
            year = entry.get('year')
            if year is None:
                continue

            years_elapsed = year - base_year
            factor = rate_base ** years_elapsed

            for key in keys:
                if key in entry:
                    entry[f"{key}_real"] = entry[key] / factor

        return entries

    def model(self, start_year: int, end_year: int) -> Tuple[List[dict], List[dict]]:
        balance_sheet, cash_flow, active_events = self._components_with_events(start_year, end_year)

        bs_projection = balance_sheet.project(start_year, end_year)
        cf_projection = cash_flow.project(start_year, end_year)

        events_in_range = [event for event in active_events if start_year <= event.start_year <= end_year]
        self.plot(bs_projection, cf_projection, events_in_range)

        return bs_projection, cf_projection
    
    def set_inflation(self, inflation_rate: float):
        self.inflation_rate = inflation_rate

if __name__ == "__main__":
    assets = [
        Savings(initial_value=25_000, start_year=2025),
        Savings(initial_value=15_000, annual_contribution=2_000, start_year=2065),
        ManagedFund(initial_value=12_000, start_year=2029),
        Property(initial_value=100_000, start_year=2032),
        Shares(initial_value=30_000, start_year=2025),
        Superannuation(initial_value=12_000, salary=80_000, start_year=2025),
        LifestyleAsset(initial_value=30_000, start_year=2025, depreciation_rate=0.15),
    ]
    liabilities = [
        HomeLoan(initial_value=500_000, interest_rate=0.05, term_years=30, start_year=2025),
        OtherLiability(initial_value=450_000, interest_rate=0.07, annual_repayment=33_000, start_year=2028),
    ]
    balance_sheet = BalanceSheet(assets, liabilities)

    incomes = [
        Income(name="Salary", amount=100_000, annual_rate=0.07, start_year=2024),
        Income(name="Rental Income", amount=20_000, annual_rate=0.01, start_year=2026),
    ]
    expenses = [
        Expense(name="Living Expenses", amount=40_000, annual_rate=0.05, start_year=2024),
        Expense(name="Vacation Expenses", amount=100_000, start_year=2027, end_year=2027),
    ]
    cash_flow = CashFlow(incomes, expenses)

    events = [
        HomePurchase(
            name="First Home Purchase",
            start_year=2030,
            purchase_price=2_000_000,
            appreciation_rate=0.035,
            mortgage_rate=0.045,
            mortgage_term_years=30,
            deposit=120_000,
            maintenance_cost=3_500,
        ),
        ChildBirth(
            name="First Child",
            start_year=2032,
            annual_cost=15_000,
            years_of_expense=18,
        ),
        Inheritance(
            name="Family Inheritance",
            start_year=2045,
            amount=100_000,
            savings_interest_rate=0.045,
        ),
    ]

    start, end = 2025, 2070
    financial_model = FinancialModel(balance_sheet, cash_flow, events=events)
    financial_model.model(start, end)

