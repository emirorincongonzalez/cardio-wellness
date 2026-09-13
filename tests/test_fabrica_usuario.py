"""
Tests para FabricaUsuario (Factory Method).
"""

import pytest

from src.servicios.fabrica_usuario import FabricaUsuario
from src.modelos.administrador import Administrador
from src.modelos.cliente import Cliente


def test_fabrica_crear_administrador():
    """Prueba crear administrador con Factory."""
    datos = {
        "nombre": "Admin",
        "apellido": "Test",
        "correo_electronico": "admin@test.com",
        "contrasenia_hash": "hash123",
        "edad": 30,
    }
    
    usuario = FabricaUsuario.crear_usuario("administrador", datos)
    
    assert isinstance(usuario, Administrador)
    assert usuario.nombre == "Admin"
    assert usuario.apellido == "Test"


def test_fabrica_crear_cliente():
    """Prueba crear cliente con Factory."""
    datos = {
        "nombre": "Cliente",
        "apellido": "Test",
        "correo_electronico": "cliente@test.com",
        "contrasenia_hash": "hash123",
        "edad": 25,
        "peso": 70.0,
        "altura": 1.75,
        "objetivo": "Perder peso",
    }
    
    usuario = FabricaUsuario.crear_usuario("cliente", datos)
    
    assert isinstance(usuario, Cliente)
    assert usuario.nombre == "Cliente"
    assert usuario.peso == 70.0


def test_fabrica_tipo_invalido():
    """Prueba que tipo inválido lanza ValueError."""
    datos = {"nombre": "Test"}
    
    with pytest.raises(ValueError, match="Tipo de usuario inválido"):
        FabricaUsuario.crear_usuario("tipo_invalido", datos)


def test_fabrica_mayusculas_minusculas():
    """Prueba que factory maneja mayúsculas/minúsculas."""
    datos_admin = {
        "nombre": "Admin",
        "apellido": "Test",
        "correo_electronico": "admin@test.com",
        "contrasenia_hash": "hash123",
        "edad": 30,
    }
    
    # Probar con diferentes formatos
    usuario1 = FabricaUsuario.crear_usuario("ADMINISTRADOR", datos_admin)
    usuario2 = FabricaUsuario.crear_usuario("administrador", datos_admin)
    usuario3 = FabricaUsuario.crear_usuario("Administrador", datos_admin)
    
    assert isinstance(usuario1, Administrador)
    assert isinstance(usuario2, Administrador)
    assert isinstance(usuario3, Administrador)