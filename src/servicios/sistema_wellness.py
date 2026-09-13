from decimal import Decimal
import unicodedata

from src.controladores.control_base import ControlBase
from src.controladores.control_clientes import ControlClientes
from src.controladores.control_progreso import ControlProgreso
from src.controladores.control_rutinas import ControlRutinas
from src.servicios.generador_reportes_pdf import GeneradorReportesPDF
from src.servicios.fabrica_usuario import FabricaUsuario


def _normalizar_texto(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto).upper())
        if unicodedata.category(c) != "Mn"
    )


class SistemaWellness(ControlBase):

    def __init__(
        self,
        control_clientes=None,
        control_rutinas=None,
        control_progreso=None,
        generador_pdf=None,
        ruta_log="logs/LOG_CARDIO.txt",
    ):
        super().__init__(ruta_log=ruta_log)
        self.control_clientes = control_clientes or ControlClientes(ruta_log=ruta_log)
        self.control_rutinas = control_rutinas or ControlRutinas(ruta_log=ruta_log)
        self.control_progreso = control_progreso or ControlProgreso(ruta_log=ruta_log)
        self.generador_pdf = generador_pdf or GeneradorReportesPDF()

    def registrar_usuario(self, tipo: str, datos: dict, asignar_rutina_inicial: bool = True):
        """
        Registra un nuevo usuario usando el Factory Method.
        
        Args:
            tipo: Tipo de usuario ('administrador' o 'cliente')
            datos: Diccionario con los datos del usuario
            asignar_rutina_inicial: Si es True, asigna rutina automáticamente a clientes
            
        Returns:
            Usuario creado
        """
        # Usar Factory Method para crear el usuario
        usuario = FabricaUsuario.crear_usuario(tipo, datos)
        
        # Guardar según el tipo
        if tipo.lower().strip() == "cliente":
            cliente = self.control_clientes.registrar_cliente(
                nombre=datos.get("nombre", ""),
                apellido=datos.get("apellido", ""),
                correo_electronico=datos.get("correo_electronico", ""),
                contrasenia_plana=datos.get("contrasenia_plana", ""),
                edad=datos.get("edad", 0),
                peso=datos.get("peso", 0.0),
                altura=datos.get("altura", 0.0),
                objetivo=datos.get("objetivo", ""),
            )
            
            # Asignar rutina inicial si corresponde
            if asignar_rutina_inicial:
                rutina_sugerida = self.evaluar_objetivo_y_sugerir_rutina(cliente)
                if rutina_sugerida:
                    self.control_rutinas.asignar_rutina(cliente, rutina_sugerida)
            
            return cliente
        
        else:
            # Para administrador, el controlador se encarga
            from src.controladores.control_autenticacion import ControlAutenticacion
            control_auth = ControlAutenticacion()
            return control_auth.registrar_administrador(
                nombre=datos.get("nombre", ""),
                apellido=datos.get("apellido", ""),
                correo_electronico=datos.get("correo_electronico", ""),
                contrasenia_plana=datos.get("contrasenia_plana", ""),
                edad=datos.get("edad", 0),
            )

    def evaluar_objetivo_y_sugerir_rutina(self, cliente):
        objetivo = getattr(cliente, "objetivo", "") or ""
        objetivo_norm = _normalizar_texto(objetivo)

        rutinas = self.control_rutinas.listar()
        if not rutinas:
            return None

        # Coincidencia por palabra clave del objetivo
        if any(w in objetivo_norm for w in ("PESO", "ADELGAZAR", "QUEMA", "GRASA", "CARDIO")):
            for r in rutinas:
                desc = _normalizar_texto(getattr(r, "descripcion", "") or r.get("descripcion", "") if isinstance(r, dict) else "")
                nom = _normalizar_texto(getattr(r, "nombre", "") or r.get("nombre", "") if isinstance(r, dict) else "")
                if "QUEMA" in nom or "CARDIO" in nom or "GRASA" in desc:
                    self._registrar_log(getattr(cliente, "id_usuario", "CLIENTE"), "SUGERENCIA_RUTINA", detalle="CARDIO_QUEMA_GRASA")
                    return r

        if any(w in objetivo_norm for w in ("MUSCULO", "HIPERTROFIA", "FUERZA", "VOLUMEN")):
            for r in rutinas:
                nom = _normalizar_texto(getattr(r, "nombre", "") or r.get("nombre", "") if isinstance(r, dict) else "")
                if "FUERZA" in nom or "HIPERTROFIA" in nom:
                    self._registrar_log(getattr(cliente, "id_usuario", "CLIENTE"), "SUGERENCIA_RUTINA", detalle="FUERZA_HIPERTROFIA")
                    return r

        # Fallback a la primera rutina disponible
        rutina_default = rutinas[0]
        self._registrar_log(getattr(cliente, "id_usuario", "CLIENTE"), "SUGERENCIA_RUTINA", detalle="DEFAULT")
        return rutina_default

    def calcular_diferencia_peso_mensual(self, id_cliente):
        historial = self.control_progreso.consultar_progreso(id_cliente)
        if not historial or len(historial) < 2:
            return Decimal("0.0")

        # Tomar los dos registros más recientes
        reg_actual = historial[0]
        reg_anterior = historial[1]

        peso_actual = Decimal(str(reg_actual.get("peso_registrado", 0) or 0))
        peso_anterior = Decimal(str(reg_anterior.get("peso_registrado", 0) or 0))

        diferencia = peso_actual - peso_anterior
        self._registrar_log(f"CLIENTE_{id_cliente}", "CALCULO_DIFERENCIA_PESO", detalle=f"DIF: {diferencia}")
        return diferencia

    def emitir_reporte_pdf_cliente(self, cliente, ruta_archivo=None):
        id_cliente = getattr(cliente, "id_usuario", cliente)
        if isinstance(id_cliente, int):
            cliente_obj = self.control_clientes.buscar_por_id(id_cliente) or cliente
        else:
            cliente_obj = cliente

        resumen = self.control_progreso.calcular_resumen_cliente(cliente_obj)
        historial = self.control_progreso.consultar_progreso(cliente_obj)

        ruta_generada = self.generador_pdf.generar_reporte_progreso_cliente(
            cliente=cliente_obj,
            resumen_actividad=resumen,
            historial_progreso=historial,
            ruta_archivo=ruta_archivo,
        )
        self._registrar_log(getattr(cliente_obj, "correo_electronico", f"ID_{id_cliente}"), "REPORTE_PDF_GENERADO")
        return ruta_generada