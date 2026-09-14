import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='cardio_wellness',
    user='postgres',
    password='postgres'
)

cur = conn.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")

print('TABLAS EXISTENTES:')
for tabla in cur.fetchall():
    print(f'  - {tabla[0]}')

conn.close()