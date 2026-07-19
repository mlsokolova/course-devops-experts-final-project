# DuckDB Quack

**Data service:**

```python
import duckdb

conn = duckdb.connect("seed-data/earthquakes.duckdb")
conn.sql("CREATE TABLE earthquakes AS SELECT * FROM 'seed-data/Earthquakes-1990-2023.parquet'")
duckdb.sql("FORCE INSTALL quack FROM core_nightly; LOAD quack")
conn.sql("CALL quack_serve('quack:0.0.0.0:9494', allow_other_hostname => true, disable_ssl => true);")
```

Expected output includes a generated auth token:

```
┌────────────────────┬─────────────────────┬──────────────────────────────────┐
│     listen_uri     │     listen_url      │            auth_token            │
│      varchar       │       varchar       │             varchar              │
├────────────────────┼─────────────────────┼──────────────────────────────────┤
│ quack:0.0.0.0:9494 │ http://0.0.0.0:9494 │ 3DCA7EE39EEF5309959AF0DC07C1FA75 │
└────────────────────┴─────────────────────┴──────────────────────────────────┘
```

Use the token in client queries and in `QUACK__TOKEN` when configuring the app.

**Client:**

```python
import duckdb

conn = duckdb.connect(":memory:")
conn.sql("""
    FROM quack_query(
        'quack:duckdb',
        'SELECT * FROM main.earthquakes LIMIT 1',
        token='3DCA7EE39EEF5309959AF0DC07C1FA75',
        disable_ssl => true
    )
""")
```

Replace `duckdb` with your Quack server hostname and use the token from the `quack_serve` output (or from the Kubernetes Secret in deployed environments).
