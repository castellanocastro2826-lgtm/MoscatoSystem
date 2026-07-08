import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


class MeseroDesignWindow(ctk.CTkToplevel):
    """Vista de referencia del terminal de mesero (solo diseno UI)."""

    def __init__(self, master: tk.Misc, usuario: str, mesa_actual: str = "Mesa 1") -> None:
        super().__init__(master)
        self.title("Terminal de Mesero - Toma de Pedidos")
        self.geometry("1320x780")
        self.minsize(1180, 680)
        self.configure(fg_color="#141517")

        self.usuario = usuario
        self.mesa_actual = mesa_actual
        self._icon_refs: list[ImageTk.PhotoImage] = []
        self._product_cards: list[ctk.CTkFrame] = []
        self._catalog_layout_pending = False
        self._catalog_canvas: tk.Canvas | None = None
        self._catalog_content: ctk.CTkFrame | None = None
        self._catalog_host: ctk.CTkFrame | None = None
        self._catalog_window_id: int | None = None
        self._center_frame: ctk.CTkFrame | None = None
        self._order_frame: ctk.CTkFrame | None = None
        self._section_frame: ctk.CTkFrame | None = None
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._active_section = "orders"

        self._build_layout()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._center_frame = self._build_center_panel()
        self._order_frame = self._build_order_panel()
        self._section_frame = ctk.CTkFrame(self, fg_color="#141517", corner_radius=0)
        self._section_frame.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self._section_frame.grid_remove()
        self._show_section("orders")

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, fg_color="#1A0D0C", width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            brand,
            text="MOSCATO",
            text_color="#F4EBD0",
            font=("Segoe UI", 30, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            brand,
            text=f"MESERO: {self.usuario.upper()}",
            text_color="#F1C6B8",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))
        ctk.CTkLabel(
            brand,
            text="Moscato HQ\nTerminal de Servicio B1",
            justify="left",
            text_color="#E7DCC3",
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="nsew", padx=8, pady=(12, 8))
        sidebar.grid_rowconfigure(1, weight=1)

        self._nav_buttons["orders"] = self._nav_button(nav, "Orders", "orders", section="orders", active=True)
        self._nav_buttons["orders"].grid(row=0, column=0, sticky="ew", pady=4)
        self._nav_buttons["kitchen"] = self._nav_button(nav, "Kitchen", "kitchen", section="kitchen")
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
            corner_radius=8,
            fg_color=bg,
            hover_color=hover,
            text_color="#F4EBD0",
            font=("Segoe UI", 14, "bold"),
            height=42,
            command=lambda s=section: self._show_section(s),
        )

    def _build_center_panel(self) -> ctk.CTkFrame:
        center = ctk.CTkFrame(self, fg_color="#16181A", corner_radius=0)
        center.grid(row=0, column=1, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(center, fg_color="#201011", corner_radius=0, height=76)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)

        ctk.CTkLabel(
            top,
            text="Plano de Mesas",
            text_color="#F4EBD0",
            font=("Segoe UI", 29, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 0))

        ctk.CTkLabel(
            top,
            text="Seleccione una mesa para iniciar o editar pedido",
            text_color="#E5D7BC",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(2, 10))

        legend = ctk.CTkFrame(top, fg_color="transparent")
        legend.grid(row=1, column=1, sticky="e", padx=12)
        self._legend_item(legend, "#57B85C", "LIBRE").grid(row=0, column=0, padx=8)
        self._legend_item(legend, "#D14A3E", "OCUPADA").grid(row=0, column=1, padx=8)
        self._legend_item(legend, "#E7A533", "ATENCION").grid(row=0, column=2, padx=8)

        mesas_wrap = ctk.CTkFrame(center, fg_color="transparent")
        mesas_wrap.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 6))
        mesas_wrap.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        mesas = [
            ("M1", "Ocupada", "#58312D"),
            ("M2", "Libre", "#2B2525"),
            ("M3", "Libre", "#2B2525"),
            ("M4", "Atencion", "#362D12"),
            ("M5", "Libre", "#2B2525"),
            ("M6", "Libre", "#2B2525"),
        ]
        for idx, (mesa, estado, bg_card) in enumerate(mesas):
            self._mesa_card(mesas_wrap, mesa, estado, bg_card).grid(row=0, column=idx, sticky="ew", padx=5, pady=2)

        categorias = ctk.CTkFrame(center, fg_color="transparent")
        categorias.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 8))
        categorias.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        chips = ["Chinese Food", "International", "Drinks & Bar", "Desserts", "Wines"]
        for idx, chip in enumerate(chips):
            self._chip(categorias, chip, active=(idx == 0)).grid(row=0, column=idx, sticky="ew", padx=4)

        self._build_catalog(center)
        return center

    def _legend_item(self, parent: tk.Misc, color: str, text: str) -> ctk.CTkFrame:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(wrap, text="●", text_color=color, font=("Segoe UI", 10, "bold")).pack(side="left")
        ctk.CTkLabel(wrap, text=f" {text}", text_color="#E5D7BC", font=("Segoe UI", 9, "bold")).pack(side="left")
        return wrap

    def _mesa_card(self, parent: tk.Misc, mesa: str, estado: str, bg_card: str) -> ctk.CTkFrame:
        border = "#D49A2B" if estado == "Atencion" else "#3A3030"
        card = ctk.CTkFrame(parent, fg_color=bg_card, border_color=border, border_width=1, corner_radius=6, height=72)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=mesa, text_color="#F3E6CC", font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkLabel(card, text=estado, text_color="#F3E6CC", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(1, 8))
        return card

    def _chip(self, parent: tk.Misc, text: str, active: bool = False) -> ctk.CTkButton:
        bg = "#8C1A11" if active else "#3A2B2A"
        return ctk.CTkButton(
            parent,
            text=text,
            corner_radius=8,
            fg_color=bg,
            hover_color="#A62216",
            text_color="#F4EBD0",
            font=("Segoe UI", 11, "bold"),
            height=34,
            command=lambda: None,
        )

    def _build_catalog(self, center: tk.Misc) -> None:
        list_wrap = ctk.CTkFrame(center, fg_color="#0F1012", corner_radius=8)
        list_wrap.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        list_wrap.grid_columnconfigure(0, weight=1)
        list_wrap.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(list_wrap, bg="#0F1012", bd=0, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(list_wrap, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        content = ctk.CTkFrame(canvas, fg_color="#0F1012", corner_radius=0)
        self._catalog_window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        self._catalog_canvas = canvas
        self._catalog_content = content
        self._catalog_host = list_wrap

        content.bind("<Configure>", self._update_catalog_scrollregion)
        list_wrap.bind("<Configure>", self._schedule_catalog_layout)
        canvas.bind("<Configure>", self._on_catalog_canvas_configure)

        cards = [
            ("Pollo Kung", "$18.50", "Pollo salteado con cacahuates, vegetales y salsa."),
            ("Arroz Yangzhou", "$14.00", "Arroz frito premium con camarones, cerdo BBQ y cebollin."),
            ("Dim Sum Mixto", "$22.00", "Seleccion de 6 piezas: Ha Gao, Siu Mai y dumplings."),
            ("Mapo Tofu", "$16.50", "Tofu suave en salsa de chile y habas fermentadas."),
            ("Rollos Primavera", "$9.50", "4 piezas de rollos crujientes rellenos de vegetales."),
            ("Cerveza Tsingtao", "$12.00", "Botella fria 330ml para maridar con platos fuertes."),
            ("Sopa Wonton", "$11.50", "Caldo suave con wontons y cebollin fresco."),
            ("Cerdo Agridulce", "$17.90", "Cubos crocantes con salsa brillante agridulce."),
            ("Te de Jazmin", "$5.00", "Infusion aromatica ideal para cerrar la comida."),
        ]

        self._product_cards = [self._product_card(content, n, p, d) for n, p, d in cards]
        self.after_idle(self._layout_catalog_cards)

    def _schedule_catalog_layout(self, _event: tk.Event | None = None) -> None:
        if self._catalog_layout_pending:
            return
        self._catalog_layout_pending = True
        self.after_idle(self._layout_catalog_cards)

    def _layout_catalog_cards(self) -> None:
        self._catalog_layout_pending = False
        if not self._catalog_content or not self._catalog_canvas:
            return

        available_width = max(1, self._catalog_canvas.winfo_width() - 20)
        card_min_width = 260
        columns = max(1, available_width // card_min_width)
        columns = min(columns, len(self._product_cards))

        for index, card in enumerate(self._product_cards):
            card.grid_forget()
            row = index // columns
            column = index % columns
            card.grid(row=row, column=column, sticky="nsew", padx=7, pady=7)
            card.configure(width=max(235, available_width // columns - 16))
            if hasattr(card, "descripcion_label"):
                card.descripcion_label.configure(wraplength=max(170, available_width // columns - 28))

        for col_idx in range(len(self._product_cards)):
            self._catalog_content.grid_columnconfigure(col_idx, weight=0)
        for col_idx in range(columns):
            self._catalog_content.grid_columnconfigure(col_idx, weight=1, uniform="catalog")

        self._update_catalog_scrollregion()

    def _update_catalog_scrollregion(self, _event: tk.Event | None = None) -> None:
        if self._catalog_canvas is not None:
            self._catalog_canvas.configure(scrollregion=self._catalog_canvas.bbox("all"))

    def _on_catalog_canvas_configure(self, event: tk.Event) -> None:
        if self._catalog_canvas is not None and self._catalog_window_id is not None:
            # Forza el ancho del frame interno al viewport para evitar desborde horizontal.
            self._catalog_canvas.itemconfigure(self._catalog_window_id, width=event.width)
        self._schedule_catalog_layout()

    def _product_card(self, parent: tk.Misc, nombre: str, precio: str, descripcion: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color="#231819", border_color="#3B2A2A", border_width=1, corner_radius=8)
        card.grid_propagate(False)

        image_box = ctk.CTkLabel(card, text="", image=self._make_icon("dish", "#DCCAA8", size=72), fg_color="transparent")
        image_box.pack(fill="x", padx=8, pady=(8, 4))

        title_wrap = ctk.CTkFrame(card, fg_color="transparent")
        title_wrap.pack(fill="x", padx=8)
        ctk.CTkLabel(title_wrap, text=nombre, text_color="#F4EBD0", font=("Segoe UI", 18, "bold"), anchor="w").pack(
            side="left", fill="x", expand=True
        )
        ctk.CTkLabel(title_wrap, text=precio, text_color="#E8A27E", font=("Segoe UI", 14, "bold")).pack(side="right")

        descripcion_label = ctk.CTkLabel(
            card,
            text=descripcion,
            justify="left",
            wraplength=190,
            text_color="#DCCAA8",
            font=("Segoe UI", 11),
            anchor="w",
        )
        descripcion_label.pack(fill="x", padx=8, pady=(6, 10))
        card.descripcion_label = descripcion_label

        return card

    def _build_order_panel(self) -> ctk.CTkFrame:
        side = ctk.CTkFrame(self, fg_color="#2A1718", width=320, corner_radius=0)
        side.grid(row=0, column=2, sticky="nsew")
        side.grid_propagate(False)

        header = ctk.CTkFrame(side, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 10))
        ctk.CTkLabel(header, text="Pedido Actual", text_color="#F4EBD0", font=("Segoe UI", 29, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text=self.mesa_actual.upper(),
            text_color="#3A1E18",
            fg_color="#E8A995",
            corner_radius=10,
            font=("Segoe UI", 9, "bold"),
            padx=9,
            pady=3,
        ).grid(row=0, column=1, sticky="e", padx=(12, 0))
        ctk.CTkLabel(header, text="TICKET #84291", text_color="#D6C9A8", font=("Segoe UI", 11, "bold")).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        item_wrap = ctk.CTkFrame(side, fg_color="transparent")
        item_wrap.grid(row=1, column=0, sticky="nsew", padx=14)
        side.grid_rowconfigure(1, weight=1)

        sample_items = [
            ("Pollo Kung Pao", "01", "$18.50"),
            ("Arroz Yangzhou", "01", "$14.00"),
            ("Cerveza Tsingtao", "02", "$12.00"),
        ]
        for idx, (nombre, cantidad, subtotal) in enumerate(sample_items):
            self._order_item(item_wrap, nombre, cantidad, subtotal).grid(row=idx, column=0, sticky="ew", pady=8)

        notes = self._preparation_notes_section(side)
        notes.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 8))

        totals = ctk.CTkFrame(side, fg_color="transparent")
        totals.grid(row=3, column=0, sticky="ew", padx=14, pady=(4, 8))
        self._total_row(totals, "Subtotal", "$44.50").grid(row=0, column=0, sticky="ew", pady=2)
        self._total_row(totals, "Servicio (10%)", "$4.45").grid(row=1, column=0, sticky="ew", pady=2)
        self._total_row(totals, "TOTAL", "$48.95", strong=True).grid(row=2, column=0, sticky="ew", pady=(8, 2))

        actions = ctk.CTkFrame(side, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 14))
        actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            actions,
            text="Precuenta",
            image=self._make_icon("receipt", "#F4EBD0", size=18),
            compound="left",
            fg_color="#3A2524",
            hover_color="#503231",
            text_color="#F4EBD0",
            font=("Segoe UI", 12, "bold"),
            command=lambda: None,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            actions,
            text="A Cocina",
            image=self._make_icon("send", "#2A1718", size=18),
            compound="left",
            fg_color="#F0A58E",
            hover_color="#F8B7A5",
            text_color="#2A1718",
            font=("Segoe UI", 12, "bold"),
            command=lambda: None,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ctk.CTkButton(
            actions,
            text="Cerrar Mesa & Pagar",
            image=self._make_icon("cash", "#0F2010", size=18),
            compound="left",
            fg_color="#4FA64F",
            hover_color="#66BB66",
            text_color="#0F2010",
            font=("Segoe UI", 12, "bold"),
            command=lambda: None,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        side.grid_columnconfigure(0, weight=1)
        return side

    def _show_section(self, section: str) -> None:
        self._active_section = section
        self._update_nav_state()

        if section == "logout":
            self.destroy()
            return

        if section == "orders":
            if self._section_frame is not None:
                self._section_frame.grid_remove()
            if self._center_frame is not None:
                self._center_frame.grid()
            if self._order_frame is not None:
                self._order_frame.grid()
            return

        if self._center_frame is not None:
            self._center_frame.grid_remove()
        if self._order_frame is not None:
            self._order_frame.grid_remove()

        if self._section_frame is not None:
            self._section_frame.grid()
            for child in self._section_frame.winfo_children():
                child.destroy()

            title_map = {
                "kitchen": "Vista Kitchen",
                "inventory": "Vista Inventory",
                "menu": "Vista Menu",
                "help": "Centro de Ayuda",
            }
            subtitle_map = {
                "kitchen": "Aqui se mostrara el monitoreo de cocina integrado para el mesero.",
                "inventory": "Aqui se mostraran existencias e indicadores del inventario.",
                "menu": "Aqui se mostrara la administracion visual del menu del dia.",
                "help": "Aqui se mostraran guias rapidas y atajos operativos.",
            }

            placeholder = ctk.CTkFrame(
                self._section_frame,
                fg_color="#1E1F22",
                border_color="#383B40",
                border_width=1,
                corner_radius=12,
            )
            placeholder.pack(fill="both", expand=True, padx=24, pady=24)

            ctk.CTkLabel(
                placeholder,
                text=title_map.get(section, "Modulo"),
                text_color="#F4EBD0",
                font=("Segoe UI", 34, "bold"),
            ).pack(anchor="w", padx=24, pady=(24, 8))
            ctk.CTkLabel(
                placeholder,
                text=subtitle_map.get(section, "Seccion en construccion."),
                text_color="#D7CBAE",
                font=("Segoe UI", 14),
                wraplength=780,
                justify="left",
            ).pack(anchor="w", padx=24)

    def _update_nav_state(self) -> None:
        for section, button in self._nav_buttons.items():
            is_active = section == self._active_section
            button.configure(
                fg_color="#9E1F14" if is_active else "#1A0D0C",
                hover_color="#B52619" if is_active else "#2A1A18",
            )

    def _preparation_notes_section(self, parent: tk.Misc) -> ctk.CTkFrame:
        section = ctk.CTkFrame(parent, fg_color="#241516", border_color="#4A3131", border_width=1, corner_radius=8)
        section.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(section, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        ctk.CTkLabel(header, text="Detalle de preparacion", text_color="#F4EBD0", font=("Segoe UI", 11, "bold")).pack(side="left")
        ctk.CTkLabel(
            header,
            text="Opcional",
            fg_color="#5B352E",
            text_color="#F4EBD0",
            corner_radius=8,
            font=("Segoe UI", 8, "bold"),
            padx=7,
            pady=2,
        ).pack(side="right")

        ctk.CTkLabel(
            section,
            text="Escribe aqui observaciones como: sin queso, sin cebolla, bien cocido, extra salsa.",
            text_color="#D9C8A9",
            justify="left",
            wraplength=260,
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))

        notes_box = ctk.CTkTextbox(
            section,
            height=90,
            fg_color="#161011",
            border_width=0,
            text_color="#F4EBD0",
            font=("Segoe UI", 11),
        )
        notes_box.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        notes_box.insert("1.0", "Detalle adicional del producto seleccionado...")
        notes_box.configure(state="disabled")
        return section

    def _order_item(self, parent: tk.Misc, nombre: str, cantidad: str, subtotal: str) -> ctk.CTkFrame:
        item = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(item, text=nombre, text_color="#F4EBD0", font=("Segoe UI", 15, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(item, text=subtotal, text_color="#F4EBD0", font=("Segoe UI", 15, "bold")).grid(row=0, column=1, sticky="e", padx=(10, 0))

        controls = ctk.CTkFrame(item, fg_color="transparent")
        controls.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        minus_icon = self._make_icon("minus", "#F4EBD0", size=12)
        plus_icon = self._make_icon("plus", "#F4EBD0", size=12)

        ctk.CTkButton(
            controls,
            text="",
            image=minus_icon,
            width=22,
            height=22,
            corner_radius=5,
            fg_color="#3A2524",
            hover_color="#503231",
            command=lambda: None,
        ).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(controls, text=cantidad, text_color="#F4EBD0", fg_color="#3A2524", corner_radius=5, width=24).pack(
            side="left", padx=(0, 4)
        )
        ctk.CTkButton(
            controls,
            text="",
            image=plus_icon,
            width=22,
            height=22,
            corner_radius=5,
            fg_color="#3A2524",
            hover_color="#503231",
            command=lambda: None,
        ).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(
            controls,
            text="Sin picante",
            text_color="#D9C8A9",
            font=("Segoe UI", 9, "italic"),
        ).pack(side="left", padx=(8, 0))

        item.grid_columnconfigure(0, weight=1)
        return item

    def _total_row(self, parent: tk.Misc, label: str, value: str, strong: bool = False) -> ctk.CTkFrame:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        size = 20 if strong else 13
        color = "#F4B39C" if strong else "#E5D7BC"

        ctk.CTkLabel(row, text=label, text_color="#F4EBD0", font=("Segoe UI", size, "bold" if strong else "normal")).pack(side="left")
        ctk.CTkLabel(row, text=value, text_color=color, font=("Segoe UI", size, "bold")).pack(side="right")
        return row

    def _make_icon(self, name: str, color: str, size: int = 18) -> ImageTk.PhotoImage:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        padding = max(2, size // 8)
        stroke = max(1, size // 8)

        if name == "orders":
            draw.rounded_rectangle((padding, padding, size - padding, size - padding), radius=3, outline=color, width=stroke)
            draw.line((padding * 2, padding + 3, size - padding * 2, padding + 3), fill=color, width=stroke)
            draw.line((padding * 2, size // 2, size - padding * 2, size // 2), fill=color, width=stroke)
        elif name == "kitchen":
            draw.arc((padding, padding + 1, size - padding, size - padding), start=180, end=360, fill=color, width=stroke)
            draw.line((padding + 2, size // 2, size - padding - 2, size // 2), fill=color, width=stroke)
            draw.line((size // 2, padding + 2, size // 2, padding + 6), fill=color, width=stroke)
        elif name == "inventory":
            draw.polygon(
                [(padding + 1, size // 2), (size // 2, padding + 1), (size - padding - 1, size // 2), (size // 2, size - padding - 1)],
                outline=color,
                fill=None,
            )
            draw.line((padding + 4, size // 2, size - padding - 4, size // 2), fill=color, width=stroke)
        elif name == "menu":
            for y in (padding + 2, size // 2, size - padding - 2):
                draw.line((padding, y, size - padding, y), fill=color, width=stroke)
        elif name == "help":
            draw.ellipse((padding, padding, size - padding, size - padding), outline=color, width=stroke)
            draw.line((size // 2, padding + 5, size // 2, size // 2), fill=color, width=stroke)
            draw.point((size // 2, size - padding - 4), fill=color)
        elif name == "logout":
            draw.rectangle((padding + 5, padding, size - padding - 2, size - padding), outline=color, width=stroke)
            draw.line((padding, size // 2, size - padding - 4, size // 2), fill=color, width=stroke)
            draw.polygon([(size - padding - 6, size // 2 - 4), (size - padding - 1, size // 2), (size - padding - 6, size // 2 + 4)], fill=color)
        elif name == "receipt":
            draw.rounded_rectangle((padding + 1, padding, size - padding - 1, size - padding), radius=2, outline=color, width=stroke)
            for y in range(padding + 4, size - padding - 2, 4):
                draw.line((padding + 4, y, size - padding - 4, y), fill=color, width=1)
        elif name == "send":
            draw.line((padding, size // 2, size - padding - 5, size // 2), fill=color, width=stroke)
            draw.polygon([(size - padding - 8, size // 2 - 5), (size - padding - 1, size // 2), (size - padding - 8, size // 2 + 5)], fill=color)
        elif name == "cash":
            draw.rounded_rectangle((padding, padding + 2, size - padding, size - padding - 2), radius=3, outline=color, width=stroke)
            draw.rectangle((padding + 4, padding + 5, size - padding - 4, padding + 8), fill=color)
            draw.ellipse((size // 2 - 2, size // 2 - 2, size // 2 + 2, size // 2 + 2), fill=color)
        elif name == "dish":
            draw.ellipse((padding, padding + 6, size - padding, size - padding - 1), outline=color, width=stroke)
            draw.arc((padding + 5, padding - 1, size - padding - 5, size - padding - 5), start=180, end=360, fill=color, width=stroke)
            draw.line((size // 2, padding + 2, size // 2, padding + 7), fill=color, width=stroke)
            draw.line((size // 2 - 3, padding + 4, size // 2 + 3, padding + 4), fill=color, width=stroke)
        elif name == "minus":
            draw.line((padding + 2, size // 2, size - padding - 2, size // 2), fill=color, width=stroke)
        elif name == "plus":
            draw.line((padding + 2, size // 2, size - padding - 2, size // 2), fill=color, width=stroke)
            draw.line((size // 2, padding + 2, size // 2, size - padding - 2), fill=color, width=stroke)
        else:
            draw.ellipse((padding, padding, size - padding, size - padding), outline=color, width=stroke)

        icon = ImageTk.PhotoImage(image)
        self._icon_refs.append(icon)
        return icon
