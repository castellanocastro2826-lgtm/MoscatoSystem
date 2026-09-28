import mysql.connector
import os

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "moscato_db")
    )
    with conn.cursor() as cursor:
        cursor.execute("SELECT id_pedido, id_mesa, estado_pedido, pagado, fecha_cierre FROM pedidos WHERE estado_pedido != 'Cancelado' AND pagado = 0")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
except Exception as e:
    print(e)
