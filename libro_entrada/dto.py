import logging
from datetime import datetime, time
from typing import List, Optional

logger = logging.getLogger(__name__)

class TipoDeMuestraDto:
    BACTERIOLOGICA = 0
    FISICO_QUIMICA = 1

    @staticmethod
    def to_string(value: int) -> str:
        """Convierte el valor entero a string para la UI."""
        return "Bacteriologica" if value == 0 else "FisicoQuimica"

    @staticmethod
    def from_string(value: str) -> int:
        """Convierte el string de la UI a entero para la API."""
        return 0 if value == "Bacteriologica" else 1

class MuestraDto:
    def __init__(
        self,
        id: int = 0,  # <-- AGREGADO
        procedencia: str = "",
        cliente_id: int = 0,
        nombre_muestreador: str = "",
        latitud: float = 0.0,
        longitud: float = 0.0,
        sitio_extraccion: str = "",
        fecha_extraccion: Optional[datetime] = None,
        hora_extraccion: Optional[time] = None,
        tipo_muestra: int = TipoDeMuestraDto.BACTERIOLOGICA
    ):
        self.id = id  # <-- AGREGADO
        self.cliente_id = cliente_id
        self.sitio_extraccion = sitio_extraccion
        self.procedencia = procedencia
        self.nombre_muestreador = nombre_muestreador
        self.latitud = latitud
        self.longitud = longitud
        self.fecha_extraccion = fecha_extraccion or datetime.now()
        self.hora_extraccion = hora_extraccion or time(0, 0)
        self.tipo_muestra = tipo_muestra

    def to_dict(self):
        """Convierte a JSON para la API, con ticks para horaExtraccion."""
        ticks = (self.hora_extraccion.hour * 3600 + self.hora_extraccion.minute * 60 + self.hora_extraccion.second) * 10_000_000
        result = {
            "clienteId": self.cliente_id,
            "sitioExtraccion": self.sitio_extraccion,
            "procedencia": self.sitio_extraccion,
            "nombreMuestreador": self.nombre_muestreador,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "fechaExtraccion": self.fecha_extraccion.isoformat(),
            "horaExtraccion": self.hora_extraccion.strftime("%H:%M:%S"),
            "tipoMuestra": int(self.tipo_muestra)
        }
        # Solo incluir id si es diferente de 0 (para UPDATE)
        if self.id != 0:
            result["id"] = self.id
        return result

    @staticmethod
    def from_dict(data):
        """Convierte desde JSON, manejando horaExtraccion como string."""
        try:
            hora_extraccion = datetime.strptime(data["horaExtraccion"], "%H:%M:%S").time() if data.get("horaExtraccion") else time(0, 0)
            tipo_muestra_raw = data.get("tipoMuestra", TipoDeMuestraDto.BACTERIOLOGICA)
            tipo_muestra = TipoDeMuestraDto.from_string(tipo_muestra_raw) if isinstance(tipo_muestra_raw, str) else int(tipo_muestra_raw)
            return MuestraDto(
                id=data.get("id", 0),
                cliente_id=data.get("clienteId", 0),
                procedencia=data.get("procedencia", ""),
                nombre_muestreador=data.get("nombreMuestreador", ""),
                latitud=data.get("latitud", 0.0),
                longitud=data.get("longitud", 0.0),
                sitio_extraccion=data.get("sitioExtraccion", ""),
                fecha_extraccion=datetime.fromisoformat(data["fechaExtraccion"].replace("Z", "+00:00")) if data.get("fechaExtraccion") else datetime.now(),
                hora_extraccion=hora_extraccion,
                tipo_muestra=tipo_muestra
            )
        except Exception as e:
            logger.error("Error en MuestraDto.from_dict: %s, datos: %s", e, data)
            return MuestraDto()


class MuestraResponseDto:
    def __init__(
        self,
        id: int = 0,
        procedencia: str = "",
        nombre_muestreador: str = "",
        sitio_extraccion: str = "",
        latitud: float = 0.0,
        longitud: float = 0.0,
        fecha_extraccion: Optional[datetime] = None,
        hora_extraccion: Optional[time] = None,
        tipo_muestra: int = TipoDeMuestraDto.BACTERIOLOGICA,
        cliente_id: int = 0,
        cliente_nombre: str = "",
        libro_entrada_id: int = 0
    ):
        self.id = id
        self.procedencia = sitio_extraccion
        self.sitio_extraccion = sitio_extraccion
        self.nombre_muestreador = nombre_muestreador
        self.latitud = latitud
        self.longitud = longitud
        self.fecha_extraccion = fecha_extraccion or datetime.now()
        self.hora_extraccion = hora_extraccion or time(0, 0)
        self.tipo_muestra = tipo_muestra
        self.cliente_id = cliente_id
        self.cliente_nombre = cliente_nombre
        self.libro_entrada_id = libro_entrada_id

    @staticmethod
    def from_dict(data):
        try:
            hora_extraccion = datetime.strptime(data["horaExtraccion"], "%H:%M:%S").time() if data.get("horaExtraccion") else time(0, 0)
            tipo_muestra_raw = data.get("tipoMuestra", TipoDeMuestraDto.BACTERIOLOGICA)
            tipo_muestra = TipoDeMuestraDto.from_string(tipo_muestra_raw) if isinstance(tipo_muestra_raw, str) else int(tipo_muestra_raw)
            return MuestraResponseDto(
                id=data.get("id", 0),
                procedencia=data.get("sitioExtraccion", ""),
                nombre_muestreador=data.get("nombreMuestreador", ""),
                sitio_extraccion=data.get("sitioExtraccion", ""),
                latitud=data.get("latitud", 0.0),
                longitud=data.get("longitud", 0.0),
                fecha_extraccion=datetime.fromisoformat(data["fechaExtraccion"].replace("Z", "+00:00")) if data.get("fechaExtraccion") else datetime.now(),
                hora_extraccion=hora_extraccion,
                tipo_muestra=tipo_muestra,
                cliente_id=data.get("clienteId", 0),
                cliente_nombre=data.get("clienteNombre", ""),
                libro_entrada_id=data.get("libroEntradaId", 0)
            )
        except Exception as e:
            logger.error("Error en MuestraResponseDto.from_dict: %s, datos: %s", e, data)
            return MuestraResponseDto()

