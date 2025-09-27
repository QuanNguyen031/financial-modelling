from abc import ABC, abstractmethod
from dataclasses import dataclass

from balance_sheet import BalanceSheet
from cash_flow import CashFlow, Income, Expense
from asset import Property, Savings
from liability import HomeLoan

@dataclass
class LifeEvent(ABC):
    start_year: int
    name: str

    @abstractmethod
    def apply(self, balance_sheet: BalanceSheet, cash_flow: CashFlow) -> None:
        raise NotImplementedError

@dataclass
class HomePurchase(LifeEvent):
    purchase_price: float
    appreciation_rate: float
    mortgage_rate: float
    mortgage_term_years: int
    deposit: float = 0.0
    maintenance_cost: float = 0.0
    maintenance_growth: float = 0.02

    def apply(self, balance_sheet: BalanceSheet, cash_flow: CashFlow) -> None:
        balance_sheet.assets.append(
            Property(
                initial_value=self.purchase_price,
                start_year=self.start_year,
                annual_appreciation=self.appreciation_rate,
            )
        )
        
        if self.deposit > 0:
            cash_flow.expenses.append(Expense(name="Deposit", amount=self.deposit, start_year=self.start_year, end_year=self.start_year))

        loan_amount = max(self.purchase_price - self.deposit, 0.0)
        if loan_amount > 0:
            home_loan = HomeLoan(
                initial_value=loan_amount,
                start_year=self.start_year,
                interest_rate=self.mortgage_rate,
                term_years=self.mortgage_term_years,
            )
            balance_sheet.liabilities.append(home_loan)

            cash_flow.expenses.append(
                Expense(
                    name="Mortgage repayment",
                    amount=home_loan.annual_payment(),
                    start_year=self.start_year,
                    end_year=self.start_year + self.mortgage_term_years - 1,
                    annual_rate=0.0,
                )
            )

        if self.maintenance_cost > 0:
            cash_flow.expenses.append(
                Expense(
                    name="Property maintenance",
                    amount=self.maintenance_cost,
                    start_year=self.start_year,
                    annual_rate=self.maintenance_growth,
                )
            )

@dataclass
class ChildBirth(LifeEvent):
    annual_cost: float
    years_of_expense: int
    expense_growth: float = 0.03

    def apply(self, balance_sheet: BalanceSheet, cash_flow: CashFlow) -> None:
        end_year = self.start_year + max(self.years_of_expense - 1, 0)
        cash_flow.expenses.append(
            Expense(
                name="Child related expenses",
                amount=self.annual_cost,
                start_year=self.start_year,
                annual_rate=self.expense_growth,
                end_year=end_year,
            )
        )

@dataclass
class Inheritance(LifeEvent):
    amount: float
    savings_interest_rate: float = 0.04
    add_to_cash_flow: bool = True

    def apply(self, balance_sheet: BalanceSheet, cash_flow: CashFlow) -> None:
        balance_sheet.assets.append(
            Savings(
                initial_value=self.amount,
                start_year=self.start_year,
                interest_rate=self.savings_interest_rate,
                annual_contribution=0,
            )
        )

        if self.add_to_cash_flow:
            cash_flow.incomes.append(
                Income(
                    name="Inheritance",
                    amount=self.amount,
                    annual_rate=0.0,
                    start_year=self.start_year,
                    end_year=self.start_year,
                )
            )
