from __future__ import annotations

import os
from typing import Any

try:
    import mysql.connector
    from mysql.connector import Error
except Exception:  # pragma: no cover - fallback cuando mysql-connector no esta disponible
    mysql = None
    Error = Exception


class ModeloUsuarios:
    """Modelo MVC para operaciones CRUD de usuarios en MySQL."""

    def __init__(self, db_config: dict[str, Any] | None = None) -> None:
        self._db_config = db_config or {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3396")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "moscato_db"),
            "autocommit": False,
        }

    def obtener_empleados(self) -> list[dict[str, Any]]:
        connection = self._connect()
        if connection is None:
            return []

        sql = """
            SELECT
                id_usuario,
                nombre,
                rol,
                activo,
                fecha_actualizacion
            FROM usuarios
            ORDER BY nombre ASC
        """

        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall() or []
        except Error:
            return []
        finally:
            connection.close()

        empleados = []
        for row in rows:
            empleados.append(
                {
                    "id": int(row.get("id_usuario") or 0),
                    "name": str(row.get("nombre") or "-"),
                    "role": self._rol_db_a_ui(str(row.get("rol") or "Mesonero")),
                    "status": "Fichado" if int(row.get("activo") or 0) == 1 else "Fuera de Turno",
                    "time": row.get("fecha_actualizacion"),
                }
            )
        return empleados

    def crear_empleado(self, nombre: str, rol_ui: str) -> bool:
        connection = self._connect()
        if connection is None:
            return False

        rol_db = self._rol_ui_a_db(rol_ui)
        username_base = self._slug_username(nombre)
        username = self._build_unique_username(connection, username_base)

        sql = """
            INSERT INTO usuarios (nombre, username, password, rol, activo)
            VALUES (%s, %s, %s, %s, 1)
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (nombre, username, "123456", rol_db))
            connection.commit()
            return True
        except Error:
            connection.rollback()
            return False
        finally:
            connection.close()

    def actualizar_empleado(self, emp_id: int, nombre: str, rol_ui: str) -> bool:
        connection = self._connect()
        if connection is None:
            return False

        rol_db = self._rol_ui_a_db(rol_ui)
        sql = """
            UPDATE usuarios
            SET nombre = %s, rol = %s
            WHERE id_usuario = %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (nombre, rol_db, emp_id))
            connection.commit()
            return True
        except Error:
            connection.rollback()
            return False
        finally:
            connection.close()

    def eliminar_empleado(self, emp_id: int) -> bool:
        connection = self._connect()
        if connection is None:
            return False

        sql = "DELETE FROM usuarios WHERE id_usuario = %s"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (emp_id,))
            connection.commit()
            return True
        except Error:
            connection.rollback()
            return False
        finally:
            connection.close()

    def _build_unique_username(self, connection, base: str) -> str:
        base = base or "empleado"
        candidate = base
        seq = 1

        sql = "SELECT 1 FROM usuarios WHERE username = %s LIMIT 1"
        with connection.cursor() as cursor:
            while True:
                cursor.execute(sql, (candidate,))
                exists = cursor.fetchone() is not None
                if not exists:
                    return candidate
                seq += 1
                candidate = f"{base}{seq}"

    def _connect(self):
        if mysql is None:
            return None
        try:
            return mysql.connector.connect(**self._db_config)
        except Error:
            return None

    @staticmethod
    def _slug_username(nombre: str) -> str:
        cleaned = "".join(ch.lower() if ch.isalnum() else "" for ch in nombre)
        return cleaned[:14] or "empleado"

    @staticmethod
    def _rol_ui_a_db(rol: str) -> str:
        if rol == "Mesero":
            return "Mesonero"
        return rol

    @staticmethod
    def _rol_db_a_ui(rol: str) -> str:
        raw = str(rol or "").strip().lower()
        if raw in {"admin", "administrador"}:
            return "Administrador"
        if raw in {"mesero", "mesonero", "waiter"}:
            return "Mesero"
        if raw in {"cocinero", "chef", "kitchen"}:
            return "Cocinero"
        return "Mesero"
