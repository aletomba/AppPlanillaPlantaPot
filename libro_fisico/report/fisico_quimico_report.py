import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)


class FisicoQuimicoReport:
    @staticmethod
    def exportar(fisicos: list, ruta_archivo: str, logo_path: str | None = None, metadata_lookup: dict | None = None, exclude_meta_keys: list | None = None) -> None:
        """
        Genera un PDF donde, para cada registro fisicoquímico, se muestran primero
        los metadatos (datos que no pertenecen al análisis) y debajo una tabla con
        los valores de análisis.

        Estructura por registro:
        - Bloque de metadatos (ID, Fecha, Llegada, Análisis, Procedencia, Muestra ID)
        - Tabla de análisis (pH, Turbidez, Alcalinidad, Dureza, Nitritos, Cloruros,
          Calcio, Magnesio, DBO5)
        """
        estilos = getSampleStyleSheet()
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
        elementos = [Paragraph("Reporte Fisicoquímico", estilos["Title"]), Spacer(1, 12)]

        meta_keys = [
            ("ID", "id"),
            ("Fecha", "fecha"),
            ("Fecha Llegada", "fecha_llegada"),
            ("Fecha Análisis", "fecha_analisis"),
            ("Procedencia", "procedencia"),
            ("Muestra ID", "muestra_id"),
        ]

        analisis_keys = [
            ("pH", "ph"),
            ("Turbidez", "turbidez"),
            ("Alcalinidad", "alcalinidad"),
            ("Dureza", "dureza"),
            ("Nitritos", "nitritos"),
            ("Cloruros", "cloruros"),
            ("Calcio", "calcio"),
            ("Magnesio", "magnesio"),
            ("DBO5", "dbo5"),
        ]

        # Default: excluir ID, Fecha (libro) y Muestra ID según lo pedido
        default_exclude = ["ID", "Fecha (libro)", "Muestra ID"]
        if exclude_meta_keys is None:
            exclude_meta_keys = default_exclude

        for fq in fisicos:
            # Si se pasó un lookup de metadatos, úsalo para enriquecer la información
            mdata = {}
            try:
                m_id = getattr(fq, "muestra_id", None) or getattr(fq, "muestraId", None)
            except Exception:
                m_id = None
            if metadata_lookup and m_id in metadata_lookup:
                mdata = metadata_lookup[m_id] or {}

            # Metadatos: construir manualmente usando lookup cuando exista, con fallback a atributos de fq
            meta_rows = [
                ["ID", FisicoQuimicoReport._format_value(getattr(fq, "id", ""))],
                ["Fecha (libro)", FisicoQuimicoReport._format_value(mdata.get("libro_fecha", getattr(fq, "fecha", "")))],
                ["Fecha Llegada (libro)", FisicoQuimicoReport._format_value(mdata.get("libro_fecha_llegada", getattr(fq, "fecha_llegada", "")))],
                ["Fecha Análisis", FisicoQuimicoReport._format_value(getattr(fq, "fecha_analisis", ""))],
                ["Procedencia (libro)", FisicoQuimicoReport._format_value(mdata.get("libro_procedencia", getattr(fq, "procedencia", "")))],
                ["Sitio Extracción", FisicoQuimicoReport._format_value(mdata.get("libro_sitio_extraccion", ""))],
                ["Muestreador", FisicoQuimicoReport._format_value(mdata.get("muestra_nombre_muestreador", ""))],
                ["Latitud", FisicoQuimicoReport._format_value(mdata.get("muestra_latitud", ""))],
                ["Longitud", FisicoQuimicoReport._format_value(mdata.get("muestra_longitud", ""))],
                ["Observaciones", FisicoQuimicoReport._format_value(mdata.get("libro_observaciones", ""))],
                ["Muestra ID", FisicoQuimicoReport._format_value(mdata.get("muestra_id", getattr(fq, "muestra_id", getattr(fq, "muestraId", ""))))],
            ]

            # Filtrar filas de metadatos según exclude_meta_keys
            if exclude_meta_keys:
                meta_rows = [row for row in meta_rows if row[0] not in exclude_meta_keys]
            meta_table = Table(meta_rows, colWidths=[120, 380])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))

            elementos.append(Paragraph(f"<b>Registro ID:</b> {getattr(fq, 'id', '')}", estilos["Heading3"]))
            elementos.append(Spacer(1, 6))
            elementos.append(meta_table)
            elementos.append(Spacer(1, 8))

            # Tabla de análisis: dos columnas (Analito, Valor)
            analisis_rows = [["Analito", "Valor"]] + [[k, FisicoQuimicoReport._format_value(getattr(fq, attr, ""))] for k, attr in analisis_keys]
            analisis_table = Table(analisis_rows, colWidths=[180, 320])
            analisis_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))

            elementos.append(analisis_table)
            elementos.append(Spacer(1, 18))

        doc.build(elementos)

    @staticmethod
    def _format_value(value):
        """Formatea valores básicos para la tabla (fechas, None, etc.)."""
        try:
            if value is None:
                return ""
            # Si es datetime, formatear como dd/mm/YYYY
            from datetime import datetime

            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y")
            return str(value)
        except Exception:
            return str(value)

    @staticmethod
    def exportar_con_libros(fisicos: list, libros: list, ruta_archivo: str, logo_path: str | None = None, debug: bool = False) -> None:
        """
        Conveniencia: construir un metadata_lookup a partir de la lista de `libros` y
        llamar a `exportar` con ese lookup para que los metadatos del libro/muestra
        se muestren en el PDF.

        - `libros` debe ser una lista de objetos `LibroDeEntradaDto` o similares que
          contengan `muestras` (cada muestra con `id`, `nombre_muestreador`, `latitud`, `longitud`, ...).
        """
        lookup = {}
        try:
            for libro in libros:
                libro_fecha = getattr(libro, "fecha", None)
                libro_fecha_llegada = getattr(libro, "fecha_llegada", None)
                for m in getattr(libro, "muestras", []) or []:
                    mid = getattr(m, "id", None) or getattr(m, "muestra_id", None) or getattr(m, "muestraId", None)
                    if mid is None:
                        continue
                    lookup[mid] = {
                        "libro_id": getattr(libro, "id", None),
                        "libro_fecha": libro_fecha,
                        "libro_fecha_llegada": libro_fecha_llegada,
                        "libro_procedencia": getattr(libro, "procedencia", ""),
                        "libro_sitio_extraccion": getattr(libro, "sitio_extraccion", ""),
                        "libro_observaciones": getattr(libro, "observaciones", ""),
                        "muestra_nombre_muestreador": getattr(m, "nombre_muestreador", ""),
                        "muestra_latitud": getattr(m, "latitud", ""),
                        "muestra_longitud": getattr(m, "longitud", ""),
                        "muestra_id": mid,
                    }
        except Exception as e:
            logger.error("Error construyendo lookup de metadatos: %s", e)

        logger.debug("Metadata lookup keys: %s", list(lookup.keys()))
        for k in list(lookup.keys())[:5]:
            logger.debug("  %s -> %s", k, lookup[k])

        FisicoQuimicoReport.exportar(fisicos, ruta_archivo, logo_path=logo_path, metadata_lookup=lookup)
