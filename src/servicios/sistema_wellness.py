"""
Servicio de alto nivel de la aplicación Cardio-Wellness.

Coordina:

- Sugerencias de rutinas.
- Cálculo de diferencias de peso.
- Generación de reportes PDF.
"""

from decimal import Decimal
from typing import Any, Optional, Union
import unicodedata


from src.controladores.control_base import ControlBase
from src.controladores.control_clientes import ControlClientes
from src.controladores.control_progreso import ControlProgreso
from src.controladores.control_rutinas import ControlRutinas
from src.modelos.cliente import Cliente
from src.modelos.progreso_mensual import ProgresoMensual
from src.modelos.rutina import Rutina
from src.servicios.generador_reportes_pdf import (
    GeneradorReportesPDF,
)


def _normalizar_texto(texto: Any) -> str:
    """
    Elimina tildes y convierte un texto a mayúsculas.
    """
    texto_normalizado = unicodedata.normalize(
        "NFD",
        str(texto).upper(),
    )

    return "".join(
        caracter
        for caracter in texto_normalizado
        if unicodedata.category(caracter) != "Mn"
    )


class SistemaWellness(ControlBase):
    """
    Servicio de alto nivel que coordina funcionalidades
    relacionadas con clientes, rutinas y progreso.
    """

    def __init__(
        self,
        control_clientes: Optional[ControlClientes],
        control_rutinas: Optional[ControlRutinas],
        control_progreso: Optional[ControlProgreso],
        generador_pdf: Optional[GeneradorReportesPDF] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ) -> None:
        """
        Inicializa el servicio con controladores inyectados.
        """
        super().__init__(ruta_log=ruta_log)

        if control_clientes is None:
            raise ValueError(
                "SistemaWellness requiere un "
                "ControlClientes inicializado."
            )

        if control_rutinas is None:
            raise ValueError(
                "SistemaWellness requiere un "
                "ControlRutinas inicializado."
            )

        if control_progreso is None:
            raise ValueError(
                "SistemaWellness requiere un "
                "ControlProgreso inicializado."
            )

        self.control_clientes = control_clientes
        self.control_rutinas = control_rutinas
        self.control_progreso = control_progreso

        self.generador_pdf = (
            generador_pdf
            if generador_pdf is not None
            else GeneradorReportesPDF()
        )

    def _registrar_log(
        self,
        usuario: str,
        accion: str,
        detalle: Optional[str] = None,
    ) -> None:
        """
        Registra una acción en el archivo de log.
        """
        if detalle is None:
            super()._registrar_log(
                usuario,
                accion,
            )
            return

        super()._registrar_log(
            usuario,
            accion,
            detalle,
        )

    def evaluar_objetivo_y_sugerir_rutina(
        self,
        cliente: Cliente,
    ) -> Optional[Union[Rutina, dict]]:
        """
        Sugiere una rutina basándose en el objetivo del cliente.
        """
        objetivo = getattr(
            cliente,
            "objetivo",
            "",
        ) or ""

        objetivo_normalizado = _normalizar_texto(
            objetivo
        )

        rutinas = self.control_rutinas.listar()

        if not rutinas:
            self._registrar_log(
                self._identificador_cliente(cliente),
                "SUGERENCIA_RUTINA",
                "SIN_RUTINAS",
            )
            return None

        palabras_peso = (
            "PESO",
            "ADELGAZAR",
            "QUEMA",
            "GRASA",
            "CARDIO",
        )

        if any(
            palabra in objetivo_normalizado
            for palabra in palabras_peso
        ):
            for rutina in rutinas:
                nombre, descripcion = (
                    self._obtener_textos_rutina(rutina)
                )

                es_rutina_cardio = (
                    "QUEMA" in nombre
                    or "CARDIO" in nombre
                    or "GRASA" in descripcion
                )

                if es_rutina_cardio:
                    self._registrar_log(
                        self._identificador_cliente(cliente),
                        "SUGERENCIA_RUTINA",
                        "CARDIO_QUEMA_GRASA",
                    )
                    return rutina

        palabras_fuerza = (
            "MUSCULO",
            "HIPERTROFIA",
            "FUERZA",
            "VOLUMEN",
        )

        if any(
            palabra in objetivo_normalizado
            for palabra in palabras_fuerza
        ):
            for rutina in rutinas:
                nombre, _ = (
                    self._obtener_textos_rutina(rutina)
                )

                es_rutina_fuerza = (
                    "FUERZA" in nombre
                    or "HIPERTROFIA" in nombre
                )

                if es_rutina_fuerza:
                    self._registrar_log(
                        self._identificador_cliente(cliente),
                        "SUGERENCIA_RUTINA",
                        "FUERZA_HIPERTROFIA",
                    )
                    return rutina

        rutina_default = rutinas[0]

        self._registrar_log(
            self._identificador_cliente(cliente),
            "SUGERENCIA_RUTINA",
            "DEFAULT",
        )

        return rutina_default

    def calcular_diferencia_peso_mensual(
        self,
        id_cliente: int,
    ) -> Decimal:
        """
        Calcula la diferencia de peso entre los dos últimos
        registros del historial.

        Resultado positivo:
            El cliente aumentó de peso.

        Resultado negativo:
            El cliente disminuyó de peso.
        """
        historial = (
            self.control_progreso.consultar_progreso(
                id_cliente
            )
        )

        if not historial or len(historial) < 2:
            self._registrar_log(
                f"CLIENTE_{id_cliente}",
                "CALCULO_DIFERENCIA_PESO",
                "HISTORIAL_INSUFICIENTE",
            )
            return Decimal("0.0")

        registro_actual = historial[0]
        registro_anterior = historial[1]

        peso_actual = self._obtener_peso(
            registro_actual
        )

        peso_anterior = self._obtener_peso(
            registro_anterior
        )

        diferencia = peso_actual - peso_anterior

        self._registrar_log(
            f"CLIENTE_{id_cliente}",
            "CALCULO_DIFERENCIA_PESO",
            f"DIF: {diferencia:.1f}",
        )

        return diferencia

    def emitir_reporte_pdf_cliente(
        self,
        cliente: Union[Cliente, int],
        ruta_archivo: Optional[str] = None,
    ) -> Optional[str]:
        """
        Genera un reporte PDF del progreso de un cliente.
        """
        cliente_obj = self._obtener_cliente(cliente)

        if cliente_obj is None:
            identificador = (
                f"ID_{cliente}"
                if isinstance(cliente, int)
                else "CLIENTE_DESCONOCIDO"
            )

            self._registrar_log(
                identificador,
                "REPORTE_PDF_ERROR",
                "CLIENTE_NO_ENCONTRADO",
            )

            return None

        id_cliente = getattr(
            cliente_obj,
            "id_usuario",
            None,
        )

        if id_cliente is None:
            raise ValueError(
                "El cliente no tiene un id_usuario válido."
            )

        usuario_log = getattr(
            cliente_obj,
            "correo_electronico",
            f"ID_{id_cliente}",
        )

        try:
            resumen = (
                self.control_progreso
                .calcular_resumen_cliente(
                    id_cliente
                )
            )

            historial = (
                self.control_progreso
                .consultar_progreso(
                    id_cliente
                )
            )

            ruta_generada = (
                self.generador_pdf
                .generar_reporte_progreso_cliente(
                    cliente=cliente_obj,
                    resumen_actividad=resumen,
                    historial_progreso=historial,
                    ruta_archivo=ruta_archivo,
                )
            )

            self._registrar_log(
                usuario_log,
                "REPORTE_PDF_GENERADO",
                str(ruta_generada),
            )

            return ruta_generada

        except Exception as error:
            self._registrar_log(
                usuario_log,
                "REPORTE_PDF_ERROR",
                str(error),
            )

            raise RuntimeError(
                "Error al generar el reporte PDF: "
                f"{error}"
            ) from error

    def _obtener_cliente(
        self,
        cliente: Union[Cliente, int],
    ) -> Optional[Cliente]:
        """
        Devuelve un Cliente a partir de un objeto o de un ID.
        """
        if isinstance(cliente, int):
            return self.control_clientes.buscar_por_id(
                cliente
            )

        return cliente

    @staticmethod
    def _identificador_cliente(
        cliente: Any,
    ) -> str:
        """
        Devuelve el identificador del cliente para los logs.
        """
        id_cliente = getattr(
            cliente,
            "id_usuario",
            None,
        )

        if id_cliente is None:
            return "CLIENTE"

        return str(id_cliente)

    @staticmethod
    def _obtener_textos_rutina(
        rutina: Any,
    ) -> tuple[str, str]:
        """
        Devuelve nombre y descripción de una rutina.
        """
        if isinstance(rutina, dict):
            nombre = rutina.get(
                "nombre",
                "",
            )

            descripcion = rutina.get(
                "descripcion",
                "",
            )

            return (
                _normalizar_texto(nombre),
                _normalizar_texto(descripcion),
            )

        nombre = getattr(
            rutina,
            "nombre",
            "",
        )

        descripcion = getattr(
            rutina,
            "descripcion",
            "",
        )

        return (
            _normalizar_texto(nombre),
            _normalizar_texto(descripcion),
        )

    @staticmethod
    def _obtener_peso(
        registro: Any,
    ) -> Decimal:
        """
        Obtiene el peso de un registro como Decimal.
        """
        if isinstance(registro, dict):
            peso = registro.get(
                "peso_registrado",
                registro.get(
                    "peso",
                    0,
                ),
            )

            return Decimal(str(peso))

        if isinstance(registro, ProgresoMensual):
            return Decimal(
                str(registro.peso)
            )

        if hasattr(registro, "peso"):
            return Decimal(
                str(registro.peso)
            )

        if hasattr(registro, "peso_registrado"):
            return Decimal(
                str(registro.peso_registrado)
            )

        raise TypeError(
            "El registro no contiene un peso válido."
        )