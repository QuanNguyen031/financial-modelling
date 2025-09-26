from typing import List, Dict
from dataclasses import dataclass, field
from asset import Asset
from growth_type import GrowthType

@dataclass
class Liability:
    name: str
    initial_balance: float
    growth_type: GrowthType
    annual_rate: float
    term_years: int
    start_year: int = 2025

    def annual_payment(self) -> float:
        if self.growth_type != GrowthType.AMORTISING:
            return 0

        P, r, n = self.initial_balance, self.annual_rate, self.term_years
        if n <= 0 or P <= 0:
            return 0.0
        if r == 0:
            return P / n
        
        # PMT = P * r / (1 - (1+r)^-n)
        return (P * r) / (1 - (1 + r) ** -n)
    
    def predict(self, target_year: int) -> float:
        if target_year < self.start_year:
            return 0
        
        P, r, n = self.initial_balance, self.annual_rate, self.term_years
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
class BalanceSheet:
    assets: List[Asset] = field(default_factory=list)
    liabilities: List[Liability] = field(default_factory=list)

    def total_assets(self, target_year) -> float:
        return sum(asset.predict(target_year) for asset in self.assets)

    def total_liabilities(self, target_year) -> float:
        return sum(liability.predict(target_year) for liability in self.liabilities)

    def net_worth(self, target_year) -> float:
        return self.total_assets(target_year) - self.total_liabilities(target_year)
    
    def project(self, start_year: int, end_year: int) -> List[Dict[str, float]]:
        projection = []
        for year in range(start_year, end_year + 1):
            projection.append({
                "year": year,
                "total_assets": self.total_assets(year),
                "total_liabilities": self.total_liabilities(year),
                "net_worth": self.net_worth(year),
            })
            
        return projection
