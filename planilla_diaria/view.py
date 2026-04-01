import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from planilla_diaria.dto import PlanillaDiariaDto, AnalisisPuntoDto, EnsayoJarrasDto

PUNTOS = ["AguaNatural", "Decantada", "Filtrada", "Consumo"]
PUNTOS_LABELS = {"AguaNatural": "Agua Natural", "Decantada": "Decantada",
                 "Filtrada": "Filtrada", "Consumo": "Consumo"}
PARAMS = [
    ("ph",         "pH"),
    ("turbidez",   "Turbidez"),
    ("alcalinidad","Alcalinidad"),
    ("dureza",     "Dureza"),
    ("nitritos",   "Nitritos"),
    ("cloruros",   "Cloruros"),
    ("calcio",     "Calcio"),
    ("magnesio",   "Magnesio"),
    ("dbo5",       "DBO5"),
    ("cloro",      "Cloro"),
]


class PlanillaDiariaView:
    def __init__(self, parent, service):
        self.parent = parent
        self.service = service
        self.frame = ttk.Frame(self.parent)
        self._buscando_por_fecha = False
        self._fecha_desde = None
        self._fecha_hasta = None
        self._current_page = 1
        self._total_pages = 1
        self._total_count = 0
        self._build()

    def _build(self):
        # ── Buscador por rango de fechas ─────────────────────────────────
        search_frame = ttk.LabelFrame(self.frame, text="Buscar por Fecha")
        search_frame.pack(fill=tk.X, padx=10, pady=(5, 2))
        ttk.Label(search_frame, text="Desde:").pack(side=tk.LEFT, padx=(5, 2))
        self.entry_desde = ttk.Entry(search_frame, width=12)
        self.entry_desde.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(search_frame, text="Hasta:").pack(side=tk.LEFT, padx=(0, 2))
        self.entry_hasta = ttk.Entry(search_frame, width=12)
        self.entry_hasta.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(search_frame, text="Buscar", command=self._buscar_por_fecha).pack(side=tk.LEFT, padx=3)
        ttk.Button(search_frame, text="Limpiar", command=self._limpiar_busqueda).pack(side=tk.LEFT, padx=3)
        ttk.Label(search_frame, text="(YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=6)

        # ── Toolbar ────────────────────────────────────────────────────────────
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(toolbar, text="Nueva Planilla",
                   command=self._open_create).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="Ver / Editar",
                   command=self._open_edit).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="Eliminar",
                   command=self._delete).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="Actualizar",
                   command=self._load).pack(side=tk.LEFT, padx=3)

        # ── Treeview lista de planillas ───────────────────────────────────────
        cols = ("id", "fecha", "operador", "observaciones")
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        for col, hdr, w in [("id", "ID", 50), ("fecha", "Fecha", 120),
                             ("operador", "Operador", 150), ("observaciones", "Observaciones", 300)]:
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w, anchor=tk.W)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Paginación ────────────────────────────────────────────────────
        pag_frame = ttk.Frame(self.frame)
        pag_frame.pack(fill=tk.X, padx=10, pady=(2, 5))
        self.btn_prev = ttk.Button(pag_frame, text="◀", width=3, command=self._prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        self.lbl_page = ttk.Label(pag_frame, text="Página 1 de 1")
        self.lbl_page.pack(side=tk.LEFT, padx=6)
        self.btn_next = ttk.Button(pag_frame, text="▶", width=3, command=self._next_page)
        self.btn_next.pack(side=tk.LEFT, padx=2)
        self.lbl_total = ttk.Label(pag_frame, text="", foreground="gray")
        self.lbl_total.pack(side=tk.LEFT, padx=10)

        self._load()

    def _load(self, page: int = 1):
        self._buscando_por_fecha = False
        self._current_page = page
        self.tree.delete(*self.tree.get_children())
        result, error = self.service.get_planillas(page=page)
        if error:
            messagebox.showerror("Error", error)
            return
        planillas = result.get('items', []) if isinstance(result, dict) else (result or [])
        self._total_pages = result.get('totalPages', 1) if isinstance(result, dict) else 1
        self._total_count = result.get('totalCount', len(planillas)) if isinstance(result, dict) else len(planillas)
        self._update_pagination()
        for p in planillas:
            self.tree.insert("", tk.END, iid=str(p.id),
                             values=(p.id, p.fecha.strftime("%Y-%m-%d"),
                                     p.operador or "", p.observaciones or ""))

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
        self._load_por_rango(page=1)

    def _limpiar_busqueda(self):
        self._buscando_por_fecha = False
        self._fecha_desde = None
        self._fecha_hasta = None
        self.entry_desde.delete(0, tk.END)
        self.entry_hasta.delete(0, tk.END)
        self._load(page=1)

    def _load_por_rango(self, page: int = 1):
        """Carga planillas en el rango de fechas almacenado en self._fecha_desde/.._hasta."""
        self._current_page = page
        result, error = self.service.get_by_fecha_rango(self._fecha_desde, self._fecha_hasta, page=page)
        if error:
            messagebox.showerror("Error", error)
            return
        planillas = result.get('items', result) if isinstance(result, dict) else (result or [])
        self._total_pages = result.get('totalPages', 1) if isinstance(result, dict) else 1
        self._total_count = result.get('totalCount', len(planillas)) if isinstance(result, dict) else len(planillas)
        self._update_pagination()
        self.tree.delete(*self.tree.get_children())
        if not planillas:
            messagebox.showinfo("Sin resultados", "No hay planillas en ese rango de fechas.")
            return
        for p in planillas:
            self.tree.insert("", tk.END, iid=str(p.id),
                             values=(p.id, p.fecha.strftime("%Y-%m-%d"),
                                     p.operador or "", p.observaciones or ""))

    def _update_pagination(self):
        self.lbl_page.config(text=f"Página {self._current_page} de {self._total_pages}")
        self.lbl_total.config(text=f"({self._total_count} registros)")
        self.btn_prev.config(state=tk.NORMAL if self._current_page > 1 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self._current_page < self._total_pages else tk.DISABLED)

    def _prev_page(self):
        if self._current_page > 1:
            if self._buscando_por_fecha:
                self._load_por_rango(page=self._current_page - 1)
            else:
                self._load(page=self._current_page - 1)

    def _next_page(self):
        if self._current_page < self._total_pages:
            if self._buscando_por_fecha:
                self._load_por_rango(page=self._current_page + 1)
            else:
                self._load(page=self._current_page + 1)

    def _selected_dto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una planilla.")
            return None
        planilla_id = int(sel[0])
        # Buscar en la lista local
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if int(vals[0]) == planilla_id:
                fecha_str = vals[1]
                # Pedimos por fecha para obtener datos completos
                dto, err = self.service.get_by_fecha(fecha_str)
                if err:
                    messagebox.showerror("Error", err)
                    return None
                return dto
        return None

    def _open_create(self):
        PlanillaDiariaForm(self.frame, self.service, on_save=self._load)

    def _open_edit(self):
        dto = self._selected_dto()
        if dto:
            PlanillaDiariaForm(self.frame, self.service, dto=dto, on_save=self._load)

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una planilla.")
            return
        planilla_id = int(sel[0])
        fecha = self.tree.item(sel[0], "values")[1]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar planilla del {fecha}?"):
            return
        data, error = self.service.eliminar(planilla_id)
        if error:
            messagebox.showerror("Error al eliminar", error)
        else:
            messagebox.showinfo("OK", "Planilla eliminada.")
            self._load()

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._load()

    def hide(self):
        self.frame.pack_forget()


# ──────────────────────────────────────────────────────────────────────────────
# Formulario (crear / editar) — grilla como la planilla física
# ──────────────────────────────────────────────────────────────────────────────

class PlanillaDiariaForm:
    def __init__(self, parent, service, dto: PlanillaDiariaDto = None, on_save=None):
        self.service = service
        self.dto = dto  # None = crear
        self.on_save = on_save
        self._editing = dto is not None

        self.win = tk.Toplevel(parent)
        self.win.title("Planilla Diaria" if not self._editing else
                       f"Editar Planilla — {dto.fecha.strftime('%Y-%m-%d')}")
        self.win.geometry("920x700")
        self.win.grab_set()

        self._build()
        if self._editing:
            self._fill(dto)

    # ── construcción ─────────────────────────────────────────────────────────

    def _build(self):
        outer = ttk.Frame(self.win)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # — Encabezado —
        hdr = ttk.LabelFrame(outer, text="Datos de la planilla")
        hdr.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(hdr, text="Fecha:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        self.ent_fecha = ttk.Entry(hdr, width=14)
        self.ent_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_fecha.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(hdr, text="Operador:").grid(row=0, column=2, sticky=tk.W, padx=6)
        self.ent_operador = ttk.Entry(hdr, width=22)
        self.ent_operador.grid(row=0, column=3, padx=6, pady=4)

        ttk.Label(hdr, text="Observaciones:").grid(row=0, column=4, sticky=tk.W, padx=6)
        self.ent_obs = ttk.Entry(hdr, width=30)
        self.ent_obs.grid(row=0, column=5, padx=6, pady=4)

        if not self._editing:
            self._load_clientes(hdr)

        # — Grilla análisis (parámetros × puntos) —
        grid_frame = ttk.LabelFrame(outer, text="Análisis Fisicoquímico por Punto de Muestreo")
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # cabecera de columnas
        ttk.Label(grid_frame, text="Parámetro", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=8, pady=4, sticky=tk.W)
        for c, punto in enumerate(PUNTOS, start=1):
            ttk.Label(grid_frame, text=PUNTOS_LABELS[punto],
                      font=("Arial", 10, "bold")).grid(row=0, column=c, padx=8, pady=4)

        # entradas por parámetro/punto
        self.entries = {}  # (punto, param) -> Entry
        for r, (param_key, param_label) in enumerate(PARAMS, start=1):
            ttk.Label(grid_frame, text=param_label).grid(
                row=r, column=0, padx=8, pady=2, sticky=tk.W)
            for c, punto in enumerate(PUNTOS, start=1):
                ent = ttk.Entry(grid_frame, width=12)
                ent.grid(row=r, column=c, padx=4, pady=2)
                self.entries[(punto, param_key)] = ent

        # — Ensayo de Jarras —
        jf = ttk.LabelFrame(outer, text="Ensayo de Jarras (mg/L)")
        jf.pack(fill=tk.X, pady=(0, 6))

        self.dosis_entries = {}
        for i, label in enumerate(["Dosis 1", "Dosis 2", "Dosis 3", "Dosis 4", "Dosis 5"], start=1):
            ttk.Label(jf, text=label).grid(row=0, column=(i - 1) * 2, padx=4, pady=4, sticky=tk.E)
            ent = ttk.Entry(jf, width=10)
            ent.grid(row=0, column=(i - 1) * 2 + 1, padx=4, pady=4)
            self.dosis_entries[f"dosis{i}"] = ent

        ttk.Label(jf, text="Dosis seleccionada:").grid(row=1, column=0, padx=4, pady=4, sticky=tk.E)
        self.ent_dosis_sel = ttk.Entry(jf, width=10)
        self.ent_dosis_sel.grid(row=1, column=1, padx=4, pady=4)

        # — Botones —
        btn_frame = ttk.Frame(outer)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Guardar", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar",
                   command=self.win.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_clientes(self, parent):
        """Muestra un combobox con los clientes cargados desde la API."""
        self._clientes = []
        self.cmb_clientes = None
        clientes, err = self.service.get_clientes()
        ttk.Label(parent, text="Cliente:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        if clientes:
            self._clientes = clientes
            nombres = [f"{c.get('id')} - {c.get('nombre','')}" for c in clientes]
            self.cmb_clientes = ttk.Combobox(parent, values=nombres, width=30, state="readonly")
            self.cmb_clientes.grid(row=1, column=1, columnspan=3, padx=6, pady=4, sticky=tk.W)
        else:
            msg = f"(Sin clientes{': ' + err if err else ''})"
            ttk.Label(parent, text=msg, foreground="red").grid(
                row=1, column=1, columnspan=3, padx=6, sticky=tk.W)

    # ── llenado ──────────────────────────────────────────────────────────────

    def _fill(self, dto: PlanillaDiariaDto):
        self.ent_fecha.delete(0, tk.END)
        self.ent_fecha.insert(0, dto.fecha.strftime("%Y-%m-%d"))
        self.ent_operador.delete(0, tk.END)
        self.ent_operador.insert(0, dto.operador or "")
        self.ent_obs.delete(0, tk.END)
        self.ent_obs.insert(0, dto.observaciones or "")

        # análisis
        for analisis in dto.analisis_por_punto:
            punto = analisis.punto_muestreo
            for param_key, _ in PARAMS:
                val = getattr(analisis, param_key, "") or ""
                ent = self.entries.get((punto, param_key))
                if ent:
                    ent.delete(0, tk.END)
                    ent.insert(0, val)

        # ensayo
        if dto.ensayo_jarras:
            e = dto.ensayo_jarras
            for i in range(1, 6):
                v = getattr(e, f"dosis{i}", None)
                ent = self.dosis_entries.get(f"dosis{i}")
                if ent and v is not None:
                    ent.delete(0, tk.END)
                    ent.insert(0, str(v))
            if e.dosis_seleccionada is not None:
                self.ent_dosis_sel.delete(0, tk.END)
                self.ent_dosis_sel.insert(0, str(e.dosis_seleccionada))

    # ── guardado ─────────────────────────────────────────────────────────────

    def _save(self):
        # Validar fecha
        fecha_str = self.ent_fecha.get().strip()
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Validación", "Fecha inválida. Use YYYY-MM-DD.")
            return

        # Armar análisis por punto
        analisis_list = []
        for punto in PUNTOS:
            a = AnalisisPuntoDto(punto_muestreo=punto)
            for param_key, _ in PARAMS:
                val = self.entries[(punto, param_key)].get().strip()
                setattr(a, param_key, val)
            analisis_list.append(a)

        # Ensayo jarras
        ensayo = EnsayoJarrasDto(
            id=self.dto.ensayo_jarras.id if (self._editing and self.dto.ensayo_jarras) else 0,
            dosis1=self.dosis_entries["dosis1"].get().strip() or None,
            dosis2=self.dosis_entries["dosis2"].get().strip() or None,
            dosis3=self.dosis_entries["dosis3"].get().strip() or None,
            dosis4=self.dosis_entries["dosis4"].get().strip() or None,
            dosis5=self.dosis_entries["dosis5"].get().strip() or None,
            dosis_seleccionada=self.ent_dosis_sel.get().strip() or None,
        )

        dto = PlanillaDiariaDto(
            id=self.dto.id if self._editing else 0,
            fecha=fecha,
            operador=self.ent_operador.get().strip(),
            observaciones=self.ent_obs.get().strip(),
            analisis_por_punto=analisis_list,
            ensayo_jarras=ensayo,
        )

        if self._editing:
            data, error = self.service.actualizar(dto)
        else:
            if not self.cmb_clientes or not self.cmb_clientes.get():
                messagebox.showwarning("Validación", "Seleccione un cliente.")
                return
            try:
                cliente_id = int(self.cmb_clientes.get().split(" - ")[0].strip())
            except ValueError:
                messagebox.showwarning("Validación", "No se pudo leer el ID del cliente seleccionado.")
                return
            data, error = self.service.registrar(dto, cliente_id)

        if error:
            messagebox.showerror("Error al guardar", error)
        else:
            messagebox.showinfo("OK", "Planilla guardada con éxito.")
            self.win.destroy()
            if self.on_save:
                self.on_save()
