from libro_bacteriologia.dto import BacteriologiaDto
from data.api_data_acces import APIDataAccess

class BacteriologiaService:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data_access = APIDataAccess(base_url)

    def update_base_url(self, new_url):
        """Actualiza la URL base del servicio y del data_access."""
        self.base_url = new_url.rstrip("/")
        self.data_access.base_url = self.base_url

    def get_bacteriologias(self, page=1, page_size=30):
        data, error = self.data_access.fetch_data(
            "/Bacteriologico", params={"page": page, "pageSize": page_size}
        )
        if data:
            try:
                if isinstance(data, dict) and "items" in data:
                    items = [BacteriologiaDto.from_dict(item) for item in data["items"]]
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
                return {"items": [BacteriologiaDto.from_dict(i) for i in items], "totalCount": len(items), "page": 1, "pageSize": page_size, "totalPages": 1, "hasNextPage": False, "hasPreviousPage": False}, None
            except Exception as e:
                return None, f"Error al procesar datos: {e}"
        return None, error

    def get_by_fecha_rango(self, desde_str, hasta_str, page=1, page_size=30):
        data, error = self.data_access.fetch_data(
            "/Bacteriologico/por-fecha",
            params={"desde": desde_str, "hasta": hasta_str, "page": page, "pageSize": page_size}
        )
        if data:
            try:
                if isinstance(data, dict) and "items" in data:
                    items = [BacteriologiaDto.from_dict(item) for item in data["items"]]
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
            f"/Bacteriologico/por-cliente/{cliente_id}",
            params={"page": page, "pageSize": page_size}
        )
        if data:
            try:
                if isinstance(data, dict) and "items" in data:
                    items = [BacteriologiaDto.from_dict(item) for item in data["items"]]
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

    def create_bacteriologia(self, bq_dto):
        return self.data_access.post_data("/Bacteriologico", bq_dto.to_dict())

    def update_bacteriologia(self, bq_dto):
        return self.data_access.put_data(f"/Bacteriologico/{bq_dto.id}", bq_dto.to_dict())

    def delete_bacteriologia(self, bq_id):
        return self.data_access.delete_data(f"/Bacteriologico/{bq_id}")
