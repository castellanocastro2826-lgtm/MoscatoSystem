import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


class CocinaDesignWindow(ctk.CTkToplevel):
    """Vista de referencia del monitor de cocina (solo diseno UI)."""

    def __init__(self, master: tk.Misc, usuario: str = "Cocina Central") -> None:
        super().__init__(master)
        self.title("Monitor de Cocina - Pedidos Activos")
        self.geometry("1320x780")
        self.minsize(980, 680)
        self.configure(fg_color="#141517")

        self.usuario = usuario
        self._icon_refs: list[ImageTk.PhotoImage] = []
        self._ticket_cards: list[ctk.CTkFrame] = []
        self._board_canvas: tk.Canvas | None = None
        self._board_content: ctk.CTkFrame | None = None
        self._board_host: ctk.CTkFrame | None = None
        self._board_window_id: int | None = None
        self._board_layout_pending = False
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._active_section = "kitchen"
        self._main_frame: ctk.CTkFrame | None = None

        self._build_layout()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()
        self._show_section("kitchen")

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, fg_color="#1A0D0C", width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(brand, text="MOSCATO HQ", text_color="#F4EBD0", font=("Segoe UI", 28, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(brand, text="Terminal B1", text_color="#E5D7BC", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=(2, 0))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="nsew", padx=8, pady=(12, 8))
        sidebar.grid_rowconfigure(1, weight=1)

        self._nav_buttons["orders"] = self._nav_button(nav, "Orders", "orders", section="orders")
        self._nav_buttons["orders"].grid(row=0, column=0, sticky="ew", pady=4)
        self._nav_buttons["kitchen"] = self._nav_button(nav, "Kitchen", "kitchen", section="kitchen", active=True)
        self._nav_buttons["kitchen"].grid(row=1, column=0, sticky="ew", pady=4)
        self._nav_buttons["inventory"] = self._nav_button(nav, "Inventory", "inventory", section="inventory")
        self._nav_buttons["inventory"].grid(row=2, column=0, sticky="ew", pady=4)
        self._nav_buttons["menu"] = self._nav_button(nav, "Menu", "menu", section="menu")
        self._nav_buttons["menu"].grid(row=3, column=0, sticky="ew", pady=4)

        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 14))
        self._nav_buttons["help"] = self._nav_button(footer, "Help", "help", section="help")
        self._nav_buttons["help"].grid(row=0, column=0, sticky="ew", pady=4)
        self._nav_buttons["logout"] = self._nav_button(footer, "Logout", "logout", section="logout")
        self._nav_buttons["logout"].grid(row=1, column=0, sticky="ew", pady=4)

        sidebar.grid_columnconfigure(0, weight=1)
        nav.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(0, weight=1)

    def _build_main_panel(self) -> None:
        self._main_frame = ctk.CTkFrame(self, fg_color="#180C0D", corner_radius=0)
        self._main_frame.grid(row=0, column=1, sticky="nsew")
        self._main_frame.grid_columnconfigure(0, weight=1)
        self._main_frame.grid_rowconfigure(0, weight=1)

    def _render_kitchen_view(self) -> None:
        if self._main_frame is None:
            return

        self._main_frame.grid_columnconfigure(0, weight=1)
        self._main_frame.grid_rowconfigure(2, weight=1)
        self._build_header(self._main_frame)
        self._build_stats(self._main_frame)
        self._build_board(self._main_frame)

    def _render_placeholder(self, section: str) -> None:
        if self._main_frame is None:
            return

        title_map = {
            "orders": "Vista Orders",
            "inventory": "Vista Inventory",
            "menu": "Vista Menu",
            "help": "Centro de Ayuda",
        }
        subtitle_map = {
            "orders": "Aqui se mostrara el historial y despacho de ordenes para cocina.",
            "inventory": "Aqui se mostraran niveles de stock y alertas de reposicion.",
            "menu": "Aqui se mostraran recetas y estatus de disponibilidad del menu.",
            "help": "Aqui se mostraran guias rapidas y recomendaciones operativas.",
        }

        panel = ctk.CTkFrame(
            self._main_frame,
            fg_color="#1E1314",
            border_color="#3A2A2B",
            border_width=1,
            corner_radius=12,
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)

        ctk.CTkLabel(
            panel,
            text=title_map.get(section, "Modulo"),
            text_color="#F4EBD0",
            font=("Segoe UI", 34, "bold"),
        ).pack(anchor="w", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            panel,
            text=subtitle_map.get(section, "Seccion en construccion."),
            text_color="#D7CBAE",
            font=("Segoe UI", 14),
            wraplength=840,
            justify="left",
        ).pack(anchor="w", padx=24)

    def _build_header(self, parent: tk.Misc) -> None:
        header = ctk.CTkFrame(parent, fg_color="#180C0D", corner_radius=0, height=66)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        header.grid_propagate(False)

        ctk.CTkLabel(header, text="MOSCATO", text_color="#F4EBD0", font=("Segoe UI", 40, "bold")).pack(side="left", padx=(8, 8))
        ctk.CTkFrame(header, fg_color="#7A3931", width=2, height=38, corner_radius=0).pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(header, text=self.usuario, text_color="#F09F86", font=("Segoe UI", 24, "bold")).pack(side="left")

        tools = ctk.CTkFrame(header, fg_color="#221214", corner_radius=8)
        tools.pack(side="right", padx=(8, 0), pady=6)

        ctk.CTkLabel(
            tools,
            text="  ONLINE  ",
            image=self._make_icon("status", "#7ED957", size=12),
            compound="left",
            fg_color="#332021",
            text_color="#F4EBD0",
            corner_radius=8,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=3,
        ).pack(side="left", padx=(6, 10), pady=4)

        for icon_name in ["wifi", "bell", "user"]:
            ctk.CTkLabel(tools, text="", image=self._make_icon(icon_name, "#F4EBD0", size=16), fg_color="transparent").pack(
                side="left", padx=4
            )

    def _build_stats(self, parent: tk.Misc) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="#180C0D", corner_radius=0)
        wrap.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 8))
        wrap.grid_columnconfigure((0, 1, 2, 3), weight=1)

        cards = [
            ("PEDIDOS ACTIVOS", "12", "clipboard", "#EFA894"),
            ("TIEMPO PROMEDIO", "14:20", "timer", "#F4EBD0"),
            ("EN PREPARACION", "08", "flame", "#FFB000"),
            ("PENDIENTES", "04", "alert", "#FF9E8F"),
        ]

        for idx, (title, value, icon, accent) in enumerate(cards):
            stat = ctk.CTkFrame(wrap, fg_color="#2A1718", border_color="#4A2D2D", border_width=1, corner_radius=8)
            stat.grid(row=0, column=idx, sticky="ew", padx=6)
            stat.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(stat, text=title, text_color="#E8DABF", font=("Segoe UI", 9, "bold")).grid(
                row=0, column=0, sticky="w", padx=10, pady=(8, 2)
            )
            ctk.CTkLabel(stat, text=value, text_color=accent, font=("Segoe UI", 38, "bold")).grid(
                row=1, column=0, sticky="w", padx=10, pady=(0, 8)
            )
            ctk.CTkLabel(stat, text="", image=self._make_icon(icon, accent, size=20), fg_color="transparent").grid(
                row=1, column=1, sticky="e", padx=(0, 10), pady=(0, 6)
            )

    def _build_board(self, parent: tk.Misc) -> None:
        host = ctk.CTkFrame(parent, fg_color="#180C0D", corner_radius=0)
        host.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        host.grid_columnconfigure(0, weight=1)
        host.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(host, bg="#180C0D", bd=0, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(host, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        content = ctk.CTkFrame(canvas, fg_color="#180C0D", corner_radius=0)
        self._board_window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        self._board_canvas = canvas
        self._board_content = content
        self._board_host = host

        content.bind("<Configure>", self._update_board_scrollregion)
        canvas.bind("<Configure>", self._on_board_canvas_configure)
        host.bind("<Configure>", self._schedule_board_layout)

        ticket_data = [
            {
                "mesa": "T-04",
                "tiempo": "22:05",
                "estado": "CRITICO",
                "estado_bg": "#8E1313",
                "borde": "#9D1B1B",
                "items": ["2x  BIFE DE CHORIZO", "1x  RISOTTO DE HONGOS", "1x  ENSALADA CAPRESE"],
                "detalle": "Punto: Sangrante",
            },
            {
                "mesa": "T-12",
                "tiempo": "08:15",
                "estado": "PREPARANDO",
                "estado_bg": "#D89B1C",
                "borde": "#B8891D",
                "items": ["3x  PASTA CARBONARA", "1x  GNOCCHI AL PESTO"],
                "detalle": "Extra queso pecorino",
            },
            {
                "mesa": "#882",
                "tiempo": "04:30",
                "estado": "PREPARANDO",
                "estado_bg": "#D89B1C",
                "borde": "#B8891D",
                "items": ["4x  PIZZA MARGHERITA"],
                "detalle": "Para llevar",
            },
            {
                "mesa": "T-08",
                "tiempo": "18:45",
                "estado": "DEMORADO",
                "estado_bg": "#8E1313",
                "borde": "#9D1B1B",
                "items": ["1x  PULPO A LA GALLEGA", "1x  CALAMARES FRITOS"],
                "detalle": "Mesa",
            },
            {
                "mesa": "T-02",
                "tiempo": "02:10",
                "estado": "NUEVO",
                "estado_bg": "#C49315",
                "borde": "#B8891D",
                "items": ["1x  TIRAMISU MOSCATO", "2x  ESPRESSO DOBLE"],
                "detalle": "Mesa",
            },
        ]

        self._ticket_cards = [self._kitchen_ticket(content, data) for data in ticket_data]
        self.after_idle(self._layout_board_cards)

    def _layout_board_cards(self) -> None:
        self._board_layout_pending = False
        if not self._board_content or not self._board_canvas:
            return

        available_width = max(1, self._board_canvas.winfo_width() - 20)
        card_min_width = 330
        columns = max(1, available_width // card_min_width)
        columns = min(columns, len(self._ticket_cards))

        for index, card in enumerate(self._ticket_cards):
            card.grid_forget()
            row = index // columns
            col = index % columns
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            card.configure(width=max(300, available_width // columns - 14))

        for col_idx in range(len(self._ticket_cards)):
            self._board_content.grid_columnconfigure(col_idx, weight=0)
        for col_idx in range(columns):
            self._board_content.grid_columnconfigure(col_idx, weight=1, uniform="kitchen")

        self._update_board_scrollregion()

    def _schedule_board_layout(self, _event: tk.Event | None = None) -> None:
        if self._board_layout_pending:
            return
        self._board_layout_pending = True
        self.after_idle(self._layout_board_cards)

    def _on_board_canvas_configure(self, event: tk.Event) -> None:
        if self._board_canvas is not None and self._board_window_id is not None:
            # Bloquea el ancho del frame interno al ancho visible del canvas para evitar desbordes laterales.
            self._board_canvas.itemconfigure(self._board_window_id, width=event.width)
        self._schedule_board_layout()

    def _update_board_scrollregion(self, _event: tk.Event | None = None) -> None:
        if self._board_canvas is not None:
            self._board_canvas.configure(scrollregion=self._board_canvas.bbox("all"))

    def _kitchen_ticket(self, parent: tk.Misc, data: dict) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color="#2A1718", border_color=data["borde"], border_width=1, corner_radius=8)
        card.grid_propagate(False)

        header_color = "#6A0E0E" if data["estado"] in {"CRITICO", "DEMORADO"} else "#4B360F"
        head = ctk.CTkFrame(card, fg_color=header_color, corner_radius=6)
        head.pack(fill="x", padx=4, pady=4)
        head.grid_columnconfigure(0, weight=1)

        label_type = "MESA" if not str(data["mesa"]).startswith("#") else "PARA LLEVAR"
        ctk.CTkLabel(head, text=label_type, text_color="#D5BFA0", font=("Segoe UI", 8, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(5, 0)
        )

        mesa_color = "#FFB000" if data["estado"] not in {"CRITICO", "DEMORADO"} else "#FF5B5B"
        ctk.CTkLabel(head, text=data["mesa"], text_color=mesa_color, font=("Segoe UI", 33, "bold")).grid(
            row=1, column=0, sticky="w", padx=8, pady=(0, 6)
        )

        time_wrap = ctk.CTkFrame(head, fg_color="transparent")
        time_wrap.grid(row=0, column=1, rowspan=2, sticky="ne", padx=8, pady=6)
        ctk.CTkLabel(time_wrap, text="", image=self._make_icon("clock", "#F4EBD0", size=12), fg_color="transparent").pack(side="left")
        ctk.CTkLabel(time_wrap, text=f" {data['tiempo']}", text_color="#F4EBD0", font=("Segoe UI", 10, "bold")).pack(side="left")

        ctk.CTkLabel(
            head,
            text=data["estado"],
            fg_color=data["estado_bg"],
            text_color="#F4EBD0",
            corner_radius=8,
            font=("Segoe UI", 8, "bold"),
            padx=7,
            pady=2,
        ).grid(row=2, column=1, sticky="e", padx=8, pady=(0, 6))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=8, pady=(8, 6))

        first = True
        for item in data["items"]:
            parts = item.split("  ", 1)
            qty = parts[0] if len(parts) > 1 else ""
            name = parts[1] if len(parts) > 1 else parts[0]

            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=(0, 4))
            ctk.CTkLabel(row, text=qty, text_color="#FF9C00", font=("Segoe UI", 22, "bold")).pack(side="left")
            ctk.CTkLabel(row, text=f" {name}", text_color="#F4EBD0", font=("Segoe UI", 20, "bold")).pack(side="left")

            if first and data.get("detalle"):
                ctk.CTkLabel(body, text=data["detalle"], text_color="#F19B95", font=("Segoe UI", 12, "italic")).pack(anchor="w", pady=(0, 6))
                first = False

            ctk.CTkFrame(body, fg_color="#5C3A3A", height=1, corner_radius=0).pack(fill="x", pady=(2, 4))

        ctk.CTkButton(
            card,
            text="NOTIFICAR AL MESERO",
            image=self._make_icon("check", "#F4EBD0", size=14),
            compound="left",
            fg_color="#49A54A",
            hover_color="#5EB95E",
            text_color="#F4EBD0",
            font=("Segoe UI", 12, "bold"),
            height=38,
            command=lambda: None,
        ).pack(fill="x", padx=6, pady=(0, 6))

        return card

    def _nav_button(
        self,
        parent: tk.Misc,
        text: str,
        icon_name: str,
        section: str,
        active: bool = False,
    ) -> ctk.CTkButton:
        bg = "#9E1F14" if active else "#1A0D0C"
        hover = "#B52619" if active else "#2A1A18"
        icon = self._make_icon(icon_name, "#F4EBD0")

        return ctk.CTkButton(
            parent,
            text=f"  {text}",
            image=icon,
            compound="left",
            anchor="w",
            fg_color=bg,
            hover_color=hover,
            text_color="#F4EBD0",
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            height=42,
            command=lambda s=section: self._show_section(s),
        )

    def _show_section(self, section: str) -> None:
        self._active_section = section
        self._update_nav_state()

        if section == "logout":
            self.destroy()
            return

        if self._main_frame is None:
            return

        for child in self._main_frame.winfo_children():
            child.destroy()

        if section == "kitchen":
            self._render_kitchen_view()
        else:
            self._render_placeholder(section)

    def _update_nav_state(self) -> None:
        for section, button in self._nav_buttons.items():
            is_active = section == self._active_section
            button.configure(
                fg_color="#9E1F14" if is_active else "#1A0D0C",
                hover_color="#B52619" if is_active else "#2A1A18",
            )

    def _make_icon(self, name: str, color: str, size: int = 18) -> ImageTk.PhotoImage:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        p = max(2, size // 8)
        s = max(1, size // 8)

        if name == "status":
            draw.ellipse((p + 1, p + 1, size - p - 1, size - p - 1), fill=color)
        elif name == "wifi":
            draw.arc((p, p + 3, size - p, size - p + 1), 200, 340, fill=color, width=s)
            draw.arc((p + 3, p + 6, size - p - 3, size - p + 1), 210, 330, fill=color, width=s)
            draw.ellipse((size // 2 - 1, size - p - 3, size // 2 + 1, size - p - 1), fill=color)
        elif name == "bell":
            draw.arc((p + 1, p + 1, size - p - 1, size - p), 200, 340, fill=color, width=s)
            draw.line((p + 3, size - p - 4, size - p - 3, size - p - 4), fill=color, width=s)
            draw.ellipse((size // 2 - 1, size - p - 2, size // 2 + 1, size - p), fill=color)
        elif name == "user":
            draw.ellipse((p + 3, p + 1, size - p - 3, p + 7), outline=color, width=s)
            draw.arc((p + 1, p + 6, size - p - 1, size - p), 200, 340, fill=color, width=s)
        elif name == "clipboard":
            draw.rounded_rectangle((p, p + 2, size - p, size - p), radius=2, outline=color, width=s)
            draw.rectangle((size // 2 - 3, p, size // 2 + 3, p + 3), outline=color, width=s)
        elif name == "timer":
            draw.ellipse((p + 1, p + 3, size - p - 1, size - p), outline=color, width=s)
            draw.line((size // 2, size // 2 + 1, size // 2, p + 6), fill=color, width=s)
            draw.line((size // 2, size // 2 + 1, size // 2 + 4, size // 2 + 1), fill=color, width=s)
        elif name == "flame":
            draw.polygon([(size // 2, p), (size - p - 2, size - p - 2), (size // 2 + 1, size - p), (p + 2, size - p - 2)], outline=color, fill=None)
        elif name == "alert":
            draw.line((size // 2, p + 1, size // 2, size - p - 5), fill=color, width=s)
            draw.ellipse((size // 2 - 1, size - p - 3, size // 2 + 1, size - p - 1), fill=color)
        elif name == "clock":
            draw.ellipse((p, p, size - p, size - p), outline=color, width=s)
            draw.line((size // 2, size // 2, size // 2, p + 3), fill=color, width=s)
            draw.line((size // 2, size // 2, size - p - 3, size // 2), fill=color, width=s)
        elif name == "check":
            draw.line((p + 1, size // 2, size // 2 - 1, size - p - 2), fill=color, width=s)
            draw.line((size // 2 - 1, size - p - 2, size - p - 1, p + 2), fill=color, width=s)
        elif name == "orders":
            draw.rounded_rectangle((p, p, size - p, size - p), radius=2, outline=color, width=s)
            draw.line((p + 3, size // 2, size - p - 3, size // 2), fill=color, width=s)
        elif name == "kitchen":
            draw.arc((p, p + 1, size - p, size - p), 180, 360, fill=color, width=s)
            draw.line((p + 1, size // 2, size - p - 1, size // 2), fill=color, width=s)
        elif name == "inventory":
            draw.rectangle((p + 2, p + 2, size - p - 2, size - p - 2), outline=color, width=s)
            draw.line((p + 5, size // 2, size - p - 5, size // 2), fill=color, width=s)
        elif name == "menu":
            for y in (p + 3, size // 2, size - p - 3):
                draw.line((p, y, size - p, y), fill=color, width=s)
        elif name == "help":
            draw.ellipse((p, p, size - p, size - p), outline=color, width=s)
            draw.line((size // 2, p + 4, size // 2, size // 2), fill=color, width=s)
            draw.ellipse((size // 2 - 1, size - p - 3, size // 2 + 1, size - p - 1), fill=color)
        elif name == "logout":
            draw.rectangle((p + 5, p, size - p - 1, size - p), outline=color, width=s)
            draw.line((p, size // 2, size - p - 4, size // 2), fill=color, width=s)
            draw.polygon([(size - p - 6, size // 2 - 4), (size - p - 1, size // 2), (size - p - 6, size // 2 + 4)], fill=color)
        else:
            draw.ellipse((p, p, size - p, size - p), outline=color, width=s)

        icon = ImageTk.PhotoImage(image)
        self._icon_refs.append(icon)
        return icon
