from src.controladores.control_base import ControlBase
from src.persistencia.usuario_dao import UsuarioDAO
from src.servicios.fabrica_usuario import FabricaUsuario
from src.servicios.gestor_seguridad import GestorSeguridad


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

    def registrar_administrador(
        self,
        nombre,
        apellido,
        correo_electronico,
        contrasenia_plana,
        edad,
    ):
        """
        Registra un nuevo administrador usando el Factory Method.
        
        Args:
            nombre: Nombre del administrador
            apellido: Apellido del administrador
            correo_electronico: Correo electrónico
            contrasenia_plana: Contraseña en texto plano
            edad: Edad del administrador
            
        Returns:
            Administrador creado
        """
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
        
        # Generar hash de contraseña
        contrasenia_hash = GestorSeguridad.generar_hash(contrasenia_plana)
        
        # Usar Factory Method para crear el administrador
        datos = {
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "correo_electronico": correo_electronico.strip(),
            "contrasenia_hash": contrasenia_hash,
            "edad": edad,
        }
        
        administrador = FabricaUsuario.crear_usuario("administrador", datos)
        
        # Guardar en BD
        try:
            admin_guardado = self.usuario_dao.guardar(administrador)
            self._registrar_log(admin_guardado.correo_electronico, "REGISTRO_ADMINISTRADOR")
            return admin_guardado
        except ValueError as error:
            raise ValueError(f"Error al registrar el administrador: {error}") from error
        except Exception as error:
            raise RuntimeError(f"Error inesperado al registrar administrador: {error}") from error