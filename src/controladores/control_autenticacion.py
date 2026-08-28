from src.controladores.control_base import ControlBase
from src.persistencia.usuario_dao import UsuarioDAO


class ControlAutenticacion(ControlBase):

    def __init__(self, usuario_dao=None, ruta_log="logs/LOG_CARDIO.txt"):
        super().__init__(ruta_log=ruta_log)
        self.usuario_dao = usuario_dao or UsuarioDAO()
        self.usuario_actual = None

    def _validar_entradas_login(self, correo_electronico, contrasenia_plana):
        if not isinstance(correo_electronico, str) or not correo_electronico.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            raise ValueError("La contraseña no puede estar vacía.")

    def iniciar_sesion(self, correo_electronico, contrasenia_plana):
        self._validar_entradas_login(correo_electronico, contrasenia_plana)
        correo_limpio = correo_electronico.strip()

        usuario = None
        if hasattr(self.usuario_dao, "iniciar_sesion"):
            usuario = self.usuario_dao.iniciar_sesion(correo_limpio, contrasenia_plana)
        elif hasattr(self.usuario_dao, "buscar_por_correo"):
            u = self.usuario_dao.buscar_por_correo(correo_limpio)
            if u and hasattr(u, "verificar_contrasenia") and u.verificar_contrasenia(contrasenia_plana):
                usuario = u

        if usuario:
            self.usuario_actual = usuario
            correo = getattr(usuario, "correo_electronico", correo_limpio)
            self._registrar_log(correo, "LOGIN_EXITOSO")
            return usuario
        else:
            self._registrar_log(correo_limpio, "LOGIN_FALLIDO")
            return None

    def cerrar_sesion(self, usuario=None):
        usr = usuario or self.usuario_actual
        if usr:
            correo = getattr(usr, "correo_electronico", "USUARIO")
            self._registrar_log(correo, "LOGOUT")
        self.usuario_actual = None
        return True

    def cerrarSesion(self, usuario=None):
        return self.cerrar_sesion(usuario)

    def validar_credenciales(self, correo_electronico, contrasenia_plana):
        if not isinstance(correo_electronico, str) or not correo_electronico.strip():
            return None
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            return None

        correo_limpio = correo_electronico.strip()
        if hasattr(self.usuario_dao, "iniciar_sesion"):
            return self.usuario_dao.iniciar_sesion(correo_limpio, contrasenia_plana)
        elif hasattr(self.usuario_dao, "buscar_por_correo"):
            u = self.usuario_dao.buscar_por_correo(correo_limpio)
            if u and hasattr(u, "verificar_contrasenia") and u.verificar_contrasenia(contrasenia_plana):
                return u
        return None

    def validarCredenciales(self, correo_electronico, contrasenia_plana):
        return self.validar_credenciales(correo_electronico, contrasenia_plana)

    def obtener_usuario_actual(self):
        return self.usuario_actual

    def esta_autenticado(self):
        return self.usuario_actual is not None