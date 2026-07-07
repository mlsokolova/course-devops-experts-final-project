import duckdb
import os

class QuakeStats:
    QUACK__TOKEN = os.environ.get("QUACK__TOKEN")
    QUACK__HOST = os.environ.get("QUACK__HOST")
    QUACK__PORT = os.environ.get("QUACK__PORT")
    

    def __init__(self,
                 latitude,
                 longitude,
                 radius,):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.conn = duckdb.connect(database=':memory:')
        #self.conn.execute("install spatial; load spatial;")
        #self.conn.execute("attach 'quack:duckdb:9494' as remote_db (token 'my-secret-token', disable_ssl true);")
        self.quack_uri = f"quack:{self.QUACK__HOST}:{self.QUACK__PORT}"
        self.stats = self.get_stats_over_area()
        self.max_earthquake = self.get_max_earthquake_in_area()

    def run_query(self, query):
        sql = f"""from quack_query('{self.quack_uri}', 
                                    '{query}', 
                                     token='{self.QUACK__TOKEN}',
                                     disable_ssl=>true)
        """
        result = self.conn.execute(sql)
        return result
    
    def jsonify_query_result(self, query_result):
        return query_result.df().to_json(orient="records")
    
    def get_stats_over_area(self):
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
        res = self.jsonify_query_result(query_result=query_res)
        return res

    def get_max_earthquake_in_area(self):
        sql = f"""
with filtered_points as
(
select *
from earthquakes
WHERE ST_Distance_Spheroid( 
    ST_Point(latitude, longitude), 
    ST_Point({self.latitude}, {self.longitude})
) <= {self.radius*1000}
)
select epoch_ms(time)::VARCHAR as "When",
       place as "Where",
       magnitudo as "Magnitude"
from filtered_points
order by magnitudo desc
limit 1
"""
        query_res = self.run_query(sql)
        res = self.jsonify_query_result(query_result=query_res)
        return res