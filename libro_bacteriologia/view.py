import tkinter as tk
from tkinter import ttk
from datetime import datetime
from libro_bacteriologia.dto import BacteriologiaDto
from libro_bacteriologia.report.bacteriologia_report import BacteriologiaReport
from shared.base_analisis_view import AnalisisViewBase


class BacteriologiaView(AnalisisViewBase):

    create_dialog_title = "Crear Bacteriología"
    edit_dialog_title = "Editar Bacteriología"

    def __init__(self, parent, bq_service, libro_service=None):
        self.bq_service = bq_service
        self._clientes = []
        super().__init__(parent, bq_service, libro_service)

    # ------------------------------------------------------------------ #
    # Widgets                                                              #
    # ------------------------------------------------------------------ #

    def create_widgets(self):
        super().create_widgets()
        if self.libro_service:
            clientes, _ = self.libro_service.get_clientes()
            self._clientes = clientes or []
        self._build_search_and_pagination(clientes=self._clientes if self._clientes else None)

    # ------------------------------------------------------------------ #
    # Implementación de métodos abstractos                                #
    # ------------------------------------------------------------------ #

    def load_data(self, page=1):
        result, error = self.bq_service.get_bacteriologias(page=page)
        if error or result is None:
            self.display_data([], error)
            return
        items = result.get("items", [])
        self._set_pagination_state(result, page)
        self.display_data(items, None)

    def _load_por_fecha(self, page=1):
        result, error = self.bq_service.get_by_fecha_rango(
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
            result, error = self.bq_service.get_by_cliente(cliente_id, page=1)
            if error or result is None:
                self.display_data([], error)
                return
            items = result.get("items", [])
            self._set_pagination_state(result, 1)
            self.display_data(items, None)

    def get_columns_headers(self):
        columns = [
            "fecha_llegada", "procedencia", "muestra_procedencia",
            "coliformesNmp", "coliformesFecalesNmp", "coloniasAgar", "coliFecalesUfc",
            "observaciones",
        ]
        headers = {
            "fecha_llegada": "Fecha Llegada",
            "procedencia": "Procedencia",
            "muestra_procedencia": "Proc. Muestra",
            "coliformesNmp": "Coliformes (NMP)",
            "coliformesFecalesNmp": "Coliformes Fecales (NMP)",
            "coloniasAgar": "Colonias Agar",
            "coliFecalesUfc": "Coli Fecales (UFC)",
            "observaciones": "Observaciones",
        }
        return columns, headers

    def build_row_values(self, bq):
        return [
            bq.fecha_llegada.strftime("%d/%m/%Y") if bq.fecha_llegada else "",
            bq.procedencia or "",
            bq.muestra_procedencia or "",
            bq.coliformesNmp or "",
            bq.coliformesFecalesNmp or "",
            bq.coloniasAgar or "",
            bq.coliFecalesUfc or "",
            bq.observaciones or "",
        ]

    def do_export_pdf(self, obj, ruta, libros=None):
        if libros is not None:
            BacteriologiaReport.exportar_con_libros([obj], libros, ruta)
        else:
            BacteriologiaReport.exportar([obj], ruta)

    def build_specific_fields_create(self, inner, fields):
        fields["coliformesNmp"]       = self._add_field(inner, "Coliformes (NMP):")
        fields["coliformesFecalesNmp"] = self._add_field(inner, "Coliformes Fecales (NMP):")
        fields["coloniasAgar"]        = self._add_field(inner, "Colonias Agar:")
        fields["coliFecalesUfc"]      = self._add_field(inner, "Coli Fecales (UFC):")
        fields["observaciones"]       = self._add_field(inner, "Observaciones:")
        fields["muestraId"]           = self._add_field(inner, "Muestra ID (numérico):", "0")

    def build_create_dto(self, fields, fecha, fecha_llegada, fecha_analisis):
        return BacteriologiaDto(
            fecha=fecha,
            fecha_llegada=fecha_llegada,
            fecha_analisis=fecha_analisis,
            procedencia=fields["procedencia"].get().strip(),
            coliformesNmp=fields["coliformesNmp"].get().strip(),
            coliformesFecalesNmp=fields["coliformesFecalesNmp"].get().strip(),
            coloniasAgar=fields["coloniasAgar"].get().strip(),
            coliFecalesUfc=fields["coliFecalesUfc"].get().strip(),
            observaciones=fields["observaciones"].get().strip(),
            muestraId=int(fields["muestraId"].get().strip() or 0),
        )

    def do_create(self, dto):
        return self.bq_service.create_bacteriologia(dto)

    def build_specific_fields_edit(self, inner, fields, obj):
        fields["coliformesNmp"]       = self._add_field(inner, "Coliformes (NMP):", obj.coliformesNmp or "")
        fields["coliformesFecalesNmp"] = self._add_field(inner, "Coliformes Fecales (NMP):", obj.coliformesFecalesNmp or "")
        fields["coloniasAgar"]        = self._add_field(inner, "Colonias Agar:", obj.coloniasAgar or "")
        fields["coliFecalesUfc"]      = self._add_field(inner, "Coli Fecales (UFC):", obj.coliFecalesUfc or "")
        fields["observaciones"]       = self._add_field(inner, "Observaciones:", obj.observaciones or "")
        fields["muestraId"]           = self._add_field(inner, "Muestra ID (numérico):", str(obj.muestraId or 0))

    def build_edit_dto(self, fields, obj, fecha, fecha_llegada, fecha_analisis):
        return BacteriologiaDto(
            id=obj.id,
            fecha=fecha,
            fecha_llegada=fecha_llegada,
            fecha_analisis=fecha_analisis,
            procedencia=fields["procedencia"].get().strip(),
            coliformesNmp=fields["coliformesNmp"].get().strip(),
            coliformesFecalesNmp=fields["coliformesFecalesNmp"].get().strip(),
            coloniasAgar=fields["coloniasAgar"].get().strip(),
            coliFecalesUfc=fields["coliFecalesUfc"].get().strip(),
            observaciones=fields["observaciones"].get().strip(),
            muestraId=int(fields["muestraId"].get().strip() or 0),
        )

    def do_update(self, dto):
        return self.bq_service.update_bacteriologia(dto)

    def do_delete(self, item_id):
        return self.bq_service.delete_bacteriologia(item_id)
