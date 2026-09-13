"""
Punto de entrada principal de la aplicación Cardio-Wellness.
"""

import sys
from pathlib import Path

# Agregar el root del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.controladores.control_autenticacion import ControlAutenticacion
from src.controladores.control_clientes import ControlClientes
from src.controladores.control_rutinas import ControlRutinas
from src.persistencia.conexion_bd import ConexionBD


def inicializar_sistema():
    """
    Inicializa el sistema Cardio-Wellness.
    
    Returns:
        dict: Diccionario con los controladores inicializados
    """
    print("=" * 60)
    print("Sistema Cardio-Wellness - Gestión de Rutinas")
    print("=" * 60)
    
    # Inicializar conexión a BD
    try:
        bd = ConexionBD.obtener_instancia()
        bd.abrir_conexion()
        print("✓ Conexión a base de datos inicializada")
        
        # Verificar integridad
        if bd.verificar_integridad():
            print("✓ Integridad de la base de datos: OK")
        else:
            print("⚠ Advertencia: Verificación de integridad fallida")
    except Exception as e:
        print(f"✗ Error al conectar a la base de datos: {e}")
        raise
    
    # Inicializar controladores
    try:
        control_auth = ControlAutenticacion()
        control_clientes = ControlClientes()
        control_rutinas = ControlRutinas()
        
        print("✓ Sistema inicializado correctamente")
        print("=" * 60)
        
        return {
            "control_auth": control_auth,
            "control_clientes": control_clientes,
            "control_rutinas": control_rutinas,
        }
    except Exception as e:
        print(f"✗ Error al inicializar el sistema: {e}")
        raise


def main():
    """Función principal de la aplicación."""
    try:
        controles = inicializar_sistema()
        control_auth = controles["control_auth"]
        control_clientes = controles["control_clientes"]
        control_rutinas = controles["control_rutinas"]
        
        # Menú de consola (backend only)
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Iniciar sesión")
        print("2. Registrar cliente")
        print("3. Ver rutinas disponibles")
        print("4. Salir")
        
        while True:
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == "1":
                correo = input("Correo: ").strip()
                contrasenia = input("Contraseña: ").strip()
                
                usuario = control_auth.iniciar_sesion(correo, contrasenia)
                
                if usuario:
                    print(f"✓ Bienvenido, {usuario.nombre} {usuario.apellido}")
                else:
                    print("✗ Credenciales inválidas")
            
            elif opcion == "2":
                print("\n=== REGISTRAR CLIENTE ===")
                nombre = input("Nombre: ").strip()
                apellido = input("Apellido: ").strip()
                correo = input("Correo: ").strip()
                contrasenia = input("Contraseña: ").strip()
                edad = int(input("Edad: ").strip())
                peso = float(input("Peso (kg): ").strip())
                altura = float(input("Altura (m): ").strip())
                objetivo = input("Objetivo: ").strip()
                
                try:
                    cliente = control_clientes.registrar_cliente(
                        nombre=nombre,
                        apellido=apellido,
                        correo_electronico=correo,
                        contrasenia_plana=contrasenia,
                        edad=edad,
                        peso=peso,
                        altura=altura,
                        objetivo=objetivo,
                    )
                    print(f"✓ Cliente registrado: {cliente.nombre} {cliente.apellido}")
                except Exception as e:
                    print(f"✗ Error: {e}")
            
            elif opcion == "3":
                print("\n=== RUTINAS DISPONIBLES ===")
                rutinas = control_rutinas.listar()
                
                if not rutinas:
                    print("No hay rutinas disponibles")
                else:
                    for i, rutina in enumerate(rutinas, 1):
                        nivel = rutina.nivel.value if hasattr(rutina.nivel, 'value') else str(rutina.nivel)
                        print(f"{i}. {rutina.nombre} - {rutina.objetivo} ({nivel})")
            
            elif opcion == "4":
                print("\nSaliendo...")
                break
            
            else:
                print("Opción inválida. Intente nuevamente.")
        
    except KeyboardInterrupt:
        print("\n\nAplicación terminada por el usuario")
    except Exception as e:
        print(f"\n✗ Error crítico: {e}")
        sys.exit(1)
    finally:
        # Cerrar conexión
        try:
            bd = ConexionBD.obtener_instancia()
            bd.cerrar_conexion()
        except Exception:
            pass


if __name__ == "__main__":
    main()