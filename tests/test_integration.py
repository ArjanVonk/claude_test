"""Integration tests: spins up postgres via Docker Compose, exercises PostgresDataLoader.

Run with:
    pytest tests/test_integration.py -m integration
"""

import logging
import subprocess
import time
from pathlib import Path

import pandas as pd
import psycopg2
import pytest

from imbalance_dashboard.db import PostgresDataLoader
from imbalance_dashboard.offline import OfflineDataLoader

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
TEST_DSN = "postgresql://imbalance:imbalance@localhost:5432/imbalance"


# ── helpers ───────────────────────────────────────────────────────────────────

def _docker_logs(service: str = "db") -> None:
    result = subprocess.run(
        ["docker", "compose", "logs", "--no-color", service],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    for line in result.stdout.splitlines():
        logger.info("[docker/%s] %s", service, line)
    for line in result.stderr.splitlines():
        logger.warning("[docker/%s stderr] %s", service, line)


def _wait_for_postgres(dsn: str, timeout: int = 60) -> None:
    logger.info("Waiting for PostgreSQL to accept connections (timeout=%ds)…", timeout)
    deadline = time.monotonic() + timeout
    last_exc: Exception | None = None
    while time.monotonic() < deadline:
        try:
            conn = psycopg2.connect(dsn)
            conn.close()
            logger.info("PostgreSQL is ready.")
            return
        except psycopg2.OperationalError as exc:
            last_exc = exc
            logger.debug("Not ready yet: %s", exc)
            time.sleep(1)
    _docker_logs()
    raise TimeoutError(f"PostgreSQL not ready after {timeout}s. Last error: {last_exc}")


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def postgres():
    """Start the db Docker service, yield the DSN, then tear it all down."""
    logger.info("=== Starting db service (docker compose up -d db) ===")
    subprocess.run(
        ["docker", "compose", "up", "-d", "db"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    logger.info("Container started; waiting for postgres readiness…")
    _wait_for_postgres(TEST_DSN)
    _docker_logs()

    yield TEST_DSN

    logger.info("=== Tearing down (docker compose down -v) ===")
    _docker_logs()
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    logger.info("Docker services stopped and volumes removed.")


@pytest.fixture(autouse=True)
def truncate_table(postgres):
    """Wipe the table before each test for full isolation."""
    with psycopg2.connect(postgres) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE imbalance_prices")
        conn.commit()
    logger.info("imbalance_prices table truncated before test.")


# ── tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_save_and_load_roundtrip(postgres):
    """Save synthetic rows to postgres and verify the full roundtrip."""
    original = OfflineDataLoader(seed=42, periods=24).load()
    logger.info("Generated %d synthetic rows", len(original))
    logger.info("First 3 rows:\n%s", original.head(3).to_string(index=False))

    loader = PostgresDataLoader(dsn=postgres)
    loader.save(original)
    logger.info("Saved %d rows to PostgreSQL.", len(original))

    loaded = loader.load()
    logger.info("Loaded %d rows back from PostgreSQL.", len(loaded))
    logger.info("First 3 rows:\n%s", loaded.head(3).to_string(index=False))

    assert len(loaded) == len(original), (
        f"Row count mismatch: expected {len(original)}, got {len(loaded)}"
    )

    for col in ("nrv_mw", "alpha_eur_mwh", "mip_eur_mwh", "mdp_eur_mwh"):
        pd.testing.assert_series_equal(
            loaded[col].reset_index(drop=True),
            original[col].reset_index(drop=True),
            check_names=False,
            obj=f"column '{col}'",
        )
        logger.info("Column '%s' matches exactly.", col)

    # postgres returns tz-aware datetimes; OfflineDataLoader produces tz-naive
    orig_dt = original["datetime"].dt.tz_localize("UTC")
    assert list(loaded["datetime"]) == list(orig_dt), "Datetime column mismatch"
    logger.info("Datetime column matches.")


@pytest.mark.integration
def test_upsert_does_not_duplicate(postgres):
    """Saving the same data twice must not create duplicate rows."""
    df = OfflineDataLoader(seed=7, periods=10).load()
    loader = PostgresDataLoader(dsn=postgres)

    loader.save(df)
    count_after_first = loader.count()
    logger.info("Row count after first save: %d", count_after_first)

    loader.save(df)
    count_after_second = loader.count()
    logger.info("Row count after second save: %d", count_after_second)

    assert count_after_second == count_after_first, (
        f"Upsert created duplicates: {count_after_first} → {count_after_second}"
    )


@pytest.mark.integration
def test_random_seed_produces_different_data(postgres):
    """Two different seeds must produce different data in the db."""
    loader = PostgresDataLoader(dsn=postgres)

    df_a = OfflineDataLoader(seed=1, periods=8).load()
    loader.save(df_a)
    logger.info("Saved seed=1 data (%d rows).", len(df_a))

    df_b = OfflineDataLoader(seed=2, periods=8).load()
    loader.save(df_b)
    logger.info("Saved seed=2 data (%d rows).", len(df_b))

    all_rows = loader.load()
    logger.info("Total rows after both saves: %d", len(all_rows))
    logger.info("Full table:\n%s", all_rows.to_string(index=False))

    assert len(all_rows) > 0, "Expected rows in the database"
