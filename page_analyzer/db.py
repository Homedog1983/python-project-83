from datetime import date
import psycopg2
from psycopg2.extras import DictCursor


def get_connection(DB_URL: str):
    try:
        connection = psycopg2.connect(DB_URL)
        connection.autocommit = True
        return connection
    except psycopg2.Error:
        print('Can`t establish connection to database')


def import_sql(DB_URL: str, sql_path: str):
    with open(sql_path) as sql_file:
        query = sql_file.read()
    with get_connection(DB_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)


def add_url(DB_URL: str, url: str):
    query_template = """
    INSERT INTO urls (name, created_at) VALUES (%s, %s)
    RETURNING id;"""
    with get_connection(DB_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query_template, (url, date.today().isoformat()))
            id = cursor.fetchone()[0]
    return id


def get_url_data_by(DB_URL: str, data: str, column: str):
    query_template = f"SELECT * FROM urls WHERE {column} = %s;"
    with get_connection(DB_URL) as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_template, (data,))
            url_data = cursor.fetchone()
    return url_data


def get_urls_data(DB_URL: str):
    query_template = """
    SELECT
    DISTINCT ON (urls.id)
        urls.id AS id,
        urls.name as name,
        url_checks.created_at AS created_at,
        url_checks.status_code AS status_code
    FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
    ORDER BY urls.id DESC, url_checks.id DESC;"""
    with get_connection(DB_URL) as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_template)
            urls_data = cursor.fetchall()
    return urls_data


def add_url_check(
        DB_URL: str, url_id: str, status_code: int, seo_data: dict):
    query_template = """
    INSERT INTO url_checks
    (url_id, status_code, created_at, h1, title, description)
    VALUES (%s, %s, %s, %s, %s, %s);"""
    with get_connection(DB_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query_template,
                (url_id, status_code, date.today().isoformat(),
                    seo_data['h1'], seo_data['title'], seo_data['description'])
            )


def get_url_checks_by(DB_URL: str, url_id: str):
    query_template = """
    SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC;"""
    with get_connection(DB_URL) as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_template, (url_id,))
            checks = cursor.fetchall()
    return checks
