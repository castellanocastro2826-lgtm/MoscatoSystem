import platform
platform.win32_ver = lambda *args, **kwargs: ("10", "10.0.0", "", "")
import os
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import mysql.connector
from mysql.connector import Error

from src.controllers.cocina.controlador_cocina import ControladorCocina
from src.controllers.admin.controlador_admin import ControladorAdmin
from src.models.auditoria.auditoria_model import AuditoriaModel
from src.models.cocina.modelo_cocina import ModeloCocina
from src.views.cocina.vista_cocina import CocinaDesignWindow
from src.views.admin.vista_admin import UnifiedDashboardWindow
from src.views.pedidos.vista_mesero import MeseroDesignWindow


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class DatabaseConnection:
    def __init__(self) -> None:
        self.config = {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "moscato_db"),
            "autocommit": True,
        }

    def connect(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as exc:
            raise ConnectionError(f"No fue posible conectar a MySQL: {exc}") from exc


class LoginWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Restaurante Moscato - Inicio de Sesion")
        self.geometry("860x520")
        self.minsize(760, 460)
        self.configure(fg_color="#1A1C1E")

        self.db = DatabaseConnection()
        self._build_layout()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="#1A1C1E", corner_radius=0)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(
            container,
            fg_color="#23272A",
            border_width=1,
            border_color="#34393D",
            corner_radius=12,
        )
        card.grid(row=0, column=0, padx=24, pady=24)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Restaurante Moscato",
            text_color="#F4EBD0",
            font=("Segoe UI", 28, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(
            card,
            text="Sistema de gestion de pedidos - Acceso de personal",
            text_color="#D6C9A8",
            font=("Segoe UI", 12),
        ).grid(row=1, column=0, sticky="w", pady=(0, 18))

        ctk.CTkLabel(card, text="Usuario", text_color="#F4EBD0", font=("Segoe UI", 12, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 6)
        )
        self.username_var = tk.StringVar()
        self.username_entry = ctk.CTkEntry(
            card,
            textvariable=self.username_var,
            width=420,
            height=40,
            fg_color="#151719",
            border_color="#35393D",
            text_color="#F4EBD0",
        )
        self.username_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(card, text="Contraseña", text_color="#F4EBD0", font=("Segoe UI", 12, "bold")).grid(
            row=4, column=0, sticky="w", pady=(0, 6)
        )
        self.password_var = tk.StringVar()
        self.password_entry = ctk.CTkEntry(
            card,
            textvariable=self.password_var,
            show="*",
            width=420,
            height=40,
            fg_color="#151719",
            border_color="#35393D",
            text_color="#F4EBD0",
        )
        self.password_entry.grid(row=5, column=0, sticky="ew", pady=(0, 18))

        ctk.CTkButton(
            card,
            text="Iniciar sesion",
            fg_color="#8C1A11",
            hover_color="#A1241A",
            text_color="#F4EBD0",
            font=("Segoe UI", 13, "bold"),
            height=40,
            command=self._attempt_login,
        ).grid(row=6, column=0, sticky="ew")

        ctk.CTkButton(
            card,
            text="Ver Diseno Mesero (Demo)",
            fg_color="#4A1E1A",
            hover_color="#5B241F",
            text_color="#F4EBD0",
            font=("Segoe UI", 12, "bold"),
            height=38,
            command=self._open_mesero_design_demo,
        ).grid(row=7, column=0, sticky="ew", pady=(8, 0))

        ctk.CTkButton(
            card,
            text="Ver Diseno Cocina (Demo)",
            fg_color="#4A1E1A",
            hover_color="#5B241F",
            text_color="#F4EBD0",
            font=("Segoe UI", 12, "bold"),
            height=38,
            command=self._open_cocina_design_demo,
        ).grid(row=8, column=0, sticky="ew", pady=(8, 0))

        self.status_var = tk.StringVar(value="Listo para autenticar")
        ctk.CTkLabel(card, textvariable=self.status_var, text_color="#D6C9A8", font=("Segoe UI", 11)).grid(
            row=9, column=0, sticky="w", pady=(12, 0)
        )

        self.bind("<Return>", lambda _event: self._attempt_login())
        self.username_entry.focus_set()

    def _attempt_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Campos requeridos", "Debe ingresar usuario y contrasena.")
            return

        self.status_var.set("Verificando credenciales...")
        self.update_idletasks()

        try:
            connection = self.db.connect()
            try:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT
                            u.id_usuario,
                            CONCAT(e.nombres, ' ', e.apellidos) AS nombre,
                            u.username,
                            u.rol
                        FROM usuarios AS u
                        INNER JOIN empleados AS e ON e.id_empleado = u.id_empleado
                        WHERE u.username = %s
                          AND u.password = %s
                          AND u.activo = 1
                          AND e.activo = 1
                        """,
                        (username, password),
                    )
                    user = cursor.fetchone()
            finally:
                connection.close()

            if not user:
                self.status_var.set("Credenciales invalidas")
                messagebox.showerror("Acceso denegado", "Usuario o contrasena incorrectos.")
                return

            self.status_var.set(f"Sesion iniciada: {user['nombre']} ({user['rol']})")
            try:
                AuditoriaModel().registrar_accion(
                    int(user.get("id_usuario") or 0),
                    "LOGIN",
                    "usuarios",
                    f"El usuario {user['nombre']} inició sesión en el sistema.",
                )
            except Exception:
                pass
            self._open_dashboard(user)

        except ConnectionError as exc:
            self.status_var.set("Error de conexion")
            messagebox.showerror("Base de datos", str(exc))
        except Error as exc:
            self.status_var.set("Error en autenticacion")
            messagebox.showerror("Error", f"No se pudo validar el usuario: {exc}")

    def _open_dashboard(self, user: dict) -> None:
        self.withdraw()
        rol = str(user.get("rol", "")).strip().lower()
        nombre_real = str(user.get("nombre", "")).strip()

        if rol == "administrador":
            vista = UnifiedDashboardWindow(self, usuario=nombre_real, id_usuario=int(user.get("id_usuario") or 0))
            ControladorAdmin(vista, id_usuario=int(user.get("id_usuario") or 0))
            vista.protocol("WM_DELETE_WINDOW", self.destroy)
        elif rol == "cocinero":
            modelo = ModeloCocina()
            vista = CocinaDesignWindow(self, usuario=nombre_real)
            controlador = ControladorCocina(vista, modelo)
            vista.controlador = controlador
            controlador.actualizar_pantalla()
            vista.protocol("WM_DELETE_WINDOW", self.destroy)
        elif rol == "mesonero":
            vista = MeseroDesignWindow(self, usuario=nombre_real)
            vista.protocol("WM_DELETE_WINDOW", self.destroy)
        else:
            vista = MeseroDesignWindow(self, usuario=nombre_real)
            vista.protocol("WM_DELETE_WINDOW", self.destroy)

    def _open_mesero_design_demo(self) -> None:
        self.withdraw()
        demo_window = MeseroDesignWindow(self, usuario="Alejandro V.")
        demo_window.protocol("WM_DELETE_WINDOW", self.destroy)

    def _open_cocina_design_demo(self) -> None:
        self.withdraw()
        modelo = ModeloCocina()
        demo_window = CocinaDesignWindow(self, usuario="Cocina Central")
        controlador = ControladorCocina(demo_window, modelo)
        demo_window.controlador = controlador
        controlador.actualizar_pantalla()
        demo_window.protocol("WM_DELETE_WINDOW", self.destroy)


def main() -> None:
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
