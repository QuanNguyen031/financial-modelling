from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Asset(ABC):
    initial_value: float
    start_year: int

    @abstractmethod
    def predict(self, target_year: int) -> float:
        pass
        
@dataclass
class Savings(Asset):
    interest_rate: float = 0.05
    annual_contribution: int = 0

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0.0

        time = target_year - self.start_year
        rate = self.interest_rate
        
        # fv = future value
        fv_principal = self.initial_value * ((1 + rate) ** time)
        if rate == 0:
            fv_contrib = self.annual_contribution * time
        else:
            fv_contrib = self.annual_contribution * (((1 + rate) ** time - 1) / rate)
        
        return fv_principal + fv_contrib

@dataclass
class ManagedFund(Asset):
    gross_return_rate: float = 0.07
    management_fee_rate: float = 0.008
    performance_fee_rate: float = 0.0
    annual_contribution: int = 0

    def net_rate(self) -> float:
        fee_cut = self.management_fee_rate + self.performance_fee_rate
        return (1 + self.gross_return_rate) * (1 - fee_cut) - 1

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0.0

        time = target_year - self.start_year
        rate = self.net_rate()

        fv_principal = self.initial_value * ((1 + rate) ** time)

        if rate == 0:
            fv_contrib = self.annual_contribution * time
        else:
            fv_contrib = self.annual_contribution * (((1 + rate) ** time) - 1) / rate

        return fv_principal + fv_contrib
    
@dataclass
class Shares(Asset):
    annual_growth_rate: float = 0.07
    dividend_yield: float = 0.03
    annual_contribution: int = 0
    reinvest_dividends: bool = True

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0.0

        time = target_year - self.start_year
        effective_rate = self.annual_growth_rate + (self.dividend_yield if self.reinvest_dividends else 0.0)

        fv_principal = self.initial_value * ((1 + effective_rate) ** time)

        if effective_rate == 0:
            fv_contrib = self.annual_contribution * time
        else:
            fv_contrib = self.annual_contribution * (((1 + effective_rate) ** time - 1) / effective_rate)

        return fv_principal + fv_contrib

@dataclass
class Property(Asset):
    annual_appreciation: float = 0.035

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0

        time = target_year - self.start_year
        return self.initial_value * ((1 + self.annual_appreciation) ** time)

@dataclass
class Superannuation(Asset):
    salary: float
    gross_return_rate: float = 0.07
    fee_rate: float = 0.008

    salary_growth: float = 0.03         # salary increases per year
    employer_sg_rate: float = 0.11      # employer Super Guarantee as % of salary
    personal_contribution: float = 0.0  # optional personal (concessional) $/yr
    personal_indexation: float = 0.0    # growth of personal contribution per year
    contribution_tax_rate: float = 0.15 # concessional contributions tax (approx)

    def net_investment_rate(self) -> float:
        return (1 + self.gross_return_rate) * (1 - self.fee_rate) - 1

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0.0

        years = target_year - self.start_year
        rate = self.net_investment_rate()

        balance = self.initial_value
        curr_salary = self.salary
        curr_personal = self.personal_contribution

        for _ in range(years):
            balance *= (1 + rate)

            employer = curr_salary * self.employer_sg_rate
            contrib_gross = employer + curr_personal
            contrib_net = contrib_gross * (1 - self.contribution_tax_rate)

            balance += contrib_net

            curr_salary *= (1 + self.salary_growth)
            curr_personal *= (1 + self.personal_indexation)

        return balance

@dataclass
class LifestyleAsset(Asset):
    depreciation_rate: float = 0.15

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0.0

        time = target_year - self.start_year
        return self.initial_value * ((1 - self.depreciation_rate) ** time)