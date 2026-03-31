import tkinter as tk
from tkinter import ttk
from libro_fisico.dto import FisicoQuimicoDto
from libro_fisico.report.fisico_quimico_report import FisicoQuimicoReport
from shared.base_analisis_view import AnalisisViewBase


class FisicoQuimicoView(AnalisisViewBase):

    create_dialog_title = "Crear Físico-Químico"
    edit_dialog_title = "Editar Físico-Químico"

    def __init__(self, parent, fq_service, libro_service=None):
        self.fq_service = fq_service
        self._clientes = []
        super().__init__(parent, fq_service, libro_service)

    # ------------------------------------------------------------------ #
    # Widgets                                                              #
    # ------------------------------------------------------------------ #

    def create_widgets(self):
        # Construir treeview, botones base
        super().create_widgets()
        # Cargar clientes para el filtro
        if self.libro_service:
            clientes, _ = self.libro_service.get_clientes()
            self._clientes = clientes or []
        # Agregar buscador + paginación encima del treeview
        self._build_search_and_pagination(clientes=self._clientes if self._clientes else None)

    # ------------------------------------------------------------------ #
    # Implementación de métodos abstractos                                #
    # ------------------------------------------------------------------ #

    def load_data(self, page=1):
        result, error = self.fq_service.get_fisicoquimicos(page=page)
        if error or result is None:
            self.display_data([], error)
            return
        items = result.get("items", [])
        self._set_pagination_state(result, page)
        self.display_data(items, None)

    def _load_por_fecha(self, page=1):
        result, error = self.fq_service.get_by_fecha_rango(
            self._fecha_desde, self._fecha_hasta, page=page)
        if error or result is None:
            self.display_data([], error)
            return
        items = result.get("items", [])
        self._set_pagination_state(result, page)
        self.display_data(items, None)

    def _apply_cliente_filter(self):
        sel = self.combo_cliente_filter.get()
        cliente_id = self._cliente_filter_map.get(sel)
        if cliente_id is None:
            self._buscando_por_fecha = False
            self.load_data(page=1)
        else:
            result, error = self.fq_service.get_by_cliente(cliente_id, page=1)
            if error or result is None:
                self.display_data([], error)
                return
            items = result.get("items", [])
            self._set_pagination_state(result, 1)
            self.display_data(items, None)

    def get_columns_headers(self):
        columns = [
            "id", "fecha", "fecha_llegada", "fecha_analisis", "procedencia",
            "ph", "turbidez", "alcalinidad", "dureza", "nitritos",
            "cloruros", "calcio", "magnesio", "dbo5", "cloro", "muestra_id",
        ]
        headers = {
            "id": "ID",
            "fecha": "Fecha Registro",
            "fecha_llegada": "Fecha Llegada",
            "fecha_analisis": "Fecha Análisis",
            "procedencia": "Procedencia",
            "ph": "pH",
            "turbidez": "Turbidez",
            "alcalinidad": "Alcalinidad",
            "dureza": "Dureza",
            "nitritos": "Nitritos",
            "cloruros": "Cloruros",
            "calcio": "Calcio",
            "magnesio": "Magnesio",
            "dbo5": "DBO5",
            "cloro": "Cloro",
            "muestra_id": "Muestra ID",
        }
        return columns, headers

    def build_row_values(self, fq):
        return [
            fq.id,
            fq.fecha.strftime("%d/%m/%Y") if fq.fecha else "",
            fq.fecha_llegada.strftime("%d/%m/%Y") if fq.fecha_llegada else "",
            fq.fecha_analisis.strftime("%d/%m/%Y") if fq.fecha_analisis else "",
            fq.procedencia or "",
            fq.ph or "",
            fq.turbidez or "",
            fq.alcalinidad or "",
            fq.dureza or "",
            fq.nitritos or "",
            fq.cloruros or "",
            fq.calcio or "",
            fq.magnesio or "",
            fq.dbo5 or "",
            fq.cloro or "",
            fq.muestra_id,
        ]

    def do_export_pdf(self, obj, ruta, libros=None):
        if libros is not None:
            FisicoQuimicoReport.exportar_con_libros([obj], libros, ruta)
        else:
            FisicoQuimicoReport.exportar([obj], ruta)

    def build_specific_fields_create(self, inner, fields):
        fields["ph"]         = self._add_field(inner, "pH:")
        fields["turbidez"]   = self._add_field(inner, "Turbidez:")
        fields["alcalinidad"] = self._add_field(inner, "Alcalinidad:")
        fields["dureza"]     = self._add_field(inner, "Dureza:")
        fields["nitritos"]   = self._add_field(inner, "Nitritos:")
        fields["cloruros"]   = self._add_field(inner, "Cloruros:")
        fields["calcio"]     = self._add_field(inner, "Calcio:")
        fields["magnesio"]   = self._add_field(inner, "Magnesio:")
        fields["dbo5"]       = self._add_field(inner, "DBO5:")
        fields["cloro"]      = self._add_field(inner, "Cloro:")
        fields["muestra_id"] = self._add_field(inner, "Muestra ID (numérico):", "0")

    def build_create_dto(self, fields, fecha, fecha_llegada, fecha_analisis):
        return FisicoQuimicoDto(
            fecha=fecha,
            fecha_llegada=fecha_llegada,
            fecha_analisis=fecha_analisis,
            procedencia=fields["procedencia"].get().strip(),
            ph=fields["ph"].get().strip(),
            turbidez=fields["turbidez"].get().strip(),
            alcalinidad=fields["alcalinidad"].get().strip(),
            dureza=fields["dureza"].get().strip(),
            nitritos=fields["nitritos"].get().strip(),
            cloruros=fields["cloruros"].get().strip(),
            calcio=fields["calcio"].get().strip(),
            magnesio=fields["magnesio"].get().strip(),
            dbo5=fields["dbo5"].get().strip(),
            cloro=fields["cloro"].get().strip(),
            muestra_id=int(fields["muestra_id"].get().strip() or 0),
        )

    def do_create(self, dto):
        return self.fq_service.create_fisicoquimico(dto)

    def build_specific_fields_edit(self, inner, fields, obj):
        fields["ph"]         = self._add_field(inner, "pH:", obj.ph or "")
        fields["turbidez"]   = self._add_field(inner, "Turbidez:", obj.turbidez or "")
        fields["alcalinidad"] = self._add_field(inner, "Alcalinidad:", obj.alcalinidad or "")
        fields["dureza"]     = self._add_field(inner, "Dureza:", obj.dureza or "")
        fields["nitritos"]   = self._add_field(inner, "Nitritos:", obj.nitritos or "")
        fields["cloruros"]   = self._add_field(inner, "Cloruros:", obj.cloruros or "")
        fields["calcio"]     = self._add_field(inner, "Calcio:", obj.calcio or "")
        fields["magnesio"]   = self._add_field(inner, "Magnesio:", obj.magnesio or "")
        fields["dbo5"]       = self._add_field(inner, "DBO5:", obj.dbo5 or "")
        fields["cloro"]      = self._add_field(inner, "Cloro:", obj.cloro or "")
        fields["muestra_id"] = self._add_field(inner, "Muestra ID (numérico):", str(obj.muestra_id or 0))

    def build_edit_dto(self, fields, obj, fecha, fecha_llegada, fecha_analisis):
        return FisicoQuimicoDto(
            id=obj.id,
            fecha=fecha,
            fecha_llegada=fecha_llegada,
            fecha_analisis=fecha_analisis,
            procedencia=fields["procedencia"].get().strip(),
            ph=fields["ph"].get().strip(),
            turbidez=fields["turbidez"].get().strip(),
            alcalinidad=fields["alcalinidad"].get().strip(),
            dureza=fields["dureza"].get().strip(),
            nitritos=fields["nitritos"].get().strip(),
            cloruros=fields["cloruros"].get().strip(),
            calcio=fields["calcio"].get().strip(),
            magnesio=fields["magnesio"].get().strip(),
            dbo5=fields["dbo5"].get().strip(),
            cloro=fields["cloro"].get().strip(),
            muestra_id=int(fields["muestra_id"].get().strip() or 0),
        )

    def do_update(self, dto):
        return self.fq_service.update_fisicoquimico(dto)

    def do_delete(self, item_id):
        return self.fq_service.delete_fisicoquimico(item_id)
