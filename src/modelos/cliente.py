from datetime import date
from decimal import Decimal
from typing import Optional, Union

from src.modelos.usuario import Usuario


class Cliente(Usuario):
    """
    Representa a un cliente del sistema Cardio Wellness.

    El tipo de usuario se fuerza siempre a "cliente".
    """

    MARGEN_MANTENIMIENTO = Decimal("4.0")

    GENEROS_VALIDOS = {
        "HOMBRE",
        "MUJER",
        "OTRO",
        "PREFIERO NO DECIRLO",
    }

    def __init__(
        self,
        nombre: str,
        apellido: str,
        correo_electronico: str,
        contrasenia_hash: str,
        edad: int,
        genero: str,
        peso: Union[
            int,
            float,
            Decimal,
        ],
        altura: Union[
            int,
            float,
            Decimal,
        ],
        objetivo: str,
        peso_objetivo: Optional[
            Union[
                int,
                float,
                Decimal,
            ]
        ] = None,
        id_usuario: Optional[int] = None,
        fecha_registro: Optional[date] = None,
        fecha_ingreso: Optional[date] = None,
    ) -> None:
        super().__init__(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=(
                correo_electronico
            ),
            contrasenia_hash=contrasenia_hash,
            edad=edad,
            tipo_usuario="cliente",
            id_usuario=id_usuario,
            fecha_registro=fecha_registro,
        )

        self.genero = genero
        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo

        if peso_objetivo is None:
            peso_objetivo = peso

        self.peso_objetivo = peso_objetivo
        self.fecha_ingreso = fecha_ingreso

    @property
    def genero(self) -> str:
        """
        Género del cliente.
        """
        return self._genero

    @genero.setter
    def genero(
        self,
        valor: str,
    ) -> None:
        """
        Valida el género del cliente.
        """
        if not isinstance(valor, str):
            raise ValueError(
                "El género debe ser texto."
            )

        genero = valor.strip().upper()

        if genero not in self.GENEROS_VALIDOS:
            raise ValueError(
                (
                    "El género debe ser HOMBRE, MUJER, "
                    "OTRO o PREFIERO NO DECIRLO."
                )
            )

        self._genero = genero

    @property
    def peso(self) -> Decimal:
        """
        Peso actual del cliente.
        """
        return self._peso

    @peso.setter
    def peso(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if (
            not isinstance(
                valor,
                (
                    int,
                    float,
                    Decimal,
                ),
            )
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "El peso debe ser mayor que cero."
            )

        self._peso = Decimal(str(valor))

    @property
    def peso_objetivo(self) -> Decimal:
        """
        Peso objetivo del cliente.
        """
        return self._peso_objetivo

    @peso_objetivo.setter
    def peso_objetivo(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if (
            not isinstance(
                valor,
                (
                    int,
                    float,
                    Decimal,
                ),
            )
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                (
                    "El peso objetivo debe ser "
                    "mayor que cero."
                )
            )

        self._peso_objetivo = Decimal(
            str(valor)
        )

    @property
    def altura(self) -> Decimal:
        """
        Altura del cliente.
        """
        return self._altura

    @altura.setter
    def altura(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if (
            not isinstance(
                valor,
                (
                    int,
                    float,
                    Decimal,
                ),
            )
            or isinstance(valor, bool)
            or valor <= 0
        ):
            raise ValueError(
                "La altura debe ser mayor que cero."
            )

        self._altura = Decimal(str(valor))

    @property
    def objetivo(self) -> str:
        """
        Meta general del cliente.
        """
        return self._objetivo

    @objetivo.setter
    def objetivo(
        self,
        valor: str,
    ) -> None:
        if (
            not isinstance(valor, str)
            or not valor.strip()
        ):
            raise ValueError(
                "El objetivo no puede estar vacío."
            )

        self._objetivo = valor.strip()

    @property
    def fecha_ingreso(self) -> date:
        """
        Fecha de ingreso del cliente.
        """
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(
        self,
        valor: Optional[date],
    ) -> None:
        self._fecha_ingreso = (
            valor
            if valor is not None
            else date.today()
        )

    def actualizar_peso(
        self,
        nuevo_peso: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        """
        Actualiza el peso actual.
        """
        self.peso = nuevo_peso

    def actualizar_peso_objetivo(
        self,
        nuevo_peso_objetivo: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        """
        Actualiza el peso objetivo.
        """
        self.peso_objetivo = (
            nuevo_peso_objetivo
        )

    def actualizar_objetivo(
        self,
        nuevo_objetivo: str,
    ) -> None:
        """
        Actualiza la meta general.
        """
        self.objetivo = nuevo_objetivo

    def _objetivo_normalizado(self) -> str:
        """
        Devuelve el objetivo normalizado.
        """
        return (
            self.objetivo
            .strip()
            .lower()
        )

    def obtener_rango_mantenimiento(
        self,
    ) -> tuple:
        """
        Devuelve el rango válido para mantener peso.
        """
        margen = self.MARGEN_MANTENIMIENTO

        minimo = (
            self.peso_objetivo - margen
        )

        maximo = (
            self.peso_objetivo + margen
        )

        return minimo, maximo

    def meta_alcanzada(self) -> bool:
        """
        Indica si el cliente alcanzó su meta.
        """
        peso_actual = self.peso
        peso_objetivo = self.peso_objetivo
        objetivo = self._objetivo_normalizado()

        if objetivo in {
            "bajar de peso",
            "bajar peso",
        }:
            return peso_actual <= peso_objetivo

        if objetivo in {
            "subir de peso",
            "subir peso",
        }:
            return peso_actual >= peso_objetivo

        if objetivo in {
            "mantener peso",
            "mantener",
        }:
            minimo, maximo = (
                self.obtener_rango_mantenimiento()
            )

            return (
                minimo
                <= peso_actual
                <= maximo
            )

        return False

    def obtener_estado_meta(self) -> str:
        """
        Devuelve el estado de la meta.
        """
        if self.meta_alcanzada():
            return "META ALCANZADA"

        return "EN PROGRESO"

    def obtener_diferencia_meta(self) -> Decimal:
        """
        Devuelve los kilogramos restantes.
        """
        peso_actual = self.peso
        peso_objetivo = self.peso_objetivo
        objetivo = self._objetivo_normalizado()

        if objetivo in {
            "bajar de peso",
            "bajar peso",
        }:
            return max(
                Decimal("0"),
                peso_actual - peso_objetivo,
            )

        if objetivo in {
            "subir de peso",
            "subir peso",
        }:
            return max(
                Decimal("0"),
                peso_objetivo - peso_actual,
            )

        if objetivo in {
            "mantener peso",
            "mantener",
        }:
            minimo, maximo = (
                self.obtener_rango_mantenimiento()
            )

            if peso_actual < minimo:
                return minimo - peso_actual

            if peso_actual > maximo:
                return peso_actual - maximo

            return Decimal("0")

        return abs(
            peso_actual - peso_objetivo
        )

    def obtener_descripcion_meta(self) -> str:
        """
        Devuelve una descripción de la meta.
        """
        objetivo = self._objetivo_normalizado()

        if objetivo in {
            "mantener peso",
            "mantener",
        }:
            minimo, maximo = (
                self.obtener_rango_mantenimiento()
            )

            return (
                "Rango objetivo: "
                f"{minimo:.1f} - {maximo:.1f} kg"
            )

        return (
            "Peso objetivo: "
            f"{self.peso_objetivo:.1f} kg"
        )

    def obtener_progreso_meta(self) -> float:
        """
        Devuelve el porcentaje básico de progreso.
        """
        if self.meta_alcanzada():
            return 100.0

        return 0.0

    def obtener_tipo_usuario(self) -> str:
        """
        Devuelve el tipo de usuario.
        """
        return "cliente"

    def __repr__(self) -> str:
        return (
            "Cliente("
            f"id_usuario={self.id_usuario}, "
            f"nombre='{self.nombre}', "
            f"correo='{self.correo_electronico}', "
            f"edad={self.edad}, "
            f"genero='{self.genero}', "
            f"peso={self.peso}, "
            f"peso_objetivo={self.peso_objetivo}, "
            f"altura={self.altura}, "
            f"objetivo='{self.objetivo}', "
            f"fecha_ingreso={self.fecha_ingreso}"
            ")"
        )