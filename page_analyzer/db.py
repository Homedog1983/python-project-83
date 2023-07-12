def sql_initializate(connection, path: str):
    # with open(path) as sql_file:
    #     i_query = sql_file.read()
    initial_query = """
    DROP TABLE IF EXISTS urls;
    CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255),
    created_at timestamp
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(initial_query)
