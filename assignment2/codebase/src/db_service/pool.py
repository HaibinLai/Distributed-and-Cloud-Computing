import os
from psycopg2.pool import SimpleConnectionPool
PG_DSN = os.getenv("PG_DSN", "dbname=merch user=merch password=merch host=postgres port=5432")
pool = SimpleConnectionPool(1, 10, dsn=PG_DSN)
def conn():
    c = pool.getconn()
    c.autocommit = False
    return c
def put(c): pool.putconn(c)
