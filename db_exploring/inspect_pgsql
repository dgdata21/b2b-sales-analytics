import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

start_time = datetime.now()

# ==================================================
# LOAD CREDENTIALS
# ==================================================
load_dotenv(r"/path/to/.creds")

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

if not all([host, port, database, user, password]):
    raise ValueError("Can't load PostgreSQL connection credentials")

port = int(port)

# ==================================================
# POSTGRESQL CONNECTION
# ==================================================

url = f"postgresql+psycopg://{user}:{password}" f"@{host}:{port}/{database}"

engine = create_engine(url)

# ==================================================
# EXPLORE DATABASE
# ==================================================

inspect_postgresql = """
SELECT
    table_schema AS schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema NOT IN (
    'information_schema',
    'pg_catalog'
)
ORDER BY table_schema, table_name
"""

print("\n", "EXPLORING POSTGRESQL DATABASE".center(100, "*"), "\n")

with engine.connect() as conn:
    tables = pd.read_sql(text(inspect_postgresql), conn)

print(tables.to_string(index=False))


# ==================================================
# TABLE PREVIEW
# ==================================================
def table_view(table_name, schema="public", limit=5):

    query = f"""
    SELECT *
    FROM {schema}.{table_name}
    LIMIT {limit}
    """

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    print("\n", f" {schema}.{table_name} ".center(80, "="))

    if df.empty:
        print("\nEmpty table")
    else:
        print("\n", df.to_string(index=False))

    print()
    df.info()


# ==================================================
# TABLE INSPECTION
# ==================================================
table_view("air_efficiency")
table_view("air_partners")

# ==================================================
# EXECUTION TIME
# ==================================================

end_time = datetime.now()

print(f"\nScript time: {end_time - start_time}")
print()

engine.dispose()
