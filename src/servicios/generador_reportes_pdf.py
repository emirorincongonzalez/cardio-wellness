from datetime import datetime
from pathlib import Path
from typing import List, Optional


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


from src.modelos.progreso_mensual import ProgresoMensual



class GeneradorReportesPDF:


    def __init__(self, directorio_salida: str = "reportes"):
        self.directorio_salida = Path(directorio_salida)
        self.directorio_salida.mkdir(parents=True, exist_ok=True)


    def generar_reporte_progreso_cliente(
        self,
        cliente,
        resumen_actividad: dict,
        historial_progreso: List[ProgresoMensual],
        ruta_archivo: Optional[str] = None,
    ) -> str:
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
            ["Mes", "Peso (kg)", "Sesiones Completadas", "Sesiones Planificadas", "Cumplimiento (%)"]
        ]


        if historial_progreso:
            for progreso in historial_progreso:
                # Manejar tanto dicts como objetos ProgresoMensual
                if isinstance(progreso, dict):
                    mes = progreso.get('mes', '')
                    if hasattr(mes, 'strftime'):
                        mes = mes.strftime("%B %Y")
                    peso = f"{progreso.get('peso_registrado', 0):.1f}"
                    completadas = progreso.get('sesiones_completadas', 0)
                    planificadas = progreso.get('sesiones_planificadas', 0)
                elif isinstance(progreso, ProgresoMensual):
                    mes = progreso.mes.strftime("%B %Y")
                    peso = f"{progreso.peso:.1f}"
                    completadas = progreso.sesiones_completadas
                    planificadas = progreso.sesiones_planificadas
                else:
                    mes = "N/A"
                    peso = "-"
                    completadas = 0
                    planificadas = 0
                
                # Calcular cumplimiento
                if planificadas > 0:
                    cumplimiento = f"{(completadas / planificadas * 100):.1f}%"
                else:
                    cumplimiento = "0.0%"
                
                tabla_historial.append([mes, peso, str(completadas), str(planificadas), cumplimiento])
        else:
            tabla_historial.append(["Sin registros", "-", "-", "-", "-"])


        t_hist = Table(tabla_historial, colWidths=[120, 80, 100, 100, 100])
        t_hist.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A5568")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(t_hist)


        doc.build(story)
        return str(ruta_destino)