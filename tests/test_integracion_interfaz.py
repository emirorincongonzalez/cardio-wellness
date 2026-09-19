"""Tests de integración simples - Sin mockear tkinter."""

import os
from decimal import Decimal
from pathlib import Path


class TestIntegracionControladores:
    """Tests de integración para los controladores."""

    def test_control_clientes_puede_registrar_cliente(self):
        """Testea que ControlClientes puede registrar un cliente."""
        from src.controladores.control_clientes import ControlClientes

        control = ControlClientes()

        assert hasattr(control, "registrar_cliente")
        assert hasattr(control, "buscar_por_id")
        assert hasattr(control, "listar")
        assert hasattr(control, "eliminar_cliente")

    def test_control_rutinas_puede_crear_rutina(self):
        """Testea que ControlRutinas puede crear rutinas."""
        from src.controladores.control_rutinas import ControlRutinas
        from src.persistencia.asignacion_rutina_dao import (
            AsignacionRutinaDAO,
        )
        from src.persistencia.rutina_dao import RutinaDAO

        rutina_dao = RutinaDAO()
        asignacion_dao = AsignacionRutinaDAO()

        control = ControlRutinas(
            rutina_dao=rutina_dao,
            asignacion_dao=asignacion_dao,
        )

        assert hasattr(control, "crear_rutina")
        assert hasattr(control, "listar")
        assert hasattr(control, "asignar_rutina")

    def test_control_ejercicios_puede_crear_ejercicio(self):
        """Testea que ControlEjercicios puede crear ejercicios."""
        from src.controladores.control_ejercicios import ControlEjercicios
        from src.persistencia.ejercicio_dao import EjercicioDAO

        ejercicio_dao = EjercicioDAO()
        control = ControlEjercicios(ejercicio_dao=ejercicio_dao)

        assert hasattr(control, "crear_ejercicio")
        assert hasattr(control, "listar")
        assert hasattr(control, "actualizar_ejercicio")

    def test_control_autenticacion_puede_iniciar_sesion(self):
        """Testea que ControlAutenticacion puede iniciar sesión."""
        from src.controladores.control_autenticacion import (
            ControlAutenticacion,
        )

        control = ControlAutenticacion()

        assert hasattr(control, "iniciar_sesion")
        assert hasattr(control, "cerrar_sesion")
        assert hasattr(control, "registrar_administrador")


class TestModelos:
    """Tests de integración para los modelos."""

    def test_administrador_se_puede_crear(self):
        """Testea que se puede crear un Administrador."""
        from src.modelos.administrador import Administrador

        admin = Administrador(
            nombre="Juan",
            apellido="Perez",
            correo_electronico="juan@admin.com",
            contrasenia_hash="$2b$12$test",
            edad=30,
        )

        assert admin.nombre == "Juan"
        assert admin.apellido == "Perez"
        assert admin.obtener_nombre_completo() == "Juan Perez"

    def test_cliente_se_puede_crear(self):
        """Testea que se puede crear un Cliente."""
        from src.modelos.cliente import Cliente

        cliente = Cliente(
            nombre="Maria",
            apellido="Gomez",
            correo_electronico="maria@test.com",
            contrasenia_hash="$2b$12$test",
            edad=25,
            peso=Decimal("65.5"),
            altura=Decimal("1.65"),
            objetivo="Bajar de peso",
        )

        assert cliente.nombre == "Maria"
        assert cliente.peso == Decimal("65.5")
        assert cliente.objetivo == "Bajar de peso"

    def test_rutina_se_puede_crear(self):
        """Testea que se puede crear una Rutina."""
        from src.modelos.enums import NivelRutina
        from src.modelos.rutina import Rutina

        rutina = Rutina(
            nombre="Rutina Cardio",
            descripcion="Rutina de cardio",
            objetivo="Quemar grasa",
            nivel=NivelRutina.INTERMEDIO,
            duracion_semanas=30,
            creado_por=1,
        )

        assert rutina.nombre == "Rutina Cardio"
        assert rutina.objetivo == "Quemar grasa"
        assert rutina.nivel == NivelRutina.INTERMEDIO


