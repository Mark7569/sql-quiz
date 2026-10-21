import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

def main():
    conn = psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        sslmode="require",
        connect_timeout=15,
    )

    try:
        conn.set_session(readonly=True)

        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, cuisine, rating, avg_cost
                FROM public.restaurants
                ORDER BY id;
            """)
            rows = cur.fetchall()

            for row in rows:
                print(row)

            print(f"\nConnection successful! Found {len(rows)} restaurants.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()