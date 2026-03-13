class ClienteDto:
    def __init__(self, id=0, nombre="", email="", telefono=""):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    def to_dict(self):
        """Convierte el DTO a un diccionario para enviar a la API."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono
        }

    @staticmethod
    def from_dict(data):
        """Crea un ClienteDto desde un diccionario (respuesta JSON)."""
        return ClienteDto(
            id=data.get("id", 0),
            nombre=data.get("nombre", ""),
            email=data.get("email", ""),
            telefono=data.get("telefono", "")
        )