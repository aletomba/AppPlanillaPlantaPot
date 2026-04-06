from data.api_data_acces import APIDataAccess
from planilla_diaria.dto import PlanillaDiariaDto


class PlanillaDiariaService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.data_access = APIDataAccess(base_url)

    def get_planillas(self, page: int = 1, page_size: int = 30):
        data, error = self.data_access.fetch_data(
            "/PlanillaDiaria", params={"page": page, "pageSize": page_size}
        )
        if data:
            try:
                items = data.get("items", data) if isinstance(data, dict) else data
                planillas = [PlanillaDiariaDto.from_dict(i) for i in items]
                if isinstance(data, dict) and 'totalCount' in data:
                    return {
                        'items': planillas,
                        'totalCount': data.get('totalCount', len(planillas)),
                        'page': data.get('page', 1),
                        'totalPages': data.get('totalPages', 1),
                        'hasNextPage': data.get('hasNextPage', False),
                        'hasPreviousPage': data.get('hasPreviousPage', False)
                    }, None
                return {'items': planillas, 'totalCount': len(planillas), 'page': 1, 'totalPages': 1, 'hasNextPage': False, 'hasPreviousPage': False}, None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def get_by_fecha(self, fecha_str: str):
        """fecha_str: 'YYYY-MM-DD'"""
        data, error = self.data_access.fetch_data(
            "/PlanillaDiaria/por-fecha", params={"fecha": fecha_str}
        )
        if data:
            try:
                return PlanillaDiariaDto.from_dict(data), None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def get_by_fecha_rango(self, desde_str: str, hasta_str: str, page: int = 1, page_size: int = 30):
        """Busca planillas entre dos fechas ('YYYY-MM-DD')."""
        data, error = self.data_access.fetch_data(
            "/PlanillaDiaria/por-rango",
            params={"desde": desde_str, "hasta": hasta_str, "page": page, "pageSize": page_size}
        )
        if data:
            try:
                items = data.get("items", data) if isinstance(data, dict) else data
                planillas = [PlanillaDiariaDto.from_dict(i) for i in items]
                if isinstance(data, dict) and 'totalCount' in data:
                    return {
                        'items': planillas,
                        'totalCount': data.get('totalCount', len(planillas)),
                        'page': data.get('page', 1),
                        'totalPages': data.get('totalPages', 1),
                        'hasNextPage': data.get('hasNextPage', False),
                        'hasPreviousPage': data.get('hasPreviousPage', False)
                    }, None
                return planillas, None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def registrar(self, dto: PlanillaDiariaDto, cliente_id: int):
        return self.data_access.post_data(
            f"/PlanillaDiaria/registrar?clienteId={cliente_id}",
            dto.to_dict()
        )

    def actualizar(self, dto: PlanillaDiariaDto):
        return self.data_access.put_data(
            f"/PlanillaDiaria/{dto.id}", dto.to_dict()
        )

    def eliminar(self, planilla_id: int):
        return self.data_access.delete_data(f"/PlanillaDiaria/{planilla_id}")

    def get_clientes(self):
        data, error = self.data_access.fetch_data("/Cliente")
        if data:
            items = data.get("items", data) if isinstance(data, dict) else data
            return items, None
        return [], error
