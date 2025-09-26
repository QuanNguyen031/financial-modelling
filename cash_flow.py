from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Income:
    name: str
    amount: float
    annual_rate: float
    start_year: int
    end_year: Optional[int] = None

    def is_active(self, year: int) -> bool:
        if year < self.start_year:
            return False
        if self.end_year is not None and year > self.end_year:
            return False
        return True

    def predict(self, target_year: int) -> float:
        if not self.is_active(target_year):
            return 0.0
        
        time = target_year - self.start_year
        return self.amount * ((1 + self.annual_rate) ** time)


@dataclass
class Expense:
    name: str
    amount: float
    start_year: int
    annual_rate: float = 0.02
    end_year: Optional[int] = None

    def is_active(self, year: int) -> bool:
        if year < self.start_year:
            return False
        if self.end_year is not None and year > self.end_year:
            return False
        return True

    def predict(self, target_year: int) -> float:
        if not self.is_active(target_year):
            return 0.0
        
        time = target_year - self.start_year
        return self.amount * ((1 + self.annual_rate) ** time)


@dataclass
class CashFlow:
    incomes: List[Income] = field(default_factory=list)
    expenses: List[Expense] = field(default_factory=list)

    def inflow(self, target_year: int) -> float:
        return sum(income.predict(target_year) for income in self.incomes)

    def outflow(self, target_year: int) -> float:
        return sum(expense.predict(target_year) for expense in self.expenses)

    def project(self, start_year: int, end_year: int) -> List[Dict[str, float]]:
        projection = []
        for year in range(start_year, end_year + 1):
            inflow = self.inflow(year)
            outflow = self.outflow(year)
            netflow = inflow - outflow

            projection.append({
                "year": year,
                "inflow": inflow,
                "outflow": outflow,
                "net_flow": netflow
            })
        return projection
