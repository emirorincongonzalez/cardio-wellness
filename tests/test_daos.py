import pytest
from datetime import date, datetime
from decimal import Decimal


from src.modelos.cliente import Cliente
from src.persistencia.usuario_dao import UsuarioDAO
from src.persistencia.cliente_dao import ClienteDAO



def crear_cliente(correo: str) -> Cliente:
    """Crea un cliente de prueba."""
    return Cliente(
        nombre="Carlos",
        apellido="Perez",
        correo_electronico=correo,
        contrasenia_hash="Clave123!",
        edad=28,
        peso=82.5,
        altura=1.75,
        objetivo="Bajar de peso",
    )



def crear_usuario(correo: str):
    """Crea un usuario administrador de prueba."""
    from src.modelos.administrador import Administrador
    return Administrador(
        nombre="Usuario",
        apellido="Prueba",
        correo_electronico=correo,
        contrasenia_hash="Clave123!",
        edad=30,
    )



def test_usuario_dao():
    correo = "usuario.dao.prueba@example.com"
    dao = UsuarioDAO()
    
    usuario = Cliente(
        nombre="Usuario",
        apellido="Prueba",
        correo_electronico=correo,
        contrasenia_hash="Clave123!",
        edad=30,
        peso=70.0,
        altura=1.70,
        objetivo="Mantener condición",
    )
    
    usuario_guardado = None
    
    try:
        usuario_guardado = dao.guardar(usuario, contrasenia_plana="Clave123!")
        
        assert usuario_guardado.id_usuario is not None
        assert usuario_guardado.fecha_registro is not None
        
        usuario_encontrado = dao.buscar_por_correo(correo)
        assert usuario_encontrado is not None
        assert usuario_encontrado.correo_electronico == correo
    finally:
        if usuario_guardado:
            dao.eliminar_por_id(usuario_guardado.id_usuario)



def test_cliente_dao():
    correo = "cliente.dao.prueba@example.com"
    dao = ClienteDAO()
    
    cliente = Cliente(
        nombre="Carlos",
        apellido="Perez",
        correo_electronico=correo,
        contrasenia_hash="Clave123!",
        edad=28,
        peso=82.5,
        altura=1.75,
        objetivo="Bajar de peso",
    )
    
    cliente_guardado = None
    
    try:
        cliente_guardado = dao.guardar(cliente)
        
        assert cliente_guardado.id_usuario is not None
        assert cliente_guardado.fecha_registro is not None
        assert cliente_guardado.fecha_ingreso is not None
        
        cliente_encontrado = dao.buscar_por_id(cliente_guardado.id_usuario)
        
        assert cliente_encontrado is not None
        assert cliente_encontrado.nombre == "Carlos"
        assert cliente_encontrado.correo_electronico == correo
        assert cliente_encontrado.tipo_usuario == "cliente"
        assert float(cliente_encontrado.peso) == 82.5
        assert float(cliente_encontrado.altura) == 1.75
        assert cliente_encontrado.objetivo == "Bajar de peso"
        assert cliente_encontrado.fecha_ingreso is not None
        
        clientes = dao.listar()
        assert len(clientes) > 0
        assert any(c.id_usuario == cliente_guardado.id_usuario for c in clientes)
    finally:
        if cliente_guardado:
            dao.eliminar_por_id(cliente_guardado.id_usuario)
