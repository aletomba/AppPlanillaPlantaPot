# --- FisicoQuimicoDto ---

import datetime
from typing import Optional
from datetime import datetime

class FisicoQuimicoDto:
    def __init__(
        self,
        id: int = 0,
        fecha: Optional[datetime] = None,
        fecha_llegada: Optional[datetime] = None,
        fecha_analisis: Optional[datetime] = None,
        procedencia: str = "",
        ph: str = "",
        turbidez: str = "",
        alcalinidad: str = "",
        dureza: str = "",
        nitritos: str = "",
        cloruros: str = "",
        calcio: str = "",
        magnesio: str = "",
        dbo5: str = "",
        cloro: str = "",
        muestra_id: int = 0
    ):
        self.id = id
        self.fecha = fecha or datetime.now()
        self.fecha_llegada = fecha_llegada or datetime.now()
        self.fecha_analisis = fecha_analisis or datetime.now()
        self.procedencia = procedencia
        self.ph = ph
        self.turbidez = turbidez
        self.alcalinidad = alcalinidad
        self.dureza = dureza
        self.nitritos = nitritos
        self.cloruros = cloruros
        self.calcio = calcio
        self.magnesio = magnesio
        self.dbo5 = dbo5
        self.cloro = cloro
        self.muestra_id = muestra_id

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() + "Z",
            "fechaLLegada": self.fecha_llegada.isoformat() + "Z",
            "fechaAnalisis": self.fecha_analisis.isoformat() + "Z",
            "procedencia": self.procedencia,
            "ph": self.ph,
            "turbidez": self.turbidez,
            "alcalinidad": self.alcalinidad,
            "dureza": self.dureza,
            "nitritos": self.nitritos,
            "cloruros": self.cloruros,
            "calcio": self.calcio,
            "magnesio": self.magnesio,
            "dbo5": self.dbo5,
            "cloro": self.cloro,
            "muestraId": self.muestra_id
        }

    @staticmethod
    def from_dict(data):
        return FisicoQuimicoDto(
            id=data.get("id", 0),
            fecha=datetime.fromisoformat(data["fecha"].replace("Z", "+00:00")) if data.get("fecha") else datetime.now(),
            fecha_llegada=datetime.fromisoformat(data["fechaLLegada"].replace("Z", "+00:00")) if data.get("fechaLLegada") else datetime.now(),
            fecha_analisis=datetime.fromisoformat(data["fechaAnalisis"].replace("Z", "+00:00")) if data.get("fechaAnalisis") else datetime.now(),
            procedencia=data.get("procedencia", ""),
            ph=data.get("ph", ""),
            turbidez=data.get("turbidez", ""),
            alcalinidad=data.get("alcalinidad", ""),
            dureza=data.get("dureza", ""),
            nitritos=data.get("nitritos", ""),
            cloruros=data.get("cloruros", ""),
            calcio=data.get("calcio", ""),
            magnesio=data.get("magnesio", ""),
            dbo5=data.get("dbo5", ""),
            cloro=data.get("cloro", ""),
            muestra_id=data.get("muestraId", 0)
        )
    
    def to_row(self):
        return [
            self.id,
            self.fecha.strftime("%d/%m/%Y") if self.fecha else "",
            self.fecha_llegada.strftime("%d/%m/%Y") if self.fecha_llegada else "",
            self.fecha_analisis.strftime("%d/%m/%Y") if self.fecha_analisis else "",
            self.procedencia,
            self.ph, self.turbidez, self.alcalinidad, self.dureza,
            self.nitritos, self.cloruros, self.calcio, self.magnesio,
            self.dbo5, self.cloro, self.muestra_id
        ]