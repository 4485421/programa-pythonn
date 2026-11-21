from __future__ import annotations

from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Any, Dict, Optional

from entidades import EntidadBase
from excepciones import (
    CalculoInconsistenteError,
    ErrorSoftwareFJ,
    ServicioNoDisponibleError,
    ValidacionEntidadError,
)


class Servicio(EntidadBase, ABC):
    """Clase abstracta para servicios de Software FJ."""

    def __init__(
        self,
        id_entidad: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
        parametros: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(id_entidad)
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible
        self._parametros: Dict[str, Any] = parametros or {}
        self.validar_parametros(self._parametros)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionEntidadError(
                "El nombre del servicio debe tener al menos 3 caracteres.",
                detalles={"servicio_id": self._id_entidad, "nombre": valor},
            )
        self._nombre = valor.strip()

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or isinstance(valor, bool) or valor <= 0:
            raise CalculoInconsistenteError(
                "La tarifa base debe ser un número positivo mayor que cero.",
                detalles={"servicio_id": self._id_entidad, "tarifa_base": valor},
            )
        self._tarifa_base = float(valor)

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ValidacionEntidadError(
                "El campo 'disponible' debe ser booleano.",
                detalles={"servicio_id": self._id_entidad, "disponible": valor},
            )
        self._disponible = valor

    @property
    def parametros(self) -> Dict[str, Any]:
        return dict(self._parametros)

    @abstractmethod
    def validar_parametros(self, parametros: Dict[str, Any]) -> None:
        """Valida los parámetros específicos del servicio."""

    @abstractmethod
    def calcular_costo(self, duracion: float) -> float:
        """Calcula el costo base según la duración o cantidad."""

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción detallada del servicio."""

    @singledispatchmethod
    def calcular_costo_ajustado(self, ajuste: Any, impuesto: float = 0.19) -> float:
        raise CalculoInconsistenteError(
            "Tipo de parámetro no soportado para calcular_costo_ajustado.",
            detalles={"servicio_id": self._id_entidad, "tipo": type(ajuste).__name__},
        )

    @calcular_costo_ajustado.register
    def _(self, duracion: int, impuesto: float = 0.19) -> float:
        return self._calcular_total(float(duracion), descuento_pct=0.0, impuesto=impuesto)

    @calcular_costo_ajustado.register
    def _(self, duracion: float, impuesto: float = 0.19) -> float:
        return self._calcular_total(duracion, descuento_pct=0.0, impuesto=impuesto)

    @calcular_costo_ajustado.register
    def _(self, config: dict, impuesto: float = 0.19) -> float:
        if "duracion" not in config:
            raise ValidacionEntidadError(
                "Falta la clave obligatoria 'duracion' en config.",
                detalles={"servicio_id": self._id_entidad, "config": config},
            )
        descuento_pct = float(config.get("descuento_pct", 0.0))
        impuesto_custom = float(config.get("impuesto", impuesto))
        return self._calcular_total(
            float(config["duracion"]),
            descuento_pct=descuento_pct,
            impuesto=impuesto_custom,
        )

    def _calcular_total(
        self,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto: float = 0.19,
    ) -> float:
        try:
            if not (0.0 <= descuento_pct < 1.0):
                raise CalculoInconsistenteError(
                    "El descuento debe estar entre 0.0 y menor que 1.0.",
                    detalles={"descuento_pct": descuento_pct},
                )
            if not (0.0 <= impuesto <= 0.50):
                raise CalculoInconsistenteError(
                    "El impuesto debe estar entre 0.0 y 0.50.",
                    detalles={"impuesto": impuesto},
                )
            subtotal = self.calcular_costo(duracion)
            con_descuento = subtotal * (1.0 - descuento_pct)
            total = con_descuento * (1.0 + impuesto)
            if total <= 0:
                raise CalculoInconsistenteError(
                    "El total calculado debe ser mayor que cero.",
                    detalles={"subtotal": subtotal, "total": total},
                )
            return round(total, 2)
        except ErrorSoftwareFJ:
            raise
        except Exception as exc:
            raise CalculoInconsistenteError(
                "Error inesperado calculando el costo total del servicio.",
                detalles={"servicio_id": self._id_entidad, "duracion": duracion},
            ) from exc

    def resumen(self) -> str:
        estado = "DISPONIBLE" if self._disponible else "NO DISPONIBLE"
        return (
            f"[Servicio {self._id_entidad}] {self._nombre} | "
            f"Base: ${self._tarifa_base:,.2f} | {estado}"
        )


class ReservaSala(Servicio):
    """Servicio para reserva de salas de reuniones o capacitación."""

    def validar_parametros(self, parametros: Dict[str, Any]) -> None:
        if "capacidad_personas" not in parametros or "ubicacion" not in parametros:
            raise ValidacionEntidadError(
                "ReservaSala requiere 'capacidad_personas' y 'ubicacion'.",
                detalles={"parametros": parametros},
            )
        cap = parametros["capacidad_personas"]
        if not isinstance(cap, int) or isinstance(cap, bool) or cap <= 0:
            raise ValidacionEntidadError(
                "La capacidad de la sala debe ser un entero positivo.",
                detalles={"capacidad_personas": cap},
            )
        if not isinstance(parametros["ubicacion"], str) or not parametros["ubicacion"].strip():
            raise ValidacionEntidadError(
                "La ubicación de la sala es obligatoria.",
                detalles={"ubicacion": parametros["ubicacion"]},
            )

    def calcular_costo(self, duracion: float) -> float:
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion <= 0:
            raise CalculoInconsistenteError(
                "La duración en horas para reserva de sala debe ser mayor que cero.",
                detalles={"duracion": duracion},
            )
        recargo = 1.15 if duracion > 4 else 1.0
        return round(self._tarifa_base * float(duracion) * recargo, 2)

    def describir(self) -> str:
        return (
            f"Reserva de Sala '{self._nombre}' en {self._parametros.get('ubicacion')} "
            f"(Capacidad: {self._parametros.get('capacidad_personas')} personas) - "
            f"Tarifa/hora: ${self._tarifa_base:,.2f}"
        )


class AlquilerEquipo(Servicio):
    """Servicio para alquiler de equipos tecnológicos."""

    def validar_parametros(self, parametros: Dict[str, Any]) -> None:
        if "tipo_equipo" not in parametros or "unidades_disponibles" not in parametros:
            raise ValidacionEntidadError(
                "AlquilerEquipo requiere 'tipo_equipo' y 'unidades_disponibles'.",
                detalles={"parametros": parametros},
            )
        unidades = parametros["unidades_disponibles"]
        if not isinstance(unidades, int) or isinstance(unidades, bool) or unidades < 0:
            raise ValidacionEntidadError(
                "Las unidades disponibles deben ser un entero mayor o igual a cero.",
                detalles={"unidades_disponibles": unidades},
            )
        if not isinstance(parametros["tipo_equipo"], str) or not parametros["tipo_equipo"].strip():
            raise ValidacionEntidadError(
                "El tipo de equipo es obligatorio.",
                detalles={"tipo_equipo": parametros["tipo_equipo"]},
            )

    def calcular_costo(self, duracion: float) -> float:
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion <= 0:
            raise CalculoInconsistenteError(
                "La duración en días para alquiler de equipo debe ser mayor que cero.",
                detalles={"duracion": duracion},
            )
        unidades = self._parametros.get("unidades_disponibles", 0)
        if unidades <= 0 or not self._disponible:
            raise ServicioNoDisponibleError(
                f"No hay unidades disponibles para '{self._nombre}'.",
                detalles={"servicio_id": self._id_entidad, "unidades": unidades},
            )
        return round((self._tarifa_base * float(duracion)) * 1.08, 2)

    def describir(self) -> str:
        return (
            f"Alquiler de Equipo '{self._nombre}' ({self._parametros.get('tipo_equipo')}) - "
            f"Unidades: {self._parametros.get('unidades_disponibles')} | "
            f"Tarifa/día: ${self._tarifa_base:,.2f}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio para asesorías técnicas o de arquitectura de software."""

    def validar_parametros(self, parametros: Dict[str, Any]) -> None:
        if "especialidad" not in parametros or "modalidad" not in parametros:
            raise ValidacionEntidadError(
                "AsesoriaEspecializada requiere 'especialidad' y 'modalidad'.",
                detalles={"parametros": parametros},
            )
        modalidad = str(parametros["modalidad"]).strip().upper()
        if modalidad not in {"REMOTA", "PRESENCIAL", "HIBRIDA"}:
            raise ValidacionEntidadError(
                "Modalidad inválida. Use REMOTA, PRESENCIAL o HIBRIDA.",
                detalles={"modalidad": parametros["modalidad"]},
            )

    def calcular_costo(self, duracion: float) -> float:
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion < 1:
            raise CalculoInconsistenteError(
                "La asesoría especializada requiere al menos 1 hora.",
                detalles={"duracion": duracion},
            )
        modalidad = str(self._parametros.get("modalidad", "REMOTA")).upper()
        factor = 1.25 if modalidad == "PRESENCIAL" else (1.10 if modalidad == "HIBRIDA" else 1.0)
        return round(self._tarifa_base * float(duracion) * factor, 2)

    def describir(self) -> str:
        return (
            f"Asesoría Especializada '{self._nombre}' en {self._parametros.get('especialidad')} "
            f"[{self._parametros.get('modalidad')}] - Tarifa/hora: ${self._tarifa_base:,.2f}"
        )