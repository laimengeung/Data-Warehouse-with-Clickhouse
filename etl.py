import os
from dotenv import load_dotenv
import pandas as pd
import clickhouse_connect

load_dotenv()

# 1. Connect to Clickhouse 
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username=os.getenv("CLICKHOUSE_USERNAME"), 
    password=os.getenv("CLICKHOUSE_PASSWORD")         
)

data_dir = "./data"

# Helper function to map Pandas data types to Clickhouse data types
# Pandas assume our data types (if it sees whole numbers: int, float: float, strings:object...)
# Clickhouse has its own data types (used for creating table columns)
def get_clichouse_type(dtype):
    dtype_str = str(dtype)
    if 'int' in dtype_str:
        return 'Int64'
    elif 'float' in dtype_str:
        return 'Float64'
    else:
        return 'String' # We'll default text and dates to String for simplicity

# 2. Loop through all CSV files
for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):
        # Get table name
        table_name = filename.replace('.csv', '')
        file_path = os.path.join(data_dir, filename)

        print(f"Processing {filename}...")
        df = pd.read_csv(file_path)

        # 3. Build the CREATE TABLE SQL query
        columns = []
        for col_name, dtype in df.dtypes.items():
            ch_type = get_clichouse_type(dtype)

            # Clickhouse columns shouldn't have spaces ro special characters
            safe_col_name = col_name.replace(' ', '_').replace('/', '_').replace('-', '_')
            columns.append(f"`{safe_col_name}` {ch_type}")

            # Update dataframe columns to match our safe column names
            df.rename(columns={col_name: safe_col_name}, inplace=True)
        
        columns_sql = ", ".join(columns)

        # MergeTree is CLickhouse's core engine.
        # ORDER BY tuple() means no specific sorting key.
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql}) ENGINE = MergeTree ORDER BY tuple()"

        client.command(f"DROP TABLE IF EXISTS {table_name}")
        client.command(create_table_sql)

        # 4. Insert the data
        client.insert_df(table_name, df)
        print(f"--> Successfully loaded {len(df)} rows into `{table_name}`\n")
    
print("ETL Process Complete!")