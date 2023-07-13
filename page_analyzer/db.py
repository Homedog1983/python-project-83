from datetime import date
from psycopg2.extras import DictCursor


def sql_load(connection, path: str):
    with open(path) as sql_file:
        query = sql_file.read()
    with connection.cursor() as cursor:
        cursor.execute(query)


def insert(connection, url: str):
    query_template = "INSERT INTO urls (name, created_at) VALUES (%s, %s);"
    with connection.cursor() as cursor:
        cursor.execute(query_template, (url, date.today().isoformat()))


def collect_raw_filtered_by(connection, data: str, column='name'):
    query_template = f"SELECT * FROM urls WHERE {column} = %s;"
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query_template, (data,))
        table_raw = cursor.fetchone()
    return table_raw
