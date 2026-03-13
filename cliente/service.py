from data.api_data_acces import APIDataAccess
from cliente.dto import ClienteDto

class ClienteService:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data_access = APIDataAccess(base_url)

    def update_base_url(self, new_url):
        """Actualiza la URL base."""
        self.base_url = new_url.rstrip("/")
        self.data_access.base_url = self.base_url

    def get_clientes(self):
        """Obtiene la lista de clientes."""
        data, error = self.data_access.fetch_data("/cliente")
        if data:
            # Extraer items si es respuesta paginada o envuelta
            items = data.get('items', data) if isinstance(data, dict) else data
            return [ClienteDto.from_dict(item) for item in items], None
        return [], error

    def create_cliente(self, cliente_dto):
        """Crea un nuevo cliente."""
        return self.data_access.post_data("/cliente/registrar", cliente_dto.to_dict())

    def update_cliente(self, cliente_dto):
        """Actualiza un cliente existente."""
        return self.data_access.put_data(f"/cliente/{cliente_dto.id}", cliente_dto.to_dict())

    def delete_cliente(self, cliente_id):
        """Elimina un cliente."""
        return self.data_access.delete_data(f"/cliente/{cliente_id}")