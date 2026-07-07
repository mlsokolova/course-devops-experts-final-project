import duckdb
import os
import requests

DUCKDB__PATH = os.environ.get("DUCKDB__PATH")
seed_data_source_url = "https://github.com/mlsokolova/course-devops-experts/raw/refs/heads/main/final-project/seed-data/Earthquakes-1990-2023.parquet"
local_filename = "/tmp/Earthquakes-1990-2023.parquet"

def download_large_github_file(url, local_filename):
    # stream=True keeps memory usage low by loading data in pieces
    with requests.get(url, stream=True) as response:
        # Raise an exception for bad status codes (404, 500, etc.)
        response.raise_for_status() 
        # Open local file in write-binary mode
        with open(local_filename, 'wb') as file:
            # Iterate over 1MB chunks of data
            for chunk in response.iter_content(chunk_size=1024 * 1024): 
                if chunk: # Filter out keep-alive new chunks
                    file.write(chunk)
                    
    print(f"Download complete: {local_filename}")

if __name__ == "__main__":    
    conn = duckdb.connect(DUCKDB__PATH)
    try:
        conn.sql("select * from earthquakes limit 1")
        print("Table 'earthquakes' already exists. No need to download the seed data.")
    except Exception as e:
        download_large_github_file(seed_data_source_url, local_filename)
        conn.sql("CREATE TABLE earthquakes AS SELECT * FROM read_parquet('/tmp/Earthquakes-1990-2023.parquet')")