#  Copyright (c) 2025 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


# -----------------------------------------------------------------------------
# System Imports
# -----------------------------------------------------------------------------

import os
from functools import cache

# -----------------------------------------------------------------------------
# Public Imports
# -----------------------------------------------------------------------------

from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------------------
# Private Imports
# -----------------------------------------------------------------------------

from .db_tables import TableBase


@cache
def db_url(db_name: str) -> str:
    pg_user = os.environ["PG_USER"]
    pg_passwd = os.environ["PG_PASSWORD"]
    pg_host = os.environ["PG_HOST"]
    return f"postgresql://{pg_user}:{pg_passwd}@{pg_host}/{db_name}"


def db_init(db_name: str):
    eng = create_engine(db_url("postgres"), isolation_level="AUTOCOMMIT")

    with eng.connect() as conn:
        res = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        )

        if res.fetchone() is None:
            conn.execute(text(f"CREATE DATABASE {db_name}"))

    eng = create_engine(db_url(db_name))
    TableBase.metadata.create_all(eng)


def db_connect(db_name: str):
    return sessionmaker(bind=create_engine(db_url(db_name)))()


def db_delete(db_name: str):
    eng = create_engine(db_url("postgres"), isolation_level="AUTOCOMMIT")

    with eng.connect() as conn:
        conn.execute(text(f"DROP DATABASE {db_name}"))


def db_erase(db_name: str):
    """Erase all records in the database"""

    engine = create_engine(db_url(db_name))
    session = sessionmaker(bind=engine)()

    # Get the metadata of all tables in the database
    metadata = MetaData()

    # Reflect all the tables from the database
    metadata.reflect(bind=engine)

    # Loop over all the tables and delete all records
    for table in metadata.tables.values():
        session.execute(table.delete())

    session.commit()
    session.close()
