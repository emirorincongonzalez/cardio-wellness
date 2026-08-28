from decimal import Decimal

from src.controladores.control_base import ControlBase
from src.modelos.cliente import Cliente
from src.persistencia.cliente_dao import ClienteDAO


class ControlClientes(ControlBase):

    def __init__(self, cliente_dao=None, ruta_log="logs/LOG_CARDIO.txt"):
        super().__init__(ruta_log=ruta_log)
        self.cliente_dao = cliente_dao or ClienteDAO()

    def registrar_cliente(
        self,
        nombre,
        apellido,
        correo_electronico,
        contrasenia_plana,
        edad,
        peso,
        altura,
        objetivo,
        meta=None,
    ):
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

        objetivo_final = (objetivo or meta or "").strip()
        if not objetivo_final:
            raise ValueError("El objetivo no puede estar vacío.")

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

        try:
            cliente_guardado = self.cliente_dao.guardar(cliente)
            self._registrar_log(
                cliente_guardado.correo_electronico,
                "REGISTRO_CLIENTE",
            )
            return cliente_guardado
        except ValueError as error:
            raise ValueError(f"Error al registrar el cliente: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al registrar cliente: {error}") from error

    def buscar_por_id(self, id_usuario):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")
        return self.cliente_dao.buscar_por_id(id_usuario)

    def obtener_por_id(self, id_usuario):
        return self.buscar_por_id(id_usuario)

    def buscar_por_correo(self, correo):
        if not isinstance(correo, str) or not correo.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        return self.cliente_dao.buscar_por_correo(correo.strip())

    def obtener_por_correo(self, correo):
        return self.buscar_por_correo(correo)

    def listar(self):
        return self.cliente_dao.listar()

    def listar_clientes(self):
        return self.listar()

    def actualizar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise TypeError("Se requiere una instancia de Cliente.")
        try:
            return self.cliente_dao.actualizar(cliente)
        except ValueError as error:
            raise ValueError(f"Error al actualizar cliente: {error}") from error

    def cambiar_contrasenia(self, id_usuario, contrasenia_actual, nueva_contrasenia):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")
        if not isinstance(nueva_contrasenia, str) or not nueva_contrasenia:
            raise ValueError("La nueva contraseña no puede estar vacía.")
        return self.cliente_dao.actualizar_contrasenia(
            id_usuario,
            contrasenia_actual,
            nueva_contrasenia,
        )

    def eliminar_cliente(self, id_usuario):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")

        resultado = self.cliente_dao.eliminar_por_id(id_usuario)
        self._registrar_log(f"ID_{id_usuario}", "ELIMINACION_CLIENTE")
        return resultado