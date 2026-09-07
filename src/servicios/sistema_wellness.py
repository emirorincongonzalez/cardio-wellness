from decimal import Decimal
from typing import List, Optional, Union
import unicodedata

from src.controladores.control_base import ControlBase
from src.controladores.control_clientes import ControlClientes
from src.controladores.control_progreso import ControlProgreso
from src.controladores.control_rutinas import ControlRutinas
from src.modelos.cliente import Cliente
from src.modelos.progreso_mensual import ProgresoMensual
from src.modelos.rutina import Rutina
from src.servicios.generador_reportes_pdf import GeneradorReportesPDF


def _normalizar_texto(texto: str) -> str:
    """Elimina tildes y convierte a mayúsculas para comparaciones."""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto).upper())
        if unicodedata.category(c) != "Mn"
    )


class SistemaWellness(ControlBase):
    """
    Servicio de alto nivel que orquesta funcionalidades del sistema:
    sugerencia de rutinas, cálculo de diferencias de peso y generación de reportes.
    """

    def __init__(
        self,
        control_clientes: Optional[ControlClientes] = None,
        control_rutinas: Optional[ControlRutinas] = None,
        control_progreso: Optional[ControlProgreso] = None,
        generador_pdf: Optional[GeneradorReportesPDF] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ) -> None:
        super().__init__(ruta_log=ruta_log)
        self.control_clientes = control_clientes or ControlClientes(ruta_log=ruta_log)
        self.control_rutinas = control_rutinas or ControlRutinas(ruta_log=ruta_log)
        self.control_progreso = control_progreso or ControlProgreso(ruta_log=ruta_log)
        self.generador_pdf = generador_pdf or GeneradorReportesPDF()

    def _registrar_log(self, usuario: str, accion: str, detalle: Optional[str] = None) -> None:
        """Sobrescribe el método de ControlBase para incluir detalle opcional."""
        if detalle:
            super()._registrar_log(usuario, f"{accion}: {detalle}")
        else:
            super()._registrar_log(usuario, accion)

    def evaluar_objetivo_y_sugerir_rutina(self, cliente: Cliente) -> Optional[Rutina]:
        """
        Sugiere una rutina basada en el objetivo del cliente.

        Args:
            cliente (Cliente): Cliente al que se le quiere sugerir una rutina.

        Returns:
            Rutina: Rutina sugerida, o None si no hay rutinas disponibles.
        """
        objetivo = getattr(cliente, "objetivo", "") or ""
        objetivo_norm = _normalizar_texto(objetivo)

        rutinas = self.control_rutinas.listar()
        if not rutinas:
            self._registrar_log(
                getattr(cliente, "id_usuario", "CLIENTE"),
                "SUGERENCIA_RUTINA",
                "SIN_RUTINAS"
            )
            return None

        # Coincidencia por palabra clave del objetivo
        if any(w in objetivo_norm for w in ("PESO", "ADELGAZAR", "QUEMA", "GRASA", "CARDIO")):
            for rutina in rutinas:
                if not isinstance(rutina, Rutina):
                    continue
                nom = _normalizar_texto(rutina.nombre)
                desc = _normalizar_texto(rutina.descripcion or "")
                if "QUEMA" in nom or "CARDIO" in nom or "GRASA" in desc:
                    self._registrar_log(
                        getattr(cliente, "id_usuario", "CLIENTE"),
                        "SUGERENCIA_RUTINA",
                        f"CARDIO_QUEMA_GRASA - {rutina.nombre}"
                    )
                    return rutina

        if any(w in objetivo_norm for w in ("MUSCULO", "HIPERTROFIA", "FUERZA", "VOLUMEN")):
            for rutina in rutinas:
                if not isinstance(rutina, Rutina):
                    continue
                nom = _normalizar_texto(rutina.nombre)
                if "FUERZA" in nom or "HIPERTROFIA" in nom:
                    self._registrar_log(
                        getattr(cliente, "id_usuario", "CLIENTE"),
                        "SUGERENCIA_RUTINA",
                        f"FUERZA_HIPERTROFIA - {rutina.nombre}"
                    )
                    return rutina

        # Fallback a la primera rutina
        rutina_default = rutinas[0]
        self._registrar_log(
            getattr(cliente, "id_usuario", "CLIENTE"),
            "SUGERENCIA_RUTINA",
            f"DEFAULT - {rutina_default.nombre}"
        )
        return rutina_default

    def calcular_diferencia_peso_mensual(self, id_cliente: int) -> Decimal:
        """
        Calcula la diferencia de peso entre los dos últimos registros mensuales.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            Decimal: Diferencia de peso (actual - anterior). Positivo = aumento.
        """
        historial = self.control_progreso.consultar_progreso(id_cliente)
        if not historial or len(historial) < 2:
            self._registrar_log(
                f"CLIENTE_{id_cliente}",
                "CALCULO_DIFERENCIA_PESO",
                "HISTORIAL_INSUFICIENTE"
            )
            return Decimal("0.0")

        # Los objetos ya vienen ordenados por fecha descendente (más reciente primero)
        reg_actual = historial[0]   # ProgresoMensual
        reg_anterior = historial[1] # ProgresoMensual

        if not isinstance(reg_actual, ProgresoMensual) or not isinstance(reg_anterior, ProgresoMensual):
            raise TypeError("El historial debe contener objetos ProgresoMensual.")

        peso_actual = Decimal(str(reg_actual.peso))
        peso_anterior = Decimal(str(reg_anterior.peso))

        diferencia = peso_actual - peso_anterior
        self._registrar_log(
            f"CLIENTE_{id_cliente}",
            "CALCULO_DIFERENCIA_PESO",
            f"DIF: {diferencia:.2f} kg"
        )
        return diferencia

    def emitir_reporte_pdf_cliente(
        self,
        cliente: Union[Cliente, int],
        ruta_archivo: Optional[str] = None
    ) -> Optional[str]:
        """
        Genera un reporte PDF del progreso de un cliente.

        Args:
            cliente (Union[Cliente, int]): Objeto Cliente o su ID.
            ruta_archivo (str, optional): Ruta donde guardar el PDF.

        Returns:
            str: Ruta del archivo generado, o None si falla.
        """
        # Obtener el objeto Cliente si se pasó un ID
        if isinstance(cliente, int):
            cliente_obj = self.control_clientes.buscar_por_id(cliente)
            if cliente_obj is None:
                self._registrar_log(
                    f"ID_{cliente}",
                    "REPORTE_PDF_ERROR",
                    "CLIENTE_NO_ENCONTRADO"
                )
                return None
        else:
            cliente_obj = cliente

        try:
            resumen = self.control_progreso.calcular_resumen_cliente(cliente_obj.id_usuario)
            historial = self.control_progreso.consultar_progreso(cliente_obj.id_usuario)

            ruta_generada = self.generador_pdf.generar_reporte_progreso_cliente(
                cliente=cliente_obj,
                resumen_actividad=resumen,
                historial_progreso=historial,
                ruta_archivo=ruta_archivo,
            )

            self._registrar_log(
                getattr(cliente_obj, "correo_electronico", f"ID_{cliente_obj.id_usuario}"),
                "REPORTE_PDF_GENERADO",
                ruta_generada
            )
            return ruta_generada

        except Exception as e:
            self._registrar_log(
                getattr(cliente_obj, "correo_electronico", f"ID_{cliente_obj.id_usuario}"),
                "REPORTE_PDF_ERROR",
                str(e)
            )
            raise RuntimeError(f"Error al generar el reporte PDF: {e}") from e
