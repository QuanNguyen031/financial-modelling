from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Liability(ABC):
    initial_value: float
    start_year: int

    @abstractmethod
    def predict(self, target_year: int) -> float:
        pass

@dataclass
class HomeLoan(Liability):
    interest_rate: float
    term_years: int

    def annual_payment(self) -> float:
        P, r, n = self.initial_value, self.interest_rate, self.term_years
        if n <= 0 or P <= 0:
            return 0.0
        if r == 0:
            return P / n
        
        # PMT = P * r / (1 - (1+r)^-n)
        return (P * r) / (1 - (1 + r) ** -n)

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0
        
        P, r, n = self.initial_value, self.interest_rate, self.term_years
        k = target_year - self.start_year + 1

        if k >= n:
            return 0

        pmt = self.annual_payment()
        if r == 0:
            return max(0, P - pmt * k)

        growth = (1 + r) ** k
        balance = P * growth - pmt * ((growth - 1) / r)
        return max(0, balance)

@dataclass
class OtherLiability(Liability):
    interest_rate: float = 0.0
    annual_repayment: float = 0.0

    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0.0

        years = target_year - self.start_year
        balance = self.initial_value

        for _ in range(years):
            balance *= (1 + self.interest_rate)
            balance -= self.annual_repayment
            if balance <= 0:
                return 0.0

        return balance
