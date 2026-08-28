import logging
import os

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
    def generar_hash(contrasenia):
        if not isinstance(contrasenia, str):
            raise ValueError("La contraseña debe ser un texto.")

        if not contrasenia.strip():
            raise ValueError("La contraseña no puede estar vacía.")

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