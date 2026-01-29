import psycopg2 as psy
from psycopg2.extensions import connection as Connection, cursor as Cursor
from psycopg2.pool import SimpleConnectionPool
from config import DATABASE_URL

connection_pool = SimpleConnectionPool(
    1,
    10,
    dsn = DATABASE_URL
)

def get_connection() -> Connection:
    return connection_pool.getconn()

def release_connection(connection : Connection):
    connection_pool.putconn(connection)