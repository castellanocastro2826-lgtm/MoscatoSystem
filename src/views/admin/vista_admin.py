import customtkinter as ctk


class UnifiedDashboardWindow(ctk.CTkToplevel):
    """Vista del panel unificado de administracion (solo UI y eventos)."""

    COLORS = {
        "primary": "#8C1A11",
        "secondary": "#F4EBD0",
        "tertiary": "#1A1C1E",
        "neutral": "#867370",
        "window": "#1A1C1E",
        "sidebar": "#171113",
        "card": "#231719",
        "profile_card": "#2A1B1E",
        "accent": "#8C1A11",
        "accent_hover": "#A1241A",
        "accent_soft": "#DFA99D",
        "wine_bg": "#1A1C1E",
        "wine_panel": "#231719",
        "wine_soft": "#2D1E21",
        "text_primary": "#F4EBD0",
        "text_secondary": "#867370",
        "text_warm": "#D8CDB2",
        "success": "#2EA44F",
        "muted": "#867370",
        "line": "#3A2A2D",
        "header_dark": "#1A1C1E",
        "table_row_a": "#281B1E",
        "table_row_b": "#24181B",
        "panel_border": "#4A3134",
        "chip_bg": "#3A2427",
        "chip_fg": "#F4EBD0",
        "hover_subtle": "#2B181A",
        "hover_surface": "#2F2023",
        "soft_hover": "#E8BBB2",
        "scroll_btn": "#5F3134",
        "scroll_btn_hover": "#754046",
        "role_cook_bg": "#2A2D31",
        "role_default_bg": "#2B2D31",
        "edit_hover": "#514044",
    }

    FONT = "Segoe UI"

    def __init__(self, parent, usuario: str, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.usuario = usuario
        self.controller = controller

        self.protocol("WM_DELETE_WINDOW", self.parent.destroy)

        self.geometry("1100x750")
        self.minsize(1100, 720)
        self.title("Moscato | Gestion de Usuarios")
        self.configure(fg_color=self.COLORS["wine_bg"])

        self._rows = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=236,
            fg_color=self.COLORS["sidebar"],
            corner_radius=0,
            border_width=1,
            border_color=self.COLORS["panel_border"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=1)

        logo_wrap = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_wrap.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))
        logo_wrap.grid_columnconfigure(0, weight=1)

        logo_title = ctk.CTkLabel(
            logo_wrap,
            text="MOSCATO",
            font=(self.FONT, 28, "bold"),
            text_color=self.COLORS["text_primary"],
            anchor="w",
        )
        logo_title.grid(row=0, column=0, sticky="w")

        admin_badge = ctk.CTkLabel(
            logo_wrap,
            text="ADMIN",
            font=(self.FONT, 9, "bold"),
            text_color=self.COLORS["text_primary"],
            fg_color=self.COLORS["accent"],
            corner_radius=8,
            padx=8,
            pady=2,
        )
        admin_badge.grid(row=0, column=1, sticky="e", padx=(8, 0), pady=(7, 0))

        logo_subtitle = ctk.CTkLabel(
            logo_wrap,
            text="Control de Usuarios",
            font=(self.FONT, 11),
            text_color=self.COLORS["neutral"],
            anchor="w",
        )
        logo_subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

        profile_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.COLORS["profile_card"],
            corner_radius=14,
            border_width=1,
            border_color=self.COLORS["line"],
        )
        profile_card.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 18))
        profile_card.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkLabel(
            profile_card,
            text="M",
            width=34,
            height=34,
            corner_radius=6,
            fg_color=self.COLORS["accent"],
            text_color=self.COLORS["text_primary"],
            font=(self.FONT, 14, "bold"),
        )
        avatar.grid(row=0, column=0, padx=(12, 8), pady=12)

        profile_text = ctk.CTkFrame(profile_card, fg_color="transparent")
        profile_text.grid(row=0, column=1, sticky="w", pady=12)

        profile_name = ctk.CTkLabel(
            profile_text,
            text="Moscato HQ",
            font=(self.FONT, 15, "bold"),
            text_color=self.COLORS["text_primary"],
            anchor="w",
        )
        profile_name.grid(row=0, column=0, sticky="w")

        profile_terminal = ctk.CTkLabel(
            profile_text,
            text="TERMINAL 01",
            font=(self.FONT, 11),
            text_color=self.COLORS["text_secondary"],
            anchor="w",
        )
        profile_terminal.grid(row=1, column=0, sticky="w", pady=(2, 0))

        nav_wrap = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_wrap.grid(row=2, column=0, sticky="ew", padx=12)
        nav_wrap.grid_columnconfigure(0, weight=1)

        self.nav_buttons = {}
        nav_items = [
            ("orders", "Orders", False),
            ("kitchen", "Kitchen", False),
            ("categories", "Gestion de Categorias", False),
            ("users", "Gestion de Usuarios", True),
        ]

        for idx, (key, text, active) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_wrap,
                text=text,
                height=38,
                corner_radius=6,
                anchor="w",
                font=(self.FONT, 12, "bold" if active else "normal"),
                fg_color=self.COLORS["accent"] if active else "transparent",
                hover_color=self.COLORS["accent_hover"] if active else self.COLORS["hover_subtle"],
                text_color=self.COLORS["text_primary"] if active else self.COLORS["text_warm"],
                border_width=1 if not active else 0,
                border_color=self.COLORS["panel_border"],
                command=lambda: None,
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=5)
            self.nav_buttons[key] = btn

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=5, column=0, sticky="ew", padx=12, pady=(8, 16))
        footer.grid_columnconfigure(0, weight=1)

        help_btn = ctk.CTkButton(
            footer,
            text="Help",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            hover_color=self.COLORS["hover_surface"],
            text_color=self.COLORS["text_secondary"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            font=(self.FONT, 12),
            command=lambda: None,
        )
        help_btn.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        logout_btn = ctk.CTkButton(
            footer,
            text="Logout",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            hover_color=self.COLORS["hover_surface"],
            text_color=self.COLORS["text_secondary"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            font=(self.FONT, 12),
            command=self._logout_to_login,
        )
        logout_btn.grid(row=1, column=0, sticky="ew")

    def _logout_to_login(self) -> None:
        self.destroy()
        if self.parent is not None and self.parent.winfo_exists():
            self.parent.deiconify()

    def _build_main_panel(self):
        self.main_panel = ctk.CTkFrame(self, fg_color=self.COLORS["wine_bg"], corner_radius=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_columnconfigure(0, weight=1)
        self.main_panel.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 8))
        top_bar.grid_columnconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=0)
        top_bar.grid_columnconfigure(2, weight=0)

        self.search_entry = ctk.CTkEntry(
            top_bar,
            height=34,
            placeholder_text="Buscar personal por nombre o rol...",
            fg_color=self.COLORS["wine_panel"],
            border_color=self.COLORS["panel_border"],
            text_color=self.COLORS["text_primary"],
            placeholder_text_color=self.COLORS["text_secondary"],
            corner_radius=6,
            font=(self.FONT, 12),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        quick_ping = ctk.CTkButton(
            top_bar,
            text="◉",
            width=34,
            height=34,
            corner_radius=6,
            fg_color=self.COLORS["wine_panel"],
            hover_color=self.COLORS["hover_surface"],
            text_color=self.COLORS["accent_soft"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            command=lambda: None,
        )
        quick_ping.grid(row=0, column=1, padx=(8, 0))

        quick_menu = ctk.CTkButton(
            top_bar,
            text="≡",
            width=34,
            height=34,
            corner_radius=6,
            fg_color=self.COLORS["wine_panel"],
            hover_color=self.COLORS["hover_surface"],
            text_color=self.COLORS["accent_soft"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            command=lambda: None,
        )
        quick_menu.grid(row=0, column=2, padx=(8, 0))

        header = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=20, pady=(2, 10))
        header.grid_columnconfigure(0, weight=1)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            title_block,
            text="Gestion de Usuarios",
            font=(self.FONT, 34, "bold"),
            text_color=self.COLORS["text_primary"],
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            title_block,
            text="Administra el personal, roles y estado de fichaje en tiempo real.",
            font=(self.FONT, 12),
            text_color=self.COLORS["neutral"],
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        add_btn = ctk.CTkButton(
            header,
            text="+ Nuevo Empleado",
            width=170,
            height=36,
            corner_radius=6,
            fg_color=self.COLORS["accent_soft"],
            hover_color=self.COLORS["soft_hover"],
            text_color=self.COLORS["tertiary"],
            font=(self.FONT, 12, "bold"),
            command=self._on_add_clicked,
        )
        add_btn.grid(row=0, column=1, sticky="e")

        body = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 14))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        directory_card = ctk.CTkFrame(
            body,
            fg_color=self.COLORS["wine_panel"],
            corner_radius=8,
            border_width=1,
            border_color=self.COLORS["panel_border"],
        )
        directory_card.grid(row=0, column=0, sticky="nsew")
        directory_card.grid_columnconfigure(0, weight=1)
        directory_card.grid_rowconfigure(2, weight=1)

        directory_title = ctk.CTkLabel(
            directory_card,
            text="Directorio de Personal",
            font=(self.FONT, 26, "bold"),
            text_color=self.COLORS["text_primary"],
            anchor="w",
        )
        directory_title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        headers_frame = ctk.CTkFrame(directory_card, fg_color=self.COLORS["wine_soft"], corner_radius=6)
        headers_frame.grid(row=1, column=0, sticky="ew", padx=12)
        headers_frame.grid_columnconfigure(0, weight=3)
        headers_frame.grid_columnconfigure(1, weight=2)
        headers_frame.grid_columnconfigure(2, weight=2)
        headers_frame.grid_columnconfigure(3, weight=3)
        headers_frame.grid_columnconfigure(4, weight=2)

        header_labels = ["EMPLEADO", "ROL", "ESTADO", "ULTIMO ACCESO", "ACCIONES"]
        for col, text in enumerate(header_labels):
            h = ctk.CTkLabel(
                headers_frame,
                text=text,
                font=(self.FONT, 10, "bold"),
                text_color=self.COLORS["text_warm"],
                anchor="w" if col != 4 else "center",
            )
            h.grid(row=0, column=col, sticky="ew", padx=12, pady=8)

        self.table_scroll = ctk.CTkScrollableFrame(
            directory_card,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.COLORS["scroll_btn"],
            scrollbar_button_hover_color=self.COLORS["scroll_btn_hover"],
        )
        self.table_scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(8, 12))
        self.table_scroll.grid_columnconfigure(0, weight=3)
        self.table_scroll.grid_columnconfigure(1, weight=2)
        self.table_scroll.grid_columnconfigure(2, weight=2)
        self.table_scroll.grid_columnconfigure(3, weight=3)
        self.table_scroll.grid_columnconfigure(4, weight=2)

        permissions = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        permissions.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 16))
        permissions.grid_columnconfigure((0, 1, 2), weight=1)

        cards = [
            (
                "Administrador",
                ["✓ Gestion total del sistema", "✓ Control de usuarios y auditoria", "✓ Acceso a reportes globales"],
            ),
            (
                "Mesero",
                ["✓ Toma y edicion de pedidos", "✓ Consulta de estado de mesas", "✓ Seguimiento de cocina"],
            ),
            (
                "Cocinero",
                ["✓ Gestion de ordenes en cola", "✓ Actualizacion de estado de platos", "✓ Vista de prioridades"],
            ),
        ]

        for idx, (role, items) in enumerate(cards):
            card = ctk.CTkFrame(
                permissions,
                fg_color=self.COLORS["wine_panel"],
                corner_radius=8,
                border_width=1,
                border_color=self.COLORS["panel_border"],
            )
            card.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 6, 0 if idx == 2 else 6), pady=(8, 0))
            card.grid_columnconfigure(0, weight=1)

            role_title = ctk.CTkLabel(
                card,
                text=role,
                font=(self.FONT, 14, "bold"),
                text_color=self.COLORS["text_primary"],
                anchor="w",
            )
            role_title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

            for line_idx, item in enumerate(items, start=1):
                entry = ctk.CTkLabel(
                    card,
                    text=item,
                    font=(self.FONT, 11),
                    text_color=self.COLORS["success"],
                    anchor="w",
                )
                entry.grid(row=line_idx, column=0, sticky="w", padx=12, pady=2)

            ctk.CTkLabel(card, text="", height=6).grid(row=len(items) + 1, column=0)

    def render_table(self, empleados_list):
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        self._rows = empleados_list or []

        if not self._rows:
            empty = ctk.CTkLabel(
                self.table_scroll,
                text="No hay empleados para mostrar.",
                font=(self.FONT, 13),
                text_color=self.COLORS["text_secondary"],
            )
            empty.grid(row=0, column=0, columnspan=5, sticky="nsew", pady=24)
            return

        role_styles = {
            "Administrador": (self.COLORS["primary"], self.COLORS["secondary"]),
            "Mesero": (self.COLORS["chip_bg"], self.COLORS["chip_fg"]),
            "Cocinero": (self.COLORS["role_cook_bg"], self.COLORS["secondary"]),
        }

        for row_idx, emp in enumerate(self._rows):
            row_bg = self.COLORS["table_row_a"] if row_idx % 2 == 0 else self.COLORS["table_row_b"]
            row = ctk.CTkFrame(
                self.table_scroll,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=self.COLORS["panel_border"],
            )
            row.grid(row=row_idx, column=0, columnspan=5, sticky="ew", padx=4, pady=4)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=3)
            row.grid_columnconfigure(4, weight=2)

            employee_wrap = ctk.CTkFrame(row, fg_color="transparent")
            employee_wrap.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
            employee_wrap.grid_columnconfigure(0, weight=1)

            employee_label = ctk.CTkLabel(
                employee_wrap,
                text=str(emp.get("name", "-")),
                font=(self.FONT, 12, "bold"),
                text_color=self.COLORS["text_primary"],
                anchor="w",
            )
            employee_label.grid(row=0, column=0, sticky="w")

            employee_id = ctk.CTkLabel(
                employee_wrap,
                text=f"ID: #{emp.get('id', '-')}",
                font=(self.FONT, 10),
                text_color=self.COLORS["neutral"],
                anchor="w",
            )
            employee_id.grid(row=1, column=0, sticky="w", pady=(1, 0))

            role_text = str(emp.get("role", "-"))
            role_bg, role_fg = role_styles.get(role_text, (self.COLORS["role_default_bg"], self.COLORS["text_warm"]))
            role_pill = ctk.CTkLabel(
                row,
                text=role_text,
                fg_color=role_bg,
                text_color=role_fg,
                corner_radius=12,
                padx=10,
                pady=3,
                font=(self.FONT, 10, "bold"),
            )
            role_pill.grid(row=0, column=1, sticky="w", padx=12)

            status_text = str(emp.get("status", "Fuera de Turno"))
            status_color = self.COLORS["success"] if status_text == "Fichado" else self.COLORS["muted"]
            status_label = ctk.CTkLabel(
                row,
                text=f"● {status_text}",
                font=(self.FONT, 11, "bold"),
                text_color=status_color,
                anchor="w",
            )
            status_label.grid(row=0, column=2, sticky="w", padx=12)

            time_label = ctk.CTkLabel(
                row,
                text=str(emp.get("time", "-")),
                font=(self.FONT, 11, "bold"),
                text_color=self.COLORS["text_secondary"],
                anchor="w",
            )
            time_label.grid(row=0, column=3, sticky="ew", padx=12)

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=4, sticky="e", padx=10)

            emp_id = emp.get("id")

            edit_btn = ctk.CTkButton(
                actions,
                text="✏️",
                width=36,
                height=30,
                corner_radius=8,
                fg_color=self.COLORS["chip_bg"],
                hover_color=self.COLORS["edit_hover"],
                text_color=self.COLORS["text_primary"],
                font=(self.FONT, 14),
                command=lambda eid=emp_id: self._on_edit_clicked(eid),
            )
            edit_btn.grid(row=0, column=0, padx=(0, 6))

            delete_btn = ctk.CTkButton(
                actions,
                text="🗑️",
                width=36,
                height=30,
                corner_radius=8,
                fg_color=self.COLORS["primary"],
                hover_color=self.COLORS["accent_hover"],
                text_color=self.COLORS["secondary"],
                font=(self.FONT, 14),
                command=lambda eid=emp_id: self._on_delete_clicked(eid),
            )
            delete_btn.grid(row=0, column=1)

    def get_search_query(self):
        return self.search_entry.get().strip()

    def _on_search_changed(self, event):
        if self.controller and hasattr(self.controller, "handle_search"):
            self.controller.handle_search()

    def _on_add_clicked(self):
        if self.controller and hasattr(self.controller, "handle_add_employee"):
            self.controller.handle_add_employee()

    def _on_edit_clicked(self, emp_id):
        if self.controller and hasattr(self.controller, "handle_edit_employee"):
            self.controller.handle_edit_employee(emp_id)

    def _on_delete_clicked(self, emp_id):
        if self.controller and hasattr(self.controller, "handle_delete_employee"):
            self.controller.handle_delete_employee(emp_id)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.withdraw()

    window = UnifiedDashboardWindow(root, usuario="admin_demo")

    demo_data = [
        {"id": 1, "name": "Marcela Ruiz", "role": "Administrador", "status": "Fichado", "time": "Hoy 08:02"},
        {"id": 2, "name": "Diego Pastor", "role": "Mesero", "status": "Fuera de Turno", "time": "Ayer 23:40"},
        {"id": 3, "name": "Valentina Sosa", "role": "Cocinero", "status": "Fichado", "time": "Hoy 07:55"},
        {"id": 4, "name": "Julian Roldan", "role": "Mesero", "status": "Fichado", "time": "Hoy 08:11"},
    ]
    window.render_table(demo_data)

    root.mainloop()
