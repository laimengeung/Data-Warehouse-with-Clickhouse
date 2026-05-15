import os
from dotenv import load_dotenv
import clickhouse_connect
import pandas as pd

load_dotenv()

# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username=os.getenv("CLICKHOUSE_USERNAME"),
    password=os.getenv("CLICKHOUSE_PASSWORD")
)

# This is our analytical SQL query
sql = """
    SELECT 
        Channel, 
        sum(Revenue) as Total_Revenue 
    FROM 
        sales_by_channel 
    GROUP BY 
        Channel 
    ORDER BY 
        Total_Revenue DESC
"""

print("Executing analytical query...\n")

# Clickhouse-connect can return the query result directly as a Pandas DataFrame!
result_df = client.query_df(sql)

print(result_df)
