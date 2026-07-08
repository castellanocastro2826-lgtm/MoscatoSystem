import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


class UnifiedDashboardWindow(ctk.CTkToplevel):
    """Panel unificado Mesero/Cocina en una sola ventana."""

    def __init__(self, master: tk.Misc, usuario: str, initial_section: str = "orders", rol: str | None = None) -> None:
        super().__init__(master)
        self.title("Moscato - Panel Unificado")
        self.geometry("1360x820")
        self.minsize(1080, 700)
        self.configure(fg_color="#141517")

        self.usuario = usuario
        if rol is None:
            rol = "cocinero" if initial_section == "kitchen" else "mesonero"
        self.rol = str(rol).strip().lower()
        self._active_section = initial_section
        self._icon_refs: list[ImageTk.PhotoImage] = []
        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        self._orders_product_cards: list[ctk.CTkFrame] = []
        self._orders_canvas: tk.Canvas | None = None
        self._orders_content: ctk.CTkFrame | None = None
        self._orders_window_id: int | None = None
        self._orders_layout_pending = False

        self._kitchen_ticket_cards: list[ctk.CTkFrame] = []
        self._kitchen_canvas: tk.Canvas | None = None
        self._kitchen_content: ctk.CTkFrame | None = None
        self._kitchen_window_id: int | None = None
        self._kitchen_layout_pending = False

        self._build_layout()
        self._show_section(initial_section)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        self.content = ctk.CTkFrame(self, fg_color="#16181A", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, fg_color="#1A0D0C", width=230, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        ctk.CTkLabel(brand, text="MOSCATO HQ", text_color="#F4EBD0", font=("Segoe UI", 30, "bold")).pack(anchor="w")
        ctk.CTkLabel(brand, text=f"USUARIO: {self.usuario}", text_color="#D9C8A9", font=("Segoe UI", 11)).pack(anchor="w", pady=(2, 0))

        menu = ctk.CTkFrame(sidebar, fg_color="transparent")
        menu.grid(row=1, column=0, sticky="nsew", padx=8, pady=(10, 8))
        sidebar.grid_rowconfigure(1, weight=1)

        if self.rol == "mesonero":
            menu_items = [("orders", "Orders")]
        elif self.rol == "cocinero":
            menu_items = [("kitchen", "Kitchen")]
        else:
            menu_items = [
                ("orders", "Orders"),
                ("kitchen", "Kitchen"),
                ("inventory", "Inventory"),
                ("menu", "Menu"),
            ]

        for row, (section, label) in enumerate(menu_items):
            self._nav_buttons[section] = self._nav_button(menu, label, section)
            self._nav_buttons[section].grid(row=row, column=0, sticky="ew", pady=4)

        foot = ctk.CTkFrame(sidebar, fg_color="transparent")
        foot.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 14))
        self._nav_buttons["help"] = self._nav_button(foot, "Help", "help")
        self._nav_buttons["help"].grid(row=0, column=0, sticky="ew", pady=4)
        self._nav_buttons["logout"] = self._nav_button(foot, "Logout", "logout")
        self._nav_buttons["logout"].grid(row=1, column=0, sticky="ew", pady=4)

        sidebar.grid_columnconfigure(0, weight=1)
        menu.grid_columnconfigure(0, weight=1)
        foot.grid_columnconfigure(0, weight=1)

    def _nav_button(self, parent: tk.Misc, text: str, section: str) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=f"  {text}",
            image=self._make_icon(section if section != "logout" else "logout", "#F4EBD0", 15),
            compound="left",
            anchor="w",
            fg_color="#1A0D0C",
            hover_color="#2A1A18",
            text_color="#F4EBD0",
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            height=42,
            command=lambda s=section: self._show_section(s),
        )

    def _show_section(self, section: str) -> None:
        self._active_section = section
        for key, btn in self._nav_buttons.items():
            active = key == section
            btn.configure(
                fg_color="#9E1F14" if active else "#1A0D0C",
                hover_color="#B52619" if active else "#2A1A18",
            )

        if section == "logout":
            self.destroy()
            return

        for child in self.content.winfo_children():
            child.destroy()

        if section == "orders":
            self._render_orders_section()
        elif section == "kitchen":
            self._render_kitchen_section()
        else:
            self._render_placeholder(section)

    def _render_orders_section(self) -> None:
        root = ctk.CTkFrame(self.content, fg_color="#16181A", corner_radius=0)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)
        root.grid_rowconfigure(3, weight=1)

        head = ctk.CTkFrame(root, fg_color="#201011", corner_radius=0, height=82)
        head.grid(row=0, column=0, columnspan=2, sticky="ew")
        head.grid_propagate(False)
        ctk.CTkLabel(head, text="Plano de Mesas", text_color="#F4EBD0", font=("Segoe UI", 30, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(8, 0)
        )
        ctk.CTkLabel(
            head,
            text="Seleccione una mesa para iniciar o editar pedido",
            text_color="#E5D7BC",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 8))

        legend = ctk.CTkFrame(head, fg_color="transparent")
        legend.grid(row=1, column=1, sticky="e", padx=12)
        for i, (color, label) in enumerate([("#57B85C", "LIBRE"), ("#D14A3E", "OCUPADA"), ("#E7A533", "ATENCION")]):
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.grid(row=0, column=i, padx=8)
            ctk.CTkLabel(item, text="●", text_color=color, font=("Segoe UI", 10, "bold")).pack(side="left")
            ctk.CTkLabel(item, text=f" {label}", text_color="#E5D7BC", font=("Segoe UI", 9, "bold")).pack(side="left")

        mesas = ctk.CTkFrame(root, fg_color="transparent")
        mesas.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 6))
        mesas.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        data = [("M1", "Ocupada", "#58312D"), ("M2", "Libre", "#2B2525"), ("M3", "Libre", "#2B2525"), ("M4", "Atencion", "#362D12"), ("M5", "Libre", "#2B2525"), ("M6", "Libre", "#2B2525")]
        for i, (mesa, estado, color) in enumerate(data):
            border = "#D49A2B" if estado == "Atencion" else "#3A3030"
            card = ctk.CTkFrame(mesas, fg_color=color, border_width=1, border_color=border, corner_radius=6)
            card.grid(row=0, column=i, sticky="ew", padx=5)
            ctk.CTkLabel(card, text=mesa, text_color="#F3E6CC", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=10, pady=(6, 0))
            ctk.CTkLabel(card, text=estado, text_color="#F3E6CC", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 6))

        chips = ctk.CTkFrame(root, fg_color="transparent")
        chips.grid(row=2, column=0, sticky="ew", padx=12, pady=(2, 8))
        chips.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        chip_data = ["Chinese Food", "International", "Drinks & Bar", "Desserts", "Wines"]
        for i, text in enumerate(chip_data):
            ctk.CTkButton(
                chips,
                text=text,
                corner_radius=8,
                fg_color="#8C1A11" if i == 0 else "#3A2B2A",
                hover_color="#A62216",
                text_color="#F4EBD0",
                font=("Segoe UI", 10, "bold"),
                height=32,
                command=lambda: None,
            ).grid(row=0, column=i, sticky="ew", padx=4)

        catalog_wrap = ctk.CTkFrame(root, fg_color="#0F1012", corner_radius=8)
        catalog_wrap.grid(row=3, column=0, sticky="nsew", padx=(12, 8), pady=(0, 12))
        catalog_wrap.grid_columnconfigure(0, weight=1)
        catalog_wrap.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(catalog_wrap, bg="#0F1012", bd=0, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll = tk.Scrollbar(catalog_wrap, orient="vertical", command=canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scroll.set)

        content = ctk.CTkFrame(canvas, fg_color="#0F1012", corner_radius=0)
        self._orders_window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        self._orders_canvas = canvas
        self._orders_content = content
        content.bind("<Configure>", lambda _e: self._orders_canvas and self._orders_canvas.configure(scrollregion=self._orders_canvas.bbox("all")))
        canvas.bind("<Configure>", self._on_orders_canvas_configure)

        platos = [
            ("Pollo Kung", "$18.50", "Pollo salteado con cacahuates, vegetales y salsa."),
            ("Arroz Yangzhou", "$14.00", "Arroz frito premium con camarones y cerdo BBQ."),
            ("Dim Sum Mixto", "$22.00", "Seleccion de 6 piezas de la casa."),
            ("Mapo Tofu", "$16.50", "Tofu suave en salsa de chile."),
            ("Rollos Primavera", "$9.50", "4 piezas rellenas de vegetales."),
            ("Cerveza Tsingtao", "$12.00", "Botella fria 330ml."),
        ]

        self._orders_product_cards = []
        for nombre, precio, desc in platos:
            card = ctk.CTkFrame(content, fg_color="#231819", border_color="#3B2A2A", border_width=1, corner_radius=8)
            ctk.CTkLabel(card, text="", image=self._make_icon("dish", "#DCCAA8", 64)).pack(anchor="w", padx=8, pady=(8, 2))
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=8)
            ctk.CTkLabel(row, text=nombre, text_color="#F4EBD0", font=("Segoe UI", 17, "bold")).pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=precio, text_color="#E8A27E", font=("Segoe UI", 13, "bold")).pack(side="right")
            lbl = ctk.CTkLabel(card, text=desc, text_color="#DCCAA8", font=("Segoe UI", 10), justify="left", wraplength=220, anchor="w")
            lbl.pack(fill="x", padx=8, pady=(4, 10))
            card.desc = lbl
            self._orders_product_cards.append(card)

        side = ctk.CTkFrame(root, fg_color="#2A1718", width=320, corner_radius=0)
        side.grid(row=1, column=1, rowspan=3, sticky="nsew", padx=(0, 12), pady=(8, 12))
        side.grid_propagate(False)
        ctk.CTkLabel(side, text="Pedido Actual", text_color="#F4EBD0", font=("Segoe UI", 28, "bold")).pack(anchor="w", padx=14, pady=(14, 0))
        head_row = ctk.CTkFrame(side, fg_color="transparent")
        head_row.pack(fill="x", padx=14)
        ctk.CTkLabel(head_row, text="TICKET #84291", text_color="#D6C9A8", font=("Segoe UI", 11, "bold")).pack(side="left")
        ctk.CTkLabel(
            head_row,
            text="MESA 1",
            text_color="#3A1E18",
            fg_color="#E8A995",
            corner_radius=10,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
        ).pack(side="right")

        item_box = ctk.CTkFrame(side, fg_color="transparent")
        item_box.pack(fill="both", expand=True, padx=14, pady=(10, 8))
        self._orders_order_item(item_box, "Pollo Kung Pao", "01", "$18.50").pack(fill="x", pady=(0, 8))
        self._orders_order_item(item_box, "Arroz Yangzhou", "01", "$14.00").pack(fill="x", pady=(0, 8))
        self._orders_order_item(item_box, "Cerveza Tsingtao", "02", "$12.00").pack(fill="x")

        totals = ctk.CTkFrame(side, fg_color="transparent")
        totals.pack(fill="x", padx=14, pady=(0, 8))
        self._orders_total_row(totals, "Subtotal", "$44.50").pack(fill="x")
        self._orders_total_row(totals, "Servicio (10%)", "$4.45").pack(fill="x", pady=(2, 0))
        self._orders_total_row(totals, "TOTAL", "$48.95", strong=True).pack(fill="x", pady=(8, 0))

        btns = ctk.CTkFrame(side, fg_color="transparent")
        btns.pack(fill="x", padx=14, pady=(0, 12))
        btns.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            btns,
            text="Precuenta",
            image=self._make_icon("receipt", "#F4EBD0", 16),
            compound="left",
            fg_color="#3A2524",
            hover_color="#503231",
            text_color="#F4EBD0",
            font=("Segoe UI", 11, "bold"),
            command=lambda: None,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            btns,
            text="A Cocina",
            image=self._make_icon("send", "#2A1718", 16),
            compound="left",
            fg_color="#F0A58E",
            hover_color="#F8B7A5",
            text_color="#2A1718",
            font=("Segoe UI", 11, "bold"),
            command=lambda: None,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkButton(
            btns,
            text="Cerrar Mesa & Pagar",
            image=self._make_icon("cash", "#0F2010", 16),
            compound="left",
            fg_color="#4FA64F",
            hover_color="#66BB66",
            text_color="#0F2010",
            font=("Segoe UI", 11, "bold"),
            command=lambda: None,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        root.after_idle(self._layout_orders_cards)

    def _orders_order_item(self, parent: tk.Misc, nombre: str, cantidad: str, subtotal: str) -> ctk.CTkFrame:
        item = ctk.CTkFrame(parent, fg_color="transparent")
        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=nombre, text_color="#F4EBD0", font=("Segoe UI", 14, "bold")).pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(top, text=subtotal, text_color="#F4EBD0", font=("Segoe UI", 14, "bold")).pack(side="right")

        controls = ctk.CTkFrame(item, fg_color="transparent")
        controls.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(controls, text="-", text_color="#F4EBD0", fg_color="#3A2524", corner_radius=4, width=20).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(controls, text=cantidad, text_color="#F4EBD0", fg_color="#3A2524", corner_radius=4, width=20).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(controls, text="+", text_color="#F4EBD0", fg_color="#3A2524", corner_radius=4, width=20).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(controls, text="Sin picante", text_color="#D9C8A9", font=("Segoe UI", 9, "italic")).pack(side="left")
        return item

    def _orders_total_row(self, parent: tk.Misc, label: str, value: str, strong: bool = False) -> ctk.CTkFrame:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        size = 13 if not strong else 22
        ctk.CTkLabel(row, text=label, text_color="#F4EBD0", font=("Segoe UI", size, "bold" if strong else "normal")).pack(side="left")
        ctk.CTkLabel(row, text=value, text_color="#F4B39C" if strong else "#E5D7BC", font=("Segoe UI", size, "bold")).pack(side="right")
        return row

    def _on_orders_canvas_configure(self, event: tk.Event) -> None:
        if self._orders_canvas is not None and self._orders_window_id is not None:
            self._orders_canvas.itemconfigure(self._orders_window_id, width=event.width)
        if not self._orders_layout_pending:
            self._orders_layout_pending = True
            self.after_idle(self._layout_orders_cards)

    def _layout_orders_cards(self) -> None:
        self._orders_layout_pending = False
        if not self._orders_canvas or not self._orders_content:
            return
        width = max(1, self._orders_canvas.winfo_width() - 20)
        cols = max(1, min(len(self._orders_product_cards), width // 260))
        for i, card in enumerate(self._orders_product_cards):
            card.grid_forget()
            r, c = divmod(i, cols)
            card.grid(row=r, column=c, sticky="nsew", padx=7, pady=7)
            card.configure(width=max(235, width // cols - 16))
            if hasattr(card, "desc"):
                card.desc.configure(wraplength=max(170, width // cols - 28))
        for i in range(len(self._orders_product_cards)):
            self._orders_content.grid_columnconfigure(i, weight=0)
        for i in range(cols):
            self._orders_content.grid_columnconfigure(i, weight=1, uniform="orders")
        self._orders_canvas.configure(scrollregion=self._orders_canvas.bbox("all"))

    def _render_kitchen_section(self) -> None:
        root = ctk.CTkFrame(self.content, fg_color="#180C0D", corner_radius=0)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(root, fg_color="#180C0D", corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="MOSCATO", text_color="#F4EBD0", font=("Segoe UI", 40, "bold")).pack(side="left", padx=(8, 8))
        ctk.CTkFrame(header, fg_color="#7A3931", width=2, height=38, corner_radius=0).pack(side="left", padx=8, pady=10)
        ctk.CTkLabel(header, text="Cocina Central", text_color="#F09F86", font=("Segoe UI", 24, "bold")).pack(side="left")

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

        kpi = ctk.CTkFrame(root, fg_color="transparent")
        kpi.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 8))
        kpi.grid_columnconfigure((0, 1, 2, 3), weight=1)
        vals = [
            ("PEDIDOS ACTIVOS", "12", "clipboard", "#EFA894"),
            ("TIEMPO PROMEDIO", "14:20", "timer", "#F4EBD0"),
            ("EN PREPARACION", "08", "flame", "#FFB000"),
            ("PENDIENTES", "04", "alert", "#FF9E8F"),
        ]
        for i, (t, v, icon, c) in enumerate(vals):
            box = ctk.CTkFrame(kpi, fg_color="#2A1718", border_color="#4A2D2D", border_width=1, corner_radius=8)
            box.grid(row=0, column=i, sticky="ew", padx=6)
            box.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(box, text=t, text_color="#E8DABF", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(box, text=v, text_color=c, font=("Segoe UI", 38, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
            ctk.CTkLabel(box, text="", image=self._make_icon(icon, c, size=20), fg_color="transparent").grid(
                row=1, column=1, sticky="e", padx=(0, 10), pady=(0, 6)
            )

        board_wrap = ctk.CTkFrame(root, fg_color="#180C0D", corner_radius=0)
        board_wrap.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        board_wrap.grid_columnconfigure(0, weight=1)
        board_wrap.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(board_wrap, bg="#180C0D", bd=0, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll = tk.Scrollbar(board_wrap, orient="vertical", command=canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scroll.set)

        content = ctk.CTkFrame(canvas, fg_color="#180C0D", corner_radius=0)
        self._kitchen_window_id = canvas.create_window((0, 0), window=content, anchor="nw")
        self._kitchen_canvas = canvas
        self._kitchen_content = content

        content.bind("<Configure>", lambda _e: self._kitchen_canvas and self._kitchen_canvas.configure(scrollregion=self._kitchen_canvas.bbox("all")))
        canvas.bind("<Configure>", self._on_kitchen_canvas_configure)

        tickets = [
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

        self._kitchen_ticket_cards = []
        for data in tickets:
            card = ctk.CTkFrame(content, fg_color="#2A1718", border_color=data["borde"], border_width=1, corner_radius=8)
            card.grid_propagate(False)

            head = ctk.CTkFrame(card, fg_color="#6A0E0E" if data["estado"] in {"CRITICO", "DEMORADO"} else "#4B360F", corner_radius=6)
            head.pack(fill="x", padx=4, pady=4)
            head.grid_columnconfigure(0, weight=1)

            label_type = "MESA" if not str(data["mesa"]).startswith("#") else "PARA LLEVAR"
            ctk.CTkLabel(head, text=label_type, text_color="#D5BFA0", font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(5, 0))

            mesa_color = "#FFB000" if data["estado"] not in {"CRITICO", "DEMORADO"} else "#FF5B5B"
            ctk.CTkLabel(head, text=data["mesa"], text_color=mesa_color, font=("Segoe UI", 33, "bold")).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))

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
            self._kitchen_ticket_cards.append(card)

        root.after_idle(self._layout_kitchen_cards)

    def _on_kitchen_canvas_configure(self, event: tk.Event) -> None:
        if self._kitchen_canvas is not None and self._kitchen_window_id is not None:
            self._kitchen_canvas.itemconfigure(self._kitchen_window_id, width=event.width)
        if not self._kitchen_layout_pending:
            self._kitchen_layout_pending = True
            self.after_idle(self._layout_kitchen_cards)

    def _layout_kitchen_cards(self) -> None:
        self._kitchen_layout_pending = False
        if not self._kitchen_canvas or not self._kitchen_content:
            return
        width = max(1, self._kitchen_canvas.winfo_width() - 20)
        cols = max(1, min(len(self._kitchen_ticket_cards), width // 330))
        for i, card in enumerate(self._kitchen_ticket_cards):
            card.grid_forget()
            r, c = divmod(i, cols)
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            card.configure(width=max(300, width // cols - 14))
        for i in range(len(self._kitchen_ticket_cards)):
            self._kitchen_content.grid_columnconfigure(i, weight=0)
        for i in range(cols):
            self._kitchen_content.grid_columnconfigure(i, weight=1, uniform="kitchen")
        self._kitchen_canvas.configure(scrollregion=self._kitchen_canvas.bbox("all"))

    def _render_placeholder(self, section: str) -> None:
        panel = ctk.CTkFrame(self.content, fg_color="#1E1314", border_color="#3A2A2B", border_width=1, corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        title = {
            "inventory": "Vista Inventory",
            "menu": "Vista Menu",
            "help": "Centro de Ayuda",
        }.get(section, "Modulo")
        ctk.CTkLabel(panel, text=title, text_color="#F4EBD0", font=("Segoe UI", 34, "bold")).pack(anchor="w", padx=24, pady=(24, 8))
        ctk.CTkLabel(panel, text="Seccion en construccion dentro del panel unificado.", text_color="#D7CBAE", font=("Segoe UI", 14)).pack(
            anchor="w", padx=24
        )

    def _make_icon(self, name: str, color: str, size: int = 18) -> ImageTk.PhotoImage:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        p = max(2, size // 8)
        s = max(1, size // 8)

        if name == "orders":
            draw.rounded_rectangle((p, p, size - p, size - p), radius=2, outline=color, width=s)
            draw.line((p + 3, size // 2, size - p - 3, size // 2), fill=color, width=s)
        elif name == "status":
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
        elif name == "kitchen":
            draw.arc((p, p + 1, size - p, size - p), 180, 360, fill=color, width=s)
            draw.line((p + 1, size // 2, size - p - 1, size // 2), fill=color, width=s)
        elif name == "inventory":
            draw.rectangle((p + 2, p + 2, size - p - 2, size - p - 2), outline=color, width=s)
        elif name == "menu":
            for y in (p + 3, size // 2, size - p - 3):
                draw.line((p, y, size - p, y), fill=color, width=s)
        elif name == "help":
            draw.ellipse((p, p, size - p, size - p), outline=color, width=s)
            draw.line((size // 2, p + 4, size // 2, size // 2), fill=color, width=s)
        elif name == "logout":
            draw.rectangle((p + 5, p, size - p - 1, size - p), outline=color, width=s)
            draw.line((p, size // 2, size - p - 4, size // 2), fill=color, width=s)
            draw.polygon([(size - p - 6, size // 2 - 4), (size - p - 1, size // 2), (size - p - 6, size // 2 + 4)], fill=color)
        elif name == "receipt":
            draw.rounded_rectangle((p + 1, p, size - p - 1, size - p), radius=2, outline=color, width=s)
            for y in range(p + 3, size - p - 1, 3):
                draw.line((p + 3, y, size - p - 3, y), fill=color, width=1)
        elif name == "send":
            draw.line((p, size // 2, size - p - 5, size // 2), fill=color, width=s)
            draw.polygon([(size - p - 8, size // 2 - 4), (size - p - 1, size // 2), (size - p - 8, size // 2 + 4)], fill=color)
        elif name == "cash":
            draw.rounded_rectangle((p, p + 1, size - p, size - p - 1), radius=3, outline=color, width=s)
            draw.rectangle((p + 3, p + 4, size - p - 3, p + 6), fill=color)
            draw.ellipse((size // 2 - 1, size // 2 - 1, size // 2 + 1, size // 2 + 1), fill=color)
        elif name == "dish":
            draw.ellipse((p, p + 6, size - p, size - p - 1), outline=color, width=s)
            draw.arc((p + 5, p - 1, size - p - 5, size - p - 5), start=180, end=360, fill=color, width=s)
        else:
            draw.ellipse((p, p, size - p, size - p), outline=color, width=s)

        icon = ImageTk.PhotoImage(image)
        self._icon_refs.append(icon)
        return icon
