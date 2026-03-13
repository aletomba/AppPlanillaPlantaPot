from datetime import datetime
from typing import Optional, List


class AnalisisPuntoDto:
    PUNTOS = ["AguaNatural", "Decantada", "Filtrada", "Consumo"]
    PARAMS = ["ph", "turbidez", "alcalinidad", "dureza", "nitritos",
              "cloruros", "calcio", "magnesio", "dbo5", "cloro"]

    def __init__(self, punto_muestreo: str = "", **kwargs):
        self.punto_muestreo = punto_muestreo
        self.ph = kwargs.get("ph", "")
        self.turbidez = kwargs.get("turbidez", "")
        self.alcalinidad = kwargs.get("alcalinidad", "")
        self.dureza = kwargs.get("dureza", "")
        self.nitritos = kwargs.get("nitritos", "")
        self.cloruros = kwargs.get("cloruros", "")
        self.calcio = kwargs.get("calcio", "")
        self.magnesio = kwargs.get("magnesio", "")
        self.dbo5 = kwargs.get("dbo5", "")
        self.cloro = kwargs.get("cloro", "")

    def to_dict(self):
        return {
            "puntoMuestreo": self.punto_muestreo,
            "ph": self.ph or None,
            "turbidez": self.turbidez or None,
            "alcalinidad": self.alcalinidad or None,
            "dureza": self.dureza or None,
            "nitritos": self.nitritos or None,
            "cloruros": self.cloruros or None,
            "calcio": self.calcio or None,
            "magnesio": self.magnesio or None,
            "dbo5": self.dbo5 or None,
            "cloro": self.cloro or None,
        }

    @staticmethod
    def from_dict(d: dict) -> "AnalisisPuntoDto":
        return AnalisisPuntoDto(
            punto_muestreo=d.get("puntoMuestreo", ""),
            ph=d.get("ph") or "",
            turbidez=d.get("turbidez") or "",
            alcalinidad=d.get("alcalinidad") or "",
            dureza=d.get("dureza") or "",
            nitritos=d.get("nitritos") or "",
            cloruros=d.get("cloruros") or "",
            calcio=d.get("calcio") or "",
            magnesio=d.get("magnesio") or "",
            dbo5=d.get("dbo5") or "",
            cloro=d.get("cloro") or "",
        )


class EnsayoJarrasDto:
    def __init__(self, id: int = 0,
                 dosis1=None, dosis2=None, dosis3=None, dosis4=None, dosis5=None,
                 dosis_seleccionada=None, unidad_medida: str = "mg/L"):
        self.id = id
        self.dosis1 = dosis1
        self.dosis2 = dosis2
        self.dosis3 = dosis3
        self.dosis4 = dosis4
        self.dosis5 = dosis5
        self.dosis_seleccionada = dosis_seleccionada
        self.unidad_medida = unidad_medida

    def to_dict(self):
        return {
            "id": self.id,
            "dosis1": self._to_float(self.dosis1),
            "dosis2": self._to_float(self.dosis2),
            "dosis3": self._to_float(self.dosis3),
            "dosis4": self._to_float(self.dosis4),
            "dosis5": self._to_float(self.dosis5),
            "dosisSeleccionada": self._to_float(self.dosis_seleccionada),
            "unidadMedida": self.unidad_medida,
        }

    @staticmethod
    def _to_float(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def from_dict(d: dict) -> "EnsayoJarrasDto":
        return EnsayoJarrasDto(
            id=d.get("id", 0),
            dosis1=d.get("dosis1"),
            dosis2=d.get("dosis2"),
            dosis3=d.get("dosis3"),
            dosis4=d.get("dosis4"),
            dosis5=d.get("dosis5"),
            dosis_seleccionada=d.get("dosisSeleccionada"),
            unidad_medida=d.get("unidadMedida", "mg/L"),
        )


class PlanillaDiariaDto:
    def __init__(self, id: int = 0,
                 fecha: Optional[datetime] = None,
                 operador: str = "",
                 observaciones: str = "",
                 libro_entrada_id: int = 0,
                 analisis_por_punto: Optional[List[AnalisisPuntoDto]] = None,
                 ensayo_jarras: Optional[EnsayoJarrasDto] = None):
        self.id = id
        self.fecha = fecha or datetime.now()
        self.operador = operador
        self.observaciones = observaciones
        self.libro_entrada_id = libro_entrada_id
        self.analisis_por_punto = analisis_por_punto or []
        self.ensayo_jarras = ensayo_jarras

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.strftime("%Y-%m-%dT00:00:00Z"),
            "operador": self.operador,
            "observaciones": self.observaciones,
            "analisisPorPunto": [a.to_dict() for a in self.analisis_por_punto],
            "ensayoJarras": self.ensayo_jarras.to_dict() if self.ensayo_jarras else None,
        }

    @staticmethod
    def from_dict(d: dict) -> "PlanillaDiariaDto":
        fecha_str = d.get("fecha", "")
        try:
            fecha = datetime.fromisoformat(fecha_str.replace("Z", ""))
        except Exception:
            fecha = datetime.now()

        analisis = [AnalisisPuntoDto.from_dict(a) for a in d.get("analisisPorPunto", [])]
        ensayo_raw = d.get("ensayoJarras")
        ensayo = EnsayoJarrasDto.from_dict(ensayo_raw) if ensayo_raw else None

        return PlanillaDiariaDto(
            id=d.get("id", 0),
            fecha=fecha,
            operador=d.get("operador") or "",
            observaciones=d.get("observaciones") or "",
            libro_entrada_id=d.get("libroEntradaId", 0),
            analisis_por_punto=analisis,
            ensayo_jarras=ensayo,
        )
