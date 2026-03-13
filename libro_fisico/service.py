from libro_fisico.dto import FisicoQuimicoDto
from data.api_data_acces import APIDataAccess
from tkinter.filedialog import FileDialog
from libro_fisico.report.fisico_quimico_report import FisicoQuimicoReport

class FisicoQuimicoService:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data_access = APIDataAccess(base_url)

    def get_fisicoquimicos(self):
        data, error = self.data_access.fetch_data("/FisicoQuimico")
        if data:
            try:
                # Extraer items si es respuesta paginada o envuelta
                items = data.get('items', data) if isinstance(data, dict) else data
                return [FisicoQuimicoDto.from_dict(item) for item in items], None
            except Exception as e:
                return [], f"Error al procesar datos: {e}"
        return [], error

    def create_fisicoquimico(self, fq_dto):
        return self.data_access.post_data("/FisicoQuimico", fq_dto.to_dict())

    def update_fisicoquimico(self, fq_dto):
        return self.data_access.put_data(f"/FisicoQuimico/{fq_dto.id}", fq_dto.to_dict())

    def delete_fisicoquimico(self, fq_id):
        return self.data_access.delete_data(f"/FisicoQuimico/{fq_id}")