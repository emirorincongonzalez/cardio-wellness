"""
Punto de entrada principal de la aplicación Cardio-Wellness.
"""

import sys
from pathlib import Path


# Permite ejecutar el proyecto desde la raíz:
# python -m src.main
ROOT_PROYECTO = Path(__file__).resolve().parent.parent

if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))


from src.controladores.control_autenticacion import (
    ControlAutenticacion,
)
from src.controladores.control_clientes import (
    ControlClientes,
)
from src.controladores.control_ejercicios import (
    ControlEjercicios,
)
from src.controladores.control_progreso import (
    ControlProgreso,
)
from src.controladores.control_rutinas import (
    ControlRutinas,
)
from src.controladores.control_sesiones import (
    ControlSesiones,
)

from src.interfaz.interfaz_login import InterfazLogin

from src.persistencia.asignacion_rutina_dao import (
    AsignacionRutinaDAO,
)
from src.persistencia.cliente_dao import ClienteDAO
from src.persistencia.ejercicio_dao import EjercicioDAO
from src.persistencia.progreso_mensual_dao import (
    ProgresoMensualDAO,
)
from src.persistencia.rutina_dao import RutinaDAO
from src.persistencia.sesion_entrenamiento_dao import (
    SesionEntrenamientoDAO,
)
from src.persistencia.usuario_dao import UsuarioDAO

from src.persistencia.conexion_bd import ConexionBD


def inicializar_sistema() -> dict:
    """
    Inicializa la conexión, los DAO y los controladores.
    """
    print("=" * 60)
    print("Sistema Cardio-Wellness - Gestion de Rutinas")
    print("=" * 60)

    bd = ConexionBD.obtener_instancia()

    try:
        bd.abrir_conexion()
        print("Conexion a base de datos inicializada")

        if bd.verificar_integridad():
            print("Integridad de la base de datos: OK")
        else:
            print(
                "Advertencia: verificacion de integridad "
                "fallida"
            )

        # Crear los DAO.
        rutina_dao = RutinaDAO()
        asignacion_dao = AsignacionRutinaDAO()
        usuario_dao = UsuarioDAO()
        cliente_dao = ClienteDAO()
        ejercicio_dao = EjercicioDAO()
        sesion_dao = SesionEntrenamientoDAO()
        progreso_dao = ProgresoMensualDAO()

        # Crear los controladores.
        control_auth = ControlAutenticacion(
            usuario_dao
        )

        control_clientes = ControlClientes(
            cliente_dao
        )

        control_ejercicios = ControlEjercicios(
            ejercicio_dao
        )

        control_rutinas = ControlRutinas(
            rutina_dao=rutina_dao,
            asignacion_dao=asignacion_dao,
        )

        control_sesiones = ControlSesiones(
            sesion_dao
        )

        # IMPORTANTE:
        # ControlProgreso necesita ambos DAO.
        control_progreso = ControlProgreso(
            progreso_dao=progreso_dao,
            sesion_dao=sesion_dao,
        )

        # Verificación temporal de las dependencias.
        print(
            "DAO de progreso:",
            type(
                control_progreso.progreso_dao
            ).__name__,
        )

        print(
            "DAO de sesiones:",
            type(
                control_progreso.sesion_dao
            ).__name__,
        )

        controladores = {
            "control_auth": control_auth,
            "control_clientes": control_clientes,
            "control_ejercicios": control_ejercicios,
            "control_rutinas": control_rutinas,
            "control_sesiones": control_sesiones,
            "control_progreso": control_progreso,
        }

        print("Controladores inicializados correctamente")
        print("=" * 60)

        return controladores

    except Exception as error:
        print(
            f"Error al inicializar el sistema: {error}"
        )
        raise


def iniciar_interfaz(controladores: dict) -> None:
    """
    Crea y ejecuta la ventana de inicio de sesión.
    """
    control_auth = controladores["control_auth"]

    app = InterfazLogin(
        control_autenticacion=control_auth,
        controladores=controladores,
    )

    app.mainloop()


def main() -> None:
    """
    Función principal de la aplicación.
    """
    bd = None

    try:
        controladores = inicializar_sistema()
        bd = ConexionBD.obtener_instancia()

        iniciar_interfaz(controladores)

    except KeyboardInterrupt:
        print("\nAplicacion terminada por el usuario")

    except Exception as error:
        print(
            f"\nError critico: {error}"
        )
        sys.exit(1)

    finally:
        try:
            if bd is not None:
                bd.cerrar_conexion()
                print(
                    "Conexion a base de datos cerrada"
                )
        except Exception:
            pass


if __name__ == "__main__":
    main()