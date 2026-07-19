"""Download and seed the DuckDB earthquakes table from parquet data."""

import os

import duckdb
import requests

DUCKDB__PATH = os.environ.get("DUCKDB__PATH")
SEED_DATA_SOURCE_URL = (
    "https://github.com/mlsokolova/course-devops-experts/raw/refs/heads/main/"
    "final-project/seed-data/Earthquakes-1990-2023.parquet"
)
LOCAL_FILENAME = "/tmp/Earthquakes-1990-2023.parquet"
REQUEST_TIMEOUT = 60


def download_large_github_file(url, dest_path):
    """Stream-download a large file from GitHub to the local filesystem."""
    with requests.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
        response.raise_for_status()
        with open(dest_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

    print(f"Download complete: {dest_path}")


if __name__ == "__main__":

    try:
        conn_ro = duckdb.connect(DUCKDB__PATH, read_only=True)
        conn_ro.sql("select * from earthquakes limit 1")
        print("Table 'earthquakes' already exists. No need to download the seed data.")
        conn_ro.close()
    except duckdb.Error:
        download_large_github_file(SEED_DATA_SOURCE_URL, LOCAL_FILENAME)
        conn = duckdb.connect(DUCKDB__PATH)
        conn.sql(
            "CREATE TABLE earthquakes AS SELECT * "
            f"FROM read_parquet('{LOCAL_FILENAME}')"
        )
        conn.close()
