"""DuckDB/Quack client for earthquake statistics queries."""
import json
import os

import duckdb


class QuakeStats:
    """Query historical earthquake statistics from the DuckDB Quack service."""

    QUACK__TOKEN = os.environ.get("QUACK__TOKEN")
    QUACK__HOST = os.environ.get("QUACK__HOST")
    QUACK__PORT = os.environ.get("QUACK__PORT")

    def __init__(self, latitude, longitude, radius):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.conn = duckdb.connect(database=':memory:')
        self.quack_uri = f"quack:{self.QUACK__HOST}:{self.QUACK__PORT}"
        self.all_stats = self.get_all_stats()

    def run_query(self, query):
        """Execute a SQL query against the remote Quack database."""
        sql = f"""from quack_query('{self.quack_uri}',
                                    '{query}',
                                     token='{self.QUACK__TOKEN}',
                                     disable_ssl=>true)
        """
        result = self.conn.execute(sql)
        return result

    def jsonify_query_result(self, query_result):
        """Convert a DuckDB query result to JSON records."""
        return query_result.df().to_json(orient="records")

    def get_stats_over_area(self):
        """Return median magnitude and average time between earthquakes."""
        sql = f"""
with filtered_points as
(
select *
from earthquakes
WHERE ST_Distance_Spheroid(
    ST_Point(latitude, longitude),
    ST_Point({self.latitude}, {self.longitude})
) <= {self.radius * 1000}
)
, df_time_lag_ms as
(
select *
      , time - LAG(time, 1) OVER (ORDER BY time) AS time_lag_ms
from filtered_points
)
, df_time_lag as
(
select *,
       to_milliseconds(time_lag_ms) time_lag
from df_time_lag_ms
)
select median(magnitudo) as median_magnitude,
       to_seconds(round(epoch(avg(time_lag))))::VARCHAR as average_time_between_earthquakes
from df_time_lag
"""
        query_res = self.run_query(sql)
        return self.jsonify_query_result(query_result=query_res)

    def get_max_earthquake_in_area(self):
        """Return the strongest earthquake in the configured area."""
        sql = f"""
with filtered_points as
(
select *
from earthquakes
WHERE ST_Distance_Spheroid(
    ST_Point(latitude, longitude),
    ST_Point({self.latitude}, {self.longitude})
) <= {self.radius * 1000}
)
select epoch_ms(time)::VARCHAR as "When",
       place as "Where",
       magnitudo as "Magnitude"
from filtered_points
order by magnitudo desc
limit 1
"""
        query_res = self.run_query(sql)
        return self.jsonify_query_result(query_result=query_res)

    def get_average_quakes_per_day(self):
        """Return the average number of earthquakes per day in the configured area."""
        sql = f"""
with filtered_points as
(
select *
from earthquakes
WHERE ST_Distance_Spheroid(
    ST_Point(latitude, longitude),
    ST_Point({self.latitude}, {self.longitude})
) <= {self.radius * 1000}
)
, daily_counts as
(
select CAST(epoch_ms(time) AS DATE) as quake_day,
       count(*) as quake_count
from filtered_points
group by 1
)
select avg(quake_count) as average_quakes_per_day
from daily_counts
"""
        query_res = self.run_query(sql)
        return self.jsonify_query_result(query_result=query_res)

    def get_day_with_max_earthquakes(self):
        """Return the day with the most earthquakes in the configured area."""
        sql = f"""
with filtered_points as
(
select *
from earthquakes
WHERE ST_Distance_Spheroid(
    ST_Point(latitude, longitude),
    ST_Point({self.latitude}, {self.longitude})
) <= {self.radius * 1000}
)
, daily_counts as
(
select CAST(epoch_ms(time) AS DATE) as quake_day,
       count(*) as quake_count
from filtered_points
group by 1
)
select quake_day::VARCHAR as "Day",
       quake_count as "Earthquakes"
from daily_counts
order by quake_count desc
limit 1
"""
        query_res = self.run_query(sql)
        return self.jsonify_query_result(query_result=query_res)


    def get_observation_date_range(self):
        """Return the date range of the observations"""
        sql = f"""
        select cast(cast(min(epoch_ms(time)) as date) as varchar) as min_date, 
               cast(cast(max(epoch_ms(time)) as date) as varchar) as max_date
        from earthquakes
        """
        query_res = self.run_query(sql)
        return self.jsonify_query_result(query_result=query_res)

    def get_all_stats(self):
        """Combine all area statistics into a single JSON object."""
        return json.dumps({
            "stats": json.loads(self.get_stats_over_area()),
            "max_earthquake": json.loads(self.get_max_earthquake_in_area()),
            "avg_per_day": json.loads(self.get_average_quakes_per_day()),
            "day_with_max_earthquakes": json.loads(self.get_day_with_max_earthquakes()),
            "observation_date_range": json.loads(self.get_observation_date_range()),
        })
