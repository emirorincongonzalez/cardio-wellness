from src.persistencia.usuario_dao import UsuarioDAO


class ControlAutenticacion:

    def __init__(self, usuario_dao=None):
        self.usuario_dao = usuario_dao or UsuarioDAO()

    def iniciar_sesion(self, correo, contrasenia):
        if not isinstance(correo, str) or not correo.strip():
            raise ValueError("El correo electrónico es obligatorio.")

        if not isinstance(contrasenia, str) or not contrasenia:
            raise ValueError("La contraseña es obligatoria.")

        return self.usuario_dao.iniciar_sesion(
            correo.strip(),
            contrasenia,
        )
