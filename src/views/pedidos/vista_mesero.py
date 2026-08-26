import os
import tkinter as tk
from typing import Callable

try:
    import winsound
except ImportError:  # pragma: no cover - fallback fuera de Windows
    winsound = None

import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from PIL import Image, ImageDraw, ImageTk

from src.core.event_bus import event_bus
from src.controllers.mesas.controlador_mesas import MesasController
from src.controllers.pedidos.controlador_pedido_actual import ControladorPedidoActual
from src.models.mesas.modelo_mesas import MesasModel
from src.models.pedidos.modelo_pedido_actual import ModeloPedidoActual
from src.views.mesas.vista_mesas import MesasView
from src.views.pedidos.vista_pedido_actual import VistaPedidoActual


class MeseroDesignWindow(ctk.CTkToplevel):
    """Vista de referencia del terminal de mesero (solo diseno UI)."""

    SYNC_PEDIDOS_MS = 3000

    def __init__(self, master: tk.Misc, usuario: str, mesa_actual: str = "Mesa 1") -> None:
        super().__init__(master)
        self.parent = master
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
        self._mesa_badge_label: ctk.CTkLabel | None = None
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._active_section = "orders"
        self._ticket_numero = 1
        self._ticket_label: ctk.CTkLabel | None = None
        self._pedido_items_container: ctk.CTkFrame | None = None
        self._pedido_vacio_label: ctk.CTkLabel | None = None
        self._categoria_botones: dict[str, ctk.CTkButton] = {}
        self._categoria_actual = "Comida China"
        self._pedido_actual_model: ModeloPedidoActual | None = None
        self._pedido_actual_view: VistaPedidoActual | None = None
        self._pedido_actual_controller: ControladorPedidoActual | None = None
        self._mesas_model: MesasModel | None = None
        self._mesas_view: MesasView | None = None
        self._mesas_controller: MesasController | None = None
        self._mesa_seleccionada_id: int | None = None
        self._mesas_por_id: dict[int, dict[str, object]] = {}
        self._ordenes_pendientes: list[dict[str, object]] = []
        self._ordenes_auditoria: list[dict[str, object]] = []
        self._notificacion_label: ctk.CTkLabel | None = None
        self._notificacion_after_id: str | None = None
        self._pendientes_window: ctk.CTkToplevel | None = None
        self._pendientes_list_container: ctk.CTkFrame | None = None
        self._pendientes_detail_container: ctk.CTkFrame | None = None
        self._ultimo_error_bd: str | None = None
        self._pedidos_estado_notificado: dict[int, str] = {}
        self._tickets_por_pedido: dict[int, int] = {}
        self._sync_pedidos_after_id: str | None = None
        self._evento_pedido_listo = self._on_pedido_listo_event
        self._evento_mesa_seleccionada = self._on_mesa_seleccionada_event
        event_bus.subscribe("pedido.listo", self._evento_pedido_listo)
        event_bus.subscribe("mesa.seleccionada", self._evento_mesa_seleccionada)
        self._db_config = {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "moscato_db"),
            "autocommit": False,
        }

        self._productos_por_categoria: dict[str, list[dict[str, object]]] = {}
        self._cargar_productos_catalogo()

        self._build_layout()
        self._programar_sincronizacion_pedidos()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self._center_frame = self._build_center_panel()
        self._order_frame = self._build_order_panel()
        self._section_frame = ctk.CTkFrame(self, fg_color="#141517", corner_radius=0)
        self._section_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self._section_frame.grid_remove()
        self._show_section("orders")

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
        center.grid(row=0, column=0, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(center, fg_color="#201011", corner_radius=0, height=102)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)

        ctk.CTkLabel(
            top,
            text="MOSCATO",
            text_color="#F4EBD0",
            font=("Segoe UI", 20, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(8, 0))

        ctk.CTkLabel(
            top,
            text="Plano de Mesas",
            text_color="#F4EBD0",
            font=("Segoe UI", 29, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 0))

        ctk.CTkLabel(
            top,
            text="Seleccione una mesa para iniciar o editar pedido",
            text_color="#E5D7BC",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=2, column=0, sticky="w", padx=14, pady=(1, 8))

        legend = ctk.CTkFrame(top, fg_color="transparent")
        legend.grid(row=2, column=1, sticky="e", padx=12)
        self._legend_item(legend, "#78F0A6", "LIBRE").grid(row=0, column=0, padx=8)
        self._legend_item(legend, "#FF8E7A", "OCUPADA").grid(row=0, column=1, padx=8)
        self._legend_item(legend, "#FFC94A", "ATENCION").grid(row=0, column=2, padx=8)

        mesas_wrap = ctk.CTkFrame(center, fg_color="transparent")
        mesas_wrap.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 6))
        mesas_wrap.grid_columnconfigure(0, weight=1)

        mesas_canvas = tk.Canvas(mesas_wrap, bg="#16181A", bd=0, highlightthickness=0, height=92)
        mesas_canvas.grid(row=0, column=0, sticky="ew")

        mesas_scroll = tk.Scrollbar(
            mesas_wrap,
            orient="horizontal",
            command=mesas_canvas.xview,
            troughcolor="#16181A",
            bg="#16181A",
            activebackground="#2A2324",
            width=5,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        mesas_scroll.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        mesas_canvas.configure(xscrollcommand=mesas_scroll.set)

        self._mesas_view = MesasView(mesas_canvas, columnas=10)
        mesas_canvas_window = mesas_canvas.create_window((0, 0), window=self._mesas_view.frame, anchor="nw")

        def _sync_mesas_scrollregion(_event: tk.Event | None = None) -> None:
            mesas_canvas.configure(scrollregion=mesas_canvas.bbox("all"))

        def _sync_mesas_canvas(event: tk.Event) -> None:
            mesas_canvas.itemconfigure(mesas_canvas_window, height=event.height)
            mesas_canvas.configure(scrollregion=mesas_canvas.bbox("all"))

        self._mesas_view.frame.bind("<Configure>", _sync_mesas_scrollregion)
        mesas_canvas.bind("<Configure>", _sync_mesas_canvas)
        self._inicializar_plano_mesas()
        mesas_canvas.xview_moveto(0.0)

        categorias = ctk.CTkFrame(center, fg_color="transparent")
        categorias.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 8))
        categorias.grid_columnconfigure((0, 1, 2, 3), weight=1)

        chips = ["Comida China", "Promos", "Combos", "Bebidas"]
        for idx, chip in enumerate(chips):
            boton = self._chip(
                categorias,
                chip,
                active=(chip == self._categoria_actual),
                command=lambda c=chip: self._mostrar_productos_categoria(c),
            )
            boton.grid(row=0, column=idx, sticky="ew", padx=4)
            self._categoria_botones[chip] = boton

        self._build_catalog(center)
        return center

    def _legend_item(self, parent: tk.Misc, color: str, text: str) -> ctk.CTkFrame:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(wrap, text="●", text_color=color, font=("Segoe UI", 10, "bold")).pack(side="left")
        ctk.CTkLabel(wrap, text=f" {text}", text_color="#E5D7BC", font=("Segoe UI", 9, "bold")).pack(side="left")
        return wrap

    def _mesa_card(self, parent: tk.Misc, mesa: str, estado: str, bg_card: str) -> ctk.CTkFrame:
        border = "#3A3030"
        hover_bg = "#3A3030"
        card = ctk.CTkFrame(
            parent,
            fg_color=bg_card,
            border_color=border,
            border_width=1,
            corner_radius=6,
            height=72,
            width=176,
        )
        card.pack_propagate(False)
        card.configure(cursor="hand2")

        mesa_label = ctk.CTkLabel(card, text=mesa, text_color="#F3E6CC", font=("Segoe UI", 26, "bold"))
        mesa_label.pack(anchor="w", padx=10, pady=(8, 0))

        estado_label = ctk.CTkLabel(card, text=estado, text_color="#F3E6CC", font=("Segoe UI", 11, "bold"))
        estado_label.pack(anchor="w", padx=10, pady=(1, 8))

        def _on_click(_event: tk.Event | None = None) -> None:
            self._select_mesa(mesa)

        def _on_enter(_event: tk.Event | None = None) -> None:
            card.configure(fg_color=hover_bg)

        def _on_leave(_event: tk.Event | None = None) -> None:
            card.configure(fg_color=bg_card)

        for widget in (card, mesa_label, estado_label):
            widget.bind("<Button-1>", _on_click)
            widget.bind("<Enter>", _on_enter)
            widget.bind("<Leave>", _on_leave)
        return card

    def _normalize_mesa_text(self, mesa: str) -> str:
        value = str(mesa).strip().upper()
        if value.startswith("MESA "):
            return value
        if value.startswith("M") and value[1:].isdigit():
            return f"MESA {value[1:]}"
        return value

    def _select_mesa(self, mesa: str) -> None:
        self.mesa_actual = self._normalize_mesa_text(mesa)
        if self._pedido_actual_controller is not None:
            self._pedido_actual_controller.establecer_mesa(self.mesa_actual)
        if self._mesa_badge_label is not None:
            self._mesa_badge_label.configure(text=self.mesa_actual)

    def _chip(
        self,
        parent: tk.Misc,
        text: str,
        active: bool = False,
        command: Callable[[], None] | None = None,
    ) -> ctk.CTkButton:
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
            command=command if command is not None else (lambda: None),
        )

    def _build_catalog(self, center: tk.Misc) -> None:
        list_wrap = ctk.CTkFrame(center, fg_color="#0F1012", corner_radius=8)
        list_wrap.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        list_wrap.grid_columnconfigure(0, weight=1)
        list_wrap.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(list_wrap, bg="#0F1012", bd=0, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(
            list_wrap,
            orient="vertical",
            command=canvas.yview,
            troughcolor="#0F1012",
            bg="#16181A",
            activebackground="#2A2324",
            width=5,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
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

        self._mostrar_productos_categoria(self._categoria_actual)

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

    def _mostrar_productos_categoria(self, categoria: str) -> None:
        if self._catalog_content is None:
            return

        self._categoria_actual = categoria
        self._actualizar_estilo_categorias()

        # Limpia cualquier tarjeta previa del contenedor principal del catalogo.
        for widget in self._catalog_content.winfo_children():
            widget.destroy()
        self._product_cards.clear()

        for producto in self._productos_por_categoria.get(categoria, []):
            card = self._product_card(
                self._catalog_content,
                producto["nombre"],
                f"${producto['precio']:,.0f}",
                str(producto.get("descripcion", "")),
            )
            self._enlazar_click_producto(card, producto)
            self._product_cards.append(card)

        if not self._product_cards:
            ctk.CTkLabel(
                self._catalog_content,
                text="Sin productos en esta categoria por ahora",
                text_color="#DCCAA8",
                font=("Segoe UI", 13, "bold"),
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self._layout_catalog_cards()

    def _actualizar_estilo_categorias(self) -> None:
        for nombre, boton in self._categoria_botones.items():
            boton.configure(fg_color="#8C1A11" if nombre == self._categoria_actual else "#3A2B2A")

    def _cargar_productos_catalogo(self) -> None:
        categorias = {
            "Moscato Chino - Compartir": "Combos",
            "Moscato Chino - Personal": "Comida China",
            "Moscato Broaster": "Combos",
            "Promociones": "Promos",
        }
        connection = self._connect_db()
        if connection is None:
            self._productos_por_categoria = {}
            return

        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT pr.id_producto, pr.nombre, pr.precio,
                              ca.nombre AS categoria_db, pr.descripcion
                    FROM productos pr
                    INNER JOIN categorias ca ON ca.id_categoria = pr.id_categoria
                    WHERE pr.activo = 1 AND pr.disponible = 1 AND ca.activo = 1
                    ORDER BY ca.id_categoria, pr.id_producto
                    """
                )
                productos_por_categoria: dict[str, list[dict[str, object]]] = {
                    "Comida China": [],
                    "Promos": [],
                    "Combos": [],
                    "Bebidas": [],
                }
                for producto in cursor.fetchall():
                    boton_categoria = categorias.get(str(producto["categoria_db"]))
                    if boton_categoria is not None:
                        producto["categoria_db"] = str(producto["categoria_db"])
                        producto["precio"] = float(producto["precio"])
                        productos_por_categoria[boton_categoria].append(producto)
                self._productos_por_categoria = productos_por_categoria
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            self._productos_por_categoria = {}
        finally:
            connection.close()

    def _enlazar_click_producto(self, card: ctk.CTkFrame, producto: dict[str, float | str]) -> None:
        def _on_click(_event: tk.Event | None = None) -> None:
            self.agregar_producto_a_ticket(producto)

        card.configure(cursor="hand2")
        for widget in (card, *card.winfo_children()):
            widget.bind("<Button-1>", _on_click)

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
        self._pedido_actual_model = ModeloPedidoActual()
        self._pedido_actual_view = VistaPedidoActual(
            self,
            ticket_numero=self._ticket_numero,
            mesa_texto=self._normalize_mesa_text(self.mesa_actual),
        )
        self._pedido_actual_controller = ControladorPedidoActual(
            self._pedido_actual_model,
            self._pedido_actual_view,
            on_send_to_kitchen=self._enviar_pedido_a_cocina,
            on_request_precuenta=self._on_precuenta_solicitada,
            on_close_table_paid=self._on_cerrar_mesa_y_pagar,
            on_exit=self._logout_to_login,
        )
        self._pedido_items_container = self._pedido_actual_view._items_container
        self._pedido_vacio_label = self._pedido_actual_view._empty_label
        self._ticket_label = self._pedido_actual_view._ticket_label
        return self._pedido_actual_view.frame

    def _actualizar_label_ticket(self) -> None:
        if self._ticket_label is not None:
            self._ticket_label.configure(text=f"TICKET #{self._ticket_numero:05d}")
        if self._pedido_actual_controller is not None:
            self._pedido_actual_controller.establecer_ticket(self._ticket_numero)

    def agregar_producto_a_ticket(self, producto: dict[str, float | str]) -> None:
        if self._pedido_actual_controller is None:
            return
        era_primer_item = self._pedido_actual_model is not None and not self._pedido_actual_model.tiene_items()
        nombre = str(producto.get("nombre", "Producto")).strip()
        precio = float(producto.get("precio", 0.0) or 0.0)
        categoria_db = str(producto.get("categoria_db", "Comida"))
        id_item = str(producto.get("id_producto") or f"{categoria_db}:{nombre.lower()}")
        self._pedido_actual_controller.agregar_item(
            id_item=id_item,
            nombre=nombre,
            precio=precio,
            cantidad=1,
            categoria_db=categoria_db,
        )
        if era_primer_item and self._mesa_seleccionada_id is not None and self._mesas_controller is not None:
            self._mesas_controller.registrar_primer_item(self._mesa_seleccionada_id)
        self._actualizar_label_ticket()

    def _on_precuenta_solicitada(self) -> None:
        self._abrir_ordenes_pendientes()

    def _on_cerrar_mesa_y_pagar(self) -> None:
        if self._mesa_seleccionada_id is None or self._mesas_controller is None:
            return
        self._mesas_controller.liberar_mesa(self._mesa_seleccionada_id)

    def _enviar_pedido_a_cocina(self, items: list[dict[str, object]] | None = None) -> bool:
        items_actuales = items or (self._pedido_actual_model.obtener_items() if self._pedido_actual_model is not None else [])
        if not items_actuales:
            self._mostrar_notificacion("No hay productos para enviar", "#6F2C2C")
            return False

        ticket = self._ticket_numero
        orden = {
            "ticket": ticket,
            "mesa": self._normalize_mesa_text(self.mesa_actual),
            "estado": "Enviado a cocina",
            "items": [dict(item) for item in items_actuales],
            "id_pedido": 0,
        }
        self._ordenes_pendientes.append(orden)
        id_pedido = self._guardar_orden_en_bd(orden)
        if id_pedido is None:
            detalle = f": {self._ultimo_error_bd}" if self._ultimo_error_bd else ""
            self._mostrar_notificacion(f"No se pudo enviar a cocina (BD){detalle}", "#6F2C2C")
            self._ordenes_pendientes.pop()
            return False
        orden["id_pedido"] = int(id_pedido)
        self._tickets_por_pedido[int(id_pedido)] = int(ticket)

        event_bus.emit(
            "pedido.creado",
            {
                "id_pedido": id_pedido,
                "ticket": ticket,
                "mesa": orden["mesa"],
            },
        )
        self._mostrar_notificacion(f"Ticket #{ticket:05d} enviado a cocina", "#2F5C36")

        self.after(5000, lambda t=ticket: self._marcar_orden_en_espera(t))
        self._ticket_numero += 1
        self._actualizar_label_ticket()
        self._refrescar_ventana_pendientes()
        if self._pedido_actual_controller is not None:
            self._pedido_actual_controller.limpiar()
        return True

    def _connect_db(self):
        try:
            return mysql.connector.connect(**self._db_config)
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            return None

    def _guardar_orden_en_bd(self, orden: dict[str, object]) -> int | None:
        self._ultimo_error_bd = None
        connection = self._connect_db()
        if connection is None:
            return None

        try:
            with connection.cursor(dictionary=True) as cursor:
                id_usuario = self._resolver_id_usuario(cursor)
                id_usuario = id_usuario or 1
                if id_usuario is None:
                    self._ultimo_error_bd = "Sin usuario activo para registrar pedido"
                    connection.rollback()
                    return None

                id_mesa = self._resolver_id_mesa(cursor, str(orden.get("mesa", "")))
                tipo_pedido = "Mesa" if id_mesa is not None else "Para llevar"

                cursor.execute(
                    """
                    INSERT INTO pedidos (id_mesa, id_usuario, tipo_pedido, estado_pedido)
                    VALUES (%s, %s, %s, 'En cocina')
                    """,
                    (id_mesa, id_usuario, tipo_pedido),
                )
                id_pedido = int(cursor.lastrowid)
                self._asegurar_tabla_tickets(cursor)
                cursor.execute(
                    """
                    INSERT INTO pedidos_ticket_map (id_pedido, ticket_numero)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE ticket_numero = VALUES(ticket_numero)
                    """,
                    (id_pedido, int(orden.get("ticket") or id_pedido)),
                )

                for item in list(orden.get("items", [])):
                    nombre = str(item.get("nombre", "")).strip()
                    precio = float(item.get("precio", 0.0) or 0.0)
                    cantidad = max(1, int(item.get("cantidad") or 1))
                    notas = str(item.get("notas") or "").strip() or None
                    categoria_db = str(item.get("categoria_db", "Comida"))
                    if not nombre:
                        continue

                    id_producto = self._resolver_o_crear_producto(cursor, nombre, precio, categoria_db)
                    subtotal = round(precio * cantidad, 2)
                    cursor.execute(
                        """
                        INSERT INTO detalle_pedido (
                            id_pedido,
                            id_producto,
                            cantidad,
                            descripcion_preparacion,
                            subtotal,
                            estado_item
                        )
                        VALUES (%s, %s, %s, %s, %s, 'Pendiente')
                        """,
                        (id_pedido, id_producto, cantidad, notas, subtotal),
                    )
                    item["id_detalle"] = int(cursor.lastrowid)
                    item["id_producto"] = int(id_producto)
                    item["cantidad"] = cantidad
                    item["notas"] = notas or ""

                connection.commit()
                return int(id_pedido)
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            connection.rollback()
            return None
        finally:
            connection.close()

    def _on_pedido_listo_event(self, evento: dict[str, object]) -> None:
        pedido_id = int(evento.get("id_pedido") or 0)
        if pedido_id <= 0:
            return

        estado_item = self._normalizar_estado_pendiente(str(evento.get("estado_item") or evento.get("estado_pedido") or ""))
        if self._pedidos_estado_notificado.get(pedido_id) == estado_item:
            return

        self._pedidos_estado_notificado[pedido_id] = estado_item
        orden = self._buscar_orden_por_id_pedido(pedido_id)
        if orden is not None:
            orden["estado"] = estado_item
            if estado_item == "Listo":
                self._mover_orden_a_auditoria(orden)
                self._refrescar_ventana_pendientes()
            else:
                self._refrescar_ventana_pendientes(int(orden.get("ticket") or 0))

        if estado_item == "En preparación":
            self._mostrar_notificacion(f"Cocina confirmo pedido #{pedido_id:05d}", "#8A6317")
        elif estado_item == "Listo":
            texto = self._texto_notificacion_pedido_listo(pedido_id)
            if texto is not None:
                self._mostrar_notificacion(texto, "#2F5C36")
                self._reproducir_campanita()

    def _mover_orden_a_auditoria(self, orden: dict[str, object]) -> None:
        if orden in self._ordenes_pendientes:
            self._ordenes_pendientes.remove(orden)

        # Se conserva copia para la vista de auditoría sin mostrarla en pendientes.
        snapshot = dict(orden)
        snapshot["estado"] = "Listo"
        snapshot["items"] = [dict(item) for item in list(orden.get("items", []))]
        self._ordenes_auditoria.append(snapshot)

    def _inicializar_plano_mesas(self) -> None:
        if self._mesas_view is None:
            return

        self._asegurar_mesas_base_1_a_10()
        self._mesas_model = MesasModel()
        self._mesas_controller = MesasController(self._mesas_model, self._mesas_view)
        self._mesas_view.configurar_accion_click(self._on_click_mesa_plano)

        mesas_db = self._mesas_model.obtener_mesas()
        mesas_por_numero: dict[int, dict[str, object]] = {}
        for mesa in mesas_db:
            try:
                numero = int(mesa.get("numero_mesa") or 0)
            except (TypeError, ValueError):
                continue
            if 1 <= numero <= 10:
                mesas_por_numero[numero] = mesa

        mesas_1_a_10 = [mesas_por_numero[num] for num in range(1, 11) if num in mesas_por_numero]
        if mesas_1_a_10:
            self._mesas_view.dibujar_mesas(mesas_1_a_10)

        self._mesas_por_id.clear()
        for mesa in mesas_1_a_10:
            id_mesa = int(mesa.get("id_mesa") or 0)
            if id_mesa > 0:
                self._mesas_por_id[id_mesa] = mesa

        mesa_inicial = mesas_por_numero.get(1)
        if mesa_inicial is not None:
            self._on_mesa_seleccionada_event(
                {
                    "id_mesa": mesa_inicial.get("id_mesa"),
                    "numero_mesa": mesa_inicial.get("numero_mesa"),
                }
            )

    def _asegurar_mesas_base_1_a_10(self) -> None:
        """Garantiza existencia de mesas 1..10 para mantener UX historica del mesero."""
        connection = self._connect_db()
        if connection is None:
            return

        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT numero_mesa FROM mesas WHERE numero_mesa BETWEEN 1 AND 10")
                existentes = {int(row["numero_mesa"]) for row in cursor.fetchall()}
                faltantes = [numero for numero in range(1, 11) if numero not in existentes]
                for numero in faltantes:
                    cursor.execute(
                        "INSERT INTO mesas (numero_mesa, estado, activo) VALUES (%s, 'Libre', 1)",
                        (numero,),
                    )
            connection.commit()
        except Error:
            connection.rollback()
        finally:
            connection.close()

    def _on_click_mesa_plano(self, id_mesa: int) -> None:
        self._mesa_seleccionada_id = int(id_mesa)
        if self._mesas_controller is not None:
            self._mesas_controller.seleccionar_mesa(id_mesa)

    def _on_mesa_seleccionada_event(self, evento: dict[str, object]) -> None:
        id_mesa = int(evento.get("id_mesa") or 0)
        if id_mesa <= 0:
            return
        self._mesa_seleccionada_id = id_mesa
        numero = evento.get("numero_mesa")
        if numero is None:
            mesa_cache = self._mesas_por_id.get(id_mesa, {})
            numero = mesa_cache.get("numero_mesa", id_mesa)

        self.mesa_actual = f"Mesa {numero}"
        mesa_ui = self._normalize_mesa_text(self.mesa_actual)
        if self._pedido_actual_controller is not None:
            self._pedido_actual_controller.establecer_mesa(mesa_ui)
        if self._mesa_badge_label is not None:
            self._mesa_badge_label.configure(text=mesa_ui)

    def _resolver_id_usuario(self, cursor) -> int | None:
        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios u
            INNER JOIN empleados e
                ON e.id_empleado = u.id_empleado
            WHERE TRIM(CONCAT(e.nombres, ' ', e.apellidos)) = %s
              AND u.rol IN ('Mesonero', 'Mesero')
              AND u.activo = 1
              AND e.activo = 1
            ORDER BY id_usuario ASC
            LIMIT 1
            """,
            (self.usuario,),
        )
        row = cursor.fetchone()
        if row:
            return int(row["id_usuario"])

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE username = %s AND rol IN ('Mesonero', 'Mesero') AND activo = 1
            ORDER BY id_usuario ASC
            LIMIT 1
            """,
            (self.usuario,),
        )
        username_match = cursor.fetchone()
        if username_match:
            return int(username_match["id_usuario"])

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE rol IN ('Mesonero', 'Mesero') AND activo = 1
            ORDER BY id_usuario ASC
            LIMIT 1
            """
        )
        fallback = cursor.fetchone()
        if fallback:
            return int(fallback["id_usuario"])

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE activo = 1
            ORDER BY id_usuario ASC
            LIMIT 1
            """
        )
        any_user = cursor.fetchone()
        if any_user:
            return int(any_user["id_usuario"])
        return None

    def _resolver_id_mesa(self, cursor, mesa_texto: str) -> int | None:
        numero = self._extraer_numero_mesa(mesa_texto)
        if numero is None:
            return None

        cursor.execute("SELECT id_mesa FROM mesas WHERE numero_mesa = %s LIMIT 1", (numero,))
        row = cursor.fetchone()
        if row:
            return int(row["id_mesa"])

        cursor.execute(
            "INSERT INTO mesas (numero_mesa, estado, activo) VALUES (%s, 'Libre', 1)",
            (numero,),
        )
        return int(cursor.lastrowid)

    @staticmethod
    def _extraer_numero_mesa(mesa_texto: str) -> int | None:
        digitos = "".join(ch for ch in str(mesa_texto) if ch.isdigit())
        if not digitos:
            return None
        try:
            return int(digitos)
        except ValueError:
            return None

    @staticmethod
    def _resolver_o_crear_producto(cursor, nombre: str, precio: float, categoria_db: str) -> int:
        cursor.execute(
            "SELECT id_producto FROM productos WHERE nombre = %s LIMIT 1",
            (nombre,),
        )
        row = cursor.fetchone()
        if row:
            return int(row["id_producto"])

        cursor.execute(
            """
            INSERT INTO productos (nombre, precio, id_categoria, disponible, activo)
            SELECT %s, %s, id_categoria, 1, 1
            FROM categorias
            WHERE nombre = %s
            LIMIT 1
            """,
            (nombre, precio, categoria_db),
        )
        if cursor.rowcount == 0:
            raise Error(f"No existe la categoria del producto: {categoria_db}")
        return int(cursor.lastrowid)

    def _limpiar_panel_pedido_actual(self) -> None:
        if self._pedido_actual_controller is not None:
            self._pedido_actual_controller.limpiar()

    def _marcar_orden_en_espera(self, ticket: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None or str(orden.get("estado")) != "Enviado a cocina":
            return
        orden["estado"] = "En espera"
        self._refrescar_ventana_pendientes()

    def _buscar_orden(self, ticket: int) -> dict[str, object] | None:
        for orden in self._ordenes_pendientes:
            if int(orden.get("ticket", 0)) == ticket:
                return orden
        return None

    def _buscar_orden_por_id_pedido(self, id_pedido: int) -> dict[str, object] | None:
        for orden in self._ordenes_pendientes:
            if int(orden.get("id_pedido", 0)) == int(id_pedido):
                return orden
        return None

    def _abrir_ordenes_pendientes(self) -> None:
        self._cargar_ordenes_pendientes_desde_bd()

        if self._pendientes_window is not None and self._pendientes_window.winfo_exists():
            self._pendientes_window.focus()
            self._refrescar_ventana_pendientes()
            return

        win = ctk.CTkToplevel(self)
        win.title("Ordenes Pendientes")
        win.geometry("860x520")
        win.minsize(760, 460)
        win.configure(fg_color="#141517")
        win.grid_columnconfigure(0, weight=0)
        win.grid_columnconfigure(1, weight=1)
        win.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            win,
            text="Ordenes pendientes",
            text_color="#F4EBD0",
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 8))

        lista = ctk.CTkFrame(win, fg_color="#1E1415", corner_radius=10)
        lista.grid(row=1, column=0, sticky="nsw", padx=(16, 8), pady=(0, 14))
        lista.grid_propagate(False)
        lista.configure(width=300)

        detalle = ctk.CTkFrame(win, fg_color="#1B1C1F", corner_radius=10)
        detalle.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(0, 14))

        self._pendientes_window = win
        self._pendientes_list_container = lista
        self._pendientes_detail_container = detalle
        self._refrescar_ventana_pendientes()

    def _cargar_ordenes_pendientes_desde_bd(self) -> None:
        connection = self._connect_db()
        if connection is None:
            return

        sql = """
            SELECT
                p.id_pedido,
                ptm.ticket_numero,
                CASE
                    WHEN p.id_mesa IS NULL OR p.tipo_pedido = 'Para llevar' THEN 'Para llevar'
                    ELSE CONCAT('Mesa ', m.numero_mesa)
                END AS mesa,
                dp.id_detalle,
                pr.id_producto,
                pr.nombre,
                pr.precio,
                dp.cantidad,
                dp.descripcion_preparacion,
                dp.estado_item
            FROM pedidos p
            INNER JOIN detalle_pedido dp
                ON dp.id_pedido = p.id_pedido
            INNER JOIN productos pr
                ON pr.id_producto = dp.id_producto
            LEFT JOIN mesas m
                ON m.id_mesa = p.id_mesa
            LEFT JOIN pedidos_ticket_map ptm
                ON ptm.id_pedido = p.id_pedido
            WHERE dp.estado_item IN ('Pendiente', 'En cocina', 'En preparación')
            ORDER BY p.id_pedido DESC, dp.id_detalle ASC
        """

        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                filas = cursor.fetchall()
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            return
        finally:
            connection.close()

        ticket_por_pedido = {
            int(orden.get("id_pedido") or 0): int(orden.get("ticket") or 0)
            for orden in self._ordenes_pendientes
            if int(orden.get("id_pedido") or 0) > 0
        }
        ticket_por_pedido.update({k: v for k, v in self._tickets_por_pedido.items() if k > 0 and v > 0})

        agrupadas: dict[int, dict[str, object]] = {}
        for fila in filas:
            id_pedido = int(fila.get("id_pedido") or 0)
            if id_pedido <= 0:
                continue

            orden = agrupadas.get(id_pedido)
            if orden is None:
                ticket_bd = int(fila.get("ticket_numero") or 0)
                orden = {
                    "ticket": ticket_bd or ticket_por_pedido.get(id_pedido, id_pedido),
                    "mesa": self._normalize_mesa_text(str(fila.get("mesa") or "Para llevar")),
                    "estado": "Enviado a cocina",
                    "items": [],
                    "id_pedido": id_pedido,
                }
                agrupadas[id_pedido] = orden

            item_estado = self._normalizar_estado_pendiente(str(fila.get("estado_item") or ""))
            estado_actual = self._normalizar_estado_pendiente(str(orden.get("estado") or ""))
            if item_estado == "En preparación" or (item_estado == "Enviado a cocina" and estado_actual == "En espera"):
                orden["estado"] = item_estado

            orden["items"].append(
                {
                    "id_item": str(fila.get("id_producto") or fila.get("nombre") or ""),
                    "id_detalle": int(fila.get("id_detalle") or 0),
                    "id_producto": int(fila.get("id_producto") or 0),
                    "nombre": str(fila.get("nombre") or "Producto"),
                    "precio": float(fila.get("precio") or 0.0),
                    "cantidad": max(1, int(fila.get("cantidad") or 1)),
                    "notas": str(fila.get("descripcion_preparacion") or "").strip(),
                    "categoria_db": "Comida",
                }
            )

        self._ordenes_pendientes = sorted(
            agrupadas.values(),
            key=lambda orden: int(orden.get("ticket") or 0),
            reverse=True,
        )
        for orden in self._ordenes_pendientes:
            id_pedido = int(orden.get("id_pedido") or 0)
            ticket = int(orden.get("ticket") or 0)
            if id_pedido > 0 and ticket > 0:
                self._tickets_por_pedido[id_pedido] = ticket

    def _refrescar_ventana_pendientes(self, ticket_seleccionado: int | None = None) -> None:
        if (
            self._pendientes_window is None
            or not self._pendientes_window.winfo_exists()
            or self._pendientes_list_container is None
            or self._pendientes_detail_container is None
        ):
            return

        for widget in self._pendientes_list_container.winfo_children():
            widget.destroy()
        for widget in self._pendientes_detail_container.winfo_children():
            widget.destroy()

        if not self._ordenes_pendientes:
            ctk.CTkLabel(
                self._pendientes_list_container,
                text="No hay ordenes pendientes",
                text_color="#D6C9A8",
                font=("Segoe UI", 12, "bold"),
            ).pack(anchor="w", padx=12, pady=12)
            ctk.CTkLabel(
                self._pendientes_detail_container,
                text="Selecciona un ticket para ver detalle",
                text_color="#D6C9A8",
                font=("Segoe UI", 12, "bold"),
            ).pack(anchor="w", padx=14, pady=14)
            return

        if ticket_seleccionado is None:
            ticket_seleccionado = int(self._ordenes_pendientes[0]["ticket"])

        for orden in self._ordenes_pendientes:
            ticket = int(orden["ticket"])
            texto = f"TICKET #{ticket:05d}  |  {orden['mesa']}  |  {orden['estado']}"
            ctk.CTkButton(
                self._pendientes_list_container,
                text=texto,
                anchor="w",
                fg_color="#8C1A11" if ticket == ticket_seleccionado else "#2A1B1B",
                hover_color="#A62216",
                text_color="#F4EBD0",
                font=("Segoe UI", 11, "bold"),
                command=lambda t=ticket: self._refrescar_ventana_pendientes(t),
            ).pack(fill="x", padx=10, pady=(10, 0))

        orden_activa = self._buscar_orden(ticket_seleccionado)
        if orden_activa is None:
            return

        ctk.CTkLabel(
            self._pendientes_detail_container,
            text=f"TICKET #{ticket_seleccionado:05d}",
            text_color="#F4EBD0",
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w", padx=14, pady=(14, 4))
        ctk.CTkLabel(
            self._pendientes_detail_container,
            text=f"Mesa: {orden_activa['mesa']}",
            text_color="#DCCAA8",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=14)
        ctk.CTkLabel(
            self._pendientes_detail_container,
            text=f"Estado: {orden_activa['estado']}",
            text_color="#E8A27E",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=14, pady=(4, 10))

        es_editable = self._pedido_pendiente_editable(orden_activa)
        ayuda_estado = "Editable antes de que cocina lo ponga en preparación." if es_editable else "Este pedido ya esta en preparación o listo y no se puede editar."
        ctk.CTkLabel(
            self._pendientes_detail_container,
            text=ayuda_estado,
            text_color="#D6C9A8",
            font=("Segoe UI", 10, "italic"),
        ).pack(anchor="w", padx=14, pady=(0, 10))

        ctk.CTkLabel(
            self._pendientes_detail_container,
            text="Productos",
            text_color="#F4EBD0",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=14)

        for index, item in enumerate(list(orden_activa.get("items", []))):
            item_frame = ctk.CTkFrame(self._pendientes_detail_container, fg_color="#241516", corner_radius=8)
            item_frame.pack(fill="x", padx=14, pady=(8, 0))
            item_frame.grid_columnconfigure(0, weight=1)

            cantidad = max(1, int(item.get("cantidad") or 1))
            precio = float(item.get("precio") or 0.0)
            subtotal = precio * cantidad
            ctk.CTkLabel(
                item_frame,
                text=f"{cantidad}x {item['nombre']}",
                text_color="#F4EBD0",
                font=("Segoe UI", 12, "bold"),
            ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(
                item_frame,
                text=f"${subtotal:.2f}",
                text_color="#F0A58E",
                font=("Segoe UI", 12, "bold"),
            ).grid(row=0, column=1, sticky="e", padx=10, pady=(8, 2))

            notas = str(item.get("notas") or "").strip()
            if notas:
                ctk.CTkLabel(
                    item_frame,
                    text=notas,
                    text_color="#F19B95",
                    font=("Segoe UI", 10, "italic"),
                    wraplength=360,
                    justify="left",
                ).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 4))

            item_actions = ctk.CTkFrame(item_frame, fg_color="transparent")
            item_actions.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
            item_actions.grid_columnconfigure((0, 1, 2, 3), weight=1)

            ctk.CTkButton(
                item_actions,
                text="+",
                width=34,
                height=28,
                fg_color="#4FA64F",
                hover_color="#66BB66",
                text_color="#0F2010",
                state="normal" if es_editable else "disabled",
                command=lambda t=ticket_seleccionado, i=index: self._incrementar_item_pendiente(t, i),
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkButton(
                item_actions,
                text="-",
                width=34,
                height=28,
                fg_color="#8C1A11",
                hover_color="#A1241A",
                text_color="#F4EBD0",
                state="normal" if es_editable else "disabled",
                command=lambda t=ticket_seleccionado, i=index: self._reducir_item_pendiente(t, i),
            ).grid(row=0, column=1)

            ctk.CTkButton(
                item_actions,
                text="Nota",
                height=28,
                fg_color="#3A2524",
                hover_color="#503231",
                text_color="#F4EBD0",
                state="normal" if es_editable else "disabled",
                command=lambda t=ticket_seleccionado, i=index: self._editar_nota_item_pendiente(t, i),
            ).grid(row=0, column=2, sticky="ew", padx=6)

            ctk.CTkButton(
                item_actions,
                text="Eliminar",
                height=28,
                fg_color="#5E2020",
                hover_color="#7B2A2A",
                text_color="#F4EBD0",
                state="normal" if es_editable else "disabled",
                command=lambda t=ticket_seleccionado, i=index: self._eliminar_item_pendiente(t, i),
            ).grid(row=0, column=3, sticky="e")

        acciones = ctk.CTkFrame(self._pendientes_detail_container, fg_color="transparent")
        acciones.pack(anchor="w", padx=14, pady=(14, 0))

        ctk.CTkButton(
            acciones,
            text="Editar en panel",
            fg_color="#3A2524",
            hover_color="#503231",
            text_color="#F4EBD0",
            font=("Segoe UI", 11, "bold"),
            state="normal" if es_editable else "disabled",
            command=lambda t=ticket_seleccionado: self._cargar_pedido_pendiente_en_panel(t),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            acciones,
            text="Cancelar pedido",
            fg_color="#8C1A11",
            hover_color="#A1241A",
            text_color="#F4EBD0",
            font=("Segoe UI", 11, "bold"),
            command=lambda t=ticket_seleccionado: self._cancelar_pedido_pendiente(t),
        ).pack(side="left")

    def _actualizar_estado_pedido_desde_cocina(self, ticket: int, estado: str) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None:
            return

        orden["estado"] = estado
        if estado == "Listo":
            self._mostrar_notificacion(f"Pedido listo: TICKET #{ticket:05d}", "#2F5C36")
        self._refrescar_ventana_pendientes(ticket)

    def _pedido_pendiente_editable(self, orden: dict[str, object]) -> bool:
        estado = self._normalizar_estado_pendiente(str(orden.get("estado") or ""))
        return estado not in {"En preparación", "Listo"}

    @staticmethod
    def _normalizar_estado_pendiente(estado: str) -> str:
        texto = (estado or "").strip().lower()
        if texto in {"en preparación", "en preparacion", "preparando"}:
            return "En preparación"
        if texto == "listo":
            return "Listo"
        if texto == "en espera":
            return "En espera"
        return "Enviado a cocina"

    def _incrementar_item_pendiente(self, ticket: int, item_index: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None or not self._pedido_pendiente_editable(orden):
            return
        items = list(orden.get("items", []))
        if item_index < 0 or item_index >= len(items):
            return
        item = items[item_index]
        item["cantidad"] = max(1, int(item.get("cantidad") or 1)) + 1
        if self._persistir_item_pendiente(orden, item):
            self._refrescar_ventana_pendientes(ticket)

    def _reducir_item_pendiente(self, ticket: int, item_index: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None or not self._pedido_pendiente_editable(orden):
            return
        items = list(orden.get("items", []))
        if item_index < 0 or item_index >= len(items):
            return
        item = items[item_index]
        cantidad_actual = max(1, int(item.get("cantidad") or 1))
        if cantidad_actual <= 1:
            self._eliminar_item_pendiente(ticket, item_index)
            return
        item["cantidad"] = cantidad_actual - 1
        if self._persistir_item_pendiente(orden, item):
            self._refrescar_ventana_pendientes(ticket)

    def _editar_nota_item_pendiente(self, ticket: int, item_index: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None or not self._pedido_pendiente_editable(orden):
            return
        items = list(orden.get("items", []))
        if item_index < 0 or item_index >= len(items) or self._pedido_actual_view is None:
            return
        item = items[item_index]
        nueva_nota = self._pedido_actual_view.pedir_nota(f"Nota para {item['nombre']}")
        if nueva_nota is None:
            return
        item["notas"] = nueva_nota
        if self._persistir_item_pendiente(orden, item):
            self._refrescar_ventana_pendientes(ticket)

    def _eliminar_item_pendiente(self, ticket: int, item_index: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None or not self._pedido_pendiente_editable(orden):
            return
        items = list(orden.get("items", []))
        if item_index < 0 or item_index >= len(items):
            return
        item = items[item_index]
        if not self._eliminar_item_pendiente_bd(int(item.get("id_detalle") or 0)):
            self._mostrar_notificacion("No se pudo eliminar el item del pedido", "#6F2C2C")
            return
        items.pop(item_index)
        orden["items"] = items
        if items:
            self._refrescar_ventana_pendientes(ticket)
            return
        self._retirar_orden_pendiente(orden)
        self._mostrar_notificacion(f"Pedido #{int(orden.get('id_pedido') or 0):05d} cancelado", "#8C1A11")

    def _cancelar_pedido_pendiente(self, ticket: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None:
            return
        id_pedido = int(orden.get("id_pedido") or 0)
        if id_pedido <= 0:
            return
        if not self._cancelar_pedido_pendiente_bd(id_pedido):
            self._mostrar_notificacion("No se pudo cancelar el pedido", "#6F2C2C")
            return
        self._retirar_orden_pendiente(orden)
        self._mostrar_notificacion(f"Pedido #{id_pedido:05d} cancelado", "#8C1A11")

    def _cargar_pedido_pendiente_en_panel(self, ticket: int) -> None:
        orden = self._buscar_orden(ticket)
        if orden is None or not self._pedido_pendiente_editable(orden) or self._pedido_actual_controller is None:
            return
        mesa = str(orden.get("mesa") or self._normalize_mesa_text(self.mesa_actual))
        self.mesa_actual = mesa.replace("MESA", "Mesa")
        self._pedido_actual_controller.establecer_mesa(mesa)
        self._pedido_actual_controller.limpiar()
        for item in list(orden.get("items", [])):
            self._pedido_actual_controller.agregar_item(
                id_item=str(item.get("id_item") or item.get("id_producto") or item.get("nombre") or ""),
                nombre=str(item.get("nombre") or "Producto"),
                precio=float(item.get("precio") or 0.0),
                cantidad=max(1, int(item.get("cantidad") or 1)),
                notas=str(item.get("notas") or ""),
                categoria_db=str(item.get("categoria_db") or "Comida"),
            )

    def _persistir_item_pendiente(self, orden: dict[str, object], item: dict[str, object]) -> bool:
        id_detalle = int(item.get("id_detalle") or 0)
        if id_detalle <= 0:
            self._ultimo_error_bd = "El item no tiene detalle asociado en BD"
            return False

        connection = self._connect_db()
        if connection is None:
            return False

        try:
            with connection.cursor() as cursor:
                cantidad = max(1, int(item.get("cantidad") or 1))
                precio = float(item.get("precio") or 0.0)
                subtotal = round(precio * cantidad, 2)
                notas = str(item.get("notas") or "").strip() or None
                cursor.execute(
                    """
                    UPDATE detalle_pedido
                    SET cantidad = %s,
                        descripcion_preparacion = %s,
                        subtotal = %s
                    WHERE id_detalle = %s
                    """,
                    (cantidad, notas, subtotal, id_detalle),
                )
            connection.commit()
            return True
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            connection.rollback()
            return False
        finally:
            connection.close()

    def _eliminar_item_pendiente_bd(self, id_detalle: int) -> bool:
        if id_detalle <= 0:
            return False
        connection = self._connect_db()
        if connection is None:
            return False
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM detalle_pedido WHERE id_detalle = %s", (id_detalle,))
            connection.commit()
            return True
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            connection.rollback()
            return False
        finally:
            connection.close()

    def _cancelar_pedido_pendiente_bd(self, id_pedido: int) -> bool:
        connection = self._connect_db()
        if connection is None:
            return False
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE detalle_pedido SET estado_item = 'Cancelado' WHERE id_pedido = %s",
                    (id_pedido,),
                )
                cursor.execute(
                    "UPDATE pedidos SET estado_pedido = 'Cancelado' WHERE id_pedido = %s",
                    (id_pedido,),
                )
            connection.commit()
            return True
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            connection.rollback()
            return False
        finally:
            connection.close()

    def _retirar_orden_pendiente(self, orden: dict[str, object]) -> None:
        if orden in self._ordenes_pendientes:
            self._ordenes_pendientes.remove(orden)
        ticket_restante = int(self._ordenes_pendientes[0]["ticket"]) if self._ordenes_pendientes else None
        self._refrescar_ventana_pendientes(ticket_restante)

    def _reproducir_campanita(self) -> None:
        if winsound is not None:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            self.after(140, lambda: winsound.MessageBeep(winsound.MB_ICONASTERISK))
            return
        self.bell()
        self.after(160, self.bell)

    def _programar_sincronizacion_pedidos(self) -> None:
        if not self.winfo_exists():
            return
        if self._sync_pedidos_after_id is not None:
            self.after_cancel(self._sync_pedidos_after_id)
        self._sync_pedidos_after_id = self.after(self.SYNC_PEDIDOS_MS, self._sincronizar_pedidos_desde_bd)

    def _sincronizar_pedidos_desde_bd(self) -> None:
        self._sync_pedidos_after_id = None
        if not self.winfo_exists():
            return

        anteriores = {
            int(orden.get("id_pedido") or 0): self._normalizar_estado_pendiente(str(orden.get("estado") or ""))
            for orden in self._ordenes_pendientes
            if int(orden.get("id_pedido") or 0) > 0
        }
        self._cargar_ordenes_pendientes_desde_bd()

        for orden in list(self._ordenes_pendientes):
            id_pedido = int(orden.get("id_pedido") or 0)
            estado_actual = self._normalizar_estado_pendiente(str(orden.get("estado") or ""))
            estado_previo = anteriores.get(id_pedido)
            if estado_previo is not None and estado_previo != estado_actual:
                self._on_pedido_listo_event({"id_pedido": id_pedido, "estado_item": estado_actual})

        if self._pendientes_window is not None and self._pendientes_window.winfo_exists():
            self._refrescar_ventana_pendientes()

        self._programar_sincronizacion_pedidos()

    def _texto_notificacion_pedido_listo(self, id_pedido: int) -> str | None:
        ticket = self._buscar_ticket_por_id_pedido(id_pedido)
        if ticket is not None and ticket > 0:
            return f"Pedido listo: TICKET #{ticket:05d}"
        return None

    def _buscar_ticket_por_id_pedido(self, id_pedido: int) -> int | None:
        ticket_cache = int(self._tickets_por_pedido.get(id_pedido) or 0)
        if ticket_cache > 0:
            return ticket_cache
        for orden in self._ordenes_pendientes:
            if int(orden.get("id_pedido") or 0) == id_pedido:
                ticket = int(orden.get("ticket") or 0)
                return ticket if ticket > 0 else None
        for orden in self._ordenes_auditoria:
            if int(orden.get("id_pedido") or 0) == id_pedido:
                ticket = int(orden.get("ticket") or 0)
                return ticket if ticket > 0 else None
        return self._consultar_ticket_por_id_pedido_bd(id_pedido)

    def _asegurar_tabla_tickets(self, cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pedidos_ticket_map (
                id_pedido INT PRIMARY KEY,
                ticket_numero INT NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def _consultar_ticket_por_id_pedido_bd(self, id_pedido: int) -> int | None:
        connection = self._connect_db()
        if connection is None:
            return None
        try:
            with connection.cursor(dictionary=True) as cursor:
                self._asegurar_tabla_tickets(cursor)
                cursor.execute(
                    "SELECT ticket_numero FROM pedidos_ticket_map WHERE id_pedido = %s LIMIT 1",
                    (id_pedido,),
                )
                fila = cursor.fetchone()
            ticket = int((fila or {}).get("ticket_numero") or 0)
            if ticket > 0:
                self._tickets_por_pedido[id_pedido] = ticket
                return ticket
            return None
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            return None
        finally:
            connection.close()

    def _consultar_pedidos_listos_bd(self) -> list[int]:
        connection = self._connect_db()
        if connection is None:
            return []

        sql = """
            SELECT DISTINCT p.id_pedido
            FROM pedidos p
            INNER JOIN detalle_pedido dp
                ON dp.id_pedido = p.id_pedido
            WHERE p.estado_pedido = 'Listo'
              AND dp.estado_item = 'Listo'
            ORDER BY p.id_pedido DESC
        """

        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                filas = cursor.fetchall()
            return [int(fila.get("id_pedido") or 0) for fila in filas if int(fila.get("id_pedido") or 0) > 0]
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            return []
        finally:
            connection.close()

    def _consultar_estado_pedido_bd(self, id_pedido: int) -> str | None:
        connection = self._connect_db()
        if connection is None:
            return None
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT estado_item
                    FROM detalle_pedido
                    WHERE id_pedido = %s
                      AND estado_item NOT IN ('Cancelado', 'Servido')
                    """,
                    (id_pedido,),
                )
                filas = cursor.fetchall()
            estados = {self._normalizar_estado_pendiente(str(fila.get("estado_item") or "")) for fila in filas}
            if "Listo" in estados:
                return "Listo"
            if "En preparación" in estados:
                return "En preparación"
            if filas:
                return "Enviado a cocina"
            return None
        except Error as exc:
            self._ultimo_error_bd = str(exc)
            return None
        finally:
            connection.close()

    def _mostrar_notificacion(self, texto: str, color: str = "#2F5C36") -> None:
        if self._notificacion_label is None or not self._notificacion_label.winfo_exists():
            self._notificacion_label = ctk.CTkLabel(
                self,
                text=texto,
                fg_color=color,
                text_color="#F4EBD0",
                corner_radius=10,
                font=("Segoe UI", 11, "bold"),
                padx=12,
                pady=6,
            )
        else:
            self._notificacion_label.configure(text=texto, fg_color=color)

        self._notificacion_label.place(relx=1.0, x=-18, y=18, anchor="ne")

        if self._notificacion_after_id is not None:
            self.after_cancel(self._notificacion_after_id)
        self._notificacion_after_id = self.after(3000, self._ocultar_notificacion)

    def _ocultar_notificacion(self) -> None:
        if self._notificacion_label is not None and self._notificacion_label.winfo_exists():
            self._notificacion_label.place_forget()
        self._notificacion_after_id = None

    def _show_section(self, section: str) -> None:
        self._active_section = section
        self._update_nav_state()

        if section == "logout":
            self._logout_to_login()
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

    def _logout_to_login(self) -> None:
        self._cleanup_event_listeners()
        self.destroy()
        if self.parent is not None and self.parent.winfo_exists():
            self.parent.deiconify()

    def _cleanup_event_listeners(self) -> None:
        if self._sync_pedidos_after_id is not None:
            self.after_cancel(self._sync_pedidos_after_id)
            self._sync_pedidos_after_id = None
        event_bus.unsubscribe("pedido.listo", self._evento_pedido_listo)
        event_bus.unsubscribe("mesa.seleccionada", self._evento_mesa_seleccionada)

    def destroy(self) -> None:
        self._cleanup_event_listeners()
        super().destroy()

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
