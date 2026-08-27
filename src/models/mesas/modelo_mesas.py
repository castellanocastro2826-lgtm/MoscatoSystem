from __future__ import annotations

import os
from typing import Any

import mysql.connector
from mysql.connector import Error


class MesasModel:
    """Modelo MVC para consultar y actualizar el estado de mesas en MySQL."""

    ESTADOS_PERMITIDOS = {"Libre", "Ocupada", "Atencion", "Atención"}

    def __init__(self) -> None:
        self._db_config = {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "moscato_db"),
            "autocommit": False,
        }
        self.ultimo_error: str | None = None

    def _connect(self):
        try:
            return mysql.connector.connect(**self._db_config)
        except Error as exc:
            raise ConnectionError(f"No fue posible conectar con MySQL: {exc}") from exc

    def obtener_mesas(self) -> list[dict[str, Any]]:
        """Obtiene id, numero y estado actual de mesas activas."""
        sql = """
            SELECT id_mesa, numero_mesa, estado
            FROM mesas
            WHERE activo = 1
            ORDER BY numero_mesa ASC
        """

        self.ultimo_error = None
        try:
            connection = self._connect()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(sql)
                    return cursor.fetchall()
            finally:
                connection.close()
        except (ConnectionError, Error) as exc:
            self.ultimo_error = str(exc)
            return []

    def actualizar_estado_mesa(self, id_mesa: int, nuevo_estado: str) -> bool:
        """Actualiza estado de una mesa; retorna True cuando el UPDATE afecta filas."""
        if nuevo_estado not in self.ESTADOS_PERMITIDOS:
            self.ultimo_error = f"Estado no permitido: {nuevo_estado}"
            return False

        estado_db = self._normalizar_estado_para_db(nuevo_estado)
        sql = """
            UPDATE mesas
            SET estado = %s
            WHERE id_mesa = %s AND activo = 1
        """

        self.ultimo_error = None
        try:
            connection = self._connect()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (estado_db, id_mesa))
                connection.commit()
                return True
            except Error:
                connection.rollback()
                raise
            finally:
                connection.close()
        except (ConnectionError, Error) as exc:
            self.ultimo_error = str(exc)
            return False

    @staticmethod
    def _normalizar_estado_para_db(estado: str) -> str:
        """
        Mapea variaciones de texto para persistencia.
        Si tu schema usa otro valor para atencion (ej. Inactiva),
        puedes configurarlo con la variable DB_ESTADO_ATENCION.
        """
        texto = (estado or "").strip()
        if texto in {"Atencion", "Atención"}:
            return os.getenv("DB_ESTADO_ATENCION", "Atencion")
        return texto
