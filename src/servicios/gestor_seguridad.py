import bcrypt


class GestorSeguridad:
    @staticmethod
    def generar_hash(contrasenia):
        contrasenia_bytes = contrasenia.encode("utf-8")
        return bcrypt.hashpw(
            contrasenia_bytes,
            bcrypt.gensalt()
        ).decode("utf-8")

    @staticmethod
    def verificar_contrasenia(contrasenia, hash_guardado):
        contrasenia_bytes = contrasenia.encode("utf-8")
        hash_bytes = hash_guardado.encode("utf-8")

        return bcrypt.checkpw(contrasenia_bytes, hash_bytes)