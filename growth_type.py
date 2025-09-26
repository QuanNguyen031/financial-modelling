from enum import Enum

class GrowthType(str, Enum):
    APPRECIATING = "Appreciating"
    DEPRECIATING = "Depreciating"
    FLAT = "Flat"
    AMORTISING = "Amortising"
