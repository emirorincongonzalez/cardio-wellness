import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='cardio_wellness',
    user='postgres',
    password='postgres'
)

tablas = [
    'clientes',
    'sesiones_entrenamiento',
    'asignaciones_rutina',
    'progreso_mensual',
    'rutinas',
    'ejercicios',
    'rutina_ejercicios',
    'usuarios',
]

for tabla in tablas:
    print(f'\n{tabla.upper()}:')
    print('-' * 60)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{tabla}'
        ORDER BY ordinal_position
    """)
    for col in cur.fetchall():
        print(f'  {col[0]:40} ({col[1]})')
    cur.close()

conn.close()