from decimal import Decimal
from typing import List, Optional, Union


from src.controladores.control_base import ControlBase
from src.modelos.cliente import Cliente
from src.persistencia.cliente_dao import ClienteDAO
from src.utilidades.logger import log_registro_cliente, log_consulta_progreso, log_generar_progreso, log_calculo_diferencia_peso


class ControlClientes(ControlBase):
    """
    Controlador para la gestión de clientes.
    Coordina las operaciones de registro, consulta, actualización y eliminación.
    """


    def __init__(
        self,
        cliente_dao: Optional[ClienteDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt"
    ) -> None:
        """
        Inicializa el controlador de clientes.


        Args:
            cliente_dao (ClienteDAO, optional): DAO de clientes. Si no se
                proporciona, se crea uno por defecto.
            ruta_log (str): Ruta al archivo de LOG para auditoría.
        """
        super().__init__(ruta_log=ruta_log)
        self.cliente_dao = cliente_dao or ClienteDAO()


    def registrar_cliente(
        self,
        nombre: str,
        apellido: str,
        correo_electronico: str,
        contrasenia_plana: str,
        edad: int,
        peso: Union[int, float, Decimal],
        altura: Union[int, float, Decimal],
        objetivo: str,
        meta: Optional[str] = None,
    ) -> Cliente:
        """
        Registra un nuevo cliente en el sistema.


        Args:
            nombre (str): Nombre del cliente.
            apellido (str): Apellido del cliente.
            correo_electronico (str): Correo electrónico.
            contrasenia_plana (str): Contraseña en texto plano.
            edad (int): Edad del cliente.
            peso (float): Peso del cliente en kg.
            altura (float): Altura del cliente en metros.
            objetivo (str): Objetivo de entrenamiento.
            meta (str, optional): Meta alternativa (se usa si objetivo está vacío).


        Returns:
            Cliente: Objeto Cliente guardado con ID asignado.


        Raises:
            ValueError: Si algún campo es inválido.
            RuntimeError: Si ocurre un error inesperado.
        """
        # ---- Validaciones ----
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not isinstance(apellido, str) or not apellido.strip():
            raise ValueError("El apellido no puede estar vacío.")
        if not isinstance(correo_electronico, str) or not correo_electronico.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            raise ValueError("La contraseña no puede estar vacía.")
        if not isinstance(edad, int) or isinstance(edad, bool) or edad <= 0:
            raise ValueError("La edad debe ser un número entero mayor que cero.")
        if (
            not isinstance(peso, (int, float, Decimal))
            or isinstance(peso, bool)
            or peso <= 0
        ):
            raise ValueError("El peso debe ser un número mayor que cero.")
        if (
            not isinstance(altura, (int, float, Decimal))
            or isinstance(altura, bool)
            or altura <= 0
        ):
            raise ValueError("La altura debe ser un número mayor que cero.")


        # Unificar objetivo y meta
        objetivo_final = (objetivo or meta or "").strip()
        if not objetivo_final:
            raise ValueError("El objetivo no puede estar vacío.")


        # ---- Crear objeto Cliente ----
        cliente = Cliente(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            correo_electronico=correo_electronico.strip(),
            contrasenia_hash=contrasenia_plana,
            edad=edad,
            peso=peso,
            altura=altura,
            objetivo=objetivo_final,
        )


        # ---- Guardar y registrar LOG ----
        try:
            cliente_guardado = self.cliente_dao.guardar(cliente)
            
            # LOG DOBLE: ControlBase + logger.py
            self._registrar_log(cliente_guardado.correo_electronico, "REGISTRO_CLIENTE")
            log_registro_cliente(cliente_guardado.correo_electronico)
            
            return cliente_guardado
        except ValueError as error:
            raise ValueError(f"Error al registrar el cliente: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al registrar cliente: {error}") from error


    def buscar_por_id(self, id_usuario: int) -> Optional[Cliente]:
        """Busca un cliente por su ID de usuario."""
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")
        return self.cliente_dao.buscar_por_id(id_usuario)


    # Alias para compatibilidad con DCD (camelCase)
    def obtener_por_id(self, id_usuario: int) -> Optional[Cliente]:
        """Alias de buscar_por_id (compatibilidad con DCD)."""
        return self.buscar_por_id(id_usuario)


    def buscar_por_correo(self, correo: str) -> Optional[Cliente]:
        """Busca un cliente por su correo electrónico."""
        if not isinstance(correo, str) or not correo.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        return self.cliente_dao.buscar_por_correo(correo.strip())


    # Alias para compatibilidad con DCD (camelCase)
    def obtener_por_correo(self, correo: str) -> Optional[Cliente]:
        """Alias de buscar_por_correo (compatibilidad con DCD)."""
        return self.buscar_por_correo(correo)


    def listar(self) -> List[Cliente]:
        """Lista todos los clientes del sistema."""
        return self.cliente_dao.listar()


    # Alias para compatibilidad
    def listar_clientes(self) -> List[Cliente]:
        """Alias de listar()."""
        return self.listar()


    def actualizar_cliente(self, cliente: Cliente) -> Cliente:
        """
        Actualiza los datos de un cliente existente.


        Args:
            cliente (Cliente): Objeto Cliente con los datos actualizados.


        Returns:
            Cliente: Cliente actualizado.


        Raises:
            TypeError: Si el argumento no es una instancia de Cliente.
            ValueError: Si no se encuentra el cliente.
            RuntimeError: Si ocurre un error inesperado.
        """
        if not isinstance(cliente, Cliente):
            raise TypeError("Se requiere una instancia de Cliente.")


        try:
            cliente_actualizado = self.cliente_dao.actualizar(cliente)
            
            # LOG DOBLE: ControlBase + logger.py
            self._registrar_log(cliente_actualizado.correo_electronico, "ACTUALIZACION_CLIENTE")
            
            return cliente_actualizado
        except ValueError as error:
            raise ValueError(f"Error al actualizar cliente: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al actualizar cliente: {error}") from error


    def cambiar_contrasenia(
        self,
        id_usuario: int,
        contrasenia_actual: str,
        nueva_contrasenia: str
    ) -> bool:
        """
        Cambia la contraseña de un cliente.


        Args:
            id_usuario (int): ID del usuario.
            contrasenia_actual (str): Contraseña actual.
            nueva_contrasenia (str): Nueva contraseña.


        Returns:
            bool: True si el cambio fue exitoso, False si la contraseña actual es incorrecta.
        """
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")
        if not isinstance(nueva_contrasenia, str) or not nueva_contrasenia:
            raise ValueError("La nueva contraseña no puede estar vacía.")


        return self.cliente_dao.actualizar_contrasenia(
            id_usuario,
            contrasenia_actual,
            nueva_contrasenia,
        )


    def eliminar_cliente(self, id_usuario: int) -> bool:
        """
        Elimina un cliente del sistema.


        Args:
            id_usuario (int): ID del usuario a eliminar.


        Returns:
            bool: True si se eliminó correctamente, False si no existía.
        """
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")


        resultado = self.cliente_dao.eliminar_por_id(id_usuario)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"ID_{id_usuario}", "ELIMINACION_CLIENTE")
        
        return resultado


    def consultar_progreso(self, id_cliente: int) -> dict:
        """
        Consulta el progreso de un cliente.
        
        Args:
            id_cliente (int): ID del cliente.
            
        Returns:
            dict: Progreso del cliente.
        """
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id de cliente debe ser un entero positivo.")
        
        # Obtener progreso (implementación según tu código existente)
        progreso = self.cliente_dao.obtener_progreso(id_cliente)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"CLIENTE_{id_cliente}", "CONSULTA_PROGRESO")
        log_consulta_progreso(f"CLIENTE_{id_cliente}")
        
        return progreso


    def generar_progreso_mensual(self, id_cliente: int) -> dict:
        """
        Genera el reporte de progreso mensual de un cliente.
        
        Args:
            id_cliente (int): ID del cliente.
            
        Returns:
            dict: Progreso mensual generado.
        """
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id de cliente debe ser un entero positivo.")
        
        # Generar progreso (implementación según tu código existente)
        progreso = self.cliente_dao.generar_progreso_mensual(id_cliente)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"CLIENTE_{id_cliente}", "GENERAR_PROGRESO")
        log_generar_progreso(f"CLIENTE_{id_cliente}")
        
        return progreso


    def calcular_diferencia_peso(self, id_cliente: int) -> float:
        """
        Calcula la diferencia de peso de un cliente.
        
        Args:
            id_cliente (int): ID del cliente.
            
        Returns:
            float: Diferencia de peso.
        """
        if not isinstance(id_cliente, int) or isinstance(id_cliente, bool) or id_cliente <= 0:
            raise ValueError("El id de cliente debe ser un entero positivo.")
        
        # Calcular diferencia (implementación según tu código existente)
        diferencia = self.cliente_dao.calcular_diferencia_peso(id_cliente)
        
        # LOG DOBLE: ControlBase + logger.py
        self._registrar_log(f"CLIENTE_{id_cliente}", "CALCULO_DIFERENCIA_PESO", f"DIF: {diferencia:.1f}")
        log_calculo_diferencia_peso(f"CLIENTE_{id_cliente}", diferencia)
        
        return diferencia