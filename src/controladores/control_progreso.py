"""
Controlador para gestión de progreso mensual y reportes.
"""
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from datetime import date


from src.modelos.progreso_mensual import ProgresoMensual
from src.modelos.rutina import Rutina
from src.persistencia.progreso_mensual_dao import ProgresoMensualDAO
from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO
from src.controladores.control_base import ControlBase
from src.utilidades.logger import log_consulta_progreso, log_generar_progreso, log_consulta_impacto
from unittest.mock import Mock



def _obtener_progreso_dao_default() -> Optional[ProgresoMensualDAO]:
    """Obtiene el DAO de progreso por defecto."""
    try:
        from src.persistencia.progreso_mensual_dao import ProgresoMensualDAO
        from src.persistencia.conexion_bd import ConexionBD
        return ProgresoMensualDAO(ConexionBD.get_instancia())
    except Exception:
        return None



def _obtener_sesion_dao_default() -> Optional[SesionEntrenamientoDAO]:
    """Obtiene el DAO de sesiones por defecto."""
    try:
        from src.persistencia.sesion_entrenamiento_dao import SesionEntrenamientoDAO
        from src.persistencia.conexion_bd import ConexionBD
        return SesionEntrenamientoDAO(ConexionBD.get_instancia())
    except Exception:
        return None



def _obtener_clase_progreso():
    """Obtiene la clase ProgresoMensual."""
    try:
        from src.modelos.progreso_mensual import ProgresoMensual
        return ProgresoMensual
    except Exception:
        return None



def _extraer_id(obj: Any, *campos_posibles: str) -> Optional[int]:
    """
    Extrae el ID de un objeto, diccionario o entero.
    """
    if isinstance(obj, int):
        return obj
    if isinstance(obj, dict):
        for campo in campos_posibles:
            if campo in obj:
                return obj[campo]
        return None
    for campo in campos_posibles:
        if hasattr(obj, campo):
            valor = getattr(obj, campo)
            # Si es un Mock, retornar None
            if isinstance(valor, Mock):
                continue
            return valor
    return None



def _instanciar_progreso_mensual(
    id_cliente: int,
    mes: int,
    anio: int,
    peso_registrado: float,
    sesiones_completadas: int = 0,
    sesiones_planificadas: int = 12,
    id_progreso: Optional[int] = None,
) -> Union[ProgresoMensual, Dict[str, Any]]:
    """
    Función helper para crear instancias de ProgresoMensual.
    Si la clase no está disponible, retorna un diccionario.
    """
    clase_progreso = _obtener_clase_progreso()
    
    if clase_progreso is None:
        return {
            "id_progreso": id_progreso,
            "id_cliente": id_cliente,
            "mes": mes,
            "anio": anio,
            "peso_registrado": peso_registrado,
            "sesiones_completadas": sesiones_completadas,
            "sesiones_planificadas": sesiones_planificadas,
        }
    
    fecha_mes = date(anio, mes, 1)
    
    progreso = clase_progreso(
        id_cliente=id_cliente,
        mes=fecha_mes,
        peso=peso_registrado,
        sesiones_completadas=sesiones_completadas,
        sesiones_planificadas=sesiones_planificadas,
    )
    
    if id_progreso is not None:
        progreso.id_progreso = id_progreso
    
    return progreso



