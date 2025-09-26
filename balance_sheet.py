from typing import List, Dict
from dataclasses import dataclass, field
from asset import Asset
from liability import Liability

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
