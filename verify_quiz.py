import os
from decimal import Decimal
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from quiz_data import QUESTIONS

load_dotenv(Path(__file__).with_name(".env"))


def normalize(value):
    # 统一数据库 Decimal 和题目中的数字格式
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    return value


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
        failures = []

        with conn.cursor() as cur:
            for question in QUESTIONS:
                cur.execute(question["expected_sql"])

                columns = [column.name for column in cur.description]
                actual = [[normalize(value) for value in row] for row in cur.fetchall()]
                expected = [
                    [normalize(value) for value in row]
                    for row in question["expected_rows"]
                ]

                passed = columns == question["expected_columns"] and actual == expected

                status = "PASS" if passed else "FAIL"
                print(f"Q{question['id']}: {status}")

                if not passed:
                    failures.append(question["id"])
                    print("Actual columns:", columns)
                    print("Actual rows:", actual)
                    print("Expected rows:", expected)

        if failures:
            raise SystemExit(f"Verification failed: {failures}")

        print("\nAll 5 questions match the live database.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
