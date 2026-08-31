import os
try:
    import mysql.connector
    from mysql.connector import Error
except Exception:
    mysql = None
    Error = Exception

class AnalisisModel:
    def __init__(self, db_config=None):
        self._db_config = db_config or {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "moscato_db"),
        }

    def _connect(self):
        if mysql is None:
            raise ConnectionError("mysql-connector-python no está instalado.")
        return mysql.connector.connect(**self._db_config)

    def get_dashboard_data(self):
        data = {
            "producto_estrella": None,
            "ticket_promedio": 0.0,
            "pico_demanda": None,
            "categoria_rentable": None,
            "top_5": [],
            "ventas_por_hora": []
        }
        
        try:
            conn = self._connect()
        except Exception:
            return data
            
        cursor = conn.cursor(dictionary=True)
        try:
            # Producto Estrella (más unidades vendidas)
            q_estrella = """
                SELECT p.nombre, SUM(dp.cantidad) as total_vendido
                FROM detalle_pedido dp
                JOIN productos p ON dp.id_producto = p.id_producto
                JOIN pedidos pe ON dp.id_pedido = pe.id_pedido
                WHERE pe.estado_pedido NOT IN ('Cancelado')
                GROUP BY p.id_producto
                ORDER BY total_vendido DESC
                LIMIT 1
            """
            cursor.execute(q_estrella)
            estrella = cursor.fetchone()
            if estrella:
                data["producto_estrella"] = estrella["nombre"]

            # Comandas por día (promedio)
            q_comandas = """
                SELECT COUNT(id_pedido) / GREATEST(COUNT(DISTINCT DATE(fecha_apertura)), 1) as promedio_diario
                FROM pedidos
                WHERE estado_pedido NOT IN ('Cancelado')
            """
            cursor.execute(q_comandas)
            comandas = cursor.fetchone()
            if comandas and comandas["promedio_diario"]:
                data["ticket_promedio"] = float(comandas["promedio_diario"])

            # Categoría más rentable
            q_categoria = """
                SELECT c.nombre, SUM(dp.subtotal) as ingresos
                FROM detalle_pedido dp
                JOIN productos p ON dp.id_producto = p.id_producto
                JOIN categorias c ON p.id_categoria = c.id_categoria
                JOIN pedidos pe ON dp.id_pedido = pe.id_pedido
                WHERE pe.estado_pedido NOT IN ('Cancelado')
                GROUP BY c.id_categoria
                ORDER BY ingresos DESC
                LIMIT 1
            """
            cursor.execute(q_categoria)
            categoria = cursor.fetchone()
            if categoria:
                data["categoria_rentable"] = categoria["nombre"]
                
            # Top 5 Platos
            q_top5 = """
                SELECT p.nombre, SUM(dp.cantidad) as total_vendido
                FROM detalle_pedido dp
                JOIN productos p ON dp.id_producto = p.id_producto
                JOIN pedidos pe ON dp.id_pedido = pe.id_pedido
                WHERE pe.estado_pedido NOT IN ('Cancelado')
                GROUP BY p.id_producto
                ORDER BY total_vendido DESC
                LIMIT 5
            """
            cursor.execute(q_top5)
            data["top_5"] = cursor.fetchall()
            
            # Pico demanda (hora)
            q_hora = """
                SELECT HOUR(fecha_apertura) as hora, COUNT(*) as cantidad_pedidos
                FROM pedidos
                WHERE estado_pedido NOT IN ('Cancelado')
                  AND HOUR(fecha_apertura) BETWEEN 9 AND 20
                GROUP BY HOUR(fecha_apertura)
                ORDER BY cantidad_pedidos DESC
            """
            cursor.execute(q_hora)
            horas = cursor.fetchall()
            
            # Format ventas_por_hora for chart (9 to 20 hours)
            ventas_dict = {h: 0 for h in range(9, 21)}
            for h in horas:
                if h["hora"] is not None:
                    ventas_dict[h["hora"]] = h["cantidad_pedidos"]
                    
            data["ventas_por_hora"] = [{"hora": f"{h:02d}:00", "pedidos": count} for h, count in ventas_dict.items()]
            
            if horas and horas[0]["hora"] is not None:
                pico_h = horas[0]["hora"]
                data["pico_demanda"] = f"{pico_h:02d}:00 - {(pico_h+1)%24:02d}:00"
            else:
                data["pico_demanda"] = "N/A"

        except Exception as e:
            print("Error en AnalisisModel:", e)
        finally:
            cursor.close()
            conn.close()
            
        return data