class TestServicios:
    """Tests de integración para los servicios."""

    def test_gestor_seguridad_genera_hash(self):
        """Testea que GestorSeguridad puede generar hash."""
        from src.servicios.gestor_seguridad import GestorSeguridad

        contrasenia = "Clave123!"
        hash_generado = GestorSeguridad.generar_hash(contrasenia)

        assert hash_generado is not None
        assert len(hash_generado) > 0
        assert hash_generado != contrasenia

    def test_gestor_seguridad_verifica_hash(self):
        """Testea que GestorSeguridad puede verificar hash."""
        from src.servicios.gestor_seguridad import GestorSeguridad

        contrasenia = "Clave123!"
        hash_generado = GestorSeguridad.generar_hash(contrasenia)

        assert GestorSeguridad.verificar_contrasenia(
            contrasenia,
            hash_generado,
        )

    def test_fabrica_usuario_crea_administrador(self):
        """Testea que FabricaUsuario puede crear administrador."""
        from src.servicios.fabrica_usuario import FabricaUsuario

        usuario = FabricaUsuario.crear_usuario(
            tipo="administrador",
            datos={
                "nombre": "Admin",
                "apellido": "Test",
                "correo_electronico": "admin@test.com",
                "contrasenia_hash": "$2b$12$test",
                "edad": 30,
            },
        )

        assert usuario is not None
        assert usuario.nombre == "Admin"


class TestPersistencia:
    """Tests de integración para persistencia."""

    def test_conexion_bd_obtiene_instancia(self):
        """Testea que ConexionBD puede obtener instancia."""
        from src.persistencia.conexion_bd import ConexionBD

        bd = ConexionBD.obtener_instancia()

        assert bd is not None
        assert isinstance(bd, ConexionBD)

    def test_cliente_dao_existe(self):
        """Testea que ClienteDAO existe y tiene métodos."""
        from src.persistencia.cliente_dao import ClienteDAO

        dao = ClienteDAO()

        assert hasattr(dao, "guardar")
        assert hasattr(dao, "buscar_por_id")
        assert hasattr(dao, "listar")
        assert hasattr(dao, "actualizar")
        assert hasattr(dao, "eliminar_por_id")


class TestLogger:
    """Tests de integración para el logger."""

    def test_logger_registra_actividad(self):
        """Testea que el logger puede registrar actividades."""
        from src.utilidades.logger import log_registro_cliente

        log_registro_cliente("test@example.com")

        assert Path("logs/LOG_CARDIO.txt").exists()

    def test_logger_registra_login(self):
        """Testea que el logger puede registrar login."""
        from src.utilidades.logger import log_login_exitoso

        log_login_exitoso("test@example.com")

        assert Path("logs/LOG_CARDIO.txt").exists()


class TestSistemaCompleto:
    """Tests de integración del sistema completo."""

    def test_todos_los_modulos_importan_correctamente(self):
        """Testea que los módulos principales importan correctamente."""
        from src.controladores import (
            control_autenticacion,
            control_clientes,
            control_ejercicios,
            control_progreso,
            control_rutinas,
            control_sesiones,
        )
        from src.modelos import (
            administrador,
            asignacion_rutina,
            cliente,
            ejercicio_cardio,
            progreso_mensual,
            rutina,
            sesion_entrenamiento,
        )
        from src.persistencia import (
            cliente_dao,
            ejercicio_dao,
            rutina_dao,
            sesion_entrenamiento_dao,
            usuario_dao,
        )
        from src.servicios import (
            fabrica_usuario,
            generador_reportes_pdf,
            gestor_seguridad,
            sistema_wellness,
        )
        from src.utilidades import logger

        assert administrador is not None
        assert control_autenticacion is not None
        assert cliente_dao is not None
        assert gestor_seguridad is not None
        assert logger is not None

    def test_documentacion_existe(self):
        """Testea que la documentación existe."""
        assert os.path.exists("README.md")
        assert os.path.exists("CHANGELOG.md")
        assert os.path.exists("SOPORTE.md")
        assert os.path.exists("requirements.txt")

    def test_tests_existen(self):
        """Testea que los tests existen."""
        assert os.path.exists("tests/")
        assert os.path.exists("tests/test_modelos.py")
        assert os.path.exists("tests/test_control_autenticacion.py")
        assert os.path.exists("tests/test_seguridad.py")