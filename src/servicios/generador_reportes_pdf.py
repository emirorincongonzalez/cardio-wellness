from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class GeneradorReportesPDF:

    def __init__(self, directorio_salida="reportes"):
        self.directorio_salida = Path(directorio_salida)
        self.directorio_salida.mkdir(parents=True, exist_ok=True)

    def generar_reporte_progreso_cliente(
        self,
        cliente,
        resumen_actividad,
        historial_progreso,
        ruta_archivo=None,
    ):
        id_cliente = getattr(cliente, "id_usuario", None) or getattr(cliente, "id", "desconocido")
        nombre_cliente = getattr(cliente, "nombre", "Cliente")
        apellido_cliente = getattr(cliente, "apellido", "")
        objetivo_cliente = getattr(cliente, "objetivo", "No especificado")
        peso_cliente = getattr(cliente, "peso", "N/A")

        if ruta_archivo is None:
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_pdf = f"reporte_progreso_cliente_{id_cliente}_{fecha_str}.pdf"
            ruta_destino = self.directorio_salida / nombre_pdf
        else:
            ruta_destino = Path(ruta_archivo)
            ruta_destino.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(ruta_destino), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Título principal
        titulo_style = ParagraphStyle(
            "TituloReporte",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A365D"),
            alignment=1,
        )
        story.append(Paragraph("<b>SISTEMA CARDIO-WELLNESS</b>", titulo_style))
        story.append(Paragraph("<b>Reporte de Progreso y Evaluación del Cliente</b>", styles["Normal"]))
        story.append(Spacer(1, 15))

        # Datos del cliente
        datos_cliente = [
            ["ID Usuario:", str(id_cliente), "Fecha Reporte:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Cliente:", f"{nombre_cliente} {apellido_cliente}".strip(), "Peso Actual:", f"{peso_cliente} kg"],
            ["Objetivo Salud:", str(objetivo_cliente), "Estado:", "Activo"],
        ]
        t_cliente = Table(datos_cliente, colWidths=[110, 160, 110, 140])
        t_cliente.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2D3748")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(t_cliente)
        story.append(Spacer(1, 15))

        # Resumen de actividad física
        total_sesiones = resumen_actividad.get("total_sesiones", 0)
        total_minutos = resumen_actividad.get("total_minutos", 0)
        total_calorias = resumen_actividad.get("total_calorias", 0)

        datos_resumen = [
            ["Total Sesiones Realizadas", "Minutos Totales", "Calorías Quemadas (Estimadas)"],
            [str(total_sesiones), f"{total_minutos} min", f"{total_calorias} kcal"],
        ]
        t_resumen = Table(datos_resumen, colWidths=[170, 170, 180])
        t_resumen.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t_resumen)
        story.append(Spacer(1, 15))

        # Historial mensual
        tabla_historial = [
            ["Año", "Mes", "Peso Reg.", "Sesiones", "Minutos", "Calorías", "Observaciones"]
        ]
        if historial_progreso:
            for reg in historial_progreso:
                anio = reg.get("anio", reg.get("año", "-"))
                mes = reg.get("mes", "-")
                peso = reg.get("peso_registrado", "-")
                ses = reg.get("total_sesiones", 0)
                mins = reg.get("total_minutos", 0)
                cals = reg.get("total_calorias", 0)
                obs = reg.get("observaciones", "") or "-"
                tabla_historial.append([str(anio), str(mes), f"{peso} kg", str(ses), str(mins), str(cals), str(obs)[:20]])
        else:
            tabla_historial.append(["-", "-", "-", "-", "-", "-", "Sin registros históricos"])

        t_hist = Table(tabla_historial, colWidths=[45, 40, 75, 60, 60, 75, 165])
        t_hist.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A5568")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-2, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(t_hist)

        doc.build(story)
        return str(ruta_destino)