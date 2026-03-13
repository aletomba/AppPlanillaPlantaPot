import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

class BacteriologiaReport:
    @staticmethod
    def exportar(bacterias: list, ruta_archivo: str, logo_path: str | None = None, metadata_lookup: dict | None = None, exclude_meta_keys: list | None = None) -> None:
        estilos = getSampleStyleSheet()
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
        elementos = [Paragraph("Reporte Bacteriología", estilos["Title"]), Spacer(1, 12)]

        # Metadata template: analytical fields removed so they always
        # appear in the results table (no duplication).
        meta_rows_template = [
            ("ID", "id"),
            ("Fecha (libro)", "fecha"),
            ("Fecha Llegada (libro)", "fecha_llegada"),
            ("Fecha Análisis", "fecha_analisis"),
            ("Procedencia (libro)", "procedencia"),
            ("Muestreador", "muestra_nombre_muestreador"),
            ("Latitud", "muestra_latitud"),
            ("Longitud", "muestra_longitud"),
            ("Muestra ID", "muestraId"),
            ("Observaciones", "observaciones"),
        ]

        # Analytical/result keys: shown in the results table
        resultado_keys = [
            ("Coliformes (NMP)", "coliformesNmp"),
            ("Coliformes Fecales (NMP)", "coliformesFecalesNmp"),
            ("Colonias Agar", "coloniasAgar"),
            ("Coli Fecales (UFC)", "coliFecalesUfc"),
        ]

        default_exclude = ["ID", "Fecha (libro)", "Muestra ID"]
        if exclude_meta_keys is None:
            exclude_meta_keys = default_exclude

        for bq in bacterias:
            mdata = {}
            try:
                m_id = getattr(bq, "muestraId", None) or getattr(bq, "muestra_id", None)
            except Exception:
                m_id = None
            if metadata_lookup and m_id in metadata_lookup:
                mdata = metadata_lookup[m_id] or {}

            # Construir meta rows usando template y lookup - con índice numérico
            meta_rows = []
            meta_label_set = set()
            for i, (label, key) in enumerate(meta_rows_template, start=1):
                value = mdata.get(key, getattr(bq, key, ""))
                if exclude_meta_keys and label in exclude_meta_keys:
                    continue
                meta_label_set.add(label)
                meta_rows.append([str(i), label, BacteriologiaReport._format_value(value)])

            # Tabla de metadatos con columna de número, etiqueta y valor
            meta_table = Table(meta_rows, colWidths=[30, 140, 330])
            meta_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ]))

            elementos.append(Paragraph(f"<b>Registro ID:</b> {getattr(bq, 'id', '')}", estilos["Heading3"]))
            elementos.append(Spacer(1, 6))
            elementos.append(meta_table)
            elementos.append(Spacer(1, 8))

            resultado_rows = [["Analito", "Valor"]]
            for k, attr in resultado_keys:
                if k in meta_label_set:
                    continue
                resultado_rows.append([k, BacteriologiaReport._format_value(getattr(bq, attr, ""))])
            resultado_table = Table(resultado_rows, colWidths=[180, 320])
            resultado_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))

            elementos.append(resultado_table)
            elementos.append(Spacer(1, 18))

        doc.build(elementos)

    @staticmethod
    def _format_value(value):
        try:
            if value is None:
                return ""
            from datetime import datetime
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y")
            return str(value)
        except Exception:
            return str(value)

    @staticmethod
    def exportar_con_libros(bacterias: list, libros: list, ruta_archivo: str, logo_path: str | None = None, debug: bool = False) -> None:
        """
        Conveniencia: construir un metadata_lookup a partir de la lista de `libros` y
        llamar a `exportar` con ese lookup para que los metadatos del libro/muestra
        se muestren en el PDF.
        """
        lookup = {}
        try:
            for libro in libros:
                # Extraer valores del libro y ponerlos con las claves que
                # utiliza el template de metadatos para que el lookup sea
                # compatible con exportar().
                libro_fecha = getattr(libro, "fecha", None)
                libro_fecha_llegada = getattr(libro, "fecha_llegada", None)
                for m in getattr(libro, "muestras", []) or []:
                    mid = getattr(m, "id", None) or getattr(m, "muestra_id", None) or getattr(m, "muestraId", None)
                    if mid is None:
                        continue
                    # Mapear claves esperadas por meta_rows_template
                    lookup[mid] = {
                        "id": getattr(libro, "id", None),
                        "fecha": libro_fecha,
                        "fecha_llegada": libro_fecha_llegada,
                        "procedencia": getattr(libro, "procedencia", ""),
                        "sitio_extraccion": getattr(libro, "sitio_extraccion", ""),
                        "observaciones": getattr(libro, "observaciones", ""),
                        # datos de la muestra
                        "muestra_nombre_muestreador": getattr(m, "nombre_muestreador", ""),
                        "muestra_latitud": getattr(m, "latitud", ""),
                        "muestra_longitud": getattr(m, "longitud", ""),
                        "muestraId": mid,
                    }
        except Exception as e:
            logger.error("Error construyendo lookup de metadatos: %s", e)

        logger.debug("Metadata lookup keys: %s", list(lookup.keys()))
        for k in list(lookup.keys())[:5]:
            logger.debug("  %s -> %s", k, lookup[k])

        BacteriologiaReport.exportar(bacterias, ruta_archivo, logo_path=logo_path, metadata_lookup=lookup)
