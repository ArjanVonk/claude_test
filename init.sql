CREATE TABLE IF NOT EXISTS imbalance_prices (
    datetime        TIMESTAMPTZ     PRIMARY KEY,
    nrv_mw          DOUBLE PRECISION,
    alpha_eur_mwh   DOUBLE PRECISION,
    mip_eur_mwh     DOUBLE PRECISION,
    mdp_eur_mwh     DOUBLE PRECISION
);
