"""
Factory Method para la creación de usuarios.
Centraliza la lógica de instanciación de Administrador y Cliente.
"""

from typing import Dict, Any, Union

from src.modelos.administrador import Administrador
from src.modelos.cliente import Cliente
from src.modelos.usuario import Usuario


class FabricaUsuario:
    """
    Factory Method para crear objetos Usuario según su tipo.
    Sigue el patrón Factory Method para ocultar la lógica de instanciación.
    """
    
    @staticmethod
    def crear_usuario(tipo: str, datos: Dict[str, Any]) -> Union[Administrador, Cliente]:
        """
        Crea un objeto Usuario según el tipo especificado.
        
        Args:
            tipo: Tipo de usuario ('administrador' o 'cliente')
            datos: Diccionario con los datos del usuario
            
        Returns:
            Instancia de Administrador o Cliente
            
        Raises:
            ValueError: Si el tipo de usuario no es válido
        """
        tipo_normalizado = tipo.lower().strip()
        
        if tipo_normalizado == "administrador":
            return Administrador(
                nombre=datos.get("nombre", ""),
                apellido=datos.get("apellido", ""),
                correo_electronico=datos.get("correo_electronico", ""),
                contrasenia_hash=datos.get("contrasenia_hash", ""),
                edad=datos.get("edad", 0),
            )
        
        elif tipo_normalizado == "cliente":
            return Cliente(
                nombre=datos.get("nombre", ""),
                apellido=datos.get("apellido", ""),
                correo_electronico=datos.get("correo_electronico", ""),
                contrasenia_hash=datos.get("contrasenia_hash", ""),
                edad=datos.get("edad", 0),
                peso=datos.get("peso", 0.0),
                altura=datos.get("altura", 0.0),
                objetivo=datos.get("objetivo", ""),
            )
        
        else:
            raise ValueError(
                f"Tipo de usuario inválido: '{tipo}'. "
                "Los tipos válidos son: 'administrador', 'cliente'"
            )