class LibroDeEntradaDto:
    def __init__(
        self,
        id: int = 0,
        observaciones: str = "",
        fecha_llegada: Optional[datetime] = None,
        fecha: Optional[datetime] = None,
        fecha_analisis: Optional[datetime] = None,
        procedencia: str = "",
        sitio_extraccion: str = "",
        muestras: Optional[List[MuestraDto]] = None
    ):
        self.id = id
        self.observaciones = observaciones
        self.fecha_llegada = fecha_llegada or datetime.now()
        self.fecha = fecha or datetime.now()
        self.fecha_analisis = fecha_analisis
        self.procedencia = procedencia
        self.sitio_extraccion = sitio_extraccion
        self.muestras = muestras or []

    def to_dict(self):
        """Convierte a JSON para la API."""
        # Serializar muestras asegurando que cada muestra tenga 'procedencia' si no la proporciona
        muestras_serializadas = []
        for muestra in self.muestras:
            m_dict = muestra.to_dict() if hasattr(muestra, 'to_dict') else dict(muestra)
            if not m_dict.get('procedencia'):
                m_dict['procedencia'] = self.procedencia
            muestras_serializadas.append(m_dict)

        result = {
            "fechaLLegada": self.fecha_llegada.isoformat() + "Z",
            "fecha": self.fecha.isoformat() + "Z",
            "fechaAnalisis": self.fecha_analisis.isoformat() + "Z" if self.fecha_analisis else None,
            "procedencia": self.procedencia,
            "sitioExtraccion": self.sitio_extraccion,
            "observaciones": self.observaciones,
            "muestras": muestras_serializadas
        }
        
        # Solo incluir id si es diferente de 0 (para UPDATE)
        if self.id != 0:
            result["id"] = self.id
            
        return result

    @staticmethod
    def from_dict(data):
        muestras = [MuestraDto.from_dict(m) for m in data.get("muestras", [])]
        fecha_analisis = datetime.fromisoformat(data["fechaAnalisis"].replace("Z", "+00:00")) if data.get("fechaAnalisis") else None
        return LibroDeEntradaDto(
            id=data.get("id", 0),
            observaciones=data.get("observaciones", ""),
            fecha_llegada=datetime.fromisoformat(data["fechaLLegada"].replace("Z", "+00:00")) if data.get("fechaLLegada") else datetime.now(),
            fecha=datetime.fromisoformat(data["fecha"].replace("Z", "+00:00")) if data.get("fecha") else datetime.now(),
            fecha_analisis=fecha_analisis,
            procedencia=data.get("procedencia", ""),
            sitio_extraccion=data.get("sitioExtraccion", ""),
            muestras=muestras
        )

class LibroDeEntradaResponseDto:
    def __init__(
        self,
        id: int = 0,
        fecha_registro: Optional[datetime] = None,
        fecha_llegada: Optional[datetime] = None,
        fecha_analisis: Optional[datetime] = None,
        procedencia: str = "",
        sitio_extraccion: str = "",
        observaciones: str = "",
        muestras: Optional[List[MuestraResponseDto]] = None
    ):
        self.id = id
        self.fecha_registro = fecha_registro or datetime.now()
        self.fecha_llegada = fecha_llegada or datetime.now()
        self.fecha_analisis = fecha_analisis
        self.procedencia = procedencia
        self.sitio_extraccion = sitio_extraccion
        self.observaciones = observaciones
        self.muestras = muestras or []

    @staticmethod
    def from_dict(data):
        try:
            muestras = [MuestraResponseDto.from_dict(m) for m in data.get("muestras", [])]
            fecha_analisis = datetime.fromisoformat(data["fechaAnalisis"].replace("Z", "+00:00")) if data.get("fechaAnalisis") else None
            fecha_registro = datetime.fromisoformat(data["fechaRegistro"].replace("Z", "+00:00")) if data.get("fechaRegistro") else datetime.now()
            fecha_llegada = datetime.fromisoformat(data["fechaLlegada"].replace("Z", "+00:00")) if data.get("fechaLlegada") else datetime.now()
            return LibroDeEntradaResponseDto(
                id=data.get("id", 0),
                fecha_registro=fecha_registro,
                fecha_llegada=fecha_llegada,
                fecha_analisis=fecha_analisis,
                procedencia=data.get("procedencia", ""),
                sitio_extraccion=data.get("sitioExtraccion", ""),
                observaciones=data.get("observaciones", ""),
                muestras=muestras
            )
        except Exception as e:
            logger.error("Error en LibroDeEntradaResponseDto.from_dict: %s, datos: %s", e, data)
            return LibroDeEntradaResponseDto()