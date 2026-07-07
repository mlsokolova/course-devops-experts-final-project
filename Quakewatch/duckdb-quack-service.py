# pylint: disable=invalid-name
"""DuckDB Quack service entrypoint for serving earthquake data."""
import os

import duckdb
from flask import Flask

DUCKDB__PATH = os.getenv("DUCKDB__PATH")
QUACK__TOKEN = os.getenv("QUACK__TOKEN")
QUACK__PORT = os.getenv("QUACK__PORT")

conn = duckdb.connect(DUCKDB__PATH, read_only=True)
conn.sql("load spatial;")
conn.sql(
    f"CALL quack_serve('quack:0.0.0.0:{QUACK__PORT}', "
    f"token='{QUACK__TOKEN}', allow_other_hostname => true, disable_ssl=true);"
)

app = Flask(__name__)


def get_duckdb_tables():
    """Return the list of table names in the connected DuckDB database."""
    tables = conn.sql("SHOW TABLES").fetchall()
    return [table[0] for table in tables]


@app.route('/')
def index():
    """Return a simple status page listing available DuckDB tables."""
    return f"""DuckDB Quack Service is running on port {QUACK__PORT}!
               Available tables:
               {', '.join(get_duckdb_tables())}
            """


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
