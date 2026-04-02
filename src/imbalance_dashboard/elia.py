import pandas as pd

from imbalance_dashboard.base import DataLoader


class EliaDataLoader(DataLoader):
    """Loads imbalance prices from the Elia open data API.

    API: https://opendata.elia.be/api/explore/v2.1/catalog/datasets/elia-grid-imbalance/records
    """

    BASE_URL = "https://opendata.elia.be/api/explore/v2.1/catalog/datasets"
    DATASET = "elia-grid-imbalance"

    def __init__(self, lookback_hours: int = 24):
        self.lookback_hours = lookback_hours

    def load(self) -> pd.DataFrame:
        raise NotImplementedError("Elia data loading not yet implemented")
