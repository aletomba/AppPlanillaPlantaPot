import logging
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font

logger = logging.getLogger(__name__)
import os
import tempfile
import webbrowser
from datetime import datetime, time
from libro_entrada.dto import LibroDeEntradaDto, MuestraDto, TipoDeMuestraDto

class LibroDeEntradaView:
    def __init__(self, parent, libro_service):
        self.parent = parent
        self.libro_service = libro_service
        self.frame = ttk.Frame(self.parent)
        self.clientes = []
        self.muestras_temp = []
        self._libros_all = []
        self._cliente_filter_map = {"Todos": None}
        self._current_page = 1
        self._total_pages = 1
        self._total_count = 0
        self._buscando_por_fecha = False
        self._fecha_desde = None
        self._fecha_hasta = None
        self.create_widgets()

    def create_widgets(self):
        # ── Buscador por rango de fechas ─────────────────────────────────────
        self.search_frame = ttk.LabelFrame(self.frame, text="Buscar por Fecha")
        self.search_frame.pack(fill=tk.X, padx=10, pady=(5, 2))
        ttk.Label(self.search_frame, text="Desde:").pack(side=tk.LEFT, padx=(5, 2))
        self.entry_desde = ttk.Entry(self.search_frame, width=12)
        self.entry_desde.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(self.search_frame, text="Hasta:").pack(side=tk.LEFT, padx=(0, 2))
        self.entry_hasta = ttk.Entry(self.search_frame, width=12)
        self.entry_hasta.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(self.search_frame, text="Buscar", command=self._buscar_por_fecha).pack(side=tk.LEFT, padx=3)
        ttk.Button(self.search_frame, text="Limpiar", command=self._limpiar_busqueda).pack(side=tk.LEFT, padx=3)
        ttk.Label(self.search_frame, text="(YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=6)

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

        ttk.Label(self.btn_frame, text="Cliente:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_cliente_filter = ttk.Combobox(self.btn_frame, state="readonly")
        self.combo_cliente_filter.pack(side=tk.LEFT, padx=5)
        self.combo_cliente_filter.bind("<<ComboboxSelected>>", lambda _e: self.apply_cliente_filter())

        self.btn_crear = ttk.Button(self.btn_frame, text="Crear Libro", command=self.open_create_dialog)
        self.btn_crear.pack(side=tk.LEFT, padx=5)

        self.btn_editar = ttk.Button(self.btn_frame, text="Editar Libro", command=self.open_edit_dialog)
        self.btn_editar.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar = ttk.Button(self.btn_frame, text="Eliminar Libro", command=self.delete_libro)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)

        self.btn_pdf = ttk.Button(self.btn_frame, text="Descargar PDF", command=self.download_pdf)
        self.btn_pdf.pack(side=tk.LEFT, padx=5)

        # Barra de paginación
        self.pagination_frame = ttk.Frame(self.frame)
        self.pagination_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.btn_prev = ttk.Button(self.pagination_frame, text="◀ Anterior", command=self._prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.lbl_page = ttk.Label(self.pagination_frame, text="Página 1 de 1")
        self.lbl_page.pack(side=tk.LEFT, padx=10)

        self.btn_next = ttk.Button(self.pagination_frame, text="Siguiente ▶", command=self._next_page)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.lbl_total = ttk.Label(self.pagination_frame, text="")
        self.lbl_total.pack(side=tk.LEFT, padx=15)

        self.load_clientes_for_filter()
        self.load_libros()

    def load_clientes_for_filter(self):
        previous_selection = self.combo_cliente_filter.get() if hasattr(self, "combo_cliente_filter") else ""
        clientes, error = self.libro_service.get_clientes()
        if error:
            # No bloquear la vista si falla el fetch; simplemente dejar "Todos"
            logger.warning("No se pudieron cargar clientes para filtro: %s", error)
            self._cliente_filter_map = {"Todos": None}
            self.combo_cliente_filter["values"] = ["Todos"]
            self.combo_cliente_filter.set("Todos")
            return

        self.clientes = clientes
        values = ["Todos"]
        mapping = {"Todos": None}
        for c in clientes:
            label = f"{c.nombre} (ID: {c.id})"
            values.append(label)
            mapping[label] = c.id

        self._cliente_filter_map = mapping
        self.combo_cliente_filter["values"] = values

        # Mantener selección previa si sigue existiendo
        if previous_selection and previous_selection in mapping:
            self.combo_cliente_filter.set(previous_selection)
        else:
            self.combo_cliente_filter.set("Todos")

    def load_libros(self, page=1):
        """Carga libros de entrada con paginación (50 por página)."""
        params = {'page': page, 'pageSize': 50}
        libros_response, error = self.libro_service.get_libros(params=params)
        
        if error:
            self._libros_all = []
            self.display_data([], error)
            return

        # Extraer items de respuesta paginada
        if isinstance(libros_response, dict) and 'items' in libros_response:
            self._libros_all = libros_response['items']
            self._total_count = libros_response.get('totalCount', 0)
            self._current_page = libros_response.get('page', 1)
            self._total_pages = libros_response.get('totalPages', 1)
        else:
            self._libros_all = libros_response or []
            self._total_count = len(self._libros_all)
            self._current_page = 1
            self._total_pages = 1
        
        self.apply_cliente_filter()
        self._update_pagination_controls()

    def _update_pagination_controls(self):
        self.lbl_page.config(text=f"Página {self._current_page} de {self._total_pages}")
        self.lbl_total.config(text=f"Total: {self._total_count} registros")
        self.btn_prev.config(state=tk.NORMAL if self._current_page > 1 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self._current_page < self._total_pages else tk.DISABLED)

    def _prev_page(self):
        if self._current_page > 1:
            if self._buscando_por_fecha:
                self._load_por_fecha(page=self._current_page - 1)
            else:
                self.load_libros(page=self._current_page - 1)

    def _next_page(self):
        if self._current_page < self._total_pages:
            if self._buscando_por_fecha:
                self._load_por_fecha(page=self._current_page + 1)
            else:
                self.load_libros(page=self._current_page + 1)

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
        self.load_libros(page=1)

    def _load_por_fecha(self, page=1):
        result, error = self.libro_service.get_by_fecha_rango(
            self._fecha_desde, self._fecha_hasta, page=page, page_size=50)
        if error:
            self._libros_all = []
            self.display_data([], error)
            return
        if isinstance(result, dict) and 'items' in result:
            self._libros_all = result['items']
            self._total_count = result.get('totalCount', 0)
            self._current_page = result.get('page', 1)
            self._total_pages = result.get('totalPages', 1)
        else:
            self._libros_all = result or []
            self._total_count = len(self._libros_all)
            self._current_page = 1
            self._total_pages = 1
        self.apply_cliente_filter()
        self._update_pagination_controls()

    def apply_cliente_filter(self):
        selected = (self.combo_cliente_filter.get() or "Todos")
        cliente_id = self._cliente_filter_map.get(selected)

        if not cliente_id:
            self.display_data(self._libros_all, None)
            return

        filtrados = []
        for libro in self._libros_all:
            try:
                if any(getattr(m, "cliente_id", None) == cliente_id for m in (libro.muestras or [])):
                    filtrados.append(libro)
            except Exception:
                continue

        self.display_data(filtrados, None)

    def display_data(self, libros, error=None):
        logger.debug("display_data: mostrando %d libros", len(libros))
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        if error or not libros:
            messagebox.showerror("Error", error or "No hay datos para mostrar.")
            self.treeview["columns"] = ["Mensaje"]
            self.treeview.heading("Mensaje", text="Mensaje")
            self.treeview.column("Mensaje", width=200, anchor="center")
            self.treeview.insert("", "end", values=["No hay datos para mostrar"])
            return

        columns = ["id", "fecha_registro", "fecha_llegada", "fecha_analisis", "procedencia", "observaciones", "muestras"]
        column_headers = {
            "id": "ID",
            "fecha_registro": "Fecha Registro",
            "fecha_llegada": "Fecha Llegada",
            "fecha_analisis": "Fecha Análisis",
            "procedencia": "Procedencia",
            "observaciones": "Observaciones",
            "muestras": "Muestras"
        }
        self.treeview["columns"] = columns
        for col in columns:
            self.treeview.heading(col, text=column_headers[col])
            self.treeview.column(col, width=100, anchor="w")

        for i, libro in enumerate(libros):
            try:
                # Texto que irá en la columna 'muestras' para la fila padre (resumen)
                muestras_summary = (
                    ", ".join(
                        f"{m.nombre_muestreador} ({TipoDeMuestraDto.to_string(m.tipo_muestra)})" for m in libro.muestras
                    ) if libro.muestras else ""
                )

                values = [
                    libro.id,
                    libro.fecha_registro.strftime("%d/%m/%Y") if libro.fecha_registro else "",
                    libro.fecha_llegada.strftime("%d/%m/%Y") if libro.fecha_llegada else "",
                    libro.fecha_analisis.strftime("%d/%m/%Y") if libro.fecha_analisis else "",
                    libro.procedencia or "",
                    libro.observaciones or "",
                    muestras_summary
                ]

                parent_iid = self.treeview.insert("", "end", text=str(i + 1), values=values, tags=(libro.id,))

                # Insertar filas hijas por cada muestra con sus detalles
                if libro.muestras:
                    for m in libro.muestras:
                        child_text = f"ID {getattr(m, 'id', '')} - {m.nombre_muestreador} ({TipoDeMuestraDto.to_string(m.tipo_muestra)}) | Lat:{m.latitud} Lon:{m.longitud} Fecha:{getattr(m, 'fecha_extraccion', '')} Hora:{getattr(m, 'hora_extraccion', '')} Sitio:{getattr(m, 'sitio_extraccion', '')}"
                        # Dejar las columnas del libro en blanco y poner la descripción en la columna 'muestras'
                        child_vals = [""] * (len(columns) - 1) + [child_text]
                        self.treeview.insert(parent_iid, "end", values=child_vals)
            except Exception as e:
                try:
                    logger.error("Error al insertar libro %s en treeview: %s", libro.id, e)
                except Exception:
                    logger.error("Error al insertar libro en índice %d en treeview: %s", i, e)

        # Ajustar anchos de columnas teniendo en cuenta el contenido de filas padre e hijas
        tk_font = font.nametofont("TkDefaultFont")
        for col in columns:
            header_width = tk_font.measure(column_headers[col])
            data_widths = []
            for libro in libros:
                if col != "muestras":
                    val = getattr(libro, col, "")
                    data_widths.append(tk_font.measure(str(val)))
                else:
                    # medir resumen y también cada muestra detallada
                    resumen = (
                        ", ".join(
                            f"{m.nombre_muestreador} ({TipoDeMuestraDto.to_string(m.tipo_muestra)})" for m in libro.muestras
                        ) if libro.muestras else ""
                    )
                    data_widths.append(tk_font.measure(str(resumen)))
                    for m in libro.muestras:
                        child_text = f"ID {getattr(m, 'id', '')} - {m.nombre_muestreador} ({TipoDeMuestraDto.to_string(m.tipo_muestra)}) | Lat:{m.latitud} Lon:{m.longitud} Fecha:{getattr(m, 'fecha_extraccion', '')} Hora:{getattr(m, 'hora_extraccion', '')}"
                        data_widths.append(tk_font.measure(child_text))

            max_width = max(data_widths + [header_width], default=100)
            self.treeview.column(col, width=min(max_width + 20, 600))

    def open_create_dialog(self):
        self.clientes, error = self.libro_service.get_clientes()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {error}")
            return

        self.muestras_temp = []
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Crear Libro de Entrada")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        ttk.Label(self.dialog, text="Cliente:").pack(pady=5)
        self.combo_cliente = ttk.Combobox(self.dialog, values=[f"{c.nombre} (ID: {c.id})" for c in self.clientes])
        self.combo_cliente.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Observaciones:").pack(pady=5)
        self.entry_observaciones = ttk.Entry(self.dialog)
        self.entry_observaciones.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Fecha Llegada (DD/MM/YYYY):").pack(pady=5)
        self.entry_fecha_llegada = ttk.Entry(self.dialog)
        self.entry_fecha_llegada.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha_llegada.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Fecha (DD/MM/YYYY):").pack(pady=5)
        self.entry_fecha = ttk.Entry(self.dialog)
        self.entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Fecha Análisis (DD/MM/YYYY, opcional):").pack(pady=5)
        self.entry_fecha_analisis = ttk.Entry(self.dialog)
        self.entry_fecha_analisis.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Procedencia:").pack(pady=5)
        self.entry_procedencia = ttk.Entry(self.dialog)
        self.entry_procedencia.pack(pady=5, fill=tk.X, padx=10)

        # Sitio Extracción ahora se ingresa por cada Muestra en su diálogo

        ttk.Label(self.dialog, text="Muestras:").pack(pady=5)
        self.muestras_listbox = tk.Listbox(self.dialog, height=5)
        self.muestras_listbox.pack(pady=5, fill=tk.X, padx=10)
        ttk.Button(self.dialog, text="Añadir Muestra", command=self.open_muestra_dialog).pack(pady=5)

        ttk.Button(self.dialog, text="Guardar", command=self.save_new_libro).pack(pady=10)

    def open_muestra_dialog(self):
        muestra_dialog = tk.Toplevel(self.dialog)
        muestra_dialog.title("Añadir Muestra")
        muestra_dialog.geometry("400x500")
        muestra_dialog.transient(self.dialog)
        muestra_dialog.grab_set()

        ttk.Label(muestra_dialog, text="Nombre Muestreador:").pack(pady=5)
        entry_nombre_muestreador = ttk.Entry(muestra_dialog)
        entry_nombre_muestreador.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Latitud (-90 a 90):").pack(pady=5)
        entry_latitud = ttk.Entry(muestra_dialog)
        entry_latitud.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Longitud (-180 a 180):").pack(pady=5)
        entry_longitud = ttk.Entry(muestra_dialog)
        entry_longitud.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Fecha Extracción (DD/MM/YYYY):").pack(pady=5)
        entry_fecha_extraccion = ttk.Entry(muestra_dialog)
        entry_fecha_extraccion.insert(0, datetime.now().strftime("%d/%m/%Y"))
        entry_fecha_extraccion.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Hora Extracción (HH:MM):").pack(pady=5)
        entry_hora_extraccion = ttk.Entry(muestra_dialog)
        entry_hora_extraccion.insert(0, "00:00")
        entry_hora_extraccion.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Tipo de Muestra:").pack(pady=5)
        combo_tipo_muestra = ttk.Combobox(muestra_dialog, values=["Bacteriologica", "FisicoQuimica"])
        combo_tipo_muestra.set("Bacteriologica")
        combo_tipo_muestra.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Sitio Extracción:").pack(pady=5)
        entry_sitio = ttk.Entry(muestra_dialog)
        entry_sitio.pack(pady=5, fill=tk.X, padx=10)

        def save_muestra():
            try:
                latitud = float(entry_latitud.get())
                longitud = float(entry_longitud.get())
                if not (-90 <= latitud <= 90):
                    raise ValueError("Latitud debe estar entre -90 y 90.")
                if not (-180 <= longitud <= 180):
                    raise ValueError("Longitud debe estar entre -180 y 180.")
                fecha_extraccion = datetime.strptime(entry_fecha_extraccion.get(), "%d/%m/%Y")
                hora_extraccion = datetime.strptime(entry_hora_extraccion.get(), "%H:%M").time()
                nombre_muestreador = entry_nombre_muestreador.get().strip()
                if not nombre_muestreador:
                    raise ValueError("El nombre del muestreador es obligatorio.")
            except ValueError as e:
                messagebox.showerror("Error", f"Formato inválido: {e}")
                return

            sitio_extraccion = entry_sitio.get().strip()
            muestra = MuestraDto(
                cliente_id=0,  # Se asignará después
                nombre_muestreador=nombre_muestreador,
                latitud=latitud,
                longitud=longitud,
                sitio_extraccion=sitio_extraccion,
                fecha_extraccion=fecha_extraccion,
                hora_extraccion=hora_extraccion,
                tipo_muestra=TipoDeMuestraDto.from_string(combo_tipo_muestra.get())
            )
            self.muestras_temp.append(muestra)
            self.muestras_listbox.insert(tk.END, f"{muestra.nombre_muestreador} ({TipoDeMuestraDto.to_string(muestra.tipo_muestra)})")
            muestra_dialog.destroy()

        ttk.Button(muestra_dialog, text="Guardar Muestra", command=save_muestra).pack(pady=10)

        # Esperar al cierre del sub-diálogo y restaurar el grab en el diálogo padre
        muestra_dialog.wait_window(muestra_dialog)
        if self.dialog.winfo_exists():
            self.dialog.grab_set()

    def save_new_libro(self):
        if not self.combo_cliente.get():
            messagebox.showerror("Error", "Seleccione un cliente.")
            return

        try:
            cliente_id = int(self.combo_cliente.get().split("ID: ")[-1].rstrip(")"))
            fecha_llegada = datetime.strptime(self.entry_fecha_llegada.get(), "%d/%m/%Y")
            fecha = datetime.strptime(self.entry_fecha.get(), "%d/%m/%Y")
            fecha_analisis_str = self.entry_fecha_analisis.get().strip()
            fecha_analisis = datetime.strptime(fecha_analisis_str, "%d/%m/%Y") if fecha_analisis_str else None
            procedencia = self.entry_procedencia.get().strip()
            observaciones = self.entry_observaciones.get().strip()
            if not procedencia:
                raise ValueError("Procedencia es obligatoria.")
        except ValueError as e:
            messagebox.showerror("Error", f"Formato inválido: {e}")
            return

        if not self.muestras_temp:
            messagebox.showerror("Error", "Debe añadir al menos una muestra.")
            return

        for muestra in self.muestras_temp:
            muestra.cliente_id = cliente_id
            # Cada muestra debe incluir la procedencia requerida por la API
            muestra.procedencia = procedencia

        libro_dto = LibroDeEntradaDto(
            observaciones=observaciones,
            fecha_llegada=fecha_llegada,
            fecha=fecha,
            fecha_analisis=fecha_analisis,
            procedencia=procedencia,
            muestras=self.muestras_temp
        )

        result, error = self.libro_service.create_libro(libro_dto)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Éxito", "Libro de entrada creado correctamente.")
            self.dialog.destroy()
            self.load_libros()

    def open_edit_dialog(self):
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un libro para editar.")
            return

        item = self.treeview.item(selected_item[0])
        libro_id = item["tags"][0]
        values = item["values"]

        self.clientes, error = self.libro_service.get_clientes()
        if error:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {error}")
            return

        libro, error = self.libro_service.get_libro_by_id(libro_id)
        if error:
            messagebox.showerror("Error", f"No se pudo cargar el libro: {error}")
            return
        if not libro:
            messagebox.showerror("Error", "No se encontró el libro.")
            return

        self.muestras_temp = [MuestraDto(
            id=getattr(m, "id", 0),  # <-- Mantén el id si existe
            cliente_id=m.cliente_id,
            procedencia=getattr(m, "procedencia", ""),
            nombre_muestreador=m.nombre_muestreador,
            sitio_extraccion=getattr(m, "sitio_extraccion", ""),
            latitud=m.latitud,
            longitud=m.longitud,
            fecha_extraccion=m.fecha_extraccion,
            hora_extraccion=m.hora_extraccion,
            tipo_muestra=m.tipo_muestra
        ) for m in libro.muestras]

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Editar Libro de Entrada")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        ttk.Label(self.dialog, text="Cliente:").pack(pady=5)
        self.combo_cliente = ttk.Combobox(self.dialog, values=[f"{c.nombre} (ID: {c.id})" for c in self.clientes])
        cliente = next((c for c in self.clientes if c.id == libro.muestras[0].cliente_id), None) if libro.muestras else None
        if cliente:
            self.combo_cliente.set(f"{cliente.nombre} (ID: {cliente.id})")
        self.combo_cliente.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Observaciones:").pack(pady=5)
        self.entry_observaciones = ttk.Entry(self.dialog)
        self.entry_observaciones.insert(0, values[5])
        self.entry_observaciones.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Fecha Llegada (DD/MM/YYYY):").pack(pady=5)
        self.entry_fecha_llegada = ttk.Entry(self.dialog)
        self.entry_fecha_llegada.insert(0, values[2])
        self.entry_fecha_llegada.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Fecha (DD/MM/YYYY):").pack(pady=5)
        self.entry_fecha = ttk.Entry(self.dialog)
        self.entry_fecha.insert(0, values[1])
        self.entry_fecha.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Fecha Análisis (DD/MM/YYYY, opcional):").pack(pady=5)
        self.entry_fecha_analisis = ttk.Entry(self.dialog)
        self.entry_fecha_analisis.insert(0, values[3])
        self.entry_fecha_analisis.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self.dialog, text="Procedencia:").pack(pady=5)
        self.entry_procedencia = ttk.Entry(self.dialog)
        self.entry_procedencia.insert(0, values[4])
        self.entry_procedencia.pack(pady=5, fill=tk.X, padx=10)

        # Sitio de extracción ahora se captura por muestra en su diálogo

        ttk.Label(self.dialog, text="Muestras:").pack(pady=5)
        self.muestras_listbox = tk.Listbox(self.dialog, height=5)
        for muestra in self.muestras_temp:
            self.muestras_listbox.insert(tk.END, f"{muestra.nombre_muestreador} ({TipoDeMuestraDto.to_string(muestra.tipo_muestra)})")
        self.muestras_listbox.pack(pady=5, fill=tk.X, padx=10)

        btns_frame = ttk.Frame(self.dialog)
        btns_frame.pack(pady=5)
        ttk.Button(btns_frame, text="Añadir Muestra", command=self.open_muestra_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns_frame, text="Editar Muestra", command=self.edit_selected_muestra).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns_frame, text="Eliminar Muestra", command=self.delete_selected_muestra).pack(side=tk.LEFT, padx=2)

        ttk.Button(self.dialog, text="Guardar", command=lambda: self.save_edited_libro(libro_id)).pack(pady=10)

    def save_edited_libro(self, libro_id):
        if not self.combo_cliente.get():
            messagebox.showerror("Error", "Seleccione un cliente.")
            return

        try:
            cliente_id = int(self.combo_cliente.get().split("ID: ")[-1].rstrip(")"))
            fecha_llegada = datetime.strptime(self.entry_fecha_llegada.get(), "%d/%m/%Y")
            fecha = datetime.strptime(self.entry_fecha.get(), "%d/%m/%Y")
            fecha_analisis_str = self.entry_fecha_analisis.get().strip()
            fecha_analisis = datetime.strptime(fecha_analisis_str, "%d/%m/%Y") if fecha_analisis_str else None
            procedencia = self.entry_procedencia.get().strip()
            observaciones = self.entry_observaciones.get().strip()
            if not procedencia:
                raise ValueError("Procedencia es obligatoria.")
        except ValueError as e:
            messagebox.showerror("Error", f"Formato inválido: {e}")
            return

        if not self.muestras_temp:
            messagebox.showerror("Error", "Debe añadir al menos una muestra.")
            return

        for muestra in self.muestras_temp:
            muestra.cliente_id = cliente_id
            # Cada muestra debe incluir la procedencia requerida por la API
            muestra.procedencia = procedencia

        libro_dto = LibroDeEntradaDto(
            id=libro_id,
            observaciones=observaciones,
            fecha_llegada=fecha_llegada,
            fecha=fecha,
            fecha_analisis=fecha_analisis,
            procedencia=procedencia,
            muestras=self.muestras_temp
        )

        result, error = self.libro_service.update_libro(libro_dto)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Éxito", "Libro de entrada actualizado correctamente.")
            self.dialog.destroy()
            self.load_libros()

    def delete_libro(self):
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un libro para eliminar.")
            return

        item = self.treeview.item(selected_item[0])
        libro_id = item["tags"][0]
        libro_procedencia = item["values"][4]

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el libro de procedencia {libro_procedencia}?"):
            return

        result, error = self.libro_service.delete_libro(libro_id)
        if error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showinfo("Éxito", "Libro de entrada eliminado correctamente.")
            self.load_libros()

    def download_pdf(self):
        selection = self.treeview.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un libro para descargar el PDF.")
            return

        item = self.treeview.item(selection[0])
        libro_id = item["tags"][0]

        data, error = self.libro_service.get_libro_pdf(libro_id)
        if error or not data:
            messagebox.showerror("Error", error or "No se recibió PDF del servidor.")
            return

        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(data)
            tmp.close()
            if os.name == "nt":
                os.startfile(tmp.name)
            else:
                webbrowser.open(tmp.name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar/abrir el PDF: {e}")

    def edit_selected_muestra(self):
        selection = self.muestras_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una muestra para editar.")
            return
        idx = selection[0]
        muestra = self.muestras_temp[idx]

        # Abre un diálogo similar a open_muestra_dialog pero con los datos precargados
        muestra_dialog = tk.Toplevel(self.dialog)
        muestra_dialog.title("Editar Muestra")
        muestra_dialog.geometry("400x500")
        muestra_dialog.transient(self.dialog)
        muestra_dialog.grab_set()

        ttk.Label(muestra_dialog, text="Nombre Muestreador:").pack(pady=5)
        entry_nombre_muestreador = ttk.Entry(muestra_dialog)
        entry_nombre_muestreador.insert(0, muestra.nombre_muestreador)
        entry_nombre_muestreador.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Latitud (-90 a 90):").pack(pady=5)
        entry_latitud = ttk.Entry(muestra_dialog)
        entry_latitud.insert(0, str(muestra.latitud))
        entry_latitud.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Longitud (-180 a 180):").pack(pady=5)
        entry_longitud = ttk.Entry(muestra_dialog)
        entry_longitud.insert(0, str(muestra.longitud))
        entry_longitud.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Fecha Extracción (DD/MM/YYYY):").pack(pady=5)
        entry_fecha_extraccion = ttk.Entry(muestra_dialog)
        entry_fecha_extraccion.insert(0, muestra.fecha_extraccion.strftime("%d/%m/%Y"))
        entry_fecha_extraccion.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Hora Extracción (HH:MM):").pack(pady=5)
        entry_hora_extraccion = ttk.Entry(muestra_dialog)
        entry_hora_extraccion.insert(0, muestra.hora_extraccion.strftime("%H:%M"))
        entry_hora_extraccion.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Tipo de Muestra:").pack(pady=5)
        combo_tipo_muestra = ttk.Combobox(muestra_dialog, values=["Bacteriologica", "FisicoQuimica"])
        combo_tipo_muestra.set(TipoDeMuestraDto.to_string(muestra.tipo_muestra))
        combo_tipo_muestra.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(muestra_dialog, text="Sitio Extracción:").pack(pady=5)
        entry_sitio = ttk.Entry(muestra_dialog)
        entry_sitio.insert(0, getattr(muestra, 'sitio_extraccion', ''))
        entry_sitio.pack(pady=5, fill=tk.X, padx=10)

        def save_edit():
            try:
                latitud = float(entry_latitud.get())
                longitud = float(entry_longitud.get())
                if not (-90 <= latitud <= 90):
                    raise ValueError("Latitud debe estar entre -90 y 90.")
                if not (-180 <= longitud <= 180):
                    raise ValueError("Longitud debe estar entre -180 y 180.")
                fecha_extraccion = datetime.strptime(entry_fecha_extraccion.get(), "%d/%m/%Y")
                hora_extraccion = datetime.strptime(entry_hora_extraccion.get(), "%H:%M").time()
                nombre_muestreador = entry_nombre_muestreador.get().strip()
                if not nombre_muestreador:
                    raise ValueError("El nombre del muestreador es obligatorio.")
            except ValueError as e:
                messagebox.showerror("Error", f"Formato inválido: {e}")
                return

            # Actualiza la muestra en la lista temporal
            sitio_extraccion = entry_sitio.get().strip()
            self.muestras_temp[idx] = MuestraDto(
                id=getattr(muestra, "id", 0),  # <-- Mantén el id original
                cliente_id=muestra.cliente_id,
                nombre_muestreador=nombre_muestreador,
                latitud=latitud,
                longitud=longitud,
                sitio_extraccion=sitio_extraccion,
                fecha_extraccion=fecha_extraccion,
                hora_extraccion=hora_extraccion,
                tipo_muestra=TipoDeMuestraDto.from_string(combo_tipo_muestra.get())
            )
            # Actualiza el Listbox
            self.muestras_listbox.delete(idx)
            self.muestras_listbox.insert(idx, f"{nombre_muestreador} ({combo_tipo_muestra.get()})")
            muestra_dialog.destroy()

        ttk.Button(muestra_dialog, text="Guardar Cambios", command=save_edit).pack(pady=10)

        # Esperar al cierre del sub-diálogo y restaurar el grab en el diálogo padre
        muestra_dialog.wait_window(muestra_dialog)
        if self.dialog.winfo_exists():
            self.dialog.grab_set()

    def delete_selected_muestra(self):
        selection = self.muestras_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una muestra para eliminar.")
            return
        idx = selection[0]
        del self.muestras_temp[idx]
        self.muestras_listbox.delete(idx)

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        # Refrescar clientes para que el combobox incluya nuevos registros
        self.load_clientes_for_filter()
        self.load_libros()

    def hide(self):
        self.frame.pack_forget()