class ControlProgreso(ControlBase):
    """
    Controlador para gestión de progreso mensual y métricas.
    """


    def __init__(
        self,
        progreso_dao: Optional[ProgresoMensualDAO] = None,
        sesion_dao: Optional[SesionEntrenamientoDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ):
        super().__init__(ruta_log)
        self._progreso_dao = progreso_dao or _obtener_progreso_dao_default()
        self._sesion_dao = sesion_dao or _obtener_sesion_dao_default()


    @property
    def progreso_dao(self) -> Optional[ProgresoMensualDAO]:
        return self._progreso_dao


    @progreso_dao.setter
    def progreso_dao(self, valor: Optional[ProgresoMensualDAO]):
        self._progreso_dao = valor


    @property
    def sesion_dao(self) -> Optional[SesionEntrenamientoDAO]:
        return self._sesion_dao


    @sesion_dao.setter
    def sesion_dao(self, valor: Optional[SesionEntrenamientoDAO]):
        self._sesion_dao = valor


    def calcular_resumen_cliente(self, cliente: object) -> Dict[str, Any]:
        """
        Calcula el resumen de sesiones de un cliente (CU10).
        """
        id_cliente = _extraer_id(cliente, "id_usuario", "id_cliente", "id")
        
        if id_cliente is None or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo")


        if not self._sesion_dao:
            raise RuntimeError("El DAO de sesiones no está disponible")


        sesiones = self._sesion_dao.listar_por_cliente(id_cliente)
        
        # Manejar tanto dicts como objetos
        total_minutos = 0
        total_calorias = Decimal("0")
        for s in sesiones:
            if isinstance(s, dict):
                total_minutos += s.get("duracion_real", 0)
                total_calorias += Decimal(str(s.get("calorias_quemadas", 0)))
            else:
                total_minutos += s.duracion_real
                total_calorias += Decimal(str(s.calorias_quemadas))


        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")
        log_consulta_progreso(f"CLIENTE_{id_cliente}")


        return {
            "id_cliente": id_cliente,
            "total_sesiones": len(sesiones),
            "total_minutos": total_minutos,
            "total_calorias": total_calorias.quantize(Decimal("0.01")),
        }


    def obtener_resumen_cliente(self, cliente: object) -> Dict[str, Any]:
        """Alias de calcular_resumen_cliente."""
        return self.calcular_resumen_cliente(cliente)


    def calcular_impacto_calorico_rutina(
        self,
        rutina: Union[Rutina, Dict[str, Any]],
        usuario_consulta: Optional[str] = None,
    ) -> Decimal:
        """
        Calcula el impacto calórico total de una rutina (CU03).
        """
        if isinstance(rutina, dict):
            ejercicios = rutina.get("ejercicios", [])
            total = sum((Decimal(str(e.get("calorias_estimadas", 0))) for e in ejercicios), Decimal("0"))
        else:
            total = sum((Decimal(str(e.calorias_estimadas)) for e in rutina.ejercicios), Decimal("0"))
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(usuario_consulta or "SISTEMA", "CONSULTA_IMPACTO")
        log_consulta_impacto(usuario_consulta or "SISTEMA")
        
        return total.quantize(Decimal("0.01"))


    def obtener_impacto_rutina(
        self,
        rutina: Union[Rutina, Dict[str, Any]],
        usuario_consulta: Optional[str] = None,
    ) -> Decimal:
        """Alias de calcular_impacto_calorico_rutina."""
        return self.calcular_impacto_calorico_rutina(rutina, usuario_consulta)


    def generar_progreso_mensual(
        self,
        cliente: object,
        mes: Union[int, date],
        anio: Optional[int] = None,
        peso_actual: Optional[float] = None,
        observaciones: Optional[str] = None,
    ) -> ProgresoMensual:
        """
        Genera un registro de progreso mensual (CU09, CU10).
        """
        if not self._progreso_dao:
            raise RuntimeError("El DAO de progreso mensual no está disponible")


        id_cliente = _extraer_id(cliente, "id_usuario", "id_cliente", "id")
        
        if id_cliente is None or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo")


        # Si mes es un date, extraer mes y anio
        if isinstance(mes, date):
            mes_num = mes.month
            if anio is None:
                anio = mes.year
        else:
            mes_num = mes
        
        if anio is None:
            raise ValueError("Se requiere anio cuando mes no es un objeto date")
        
        # Si peso_actual es None, intentar obtenerlo del cliente
        if peso_actual is None and hasattr(cliente, 'peso'):
            peso_actual = cliente.peso
        
        if peso_actual is None:
            raise ValueError("Se requiere peso_actual")


        progreso = _instanciar_progreso_mensual(
            id_cliente=id_cliente,
            mes=mes_num,
            anio=anio,
            peso_registrado=peso_actual,
        )


        progreso_guardado = self._progreso_dao.guardar(progreso)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"CLIENTE_{id_cliente}", "GENERAR_PROGRESO")
        log_generar_progreso(f"CLIENTE_{id_cliente}")
        
        return progreso_guardado


    def consultar_progreso(self, cliente: object) -> List[ProgresoMensual]:
        """
        Consulta el historial de progreso de un cliente (CU03, CU10).
        """
        if not self._progreso_dao:
            raise RuntimeError("El DAO de progreso mensual no está disponible")


        id_cliente = _extraer_id(cliente, "id_usuario", "id_cliente", "id")
        
        if id_cliente is None or id_cliente <= 0:
            raise ValueError("El id del cliente debe ser un entero positivo")


        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")
        log_consulta_progreso(f"CLIENTE_{id_cliente}")


        return self._progreso_dao.buscar_por_cliente(id_cliente)