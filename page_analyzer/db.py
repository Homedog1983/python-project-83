from datetime import date
import psycopg2
from psycopg2.extras import DictCursor


def make_connection(DB_URL: str):
    try:
        connection = psycopg2.connect(DB_URL)
        connection.autocommit = True
        return connection
    except psycopg2.Error:
        print('Can`t establish connection to database')


def import_sql(DB_URL: str, sql_path: str):
    with open(sql_path) as sql_file:
        query = sql_file.read()
    connection = make_connection(DB_URL)
    with connection.cursor() as cursor:
        cursor.execute(query)
    connection.close()


def insert(DB_URL: str, url: str):
    connection = make_connection(DB_URL)
    query_template = "INSERT INTO urls (name, created_at) VALUES (%s, %s);"
    with connection.cursor() as cursor:
        cursor.execute(query_template, (url, date.today().isoformat()))
    connection.close()


def collect_raw_filtered_by(DB_URL: str, data: str, column='name'):
    connection = make_connection(DB_URL)
    query_template = f"SELECT * FROM urls WHERE {column} = %s;"
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query_template, (data,))
        table_raw = cursor.fetchone()
    connection.close()
    return table_raw


def collect_all_raws_desc(DB_URL: str):
    connection = make_connection(DB_URL)
    query_template = "SELECT * FROM urls ORDER BY created_at DESC;"
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query_template)
        table_raws = cursor.fetchall()
    connection.close()
    return table_raws
