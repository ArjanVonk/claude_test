import os

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

from imbalance_dashboard.base import DataLoader


class PostgresDataLoader(DataLoader):
    """Load imbalance prices from PostgreSQL and optionally persist new data."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.environ["DATABASE_URL"]

    def load(self) -> pd.DataFrame:
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT datetime, nrv_mw, alpha_eur_mwh, mip_eur_mwh, mdp_eur_mwh"
                    " FROM imbalance_prices ORDER BY datetime"
                )
                rows = cur.fetchall()
        df = pd.DataFrame(rows)
        if not df.empty:
            df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        return df

    def count(self) -> int:
        """Return the number of rows in imbalance_prices without fetching all data."""
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM imbalance_prices")
                return cur.fetchone()[0]

    def save(self, df: pd.DataFrame) -> None:
        """Upsert a DataFrame of imbalance prices into the database."""
        rows = list(
            df[["datetime", "nrv_mw", "alpha_eur_mwh", "mip_eur_mwh", "mdp_eur_mwh"]]
            .itertuples(index=False, name=None)
        )
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO imbalance_prices
                        (datetime, nrv_mw, alpha_eur_mwh, mip_eur_mwh, mdp_eur_mwh)
                    VALUES %s
                    ON CONFLICT (datetime) DO UPDATE SET
                        nrv_mw        = EXCLUDED.nrv_mw,
                        alpha_eur_mwh = EXCLUDED.alpha_eur_mwh,
                        mip_eur_mwh   = EXCLUDED.mip_eur_mwh,
                        mdp_eur_mwh   = EXCLUDED.mdp_eur_mwh
                    """,
                    rows,
                )
            conn.commit()
