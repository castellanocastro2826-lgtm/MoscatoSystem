from __future__ import annotations

from datetime import datetime
from tkinter import messagebox, simpledialog
from typing import Any

from src.models.usuarios.modelo_usuarios import ModeloUsuarios


class ControladorAdmin:
    """Controlador MVC para gestion de usuarios del panel admin."""

    def __init__(self, vista, modelo: ModeloUsuarios | None = None, empleados_seed: list[dict[str, Any]] | None = None) -> None:
        self.vista = vista
        self.modelo = modelo or ModeloUsuarios()
        self._seed = empleados_seed or []
        self._all_empleados: list[dict[str, Any]] = []

        self.vista.controller = self
        self.cargar_empleados()

    def cargar_empleados(self) -> None:
        """Carga empleados desde DB y actualiza la tabla en la vista."""
        empleados = self.modelo.obtener_empleados()
        empleados = self._normalizar_empleados_para_vista(empleados)
        if empleados:
            self._all_empleados = empleados
        elif self._seed:
            self._all_empleados = list(self._seed)
        else:
            self._all_empleados = []
        self._render_filtrado_actual()

    def handle_search(self) -> None:
        self._render_filtrado_actual()

    def handle_add_employee(self) -> None:
        nombre = simpledialog.askstring("Nuevo empleado", "Nombre completo:", parent=self.vista)
        if not nombre:
            return

        rol = simpledialog.askstring(
            "Nuevo empleado",
            "Rol (Administrador, Mesero, Cocinero):",
            parent=self.vista,
            initialvalue="Mesero",
        )
        if not rol:
            return

        rol = self._normalizar_rol(rol)
        status = "Fichado"
        current_time = self._formatear_time(datetime.now())

        created = self.modelo.crear_empleado(nombre.strip(), rol)
        if created:
            self.cargar_empleados()
            return

        new_id = max([int(emp.get("id", 0)) for emp in self._all_empleados] + [0]) + 1
        self._all_empleados.append(
            {
                "id": new_id,
                "name": nombre.strip(),
                "role": rol,
                "status": status,
                "time": current_time,
            }
        )
        self._render_filtrado_actual()

    def handle_edit_employee(self, emp_id: int) -> None:
        empleado = self._find_by_id(emp_id)
        if empleado is None:
            messagebox.showwarning("Editar empleado", "No se encontro el empleado seleccionado.", parent=self.vista)
            return

        nuevo_nombre = simpledialog.askstring(
            "Editar empleado",
            "Nombre completo:",
            parent=self.vista,
            initialvalue=str(empleado.get("name", "")),
        )
        if not nuevo_nombre:
            return

        nuevo_rol = simpledialog.askstring(
            "Editar empleado",
            "Rol (Administrador, Mesero, Cocinero):",
            parent=self.vista,
            initialvalue=str(empleado.get("role", "Mesero")),
        )
        if not nuevo_rol:
            return

        nuevo_rol = self._normalizar_rol(nuevo_rol)

        updated = self.modelo.actualizar_empleado(emp_id, nuevo_nombre.strip(), nuevo_rol)
        if updated:
            self.cargar_empleados()
            return

        empleado["name"] = nuevo_nombre.strip()
        empleado["role"] = nuevo_rol
        empleado["time"] = self._formatear_time(datetime.now())
        self._render_filtrado_actual()

    def handle_delete_employee(self, emp_id: int) -> None:
        empleado = self._find_by_id(emp_id)
        if empleado is None:
            messagebox.showwarning("Eliminar empleado", "No se encontro el empleado seleccionado.", parent=self.vista)
            return

        confirm = messagebox.askyesno(
            "Eliminar empleado",
            f"Confirma eliminar a {empleado.get('name', 'este empleado')}?",
            parent=self.vista,
        )
        if not confirm:
            return

        deleted = self.modelo.eliminar_empleado(emp_id)
        if deleted:
            self.cargar_empleados()
            return

        self._all_empleados = [emp for emp in self._all_empleados if int(emp.get("id", -1)) != int(emp_id)]
        self._render_filtrado_actual()

    def _render_filtrado_actual(self) -> None:
        query = (self.vista.get_search_query() if hasattr(self.vista, "get_search_query") else "") or ""
        query = query.strip().lower()

        if not query:
            self.vista.render_table(self._all_empleados)
            return

        filtrados = []
        for emp in self._all_empleados:
            name = str(emp.get("name", "")).lower()
            role = str(emp.get("role", "")).lower()
            status = str(emp.get("status", "")).lower()
            if query in name or query in role or query in status:
                filtrados.append(emp)

        self.vista.render_table(filtrados)

    def _normalizar_empleados_para_vista(self, empleados: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalizados = []
        for emp in empleados:
            normalizados.append(
                {
                    "id": int(emp.get("id") or 0),
                    "name": str(emp.get("name") or "-"),
                    "role": self._normalizar_rol(str(emp.get("role") or "Mesero")),
                    "status": str(emp.get("status") or "Fuera de Turno"),
                    "time": self._formatear_time(emp.get("time")),
                }
            )
        return normalizados

    def _find_by_id(self, emp_id: int) -> dict[str, Any] | None:
        for emp in self._all_empleados:
            if int(emp.get("id", -1)) == int(emp_id):
                return emp
        return None

    @staticmethod
    def _normalizar_rol(rol: str) -> str:
        raw = str(rol or "").strip().lower()
        if raw in {"admin", "administrador"}:
            return "Administrador"
        if raw in {"mesero", "mesonero", "waiter"}:
            return "Mesero"
        if raw in {"cocinero", "chef", "kitchen"}:
            return "Cocinero"
        return "Mesero"

    @staticmethod
    def _formatear_time(valor: Any) -> str:
        if isinstance(valor, datetime):
            return valor.strftime("Hoy %H:%M")

        texto = str(valor or "").strip()
        if not texto:
            return "-"

        formatos = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        for fmt in formatos:
            try:
                dt = datetime.strptime(texto, fmt)
                return dt.strftime("Hoy %H:%M")
            except ValueError:
                continue

        return texto[:16]

