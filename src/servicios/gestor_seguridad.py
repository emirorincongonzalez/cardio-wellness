import logging
import os
import re

import bcrypt


logger = logging.getLogger(__name__)



class GestorSeguridad:


    @classmethod
    def _obtener_rounds(cls):
        try:
            val = os.getenv("BCRYPT_ROUNDS") or os.getenv("ROUNDS")
            if val is not None:
                r = int(val)
                if 4 <= r <= 31:
                    return r
        except (ValueError, TypeError):
            pass
        return 12


    # Propiedad o getter para retrocompatibilidad
    @property
    def ROUNDS(self):
        return self._obtener_rounds()


    @staticmethod
    def validar_fortaleza_contrasena(contrasenia: str) -> bool:
        """
        Valida que la contrasena sea fuerte.
        
        Requisitos:
        - Minimo 8 caracteres
        - Al menos 1 mayuscula
        - Al menos 1 numero
        - Al menos 1 caracter especial
        
        Args:
            contrasenia: La contrasena a validar
            
        Returns:
            bool: True si es fuerte, False si es debil
        """
        if not isinstance(contrasenia, str):
            return False
        
        if len(contrasenia) < 8:
            return False
        
        # Verificar al menos 1 mayuscula
        if not any(c.isupper() for c in contrasenia):
            return False
        
        # Verificar al menos 1 numero
        if not any(c.isdigit() for c in contrasenia):
            return False
        
        # Verificar al menos 1 caracter especial
        caracteres_especiales = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(c in caracteres_especiales for c in contrasenia):
            return False
        
        return True


    @staticmethod
    def generar_hash(contrasenia):
        if not isinstance(contrasenia, str):
            raise ValueError("La contraseña debe ser un texto.")


        if not contrasenia.strip():
            raise ValueError("La contraseña no puede estar vacía.")


        # Validar fortaleza de la contrasena
        if not GestorSeguridad.validar_fortaleza_contrasena(contrasenia):
            raise ValueError(
                "La contraseña es muy debil. Debe tener al menos 8 caracteres, "
                "1 mayuscula, 1 numero y 1 caracter especial."
            )


        contrasenia_bytes = contrasenia.encode("utf-8")
        rounds = GestorSeguridad._obtener_rounds()


        return bcrypt.hashpw(
            contrasenia_bytes,
            bcrypt.gensalt(rounds=rounds),
        ).decode("utf-8")


    @staticmethod
    def verificar_contrasenia(
        contrasenia,
        hash_guardado,
    ):
        if not isinstance(contrasenia, str):
            logger.warning("Intento de verificación con contraseña inválida.")
            return False


        if not contrasenia.strip():
            logger.warning("Intento de verificación con contraseña vacía.")
            return False


        if not isinstance(hash_guardado, str):
            logger.warning("Intento de verificación con hash inválido.")
            return False


        if not hash_guardado.strip():
            logger.warning("Intento de verificación con hash vacío.")
            return False


        try:
            contrasenia_bytes = contrasenia.encode("utf-8")
            hash_bytes = hash_guardado.encode("utf-8")


            resultado = bcrypt.checkpw(
                contrasenia_bytes,
                hash_bytes,
            )


            if not resultado:
                logger.warning("Falló la verificación de contraseña.")


            return resultado


        except ValueError:
            logger.exception("El hash de contraseña tiene un formato inválido.")
            return False


        except Exception:
            logger.exception("Error inesperado al verificar contraseña.")
            return False