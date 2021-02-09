
from psycopg2 import connect

# declare connection instance
conn = connect(
    dbname = "bbdb",
    host = "172.17.0.2:5432",
    user = "postgres",
    password = "Pass2021!"
)

# declare connection instance
#conn = connect('dbname = "bbdb", host = "172.17.0.2", user = "postgres", password = "Pass2021!"')


cursor = conn.cursor()
cursor.execute("\list")

