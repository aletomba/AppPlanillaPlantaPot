import logging
from data.api_data_acces import APIDataAccess
from libro_entrada.dto import LibroDeEntradaDto, LibroDeEntradaResponseDto
from cliente.dto import ClienteDto

logger = logging.getLogger(__name__)

class LibroDeEntradaService:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data_access = APIDataAccess(base_url)

    def update_base_url(self, new_url):
        """Actualiza la URL base."""
        self.base_url = new_url.rstrip("/")
        self.data_access.base_url = self.base_url

    def get_libros(self, params=None):
        """Obtiene la lista de libros de entrada con soporte para paginación."""
        data, error = self.data_access.fetch_data("/libroEntrada", params=params)
        logger.debug("get_libros respuesta raw: %s", data)
        if data:
            try:
                # Si es respuesta paginada, extraer items
                items = data.get('items', data) if isinstance(data, dict) else data
                libros = [LibroDeEntradaResponseDto.from_dict(item) for item in items]
                logger.debug("get_libros: %d libros recibidos", len(libros))
                
                # Si había metadata de paginación, agregarla
                if isinstance(data, dict) and 'totalCount' in data:
                    return {
                        'items': libros,
                        'totalCount': data.get('totalCount', len(libros)),
                        'page': data.get('page', 1),
                        'pageSize': data.get('pageSize', 50),
                        'totalPages': data.get('totalPages', 1),
                        'hasNextPage': data.get('hasNextPage', False),
                        'hasPreviousPage': data.get('hasPreviousPage', False)
                    }, None
                else:
                    # Sin paginación, devolver solo lista
                    return libros, None
            except Exception as e:
                logger.error("Error al convertir libros: %s", e)
                return [], f"Error al procesar datos: {e}"
        return [], error

    def create_libro(self, libro_dto):      
        return self.data_access.post_data("/libroEntrada/registrar", libro_dto.to_dict())

    def get_libro_by_id(self, libro_id):
        """Obtiene un libro de entrada por su ID."""
        data, error = self.data_access.fetch_data(f"/libroEntrada/{libro_id}")
        if error:
            return None, error
        try:
            libro = LibroDeEntradaResponseDto.from_dict(data)
            return libro, None
        except Exception as e:
            logger.error("Error al convertir libro (id=%s): %s", libro_id, e)
            return None, f"Error al procesar datos: {e}"

    def update_libro(self, libro_dto):       
        return self.data_access.put_data(f"/libroEntrada/{libro_dto.id}", libro_dto.to_dict())

    def delete_libro(self, libro_id):
        """Elimina un libro de entrada."""
        return self.data_access.delete_data(f"/libroEntrada/{libro_id}")

    def get_libro_pdf(self, libro_id):
        """Solicita al endpoint que devuelve el PDF de un libro de entrada."""
        # Se asume que el endpoint es /libroEntrada/{id}/pdf y devuelve application/pdf
        return self.data_access.get_binary(f"/libroEntrada/{libro_id}/reporte")

    def get_by_fecha_rango(self, desde_str, hasta_str, page=1, page_size=50):
        """Busca libros de entrada entre dos fechas (formato 'YYYY-MM-DD')."""
        data, error = self.data_access.fetch_data(
            "/libroEntrada/por-fecha",
            params={"desde": desde_str, "hasta": hasta_str, "page": page, "pageSize": page_size}
        )
        if data:
            try:
                items = data.get('items', data) if isinstance(data, dict) else data
                libros = [LibroDeEntradaResponseDto.from_dict(item) for item in items]
                if isinstance(data, dict) and 'totalCount' in data:
                    return {
                        'items': libros,
                        'totalCount': data.get('totalCount', len(libros)),
                        'page': data.get('page', 1),
                        'pageSize': data.get('pageSize', 50),
                        'totalPages': data.get('totalPages', 1),
                        'hasNextPage': data.get('hasNextPage', False),
                        'hasPreviousPage': data.get('hasPreviousPage', False)
                    }, None
                return libros, None
            except Exception as e:
                logger.error("Error al procesar búsqueda por fecha: %s", e)
                return [], f"Error al procesar datos: {e}"
        return [], error

    def get_clientes(self):
        """Obtiene la lista de clientes disponibles."""
        data, error = self.data_access.fetch_data("/cliente")
        if data:
            # Extraer items si es respuesta paginada
            items = data.get('items', data) if isinstance(data, dict) else data
            return [ClienteDto.from_dict(item) for item in items], None
        return [], error