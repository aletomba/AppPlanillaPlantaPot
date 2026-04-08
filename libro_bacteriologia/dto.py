from datetime import datetime
from typing import Optional

class BacteriologiaDto:
    """DTO que refleja lo que espera la API de bacteriología."""
    def __init__(
        self,
        id: int = 0,
        fecha: Optional[datetime] = None,
        fecha_llegada: Optional[datetime] = None,
        fecha_analisis: Optional[datetime] = None,
        procedencia: str = "",
        coliformesNmp: str = "",
        coliformesFecalesNmp: str = "",
        coloniasAgar: str = "",
        coliFecalesUfc: str = "",
        observaciones: str = "",
        muestraId: int = 0,
        muestra_procedencia: str = ""
    ):
        self.id = id
        self.fecha = fecha or datetime.now()
        self.fecha_llegada = fecha_llegada or datetime.now()
        self.fecha_analisis = fecha_analisis or datetime.now()
        self.procedencia = procedencia
        self.coliformesNmp = coliformesNmp
        self.coliformesFecalesNmp = coliformesFecalesNmp
        self.coloniasAgar = coloniasAgar
        self.coliFecalesUfc = coliFecalesUfc
        self.observaciones = observaciones
        self.muestraId = muestraId
        self.muestra_procedencia = muestra_procedencia

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "fechaLLegada": self.fecha_llegada.isoformat() if self.fecha_llegada else None,
            "fechaAnalisis": self.fecha_analisis.isoformat() if self.fecha_analisis else None,
            "procedencia": self.procedencia,
            "coliformesNmp": self.coliformesNmp,
            "coliformesFecalesNmp": self.coliformesFecalesNmp,
            "coloniasAgar": self.coloniasAgar,
            "coliFecalesUfc": self.coliFecalesUfc,
            "observaciones": self.observaciones,
            "muestraId": self.muestraId
        }

    @staticmethod
    def from_dict(data: dict):
        if not data:
            return BacteriologiaDto()
        return BacteriologiaDto(
            id=data.get("id", 0),
            fecha=datetime.fromisoformat(data["fecha"]) if data.get("fecha") else None,
            fecha_llegada=datetime.fromisoformat(data["fechaLLegada"]) if data.get("fechaLLegada") else None,
            fecha_analisis=datetime.fromisoformat(data["fechaAnalisis"]) if data.get("fechaAnalisis") else None,
            procedencia=data.get("procedencia", ""),
            coliformesNmp=data.get("coliformesNmp", ""),
            coliformesFecalesNmp=data.get("coliformesFecalesNmp", ""),
            coloniasAgar=data.get("coloniasAgar", ""),
            coliFecalesUfc=data.get("coliFecalesUfc", ""),
            observaciones=data.get("observaciones", ""),
            muestraId=data.get("muestraId", 0),
            muestra_procedencia=data.get("muestraProcedencia", "")
        )

    def to_row(self):
        """Retorna una lista con los valores para uso en reportes/tableviews."""
        return [
            self.id,
            self.fecha.strftime("%d/%m/%Y") if self.fecha else "",
            self.fecha_llegada.strftime("%d/%m/%Y") if self.fecha_llegada else "",
            self.fecha_analisis.strftime("%d/%m/%Y") if self.fecha_analisis else "",
            self.procedencia,
            self.coliformesNmp,
            self.coliformesFecalesNmp,
            self.coloniasAgar,
            self.coliFecalesUfc,
            self.observaciones,
            self.muestraId
        ]
