from datetime import date
import os
import psycopg2
from psycopg2.extras import DictCursor


def get_connection():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError('Not found $DATABASE_URL')
    try:
        connection = psycopg2.connect(db_url)
        connection.autocommit = True
        return connection
    except psycopg2.Error:
        print('Can`t establish connection to database')


def import_sql(sql_path: str):
    with open(sql_path) as sql_file:
        query = sql_file.read()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)


def add_url(url: str):
    query_template = """
    INSERT INTO urls (name, created_at) VALUES (%s, %s)
    RETURNING id;"""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_template, (url, date.today().isoformat()))
            return cursor.fetchone()[0]


def get_url_by_attrs(attrs: dict):
    data = attrs.get('data')
    column = attrs.get('column')
    query_template = f"SELECT * FROM urls WHERE {column} = %s;"
    with get_connection() as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_template, (data,))
            return cursor.fetchone()


def get_urls_with_last_check_info():
    query_template = """
    SELECT
    DISTINCT ON (urls.id)
        urls.id AS id,
        urls.name as name,
        url_checks.created_at AS created_at,
        url_checks.status_code AS status_code
    FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
    ORDER BY urls.id DESC, url_checks.id DESC;"""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_template)
            return cursor.fetchall()


def add_url_check(url_id: str, status_code: int, seo_data: dict):
    query_template = """
    INSERT INTO url_checks
    (url_id, status_code, created_at, h1, title, description)
    VALUES (%s, %s, %s, %s, %s, %s);"""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query_template,
                (url_id, status_code, date.today().isoformat(),
                    seo_data['h1'], seo_data['title'], seo_data['description'])
            )


def get_url_checks_by(url_id: str):
    query_template = """
    SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC;"""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_template, (url_id,))
            return cursor.fetchall()
