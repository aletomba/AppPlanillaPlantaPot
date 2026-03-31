import logging
import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalisisViewBase(ABC):
    """
    Clase base para BacteriologiaView y FisicoQuimicoView.
    Contiene toda la lógica compartida: treeview, botones, diálogos scrollables,
    exportar PDF, crear/editar/eliminar. Las subclases solo implementan
    los métodos abstractos con sus diferencias específicas.
    """

    # Títulos de los diálogos — sobreescribir en cada subclase
    create_dialog_title = "Crear Registro"
    edit_dialog_title = "Editar Registro"

    def __init__(self, parent, service, libro_service=None):
        self.parent = parent
        self.service = service
        self.libro_service = libro_service
        self.frame = ttk.Frame(self.parent)
        self.muestras_temp = []
        # Estado de paginación y búsqueda (usado por subclases que lo activen)
        self._current_page = 1
        self._total_pages = 1
        self._total_count = 0
        self._buscando_por_fecha = False
        self._fecha_desde = None
        self._fecha_hasta = None
        self.create_widgets()

    # ------------------------------------------------------------------ #
    # Widgets principales                                                  #
    # ------------------------------------------------------------------ #

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.treeview = ttk.Treeview(self.main_frame, show="headings")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        self.scroll_y = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.treeview.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_x = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.treeview.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.configure(xscrollcommand=self.scroll_x.set)

        self.btn_frame = ttk.Frame(self.frame)
        self.btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(self.btn_frame, text="Exportar PDF", command=self.exportar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Crear Libro", command=self.open_create_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Editar Libro", command=self.open_edit_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Eliminar Libro", command=self.delete_selected).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def _build_search_and_pagination(self, clientes=None):
        """Agrega barra de búsqueda por fecha + filtro cliente (opcional) + paginación.
        Llamar desde create_widgets() de la subclase ANTES de load_data()."""

        # ── Buscador por rango de fechas ─────────────────────────────────
        search_frame = ttk.LabelFrame(self.frame, text="Buscar por Fecha")
        # Insertar ARRIBA del main_frame
        search_frame.pack(fill=tk.X, padx=10, pady=(5, 2), before=self.main_frame)

        ttk.Label(search_frame, text="Desde:").pack(side=tk.LEFT, padx=(5, 2))
        self.entry_desde = ttk.Entry(search_frame, width=12)
        self.entry_desde.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(search_frame, text="Hasta:").pack(side=tk.LEFT, padx=(0, 2))
        self.entry_hasta = ttk.Entry(search_frame, width=12)
        self.entry_hasta.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(search_frame, text="Buscar", command=self._buscar_por_fecha).pack(side=tk.LEFT, padx=3)
        ttk.Button(search_frame, text="Limpiar", command=self._limpiar_busqueda).pack(side=tk.LEFT, padx=3)
        ttk.Label(search_frame, text="(YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=6)

        # ── Filtro por cliente (opcional) ────────────────────────────────
        self._cliente_filter_map = {"Todos": None}
        if clientes is not None:
            ttk.Label(search_frame, text="  Cliente:").pack(side=tk.LEFT, padx=(8, 2))
            self.combo_cliente_filter = ttk.Combobox(search_frame, state="readonly", width=20)
            self.combo_cliente_filter.pack(side=tk.LEFT, padx=(0, 5))
            self._load_cliente_filter(clientes)
            self.combo_cliente_filter.bind("<<ComboboxSelected>>", lambda _e: self._apply_cliente_filter())

        # ── Paginación ─────────────────────────────────────────────────
        pagination_frame = ttk.Frame(self.frame)
        pagination_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.btn_prev = ttk.Button(pagination_frame, text="◀ Anterior", command=self._prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.lbl_page = ttk.Label(pagination_frame, text="Página 1 de 1")
        self.lbl_page.pack(side=tk.LEFT, padx=10)

        self.btn_next = ttk.Button(pagination_frame, text="Siguiente ▶", command=self._next_page)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.lbl_total = ttk.Label(pagination_frame, text="")
        self.lbl_total.pack(side=tk.LEFT, padx=15)

    def _load_cliente_filter(self, clientes):
        values = ["Todos"]
        mapping = {"Todos": None}
        for c in clientes:
            label = f"{c.nombre} (ID: {c.id})"
            values.append(label)
            mapping[label] = c.id
        self._cliente_filter_map = mapping
        self.combo_cliente_filter["values"] = values
        self.combo_cliente_filter.set("Todos")

    def _apply_cliente_filter(self):
        """Subclases pueden sobrescribir para filtrar por cliente."""
        pass

    def _update_pagination_controls(self):
        if hasattr(self, "lbl_page"):
            self.lbl_page.config(text=f"Página {self._current_page} de {self._total_pages}")
            self.lbl_total.config(text=f"Total: {self._total_count} registros")
            self.btn_prev.config(state=tk.NORMAL if self._current_page > 1 else tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL if self._current_page < self._total_pages else tk.DISABLED)

    def _prev_page(self):
        if self._current_page > 1:
            if self._buscando_por_fecha:
                self._load_por_fecha(page=self._current_page - 1)
            else:
                self.load_data(page=self._current_page - 1)

    def _next_page(self):
        if self._current_page < self._total_pages:
            if self._buscando_por_fecha:
                self._load_por_fecha(page=self._current_page + 1)
            else:
                self.load_data(page=self._current_page + 1)

    def _buscar_por_fecha(self):
        desde = self.entry_desde.get().strip()
        hasta = self.entry_hasta.get().strip()
        if not desde or not hasta:
            messagebox.showwarning("Aviso", "Ingrese ambas fechas (YYYY-MM-DD).")
            return
        try:
            datetime.strptime(desde, "%Y-%m-%d")
            datetime.strptime(hasta, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
            return
        self._buscando_por_fecha = True
        self._fecha_desde = desde
        self._fecha_hasta = hasta
        self._load_por_fecha(page=1)

    def _limpiar_busqueda(self):
        self._buscando_por_fecha = False
        self._fecha_desde = None
        self._fecha_hasta = None
        self.entry_desde.delete(0, tk.END)
        self.entry_hasta.delete(0, tk.END)
        self.load_data(page=1)

    def _load_por_fecha(self, page=1):
        """Subclases que usan búsqueda por fecha deben sobrescribir este método."""
        pass

    def _set_pagination_state(self, response_dict, page):
        """Extrae el estado de paginación de una respuesta paginada."""
        self._total_count = response_dict.get("totalCount", 0)
        self._current_page = response_dict.get("page", page)
        self._total_pages = response_dict.get("totalPages", 1)
        self._update_pagination_controls()

    # ------------------------------------------------------------------ #
    # Carga y visualización de datos                                      #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def load_data(self):
        """Llama al servicio y luego llama a display_data(items, error)."""
        pass

    def display_data(self, items, error=None):
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if error or not items:
            messagebox.showerror("Error", error or "No hay datos para mostrar.")
            self.treeview["columns"] = ["Mensaje"]
            self.treeview.heading("Mensaje", text="Mensaje")
            self.treeview.column("Mensaje", width=300, anchor="center")
            self.treeview.insert("", "end", values=["No hay datos para mostrar"])
            return

        self.muestras_temp = items
        columns, headers = self.get_columns_headers()

        self.treeview["columns"] = columns
        for col in columns:
            self.treeview.heading(col, text=headers[col])
            self.treeview.column(col, anchor="w")

        for idx, obj in enumerate(items, start=1):
            try:
                vals = self.build_row_values(obj)
                self.treeview.insert("", "end", text=str(idx), values=vals, tags=(str(obj.id),))
            except Exception as e:
                logger.error("Error al insertar item %s en treeview: %s", getattr(obj, 'id', idx), e)

        tk_font = font.nametofont("TkDefaultFont")
        for col in columns:
            header_w = tk_font.measure(headers[col])
            data_ws = [tk_font.measure(str(v if v is not None else "")) for obj in items for v in [getattr(obj, col, "")]]
            max_w = max(data_ws + [header_w], default=100)
            self.treeview.column(col, width=min(max_w + 20, 300))

    @abstractmethod
    def get_columns_headers(self):
        """Retorna (columns: list[str], headers: dict[str, str])."""
        pass

    @abstractmethod
    def build_row_values(self, obj) -> list:
        """Retorna la lista de valores para una fila del treeview."""
        pass

    # ------------------------------------------------------------------ #
    # Helpers de UI compartidos                                           #
    # ------------------------------------------------------------------ #

    def _get_selected_id(self):
        """Retorna (id, None) o (None, 'error') mostrando el mensaje apropiado."""
        sel = self.treeview.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un registro.")
            return None, "no_selection"
        tags = self.treeview.item(sel[0], "tags")
        if not tags:
            messagebox.showerror("Error", "No se pudo identificar el registro seleccionado.")
            return None, "no_tags"
        try:
            return int(tags[0]), None
        except ValueError:
            messagebox.showerror("Error", "ID inválido en el registro seleccionado.")
            return None, "invalid_id"

    def _build_scrollable_dialog(self, title, geometry="480x520"):
        """Crea un Toplevel con canvas + scrollbar vertical + soporte mousewheel.
        Retorna (dlg, inner_frame)."""
        dlg = tk.Toplevel(self.parent)
        dlg.title(title)
        dlg.geometry(geometry)
        dlg.transient(self.parent)
        dlg.grab_set()

        canvas = tk.Canvas(dlg)
        v_scroll = ttk.Scrollbar(dlg, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

        return dlg, inner

    @staticmethod
    def _add_field(parent, label, default=""):
        """Agrega un Label + Entry al frame dado. Retorna el Entry."""
        ttk.Label(parent, text=label).pack(pady=3, anchor="w", padx=8)
        entry = ttk.Entry(parent)
        entry.insert(0, default)
        entry.pack(fill=tk.X, padx=8)
        return entry

    @staticmethod
    def _parse_dates(fields):
        """Parsea fecha, fecha_llegada y fecha_analisis del dict de fields.
        Lanza ValueError si el formato es inválido."""
        fecha = datetime.strptime(fields["fecha"].get().strip(), "%d/%m/%Y")
        fecha_llegada = datetime.strptime(fields["fecha_llegada"].get().strip(), "%d/%m/%Y")
        fa_str = fields["fecha_analisis"].get().strip()
        fecha_analisis = datetime.strptime(fa_str, "%d/%m/%Y") if fa_str else None
        return fecha, fecha_llegada, fecha_analisis

    def _add_base_date_fields(self, inner, fields, obj=None):
        """Agrega los campos de fecha comunes al formulario."""
        today = datetime.now().strftime("%d/%m/%Y")
        fields["fecha"] = self._add_field(inner, "Fecha (DD/MM/YYYY):",
            obj.fecha.strftime("%d/%m/%Y") if obj and obj.fecha else today)
        fields["fecha_llegada"] = self._add_field(inner, "Fecha Llegada (DD/MM/YYYY):",
            obj.fecha_llegada.strftime("%d/%m/%Y") if obj and obj.fecha_llegada else today)
        fields["fecha_analisis"] = self._add_field(inner, "Fecha Análisis (DD/MM/YYYY):",
            obj.fecha_analisis.strftime("%d/%m/%Y") if obj and obj.fecha_analisis else "")
        fields["procedencia"] = self._add_field(inner, "Procedencia:",
            obj.procedencia if obj else "")

    # ------------------------------------------------------------------ #
    # Exportar PDF                                                        #
    # ------------------------------------------------------------------ #

    def exportar_pdf(self):
        item_id, err = self._get_selected_id()
        if err:
            return

        obj = next((x for x in self.muestras_temp if x.id == item_id), None)
        if not obj:
            messagebox.showerror("Error", f"No se encontró el registro con ID {item_id}.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar reporte como PDF"
        )
        if not ruta:
            return

        try:
            libros = None
            if self.libro_service:
                libros, err_libros = self.libro_service.get_libros()
                if err_libros:
                    logger.warning("No se pudieron cargar libros para reporte: %s", err_libros)
                    libros = None
            self.do_export_pdf(obj, ruta, libros=libros)
            messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")

    @abstractmethod
    def do_export_pdf(self, obj, ruta, libros=None):
        pass

    # ------------------------------------------------------------------ #
    # Crear                                                               #
    # ------------------------------------------------------------------ #

    def open_create_dialog(self):
        dlg, inner = self._build_scrollable_dialog(self.create_dialog_title)
        fields = {}
        self._add_base_date_fields(inner, fields)
        self.build_specific_fields_create(inner, fields)

        def guardar():
            try:
                fecha, fecha_llegada, fecha_analisis = self._parse_dates(fields)
                dto = self.build_create_dto(fields, fecha, fecha_llegada, fecha_analisis)
            except Exception as e:
                messagebox.showerror("Error", f"Formato inválido: {e}")
                return
            res, err = self.do_create(dto)
            if err:
                messagebox.showerror("Error", err)
            else:
                messagebox.showinfo("Éxito", "Registro creado correctamente.")
                dlg.destroy()
                self.load_data()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="Guardar", command=guardar).pack(pady=6)

    @abstractmethod
    def build_specific_fields_create(self, inner, fields):
        """Agrega los campos específicos de la subclase al formulario de creación."""
        pass

    @abstractmethod
    def build_create_dto(self, fields, fecha, fecha_llegada, fecha_analisis):
        """Construye y retorna el DTO de creación a partir de los fields."""
        pass

    @abstractmethod
    def do_create(self, dto):
        """Llama al servicio para crear. Retorna (result, error)."""
        pass

    # ------------------------------------------------------------------ #
    # Editar                                                              #
    # ------------------------------------------------------------------ #

    def open_edit_dialog(self):
        item_id, err = self._get_selected_id()
        if err:
            return

        obj = next((x for x in self.muestras_temp if x.id == item_id), None)
        if not obj:
            messagebox.showerror("Error", f"No se encontró el registro con ID {item_id}.")
            return

        dlg, inner = self._build_scrollable_dialog(self.edit_dialog_title)
        fields = {}
        self._add_base_date_fields(inner, fields, obj)
        self.build_specific_fields_edit(inner, fields, obj)

        def guardar():
            try:
                fecha, fecha_llegada, fecha_analisis = self._parse_dates(fields)
                dto = self.build_edit_dto(fields, obj, fecha, fecha_llegada, fecha_analisis)
            except Exception as e:
                messagebox.showerror("Error", f"Formato inválido: {e}")
                return
            res, err = self.do_update(dto)
            if err:
                messagebox.showerror("Error", err)
            else:
                messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
                dlg.destroy()
                self.load_data()

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar).pack(pady=6)

    @abstractmethod
    def build_specific_fields_edit(self, inner, fields, obj):
        """Agrega los campos específicos de la subclase al formulario de edición."""
        pass

    @abstractmethod
    def build_edit_dto(self, fields, obj, fecha, fecha_llegada, fecha_analisis):
        """Construye y retorna el DTO de edición a partir de los fields."""
        pass

    @abstractmethod
    def do_update(self, dto):
        """Llama al servicio para actualizar. Retorna (result, error)."""
        pass

    # ------------------------------------------------------------------ #
    # Eliminar                                                            #
    # ------------------------------------------------------------------ #

    def delete_selected(self):
        item_id, err = self._get_selected_id()
        if err:
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar el registro ID {item_id}?"):
            return
        res, err = self.do_delete(item_id)
        if err:
            messagebox.showerror("Error", err)
        else:
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
            self.load_data()

    @abstractmethod
    def do_delete(self, item_id):
        """Llama al servicio para eliminar. Retorna (result, error)."""
        pass

    # ------------------------------------------------------------------ #
    # Show / Hide                                                         #
    # ------------------------------------------------------------------ #

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def hide(self):
        self.frame.pack_forget()
