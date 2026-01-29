import psycopg
from psycopg.rows import dict_row
import os



def get_connection():
    return psycopg.connect(
        os.environ["SUPABASE_DB_URL"],
        row_factory=dict_row,
    )

if __name__ == "__main__":
    

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select 1;")
                row = cur.fetchone()
                

      

    except Exception as e:
        
        raise
