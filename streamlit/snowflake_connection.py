import snowflake.connector
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / 'snowflake.env')

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE", "SPOTIFY"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "GOLD"),
    )

if __name__ == "__main__":
    conn = get_connection()
    print("Connection established:", conn is not None)
    conn.close()