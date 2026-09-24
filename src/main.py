"""
Punto de entrada principal de la aplicación
Cardio-Wellness.
"""

import sys
from pathlib import Path


ROOT_PROYECTO = (
    Path(__file__).resolve().parent.parent
)

if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT_PROYECTO),
    )


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

from src.interfaz.interfaz_login import (
    InterfazLogin,
)

from src.persistencia.asignacion_rutina_dao import (
    AsignacionRutinaDAO,
)
from src.persistencia.cliente_dao import (
    ClienteDAO,
)
from src.persistencia.conexion_bd import (
    ConexionBD,
)
from src.persistencia.ejercicio_dao import (
    EjercicioDAO,
)
from src.persistencia.progreso_mensual_dao import (
    ProgresoMensualDAO,
)
from src.persistencia.rutina_dao import (
    RutinaDAO,
)
from src.persistencia.sesion_entrenamiento_dao import (
    SesionEntrenamientoDAO,
)
from src.persistencia.usuario_dao import (
    UsuarioDAO,
)


def inicializar_sistema() -> dict:
    """
    Inicializa conexión, DAO y controladores.
    """
    print("=" * 60)
    print(
        "Sistema Cardio-Wellness - "
        "Gestion de Rutinas"
    )
    print("=" * 60)

    bd = ConexionBD.obtener_instancia()

    try:
        bd.abrir_conexion()

        print(
            "Conexion a base de datos inicializada"
        )

        if bd.verificar_integridad():
            print(
                "Integridad de la base de datos: OK"
            )
        else:
            print(
                "Advertencia: verificacion de "
                "integridad fallida"
            )

        rutina_dao = RutinaDAO()
        asignacion_dao = AsignacionRutinaDAO()
        usuario_dao = UsuarioDAO()
        cliente_dao = ClienteDAO()
        ejercicio_dao = EjercicioDAO()
        sesion_dao = SesionEntrenamientoDAO()
        progreso_dao = ProgresoMensualDAO()

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

        control_progreso = ControlProgreso(
            progreso_dao=progreso_dao,
            sesion_dao=sesion_dao,
            cliente_dao=cliente_dao,
        )

        controladores = {
            "control_auth": control_auth,
            "control_autenticacion": control_auth,
            "control_clientes": control_clientes,
            "control_ejercicios": control_ejercicios,
            "control_rutinas": control_rutinas,
            "control_sesiones": control_sesiones,
            "control_progreso": control_progreso,
        }

        print(
            "Controladores inicializados "
            "correctamente"
        )

        print("=" * 60)

        return controladores

    except Exception as error:
        print(
            "Error al inicializar el sistema: "
            f"{error}"
        )
        raise


def iniciar_interfaz(
    controladores: dict,
) -> None:
    """
    Crea y ejecuta la interfaz gráfica de inicio de sesión.
    """
    control_auth = controladores[
        "control_auth"
    ]

    app = InterfazLogin(
        control_autenticacion=control_auth,
        controladores=controladores,
    )

    app.mainloop()


def mostrar_menu_principal() -> None:
    """
    Muestra el menú de consola.
    """
    print("\n=== CARDIO-WELLNESS ===")
    print("1. Iniciar sesión")
    print("2. Registrar cliente")
    print("3. Ver rutinas disponibles")
    print("4. Salir")


def iniciar_sesion_consola(
    control_auth: ControlAutenticacion,
) -> None:
    """
    Solicita credenciales e inicia sesión desde consola.
    """
    correo = input("Correo: ").strip()
    contrasena = input("Contraseña: ").strip()

    usuario = control_auth.iniciar_sesion(
        correo,
        contrasena,
    )

    if usuario is None:
        print("✗ Credenciales inválidas")
        return

    nombre = getattr(
        usuario,
        "nombre",
        "",
    )

    apellido = getattr(
        usuario,
        "apellido",
        "",
    )

    print(
        f"✓ Bienvenido, {nombre} {apellido}"
    )


def registrar_cliente_consola(
    control_clientes: ControlClientes,
) -> None:
    """
    Registra un cliente solicitando sus datos por consola.
    """
    try:
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        correo = input("Correo: ").strip()
        contrasena = input("Contraseña: ").strip()
        edad = int(
            input("Edad: ").strip()
        )
        peso = float(
            input("Peso (kg): ").strip()
        )
        altura = float(
            input("Altura (m): ").strip()
        )
        objetivo = input("Objetivo: ").strip()

        cliente = control_clientes.registrar_cliente(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            contrasena=contrasena,
            edad=edad,
            peso=peso,
            altura=altura,
            objetivo=objetivo,
        )

        print(
            "✓ Cliente registrado: "
            f"{cliente.nombre} {cliente.apellido}"
        )

    except ValueError as error:
        print(f"✗ Error: {error}")

    except Exception as error:
        print(f"✗ Error: {error}")


def mostrar_rutinas_consola(
    control_rutinas: ControlRutinas,
) -> None:
    """
    Muestra las rutinas disponibles por consola.
    """
    rutinas = control_rutinas.listar()

    if not rutinas:
        print("No hay rutinas disponibles")
        return

    print("\n=== RUTINAS DISPONIBLES ===")

    for rutina in rutinas:
        nivel = getattr(
            rutina,
            "nivel",
            "",
        )

        nivel_texto = getattr(
            nivel,
            "value",
            nivel,
        )

        print(
            f"Nombre: {rutina.nombre}"
        )
        print(
            f"Objetivo: {rutina.objetivo}"
        )
        print(
            f"Nivel: {nivel_texto}"
        )
        print("-" * 30)


def main(
    iniciar_gui: bool = False,
) -> None:
    """
    Ejecuta la aplicación.

    Si iniciar_gui es True, abre la interfaz gráfica.
    Si iniciar_gui es False, ejecuta el menú de consola,
    utilizado por las pruebas unitarias.
    """
    bd = None

    try:
        controladores = inicializar_sistema()

        try:
            bd = ConexionBD.obtener_instancia()
        except Exception:
            bd = None

        if iniciar_gui:
            iniciar_interfaz(controladores)
            return

        control_auth = controladores[
            "control_auth"
        ]

        control_clientes = controladores[
            "control_clientes"
        ]

        control_rutinas = controladores[
            "control_rutinas"
        ]

        while True:
            mostrar_menu_principal()

            opcion = input(
                "Seleccione una opción: "
            ).strip()

            if opcion == "1":
                iniciar_sesion_consola(
                    control_auth
                )

            elif opcion == "2":
                registrar_cliente_consola(
                    control_clientes
                )

            elif opcion == "3":
                mostrar_rutinas_consola(
                    control_rutinas
                )

            elif opcion == "4":
                print("\nSaliendo...")
                break

            else:
                print(
                    "Opción inválida. "
                    "Intente nuevamente."
                )

    except KeyboardInterrupt:
        print(
            "\n\nAplicación terminada por el usuario"
        )

    except Exception as error:
        print(
            f"\n✗ Error crítico: {error}"
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
    main(
        iniciar_gui=True,
    )