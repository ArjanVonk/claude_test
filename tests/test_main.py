from imbalance_dashboard.offline import OfflineDataLoader


def test_offline_loader_columns():
    df = OfflineDataLoader().load()
    assert list(df.columns) == ["datetime", "nrv_mw", "alpha_eur_mwh", "mip_eur_mwh", "mdp_eur_mwh"]


def test_offline_loader_row_count():
    df = OfflineDataLoader(periods=96).load()
    assert len(df) == 96


def test_offline_loader_deterministic():
    df1 = OfflineDataLoader(seed=1).load()
    df2 = OfflineDataLoader(seed=1).load()
    assert df1.equals(df2)
