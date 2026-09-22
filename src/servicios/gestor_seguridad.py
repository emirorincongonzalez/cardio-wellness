import logging
import os

try:
    import bcrypt
except ImportError as error:
    raise ImportError(
        "No se pudo importar bcrypt. "
        "Instálalo con: python -m pip install bcrypt"
    ) from error


logger = logging.getLogger(__name__)


class GestorSeguridad:
    """
    Gestiona el hash y la verificación de contraseñas.
    Utiliza bcrypt.
    """

    @classmethod
    def _obtener_rounds(cls) -> int:
        """
        Obtiene el costo de bcrypt desde una variable de entorno.
        """
        valor = (
            os.getenv("BCRYPT_ROUNDS")
            or os.getenv("ROUNDS")
        )

        if valor is not None:
            try:
                rounds = int(valor)

                if 4 <= rounds <= 31:
                    return rounds

            except (TypeError, ValueError):
                logger.warning(
                    "Valor inválido para BCRYPT_ROUNDS: %s",
                    valor,
                )

        return 12

    @property
    def ROUNDS(self) -> int:
        """
        Propiedad de compatibilidad.
        """
        return self._obtener_rounds()

    @staticmethod
    def validar_fortaleza_contrasena(
        contrasenia: str,
    ) -> bool:
        """
        Valida que la contraseña cumpla los requisitos mínimos:
        - Al menos 8 caracteres.
        - Una letra mayúscula.
        - Un número.
        - Un carácter especial.
        """
        if not isinstance(contrasenia, str):
            return False

        if len(contrasenia) < 8:
            return False

        if not any(
            caracter.isupper()
            for caracter in contrasenia
        ):
            return False

        if not any(
            caracter.isdigit()
            for caracter in contrasenia
        ):
            return False

        caracteres_especiales = (
            "!@#$%^&*()_+-=[]{}|;:,.<>?"
        )

        if not any(
            caracter in caracteres_especiales
            for caracter in contrasenia
        ):
            return False

        return True

    @classmethod
    def generar_hash(
        cls,
        contrasenia: str,
    ) -> str:
        """
        Genera un hash bcrypt para una contraseña.
        """
        if not isinstance(contrasenia, str):
            raise ValueError(
                "La contraseña debe ser un texto."
            )

        if not contrasenia:
            raise ValueError(
                "La contraseña no puede estar vacía."
            )

        if not cls.validar_fortaleza_contrasena(
            contrasenia
        ):
            raise ValueError(
                "La contraseña es muy débil. "
                "Debe tener al menos 8 caracteres, "
                "una mayúscula, un número y un "
                "carácter especial."
            )

        try:
            contrasenia_bytes = (
                contrasenia.encode("utf-8")
            )

            if len(contrasenia_bytes) > 72:
                raise ValueError(
                    "La contraseña no puede superar "
                    "los 72 bytes."
                )

            salt = bcrypt.gensalt(
                rounds=cls._obtener_rounds()
            )

            hash_bytes = bcrypt.hashpw(
                contrasenia_bytes,
                salt,
            )

            return hash_bytes.decode("utf-8")

        except ValueError:
            raise

        except Exception as error:
            logger.exception(
                "No se pudo generar el hash."
            )

            raise RuntimeError(
                "Error al generar el hash de "
                "la contraseña."
            ) from error

    @staticmethod
    def verificar_contrasenia(
        contrasenia: str,
        hash_guardado: str,
    ) -> bool:
        """
        Verifica una contraseña contra un hash bcrypt.
        """
        if not isinstance(contrasenia, str):
            logger.warning(
                "La contraseña recibida no es válida."
            )
            return False

        if not contrasenia:
            logger.warning(
                "Se intentó verificar una contraseña vacía."
            )
            return False

        if not isinstance(hash_guardado, str):
            logger.warning(
                "El hash guardado no es texto."
            )
            return False

        if not hash_guardado:
            logger.warning(
                "El hash guardado está vacío."
            )
            return False

        try:
            contrasenia_bytes = (
                contrasenia.encode("utf-8")
            )

            hash_bytes = (
                hash_guardado.encode("utf-8")
            )

            if len(contrasenia_bytes) > 72:
                return False

            return bool(
                bcrypt.checkpw(
                    contrasenia_bytes,
                    hash_bytes,
                )
            )

        except (
            ValueError,
            TypeError,
            UnicodeEncodeError,
        ):
            logger.warning(
                "El hash bcrypt tiene un formato inválido."
            )
            return False

        except Exception:
            logger.exception(
                "Error inesperado al verificar "
                "la contraseña."
            )
            return False

    @classmethod
    def hash_valido(
        cls,
        hash_guardado: str,
    ) -> bool:
        """
        Comprueba si un texto tiene una estructura
        reconocible de hash bcrypt.
        """
        if not isinstance(hash_guardado, str):
            return False

        hash_limpio = hash_guardado.strip()

        return hash_limpio.startswith(
            ("$2a$", "$2b$", "$2y$")
        )

    @classmethod
    def necesita_rehash(
        cls,
        hash_guardado: str,
    ) -> bool:
        """
        Indica si el hash usa un costo diferente
        al configurado actualmente.
        """
        if not cls.hash_valido(hash_guardado):
            return True

        try:
            partes = hash_guardado.split("$")

            if len(partes) < 3:
                return True

            rounds_actuales = int(partes[2])

            return (
                rounds_actuales
                != cls._obtener_rounds()
            )

        except (TypeError, ValueError):
            return True