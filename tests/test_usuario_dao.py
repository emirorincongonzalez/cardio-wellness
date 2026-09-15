import pytest
from datetime import date, datetime
from decimal import Decimal


from src.modelos.cliente import Cliente
from src.modelos.administrador import Administrador
from src.persistencia.usuario_dao import UsuarioDAO




@pytest.fixture
def dao():
    return UsuarioDAO()




def crear_usuario(correo: str) -> Administrador:
    """Crea un usuario administrador de prueba."""
    return Administrador(
        nombre="Usuario",
        apellido="Prueba",
        correo_electronico=correo,
        contrasenia_hash="Clave123!",
        edad=30,
    )




def test_usuario_dao_guardar(dao):
    correo = "usuario.dao.guardar@example.com"
    usuario = crear_usuario(correo)
    
    usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
    
    assert usuario_guardado.id_usuario is not None
    assert usuario_guardado.fecha_registro is not None
    assert usuario_guardado.tipo_usuario == "administrador"
    
    # Limpieza
    dao.eliminar_por_id(usuario_guardado.id_usuario)




def test_usuario_dao_buscar_por_correo(dao):
    correo = "usuario.buscar.correo@example.com"
    usuario = crear_usuario(correo)
    
    usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
    
    usuario_encontrado = dao.buscar_por_correo(correo)
    
    assert usuario_encontrado is not None
    assert usuario_encontrado.id_usuario == usuario_guardado.id_usuario
    assert usuario_encontrado.correo_electronico == correo
    
    # Limpieza
    dao.eliminar_por_id(usuario_guardado.id_usuario)




def test_usuario_dao_actualizar(dao):
    correo = "usuario.actualizar@example.com"
    usuario = crear_usuario(correo)
    
    usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
    usuario_guardado.nombre = "NombreActualizado"
    
    usuario_actualizado = dao.actualizar(usuario_guardado)
    
    assert usuario_actualizado.nombre == "NombreActualizado"
    
    usuario_encontrado = dao.buscar_por_correo(correo)
    assert usuario_encontrado.nombre == "NombreActualizado"
    
    # Limpieza
    dao.eliminar_por_id(usuario_guardado.id_usuario)




def test_usuario_dao_actualizar_correo(dao):
    correo_original = "usuario.correo.original@example.com"
    correo_nuevo = "usuario.correo.nuevo@example.com"
    usuario = crear_usuario(correo_original)
    
    usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
    usuario_guardado.correo_electronico = correo_nuevo
    
    dao.actualizar(usuario_guardado)
    
    usuario_encontrado = dao.buscar_por_correo(correo_nuevo)
    assert usuario_encontrado is not None
    assert usuario_encontrado.correo_electronico == correo_nuevo
    
    # Limpieza
    dao.eliminar_por_id(usuario_guardado.id_usuario)




def test_usuario_dao_actualizar_preserva_hash(dao):
    correo = "usuario.preservar.hash@example.com"
    usuario = crear_usuario(correo)
    
    usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
    
    # ✅ Busca de nuevo para obtener el hash real de la BD
    usuario_fresh = dao.buscar_por_correo(correo)
    hash_original = usuario_fresh.contrasenia_hash
    
    usuario_guardado.nombre = "NombreActualizado"
    dao.actualizar(usuario_guardado)
    
    usuario_encontrado = dao.buscar_por_correo(correo)
    assert usuario_encontrado.contrasenia_hash == hash_original
    
    # Limpieza
    dao.eliminar_por_id(usuario_guardado.id_usuario)




def test_usuario_dao_actualizar_usuario_inexistente(dao):
    usuario = crear_usuario("usuario.inexistente@example.com")
    usuario.id_usuario = 999999999
    
    with pytest.raises(ValueError, match="No se encontró el usuario"):
        dao.actualizar(usuario)




def test_usuario_dao_eliminar_retorna_true(dao):
    correo = "usuario.eliminar.true@example.com"
    usuario = crear_usuario(correo)
    
    usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
    
    resultado = dao.eliminar_por_id(usuario_guardado.id_usuario)
    
    assert resultado is True
    
    usuario_encontrado = dao.buscar_por_correo(correo)
    assert usuario_encontrado is None




def test_usuario_dao_rechaza_correo_duplicado(dao):
    import time
    correo = f"usuario.duplicado.{int(time.time())}@example.com"
    usuario = crear_usuario(correo)
    
    dao.guardar(usuario, contrasenia_plana="Clave123!")
    
    segundo_usuario = crear_usuario(correo)
    
    with pytest.raises(ValueError, match="El correo ya está registrado"):
        dao.guardar(segundo_usuario, contrasenia_plana="Clave123!")
    
    # Limpieza
    dao.eliminar_por_id(usuario.id_usuario)
