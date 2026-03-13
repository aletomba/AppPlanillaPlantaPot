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

    def get_bacteriologias(self):
        data, error = self.data_access.fetch_data("/Bacteriologico")
        if data:
            try:
                # Extraer items si es respuesta paginada o envuelta
                items = data.get('items', data) if isinstance(data, dict) else data
                return [BacteriologiaDto.from_dict(item) for item in items], None
            except Exception as e:
                return [], f"Error al procesar datos: {e}"
        return [], error

    def create_bacteriologia(self, bq_dto):
        return self.data_access.post_data("/Bacteriologico", bq_dto.to_dict())

    def update_bacteriologia(self, bq_dto):
        return self.data_access.put_data(f"/Bacteriologico/{bq_dto.id}", bq_dto.to_dict())

    def delete_bacteriologia(self, bq_id):
        return self.data_access.delete_data(f"/Bacteriologico/{bq_id}")
