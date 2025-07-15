import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy import create_engine


from pytest_postgresql.factories import postgresql_proc as _orig_proc


postgresql_proc = _orig_proc(
        exec=r"C:\Progra~1\PostgreSQL\17\bin\pg_ctl.exe",
        pg_config=r"C:\Progra~1\PostgreSQL\17\bin\pg_config.exe",
        initdb_args="-A trust -E UTF8",
        port=5432,
        startparams="-F",
        postgres_options=[
            "-c", "log_destination=stderr",
            "-c", "logging_collector=off",
        ],
    )


@pytest.fixture(autouse=True, scope="module")
def test_db(postgresql_proc):
    dsn = postgresql_proc().dsn()

    # temporarily swaps actual server route with ephemeral testing one, refreshed per {scope}
    mp = MonkeyPatch()
    mp.setenv("DB_URL", dsn)

    # test_db = Database(create_engine(dsn))
    # yield test_db