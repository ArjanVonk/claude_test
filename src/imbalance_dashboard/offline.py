from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from imbalance_dashboard.base import DataLoader


class OfflineDataLoader(DataLoader):
    """Generates synthetic 15-min imbalance price data for local development."""

    def __init__(self, periods: int = 96, seed: int = 42):
        self.periods = periods
        self.seed = seed

    def load(self) -> pd.DataFrame:
        now = datetime.utcnow().replace(second=0, microsecond=0)
        now -= timedelta(minutes=now.minute % 15)

        timestamps = [
            now - timedelta(minutes=15 * i)
            for i in range(self.periods - 1, -1, -1)
        ]

        rng = np.random.default_rng(self.seed)
        nrv = rng.normal(0, 150, self.periods)
        alpha = 80 + rng.uniform(-10, 10, self.periods)
        mip = alpha + rng.normal(0, 5, self.periods)
        mdp = alpha - rng.normal(0, 5, self.periods)

        return pd.DataFrame({
            "datetime": timestamps,
            "nrv_mw": nrv.round(1),
            "alpha_eur_mwh": alpha.round(2),
            "mip_eur_mwh": mip.round(2),
            "mdp_eur_mwh": mdp.round(2),
        })
