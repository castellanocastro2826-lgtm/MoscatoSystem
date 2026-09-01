import os
import platform
import tkinter as tk
from tkinter import messagebox
import logging

import customtkinter as ctk

from src.controllers.cocina.controlador_cocina import ControladorCocina
from src.controllers.admin.controlador_admin import ControladorAdmin
from src.models.auditoria.auditoria_model import AuditoriaModel
from src.models.cocina.modelo_cocina import ModeloCocina
from src.models.usuarios.modelo_usuarios import ModeloUsuarios
from src.views.cocina.vista_cocina import CocinaDesignWindow
from src.views.admin.vista_admin import UnifiedDashboardWindow
from src.views.pedidos.vista_mesero import MeseroDesignWindow

platform.win32_ver = lambda *args, **kwargs: ("10", "10.0.0", "", "")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success, on_mesero_demo, on_cocina_demo):
        super().__init__(master, fg_color="#1A1C1E")
        self.on_login_success = on_login_success
        self.on_mesero_demo = on_mesero_demo
        self.on_cocina_demo = on_cocina_demo
        self.modelo_usuarios = ModeloUsuarios()
        self._build_layout()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(
            self,
            fg_color="#23272A",
            border_width=1,
            border_color="#34393D",
            corner_radius=12,
        )
        card.grid(row=0, column=0, padx=24, pady=24)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Restaurante Moscato", text_color="#F4EBD0", font=("Segoe UI", 28, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(card, text="Sistema de gestion de pedidos - Acceso de personal", text_color="#D6C9A8", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", pady=(0, 18))

        ctk.CTkLabel(card, text="Usuario", text_color="#F4EBD0", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.username_var = tk.StringVar()
        self.username_entry = ctk.CTkEntry(card, textvariable=self.username_var, width=420, height=40, fg_color="#151719", border_color="#35393D", text_color="#F4EBD0")
        self.username_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(card, text="Contraseña", text_color="#F4EBD0", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", pady=(0, 6))
        self.password_var = tk.StringVar()
        self.password_entry = ctk.CTkEntry(card, textvariable=self.password_var, show="*", width=420, height=40, fg_color="#151719", border_color="#35393D", text_color="#F4EBD0")
        self.password_entry.grid(row=5, column=0, sticky="ew", pady=(0, 18))

        ctk.CTkButton(card, text="Iniciar sesion", fg_color="#8C1A11", hover_color="#A1241A", text_color="#F4EBD0", font=("Segoe UI", 13, "bold"), height=40, command=self._attempt_login).grid(row=6, column=0, sticky="ew")

        ctk.CTkButton(card, text="Ver Diseno Mesero (Demo)", fg_color="#4A1E1A", hover_color="#5B241F", text_color="#F4EBD0", font=("Segoe UI", 12, "bold"), height=38, command=self.on_mesero_demo).grid(row=7, column=0, sticky="ew", pady=(8, 0))
        ctk.CTkButton(card, text="Ver Diseno Cocina (Demo)", fg_color="#4A1E1A", hover_color="#5B241F", text_color="#F4EBD0", font=("Segoe UI", 12, "bold"), height=38, command=self.on_cocina_demo).grid(row=8, column=0, sticky="ew", pady=(8, 0))

        self.status_var = tk.StringVar(value="Listo para autenticar")
        ctk.CTkLabel(card, textvariable=self.status_var, text_color="#D6C9A8", font=("Segoe UI", 11)).grid(row=9, column=0, sticky="w", pady=(12, 0))

        # We must bind to the username entry because the frame won't catch <Return> globally easily
        self.password_entry.bind("<Return>", lambda _event: self._attempt_login())
        self.username_entry.bind("<Return>", lambda _event: self._attempt_login())
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
            user = self.modelo_usuarios.autenticar_usuario(username, password)
            if not user:
                self.status_var.set("Credenciales invalidas")
                messagebox.showerror("Acceso denegado", "Usuario o contrasena incorrectos.")
                logging.warning(f"Intento de acceso fallido para usuario: {username}")
                return

            self.status_var.set(f"Sesion iniciada: {user['nombre']} ({user['rol']})")
            logging.info(f"Usuario {username} ha iniciado sesión.")
            try:
                AuditoriaModel().registrar_accion(
                    int(user.get("id_usuario") or 0),
                    "LOGIN",
                    "usuarios",
                    f"El usuario {user['nombre']} inició sesión en el sistema.",
                )
            except Exception as e:
                logging.error(f"Fallo al registrar auditoría: {e}")
            self.on_login_success(user)
        except Exception as exc:
            self.status_var.set("Error en autenticacion")
            logging.error(f"Error autenticando: {exc}", exc_info=True)
            messagebox.showerror("Error", f"No se pudo validar el usuario: {exc}")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Restaurante Moscato")
        self.geometry("1100x750")
        self.minsize(1100, 720)
        
        self.current_frame = None
        self.show_login()

    def _clear_frame(self):
        if self.current_frame is not None:
            if hasattr(self.current_frame, "destroy"):
                self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        self._clear_frame()
        self.current_frame = LoginView(
            self, 
            on_login_success=self.open_dashboard,
            on_mesero_demo=self.open_mesero_demo,
            on_cocina_demo=self.open_cocina_demo
        )
        self.current_frame.pack(fill="both", expand=True)

    def open_dashboard(self, user: dict) -> None:
        self._clear_frame()
        rol = str(user.get("rol", "")).strip().lower()
        nombre_real = str(user.get("nombre", "")).strip()

        if rol == "administrador":
            self.current_frame = UnifiedDashboardWindow(self, usuario=nombre_real, id_usuario=int(user.get("id_usuario") or 0))
            ControladorAdmin(self.current_frame, id_usuario=int(user.get("id_usuario") or 0))
        elif rol == "cocinero":
            modelo = ModeloCocina()
            self.current_frame = CocinaDesignWindow(self, usuario=nombre_real)
            controlador = ControladorCocina(self.current_frame, modelo)
            self.current_frame.controlador = controlador
            controlador.actualizar_pantalla()
        elif rol == "mesero":
            self.current_frame = MeseroDesignWindow(self, usuario=nombre_real)
        else:
            self.current_frame = MeseroDesignWindow(self, usuario=nombre_real)
            
        self.current_frame.pack(fill="both", expand=True)

    def open_mesero_demo(self) -> None:
        self._clear_frame()
        self.current_frame = MeseroDesignWindow(self, usuario="Alejandro V.")
        self.current_frame.pack(fill="both", expand=True)

    def open_cocina_demo(self) -> None:
        self._clear_frame()
        modelo = ModeloCocina()
        self.current_frame = CocinaDesignWindow(self, usuario="Cocina Central")
        controlador = ControladorCocina(self.current_frame, modelo)
        self.current_frame.controlador = controlador
        controlador.actualizar_pantalla()
        self.current_frame.pack(fill="both", expand=True)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log", mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def main() -> None:
    setup_logging()
    logging.info("Iniciando aplicacion Moscato...")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
