from abc import ABC, abstractmethod

import pandas as pd


class DataLoader(ABC):
    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Return a DataFrame with columns:
        - datetime (UTC, 15-min quarters)
        - nrv_mw: Net Regulation Volume (MW)
        - alpha_eur_mwh: Alpha price (€/MWh)
        - mip_eur_mwh: Marginal Incremental Price (€/MWh)
        - mdp_eur_mwh: Marginal Decremental Price (€/MWh)
        """
