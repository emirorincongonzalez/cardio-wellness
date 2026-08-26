from decimal import Decimal

from src.modelos.cliente import Cliente
from src.persistencia.cliente_dao import ClienteDAO


class ControlClientes:

    def __init__(self, cliente_dao=None):
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
    ):
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            raise ValueError("La contraseña no puede estar vacía.")

        cliente = Cliente(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo_electronico,
            contrasenia_hash=contrasenia_plana,
            edad=edad,
            peso=peso,
            altura=altura,
            objetivo=objetivo,
        )
        return self.cliente_dao.guardar(cliente)

    def obtener_por_id(self, id_usuario):
        if not isinstance(id_usuario, int) or isinstance(id_usuario, bool) or id_usuario <= 0:
            raise ValueError("El id de usuario debe ser un entero positivo.")
        return self.cliente_dao.buscar_por_id(id_usuario)

    def obtener_por_correo(self, correo):
        if not isinstance(correo, str) or not correo.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        return self.cliente_dao.buscar_por_correo(correo.strip())

    def listar_clientes(self):
        return self.cliente_dao.listar()

    def actualizar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise TypeError("Se requiere una instancia de Cliente.")
        return self.cliente_dao.actualizar(cliente)

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
        return self.cliente_dao.eliminar_por_id(id_usuario)