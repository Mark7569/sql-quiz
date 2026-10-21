import json
import os

import psycopg2
from pglast.parser import parse_sql_json

from auth import require_user

ALLOWED_NODES = {
    "SelectStmt",
    "ResTarget",
    "ColumnRef",
    "A_Star",
    "RangeVar",
    "Alias",
    "A_Const",
    "Integer",
    "Float",
    "String",
    "Boolean",
    "A_Expr",
    "BoolExpr",
    "NullTest",
    "SortBy",
    "FuncCall",
    "SubLink",
    "RangeSubselect",
    "JoinExpr",
}

ALLOWED_FUNCTIONS = {"count", "avg", "sum", "min", "max", "round"}

ALLOWED_OPERATORS = {
    "=",
    "<>",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "+",
    "-",
    "*",
    "/",
    "%",
}


def validate_query(sql_text):
    if not sql_text.strip():
        raise ValueError("Enter a SQL query first.")

    if len(sql_text) > 10000:
        raise ValueError("The query is too long.")

    try:
        statements = json.loads(parse_sql_json(sql_text))["stmts"]
    except Exception:
        raise ValueError("Invalid SQL syntax. Check your query.") from None

    if len(statements) != 1:
        raise ValueError("Run exactly one SELECT statement at a time.")

    statement = statements[0]["stmt"]
    if set(statement) != {"SelectStmt"}:
        raise ValueError("Only SELECT queries are allowed.")

    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
            return

        if not isinstance(value, dict):
            return

        for key, content in value.items():
            if key and key[0].isupper() and key not in ALLOWED_NODES:
                raise ValueError(
                    f"This SQL feature is not supported in this quiz: {key}"
                )

            if key == "SelectStmt":
                if content.get("intoClause") or content.get("lockingClause"):
                    raise ValueError("SELECT INTO and row locking are not allowed.")

            if key == "RangeVar":
                if (
                    content.get("relname") != "restaurants"
                    or content.get("schemaname") not in (None, "public")
                    or content.get("catalogname")
                ):
                    raise ValueError("You may query only public.restaurants.")

            if key == "FuncCall":
                names = [item["String"]["sval"] for item in content["funcname"]]
                if not (
                    (len(names) == 1 and names[0] in ALLOWED_FUNCTIONS)
                    or (
                        len(names) == 2
                        and names[0] == "pg_catalog"
                        and names[1] in ALLOWED_FUNCTIONS
                    )
                ):
                    raise ValueError(
                        "Allowed functions: COUNT, AVG, SUM, MIN, MAX, ROUND."
                    )

            if key == "A_Expr":
                names = [item["String"]["sval"] for item in content.get("name", [])]
                if len(names) != 1 or names[0] not in ALLOWED_OPERATORS:
                    raise ValueError("This operator is not supported in the quiz.")

            walk(content)

    walk(statement)


def run_query(sql_text, access_token):
    # Authentication is enforced here, not just by hiding the button.
    require_user(access_token)
    validate_query(sql_text)

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
            cur.execute("SET LOCAL ROLE quiz_reader")
            cur.execute("SET LOCAL search_path TO pg_catalog, public")
            cur.execute("SET LOCAL statement_timeout = '3s'")
            cur.execute("SET LOCAL lock_timeout = '1s'")

        # A server-side cursor avoids downloading an unlimited result set.
        with conn.cursor(name="quiz_result") as cur:
            cur.execute(sql_text)
            rows = cur.fetchmany(201)
            columns = [column.name for column in cur.description]

        return columns, rows[:200], len(rows) > 200

    except psycopg2.Error as exc:
        message = exc.diag.message_primary or "Database query failed."
        raise ValueError(message) from None

    finally:
        try:
            conn.rollback()
        finally:
            conn.close()
