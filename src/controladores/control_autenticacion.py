from typing import Optional

from src.modelos.usuario import Usuario
from src.controladores.control_base import ControlBase
from src.persistencia.usuario_dao import UsuarioDAO


class ControlAutenticacion(ControlBase):
    """
    Controlador para la autenticación de usuarios.
    Gestiona el inicio y cierre de sesión, y mantiene el usuario actual.
    """

    def __init__(self, usuario_dao: Optional[UsuarioDAO] =None, ruta_log: str ="logs/LOG_CARDIO.txt") -> None:
        """
        Inicializa el controlador de autenticación.

        Args:
            usuario_dao (UsuarioDAO, optional): DAO de usuarios. Si no se
                proporciona, se crea uno por defecto.
            ruta_log (str): Ruta al archivo de LOG para auditoría.
        """
        super().__init__(ruta_log=ruta_log)
        self.usuario_dao = usuario_dao or UsuarioDAO()
        self.usuario_actual: Optional[Usuario] = None

    def _validar_entradas_login(self, correo_electronico: str, contrasenia_plana: str) -> None:
        """
                Valida las entradas para el inicio de sesión.
        
                Args:
                    correo_electronico (str): Correo del usuario.
                    contrasenia_plana (str): Contraseña en texto plano.
        
                Raises:
                    ValueError: Si algún campo es inválido.
                """
        if not isinstance(correo_electronico, str) or not correo_electronico.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            raise ValueError("La contraseña no puede estar vacía.")

    def iniciar_sesion(self, correo_electronico: str, contrasenia_plana: str) -> Optional[Usuario]:
        """
        Inicia sesión de un usuario.
        
        Args:
            correo_electronico (str): Correo del usuario.
            contrasenia_plana (str): Contraseña en texto plano.
        
        Returns:
            Usuario: Objeto usuario si las credenciales son correctas, None en caso contrario.
        """
        self._validar_entradas_login(correo_electronico, contrasenia_plana)
        correo_limpio = correo_electronico.strip()

        #Usar el DAO para inciar sesion.
        usuario = self.usuario_dao.iniciar_sesion(correo_limpio, contrasenia_plana)

        if usuario:
            self.usuario_actual = usuario
            correo = getattr(usuario, "correo_electronico", correo_limpio)
            self._registrar_log(correo, "LOGIN EXITOSO")
            return usuario
        else:
            self._registrar_log(correo_limpio, "LOGIN FALLIDO")
            return None

    def cerrar_sesion(self, usuario: Optional[Usuario] = None) -> bool:
        """
        Cierra la sesion del usuario actual o del usuario especificado.

        Args:
            usuario (Usuario, optional): Usuario cuya sesion se cerrara.
                Si no se proporciona, se usa el usuario actual.

        Returns:
            bool: Siempre True.
        """
        usr = usuario or self.usuario_actual
        if usr:
            correo = getattr(usr, "correo_electronico", "USUARIO")
            self._registrar_log(correo, "LOGOUT")
        self.usuario_actual = None
        return True
    
    #Alias para compatibilidad con el DCD (camelCase)
    def cerrarSesion(self, usuario: Optional[Usuario] = None) -> bool:
        return self.cerrar_sesion(usuario)

    def validar_credenciales(self, correo_electronico: str, contrasenia_plana: str) -> Optional[Usuario]:
        """
        Valida las credenciales de un usuario sin modificar la sesion.

        Args:
            correo_electronico (str): Correo del usuario.
            contrasenia_plana (str): Contrasena en texto plano.

        Returns:
            Usuario: Objeto usuario si las credenciales son correctas. None en caso contrario.
        """
        if not isinstance(correo_electronico, str) or not correo_electronico.strip():
            return None
        if not isinstance(contrasenia_plana, str) or not contrasenia_plana:
            return None

        correo_limpio = correo_electronico.strip()
        return self.usuario_dao.iniciar_sesion(correo_limpio, contrasenia_plana)

    #Alias para compatibilidad con el DCD
    def validarCredenciales(self, correo_electronico: str, contrasenia_plana: str) -> Optional[Usuario]:
        return self.validar_credenciales(correo_electronico, contrasenia_plana)

    def obtener_usuario_actual(self) -> Optional[Usuario]:
        return self.usuario_actual

    def esta_autenticado(self) -> bool:
        return self.usuario_actual is not None