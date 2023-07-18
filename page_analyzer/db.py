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


def insert_to_urls(DB_URL: str, url: str):
    connection = make_connection(DB_URL)
    query_template = """
    INSERT INTO urls (name, created_at) VALUES (%s, %s);"""
    with connection.cursor() as cursor:
        cursor.execute(query_template, (url, date.today().isoformat()))
    connection.close()


def select_url_where(DB_URL: str, data: str, column='name'):
    connection = make_connection(DB_URL)
    query_template = f"SELECT * FROM urls WHERE {column} = %s;"
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query_template, (data,))
        urls_raw = cursor.fetchone()
    connection.close()
    return urls_raw


def select_join_desc(DB_URL: str):
    connection = make_connection(DB_URL)
    query_template = """
    SELECT urls.id AS id,
      urls.name AS name,
      url_checks.created_at AS created_at,
      url_checks.status_code AS status_code
    FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
    ORDER BY urls.id DESC;"""
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query_template)
        raws = cursor.fetchall()
    connection.close()
    return raws


def insert_to_url_checks(DB_URL: str, url_id: str, status_code: int):
    connection = make_connection(DB_URL)
    query_template = """
    INSERT INTO url_checks
    (url_id, status_code, created_at)
    VALUES (%s, %s, %s);"""
    with connection.cursor() as cursor:
        cursor.execute(
            query_template,
            (url_id, status_code, date.today().isoformat())
        )
    connection.close()


def select_url_checks_desc(DB_URL: str, url_id: str):
    connection = make_connection(DB_URL)
    query_template = """
    SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC;"""
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query_template, (url_id,))
        raws = cursor.fetchall()
    connection.close()
    return raws
