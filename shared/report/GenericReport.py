from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class GenericReport:
    @staticmethod
    def generar_pdf(titulo, columnas, registros, ruta_archivo):   
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
        estilos = getSampleStyleSheet()
        elementos = [
            Paragraph(titulo, estilos["Title"]),
            Spacer(1, 12),
            Table([columnas] + registros, repeatRows=1, style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]))
        ]
        doc.build(elementos)