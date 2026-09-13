"""
Limpieza mensual de registros temporales y mantenimiento.
Ejecutar mensualmente para mantener el sistema optimizado.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.persistencia.conexion_bd import ConexionBD


def limpiar_registros_temporales():
    """Elimina registros temporales antiguos (>30 días)."""
    
    print("=" * 60)
    print("Limpieza Mensual - Cardio-Wellness")
    print("=" * 60)
    
    try:
        bd = ConexionBD.obtener_instancia()
        bd.abrir_conexion()
        
        # 1. Eliminar backups antiguos (>90 días)
        print("\n🗑️  Limpiando backups antiguos...")
        backup_dir = Path(__file__).parent.parent / "backups"
        if backup_dir.exists():
            backups_viejos = [
                f for f in backup_dir.glob("*.sql")
                if datetime.fromtimestamp(f.stat().st_mtime) < (datetime.now() - timedelta(days=90))
            ]
            for backup in backups_viejos:
                backup.unlink()
                print(f"   ✓ Eliminado: {backup.name}")
        
        # 2. Verificar integridad
        print("\n✅ Verificando integridad de la base de datos...")
        if bd.verificar_integridad():
            print("   ✓ Integridad: OK")
        else:
            print("   ⚠️  Advertencia: Problemas de integridad detectados")
        
        bd.cerrar_conexion()
        
        print("\n✓ Limpieza mensual completada exitosamente")
        return True
        
    except Exception as e:
        print(f"\n✗ Error en limpieza: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    exit(0 if limpiar_registros_temporales() else 1)