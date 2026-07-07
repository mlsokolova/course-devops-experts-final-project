from flask import Flask
import os
import duckdb

DUCKDB__PATH = os.getenv("DUCKDB__PATH")
QUACK__TOKEN = os.getenv("QUACK__TOKEN")
QUACK__PORT = os.getenv("QUACK__PORT")

conn = duckdb.connect(DUCKDB__PATH, read_only=True)  
conn.sql("load spatial;")
conn.sql(f"CALL quack_serve('quack:0.0.0.0:{QUACK__PORT}',  token='{QUACK__TOKEN}', allow_other_hostname => true, disable_ssl=true);")  


app = Flask(__name__)    


def get_duckdb_tables():
    tables = conn.sql("SHOW TABLES").fetchall()
    return [table[0] for table in tables]

@app.route('/')
def index():
    return f"""DuckDB Quack Service is running on port {QUACK__PORT}!
               Available tables:
               {', '.join(get_duckdb_tables())}
            """

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
