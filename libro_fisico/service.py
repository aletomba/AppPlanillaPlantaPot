from libro_fisico.dto import FisicoQuimicoDto
from data.api_data_acces import APIDataAccess
from tkinter.filedialog import FileDialog
from libro_fisico.report.fisico_quimico_report import FisicoQuimicoReport

class FisicoQuimicoService:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data_access = APIDataAccess(base_url)

    def get_fisicoquimicos(self, page=1, page_size=30):
        data, error = self.data_access.fetch_data(
            "/FisicoQuimico", params={"page": page, "pageSize": page_size}
        )
        if data:
            try:
                if isinstance(data, dict) and "items" in data:
                    items = [FisicoQuimicoDto.from_dict(item) for item in data["items"]]
                    return {
                        "items": items,
                        "totalCount": data.get("totalCount", len(items)),
                        "page": data.get("page", page),
                        "pageSize": data.get("pageSize", page_size),
                        "totalPages": data.get("totalPages", 1),
                        "hasNextPage": data.get("hasNextPage", False),
                        "hasPreviousPage": data.get("hasPreviousPage", False),
                    }, None
                items = data if isinstance(data, list) else []
                return {"items": [FisicoQuimicoDto.from_dict(i) for i in items], "totalCount": len(items), "page": 1, "pageSize": page_size, "totalPages": 1, "hasNextPage": False, "hasPreviousPage": False}, None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def get_by_fecha_rango(self, desde_str, hasta_str, page=1, page_size=30):
        data, error = self.data_access.fetch_data(
            "/FisicoQuimico/por-fecha",
            params={"desde": desde_str, "hasta": hasta_str, "page": page, "pageSize": page_size}
        )
        if data:
            try:
                if isinstance(data, dict) and "items" in data:
                    items = [FisicoQuimicoDto.from_dict(item) for item in data["items"]]
                    return {
                        "items": items,
                        "totalCount": data.get("totalCount", len(items)),
                        "page": data.get("page", page),
                        "pageSize": data.get("pageSize", page_size),
                        "totalPages": data.get("totalPages", 1),
                        "hasNextPage": data.get("hasNextPage", False),
                        "hasPreviousPage": data.get("hasPreviousPage", False),
                    }, None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def get_by_cliente(self, cliente_id, page=1, page_size=30):
        data, error = self.data_access.fetch_data(
            f"/FisicoQuimico/por-cliente/{cliente_id}",
            params={"page": page, "pageSize": page_size}
        )
        if data:
            try:
                if isinstance(data, dict) and "items" in data:
                    items = [FisicoQuimicoDto.from_dict(item) for item in data["items"]]
                    return {
                        "items": items,
                        "totalCount": data.get("totalCount", len(items)),
                        "page": data.get("page", page),
                        "pageSize": data.get("pageSize", page_size),
                        "totalPages": data.get("totalPages", 1),
                        "hasNextPage": data.get("hasNextPage", False),
                        "hasPreviousPage": data.get("hasPreviousPage", False),
                    }, None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def create_fisicoquimico(self, fq_dto):
        return self.data_access.post_data("/FisicoQuimico", fq_dto.to_dict())

    def update_fisicoquimico(self, fq_dto):
        return self.data_access.put_data(f"/FisicoQuimico/{fq_dto.id}", fq_dto.to_dict())

    def delete_fisicoquimico(self, fq_id):
        return self.data_access.delete_data(f"/FisicoQuimico/{fq_id}")