from decimal import Decimal
from typing import List, Optional, Union

from src.controladores.control_base import ControlBase
from src.modelos.cliente import Cliente
from src.persistencia.cliente_dao import ClienteDAO
from src.servicios.gestor_seguridad import GestorSeguridad
from src.utilidades.logger import (
    log_calculo_diferencia_peso,
    log_consulta_progreso,
    log_generar_progreso,
    log_registro_cliente,
)


class ControlClientes(ControlBase):
    """
    Controlador para la gestión de clientes.
    """

    def __init__(
        self,
        cliente_dao: Optional[ClienteDAO] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ) -> None:
        super().__init__(ruta_log=ruta_log)

        self.cliente_dao = (
            cliente_dao
            if cliente_dao is not None
            else ClienteDAO()
        )

    @staticmethod
    def _validar_datos_registro(
        nombre: str,
        apellido: str,
        correo_electronico: str,
        contrasenia_plana: str,
        edad: int,
        peso: Union[int, float, Decimal],
        altura: Union[int, float, Decimal],
        objetivo: str,
    ) -> None:
        """
        Valida los datos del registro.
        """
        if (
            not isinstance(nombre, str)
            or not nombre.strip()
        ):
            raise ValueError(
                "El nombre no puede estar vacío."
            )

        if (
            not isinstance(apellido, str)
            or not apellido.strip()
        ):
            raise ValueError(
                "El apellido no puede estar vacío."
            )

        if (
            not isinstance(
                correo_electronico,
                str,
            )
            or not correo_electronico.strip()
        ):
            raise ValueError(
                "El correo electrónico es obligatorio."
            )

        if (
            not isinstance(
                contrasenia_plana,
                str,
            )
            or not contrasenia_plana
        ):
            raise ValueError(
                "La contraseña no puede estar vacía."
            )

        if (
            not isinstance(edad, int)
            or isinstance(edad, bool)
            or edad <= 0
        ):
            raise ValueError(
                "La edad debe ser un entero mayor "
                "que cero."
            )

        if (
            not isinstance(
                peso,
                (int, float, Decimal),
            )
            or isinstance(peso, bool)
            or peso <= 0
        ):
            raise ValueError(
                "El peso debe ser mayor que cero."
            )

        if (
            not isinstance(
                altura,
                (int, float, Decimal),
            )
            or isinstance(altura, bool)
            or altura <= 0
        ):
            raise ValueError(
                "La altura debe ser mayor que cero."
            )

        if (
            not isinstance(objetivo, str)
            or not objetivo.strip()
        ):
            raise ValueError(
                "El objetivo no puede estar vacío."
            )

        if not GestorSeguridad.validar_fortaleza_contrasena(
            contrasenia_plana
        ):
            raise ValueError(
                "La contraseña es muy débil. "
                "Debe tener al menos 8 caracteres, "
                "una mayúscula, un número y un "
                "carácter especial."
            )

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
        Registra un cliente con hash bcrypt.
        """
        objetivo_texto = (
            objetivo
            if isinstance(objetivo, str)
            else ""
        ).strip()

        if not objetivo_texto and meta:
            objetivo_texto = meta.strip()

        self._validar_datos_registro(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=(
                correo_electronico
            ),
            contrasenia_plana=(
                contrasenia_plana
            ),
            edad=edad,
            peso=peso,
            altura=altura,
            objetivo=objetivo_texto,
        )

        # Generar el hash antes de crear Cliente.
        hash_bcrypt = (
            GestorSeguridad.generar_hash(
                contrasenia_plana
            )
        )

        if (
            not hash_bcrypt.startswith(
                ("$2a$", "$2b$", "$2y$")
            )
            or len(hash_bcrypt) != 60
        ):
            raise RuntimeError(
                "No se generó un hash bcrypt válido."
            )

        cliente = Cliente(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            correo_electronico=(
                correo_electronico
                .strip()
                .lower()
            ),
            contrasenia_hash=hash_bcrypt,
            edad=edad,
            peso=peso,
            altura=altura,
            objetivo=objetivo_texto,
        )

        try:
            # ClienteDAO.guardar() debe usar el hash
            # que ya está dentro del objeto Cliente.
            cliente_guardado = (
                self.cliente_dao.guardar(
                    cliente
                )
            )

            self._registrar_log(
                cliente_guardado.correo_electronico,
                "REGISTRO_CLIENTE",
            )

            log_registro_cliente(
                cliente_guardado.correo_electronico
            )

            return cliente_guardado

        except ValueError as error:
            raise ValueError(
                "Error al registrar el cliente: "
                f"{error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al registrar "
                f"cliente: {error}"
            ) from error

    def buscar_por_id(
        self,
        id_usuario: int,
    ) -> Optional[Cliente]:
        """
        Busca un cliente por ID de usuario.
        """
        self._validar_id_usuario(id_usuario)

        return self.cliente_dao.buscar_por_id(
            id_usuario
        )

    def obtener_por_id(
        self,
        id_usuario: int,
    ) -> Optional[Cliente]:
        """
        Alias de buscar_por_id().
        """
        return self.buscar_por_id(id_usuario)

    def buscar_por_correo(
        self,
        correo: str,
    ) -> Optional[Cliente]:
        """
        Busca un cliente por correo.
        """
        if (
            not isinstance(correo, str)
            or not correo.strip()
        ):
            raise ValueError(
                "El correo electrónico es obligatorio."
            )

        return self.cliente_dao.buscar_por_correo(
            correo.strip().lower()
        )

    def obtener_por_correo(
        self,
        correo: str,
    ) -> Optional[Cliente]:
        """
        Alias de buscar_por_correo().
        """
        return self.buscar_por_correo(correo)

    def listar(self) -> List[Cliente]:
        """
        Lista todos los clientes.
        """
        return self.cliente_dao.listar()

    def listar_clientes(self) -> List[Cliente]:
        """
        Alias de listar().
        """
        return self.listar()

    def actualizar_cliente(
        self,
        cliente: Cliente,
    ) -> Cliente:
        """
        Actualiza un cliente existente.
        """
        if not isinstance(cliente, Cliente):
            raise TypeError(
                "Se requiere una instancia de Cliente."
            )

        try:
            cliente_actualizado = (
                self.cliente_dao.actualizar(
                    cliente
                )
            )

            self._registrar_log(
                cliente_actualizado.correo_electronico,
                "ACTUALIZACION_CLIENTE",
            )

            return cliente_actualizado

        except ValueError as error:
            raise ValueError(
                "Error al actualizar cliente: "
                f"{error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al actualizar "
                f"cliente: {error}"
            ) from error

    def cambiar_contrasenia(
        self,
        id_usuario: int,
        contrasenia_actual: str,
        nueva_contrasenia: str,
    ) -> bool:
        """
        Cambia la contraseña de un cliente.
        """
        self._validar_id_usuario(id_usuario)

        if (
            not isinstance(
                contrasenia_actual,
                str,
            )
            or not contrasenia_actual
        ):
            raise ValueError(
                "La contraseña actual es obligatoria."
            )

        if (
            not isinstance(
                nueva_contrasenia,
                str,
            )
            or not nueva_contrasenia
        ):
            raise ValueError(
                "La nueva contraseña no puede estar "
                "vacía."
            )

        if not GestorSeguridad.validar_fortaleza_contrasena(
            nueva_contrasenia
        ):
            raise ValueError(
                "La nueva contraseña es muy débil."
            )

        return (
            self.cliente_dao.actualizar_contrasenia(
                id_usuario,
                contrasenia_actual,
                nueva_contrasenia,
            )
        )

    def eliminar_cliente(
        self,
        id_usuario: int,
    ) -> bool:
        """
        Elimina un cliente por ID de usuario.
        """
        self._validar_id_usuario(id_usuario)

        resultado = (
            self.cliente_dao.eliminar_por_id(
                id_usuario
            )
        )

        self._registrar_log(
            f"ID_{id_usuario}",
            "ELIMINACION_CLIENTE",
        )

        return resultado

    def consultar_progreso(
        self,
        id_cliente: int,
    ) -> dict:
        """
        Consulta el progreso de un cliente.
        """
        self._validar_id_cliente(id_cliente)

        progreso = (
            self.cliente_dao.obtener_progreso(
                id_cliente
            )
        )

        self._registrar_log(
            f"CLIENTE_{id_cliente}",
            "CONSULTA_PROGRESO",
        )

        log_consulta_progreso(
            f"CLIENTE_{id_cliente}"
        )

        return progreso

    def generar_progreso_mensual(
        self,
        id_cliente: int,
    ) -> dict:
        """
        Genera el progreso mensual.
        """
        self._validar_id_cliente(id_cliente)

        progreso = (
            self.cliente_dao
            .generar_progreso_mensual(
                id_cliente
            )
        )

        self._registrar_log(
            f"CLIENTE_{id_cliente}",
            "GENERAR_PROGRESO",
        )

        log_generar_progreso(
            f"CLIENTE_{id_cliente}"
        )

        return progreso

    def calcular_diferencia_peso(
        self,
        id_cliente: int,
    ) -> float:
        """
        Calcula la diferencia de peso.
        """
        self._validar_id_cliente(id_cliente)

        diferencia = (
            self.cliente_dao
            .calcular_diferencia_peso(
                id_cliente
            )
        )

        self._registrar_log(
            f"CLIENTE_{id_cliente}",
            "CALCULO_DIFERENCIA_PESO",
            f"DIF: {diferencia:.1f}",
        )

        log_calculo_diferencia_peso(
            f"CLIENTE_{id_cliente}",
            diferencia,
        )

        return diferencia

    @staticmethod
    def _validar_id_usuario(
        id_usuario: int,
    ) -> None:
        """
        Valida un ID de usuario.
        """
        if (
            not isinstance(id_usuario, int)
            or isinstance(id_usuario, bool)
            or id_usuario <= 0
        ):
            raise ValueError(
                "El ID de usuario debe ser un entero "
                "positivo."
            )

    @staticmethod
    def _validar_id_cliente(
        id_cliente: int,
    ) -> None:
        """
        Valida un ID de cliente.
        """
        if (
            not isinstance(id_cliente, int)
            or isinstance(id_cliente, bool)
            or id_cliente <= 0
        ):
            raise ValueError(
                "El ID de cliente debe ser un entero "
                "positivo."
            )